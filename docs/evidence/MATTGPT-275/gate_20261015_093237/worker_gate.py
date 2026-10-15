"""MATTGPT-275 gate run (Oct 14, 2026): run 2's frozen lever2_sol arm as a
worker the gate driver calls one (case, run) at a time, so the baseline is
interleaved with the new arms. Reuses probe_282b.one_turn() unchanged
(lever2_sol config, loggers patched, call recording); adds only the seeded
turn of conversation 17, as probe_275_rerun.one_run() handled it for lever 2.
Protocol: one JSON job per stdin line, one JSON result per stdout line;
everything the probe prints goes to stderr. Untracked.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
PROTO = sys.stdout
sys.stdout = sys.stderr
import probe_282b as b  # noqa: E402

rr, pc, ARM = b.rr, b.pc, "lever2_sol"


def run(job):
    conv = pc.CONVS[int(job["case"][1:])] if job["case"].startswith("c") else None
    turns = conv["turns"] if conv else [job["question"]]
    extra = conv is None
    session = {"ask_transcript": []}
    rows = []
    for t, q in enumerate(turns, 1):
        base = {"arm": "baseline", "case": job["case"], "run": job["run"], "turn": t}
        if q is None:
            entry = pc.seed_entry(conv, "lever2")
            session["ask_transcript"].append(entry)
            rows.append({**base, "question": None, "answer_md": entry["text"], "seeded": True})
            continue
        session["ask_transcript"].append({"role": "user", "text": q})
        row = b.one_turn(ARM, q, session, extra)
        if session.get("__embed_failure__"):
            raise rr.Abort(f"embed failure flagged on {q!r}")
        row.update({**base, "question": q, "nonsense_skipped": extra})
        session["ask_transcript"].append({"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""})
        rows.append(row)
        print(f"[baseline {job['case']} r{job['run']} t{t}] {row['seconds']}s {row.get('error') or ''}| {(row['answer_md'] or '')[:50]!r}", flush=True)
    return rows


def main():
    assert pc.checks(), "pre-run checks failed"
    for p in rr.GUARDS:
        p.start()
    try:
        rr.canary("worker start")
        PROTO.write(json.dumps({"ready": True}) + "\n")
        PROTO.flush()
        for line in sys.stdin:
            job = json.loads(line)
            if job.get("stop"):
                break
            try:
                out = {"ok": True, "rows": run(job)}
            except rr.Abort as e:
                out = {"ok": False, "abort": str(e)}
            PROTO.write(json.dumps(out, ensure_ascii=False) + "\n")
            PROTO.flush()
            if not out["ok"]:
                break
        rr.canary("worker end")
    finally:
        for p in reversed(rr.GUARDS):
            p.stop()


if __name__ == "__main__":
    main()
