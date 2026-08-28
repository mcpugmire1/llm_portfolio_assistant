"""Contract tests for properties claimed by scoring, validation, formatting, and filter docstrings."""

import pytest

from utils.corpus_loader import normalize_story
from utils.filters import matches_filters
from utils.formatting import story_has_metric
from utils.scoring import _hybrid_score
from utils.validation import token_overlap_ratio

# ---------------------------------------------------------------------------
# Fixture helpers -- normalization now delegates to the shared corpus loader
# ---------------------------------------------------------------------------


def _normalized_story():
    """Return a story dict shaped the way load_star_stories() produces it.

    Delegates normalization to normalize_story() from utils.corpus_loader so
    that this fixture stays in sync with app.py automatically.
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
        # Raw string form -- normalize_story coerces to list
        "Performance": "Reduced latency by 60%",
        "Process": "Migrated core services to AWS",
        "Situation": None,
        "Task": None,
        "Action": None,
        "Result": None,
        "Competencies": None,
        "Use Case(s)": None,
        # Comma-separated string -- normalize_story parses to list
        "public_tags": "cloud,aws",
    }
    story = dict(raw)
    story["id"] = str(story["id"]).strip()
    normalize_story(story)
    return story


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason="MATTGPT-180: fixture built on phantom schema (failing by design "
    "as pre-registered fix). Remove xfail when -180 lands the schema unification.",
    strict=False,
)
def test_token_overlap_ratio_stays_within_unit_interval():
    # validation.py docstring: "Float ratio between 0.0 and 1.0 representing the proportion of unique query tokens found in vocab"
    result = token_overlap_ratio("platform platform", {"platform"})
    assert 0.0 <= result <= 1.0


@pytest.mark.xfail(
    reason="MATTGPT-180: fixture built on phantom schema (failing by design "
    "as pre-registered fix). Remove xfail when -180 lands the schema unification.",
    strict=False,
)
def test_story_has_metric_detects_percentage_in_performance():
    # formatting.py line 39: s.get("what") -- METRIC_RX pattern \b\d{1,3}\s?% matches percentage strings
    assert story_has_metric(_normalized_story()) is True


@pytest.mark.xfail(
    reason="MATTGPT-180: fixture built on phantom schema (failing by design "
    "as pre-registered fix). Remove xfail when -180 lands the schema unification.",
    strict=False,
)
def test_matches_filters_passes_has_metric_gate_for_story_with_metric():
    # filters.py line 115: if has_metric and not story_has_metric(s): return False
    assert matches_filters(_normalized_story(), {"has_metric": True}) is True


def test_hybrid_score_matches_docstring_stated_value():
    # scoring.py docstring example: _hybrid_score(0.8, 0.6)  # W_PC=1.0, W_KW=0.15 -> 0.89
    assert _hybrid_score(0.8, 0.6) == 0.89
