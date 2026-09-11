"""MATTGPT-249 before-and-after benchmark: measure the rank of the JP
Morgan Dynamics CRM crisis story in retrieve_stories() against the AT&T
Row 6 requirement.

Originally written as MATTGPT-243's pre-Red top_k probe. When the
Sept 11, 2026 run put the target at rank 18, top_k left -243 and this
probe was repurposed as the ranking benchmark for -249. Re-run this
before and after any -249 change to the ranker or filter path so the
rank movement is legible.

Corpus finding at first run (Sept 11, 2026, pre-249): target at rank 18,
score 0.3733. Top 8 dominated by internal Accenture-authored leadership
stories; three of eight carry Theme == "Professional Narrative", so PN
alone is not the discriminating signal (Cowork corroboration in
MATTGPT-249). The target itself carries the incident vocabulary in its
own text, so this is a ranking problem, not a corpus gap.

Source of the requirement string: probe_159_att_output/arm2_run1.json,
Row 6 (see MATTGPT-159 AT&T audit).

Run: python probe_243_top_k_rank.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from services.jd_assessor import retrieve_stories
from utils.corpus_loader import load_stories

load_dotenv()

ATT_ROW_6_REQUIREMENT = (
    "Calm, decisive leadership during incidents, escalations, and "
    "high-pressure situations"
)
TARGET_STORY_ID = (
    "rescuing-and-stabilizing-jp-morgans-ts-dynamics-crm-program|jp-morgan-chase"
)
TARGET_STORY_TITLE = "Rescuing and Stabilizing JP Morgan's TS Dynamics CRM Program"
PROBE_TOP_K = 25


def main() -> None:
    stories = load_stories("echo_star_stories_nlp.jsonl")
    print(f"Corpus: {len(stories)} stories loaded.\n")

    results = retrieve_stories(ATT_ROW_6_REQUIREMENT, stories, top_k=PROBE_TOP_K)

    print(f"Requirement: {ATT_ROW_6_REQUIREMENT!r}")
    print(f"Target:      {TARGET_STORY_TITLE!r}")
    print(f"Target id:   {TARGET_STORY_ID}")
    print(f"Probe top_k: {PROBE_TOP_K}\n")

    print(f"{'rank':>4}  {'score':>8}  id / title")
    print("-" * 88)
    target_rank = None
    for rank, hit in enumerate(results, 1):
        marker = " <== target" if hit["id"] == TARGET_STORY_ID else ""
        print(
            f"{rank:>4}  {hit['score']:>8.4f}  {hit['id']} / {hit['title'][:60]}{marker}"
        )
        if hit["id"] == TARGET_STORY_ID:
            target_rank = rank

    print()
    if target_rank is None:
        print(f"Target NOT in top {PROBE_TOP_K}. Re-run at higher top_k to locate.")
    else:
        print(
            f"Target rank: {target_rank}  (score {results[target_rank - 1]['score']:.4f})"
        )
        print(
            "Compare this rank against the last recorded value in MATTGPT-249 to "
            "see the direction of change from any ranker or filter-path edit."
        )


if __name__ == "__main__":
    main()
