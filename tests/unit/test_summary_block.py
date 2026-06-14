"""
Unit tests for summary block helpers — MATTGPT-067.

Tests pure-logic functions in services/role_match_summary.py:
  - compute_summary_counts: strong/partial/gap tallies per section
  - build_discussion_points: inclusion rules, ordering, cap, zero case, truncation

Also tests that _build_export_html() (role_match.py) includes the summary
block above the requirements section.

Red state: all tests fail with ModuleNotFoundError until
services/role_match_summary.py is created in the Green phase.
"""

import pytest

from services.role_match_summary import build_discussion_points, compute_summary_counts

# ---------------------------------------------------------------------------
# Shared fixture factory
# ---------------------------------------------------------------------------


def _req(category: str, match_status: str, text: str = "Some requirement") -> dict:
    return {
        "category": category,
        "requirement": text,
        "match_status": match_status,
        "evidence": [],
        "gap_explanation": f"Note: missing {text[:20]}"
        if match_status != "strong"
        else "",
        "confidence": "medium",
    }


# ---------------------------------------------------------------------------
# compute_summary_counts
# ---------------------------------------------------------------------------


class TestComputeSummaryCounts:
    def test_required_counts(self):
        results = [
            _req("required", "strong"),
            _req("required", "partial"),
            _req("required", "gap"),
            _req("required", "gap"),
        ]
        counts = compute_summary_counts(results)
        assert counts["required"]["strong"] == 1
        assert counts["required"]["partial"] == 1
        assert counts["required"]["gap"] == 2

    def test_preferred_counts(self):
        results = [
            _req("preferred", "strong"),
            _req("preferred", "partial"),
            _req("preferred", "gap"),
        ]
        counts = compute_summary_counts(results)
        assert counts["preferred"]["strong"] == 1
        assert counts["preferred"]["partial"] == 1
        assert counts["preferred"]["gap"] == 1

    def test_mixed_required_and_preferred(self):
        results = [
            _req("required", "strong"),
            _req("required", "gap"),
            _req("preferred", "partial"),
        ]
        counts = compute_summary_counts(results)
        assert counts["required"]["strong"] == 1
        assert counts["required"]["gap"] == 1
        assert counts["preferred"]["partial"] == 1
        assert counts["preferred"]["strong"] == 0

    def test_empty_results_returns_zero_counts(self):
        counts = compute_summary_counts([])
        assert counts["required"]["strong"] == 0
        assert counts["required"]["partial"] == 0
        assert counts["required"]["gap"] == 0
        assert counts["preferred"]["strong"] == 0

    def test_zero_count_keys_always_present(self):
        results = [_req("required", "strong")]
        counts = compute_summary_counts(results)
        assert "partial" in counts["required"]
        assert "gap" in counts["required"]
        assert "strong" in counts["preferred"]


# ---------------------------------------------------------------------------
# build_discussion_points — inclusion rules
# ---------------------------------------------------------------------------


class TestDiscussionPointsInclusionRules:
    def test_required_gap_included(self):
        results = [_req("required", "gap", "Budget P&L accountability")]
        points = build_discussion_points(results)
        assert any(
            "Budget P&L" in p["text"] for p in points if not p.get("is_zero_case")
        )

    def test_required_partial_included(self):
        results = [_req("required", "partial", "Kubernetes at production scale")]
        points = build_discussion_points(results)
        assert any(
            "Kubernetes" in p["text"] for p in points if not p.get("is_zero_case")
        )

    def test_preferred_gap_included(self):
        results = [_req("preferred", "gap", "Hands-on Kubernetes experience")]
        points = build_discussion_points(results)
        assert any(
            "Kubernetes" in p["text"] for p in points if not p.get("is_zero_case")
        )

    def test_preferred_partial_excluded(self):
        results = [_req("preferred", "partial", "SaaS product background")]
        points = build_discussion_points(results)
        visible = [
            p
            for p in points
            if not p.get("is_zero_case") and not p.get("is_overflow_indicator")
        ]
        assert (
            len(visible) == 0
        ), "Preferred partials must NOT appear in discussion points"

    def test_required_strong_excluded(self):
        results = [_req("required", "strong", "Engineering leadership 10+ years")]
        points = build_discussion_points(results)
        visible = [
            p
            for p in points
            if not p.get("is_zero_case") and not p.get("is_overflow_indicator")
        ]
        assert len(visible) == 0

    def test_preferred_strong_excluded(self):
        results = [_req("preferred", "strong", "Graduate degree technical field")]
        points = build_discussion_points(results)
        visible = [
            p
            for p in points
            if not p.get("is_zero_case") and not p.get("is_overflow_indicator")
        ]
        assert len(visible) == 0

    def test_label_type_on_each_point(self):
        results = [
            _req("required", "gap", "P&L ownership"),
            _req("required", "partial", "Kubernetes"),
            _req("preferred", "gap", "SaaS background"),
        ]
        points = build_discussion_points(results)
        label_types = {p["label_type"] for p in points if not p.get("is_zero_case")}
        assert "Required, Gap" in label_types
        assert "Required, Partial" in label_types
        assert "Preferred, Gap" in label_types


# ---------------------------------------------------------------------------
# build_discussion_points — ordering
# ---------------------------------------------------------------------------


class TestDiscussionPointsOrdering:
    def test_required_gaps_before_required_partials(self):
        results = [
            _req("required", "partial", "Kubernetes at scale"),
            _req("required", "gap", "Budget P&L"),
        ]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        types = [p["label_type"] for p in points]
        assert types.index("Required, Gap") < types.index("Required, Partial")

    def test_required_partials_before_preferred_gaps(self):
        results = [
            _req("preferred", "gap", "Kubernetes hands-on"),
            _req("required", "partial", "Kubernetes at scale"),
        ]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        types = [p["label_type"] for p in points]
        assert types.index("Required, Partial") < types.index("Preferred, Gap")

    def test_full_ordering_all_three_present(self):
        results = [
            _req("preferred", "gap", "Preferred gap item"),
            _req("required", "partial", "Required partial item"),
            _req("required", "gap", "Required gap item"),
        ]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        types = [p["label_type"] for p in points]
        assert types == ["Required, Gap", "Required, Partial", "Preferred, Gap"]


# ---------------------------------------------------------------------------
# build_discussion_points — cap at 5
# ---------------------------------------------------------------------------


class TestDiscussionPointsCap:
    def test_capped_at_5_visible_items(self):
        results = [_req("required", "gap", f"Requirement {i}") for i in range(8)]
        points = build_discussion_points(results)
        visible = [
            p
            for p in points
            if not p.get("is_overflow_indicator") and not p.get("is_zero_case")
        ]
        assert len(visible) == 5

    def test_overflow_indicator_when_more_than_5(self):
        results = [_req("required", "gap", f"Requirement {i}") for i in range(8)]
        points = build_discussion_points(results)
        overflow = [p for p in points if p.get("is_overflow_indicator")]
        assert len(overflow) == 1

    def test_overflow_text_includes_count(self):
        results = [_req("required", "gap", f"Requirement {i}") for i in range(8)]
        points = build_discussion_points(results)
        overflow = [p for p in points if p.get("is_overflow_indicator")]
        assert "3 more below" in overflow[0]["text"]

    def test_no_overflow_when_exactly_5(self):
        results = [_req("required", "gap", f"Requirement {i}") for i in range(5)]
        points = build_discussion_points(results)
        overflow = [p for p in points if p.get("is_overflow_indicator")]
        assert len(overflow) == 0

    def test_no_overflow_when_fewer_than_5(self):
        results = [_req("required", "gap", f"Requirement {i}") for i in range(3)]
        points = build_discussion_points(results)
        overflow = [p for p in points if p.get("is_overflow_indicator")]
        assert len(overflow) == 0


# ---------------------------------------------------------------------------
# build_discussion_points — zero case
# ---------------------------------------------------------------------------


class TestDiscussionPointsZeroCase:
    def test_empty_results_returns_no_items_message(self):
        points = build_discussion_points([])
        assert len(points) == 1
        assert points[0].get("is_zero_case") is True
        assert (
            points[0]["text"]
            == "No items to flag -- strong match across all requirements."
        )

    def test_all_strong_returns_no_items_message(self):
        results = [
            _req("required", "strong"),
            _req("preferred", "strong"),
        ]
        points = build_discussion_points(results)
        assert len(points) == 1
        assert "No items to flag" in points[0]["text"]

    def test_only_preferred_partials_returns_no_items_message(self):
        results = [_req("preferred", "partial", "SaaS background")]
        points = build_discussion_points(results)
        assert len(points) == 1
        assert points[0].get("is_zero_case") is True


# ---------------------------------------------------------------------------
# build_discussion_points — 80-char truncation
# ---------------------------------------------------------------------------


class TestDiscussionPointsTruncation:
    def test_long_requirement_truncated(self):
        long_text = "A" * 90
        results = [_req("required", "gap", long_text)]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        assert "..." in points[0]["text"]

    def test_short_requirement_not_truncated(self):
        short_text = "Short requirement"
        results = [_req("required", "gap", short_text)]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        assert "..." not in points[0]["text"]

    def test_truncation_boundary_at_80_chars(self):
        text_80 = "B" * 80
        results = [_req("required", "gap", text_80)]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        assert "..." not in points[0]["text"]

    def test_truncation_one_over_boundary(self):
        text_81 = "C" * 81
        results = [_req("required", "gap", text_81)]
        points = [
            p for p in build_discussion_points(results) if not p.get("is_zero_case")
        ]
        assert "..." in points[0]["text"]


# ---------------------------------------------------------------------------
# _build_export_html — summary block included
# ---------------------------------------------------------------------------
# These tests validate that _build_export_html() includes the summary block
# (counts + discussion points) above the requirements section.
# Red state: import succeeds but the summary content assertions fail until
# Green phase adds the summary block to the export function.


class TestBuildExportHtmlSummary:
    @pytest.fixture
    def result_payload(self):
        return {
            "extraction": {
                "role_title": "Senior Engineering Leader",
                "company": "Acme Corp",
            },
            "results": [
                _req("required", "strong", "Engineering leadership 10+ years"),
                _req("required", "gap", "Budget P&L accountability"),
                _req("preferred", "partial", "SaaS background"),
            ],
        }

    def test_summary_section_present_in_export(self, result_payload):
        from ui.pages.role_match import _build_export_html

        html_out = _build_export_html(result_payload)
        assert "SUMMARY" in html_out, "Export HTML must include SUMMARY section"

    def test_export_summary_before_requirements(self, result_payload):
        from ui.pages.role_match import _build_export_html

        html_out = _build_export_html(result_payload)
        summary_pos = html_out.find("SUMMARY")
        req_pos = html_out.find("Required Qualifications")
        assert (
            summary_pos < req_pos
        ), "Summary must appear before requirements in export HTML"

    def test_export_includes_discussion_points(self, result_payload):
        from ui.pages.role_match import _build_export_html

        html_out = _build_export_html(result_payload)
        assert "Discussion points" in html_out or "No items to flag" in html_out
