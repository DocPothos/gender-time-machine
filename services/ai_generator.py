import os
import re
import anthropic
from pathlib import Path

from core.timeline_engine import build_decade_context, build_multi_decade_context

MODEL = "claude-sonnet-4-20250514"
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "reflection_prompt.txt"


def _get_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. "
            "Copy .env.example to .env and add your key, then restart the app."
        )
    return anthropic.Anthropic(api_key=api_key)


def _load_reflection_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def generate_reflection_questions(
    growing_up_decades: list,
    all_decades: dict,
    identity_info: dict,
) -> list:
    """
    Generate exactly 3 reflection questions personalized to BOTH the era AND the
    person's identity (gender identity, sexuality, pressure felt).

    Parameters
    ----------
    growing_up_decades : list
        Ordered list of decade keys spanning the user's growing-up years.
    all_decades : dict
        Full decades data loaded from decades.json.
    identity_info : dict
        Keys: birth_year, gender_identity, sexuality, pressure_to_conform, felt_different.
    """
    client = _get_client()

    # Build context from all growing-up decades
    multi_context = build_multi_decade_context(growing_up_decades, all_decades)

    # Load base system prompt and append identity-specific instructions
    base_prompt = _load_reflection_prompt()
    gender_identity = identity_info.get("gender_identity", "not specified")
    sexuality = identity_info.get("sexuality", "not specified")
    pressure = identity_info.get("pressure_to_conform", "not specified")
    felt_different = identity_info.get("felt_different", "not specified")
    birth_year = identity_info.get("birth_year", "not specified")

    identity_instructions = f"""
PERSONALIZATION INSTRUCTIONS:
The user has shared the following about themselves:
- Birth year: {birth_year}
- Gender identity: {gender_identity}
- Sexuality: {sexuality}
- Felt pressure to conform to gender norms: {pressure}
- Felt different from peers around gender: {felt_different}

Generate exactly 3 reflection questions that are:
1. Deeply personalized to this specific person's gender identity and sexuality
2. Grounded in the historical era(s) they grew up in
3. Sensitive to the degree of conformity pressure and difference they felt
4. Written in second person ("you"/"your")
5. Open-ended and introspective — not yes/no questions
6. Compassionate and non-judgmental in tone

Return only the 3 numbered questions, nothing else.
"""

    system_prompt = base_prompt + "\n\n" + identity_instructions

    # Determine the primary decade label for the user message
    primary_decade_key = growing_up_decades[len(growing_up_decades) // 2] if growing_up_decades else ""
    primary_label = ""
    if primary_decade_key and primary_decade_key in all_decades:
        primary_label = all_decades[primary_decade_key].get("label", primary_decade_key)

    user_message = (
        f"Generate 3 reflection questions for a user who grew up across the "
        f"following era(s): {', '.join(growing_up_decades)}. "
        f"Their primary coming-of-age decade was the {primary_label}.\n\n"
        f"DECADE CONTEXT:\n{multi_context}\n\n"
        f"USER IDENTITY:\n"
        f"Gender identity: {gender_identity}\n"
        f"Sexuality: {sexuality}\n"
        f"Pressure to conform: {pressure}\n"
        f"Felt different from peers: {felt_different}"
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    questions = _parse_numbered_list(raw)

    if len(questions) < 1:
        questions = [
            line.strip()
            for line in raw.split("\n")
            if line.strip() and not line.strip().isdigit()
        ]

    return questions[:3]


def generate_experience_narrative(
    birth_year: int,
    growing_up_decades: list,
    all_decades: dict,
    identity_info: dict,
    answers: dict,
    questions: list,
) -> str:
    """
    Generate a 250-300 word narrative in second person about how the era's gender
    norms would have shaped THIS specific person's experience growing up.
    """
    client = _get_client()

    # Use the middle decade as primary context
    primary_decade_key = growing_up_decades[len(growing_up_decades) // 2] if growing_up_decades else ""
    primary_context = ""
    if primary_decade_key and primary_decade_key in all_decades:
        primary_context = build_decade_context(primary_decade_key, all_decades[primary_decade_key])

    # Build Q&A text
    qa_pairs = []
    for i, (key, answer) in enumerate(answers.items()):
        if answer.strip() and i < len(questions):
            qa_pairs.append(f"Q{i + 1}: {questions[i]}\nAnswer: {answer.strip()}")
    qa_text = "\n\n".join(qa_pairs)

    gender_identity = identity_info.get("gender_identity", "not specified")
    sexuality = identity_info.get("sexuality", "not specified")
    pressure = identity_info.get("pressure_to_conform", "not specified")
    felt_different = identity_info.get("felt_different", "not specified")

    decade_labels = []
    for dk in growing_up_decades:
        if dk in all_decades:
            decade_labels.append(all_decades[dk].get("label", dk))
    era_span = " and the ".join(decade_labels) if decade_labels else "their growing-up era"

    system_prompt = (
        "You are a warm, empathetic cultural historian specializing in gender studies and personal narrative. "
        "You help people understand how historical gender norms shaped their lived experience in deeply personal ways. "
        "Your tone is compassionate, non-judgmental, intellectually grounded, and emotionally attuned. "
        "You never moralize or tell people what to believe or feel. "
        "You speak directly to the user in second person using 'you' and 'your'. "
        "You are especially sensitive to LGBTQ+ identities and the particular challenges they faced in different eras. "
        "Write in flowing prose — no bullet points, no headers. Just warm, narrative paragraphs."
    )

    user_message = f"""A user has shared their identity and answered reflection questions about growing up
in the {era_span}. Write a personal narrative about their experience.

USER IDENTITY:
- Birth year: {birth_year}
- Gender identity: {gender_identity}
- Sexuality: {sexuality}
- Felt pressure to conform to gender norms: {pressure}
- Felt different from peers around gender: {felt_different}

THEIR GROWING-UP ERA CONTEXT:
{primary_context}

USER'S REFLECTION RESPONSES:
{qa_text}

Write a 250-300 word narrative in second person ("you", "your") about how the gender norms
of the {era_span} would have specifically shaped THIS person's experience growing up,
given their {gender_identity} gender identity and {sexuality} sexuality.

Be specific: name the cultural forces, social expectations, and historical realities that
would have touched their daily life — at school, at home, in friendships, in their own
interior world. Reference their reflection answers where relevant.

Do not use headers or bullet points. Write in warm, flowing prose paragraphs.
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text.strip()


def generate_whatif_narrative(
    identity_info: dict,
    all_decades: dict,
) -> str:
    """
    Generate a 250-300 word narrative imagining what life would have been like
    if the user had grown up in the 2020s with today's visibility and language.
    """
    client = _get_client()

    # Use 2020s context
    context_2020s = ""
    if "2020s" in all_decades:
        context_2020s = build_decade_context("2020s", all_decades["2020s"])

    gender_identity = identity_info.get("gender_identity", "not specified")
    sexuality = identity_info.get("sexuality", "not specified")
    birth_year = identity_info.get("birth_year", "not specified")

    system_prompt = (
        "You are a warm, hopeful cultural historian specializing in gender studies and LGBTQ+ history. "
        "You help people imagine alternative futures and the liberating possibilities of greater visibility and representation. "
        "Your tone is hopeful, affirming, emotionally resonant, and grounded in real cultural shifts. "
        "You never minimize the challenges that remain, but you focus on the genuine progress and expanded possibilities of today. "
        "You speak directly to the user in second person using 'you' and 'your'. "
        "Write in flowing, evocative prose — no bullet points, no headers."
    )

    user_message = f"""Imagine a person who was actually born in {birth_year} but ask:
what if they had grown up in the 2020s instead — with today's visibility, language, and representation?

USER IDENTITY:
- Gender identity: {gender_identity}
- Sexuality: {sexuality}
- Actual birth year: {birth_year}

2020s CONTEXT:
{context_2020s}

Write a 250-300 word narrative in second person ("you", "your") answering the question:
"What if you had grown up in the 2020s with today's visibility, language, and representation?"

Be specific to their {gender_identity} gender identity and {sexuality} sexuality.
Name the real resources, communities, language, media representation, and cultural shifts
that would have been available to them. Paint a picture of the freedoms, the words they
would have had, the role models they could have found, the communities that would have
been there for them.

Acknowledge what has changed and what genuine progress exists today — while also being
honest that challenges remain. End on a note of warmth and possibility.

Do not use headers or bullet points. Write in warm, flowing prose paragraphs.
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text.strip()


def _parse_numbered_list(text: str) -> list:
    """Parse a numbered list like '1. Question text' into a list of strings."""
    lines = text.split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove leading number + punctuation: "1.", "1)", "1:"
        cleaned = re.sub(r"^\d+[\.\)\:]\s*", "", line).strip()
        if cleaned and len(cleaned) > 10:
            questions.append(cleaned)
    return questions
