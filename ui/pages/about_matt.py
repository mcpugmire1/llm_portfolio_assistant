"""
About Matt Page

Professional background, resume, and contact information.
Updated for dark mode compatibility using CSS variables.
"""

import streamlit as st

from ui.components.category_cards import on_chip_click

# Seed prompts for the four clickable sample-question buttons in the
# "See It In Action" card. Exposed as a module-level constant so BDD tests
# (tests/bdd/steps/test_about_matt.py) and any future eval pinning can
# import the exact prompts. Editing this list changes both the rendered
# button labels AND the auto-fired Ask Agy prompts; the two are
# intentionally identical (DOM-observable contract).
ABOUT_MATT_SEED_QUESTIONS = [
    "How did Matt scale engineering teams from 4 to 150+ people?",
    "What were the biggest challenges at the Accenture Innovation Center?",
    "Show me examples of agile transformation with measurable outcomes",
    "How did Matt turn around a failing program?",
]


def render_about_matt():
    """
    Render the About Matt page with professional background and contact info.
    Dark mode compatible using CSS variables.
    """

    # About Matt page CSS now lives in ui/styles/global_styles.py
    # (apply_global_styles): injected on every rerun at a stable position
    # so it survives Streamlit position-reconciliation during chip-click
    # page transitions (MATTGPT-068). App-wide collision-prone selectors
    # (stats-bar / stat-* / section-*) are namespaced .am-* to avoid
    # leaking onto other pages.

    # =========================================================================
    # 1. HERO SECTION
    # =========================================================================
    st.markdown(
        """
<div class="about-header">
    <div class="about-header-content">
        <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/MattCartoon-Transparent.png"
             width="120" height="120"
             style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2); object-fit: cover; background: rgba(255,255,255,0.1);"
             alt="Matt Pugmire">
        <div class="about-header-text">
            <h1 style="margin-bottom: 4px;">Matt Pugmire</h1>
            <p style="font-size: 17px; opacity: 0.9; line-height: 1.6; max-width: 800px;">
                Engineering leader · builds organizations from zero · platform modernization · AI · Atlanta · open to relocate
            </p>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 2. STATS BAR
    # =========================================================================
    st.markdown(
        """
<div class="am-stats-bar">
    <div class="am-stat-card">
        <span class="am-stat-number">20+</span>
        <span class="am-stat-label">Years Experience</span>
    </div>
    <div class="am-stat-card">
        <span class="am-stat-number">130+</span>
        <span class="am-stat-label">Projects Delivered</span>
    </div>
    <div class="am-stat-card">
        <span class="am-stat-number">300+</span>
        <span class="am-stat-label">Professionals Trained</span>
    </div>
    <div class="am-stat-card">
        <span class="am-stat-number">15+</span>
        <span class="am-stat-label">Enterprise Clients</span>
    </div>
    <div class="am-stat-card">
        <span class="am-stat-number">4x</span>
        <span class="am-stat-label">Delivery Acceleration</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 3. CAREER TIMELINE
    # =========================================================================
    st.markdown(
        '<h2 class="am-section-title">Career Evolution</h2>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="am-section-subtitle">From engineer to director—building, modernizing, and leading along the way</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-year">2023–Present</div>
        <div class="timeline-title">Sabbatical | Innovation & Upskilling</div>
        <div class="timeline-company">Independent</div>
        <div class="timeline-desc">Sabbatical to recharge, refocus, and reskill — with MattGPT as tangible proof of the work.</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2019–2023</div>
        <div class="timeline-title">Director, Cloud Innovation Center</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Launched Innovation Centers (150+ engineers) • 30+ products • $300M+ revenue • 4x faster delivery.</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2016–2023</div>
        <div class="timeline-title">Capability Development Lead, CloudFirst</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Enterprise capability development, engineering enablement, and culture transformation.</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2018–2019</div>
        <div class="timeline-title">Cloud Native Architecture Lead, Liquid Studio</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Cloud-native prototyping and product shaping through rapid experimentation and modern engineering practices.</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2009–2017</div>
        <div class="timeline-title">Sr. Technology Architecture Manager, Financial Services</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Financial services platform modernization and architecture at global scale.</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2005–2009</div>
        <div class="timeline-title">Technology Manager</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Enterprise integration and solution architecture for large-scale telecom and enterprise platforms.</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2000–2005</div>
        <div class="timeline-title">Startups & Consulting</div>
        <div class="timeline-company">Including Cendian Corp</div>
        <div class="timeline-desc">Building B2B and supply-chain platforms using enterprise integration technologies.</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 4. MATTGPT DEEP-DIVE (RELOCATED — MATTGPT-102)
    # =========================================================================
    # The "How I Built MattGPT" technical deep-dive (heading + 6 deep-dive
    # cards + design spec link) was relocated to ui/pages/how_i_built.py as
    # a standalone deep-link surface. Reached via ?route=how-i-built[&from=X]
    # — from the Why Agy modal footer, Ask Agy Landing Why Agy section, or
    # Profile signals panel. The "See It In Action" CTA card below stays
    # on My Profile (it's a "try Agy" CTA, not part of the deep-dive content).

    # CTA — See It In Action card (MATTGPT-068, May 27, 2026 wireframe
    # amendment). The four sample-question prompts are rendered as st.button
    # widgets DOM-nested INSIDE the card container. The st.container(key=...)
    # wrapper takes the .cta-card visual styling (via the
    # [class*='st-key-about_matt_cta_card'] CSS selector above) AND scopes
    # the chip buttons as DOM children — true containment, not visual-only
    # siblings. Click handlers go through on_chip_click
    # (ui/components/category_cards.py) which sets seed_prompt +
    # __ask_from_suggestion__ + active_tab="Ask Agy". Prompts come from
    # ABOUT_MATT_SEED_QUESTIONS at module top.
    with st.container(key="about_matt_cta_card"):
        st.markdown(
            """
<h3 style="font-size: 28px; margin: 0 0 16px 0;">See It In Action</h3>
<p style="line-height: 1.7; margin-bottom: 20px;">
    This isn't just a portfolio showcase — <strong>Agy is a working AI assistant</strong> that can
    answer detailed questions about my projects, methodologies, and outcomes.
</p>
            """,
            unsafe_allow_html=True,
        )
        for idx, question in enumerate(ABOUT_MATT_SEED_QUESTIONS):
            st.button(
                question,
                key=f"about_matt_sample_q_{idx}",
                on_click=on_chip_click,
                args=(question,),
                use_container_width=True,
            )

    # =========================================================================
    # 5. CORE COMPETENCIES
    # =========================================================================
    st.markdown(
        '<h2 class="am-section-title">Core Competencies</h2>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="am-section-subtitle">Technical expertise meets organizational transformation</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="competencies-grid">
    <div class="competency-card">
        <div class="competency-card-accent"></div>
        <h4>Product & Innovation</h4>
        <ul>
            <li>→ Lean Product Management</li>
            <li>→ Hypothesis-Driven Development</li>
            <li>→ OKRs & North Star Metrics</li>
            <li>→ Product-Market Fit Validation</li>
            <li>→ Design Thinking & Prototyping</li>
        </ul>
    </div>
    <div class="competency-card">
        <div class="competency-card-accent"></div>
        <h4>Modern Engineering</h4>
        <ul>
            <li>→ Cloud-Native Microservices</li>
            <li>→ Event-Driven Architecture</li>
            <li>→ CI/CD & DevOps Practices</li>
            <li>→ TDD/BDD & Extreme Programming</li>
            <li>→ Platform Engineering</li>
        </ul>
    </div>
    <div class="competency-card">
        <div class="competency-card-accent"></div>
        <h4>Agile at Scale</h4>
        <ul>
            <li>→ SAFe, LeSS, Scrum@Scale</li>
            <li>→ Team Topologies</li>
            <li>→ Organizational Design</li>
            <li>→ Servant Leadership</li>
            <li>→ Continuous Improvement</li>
        </ul>
    </div>
    <div class="competency-card">
        <div class="competency-card-accent"></div>
        <h4>Transformation Leadership</h4>
        <ul>
            <li>→ Change Management</li>
            <li>→ Stakeholder Engagement</li>
            <li>→ Executive Communication</li>
            <li>→ Value Stream Mapping</li>
            <li>→ Business Agility</li>
        </ul>
    </div>
    <div class="competency-card">
        <div class="competency-card-accent"></div>
        <h4>Team Building</h4>
        <ul>
            <li>→ Talent Development & Coaching</li>
            <li>→ Innovation Center Setup</li>
            <li>→ Cross-Functional Collaboration</li>
            <li>→ Performance Management</li>
            <li>→ Culture Transformation</li>
        </ul>
    </div>
    <div class="competency-card">
        <div class="competency-card-accent"></div>
        <h4>AI & Emerging Tech</h4>
        <ul>
            <li>→ GenAI Application Development</li>
            <li>→ Vector Databases & RAG</li>
            <li>→ LLM Integration (GPT-4, Claude)</li>
            <li>→ Semantic Search & NLP</li>
            <li>→ Python & Data Engineering</li>
        </ul>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 6. LEADERSHIP PHILOSOPHY
    # =========================================================================
    st.markdown(
        '<h2 class="am-section-title">Leadership Philosophy</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="am-section-subtitle">How I approach transformation and team development</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="philosophy-grid">
    <div class="philosophy-card">
        <h3>Outcomes Over Output</h3>
        <p>
            I don't measure success by velocity or features shipped. I measure it by business outcomes,
            customer impact, and organizational capability built. Focus on what moves the needle.
        </p>
    </div>
    <div class="philosophy-card">
        <h3>Experimentation Culture</h3>
        <p>
            Innovation requires safe-to-fail environments. I create spaces where teams can test hypotheses,
            learn from failures fast, and iterate toward product-market fit. Data informs decisions.
        </p>
    </div>
    <div class="philosophy-card">
        <h3>Servant Leadership</h3>
        <p>
            My job is to remove blockers, amplify team voices, and create conditions for excellence.
            The best ideas come from the people closest to the work. I ask questions, not give answers.
        </p>
    </div>
    <div class="philosophy-card">
        <h3>Continuous Learning</h3>
        <p>
            Technology evolves fast. Organizations that don't invest in upskilling fall behind. I build
            learning cultures through coaching, mentorship, and hands-on practice. Growth is strategic.
        </p>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # FOOTER (imported from shared component)
    # =========================================================================
    from ui.components.footer import render_footer

    render_footer()
