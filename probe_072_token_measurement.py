"""MATTGPT-072: measure actual input token count for the tag prompt.

Builds the real system_msg and user_msg per current extract_semantic_tags,
counts tokens with tiktoken against gpt-4o, and reports corpus-wide stats
plus three named samples (sparse, average, dense).

No API calls. Sanity-check the measured average against OpenAI dashboard's
3,216 tokens-per-request (30-day, all callers).
"""

import statistics
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

_dbg.DEBUG = False

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

import tiktoken  # noqa: E402

from generate_public_tags import TECHNICAL_ONLY_ERAS, _prompt_view  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402

# Match the exact strings in generate_public_tags.py extract_semantic_tags.
SYSTEM_MSG = (
    "You are generating discovery vocabulary for a portfolio of STAR stories.\n\n"
    "public_tags are search terms: words a reader might type into a search box "
    "to find this story. They are NOT a claim about what the practitioner is "
    "skilled at; capability is captured separately in the Competencies field, "
    "which this prompt does not produce.\n\n"
    "Given the story data provided by the user, generate distinct tags naming "
    "what the story is ABOUT: topics, technologies, domains, methodologies, "
    "and concepts a reader might use to search for it. Do not produce multiple "
    "phrasings of the same concept."
)

IPD_CONTEXT_NOTE = (
    "\n\n**CONTEXT FOR THIS STORY:**\n"
    "This story documents independent product engineering work: solo or "
    "small-team development with no external client and no organizational "
    "stakeholders to coordinate across. Use product engineering and technical "
    "vocabulary. Avoid business strategy and organizational leadership phrasing. "
    "Do not infer stakeholder coordination, change management, or cross-functional "
    "dynamics where the work was independent."
)


def _build_user_msg(story: dict) -> str:
    view = _prompt_view(story)
    context_note = IPD_CONTEXT_NOTE if view["Era"] in TECHNICAL_ONLY_ERAS else ""
    return (
        f"Title: {view['Title']}\n"
        f"Role: {view['Role']}\n"
        f"Industry: {view['Industry']}\n"
        f"Theme: {view['Theme']}\n"
        f"Category: {view['Category']}\n"
        f"Sub-category: {view['Sub-category']}\n"
        f"Project Scope: {view['Project Scope / Complexity']}\n"
        f"Competencies: {view['Competencies']}\n"
        f"Use Cases: {view['Use Case(s)']}\n"
        f"Situation: {view['Situation']}\n"
        f"Task: {view['Task']}\n"
        f"Action: {view['Action']}\n"
        f"Result: {view['Result']}\n"
        f"Process: {view['Process']}\n"
        f"Performance: {view['Performance']}" + context_note
    )


def _count_chat_tokens(system_msg: str, user_msg: str, encoding) -> int:
    """Total input tokens for a system+user chat completion, per OpenAI cookbook.

    tokens_per_message=3, plus reply priming (3), plus role tokens (implicit).
    """
    tokens_per_message = 3
    total = 0
    for msg in (
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ):
        total += tokens_per_message
        total += len(encoding.encode(msg["role"]))
        total += len(encoding.encode(msg["content"]))
    total += 3  # reply priming
    return total


def main():
    stories = load_stories("echo_star_stories_nlp.jsonl")
    encoding = tiktoken.encoding_for_model("gpt-4o")

    per_story = []
    id_to_story = {}
    for i, s in enumerate(stories):
        user_msg = _build_user_msg(s)
        tokens = _count_chat_tokens(SYSTEM_MSG, user_msg, encoding)
        per_story.append((i + 1, s.get("id", ""), s.get("Title", ""), tokens))
        id_to_story[str(s.get("id", ""))] = (i + 1, tokens)

    counts = [t for _, _, _, t in per_story]
    counts_sorted = sorted(counts)

    print(f"Corpus: {len(stories)} stories")
    print(f"System message tokens alone: {len(encoding.encode(SYSTEM_MSG))}")
    print()

    print("=" * 70)
    print("INPUT TOKEN DISTRIBUTION (system + user + chat overhead)")
    print("=" * 70)
    print(f"  min:    {min(counts):>5}")
    print(f"  p10:    {counts_sorted[int(0.10 * len(counts))]:>5}")
    print(f"  p25:    {counts_sorted[int(0.25 * len(counts))]:>5}")
    print(f"  median: {int(statistics.median(counts)):>5}")
    print(f"  mean:   {int(statistics.mean(counts)):>5}")
    print(f"  p75:    {counts_sorted[int(0.75 * len(counts))]:>5}")
    print(f"  p90:    {counts_sorted[int(0.90 * len(counts))]:>5}")
    print(f"  max:    {max(counts):>5}")
    print()

    named_targets = (
        ("why-hire-matt", "SPARSE (positioning arc)"),
        ("leading-people-from-delivery-teams", "AVERAGE (leadership narrative)"),
        ("integrating-a-chemical-logistics-network", "DENSE (Cendian integration)"),
    )
    print("=" * 70)
    print("NAMED SAMPLES")
    print("=" * 70)
    for sub, label in named_targets:
        match = next((r for r in per_story if sub in str(r[1]).lower()), None)
        if match:
            row, sid, title, tokens = match
            print(f"  {label}")
            print(f"    Row {row}: {title[:60]}")
            print(f"    Tokens: {tokens}")
            print()

    print("=" * 70)
    print("SANITY CHECK vs OpenAI dashboard")
    print("=" * 70)
    dashboard_avg = 3216
    corpus_mean = int(statistics.mean(counts))
    corpus_median = int(statistics.median(counts))
    delta_mean = corpus_mean - dashboard_avg
    delta_median = corpus_median - dashboard_avg
    print(f"  Dashboard 30-day avg (all callers): {dashboard_avg}")
    print(
        f"  This script's mean per-story:       {corpus_mean}  (delta: {delta_mean:+d})"
    )
    print(
        f"  This script's median per-story:     {corpus_median}  (delta: {delta_median:+d})"
    )
    print()

    # Recommended constant
    print("=" * 70)
    print("RECOMMENDED CONSTANT for cost estimate")
    print("=" * 70)
    print(f"  Use mean:   {corpus_mean} (fair estimate across the corpus)")
    print(f"  Use median: {corpus_median} (typical single story)")
    print("  Current code assumes: 1000 (drastically low)")


if __name__ == "__main__":
    main()
