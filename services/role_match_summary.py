"""
Summary block helpers for Role Match: MATTGPT-067 + MATTGPT-248.

Pure-logic, no Streamlit import. Called from role_match.py (panel render and
_build_export_html) and unit tests (test_summary_block.py).

MATTGPT-248: `unassessed` joins strong/partial/gap as a first-class status
for partial-failure handling. Row shape has `match_status="unassessed"`,
`category` + `requirement` populated from the source requirement dict,
empty `evidence` and `gap_explanation`. Any row whose `match_status` is
not one of strong/partial/gap (unknown value, missing key, empty string)
coerces to `unassessed` at the count layer so the count line and the
badges never disagree; render sites do the same coercion so the two
layers stay word-identical.

The same principle applies on the category axis: a row with an
unrecognized category coerces to `required` with a logged warning,
rather than being silently dropped from the counts. Silent drops would
reproduce the exact defect this ticket exists to remove, one axis over.
Renderer splits in role_match.py apply the identical coercion so the
count and rendered rows agree on both axes.
"""

import logging

logger = logging.getLogger(__name__)

_MAX_DISCUSSION_POINTS = 5
_TEXT_TRUNCATE_LEN = 80
_ZERO_CASE_TEXT = "No items to flag -- strong match across all requirements."

# Statuses `compute_summary_counts` knows how to tally directly. Anything
# else coerces to "unassessed". Kept as a tuple so the coercion logic
# and the count-dict initialization stay pinned to the same set.
_ASSESSED_STATUSES = ("strong", "partial", "gap")

# Maps (category, match_status) → human-readable label shown next to each point.
# Only combinations included here surface in discussion points; everything else
# is excluded (required/preferred strong, preferred partial, and every
# unassessed row -- unassessed rows don't get a discussion point because
# there's nothing to discuss about a requirement that wasn't evaluated;
# the incomplete notice above the summary block carries that signal).
_LABEL_MAP = {
    ("required", "gap"): "Required, Gap",
    ("required", "partial"): "Required, Partial",
    ("preferred", "gap"): "Preferred, Gap",
}

_SORT_ORDER = {
    "Required, Gap": 0,
    "Required, Partial": 1,
    "Preferred, Gap": 2,
}


def compute_summary_counts(results: list[dict]) -> dict:
    """Tally strong/partial/gap/unassessed counts per category.

    Args:
        results: List of requirement dicts from services.jd_assessor.run_assessment,
                 each with "category" ("required"/"preferred") and
                 "match_status" ("strong"/"partial"/"gap"/"unassessed").

    Returns:
        {
            "required": {"strong": N, "partial": N, "gap": N, "unassessed": N},
            "preferred": {"strong": N, "partial": N, "gap": N, "unassessed": N},
        }
        All eight keys are always present (zero if no occurrences).

    MATTGPT-248: Coerces malformed rows on both axes rather than
    silently dropping them. A row whose match_status is not in
    _ASSESSED_STATUSES coerces to "unassessed"; a row whose category
    is not "required" or "preferred" coerces to "required" and logs
    a warning naming the offending value. Silent drops would make
    the count line disagree with the number of rendered rows, which
    is the defect this ticket exists to remove.
    """
    counts: dict = {
        "required": {"strong": 0, "partial": 0, "gap": 0, "unassessed": 0},
        "preferred": {"strong": 0, "partial": 0, "gap": 0, "unassessed": 0},
    }
    for r in results:
        cat = r.get("category", "")
        if cat not in counts:
            logger.warning(
                "role_match_summary malformed row: category %r not in "
                "required/preferred; coercing to 'required'. Requirement: %r",
                cat,
                (r.get("requirement") or "")[:60],
            )
            cat = "required"
        status = r.get("match_status", "")
        if status not in _ASSESSED_STATUSES:
            status = "unassessed"
        counts[cat][status] += 1
    return counts


def build_discussion_points(results: list[dict]) -> list[dict]:
    """Build ordered discussion point list for the summary block.

    Inclusion rules:
    - Required gaps → included, label "Required, Gap"
    - Required partials → included, label "Required, Partial"
    - Preferred gaps → included, label "Preferred, Gap"
    - Preferred partials → EXCLUDED
    - Required/preferred strongs → EXCLUDED

    Ordering: Required, Gap → Required, Partial → Preferred, Gap.
    Cap: 5 visible items; overflow indicator appended when more exist.
    Zero case: single item with is_zero_case=True when nothing to flag.
    Truncation: requirement text clipped to 80 chars + "..." if longer.

    Returns:
        List of dicts, each with:
        {
            "text": str,
            "label_type": str,          # e.g. "Required, Gap" — empty for zero-case/overflow
            "is_overflow_indicator": bool,
            "is_zero_case": bool,
        }
    """
    included = []
    for r in results:
        cat = r.get("category", "")
        status = r.get("match_status", "")
        label_type = _LABEL_MAP.get((cat, status))
        if label_type is None:
            continue
        req_text = r.get("requirement", "")
        if len(req_text) > _TEXT_TRUNCATE_LEN:
            req_text = req_text[:_TEXT_TRUNCATE_LEN] + "..."
        included.append(
            {
                "text": req_text,
                "label_type": label_type,
                "is_overflow_indicator": False,
                "is_zero_case": False,
            }
        )

    included.sort(key=lambda p: _SORT_ORDER.get(p["label_type"], 99))

    if not included:
        # MATTGPT-248 branch 4: when no gap/partial items exist to
        # discuss AND any row is unassessed-like (match_status not one
        # of the assessed statuses -- includes explicit "unassessed",
        # unknown values, missing keys), suppress the zero-case
        # "strong match across all requirements" claim by returning [].
        # The incomplete notice above the summary block carries the
        # visible signal.
        if any(r.get("match_status") not in _ASSESSED_STATUSES for r in results):
            return []
        return [
            {
                "text": _ZERO_CASE_TEXT,
                "label_type": "",
                "is_overflow_indicator": False,
                "is_zero_case": True,
            }
        ]

    if len(included) > _MAX_DISCUSSION_POINTS:
        overflow_count = len(included) - _MAX_DISCUSSION_POINTS
        visible = included[:_MAX_DISCUSSION_POINTS]
        visible.append(
            {
                "text": f"and {overflow_count} more below",
                "label_type": "",
                "is_overflow_indicator": True,
                "is_zero_case": False,
            }
        )
        return visible

    return included
