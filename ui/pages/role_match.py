"""
Role Match Page

Paste a job description and see how Matt's experience maps to the requirements.
Three-step pipeline: extract requirements → retrieve stories → assess match.

Architecture: See ADR 016 and services/jd_assessor.py
"""

import html

import streamlit as st

from ui.components.action_buttons import (
    get_action_buttons_css,
    get_action_buttons_html,
    render_action_button_handlers,
)
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


def _build_share_text(result_payload: dict) -> str:
    """Build a plain-text summary of the assessment for clipboard sharing.

    Recipients of this text get a self-contained, readable assessment they
    can paste into email, Slack, or a doc. Format is intentionally narrow:
    role/company header, then required and preferred sections with status
    icons and gap explanations under partials/gaps.
    """
    extraction = result_payload.get("extraction") or {}
    role = extraction.get("role_title") or "Untitled Role"
    company = extraction.get("company") or ""
    header = role + (f" — {company}" if company else "")

    results = result_payload.get("results") or []
    required = [r for r in results if r.get("category") == "required"]
    preferred = [r for r in results if r.get("category") == "preferred"]

    lines = [f"Role Match: {header}", ""]

    def _section(title: str, items: list[dict]) -> None:
        if not items:
            return
        lines.append(f"{title} ({len(items)})")
        for r in items:
            icon = _STATUS_ICON.get(r.get("match_status", "gap"), "?")
            lines.append(f"{icon} {r.get('requirement', '')}")
            if r.get("match_status") in ("partial", "gap"):
                gap = (r.get("gap_explanation") or "").strip()
                if gap:
                    lines.append(f"   Gap: {gap}")
        lines.append("")

    _section("REQUIRED", required)
    _section("PREFERRED", preferred)

    return "\n".join(lines).rstrip() + "\n"


def _build_export_html(result_payload: dict) -> str:
    """Build a printable HTML document for the Export action.

    Mirrors the structure of the on-screen results panel but laid out for
    print: role/company header, required and preferred sections, status
    icons, evidence under each requirement, gap explanations.
    """
    extraction = result_payload.get("extraction") or {}
    role = html.escape(extraction.get("role_title") or "Untitled Role")
    company = html.escape(extraction.get("company") or "")
    header_meta = company if company else ""

    results = result_payload.get("results") or []
    required = [r for r in results if r.get("category") == "required"]
    preferred = [r for r in results if r.get("category") == "preferred"]

    def _render_section(title: str, items: list[dict]) -> str:
        if not items:
            return ""
        rows = []
        rows.append(f'<h2 class="section-title">{title} ({len(items)})</h2>')
        for r in items:
            status = r.get("match_status", "gap")
            icon = _STATUS_ICON.get(status, "?")
            req_text = html.escape(r.get("requirement", ""))
            rows.append(
                f'<div class="req"><span class="status {status}">{icon}</span><span class="req-text">{req_text}</span></div>'
            )

            if status in ("strong", "partial"):
                for ev in (r.get("evidence") or [])[:2]:
                    ev_type = ev.get("evidence_type", "story")
                    if ev_type == "profile":
                        relevance = html.escape(ev.get("relevance", ""))
                        rows.append(
                            f'<div class="evidence profile"><strong>Verified skill</strong> — {relevance}</div>'
                        )
                    else:
                        title_text = html.escape(ev.get("story_title") or "Untitled")
                        client = html.escape(ev.get("client") or "")
                        client_str = f" ({client})" if client else ""
                        rows.append(
                            f'<div class="evidence">{title_text}{client_str}</div>'
                        )

            gap = (r.get("gap_explanation") or "").strip()
            if status in ("partial", "gap") and gap:
                rows.append(f'<div class="gap"><em>{html.escape(gap)}</em></div>')

        return "\n".join(rows)

    required_html = _render_section("Required Qualifications", required)
    preferred_html = _render_section("Preferred Qualifications", preferred)

    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Role Match — {role}</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; max-width: 900px; margin: 0 auto; color: #1F2937; }}
                h1 {{ color: #1F2937; font-size: 24px; margin-bottom: 4px; }}
                .meta {{ color: #6B7280; font-size: 14px; margin-bottom: 24px; }}
                .section-title {{ color: #8B5CF6; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 24px 0 12px 0; }}
                .req {{ display: flex; gap: 10px; align-items: flex-start; margin-bottom: 4px; padding-top: 12px; }}
                .req-text {{ font-size: 14px; font-weight: 500; color: #1F2937; line-height: 1.45; }}
                .status {{ display: inline-flex; flex-shrink: 0; width: 22px; height: 22px; border-radius: 50%; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: white; }}
                .status.strong {{ background: #10B981; }}
                .status.partial {{ background: #F59E0B; }}
                .status.gap {{ background: #EF4444; }}
                .evidence {{ margin-left: 32px; margin-top: 6px; padding: 6px 10px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; font-size: 12px; color: #1F2937; }}
                .evidence.profile {{ background: rgba(139, 92, 246, 0.08); border-color: rgba(139, 92, 246, 0.2); }}
                .gap {{ margin-left: 32px; margin-top: 6px; font-size: 12px; color: #6B7280; }}
            </style>
        </head>
        <body>
            <h1>Role Match — {role}</h1>
            <div class="meta">{header_meta}</div>
            {required_html}
            {preferred_html}
        </body>
        </html>
    """


def _render_results_header(result_payload: dict) -> None:
    """Render the results header bar: extracted role title + action buttons.

    The header is a flex container with the role title on the left and the
    shared Helpful / Share / Export buttons on the right (per story_detail
    pattern). Buttons appear only when there is a result to act on.
    """
    extraction = result_payload.get("extraction") or {}
    role = html.escape(extraction.get("role_title") or "Untitled Role")
    company = html.escape(extraction.get("company") or "")

    # Stable per-assessment id so the helpful-confirmed flag resets on a new
    # assessment. id() is stable for the lifetime of the dict in session_state.
    assessment_id = id(result_payload)
    confirmed_key = f"role_match_helpful_{assessment_id}"
    is_helpful_confirmed = st.session_state.get(confirmed_key) == "up"

    buttons_html = get_action_buttons_html(
        button_id_prefix="btn-role-match",
        is_helpful_confirmed=is_helpful_confirmed,
    )

    company_html = (
        f'<div class="role-match-results-company">{company}</div>' if company else ""
    )
    st.markdown(
        f"""
        <div class="role-match-results-header">
            <div class="role-match-results-title-section">
                <div class="role-match-results-title">{role}</div>
                {company_html}
            </div>
            {buttons_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_action_button_handlers(
        button_id_prefix="btn-role-match",
        key_suffix=f"role_match_{assessment_id}",
        share_text=_build_share_text(result_payload),
        export_html_doc=_build_export_html(result_payload),
        feedback_query=extraction.get("role_title") or "Role Match",
        feedback_sources=f"role_match:{extraction.get('role_title') or 'unknown'}",
        confirmed_key=confirmed_key,
        feedback_msg_hash=assessment_id % 100000,
    )


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

    # Header bar with role title + action buttons (Helpful / Share / Export)
    _render_results_header(result_payload)

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
    # CSS STYLES (page hero only)
    # =========================================================================
    # IMPORTANT: action_buttons CSS + .role-match-results-header styles are
    # injected at the BOTTOM of this function (just before render_footer()).
    # DO NOT add a second st.markdown here or it will break the navbar gap —
    # an extra empty stMarkdownContainer between the navbar and the
    # .conversation-header element adds ~16px of vertical space that the
    # `.conversation-header { margin: -3rem 0 0 0 }` rule was tuned for ONE
    # preceding element only. See git commit history for the regression we
    # introduced and reverted (April 2026).
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
    # MOBILE GATE — Desktop only for v1 (≥ 1024px, iPad Pro and up)
    # =========================================================================
    # Threshold raised from 768 to 1024 (April 2026) after visual testing
    # confirmed that the two-column workspace is only legible at iPad Pro
    # width or wider. Tablets in the 768-1023px range previously slipped
    # through the gate and rendered the workspace in a cramped state.
    screen_width = st.session_state.get("_browser_screen_size", "")
    if screen_width and int(screen_width) < 1024:
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

    # =========================================================================
    # CSS STYLES (results panel + shared action buttons)
    # =========================================================================
    # IMPORTANT: this block lives at the BOTTOM of render_role_match — NOT
    # next to the page hero CSS at the top. Adding a second st.markdown
    # between the navbar and the .conversation-header element introduces an
    # extra empty stMarkdownContainer that adds ~16px of vertical space the
    # navbar→hero negative-margin compensation cannot absorb. Browser CSS
    # parsing does not depend on source order, so injecting these rules at
    # the bottom of the document still applies them to elements rendered
    # above. See git history for the regression we introduced and reverted
    # (April 2026).
    st.markdown(
        f"""
<style>
{get_action_buttons_css()}

/* Results header bar — flex container for the role title (left) and the
   shared Helpful / Share / Export action buttons (right). Sits at the top
   of the right column when results render. */
.role-match-results-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    padding-bottom: 16px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--border-color);
}}
.role-match-results-title-section {{
    flex: 1;
    min-width: 0;
}}
.role-match-results-title {{
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.3;
}}
.role-match-results-company {{
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 4px;
}}
@media (max-width: 768px) {{
    .role-match-results-header {{
        flex-direction: column;
        gap: 8px;
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
