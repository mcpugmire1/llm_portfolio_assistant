"""MATTGPT-236 gate run (Oct 16, 2026; untracked probe). Three arms of the
shipped pipeline, interleaved run by run within each (case, run):

  A  as shipped: the router's redirects and its synthesis pick
  B  router off: is_portfolio_query_semantic() returns an empty family, so no
     redirect and the standard prompt on every question
  C  personal redirect only: the router runs; a personal family passes
     through (redirected at HARD_ACCEPT, as shipped), any other family is
     returned empty (no out_of_scope redirect, no synthesis pick)

Every arm runs send_to_backend() -> agy_answer() unchanged; the arms differ
only in what the patched is_portfolio_query_semantic() returns. Each row
records the router's real answer (family, score) and what the arm passed on.

Cases: the 275 gate's 45 live turns (probe_275_gate.CASES; x1 to x7 bypass
the nonsense rules as in that gate) plus the router set r01 to r16 from
probe_236_step0.ROUTER_SET (nonsense rules on, as in production). 10 runs.
Loggers, the Pinecone health check, the search-fallback and embed-failure
aborts, and the per-call recording all come from probe_275_gate.new_turn().
A redirected turn records the reason the UI renders its banner from.

Lanes: LANE=i/N runs every Nth (case, run) job. Usage:
  LANE=0/7 python probes/probe_236_gate.py <out_dir>
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)
from probe_236_step0 import ROUTER_SET  # noqa: E402

from services import semantic_router  # noqa: E402

RUNS = 10
ARMS = ["A", "B", "C"]
CASES = dict(g.CASES)
CASES.update({f"r{i:02d}": [q] for i, (_kind, q) in enumerate(ROUTER_SET, 1)})
assert sum(1 for t in CASES.values() for q in t if q is not None) == 61
ROUTER = {}
_real_router = g.bs.is_portfolio_query_semantic


def arm_router(arm):
    def router(q, *args, **kwargs):
        valid, score, matched, family = _real_router(q, *args, **kwargs)
        ROUTER["real"] = {"family": family, "score": round(score, 3), "matched": matched}
        if arm == "B" or (arm == "C" and family != "personal"):
            family = ""
        ROUTER["passed"] = family
        return valid, score, matched, family

    return router


def run_case(arm, case, r):
    session = {"ask_transcript": []}
    extra = case.startswith("x")
    rows = []
    for t, q in enumerate(CASES[case], 1):
        base = {"arm": arm, "case": case, "run": r, "turn": t}
        if q is None:
            entry = g.seed_entry(case)
            session["ask_transcript"].append(entry)
            rows.append({**base, "question": None, "answer_md": entry["text"], "seeded": True})
            continue
        session["ask_transcript"].append({"role": "user", "text": q})
        session.pop("ask_last_reason", None)
        ROUTER.clear()
        with patch.object(g.bs, "is_portfolio_query_semantic", arm_router(arm)):
            row = g.new_turn(arm, q, session, extra)
        row.update({
            **base, "question": q, "nonsense_skipped": extra,
            "router_real": ROUTER.get("real"), "router_passed": ROUTER.get("passed"),
            "ui_reason": session.get("ask_last_reason"),
        })
        session["ask_transcript"].append({"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""})
        rows.append(row)
        print(f"[{arm} {case} r{r} t{t}] {row['seconds']}s {row.get('error') or row.get('rejection') or ''}"
              f" | {(row['answer_md'] or '')[:50]!r}", flush=True)
    return rows


def main():
    # Pre-flight: each arm passes on what it should, without a model call.
    with patch.object(semantic_router, "_log_borderline", lambda *a, **k: None), \
         patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None):
        for arm, q, want in [
            ("A", "Why hire Matt?", "synthesis"), ("B", "Why hire Matt?", ""), ("C", "Why hire Matt?", ""),
            ("A", "Is Matt married?", "personal"), ("B", "Is Matt married?", ""), ("C", "Is Matt married?", "personal"),
            ("A", "Has Matt worked in retail?", "out_of_scope"), ("C", "Has Matt worked in retail?", ""),
        ]:
            got = arm_router(arm)(q)[3]
            assert got == want, (arm, q, got, want)
    jobs = [(c, r) for c in CASES for r in range(1, RUNS + 1)]
    mine = jobs[g.LANE::g.LANES]
    if os.environ.get("SMOKE_JOBS"):  # smoke test only; the gate run never sets it
        mine = [(c, int(r)) for c, r in (j.split(":") for j in os.environ["SMOKE_JOBS"].split(","))]
    print(f"lane {g.LANE}/{g.LANES}: {len(mine)} of {len(jobs)} (case, run) jobs", flush=True)
    rows, errors = [], []
    g.canary("start")
    for case, r in mine:
        k = r % len(ARMS)
        for arm in ARMS[k:] + ARMS[:k]:
            got = run_case(arm, case, r)
            rows += got
            errors += [(arm, case, r, x["turn"], x["error"]) for x in got if x.get("error")]
            if len(errors) > g.MAX_ERRORS:
                raise g.Abort(f"more than {g.MAX_ERRORS} errors: {errors[-3:]}")
            (g.OUT / f"rows_lane{g.LANE}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    g.canary("end")
    print(f"done | rows {len(rows)} | errors {errors}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except g.Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
