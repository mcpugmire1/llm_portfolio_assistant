"""
MATTGPT-077 Step A -- degenerate-query probe.

Runs "Matt?" and "he?" through the production pipeline.
Two equally informative outcomes:
  (1) low scores, gate-caught -- zero hits, gate lines visible in debug
  (2) centroid-junk retrieval at confident classification -- pre-existing
      finding about confidence gate on degenerate queries (BACKLOG shape)

Zero hits is NOT a script failure here. Distinguish gate-caught from
parser-silent via raw debug lines: if hits==0 and no gate/router lines
appear in capture, the parser missed everything -- read raw output.

Output: stdout only.
"""

import contextlib
import io
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock


class _SessionState(dict):
    pass


_session = _SessionState()
_session["__suppress_logging__"] = True

_st = MagicMock()
_st.session_state = _session
_st.secrets = {}
sys.modules["streamlit"] = _st
sys.modules["streamlit.components"] = MagicMock()
sys.modules["streamlit.components.v1"] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent))

import config.debug as _debug_mod  # noqa: E402

_debug_mod.DEBUG = True

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from ui.pages.ask_mattgpt.backend_service import rag_answer  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

STORIES_JSONL = Path("echo_star_stories_nlp.jsonl")
PROBES = [("matt_q", "Matt?"), ("he_q", "he?")]

GATE_KEYWORDS = (
    "confidence",
    "Confidence",
    "gate",
    "Gate",
    "nonsense",
    "out_of_scope",
    "router",
    "Router",
    "semantic",
    "Semantic",
    "valid",
    "invalid",
)


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


def _parse_hits(output: str) -> list:
    hits = []
    for line in output.splitlines():
        m = re.search(
            r"DEBUG Hit: id=(\S+) pc=([\d.]+) kw=([\d.]+) blend=([\d.]+)", line
        )
        if m:
            hits.append(
                {
                    "id": m.group(1),
                    "pc": float(m.group(2)),
                    "kw": float(m.group(3)),
                    "blend": float(m.group(4)),
                }
            )
    return hits


def _short(sid: str, n: int = 50) -> str:
    return sid.split("|")[0][:n]


def main():
    print("Loading stories...", flush=True)
    stories = _load_stories()
    contam_ids = _derive_contam(stories)
    print(f"  {len(stories)} stories, {len(contam_ids)} contam IDs")

    for pid, query in PROBES:
        print(f"\n{'=' * 70}")
        print(f"[{pid}] query: {query!r}")
        print(f"{'=' * 70}")

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
        hits = _parse_hits(captured)
        sources = result.get("sources", []) if result else []
        gate_lines = [
            ln for ln in captured.splitlines() if any(kw in ln for kw in GATE_KEYWORDS)
        ]

        # Zero-hits discriminator
        if not hits:
            if gate_lines:
                print("Pool hits: 0  [GATE-CAUGHT -- gate/router lines present]")
            else:
                print(
                    "Pool hits: 0  *** WARN: no gate lines in capture -- possible parser failure; read raw output below ***"
                )
        else:
            print(f"Pool hits: {len(hits)}")
            for i, h in enumerate(hits):
                marker = "  ** CONTAM" if h["id"] in contam_ids else ""
                lead = " [LEAD]" if i == 0 else ""
                print(
                    f"  [{i+1:>2}] pc={h['pc']:.4f} kw={h['kw']:.4f} blend={h['blend']:.4f}  {_short(h['id'])}{lead}{marker}"
                )

        print(f"LLM set: {len(sources)} stories")
        for i, s in enumerate(sources):
            marker = "  ** CONTAM" if s.get("id", "") in contam_ids else ""
            print(f"  [{i+1}] {s.get('client','?')}: {s.get('title','?')}{marker}")

        if err:
            print(f"ERROR: {err}")

        print(f"\nGate/router/confidence debug lines ({len(gate_lines)}):")
        if gate_lines:
            for line in gate_lines:
                print(f"  {line}")
        else:
            print("  (none -- full raw capture follows)")
            print(captured[:3000])

    print(f"\n{'=' * 70}")
    print("NOTE: DEBUG forced True via config.debug module")


if __name__ == "__main__":
    main()
