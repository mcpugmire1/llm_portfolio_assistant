"""
Role Match Page

Paste a job description and see how Matt's experience maps to the requirements.
Three-step pipeline: extract requirements → retrieve stories → assess match.

Architecture: See ADR 016 and services/jd_assessor.py
"""

import html

import streamlit as st

from ui.components.thinking_indicator import render_thinking_indicator

# =============================================================================
# RESULTS RENDERING HELPERS
# =============================================================================
# Pure presentation — given a result dict from services.jd_assessor.run_assessment,
# render the recruiter view (status icons, evidence chips, gap explanations).
# Phase 2: recruiter view only — no fit score / recommendation / private section.

_STATUS_ICON = {"strong": "✓", "partial": "~", "gap": "✗"}


def _render_requirement_card(result: dict) -> str:
    """Build the HTML for a single requirement card. Returns a string (no st calls)."""
    status = result.get("match_status", "gap")
    icon = _STATUS_ICON.get(status, "?")
    requirement_text = html.escape(result.get("requirement", ""))

    parts = [
        '<div class="role-match-req-card">',
        '  <div class="role-match-req-header">',
        f'    <span class="role-match-status {status}">{icon}</span>',
        f'    <div class="role-match-req-text">{requirement_text}</div>',
        "  </div>",
    ]

    # Evidence chips (only for strong / partial — gaps render no chips per BDD)
    evidence_items = result.get("evidence") or []
    if status in ("strong", "partial") and evidence_items:
        parts.append('  <div class="role-match-evidence">')
        for ev in evidence_items[:2]:  # max 2 per BDD
            ev_type = ev.get("evidence_type", "story")
            if ev_type == "profile":
                # Profile-level evidence: "Verified skill" pill, no story/client.
                # Differentiated from story chips by purple-tinted background.
                relevance = html.escape(ev.get("relevance", ""))
                parts.append(
                    '    <div class="role-match-evidence-chip profile">'
                    '<span class="chip-label">Verified skill</span> — '
                    f"{relevance}</div>"
                )
            else:
                # Story evidence chip: title + client. Surface-gray background.
                title = html.escape(ev.get("story_title") or "Untitled")
                client = html.escape(ev.get("client") or "")
                client_str = (
                    f' <span class="chip-client">({client})</span>' if client else ""
                )
                parts.append(
                    '    <div class="role-match-evidence-chip">'
                    f"{title}{client_str}</div>"
                )
        parts.append("  </div>")

    # Gap explanation for partial / gap
    gap_text = (result.get("gap_explanation") or "").strip()
    if status in ("partial", "gap") and gap_text:
        parts.append(f'  <div class="role-match-gap">{html.escape(gap_text)}</div>')

    parts.append("</div>")
    return "\n".join(parts)


def _render_results_panel(result_payload: dict) -> None:
    """Render the full results panel — required + preferred sections.

    Args:
        result_payload: Output of services.jd_assessor.run_assessment, shape:
            {"extraction": {...}, "results": [{...}, ...]}
    """
    results = result_payload.get("results") or []
    if not results:
        st.markdown(
            '<p style="color: var(--text-secondary); text-align: center;">'
            "Couldn't extract any requirements from this job description.</p>",
            unsafe_allow_html=True,
        )
        return

    required = [r for r in results if r.get("category") == "required"]
    preferred = [r for r in results if r.get("category") == "preferred"]

    html_parts = ['<div class="role-match-results">']

    if required:
        html_parts.append(f"<h3>Required Qualifications ({len(required)})</h3>")
        for r in required:
            html_parts.append(_render_requirement_card(r))

    if preferred:
        html_parts.append(f"<h3>Preferred Qualifications ({len(preferred)})</h3>")
        for r in preferred:
            html_parts.append(_render_requirement_card(r))

    html_parts.append("</div>")

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)


def render_role_match(stories: list[dict]):
    """Render the Role Match page.

    Args:
        stories: All available stories for Pinecone retrieval
    """

    # =========================================================================
    # CSS STYLES
    # =========================================================================
    st.markdown(
        """
<style>
/* Conversation header styles for hero section */
.conversation-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    min-height: 184px;
    box-sizing: border-box;
    border-radius: 0;
    margin: -3rem 0 0 0;
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
</style>
""",
        unsafe_allow_html=True,
    )

    # =========================================================================
    # HEADER
    # =========================================================================
    st.markdown(
        """
<div class="conversation-header">
    <div class="conversation-header-content">
        <img class="conversation-agy-avatar" src="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/agy_avatar.png" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
        <div class="conversation-header-text">
            <h1>Role Match</h1>
            <p>Drop a job description. Agy will show you evidence where Matt fits — and where he doesn't.</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # =========================================================================
    # MOBILE GATE — Desktop only for v1
    # =========================================================================
    screen_width = st.session_state.get("_browser_screen_size", "")
    if screen_width and int(screen_width) < 768:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
                <p style="font-size: 18px; font-weight: 600;">Best experienced on desktop</p>
                <p style="font-size: 14px;">Role Match requires a wider screen to display the two-column layout.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        from ui.components.footer import render_footer

        render_footer()
        return

    # =========================================================================
    # JD INPUT ROW — textarea + button side by side
    # =========================================================================
    # Style the submit button to match Ask Agy purple treatment
    st.markdown(
        """
<style>
/* Role Match workspace — 2:3 columns (input | results) */
.st-key-role_match_workspace {
    margin-top: 48px;
}
/* Tight stacking inside the LEFT (input) column so button sits attached to textarea.
   Scoped to the first column only so result cards in the right column keep spacing. */
.st-key-role_match_workspace [data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* ===== RESULT PANEL — section headers, requirement cards, evidence ===== */
.role-match-results h3 {
    font-size: 13px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin: 0 0 12px 0 !important;
}
.role-match-results h3:not(:first-child) {
    margin-top: 24px !important;
}
.role-match-req-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.role-match-req-header {
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
.role-match-status {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    color: white;
    margin-top: 1px;
}
.role-match-status.strong  { background: #10B981; }     /* success green */
.role-match-status.partial { background: #F59E0B; }     /* amber */
.role-match-status.gap     { background: #EF4444; }     /* red */
.role-match-req-text {
    flex: 1;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.45;
}
.role-match-evidence {
    margin-top: 10px;
    padding-left: 32px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.role-match-evidence-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.35;
}
.role-match-evidence-chip .chip-client {
    color: var(--text-secondary);
    font-style: italic;
}
.role-match-evidence-chip.profile {
    background: var(--accent-purple-bg);
    border-color: var(--accent-purple-light);
}
.role-match-evidence-chip.profile .chip-label {
    font-weight: 600;
    color: var(--accent-purple-text);
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.05em;
}
.role-match-gap {
    margin-top: 8px;
    padding-left: 32px;
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
    font-style: italic;
}

/* ----- Subtle card treatment on both columns — uses existing variables ----- */
.st-key-role_match_workspace [data-testid="stColumn"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    box-shadow: var(--card-shadow) !important;
    padding: 24px 24px 32px 24px !important;
}

/* ----- Textarea styling — borderless, relies on card container for framing ----- */
.st-key-role_match_workspace textarea {
    padding: 20px 24px !important;
    font-size: 17px !important;
    border: none !important;
    border-radius: 12px !important;
    background: var(--bg-input) !important;
    color: var(--text-primary) !important;
    font-family: inherit !important;
    transition: box-shadow 0.2s ease !important;
}
.st-key-role_match_workspace textarea:focus {
    outline: none !important;
    background: var(--bg-card) !important;
    box-shadow: 0 0 0 2px var(--accent-purple-light) !important;
}
.st-key-role_match_workspace textarea::placeholder {
    color: var(--text-secondary) !important;
}
/* Kill BaseWeb wrapper borders so only the textarea itself shows a border */
.st-key-role_match_workspace div[data-baseweb="textarea"],
.st-key-role_match_workspace div[data-baseweb="base-input"] {
    border: none !important;
    background: transparent !important;
}
/* Small breathing room between textarea and button */
.st-key-role_match_workspace .st-key-role_match_submit {
    margin-top: 12px !important;
}
/* Match this role button — copied from .st-key-landing_ask in ask_mattgpt/styles.py */
.st-key-role_match_submit button,
.st-key-role_match_submit button[data-testid="stBaseButton-primary"],
.st-key-role_match_submit button[data-testid="stBaseButton-secondary"],
.st-key-role_match_submit button[class*="st-emotion-cache"] {
    background: #8B5CF6 !important;
    background-color: #8B5CF6 !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 32px !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    height: auto !important;
    min-height: 48px !important;
    white-space: nowrap !important;
    min-width: fit-content !important;
}
.st-key-role_match_submit button:hover:not(:disabled) {
    background: #7C3AED !important;
    color: white !important;
    transform: scale(1.02) !important;
}
.st-key-role_match_submit button p,
.st-key-role_match_submit button * {
    color: white !important;
    font-weight: 600 !important;
    margin: 0 !important;
}
</style>
""",
        unsafe_allow_html=True,
    )

    with st.container(key="role_match_workspace"):
        input_col, results_col = st.columns([2, 3], gap="large")

        # ----- LEFT: JD input + submit button (stacked, attached) -----
        with input_col:
            jd_text = st.text_area(
                "Job description",
                height=400,
                placeholder="Paste job description here...",
                key="role_match_jd_input",
                label_visibility="collapsed",
            )

            with st.container(key="role_match_submit"):
                submit_clicked = st.button(
                    "Match this role 🐾",
                    type="primary",
                    use_container_width=True,
                )

        # ----- RIGHT: results area — Agy thinking indicator during processing, results or empty state otherwise -----
        with results_col:
            # Process click first so the thinking indicator appears before results render
            if submit_clicked:
                if not jd_text.strip():
                    st.warning("Paste a job description first.")
                else:
                    # Match the Ask MattGPT pattern: st.empty() container + render_thinking_indicator()
                    # The indicator is a fixed-position overlay so it covers the whole viewport.
                    loading_container = st.empty()
                    with loading_container:
                        render_thinking_indicator()
                    try:
                        from services.jd_assessor import run_assessment

                        st.session_state["role_match_result"] = run_assessment(
                            jd_text, stories
                        )
                        st.session_state.pop("role_match_error", None)
                    except Exception as e:  # noqa: BLE001
                        st.session_state["role_match_error"] = str(e)
                        st.session_state.pop("role_match_result", None)
                    finally:
                        loading_container.empty()

            # Render: error → results → empty state, in priority order
            if st.session_state.get("role_match_error"):
                st.markdown(
                    '<div style="padding: 24px; color: var(--text-secondary);">'
                    "<strong>Couldn't run the assessment.</strong><br>"
                    f"{html.escape(st.session_state['role_match_error'])}</div>",
                    unsafe_allow_html=True,
                )
            elif st.session_state.get("role_match_result"):
                _render_results_panel(st.session_state["role_match_result"])
            else:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; justify-content: center; min-height: 400px;">
                        <p style="color: var(--text-secondary); font-size: 16px; text-align: center; margin: 0;">
                            Agy will match each requirement to Matt's career stories.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
