"""MATTGPT-243 probe: concurrency 10 vs 5 on the SEL fixture, interleaved.

Six runs in the order 10, 5, 10, 5, 10, 5. Interleaving disperses any
prompt-cache drift (OpenAI prefix cache TTL is roughly five minutes)
across both arms rather than concentrating it on the second arm, which
is what blocking three-then-three would do.

Concurrency is set by monkey-patching `services.jd_assessor._CONCURRENCY`
before each `run_assessment` call. `_fan_out_assessments` reads that
module attribute at each invocation when it constructs its semaphore,
so a fresh patch takes effect on each run without any production edit.
The patch is asserted immediately after being set so a failed patch
blows up loudly rather than reporting stale-arm data.

DEBUG handling: `jd_assessor.DEBUG` and `pinecone_service.DEBUG` are
independent bindings created at each module's import (both via
`from config.debug import DEBUG`), so rebinding one does not affect the
other. The probe explicitly sets `jd_assessor.DEBUG = True` (so per-stage
and per-call timer lines emit) and `pinecone_service.DEBUG = False` (so
retrieval-side lines stay silent regardless of the baseline in
config/debug.py). Both are restored on exit via try/finally. The
probe also prints `config.debug.DEBUG`'s current value at start so the
baseline state is visible in the output.

Stdout is captured to a StringIO per run and parsed for the three
`[jd_assessor]` timer lines: `extraction_ms=<float> n_reqs=<int>`,
`fan_out_ms=<float> n_reqs=<int>`, and one `assess_call_ms=<float>
req_idx=<int>` per requirement. Any parse miss on the timer lines is a
loud failure -- with 6 full assessments per probe run, a silent zero
in the summary would be expensive to discover after the fact.

Contention caveat (see the assess_call_ms Green commit): shared-endpoint
contention couples in-flight call latencies, so a delta in arm-averaged
assess_call_ms between arm 10 and arm 5 is not pure endpoint variance
-- it also reflects the contention shift itself. Read the delta as a
signal about "concurrency N vs concurrency M with this OpenAI account
under this load," not as a single-call cost curve.

Summary shape: pooled `assess_call_ms` leads because each sample is a
direct per-call measurement, independent of n_reqs. `fan_out_ms` is
secondary and carries an inline caveat: with count variance between
runs, fan_out totals are not directly comparable across arms without
normalizing for count.

Fixture: data/demo_jd.txt (Senior Engineering Leader, Product Platform,
465 words). First line is verified against SEL_JD_EXPECTED_FIRST_LINE
so results are comparable to the earlier 22-, 23-, 23-req paste runs.

Run: python probe_243_concurrency_alternating.py
"""

from __future__ import annotations

import io
import re
import statistics
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

import config.debug as _debug_module
from services import jd_assessor, pinecone_service
from utils.corpus_loader import load_stories

load_dotenv()

SEL_JD_PATH = Path(__file__).parent / "data" / "demo_jd.txt"
SEL_JD_EXPECTED_FIRST_LINE = "Senior Engineering Leader, Product Platform"
RUN_ORDER = [10, 5, 10, 5, 10, 5]

_RE_EXTRACTION = re.compile(r"\[jd_assessor\] extraction_ms=([\d.]+) n_reqs=(\d+)")
_RE_FAN_OUT = re.compile(r"\[jd_assessor\] fan_out_ms=([\d.]+) n_reqs=(\d+)")
_RE_ASSESS_CALL = re.compile(r"\[jd_assessor\] assess_call_ms=([\d.]+) req_idx=(\d+)")


def _parse_run_output(text: str, run_idx: int) -> dict:
    """Extract the three timer lines from a single run's captured stdout.

    Fails loudly (raises RuntimeError) if any of the three expected timer
    lines is absent, so a silent parse miss cannot poison the summary.
    """
    m_ext = _RE_EXTRACTION.search(text)
    m_fan = _RE_FAN_OUT.search(text)
    assess_hits = _RE_ASSESS_CALL.findall(text)

    missing = []
    if not m_ext:
        missing.append("extraction_ms")
    if not m_fan:
        missing.append("fan_out_ms")
    if not assess_hits:
        missing.append("assess_call_ms")
    if missing:
        preview = text[:800]
        raise RuntimeError(
            f"Run {run_idx}: missing timer line(s) {missing} in captured "
            f"stdout. Preview:\n{preview!r}\n"
            f"(This means DEBUG was False on the imported binding, the "
            f"timer emit was removed, or output format drifted.)"
        )

    return {
        "extraction_ms": float(m_ext.group(1)),
        "n_reqs": int(m_ext.group(2)),
        "fan_out_ms": float(m_fan.group(1)),
        "assess_call_ms_samples": [float(x) for x, _idx in assess_hits],
    }


def _summarize_arm(arm_runs: list[dict], label: str) -> None:
    print(f"\n=== Concurrency {label} arm ({len(arm_runs)} runs) ===")
    for r in arm_runs:
        samples = r["assess_call_ms_samples"]
        s_mean = statistics.mean(samples)
        s_stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
        print(
            f"  Run {r['run_idx']}: n_reqs={r['n_reqs']} "
            f"assess mean={s_mean:.1f} stdev={s_stdev:.1f} "
            f"min={min(samples):.1f} max={max(samples):.1f} "
            f"(n={len(samples)}) "
            f"| extraction={r['extraction_ms']:.1f}ms "
            f"fan_out={r['fan_out_ms']:.1f}ms"
        )
    pooled = [s for r in arm_runs for s in r["assess_call_ms_samples"]]
    print(
        f"  Arm assess (pooled): mean={statistics.mean(pooled):.1f}ms "
        f"stdev={statistics.stdev(pooled):.1f}ms n={len(pooled)}"
    )
    fan_outs = [r["fan_out_ms"] for r in arm_runs]
    extractions = [r["extraction_ms"] for r in arm_runs]
    n_reqs_set = {r["n_reqs"] for r in arm_runs}
    fan_out_note = (
        ""
        if len(n_reqs_set) == 1
        else f"  (n_reqs varied {sorted(n_reqs_set)}, not directly comparable across arms)"
    )
    print(f"  Arm fan_out mean:    {statistics.mean(fan_outs):.1f}ms{fan_out_note}")
    print(f"  Arm extraction mean: {statistics.mean(extractions):.1f}ms")


def main() -> None:
    if not SEL_JD_PATH.exists():
        raise SystemExit(f"SEL fixture not found: {SEL_JD_PATH}")
    jd_text = SEL_JD_PATH.read_text()
    first_line = jd_text.splitlines()[0].strip()
    if first_line != SEL_JD_EXPECTED_FIRST_LINE:
        raise SystemExit(
            f"SEL fixture first-line mismatch:\n"
            f"  expected: {SEL_JD_EXPECTED_FIRST_LINE!r}\n"
            f"  got:      {first_line!r}\n"
            f"Comparison to prior 22-/23-req runs assumes this JD; refusing "
            f"to proceed against a different one."
        )

    stories = load_stories("echo_star_stories_nlp.jsonl")
    print(f"SEL fixture: {SEL_JD_PATH.name} ({len(jd_text.split())} words)")
    print(f"First line:  {first_line!r}")
    print(f"Corpus:      {len(stories)} stories")
    print(f"config.debug.DEBUG baseline (before probe): {_debug_module.DEBUG}")
    print(f"Run order:   {RUN_ORDER}\n")

    original_concurrency = jd_assessor._CONCURRENCY
    original_jd_debug = jd_assessor.DEBUG
    original_pc_debug = pinecone_service.DEBUG
    jd_assessor.DEBUG = True
    pinecone_service.DEBUG = False

    runs: list[dict] = []
    try:
        for i, concurrency in enumerate(RUN_ORDER):
            jd_assessor._CONCURRENCY = concurrency
            assert jd_assessor._CONCURRENCY == concurrency, (
                f"patch failed on run {i + 1}: "
                f"expected {concurrency}, got {jd_assessor._CONCURRENCY}"
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                jd_assessor.run_assessment(jd_text, stories)
            output = buf.getvalue()

            parsed = _parse_run_output(output, run_idx=i + 1)
            parsed["run_idx"] = i + 1
            parsed["concurrency"] = concurrency
            runs.append(parsed)

            print(
                f"Run {i + 1}/{len(RUN_ORDER)}: "
                f"concurrency={concurrency} "
                f"n_reqs={parsed['n_reqs']} "
                f"extraction={parsed['extraction_ms']:.1f}ms "
                f"fan_out={parsed['fan_out_ms']:.1f}ms "
                f"assess samples={len(parsed['assess_call_ms_samples'])}"
            )
    finally:
        jd_assessor._CONCURRENCY = original_concurrency
        jd_assessor.DEBUG = original_jd_debug
        pinecone_service.DEBUG = original_pc_debug

    arm10 = [r for r in runs if r["concurrency"] == 10]
    arm5 = [r for r in runs if r["concurrency"] == 5]
    _summarize_arm(arm10, "10")
    _summarize_arm(arm5, "5")

    print("\n=== Count variance across all runs ===")
    n_reqs_values = [r["n_reqs"] for r in runs]
    print(f"  n_reqs per run: {n_reqs_values}")
    print(f"  Range: [{min(n_reqs_values)}, {max(n_reqs_values)}]")

    print("\n=== Cross-arm assess_call_ms comparison ===")
    pooled_10 = [s for r in arm10 for s in r["assess_call_ms_samples"]]
    pooled_5 = [s for r in arm5 for s in r["assess_call_ms_samples"]]
    if pooled_10 and pooled_5:
        m10, m5 = statistics.mean(pooled_10), statistics.mean(pooled_5)
        print(f"  Concurrency 10 pooled mean: {m10:.1f}ms (n={len(pooled_10)})")
        print(f"  Concurrency  5 pooled mean: {m5:.1f}ms (n={len(pooled_5)})")
        print(f"  Delta (10 - 5): {m10 - m5:+.1f}ms")
        print(
            "  Contention caveat: this delta is not pure endpoint variance;"
            " it also reflects the contention shift between concurrency"
            " settings on the shared OpenAI endpoint."
        )


if __name__ == "__main__":
    main()
