"""MATTGPT-247: wiring tests between the role_match failure/success paths
and services.query_logger.

Distinct from tests/unit/test_query_logger.py, which pins the log
function contracts. This file pins that role_match.py's handlers
actually invoke those log functions and forward the correct kwargs.

Patch-target caveat (applies to every test here):

    patch.object(role_match, "log_role_match_assessment", ...)

pins the module-scope binding in role_match's namespace. The Red for
this ticket adds `from services.query_logger import is_bot,
log_role_match_assessment` at role_match.py's module top so these
patches bind today. If a caller inside role_match.py re-imports
`is_bot` or `log_role_match_assessment` locally (e.g., delayed
`from services.query_logger import ...` inside the function body),
that local name shadows the module-scope binding for the duration
of the call and this patch does not affect it.

Green for -247 must:

  1. Use the module-scope names in both `_log_role_match_success` and
     `_handle_assessment_error` -- no delayed imports inside those
     two functions.
  2. Remove the redundant delayed import at role_match.py:2308 (the
     old success-path block). Line 562 (chip-click path) stays as-is;
     these tests do not cover that call site.

Until (2) lands, `_log_role_match_success` could be implemented with
a local re-import and this test would silently pass while covering
nothing -- same class of failure the module docstring in
test_query_logger.py warns about, arriving from the other direction.
"""

from unittest.mock import patch


class TestFailureHandlerCallsLogger:
    """MATTGPT-247: `_handle_assessment_error` (called from role_match.py's
    outer `except Exception` when run_assessment propagates a Mode 4
    retrieval-raised exception out of the fan-out) must write a Sheet
    row with Failure Type `retrieval_failed`. Sits outside the
    assessment try/except (same as the success write), so a logging
    failure can't interfere with the assessment result -- the invariant
    the success-path comment at role_match.py:2268-2270 already
    establishes."""

    def test_handle_assessment_error_calls_log_role_match_assessment_with_retrieval_failed(
        self,
    ):
        """Test 9. Drive `_handle_assessment_error` with a simulated
        RuntimeError, assert `log_role_match_assessment` was called
        exactly once with `failure_type="retrieval_failed"` and all
        count kwargs zero (no requirements were successfully assessed,
        so nothing to count).

        Patches `is_bot` to return False -- the failure path gates on
        the bot filter parallel to the success path, so an
        unpatched `is_bot()` running under a bot-shaped test
        environment could suppress the log call and mask a wiring
        break. Explicit patch pins the design.

        `_handle_assessment_error` is a plain function that returns
        the UI-facing banner string. No Streamlit fixture needed."""
        from ui.pages import role_match

        with (
            patch.object(role_match, "log_role_match_assessment") as mock_log,
            patch.object(role_match, "is_bot", return_value=False),
        ):
            role_match._handle_assessment_error(RuntimeError("simulated Mode 4"))

        assert mock_log.call_count == 1, (
            f"expected exactly one log_role_match_assessment call from "
            f"_handle_assessment_error; got {mock_log.call_count}. "
            f"Calls: {mock_log.call_args_list!r}"
        )
        call_kwargs = mock_log.call_args.kwargs
        assert call_kwargs.get("failure_type") == "retrieval_failed", (
            f"expected failure_type='retrieval_failed' on the failure "
            f"path; got {call_kwargs.get('failure_type')!r}"
        )
        for zero_kwarg in (
            "required_count",
            "preferred_count",
            "strong_count",
            "partial_count",
            "gap_count",
            "unassessed_count",
        ):
            assert call_kwargs.get(zero_kwarg) == 0, (
                f"expected {zero_kwarg}=0 on retrieval_failed row "
                f"(no requirements were assessed); got "
                f"{call_kwargs.get(zero_kwarg)!r}"
            )


class TestSuccessPathCallsLogger:
    """MATTGPT-247: `_log_role_match_success` (extracted from the inline
    submit-branch log block so it can be unit-tested) must derive
    `unassessed_count` from the results list rather than hardcoding 0
    or omitting it. This class pins the SUCCESS-PATH call site
    correctness fix -- Test 8 in test_query_logger.py pins the
    arithmetic invariant on the underlying helper; this test pins that
    the wiring calls that helper and forwards its result to
    log_role_match_assessment.

    Without this test, a Green that adds `_build_role_match_log_kwargs`
    but forgets to rewire the inline `sum()` lines to call it leaves
    production unchanged and unassessed_count stuck at 0 while tests
    1-8 all pass."""

    def test_log_role_match_success_calls_logger_with_derived_unassessed_count(
        self,
    ):
        """Test 10. Call `_log_role_match_success` with a payload
        containing three unassessed rows across both categories,
        assert `log_role_match_assessment` was called with
        `unassessed_count=3` and `failure_type="ok"`, and that the
        arithmetic invariant holds on the forwarded kwargs."""
        from ui.pages import role_match

        payload = {
            "extraction": {
                "role_title": "Senior Engineer",
                "company": "Acme",
                "jd_format": "hybrid",
            },
            "results": [
                {
                    "category": "required",
                    "requirement": "Requirement A",
                    "match_status": "strong",
                    "evidence": [],
                    "gap_explanation": "",
                },
                {
                    "category": "required",
                    "requirement": "Requirement B",
                    "match_status": "unassessed",
                    "evidence": [],
                    "gap_explanation": (
                        "I couldn't reach Matt's work history for this one."
                    ),
                },
                {
                    "category": "required",
                    "requirement": "Requirement C",
                    "match_status": "unassessed",
                    "evidence": [],
                    "gap_explanation": "I couldn't finish assessing this one.",
                },
                {
                    "category": "preferred",
                    "requirement": "Requirement D",
                    "match_status": "gap",
                    "evidence": [],
                    "gap_explanation": "Note: no direct evidence.",
                },
                {
                    "category": "preferred",
                    "requirement": "Requirement E",
                    "match_status": "unassessed",
                    "evidence": [],
                    "gap_explanation": (
                        "I couldn't reach Matt's work history for this one."
                    ),
                },
            ],
        }

        with (
            patch.object(role_match, "log_role_match_assessment") as mock_log,
            patch.object(role_match, "is_bot", return_value=False),
        ):
            role_match._log_role_match_success(payload)

        assert mock_log.call_count == 1, (
            f"expected exactly one log_role_match_assessment call from "
            f"_log_role_match_success; got {mock_log.call_count}. "
            f"Calls: {mock_log.call_args_list!r}"
        )
        call_kwargs = mock_log.call_args.kwargs
        assert call_kwargs.get("failure_type") == "ok", (
            f"expected failure_type='ok' on the success path; got "
            f"{call_kwargs.get('failure_type')!r}"
        )
        assert call_kwargs.get("unassessed_count") == 3, (
            f"expected unassessed_count=3 (three unassessed rows in the "
            f"payload); got {call_kwargs.get('unassessed_count')!r}. "
            f"This is the correctness fix: the inline submit-branch "
            f"code hardcoded per-status sum() calls that omitted "
            f"unassessed_count."
        )
        lhs = (
            call_kwargs["strong_count"]
            + call_kwargs["partial_count"]
            + call_kwargs["gap_count"]
            + call_kwargs["unassessed_count"]
        )
        rhs = call_kwargs["required_count"] + call_kwargs["preferred_count"]
        assert lhs == rhs, (
            f"arithmetic invariant broken on the forwarded kwargs: "
            f"strong+partial+gap+unassessed={lhs} != "
            f"required+preferred={rhs}. Forwarded kwargs: {call_kwargs!r}"
        )
