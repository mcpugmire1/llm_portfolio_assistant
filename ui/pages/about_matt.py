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

    # =========================================================================
    # CSS STYLES - Dark Mode Compatible
    # =========================================================================
    st.markdown(
        """
<style>
/* ============================================================================
   ABOUT MATT PAGE STYLES - Dark Mode Compatible
   ============================================================================ */

/* Header - matches other pages */
.about-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px 40px;
    margin-top: -60px !important;
    margin-bottom: 0 !important;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.about-header-content {
    display: flex;
    align-items: center;
    gap: 24px;
}

.about-header-text h1 {
    font-size: 36px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: white;
}

.about-header-text p {
    font-size: 16px;
    margin: 0;
    opacity: 0.95;
    color: white;
}

/* Stats bar */
.stats-bar {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    margin: 24px 0;
    padding: 0 1rem;
}

@media (max-width: 768px) {
    .stats-bar { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
    background: var(--bg-card, #ffffff);
    padding: 28px 20px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid var(--border-color, #e0e0e0);
    box-shadow: var(--card-shadow, 0 4px 12px rgba(128, 128, 128, 0.1));
}

.stat-number {
    font-size: 36px;
    font-weight: 700;
    color: var(--accent-purple, #8B5CF6);
    display: block;
    margin-bottom: 8px;
}

.stat-label {
    color: var(--text-muted, #999999);
    font-size: 15px;
    display: block;
}

/* Section titles */
.section-title {
    font-size: 32px;
    font-weight: 600;
    text-align: center;
    margin: 60px 0 12px 0;
    color: var(--text-heading, #2c3e50);
}

.section-subtitle {
    font-size: 16px;
    color: var(--text-muted, #7f8c8d);
    text-align: center;
    margin-bottom: 40px;
}

/* Career timeline */
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
    background: var(--bg-primary, white);
    border: 4px solid var(--accent-purple, #8B5CF6);
    border-radius: 50%;
}

.timeline-year {
    font-size: 14px;
    font-weight: 700;
    color: var(--accent-purple, #8B5CF6);
    margin-bottom: 8px;
}

.timeline-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin-bottom: 6px;
}

.timeline-company {
    font-size: 14px;
    color: var(--text-muted, #7f8c8d);
    margin-bottom: 8px;
}

.timeline-desc {
    font-size: 14px;
    color: var(--text-secondary, #888);
    line-height: 1.6;
}

/* Deep-dive section */
.deep-dive-section {
    background: var(--bg-surface, #f8f9fa);
    padding: 50px 20px;
    margin: 40px -1rem 0 -1rem;
}

.deep-dive-card {
    background: var(--bg-card, white);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 24px;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}

.deep-dive-card h3 {
    color: var(--text-heading, #2c3e50);
}

.deep-dive-card p {
    color: var(--text-secondary, #888);
}

.tech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 16px;
}

@media (max-width: 768px) {
    .tech-grid { grid-template-columns: repeat(2, 1fr); }
}

.tech-item {
    background: var(--bg-surface, #f8f9fa);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 16px 12px;
    text-align: center;
    color: var(--text-primary, #333);
    transition: all 0.2s ease;
}

.tech-item:hover {
    border-color: var(--accent-purple, #8B5CF6);
}

.flow-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 32px;
    margin: 24px 0;
    align-items: center;
}

@media (max-width: 768px) {
    .flow-grid { grid-template-columns: repeat(2, 1fr); }
}

.flow-step {
    background: var(--bg-surface, #f8f9fa);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    padding: 16px 12px;
    text-align: center;
    position: relative;
    color: var(--text-primary, #333);
}

.flow-step:not(:last-child)::after {
    content: '→';
    position: absolute;
    right: -24px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
    color: var(--accent-purple, #8B5CF6);
    font-weight: bold;
}

.flow-num {
    width: 28px;
    height: 28px;
    background: var(--accent-purple, #8B5CF6);
    color: white;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 10px;
}

.flow-step-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-heading, #333);
}

.flow-step-desc {
    font-size: 11px;
    color: var(--text-muted, #7f8c8d);
}

/* Code block - works in both modes */
.code-block {
    background: #1e1e2e;
    color: #cdd6f4;
    border-radius: 8px;
    padding: 20px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    line-height: 1.6;
    overflow-x: auto;
    white-space: pre-wrap;
    margin-top: 12px;
}

.code-comment {
    color: #6c7086;
}

.code-keyword {
    color: #cba6f7;
}

.code-string {
    color: #a6e3a1;
}

.code-function {
    color: #89b4fa;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 900px;
    margin: 0 auto;
}

@media (max-width: 768px) {
    .details-grid { grid-template-columns: 1fr; }
}

.detail-card {
    background: var(--bg-card, white);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s ease;
}

.detail-card:hover {
    border-color: var(--accent-purple, #8B5CF6);
}

.detail-card h4 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin: 0 0 16px 0;
}

.detail-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.detail-card li {
    font-size: 13px;
    color: var(--text-secondary, #888);
    line-height: 1.6;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-light, #f0f0f0);
}

.detail-card li:last-child {
    border-bottom: none;
}

.detail-card li strong {
    color: var(--text-primary, #333);
}

.cta-card {
    max-width: 900px;
    margin: 32px auto 0;
    background: var(--bg-card, white);
    border-left: 4px solid var(--accent-purple, #8B5CF6);
    border-radius: 12px;
    padding: 40px;
    box-shadow: var(--card-shadow, 0 4px 12px rgba(0, 0, 0, 0.08));
}

.cta-card h3 {
    color: var(--text-heading, #333);
}

.cta-card p {
    color: var(--text-secondary, #888);
}

.cta-card ul {
    color: var(--text-secondary, #888);
}

.cta-card strong {
    color: var(--text-primary, #333);
}

/* Competencies grid */
.competencies-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    max-width: 1000px;
    margin: 0 auto;
    padding: 0 1rem;
}

@media (max-width: 900px) {
    .competencies-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
    .competencies-grid { grid-template-columns: 1fr; }
}

.competency-card {
    background: var(--bg-card, #fafafa);
    border: 2px solid var(--border-color, #e0e0e0);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s ease;
}

.competency-card:hover {
    border-color: var(--accent-purple, #8B5CF6);
    transform: translateY(-2px);
}

.competency-card h4 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-heading, #2c3e50);
    margin: 12px 0 16px 0;
}

.competency-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.competency-card li {
    font-size: 13px;
    color: var(--text-secondary, #888);
    padding: 6px 0;
}

/* Philosophy grid - gradient cards work in both modes */
.philosophy-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 900px;
    margin: 0 auto;
    padding: 0 1rem;
}

@media (max-width: 768px) {
    .philosophy-grid { grid-template-columns: 1fr; }
}

.philosophy-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 32px;
    transition: all 0.2s ease;
}

.philosophy-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.philosophy-card h3 {
    font-size: 20px;
    margin: 0 0 16px 0;
    color: white;
}

.philosophy-card p {
    font-size: 15px;
    line-height: 1.7;
    opacity: 0.95;
    margin: 0;
    color: white;
}

/* Contact section - gradient works in both modes */
.contact-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 60px 20px;
    margin: 60px -1rem 0 -1rem;
    text-align: center;
}

.contact-section h2 {
    font-size: 32px;
    color: white;
    margin-bottom: 16px;
}

.contact-section p {
    color: rgba(255, 255, 255, 0.9);
}

.contact-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 32px;
}

.contact-btn {
    padding: 14px 28px;
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid white;
    border-radius: 8px;
    color: white;
    text-decoration: none;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.contact-btn:hover {
    background: white;
    color: #8B5CF6;
}

.contact-btn.primary {
    background: white;
    color: #8B5CF6;
}

/* Secret sauce badge */
.secret-sauce-badge {
    display: inline-block;
    background: var(--accent-purple-bg, #e3f2fd);
    color: var(--accent-purple, #1976d2);
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}

/* Dark mode adjustments */
[data-theme="dark"] .secret-sauce-badge {
    background: rgba(139, 92, 246, 0.2);
    color: #a78bfa;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 1. HERO SECTION
    # =========================================================================
    st.markdown(
        """
<div class="about-header">
    <div class="about-header-content">
        <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png"
             width="64" height="64"
             style="width: 120px; height: 120px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);"
             alt="Agy">
        <div class="about-header-text">
            <h1>Matt Pugmire</h1>
            <p style="font-size: 17px; margin-bottom: 12px;">Digital Transformation Leader | Director of Technology Delivery</p>
            <p style="font-size: 14px; opacity: 0.9; line-height: 1.6; max-width: 800px;">
                20+ years driving innovation, agile transformation, and application modernization across Fortune 500 companies.
                Proven track record of accelerating delivery 4x, scaling engineering teams to 150+ people, and building
                high-performing product organizations.
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
<div class="stats-bar">
    <div class="stat-card">
        <span class="stat-number">20+</span>
        <span class="stat-label">Years Experience</span>
    </div>
    <div class="stat-card">
        <span class="stat-number">130+</span>
        <span class="stat-label">Projects Delivered</span>
    </div>
    <div class="stat-card">
        <span class="stat-number">300+</span>
        <span class="stat-label">Professionals Trained</span>
    </div>
    <div class="stat-card">
        <span class="stat-number">15+</span>
        <span class="stat-label">Enterprise Clients</span>
    </div>
    <div class="stat-card">
        <span class="stat-number">4x</span>
        <span class="stat-label">Delivery Acceleration</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 3. CAREER TIMELINE
    # =========================================================================
    st.markdown(
        '<h2 class="section-title">Career Evolution</h2>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-subtitle">From individual contributor to enterprise transformation leader</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-year">2023–Present</div>
        <div class="timeline-title">🧘 Sabbatical | Innovation & Upskilling</div>
        <div class="timeline-company">Independent</div>
        <div class="timeline-desc">Focused on GenAI, cloud-native architecture, and building LLM-powered portfolio assistant (MattGPT)</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2019–2023</div>
        <div class="timeline-title">🚀 Director, Cloud Innovation Center</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Launched Innovation Centers (150+ engineers) • 30+ products • $300M+ revenue • 4x faster delivery</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2016–2023</div>
        <div class="timeline-title">📚 Capability Development Lead, CloudFirst</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Upskilled 300+ professionals • 40% proficiency increase • 50% faster delivery • Culture transformation</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2018–2019</div>
        <div class="timeline-title">☁️ Cloud Native Architecture Lead, Liquid Studio</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Built cloud-native accelerator • AWS enablement (200+ certs) • Rapid prototyping for Fortune 500</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2009–2017</div>
        <div class="timeline-title">💳 Sr. Technology Architecture Manager, Payments</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">$500M+ payments modernization • 12 countries • ACH/FX/Wire hubs • Salesforce integration</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2005–2009</div>
        <div class="timeline-title">🏗️ Technology Manager</div>
        <div class="timeline-company">Accenture</div>
        <div class="timeline-desc">Early leadership in payments, banking, and platform modernization</div>
    </div>
    <div class="timeline-item">
        <div class="timeline-year">2000–2005</div>
        <div class="timeline-title">⚡ Startups & Consulting</div>
        <div class="timeline-company">Including Cendian Corp</div>
        <div class="timeline-desc">Built B2B/supply chain platforms • webMethods & J2EE integration solutions</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 4. MATTGPT DEEP-DIVE
    # =========================================================================
    st.markdown(
        '<h2 class="section-title" style="margin-top: 60px;">How I Built MattGPT</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="section-subtitle">A technical deep-dive into the system architecture behind this portfolio</p>',
        unsafe_allow_html=True,
    )

    # Problem section
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="margin: 0 0 12px 0;">💭 The Problem</h3>
    <p style="line-height: 1.7;">
        Traditional portfolios are static PDFs that don't scale. Recruiters and hiring managers can't easily
        search 130+ projects by methodology, outcome, or domain. I wanted to create an <strong>intelligent,
        conversational interface</strong> that understands intent and surfaces relevant experience.
    </p>
</div>
    """,
        unsafe_allow_html=True,
    )

    # Agy story
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="margin: 0 0 12px 0;">🐾 Why "Agy"?</h3>
    <p style="line-height: 1.7; margin-bottom: 12px;">
        When I started building this AI assistant, there was only one name that made sense: Agy, named in honor
        of my Plott Hound who was my companion through 20+ years of transformation work.
    </p>
    <p style="line-height: 1.7; margin-bottom: 12px;">
        Plott Hounds are bred for determination and tracking skills—they don't give up on a trail. Those same
        traits define how this AI assistant works: determined to find the right insights, skilled at tracking down
        relevant experience across 130+ projects.
    </p>
    <p style="font-style: italic; color: var(--text-muted, #7f8c8d);">
        It felt right to keep his name part of the work we loved doing together.
    </p>
</div>
    """,
        unsafe_allow_html=True,
    )

    # Tech Stack
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="margin: 0 0 16px 0;">🛠️ Tech Stack</h3>
    <div class="tech-grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="tech-item"><div style="font-size: 28px;">🐍</div><div style="font-size: 11px; font-weight: 600;">Python 3.11</div></div>
        <div class="tech-item"><div style="font-size: 28px;">⚡</div><div style="font-size: 11px; font-weight: 600;">Streamlit</div></div>
        <div class="tech-item"><div style="font-size: 28px;">🤖</div><div style="font-size: 11px; font-weight: 600;">OpenAI GPT-4o-mini</div></div>
        <div class="tech-item"><div style="font-size: 28px;">📌</div><div style="font-size: 11px; font-weight: 600;">Pinecone</div></div>
        <div class="tech-item"><div style="font-size: 28px;">🧠</div><div style="font-size: 11px; font-weight: 600;">text-embedding-3-small</div></div>
        <div class="tech-item"><div style="font-size: 28px;">🔀</div><div style="font-size: 11px; font-weight: 600;">GitHub Actions</div></div>
    </div>
</div>
    """,
        unsafe_allow_html=True,
    )

    # Architecture Flow
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="text-align: center; margin: 0 0 24px 0;">🔄 System Architecture Flow</h3>
    <div class="flow-grid">
        <div class="flow-step">
            <div class="flow-num">1</div>
            <div class="flow-step-title">Data Ingestion</div>
            <div class="flow-step-desc">Excel → JSONL with STAR format</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">2</div>
            <div class="flow-step-title">Embeddings</div>
            <div class="flow-step-desc">OpenAI text-embedding-3-small</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">3</div>
            <div class="flow-step-title">Vector Store</div>
            <div class="flow-step-desc">Pinecone with metadata filters</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">4</div>
            <div class="flow-step-title">RAG Pipeline</div>
            <div class="flow-step-desc">Semantic search + GPT-4o-mini</div>
        </div>
    </div>
    <div style="text-align: center; margin: 24px 0 16px 0;">
        <span class="secret-sauce-badge">
            🔬 The Secret Sauce: 3-Stage Quality Pipeline
        </span>
    </div>
<div class="code-block"><span class="code-comment"># 3-Stage Quality Pipeline</span>
<span class="code-comment"># Stage 1: Rules-based nonsense detection</span>
def check_rules_filter(query: str) -&gt; bool:
    <span class="code-string">"Fast rejection of obvious non-portfolio queries"</span>
    blocked_patterns = [<span class="code-string">"weather"</span>, <span class="code-string">"stock price"</span>, <span class="code-string">"recipe"</span>]
    return not any(p in query.lower() for p in blocked_patterns)

<span class="code-comment"># Stage 2: Semantic router intent classification</span>
def classify_intent(query: str) -&gt; dict:
    <span class="code-string">"LLM-based intent detection with confidence scoring"</span>
    return semantic_router.route(query)  <span class="code-comment"># Returns intent + score</span>

<span class="code-comment"># Stage 3: Confidence gating on Pinecone results</span>
def confidence_gate(results: list, threshold: float = 0.25) -&gt; list:
    <span class="code-string">"Only return results above confidence threshold"</span>
    return [r for r in results if r.score &gt;= threshold]

<span class="code-comment"># Client Diversity Algorithm - No repetitive results</span>
def diversify_results(stories: list, max_per_client: int = 2) -&gt; list:
    <span class="code-string">"Ensure variety across different clients/industries"</span>
    seen = {}
    return [s for s in stories
            if seen.setdefault(s[<span class="code-string">'client'</span>], 0) &lt; max_per_client
            and not seen.update({s[<span class="code-string">'client'</span>]: seen[s[<span class="code-string">'client'</span>]] + 1})]

<span class="code-comment"># Behavioral Query Detection for Interview Prep</span>
def detect_behavioral_query(query: str) -&gt; bool:
    <span class="code-string">"Recognize STAR-format interview questions"</span>
    signals = [<span class="code-string">"tell me about a time"</span>, <span class="code-string">"difficult"</span>, <span class="code-string">"challenge"</span>, <span class="code-string">"conflict"</span>]
    return any(signal in query.lower() for signal in signals)</div>
</div>
    """,
        unsafe_allow_html=True,
    )

    # Technical details grid
    st.markdown(
        """
<div class="details-grid">
    <div class="detail-card">
        <h4>📊 Data Pipeline</h4>
        <ul>
            <li>Excel master sheet with 130+ STAR stories</li>
            <li>Python script converts to JSONL with rich metadata</li>
            <li>5P framework: Person, Place, Purpose, Performance, Process</li>
            <li>Automated validation ensures consistency</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>🧠 Embeddings Strategy</h4>
        <ul>
            <li><strong>Model:</strong> OpenAI text-embedding-3-small (1536 dim)</li>
            <li><strong>Chunking:</strong> Full STAR story per vector</li>
            <li><strong>Metadata:</strong> Category, client, themes indexed</li>
            <li><strong>Refresh:</strong> Re-index via CI/CD pipeline</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>🔍 3-Stage Quality Pipeline</h4>
        <ul>
            <li><strong>Stage 1:</strong> Rules-based nonsense detection</li>
            <li><strong>Stage 2:</strong> Semantic router intent classification</li>
            <li><strong>Stage 3:</strong> Confidence gating (threshold: 0.25)</li>
            <li><strong>Diversity:</strong> Max 2 stories per client</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>💬 RAG with GPT-4o-mini</h4>
        <ul>
            <li><strong>System Prompt:</strong> Defines Agy's personality & voice</li>
            <li><strong>Context Injection:</strong> Top 3-5 stories as grounding</li>
            <li><strong>Response Structure:</strong> Answer → Example → Invitation</li>
            <li><strong>Source Citations:</strong> Links to full STAR stories</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>🎨 Frontend (Streamlit)</h4>
        <ul>
            <li>Conversational chat interface with history</li>
            <li>Dark mode support with CSS variables</li>
            <li>Story cards with expandable details</li>
            <li>Responsive design with custom CSS</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>🚀 DevOps & Quality</h4>
        <ul>
            <li><strong>CI/CD:</strong> GitHub Actions → Streamlit Cloud</li>
            <li><strong>Testing:</strong> pytest with behavioral tests</li>
            <li><strong>Monitoring:</strong> Query logging, error tracking</li>
            <li><strong>Security:</strong> API keys in secrets, no PII</li>
        </ul>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # CTA
    st.markdown(
        """
<div class="cta-card">
    <h3 style="font-size: 28px; margin: 0 0 16px 0;">🎯 See It In Action</h3>
    <p style="line-height: 1.7; margin-bottom: 20px;">
        This isn't just a portfolio showcase — <strong>Agy 🐾 is a working AI assistant</strong> that can
        answer detailed questions about my 130+ projects, methodologies, and outcomes.
    </p>
    <p style="font-weight: 600; margin-bottom: 12px;">Try asking questions like:</p>
    <ul style="line-height: 2; margin-bottom: 24px;">
        <li>"How did Matt scale engineering teams from 4 to 150+ people?"</li>
        <li>"What were the biggest challenges at the Accenture Innovation Center?"</li>
        <li>"Show me examples of agile transformation with measurable outcomes"</li>
        <li>"Tell me about a time Matt resolved conflict between senior engineers"</li>
    </ul>
    <p style="text-align: center; font-size: 14px; color: var(--text-muted, #95a5a6);">
        Head to <strong>Ask MattGPT</strong> in the navigation above to try it yourself.<br>
        Real AI assistant • 130+ projects • Instant answers • Available 24/7
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # 5. CORE COMPETENCIES
    # =========================================================================
    st.markdown(
        '<h2 class="section-title">Core Competencies</h2>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-subtitle">Technical expertise meets organizational transformation</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="competencies-grid">
    <div class="competency-card">
        <div style="font-size: 32px;">🚀</div>
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
        <div style="font-size: 32px;">🔧</div>
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
        <div style="font-size: 32px;">⚡</div>
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
        <div style="font-size: 32px;">💡</div>
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
        <div style="font-size: 32px;">👥</div>
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
        <div style="font-size: 32px;">🤖</div>
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
        '<h2 class="section-title">Leadership Philosophy</h2>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="section-subtitle">How I approach transformation and team development</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="philosophy-grid">
    <div class="philosophy-card">
        <h3>🎯 Outcomes Over Output</h3>
        <p>
            I don't measure success by velocity or features shipped. I measure it by business outcomes,
            customer impact, and organizational capability built. Focus on what moves the needle.
        </p>
    </div>
    <div class="philosophy-card">
        <h3>🔬 Experimentation Culture</h3>
        <p>
            Innovation requires safe-to-fail environments. I create spaces where teams can test hypotheses,
            learn from failures fast, and iterate toward product-market fit. Data informs decisions.
        </p>
    </div>
    <div class="philosophy-card">
        <h3>🤝 Servant Leadership</h3>
        <p>
            My job is to remove blockers, amplify team voices, and create conditions for excellence.
            The best ideas come from the people closest to the work. I ask questions, not give answers.
        </p>
    </div>
    <div class="philosophy-card">
        <h3>📈 Continuous Learning</h3>
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
