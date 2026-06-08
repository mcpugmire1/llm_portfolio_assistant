"""
About Matt Page

Professional background, resume, and contact information.
Updated for dark mode compatibility using CSS variables.
"""

import streamlit as st


def render_about_matt():
    """
    Render the About Matt page with professional background and contact info.
    Dark mode compatible using CSS variables.
    """

    # About Matt page CSS lives in ui/styles/global_styles.py (apply_global_styles)
    # so it survives Streamlit position-reconciliation during chip-click transitions
    # (MATTGPT-068). am-* namespace prevents leaking to other pages.
    #
    # Visual language (MATTGPT-093): prof-* classes match wireframe exactly.
    # BDD compat via dual-classing — am-section-title kept on section labels so
    # BDD locators work; prof-section-h !important wins the cascade.

    # =========================================================================
    # 1. HERO SECTION
    # =========================================================================
    st.markdown(
        """
<div class="about-header">
    <div class="about-header-content">
        <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/MattCartoon-Transparent.png"
             width="120" height="120"
             style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2); object-fit: cover; background: rgba(255,255,255,0.1);"
             alt="Matt Pugmire">
        <div class="about-header-text">
            <span class="prof-status-badge">● In active conversations</span>
            <h1>Matt Pugmire</h1>
            <p style="line-height: 1.6; max-width: 800px;">
                Engineering leader · builds organizations from zero · platform modernization · AI · Atlanta · open to relocate
            </p>
        </div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 2. SIGNALS PANEL (replaces stats bar — MATTGPT-093)
    # BDD: .am-signal-tile count inside [class*='st-key-am_signals_panel'].
    # Dual-class tiles: am-signal-tile (BDD) + prof-signal-tile (visual).
    # Inner labels/values use wireframe class names: prof-signal-lbl/prof-signal-val.
    # =========================================================================

    with st.container(key="am_signals_panel"):
        st.markdown('<p class="prof-section-h">Signals</p>', unsafe_allow_html=True)
        st.markdown(
            '<div class="am-signals-grid prof-signals-grid">'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Level</p><p class="prof-signal-val">Senior leader</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Most recent</p><p class="prof-signal-val">Director, Cloud Innovation Center</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Peak team</p><p class="prof-signal-val">150+ practitioners</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Geo</p><p class="prof-signal-val">Atlanta · relocate ok</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Status</p><p class="prof-signal-val">Active search</p></div>'
            '<div class="am-signal-tile prof-signal-tile"><p class="prof-signal-lbl">Work mode</p><p class="prof-signal-val">Hybrid or in-person</p></div>'
            "</div>",
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 3. IN MY OWN WORDS — voice block (MATTGPT-093)
    # BDD: .am-section-title (heading text, page-wide), st-key-am_in_my_own_words (content).
    # Section label is <p> not <h2> — matches wireframe; !important in prof-section-h wins.
    # Prose verbatim from wireframe spec — do not paraphrase.
    # =========================================================================
    with st.container(key="am_in_my_own_words"):
        st.markdown(
            '<p class="am-section-title prof-section-h">In my own words</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="prof-voice-p">I build what\'s next, modernize what\'s not, and grow teams along the way. '
            'Before the Cloud Innovation Center I was the person JPMorgan called to build payments infrastructure '
            'across 12 countries with a 60-engineer team. The CIC was the same work at a different scale, bringing '
            'product culture into the enterprise: 150+ practitioners, 30+ products, $100M+ in repeat business.</p>'
            '<p class="prof-voice-p">Early in my career, we specified everything upfront and found out if it worked at the very end. '
            'I work the opposite way now: prototypes in days, a working MVP in weeks, quality built in from the '
            'first commit rather than tested in afterward, with modern engineering and AI tightening the loop. '
            'That is when a team becomes a system that delivers, and the people on it do work they are proud of.</p>'
            '<p class="prof-voice-p">Career built through networking and referrals, not cold applications. '
            'If you\'ve found me, you\'ve probably been told to.</p>',
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 4. FOR A REFERRER — copy snippet and action buttons (MATTGPT-093)
    # BDD: .am-section-title (heading, page-wide), .am-referrer-snippet (snippet),
    # st-key-am_for_a_referrer (container), buttons by label text inside container.
    # Heading is BEFORE the container so the container IS the info-box (styled via CSS).
    # prof-copy-snippet dual-classes am-referrer-snippet for BDD + white box styling.
    # Snippet verbatim from wireframe spec — do not paraphrase.
    # =========================================================================
    # Inline SVG icons for action buttons (ti-copy / ti-file-download pattern)
    _SVG_COPY = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="8" y="8" width="12" height="12" rx="2"/>'
        '<path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>'
        '</svg>'
    )
    _SVG_DOWNLOAD = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14,2 14,8 20,8"/>'
        '<line x1="12" y1="18" x2="12" y2="12"/>'
        '<polyline points="9,15 12,18 15,15"/>'
        '</svg>'
    )
    _REFERRER_SNIPPET = (
        "Matt Pugmire is a senior product engineering leader with a track record of building at scale across two eras. "
        "He built global payments infrastructure for JPMorgan across 12 countries with a 60-engineer team, then scaled "
        "Accenture’s Cloud Innovation Center from zero to 150+ practitioners, 30+ products, and $100M+ in repeat business. "
        "In active conversations for Head of Engineering and senior leadership roles. "
        "Atlanta-based, open to relocate."
    )
    with st.container(key="am_for_a_referrer"):
        st.markdown(
            '<p class="am-section-title prof-section-h">For a referrer</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="prof-copy-h">Copy this intro language</p>'
            f'<p class="am-referrer-snippet prof-copy-snippet">{_REFERRER_SNIPPET}</p>'
            f'<div class="prof-copy-actions">'
            f'<span class="prof-act-btn">{_SVG_COPY}&nbsp;Copy snippet</span>'
            f'<span class="prof-act-btn">{_SVG_DOWNLOAD}&nbsp;Download PDF</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 5. CORE COMPETENCIES (MATTGPT-093: "Agile at Scale" -> "Product delivery at scale")
    # BDD: .competencies-grid .competency-card h4 (heading text).
    # Dual-class grid + cards; h4 kept for BDD, prof-comp-name class styles it.
    # prof-comp-desc replaces old bullet lists.
    # No subtitle — wireframe has none.
    # =========================================================================
    with st.container(key="am_competencies"):
        st.markdown(
            '<p class="am-section-title prof-section-h">Core Competencies</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="competencies-grid prof-comp-grid">
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Product &amp; Innovation</h4>
        <p class="prof-comp-desc">From discovery and prototypes to enterprise platforms, built around outcomes.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Modern Engineering</h4>
        <p class="prof-comp-desc">Cloud-native and event-driven, with quality engineered in so defects stay out of production.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Product delivery at scale</h4>
        <p class="prof-comp-desc">Scaling product delivery across teams: SAFe, Team Topologies, and the operating model that keeps it fast.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Transformation Leadership</h4>
        <p class="prof-comp-desc">Moving organizations from IT delivery to product operating models, and making the shift stick.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">Team Building</h4>
        <p class="prof-comp-desc">Building cross-functional product teams from zero, and the capability to keep them growing.</p>
    </div>
    <div class="competency-card prof-comp-card">
        <h4 class="prof-comp-name">AI &amp; Emerging Tech</h4>
        <p class="prof-comp-desc">RAG, vector search, and eval-driven development; built hands-on.</p>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 6. HOW I LEAD (MATTGPT-093: "Leadership Philosophy" -> "How I Lead",
    #    4 locked value/claim pairs; no subtitle — wireframe has none)
    # BDD: .am-section-title (heading), .philosophy-grid inner_text (card content).
    # Grid: philosophy-grid (BDD) + prof-philosophy (visual, wireframe class).
    # Cards: prof-phil-card. Content: prof-phil-h + prof-phil-p (<p> tags per wireframe).
    # =========================================================================
    with st.container(key="am_how_i_lead"):
        st.markdown(
            '<p class="am-section-title prof-section-h">How I Lead</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="philosophy-grid prof-philosophy">
    <div class="prof-phil-card">
        <p class="prof-phil-h">Outcomes over output</p>
        <p class="prof-phil-p">I measure a team by what it changes, not how much it produces.</p>
    </div>
    <div class="prof-phil-card">
        <p class="prof-phil-h">Experimentation over certainty</p>
        <p class="prof-phil-p">I trust what a prototype teaches me over what a plan promises.</p>
    </div>
    <div class="prof-phil-card">
        <p class="prof-phil-h">High-trust, sustainable teams</p>
        <p class="prof-phil-p">I build teams where ten people do what twenty usually do, and can still do it next quarter.</p>
    </div>
    <div class="prof-phil-card">
        <p class="prof-phil-h">Grow the people</p>
        <p class="prof-phil-p">I develop people with the same discipline I bring to building systems.</p>
    </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # 7. CAREER TIMELINE (MATTGPT-093)
    # BDD: .timeline .timeline-item (count=7), .timeline .timeline-year (period text),
    # .timeline inner_text (Cendian/Wellfound/Liquid Studio/2023-2026 checks).
    # Dual-class outer (timeline + prof-timeline) and items (timeline-item + prof-timeline-item).
    # Period uses dual-class (timeline-year + prof-timeline-period); rest wireframe only.
    # No subtitle — wireframe has none.
    # Intentional divergence from wireframe: 7 entries vs 4. See CLAUDE.md.
    # =========================================================================
    with st.container(key="am_career_evolution"):
        st.markdown(
            '<p class="am-section-title prof-section-h">Career Evolution</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="timeline prof-timeline">
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2023–2026</p>
        <p class="prof-timeline-role">Sabbatical | Innovation &amp; Upskilling</p>
        <p class="prof-timeline-org">Independent</p>
        <p class="prof-timeline-desc">Sabbatical to recharge, refocus, and reskill — with MattGPT as tangible proof of the work.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2019–2023</p>
        <p class="prof-timeline-role">Director, Cloud Innovation Center</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Launched Innovation Centers (150+ engineers) • 30+ products • $100M+ in repeat business • 4x faster delivery.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2016–2023</p>
        <p class="prof-timeline-role">Capability Development Lead, CloudFirst</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Enterprise capability development, engineering enablement, and culture transformation.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2018–2019</p>
        <p class="prof-timeline-role">Cloud Native Architecture Lead, Liquid Studio</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Cloud-native prototyping and product shaping through rapid experimentation and modern engineering practices.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2009–2017</p>
        <p class="prof-timeline-role">Sr. Technology Architecture Manager, Financial Services</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Financial services platform modernization and architecture at global scale.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2005–2009</p>
        <p class="prof-timeline-role">Technology Manager</p>
        <p class="prof-timeline-org">Accenture</p>
        <p class="prof-timeline-desc">Enterprise integration and solution architecture for large-scale telecom and enterprise platforms.</p>
    </div>
    <div class="timeline-item prof-timeline-item">
        <p class="timeline-year prof-timeline-period">2000–2005</p>
        <p class="prof-timeline-role">Startups &amp; Consulting</p>
        <p class="prof-timeline-org">Cendian Corporation · Wellfound Technology</p>
        <p class="prof-timeline-desc">Building B2B and supply-chain platforms using enterprise integration technologies.</p>
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
