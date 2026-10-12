"""MATTGPT-282 run 2 (Oct 11, 2026): four arms on gpt-6.1-sol, one interleaved run.
  poc_4oplan  PoC, planner gpt-4o, answerer Sol medium (the 282 Sol arm; control)
  poc_sol     PoC, planner Sol medium, answerer Sol medium
  poc_sollow  PoC, planner Sol low, answerer Sol low
  lever2_sol  lever 2 (send_to_backend), answering calls on Sol medium
Every Sol call streamed (Responses API); each row records each call's resolved
model, effort, usage, time to first output delta, duration, and the turn's time
to first visible token. Subset approved by Matt: c01, c03, c04, c09, c11, c12
(5 runs; c09 10) and x1 to x5 (5 runs); corpus 6ec9aec; same guards and canary
as probe_275_rerun.py. Untracked. Usage: python probes_282b/probe_282b.py <out_dir>
"""
import json
import random
import string
import sys
import time
from pathlib import Path
from unittest.mock import patch

import probe_275_rerun as rr

pc = rr.pc
bs = rr.bs
pc.CORPUS_COMMIT = "6ec9aec"
assert hasattr(pc, "sol_stream") and hasattr(pc, "lever2_sol_create"), "282b probe not loaded"
SUBSET = [1, 3, 4, 9, 11, 12]
RUNS = {n: (10 if n == 9 else 5) for n in SUBSET}
EXTRAS = [e for e in rr.EXTRAS if e[0] != "x6"]
EXTRA_RUNS = 5
ARMS = {
    "poc_4oplan": {"kind": "poc", "planner": "gpt-4o", "effort": "medium"},
    "poc_sol": {"kind": "poc", "planner": "gpt-6.1-sol", "effort": "medium"},
    "poc_sollow": {"kind": "poc", "planner": "gpt-6.1-sol", "effort": "low"},
    "lever2_sol": {"kind": "lever2", "planner": None, "effort": "medium"},
}
MAX_ERRORS = 5
_all = pc.CONVS
ERRORS = []


def configure(arm):
    a = ARMS[arm]
    pc.ANSWER_MODEL = "gpt-6.1-sol"
    pc.LEVER2_MODEL = "gpt-6.1-sol"
    pc.PLANNER_MODEL = a["planner"] or "gpt-4o"
    pc.PLANNER_EFFORT = pc.ANSWER_EFFORT = pc.LEVER2_EFFORT = a["effort"]


def one_turn(arm, q, session, extra):
    configure(arm)
    search_log = []
    kind = ARMS[arm]["kind"]
    ps = pc.patches(session, search_log, "lever2" if kind == "lever2" else "poc")
    if extra:
        ps.append(patch.object(bs, "_nonsense_rejection", lambda *a, **k: None))
    for p in ps:
        p.start()
    pc.CALLS.clear()
    pc.PLANNER_SEEN.clear()
    t0 = time.perf_counter()
    try:
        if kind == "lever2":
            res = bs.send_to_backend(q, {}, None, pc.stories)
            row = {"answer_md": res.get("answer_md") or "", "rejection": res.get("rejection_reason"),
                   "sources": [f"{s.get('title')} ({s.get('client')})" for s in res.get("sources") or []]}
        else:
            row = pc.poc_turn(q, session)
    except Exception as e:  # recorded, scored as a fail; the run goes on (Abort is not an Exception)
        row = {"answer_md": "", "error": f"{type(e).__name__}: {e}"}
    finally:
        for p in reversed(ps):
            p.stop()
    total = time.perf_counter() - t0
    calls = [{**c, "start": round(c["start"] - t0, 3)} for c in pc.CALLS]
    visible = [c for c in calls if c["role"] in ("answer", "lever2")]
    first_visible = None
    if visible and visible[-1]["ttft"] is not None:
        first_visible = round(visible[-1]["start"] + visible[-1]["ttft"], 3)
    elif row.get("plan") and row["plan"]["action"] == "clarify":
        first_visible = round(total, 3)  # rendered by code, no answering call
    row.update({"calls": calls, "first_visible_secs": first_visible, "seconds": round(total, 2), "search_queries": search_log})
    return row


def one_run(arm, case, r, turns, extra):
    session = {"ask_transcript": []}
    rows = []
    for t, q in enumerate(turns, 1):
        session["ask_transcript"].append({"role": "user", "text": q})
        row = one_turn(arm, q, session, extra)
        if session.get("__embed_failure__"):
            raise rr.Abort(f"embed failure flagged on {q!r}")
        row.update({"arm": arm, "case": case, "run": r, "turn": t, "question": q, "nonsense_skipped": extra})
        if row.get("error"):
            ERRORS.append((arm, case, r, t, row["error"]))
            if len(ERRORS) > MAX_ERRORS:
                raise rr.Abort(f"more than {MAX_ERRORS} errors: {ERRORS[-3:]}")
        entry = {"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""}
        if row.get("record"):
            entry["poc_record"] = row["record"]
        session["ask_transcript"].append(entry)
        rows.append(row)
        models = sorted({c["model"] for c in row["calls"]})
        tag = row["plan"]["action"] if row.get("plan") else row.get("error") or row.get("rejection") or "lever2"
        print(f"[{arm} {case} r{r} t{t}] {row['seconds']}s fv={row['first_visible_secs']} {tag} {models} | {(row['answer_md'] or '')[:50]!r}", flush=True)
    return rows


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    assert pc.checks(), "pre-run checks failed"
    pc.CONVS = {n: _all[n] for n in SUBSET}
    cases = [(f"c{n:02d}", RUNS[n], pc.CONVS[n]["turns"], False) for n in SUBSET]
    cases += [(cid, EXTRA_RUNS, [q], True) for cid, _label, q in EXTRAS]
    assert all(None not in turns for *_x, turns, _e in cases), "no seeded turns in this subset"
    names = list(ARMS)
    rows = {a: [] for a in names}
    live = 0
    for p in rr.GUARDS:
        p.start()
    try:
        rr.canary("before")
        for case, runs, turns, extra in cases:
            for r in range(1, runs + 1):
                k = r % len(names)
                for arm in names[k:] + names[:k]:
                    got = one_run(arm, case, r, turns, extra)
                    rows[arm] += got
                    before = live
                    live += len(got)
                    if live // 50 > before // 50:
                        rr.canary(f"after {live} turns")
                    for a in rows:
                        (out / f"{a}.json").write_text(json.dumps(rows[a], indent=2, ensure_ascii=False))
        rr.canary("after")
    finally:
        for p in reversed(rr.GUARDS):
            p.stop()
    print("done | live turns:", live, "| errors:", ERRORS, flush=True)
    packets(out, rows)


def packets(out, rows):
    pdir = out / "packets"
    pdir.mkdir(exist_ok=True)
    rng = random.Random(2822)
    key = {}
    by = {}
    for arm, rs in rows.items():
        for x in rs:
            by.setdefault((x["case"], x["run"]), {}).setdefault(arm, []).append(x)
    titles = {c: l for c, l, _ in EXTRAS}
    letters = list(string.ascii_uppercase[:len(ARMS)])
    for (case, r), arms in sorted(by.items()):
        order = list(ARMS)
        rng.shuffle(order)
        name = f"{case}_r{r:02d}"
        key[name] = dict(zip(letters, order))
        title = f"Conversation {int(case[1:])}" if case.startswith("c") else f"Extra {case} ({titles[case]})"
        lines = [f"# {title}, run {r}", ""]
        per = {lab: sorted(arms[arm], key=lambda x: x["turn"]) for lab, arm in zip(letters, order)}
        for i, tx in enumerate(per["A"]):
            lines += [f"## Turn {tx['turn']}. Visitor: {tx['question']}", ""]
            for lab in letters:
                lines += [f"### {lab}", "", per[lab][i].get("answer_md") or "(no answer)", ""]
        (pdir / f"{name}.md").write_text("\n".join(lines))
    (out / "key").mkdir(exist_ok=True)
    (out / "key" / "key.json").write_text(json.dumps(key, indent=2))
    print("packets:", len(key), flush=True)


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]))
    except rr.Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
