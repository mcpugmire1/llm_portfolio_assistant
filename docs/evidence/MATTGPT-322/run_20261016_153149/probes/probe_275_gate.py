"""MATTGPT-275 gate run (Oct 14, 2026; untracked probe). Three arms, interleaved
run by run within each (case, run):

  new       the working tree's send_to_backend() -> agy_answer(), as shipped
  opener    the same, with build_tool_system_prompt()'s examples line replaced
            in memory by "Start your response with this exact text: {opening}",
            the opener agy_answer() already picks in _choose_opening_and_focus()
  baseline  run 2's frozen lever2_sol (worktree b55f9ce plus its probe diff),
            through probes_282b/worker_gate.py in that worktree

Cases: fixture conversations 1 to 18 (609f903; conversation 17's first turn is
the seeded answer) and the extras x1 to x5 and x7: 45 live turns. new and
opener run 10 times on every case. baseline runs where run 2 left no count
out of 10: runs 1 to 10 on the conversations run 2 didn't cover and on x7,
runs 6 to 10 on run 2's five-run cases, none on conversation 9.

As run 2 did, the extras bypass the nonsense rules on every arm; each extra
row also records what is_nonsense() returns for it in production.
Loggers patched on every arm: log_query, log_offdomain, _log_borderline,
_log_router_low_confidence, and the query logger's sheet. A Pinecone health
check runs at start and end; a search fallback or an embed failure aborts.
Every answering call's raw model text and usage are recorded.

Lanes: LANE=i/N runs every Nth (case, run) job. Usage:
  LANE=0/4 python probes/probe_275_gate.py <out_dir>
"""

import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parents[1]
FROZEN = REPO.parent / "llm_portfolio_assistant-l2frozen"
sys.path.insert(0, str(REPO))

from services import pinecone_service, query_logger, semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from utils.validation import is_nonsense  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
LANE, LANES = (int(x) for x in os.environ.get("LANE", "0/1").split("/"))
FIXTURE_COMMIT = "609f903"
RUNS = 10
MAX_ERRORS = 5
EXTRAS = [
    ("x1", "Has Matt worked in real estate?"),
    ("x2", "Has Matt worked with SAP?"),
    ("x3", "Has Matt worked on trading platforms?"),
    ("x4", "How did Matt calculate ROI?"),
    ("x5", "Has Matt worked on gaming platforms?"),
    ("x7", "When was he at JP Morgan?"),
]
RUN2_FIVE = {"c01", "c03", "c04", "c11", "c12", "x1", "x2", "x3", "x4", "x5"}
RUN2_TEN = {"c09"}
EXAMPLES_PREFIX = "Begin with a short opening line in Agy's voice. Examples of how Agy opens: "


class Abort(BaseException):
    """Not an Exception, so no except-Exception in the pipeline swallows it."""


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


def parse_fixture(text):
    """Same parse as run 2's probe: visitor turns (None for the seeded turn)
    and the seed's answer and offer paragraphs."""
    part = text.split("## Expected Answers", 1)[0].split("## Acceptance Criteria")[0]
    convs = {}
    for num, title, line in re.findall(r"^(\d+)\. (.+)\n(.+)$", part, re.M):
        turns = []
        for t in line.split(" → "):
            t = t.strip()
            if t == "(seeded answer)":
                turns.append(None)
            else:
                assert t.startswith("“") and t.endswith("”"), (num, t)
                turns.append(t[1:-1])
        convs[int(num)] = {"title": title, "turns": turns, "seed": None}
    for num, c in convs.items():
        if None in c["turns"]:
            block = part.split(f"{num}. {c['title']}\n", 1)[1].split(f"\n\n{num + 1}. ", 1)[0]
            quoted = [ln[2:] if ln.startswith("> ") else "" for ln in block.splitlines() if ln.startswith(">")]
            paras = "\n".join(quoted).split("\n\n")
            assert len(paras) == 2, (num, paras)
            c["seed"] = {"answer": paras[0].strip(), "offer": paras[1].strip()}
    return convs


CONVS = parse_fixture(git("show", f"{FIXTURE_COMMIT}:tests/fixtures/evaluator_conversations.md"))
assert sorted(CONVS) == list(range(1, 19)), sorted(CONVS)
CASES = {f"c{n:02d}": CONVS[n]["turns"] for n in sorted(CONVS)}
CASES.update({cid: [q] for cid, q in EXTRAS})
LIVE_TURNS = sum(1 for turns in CASES.values() for q in turns if q is not None)
assert LIVE_TURNS == 45, LIVE_TURNS


def baseline_runs(case):
    if case in RUN2_TEN:
        return set()
    if case in RUN2_FIVE:
        return set(range(6, RUNS + 1))
    return set(range(1, RUNS + 1))


def seed_entry(case):
    seed = CONVS[int(case[1:])]["seed"]
    return {"type": "conversational", "Role": "assistant", "text": seed["answer"] + "\n\n" + seed["offer"]}


# ---------------------------------------------------------------- new arms
STORIES = [
    json.loads(line)
    for line in (REPO / "echo_star_stories_nlp.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
for _s in STORIES:
    _s["id"] = str(_s.get("id", "")).strip()
bs.sync_portfolio_metadata(STORIES)

_orig_build = bs.build_tool_system_prompt
_orig_choose = bs._choose_opening_and_focus
_orig_stream = bs._stream_response
_orig_search = bs.semantic_search
TURN = {}


def choose_recording(is_synthesis):
    opening, focus = _orig_choose(is_synthesis)
    TURN["opening"] = opening
    return opening, focus


def build_exact_opener(*args, **kwargs):
    prompt = _orig_build(*args, **kwargs)
    examples = EXAMPLES_PREFIX + "; ".join(f'"{o}"' for o in kwargs["opener_examples"]) + "."
    assert prompt.count(examples) == 1, "examples line not found exactly once"
    return prompt.replace(examples, f"Start your response with this exact text: {TURN['opening']}")


def stream_recording(*args, **kwargs):
    resp = _orig_stream(*args, **kwargs)
    u = getattr(resp, "usage", None)
    TURN["calls"].append({
        "model": getattr(resp, "model", None),
        "raw_text": getattr(resp, "output_text", "") or "",
        "function_calls": sum(1 for o in resp.output if getattr(o, "type", "") == "function_call"),
        "usage": {
            "input": u.input_tokens, "cached": u.input_tokens_details.cached_tokens or 0,
            "output": u.output_tokens, "reasoning": u.output_tokens_details.reasoning_tokens or 0,
        } if u else None,
    })
    return resp


def search_guard(query, *args, **kwargs):
    result = _orig_search(query, *args, **kwargs)
    if str(result.get("reason") or "").startswith("fallback"):
        raise Abort(f"search fallback ({result.get('reason')}) for {query!r}")
    TURN["searches"].append({"query": query, "top_score": result.get("top_score"), "n": len(result.get("results") or [])})
    return result


def canary(label):
    h = pinecone_service.pinecone_semantic_search("Fiserv white-label card portal", {}, STORIES, top_k=25)
    if not h or h[0]["story"]["Client"] != "Fiserv":
        raise Abort(f"health check failed ({label})")
    print(f"health check {label}: top Fiserv {h[0]['pc_score']:.3f}", flush=True)


def new_turn(arm, q, session, extra):
    mock_st = MagicMock()
    mock_st.session_state = session
    TURN.clear()
    TURN.update({"calls": [], "searches": [], "opening": None})
    ps = [
        patch("streamlit.session_state", session),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "log_query", lambda *a, **k: None),
        patch.object(bs, "log_offdomain", lambda *a, **k: None),
        patch.object(semantic_router, "_log_borderline", lambda *a, **k: None),
        patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None),
        patch.object(query_logger, "get_sheet", lambda *a, **k: None),
        patch.object(bs, "_choose_opening_and_focus", choose_recording),
        patch.object(bs, "_stream_response", stream_recording),
        patch.object(bs, "semantic_search", search_guard),
    ]
    if arm == "opener":
        ps.append(patch.object(bs, "build_tool_system_prompt", build_exact_opener))
    if extra:
        ps.append(patch.object(bs, "_nonsense_rejection", lambda *a, **k: None))
    for p in ps:
        p.start()
    t0 = time.perf_counter()
    try:
        res = bs.send_to_backend(q, {}, None, STORIES)
        row = {
            "answer_md": res.get("answer_md") or "",
            "rejection": res.get("rejection_reason"),
            "degraded": res.get("degraded"),
            "sources": [f"{s.get('title')} ({s.get('client')})" for s in res.get("sources") or []],
            "intent_family": res.get("intent_family"),
        }
    except Exception as e:  # recorded, scored as a fail; the run goes on
        row = {"answer_md": "", "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}
    finally:
        for p in reversed(ps):
            p.stop()
    if session.get("__embed_failure__"):
        raise Abort(f"embed failure flagged on {q!r}")
    row.update({
        "seconds": round(time.perf_counter() - t0, 2),
        "opening": TURN["opening"], "calls": TURN["calls"], "search_queries": TURN["searches"],
    })
    return row


def new_run(arm, case, r):
    session = {"ask_transcript": []}
    extra = case.startswith("x")
    rows = []
    for t, q in enumerate(CASES[case], 1):
        base = {"arm": arm, "case": case, "run": r, "turn": t}
        if q is None:
            entry = seed_entry(case)
            session["ask_transcript"].append(entry)
            rows.append({**base, "question": None, "answer_md": entry["text"], "seeded": True})
            continue
        session["ask_transcript"].append({"role": "user", "text": q})
        row = new_turn(arm, q, session, extra)
        row.update({**base, "question": q, "nonsense_skipped": extra})
        if extra:
            row["production_nonsense"] = is_nonsense(q)
        session["ask_transcript"].append({"type": "conversational", "Role": "assistant", "text": row["answer_md"] or ""})
        rows.append(row)
        print(f"[{arm} {case} r{r} t{t}] {row['seconds']}s {row.get('error') or row.get('rejection') or ''}"
              f" | {(row['answer_md'] or '')[:50]!r}", flush=True)
    return rows


# ---------------------------------------------------------------- baseline worker
class Worker:
    def __init__(self):
        log = open(OUT / f"baseline_stderr_lane{LANE}.txt", "w")
        self.p = subprocess.Popen(
            [sys.executable, "probes_282b/worker_gate.py"], cwd=FROZEN,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True, bufsize=1,
        )
        ready = json.loads(self.p.stdout.readline() or "{}")
        if not ready.get("ready"):
            raise Abort("baseline worker did not start; see baseline_stderr")

    def run(self, case, r):
        job = {"case": case, "run": r}
        if case.startswith("x"):
            job["question"] = CASES[case][0]
        self.p.stdin.write(json.dumps(job) + "\n")
        self.p.stdin.flush()
        out = json.loads(self.p.stdout.readline() or '{"ok": false, "abort": "worker exited"}')
        if not out["ok"]:
            raise Abort(f"baseline worker: {out['abort']}")
        return out["rows"]

    def close(self):
        if self.p.poll() is None:
            self.p.stdin.write(json.dumps({"stop": True}) + "\n")
            self.p.stdin.flush()
            self.p.wait(timeout=120)


def main():
    # Pre-flight: the exact-opener replacement applies in both modes.
    for syn in (False, True):
        TURN["opening"] = "ZZZ_SENTINEL opener"
        p = build_exact_opener(
            is_synthesis=syn, matt_dna=bs.MATT_DNA, profile_facts="",
            opener_examples=bs.SYNTHESIS_OPENERS + bs.STANDARD_OPENERS, focus_angle="",
        )
        assert "Start your response with this exact text: ZZZ_SENTINEL opener" in p and EXAMPLES_PREFIX not in p
    jobs = [(c, r) for c in CASES for r in range(1, RUNS + 1)]
    mine = jobs[LANE::LANES]
    if os.environ.get("SMOKE_JOBS"):  # smoke tests and acceptance subsets; the gate run never sets it
        mine = [(c, int(r)) for c, r in (j.split(":") for j in os.environ["SMOKE_JOBS"].split(","))]
    only = os.environ.get("ARMS", "").split(",") if os.environ.get("ARMS") else None  # same rule
    print(f"lane {LANE}/{LANES}: {len(mine)} of {len(jobs)} (case, run) jobs", flush=True)
    rows, errors = [], []
    worker = Worker() if any(r in baseline_runs(c) for c, r in mine) and (only is None or "baseline" in only) else None
    canary("start")
    try:
        for case, r in mine:
            arms = ["new", "opener"] + (["baseline"] if r in baseline_runs(case) else [])
            arms = [a for a in arms if only is None or a in only]
            k = r % len(arms)
            for arm in arms[k:] + arms[:k]:
                got = worker.run(case, r) if arm == "baseline" else new_run(arm, case, r)
                rows += got
                errors += [(arm, case, r, x["turn"], x["error"]) for x in got if x.get("error")]
                if len(errors) > MAX_ERRORS:
                    raise Abort(f"more than {MAX_ERRORS} errors: {errors[-3:]}")
                (OUT / f"rows_lane{LANE}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
        canary("end")
    finally:
        if worker:
            worker.close()
    print(f"done | rows {len(rows)} | errors {errors}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Abort as e:
        print(f"ABORT: {e}", flush=True)
        sys.exit(2)
