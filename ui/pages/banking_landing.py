"""
Banking Landing Page

Banking projects organized by capability and client.
Counts are derived dynamically from JSONL data.
"""

from collections import Counter

import streamlit as st
import streamlit.components.v1 as components

from ui.components.footer import render_footer
from ui.components.how_i_built_dialog import render_how_i_built_dialog
from ui.components.why_agy_dialog import render_why_agy_dialog
from utils.client_utils import is_generic_client
from utils.landing_cards import build_card_wiring_js, build_landing_cards


def render_banking_landing(stories: list[dict]):
    """Render Banking / Financial Services landing page using Streamlit components

    Args:
        stories: Full story corpus from JSONL.

    KNOWN ISSUE: Streamlit preserves scroll position when using st.session_state + st.rerun(),
    causing pages to load at the same vertical position as the previous page. This is a
    Streamlit limitation that cannot be overridden without converting to multipage app.
    """
    # === DYNAMIC COUNTS (derived from JSONL) ===
    # MATTGPT-104: post-Era counts — exclude Professional Narrative stories
    # so hero/stats agree with the landing card grid (which already excludes
    # narrative via build_landing_cards) and with Home / Timeline / Explore
    # Stories. Without this, hero showed 33 while card grid showed 32.
    banking_stories = [
        s
        for s in stories
        if s.get("Industry") == "Financial Services / Banking"
        and s.get("Category") != "Professional Narrative"
    ]
    total_projects = len(banking_stories)

    # Client counts (excluding generic clients)
    client_counter = Counter(
        s.get("Client", "Unknown")
        for s in banking_stories
        if not is_generic_client(s.get("Client"))
    )
    named_clients = [(client, count) for client, count in client_counter.most_common()]
    num_clients = len(named_clients)

    # Capability areas (unique Solution / Offering values)
    capabilities = set(
        s.get("Solution / Offering", "")
        for s in banking_stories
        if s.get("Solution / Offering")
    )
    num_capabilities = len(capabilities)

    # === END DYNAMIC COUNTS ===

    # Scroll to top on page load
    components.html(
        """
        <script>
            setTimeout(function() {
                const main = window.parent.document.querySelector('[data-testid="stMain"]');
                if (main) main.scrollTop = 0;
            }, 100);
        </script>
        """,
        height=0,
    )

    if st.session_state.get("active_dialog") == "why_agy":
        render_why_agy_dialog()
        st.session_state.pop("active_dialog", None)
    elif st.session_state.get("active_dialog") == "how_i_built":
        render_how_i_built_dialog()
        st.session_state.pop("active_dialog", None)

    # Hidden trigger — position:absolute+height:0 removes from flow (no layout space).
    # Must come before the hero so CSS in the hero's <style> block can target it.
    # Pattern mirrors ask_mattgpt_header.py how_agy_trigger handling exactly.
    if st.button("trigger", key="why_agy_banking_trigger"):
        st.session_state["active_dialog"] = "why_agy"
        st.rerun()
    components.html(
        """
<script>
(function() {
    function wireBadge() {
        var parentDoc = window.parent.document;
        var badge = parentDoc.getElementById('why-agy-badge-banking');
        var btn = parentDoc.querySelector('[class*="st-key-why_agy_banking_trigger"] button');
        if (badge && btn && !badge.dataset.wired) {
            badge.dataset.wired = 'true';
            badge.addEventListener('pointerdown', function(e) {
                e.preventDefault();
                btn.click();
            });
            return true;
        }
        return false;
    }
    if (!wireBadge()) {
        var attempts = 0;
        var iv = setInterval(function() {
            if (wireBadge() || ++attempts > 10) clearInterval(iv);
        }, 200);
    }
})();
</script>
""",
        height=0,
    )

    # Hero — CSS for trigger hiding embedded here (same st.markdown = same
    # stMarkdownContainer, no extra DOM element before the hero).
    st.markdown(
        f"""
<style>
[class*="st-key-why_agy_banking_trigger"] {{
    position: absolute !important;
    left: -9999px !important;
    height: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}
div[data-testid="stElementContainer"]:has([class*="st-key-why_agy_banking_trigger"]) {{
    position: absolute !important;
    left: -9999px !important;
    height: 0 !important;
    overflow: hidden !important;
}}
</style>
<div class="conversation-header">
    <div class="conversation-header-content">
        <div style="position: relative; display: inline-block; flex-shrink: 0;">
            <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_banking.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
            <span class="why-agy-badge--header" id="why-agy-badge-banking">i</span>
        </div>
        <div class="conversation-header-text">
            <h1>Matt's Financial Services Expertise</h1>
            <p>{total_projects} projects across {num_capabilities} specialized areas — trust Agy 🐾 to filter decades of domain experience</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Stats bar - using same pattern as hero.py
    st.markdown(
        f'''
    <div class="stats-bar">
        <div class="stat">
            <div class="stat-number">{total_projects}</div>
            <div class="stat-label">Projects Delivered</div>
        </div>
        <div class="stat">
            <div class="stat-number">{num_capabilities}</div>
            <div class="stat-label">Capability Areas</div>
        </div>
        <div class="stat">
            <div class="stat-number">{num_clients}</div>
            <div class="stat-label">Banking Clients</div>
        </div>
    </div>
    ''',
        unsafe_allow_html=True,
    )

    # Inject CSS for this page
    st.markdown(
        """
    <style>
    /* === CARD BUTTON STYLES === */

    /* Ask Agy button - always purple filled */
    .card-btn-primary {
        display: inline-block;
        padding: 14px 28px;
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        border: none;
        border-radius: 8px;
        color: white !important;
        font-weight: 600;
        font-size: 15px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25);
    }

    .card-btn-primary:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
        text-decoration: none !important;
    }

    /* Hide the trigger buttons */
    [class*="st-key-card_btn_"] {
        display: none !important;
    }

    /* CTA section (theme-aware) */
    .cta-section {
        background: var(--bg-surface);
        padding: 38px 32px;
        text-align: center;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        margin: 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .cta-heading {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: var(--text-heading) !important;
        margin-bottom: 16px !important;
    }

    .cta-subtext {
        font-size: 16px;
        color: var(--text-secondary);
        margin-bottom: 0px;
        line-height: 1.6;
    }

    /* Conversation header styles for hero section */
    .conversation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        min-height: 184px;
        box-sizing: border-box;
        border-radius: 0;
        margin: -2rem 0 0 0;
    }

    .conversation-header-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0;
    }

    .conversation-agy-avatar {
            flex-shrink: 0;
            width: 120px !important;
            height: 120px !important;
            border-radius: 50% !important;
            border: 4px solid white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }

    .conversation-header-text h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
    }

    .conversation-header-text p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* Landing page specific styles */
    .stApp {
        background: var(--bg-primary) !important;
    }
    .main .block-container {
        max-width: 1400px !important;
        background: var(--bg-primary) !important;
    }
    h1 {
        color: var(--text-heading) !important;
        font-size: 28px !important;
        margin-bottom: 8px !important;
    }
    .subtitle {
        color: var(--text-secondary);
        font-size: 14px;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-heading);
        margin-top: 5px;
        margin-bottom: 16px;
    }
    /* Stats bar - matches hero.py pattern exactly */
    .stats-bar {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        border-bottom: 2px solid var(--border-color);
        margin-bottom: 8px;
    }
    .stat {
        padding: 2px;
        text-align: center;
        border-right: 1px solid var(--border-color);
    }
    .stat:last-child {
        border-right: none;
    }
    .stat-number {
        font-size: 36px;
        font-weight: 700;
        color: var(--purple-gradient-start);
        margin-bottom: 8px;
        display: block;
    }
    .stat-label {
        font-size: 14px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* === MOBILE RESPONSIVE === */
    @media (max-width: 767px) {
        /* Header - compact and stacked */
        .conversation-header {
            padding: 20px 16px !important;
            min-height: 145.59px !important;
            margin: 60px 0 0 0 !important;  /* clear 60px fixed mobile nav (nav bottom 60 - header top -16 = 76) */
        }
        .conversation-header-content {
            flex-direction: row !important;
            align-items: flex-start !important;
            text-align: left !important;
            gap: 12px !important;
        }
        .conversation-agy-avatar {
            width: 64px !important;
            height: 64px !important;
            border: 3px solid white !important;
        }
        .conversation-header-text h1 {
            font-size: 20px !important;
        }
        .conversation-header-text p {
            font-size: 13px !important;
            line-height: 1.4 !important;
        }
        /* Stats - 3 across, compact */
        .stats-bar {
            grid-template-columns: repeat(3, 1fr) !important;
            padding: 8px 0 !important;
            margin-bottom: 12px !important;
        }
        .stat {
            padding: 6px 2px !important;
        }
        .stat-number {
            font-size: 20px !important;
            margin-bottom: 4px !important;
        }
        .stat-label {
            font-size: 9px !important;
            letter-spacing: 0 !important;
        }
        /* Section headers */
        .section-header {
            font-size: 16px !important;
            margin-top: 12px !important;
            margin-bottom: 8px !important;
        }
        .subtitle {
            font-size: 12px !important;
            margin-bottom: 12px !important;
        }
        /* Client pills - horizontal scroll */
        .client-pills {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            gap: 6px !important;
            margin-bottom: 16px !important;
            padding-bottom: 4px !important;
        }
        .client-pill {
            flex-shrink: 0 !important;
            padding: 6px 10px !important;
            font-size: 11px !important;
        }
        /* Cards - force compact height */
        .capability-card {
            padding: 14px !important;
            margin-bottom: 10px !important;
            height: auto !important;
            min-height: 0 !important;
        }
        /* Fix Streamlit column equal-height behavior on mobile */
        .stColumn {
            width: 100% !important;
            flex: none !important;
        }
        .stColumn .stVerticalBlock {
            height: auto !important;
        }
        .stHorizontalBlock {
            flex-wrap: wrap !important;
            gap: 0 !important;
        }
        .stHorizontalBlock > .stColumn {
            min-height: 0 !important;
        }
        .card-icon {
            font-size: 22px !important;
            margin-bottom: 6px !important;
        }
        .card-title {
            font-size: 14px !important;
        }
        .card-count {
            font-size: 11px !important;
        }
        .card-desc {
            font-size: 11px !important;
            margin-bottom: 8px !important;
        }
        /* CTA */
        .cta-section {
            padding: 20px 14px !important;
            margin: 16px 0 !important;
        }
        .cta-heading {
            font-size: 18px !important;
        }
        .cta-subtext {
            font-size: 13px !important;
        }
        .card-btn-primary {
            padding: 10px 20px !important;
            font-size: 13px !important;
        }
    }
    /* Client pills (theme-aware) */
    .client-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 40px;
    }
    .client-pill {
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        color: var(--text-primary);
        display: inline-block;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .client-pill:hover {
        border-color: var(--accent-purple);
        color: var(--accent-purple);
        background: var(--accent-purple-bg);
    }
    /* Category cards (theme-aware) - CLICKABLE, NO BUTTON */
    .capability-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
        cursor: pointer;
    }
    .capability-card:hover {
        border-color: var(--accent-purple);
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
        transform: translateY(-3px);
    }
    .card-icon {
        font-size: 28px;
        margin-bottom: 10px;
        display: block;
    }
    .card-title {
        font-size: 17px;
        font-weight: 700;
        color: var(--text-heading);
        margin-bottom: 6px;
        line-height: 1.3;
    }
    .card-count {
        font-size: 13px;
        color: var(--accent-purple);
        font-weight: 700;
        margin-bottom: 8px;
        /* display: inline so the optional .card-clients sibling sits on
           the same line. The old pre-refactor layout had card-count as
           the only meta element so display: block was fine; the new
           tiered layout puts count + client count side by side. */
        display: inline;
    }
    /* Tiered hierarchy (Core / Specialized Capabilities) — added Phase 2
       data-derivation refactor. Specialized cards demoted visually so the
       eye lands on Core first. */
    .tier-header {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-heading);
        margin: 32px 0 16px;
    }
    .capability-card.muted {
        opacity: 0.85;
        padding: 16px;
    }
    .capability-card.muted .card-title {
        font-size: 14px;
    }
    /* Subtitle from CAPABILITY_SUBTITLES — italic muted, mirrors
       ERA_SUBTITLES rendering in timeline_view.py */
    .card-subtitle {
        font-size: 13px;
        font-style: italic;
        color: var(--text-secondary);
        line-height: 1.4;
        margin-bottom: 8px;
    }
    .capability-card.muted .card-subtitle {
        font-size: 12px;
    }
    /* Client count meta — visually subordinate to project count.
       Only rendered when card count > 1 (signal-driven, no "· 1 client"
       repetition where it's trivially derivable). */
    .card-clients {
        font-size: 13px;
        color: var(--text-secondary);
        margin-left: 8px;
        /* Explicit inline (defense — span is inline by default, but
           sibling .card-count was previously display: block which forced
           a line break). */
        display: inline;
    }
    .card-desc {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.5;
        margin-bottom: 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Clients section - using DIV instead of H2 to prevent anchor generation
    st.markdown(
        '<div class="section-header">Clients</div>',
        unsafe_allow_html=True,
    )

    # Generate client pills dynamically from JSONL data
    client_pills = "".join(
        f'<span class="client-pill">{client} ({count})</span>'
        for client, count in named_clients
    )
    clients_html = f'<div class="client-pills">{client_pills}</div>'
    st.markdown(clients_html, unsafe_allow_html=True)

    # Cards are data-derived from real Solution/Offering values that have >=1
    # banking story (after Era exclusion). This kills the May 12, 2026 Card 3
    # regression shape by construction: no hardcoded card can reference a
    # value that doesn't exist in the data, because cards ARE the data.
    # Contract pinned by tests/unit/test_landing_cards.py.
    cards = build_landing_cards(stories, industry="Financial Services / Banking")
    core_cards = [c for c in cards if c["tier"] == "core"]
    specialized_cards = [c for c in cards if c["tier"] == "specialized"]
    # Browseable total = sum of card counts. Differs from total_projects
    # (which includes Era-excluded narrative stories) by the count of narrative
    # banking stories. Used in the subtitle below so the "Browse N" claim
    # matches what's actually reachable via the cards.
    browseable_total = sum(c["count"] for c in cards)

    # Categories section - using DIV instead of H2 to prevent anchor generation
    st.markdown(
        '<div class="section-header">Explore by Capability</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="subtitle">Browse {browseable_total} banking projects organized by specialty area</p>',
        unsafe_allow_html=True,
    )

    def _render_card_grid(card_list: list[dict], key_prefix: str, *, muted: bool):
        """Render one tier's cards in a 3-column grid.

        Each card click sets the same prefilter state the previous hardcoded
        flow did (prefilter_industry, prefilter_capability, return_to_landing).
        The prefilter_capability value is now data-derived (a real Solution/
        Offering string from the corpus), so the Capability dropdown widget
        on My Work can't silently sanitize it to "All" anymore.
        """
        muted_cls = " muted" if muted else ""
        for row_start in range(0, len(card_list), 3):
            cols = st.columns(3)
            for offset in range(3):
                idx = row_start + offset
                if idx >= len(card_list):
                    continue
                card = card_list[idx]
                with cols[offset]:
                    # Meta line — signal-driven: only show client count when
                    # card has >1 project (avoids trivially-redundant "1 client"
                    # repetition that adds no signal).
                    project_plural = "s" if card["count"] != 1 else ""
                    meta = (
                        f'<span class="card-count">{card["count"]} '
                        f"banking project{project_plural}</span>"
                    )
                    if card["count"] > 1:
                        client_plural = "s" if card["clients"] != 1 else ""
                        meta += (
                            f'<span class="card-clients">· {card["clients"]} '
                            f"client{client_plural}</span>"
                        )

                    # Subtitle from CAPABILITY_SUBTITLES, empty-string fallback.
                    # Mirrors ERA_SUBTITLES.get(era, "") in timeline_view.py.
                    subtitle_html = (
                        f'<div class="card-subtitle">{card["subtitle"]}</div>'
                        if card["subtitle"]
                        else ""
                    )

                    # ID is referenced by the JS click-bridge at the bottom of
                    # this function. If the naming changes here, update the JS
                    # template too — the bridge loops over (key_prefix, idx)
                    # pairs to wire clicks.
                    card_id = f"card-banking-{key_prefix}-{idx}"
                    st.markdown(
                        f"""
                    <div class="capability-card{muted_cls}" id="{card_id}" data-title="{card["title"]}">
                        <div class="card-title">{card["title"]}</div>
                        {subtitle_html}
                        <div>{meta}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Hidden Streamlit button — keyed with tier prefix + index
                    # so Core and Specialized cards don't collide. BDD test
                    # targets card_btn_banking_core_0 (the top Core card).
                    if st.button("", key=f"card_btn_banking_{key_prefix}_{idx}"):
                        st.session_state["prefilter_industry"] = (
                            "Financial Services / Banking"
                        )
                        st.session_state["prefilter_capability"] = card["title"]
                        st.session_state["return_to_landing"] = "banking"
                        st.session_state["active_tab"] = "My Work"
                        st.rerun()

    # Core Capabilities tier — cards with >=3 banking stories
    st.markdown(
        '<div class="tier-header">Core Capabilities</div>',
        unsafe_allow_html=True,
    )
    _render_card_grid(core_cards, key_prefix="core", muted=False)

    # Specialized Capabilities tier — cards with <3 banking stories.
    # Single-story specialized capabilities (Security & Compliance, DevOps, etc.)
    # are intentionally surfaced — see feedback_dont_hide_thin_capabilities.md
    # in memory; hiding them creates false-negative signal for hiring managers
    # searching for specific niche capabilities.
    st.markdown(
        '<div class="tier-header">Specialized Capabilities</div>',
        unsafe_allow_html=True,
    )
    _render_card_grid(specialized_cards, key_prefix="spec", muted=True)

    # CTA section with button inside
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="cta-section">
        <h2 class="cta-heading">Can't find what you're looking for?</h2>
        <p class="cta-subtext">Ask Agy 🐾 about Matt's banking experience — get conversational answers tailored to your needs</p>
        <div style="margin-top: 24px;">
            <a id="btn-banking-cta" class="card-btn-primary">Ask Agy 🐾</a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Hidden Streamlit button for CTA
    if st.button("", key="card_btn_banking_cta"):
        st.session_state["active_tab"] = "Ask Agy"
        st.rerun()

    # JS click-bridge for cards + CTA button. Shared with cross_industry_landing
    # via utils/landing_cards.build_card_wiring_js — both landings consume the
    # same source so the wiring contract can't drift independently.
    # Contract pinned by tests/unit/test_banking_landing_js.py.
    components.html(
        build_card_wiring_js("banking", len(core_cards), len(specialized_cards)),
        height=0,
    )

    # === ADD FOOTER ===
    render_footer()
