"""MATTGPT-275 breadth comparison: old rag_answer() vs tool-path agy_answer(). Not tracked.

Questions: "Why hire Matt?" (golden Q65), the golden eval's other synthesis
questions (Q17, Q45), and two client-broad questions. N runs per path, no
history. Loggers patched out (log_query, log_offdomain, the router's two CSV
writers). No model or retrieval call is mocked: the Pinecone index's query
method is wrapped only to count calls.

Writes, in <out_dir>:
  blind.json     answers shuffled, labelled A/B at random per (question, run);
                 no path, no counts. Scored first.
  reveal.json    label -> path mapping plus the mechanical counts per answer:
                 distinct clients named in the answer text (corpus Client
                 values, generic clients excluded), distinct themes of the
                 sources, Pinecone queries, search queries, and whether the
                 synthesis shape was used. Opened only after blind scoring.
  raw.json       everything.

Usage: python probes/probe_275_breadth.py <out_dir> <runs>
"""

import json
import logging
import random
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / ".env")
logging.getLogger("streamlit").setLevel(logging.ERROR)
sys.path.insert(0, str(REPO))

from services import pinecone_service, semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from utils.client_utils import is_generic_client  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

out_dir, runs = Path(sys.argv[1]), int(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
stories = load_stories(str(REPO / "echo_star_stories_nlp.jsonl"))
bs.sync_portfolio_metadata(stories)
THEME_BY_TITLE = {s.get("Title"): s.get("Theme") for s in stories}
CLIENTS = sorted(
    {s.get("Client") for s in stories if s.get("Client") and not is_generic_client(s.get("Client"))},
    key=len,
    reverse=True,
)

QUESTIONS = [
    ("Q65", "Why hire Matt?"),
    ("Q17", "What are Matt's core themes?"),
    ("Q45", "What evidence shows Matt can operate at Director or VP level?"),
    ("RBC", "What did Matt do at RBC?"),
    ("JPM", "What did he do at JP Morgan?"),
]

idx = pinecone_service._init_pinecone()
_orig_query = idx.query
COUNT = {"pinecone": 0}


def counting_query(*a, **k):
    COUNT["pinecone"] += 1
    return _orig_query(*a, **k)


idx.query = counting_query


def clients_named(text):
    found, rest = [], text.lower()
    for c in CLIENTS:
        if c.lower() in rest:
            found.append(c)
            rest = rest.replace(c.lower(), " ")
    return sorted(found)


def ask(path, q):
    COUNT["pinecone"] = 0
    seen = {"queries": [], "synthesis_shape": None}
    real_search, real_bsp, real_btsp = bs.semantic_search, bs.build_system_prompt, bs.build_tool_system_prompt

    def search_wrap(query, *a, **k):
        seen["queries"].append(query)
        return real_search(query, *a, **k)

    def bsp_wrap(*a, **k):
        seen["synthesis_shape"] = k.get("is_synthesis", a[0] if a else None)
        return real_bsp(*a, **k)

    def btsp_wrap(*a, **k):
        seen["synthesis_shape"] = k.get("is_synthesis", a[0] if a else None)
        return real_btsp(*a, **k)

    session = {}
    mock_st = MagicMock()
    mock_st.session_state = session
    ps = [
        patch("streamlit.session_state", session),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "log_query", lambda *a, **k: None),
        patch.object(bs, "log_offdomain", lambda *a, **k: None),
        patch.object(semantic_router, "_log_borderline", lambda *a, **k: None),
        patch.object(semantic_router, "_log_router_low_confidence", lambda *a, **k: None),
        patch.object(bs, "semantic_search", search_wrap),
        patch.object(bs, "build_system_prompt", bsp_wrap),
        patch.object(bs, "build_tool_system_prompt", btsp_wrap),
    ]
    for p in ps:
        p.start()
    try:
        if path == "old":
            r = bs.rag_answer(q, {}, stories, history=[])
        else:
            r = bs.agy_answer(q, stories, history=[])
    finally:
        for p in reversed(ps):
            p.stop()
    answer = r.get("answer_md") or ""
    source_titles = [s.get("title") for s in r.get("sources") or []]
    return {
        "answer_md": answer,
        "rejection_reason": r.get("rejection_reason"),
        "clients_named": clients_named(answer),
        "source_titles": source_titles,
        "source_themes": sorted({THEME_BY_TITLE.get(t) for t in source_titles if THEME_BY_TITLE.get(t)}),
        "pinecone_queries": COUNT["pinecone"],
        "search_queries": seen["queries"],
        "synthesis_shape": seen["synthesis_shape"],
    }


rows = []
for qid, q in QUESTIONS:
    for run in range(1, runs + 1):
        for path in ("old", "tool"):
            rows.append({"qid": qid, "question": q, "run": run, "path": path, **ask(path, q)})
            print(f"{qid} r{run} done ({len(rows)}/{len(QUESTIONS) * runs * 2})", flush=True)

rng = random.SystemRandom()
blind, reveal = [], []
for qid, q in QUESTIONS:
    for run in range(1, runs + 1):
        pair = [r for r in rows if r["qid"] == qid and r["run"] == run]
        rng.shuffle(pair)
        for label, r in zip("AB", pair):
            key = f"{qid}-r{run}-{label}"
            blind.append({"key": key, "question": q, "answer_md": r["answer_md"]})
            reveal.append({"key": key, "path": r["path"], **{k: r[k] for k in (
                "rejection_reason", "clients_named", "source_themes", "pinecone_queries",
                "search_queries", "synthesis_shape", "source_titles")}})
(out_dir / "blind.json").write_text(json.dumps(blind, indent=2, ensure_ascii=False))
(out_dir / "reveal.json").write_text(json.dumps(reveal, indent=2, ensure_ascii=False))
(out_dir / "raw.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
print("done", len(rows))
