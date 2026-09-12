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
# MATTGPT-248 Cycle 1: 8-key contract + four-branch discussion points
# ---------------------------------------------------------------------------
# compute_summary_counts shifts from 6 keys to 8 -- adds `unassessed` under
# each of `required` and `preferred`. The pre-existing
# `if cat in counts and status in counts[cat]` guard silently dropped rows
# whose match_status wasn't strong/partial/gap; under -248 those rows are
# counted into the new keys instead.


class TestComputeSummaryCountsUnassessedKeys:
    """MATTGPT-248: `unassessed` key appears under both required and
    preferred so partial-failure rows are counted rather than silently
    dropped. Total keys 6 -> 8; nothing else added."""

    def test_unassessed_key_present_under_required(self):
        counts = compute_summary_counts([])
        assert "unassessed" in counts["required"], (
            f"missing counts['required']['unassessed']; keys are "
            f"{sorted(counts['required'].keys())}"
        )

    def test_unassessed_key_present_under_preferred(self):
        counts = compute_summary_counts([])
        assert "unassessed" in counts["preferred"], (
            f"missing counts['preferred']['unassessed']; keys are "
            f"{sorted(counts['preferred'].keys())}"
        )

    def test_unassessed_key_zero_when_no_unassessed_rows(self):
        """Uses `.get(..., 0)` so this test fails on assertion if the key
        is missing rather than on KeyError."""
        results = [_req("required", "strong"), _req("preferred", "strong")]
        counts = compute_summary_counts(results)
        assert counts["required"].get("unassessed", 0) == 0
        assert counts["preferred"].get("unassessed", 0) == 0

    def test_unassessed_required_counted(self):
        results = [
            _req("required", "unassessed"),
            _req("required", "unassessed"),
            _req("required", "strong"),
        ]
        counts = compute_summary_counts(results)
        assert counts["required"].get("unassessed", 0) == 2

    def test_unassessed_preferred_counted(self):
        results = [
            _req("preferred", "unassessed"),
            _req("preferred", "gap"),
        ]
        counts = compute_summary_counts(results)
        assert counts["preferred"].get("unassessed", 0) == 1

    def test_exactly_eight_keys_present(self):
        """Contract is 6 -> 8, not 6 -> 8+. Nothing else added under
        either category."""
        counts = compute_summary_counts([])
        for cat in ("required", "preferred"):
            assert len(counts[cat]) == 4, (
                f"expected exactly 4 keys under {cat!r}; got "
                f"{sorted(counts[cat].keys())}"
            )
            for status in ("strong", "partial", "gap", "unassessed"):
                assert status in counts[cat], (
                    f"missing counts[{cat!r}][{status!r}]; keys are "
                    f"{sorted(counts[cat].keys())}"
                )

    def test_existing_status_counts_unaffected_by_unassessed_rows(self):
        """Adding unassessed rows must not perturb strong/partial/gap tallies."""
        results = [
            _req("required", "strong"),
            _req("required", "gap"),
            _req("required", "unassessed"),
        ]
        counts = compute_summary_counts(results)
        assert counts["required"]["strong"] == 1
        assert counts["required"]["gap"] == 1

    def test_unknown_match_status_counted_as_unassessed(self):
        """MATTGPT-248: any match_status not in strong/partial/gap
        coerces to unassessed for counting. Matches the render-time
        coercion so N in the notice always equals the number of
        unassessed-badged rows."""
        results = [
            _req("required", "not-a-real-status"),
            _req("required", "banana"),
        ]
        counts = compute_summary_counts(results)
        assert counts["required"].get("unassessed", 0) == 2, (
            f"expected unknown statuses to count as unassessed; got "
            f"counts['required']={counts['required']!r}"
        )

    def test_missing_match_status_counted_as_unassessed(self):
        """MATTGPT-248: a row lacking a match_status key entirely also
        coerces to unassessed for counting."""
        results = [
            {
                "category": "required",
                "requirement": "Some req",
                "evidence": [],
                "gap_explanation": "",
                "confidence": "",
            },
        ]
        counts = compute_summary_counts(results)
        assert counts["required"].get("unassessed", 0) == 1, (
            f"expected missing match_status to count as unassessed; got "
            f"counts['required']={counts['required']!r}"
        )

    def test_unknown_category_coerces_to_required(self):
        """MATTGPT-248: a row with an unrecognized category coerces to
        'required' rather than being silently dropped. Silent drops
        would make the count line disagree with the number of rendered
        rows -- the same defect as the status-axis coercion, one axis
        over. Renderer splits in role_match.py apply the identical
        coercion so count and render agree."""
        results = [
            {
                "category": "not-a-category",
                "match_status": "gap",
                "requirement": "Test",
                "evidence": [],
                "gap_explanation": "",
                "confidence": "",
            },
        ]
        counts = compute_summary_counts(results)
        assert counts["required"]["gap"] == 1, (
            f"expected unknown-category row to coerce to required; got "
            f"counts['required']={counts['required']!r}"
        )
        assert counts["preferred"]["gap"] == 0, (
            f"coerced row must not also count under preferred; got "
            f"counts['preferred']={counts['preferred']!r}"
        )

    def test_unknown_category_logs_warning_naming_bad_value(self, caplog):
        """MATTGPT-248: coercion logs a warning that names the offending
        category value so the producer bug remains diagnosable in the
        log even though the row still counts and still renders."""
        import logging

        results = [
            {
                "category": "not-a-category",
                "match_status": "gap",
                "requirement": "Some req",
                "evidence": [],
                "gap_explanation": "",
                "confidence": "",
            },
        ]
        with caplog.at_level(logging.WARNING, logger="services.role_match_summary"):
            compute_summary_counts(results)
        matching = [r for r in caplog.records if "not-a-category" in r.message]
        assert matching, (
            f"expected warning naming bad category value 'not-a-category'; "
            f"got {[r.message for r in caplog.records]!r}"
        )


# build_discussion_points four-branch contract explicitly.
# Branch matrix on (any rows hit _LABEL_MAP, any unassessed rows present):
#   1. (yes, no)  -> return items normally (existing)
#   2. (yes, yes) -> return items normally; incomplete notice is a
#                    separate renderer concern above the summary block
#   3. (no,  no)  -> zero-case single-item list (existing)
#   4. (no,  yes) -> return []; renderers omit the section entirely so
#                    the page cannot claim "strong match across all
#                    requirements" over rows nobody assessed


class TestDiscussionPointsFourBranchesWithUnassessed:
    """MATTGPT-248: explicit coverage of all four contract branches."""

    def test_branch_1_gaps_no_unassessed_returns_items(self):
        """(hits _LABEL_MAP, no unassessed) -> items returned normally.

        Both fixture rows are in _LABEL_MAP: required+gap and
        required+partial. `preferred + partial` is deliberately excluded
        per TestDiscussionPointsInclusionRules.test_preferred_partial_excluded
        at line 120 in this file, so it does not appear in fixture rows
        used to assert visible-count."""
        results = [
            _req("required", "gap", "Kubernetes"),
            _req("required", "partial", "SaaS at scale"),
        ]
        points = build_discussion_points(results)
        assert not any(p.get("is_zero_case") for p in points)
        visible = [
            p
            for p in points
            if not p.get("is_zero_case") and not p.get("is_overflow_indicator")
        ]
        assert len(visible) == 2

    def test_branch_2_gaps_with_unassessed_returns_gap_partial_only(self):
        """(hits _LABEL_MAP, unassessed present) -> gap/partial items
        returned normally; unassessed excluded (not in _LABEL_MAP); no
        notice item injected into the list. This is the guard's inner
        placement -- the branch-4 empty-list return is inside
        `if not included`, so rows that hit _LABEL_MAP take the normal
        return path regardless of unassessed presence.

        Fixture uses required+gap and required+partial (both in
        _LABEL_MAP); `preferred + partial` is deliberately excluded per
        the existing test_preferred_partial_excluded pin."""
        results = [
            _req("required", "gap", "Kubernetes"),
            _req("required", "unassessed", "Budget P&L"),
            _req("required", "partial", "SaaS at scale"),
        ]
        points = build_discussion_points(results)
        visible = [
            p
            for p in points
            if not p.get("is_zero_case") and not p.get("is_overflow_indicator")
        ]
        assert len(visible) == 2, (
            f"expected 2 items (gap + partial), got {len(visible)}: "
            f"{[p['text'] for p in visible]!r}"
        )
        texts = " ".join(p["text"] for p in visible)
        assert "Kubernetes" in texts
        assert "SaaS" in texts
        assert (
            "Budget P&L" not in texts
        ), "unassessed row must not appear as a discussion point"

    def test_branch_2_overflow_excludes_unassessed_before_cap(self):
        """Six gap rows + two unassessed, cap = 5. Overflow indicator
        reads 'and 1 more' (6 - 5), not 'and 3 more' (8 - 5). Unassessed
        must be excluded from the visible list BEFORE the cap is applied,
        not counted into the total then subtracted."""
        results = [_req("required", "gap", f"Gap {i}") for i in range(6)]
        results.extend(
            [
                _req("required", "unassessed", "Unassessed row A"),
                _req("required", "unassessed", "Unassessed row B"),
            ]
        )
        points = build_discussion_points(results)
        overflow = [p for p in points if p.get("is_overflow_indicator")]
        assert (
            len(overflow) == 1
        ), f"expected exactly one overflow indicator, got {len(overflow)}"
        assert "1 more" in overflow[0]["text"], (
            f"expected 'and 1 more' (6 gaps - 5 cap), got "
            f"{overflow[0]['text']!r}. Unassessed rows counted into the "
            f"overflow total instead of being excluded before the cap."
        )
        # And guard against the specific wrong number that surfaces when
        # unassessed rows leak into the cap arithmetic.
        assert "3 more" not in overflow[0]["text"], (
            f"overflow text reads '3 more', which means unassessed rows "
            f"were included in the pre-cap total (8 rows - 5 cap): "
            f"{overflow[0]['text']!r}"
        )

    def test_branch_3_all_strong_no_unassessed_returns_zero_case(self):
        """(no _LABEL_MAP hits, no unassessed) -> zero-case single item."""
        results = [_req("required", "strong"), _req("preferred", "strong")]
        points = build_discussion_points(results)
        assert len(points) == 1
        assert points[0].get("is_zero_case") is True

    def test_branch_4_all_unassessed_returns_empty_list(self):
        """(no _LABEL_MAP hits, unassessed present) -> return []. Renderer
        omits the section entirely; the incomplete notice above the
        summary carries the visible signal instead."""
        results = [
            _req("required", "unassessed"),
            _req("required", "unassessed"),
            _req("preferred", "unassessed"),
        ]
        points = build_discussion_points(results)
        assert points == [], (
            f"expected [] on all-unassessed; got {points!r} "
            f"(zero-case fired incorrectly -- guard missing)"
        )

    def test_branch_4_strongs_plus_unassessed_returns_empty_list(self):
        """(no _LABEL_MAP hits, unassessed present) -> return [] even
        when some strongs are present. 'Strong match across all
        requirements' would be dishonest with unassessed rows mixed in."""
        results = [
            _req("required", "strong"),
            _req("required", "strong"),
            _req("required", "unassessed"),
        ]
        points = build_discussion_points(results)
        assert points == [], (
            f"expected [] when unassessed present without gap/partial; "
            f"got {points!r}"
        )


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
