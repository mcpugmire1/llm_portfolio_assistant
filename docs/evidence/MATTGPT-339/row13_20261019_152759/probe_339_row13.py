"""MATTGPT-339: row 13 check, work-history questions whose search returns nothing.

Arm A (natural): agy_answer() as at HEAD. A run is a row 13 sample only if
every search_stories call returned 0 results.
Arm B (forced): the real search runs and its scores are recorded, then the
model is handed results=[] ("No stories found."), the row 13 path.

Loggers patched: log_query, log_offdomain, _log_borderline,
_log_router_low_confidence, query_logger.get_sheet. Every call's usage is
recorded; cost.txt is computed from it.

Usage: python probes/probe_339_row13.py  (writes probes/output/MATTGPT-339/<ts>/)
"""

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from services import pinecone_service, query_logger, semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402

QUESTIONS = [
    "Has Matt worked in agriculture?",
    "Tell me about Matt's work in oil and gas.",
    "Has Matt worked in insurance?",
    "Has Matt worked on video streaming platforms?",
    "Agriculture experience?",
]
ARMS = ("natural", "forced")
RUNS = 2
# $ per 1M tokens: input, cached input, output (MATTGPT-282 evidence, Oct 11 2026)
PRICE = (2.00, 0.10, 10.0)

OUT = REPO / "probes" / "output" / "MATTGPT-339" / datetime.now().strftime("%Y%m%d_%H%M%S")
OUT.mkdir(parents=True, exist_ok=True)

STORIES = [
    json.loads(line)
    for line in (REPO / "echo_star_stories_nlp.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
for _s in STORIES:
    _s["id"] = str(_s.get("id", "")).strip()
bs.sync_portfolio_metadata(STORIES)

_orig_stream = bs._stream_response
_orig_search = bs.semantic_search
TURN: dict = {}


class Abort(Exception):
    pass


def stream_recording(*args, **kwargs):
    if TURN.get("system_prompt") is None:
        TURN["system_prompt"] = kwargs["input"][0]["content"]
    resp = _orig_stream(*args, **kwargs)
    u = getattr(resp, "usage", None)
    TURN["calls"].append({
        "model": getattr(resp, "model", None),
        "function_calls": sum(1 for o in resp.output if getattr(o, "type", "") == "function_call"),
        "usage": {
            "input": u.input_tokens, "cached": u.input_tokens_details.cached_tokens or 0,
            "output": u.output_tokens, "reasoning": u.output_tokens_details.reasoning_tokens or 0,
        } if u else None,
    })
    return resp


def search_spy(query, *args, **kwargs):
    result = _orig_search(query, *args, **kwargs)
    if str(result.get("reason") or "").startswith("fallback"):
        raise Abort(f"search fallback ({result.get('reason')}) for {query!r}")
    TURN["searches"].append({
        "query": query,
        "top_score": result.get("top_score"),
        "n": len(result.get("results") or []),
    })
    if TURN["arm"] == "forced":
        result = {**result, "results": []}
    return result


def canary():
    h = pinecone_service.pinecone_semantic_search("Fiserv white-label card portal", {}, STORIES, top_k=25)
    if not h or h[0]["story"]["Client"] != "Fiserv":
        raise Abort("health check failed")
    print(f"health check: top Fiserv {h[0]['pc_score']:.3f}", flush=True)


def run_turn(arm, q):
    session: dict = {}
    mock_st = MagicMock()
    mock_st.session_state = session
    TURN.clear()
    TURN.update({"arm": arm, "calls": [], "searches": [], "system_prompt": None})
    ps = [
        patch("streamlit.session_state", session),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "log_query", lambda *a, **k: None),
        patch.object(bs, "log_offdomain", lambda *a, **k: None),
        patch.object(semantic_router, "_log_borderline", lambda *a, **k: None),
        patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None),
        patch.object(query_logger, "get_sheet", lambda *a, **k: None),
        patch.object(bs, "_stream_response", stream_recording),
        patch.object(bs, "semantic_search", search_spy),
    ]
    for p in ps:
        p.start()
    t0 = time.perf_counter()
    try:
        res = bs.agy_answer(q, STORIES)
        row = {
            "answer_md": res.get("answer_md") or "",
            "rejection": res.get("rejection_reason"),
            "degraded": res.get("degraded"),
            "intent_family": res.get("intent_family"),
            "sources": [f"{s.get('title')} ({s.get('client')})" for s in res.get("sources") or []],
        }
    except Abort:
        raise
    except Exception as e:
        row = {"answer_md": "", "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()}
    finally:
        for p in reversed(ps):
            p.stop()
    if session.get("__embed_failure__"):
        raise Abort(f"embed failure flagged on {q!r}")
    searches = TURN["searches"]
    row.update({
        "arm": arm,
        "question": q,
        "seconds": round(time.perf_counter() - t0, 2),
        "searches": searches,
        # Arm B always hands the model 0 results; the recorded n is the real search.
        "zero_result_run": bool(searches) and all(s["n"] == 0 for s in searches),
        "calls": TURN["calls"],
        "system_prompt": TURN["system_prompt"],
    })
    return row


def cost(u):
    return ((u["input"] - u["cached"]) * PRICE[0] + u["cached"] * PRICE[1] + u["output"] * PRICE[2]) / 1e6


def main():
    canary()
    rows = []
    for arm in ARMS:
        for q in QUESTIONS:
            for r in range(1, RUNS + 1):
                row = run_turn(arm, q)
                row["run"] = r
                rows.append(row)
                print(
                    f"[{arm} r{r}] {q} | searches {[(round(s['top_score'] or 0, 3), s['n']) for s in row['searches']]}"
                    f" | rejection {row.get('rejection')} | {row['seconds']}s",
                    flush=True,
                )
                (OUT / "rows.json").write_text(json.dumps(rows, indent=2))
    canary()

    calls = [c for row in rows for c in row["calls"] if c["usage"]]
    total = sum(cost(c["usage"]) for c in calls)
    lines = [
        f"turns {len(rows)}, model calls {len(calls)} (usage missing on "
        f"{sum(1 for row in rows for c in row['calls'] if not c['usage'])})",
        f"prices $/1M (input, cached, output): {PRICE}",
        f"tokens: input {sum(c['usage']['input'] for c in calls)}, cached {sum(c['usage']['cached'] for c in calls)}, "
        f"output {sum(c['usage']['output'] for c in calls)} (reasoning {sum(c['usage']['reasoning'] for c in calls)})",
    ]
    for arm in ARMS:
        ac = [c for row in rows if row["arm"] == arm for c in row["calls"] if c["usage"]]
        lines.append(f"{arm}: ${sum(cost(c['usage']) for c in ac):.4f}")
    lines.append(f"total ${total:.4f} (${total / len(rows):.4f}/turn)")
    (OUT / "cost.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    with open(OUT / "answers.md", "w") as f:
        for row in rows:
            f.write(f"## [{row['arm']} r{row['run']}] {row['question']}\n\n")
            f.write(f"searches: {json.dumps(row['searches'])}\n\n")
            f.write(f"sources: {row['sources'] if 'sources' in row else row.get('error')}\n\n")
            f.write(row["answer_md"] + "\n\n---\n\n")
    (OUT / "matt_dna.txt").write_text(bs.MATT_DNA or "")
    print(f"output: {OUT}")


if __name__ == "__main__":
    main()
