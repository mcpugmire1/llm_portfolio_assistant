"""MATTGPT-320 extras (Oct 16, 2026; untracked probe), run inside the frozen
checkout of 3d1f63d next to probe_275_gate.py (REPO resolves to the checkout).

Two runs of:
- MATTGPT-250's acceptance queries (11 single turns);
- MATTGPT-253's formerly refused single queries (4);
- MATTGPT-253's follow-ups inside their fixture conversations (fixture
  609f903): c02, c03, c04 (t3 asked as "Are any of those current", no
  question mark), c05, c06;
- MATTGPT-250's Role Match equivalence note: one requirement through
  retrieve_stories() and assess_requirement() (gpt-4o), per run.
Ask Agy turns go through probe_275_gate.new_turn(): send_to_backend() ->
agy_answer(), loggers patched, raw text, usage and searches recorded.
Usage: python probes/probe_320_extras.py <out_dir>
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_275_gate as g  # noqa: E402  (reads sys.argv[1] as the out dir)

RUNS = 2
SINGLE = [
    ("250", "Is Matt certified?"),
    ("250", "Does Matt have a PMP?"),
    ("250", "What languages does Matt speak?"),
    ("250", "Does Matt speak French?"),
    ("250", "Does Matt have a master's degree?"),
    ("250", "Does Matt have any patents?"),
    ("250-control", "Tell me about Matt's payments work at JPMorgan"),
    ("250-control", "What's Matt's leadership philosophy?"),
    ("250-control", "Why hire Matt?"),
    ("250-control", "Tell me about a time Matt failed"),
    ("250-control", "How did Matt build the AWS certification program?"),
    ("253", "Where does Matt live?"),
    ("253", "Where did Matt get his degree?"),
    ("253", "What did Matt study in college?"),
    ("253", "where's he based these days"),
]
CONVERSATIONS = ["c02", "c03", "c04", "c05", "c06"]
RM_REQUIREMENT = "Bachelor's degree in Computer Science or a related field"


def conversation_turns(case):
    turns = list(g.CASES[case])
    if case == "c04":
        assert turns[2] == "Are any of those current?", turns
        turns[2] = "Are any of those current"
    return turns


def run_conversation(case, r):
    session = {"ask_transcript": []}
    rows = []
    for t, q in enumerate(conversation_turns(case), 1):
        assert q is not None, (case, t)
        session["ask_transcript"].append({"role": "user", "text": q})
        row = g.new_turn("new", q, session, False)
        row.update({"kind": "conversation", "case": case, "run": r, "turn": t, "question": q})
        session["ask_transcript"].append({"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""})
        rows.append(row)
        print(f"[{case} r{r} t{t}] {row['seconds']}s | {(row['answer_md'] or '')[:60]!r}", flush=True)
    return rows


def run_role_match(r):
    from services import jd_assessor

    t0 = time.perf_counter()
    client = jd_assessor._get_openai_client()
    candidates = jd_assessor.retrieve_stories(RM_REQUIREMENT, g.STORIES)
    result = jd_assessor.assess_requirement(client, RM_REQUIREMENT, candidates)
    row = {"kind": "role_match", "run": r, "requirement": RM_REQUIREMENT,
           "candidates": [c.get("title") for c in candidates], "result": result,
           "seconds": round(time.perf_counter() - t0, 2)}
    print(f"[role match r{r}] {row['seconds']}s | {json.dumps(result)[:120]}", flush=True)
    return row


def main():
    g.canary("start")
    rows = []
    for r in range(1, RUNS + 1):
        for source, q in SINGLE:
            session = {"ask_transcript": [{"role": "user", "text": q}]}
            row = g.new_turn("new", q, session, False)
            row.update({"kind": "single", "source": source, "run": r, "question": q})
            rows.append(row)
            print(f"[{source} r{r}] {row['seconds']}s {q} | {(row['answer_md'] or '')[:60]!r}", flush=True)
        for case in CONVERSATIONS:
            rows += run_conversation(case, r)
        rows.append(run_role_match(r))
        (g.OUT / "rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    g.canary("end")
    print(f"done | rows {len(rows)}", flush=True)


if __name__ == "__main__":
    main()
