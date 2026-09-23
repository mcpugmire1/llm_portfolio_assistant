"""MATTGPT-250 Red: return-shape work for the profile_facts key.

Class A: semantic_search returns profile_facts on every return path.
Class B: profile_facts is a top-level key, not mixed into results.
  B1: separation change test.
  B2: My Work view iteration guard -- passes on Red by design (regression
      guard; results are already pure stories, so the assertion holds
      today and continues to hold on Green as long as profile_facts stays
      out of results).

Every A test asserts profile_facts equals load_matt_profile() output --
not just non-empty. A Green that returns "" or None or a placeholder
would fail.

Class A uses the REAL semantic_search with pinecone_semantic_search mocked
per branch. Class B reuses Class A's happy-path fixture so B doesn't test
its own mock shape.

Path markers per branch (so tests can't accidentally pass on a different
path than they name):
  - empty-query short-circuit: results == [] AND top_score == 0.0
  - pinecone unavailable + overlap-rejected: reason == "fallback:pinecone_unavailable" AND results == []
  - pinecone unavailable + local fallback: reason == "fallback:pinecone_unavailable" AND results != []
  - no confident hits (confidence "none"): confidence == "none" AND top_score > 0
  - filters blocked all: relaxed_count in return AND results == []
  - happy path: confidence == "high" AND results != []
"""

from unittest.mock import patch

import pytest

from services.jd_assessor import load_matt_profile
from services.rag_service import semantic_search

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_STORY_A = {
    "id": "story-a|jpmc",
    "Title": "Payments Platform",
    "Client": "JPMC",
    "Industry": "Banking",
    "Solution / Offering": "Platform Engineering",
    "5PSummary": "Transformed global payments infrastructure",
}

_STORY_B = {
    "id": "story-b|capital-one",
    "Title": "Agile Transformation",
    "Client": "Capital One",
    "Industry": "Banking",
    "Solution / Offering": "Agile Coaching",
    "5PSummary": "Led agile transformation across 150+ person org",
}


@pytest.fixture
def stories():
    return [_STORY_A, _STORY_B]


@pytest.fixture
def high_confidence_hits():
    return [
        {"story": _STORY_A, "pc_score": 0.85, "snippet": "hit A"},
        {"story": _STORY_B, "pc_score": 0.72, "snippet": "hit B"},
    ]


@pytest.fixture
def low_confidence_hits():
    """All hits below CONFIDENCE_LOW (0.20). Triggers the confidence=none
    branch inside semantic_search."""
    return [
        {"story": _STORY_A, "pc_score": 0.10, "snippet": "hit A"},
        {"story": _STORY_B, "pc_score": 0.08, "snippet": "hit B"},
    ]


def _empty_filters() -> dict:
    return {
        "industry": "",
        "capability": "",
        "era": "",
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
    }


def _assert_profile_facts_equals_loader(result: dict, path_label: str) -> None:
    """profile_facts must equal load_matt_profile() output. Empty string,
    None, or a placeholder all fail."""
    expected = load_matt_profile()
    pf = result.get("profile_facts")
    assert pf == expected, (
        f"profile_facts on {path_label} must equal load_matt_profile() "
        f"output. got: {pf!r}. expected: {expected!r}"
    )


# ---------------------------------------------------------------------------
# Class A: every return path
# ---------------------------------------------------------------------------


class TestSemanticSearchReturnsProfileFacts:
    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_empty_query_return_includes_profile_facts(self, mock_st, mock_pc, stories):
        mock_st.session_state = {}
        result = semantic_search(query="", filters=_empty_filters(), stories=stories)
        assert result["results"] == [] and result["top_score"] == 0.0, (
            f"expected empty-query path marker (results==[] AND top_score==0.0); "
            f"got results={result['results']!r} top_score={result['top_score']!r}"
        )
        _assert_profile_facts_equals_loader(result, "empty-query path")

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_pinecone_unavailable_overlap_rejected_return_includes_profile_facts(
        self, mock_st, mock_pc, stories
    ):
        mock_st.session_state = {}
        mock_pc.return_value = None
        result = semantic_search(
            query="xyz nonsense",
            filters=_empty_filters(),
            stories=stories,
            enforce_overlap=True,
            min_overlap=0.5,
        )
        assert (
            result.get("reason") == "fallback:pinecone_unavailable"
            and result["results"] == []
        ), (
            f"expected pinecone-unavailable + overlap-rejected marker; "
            f"got reason={result.get('reason')!r} results={result['results']!r}"
        )
        _assert_profile_facts_equals_loader(
            result, "pinecone-unavailable + overlap-rejected path"
        )

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_pinecone_unavailable_local_fallback_return_includes_profile_facts(
        self, mock_st, mock_pc, stories
    ):
        mock_st.session_state = {}
        mock_pc.return_value = None
        result = semantic_search(
            query="payments",
            filters=_empty_filters(),
            stories=stories,
            enforce_overlap=False,
        )
        assert (
            result.get("reason") == "fallback:pinecone_unavailable"
            and result["results"] != []
        ), (
            f"expected pinecone-unavailable + local-fallback marker "
            f"(reason set AND results non-empty from local keyword match); "
            f"got reason={result.get('reason')!r} results={result['results']!r}"
        )
        _assert_profile_facts_equals_loader(
            result, "pinecone-unavailable + local-fallback path"
        )

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_no_confident_hits_return_includes_profile_facts(
        self, mock_st, mock_pc, stories, low_confidence_hits
    ):
        mock_st.session_state = {}
        mock_pc.return_value = low_confidence_hits
        result = semantic_search(
            query="anything",
            filters=_empty_filters(),
            stories=stories,
        )
        assert result["confidence"] == "none" and result["top_score"] > 0, (
            f"expected no-confident-hits marker (confidence=='none' AND "
            f"top_score>0, distinguishing from empty-query path); got "
            f"confidence={result['confidence']!r} top_score={result['top_score']!r}"
        )
        _assert_profile_facts_equals_loader(result, "no-confident-hits path")

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_filters_blocked_all_return_includes_profile_facts(
        self, mock_st, mock_pc, stories, high_confidence_hits
    ):
        mock_st.session_state = {}
        mock_pc.return_value = high_confidence_hits
        filters = _empty_filters()
        filters["industry"] = "Retail"  # no story matches Retail
        result = semantic_search(
            query="leadership",
            filters=filters,
            stories=stories,
        )
        assert "relaxed_count" in result and result["results"] == [], (
            f"expected filters-blocked-all marker (relaxed_count key present "
            f"AND results==[]); got keys={sorted(result.keys())} "
            f"results={result['results']!r}"
        )
        _assert_profile_facts_equals_loader(result, "filters-blocked-all path")

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_happy_path_return_includes_profile_facts(
        self, mock_st, mock_pc, stories, high_confidence_hits
    ):
        mock_st.session_state = {}
        mock_pc.return_value = high_confidence_hits
        result = semantic_search(
            query="payments",
            filters=_empty_filters(),
            stories=stories,
        )
        assert result["confidence"] == "high" and result["results"] != [], (
            f"expected happy-path marker (confidence=='high' AND results non-empty); "
            f"got confidence={result['confidence']!r} results={result['results']!r}"
        )
        _assert_profile_facts_equals_loader(result, "happy path")


# ---------------------------------------------------------------------------
# Class B: separation guard
# ---------------------------------------------------------------------------


class TestReturnShapeSeparation:
    """B1 is a change test (fails on Red because profile_facts key absent).
    B2 is a regression guard: passes on Red by design because results is
    already pure stories today; continues to pass on Green as long as Green
    keeps profile_facts out of results. Guards against a future edit that
    accidentally mixes them."""

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_profile_facts_is_top_level_key_not_inside_results(
        self, mock_st, mock_pc, stories, high_confidence_hits
    ):
        """Reuses Class A's happy-path setup so this doesn't test its own
        mock -- runs real semantic_search with pinecone mocked, then asserts
        profile_facts is at top level AND no element of results contains
        the profile-facts value or shape."""
        mock_st.session_state = {}
        mock_pc.return_value = high_confidence_hits
        result = semantic_search(
            query="payments",
            filters=_empty_filters(),
            stories=stories,
        )
        assert "profile_facts" in result, (
            f"profile_facts must be a top-level key; got keys "
            f"{sorted(result.keys())}"
        )
        pf_value = result["profile_facts"]
        for item in result["results"]:
            assert item.get("Title"), (
                f"results contains an item without Title -- profile_facts "
                f"was likely mixed into results. Item keys: "
                f"{sorted(item.keys())}"
            )
            # Also assert no story item accidentally holds the profile_facts
            # value (would happen if Green stored profile_facts inside each
            # story dict).
            for k, v in item.items():
                assert v != pf_value, (
                    f"story item {item.get('id')!r} field {k!r} holds the "
                    f"profile_facts value -- payload leaked into results"
                )

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_my_work_view_iteration_stays_pure_stories(
        self, mock_st, mock_pc, stories, high_confidence_hits
    ):
        """My Work reads view = search_result['results'] and iterates story
        rows. Regression guard -- passes on Red because current results is
        pure stories; guards Green from a future edit that mixes
        profile_facts into results."""
        mock_st.session_state = {}
        mock_pc.return_value = high_confidence_hits
        result = semantic_search(
            query="payments",
            filters=_empty_filters(),
            stories=stories,
        )
        view = result["results"]  # My Work's exact unpacking
        for item in view:
            assert item.get("Title"), (
                f"view row missing Title; profile_facts leaked into results. "
                f"Row keys: {sorted(item.keys())}"
            )
            assert item.get("id"), (
                f"view row missing id; profile_facts leaked into results. "
                f"Row keys: {sorted(item.keys())}"
            )
