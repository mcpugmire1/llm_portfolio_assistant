"""pytest plugin for the MATTGPT-275 golden eval runs (untracked).

Patches every logger a live run must not write to (log_query, log_offdomain,
semantic_router._log_borderline, _log_router_low_confidence) for the whole
session, and records each pipeline call (question, answer, key fields) to
$GOLDEN_OUT/calls.jsonl. GOLDEN_SIDE=rag records rag_answer(); the agy side
is added with the migration.
"""
import json, os, time
from pathlib import Path
from unittest.mock import MagicMock, patch

OUT = Path(os.environ["GOLDEN_OUT"])
SIDE = os.environ.get("GOLDEN_SIDE", "rag")
_patches = []


def _record(fn_name, question, result, seconds, test_id):
    row = {
        "side": SIDE, "fn": fn_name, "test": test_id, "question": question,
        "seconds": round(seconds, 2),
        "answer_md": (result or {}).get("answer_md", "") if isinstance(result, dict) else str(result),
        "sources": [s.get("title") if isinstance(s, dict) else s for s in ((result or {}).get("sources") or [])] if isinstance(result, dict) else [],
        **{k: (result or {}).get(k) for k in ("rejection_reason", "intent_family", "entity_match", "degraded", "pool_size") if isinstance(result, dict)},
    }
    with open(OUT / "calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


_CURRENT = {"test": ""}


def pytest_runtest_setup(item):
    _CURRENT["test"] = item.nodeid


def pytest_configure(config):
    OUT.mkdir(parents=True, exist_ok=True)
    from services import semantic_router
    from ui.pages.ask_mattgpt import backend_service as bs
    for target in (
        patch.object(bs, "log_query", MagicMock()),
        patch.object(bs, "log_offdomain", MagicMock()),
        patch.object(semantic_router, "_log_borderline", MagicMock()),
        patch.object(semantic_router, "_log_router_low_confidence", MagicMock()),
    ):
        target.start(); _patches.append(target)
    if SIDE == "rag":
        real = bs.rag_answer

        def recording_rag_answer(question, *a, **k):
            t0 = time.perf_counter()
            res = real(question, *a, **k)
            _record("rag_answer", question, res, time.perf_counter() - t0, _CURRENT["test"])
            return res

        p = patch.object(bs, "rag_answer", recording_rag_answer)
        p.start(); _patches.append(p)


def pytest_unconfigure(config):
    for p in reversed(_patches):
        p.stop()
