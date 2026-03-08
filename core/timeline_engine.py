import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "decades.json"

DIMENSION_DISPLAY = {
    "norm_rigidity": "Norm Rigidity",
    "work_access": "Work Access (Women)",
    "political_power": "Political Power (Women)",
    "appearance_pressure": "Appearance Pressure",
    "sexuality_openness": "Sexuality/Gender Openness",
    "domestic_expectation": "Domestic Role Expectation",
}


def load_decades() -> dict:
    """Load all decade data from the JSON data file."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_decades() -> list:
    """Return ordered list of decade keys."""
    data = load_decades()
    return list(data.keys())


def get_decade_data(decade: str) -> dict:
    """Return data for a single decade by key (e.g. '1950s')."""
    data = load_decades()
    return data.get(decade, {})


def build_decade_context(decade_key: str, decade_data: dict) -> str:
    """
    Build a rich, structured text context string suitable for use in AI prompts.
    Combines all relevant fields into a single readable block.
    """
    norms = decade_data.get("gender_norms", {})
    dims = decade_data.get("dimensions", {})
    women_norms = "; ".join(norms.get("women", []))
    men_norms = "; ".join(norms.get("men", []))
    key_events = "; ".join(decade_data.get("key_events", []))
    expectations = "; ".join(decade_data.get("dominant_expectations", []))
    touchstones = "; ".join(decade_data.get("cultural_touchstones", []))

    dim_lines = "\n".join(
        f"  - {DIMENSION_DISPLAY.get(k, k)} (0–10 scale): {dims.get(k, 'N/A')}"
        for k in DIMENSION_DISPLAY
    )

    context = f"""DECADE: {decade_data.get("label", decade_key)}
YEARS: {decade_data.get("years", "")}
ERA TAGLINE: {decade_data.get("tagline", "")}

HISTORICAL CONTEXT:
{decade_data.get("context", "")}

GENDER NORMS — WOMEN WERE EXPECTED TO:
{women_norms}

GENDER NORMS — MEN WERE EXPECTED TO:
{men_norms}

DOMINANT CULTURAL EXPECTATIONS:
{expectations}

KEY HISTORICAL EVENTS:
{key_events}

CULTURAL TOUCHSTONES (books, films, icons):
{touchstones}

QUANTIFIED NORM DIMENSIONS (0 = least, 10 = most):
{dim_lines}
""".strip()

    return context


def build_multi_decade_context(decade_keys: list, all_decades: dict) -> str:
    """Build combined context for multiple decades."""
    parts = []
    for key in decade_keys:
        if key in all_decades:
            parts.append(build_decade_context(key, all_decades[key]))
    return "\n\n---\n\n".join(parts)


def compute_century_averages(all_decades: dict) -> dict:
    """Compute the average score for each dimension across all decades."""
    dim_keys = list(DIMENSION_DISPLAY.keys())
    totals = {k: 0.0 for k in dim_keys}
    count = len(all_decades)

    for data in all_decades.values():
        dims = data.get("dimensions", {})
        for k in dim_keys:
            totals[k] += dims.get(k, 5)

    return {k: round(v / count, 2) for k, v in totals.items()}


def get_decade_summary(decade_key: str, decade_data: dict) -> str:
    """Return a short one-paragraph summary for display in the UI."""
    return (
        f"**{decade_data.get('label', decade_key)}: {decade_data.get('tagline', '')}** — "
        f"{decade_data.get('context', '')[:300]}..."
    )


def calculate_growing_up_decades(birth_year: int) -> list:
    """
    Return ordered list of decade keys that overlap with the user's growing-up
    period (birth_year through birth_year + 18).
    Only returns keys that exist in decades.json.
    """
    end_year = birth_year + 18
    all_data = load_decades()
    result = []
    for key in all_data.keys():
        try:
            start = int(key.replace("s", ""))
        except ValueError:
            continue
        decade_end = start + 9
        if start <= end_year and decade_end >= birth_year:
            result.append(key)
    return result


def get_era_glance_facts(growing_up_decades: list, all_decades: dict) -> list:
    """
    Return 3-4 key facts (strings) about gender norms across the user's growing-up decades.
    Pulls from key_events of the first 2 overlapping decades.
    """
    facts = []
    for dk in growing_up_decades[:2]:
        if dk in all_decades:
            events = all_decades[dk].get("key_events", [])
            facts.extend(events[:2])
    # Also add a norm context snippet from the primary decade
    if growing_up_decades and growing_up_decades[0] in all_decades:
        primary = all_decades[growing_up_decades[0]]
        facts.append(primary.get("tagline", ""))
    return [f for f in facts if f][:4]
