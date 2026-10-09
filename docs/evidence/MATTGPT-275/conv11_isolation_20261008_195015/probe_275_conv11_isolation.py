"""MATTGPT-275 conversation 11 isolation: query wording vs MATT_DNA CIC lines. Not tracked.

All arms use the pre-contract Green system prompt (build_system_prompt +
the **TOOLS:** note + build_answer_instructions with all 12 openers as
examples), rebuilt here from the unchanged old builders and checked
byte-for-byte against the capture taken before the contract prompt. One
variable per arm:

  baseline    pre-contract Green as captured ("A standalone search query.")
  query_only  baseline + only the query description changed to the new wording
  dna_only    baseline + only the three CIC lines removed from MATT_DNA
              ("Built CIC from 0 to N+ practitioners" twice, "CIC teams of 10
              consistently delivered impact of typical teams of 20")

Conversation 11 through send_to_backend() (history built as the UI does),
N runs per arm. Loggers patched out; no model or retrieval call mocked.

Usage: python probes/probe_275_conv11_isolation.py <out_dir> <runs> <pre_contract_capture.txt>
"""

import copy
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
from ui.pages.ask_mattgpt.prompts import build_answer_instructions, build_system_prompt  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

out_dir, runs, capture_path = Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
out_dir.mkdir(parents=True, exist_ok=True)
stories = load_stories(str(REPO / "echo_star_stories_nlp.jsonl"))
bs.sync_portfolio_metadata(stories)

# Pre-contract Green, verbatim from the working tree before the contract prompt.
OLD_TOOL_STORY_NOTE = (
    "No stories are preloaded. Call search_stories when the question needs "
    "evidence from Matt's work history. Answer directly from the facts about "
    "Matt above or from the conversation when they already answer it."
)
OLD_OPENER_LINE = (
    "Begin with a short opening line in Agy's voice. Examples of how Agy opens: "
    + "; ".join(f'"{o}"' for o in bs.SYNTHESIS_OPENERS + bs.STANDARD_OPENERS)
    + "."
)
OLD_QUERY_DESC = "A standalone search query."
NEW_QUERY_DESC = bs._SEARCH_STORIES_TOOL["function"]["parameters"]["properties"]["query"]["description"]


def old_system_prompt(is_synthesis, matt_dna, profile_facts, opener_examples, focus_angle=""):
    return (
        build_system_prompt(is_synthesis=is_synthesis, matt_dna=matt_dna, profile_facts=profile_facts)
        + "\n\n**TOOLS:** "
        + OLD_TOOL_STORY_NOTE
        + "\n\n"
        + build_answer_instructions(
            opening_line=OLD_OPENER_LINE,
            is_synthesis=is_synthesis,
            focus_angle=focus_angle if not is_synthesis else "",
            profile_facts=profile_facts,
        )
    )


def tool_with(desc):
    t = copy.deepcopy(bs._SEARCH_STORIES_TOOL)
    t["function"]["parameters"]["properties"]["query"]["description"] = desc
    return t


CIC_PREFIXES = ("- Built CIC from 0 to", "- CIC teams of 10 consistently delivered")
DNA_NO_CIC = "\n".join(line for line in bs.MATT_DNA.splitlines() if not line.startswith(CIC_PREFIXES))
removed = [line for line in bs.MATT_DNA.splitlines() if line.startswith(CIC_PREFIXES)]
assert len(removed) == 3, removed

# Parity: the rebuilt baseline system prompt equals the pre-contract capture.
captured_system = capture_path.read_text().split("===== SYSTEM =====\n", 1)[1].split("\n\n===== USER =====", 1)[0]
cap = []


class _Fake:
    def __init__(self):
        self.chat = MagicMock()
        self.chat.completions.create = self._c

    def _c(self, **k):
        cap.append(k)
        m = MagicMock()
        m.choices = [MagicMock(message=MagicMock(content="ok", tool_calls=None))]
        return m


import random  # noqa: E402

random.seed(7)
_ms = MagicMock()
_ms.session_state = {}
with (
    patch.object(bs, "_openai_client", lambda: _Fake()),
    patch.object(bs, "st", _ms),
    patch.object(bs, "is_portfolio_query_semantic", return_value=(True, 0.6, "x", "behavioral")),
    patch.object(bs, "is_nonsense", return_value=None),
    patch.object(bs, "log_query", MagicMock()),
    patch.object(bs, "build_tool_system_prompt", old_system_prompt),
):
    bs.agy_answer("Tell me about his payments work", stories, history=[])
parity = cap[0]["messages"][0]["content"] == captured_system.rstrip("\n") or cap[0]["messages"][0]["content"] == captured_system
print("baseline parity with pre-contract capture:", parity, flush=True)
assert parity, "rebuilt baseline differs from the pre-contract capture"

ARMS = {
    "baseline": {"dna": bs.MATT_DNA, "tool": tool_with(OLD_QUERY_DESC)},
    "query_only": {"dna": bs.MATT_DNA, "tool": tool_with(NEW_QUERY_DESC)},
    "dna_only": {"dna": DNA_NO_CIC, "tool": tool_with(OLD_QUERY_DESC)},
}
QUESTIONS = [
    "How did Matt scale engineering teams from 4 to 150+ people?",
    "Tell me about his payments work",
    "how big was his teams",
]
rows = []
for arm, cfg in ARMS.items():
    for run in range(1, runs + 1):
        session = {"ask_transcript": []}
        for turn, q in enumerate(QUESTIONS, 1):
            session["ask_transcript"].append({"role": "user", "text": q})
            queries = []
            real_search = bs.semantic_search

            def search_wrap(query, *a, _rs=real_search, **k):
                queries.append(query)
                return _rs(query, *a, **k)

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
                patch.object(bs, "build_tool_system_prompt", old_system_prompt),
                patch.object(bs, "MATT_DNA", cfg["dna"]),
                patch.object(bs, "_SEARCH_STORIES_TOOL", cfg["tool"]),
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
            rows.append({"arm": arm, "run": run, "turn": turn, "question": q, "search_queries": queries,
                         "sources": [s.get("title") for s in r.get("sources") or []], "answer_md": ans})
            print(f"[{arm} r{run} t{turn}] q={queries}", flush=True)
(out_dir / "conv11_isolation.json").write_text(json.dumps(
    {"removed_dna_lines": removed, "new_query_desc": NEW_QUERY_DESC, "rows": rows}, indent=2, ensure_ascii=False))
print("done", len(rows))
