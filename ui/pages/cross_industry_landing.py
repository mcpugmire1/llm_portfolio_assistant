"""
Cross-Industry Transformation Landing Page

53 transformation projects across multiple industries.
"""

import streamlit as st
import streamlit.components.v1 as components

from ui.components.footer import render_footer


def render_cross_industry_landing():
    """Render Cross-Industry Transformation landing page using Streamlit components

    KNOWN ISSUE: Streamlit preserves scroll position when using st.session_state + st.rerun(),
    causing pages to load at the same vertical position as the previous page. This is a
    Streamlit limitation that cannot be overridden without converting to multipage app.
    """

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

    # Hero header with Agy avatar (green headphones - versatility, growth)
    st.markdown(
        """
<div class="conversation-header">
    <div class="conversation-header-content">
        <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_cross_industry.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
        <div class="conversation-header-text">
            <h1>Agy's Cross-Industry Playbook</h1>
            <p>Tracking proven methods across 53 transformation capabilities — ask Agy 🐾 to find what's repeatable</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Stats bar - using same pattern as hero.py
    st.markdown(
        '''
    <div class="stats-bar">
        <div class="stat">
            <div class="stat-number">53</div>
            <div class="stat-label">Projects Delivered</div>
        </div>
        <div class="stat">
            <div class="stat-number">15+</div>
            <div class="stat-label">Capability Areas</div>
        </div>
        <div class="stat">
            <div class="stat-number">6</div>
            <div class="stat-label">Industries</div>
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
            margin: -24px 0 0 0 !important;
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
        /* Client/Industry pills - horizontal scroll */
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
        background: rgba(139, 92, 246, 0.05);
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

    # Industries section - using DIV instead of H2 to prevent anchor generation
    st.markdown(
        '<div class="section-header">Industries Served</div>',
        unsafe_allow_html=True,
    )

    industries_html = """
    <div class="client-pills">
        <span class="client-pill">Banking & Financial Services</span>
        <span class="client-pill">Healthcare & Life Sciences</span>
        <span class="client-pill">Manufacturing</span>
        <span class="client-pill">Retail & Consumer Goods</span>
        <span class="client-pill">Transportation & Logistics</span>
        <span class="client-pill">Telecommunications</span>
        <span class="client-pill">Public Sector</span>
        <span class="client-pill">Technology & Software</span>
    </div>
    """
    st.markdown(industries_html, unsafe_allow_html=True)

    # Categories section - using DIV instead of H2 to prevent anchor generation
    st.markdown(
        '<div class="section-header">Explore by Transformation Capability</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">Browse 53 cross-industry projects organized by transformation approach and methodology</p>',
        unsafe_allow_html=True,
    )

    # Cross-industry categories data (removed button_text - no longer needed)
    cross_industry_categories = [
        (
            "🔧",
            "Modern Engineering Practices & Solutions",
            26,
            "DevOps, CI/CD, test automation, engineering excellence, quality practices",
        ),
        (
            "🤝",
            "Cross-Functional Collaboration & Team Enablement",
            8,
            "Breaking down silos, team alignment, collaboration frameworks, culture change",
        ),
        (
            "🎓",
            "Client Enablement & Sustainable Innovation",
            8,
            "Knowledge transfer, capability building, innovation centers, sustainable practices",
        ),
        (
            "⚡",
            "Agile Transformation & Delivery",
            2,
            "Scaling agile practices, SAFe, Scrum at scale, delivery acceleration across industries",
        ),
        (
            "💡",
            "Product Management & Innovation Labs",
            2,
            "Innovation programs, experimentation, lean startup methodology, product discovery",
        ),
        (
            "🚀",
            "Application Modernization",
            2,
            "Legacy transformation, microservices migration, platform engineering",
        ),
        (
            "🎨",
            "User-Centered Design & Experience",
            1,
            "UX research, design thinking, customer journey mapping, experience design",
        ),
        (
            "🌩️",
            "Platform Optimization & Cloud-Native Development",
            1,
            "Platform engineering, developer experience, internal platforms, service catalogs",
        ),
        (
            "📱",
            "Modern Product Engineering Methodology",
            1,
            "Product thinking, user-centered design, rapid prototyping, product-market fit",
        ),
        (
            "🚢",
            "DevOps & Continuous Delivery",
            1,
            "Deployment automation, pipeline engineering, continuous integration, release management",
        ),
        (
            "🤖",
            "AI & Machine Learning Solutions",
            1,
            "Machine learning platforms, AI strategy, intelligent automation, predictive analytics",
        ),
    ]

    # Render cards in 3-column grid - CLICKABLE CARDS, NO BUTTONS
    for i in range(0, len(cross_industry_categories), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(cross_industry_categories):
                icon, title, count, desc = cross_industry_categories[i + j]
                with cols[j]:
                    # Singular/plural handling
                    project_text = "project" if count == 1 else "projects"

                    # Generate safe ID for card
                    card_id = f"card-cross-industry-{i}-{j}"

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
                    if st.button("", key=f"card_btn_cross_industry_{i}_{j}"):
                        # Set pre-filters for Explore Stories
                        st.session_state["prefilter_industry"] = "Cross Industry"
                        st.session_state["prefilter_capability"] = title
                        st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()

    # CTA section with button inside
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="cta-section">
        <h2 class="cta-heading">Can't find what you're looking for?</h2>
        <p class="cta-subtext">Ask Agy 🐾 about Matt's cross-industry transformation experience — get conversational answers tailored to your needs</p>
        <div style="margin-top: 24px;">
            <a id="btn-cross-industry-cta" class="card-btn-primary">Ask Agy 🐾</a>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Hidden Streamlit button for CTA
    if st.button("", key="card_btn_cross_industry_cta"):
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
        const ctaBtn = parentDoc.getElementById('btn-cross-industry-cta');
        if (ctaBtn && !ctaBtn.dataset.wired) {
            ctaBtn.dataset.wired = 'true';
            ctaBtn.onclick = function() {
                const stBtn = parentDoc.querySelector('[class*="st-key-card_btn_cross_industry_cta"] button');
                if (stBtn) stBtn.click();
            };
        }

        // Wire all capability cards (click anywhere on card)
        for (let i = 0; i < 12; i++) {
            for (let j = 0; j < 3; j++) {
                const cardId = `card-cross-industry-${i}-${j}`;
                const card = parentDoc.getElementById(cardId);
                if (card && !card.dataset.wired) {
                    card.dataset.wired = 'true';
                    card.onclick = function() {
                        const stBtn = parentDoc.querySelector(`[class*="st-key-card_btn_cross_industry_${i}_${j}"] button`);
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
