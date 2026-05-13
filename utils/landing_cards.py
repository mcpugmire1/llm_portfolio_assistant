"""
Data-driven card derivation and JS click-bridge for landing pages
(Banking, Cross-Industry).

Two functions, two halves of the same contract:

build_landing_cards(stories, industry) — pure data transformation. Returns
the tiered card list (Core/Specialized) derived from real story data.
Contract pinned by tests/unit/test_landing_cards.py.

build_card_wiring_js(industry_prefix, core_count, spec_count) — pure string
producer. Returns the JS click-bridge that wires visible card divs to
hidden Streamlit buttons. Co-located with build_landing_cards so both
halves of the contract (data → cards → wiring) live in one source of truth.
Contract pinned by tests/unit/test_banking_landing_js.py (and the
cross-industry equivalent once that lands).

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


def build_card_wiring_js(industry_prefix: str, core_count: int, spec_count: int) -> str:
    """Build the JS click-bridge that wires visible card divs to hidden Streamlit buttons.

    Args:
        industry_prefix: short prefix that identifies the landing page in
            element naming. Used in both card IDs (`card-{industry_prefix}-{tier}-{idx}`)
            and Streamlit button keys (`card_btn_{industry_prefix}_{tier}_{idx}`).
            Examples: "banking", "cross_industry".
        core_count: number of Core-tier cards rendered on the page.
        spec_count: number of Specialized-tier cards rendered on the page.

    Returns:
        A `<script>` block (as a string) that, when injected via
        components.html(), iterates the tiers and wires onclick handlers
        from each visible card to its hidden Streamlit button.

    Contract: the patterns this JS uses for card IDs and button keys must
    match the patterns render_*_landing() functions actually create. If
    they drift, clicks silently no-op (the May 12 click-bridge bug shape).
    Drift caught by tests/unit/test_banking_landing_js.py (and the
    cross-industry equivalent).
    """
    return f"""
<script>
(function() {{
    function wireCards() {{
        const parentDoc = window.parent.document;

        // Wire CTA button
        const ctaBtn = parentDoc.getElementById('btn-{industry_prefix.replace("_", "-")}-cta');
        if (ctaBtn && !ctaBtn.dataset.wired) {{
            ctaBtn.dataset.wired = 'true';
            ctaBtn.onclick = function() {{
                const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_{industry_prefix}_cta"] button');
                if (stBtn) stBtn.click();
            }};
        }}

        // Wire capability cards. Both tiers share the same shape — only the
        // tier prefix in the card ID and button key differs.
        const tiers = [
            ['core', {core_count}],
            ['spec', {spec_count}],
        ];
        tiers.forEach(function(tierEntry) {{
            const tier = tierEntry[0];
            const count = tierEntry[1];
            for (let idx = 0; idx < count; idx++) {{
                const cardId = `card-{industry_prefix.replace("_", "-")}-${{tier}}-${{idx}}`;
                const card = parentDoc.getElementById(cardId);
                if (card && !card.dataset.wired) {{
                    card.dataset.wired = 'true';
                    card.onclick = function() {{
                        const stBtn = parentDoc.querySelector(
                            `[class*="st-key-card_btn_{industry_prefix}_${{tier}}_${{idx}}"] button`
                        );
                        if (stBtn) stBtn.click();
                    }};
                }}
            }}
        }});
    }}

    // Run multiple times to catch all cards as they render
    setTimeout(wireCards, 100);
    setTimeout(wireCards, 300);
    setTimeout(wireCards, 600);
    setTimeout(wireCards, 1000);
}})();
</script>
"""
