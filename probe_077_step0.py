"""
MATTGPT-077 Phase 1 Step 0 re-baseline.

Calls production rag_answer() for 9 probe queries. Captures DEBUG output
to extract router family, is_synthesis flag, per-hit pc/kw/blend, entity
detection, and final LLM story set.

CONTAM_IDS: derived from loaded JSONL at runtime (Independent Project
stories whose subject is MattGPT or Strangler Fig -- see _derive_contam).
Asserts every derived id exists in the JSONL. Hard exits on empty hit parse
so a silent dead-parser cannot masquerade as data.

Output: stdout only. No CSV written.
"""

import contextlib
import io
import re
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# 1. Streamlit mock -- must be in sys.modules BEFORE any project module.
# ---------------------------------------------------------------------------


class _SessionState(dict):
    """Minimal dict-backed mock of st.session_state."""


_session = _SessionState()
_session["__suppress_logging__"] = True  # silence Google Sheets writes

_st = MagicMock()
_st.session_state = _session
_st.secrets = {}  # empty dict so get_conf() falls through to os.getenv()
sys.modules["streamlit"] = _st
sys.modules["streamlit.components"] = MagicMock()
sys.modules["streamlit.components.v1"] = MagicMock()

# ---------------------------------------------------------------------------
# 2. Force DEBUG = True BEFORE importing any project module that does
#    "from config.debug import DEBUG".  Setting the attribute on the module
#    object ensures every subsequent from-import gets True, regardless of
#    what config/debug.py says on disk (committed value is False).
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent))

import config.debug as _debug_mod  # noqa: E402 -- must precede backend import

_debug_mod.DEBUG = True

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from ui.pages.ask_mattgpt.backend_service import rag_answer  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

STORIES_JSONL = Path("echo_star_stories_nlp.jsonl")

# May 19 recorded states (BACKLOG.md MATTGPT-077 probe table).
MAY19 = {
    "P1": "LEAD:StranglerFig",
    "P2": "CLEAN",
    "P3": "CLEAN",
    "P4": "LEAD:MattGPT",
    "P5": "LEAD:StranglerFig",
    "P6": "CLEAN",
    "P7": "CLEAN",
    "P8": "LEAD:StranglerFig",
    "Q1": "CLEAN(post-fix)",
}

PROBES = [
    ("P1", "How does Matt modernize monoliths into microservices?"),
    ("P2", "How does Matt approach microservices?"),
    ("P3", "How does Matt handle legacy modernization?"),
    ("P4", "How does Matt build MVPs?"),
    ("P5", "How does Matt do platform refactoring?"),
    ("P6", "How do you modernize monoliths into microservices?"),
    ("P7", "How do you build MVPs?"),
    ("P8", "How do you do platform refactoring?"),
    ("Q1", "How does Matt use event storming?"),
]


# ---------------------------------------------------------------------------
# Corpus helpers
# ---------------------------------------------------------------------------


def _load_stories() -> list:
    return load_stories(str(STORIES_JSONL))


def _derive_contam(stories: list) -> frozenset:
    """
    Derive contaminating story IDs from the loaded JSONL.

    Rule (per amended handoff v2):
      Client == "Independent Project" (case-insensitive)
      AND the story's subject is MattGPT itself OR the Strangler Fig refactor.

    Excluded from Independent Project set:
      - Career Intent story (professional narrative, not self-referential)

    Inclusion signals:
      - Title contains "MattGPT" (explicit product stories)
      - Title/text contains "strangler" (Strangler Fig / monolith-by-accident story)
      - All other Independent Project stories whose titles/subjects are
        about building or improving the MattGPT portfolio tool.

    The simplest reliable rule that matches the amended definition:
      Client == "Independent Project"
      AND id does NOT start with "career-intent"
    """
    result = set()
    for s in stories:
        client = (s.get("Client") or "").lower().strip()
        if client != "independent project":
            continue
        sid = s.get("id", "")
        title = s.get("Title", "")
        # Exclude career-intent narrative (not about the product)
        if sid.startswith("career-intent") or "Career Intent" in title:
            continue
        result.add(sid)
    return frozenset(result)


# ---------------------------------------------------------------------------
# Debug output parser
# ---------------------------------------------------------------------------


def _parse_debug(output: str) -> dict:
    data: dict[str, Any] = {
        "family": None,
        "entity": None,
        "synthesis": False,
        "hits": [],  # [{id, pc, kw, blend}] -- raw Pinecone results
    }
    for line in output.splitlines():
        # Router family
        m = re.search(r"Semantic router: valid=\w+, score=[\d.]+, family=(\w+)", line)
        if m:
            data["family"] = m.group(1)

        # Synthesis flag (from "DEBUG: intent_family=X, is_synthesis=True/False")
        m = re.search(r"is_synthesis=(True|False)", line)
        if m:
            data["synthesis"] = m.group(1) == "True"

        # Entity detection
        m = re.search(r"Entity detected - (.+)", line)
        if m:
            data["entity"] = m.group(1).strip()

        # Per-hit: "DEBUG Hit: id=XXX pc=0.000 kw=0.000 blend=0.000  [client] title"
        m = re.search(
            r"DEBUG Hit: id=(\S+) pc=([\d.]+) kw=([\d.]+) blend=([\d.]+)", line
        )
        if m:
            data["hits"].append(
                {
                    "id": m.group(1),
                    "pc": float(m.group(2)),
                    "kw": float(m.group(3)),
                    "blend": float(m.group(4)),
                }
            )

    return data


# ---------------------------------------------------------------------------
# Contamination status
# ---------------------------------------------------------------------------


def _contam_status(hits: list, sources: list, contam_ids: frozenset) -> tuple:
    """Returns (status, [contam_ids_found]).

    LEAD  = contam id at pool position 0 OR source position 0.
    POOL  = contam id present elsewhere in pool or LLM set.
    CLEAN = not present.
    """
    pool_ids = [h["id"] for h in hits]
    source_ids = [s.get("id", "") for s in sources]

    found = list(dict.fromkeys(i for i in (pool_ids + source_ids) if i in contam_ids))
    if not found:
        return "CLEAN", []

    lead_pool = pool_ids[0] if pool_ids else ""
    lead_src = source_ids[0] if source_ids else ""
    if lead_pool in contam_ids or lead_src in contam_ids:
        return "LEAD", found

    return "POOL", found


def _short(sid: str, n: int = 36) -> str:
    """Drop the |client-slug suffix and truncate for display."""
    return sid.split("|")[0][:n]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading stories...", flush=True)
    stories = _load_stories()
    print(f"  {len(stories)} stories loaded", flush=True)

    # Derive and validate contamination set
    contam_ids = _derive_contam(stories)
    all_story_ids = {s.get("id", "") for s in stories}
    bad = contam_ids - all_story_ids
    if bad:
        print(f"\nFATAL: derived contam IDs not found in JSONL: {bad}", file=sys.stderr)
        sys.exit(1)

    print(f"\nContamination set ({len(contam_ids)} stories):")
    for cid in sorted(contam_ids):
        print(f"  {_short(cid, 60)}")

    rows = []

    for pid, query in PROBES:
        print(f"\n[{pid}] {query[:75]}", flush=True)

        # Reset volatile session state; preserve vocab cache across probes.
        vocab = _session.get("_known_vocab")
        _session.clear()
        _session["__suppress_logging__"] = True
        if vocab:
            _session["_known_vocab"] = vocab

        buf = io.StringIO()
        result = {}
        err = None
        try:
            with contextlib.redirect_stdout(buf):
                result = rag_answer(query, {"q": query}, stories)
        except Exception as exc:
            err = str(exc)

        captured = buf.getvalue()
        parsed = _parse_debug(captured)
        sources = result.get("sources", []) if result else []

        # Hard fail if parser returned zero hits (indicates dead debug output)
        if not parsed["hits"] and not err:
            print(
                f"\nFATAL [{pid}]: zero hits parsed from debug output -- "
                "DEBUG may be off or parser is broken. Cannot produce valid table.",
                file=sys.stderr,
            )
            print("--- captured output (first 2000 chars) ---", file=sys.stderr)
            print(captured[:2000], file=sys.stderr)
            sys.exit(1)

        status, contam_found = _contam_status(parsed["hits"], sources, contam_ids)
        family_str = parsed["family"] or "?"
        if parsed["synthesis"]:
            family_str += "[synth]"
        if parsed["entity"]:
            family_str += f"[ent:{parsed['entity'][:12]}]"

        rows.append(
            {
                "pid": pid,
                "query": query,
                "family": family_str,
                "raw_family": parsed["family"],
                "synthesis": parsed["synthesis"],
                "entity": parsed["entity"],
                "hits": parsed["hits"],
                "sources": sources,
                "status": status,
                "contam": contam_found,
                "err": err,
            }
        )

        flag = (
            f"  ** {status} {[_short(c) for c in contam_found]}" if contam_found else ""
        )
        print(f"  -> {status}  family={family_str}{flag}", flush=True)

    # -------------------------------------------------------------------------
    # Summary table
    # -------------------------------------------------------------------------
    W = 150
    print("\n\n" + "=" * W)
    print("MATTGPT-077 Step 0 Re-baseline — Summary Table")
    print("=" * W)
    print(
        f"{'ID':<3}  {'Family':<26}  {'Status':<5}  "
        f"{'Pool lead (id / pc / kw / blend)':<56}  "
        f"{'LLM top-3 ids':<55}  May19 / Delta"
    )
    print("-" * W)

    for r in rows:
        pid = r["pid"]
        hits = r["hits"]
        sources = r["sources"]
        may19 = MAY19.get(pid, "?")
        status = r["status"]

        lead_str = "—"
        if hits:
            h0 = hits[0]
            lead_str = (
                f"{_short(h0['id'])} ({h0['pc']:.3f}/{h0['kw']:.3f}/{h0['blend']:.3f})"
            )

        llm_ids = ", ".join(_short(s.get("id", "")) for s in sources[:3])

        if "CLEAN" in may19 and status in ("LEAD", "POOL"):
            delta = "<- REGRESSION"
        elif ("LEAD" in may19 or "POOL" in may19) and status == "CLEAN":
            delta = "<- FIXED"
        elif "LEAD" in may19 and status == "LEAD":
            delta = "still LEAD"
        elif "LEAD" in may19 and status == "POOL":
            delta = "improved->POOL"
        else:
            delta = "—"

        print(
            f"{pid:<3}  {r['family']:<26}  {status:<5}  "
            f"{lead_str:<56}  "
            f"{llm_ids:<55}  {may19} / {delta}"
        )

    print("=" * W)

    # -------------------------------------------------------------------------
    # Per-probe detail
    # -------------------------------------------------------------------------
    print("\n\nDETAIL (all pool hits per probe)\n" + "=" * W)
    for r in rows:
        pid = r["pid"]
        synth_flag = " [SYNTHESIS]" if r["synthesis"] else ""
        ent_flag = f" [entity: {r['entity']}]" if r["entity"] else ""
        print(
            f"\n{pid}  [{r['raw_family'] or '?'}]{synth_flag}{ent_flag}  status={r['status']}"
        )
        print(f"  Query: {r['query']}")
        if r["err"]:
            print(f"  ERROR: {r['err']}")
            continue
        print(f"  Pool hits ({len(r['hits'])} total):")
        for i, h in enumerate(r["hits"]):
            marker = "  ** CONTAM" if h["id"] in contam_ids else ""
            lead_flag = " [LEAD]" if i == 0 else ""
            print(
                f"    [{i+1:>2}] pc={h['pc']:.4f} kw={h['kw']:.4f} "
                f"blend={h['blend']:.4f}  {_short(h['id'])}{lead_flag}{marker}"
            )
        print(f"  LLM set ({len(r['sources'])} stories):")
        for i, s in enumerate(r["sources"]):
            sid = s.get("id", "")
            marker = "  ** CONTAM" if sid in contam_ids else ""
            print(
                f"    [{i+1}] {s.get('client','?')[:20]}: "
                f"{s.get('title','?')[:50]}{marker}"
            )
        if r["contam"]:
            print(f"  Contaminating IDs found: {[_short(c) for c in r['contam']]}")

    print("\n" + "=" * W)
    print("END Step 0")
    print("NOTE: DEBUG forced True via config.debug module (committed default = False)")


if __name__ == "__main__":
    main()
