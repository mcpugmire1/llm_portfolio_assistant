"""MATTGPT-322 probe run 7 (Oct 17, 2026; untracked probe): does the decline
line hold inside a conversation? Same frozen Green as run 6 ("Begin with
this line", two lines), router off, three turns per conversation through
send_to_backend() with history, the transcript built as the app builds it
(push_user_turn: {"role": "user"}; push_conversational_answer: {"Role":
"assistant", "text": answer_md}).

  R  repeat: "Does Matt have any patents?" three times (the browser check)
  M  mix: JPMorgan payments story, then hobbies, then patents

10 conversations each. The real _choose_decline_line() is wrapped to record
each turn's assigned line; the model's input is unchanged by the wrapper.
Run 6's machinery otherwise (probe_275_gate.new_turn: loggers patched,
health checks, aborts).
Usage: LANE=0/5 python probes/probe_322g_run.py <out_dir>
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)

from ui.pages.ask_mattgpt import prompts  # noqa: E402

RUNS = 10
assert len(g.bs.DECLINE_LINES) == 2
assert "Begin with this line, filling in the topic" in prompts.build_answer_instructions(
    "x", False, decline_line="y"
)
PATENTS = "Does Matt have any patents?"
CONVERSATIONS = {
    "R": [("decline", PATENTS), ("decline", PATENTS), ("decline", PATENTS)],
    "M": [
        ("control", "Tell me about Matt's payments work at JPMorgan"),
        ("decline", "What are Matt's hobbies?"),
        ("decline", PATENTS),
    ],
}
_real_router = g.bs.is_portfolio_query_semantic
_real_decline = g.bs._choose_decline_line


def router_off(q, *args, **kwargs):
    valid, score, matched, _family = _real_router(q, *args, **kwargs)
    return valid, score, matched, ""


def run_conversation(conv, r):
    session = {"ask_transcript": []}
    rows = []
    for t, (kind, q) in enumerate(CONVERSATIONS[conv], 1):
        session["ask_transcript"].append({"role": "user", "text": q})
        assigned = []

        def record_decline():
            line = _real_decline()
            assigned.append(line)
            return line

        ps = [
            patch.object(g.bs, "_choose_decline_line", record_decline),
            patch.object(g.bs, "is_portfolio_query_semantic", router_off),
        ]
        for p in ps:
            p.start()
        try:
            row = g.new_turn(conv, q, session, False)
        finally:
            for p in reversed(ps):
                p.stop()
        row.update({"arm": conv, "conv": conv, "case": f"{conv}t{t}", "kind": kind, "run": r,
                    "turn": t, "question": q, "ui_reason": session.get("ask_last_reason"),
                    "history_messages": len(session["ask_transcript"]) - 1,
                    "decline_line": assigned[0] if len(assigned) == 1 else assigned})
        if row.get("answer_md"):
            session["ask_transcript"].append({"Role": "assistant", "text": row["answer_md"]})
        print(f"[{conv} r{r} t{t}] {row['seconds']}s {row.get('error') or row.get('rejection') or ''}"
              f" | {(row['answer_md'] or '')[:60]!r}", flush=True)
        rows.append(row)
    return rows


def main():
    jobs = [(c, r) for c in CONVERSATIONS for r in range(1, RUNS + 1)]
    mine = jobs[g.LANE::g.LANES]
    print(f"lane {g.LANE}/{g.LANES}: {len(mine)} of {len(jobs)} conversations", flush=True)
    rows, errors = [], []
    g.canary("start")
    for conv, r in mine:
        for row in run_conversation(conv, r):
            rows.append(row)
            if row.get("error"):
                errors.append((conv, r, row["turn"], row["error"]))
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
