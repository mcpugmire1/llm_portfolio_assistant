"""MATTGPT-275 Green browser FAIL repro: Matt's three-turn conversation. Not tracked.

Runs the exact browser conversation through send_to_backend() (the Green path,
history from ask_transcript as the UI builds it), N runs, logging the model's
search queries and the stories each search returned. Loggers patched out.

Usage: python probes/probe_275_team_size.py <out_dir> <runs>
"""

import json
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[1]
load_dotenv(REPO / ".env")
logging.getLogger("streamlit").setLevel(logging.ERROR)
sys.path.insert(0, str(REPO))

from services import semantic_router  # noqa: E402
from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

out_dir, runs = Path(sys.argv[1]), int(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
stories = load_stories(str(REPO / "echo_star_stories_nlp.jsonl"))
bs.sync_portfolio_metadata(stories)
_real_search = bs.semantic_search
QUESTIONS = [
    "How did Matt scale engineering teams from 4 to 150+ people?",
    "Tell me about his payments work",
    "how big was his teams",
]
rows = []
for run in range(1, runs + 1):
    session = {"ask_transcript": []}
    for turn, q in enumerate(QUESTIONS, 1):
        searches = []
        session["ask_transcript"].append({"role": "user", "text": q})

        def search_wrap(query, *a, **k):
            r = _real_search(query, *a, **k)
            searches.append({"query": query, "results": [s.get("Title") for s in (r.get("results") or [])[:5]]})
            return r

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
        ]
        for p in ps:
            p.start()
        try:
            r = bs.send_to_backend(q, {}, None, stories)
        finally:
            for p in reversed(ps):
                p.stop()
        ans = r.get("answer_md") or ""
        session["ask_transcript"].append({"type": "conversational", "Role": "assistant", "text": ans})
        rows.append({"run": run, "turn": turn, "question": q, "searches": searches,
                     "sources": [s.get("title") for s in r.get("sources") or []], "answer_md": ans})
        print(f"r{run} t{turn} q={[s['query'] for s in searches]}", flush=True)
(out_dir / "team_size.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
print("done", len(rows))
