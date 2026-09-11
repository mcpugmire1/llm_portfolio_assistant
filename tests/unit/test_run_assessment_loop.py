"""MATTGPT-243: characterization tests for run_assessment's aggregation loop.

Patches inside `services.jd_assessor` so `run_assessment` actually
executes and its per-requirement dependencies (`extract_requirements`,
`retrieve_stories`, `assess_requirement`, `_get_openai_client`) are
stubbed at the point the loop consumes them.

Distinct from `tests/unit/test_assess_jd.py`, which loads
`scripts/assess_jd.py` via `importlib.util` and patches on the loaded
module object -- the loop in `services.jd_assessor.run_assessment` is
never touched by that test. The two files must not be consolidated.

Not classical Red. All four assertions pass against the current
sequential loop. Regression protection for -243's mechanism swap
(sequential -> `asyncio.as_completed` at concurrency 10). Reverse-sleep
on the patched `assess_requirement` gives the order assertion teeth
once Green ships -- without it, order preservation passes by accident
under any parallel implementation, including one that skips the
re-sort by submission order.

`return_exceptions` stays False for -243; per-requirement error rows
are -248. The propagation assertion here pins that contract.
"""

import time
from unittest.mock import patch

import pytest

from services import jd_assessor

_N_REQS = 5


def _fake_extraction():
    """Return an extraction with `_N_REQS` required requirements whose
    text encodes the submission index so the reverse-sleep fixture can
    decode it."""
    return {
        "required_qualifications": [
            {
                "requirement": f"req_{i}",
                "source_text": f"req_{i}",
                "type": "skill",
            }
            for i in range(_N_REQS)
        ],
        "preferred_qualifications": [],
        "implicit_requirements": [],
    }


def _fake_assess_success(_client, requirement, _candidates):
    """Fake `assess_requirement` return. Sleeps inversely to the
    requirement's submission index so completion order is deliberately
    the reverse of submission order under any parallel implementation."""
    idx = int(requirement.split("_")[-1])
    time.sleep((_N_REQS - idx) * 0.02)
    return {
        "requirement": requirement,
        "match_status": "strong",
        "evidence": [],
        "gap_explanation": "",
        "confidence": "high",
    }


def _fake_assess_one_raises(_client, requirement, _candidates):
    """Same as `_fake_assess_success` except `req_2` raises."""
    if requirement == "req_2":
        raise RuntimeError("simulated upstream failure on req_2")
    idx = int(requirement.split("_")[-1])
    time.sleep((_N_REQS - idx) * 0.02)
    return {
        "requirement": requirement,
        "match_status": "strong",
        "evidence": [],
        "gap_explanation": "",
        "confidence": "high",
    }


def _patched_loop_context(assess_side_effect):
    """Return a tuple of four `patch.object` context managers covering
    the loop's dependencies at the `services.jd_assessor` namespace.
    `extract_requirements` uses `side_effect=lambda ...: _fake_extraction()`
    so each call builds a fresh dict -- shared module-level structures
    across tests are the class of coupling that produces a failure in
    one test caused by another."""
    return (
        patch.object(jd_assessor, "_get_openai_client", return_value=None),
        patch.object(
            jd_assessor,
            "extract_requirements",
            side_effect=lambda *_a, **_kw: _fake_extraction(),
        ),
        patch.object(jd_assessor, "retrieve_stories", return_value=[]),
        patch.object(jd_assessor, "assess_requirement", side_effect=assess_side_effect),
    )


class TestRunAssessmentLoop:
    def test_result_order_matches_submission_order(self):
        """Order assertion. Under the sequential loop this passes
        trivially (completion order == submission order). Under a
        parallel Green that skips re-sort, the reverse-sleep fixture
        makes it fail: `req_0` sleeps longest, `req_{N-1}` returns
        first, and results come back in reverse completion order."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with p1, p2, p3, p4:
            out = jd_assessor.run_assessment("fake jd text", [])

        result_reqs = [r["requirement"] for r in out["results"]]
        expected = [f"req_{i}" for i in range(_N_REQS)]
        assert result_reqs == expected

    def test_result_length_equals_requirement_count(self):
        """Structural today: every requirement submitted gets a row and
        the loop cannot drop or dedupe. Becomes a real claim under
        -248, where `return_exceptions=True` could otherwise cause a
        raising `assess_requirement` to swallow the row instead of
        producing an error row for it."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with p1, p2, p3, p4:
            out = jd_assessor.run_assessment("fake jd text", [])
        assert len(out["results"]) == _N_REQS

    def test_every_row_carries_category(self):
        """`category` is stamped by the loop caller onto the LLM's
        parsed JSON; every row should carry it. Value is one of the
        two known categories, not the placeholder default."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with p1, p2, p3, p4:
            out = jd_assessor.run_assessment("fake jd text", [])
        for r in out["results"]:
            assert r["category"] in {"required", "preferred"}

    def test_raising_assess_requirement_propagates(self):
        """Under the sequential loop a raising `assess_requirement`
        propagates up through `run_assessment` as-is. -243's Green swap
        to `asyncio.as_completed` must preserve this contract
        (`return_exceptions=False`; error rows are -248, not -243)."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_one_raises)
        with p1, p2, p3, p4:
            with pytest.raises(
                RuntimeError, match="simulated upstream failure on req_2"
            ):
                jd_assessor.run_assessment("fake jd text", [])
