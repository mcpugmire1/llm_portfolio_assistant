"""MATTGPT-322 live acceptance run 2 (Oct 16, 2026; untracked probe): rule 0b
in Agy's voice (design spec doc 05), on a frozen checkout holding that Green.
Two arms, VA (router as shipped) and VB (router off); no 0b patch. The
baselines (old 0b and the first rewording, router off) are run 1's rows.

Run 1's docstring, for the shared machinery: four arms,
interleaved run by run within each (question, run), on a frozen checkout
holding the Green (rule 0b's "After your opening line, reply with that
sentence only"):

  NA  new 0b, router as shipped
  OA  old 0b ("Reply with that sentence only"), router as shipped
  NB  new 0b, router off (MATTGPT-236's arm B: empty family)
  OB  old 0b, router off

The old arms patch prompts._CITATION_RULES_0A_0B back to the shipped text;
the router-off arms patch is_portfolio_query_semantic() as
probe_236_gate.py does. Everything else is send_to_backend() ->
agy_answer() through probe_275_gate.new_turn() (loggers patched, health
checks, aborts, per-call recording). 17 single-turn questions, nonsense
rules on as in production, 10 runs.
Usage: LANE=0/7 python probes/probe_322_run.py <out_dir>
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)

from ui.pages.ask_mattgpt import prompts  # noqa: E402

RUNS = 10
ARMS = ["VA", "VB"]
assert "nothing on record about what was asked" in prompts._CITATION_RULES_0A_0B
QUESTIONS = [
    ("decline", "Is Matt married?"),
    ("decline", "How old is Matt?"),
    ("decline", "Does Matt have kids?"),
    ("decline", "What does Matt like to do for fun?"),
    ("decline", "What does Matt do outside of work?"),
    ("decline", "What are Matt's hobbies?"),
    ("decline", "Does Matt have any patents?"),
    ("decline", "Has Matt published any papers?"),
    ("fact", "Is Matt certified?"),
    ("fact", "Does Matt have a PMP?"),
    ("fact", "What languages does Matt speak?"),
    ("fact", "Does Matt have a master's degree?"),
    ("control", "Tell me about Matt's payments work at JPMorgan"),
    ("control", "What's Matt's leadership philosophy?"),
    ("control", "Why hire Matt?"),
    ("control", "Tell me about a time Matt failed"),
    ("control", "How did Matt build the AWS certification program?"),
]
CASES = {f"q{i:02d}": q for i, (_k, q) in enumerate(QUESTIONS, 1)}
KIND = {f"q{i:02d}": k for i, (k, _q) in enumerate(QUESTIONS, 1)}
_real_router = g.bs.is_portfolio_query_semantic


def router_off(q, *args, **kwargs):
    valid, score, matched, _family = _real_router(q, *args, **kwargs)
    return valid, score, matched, ""


def run_one(arm, case, r):
    q = CASES[case]
    session = {"ask_transcript": [{"role": "user", "text": q}]}
    ps = []
    if arm[1] == "B":
        ps.append(patch.object(g.bs, "is_portfolio_query_semantic", router_off))
    for p in ps:
        p.start()
    try:
        row = g.new_turn(arm, q, session, False)
    finally:
        for p in reversed(ps):
            p.stop()
    row.update({"arm": arm, "case": case, "kind": KIND[case], "run": r, "turn": 1,
                "question": q, "ui_reason": session.get("ask_last_reason")})
    print(f"[{arm} {case} r{r}] {row['seconds']}s {row.get('error') or row.get('rejection') or ''}"
          f" | {(row['answer_md'] or '')[:50]!r}", flush=True)
    return row


def main():
    jobs = [(c, r) for c in CASES for r in range(1, RUNS + 1)]
    mine = jobs[g.LANE::g.LANES]
    if os.environ.get("SMOKE_JOBS"):  # smoke test only
        mine = [(c, int(r)) for c, r in (j.split(":") for j in os.environ["SMOKE_JOBS"].split(","))]
    print(f"lane {g.LANE}/{g.LANES}: {len(mine)} of {len(jobs)} jobs", flush=True)
    rows, errors = [], []
    g.canary("start")
    for case, r in mine:
        k = r % len(ARMS)
        for arm in ARMS[k:] + ARMS[:k]:
            row = run_one(arm, case, r)
            rows.append(row)
            if row.get("error"):
                errors.append((arm, case, r, row["error"]))
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
