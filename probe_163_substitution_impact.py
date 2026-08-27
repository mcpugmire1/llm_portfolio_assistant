"""MATTGPT-163 discovery: measure whether pronoun substitution earns its place.

_substitute_matt_subject() (utils/scoring.py:117) replaces "Matt's" -> "his"
and "Matt" -> "he" in the retrieval query when intent_family is in
SUBSTITUTION_FAMILIES (technical, team_scaling, agile_transformation per
config/constants.py:73). The substituted string feeds both the embedding and
the keyword scorer.

On team_scaling queries the substitution can produce grammatical breakage
("How many people reported to Matt at the CIC" -> "reported to he at the
CIC"), though only the embedding sees it.

For each query, this probe calls semantic_search twice -- once with the
original string, once with the substituted string -- and prints top-10 hits
with pc scores side by side. Reports Jaccard overlap, order shifts, and
stories unique to each arm.

No LLM calls. Embeddings only, effectively free.
"""

import sys
from unittest.mock import MagicMock


class _SS(dict):
    pass


_st = MagicMock()
_st.session_state = _SS()
_st.secrets = {}
sys.modules["streamlit"] = _st
sys.modules["streamlit.components"] = MagicMock()
sys.modules["streamlit.components.v1"] = MagicMock()

from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))

import config.debug as _dbg  # noqa: E402

_dbg.DEBUG = False

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from services.rag_service import semantic_search  # noqa: E402
from utils.corpus_loader import load_stories  # noqa: E402
from utils.scoring import _substitute_matt_subject  # noqa: E402

QUERIES = [
    "How many people reported to Matt at the CIC",
    "How many direct reports did Matt have",
    "What did Matt do before Accenture",
    "Tell me about Matt's leadership style",
    "How did Matt scale the team",
]

TOP_K = 10


def _top_ids_and_scores(result: dict) -> tuple[list[str], dict[str, float]]:
    hits = (result or {}).get("results", []) or []
    ids = [str(s.get("id", "") or "") for s in hits[:TOP_K]]
    scores = {
        str(s.get("id", "") or ""): float(s.get("pc", 0.0) or 0.0) for s in hits[:TOP_K]
    }
    return ids, scores


def _print_side_by_side(
    q: str, sub: str, ids_o: list[str], sc_o: dict, ids_s: list[str], sc_s: dict
) -> None:
    print(f"\n{'=' * 100}")
    print(f"ORIGINAL:    {q!r}")
    print(f"SUBSTITUTED: {sub!r}")
    print("=" * 100)
    print(f"{'#':<3} {'ORIGINAL (pc)':<48} {'SUBSTITUTED (pc)':<48}")
    print("-" * 100)
    n = max(len(ids_o), len(ids_s))
    for i in range(n):
        left = ""
        if i < len(ids_o):
            sid = ids_o[i]
            left = f"{sid[:38]:<38} ({sc_o.get(sid, 0.0):.3f})"
        right = ""
        if i < len(ids_s):
            sid = ids_s[i]
            right = f"{sid[:38]:<38} ({sc_s.get(sid, 0.0):.3f})"
        print(f"{i+1:<3} {left:<48} {right:<48}")


def _print_diff_summary(ids_o: list[str], ids_s: list[str]) -> None:
    set_o, set_s = set(ids_o), set(ids_s)
    overlap = set_o & set_s
    only_o = sorted(set_o - set_s)
    only_s = sorted(set_s - set_o)
    union = set_o | set_s
    jaccard = len(overlap) / len(union) if union else 0.0

    order_shifts = []
    for sid in overlap:
        r_o = ids_o.index(sid)
        r_s = ids_s.index(sid)
        if r_o != r_s:
            order_shifts.append((sid, r_o + 1, r_s + 1))

    print()
    print(f"OVERLAP:  {len(overlap)}/{TOP_K}   JACCARD: {jaccard:.2f}")
    if only_o:
        print(f"ONLY IN ORIGINAL ({len(only_o)}):")
        for sid in only_o[:5]:
            print(f"  - {sid}")
    if only_s:
        print(f"ONLY IN SUBSTITUTED ({len(only_s)}):")
        for sid in only_s[:5]:
            print(f"  - {sid}")
    if order_shifts:
        print(f"ORDER SHIFTS ({len(order_shifts)} common stories moved):")
        for sid, o, s in sorted(
            order_shifts, key=lambda x: abs(x[1] - x[2]), reverse=True
        )[:5]:
            print(f"  - {sid[:60]}: rank {o} -> {s}  (delta {s-o:+d})")
    elif overlap:
        print("ORDER: identical for overlapping stories")


def run() -> None:
    stories = load_stories("echo_star_stories_nlp.jsonl")
    print(f"Corpus: {len(stories)} stories | top-k={TOP_K}\n")

    verdicts = []
    for q in QUERIES:
        sub = _substitute_matt_subject(q)
        r_o = semantic_search(q, {}, stories=stories, top_k=TOP_K)
        r_s = semantic_search(sub, {}, stories=stories, top_k=TOP_K)

        ids_o, sc_o = _top_ids_and_scores(r_o)
        ids_s, sc_s = _top_ids_and_scores(r_s)

        _print_side_by_side(q, sub, ids_o, sc_o, ids_s, sc_s)
        _print_diff_summary(ids_o, ids_s)

        set_o, set_s = set(ids_o), set(ids_s)
        jaccard = len(set_o & set_s) / len(set_o | set_s) if (set_o | set_s) else 0.0
        differ_in_membership = set_o != set_s
        order_shifts = sum(
            1 for sid in (set_o & set_s) if ids_o.index(sid) != ids_s.index(sid)
        )
        verdicts.append((q, jaccard, differ_in_membership, order_shifts))

    print(f"\n{'=' * 100}")
    print("SUMMARY")
    print("=" * 100)
    print(f"{'query':<52} {'jaccard':>8} {'membership':>12} {'order-shifts':>13}")
    print("-" * 100)
    for q, j, memb, shifts in verdicts:
        print(
            f"{q[:50]:<52} {j:>8.2f} {('different' if memb else 'same'):>12} {shifts:>13}"
        )


if __name__ == "__main__":
    run()
