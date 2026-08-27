"""MATTGPT-208: what's at ranks 11-25 if we raise SEARCH_TOP_K to 25?

No code change to the app. Monkeypatches backend_service.SEARCH_TOP_K = 25
for this probe run only; propagates to the Pinecone query via the explicit
top_k= argument in rag_answer.
"""

import contextlib
import io
import re
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
import config.debug as _dbg  # noqa: E402

_dbg.DEBUG = True

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from ui.pages.ask_mattgpt import backend_service as bs  # noqa: E402
from ui.pages.ask_mattgpt.backend_service import (  # noqa: E402
    rag_answer,
    sync_portfolio_metadata,
)
from utils.corpus_loader import load_stories  # noqa: E402

# Patch the imported constant. rag_answer calls semantic_search(top_k=SEARCH_TOP_K)
# with this module-local reference, so mutating it here changes the effective
# fetch depth without touching config/constants.py.
bs.SEARCH_TOP_K = 25

stories = load_stories("echo_star_stories_nlp.jsonl")
sync_portfolio_metadata(stories)
print(f"Corpus: {len(stories)} stories")
print(f"Probe SEARCH_TOP_K override: {bs.SEARCH_TOP_K}\n")

QUERIES = [
    ("Q_BROAD", "tell me about Matt's career"),
    ("Q_EARLY", "tell me about Matt's early career"),
]

HIT_RE = re.compile(
    r"DEBUG Hit: id=(\S+) pc=([\d.]+) kw=([\d.]+) blend=([\d.]+)\s+\[([^\]]*)\]\s*(.*)"
)


def _story_by_id(sid):
    for s in stories:
        if str(s.get("id")) == str(sid):
            return s
    return {}


def _field(sid, *keys):
    s = _story_by_id(sid)
    for k in keys:
        if s.get(k):
            return s.get(k)
    return "?"


# Classification for the "is it engagement or meta?" call
META_THEMES = {"Professional Narrative"}
META_EMPLOYERS = {"Sabbatical"}  # Independent-project stories


def _kind(sid):
    theme = _field(sid, "Theme", "theme")
    emp = _field(sid, "Employer", "employer")
    if theme in META_THEMES:
        return "META-PN"
    if emp in META_EMPLOYERS:
        return "META-IND"
    return "ENGAGE"


for label, q in QUERIES:
    print("=" * 110)
    print(f"{label}: {q!r}   (top_k=25)")
    print("=" * 110)

    buf = io.StringIO()
    _s.clear()
    _s["__suppress_logging__"] = True
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rag_answer(q, {"q": q}, stories)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.__stderr__)
    out = buf.getvalue()

    hits = []
    for line in out.splitlines():
        mh = HIT_RE.search(line)
        if mh:
            sid, pc, kw, blend, client, title = mh.groups()
            hits.append(
                {
                    "id": sid,
                    "pc": float(pc),
                    "kw": float(kw),
                    "blend": float(blend),
                    "client": client,
                    "title": title.strip(),
                }
            )
    hits.sort(key=lambda h: h["blend"], reverse=True)

    print(f"\nPinecone returned {len(hits)} hits.")
    print(
        f"  {'#':>2}  {'kind':<8}  {'pc':>5} {'kw':>5} {'blend':>5}  "
        f"{'Theme':<26} {'Era':<22} {'Employer':<22} Title"
    )
    for i, h in enumerate(hits[:25], 1):
        kind = _kind(h["id"])
        theme = _field(h["id"], "Theme", "theme")
        era = _field(h["id"], "Era", "era")
        emp = _field(h["id"], "Employer", "employer")
        title = _field(h["id"], "Title", "title")
        marker = "  <-- 11+" if i == 11 else ""
        print(
            f"  {i:>2}. {kind:<8}  {h['pc']:.3f} {h['kw']:.3f} {h['blend']:.3f}  "
            f"{theme[:26]:<26} {era[:22]:<22} {emp[:22]:<22} {title[:55]}{marker}"
        )

    # Composition summary
    top10 = hits[:10]
    tail11_25 = hits[10:25]
    print("\nComposition summary:")
    for name, group in [("Top 10", top10), ("Ranks 11-25", tail11_25)]:
        kinds = [_kind(h["id"]) for h in group]
        eras = sorted({_field(h["id"], "Era", "era") for h in group})
        emps = sorted({_field(h["id"], "Employer", "employer") for h in group})
        n_engage = kinds.count("ENGAGE")
        n_meta_pn = kinds.count("META-PN")
        n_meta_ind = kinds.count("META-IND")
        print(
            f"  {name}: {len(group)} hits | ENGAGE={n_engage} META-PN={n_meta_pn} META-IND={n_meta_ind}"
        )
        print(f"    eras:      {eras}")
        print(f"    employers: {emps}")

    # New material entering pool at 11+
    print("\nNew engagement stories entering at rank 11+:")
    for i, h in enumerate(hits[10:25], 11):
        if _kind(h["id"]) == "ENGAGE":
            title = str(_field(h["id"], "Title", "title") or "")
            emp = _field(h["id"], "Employer", "employer")
            era = _field(h["id"], "Era", "era")
            client = str(h["client"] or "")
            print(f"  rank {i:>2}: [{client[:20]:<20}] ({emp}, {era}) {title[:60]}")

    print()
