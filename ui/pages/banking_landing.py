"""
Banking Landing Page

Banking projects organized by capability and client.
Counts are derived dynamically from JSONL data.
"""

from collections import Counter

import streamlit as st
import streamlit.components.v1 as components

from ui.components.footer import render_footer

# Clients to exclude from pills (too generic)
_EXCLUDED_CLIENTS = {
    "Multiple Clients",
    "Multiple Financial Services Clients",
    "Financial Services Client",
    "Various",
    "Independent",
    "Career Narrative",
    "N/A",
    "",
    None,
}


def render_banking_landing(stories: list[dict]):
    """Render Banking / Financial Services landing page using Streamlit components

    Args:
        stories: Full story corpus from JSONL.

    KNOWN ISSUE: Streamlit preserves scroll position when using st.session_state + st.rerun(),
    causing pages to load at the same vertical position as the previous page. This is a
    Streamlit limitation that cannot be overridden without converting to multipage app.
    """
    # === DYNAMIC COUNTS (derived from JSONL) ===
    banking_stories = [
        s for s in stories if s.get("Industry") == "Financial Services / Banking"
    ]
    total_projects = len(banking_stories)

    # Client counts (excluding generic clients)
    client_counter = Counter(
        s.get("Client", "Unknown")
        for s in banking_stories
        if s.get("Client") not in _EXCLUDED_CLIENTS
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

    # Hero header with Agy avatar (deep blue headphones - authority, trust)
    st.markdown(
        f"""
<div class="conversation-header">
    <div class="conversation-header-content">
        <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_banking.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
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
        margin: -3rem 0 0 0;
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
            min-height: auto !important;
            margin: -24px 0 0 0 !important;  /* top right bottom left */
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
        display: block;
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

    # Categories section - using DIV instead of H2 to prevent anchor generation
    st.markdown(
        '<div class="section-header">Explore by Capability</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="subtitle">Browse {total_projects} banking projects organized by specialty area</p>',
        unsafe_allow_html=True,
    )

    # Dynamic counts: Solution / Offering occurrences in banking stories
    capability_counts = Counter(
        s.get("Solution / Offering", "")
        for s in banking_stories
        if s.get("Solution / Offering")
    )

    # Banking capability cards (icon, title, description)
    # Count for each card is looked up dynamically from capability_counts
    banking_categories = [
        (
            "⚡",
            "Agile Transformation & Delivery",
            "Scaling agile practices, delivery acceleration, team transformation",
        ),
        (
            "💰",
            "Global Payments & Treasury Solutions",
            "Payment platforms, treasury systems, real-time processing",
        ),
        (
            "🎯",
            "Technology Strategy & Advisory",
            "Architecture roadmaps, strategic planning, technology vision",
        ),
        (
            "📊",
            "Program Management & Governance",
            "Large-scale program delivery, governance frameworks, PMO",
        ),
        (
            "🔧",
            "Modern Engineering Practices & Solutions",
            "DevOps, CI/CD, cloud-native engineering, modern toolchains",
        ),
        (
            "📈",
            "Data & Analytics Solutions",
            "Data platforms, analytics, business intelligence",
        ),
        (
            "🤝",
            "Cross-Functional Collaboration & Team Enablement",
            "Team alignment, collaboration frameworks, culture change",
        ),
        (
            "🔄",
            "Business Process Optimization",
            "Process reengineering, workflow automation, efficiency",
        ),
        (
            "🔌",
            "Enterprise Integration & API Management",
            "API platforms, integration architecture, service mesh",
        ),
        (
            "📱",
            "Digital Product Development",
            "Mobile banking, customer experiences, digital channels",
        ),
        (
            "🔐",
            "Compliance & Risk Solutions",
            "Regulatory compliance, risk frameworks, audit support",
        ),
        (
            "🚢",
            "DevOps & Continuous Delivery",
            "Automation, deployment pipelines, continuous integration",
        ),
        (
            "☁️",
            "Cloud Transformation & Migration",
            "Cloud strategy, migrations, hybrid cloud architectures",
        ),
        (
            "🔨",
            "Application Modernization",
            "Legacy modernization, microservices, platform engineering",
        ),
        (
            "📦",
            "Adoption Enablement & Developer Toolkit",
            "Developer experience, tooling, productivity platforms",
        ),
    ]

    # Render cards in 3-column grid - CLICKABLE CARDS, NO BUTTONS
    for i in range(0, len(banking_categories), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(banking_categories):
                icon, title, desc = banking_categories[i + j]
                count = capability_counts.get(title, 0)
                with cols[j]:
                    # Singular/plural handling
                    project_text = "project" if count == 1 else "projects"

                    # Generate safe ID for card
                    card_id = f"card-banking-{i}-{j}"

                    # Card content - NO BUTTON, whole card is clickable
                    st.markdown(
                        f"""
                    <div class="capability-card" id="{card_id}" data-title="{title}">
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{title}</div>
                        <div class="card-count">{count} {project_text}</div>
                        <div class="card-desc">{desc}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Hidden Streamlit button (triggers the action)
                    if st.button("", key=f"card_btn_banking_{i}_{j}"):
                        # Set pre-filters for Explore Stories
                        st.session_state["prefilter_industry"] = (
                            "Financial Services / Banking"
                        )
                        st.session_state["prefilter_capability"] = title
                        st.session_state["return_to_landing"] = "banking"
                        st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()

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
        st.session_state["active_tab"] = "Ask MattGPT"
        st.rerun()

    # JavaScript to wire clickable cards and CTA button to Streamlit buttons
    components.html(
        """
<script>
(function() {
    function wireCards() {
        const parentDoc = window.parent.document;

        // Wire CTA button
        const ctaBtn = parentDoc.getElementById('btn-banking-cta');
        if (ctaBtn && !ctaBtn.dataset.wired) {
            ctaBtn.dataset.wired = 'true';
            ctaBtn.onclick = function() {
                const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_banking_cta"] button');
                if (stBtn) stBtn.click();
            };
        }

        // Wire all capability cards (click anywhere on card)
        for (let i = 0; i < 15; i++) {
            for (let j = 0; j < 3; j++) {
                const cardId = `card-banking-${i}-${j}`;
                const card = parentDoc.getElementById(cardId);
                if (card && !card.dataset.wired) {
                    card.dataset.wired = 'true';
                    card.onclick = function() {
                        const stBtn = parentDoc.querySelector(`[class*="st-key-card_btn_banking_${i}_${j}"] button`);
                        if (stBtn) stBtn.click();
                    };
                }
            }
        }
    }

    // Run multiple times to catch all cards as they render
    setTimeout(wireCards, 100);
    setTimeout(wireCards, 300);
    setTimeout(wireCards, 600);
    setTimeout(wireCards, 1000);
})();
</script>
""",
        height=0,
    )

    # === ADD FOOTER ===
    render_footer()
