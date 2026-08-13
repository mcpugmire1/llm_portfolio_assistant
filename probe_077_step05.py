"""
MATTGPT-077 Phase 1 Step 0.6 -- three-arm A/B/C evidence for the strip.

  A: original query
  B: deletion -- "Matt"/"Matt's" removed (produces grammatical fragments)
  C: substitution -- "Matt"→"he", "Matt's"→"his" (grammatical, no name)

P6/P7/P8 carry no Matt token and run once as unchanged references.

Three questions from this run:
  1. Does C fix P4 like B did?
  2. Does C keep Q1's Revenue at LLM position 1 where B displaced it?
  3. Do P2/P3 stay clean under C?

If C matches B's wins and removes B's Q1 damage, substitution replaces
deletion in the implementation. If C behaves like B, deletion stands.

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
_session["__suppress_logging__"] = True

_st = MagicMock()
_st.session_state = _session
_st.secrets = {}
sys.modules["streamlit"] = _st
sys.modules["streamlit.components"] = MagicMock()
sys.modules["streamlit.components.v1"] = MagicMock()

# ---------------------------------------------------------------------------
# 2. Force DEBUG = True BEFORE importing any project module.
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).parent))

import config.debug as _debug_mod  # noqa: E402

_debug_mod.DEBUG = True

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from ui.pages.ask_mattgpt.backend_service import rag_answer  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

STORIES_JSONL = Path("echo_star_stories_nlp.jsonl")

MATT_PROBES = [
    ("P1", "How does Matt modernize monoliths into microservices?"),
    ("P2", "How does Matt approach microservices?"),
    ("P3", "How does Matt handle legacy modernization?"),
    ("P4", "How does Matt build MVPs?"),
    ("P5", "How does Matt do platform refactoring?"),
    ("Q1", "How does Matt use event storming?"),
]

REF_PROBES = [
    ("P6", "How do you modernize monoliths into microservices?"),
    ("P7", "How do you build MVPs?"),
    ("P8", "How do you do platform refactoring?"),
]


# ---------------------------------------------------------------------------
# Query transforms
# ---------------------------------------------------------------------------


def _delete(query: str) -> str:
    stripped = re.sub(r"\bMatt(?:'s)?\b\s*", "", query).strip()
    return re.sub(r" {2,}", " ", stripped)


def _substitute(query: str) -> str:
    # possessive first to avoid double-substitution
    result = re.sub(r"\bMatt's\b", "his", query)
    result = re.sub(r"\bMatt\b", "he", result)
    return result


# ---------------------------------------------------------------------------
# Corpus + contamination
# ---------------------------------------------------------------------------


def _load_stories() -> list:
    return load_stories(str(STORIES_JSONL))


def _derive_contam(stories: list) -> frozenset:
    result = set()
    for s in stories:
        client = (s.get("Client") or "").lower().strip()
        if client != "independent project":
            continue
        sid = s.get("id", "")
        title = s.get("Title", "")
        if sid.startswith("career-intent") or "Career Intent" in title:
            continue
        result.add(sid)
    return frozenset(result)


# ---------------------------------------------------------------------------
# Debug output parser
# ---------------------------------------------------------------------------


def _parse_debug(output: str) -> dict:
    data: dict[str, Any] = {"family": None, "hits": []}
    for line in output.splitlines():
        m = re.search(r"Semantic router: valid=\w+, score=[\d.]+, family=(\w+)", line)
        if m:
            data["family"] = m.group(1)
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
    return sid.split("|")[0][:n]


# ---------------------------------------------------------------------------
# Single probe run
# ---------------------------------------------------------------------------


def _run(query: str, stories: list) -> dict:
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

    if not parsed["hits"] and not err:
        print(
            "\nFATAL: zero hits parsed -- DEBUG may be off or parser broken.",
            file=sys.stderr,
        )
        print(captured[:2000], file=sys.stderr)
        sys.exit(1)

    return {
        "family": parsed["family"] or "?",
        "hits": parsed["hits"],
        "sources": sources,
        "err": err,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading stories...", flush=True)
    stories = _load_stories()
    print(f"  {len(stories)} stories loaded", flush=True)

    contam_ids = _derive_contam(stories)
    all_story_ids = {s.get("id", "") for s in stories}
    bad = contam_ids - all_story_ids
    if bad:
        print(f"\nFATAL: derived contam IDs not in JSONL: {bad}", file=sys.stderr)
        sys.exit(1)

    print(f"  {len(contam_ids)} contamination IDs derived")

    # -------------------------------------------------------------------------
    # A/B/C runs for Matt-token probes
    # -------------------------------------------------------------------------
    rows = []

    for pid, query in MATT_PROBES:
        q_b = _delete(query)
        q_c = _substitute(query)

        print(f"\n[{pid}] A: {query}", flush=True)
        a = _run(query, stories)
        status_a, _ = _contam_status(a["hits"], a["sources"], contam_ids)

        print(f"       B: {q_b}", flush=True)
        b = _run(q_b, stories)
        status_b, _ = _contam_status(b["hits"], b["sources"], contam_ids)

        print(f"       C: {q_c}", flush=True)
        c = _run(q_c, stories)
        status_c, _ = _contam_status(c["hits"], c["sources"], contam_ids)

        print(f"       A={status_a} B={status_b} C={status_c}", flush=True)

        rows.append(
            {
                "pid": pid,
                "query_a": query,
                "query_b": q_b,
                "query_c": q_c,
                "family_a": a["family"],
                "status_a": status_a,
                "status_b": status_b,
                "status_c": status_c,
                "lead_a": _short(a["hits"][0]["id"]) if a["hits"] else "—",
                "lead_b": _short(b["hits"][0]["id"]) if b["hits"] else "—",
                "lead_c": _short(c["hits"][0]["id"]) if c["hits"] else "—",
                "sources_a": a["sources"],
                "sources_b": b["sources"],
                "sources_c": c["sources"],
            }
        )

    # -------------------------------------------------------------------------
    # Reference runs
    # -------------------------------------------------------------------------
    ref_rows = []

    for pid, query in REF_PROBES:
        print(f"\n[{pid}] REF: {query}", flush=True)
        r = _run(query, stories)
        status_r, _ = _contam_status(r["hits"], r["sources"], contam_ids)
        lead_r = _short(r["hits"][0]["id"]) if r["hits"] else "—"
        ref_rows.append(
            {
                "pid": pid,
                "family": r["family"],
                "status": status_r,
                "lead": lead_r,
            }
        )
        print(f"       status={status_r}", flush=True)

    # -------------------------------------------------------------------------
    # Summary table -- A/B/C
    # -------------------------------------------------------------------------
    W = 130
    print("\n\n" + "=" * W)
    print("MATTGPT-077 Step 0.6 -- A/B/C Evidence")
    print("  A=original  B=deletion  C=substitution (Matt->he, Matt's->his)")
    print("=" * W)
    print(
        f"{'ID':<3}  {'Family':<20}  {'Sta-A':<5}  {'Lead-A':<36}  ||  {'Sta-B':<5}  {'Lead-B':<36}  ||  {'Sta-C':<5}  {'Lead-C'}"
    )
    print("-" * W)

    for r in rows:

        def delta(sa, sb):
            if sa in ("LEAD", "POOL") and sb == "CLEAN":
                return "FIXED"
            if sa == "CLEAN" and sb in ("LEAD", "POOL"):
                return "REGR"
            if sa == sb and sa != "CLEAN":
                return "same"
            return ""

        db = delta(r["status_a"], r["status_b"])
        dc = delta(r["status_a"], r["status_c"])

        print(
            f"{r['pid']:<3}  {r['family_a']:<20}  {r['status_a']:<5}  {r['lead_a']:<36}  ||  "
            f"{r['status_b']:<5}  {r['lead_b']:<36}  {db:<6}  ||  "
            f"{r['status_c']:<5}  {r['lead_c']:<36}  {dc}"
        )

    print("=" * W)

    # -------------------------------------------------------------------------
    # Reference table
    # -------------------------------------------------------------------------
    print("\nREFERENCE PROBES (no Matt token)")
    print("-" * 70)
    print(f"{'ID':<3}  {'Family':<20}  {'Status':<6}  Lead")
    print("-" * 70)
    for r in ref_rows:
        print(f"{r['pid']:<3}  {r['family']:<20}  {r['status']:<6}  {r['lead']}")
    print("-" * 70)

    # -------------------------------------------------------------------------
    # Q1 full LLM set -- all three arms
    # -------------------------------------------------------------------------
    q1 = next((r for r in rows if r["pid"] == "Q1"), None)
    if q1:
        for arm, label, sources in [
            ("A", q1["query_a"], q1["sources_a"]),
            ("B", q1["query_b"], q1["sources_b"]),
            ("C", q1["query_c"], q1["sources_c"]),
        ]:
            print(f"\nQ1 arm {arm} full LLM set -- '{label}'")
            print("-" * 80)
            for i, s in enumerate(sources):
                marker = "  ** CONTAM" if s.get("id", "") in contam_ids else ""
                print(f"  [{i+1}] {s.get('client','?')}: {s.get('title','?')}{marker}")
            print("-" * 80)

    # -------------------------------------------------------------------------
    # Decision
    # -------------------------------------------------------------------------
    p4 = next((r for r in rows if r["pid"] == "P4"), None)
    p2 = next((r for r in rows if r["pid"] == "P2"), None)
    p3 = next((r for r in rows if r["pid"] == "P3"), None)

    print("\nDECISION EVALUATION")
    print("-" * 50)
    if p4:
        print(f"P4: A={p4['status_a']}  B={p4['status_b']}  C={p4['status_c']}")
    if p2:
        print(f"P2: A={p2['status_a']}  B={p2['status_b']}  C={p2['status_c']}")
    if p3:
        print(f"P3: A={p3['status_a']}  B={p3['status_b']}  C={p3['status_c']}")
    if q1:
        print(f"Q1: A={q1['status_a']}  B={q1['status_b']}  C={q1['status_c']}")
        q1_c_lead = q1["sources_c"][0].get("title", "") if q1["sources_c"] else ""
        print(f"Q1 C LLM[1]: {q1_c_lead}")

    regressions_b = [
        r
        for r in rows
        if r["status_b"] in ("LEAD", "POOL") and r["status_a"] == "CLEAN"
    ]
    regressions_c = [
        r
        for r in rows
        if r["status_c"] in ("LEAD", "POOL") and r["status_a"] == "CLEAN"
    ]
    print(f"New regressions B: {[r['pid'] for r in regressions_b] or 'none'}")
    print(f"New regressions C: {[r['pid'] for r in regressions_c] or 'none'}")

    print("=" * W)
    print("NOTE: DEBUG forced True via config.debug module")


if __name__ == "__main__":
    main()
