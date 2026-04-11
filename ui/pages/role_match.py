"""
Role Match Page

Paste a job description and see how Matt's experience maps to the requirements.
Three-step pipeline: extract requirements → retrieve stories → assess match.

Architecture: See ADR 016 and services/jd_assessor.py
"""

import html
from urllib.parse import urlencode

import streamlit as st

from scripts.utils import slugify
from ui.components.action_buttons import (
    get_action_buttons_css,
    get_action_buttons_html,
    render_action_button_handlers,
)
from ui.components.story_detail import render_story_detail
from ui.components.thinking_indicator import render_thinking_indicator

# =============================================================================
# RESULTS RENDERING HELPERS
# =============================================================================
# Pure presentation — given a result dict from services.jd_assessor.run_assessment,
# render the recruiter view (status icons, evidence chips, gap explanations).
# Phase 2: recruiter view only — no fit score / recommendation / private section.

_STATUS_ICON = {"strong": "✓", "partial": "~", "gap": "✗"}


def _find_story_by_title_client(
    stories: list[dict], title: str | None, client: str | None
) -> dict | None:
    """Look up a story in the corpus by title (and optionally client).

    Used to map an LLM-returned evidence chip back to the full story dict so
    the chip can be made clickable for inline detail expansion. Match is
    case-insensitive on title; if a client is provided, the client must also
    match (case-insensitive).

    Returns the first matching story, or None if no story matches. None
    return is the graceful-degradation path: the chip stays non-clickable
    rather than offering a click that does nothing.
    """
    if not title:
        return None

    # Normalize: lowercase + collapse internal whitespace runs to a single
    # space. The corpus has historical titles with double spaces (e.g.
    # "Launchpad:  Empowering Clients..."), and the LLM normalizes them
    # to single spaces in its output. Without internal whitespace
    # collapse, the strict equality below misses those titles and the
    # chip falls through to the non-clickable unresolved-chip path.
    def _norm(s: str) -> str:
        return " ".join(s.split()).lower()

    title_norm = _norm(title)
    client_norm = _norm(client or "")
    for s in stories:
        s_title = _norm(s.get("Title") or "")
        if s_title != title_norm:
            continue
        if not client_norm:
            return s
        s_client = _norm(s.get("Client") or "")
        if s_client == client_norm:
            return s
    return None


def _resolve_evidence_stories(
    results: list[dict], stories: list[dict]
) -> dict[str, dict]:
    """Walk every story-evidence chip in the assessment and resolve to story dicts.

    Returns a map keyed by composite index `f"{req_idx}_{ev_idx}"` whose
    values are the full story dicts. Profile-evidence chips and story chips
    whose title/client cannot be resolved are NOT included in the map — the
    presence of a key in the map is the canonical signal that the chip is
    clickable.

    Resolution happens once at render time so the click handler doesn't
    need to re-look-up at click time. Pattern borrowed from Timeline view's
    story_map (ui/components/timeline_view.py).
    """
    # Resolve EVERY story-evidence item, not just the first two. The
    # rendering layer enforces the per-type cap (1 profile + 2 stories).
    # If we capped here at the combined first 2, an LLM response of
    # [profile, story_A, story_B] would never resolve story_B → it would
    # render as a non-clickable unresolved chip even though the story
    # exists in the corpus. (Bug found April 2026.)
    resolved: dict[str, dict] = {}
    for req_idx, result in enumerate(results):
        for ev_idx, ev in enumerate(result.get("evidence") or []):
            if ev.get("evidence_type", "story") != "story":
                continue
            story = _find_story_by_title_client(
                stories, ev.get("story_title"), ev.get("client")
            )
            if story is not None:
                resolved[f"{req_idx}_{ev_idx}"] = story
    return resolved


def _render_requirement_card(
    result: dict,
    req_idx: int,
    evidence_stories: dict[str, dict],
    active_evidence_key: str | None = None,
) -> None:
    """Emit Streamlit elements for a single requirement card.

    Pattern: matches ui/pages/ask_mattgpt/conversation_helpers.py:626-700.
    The chip is a real `st.button` styled via scoped CSS targeting its
    `st-key-evidence_btn_<key>` class. No HTML chip, no JS bridge, no
    hidden trigger button. Click is handled by Streamlit natively.

    Toggle behavior comes for free from the if-clicked handler:
      - Click same chip again → pop the active key (close)
      - Click different chip → overwrite the active key (switch)
    """
    status = result.get("match_status", "gap")
    icon = _STATUS_ICON.get(status, "?")
    requirement_text = html.escape(result.get("requirement", ""))

    with st.container(key=f"role_match_req_{req_idx}"):
        # 1. Title row — 22px circular status badge + requirement title.
        # Class structure matches the locked v3 spec (April 2026 design
        # pivot): the link icon (🔗) is reserved EXCLUSIVELY for clickable
        # story chips, so the badge here is purely structural.
        st.markdown(
            f'<div class="role-match-req-title-row">'
            f'<div class="role-match-status-badge {status}">{icon}</div>'
            f'<span class="role-match-req-title">{requirement_text}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # 2. Evidence — split by type, then cap PER TYPE so a noisy
        # profile-only response doesn't starve the chip row of proof
        # points. The per-type cap is:
        #   - up to 1 profile evidence block (the argument)
        #   - up to 2 story chips (the proof)
        # Original ev_idx values are preserved across both passes so the
        # composite_key stays stable for the click toggle.
        #
        # Order in the card:
        #   title row
        #   → profile evidence block      ← argument first
        #   → story chip row              ← proof second
        #   → gap text                    ← caveat last
        evidence_items = result.get("evidence") or []
        indexed_evidence = list(enumerate(evidence_items))
        profile_evidence = [
            (ev_idx, ev)
            for ev_idx, ev in indexed_evidence
            if ev.get("evidence_type", "story") == "profile"
        ][:1]  # 1 profile block max
        story_evidence = [
            (ev_idx, ev)
            for ev_idx, ev in indexed_evidence
            if ev.get("evidence_type", "story") == "story"
        ][:2]  # 2 story chips max

        if status in ("strong", "partial") and (profile_evidence or story_evidence):
            # --- Pass A: profile evidence block (argument) ---
            for _ev_idx, ev in profile_evidence:
                relevance = html.escape(ev.get("relevance", ""))
                st.markdown(
                    '<div class="role-match-profile-evidence">'
                    '<span class="role-match-verified-dot"></span>'
                    f" Verified profile · {relevance}"
                    "</div>",
                    unsafe_allow_html=True,
                )

            # --- Pass B: story chip row (proof) ---
            # Only emit the flex-wrap container when there are story
            # chips to put in it; an empty container leaves stray padding.
            if story_evidence:
                with st.container(key=f"role_match_evidence_{req_idx}"):
                    for ev_idx, ev in story_evidence:
                        composite_key = f"{req_idx}_{ev_idx}"

                        if composite_key in evidence_stories:
                            # Story chip resolved to a corpus story → render
                            # as a Streamlit button. Label changes based on
                            # active state: collapsed shows "🔗 Title · Client",
                            # expanded shows "✕ Close". Toggle handled in the
                            # if-clicked block below.
                            #
                            # DO NOT change the button key pattern or the
                            # toggle logic — this is the locked-in fix for
                            # the chip expansion bug (April 2026). Only the
                            # label string format and CSS may change.
                            is_active = active_evidence_key == composite_key
                            title_text = ev.get("story_title") or "Untitled"
                            client = ev.get("client") or ""

                            if is_active:
                                button_label = "✕ Close"
                                # Inject scoped CSS for the active button only.
                                st.markdown(
                                    f"""
                                    <style>
                                    [class*="st-key-evidence_btn_{composite_key}"] button[kind="secondary"] {{
                                        background: var(--accent-purple) !important;
                                        border-color: var(--accent-purple-hover) !important;
                                        color: white !important;
                                    }}
                                    [class*="st-key-evidence_btn_{composite_key}"] button[kind="secondary"] p {{
                                        color: white !important;
                                        font-weight: 600 !important;
                                    }}
                                    </style>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                client_suffix = f" · {client}" if client else ""
                                button_label = f"🔗 {title_text}{client_suffix}"

                            if st.button(
                                button_label,
                                key=f"evidence_btn_{composite_key}",
                            ):
                                # Toggle: same → close. Different → switch.
                                if (
                                    st.session_state.get("role_match_active_evidence")
                                    == composite_key
                                ):
                                    st.session_state.pop(
                                        "role_match_active_evidence", None
                                    )
                                else:
                                    st.session_state["role_match_active_evidence"] = (
                                        composite_key
                                    )
                                st.rerun()
                        else:
                            # Unresolved story chip — non-clickable pill in
                            # the same muted treatment as the profile chip
                            # family. Stays a PILL because "Title · Client"
                            # is a short reference, not an argument.
                            title_text = html.escape(
                                ev.get("story_title") or "Untitled"
                            )
                            client = html.escape(ev.get("client") or "")
                            client_suffix = f" · {client}" if client else ""
                            st.markdown(
                                '<div class="role-match-chip-verified '
                                'role-match-chip-verified--no-dot">'
                                f"{title_text}{client_suffix}"
                                "</div>",
                                unsafe_allow_html=True,
                            )

        # 3. .gap-text — markup copied verbatim from mockup (line 213):
        #     <div class="gap-text">...</div>
        gap_text = (result.get("gap_explanation") or "").strip()
        if status in ("partial", "gap") and gap_text:
            st.markdown(
                f'<div class="role-match-gap-text">{html.escape(gap_text)}</div>',
                unsafe_allow_html=True,
            )


def _build_share_text(result_payload: dict) -> str:
    """Build a plain-text summary of the assessment for clipboard sharing.

    Recipients of this text get a self-contained, readable fit assessment
    they can paste into email, Slack, or an ATS notes field. Format is
    intentionally narrow:

        Matt Pugmire — <role> fit assessment
        <company>

        REQUIRED (N)
        ✓/~/✗ requirement
           Note: ... (only for partial/gap)

        PREFERRED (N)
        ...

        Explore Matt's full portfolio: https://askmattgpt.streamlit.app

    The header reframes the artifact as a fit assessment (not a generic
    "role match"), names Matt explicitly so a forwarded report is
    self-contained, and the trailing portfolio URL turns every paste
    into a referral channel back to the live experience.
    """
    extraction = result_payload.get("extraction") or {}
    role = extraction.get("role_title") or "Untitled Role"
    company = extraction.get("company") or ""

    results = result_payload.get("results") or []
    required = [r for r in results if r.get("category") == "required"]
    preferred = [r for r in results if r.get("category") == "preferred"]

    lines = [f"Matt Pugmire — {role} fit assessment"]
    if company:
        lines.append(company)
    lines.append("")

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
                    # Indent only — no "Gap:" prefix. The LLM's gap_explanation
                    # already starts with "Note:" (per the assessment prompt),
                    # so a "Gap:" prefix produces the redundant "Gap: Note: ..."
                    # in the clipboard output. The 3-space indent visually
                    # subordinates the note to its requirement.
                    lines.append(f"   {gap}")
        lines.append("")

    _section("REQUIRED", required)
    _section("PREFERRED", preferred)

    # Trailing portfolio referral — every forwarded report is a referral
    # back to the live experience. UTM params let the existing
    # log_page_load() flow in app.py attribute inbound traffic from
    # forwarded reports back to the originating role.
    #
    # utm_source=role_match     — names the surface that produced the link
    # utm_medium=clipboard      — names the mechanism (not the channel — we
    #                             don't know if it's Slack/email/ATS/etc.)
    # utm_campaign=fit_assessment — stable artifact category
    # utm_content=<role-company> — slugified role + company so analytics
    #                             can split inbound clicks by which forwarded
    #                             report they came from. Skipped if both
    #                             role and company are empty.
    utm_params = {
        "utm_source": "role_match",
        "utm_medium": "clipboard",
        "utm_campaign": "fit_assessment",
    }
    content_slug = slugify(f"{role} {company}".strip())
    if content_slug:
        utm_params["utm_content"] = content_slug
    portfolio_url = f"https://askmattgpt.streamlit.app/?{urlencode(utm_params)}"

    lines.append("")
    lines.append(f"Explore Matt's full portfolio: {portfolio_url}")

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
                .req {{ display: flex; gap: 10px; align-items: center; margin: 0 0 4px 0; padding: 12px 0 0 0; }}
                .req-text {{ font-size: 14px; font-weight: 500; color: #1F2937; line-height: 1.45; margin: 0; padding: 0; }}
                /* Status badge — explicit margin/padding zero and line-height
                   lock so the badge sits identically across strong/partial/gap
                   regardless of how the inner glyph (✓ ~ ✗) renders in the
                   browser's print font. */
                .status {{ display: inline-flex; flex-shrink: 0; width: 22px; height: 22px; border-radius: 50%; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: white; line-height: 1; margin: 0; padding: 0; box-sizing: border-box; text-align: center; }}
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


def _render_results_panel(result_payload: dict, stories: list[dict]) -> None:
    """Render the full results panel — required + preferred sections.

    Per-requirement rendering loop. Each requirement card is emitted as its
    own st.markdown call so that hidden Streamlit buttons (for chip click
    handling) and an inline render_story_detail call (for the expanded chip,
    if any) can be interleaved between cards. The Cards-view pattern from
    Explore Stories — see ui/pages/explore_stories.py:2393-2487 — was the
    direct inspiration.

    Args:
        result_payload: Output of services.jd_assessor.run_assessment, shape:
            {"extraction": {...}, "results": [{...}, ...]}
        stories: Full story corpus, used to resolve evidence-chip
            (title, client) pairs to story dicts for inline expansion.
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

    # Legend bar — sits between the results header and the first section
    # header, gives the recruiter a key to the badges and chip affordances
    # (✓ ~ ✗ status, 🔗 = clickable story, ● = profile evidence).
    #
    # IMPORTANT: rendered with INLINE styles, not class selectors. An
    # earlier class-based version rendered stacked vertically because
    # Streamlit's markdown parser broke the inline-flex layout. Inline
    # styles bypass the parser entirely.
    legend_html = (
        '<div class="role-match-legend" '
        'style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;'
        "padding:10px 14px;background:var(--bg-card);"
        "border:1px solid var(--border-color);border-radius:10px;"
        'margin-bottom:14px;font-size:11px;color:var(--text-secondary);">'
        # ✓ Strong match
        '<div style="display:inline-flex;align-items:center;gap:6px;">'
        '<span style="display:inline-flex;align-items:center;justify-content:center;'
        "width:16px;height:16px;border-radius:50%;background:var(--success-color);"
        'color:white;font-size:10px;font-weight:700;line-height:1;">✓</span>'
        "Strong match</div>"
        # ~ Partial
        '<div style="display:inline-flex;align-items:center;gap:6px;">'
        '<span style="display:inline-flex;align-items:center;justify-content:center;'
        "width:16px;height:16px;border-radius:50%;"
        "background:var(--warning-color,#F59E0B);"
        'color:white;font-size:10px;font-weight:700;line-height:1;">~</span>'
        "Partial</div>"
        # ✗ Gap
        '<div style="display:inline-flex;align-items:center;gap:6px;">'
        '<span style="display:inline-flex;align-items:center;justify-content:center;'
        "width:16px;height:16px;border-radius:50%;"
        "background:var(--error-color,#EF4444);"
        'color:white;font-size:10px;font-weight:700;line-height:1;">✗</span>'
        "Gap</div>"
        # divider
        '<span style="width:1px;height:14px;background:var(--border-color);'
        'display:inline-block;"></span>'
        # 🔗 = clickable story
        '<div style="display:inline-flex;align-items:center;gap:6px;">'
        "🔗 = clickable story</div>"
        # ● = profile evidence
        '<div style="display:inline-flex;align-items:center;gap:6px;">'
        '<span style="width:8px;height:8px;border-radius:50%;'
        'background:var(--success-color);display:inline-block;"></span>'
        " = profile evidence</div>"
        "</div>"
    )
    st.markdown(legend_html, unsafe_allow_html=True)

    # Hint text lives in the LEFT column above the textarea (rendered in
    # render_role_match), NOT in the right column above the results panel.

    # Resolve every story-evidence chip to a story dict at render time so
    # the chips can be marked clickable up-front and chips that don't
    # resolve fall back to non-clickable plain text (graceful degradation
    # when the LLM paraphrases a title and the corpus lookup misses).
    evidence_stories = _resolve_evidence_stories(results, stories)
    active_evidence_key = st.session_state.get("role_match_active_evidence")

    # Reset active evidence if it points to a chip that no longer exists in
    # this assessment (e.g., user submitted a new JD between renders).
    if active_evidence_key and active_evidence_key not in evidence_stories:
        active_evidence_key = None
        st.session_state.pop("role_match_active_evidence", None)

    # Group requirements by category, preserving original index for the
    # composite key that the click handler uses.
    required = [
        (idx, r) for idx, r in enumerate(results) if r.get("category") == "required"
    ]
    preferred = [
        (idx, r) for idx, r in enumerate(results) if r.get("category") == "preferred"
    ]

    if required:
        _render_results_section(
            "Required Qualifications",
            required,
            evidence_stories,
            active_evidence_key,
            stories,
        )

    if preferred:
        _render_results_section(
            "Preferred Qualifications",
            preferred,
            evidence_stories,
            active_evidence_key,
            stories,
        )

    # No JS click handler — chip clicks are handled by Streamlit natively
    # via the st.button calls inside _render_requirement_card. Pattern matches
    # ui/pages/ask_mattgpt/conversation_helpers.py:626-700.


def _render_results_section(
    title: str,
    indexed_results: list[tuple[int, dict]],
    evidence_stories: dict[str, dict],
    active_evidence_key: str | None,
    stories: list[dict],
) -> None:
    """Render a section header (h3) and all requirement cards in the section."""
    st.markdown(
        f'<h3 class="role-match-section-header">{html.escape(title)} '
        f"({len(indexed_results)})</h3>",
        unsafe_allow_html=True,
    )

    for req_idx, result in indexed_results:
        _render_requirement_card(result, req_idx, evidence_stories, active_evidence_key)

        # If the active chip belongs to this requirement, expand inline below.
        if active_evidence_key:
            try:
                active_req_idx = int(active_evidence_key.split("_")[0])
            except (ValueError, IndexError):
                active_req_idx = None
            if active_req_idx == req_idx and active_evidence_key in evidence_stories:
                render_story_detail(
                    evidence_stories[active_evidence_key],
                    f"role_match_ev_{active_evidence_key}",
                    stories,
                    show_actions=False,
                )


def render_role_match(stories: list[dict]):
    """Render the Role Match page.

    Args:
        stories: All available stories for Pinecone retrieval
    """

    # =========================================================================
    # SESSION STATE RESTORE — JD textarea persistence across navigation
    # =========================================================================
    # Streamlit garbage-collects widget state for widgets that aren't in the
    # current page tree. When the user navigates away from Role Match (e.g.
    # to Home) and back, the textarea's `role_match_jd_input` widget key is
    # gone, but `role_match_result` (a regular session_state key) survives.
    # Without this restore, the user comes back to an empty textarea sitting
    # next to populated results — confusing and inconsistent.
    #
    # Pattern: prefilter — set the widget's session_state key BEFORE the
    # widget renders so Streamlit picks it up on first render. See
    # CLAUDE.md "Use prefilter pattern for cross-page navigation" and the
    # banking_landing.py → explore_stories.py example.
    if (
        "role_match_jd_input" not in st.session_state
        and "role_match_jd_persisted" in st.session_state
    ):
        st.session_state["role_match_jd_input"] = st.session_state[
            "role_match_jd_persisted"
        ]

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

/* Zero the parent stLayoutWrapper gap inside the workspace. The wrapper
   has `gap: normal` (~16px) by default which would stack on top of each
   card's `margin-bottom: 10px`, producing 26px of visible space between
   cards — too much. With this rule, the card's margin-bottom is the
   ONLY thing controlling card-to-card spacing → ~10px breathing room.
   Scoped to .st-key-role_match_workspace so the rule does not affect
   other pages that use stLayoutWrapper. (April 2026 incident: see
   the diagnostic in the chat history that identified the parent
   stLayoutWrapper gap as the source of excess card-to-card space.) */
.st-key-role_match_workspace [data-testid="stLayoutWrapper"] {
    gap: 0 !important;
}

/* ===== RESULT PANEL — section headers, requirement cards, evidence =====
   Locked design: see role_match_mockup_v2.html. Status indicators are plain
   colored text (no circle/badge), chips are pill-shaped purple tags in the
   "🔗 Title · Client" format, gap text is plain secondary-color (no italic).
   Profile-evidence and unresolved story chips share the same chip family. */
h3.role-match-section-header {
    font-size: 10px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted, #9CA3AF);
    margin: 4px 0 8px 2px !important;
}
h3.role-match-section-header:not(:first-of-type) {
    margin-top: 16px !important;
}
/* Card container — each requirement is wrapped in
   `with st.container(key=f"role_match_req_{req_idx}"):` which produces a
   single div that IS the stVerticalBlock (verified via DevTools: the card
   div has class "stVerticalBlock st-key-role_match_req_X"). This rule
   styles the card frame AND tightens the gap between its direct children
   in one selector — there is no nested vertical block to target.

   IMPORTANT: do NOT add a nested-descendant gap selector like
   `[class*="st-key-role_match_req_"] [data-testid="stVerticalBlock"]`.
   That selector matches nothing because there is no nested vertical block
   inside the card. (April 2026 incident: this exact mistake left
   Streamlit's default 1rem gap in effect for an entire debug session.) */
/* .req-card — values copied verbatim from role_match_mockup_v2.html.
   Streamlit's st.container(key="role_match_req_X") produces a stVerticalBlock
   that we style as the card directly. Class names below match the mockup
   (req-card, req-title-row, status, req-title, chip, chip-icon, gap-text)
   so the markup structure mirrors the mockup node-for-node. */
[class*="st-key-role_match_req_"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    /* Explicit longhand padding-bottom — the shorthand above is sometimes
       clobbered by a Streamlit stVerticalBlock default, leaving the last
       child (typically gap text) flush against the card's bottom border.
       The longhand re-asserts the bottom breathing room with higher
       resilience. (April 2026 incident: gap text rendered flush even
       though shorthand padding declared 12px bottom.) */
    padding-bottom: 14px !important;
    margin-bottom: 12px !important;
    gap: 10px !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Zero margin/padding on the DIRECT CHILDREN of the card only.
   Uses the `>` direct-child combinator (not the descendant space)
   so the rule physically cannot match the card itself or any outer
   wrapper Streamlit puts around the card — only the elements
   immediately inside the card. This is what fixes the inside-card
   spacing without nuking the card-to-card margin-bottom. */
[class*="st-key-role_match_req_"] > [data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}
/* Reach one level deeper for any emotion-cache wrappers that sit
   between the stElementContainer and the actual stMarkdown / stButton.
   Still scoped to direct children of the card via the leading `>`. */
[class*="st-key-role_match_req_"] > [data-testid="stElementContainer"] > div,
[class*="st-key-role_match_req_"] > [data-testid="stElementContainer"] .stMarkdown,
[class*="st-key-role_match_req_"] > [data-testid="stElementContainer"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
}

/* Defensive re-assertion of margin-bottom on the card itself with a
   higher-specificity selector. If anything in the broader cascade
   manages to zero the card's bottom margin, this rule pulls it back
   to 12px. The added attribute selector `[data-testid="stVerticalBlock"]`
   bumps specificity from (0,1,0) to (0,2,0) so it beats any
   competing class-only rule. */
div[class*="st-key-role_match_req_"][data-testid="stVerticalBlock"] {
    margin-bottom: 12px !important;
}

/* JD input hint — sits in the LEFT column above the textarea. */
.role-match-jd-hint {
    font-family: inherit;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0 0 16px 0 !important;
    padding: 0;
}
/* The left column's vertical block has `gap: 0` to keep the textarea
   attached to its submit button. That rule also collapses the breathing
   room between the hint paragraph and the textarea, so we restore it
   here by giving the hint's stElementContainer a real bottom margin. */
.st-key-role_match_workspace [data-testid="stColumn"]:first-child
    [data-testid="stElementContainer"]:has(.role-match-jd-hint) {
    margin-bottom: 16px !important;
}

/* === V3 design pivot (April 2026) ===
   Status badge: 22px colored circle with white glyph (NOT plain colored text)
   Profile chips: muted bg, secondary text, green dot prefix, NO 🔗
   Story chips: pill, brand purple text, 🔗 prefix, clickable
   Unresolved story chips: SAME visual as profile chip, no green dot
   Evidence row: horizontal flex-wrap at padding-left 32px
   Gap text: italic muted text at padding-left 32px */

/* Title row — flex with the badge sitting in a fixed gutter to the left
   of the wrapping title text. */
.role-match-req-title-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
/* Status badge — 22px circle, colored bg with white glyph inside.
   Backgrounds use the existing semantic CSS variables (success/warning/error)
   so they stay in lockstep with the rest of the app's color tokens. */
.role-match-status-badge {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    color: white;
    line-height: 1;
    margin-top: 1px;
}
.role-match-status-badge.strong  { background: var(--success-color, #10B981); }
.role-match-status-badge.partial { background: var(--warning-color, #F59E0B); }
.role-match-status-badge.gap     { background: var(--error-color, #EF4444); }
.role-match-req-title {
    flex: 1;
    font-size: 13px;
    color: var(--text-primary);
    line-height: 1.4;
    margin-top: 2px;
}

/* Evidence row — st.container(key="role_match_evidence_X") wraps every
   chip for a given requirement. We turn the container into a horizontal
   flex-wrap row and force its inner stElementContainers to size to
   content so chips flow inline instead of stacking. The 32px padding-left
   indents the row to align with the requirement title (22px badge + 10px gap). */
[class*="st-key-role_match_evidence_"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
    padding-left: 32px !important;
    margin-top: 2px !important;
}
[class*="st-key-role_match_evidence_"] [data-testid="stElementContainer"] {
    width: auto !important;
    flex: 0 0 auto !important;
    margin: 0 !important;
    padding: 0 !important;
}
[class*="st-key-role_match_evidence_"] [data-testid="stElementContainer"] .stMarkdown {
    width: auto !important;
}

/* Profile evidence — block-level argumentative prose, NOT a pill. The
   pill format breaks for substantive sentences, so profile evidence
   gets a block container indented to 32px (matching the chip row),
   with a small green dot prefix in muted secondary-color text.
   (April 2026 v3.1 design pivot.) */
.role-match-profile-evidence {
    display: block;
    padding-left: 32px;
    padding-right: 8px;
    margin: 4px 0;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-secondary);
}
.role-match-profile-evidence .role-match-verified-dot {
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
    margin-bottom: 1px;
}

/* Verified profile chip — muted background, secondary text, small
   green dot prefix. Used for both profile evidence chips and unresolved
   story chips (the unresolved variant suppresses the dot). */
.role-match-chip-verified {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 11px;
    color: var(--text-secondary);
    line-height: 1.4;
    cursor: default;
    max-width: 100%;
}
.role-match-verified-dot {
    flex-shrink: 0;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--success-color);
    display: inline-block;
}
.role-match-chip-verified--no-dot .role-match-verified-dot {
    display: none;
}

/* Gap explanation — italic muted text indented 32px to align with the
   chip row. The 8px margin-top creates clear visual separation from
   the chip row above so the explanation reads as a distinct caveat,
   not as a continuation of the chip label. */
.role-match-gap-text {
    font-size: 12px;
    color: var(--text-secondary);
    padding-left: 32px;
    line-height: 1.4;
    font-style: normal;
    margin: 8px 0 4px 0;
}

/* Legend bar — static row at the top of the results panel above the
   first section header. */
.role-match-legend {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 16px;
    padding: 10px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    margin-bottom: 14px;
    font-size: 11px;
    color: var(--text-secondary);
}
.role-match-legend .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.role-match-legend .legend-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    color: white;
    font-size: 10px;
    font-weight: 700;
    line-height: 1;
}
.role-match-legend .legend-badge.strong  { background: var(--success-color); }
.role-match-legend .legend-badge.partial { background: var(--warning-color); }
.role-match-legend .legend-badge.gap     { background: var(--error-color); }
.role-match-legend .legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--success-color);
    display: inline-block;
}
.role-match-legend .legend-divider {
    width: 1px;
    height: 14px;
    background: var(--border-color);
}

/* ----- Subtle card treatment on both columns — uses existing variables ----- */
.st-key-role_match_workspace [data-testid="stColumn"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    box-shadow: var(--card-shadow) !important;
    padding: 24px 24px 32px 24px !important;
}

/* ----- Textarea styling — borderless, relies on card container for framing.
   Font size matches .role-match-jd-hint (13px) and the right-column results
   panel so the left and right sides read in the same visual register. */
.st-key-role_match_workspace textarea {
    padding: 20px 24px !important;
    font-size: 13px !important;
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
    font-family: inherit !important;
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

        # ----- LEFT: hint + JD input + submit button (stacked, attached) -----
        with input_col:
            # Hint text — plain secondary-color, sits above the textarea.
            # Per role_match_mockup_v2.html, the hint lives in the LEFT
            # column only and is NOT duplicated in the right column.
            st.markdown(
                '<p class="role-match-jd-hint">'
                "Paste a job description below. Agy will match each "
                "requirement and you can click any chip to explore the story."
                "</p>",
                unsafe_allow_html=True,
            )

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
                        # Persist the JD text in a NON-widget session key so
                        # we can restore the textarea after a navigation away
                        # and back. Streamlit garbage-collects widget state
                        # for widgets that aren't currently in the page tree
                        # (e.g., when the user navigates to Home), but
                        # role_match_result survives because it's a regular
                        # session_state key. Without this persisted copy the
                        # user comes back to an empty textarea sitting next
                        # to populated results — a confusing inconsistency.
                        st.session_state["role_match_jd_persisted"] = jd_text
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
                _render_results_panel(st.session_state["role_match_result"], stories)
            else:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; justify-content: center; min-height: 400px;">
                        <p style="color: var(--text-secondary); font-size: 16px; text-align: center; margin: 0; font-family: inherit;">
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

/* ===== Clickable story-evidence chips (real Streamlit buttons) =====
   Each clickable story chip is a `st.button(key=f"evidence_btn_<key>")`
   call inside the requirement card container. The button key pattern and
   the toggle logic are LOCKED — only the label string format and the CSS
   below may change. See the comment in _render_requirement_card.

   We style the Streamlit button to look like the same pill chip used for
   profile-evidence and unresolved-story chips (.role-match-evidence-chip),
   so all evidence on the page reads as a single UI family. Format:
   "🔗 Title · Client" — purple text, pill shape, fit-content width.

   The active state (purple background, white text, "✕ Close" label) is
   applied via per-button inline CSS injection from the render code, so
   only the currently-active button gets the override. */

/* Force the wrapper divs to size to content. Without these the
   stElementContainer is block-level full-width and the chip appears as
   a wide form button regardless of the inner button's width. NO
   margin-left here — the parent .role-match-evidence-row container
   handles indentation via padding-left: 32px. */
[class*="st-key-evidence_btn_"] {{
    width: fit-content !important;
    max-width: 100% !important;
    margin: 0 !important;
}}
[class*="st-key-evidence_btn_"] .stButton {{
    width: fit-content !important;
}}

/* Adding `[kind="secondary"]` to the selector bumps specificity from
   (0,1,1) to (0,2,1) so we beat Streamlit's emotion-cache class-based
   defaults. */
[class*="st-key-evidence_btn_"] button[kind="secondary"] {{
    background: var(--bg-surface) !important;
    border-style: solid !important;
    border-width: 1px !important;
    border-color: var(--border-color) !important;
    color: var(--accent-purple) !important;
    font-size: 11px !important;
    font-weight: 400 !important;
    padding: 4px 10px !important;
    min-height: auto !important;
    height: auto !important;
    width: auto !important;
    min-width: auto !important;
    border-radius: 20px !important;
    line-height: 1.4 !important;
    box-shadow: none !important;
    transition: border-color 0.15s ease, background 0.15s ease !important;
    font-family: inherit !important;
    display: inline-flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    text-align: left !important;
    gap: 5px !important;
}}
[class*="st-key-evidence_btn_"] button[kind="secondary"]:hover {{
    border-color: var(--accent-purple) !important;
    background: var(--bg-card) !important;
}}
/* The label text inside the button lives in a stMarkdownContainer wrapping
   a <p>. Override Streamlit's default centered + bold treatment at every
   level to win specificity. */
[class*="st-key-evidence_btn_"] button[kind="secondary"] div[data-testid="stMarkdownContainer"] {{
    text-align: left !important;
    width: auto !important;
}}
[class*="st-key-evidence_btn_"] button[kind="secondary"] p {{
    font-size: 11px !important;
    font-weight: 400 !important;
    color: var(--accent-purple) !important;
    margin: 0 !important;
    text-align: left !important;
    line-height: 1.4 !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )

    # === ADD FOOTER ===
    from ui.components.footer import render_footer

    render_footer()
