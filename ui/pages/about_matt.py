"""
About Matt Page

Professional background, resume, and contact information.
"""

import streamlit as st

def render_about_matt():
    """
    Render the About Matt page with professional background and contact info.
    """

    # Global styles already applied via apply_global_styles() in app.py
    # Inject page-specific styles
    st.markdown(
        """
    <style>
    /* Conversation header styles - matches Ask MattGPT pattern */
    .conversation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        margin-top: -50px !important;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }

    .conversation-header-content {
        display: flex;
        align-items: center;
        gap: 24px;
    }

    .conversation-agy-avatar {
        width: 64px !important;
        height: 64px !important;
        border-radius: 50% !important;
        border: 3px solid white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        flex-shrink: 0;
    }

    .conversation-header-text h1 {
        font-size: 32px;
        margin: 0 0 8px 0;
        color: white;
    }

    .conversation-header-text p {
        font-size: 16px;
        margin: 0;
        opacity: 0.95;
    }

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

    /* Career Timeline - matches wireframe exactly */
    .timeline {
        max-width: 900px;
        margin: 0 auto;
        position: relative;
        padding-left: 40px;
    }

    .timeline::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(to bottom, #8B5CF6, #7C3AED);
    }

    .timeline-item {
        position: relative;
        margin-bottom: 30px;
        padding-left: 30px;
    }

    .timeline-item::before {
        content: '';
        position: absolute;
        left: -50px;
        top: 4px;
        width: 20px;
        height: 20px;
        background: white;
        border: 4px solid #8B5CF6;
        border-radius: 50%;
    }

    .timeline-year {
        font-size: 14px;
        font-weight: 700;
        color: #8B5CF6;
        margin-bottom: 8px;
    }

    .timeline-title {
        font-size: 18px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 6px;
    }

    .timeline-company {
        font-size: 14px;
        color: #7f8c8d;
        margin-bottom: 8px;
    }

    .timeline-desc {
        font-size: 14px;
        color: #555;
        line-height: 1.6;
    }

    /* Timeline card styling - no background, matches wireframe */
    .timeline-card {
        background: transparent;
        padding: 0;
        border: none;
        transition: all 0.3s ease;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Purple header with avatar - matches Ask MattGPT pattern
    st.markdown("""
    <div class="conversation-header">
        <div class="conversation-header-content">
            <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png"
                 alt="Agy"
                 class="conversation-agy-avatar">
            <div class="conversation-header-text">
                <h1>Matt Pugmire</h1>
                <p>Digital Transformation Leader | Director of Technology Delivery</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # Stats bar - 5 stats with purple accent
    st.markdown(
    """
    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin: 8px 0 24px 0;">
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #8B5CF6; display: block; margin-bottom: 8px;">20+</span>
            <span style="color: #999999; font-size: 15px; display: block;">Years Experience</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #8B5CF6; display: block; margin-bottom: 8px;">115</span>
            <span style="color: #999999; font-size: 15px; display: block;">Projects Delivered</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #8B5CF6; display: block; margin-bottom: 8px;">300+</span>
            <span style="color: #999999; font-size: 15px; display: block;">Professionals Trained</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #8B5CF6; display: block; margin-bottom: 8px;">15+</span>
            <span style="color: #999999; font-size: 15px; display: block;">Enterprise Clients</span>
        </div>
        <div style="background: var(--secondary-background-color); padding: 28px 20px; border-radius: 12px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 8px 25px rgba(128, 128, 128, 0.2);">
            <span style="font-size: 36px; font-weight: 700; color: #8B5CF6; display: block; margin-bottom: 8px;">3-20x</span>
            <span style="color: #999999; font-size: 14px; line-height: 1.3; display: block;">Delivery Acceleration</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    st.markdown(
        "<h2 class='section-title'>Career Evolution</h2>", unsafe_allow_html=True
    )

    # Timeline - matches wireframe exactly (7 positions)
    timeline_data = [
        {
            "year": "2023–Present",
            "title": "🧘 Sabbatical | Innovation & Upskilling",
            "company": "Independent",
            "desc": "Focused on GenAI, cloud-native architecture, and building LLM-powered portfolio assistant"
        },
        {
            "year": "2019–2023",
            "title": "🚀 Director, Cloud Innovation Center",
            "company": "Accenture",
            "desc": "Launched Innovation Centers (150+ engineers) • 30+ products • $300M+ revenue • 4x faster delivery"
        },
        {
            "year": "2016–2023",
            "title": "📚 Capability Development Lead, CloudFirst",
            "company": "Accenture",
            "desc": "Upskilled 300+ professionals • 40% proficiency increase • 50% faster delivery • Culture transformation"
        },
        {
            "year": "2018–2019",
            "title": "☁️ Cloud Native Architecture Lead, Liquid Studio",
            "company": "Accenture",
            "desc": "Built cloud-native accelerator • AWS enablement (200+ certs) • Rapid prototyping for Fortune 500"
        },
        {
            "year": "2009–2017",
            "title": "💳 Sr. Technology Architecture Manager, Payments",
            "company": "Accenture",
            "desc": "$500M+ payments modernization • 12 countries • ACH/FX/Wire hubs • Salesforce integration"
        },
        {
            "year": "2005–2009",
            "title": "🏗️ Technology Manager",
            "company": "Accenture",
            "desc": "Early leadership in payments, banking, and platform modernization"
        },
        {
            "year": "2000–2005",
            "title": "⚡ Startups & Consulting",
            "company": "Including Cendian Corp",
            "desc": "Built B2B/supply chain platforms • webMethods & J2EE integration solutions"
        }
    ]

    # Render timeline with vertical line
    # Build complete HTML in one call to prevent Streamlit wrapper divs
    timeline_items = []
    for item in timeline_data:
        timeline_items.append(f"""
        <div class="timeline-item">
            <div class="timeline-card">
                <div class="timeline-year">{item["year"]}</div>
                <div class="timeline-title">{item["title"]}</div>
                <div class="timeline-company">{item["company"]}</div>
                <div class="timeline-desc">{item["desc"]}</div>
            </div>
        </div>""")

    timeline_html = '<div class="timeline">' + ''.join(timeline_items) + '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

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