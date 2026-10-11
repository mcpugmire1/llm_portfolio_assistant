"""MATTGPT-275 rerun (Oct 11, 2026): the approved clean PoC vs lever 2
(probe_275_poc_clean.py, imported unchanged) plus the five amendments Matt
approved:
  1. corpus 5620dfc and the egress fix (3d0da24) in this worktree, both arms;
  2. sequential, one process, arms interleaved per (case, run), order
     alternating by run number;
  3. abort on Pinecone None/[], local fallback, a failed synthesis theme query,
     _degraded_fallback, or an embed failure; health check before, every 50
     turns, and after;
  4. MATTGPT-251 extras, single-turn, 5 runs each, nonsense filter skipped in
     both arms (the frozen tree has the pre-MATTGPT-285 rules);
  5. blind A/B packets with the key in a separate file.
Untracked. Usage: python probes/probe_275_rerun.py <out_dir>
"""
import json
import random
import sys
import time
from pathlib import Path
from unittest.mock import patch

import probe_275_poc_clean as pc

pc.CORPUS_COMMIT = "5620dfc"
from services import pinecone_service, query_logger, rag_service  # noqa: E402

bs = pc.bs
EXTRAS = [
    ("x1", "real estate", "Has Matt worked in real estate?"),
    ("x2", "SAP", "Has Matt worked with SAP?"),
    ("x3", "trading platforms", "Has Matt worked on trading platforms?"),
    ("x4", "ROI", "How did Matt calculate ROI?"),
    ("x5", "gaming", "Has Matt worked on gaming platforms?"),
    ("x6", "capital markets", "Has Matt worked on capital markets platforms?"),
]
EXTRA_RUNS = 5


class Abort(BaseException):
    """Not an Exception, so no except-Exception in the pipeline or probe swallows it."""


_real_pcs = rag_service.pinecone_semantic_search
_real_semantic = pc._real_search
_real_init = bs._init_pinecone
_real_synth = bs.get_synthesis_stories


def pcs_guard(q, *a, **k):
    h = _real_pcs(q, *a, **k)
    if not h:
        raise Abort(f"Pinecone returned {h!r} for {q!r}")
    return h


def semantic_guard(q, *a, **k):
    r = _real_semantic(q, *a, **k)
    if str(r.get("reason") or "").startswith("fallback"):
        raise Abort(f"local fallback ({r.get('reason')}) for {q!r}")
    return r


class IdxProxy:
    def __init__(self, idx):
        self._idx = idx

    def query(self, *a, **k):
        try:
            return self._idx.query(*a, **k)
        except Exception as e:
            raise Abort(f"synthesis theme query failed: {type(e).__name__}: {e}")

    def __getattr__(self, name):
        return getattr(self._idx, name)


def init_guard(*a, **k):
    idx = _real_init(*a, **k)
    if not idx:
        raise Abort("_init_pinecone returned no index")
    return IdxProxy(idx)


def synth_guard(*a, **k):
    r = _real_synth(*a, **k)
    if not r:
        raise Abort("get_synthesis_stories returned no stories")
    return r


def degraded(*a, **k):
    raise Abort("_degraded_fallback called")


pc._real_search = semantic_guard  # pc.patches() wraps bs.semantic_search with this
GUARDS = [
    patch.object(rag_service, "pinecone_semantic_search", pcs_guard),
    patch.object(bs, "_init_pinecone", init_guard),
    patch.object(bs, "get_synthesis_stories", synth_guard),
    patch.object(bs, "_degraded_fallback", degraded),
    patch.object(query_logger, "get_sheet", lambda *a, **k: None),
]


def canary(label):
    h = pinecone_service.pinecone_semantic_search("Fiserv white-label card portal", {}, pc.stories, top_k=25)
    if not h or h[0]["story"]["Client"] != "Fiserv":
        raise Abort(f"health check failed ({label})")
    print(f"health check {label}: top Fiserv {h[0]['pc_score']:.3f}", flush=True)


def one_run(arm, case, r, turns, conv=None, extra=False):
    session = {"ask_transcript": []}
    rows = []
    for t, q in enumerate(turns, 1):
        if q is None:
            entry = pc.seed_entry(conv, arm)
            session["ask_transcript"].append(entry)
            rows.append({"arm": arm, "case": case, "run": r, "turn": t, "question": None,
                         "answer_md": entry["text"], "seeded": True})
            continue
        session["ask_transcript"].append({"role": "user", "text": q})
        search_log = []
        ps = pc.patches(session, search_log, arm)
        if extra:
            ps.append(patch.object(bs, "_nonsense_rejection", lambda *a, **k: None))
        for p in ps:
            p.start()
        t0 = time.time()
        try:
            if arm == "lever2":
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
        if session.get("__embed_failure__"):
            raise Abort(f"embed failure flagged on {q!r}")
        row.update({"arm": arm, "case": case, "run": r, "turn": t, "question": q, "nonsense_skipped": extra,
                    "search_queries": search_log, "seconds": round(time.time() - t0, 2)})
        entry = {"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""}
        if arm == "poc" and row.get("record"):
            entry["poc_record"] = row["record"]
        session["ask_transcript"].append(entry)
        rows.append(row)
        tag = f"{row['raw_plan']['turn_type']} {row['plan']['action']}" if row.get("plan") else row.get("error", "")
        print(f"[{arm} {case} r{r} t{t}] {row['seconds']}s {tag} | {(row['answer_md'] or '')[:60]!r}", flush=True)
    return rows


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    assert pc.checks(), "pre-run checks failed"
    cases = [(f"c{n:02d}", pc.RUNS[n], pc.CONVS[n]["turns"], pc.CONVS[n], False) for n in sorted(pc.CONVS)]
    cases += [(cid, EXTRA_RUNS, [q], None, True) for cid, _label, q in EXTRAS]
    rows = {"lever2": [], "poc": []}
    live = 0
    for p in GUARDS:
        p.start()
    try:
        canary("before")
        for case, runs, turns, conv, extra in cases:
            for r in range(1, runs + 1):
                order = ["lever2", "poc"] if r % 2 else ["poc", "lever2"]
                for arm in order:
                    got = one_run(arm, case, r, turns, conv, extra)
                    rows[arm] += got
                    before = live
                    live += sum(1 for x in got if not x.get("seeded"))
                    if live // 50 > before // 50:
                        canary(f"after {live} turns")
                    for a in rows:
                        (out / f"{a}.json").write_text(json.dumps(rows[a], indent=2, ensure_ascii=False))
        canary("after")
    finally:
        for p in reversed(GUARDS):
            p.stop()
    print("done | live turns:", live, "| splits", dict(pc.SPLITS), flush=True)
    packets(out, rows)


def packets(out, rows):
    pdir = out / "packets"
    pdir.mkdir(exist_ok=True)
    rng = random.Random(275)
    key = {}
    by = {}
    for arm, rs in rows.items():
        for x in rs:
            by.setdefault((x["case"], x["run"]), {}).setdefault(arm, []).append(x)
    for (case, r), arms in sorted(by.items()):
        labels = ["lever2", "poc"]
        rng.shuffle(labels)
        name = f"{case}_r{r:02d}"
        key[name] = {"A": labels[0], "B": labels[1]}
        title = f"Conversation {int(case[1:])}" if case.startswith("c") else f"Extra {case} ({dict((c, l) for c, l, _ in EXTRAS)[case]})"
        lines = [f"# {title}, run {r}", ""]
        turns = sorted(arms[labels[0]], key=lambda x: x["turn"])
        for i, tx in enumerate(turns):
            if tx.get("seeded"):
                lines += [f"## Turn {tx['turn']}. Seeded assistant answer (given, not scored)", "", tx["answer_md"], ""]
                continue
            lines += [f"## Turn {tx['turn']}. Visitor: {tx['question']}", ""]
            for lab, arm in (("A", labels[0]), ("B", labels[1])):
                ans = sorted(arms[arm], key=lambda x: x["turn"])[i].get("answer_md") or "(no answer)"
                lines += [f"### {lab}", "", ans, ""]
        (pdir / f"{name}.md").write_text("\n".join(lines))
    (out / "key").mkdir(exist_ok=True)
    (out / "key" / "key.json").write_text(json.dumps(key, indent=2))
    print("packets:", len(key), flush=True)


if __name__ == "__main__":
    try:
        main(Path(sys.argv[1]))
    except Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
