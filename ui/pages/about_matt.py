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
            <h1>Matt Pugmire</h1>
            <p style="font-size: 17px; margin-bottom: 12px;">Technology & Transformation Leader | Platform Engineering | Digital Product Development | AI & Cloud</p>
            <p style="font-size: 14px; opacity: 0.9; line-height: 1.6; max-width: 800px;">
                I build new capabilities — products, platforms, and teams — using modern engineering, cloud, and AI.
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
    # 4. MATTGPT DEEP-DIVE
    # =========================================================================
    st.markdown(
        '<h2 class="am-section-title" style="margin-top: 60px;">How I Built MattGPT</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="am-section-subtitle">A technical deep-dive into the system architecture behind this portfolio</p>',
        unsafe_allow_html=True,
    )

    # Problem section
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="margin: 0 0 12px 0;">The Problem</h3>
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
<div class="deep-dive-card" style="display: flex; gap: 24px; align-items: center;">
    <div style="flex: 1;">
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
        <p style="font-style: italic; color: var(--text-secondary, #6B7280);">
            It felt right to keep his name part of the work we loved doing together.
        </p>
    </div>
    <img src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/AgyMattCartoon-Transparent.png"
         style="width: 160px; height: auto; flex-shrink: 0; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));"
         alt="Matt and Agy">
</div>
    """,
        unsafe_allow_html=True,
    )

    # Tech Stack
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="margin: 0 0 16px 0;">Tech Stack</h3>
    <div class="tech-grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="tech-item"><div style="font-size: 28px;">🐍</div><div style="font-size: 11px; font-weight: 600;">Python 3.11</div></div>
        <div class="tech-item"><div style="font-size: 28px;">⚡</div><div style="font-size: 11px; font-weight: 600;">Streamlit</div></div>
        <div class="tech-item"><div style="font-size: 28px;">🤖</div><div style="font-size: 11px; font-weight: 600;">OpenAI GPT-4o</div></div>
        <div class="tech-item"><div style="font-size: 28px;">📌</div><div style="font-size: 11px; font-weight: 600;">Pinecone</div></div>
        <div class="tech-item"><div style="font-size: 28px;">🧠</div><div style="font-size: 11px; font-weight: 600;">text-embedding-3-small</div></div>
        <div class="tech-item"><div style="font-size: 28px;">🔀</div><div style="font-size: 11px; font-weight: 600;">GitHub Webhook</div></div>
    </div>
</div>
    """,
        unsafe_allow_html=True,
    )

    # Architecture Flow
    st.markdown(
        """
<div class="deep-dive-card">
    <h3 style="text-align: center; margin: 0 0 24px 0;">System Architecture Flow</h3>
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
            <div class="flow-step-title">Intent & Entity</div>
            <div class="flow-step-desc">Query classification + entity pinning</div>
        </div>
        <div class="flow-step">
            <div class="flow-num">5</div>
            <div class="flow-step-title">RAG + GPT-4o</div>
            <div class="flow-step-desc">XML-isolated context → generation</div>
        </div>
    </div>
    <div style="text-align: center; margin: 24px 0 16px 0;">
        <span class="secret-sauce-badge">
            The Secret Sauce: 5-Stage RAG Pipeline with Context Isolation
        </span>
    </div>
<details>
<summary>Show code</summary>
<div class="code-block"><span class="code-comment"># 5-Stage RAG Pipeline</span>
<span class="code-comment"># Stage 1: Nonsense filter (regex)</span>
def is_nonsense(query: str) -&gt; bool:
    <span class="code-string">"Fast regex rejection of clearly off-topic queries"</span>
    return matches_blocked_patterns(query)

<span class="code-comment"># Stage 2: Semantic router (embedding-based, no LLM call)</span>
def route(query: str) -&gt; tuple[str, float]:
    <span class="code-string">"Embedding similarity → intent family + score; flags out_of_scope"</span>
    return router.classify(query)  <span class="code-comment"># → (intent_family, score)</span>

<span class="code-comment"># Stage 3: Pinecone retrieval with entity-aware pinning</span>
def retrieve(query: str) -&gt; list:
    <span class="code-string">"Vector search; pin a known-entity story to #1 when detected"</span>
    results = pinecone.search(embed(query))
    entity = detect_entity(query)  <span class="code-comment"># NER on known clients/divisions</span>
    if entity:
        results = pin_to_top(results, entity)
    return results

<span class="code-comment"># Stage 4: Confidence gating</span>
def confidence_gate(results: list) -&gt; list:
    <span class="code-string">"Drop low-similarity hits below the semantic confidence floor"</span>
    return [r for r in results if r.pc_score &gt;= CONFIDENCE_HIGH]

<span class="code-comment"># Stage 5: LLM generation with XML context isolation</span>
def generate(stories: list, intent_family: str) -&gt; str:
    <span class="code-string">"GPT-4o reads &lt;primary_story&gt;/&lt;supporting_story&gt; tagged context"</span>
    ctx = build_xml_context(stories)
    return gpt_4o.complete(SYSTEM_PROMPT + ctx)</div>
</details>
</div>
    """,
        unsafe_allow_html=True,
    )

    # Technical details grid
    st.markdown(
        """
<div class="details-grid">
    <div class="detail-card">
        <h4>Data Pipeline</h4>
        <ul>
            <li>Excel master sheet with 130+ STAR stories</li>
            <li>Python script converts to JSONL with rich metadata</li>
            <li>5P framework: Person, Place, Purpose, Performance, Process</li>
            <li>Automated validation ensures consistency</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>Embeddings Strategy</h4>
        <ul>
            <li><strong>Model:</strong> OpenAI text-embedding-3-small (1536 dim)</li>
            <li><strong>Chunking:</strong> Full STAR story per vector</li>
            <li><strong>Metadata:</strong> Category, client, themes indexed</li>
            <li><strong>Refresh:</strong> Re-index via data ingestion pipeline (Excel → JSONL → enrich → embed → Pinecone)</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>5-Stage RAG Pipeline</h4>
        <ul>
            <li><strong>Stage 1:</strong> Nonsense filter (fast regex rejection)</li>
            <li><strong>Stage 2:</strong> Semantic router (intent + out-of-scope detection)</li>
            <li><strong>Stage 3:</strong> Pinecone retrieval with entity-aware pinning</li>
            <li><strong>Stage 4:</strong> Confidence gating (threshold: 0.25)</li>
            <li><strong>Stage 5:</strong> LLM generation (GPT-4o with XML context isolation)</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>CI/CD Pipeline</h4>
        <ul>
            <li><strong>Trigger:</strong> Git push to main</li>
            <li><strong>Mechanism:</strong> GitHub webhook → Streamlit Cloud</li>
            <li><strong>Action:</strong> Auto-rebuild and deploy</li>
            <li><strong>Testing:</strong> pytest with behavioral tests</li>
            <li><strong>Monitoring:</strong> Query logging, error tracking</li>
            <li><strong>Security:</strong> API keys in secrets, no PII</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>RAG with GPT-4o</h4>
        <ul>
            <li><strong>Context Isolation:</strong> XML tags prevent cross-story bleed</li>
            <li><strong>Texture Preservation:</strong> Quotes distinctive phrases verbatim</li>
            <li><strong>Synthesis Mode:</strong> Multi-theme responses for broad queries</li>
            <li><strong>Source Citations:</strong> Links to full STAR stories</li>
        </ul>
    </div>
    <div class="detail-card">
        <h4>Frontend (Streamlit)</h4>
        <ul>
            <li>Conversational chat interface with history</li>
            <li>Dark mode support with CSS variables</li>
            <li>Story cards with expandable details</li>
            <li>Responsive design with custom CSS</li>
        </ul>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Design Spec Link
    st.markdown(
        """I
<div class="deep-dive-card" style="margin-top: 2rem; margin-bottom: 2rem;">
    <p style="margin: 0; font-size: 1rem; line-height: 1.6; text-align: center;">
        I documented the entire product development process — from strategy through architecture to implementation.
        <a href="https://mcpugmire1.github.io/mattgpt-design-spec/"
           target="_blank"
           rel="noopener noreferrer"
           style="color: #8B5CF6; text-decoration: none; font-weight: 600; margin-left: 0.25rem; white-space: nowrap;">
            View Design Specification →
        </a>
    </p>
</div>

        """,
        unsafe_allow_html=True,
    )

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
