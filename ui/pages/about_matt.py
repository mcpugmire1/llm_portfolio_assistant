"""
About Matt Page

Professional background, resume, and contact information.
"""

import streamlit as st
from typing import List, Dict, Optional

from ui.legacy_components import css_once

def render_about_matt():
    """
    Render the About Matt page with professional background and contact info.
    """
    
    # Page header
    st.title("About Matt")
    
    # First, ensure CSS is loaded
    css_once()  # This should load your existing styles

    # If that doesn't work, inject the specific styles needed
    st.markdown(
        """
    <style>
    .hero-section {
        text-align: center;
            padding: 60px 30px;
            background: var(--background-color);  
            color: var(--text-color);  /* Instead of white */
            border-radius: 16px;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
    }
    
    .stat-card {
        background: #2d2d2d;
        padding: 32px 24px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #3a3a3a;
        transition: transform 0.3s ease;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(128, 128, 128, 0.2);  /* Always visible shadow */
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 16px rgba(74, 144, 226, 0.2);
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: 700;
        color: #4a90e2;
        display: block;
        margin-bottom: 8px;
    }
    
    .stat-label {
        color: #b0b0b0;
        font-size: 16px;
    }
    
    .section-title {
        font-size: 32px;
        font-weight: 600;
        text-align: center;
        margin: 60px 0 40px 0;
        color: #ffffff;
    }
    
    .fixed-height-card {
        background: var(--secondary-background-color);
        padding: 28px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        min-height: 250px;
        box-shadow: 0 4px 12px rgba(0,0,0,.25);
    }

    .fixed-height-card:hover {
        transform: translateY(-4px);
        border-color: var(--border-color);
        box-shadow: 0 8px 25px rgba(74,144,226,.15);

    }
    .card-desc {
        color: #b0b0b0;
        margin-bottom: 8px;
        line-height: 1.5;
        font-size: 14px;
    }
    .skill-bar {
        height: 6px;
        background: var(--border-color);
        border-radius: 3px;
        margin-bottom: 16px;
        position: relative;
    }

    .skill-fill {
        height: 100%;
        background: #4a90e2;
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .philosophy-card {
        background: var(--secondary-background-color);
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid var(--border-color);
        min-height: 180px;
    }

    .philosophy-icon {
        font-size: 48px;
        margin-bottom: 16px;
        box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);  /* Always visible shadow */
        }

    .timeline-marker {
        width: 64px;
        height: 64px;
        background: #4a90e2;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
    .hero-section {
        padding: 20px 30px 16px 30px !important;
        margin-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Force About page content to start at the same position as Home */
    section[data-testid="stAppViewContainer"] {
        padding-top: 1rem !important;
    }

    /* Remove any extra spacing from the main block */
    .main > div.block-container {
        padding-top: 1rem !important;
        max-width: 100%;
    }

    /* Eliminate hero section top spacing */
    .hero-section {
        margin-top: 0 !important;
        padding-top: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)


    st.markdown("""<div class='hero-section' style='margin-top: 0; margin-bottom: 8px; padding: 20px 30px 16px 30px;'>
    <h1 style='font-size: 48px; font-weight: 700; margin-bottom: 16px; margin-top: 0;'>Matt's Journey</h1>
    <p style='font-size: 20px; color: #b0b0b0; max-width: 800px; margin: 0 auto;'>
        Helping Fortune 500 companies modernize legacy systems and launch new cloud-native products — combining modern architecture, product mindset, 
            and innovative engineering practices to deliver scalable digital platforms.</p>
    </div>""", unsafe_allow_html=True)


    # Pure HTML stats that bypass Streamlit's CSS
    st.markdown(
    """
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 8px 0 24px 0;">
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">20+</span>
            <span style="color: #999999; font-size: 15px; display: block;">Years Experience</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">300+</span>
            <span style="color: #999999; font-size: 15px; display: block;">Professionals Upskilled</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">200+</span>
            <span style="color: #999999; font-size: 15px; display: block;">Engineers Certified</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #4a90e2; display: block; margin-bottom: 8px;">2</span>
            <span style="color: #999999; font-size: 14px; line-height: 1.3; display: block;">Innovation Centers Built & Scaled to 150+</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    st.markdown(
        "<h2 class='section-title'>Career Evolution</h2>", unsafe_allow_html=True
    )

    # Timeline using fixed-height-card styling
    timeline_data = [
        (
            "🧘",
            "2023–Present",
            "Sabbatical | Innovation & Upskilling",
            "Focused on GenAI, cloud-native architecture, and building LLM-powered portfolio assistant",
        ),
        (
            "🚀",
            "2019–2023",
            "Director, Cloud Innovation Center @ Accenture",
            "Launched Innovation Centers (150+ engineers) • 30+ products • $300M+ revenue • 4x faster delivery",
        ),
        (
            "📚",
            "2016–2023",
            "Capability Development Lead, CloudFirst @ Accenture",
            "Upskilled 300+ professionals • 40% proficiency increase • 50% faster delivery • Culture transformation",
        ),
        (
            "☁️",
            "2018–2019",
            "Cloud Native Architecture Lead, Liquid Studio @ Accenture",
            "Built cloud-native accelerator • AWS enablement (200+ certs) • Rapid prototyping for Fortune 500",
        ),
        (
            "💳",
            "2009–2017",
            "Sr. Technology Architecture Manager, Payments @ Accenture",
            "$500M+ payments modernization • 12 countries • ACH/FX/Wire hubs • Salesforce integration",
        ),
        (
            "🏗️",
            "2005–2009",
            "Technology Manager @ Accenture",
            "Early leadership in payments, banking, and platform modernization",
        ),
        (
            "⚡",
            "2000–2005",
            "Startups & Consulting (incl. Cendian Corp)",
            "Built B2B/supply chain platforms • webMethods & J2EE integration solutions",
        ),
    ]

    for icon, period, role, desc in timeline_data:
        col1, col2 = st.columns([1, 11])
        with col1:
            # class="timeline-marker
            st.markdown(
                f"<div class='timeline-marker'>{icon}</div>", unsafe_allow_html=True
            )

            # st.markdown(f"<div style='font-size: 40px; text-align: center; margin-top: 20px;'>{icon}</div>",
            # unsafe_allow_html=True)
        with col2:
            st.markdown(
                f"""
            <div class='fixed-height-card' style='margin-bottom: 16px; min-height: auto;'>
                <div style='color: #4a90e2; font-size: 14px; margin-bottom: 8px;'>{period}</div>
                <h3 style='font-size: 20px; font-weight: 600; margin-bottom: 8px;'>{role}</h3>
                <p style='color: #b0b0b0; font-size: 14px;'>{desc}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Core Competencies with skill bars
    st.markdown("<h2 class='section-title' style='margin: 48px 0 32px 0;'>Core Competencies</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class='fixed-height-card'>
            <h3 style='color: var(--text-color); font-size: 20px; margin-bottom: 24px;'>Digital Product & Innovation</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Product Mindset</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Modern Engineering</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 90%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Innovation Strategy</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 85%;'></div></div>
            </div>
            <div>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Digital Transformation</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class='fixed-height-card'>
            <h3 style='color: var(--text-color); font-size: 20px; margin-bottom: 24px;'>Technical Architecture</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Cloud Modernization</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Microservices</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 85%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>DevOps & CI/CD</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 85%;'></div></div>
            </div>
            <div>
                <p style='color: var(--text-color); margin-bottom: 8px;'>API Strategy</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 90%;'></div></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class='fixed-height-card'>
            <h3 style='color: var(--text-color); font-size: 20px; margin-bottom: 24px;'>Industry Expertise</h3>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Financial Services</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 95%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Healthcare & Life Sciences</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 80%;'></div></div>
            </div>
            <div style='margin-bottom: 20px;'>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Enterprise Technology</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 90%;'></div></div>
            </div>
            <div>
                <p style='color: var(--text-color); margin-bottom: 8px;'>Startup Operations</p>
                <div class='skill-bar'><div class='skill-fill' style='width: 75%;'></div></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Leadership Philosophy
    st.markdown("<h2 class='section-title' style='margin: 48px 0 32px 0;'>Leadership Philosophy</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; max-width: 800px; margin: 0 auto 32px auto;'>
        <p style='color: #b0b0b0; font-size: 16px;'>Principles that guide how I approach transformation, team building, and complex challenges</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    philosophy_items = [
        ("🎯", "Outcome-Driven", "Measure success by business impact, not activity"),
        ("🚀", "Iterate Fast", "Small experiments beat big plans"),
        ("👥", "People First", "Technology serves humans, not the other way around"),
        ("🔄", "Learn Continuously", "Every failure is data for the next attempt"),
    ]

    for col, (icon, title, desc) in zip(cols, philosophy_items):
        with col:
            st.markdown(
                f"""
            <div style='text-align: center;'>
                <div class='philosophy-icon'>{icon}</div>
                <h4 style='font-size: 18px; margin-bottom: 8px;'>{title}</h4>
                <p style='font-size: 14px; color: #b0b0b0;'>{desc}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Let's Connect section with better UI/UX
    st.markdown("<h2 class='section-title' style='margin: 48px 0 32px 0;'>Let's Connect</h2>", unsafe_allow_html=True)

    # Professional summary with visual appeal
    st.markdown(
        """
    <div style='text-align: center; max-width: 800px; margin: 0 auto 40px auto;'>
        <p style='font-size: 18px; color: var(--text-color); margin-bottom: 24px;'>
            Open to Director/VP roles in platform modernization and innovation strategy
        </p>
        <div style='display: flex; justify-content: center; gap: 40px; margin-bottom: 32px;box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);'>
            <div style='text-align: center;'>
                <span style='font-size: 24px;'>🏢</span>
                <p style='font-size: 14px; color: #999; margin-top: 8px;'>Office Preferred</p>
            </div>
            <div style='text-align: center;'>
                <span style='font-size: 24px;'>🤝</span>
                <p style='font-size: 14px; color: #999; margin-top: 8px;'>Team Collaboration</p>
            </div>
            <div style='text-align: center;'>
                <span style='font-size: 24px;'>📍</span>
                <p style='font-size: 14px; color: #999; margin-top: 8px;'>Open to Relocation</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Contact cards in a grid
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown(
            """
        <div class='fixed-height-card' style='text-align: center; min-height: 180px; cursor: pointer; transition: all 0.3s;'>
            <span style='font-size: 32px;'>📧</span>
            <h4 style='margin: 16px 0 8px 0; color: var(--text-color);'>Email</h4>
            <p style='color: #4a90e2; font-size: 14px;'>mcpugmire@gmail.com</p>
            <p style='color: #999; font-size: 12px; margin-top: 8px;'>Direct inquiries</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Copy Email", key="copy_email", use_container_width=True):
            st.code("mcpugmire@gmail.com")

    with col2:
        st.markdown(
            """
        <div class='fixed-height-card' style='text-align: center; min-height: 180px; cursor: pointer; transition: all 0.3s;'>
            <span style='font-size: 32px;'>💼</span>
            <h4 style='margin: 16px 0 8px 0; color: var(--text-color);'>LinkedIn</h4>
            <p style='color: #4a90e2; font-size: 14px;'>matt-pugmire</p>
            <p style='color: #999; font-size: 12px; margin-top: 8px;'>Professional network</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Open LinkedIn", key="open_linkedin", use_container_width=True):
            st.markdown(
                "[→ linkedin.com/in/matt-pugmire](https://linkedin.com/in/matt-pugmire/)"
            )

    with col3:
        st.markdown(
            """
        <div class='fixed-height-card' style='text-align: center; min-height: 180px; cursor: pointer; transition: all 0.3s;'>
            <span style='font-size: 32px;'>☕</span>
            <h4 style='margin: 16px 0 8px 0; color: var(--text-color);'>Coffee Chat</h4>
            <p style='color: #4a90e2; font-size: 14px;'>In-person meeting</p>
            <p style='color: #999; font-size: 12px; margin-top: 8px;'>Let's meet face-to-face</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Schedule Coffee", key="coffee_chat", use_container_width=True):
            st.info("Reach out via email or LinkedIn to schedule an in-person meeting")
    
    # === ADD FOOTER ===
    from ui.components.footer import render_footer
    render_footer()