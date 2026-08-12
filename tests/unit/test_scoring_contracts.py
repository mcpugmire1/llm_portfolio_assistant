"""Contract tests for properties claimed by scoring, validation, formatting, and filter docstrings."""

from utils.filters import matches_filters
from utils.formatting import story_has_metric
from utils.scoring import _hybrid_score
from utils.validation import token_overlap_ratio

# ---------------------------------------------------------------------------
# Fixture helpers -- replicate load_star_stories() normalization from app.py
# ---------------------------------------------------------------------------


def _ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if str(x).strip()]
    return [str(v)] if str(v).strip() else []


def _split_tags(s):
    if not s:
        return []
    if isinstance(s, list):
        return [str(x).strip() for x in s if str(x).strip()]
    return [t.strip() for t in str(s).split(",") if t.strip()]


def _normalized_story():
    """Return a story dict shaped the way load_star_stories() produces it.

    Applies the same two normalization steps from app.py: list fields coerced
    via _ensure_list(), public_tags parsed from comma-separated string via
    _split_tags(). No synthetic keys added; shape matches what production
    stories look like after the loader runs.
    """
    raw = {
        "id": "test-001",
        "Title": "Platform Modernization",
        "Client": "JPMC",
        "Role": "Engineering Lead",
        "Sub-category": "Platform Engineering",
        "Industry": "Financial Services",
        "Solution / Offering": "Cloud Migration",
        "Era": "Accenture",
        # Raw string form -- _ensure_list normalizes to list
        "Performance": "Reduced latency by 60%",
        "Process": "Migrated core services to AWS",
        "Situation": None,
        "Task": None,
        "Action": None,
        "Result": None,
        "Competencies": None,
        "Use Case(s)": None,
        # Comma-separated string -- _split_tags parses to list
        "public_tags": "cloud,aws",
    }
    story = dict(raw)
    story["id"] = str(story["id"]).strip()
    for field in (
        "Situation",
        "Task",
        "Action",
        "Result",
        "Process",
        "Performance",
        "Competencies",
        "Use Case(s)",
    ):
        if field in story:
            story[field] = _ensure_list(story[field])
    if isinstance(story.get("public_tags"), str):
        story["public_tags"] = _split_tags(story["public_tags"])
    return story


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------


def test_token_overlap_ratio_stays_within_unit_interval():
    # validation.py docstring: "Float ratio between 0.0 and 1.0 representing the proportion of unique query tokens found in vocab"
    result = token_overlap_ratio("platform platform", {"platform"})
    assert 0.0 <= result <= 1.0


def test_story_has_metric_detects_percentage_in_performance():
    # formatting.py line 39: s.get("what") -- METRIC_RX pattern \b\d{1,3}\s?% matches percentage strings
    assert story_has_metric(_normalized_story()) is True


def test_matches_filters_passes_has_metric_gate_for_story_with_metric():
    # filters.py line 115: if has_metric and not story_has_metric(s): return False
    assert matches_filters(_normalized_story(), {"has_metric": True}) is True


def test_hybrid_score_matches_docstring_stated_value():
    # scoring.py docstring example: _hybrid_score(0.8, 0.6)  # Default: semantic only → 0.8
    assert _hybrid_score(0.8, 0.6) == 0.8
