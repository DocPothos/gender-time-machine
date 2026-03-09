import os
import re
import sys

# Ensure project root is on the path so sub-packages resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Gender Norms Time Machine",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }

    /* Typography */
    .gtm-hero-title {
        font-size: 2.6rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #F26076 0%, #FF9760 55%, #FFD150 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        line-height: 1.2; margin-bottom: 0.3rem;
    }
    .gtm-subtitle { font-size: 1.1rem; text-align: center; color: #666; margin-bottom: 1.2rem; }

    /* Era/past sections — warm cream */
    .era-card {
        background: #FFF9F0;
        border-left: 4px solid #458B73;
        border-radius: 10px; padding: 1.2rem 1.4rem; margin: 0.8rem 0;
    }

    /* Future/whatif sections — coral warmth */
    .whatif-card {
        background: linear-gradient(135deg, #FFF9F0 0%, #FFE8E0 100%);
        border-left: 4px solid #F26076;
        border-radius: 10px; padding: 1.2rem 1.4rem; margin: 0.8rem 0;
    }

    /* Pull-quote */
    .pull-quote {
        border-left: 5px solid #458B73;
        background: #f4faf7;
        padding: 1.2rem 1.5rem;
        border-radius: 0 10px 10px 0;
        font-style: italic;
        font-size: 1.0rem;
        color: #444;
        margin: 1rem 0;
    }
    .pull-quote-attribution {
        font-style: normal; font-weight: 600; color: #458B73;
        margin-top: 0.5rem; font-size: 0.9rem;
    }

    /* Micro-copy affirming */
    .affirm-text { color: #458B73; font-style: italic; font-size: 0.95rem; text-align: center; margin: 0.5rem 0; }

    /* Share card */
    .share-card {
        background: linear-gradient(135deg, #F26076 0%, #FF9760 55%, #FFD150 100%);
        color: white; border-radius: 14px;
        padding: 1.5rem 2rem; margin: 1rem 0;
        text-align: center;
    }
    .share-card h3 { color: white; margin-bottom: 0.5rem; }
    .share-card p { color: rgba(255,255,255,0.92); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state defaults ────────────────────────────────────────────────────
DEFAULTS = {
    "page": "welcome",
    "birth_year": None,
    "gender_identity": None,
    "sexuality": None,
    "pressure_to_conform": None,
    "felt_different": None,
    "growing_up_decades": [],
    "primary_decade": None,
    "era_facts": [],
    "reflection_questions": [],
    "reflection_answers": {},
    "experience_narrative": None,
    "whatif_narrative": None,
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Navigation helper ─────────────────────────────────────────────────────────
def go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


# ── Progress indicator ────────────────────────────────────────────────────────
PAGES = [
    ("welcome", "Welcome"),
    ("about_you", "About You"),
    ("reflection_questions", "Reflection"),
    ("results_dashboard", "Results"),
]


def render_progress() -> None:
    current = st.session_state.page
    page_keys = [p[0] for p in PAGES]
    current_idx = page_keys.index(current) if current in page_keys else 0

    cols = st.columns(len(PAGES))
    for i, (key, label) in enumerate(PAGES):
        with cols[i]:
            if i < current_idx:
                style = "background:#458B73;color:white;"
                text = f"✓ {label}"
            elif i == current_idx:
                style = "background:#F26076;color:white;font-weight:700;"
                text = label
            else:
                style = "background:#e0e0e0;color:#777;"
                text = label
            st.markdown(
                f"<div style='{style}text-align:center;padding:0.4rem 0;"
                f"border-radius:20px;font-size:0.82rem;'>{text}</div>",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)



# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — WELCOME
# ═════════════════════════════════════════════════════════════════════════════
def page_welcome() -> None:
    st.markdown(
        "<h1 class='gtm-hero-title'>The Gender Norms Time Machine</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='gtm-subtitle'>A personal journey through a century of gender expectations</p>",
        unsafe_allow_html=True,
    )

    render_progress()

    # Pull-quote — creator's statement
    st.markdown(
        """
        <div class="pull-quote">
            This app was born from a personal realization. Growing up surrounded by the heteronormativity of the
            1980s and 1990s, I didn't realize that I was queer until decades
            later. I built the Gender Norms Time Machine to explore a question that still moves me: how
            different might my journey have been if I'd grown up with today's visibility, language,
            and representation?
            <div class="pull-quote-attribution">— The Creator</div>
        </div>
        """.strip(),
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### About This Experience")
    st.markdown(
        """
        This app asks you to share a bit about yourself — your birth year and how you experienced
        gender growing up — then uses AI to explore how history shaped you, and what might have
        been different.

        Using AI powered by [Claude](https://anthropic.com), it will:

        - **Situate you in your historical era** with rich cultural context drawn from your birth year
        - **Ask you 3 personal reflection questions** tailored to your era and identity
        - **Generate a narrative** about how those years shaped your specific experience
        - **Imagine an alternative** — what if you'd grown up in the 2020s with today's visibility?

        ---

        """
    )

    has_key = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    if not has_key:
        st.warning(
            "**API key not found.** Copy `.env.example` → `.env` and add your "
            "`ANTHROPIC_API_KEY`, then restart the app."
        )

    st.markdown("")
    if st.button("Begin Your Journey →", type="primary", use_container_width=True):
        go("about_you")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ABOUT YOU
# ═════════════════════════════════════════════════════════════════════════════
def page_about_you() -> None:
    from core.timeline_engine import load_decades, calculate_growing_up_decades, get_era_glance_facts

    st.markdown(
        "<h1 class='gtm-hero-title'>About You</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='gtm-subtitle'>Help us understand your experience growing up</p>",
        unsafe_allow_html=True,
    )

    render_progress()

    all_decades = load_decades()

    left_col, right_col = st.columns(2)

    with left_col:
        birth_year_input = st.number_input(
            "What year were you born?",
            min_value=1920,
            max_value=2010,
            value=st.session_state.birth_year if st.session_state.birth_year else 1975,
            step=1,
            key="birth_year_widget",
        )

        gender_identity_input = st.selectbox(
            "How did you identify your gender growing up?",
            options=[
                "-- Select --",
                "Cisgender man",
                "Cisgender woman",
                "Transgender man",
                "Transgender woman",
                "Nonbinary/genderqueer",
                "Genderfluid",
                "Not sure / questioning",
                "Prefer not to say",
            ],
            index=0 if not st.session_state.gender_identity else [
                "-- Select --",
                "Cisgender man",
                "Cisgender woman",
                "Transgender man",
                "Transgender woman",
                "Nonbinary/genderqueer",
                "Genderfluid",
                "Not sure / questioning",
                "Prefer not to say",
            ].index(st.session_state.gender_identity)
            if st.session_state.gender_identity in [
                "-- Select --",
                "Cisgender man",
                "Cisgender woman",
                "Transgender man",
                "Transgender woman",
                "Nonbinary/genderqueer",
                "Genderfluid",
                "Not sure / questioning",
                "Prefer not to say",
            ] else 0,
        )

        sexuality_input = st.selectbox(
            "How did you identify your sexuality growing up?",
            options=[
                "-- Select --",
                "Heterosexual / straight",
                "Gay / lesbian",
                "Bisexual",
                "Pansexual",
                "Asexual",
                "Not sure / questioning",
                "Prefer not to say",
            ],
            index=0 if not st.session_state.sexuality else [
                "-- Select --",
                "Heterosexual / straight",
                "Gay / lesbian",
                "Bisexual",
                "Pansexual",
                "Asexual",
                "Not sure / questioning",
                "Prefer not to say",
            ].index(st.session_state.sexuality)
            if st.session_state.sexuality in [
                "-- Select --",
                "Heterosexual / straight",
                "Gay / lesbian",
                "Bisexual",
                "Pansexual",
                "Asexual",
                "Not sure / questioning",
                "Prefer not to say",
            ] else 0,
        )

    with right_col:
        pressure_input = st.selectbox(
            "Did you feel pressure to conform to gender norms growing up?",
            options=["-- Select --", "Yes, definitely", "Somewhat", "Not really", "No"],
            index=0 if not st.session_state.pressure_to_conform else [
                "-- Select --", "Yes, definitely", "Somewhat", "Not really", "No"
            ].index(st.session_state.pressure_to_conform)
            if st.session_state.pressure_to_conform in [
                "-- Select --", "Yes, definitely", "Somewhat", "Not really", "No"
            ] else 0,
        )

        felt_different_input = st.selectbox(
            "Did you feel different from your peers around gender?",
            options=["-- Select --", "Yes, definitely", "Somewhat", "Not really", "No"],
            index=0 if not st.session_state.felt_different else [
                "-- Select --", "Yes, definitely", "Somewhat", "Not really", "No"
            ].index(st.session_state.felt_different)
            if st.session_state.felt_different in [
                "-- Select --", "Yes, definitely", "Somewhat", "Not really", "No"
            ] else 0,
        )


    # ── Era at a Glance — renders immediately as birth year changes ───────────
    if birth_year_input:
        growing_decades = calculate_growing_up_decades(birth_year_input)
        if growing_decades:
            era_facts = get_era_glance_facts(growing_decades, all_decades)

            # Build decade info lines
            decade_info_lines = []
            for dk in growing_decades:
                if dk in all_decades:
                    dd = all_decades[dk]
                    decade_info_lines.append(
                        f"<strong>{dd.get('emoji', '')} {dd.get('label', dk)}</strong>: "
                        f"<em>{dd.get('tagline', '')}</em>"
                    )
            decade_info_html = "<br>".join(decade_info_lines)

            facts_html = "".join(
                f"<li style='margin-bottom:0.3rem;'>{fact}</li>" for fact in era_facts
            )

            primary_growing_decade = growing_decades[len(growing_decades) // 2]
            era_image_path = f"images/{primary_growing_decade}.jpg"

            img_col, card_col = st.columns([1, 2])
            with img_col:
                try:
                    st.image(era_image_path, use_container_width=True)
                except Exception:
                    pass
            with card_col:
                st.markdown(
                    f"""
                    <div class="era-card" style="margin-top:0;height:100%;">
                        <h4 style="margin-top:0;color:#2d6a55;">Your Era at a Glance</h4>
                        <p style="margin-bottom:0.6rem;">You grew up across:</p>
                        <p style="margin-bottom:0.8rem;">{decade_info_html}</p>
                        <p style="font-weight:600;color:#2d6a55;margin-bottom:0.4rem;">
                            Here's what was happening around gender during those years:
                        </p>
                        <ul style="margin:0;padding-left:1.2rem;color:#3a4a42;">
                            {facts_html}
                        </ul>
                    </div>
                    """.strip(),
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    nav_back, nav_continue = st.columns([1, 2])
    with nav_back:
        if st.button("← Back", use_container_width=True):
            go("welcome")
    with nav_continue:
        if st.button("Continue →", type="primary", use_container_width=True):
            # Validate
            errors = []
            if gender_identity_input == "-- Select --":
                errors.append("Please select your gender identity.")
            if sexuality_input == "-- Select --":
                errors.append("Please select your sexuality.")
            if pressure_input == "-- Select --":
                errors.append("Please answer the pressure to conform question.")
            if felt_different_input == "-- Select --":
                errors.append("Please answer the felt different question.")

            if errors:
                for err in errors:
                    st.warning(err)
            else:
                # Save to session state
                st.session_state.birth_year = birth_year_input
                st.session_state.gender_identity = gender_identity_input
                st.session_state.sexuality = sexuality_input
                st.session_state.pressure_to_conform = pressure_input
                st.session_state.felt_different = felt_different_input

                growing_decades = calculate_growing_up_decades(birth_year_input)
                st.session_state.growing_up_decades = growing_decades

                # Determine primary decade (middle of span)
                if growing_decades:
                    primary_idx = len(growing_decades) // 2
                    st.session_state.primary_decade = growing_decades[primary_idx]
                else:
                    st.session_state.primary_decade = None

                # Store era facts
                st.session_state.era_facts = get_era_glance_facts(growing_decades, all_decades)

                # Reset downstream state
                st.session_state.reflection_questions = []
                st.session_state.reflection_answers = {}
                st.session_state.experience_narrative = None
                st.session_state.whatif_narrative = None

                go("reflection_questions")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — REFLECTION QUESTIONS
# ═════════════════════════════════════════════════════════════════════════════
def page_reflection_questions() -> None:
    from core.timeline_engine import load_decades
    from services.ai_generator import generate_reflection_questions

    if not st.session_state.birth_year or not st.session_state.growing_up_decades:
        st.error("Please complete the About You section first.")
        if st.button("← Go Back"):
            go("about_you")
        return

    all_decades = load_decades()
    growing_up_decades = st.session_state.growing_up_decades
    primary_decade_key = st.session_state.primary_decade or growing_up_decades[0]
    primary_decade_data = all_decades.get(primary_decade_key, {})
    primary_label = primary_decade_data.get("label", primary_decade_key)

    st.markdown(
        f"<h1 class='gtm-hero-title'>Reflecting on the {primary_label}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='gtm-subtitle'>Answer honestly — from your own perspective today</p>",
        unsafe_allow_html=True,
    )

    render_progress()


    # ── Generate questions once ───────────────────────────────────────────────
    if not st.session_state.reflection_questions:
        if not os.getenv("ANTHROPIC_API_KEY", "").strip():
            st.error(
                "**API key required** to generate reflection questions. "
                "Add your `ANTHROPIC_API_KEY` to `.env` and restart the app."
            )
            if st.button("← Back to About You"):
                go("about_you")
            return

        with st.spinner("Generating your reflection questions..."):
            try:
                identity_info = {
                    "birth_year": st.session_state.birth_year,
                    "gender_identity": st.session_state.gender_identity,
                    "sexuality": st.session_state.sexuality,
                    "pressure_to_conform": st.session_state.pressure_to_conform,
                    "felt_different": st.session_state.felt_different,
                }
                questions = generate_reflection_questions(
                    growing_up_decades, all_decades, identity_info
                )
                st.session_state.reflection_questions = questions
                st.rerun()
            except Exception as e:
                st.error(f"Error generating questions: {e}")
                if st.button("← Back"):
                    go("about_you")
                return

    questions = st.session_state.reflection_questions

    st.markdown("")

    # ── Reflection form ───────────────────────────────────────────────────────
    with st.form("reflection_form"):
        answers = {}
        for i, question in enumerate(questions):
            st.markdown(
                f"""
                <div class="era-card">
                    <p style="font-weight:600;margin-bottom:0.5rem;color:#8B6914;">
                        Question {i + 1}
                    </p>
                    <p style="margin:0;color:#3d2b00;">{question}</p>
                </div>
                """.strip(),
                unsafe_allow_html=True,
            )
            answers[f"q{i + 1}"] = st.text_area(
                label=f"answer_{i + 1}",
                value=st.session_state.reflection_answers.get(f"q{i + 1}", ""),
                height=110,
                placeholder="Share your thoughts honestly...",
                label_visibility="collapsed",
            )
            if i < len(questions) - 1:
                st.markdown("")

        st.markdown("")
        form_cols = st.columns([1, 2])
        with form_cols[0]:
            back_btn = st.form_submit_button("← Back")
        with form_cols[1]:
            submit_btn = st.form_submit_button("Reveal My Story →", type="primary")

    if back_btn:
        go("about_you")

    if submit_btn:
        filled = sum(1 for v in answers.values() if v.strip())
        if filled < 2:
            st.warning("Please answer at least **2 questions** before continuing.")
        else:
            st.session_state.reflection_answers = answers
            st.session_state.experience_narrative = None
            st.session_state.whatif_narrative = None
            go("results_dashboard")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — RESULTS DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
def page_results_dashboard() -> None:
    from core.timeline_engine import load_decades
    from services.ai_generator import generate_experience_narrative, generate_whatif_narrative
    from visualization.charts import (
        create_timeline_chart,
        create_era_vs_2020s_chart,
    )

    if not st.session_state.birth_year or not st.session_state.reflection_answers:
        st.error("Please complete the reflection questions first.")
        if st.button("← Go to Reflection Questions"):
            go("reflection_questions")
        return

    all_decades = load_decades()
    growing_up_decades = st.session_state.growing_up_decades
    primary_decade_key = st.session_state.primary_decade or (growing_up_decades[0] if growing_up_decades else None)

    if not primary_decade_key:
        st.error("Could not determine your primary decade. Please go back.")
        if st.button("← Back"):
            go("about_you")
        return

    primary_decade_data = all_decades.get(primary_decade_key, {})
    primary_label = primary_decade_data.get("label", primary_decade_key)

    # Build decade label span for display
    decade_labels_list = []
    for dk in growing_up_decades:
        if dk in all_decades:
            decade_labels_list.append(all_decades[dk].get("label", dk))
    primary_decades_label = " & ".join(decade_labels_list) if decade_labels_list else primary_label

    st.markdown(
        "<h1 class='gtm-hero-title'>Your Story</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='gtm-subtitle'>How the {primary_decades_label} shaped you — and what might have been</p>",
        unsafe_allow_html=True,
    )

    render_progress()

    # ── Generate narratives if not yet generated ──────────────────────────────
    identity_info = {
        "birth_year": st.session_state.birth_year,
        "gender_identity": st.session_state.gender_identity,
        "sexuality": st.session_state.sexuality,
        "pressure_to_conform": st.session_state.pressure_to_conform,
        "felt_different": st.session_state.felt_different,
    }

    needs_generation = (
        not st.session_state.experience_narrative
        or not st.session_state.whatif_narrative
    )

    if needs_generation:
        if not os.getenv("ANTHROPIC_API_KEY", "").strip():
            st.session_state.experience_narrative = (
                "_AI narrative unavailable — no API key provided. "
                "Add your `ANTHROPIC_API_KEY` to `.env` and restart._"
            )
            st.session_state.whatif_narrative = (
                "_AI narrative unavailable — no API key provided._"
            )
        else:
            gen_container = st.container()
            with gen_container:
                st.markdown("### Exploring your journey through history...")
                for fact in st.session_state.era_facts:
                    st.info(fact)
                with st.spinner("Claude is writing your personal narrative..."):
                    try:
                        if not st.session_state.experience_narrative:
                            st.session_state.experience_narrative = generate_experience_narrative(
                                birth_year=st.session_state.birth_year,
                                growing_up_decades=growing_up_decades,
                                all_decades=all_decades,
                                identity_info=identity_info,
                                answers=st.session_state.reflection_answers,
                                questions=st.session_state.reflection_questions,
                            )
                        if not st.session_state.whatif_narrative:
                            st.session_state.whatif_narrative = generate_whatif_narrative(
                                identity_info=identity_info,
                                all_decades=all_decades,
                            )
                        st.rerun()
                    except Exception as e:
                        st.session_state.experience_narrative = f"_Error generating narrative: {e}_"
                        st.session_state.whatif_narrative = f"_Error generating narrative: {e}_"

    experience_narrative = st.session_state.experience_narrative or ""
    whatif_narrative = st.session_state.whatif_narrative or ""

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1: Your Growing Up Era
    # ═══════════════════════════════════════════════════════════════════════
    decades_emoji_str = " ".join(
        all_decades[dk].get("emoji", "") for dk in growing_up_decades if dk in all_decades
    )

    st.markdown(
        f"""
        <div class="era-card">
            <h3 style="margin-top:0;color:#8B6914;">Your Growing Up Era</h3>
            <p style="color:#5a3e10;margin-bottom:0;">
                {decades_emoji_str} You grew up across the <strong>{primary_decades_label}</strong>
            </p>
        </div>
        """.strip(),
        unsafe_allow_html=True,
    )

    timeline_fig = create_timeline_chart(all_decades, primary_decade_key)
    st.plotly_chart(timeline_fig, use_container_width=True)

    # Comparison bar: their era vs 2020s
    st.markdown("#### How Much Has Changed Since Your Growing Up Years?")
    era_vs_fig = create_era_vs_2020s_chart(all_decades, primary_decade_key)
    st.plotly_chart(era_vs_fig, use_container_width=True)

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2: Your Experience
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        """
        <div class="era-card">
            <h3 style="margin-top:0;color:#8B6914;">How Those Years Shaped You</h3>
        </div>
        """.strip(),
        unsafe_allow_html=True,
    )

    st.markdown(experience_narrative)

    # Reflection Q&A in expanders
    questions = st.session_state.reflection_questions
    answers = st.session_state.reflection_answers
    if questions and answers:
        st.markdown("**Your reflection responses:**")
        for i, (key, answer) in enumerate(answers.items()):
            if answer.strip() and i < len(questions):
                short_q = questions[i][:80] + ("..." if len(questions[i]) > 80 else "")
                with st.expander(f"Q{i + 1}: {short_q}"):
                    st.write(answer)

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3: What If You Were Born Today?
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(
        """
        <div class="whatif-card">
            <h3 style="margin-top:0;color:#1565C0;">What If You'd Grown Up in the 2020s?</h3>
        </div>
        """.strip(),
        unsafe_allow_html=True,
    )

    st.markdown(whatif_narrative)

    # Local images for 2020s section
    whatif_local_images = ["images/nonbinary.jpg", "images/pride_bracelet.jpg", "images/pride_skirt.jpg"]
    whatif_img_cols = st.columns(3)
    for i, img_path in enumerate(whatif_local_images):
        with whatif_img_cols[i]:
            try:
                st.image(img_path, use_container_width=True)
            except Exception:
                pass

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════════════
    # SHARE CARD
    # ═══════════════════════════════════════════════════════════════════════
    birth_year = st.session_state.birth_year
    gender_identity = st.session_state.gender_identity or ""
    sexuality = st.session_state.sexuality or ""

    # Extract first sentence from experience_narrative (strip markdown)
    first_sentence = ""
    if experience_narrative:
        clean_text = re.sub(r"[#*_`]", "", experience_narrative)
        parts = clean_text.split(".")
        if parts:
            first_sentence = parts[0].strip() + "."

    st.markdown(
        f"""
        <div class="share-card">
            <h3>The Gender Norms Time Machine</h3>
            <p>Born {birth_year} · {gender_identity} · {sexuality}</p>
            <p>Growing up era: {primary_decades_label}</p>
            <p style="font-style:italic;margin-top:0.8rem;">{first_sentence}</p>
            <p style="font-size:0.8rem;opacity:0.8;margin-top:0.5rem;">Screenshot to share your story</p>
        </div>
        """.strip(),
        unsafe_allow_html=True,
    )

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown("---")
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("← Explore Another Era", use_container_width=True):
            # Reset to about_you, preserve birth year and identity info
            st.session_state.growing_up_decades = []
            st.session_state.primary_decade = None
            st.session_state.era_facts = []
            st.session_state.reflection_questions = []
            st.session_state.reflection_answers = {}
            st.session_state.experience_narrative = None
            st.session_state.whatif_narrative = None
            go("about_you")
    with nav2:
        if st.button("Start Over", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            go("welcome")


# ═════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════════════════
ROUTE_MAP = {
    "welcome": page_welcome,
    "about_you": page_about_you,
    "reflection_questions": page_reflection_questions,
    "results_dashboard": page_results_dashboard,
}

current = st.session_state.get("page", "welcome")
ROUTE_MAP.get(current, page_welcome)()
