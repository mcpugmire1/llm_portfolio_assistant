"""MATTGPT-282 probe (Oct 11, 2026): the current PoC (fixes rerun 2, frozen
e4426f5) with only the answering model varied: gpt-4o (Chat Completions, as
before) vs gpt-6.1-sol (Responses API, default reasoning effort). Planner
gpt-4o in both arms. Subset approved by Matt: c03, c04, c09, x3, x4, plus c12
and x1 as no-regress controls; 10 runs each, both arms, interleaved, same
guards and canary as probe_275_rerun.py, corpus 6ec9aec. Each row records the
resolved model (response.model) and token usage of the answering and planner
calls. Untracked. Usage: python probes_282/probe_282.py <out_dir>
"""
import json
import random
import sys
import time
from pathlib import Path
from unittest.mock import patch

import probe_275_rerun as rr

pc = rr.pc
bs = rr.bs
pc.CORPUS_COMMIT = "6ec9aec"
assert hasattr(pc, "answer_call") and hasattr(pc, "GAP_RULE"), "282 probe not loaded"
SUBSET = [3, 4, 9, 12]
EXTRAS = [e for e in rr.EXTRAS if e[0] in ("x1", "x3", "x4")]
RUNS = 10
ARMS = {"poc4o": "gpt-4o", "pocsol": "gpt-6.1-sol"}
_all = pc.CONVS


def one_run(arm, case, r, turns, extra):
    pc.ANSWER_MODEL = ARMS[arm]
    session = {"ask_transcript": []}
    rows = []
    for t, q in enumerate(turns, 1):
        session["ask_transcript"].append({"role": "user", "text": q})
        search_log = []
        ps = pc.patches(session, search_log, "poc")
        if extra:
            ps.append(patch.object(bs, "_nonsense_rejection", lambda *a, **k: None))
        for p in ps:
            p.start()
        t0 = time.time()
        pc.PLANNER_SEEN.clear()
        try:
            row = pc.poc_turn(q, session)
        except Exception as e:  # recorded, scored as a fail; the run goes on (Abort is not an Exception)
            row = {"answer_md": "", "error": f"{type(e).__name__}: {e}"}
        finally:
            for p in reversed(ps):
                p.stop()
        if session.get("__embed_failure__"):
            raise rr.Abort(f"embed failure flagged on {q!r}")
        row.update({"arm": arm, "case": case, "run": r, "turn": t, "question": q, "nonsense_skipped": extra,
                    "search_queries": search_log, "seconds": round(time.time() - t0, 2)})
        entry = {"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""}
        if row.get("record"):
            entry["poc_record"] = row["record"]
        session["ask_transcript"].append(entry)
        rows.append(row)
        tag = f"{row['plan']['action']} {row.get('answer_model_resolved')}" if row.get("plan") else row.get("error", row.get("rejection", ""))
        print(f"[{arm} {case} r{r} t{t}] {row['seconds']}s {tag} | {(row['answer_md'] or '')[:60]!r}", flush=True)
    return rows


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    assert pc.checks(), "pre-run checks failed"
    pc.CONVS = {n: _all[n] for n in SUBSET}
    cases = [(f"c{n:02d}", pc.CONVS[n]["turns"], False) for n in SUBSET]
    cases += [(cid, [q], True) for cid, _label, q in EXTRAS]
    assert all(None not in turns for _c, turns, _e in cases), "no seeded turns in this subset"
    rows = {a: [] for a in ARMS}
    live = 0
    for p in rr.GUARDS:
        p.start()
    try:
        rr.canary("before")
        for case, turns, extra in cases:
            for r in range(1, RUNS + 1):
                order = list(ARMS) if r % 2 else list(ARMS)[::-1]
                for arm in order:
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
    print("done | live turns:", live, flush=True)
    packets(out, rows)


def packets(out, rows):
    pdir = out / "packets"
    pdir.mkdir(exist_ok=True)
    rng = random.Random(282)
    key = {}
    by = {}
    for arm, rs in rows.items():
        for x in rs:
            by.setdefault((x["case"], x["run"]), {}).setdefault(arm, []).append(x)
    titles = {c: l for c, l, _ in EXTRAS}
    for (case, r), arms in sorted(by.items()):
        labels = list(ARMS)
        rng.shuffle(labels)
        name = f"{case}_r{r:02d}"
        key[name] = {"A": labels[0], "B": labels[1]}
        title = f"Conversation {int(case[1:])}" if case.startswith("c") else f"Extra {case} ({titles[case]})"
        lines = [f"# {title}, run {r}", ""]
        a_turns = sorted(arms[labels[0]], key=lambda x: x["turn"])
        b_turns = sorted(arms[labels[1]], key=lambda x: x["turn"])
        for ta, tb in zip(a_turns, b_turns):
            lines += [f"## Turn {ta['turn']}. Visitor: {ta['question']}", ""]
            for lab, tx in (("A", ta), ("B", tb)):
                lines += [f"### {lab}", "", tx.get("answer_md") or "(no answer)", ""]
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
