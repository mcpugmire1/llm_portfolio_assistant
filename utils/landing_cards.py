"""
Data-driven card derivation for landing pages (Banking, Cross-Industry).

Contract (pinned by tests/unit/test_landing_cards.py):
- Cards are derived from real story data — no hardcoded list.
- Card universe = Solution/Offering values that have >=1 story matching the
  industry filter (after Era exclusion).
- Era exclusion mirrors timeline_view.py:42 — narrative content does not
  contribute to landing-page card counts.
- Tiered: Core (>=3 stories) vs Specialized (<3 stories).
- Subtitle pulled from config.constants.CAPABILITY_SUBTITLES; empty string
  fallback if no curated entry (same pattern as ERA_SUBTITLES).

This module is the structural fix for the May 12, 2026 Card 3 regression
shape: hardcoded card strings cannot reference Solution/Offering values
that don't exist in the data, because cards ARE the data.
"""

from collections import defaultdict
from typing import Any

from config.constants import CAPABILITY_SUBTITLES

# Same constant timeline_view.py uses — narrative content stays off
# project-categorization surfaces. If this rule changes in one place it
# must change in both; see MATTGPT-060 in BACKLOG.md for the lineage.
EXCLUDED_ERA = "Leadership & Professional Narrative"

# Story-count threshold that splits Core (>=) from Specialized (<).
CORE_TIER_THRESHOLD = 3


def build_landing_cards(
    stories: list[dict[str, Any]], industry: str
) -> list[dict[str, Any]]:
    """Return the data-derived list of capability cards for a landing page.

    Each card is a dict with:
      - title: the Solution/Offering value (verbatim from data)
      - count: integer story count (industry-scoped, post Era exclusion)
      - clients: integer unique-client count for those stories
      - subtitle: editorial description from CAPABILITY_SUBTITLES, or ""
      - tier: "core" if count >= CORE_TIER_THRESHOLD, else "specialized"

    Cards are returned in story-count descending order within each tier
    (Core cards first, then Specialized).
    """
    # Filter to industry + drop narrative Era stories.
    filtered = [
        s
        for s in stories
        if s.get("Industry") == industry
        and s.get("Era") != EXCLUDED_ERA
        and s.get("Solution / Offering")
    ]

    # Group by Solution/Offering.
    by_offering: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for s in filtered:
        by_offering[s["Solution / Offering"]].append(s)

    cards: list[dict[str, Any]] = []
    for offering, group in by_offering.items():
        count = len(group)
        clients = {s.get("Client") for s in group if s.get("Client")}
        tier = "core" if count >= CORE_TIER_THRESHOLD else "specialized"
        cards.append(
            {
                "title": offering,
                "count": count,
                "clients": len(clients),
                "subtitle": CAPABILITY_SUBTITLES.get(offering, ""),
                "tier": tier,
            }
        )

    # Sort: Core first (within Core by count desc), then Specialized (by count desc).
    cards.sort(key=lambda c: (0 if c["tier"] == "core" else 1, -c["count"]))
    return cards
