"""
How I Built MattGPT — @st.dialog wrapper (MATTGPT-102).

Reuses existing CSS classes from global_styles.py (deep-dive-card, tech-grid,
tech-item, flow-grid, flow-step, pipeline-wrapper, pipeline-step, details-grid,
detail-card) — same classes used by how_i_built.py standalone page. No new CSS.

Triggered sequentially from Why Agy and How Agy Searches footer buttons
via active_dialog = "how_i_built".
"""

import streamlit as st
import streamlit.components.v1 as components


@st.dialog("How I Built MattGPT", width="large")
def render_how_i_built_dialog():
    """How I Built MattGPT as @st.dialog — wireframe content, existing CSS classes."""

    components.html(
        """
<script>
(function() {
    function reset() {
        var pd = window.parent.document;
        if (pd.activeElement && pd.activeElement !== pd.body) pd.activeElement.blur();
        var container = pd.querySelector('[data-testid="stDialog"]');
        if (container) container.scrollTop = 0;
    }
    setTimeout(reset, 200);
    setTimeout(reset, 600);
})();
</script>""",
        height=0,
    )

    st.markdown(
        '<p style="font-size:13px;color:var(--text-secondary);margin:0 0 20px;">A technical deep-dive into the system architecture behind this portfolio.</p>',
        unsafe_allow_html=True,
    )

    # 1. The Problem
    st.markdown(
        """<div class="deep-dive-card">
    <h3 style="margin:0 0 12px;">The Problem</h3>
    <p style="line-height:1.7;">Traditional portfolios are static PDFs that don't scale. Recruiters and hiring managers can't easily search 100+ projects by methodology, outcome, or domain. I wanted to create an <strong>intelligent, conversational interface</strong> that understands intent and surfaces relevant experience.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # 2. Tech Stack
    st.markdown(
        """<div class="deep-dive-card">
    <h3 style="margin:0 0 16px;">Tech Stack</h3>
    <div class="tech-grid" style="grid-template-columns:repeat(3,1fr);">
        <div class="tech-item"><div style="font-size:28px;">🐍</div><div style="font-size:11px;font-weight:600;">Python 3.11</div></div>
        <div class="tech-item"><div style="font-size:28px;">⚡</div><div style="font-size:11px;font-weight:600;">Streamlit</div></div>
        <div class="tech-item"><div style="font-size:28px;">⊙</div><div style="font-size:11px;font-weight:600;">OpenAI GPT-4o</div></div>
        <div class="tech-item"><div style="font-size:28px;">📌</div><div style="font-size:11px;font-weight:600;">Pinecone</div></div>
        <div class="tech-item"><div style="font-size:28px;">🧠</div><div style="font-size:11px;font-weight:600;">text-embedding-3-small</div></div>
        <div class="tech-item"><div style="font-size:28px;">🔀</div><div style="font-size:11px;font-weight:600;">GitHub Webhook</div></div>
    </div>
</div>""",
        unsafe_allow_html=True,
    )

    # 3. System Architecture Flow
    st.markdown(
        """<div class="deep-dive-card">
    <h3 style="text-align:center;margin:0 0 24px;">System Architecture Flow</h3>
    <p style="font-size:12px;color:var(--text-secondary);margin:0 0 16px;">How data moves through the system, from raw Excel stories to a deployed RAG pipeline.</p>
    <div class="flow-grid">
        <div class="flow-step"><div class="flow-num">1</div><div class="flow-step-title">Data Ingestion</div><div class="flow-step-desc">Excel → JSONL with STAR format</div></div>
        <div class="flow-step"><div class="flow-num">2</div><div class="flow-step-title">Embeddings</div><div class="flow-step-desc">OpenAI text-embedding-3-small</div></div>
        <div class="flow-step"><div class="flow-num">3</div><div class="flow-step-title">Vector Store</div><div class="flow-step-desc">Pinecone with metadata filters</div></div>
        <div class="flow-step"><div class="flow-num">4</div><div class="flow-step-title">Intent &amp; Entity</div><div class="flow-step-desc">Query classification + entity pinning</div></div>
        <div class="flow-step"><div class="flow-num">5</div><div class="flow-step-title">RAG + GPT-4o</div><div class="flow-step-desc">XML-isolated context → generation</div></div>
    </div>
</div>""",
        unsafe_allow_html=True,
    )

    # 4. Per-query Runtime Pipeline
    st.markdown(
        """<div class="deep-dive-card">
    <p style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-secondary);margin:0 0 4px;">Per-query runtime pipeline</p>
    <p style="font-size:12px;color:var(--text-secondary);margin:0 0 14px;">What happens on every query, from the moment a user types to the moment Agy responds.</p>
    <div class="hib-runtime-wrapper">
        <div class="hib-runtime-step"><div class="hib-runtime-num">1</div><div class="hib-runtime-card"><h4>Filters irrelevant/noisy input</h4><ul><li>Regex-based nonsense rejection, sub-millisecond</li><li>Catches homework asks, gibberish, off-domain queries</li><li>No LLM cost for rejected queries</li></ul></div></div>
        <div class="hib-runtime-step"><div class="hib-runtime-num">2</div><div class="hib-runtime-card"><h4>Detects interview intent</h4><ul><li>Semantic router classifies into 15 intent families</li><li>Background, behavioral, technical, leadership, synthesis</li><li>Detects out-of-scope and personal queries before retrieval</li></ul></div></div>
        <div class="hib-runtime-step"><div class="hib-runtime-num">3</div><div class="hib-runtime-card"><h4>Retrieves grounded experience stories</h4><ul><li>Pinecone top-K vector search</li><li>text-embedding-3-small, 1536 dimensions</li><li>Entity-aware pinning for known clients, employers, divisions</li></ul></div></div>
        <div class="hib-runtime-step"><div class="hib-runtime-num">4</div><div class="hib-runtime-card"><h4>Refuses weak matches / avoids fabrication</h4><ul><li>Confidence gate inspects top match similarity</li><li>Below threshold, returns a "no strong matches" response</li><li>Prevents low-quality fabrication</li></ul></div></div>
        <div class="hib-runtime-step"><div class="hib-runtime-num">5</div><div class="hib-runtime-card"><h4>Synthesizes a tailored interview response</h4><ul><li>GPT-4o grounded synthesis</li><li>primary_story + supporting_story XML tags prevent cross-story bleed</li><li>STAR format, distinctive phrases preserved verbatim</li></ul></div></div>
    </div>
</div>""",
        unsafe_allow_html=True,
    )

    # 5–7. Detail grid (Data Pipeline, Embeddings, CI/CD, RAG, Frontend)
    st.markdown(
        """<div class="details-grid">
    <div class="detail-card">
        <h4>Data Pipeline</h4>
        <ul>
            <li>Excel master sheet with 100+ STAR stories</li>
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
            <li><strong>Refresh:</strong> Excel → JSONL → enrich → embed → Pinecone</li>
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
    <div class="detail-card" style="grid-column:span 2;">
        <h4>Frontend (Streamlit)</h4>
        <ul style="display:grid;grid-template-columns:1fr 1fr;gap:5px;">
            <li>Conversational chat interface with history</li>
            <li>Dark mode support with CSS variables</li>
            <li>Story cards with expandable details</li>
            <li>Responsive design with custom CSS</li>
        </ul>
    </div>
</div>""",
        unsafe_allow_html=True,
    )

    # 8. Go-deeper footer — wireframe hib-block / hib-godeeper-* classes, inline SVG icons (MATTGPT-102)
    _SVG_GITHUB = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/></svg>'
    _SVG_FILE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/></svg>'
    _SVG_EXT = '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15,3 21,3 21,9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>'
    _SVG_ARR = '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12,5 19,12 12,19"/></svg>'
    st.markdown(
        '<div class="hib-block">'
        f'<p class="hib-cta-h">Go Deeper</p>'
        f'<p class="hib-godeeper-lead"></p><div class="hib-godeeper-grid">'
        f'<div class="hib-godeeper-card"><div class="hib-godeeper-top">{_SVG_GITHUB}<span class="hib-godeeper-ttl">View the source</span></div><p class="hib-godeeper-desc">The full codebase behind everything above: the RAG pipeline, data ingestion, and behavioral tests.</p><a href="https://github.com/mcpugmire1/llm_portfolio_assistant" target="_blank" class="hib-godeeper-link">View on GitHub {_SVG_EXT}</a></div>'
        f'<div class="hib-godeeper-card"><div class="hib-godeeper-top">{_SVG_FILE}<span class="hib-godeeper-ttl">Read the design spec</span></div><p class="hib-godeeper-desc">The end-to-end product process: strategy, architecture, and design decisions, documented in full.</p><a href="https://mcpugmire1.github.io/mattgpt-design-spec/" target="_blank" class="hib-godeeper-link">View the full specification {_SVG_ARR}</a></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # 9. See It In Action — hib-cta-block HTML chips + delegated parentDoc listener.
    # st.button + scoped CSS can't achieve wireframe's 11px chip height: Streamlit
    # Emotion-cache min-height beats !important. HTML spans + JS bridge instead.
    _PROMPTS = [
        "How did Matt scale engineering teams from 4 to 150+ people?",
        "What were the biggest challenges at the Accenture Innovation Center?",
        "Show me examples of agile transformation with measurable outcomes",
        "How did Matt turn around a failing program?",
    ]
    st.markdown(
        '<div class="hib-cta-block">'
        '<p class="hib-cta-h">See It In Action</p>'
        '<p class="hib-cta-sub">This isn\'t just a portfolio showcase. <strong>Agy is a working AI assistant</strong> that can answer detailed questions about my projects, methodologies, and outcomes.</p>'
        '<div class="hib-cta-prompts">'
        f'<span class="hib-cta-prompt" data-hib-idx="0">How did Matt scale engineering teams from 4 to 150+ people?{_SVG_ARR}</span>'
        f'<span class="hib-cta-prompt" data-hib-idx="1">What were the biggest challenges at the Accenture Innovation Center?{_SVG_ARR}</span>'
        f'<span class="hib-cta-prompt" data-hib-idx="2">Show me examples of agile transformation with measurable outcomes{_SVG_ARR}</span>'
        f'<span class="hib-cta-prompt" data-hib-idx="3">How did Matt turn around a failing program?{_SVG_ARR}</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    for i, prompt in enumerate(_PROMPTS):
        if st.button("", key=f"hib_prompt_{i}"):
            st.session_state["seed_prompt"] = prompt
            st.session_state["__ask_from_suggestion__"] = True
            st.session_state["active_tab"] = "Ask Agy"
            st.session_state.pop("active_dialog", None)
            st.rerun()
    components.html(
        """
<script>
(function() {
    var parentDoc = window.parent.document;
    parentDoc.addEventListener('click', function(e) {
        var chip = e.target.closest('.hib-cta-prompt[data-hib-idx]');
        if (!chip) return;
        var idx = chip.getAttribute('data-hib-idx');
        var btn = parentDoc.querySelector('[class*="st-key-hib_prompt_' + idx + '"] button');
        if (btn) btn.click();
    });
})();
</script>
""",
        height=0,
    )
