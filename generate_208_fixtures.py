"""MATTGPT-208: capture Q_BROAD and Q_EARLY top-25 pools as JSON fixtures.

One-shot script. Hits Pinecone once per query, writes deterministic pool
data to tests/unit/fixtures/ for the Red-gate unit tests. Re-run only if
the corpus embeddings change materially (typically an ingest event).

The fixture JSONs contain the minimum fields diversify_results reads plus
scoring fields for readability of the pool ordering: id, Title, Client,
Employer, Era, Theme, pc, kw, blend. Fixtures are pre-sorted by blend
descending, matching what rag_answer feeds to diversify.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock


class _SS(dict):
    pass


_s = _SS()
_s["__suppress_logging__"] = True
_st = MagicMock()
_st.session_state = _s
_st.secrets = {}
sys.modules["streamlit"] = _st
sys.modules["streamlit.components"] = MagicMock()
sys.modules["streamlit.components.v1"] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent))
import config.debug as _dbg  # noqa: E402 -- must precede backend import

_dbg.DEBUG = False

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from services.rag_service import semantic_search  # noqa: E402
from ui.pages.ask_mattgpt.backend_service import sync_portfolio_metadata  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

stories = load_stories("echo_star_stories_nlp.jsonl")
sync_portfolio_metadata(stories)

QUERIES = {
    "mattgpt208_pool_broad": "tell me about Matt's career",
    "mattgpt208_pool_early": "tell me about Matt's early career",
}

FIXTURE_DIR = Path("tests/unit/fixtures")
FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

FIELDS = ("id", "Title", "Client", "Employer", "Era", "Theme")

for name, q in QUERIES.items():
    result = semantic_search(q, {"q": q}, stories=stories, top_k=25)
    pool = result["results"]

    out = []
    for s in pool:
        entry = {k: s.get(k) for k in FIELDS}
        entry["pc"] = round(float(s.get("pc") or 0.0), 4)
        entry["kw"] = round(float(s.get("kw") or 0.0), 4)
        out.append(entry)

    payload = {
        "query": q,
        "top_k": 25,
        "captured_from": "generate_208_fixtures.py",
        "story_count": len(out),
        "pool": out,
    }

    path = FIXTURE_DIR / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {path} ({len(out)} stories)")
