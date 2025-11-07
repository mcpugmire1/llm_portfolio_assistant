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

    # Stats section - separate st.markdown() to avoid anchor conflicts
    st.markdown('''
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin: 0 0 15px 0; padding: 30px; background: #f8f9fa; border-radius: 10px;">
        <div style="text-align: center;">
            <div style="font-size: 36px; font-weight: 700; color: #764ba2; margin-bottom: 8px;">47</div>
            <div style="font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Projects Delivered</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 36px; font-weight: 700; color: #764ba2; margin-bottom: 8px;">16</div>
            <div style="font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Capability Areas</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 36px; font-weight: 700; color: #764ba2; margin-bottom: 8px;">6</div>
            <div style="font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">Banking Clients</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Inject CSS for this page
    st.markdown("""
    <style>
    /* Conversation header styles for hero section */
    .conversation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0;
        margin: -1rem 0 0 0;
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
        width: 64px !important;
        height: 64px !important;
        border-radius: 50% !important;
        border: 3px solid white !important;
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
        background: white !important;
    }
    .main .block-container {
        max-width: 1400px !important;
        padding: 2rem 1rem !important;
        background: white !important;
    }
    h1 {
        color: #2c3e50 !important;
        font-size: 28px !important;
        margin-bottom: 8px !important;
    }
    .subtitle {
        color: #7f8c8d;
        font-size: 14px;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 30px;
        margin-bottom: 16px;
    }
    /* Client pills */
    .client-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 40px;
    }
    .client-pill {
        background: white;
        border: 1px solid #d0d0d0;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        color: #555;
        display: inline-block;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .client-pill:hover {
        border-color: #8B5CF6;
        color: #8B5CF6;
        background: rgba(139, 92, 246, 0.05);
    }
    /* Category cards */
    .capability-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        height: 100%;
    }
    .capability-card:hover {
        border-color: #7c3aed;
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
        color: #1a202c;
        margin-bottom: 6px;
        line-height: 1.3;
    }
    .card-count {
        font-size: 13px;
        color: #7c3aed;
        font-weight: 700;
        margin-bottom: 8px;
        display: block;
    }
    .card-desc {
        font-size: 13px;
        color: #6b7280;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    /* Category buttons - Premium subtle secondary style */
    [class*="st-key-banking_card"] .stButton > button {
        background: white !important;
        color: #8B5CF6 !important;
        border: 2px solid #e5e5e5 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [class*="st-key-banking_card"] .stButton > button:hover {
        background: #8B5CF6 !important;
        color: white !important;
        border-color: #8B5CF6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    /* CTA "Ask Agy" button - purple like explore stories */
    [class*="st-key-banking_cta"] .stButton > button,
    [class*="st-key-banking_cta"] button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25), 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [class*="st-key-banking_cta"] .stButton > button:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4), 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Clients section - using DIV instead of H2 to prevent anchor generation
    st.markdown('<div class="section-header" style="font-size: 20px; font-weight: 600; color: #2c3e50; margin-top: 30px; margin-bottom: 16px;">Clients</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="section-header" style="font-size: 20px; font-weight: 600; color: #2c3e50; margin-top: 30px; margin-bottom: 16px;">Explore by Capability</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 14px; color: #7f8c8d; margin-bottom: 24px;">Browse 47 banking projects organized by specialty area</p>', unsafe_allow_html=True)

    # Banking categories data with varied button text
    banking_categories = [
        ("⚡", "Agile Transformation & Delivery", 8, "Scaling agile practices, delivery acceleration, team transformation", "View Agile Projects →"),
        ("💰", "Global Payments & Treasury Solutions", 7, "Payment platforms, treasury systems, real-time processing", "View Payment Projects →"),
        ("🎯", "Technology Strategy & Advisory", 5, "Architecture roadmaps, strategic planning, technology vision", "View Strategy Work →"),
        ("📊", "Program Management & Governance", 4, "Large-scale program delivery, governance frameworks, PMO", "View Programs →"),
        ("🔧", "Modern Engineering Practices & Solutions", 4, "DevOps, CI/CD, cloud-native engineering, modern toolchains", "View Engineering Work →"),
        ("📈", "Data & Analytics Solutions", 3, "Data platforms, analytics, business intelligence", "View Analytics Projects →"),
        ("🤝", "Cross-Functional Collaboration & Team Enablement", 3, "Team alignment, collaboration frameworks, culture change", "View Team Projects →"),
        ("🔄", "Business Process Optimization", 3, "Process reengineering, workflow automation, efficiency", "View Process Work →"),
        ("🔌", "Enterprise Integration & API Management", 2, "API platforms, integration architecture, service mesh", "View Integration Work →"),
        ("📱", "Digital Product Development", 2, "Mobile banking, customer experiences, digital channels", "View Product Work →"),
        ("🔐", "Compliance & Risk Solutions", 2, "Regulatory compliance, risk frameworks, audit support", "View Compliance Work →"),
        ("🚢", "DevOps & Continuous Delivery", 1, "Automation, deployment pipelines, continuous integration", "View DevOps Projects →"),
        ("☁️", "Cloud Transformation & Migration", 1, "Cloud strategy, migrations, hybrid cloud architectures", "View Cloud Projects →"),
        ("🔨", "Application Modernization", 1, "Legacy modernization, microservices, platform engineering", "View Modernization Work →"),
        ("📦", "Adoption Enablement & Developer Toolkit", 1, "Developer experience, tooling, productivity platforms", "View Enablement Work →"),
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

                    # Card content
                    st.markdown(f"""
                    <div class="capability-card">
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{title}</div>
                        <div class="card-count">{count} {project_text}</div>
                        <div class="card-desc">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Varied button text matching the category (not full width to match home page)
                    if st.button(button_text, key=f"banking_card_{i}_{j}", use_container_width=False):
                        # Set pre-filters for Explore Stories (Phase 4)
                        st.session_state["prefilter_industry"] = "Financial Services / Banking"
                        st.session_state["prefilter_capability"] = title
                        st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()

    # CTA section
    st.markdown("<br><br>", unsafe_allow_html=True)

    cta_html = """
    <div class="cta-section">
        <h2 class="cta-heading">Need a different way to explore?</h2>
        <p class="cta-subtext">Ask Agy 🐾 about Matt's banking experience — get conversational answers tailored to your needs</p>
    </div>
    <style>
    .cta-section {
        background: #f8f9fa;
        padding: 48px 32px;
        text-align: center;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
        margin: 40px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .cta-heading {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1a202c !important;
        margin-bottom: 16px !important;
    }
    .cta-subtext {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 0px;
        line-height: 1.6;
    }
    </style>
    """
    st.markdown(cta_html, unsafe_allow_html=True)

    # Center the button using columns (narrower center column for better proportions)
    _, col_center, _ = st.columns([1.5, 1, 1.5])
    with col_center:
        if st.button("Ask Agy 🐾", key="banking_cta", type="primary", use_container_width=True):
            st.session_state["active_tab"] = "Ask MattGPT"
            st.rerun()

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)

    footer_html = """
    <div style="background: #334155; color: white; padding: 80px 40px; text-align: center; margin-top: 80px;">
        <h2 style="font-size: 32px; font-weight: 700; margin-bottom: 24px; color: white; line-height: 1.2;">Let's Connect</h2>
        <p style="font-size: 16px; margin-bottom: 16px; color: rgba(255, 255, 255, 0.95); line-height: 1.6; max-width: 850px; margin-left: auto; margin-right: auto;">
            Exploring Director/VP opportunities in <strong>Product Leadership</strong>, <strong>Platform Engineering</strong>, and <strong>Organizational Transformation</strong>
        </p>
        <p style="font-size: 14px; margin-bottom: 40px; color: rgba(255, 255, 255, 0.8); line-height: 1.5;">
            Available for immediate start • Remote or Atlanta-based • Open to consulting engagements
        </p>
        <div style="display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; align-items: center;">
            <a href="mailto:mcpugmire@gmail.com" style="padding: 15px 32px; background: #8b5cf6; color: white; border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                📧 mcpugmire@gmail.com
            </a>
            <a href="https://www.linkedin.com/in/mattpugmire/" target="_blank" style="padding: 15px 32px; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                💼 LinkedIn
            </a>
            <a href="#ask-mattgpt" style="padding: 15px 32px; background: rgba(255,255,255,0.08); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; font-size: 16px; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; transition: all 0.2s ease;">
                🐾 Ask Agy
            </a>
        </div>
    </div>
    <style>
    .landing-footer {
        background: #334155;
        color: white;
        padding: 72px 40px;
        text-align: center;
        margin-top: 80px;
        border-radius: 0;
        margin-left: -1rem;
        margin-right: -1rem;
    }
    .footer-heading {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: white !important;
        margin-bottom: 20px !important;
        margin-top: 0 !important;
        line-height: 1.2 !important;
    }
    .footer-subheading {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.95);
        margin-bottom: 12px;
        line-height: 1.6;
        max-width: 850px;
        margin-left: auto;
        margin-right: auto;
    }
    .footer-subheading strong {
        font-weight: 700;
        color: white;
    }
    .footer-availability {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 40px;
        margin-top: 10px;
        line-height: 1.5;
    }
    .footer-buttons {
        display: flex;
        gap: 18px;
        justify-content: center;
        flex-wrap: wrap;
        align-items: center;
    }
    .footer-btn {
        padding: 15px 32px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        color: white !important;
    }
    .footer-btn svg {
        fill: white !important;
        stroke: white !important;
    }
    .footer-btn-primary {
        background: #8b5cf6;
        color: white !important;
        border: none;
    }
    .footer-btn-primary:hover {
        background: #7c3aed;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
        color: white !important;
    }
    .footer-btn-secondary {
        background: rgba(255, 255, 255, 0.08);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .footer-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        color: white !important;
    }
    @media (max-width: 768px) {
        .footer-buttons {
            flex-direction: column;
            align-items: stretch;
        }
        .footer-btn {
            width: 100%;
            max-width: 320px;
        }
    }
    </style>
    """
    # st.markdown(footer_html, unsafe_allow_html=True)
    # === ADD FOOTER ===
    from ui.components.footer import render_footer
    render_footer()