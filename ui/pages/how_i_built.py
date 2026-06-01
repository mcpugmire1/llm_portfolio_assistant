"""
How I Built MattGPT — Deep-link Surface (MATTGPT-102)

Standalone secondary surface relocated from About Matt's "How I Built MattGPT"
section. Not in main nav; reached only via:
  - ?route=how-i-built[&from=<surface-slug>] URL deep-link
  - Why Agy modal footer link (ships in MATTGPT-101)
  - Ask Agy Landing Why Agy section (ships with Ask Agy Landing refresh)
  - Profile signals panel (ships when signals panel is implemented)

Context-aware back link: the ?from=<surface-slug> query param sets
session_state["how_i_built_from"] in app.py's route handler. Defaults to
"profile" if from is missing (sensible fallback for direct deep-links).

CSS for .deep-dive-card / .tech-grid / .flow-grid / .details-grid /
.detail-card / .secret-sauce-badge / .code-block lives in
ui/styles/global_styles.py via apply_global_styles() — survives Streamlit
position-reconciliation per the MATTGPT-068 relocation rationale.
"""

import streamlit as st

# Map of from-param slug → human-readable surface label.
# Used for the context-aware back link. Defaults to "profile" → "My Profile"
# when no from slug is provided (sensible fallback per MATTGPT-102 ticket).
FROM_LABELS = {
    "home": "Home",
    "my-work": "My Work",
    "ask-agy": "Ask Agy",
    "role-match": "Role Match",
    "profile": "My Profile",
    "banking": "Banking",
    "cross-industry": "Cross-Industry",
}


def _resolve_back(from_slug: str | None) -> tuple[str, str]:
    """Resolve (label, slug-for-href). Defaults to ("My Profile", "profile")."""
    if from_slug and from_slug in FROM_LABELS:
        return (FROM_LABELS[from_slug], from_slug)
    return ("My Profile", "profile")


def render_how_i_built():
    """Render the How I Built MattGPT deep-link surface.

    Reads session_state["how_i_built_from"] (set by app.py's ?route= handler
    from the ?from=<surface-slug> query param) to render a context-aware
    back link. The back link is a subtle text anchor (matching the existing
    "← Banking" breadcrumb pattern), not a styled CTA button. href routes
    through app.py's ?nav=<slug> handler which maps the slug to active_tab.
    """
    # Context-aware back link — subtle anchor, not CTA
    from_slug = st.session_state.get("how_i_built_from")
    back_label, back_slug = _resolve_back(from_slug)
    st.markdown(
        f'<a href="?nav={back_slug}" class="back-link">← {back_label}</a>',
        unsafe_allow_html=True,
    )

    # Section heading
    st.markdown(
        '<h2 class="am-section-title" style="margin-top: 24px;">How I Built MattGPT</h2>',
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
        """
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
