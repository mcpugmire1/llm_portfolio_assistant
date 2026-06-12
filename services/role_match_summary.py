"""
Summary block helpers for Role Match — MATTGPT-067.

Pure-logic, no Streamlit import. Called from role_match.py (panel render and
_build_export_html) and unit tests (test_summary_block.py).
"""

_MAX_DISCUSSION_POINTS = 5
_TEXT_TRUNCATE_LEN = 80
_ZERO_CASE_TEXT = "No items to flag -- strong match across all requirements."

# Maps (category, match_status) → human-readable label shown next to each point.
# Only combinations included here surface in discussion points; everything else
# is excluded (required/preferred strong, preferred partial).
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
    """Tally strong/partial/gap counts per category.

    Args:
        results: List of requirement dicts from services.jd_assessor.run_assessment,
                 each with "category" ("required"/"preferred") and
                 "match_status" ("strong"/"partial"/"gap").

    Returns:
        {
            "required": {"strong": N, "partial": N, "gap": N},
            "preferred": {"strong": N, "partial": N, "gap": N},
        }
        All six keys are always present (zero if no occurrences).
    """
    counts: dict = {
        "required": {"strong": 0, "partial": 0, "gap": 0},
        "preferred": {"strong": 0, "partial": 0, "gap": 0},
    }
    for r in results:
        cat = r.get("category", "")
        status = r.get("match_status", "")
        if cat in counts and status in counts[cat]:
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
