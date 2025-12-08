"""
Banking Landing Page

47 banking projects organized by capability and client.
"""

import streamlit as st
import streamlit.components.v1 as components

from ui.components.footer import render_footer


def render_banking_landing():
    """Render Banking / Financial Services landing page using Streamlit components

    KNOWN ISSUE: Streamlit preserves scroll position when using st.session_state + st.rerun(),
    causing pages to load at the same vertical position as the previous page. This is a
    Streamlit limitation that cannot be overridden without converting to multipage app.
    """

    # Hero header with Agy avatar (deep blue headphones - authority, trust)
    st.markdown(
        """
<div class="conversation-header">
    <div class="conversation-header-content">
        <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_banking.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
        <div class="conversation-header-text">
            <h1>Matt's Financial Services Expertise</h1>
            <p>47 projects across 16 specialized areas — trust Agy 🐾 to filter decades of domain experience</p>
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
            <div class="stat-number">47</div>
            <div class="stat-label">Projects Delivered</div>
        </div>
        <div class="stat">
            <div class="stat-number">16</div>
            <div class="stat-label">Capability Areas</div>
        </div>
        <div class="stat">
            <div class="stat-number">6</div>
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

    /* Buttons inside capability cards (theme-aware) */
    .card-btn-outline {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-radius: 6px;
        color: var(--accent-purple) !important;
        font-weight: 600;
        font-size: 13px;
        text-decoration: none !important;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .card-btn-outline:hover {
        background: var(--accent-purple);
        border-color: var(--accent-purple);
        color: white !important;
        text-decoration: none !important;
    }

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
    @media (max-width: 768px) {
        .stats-bar {
            grid-template-columns: repeat(2, 1fr);
        }
        .stat:nth-child(2) {
            border-right: none;
        }
    }
    @media (max-width: 480px) {
        .stats-bar {
            grid-template-columns: 1fr;
        }
        .stat {
            border-right: none;
            border-bottom: 1px solid var(--border-color);
        }
        .stat:last-child {
            border-bottom: none;
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
    /* Category cards (theme-aware) */
    .capability-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
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
        margin-bottom: 12px;
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

    clients_html = """
    <div class="client-pills">
        <span class="client-pill">JP Morgan Chase (22)</span>
        <span class="client-pill">RBC (11)</span>
        <span class="client-pill">Fiserv (7)</span>
        <span class="client-pill">American Express (3)</span>
        <span class="client-pill">Capital One (2)</span>
        <span class="client-pill">HSBC (2)</span>
    </div>
    """
    st.markdown(clients_html, unsafe_allow_html=True)

    # Categories section - using DIV instead of H2 to prevent anchor generation
    st.markdown(
        '<div class="section-header">Explore by Capability</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle">Browse 47 banking projects organized by specialty area</p>',
        unsafe_allow_html=True,
    )

    # Banking categories data with varied button text
    banking_categories = [
        (
            "⚡",
            "Agile Transformation & Delivery",
            8,
            "Scaling agile practices, delivery acceleration, team transformation",
            "View Agile Projects →",
        ),
        (
            "💰",
            "Global Payments & Treasury Solutions",
            7,
            "Payment platforms, treasury systems, real-time processing",
            "View Payment Projects →",
        ),
        (
            "🎯",
            "Technology Strategy & Advisory",
            5,
            "Architecture roadmaps, strategic planning, technology vision",
            "View Strategy Work →",
        ),
        (
            "📊",
            "Program Management & Governance",
            4,
            "Large-scale program delivery, governance frameworks, PMO",
            "View Programs →",
        ),
        (
            "🔧",
            "Modern Engineering Practices & Solutions",
            4,
            "DevOps, CI/CD, cloud-native engineering, modern toolchains",
            "View Engineering Work →",
        ),
        (
            "📈",
            "Data & Analytics Solutions",
            3,
            "Data platforms, analytics, business intelligence",
            "View Analytics Projects →",
        ),
        (
            "🤝",
            "Cross-Functional Collaboration & Team Enablement",
            3,
            "Team alignment, collaboration frameworks, culture change",
            "View Team Projects →",
        ),
        (
            "🔄",
            "Business Process Optimization",
            3,
            "Process reengineering, workflow automation, efficiency",
            "View Process Work →",
        ),
        (
            "🔌",
            "Enterprise Integration & API Management",
            2,
            "API platforms, integration architecture, service mesh",
            "View Integration Work →",
        ),
        (
            "📱",
            "Digital Product Development",
            2,
            "Mobile banking, customer experiences, digital channels",
            "View Product Work →",
        ),
        (
            "🔐",
            "Compliance & Risk Solutions",
            2,
            "Regulatory compliance, risk frameworks, audit support",
            "View Compliance Work →",
        ),
        (
            "🚢",
            "DevOps & Continuous Delivery",
            1,
            "Automation, deployment pipelines, continuous integration",
            "View DevOps Projects →",
        ),
        (
            "☁️",
            "Cloud Transformation & Migration",
            1,
            "Cloud strategy, migrations, hybrid cloud architectures",
            "View Cloud Projects →",
        ),
        (
            "🔨",
            "Application Modernization",
            1,
            "Legacy modernization, microservices, platform engineering",
            "View Modernization Work →",
        ),
        (
            "📦",
            "Adoption Enablement & Developer Toolkit",
            1,
            "Developer experience, tooling, productivity platforms",
            "View Enablement Work →",
        ),
    ]

    # Render cards in 3-column grid with varied button text
    for i in range(0, len(banking_categories), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(banking_categories):
                icon, title, count, desc, button_text = banking_categories[i + j]
                with cols[j]:
                    # Singular/plural handling
                    project_text = "project" if count == 1 else "projects"

                    # Generate safe ID for button
                    button_id = f"btn-banking-{i}-{j}"

                    # Card content with HTML button
                    st.markdown(
                        f"""
                    <div class="capability-card">
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{title}</div>
                        <div class="card-count">{count} {project_text}</div>
                        <div class="card-desc">{desc}</div>
                        <div>
                            <a id="{button_id}" class="card-btn-outline">{button_text}</a>
                        </div>
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

    # JavaScript to wire HTML buttons to Streamlit buttons
    components.html(
        """
<script>
(function() {
    function wireButtons() {
        const parentDoc = window.parent.document;

        // Build button map dynamically for all banking cards
        const buttonMap = {
            'btn-banking-cta': 'card_btn_banking_cta'
        };

        // Add all banking card buttons (15 capability cards in 3-column grid)
        for (let i = 0; i < 15; i++) {
            for (let j = 0; j < 3; j++) {
                const idx = i + j;
                if (idx < 15) {
                    buttonMap[`btn-banking-${i}-${j}`] = `card_btn_banking_${i}_${j}`;
                }
            }
        }

        // Wire each HTML button to its Streamlit counterpart
        for (const [htmlId, stKey] of Object.entries(buttonMap)) {
            const htmlBtn = parentDoc.getElementById(htmlId);
            if (htmlBtn && !htmlBtn.dataset.wired) {
                htmlBtn.dataset.wired = 'true';
                htmlBtn.onclick = function() {
                    const stBtn = parentDoc.querySelector('[class*="st-key-' + stKey + '"] button');
                    if (stBtn) stBtn.click();
                };
            }
        }
    }

    // Run multiple times to catch all buttons as they render
    setTimeout(wireButtons, 100);
    setTimeout(wireButtons, 300);
    setTimeout(wireButtons, 600);
    setTimeout(wireButtons, 1000);
})();
</script>
""",
        height=0,
    )

    # === ADD FOOTER ===
    render_footer()
