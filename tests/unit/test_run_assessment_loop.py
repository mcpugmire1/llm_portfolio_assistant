"""MATTGPT-243 + MATTGPT-248 Cycle 2: aggregation-loop tests for
`run_assessment` and its per-requirement failure modes.

Patches inside `services.jd_assessor` so `run_assessment` actually
executes and its per-requirement dependencies (`extract_requirements`,
`retrieve_stories`, `assess_requirement`, `_get_openai_client`) are
stubbed at the point the loop consumes them.

Distinct from `tests/unit/test_assess_jd.py`, which loads
`scripts/assess_jd.py` via `importlib.util` and patches on the loaded
module object -- the loop in `services.jd_assessor.run_assessment` is
never touched by that test. The two files must not be consolidated.

`TestRunAssessmentLoop` + timing classes are the -243 characterization
tests: not classical Red, they pass against the current parallel loop
and protect the mechanism swap (sequential -> `asyncio.as_completed`
at concurrency 10). Reverse-sleep on the patched `assess_requirement`
gives the order assertion teeth -- without it, order preservation
passes by accident under any parallel implementation.

`TestPartialFailureRows` + `TestRetrieveStoriesNoneVsEmpty` are the
-248 Cycle 2 Red tests. They pin four failure modes:

- Mode 1: `assess_requirement` raises -> per-call catch, unassessed
  row carrying category + requirement + a per-mode gap_explanation.
- Mode 2: `retrieve_stories` returns None -> unassessed row emitted
  directly without calling the LLM (during a Pinecone outage this
  avoids paying N gpt-4o calls to produce N unassessed rows).
- Mode 3: `retrieve_stories` returns [] -> real empty match; the
  loop proceeds normally and the LLM is still called.
- Mode 4: `retrieve_stories` raises -> propagates (deliberately
  different from Mode 2, and the log phrase says so).

Three distinct log phrases -- 'assess-caught' (Mode 1),
'retrieval-returned-None' (Mode 2), 'retrieval-raised' (Mode 4) --
keep the producer-side causes grep-separable. 'assess-caught' names
the outcome (caught, not propagated) so it can't be confused with
Mode 4's 'retrieval-raised', which does propagate. Distinct from the
'malformed row' phrase used at the consumer render sites
(see `test_role_match_render.py`).

The `test_raising_assess_requirement_propagates` -243 contract has
been inverted here as `test_assess_requirement_exception_yields_unassessed_row`
under Mode 1. The propagation contract moves to Mode 4 (retrieve raises).
"""

import logging
import re
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


def _fake_retrieve_returns_none_for_req_2(requirement_text, *_args, **_kwargs):
    """Fake `retrieve_stories` that returns None for `req_2` and [] for
    every other requirement. Mode 2: simulates a Pinecone outage
    scoped to a single requirement so mixed-failure runs (retrieval up
    for most, down for one) can be pinned distinctly from a total
    failure."""
    if requirement_text == "req_2":
        return None
    return []


def _fake_retrieve_raises_on_req_2(requirement_text, *_args, **_kwargs):
    """Fake `retrieve_stories` that raises on `req_2` and returns [] for
    every other requirement. Mode 4: retrieval-layer exception that
    Green must propagate rather than convert to an unassessed row --
    deliberately different from Mode 2 so the two failure classes
    stay grep-distinguishable in logs and behavior."""
    if requirement_text == "req_2":
        raise RuntimeError("simulated retrieval failure on req_2")
    return []


def _make_tracking_assess(base=None):
    """Wrap an `assess_requirement` side_effect with a per-call
    requirement-text log so tests can assert on which requirements
    reached the LLM without depending on `MagicMock.call_count`
    (patch.object with `side_effect=<callable>` does not expose the
    mock object at the `with` boundary in this file's `p1, p2, p3, p4`
    unpacking pattern)."""
    base_fn = base if base is not None else _fake_assess_success
    calls: list[str] = []

    def _tracker(client, requirement, candidates):
        calls.append(requirement)
        return base_fn(client, requirement, candidates)

    _tracker.calls = calls
    return _tracker


def _patched_loop_context(assess_side_effect, retrieve_side_effect=None):
    """Return a tuple of four `patch.object` context managers covering
    the loop's dependencies at the `services.jd_assessor` namespace.
    `extract_requirements` uses `side_effect=lambda ...: _fake_extraction()`
    so each call builds a fresh dict -- shared module-level structures
    across tests are the class of coupling that produces a failure in
    one test caused by another.

    `retrieve_side_effect` defaults to `return_value=[]` (Mode 3, real
    empty match). Pass a callable to exercise Mode 2 (returns None for
    a specific requirement) or Mode 4 (raises on a specific
    requirement)."""
    retrieve_kwargs = (
        {"side_effect": retrieve_side_effect}
        if retrieve_side_effect is not None
        else {"return_value": []}
    )
    return (
        patch.object(jd_assessor, "_get_openai_client", return_value=None),
        patch.object(
            jd_assessor,
            "extract_requirements",
            side_effect=lambda *_a, **_kw: _fake_extraction(),
        ),
        patch.object(jd_assessor, "retrieve_stories", **retrieve_kwargs),
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

    # `test_raising_assess_requirement_propagates` (-243) has been
    # inverted under Cycle 2 Mode 1 and moved to
    # `TestPartialFailureRows.test_assess_requirement_exception_yields_unassessed_row`
    # below. The propagation contract now belongs to Mode 4
    # (retrieve_stories raises), pinned by
    # `TestPartialFailureRows.test_retrieve_raise_propagates`.


class TestRunAssessmentTiming:
    """MATTGPT-243 timing instrumentation. `run_assessment` prints per-stage
    elapsed times to stdout when `config.debug.DEBUG` is True and stays
    silent when False. Print rather than dbg() because -152 is moving debug
    output off the Streamlit sidecar; the terminal is the new sink."""

    def test_extraction_line_carries_ms_and_n_reqs_when_debug_true(self, capsys):
        """DEBUG=True: the extraction line carries both `extraction_ms=<float>`
        and `n_reqs=<int>` on the same line so extraction cost and the
        requirement count it produced are grep-legible together.

        Patches without create=True so a missing or misnamed DEBUG import
        in services.jd_assessor fails loudly at patch time rather than
        silently creating an attribute production never reads."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with patch.object(jd_assessor, "DEBUG", True), p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        captured = capsys.readouterr()
        lines = [ln for ln in captured.out.splitlines() if "extraction_ms=" in ln]
        assert lines, f"expected an extraction_ms line, got: {captured.out!r}"
        line = lines[0]
        assert re.search(
            r"extraction_ms=\d+\.\d+", line
        ), f"expected 'extraction_ms=<float>' on line, got: {line!r}"
        assert re.search(
            r"n_reqs=\d+", line
        ), f"expected 'n_reqs=<int>' on the extraction line, got: {line!r}"

    def test_fan_out_line_carries_ms_and_n_reqs_when_debug_true(self, capsys):
        """DEBUG=True: the fan-out line carries both `fan_out_ms=<float>`
        and `n_reqs=<int>` on the same line so per-requirement time is
        derivable without needing the extraction dict."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with patch.object(jd_assessor, "DEBUG", True), p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        captured = capsys.readouterr()
        lines = [ln for ln in captured.out.splitlines() if "fan_out_ms=" in ln]
        assert lines, f"expected a fan_out_ms line, got: {captured.out!r}"
        line = lines[0]
        assert re.search(
            r"fan_out_ms=\d+\.\d+", line
        ), f"expected 'fan_out_ms=<float>' on line, got: {line!r}"
        assert re.search(
            r"n_reqs=\d+", line
        ), f"expected 'n_reqs=<int>' on the fan-out line, got: {line!r}"

    def test_no_timing_output_when_debug_false(self, capsys):
        """DEBUG=False: neither timing token appears. Guards against a
        Green implementation that forgets the gate and prints on every
        production request."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with patch.object(jd_assessor, "DEBUG", False), p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        captured = capsys.readouterr()
        assert (
            "extraction_ms" not in captured.out
        ), f"expected no 'extraction_ms' when DEBUG=False, got: {captured.out!r}"
        assert (
            "fan_out_ms" not in captured.out
        ), f"expected no 'fan_out_ms' when DEBUG=False, got: {captured.out!r}"


class TestAssessCallTiming:
    """MATTGPT-243 per-call timing: one `assess_call_ms=<float:.1f>
    req_idx=<int>` line per requirement, emitted from inside
    `_assess_one_with_index` around the assess_requirement await.

    Purpose is to isolate a single gpt-4o call's latency from the fan-out
    wall time so wave math becomes measured instead of inferred. Same
    DEBUG gate and same patch shape as the extraction / fan-out timers."""

    def test_assess_call_line_carries_ms_and_req_idx_when_debug_true(self, capsys):
        """DEBUG=True: at least one line contains both `assess_call_ms=<float:.1f>`
        and `req_idx=<int>` on the same line so per-call latency is
        grep-legible and attributable to a specific requirement."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with patch.object(jd_assessor, "DEBUG", True), p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        captured = capsys.readouterr()
        lines = [ln for ln in captured.out.splitlines() if "assess_call_ms=" in ln]
        assert lines, f"expected assess_call_ms lines, got: {captured.out!r}"
        line = lines[0]
        assert re.search(
            r"assess_call_ms=\d+\.\d+", line
        ), f"expected 'assess_call_ms=<float>' on line, got: {line!r}"
        assert re.search(
            r"req_idx=\d+", line
        ), f"expected 'req_idx=<int>' on line, got: {line!r}"

    def test_one_assess_call_line_per_requirement_when_debug_true(self, capsys):
        """DEBUG=True: N requirements produce N assess_call_ms lines.
        Guards against a Green that emits per-wave rather than per-call
        (which would collapse the sample count and defeat the point of
        the per-call measurement)."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with patch.object(jd_assessor, "DEBUG", True), p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        captured = capsys.readouterr()
        lines = [ln for ln in captured.out.splitlines() if "assess_call_ms=" in ln]
        assert len(lines) == _N_REQS, (
            f"expected {_N_REQS} assess_call_ms lines (one per requirement), "
            f"got {len(lines)}: {captured.out!r}"
        )

    def test_no_assess_call_line_when_debug_false(self, capsys):
        """DEBUG=False: no assess_call_ms lines. Guards against a Green
        that forgets the gate and prints on every production request."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_success)
        with patch.object(jd_assessor, "DEBUG", False), p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        captured = capsys.readouterr()
        assert (
            "assess_call_ms" not in captured.out
        ), f"expected no 'assess_call_ms' when DEBUG=False, got: {captured.out!r}"


# ---------------------------------------------------------------------------
# MATTGPT-248 Cycle 2: partial-failure producer Red
# ---------------------------------------------------------------------------


_MODE_1_GAP_TEXT = "I couldn't finish assessing this one."
_MODE_2_GAP_TEXT = "I couldn't reach Matt's work history for this one."
_LOGGER_NAME = "services.jd_assessor"


def _records_matching(caplog, phrase: str, req_marker: str) -> list:
    """Filter caplog records to those from `services.jd_assessor` whose
    message contains both the given phrase (case-insensitive) and the
    given req marker. Scoping to the producer's logger keeps the
    assertion honest -- an unrelated logger emitting the same substring
    would otherwise satisfy the test by accident."""
    return [
        r
        for r in caplog.records
        if r.name == _LOGGER_NAME
        and phrase.lower() in r.message.lower()
        and req_marker in r.message
    ]


class TestPartialFailureRows:
    """MATTGPT-248 Cycle 2: four per-requirement failure modes on the
    producer side.

    Mode 1 (assess_requirement raises): caught inside
    `_assess_one_with_index`, emits an unassessed row carrying the
    Mode 1 gap_explanation. The row still counts and still renders;
    the previous -243 contract of "raise propagates" has moved to
    Mode 4 below, because a single-requirement LLM outage should not
    take down the whole assessment.

    Mode 2 (retrieve_stories returns None): the retrieval-layer
    signal for a Pinecone outage. Emits an unassessed row directly
    without calling the LLM at all. During a total Pinecone outage on
    an N-requirement JD this saves N gpt-4o calls that would each
    have produced 'gap' rows the reader would have to disbelieve
    row-by-row.

    Mode 3 (retrieve_stories returns []): real empty match. The LLM
    is still called (grounding-only path); a `gap` verdict is the
    correct outcome. Distinguished from Mode 2 by the log phrase and
    by whether the LLM ran.

    Mode 4 (retrieve_stories raises): unexpected failure at the
    retrieval layer. Propagates through `_fan_out_assessments`'s
    existing cancel-and-drain BaseException handler and out of
    `run_assessment`, same shape as -243's raising-assess contract
    (which this cycle moves off of Mode 1). The log phrase says why
    Mode 4 is deliberately different from Mode 2.

    Three distinct log phrases -- `assess-caught` (Mode 1),
    `retrieval-returned-None` (Mode 2), `retrieval-raised` (Mode 4)
    -- keep the producer-side causes grep-separable. `assess-caught`
    names the outcome (the exception was caught, not propagated) so
    it can't be confused with `retrieval-raised` (which does
    propagate); a `retrieval-raised` / `assess-raised` pairing
    would put two near-identical tokens on opposite outcomes.
    Distinct also from the consumer-side `malformed row` phrase in
    test_role_match_render.py TestMalformedMatchStatusCoercion.

    Row shape for unassessed rows (both Mode 1 and Mode 2):
      match_status = "unassessed"
      category     = passed through from the source requirement dict
      requirement  = passed through from the source requirement dict
      evidence     = []
      gap_explanation = per-mode string; renders under the ⋯ badge on
                        all three surfaces via the follow-up Green
                        that landed at 9b0ddc8 (gate widened through
                        _owes_explanation)."""

    def test_assess_requirement_exception_yields_unassessed_row(self):
        """Mode 1. Replaces the -243 `test_raising_assess_requirement_propagates`
        contract: after Cycle 2 Green, a raising `assess_requirement`
        does NOT propagate -- it becomes an unassessed row carrying
        the Mode 1 gap_explanation."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_one_raises)
        with p1, p2, p3, p4:
            out = jd_assessor.run_assessment("fake jd text", [])

        assert len(out["results"]) == _N_REQS, (
            f"expected {_N_REQS} rows, one per requirement; got "
            f"{len(out['results'])}: {out['results']!r}"
        )
        req2_row = next(
            (r for r in out["results"] if r.get("requirement") == "req_2"),
            None,
        )
        assert req2_row is not None, (
            f"req_2's row missing from results after assess raised; "
            f"rows: {[r.get('requirement') for r in out['results']]!r}"
        )
        assert req2_row.get("match_status") == "unassessed", (
            f"expected match_status='unassessed' on req_2 (assess raised); "
            f"got {req2_row.get('match_status')!r}"
        )
        assert req2_row.get("category") == "required"
        assert req2_row.get("evidence") == []
        assert req2_row.get("gap_explanation") == _MODE_1_GAP_TEXT, (
            f"expected Mode 1 gap_explanation {_MODE_1_GAP_TEXT!r}; "
            f"got {req2_row.get('gap_explanation')!r}"
        )
        other_rows = [r for r in out["results"] if r.get("requirement") != "req_2"]
        for r in other_rows:
            assert (
                r.get("match_status") == "strong"
            ), f"non-req_2 rows must be unaffected; row: {r!r}"

    def test_assess_requirement_exception_logs_assess_caught_phrase(self, caplog):
        """Mode 1 log. `assess-caught` names the outcome (the exception
        was caught, not propagated), which is the load-bearing
        distinction from Mode 4's `retrieval-raised`. Substring pin,
        not exact phrasing, so Green can pick the surrounding sentence.
        Scoped to `services.jd_assessor` so an unrelated logger can't
        satisfy the assertion by accident."""
        p1, p2, p3, p4 = _patched_loop_context(_fake_assess_one_raises)
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            with p1, p2, p3, p4:
                jd_assessor.run_assessment("fake jd text", [])
        matching = _records_matching(caplog, "assess-caught", "req_2")
        assert matching, (
            f"expected a `services.jd_assessor` warning containing "
            f"'assess-caught' and 'req_2'; got: "
            f"{[(r.name, r.message) for r in caplog.records]!r}"
        )

    def test_retrieve_returns_none_yields_unassessed_row_and_skips_assess(self):
        """Mode 2. Two claims in one test because they're two sides of
        the same branch: the row shape is unassessed carrying the Mode
        2 gap_explanation, AND `assess_requirement` was not called for
        req_2. The second claim is the "avoid paying N gpt-4o calls
        during an outage" contract."""
        tracker = _make_tracking_assess()
        p1, p2, p3, p4 = _patched_loop_context(
            tracker, retrieve_side_effect=_fake_retrieve_returns_none_for_req_2
        )
        with p1, p2, p3, p4:
            out = jd_assessor.run_assessment("fake jd text", [])

        assert "req_2" not in tracker.calls, (
            f"assess_requirement was called for req_2 despite retrieve "
            f"returning None; tracked calls: {tracker.calls!r}"
        )
        assert len(tracker.calls) == _N_REQS - 1, (
            f"expected {_N_REQS - 1} assess calls (all reqs except req_2); "
            f"got {len(tracker.calls)}: {tracker.calls!r}"
        )
        req2_row = next(
            (r for r in out["results"] if r.get("requirement") == "req_2"),
            None,
        )
        assert req2_row is not None
        assert req2_row.get("match_status") == "unassessed"
        assert req2_row.get("category") == "required"
        assert req2_row.get("evidence") == []
        assert req2_row.get("gap_explanation") == _MODE_2_GAP_TEXT, (
            f"expected Mode 2 gap_explanation {_MODE_2_GAP_TEXT!r}; "
            f"got {req2_row.get('gap_explanation')!r}"
        )

    def test_retrieve_returns_none_logs_retrieval_returned_none_phrase(self, caplog):
        """Mode 2 log. `retrieval-returned-None` phrase, distinct from
        Mode 4's `retrieval-raised` -- an outage (None) is not a bug
        (raise) and the log has to say which happened. Scoped to
        `services.jd_assessor`."""
        p1, p2, p3, p4 = _patched_loop_context(
            _fake_assess_success,
            retrieve_side_effect=_fake_retrieve_returns_none_for_req_2,
        )
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            with p1, p2, p3, p4:
                jd_assessor.run_assessment("fake jd text", [])
        matching = _records_matching(caplog, "retrieval-returned-none", "req_2")
        assert matching, (
            f"expected a `services.jd_assessor` warning containing "
            f"'retrieval-returned-None' and 'req_2'; got: "
            f"{[(r.name, r.message) for r in caplog.records]!r}"
        )

    def test_retrieve_returns_empty_list_still_calls_assess(self):
        """Mode 3. Distinguishes an empty match (retrieve returned [])
        from an outage (retrieve returned None): the LLM is still
        called on the grounding-only path. Guards against a Green
        that over-collapses `[] -> None` and skips the LLM for real
        empty matches."""
        tracker = _make_tracking_assess()
        p1, p2, p3, p4 = _patched_loop_context(tracker)  # default retrieve = []
        with p1, p2, p3, p4:
            jd_assessor.run_assessment("fake jd text", [])
        assert len(tracker.calls) == _N_REQS, (
            f"expected assess_requirement called {_N_REQS} times (Mode 3, "
            f"empty match is not an outage); got {len(tracker.calls)}: "
            f"{tracker.calls!r}"
        )

    def test_retrieve_raise_propagates(self):
        """Mode 4. The propagation contract that lived on Mode 1
        under -243 moves here. A retrieval-layer exception is
        unexpected (Mode 2's None is the expected outage signal), so
        it bubbles through `_fan_out_assessments`'s cancel-and-drain
        BaseException handler and out of `run_assessment`. Passes
        against today's tree via the same handler; Cycle 2 Green must
        preserve it while still adding the log-before-reraise from
        the next test."""
        p1, p2, p3, p4 = _patched_loop_context(
            _fake_assess_success,
            retrieve_side_effect=_fake_retrieve_raises_on_req_2,
        )
        with p1, p2, p3, p4:
            with pytest.raises(
                RuntimeError, match="simulated retrieval failure on req_2"
            ):
                jd_assessor.run_assessment("fake jd text", [])

    def test_retrieve_raise_logs_retrieval_raised_phrase_before_reraise(self, caplog):
        """Mode 4 log. Green adds a `try/except: log; raise` around
        the retrieve_stories call in `_assess_one_with_index` so the
        outage is grep-legible before it propagates. `caplog` captures
        records emitted before the raise even inside a `pytest.raises`
        block, so the assertion after both `with` blocks reads the
        log honestly. Scoped to `services.jd_assessor`."""
        p1, p2, p3, p4 = _patched_loop_context(
            _fake_assess_success,
            retrieve_side_effect=_fake_retrieve_raises_on_req_2,
        )
        with caplog.at_level(logging.WARNING, logger=_LOGGER_NAME):
            with p1, p2, p3, p4:
                with pytest.raises(
                    RuntimeError, match="simulated retrieval failure on req_2"
                ):
                    jd_assessor.run_assessment("fake jd text", [])
        matching = _records_matching(caplog, "retrieval-raised", "req_2")
        assert matching, (
            f"expected a `services.jd_assessor` warning containing "
            f"'retrieval-raised' and 'req_2' before the re-raise; got: "
            f"{[(r.name, r.message) for r in caplog.records]!r}"
        )


class TestRetrieveStoriesNoneVsEmpty:
    """MATTGPT-248 Cycle 2: the mechanical change at the retrieve_stories
    layer. Today, `retrieve_stories` collapses `pinecone_semantic_search`'s
    None-on-failure signal into `[]` (`if not results: return []`), so
    the `_assess_one_with_index` caller cannot distinguish an outage
    from an empty match. Green undoes that collapse: None propagates,
    [] stays [].

    Bidirectional pin: the None-branch test fails today; the []-branch
    test passes today and guards against a Green that over-swaps and
    accidentally converts real empty matches to None (which would then
    route to Mode 2's unassessed row instead of Mode 3's gap)."""

    def test_retrieve_stories_propagates_none_from_pinecone(self):
        with patch.object(jd_assessor, "pinecone_semantic_search", return_value=None):
            result = jd_assessor.retrieve_stories("some requirement text", stories=[])
        assert result is None, (
            f"expected None to propagate from pinecone_semantic_search; "
            f"got {result!r}. retrieve_stories still collapses None -> []."
        )

    def test_retrieve_stories_returns_empty_list_when_pinecone_returns_empty(self):
        with patch.object(jd_assessor, "pinecone_semantic_search", return_value=[]):
            result = jd_assessor.retrieve_stories("some requirement text", stories=[])
        assert result == [], (
            f"expected [] to stay [] (real empty match, not an outage); "
            f"got {result!r}"
        )


# =============================================================================
# MATTGPT-245 phase two: on_row callback on _fan_out_assessments
# =============================================================================
# The service layer gains an optional on_row(index, assessment) callback
# invoked as each coroutine completes. The Role Match UI passes a closure
# that writes into a per-requirement st.empty() slot for progressive
# row-fill. The service stays Streamlit-free -- on_row is a plain Python
# callable, and the return contract (submission-ordered assessment dicts)
# is unchanged whether or not on_row is provided.
#
# Tests 1-5 fail on Red with TypeError: unexpected keyword argument
# 'on_row'. Test 6 fails on Red on the with-callback branch (same TypeError).
class TestFanOutOnRowCallback:
    """MATTGPT-245 phase two."""

    _FIXTURE_REQS = [
        {"text": f"req_{i}", "category": "required"} for i in range(_N_REQS)
    ]

    def _run_fanout(
        self, on_row=None, assess_side_effect=None, retrieve_side_effect=None
    ):
        """Helper: run _fan_out_assessments with the standard patches.
        on_row is passed only when provided so tests can exercise both
        the omit-callback and pass-callback shapes cleanly."""
        import asyncio

        assess = assess_side_effect or _fake_assess_success
        retrieve_kwargs = (
            {"side_effect": retrieve_side_effect}
            if retrieve_side_effect is not None
            else {"return_value": []}
        )
        kwargs = {"on_row": on_row} if on_row is not None else {}
        with (
            patch.object(jd_assessor, "retrieve_stories", **retrieve_kwargs),
            patch.object(jd_assessor, "assess_requirement", side_effect=assess),
        ):
            return asyncio.run(
                jd_assessor._fan_out_assessments(None, self._FIXTURE_REQS, [], **kwargs)
            )

    def test_on_row_fires_once_per_requirement(self):
        """Test 1. on_row(index, assessment) invoked exactly N times for
        N submitted requirements. Success path (all rows return
        assessment dicts, no failures)."""
        received: list[tuple[int, dict]] = []

        def _capture(index, assessment):
            received.append((index, assessment))

        self._run_fanout(on_row=_capture)

        assert len(received) == _N_REQS, (
            f"expected on_row to fire exactly {_N_REQS} times "
            f"(one per submitted requirement); got {len(received)}. "
            f"Received: {received!r}"
        )

    def test_on_row_receives_every_submission_index_exactly_once(self):
        """Test 2. Every index in [0, N-1] arrives via on_row exactly
        once. Guards against a Green that skips indices, double-fires,
        or fires with out-of-range indices."""
        received_indices: list[int] = []

        def _capture(index, _assessment):
            received_indices.append(index)

        self._run_fanout(on_row=_capture)

        assert sorted(received_indices) == list(range(_N_REQS)), (
            f"expected every submission index in [0, {_N_REQS - 1}] to "
            f"appear exactly once; got sorted={sorted(received_indices)!r}. "
            f"Full received order: {received_indices!r}"
        )

    def test_on_row_index_matches_submission_position_not_completion_order(
        self,
    ):
        """Test 3. on_row receives the SUBMISSION index, not the
        completion order. Load-bearing: the UI's slot-writer closure
        indexes into a submission-ordered list of st.empty()
        placeholders; a Green that passes completion-order indices
        would write results into the wrong slots.

        The reverse-sleep fixture makes completion order deliberately
        different from submission order (req_{N-1} completes first,
        req_0 last), so a Green that fires on_row with the completion
        counter instead of the submission index would break the
        (index, requirement_text) self-consistency asserted below.

        The assertion is pair-consistency, not arrival sequence:
        req_N carries the text f'req_{N}' regardless of when it
        arrives. Pins index correctness without pinning wall-clock
        timing, so the fixture's sleep values can drift without
        making the test flake on CI."""
        received: list[tuple[int, str]] = []

        def _capture(index, assessment):
            received.append((index, assessment["requirement"]))

        self._run_fanout(on_row=_capture)

        # Primary invariant: every (index, requirement_text) pair is
        # self-consistent (req_N carries "req_N"). Iterated per-pair
        # so a mismatch names the offending index.
        for index, requirement_text in received:
            assert requirement_text == f"req_{index}", (
                f"on_row received (index={index}, requirement={requirement_text!r}), "
                f"but the requirement text should encode the SUBMISSION "
                f"index (expected 'req_{index}'). A Green that fires "
                f"on_row with completion-order counters instead of the "
                f"submission index would produce this mismatch. Full "
                f"received: {received!r}"
            )

    def test_on_row_fires_for_mode_1_assess_caught_with_unassessed_row(self):
        """Test 4. Mode 1 (assess_requirement raises on req_2):
        _assess_one_with_index catches the exception and returns an
        unassessed row. on_row must still fire for index 2, with that
        unassessed row -- not skipped, not with the raised exception.
        Load-bearing: the UI slot for req_2 would otherwise stay at
        the pending state indefinitely."""
        received: dict[int, dict] = {}

        def _capture(index, assessment):
            received[index] = assessment

        self._run_fanout(on_row=_capture, assess_side_effect=_fake_assess_one_raises)

        assert 2 in received, (
            f"expected on_row to fire for index 2 even though "
            f"assess_requirement raised on req_2. Received indices: "
            f"{sorted(received.keys())!r}"
        )
        assert received[2].get("match_status") == "unassessed", (
            f"expected the on_row payload for index 2 to be an unassessed "
            f"row (Mode 1 assess-caught); got match_status="
            f"{received[2].get('match_status')!r}. Full row: {received[2]!r}"
        )

    def test_on_row_fires_for_mode_2_retrieval_none_with_unassessed_row(self):
        """Test 5. Mode 2 (retrieve_stories returns None for req_2):
        _assess_one_with_index emits an unassessed row directly
        without calling the LLM. on_row must still fire for index 2
        with that unassessed row. Same load-bearing reason as test 4
        (UI slot must not stay pending)."""
        received: dict[int, dict] = {}

        def _capture(index, assessment):
            received[index] = assessment

        self._run_fanout(
            on_row=_capture,
            retrieve_side_effect=_fake_retrieve_returns_none_for_req_2,
        )

        assert 2 in received, (
            f"expected on_row to fire for index 2 even though "
            f"retrieve_stories returned None on req_2. Received "
            f"indices: {sorted(received.keys())!r}"
        )
        assert received[2].get("match_status") == "unassessed", (
            f"expected the on_row payload for index 2 to be an unassessed "
            f"row (Mode 2 retrieval-returned-None); got match_status="
            f"{received[2].get('match_status')!r}. Full row: {received[2]!r}"
        )

    def test_fan_out_return_contract_unchanged_with_or_without_on_row(self):
        """Test 6. Pin the return contract for callers of
        _fan_out_assessments (via run_assessment, e.g.
        scripts/assess_jd.py). Adding the on_row callback must not
        change what the function returns -- it's a side channel, not
        a replacement. Same fixture on both runs, so the returned
        assessment lists must be equal element-for-element.

        Existing tests exercise the on_row=None path implicitly.
        This test's job is to make the contract-preservation
        explicit: 'implicitly covered' is how a contract change gets
        shipped unnoticed."""
        result_no_callback = self._run_fanout()

        received: list[int] = []
        result_with_callback = self._run_fanout(
            on_row=lambda idx, _r: received.append(idx)
        )

        assert result_no_callback == result_with_callback, (
            f"expected _fan_out_assessments return value to be identical "
            f"whether on_row is provided or omitted (deterministic assess "
            f"fixture, same inputs).\n"
            f"no_callback: {result_no_callback!r}\n"
            f"with_callback: {result_with_callback!r}"
        )
        # Sanity: the with-callback run actually invoked the callback,
        # so we know the equality holds despite on_row firing (not
        # because on_row was silently no-op'd).
        assert len(received) == _N_REQS, (
            f"sanity: with-callback run should have fired on_row {_N_REQS} "
            f"times; got {len(received)}. If this fails but the equality "
            f"above passes, Green implemented on_row as a no-op and the "
            f"return-contract pin is meaningless."
        )


# ---------------------------------------------------------------------------
# MATTGPT-244 prep: flatten passes source_text (not requirement) to the
# assessor for required/preferred rows. Implicit continues passing
# requirement because inferred_from is the source of inference, not the
# requirement itself.
# ---------------------------------------------------------------------------


def _extraction_with_distinct_source():
    """Fake extraction where source_text (and inferred_from) differ from
    requirement so tests can distinguish which field the flatten passes
    downstream. A row's category is inferable from its text prefix:
    'req_' -> required-proper, 'pref_' -> preferred, 'impl_' -> implicit.
    Text values are unique across sections so a single row can be located
    by content without depending on ordering."""
    return {
        "required_qualifications": [
            {
                "requirement": "req_compressed",
                "source_text": "req_verbatim clause",
                "type": "skill",
            },
        ],
        "preferred_qualifications": [
            {
                "requirement": "pref_compressed",
                "source_text": "pref_verbatim clause",
                "type": "skill",
            },
        ],
        "implicit_requirements": [
            {
                "requirement": "impl_capability",
                "inferred_from": "impl_source clause",
                "confidence": "medium",
            },
        ],
    }


class TestFlattenSourceTextPassthrough:
    """MATTGPT-244 flatten fix: required and preferred pass source_text
    (verbatim JD clause) downstream to retrieve_stories,
    assess_requirement, and the render surface. Implicit keeps passing
    requirement (the model's inferred capability) because inferred_from
    is the source of inference, not the requirement itself.

    Test 1, 2, 4 are change tests -- fail on Red, pass on Green.
    Test 3, 5 are characterization tests -- pass on Red as guards that
    Green does not accidentally switch implicit to inferred_from.

    Fixture (`_extraction_with_distinct_source`) makes requirement and
    source_text distinguishable per section, so tests can locate the
    right row by content without depending on ordering across the
    three-block flatten."""

    def _run_with_tracking(self):
        """Run run_assessment against the distinct-source fixture with
        tracking mocks on retrieve_stories and assess_requirement.
        Returns (out, retrieve_texts, assess_texts).

        Both mocks record the first positional argument -- for
        retrieve_stories that's requirement_text; for
        assess_requirement it's requirement. The distinct-source
        fixture uses unique text values so a text appearing in the
        recorded list uniquely identifies which row produced the
        call."""
        retrieve_texts: list[str] = []
        assess_texts: list[str] = []

        def _tracked_retrieve(text, *args, **kwargs):
            retrieve_texts.append(text)
            return []

        def _tracked_assess(client, requirement, candidates):
            assess_texts.append(requirement)
            return {
                "requirement": requirement,
                "match_status": "strong",
                "evidence": [],
                "gap_explanation": "",
                "confidence": "high",
            }

        with (
            patch.object(jd_assessor, "_get_openai_client", return_value=None),
            patch.object(
                jd_assessor,
                "extract_requirements",
                side_effect=lambda *_a, **_kw: _extraction_with_distinct_source(),
            ),
            patch.object(
                jd_assessor, "retrieve_stories", side_effect=_tracked_retrieve
            ),
            patch.object(
                jd_assessor, "assess_requirement", side_effect=_tracked_assess
            ),
        ):
            out = jd_assessor.run_assessment("fake jd", [])

        return out, retrieve_texts, assess_texts

    def test_required_row_passes_source_text_to_retrieve_and_assess(self):
        """Required-section row: retrieve_stories and assess_requirement
        both receive `source_text` (verbatim JD clause), not the
        compressed `requirement` field. Change test -- fails on Red."""
        _, retrieve_texts, assess_texts = self._run_with_tracking()

        assert "req_verbatim clause" in retrieve_texts, (
            f"expected retrieve_stories to receive the required row's "
            f"source_text ('req_verbatim clause'); got retrieve texts "
            f"{retrieve_texts!r}"
        )
        assert "req_verbatim clause" in assess_texts, (
            f"expected assess_requirement to receive the required row's "
            f"source_text ('req_verbatim clause'); got assess texts "
            f"{assess_texts!r}"
        )
        assert "req_compressed" not in retrieve_texts, (
            f"required row's compressed requirement ('req_compressed') "
            f"leaked into retrieval; got {retrieve_texts!r}"
        )
        assert "req_compressed" not in assess_texts, (
            f"required row's compressed requirement ('req_compressed') "
            f"leaked into assessor; got {assess_texts!r}"
        )

    def test_preferred_row_passes_source_text_to_retrieve_and_assess(self):
        """Preferred-section row: same as required. Change test."""
        _, retrieve_texts, assess_texts = self._run_with_tracking()

        assert "pref_verbatim clause" in retrieve_texts, (
            f"expected retrieve_stories to receive the preferred row's "
            f"source_text; got {retrieve_texts!r}"
        )
        assert "pref_verbatim clause" in assess_texts, (
            f"expected assess_requirement to receive the preferred row's "
            f"source_text; got {assess_texts!r}"
        )
        assert "pref_compressed" not in retrieve_texts, (
            f"preferred row's compressed requirement leaked into "
            f"retrieval; got {retrieve_texts!r}"
        )
        assert "pref_compressed" not in assess_texts, (
            f"preferred row's compressed requirement leaked into "
            f"assessor; got {assess_texts!r}"
        )

    def test_implicit_row_passes_requirement_to_retrieve_and_assess(self):
        """Implicit-section row: retrieve_stories and assess_requirement
        both receive `requirement` (the model's inferred capability),
        NOT `inferred_from`. inferred_from is the text that led to the
        inference, not the requirement itself -- sending it as the
        requirement would ask the assessor to judge evidence against a
        responsibility instead of against a capability.

        Characterization test -- passes on Red as a guard against Green
        accidentally switching implicit to inferred_from."""
        _, retrieve_texts, assess_texts = self._run_with_tracking()

        assert "impl_capability" in retrieve_texts, (
            f"expected retrieve_stories to receive the implicit row's "
            f"requirement ('impl_capability'); got {retrieve_texts!r}"
        )
        assert "impl_capability" in assess_texts, (
            f"expected assess_requirement to receive the implicit row's "
            f"requirement ('impl_capability'); got {assess_texts!r}"
        )
        assert "impl_source clause" not in retrieve_texts, (
            f"implicit row's inferred_from leaked into retrieval "
            f"(should only send requirement for implicit); got "
            f"{retrieve_texts!r}"
        )
        assert "impl_source clause" not in assess_texts, (
            f"implicit row's inferred_from leaked into assessor "
            f"(should only send requirement for implicit); got "
            f"{assess_texts!r}"
        )

    def test_non_implicit_row_requirement_field_is_source_text(self):
        """Render surface pin: after -245 phase-two passthrough
        (`assessment['requirement'] = req['text']`), the final row's
        `requirement` field is what recruiter-facing surfaces render.
        For required and preferred rows, this must be source_text.
        Change test -- fails on Red."""
        out, _, _ = self._run_with_tracking()
        rendered = [r.get("requirement") for r in out["results"]]

        assert "req_verbatim clause" in rendered, (
            f"required row's rendered requirement should be source_text; "
            f"got {rendered!r}"
        )
        assert "pref_verbatim clause" in rendered, (
            f"preferred row's rendered requirement should be source_text; "
            f"got {rendered!r}"
        )
        assert "req_compressed" not in rendered, (
            f"required row's compressed requirement leaked to the render "
            f"surface; got {rendered!r}"
        )
        assert "pref_compressed" not in rendered, (
            f"preferred row's compressed requirement leaked to the render "
            f"surface; got {rendered!r}"
        )

    def test_implicit_row_requirement_field_is_requirement(self):
        """Render surface pin for implicit: the row's `requirement`
        field is the model's inferred capability, NOT inferred_from.
        Characterization test -- passes on Red."""
        out, _, _ = self._run_with_tracking()
        rendered = [r.get("requirement") for r in out["results"]]

        assert "impl_capability" in rendered, (
            f"implicit row's rendered requirement should be the "
            f"inferred capability; got {rendered!r}"
        )
        assert "impl_source clause" not in rendered, (
            f"implicit row's inferred_from leaked to the render surface; "
            f"got {rendered!r}"
        )
