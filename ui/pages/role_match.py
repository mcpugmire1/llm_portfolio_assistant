"""
Role Match Page

Paste a job description and see how Matt's experience maps to the requirements.
Three-step pipeline: extract requirements → retrieve stories → assess match.

Architecture: See ADR 016 and services/jd_assessor.py
"""

import html
import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import urlencode

import streamlit as st

from config.debug import DEBUG
from scripts.utils import slugify
from services.query_logger import (
    is_bot,
    log_role_match_assessment,
    log_role_match_gate_rejection,
)
from services.role_match_summary import build_discussion_points, compute_summary_counts
from ui.components.action_buttons import (
    get_action_buttons_css,
    get_action_buttons_html,
    render_action_button_handlers,
)
from ui.components.how_i_built_dialog import render_how_i_built_dialog
from ui.components.story_detail import render_story_detail
from ui.components.thinking_indicator import render_thinking_indicator
from ui.components.why_agy_dialog import render_why_agy_dialog
from ui.image_assets import AGY_AVATAR_64_B64

logger = logging.getLogger(__name__)


# =============================================================================
# MATTGPT-240: Rejection contract (gate + failure branch)
# =============================================================================

_JD_SHAPE_TERMS = (
    "responsibilities",
    "requirements",
    "experience",
    "years",
    "qualifications",
    "job",
    "role",
    "position",
    "skills",
    "candidate",
    "salary",
    "compensation",
    "benefits",
    "apply",
    "reporting to",
)

# Word-boundary matcher (pins the "casserole should not match role" test).
# "reporting to" is a two-word phrase; \b boundaries wrap the whole
# alternation so `\breporting to\b` matches the phrase cleanly.
_JD_SHAPE_RE = re.compile(r"\b(?:" + "|".join(_JD_SHAPE_TERMS) + r")\b", re.IGNORECASE)

# String comparison against e.__class__.__name__ keeps role_match.py free
# of an openai import. APIError deliberately excluded -- it's the base
# class for many OpenAI exceptions including BadRequestError, so a bare
# APIError may carry a non-transient fault. InternalServerError is a
# sibling of RateLimitError (both APIStatusError subclasses in
# openai/_exceptions.py) and is 5xx-transient, so it belongs here even
# though the shared APIStatusError base is not name-comparable to a
# single retryable/not-retryable outcome.
_RETRYABLE_ERROR_CLASSES = frozenset(
    {
        "RateLimitError",
        "APIConnectionError",
        "APITimeoutError",
        "InternalServerError",
    }
)

# Retryable copy matches -230's canonical form at explore_stories.py:397
# (colon, not em dash). Not-retryable matches app.py:288's startup-error
# pattern ("has been logged").
_RETRYABLE_MSG = "🐾 I need a quick breather: please try again in a moment!"
_NOT_RETRYABLE_MSG = "🐾 Something broke on my end. The issue has been logged."
_GATE_REJECT_MSG = (
    "🐾 I couldn't find a job description here. I look for "
    "responsibilities, requirements, or qualifications."
)


def _looks_like_jd(text: str) -> bool:
    """JD gate. Every input must match at least one JD-shape term on a
    word boundary. Length does not bypass the shape check -- a 500-word
    recipe rejects the same as a 20-word one. Word-boundary matching
    means substrings (e.g., "role" inside "casserole") do not pass."""
    return _JD_SHAPE_RE.search(text) is not None


def _is_retryable_error(e: Exception) -> bool:
    """Classify an OpenAI exception for the UI's two-state failure copy."""
    return e.__class__.__name__ in _RETRYABLE_ERROR_CLASSES


def _build_role_match_log_kwargs(extraction: dict, results: list[dict]) -> dict:
    """MATTGPT-247: build the kwargs for a successful-run
    `log_role_match_assessment` call.

    Extracted from the inline counting logic in the submit branch so
    the arithmetic invariant (`strong + partial + gap + unassessed
    == required + preferred`) can be tested without a Streamlit
    fixture. The extraction is itself the correctness fix -- the
    inline code hardcoded per-status `sum()` calls that structurally
    omitted `unassessed_count`, so partial-outage rows have been
    understating the total since Cycle 2 shipped.

    Derives all four status counts (strong/partial/gap/unassessed)
    and both category totals (required/preferred) from a single
    `compute_summary_counts(results)` pass, so the invariant holds
    by construction as long as every status is forwarded to the log
    kwargs. Test 8 in test_query_logger.py pins that forwarding."""
    counts = compute_summary_counts(results)
    r = counts["required"]
    p = counts["preferred"]
    return {
        "role_title": extraction.get("role_title") or "",
        "company": extraction.get("company") or "",
        "jd_format": extraction.get("jd_format") or "",
        "required_count": sum(r.values()),
        "preferred_count": sum(p.values()),
        "strong_count": r["strong"] + p["strong"],
        "partial_count": r["partial"] + p["partial"],
        "gap_count": r["gap"] + p["gap"],
        "unassessed_count": r["unassessed"] + p["unassessed"],
        "failure_type": "ok",
        # Per-category counts (added post-086): all twelve derive from
        # the same `compute_summary_counts(results)` pass so the split
        # invariant (combined == required + preferred per status) holds
        # by construction. Recruiter analytics filter on the Sheet's
        # per-category columns to distinguish required-strong from
        # preferred-strong -- the distinction fit assessment actually
        # turns on.
        "required_strong_count": r["strong"],
        "required_partial_count": r["partial"],
        "required_gap_count": r["gap"],
        "required_unassessed_count": r["unassessed"],
        "preferred_strong_count": p["strong"],
        "preferred_partial_count": p["partial"],
        "preferred_gap_count": p["gap"],
        "preferred_unassessed_count": p["unassessed"],
    }


def _log_role_match_success(result_payload: dict) -> None:
    """MATTGPT-247: extracted wiring for the success-path Sheet write.

    Called from the submit branch when `role_match_result` is present
    in session state. Checks the bot filter (parallel to
    `_handle_assessment_error`'s bot handling), builds the log kwargs
    via `_build_role_match_log_kwargs`, and forwards to
    `log_role_match_assessment`.

    Extracted so the wiring itself is unit-testable rather than being
    an inline block inside the submit branch that requires a full
    Streamlit fixture to exercise.

    MATTGPT-247: the is_bot skip emits a WARNING so a bot-filtered
    skip is distinguishable from a Sheet-write failure. The three
    silent-skip sites in this flow (is_bot here, `get_sheet() returns
    None` in _append_row, `except Exception` in _append_row) each
    have their own log phrase so a missing Sheet row can be
    diagnosed from terminal output in one test cycle."""
    if is_bot():
        logger.warning("[role_match] Sheet write skipped: is_bot() returned True")
        return
    extraction = result_payload.get("extraction") or {}
    results = result_payload.get("results") or []
    log_role_match_assessment(**_build_role_match_log_kwargs(extraction, results))


def _handle_assessment_error(e: Exception) -> str:
    """Log the failure with error class name, write a Sheet row via
    log_role_match_assessment with failure_type='retrieval_failed' and
    all counts zero (no requirements were assessed), and return the
    UI-facing message. Never leaks str(e) into the returned message
    (that was the -240 defect).

    MATTGPT-247: the Sheet write is bot-gated at the call site, parallel
    to the success path. Sits outside the assessment try/except, so a
    logging failure can't interfere with the assessment result. Uses
    the module-scope import of log_role_match_assessment / is_bot so
    the tests can patch at role_match's namespace."""
    err_class = e.__class__.__name__
    logger.warning(
        "role_match assessment failure [%s]: %s", err_class, e, exc_info=True
    )
    if not is_bot():
        log_role_match_assessment(
            role_title="",
            company="",
            jd_format="",
            required_count=0,
            preferred_count=0,
            strong_count=0,
            partial_count=0,
            gap_count=0,
            unassessed_count=0,
            failure_type="retrieval_failed",
            required_strong_count=0,
            required_partial_count=0,
            required_gap_count=0,
            required_unassessed_count=0,
            preferred_strong_count=0,
            preferred_partial_count=0,
            preferred_gap_count=0,
            preferred_unassessed_count=0,
        )
    return _RETRYABLE_MSG if _is_retryable_error(e) else _NOT_RETRYABLE_MSG


# Word-count floor below which we do not send text to the LLM. The extractor
# needs enough surface area to produce a useful requirement list; below this
# it consistently returns near-empty results that read as failed assessments.
# Enforced in _handle_submit_click as a gate rejection so the visitor gets
# the same banner treatment as a wrong-shape rejection -- from their side,
# a 25-word paste and a recipe are the same problem.
_MIN_JD_WORDS = 30


def _debug_print_click_to_render(total_ms: float, n_reqs: int) -> None:
    """Click-to-render timing emit for Role Match.

    Green will print `[role_match] total_ms=<float:.1f> n_reqs=<int>` when
    DEBUG=True and be a no-op when False. The number captures the full
    submit-branch + _render_results_panel span, so it ALWAYS exceeds
    extraction_ms + fan_out_ms; the delta is the Streamlit render-tree-build
    cost and any small pre/post overhead. Browser paint is on top of that
    and out of scope for a Python-side timer.

    Extracted so it can be unit-tested with capsys under a plain patch of
    the DEBUG flag on ui.pages.role_match, without needing a Streamlit
    runtime. The wiring around _render_results_panel is exercised
    end-to-end by manual runs and BDD.
    """
    if DEBUG:
        print(f"[role_match] total_ms={total_ms:.1f} n_reqs={n_reqs}")


def _consume_assessment_in_progress_flag() -> bool:
    """MATTGPT-245: read AND clear the assessment-in-progress flag in
    one step. Called on each render pass before Clear + Submit render
    so they receive the flag value once and it does not leak to
    subsequent reruns.

    Returns True on the render pass immediately after
    _handle_submit_click fired for a passing gate (the pass that
    also runs the LLM); False on all other passes.

    Must be .pop, not .get -- if the flag persists across reruns,
    Clear + Submit stay disabled forever after the first assessment."""
    return st.session_state.pop("role_match_assessment_in_progress", False)


def _handle_submit_click() -> None:
    """form_submit_button on_click callback. Runs BEFORE Streamlit reruns
    the script, so any session_state changes are visible when input_col's
    banner code reads them on the same pass. This is the reliable ordering
    fix -- a prior st.rerun() from inside the submit handler ran on the
    same pass where input_col had already rendered without the banner,
    forcing a second click to see the rejection.

    Also paired with st.form so the textarea value commits atomically with
    the submit click. Without the form, uncommitted textarea content let
    the first click consume the widget commit without registering as a
    submit -- same two-click failure surfaced from a different direction.

    Handles the gate path only. The LLM path stays in main script flow so
    the loading indicator renders correctly (callbacks cannot render UI).
    Main script's submit branch guards on role_match_gate_error so the LLM
    path skips when the gate rejects.

    Empty text is a no-op: the textarea already carries the "Paste a job
    description below" label, so a rejection banner saying the same thing
    would be redundant."""
    jd_text = st.session_state.get("role_match_jd_input") or ""
    if not jd_text.strip():
        return
    words = len(jd_text.split())
    looks_like = _looks_like_jd(jd_text)
    if words < _MIN_JD_WORDS or not looks_like:
        logger.warning(
            "role_match gate: rejected non-JD input (words=%d, looks_like_jd=%s)",
            words,
            looks_like,
        )
        # MATTGPT-247: Sheet write for the gate-rejected event. Bot-gated
        # at the call site (parallel to the two other role_match write
        # paths); no unit-test coverage on this call site. Manual check
        # for Green: paste a non-JD, confirm the Sheet row lands with
        # Event Type='role_match_gate_rejection' and Failure Type='gate_rejected'.
        if not is_bot():
            log_role_match_gate_rejection()
        for _k in (
            "role_match_result",
            "role_match_matched_jd",
            "role_match_active_evidence",
            "role_match_error",
        ):
            st.session_state.pop(_k, None)
        st.session_state["role_match_gate_error"] = _GATE_REJECT_MSG
        # Persist the raw paste so the textarea restores on
        # navigation-return, matching the LLM-success path. Without
        # this, a rejected visitor returns to a rejection banner over
        # an empty textarea -- same inconsistency the LLM-success
        # jd_persisted write prevents for results. Same variable name
        # (jd_text) as the LLM path so the two persist sites are
        # trivially comparable.
        st.session_state["role_match_jd_persisted"] = jd_text
    else:
        # Gate passes -- clear any prior gate rejection so a stale banner
        # doesn't linger over a fresh valid submission.
        st.session_state.pop("role_match_gate_error", None)
        # MATTGPT-245: set the assessment-in-progress flag so the render
        # pass that follows (same rerun as this callback) renders Clear
        # and Submit with disabled=True. Cleared by
        # _consume_assessment_in_progress_flag on read so it fires once,
        # on the render pass that also runs the LLM.
        st.session_state["role_match_assessment_in_progress"] = True


_HEADER_HTML = f"""
<div class="conversation-header">
    <div class="conversation-header-content">
        <div style="position: relative; display: inline-block; flex-shrink: 0;">
            <img class="conversation-agy-avatar" src="{AGY_AVATAR_64_B64}" width="64" height="64" style="width: 64px; height: 64px; border-radius: 50%; border: 3px solid white !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;" alt="Agy"/>
            <span class="why-agy-badge--header" id="why-agy-badge-role-match">i</span>
        </div>
        <div class="conversation-header-text">
            <h1>Role Match</h1>
            <p>Agy shows where Matt fits your role, and where he doesn't.</p>
        </div>
    </div>
</div>
"""

# =============================================================================
# RESULTS RENDERING HELPERS
# =============================================================================
# Pure presentation — given a result dict from services.jd_assessor.run_assessment,
# render the recruiter view (status icons, evidence chips, gap explanations).
# Phase 2: recruiter view only — no fit score / recommendation / private section.

_STATUS_ICON = {"strong": "✓", "partial": "~", "gap": "✗", "unassessed": "⋯"}

# MATTGPT-248: statuses the render sites accept without coercion. Anything
# else (missing key, unknown value) coerces to "unassessed" via
# `_normalize_row_status` and logs a warning naming the offending value.
# Matches services.role_match_summary._ASSESSED_STATUSES + ("unassessed",)
# so the render layer and the count layer stay word-identical.
_KNOWN_MATCH_STATUSES = ("strong", "partial", "gap", "unassessed")

# MATTGPT-248: per-status treatment maps. Three statuses are verdicts and
# render as a white glyph on a saturated fill; `unassessed` is deliberately
# quieter -- --text-secondary on --pill-bg -- because it is an absence of
# information rather than a verdict. --success-color is defined in
# global_styles.py; --warning-color/--error-color are not, so the hex
# fallbacks carry those two (same note as _render_results_panel).
_STATUS_ORDER = ("strong", "partial", "gap", "unassessed")

_STATUS_LABEL = {
    "strong": "Strong match",
    "partial": "Partial",
    "gap": "Gap",
    "unassessed": "Unassessed",
}

_STATUS_BADGE_STYLE = {
    "strong": ("var(--success-color,#10B981)", "white"),
    "partial": ("var(--warning-color,#F59E0B)", "white"),
    "gap": ("var(--error-color,#EF4444)", "white"),
    "unassessed": ("var(--pill-bg,#F3F4F6)", "var(--text-secondary,#6B7280)"),
}

_STATUS_TEXT_COLOR = {
    "strong": "var(--success-color,#10B981)",
    "partial": "var(--warning-color,#F59E0B)",
    "gap": "var(--error-color,#EF4444)",
    "unassessed": "var(--text-secondary,#6B7280)",
}


def _normalize_row_status(row: dict) -> str:
    """MATTGPT-248: coerce a row's match_status to one of
    strong/partial/gap/unassessed. A missing key or unknown value
    coerces to 'unassessed' and logs a warning naming the offending
    value so the producer bug is diagnosable. The row still renders
    (with the unassessed badge) and still counts.

    The developer-facing log phrase is 'malformed row', distinct from
    Cycle 2's caught-exception log wording, so the two producer-side
    causes are grep-distinguishable.
    """
    status = row.get("match_status")
    if status in _KNOWN_MATCH_STATUSES:
        return status
    logger.warning(
        "role_match malformed row: match_status %r not in %r; "
        "coercing to 'unassessed'. Requirement: %r",
        status,
        _KNOWN_MATCH_STATUSES,
        (row.get("requirement") or "")[:60],
    )
    return "unassessed"


def _normalize_row_category(row: dict) -> str:
    """MATTGPT-248: coerce a row's category to 'required' or 'preferred'.
    Any other value coerces to 'required' and logs a warning naming
    the offending value. Matches
    services.role_match_summary.compute_summary_counts's category
    coercion so the count layer and the rendered rows agree on both
    axes.
    """
    cat = row.get("category")
    if cat in ("required", "preferred"):
        return cat
    logger.warning(
        "role_match malformed row: category %r not in "
        "('required', 'preferred'); coercing to 'required'. Requirement: %r",
        cat,
        (row.get("requirement") or "")[:60],
    )
    return "required"


def _owes_explanation(status: str) -> bool:
    """MATTGPT-248 Cycle 1 follow-up: the render-gate rule -- anything
    short of a strong match owes the reader an explanation. Consumed
    at three render sites (`_render_requirement_card` for the panel,
    `_section` in `_build_share_text`, `_render_section` in
    `_build_export_html`) so the rule lives in one place and can't
    drift the way the literal `status in ('partial', 'gap')` tuple
    did once already.

    Expects a status already normalized via `_normalize_row_status`.
    Callers pass the coerced value; this predicate does not re-coerce."""
    return status != "strong"


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
    status = _normalize_row_status(result)
    icon = _STATUS_ICON[status]
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
                    f" Profile · {relevance}"
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
                                    # Log chip OPEN only (not close).
                                    # The close path (pop above) has no log call.
                                    from services.query_logger import (
                                        is_bot,
                                        log_role_match_chip_click,
                                    )

                                    if not is_bot():
                                        log_role_match_chip_click(
                                            story_title=title_text,
                                            client=client,
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
        if _owes_explanation(status) and gap_text:
            st.markdown(
                f'<div class="role-match-gap-text">{html.escape(gap_text)}</div>',
                unsafe_allow_html=True,
            )


def _count_fragments(counts: dict) -> list[str]:
    """MATTGPT-248: the single source of truth for count-line wording.

    Returns plain-text fragments in fixed status order, omitting any
    status whose count is zero:

        ["16 ✓ strong", "2 ~ partial"]

    Every surface builds its count line from these fragments and owns
    only its joiner and its decoration. That is what makes the three
    surfaces word-identical -- the words live in exactly one place, so
    they cannot drift the way _count_spans and _ex_count_line did.
    """
    return [
        f"{counts[status]} {_STATUS_ICON[status]} {status}"
        for status in _STATUS_ORDER
        if counts.get(status, 0) > 0
    ]


def _count_spans(counts: dict) -> str:
    """MATTGPT-248: screen count line as colored HTML spans.

    Promoted from a nested closure in _render_results_panel to module
    scope so the parity tests can compare its fragments against the
    off-screen builder's. Style constants inlined rather than closed over.

    The ,&nbsp; joiner is screen-only, matching the export's ", " on punctuation
    while keeping the space non-breaking. Off-screen surfaces read _count_fragments
    directly so no HTML entity reaches a plain-text surface.


    """
    parts = [
        f'<span class="count-{status}" '
        f'style="color:{_STATUS_TEXT_COLOR[status]};font-weight:600;">'
        f"{counts[status]} {_STATUS_ICON[status]} {status}</span>"
        for status in _STATUS_ORDER
        if counts.get(status, 0) > 0
    ]
    return ",&nbsp;".join(parts)


def _ex_count_line(label: str, counts: dict) -> str:
    """MATTGPT-248: count line for both off-screen surfaces, plain text.

    Promoted to module scope from a nested closure in _build_export_html
    so _build_share_text can share it. Export and report take identical
    count copy because neither reader can act on it.
    """
    fragments = _count_fragments(counts)
    return f"{label}: {', '.join(fragments)}" if fragments else ""


def _dp_lines(points: list[dict], *, surface: str) -> list[str]:
    """MATTGPT-248: discussion-points section for one surface.

    Returns [] on empty input; callers skip the section header when the
    return is empty. That is what makes branch 4 (all rows unassessed,
    so no honest discussion points exist) safe on all three surfaces
    without three separate empty guards.

    Three branches because the three surfaces genuinely differ: screen
    carries inline styles, export relies on its own stylesheet, report
    is plain text. One function keeps them from drifting apart.
    """
    if not points:
        return []
    lines = []
    for pt in points:
        text = pt["text"]
        label = pt.get("label_type") or ""
        if surface == "share":
            prefix = f"{label}: " if label and not pt.get("is_zero_case") else ""
            lines.append(f"   {prefix}{text}")
        elif surface == "export":
            esc = html.escape(text)
            if pt.get("is_zero_case"):
                lines.append(f"<li>{esc}</li>")
            elif pt.get("is_overflow_indicator"):
                lines.append(f"<li><em>{esc}</em></li>")
            else:
                lines.append(f"<li><strong>{html.escape(label)}:</strong> {esc}</li>")
        else:
            esc = html.escape(text)
            if pt.get("is_zero_case"):
                lines.append(
                    '<li style="list-style:none;padding:2px 0;'
                    f'color:var(--success-color);">{esc}</li>'
                )
            elif pt.get("is_overflow_indicator"):
                lines.append(
                    '<li style="list-style:none;padding:2px 0;'
                    f'color:var(--text-secondary);font-style:italic;">{esc}</li>'
                )
            else:
                color = (
                    _STATUS_TEXT_COLOR["gap"]
                    if "Gap" in label
                    else _STATUS_TEXT_COLOR["partial"]
                )
                lines.append(
                    '<li style="list-style:none;padding:2px 0;">'
                    f'<span style="font-size:11px;font-weight:700;'
                    f'color:{color};margin-right:6px;">'
                    f"{html.escape(label)}</span>{esc}</li>"
                )
    return lines


def _legend_entries(*, surface: str) -> list[str]:
    """MATTGPT-248: ordered legend entries for one surface.

    Order is fixed: strong, partial, gap, unassessed, then the two
    evidence types. Static by construction -- no `results` argument,
    because a legend that appeared and disappeared with assessment
    content would be a second thing for the reader to interpret.

    The 🔗 icon is the only per-surface difference. It marks a clickable
    chip, and nothing is clickable in a PDF or a pasted email, so the
    off-screen surfaces name the evidence type in words instead.
    """
    entries = []
    for status in _STATUS_ORDER:
        label = _STATUS_LABEL[status]
        if surface == "share":
            entries.append(f"{_STATUS_ICON[status]} {label}")
            continue
        fill, glyph_color = _STATUS_BADGE_STYLE[status]
        entries.append(
            '<div style="display:inline-flex;align-items:center;gap:6px;">'
            '<span style="display:inline-flex;align-items:center;'
            "justify-content:center;width:16px;height:16px;border-radius:50%;"
            f"background:{fill};color:{glyph_color};font-size:10px;"
            f'font-weight:700;line-height:1;">{_STATUS_ICON[status]}</span>'
            f"{label}</div>"
        )

    if surface == "share":
        entries.append("Project evidence: a story from the portfolio")
        entries.append("Profile: background from Matt's profile")
        return entries

    entries.append(
        '<span style="width:1px;height:14px;background:var(--border-color);'
        'display:inline-block;"></span>'
    )
    if surface == "screen":
        entries.append(
            '<div style="display:inline-flex;align-items:center;gap:6px;">'
            "🔗 = project evidence</div>"
        )
        entries.append(
            '<div style="display:inline-flex;align-items:center;gap:6px;">'
            '<span style="width:8px;height:8px;border-radius:50%;'
            'background:var(--text-secondary);display:inline-block;"></span>'
            " = profile</div>"
        )
    else:
        entries.append(
            '<div style="display:inline-flex;align-items:center;gap:6px;">'
            "Project evidence: a story from the portfolio</div>"
        )
        entries.append(
            '<div style="display:inline-flex;align-items:center;gap:6px;">'
            "Profile: background from Matt's profile</div>"
        )
    return entries


def _incomplete_notice_text(counts: dict, total: int, *, surface: str) -> str | None:
    """MATTGPT-248: format the partial-failure notice for a given surface.

    Returns None when no unassessed rows are present (no notice to render).
    Otherwise returns the surface-appropriate copy. Per the parity rule,
    facts are identical across surfaces; the action clause appears only
    on the screen surface, where "try again" is a real affordance. The
    PDF and clipboard artifacts drop the action clause because the reader
    cannot retry from those surfaces.

    Callers pass surface="print" for both _build_export_html and
    _build_share_text since the copy is the same for those two surfaces.

    N is the combined unassessed count across required + preferred.
    """
    required_unassessed = counts.get("required", {}).get("unassessed", 0)
    preferred_unassessed = counts.get("preferred", {}).get("unassessed", 0)
    n = required_unassessed + preferred_unassessed
    if n <= 0:
        return None
    # Cycle 2 follow-up: "N of these N requirements" reads awkward when
    # n == total (a total outage); "any of these N requirements" is
    # cleaner. Keep the subset form when n < total because the two
    # numbers there carry different information (what failed vs how
    # much there was).
    if n == total:
        body = f"I couldn't get to any of these {total} requirements."
    else:
        body = f"I couldn't get to {n} of these {total} requirements."
    # Cycle 2 follow-up: paw appears on screen only. In the export PDF
    # the codepoint falls back to a system font with no guarantee of
    # what glyph the reader gets (observed clipped / substituted at
    # the header size during a manual Mode 2 test). Agy's voice
    # survives in the first-person copy; the paw is decoration that
    # renders reliably only on screen. The export legend already
    # carries the status glyphs.
    if surface == "screen":
        return f"🐾 {body} Try again for the full picture."
    return body


# =============================================================================
# MATTGPT-089: Location & Availability block
# =============================================================================
# Fixed-content four-cell strip rendered above SUMMARY on all three surfaces
# (screen panel, share text, export html). Facts only, no LLM, no JD
# comparison, no verdict badges. Labels live here (design vocabulary);
# values + sublines live in data/matt_profile.json under the "logistics" key.

_LOCATION_HEADER = "Location & Availability"

# Shared CSS: one source, two consumers. Export template splices it
# into its <style> block; screen render injects it via st.markdown once
# per panel. Same parity discipline as the count builders -- edit here,
# both surfaces update.
#
# `var(--token, #hex)` follows the _STATUS_BADGE_STYLE pattern: screen
# resolves to the CSS variable (light + dark palettes in
# global_styles.py), export falls back to the literal since the
# standalone HTML has no :root. Do not switch to bare hex -- that
# breaks dark mode on the panel.
_LOCATION_BLOCK_CSS = """
.loc-block { margin-bottom: 24px; padding: 16px; background: var(--bg-surface, #F9FAFB); border: 1px solid var(--border-color, #E5E7EB); border-radius: 8px; }
.loc-block .section-title { color: var(--accent-purple, #8B5CF6); font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 12px 0; }
.loc-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.loc-cell { display: flex; flex-direction: column; gap: 4px; }
.loc-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary, #6B7280); font-weight: 600; }
.loc-value { font-size: 14px; font-weight: 700; color: var(--text-primary, #1F2937); }
.loc-subline { font-size: 12px; color: var(--text-secondary, #6B7280); }
@media (max-width: 600px) { .loc-grid { grid-template-columns: repeat(2, 1fr); } }
"""

# Cell order pinned here; labels displayed to visitors. Field keys match
# data/matt_profile.json["logistics"] structure.
_LOCATION_CELL_ORDER = (
    ("location", "Location"),
    ("work_model", "Work model"),
    ("availability", "Availability"),
    ("authorization", "Authorization"),
)


def _load_matt_profile_dict() -> dict:
    """Load matt_profile.json as a dict. Empty dict on failure so the
    render surfaces degrade gracefully (no block rendered, no crash).
    Distinct from services.jd_assessor.load_matt_profile which returns
    a formatted string for the assessment prompt."""
    profile_path = Path(__file__).parent.parent.parent / "data" / "matt_profile.json"
    try:
        with open(profile_path) as f:
            return json.load(f)
    except Exception:
        return {}


def _iter_location_cells(profile: dict) -> list[tuple[str, str, str]]:
    """Return [(label, value, subline), ...] for populated logistics
    cells only, in fixed order. Cells whose field is absent from the
    profile's logistics dict, or whose value is empty/missing, are
    omitted entirely -- MATTGPT-089's omit-cleanly contract, pinned
    by test_location_block_omits_cell_when_field_missing_from_profile.
    A cell that rendered label-only with an empty value would be the
    'blank box' failure mode."""
    logistics = (profile or {}).get("logistics") or {}
    cells: list[tuple[str, str, str]] = []
    for field_key, label in _LOCATION_CELL_ORDER:
        cell_data = logistics.get(field_key)
        if not cell_data:
            continue
        value = str(cell_data.get("value", "")).strip()
        subline = str(cell_data.get("subline", "")).strip()
        if not value:
            continue
        cells.append((label, value, subline))
    return cells


def _render_location_block_share_text(cells: list[tuple[str, str, str]]) -> str:
    """Plain-text Location & Availability block for the share
    surface. Returns empty string when no cells to render, so
    callers can concatenate unconditionally without producing
    stray blank lines."""
    if not cells:
        return ""
    lines = [_LOCATION_HEADER]
    for label, value, subline in cells:
        lines.append(f"{label}: {value}")
        if subline:
            lines.append(f"   {subline}")
    return "\n".join(lines)


def _render_pending_row_html(requirement_text: str) -> str:
    """MATTGPT-245 phase two: pending-state HTML for one requirement
    slot. Each per-requirement st.empty() is seeded with this HTML
    before the fan-out starts; the on_row callback overwrites the
    slot with the finished-row HTML as each assessment completes.

    Emits a hollow purple ring (CSS-styled via .role-match-pending-ring
    to match the resolved status-badge footprint, so nothing shifts
    when the ring resolves to a badge) beside the requirement text.
    Deliberately omits .role-match-status-badge, evidence chips, and
    the U+22EF ellipsis glyph -- pending must be visually distinct
    from the unassessed terminal state (tests 8a and 8b guard this)."""
    return (
        '<div class="role-match-pending-row">'
        '<span class="role-match-pending-ring"></span>'
        f'<span class="role-match-pending-text">{html.escape(requirement_text)}</span>'
        "</div>"
    )


def _render_location_block_html(cells: list[tuple[str, str, str]]) -> str:
    """HTML Location & Availability block for both the export
    surface and the screen panel. Header ampersand is html.escape'd
    per the convention pinned by
    test_export_html_escapes_ampersand. Returns empty string when no
    cells to render.

    Screen and export share this output plus _LOCATION_BLOCK_CSS.
    Screen injects the CSS via st.markdown once per panel; export
    splices it into its <style> block. The two surfaces stay in
    sync by construction, not by memory.

    Subline div is gated on subline being non-empty -- an empty
    `<div class="loc-subline"></div>` produces phantom vertical
    space on cells with values but no sublines. Same omit-cleanly
    shape as the missing-cell contract, one level down."""
    if not cells:
        return ""
    header_escaped = html.escape(_LOCATION_HEADER)
    cell_divs = []
    for label, value, subline in cells:
        subline_html = (
            f'<div class="loc-subline">{html.escape(subline)}</div>' if subline else ""
        )
        cell_divs.append(
            '<div class="loc-cell">'
            f'<div class="loc-label">{html.escape(label)}</div>'
            f'<div class="loc-value">{html.escape(value)}</div>'
            f"{subline_html}"
            "</div>"
        )
    return (
        '<div class="loc-block">'
        f'<h2 class="section-title">{header_escaped}</h2>'
        '<div class="loc-grid">'
        f'{"".join(cell_divs)}'
        "</div>"
        "</div>"
    )


def _build_share_text(result_payload: dict, profile: dict | None = None) -> str:
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
    # MATTGPT-248: category coercion aligned with
    # services.role_match_summary.compute_summary_counts so a row with
    # an unrecognized category falls into 'required' rather than being
    # silently dropped from both sections. Also normalizes match_status
    # so each row carries a known value before the render loop touches
    # it -- the ? sentinel fallback is retired because it has no legend
    # entry on any surface.
    required: list[dict] = []
    preferred: list[dict] = []
    for r in results:
        if _normalize_row_category(r) == "required":
            required.append(r)
        else:
            preferred.append(r)

    lines = [f"Matt Pugmire: {role} fit assessment"]
    if company:
        lines.append(company)
    lines.append("")
    # MATTGPT-248: the report had no summary, so a forwarded assessment
    # opened on the first requirement and gave the reader no top-line
    # read. Counts route through _ex_count_line so the wording is
    # identical to the export's.
    _counts = compute_summary_counts(results)
    _points = build_discussion_points(results)
    _notice = _incomplete_notice_text(_counts, len(results), surface="print")
    if _notice:
        lines.append(_notice)
        lines.append("")
    # MATTGPT-089: Location & Availability block above SUMMARY.
    # Fixed content, always renders (unless the profile is empty
    # and every cell is skipped). Parity with the export html
    # placement.
    _location_cells = _iter_location_cells(profile or _load_matt_profile_dict())
    _location_block = _render_location_block_share_text(_location_cells)
    if _location_block:
        lines.append(_location_block)
        lines.append("")
    _count_lines = [
        line
        for line in [
            _ex_count_line("Required", _counts["required"]),
            _ex_count_line("Preferred", _counts["preferred"]),
        ]
        if line
    ]
    if _count_lines:
        lines.append("SUMMARY")
        lines.append("  |  ".join(_count_lines))
        _dp = _dp_lines(_points, surface="share")
        if _dp:
            _dp_count = sum(
                1
                for p in _points
                if not p.get("is_overflow_indicator") and not p.get("is_zero_case")
            )
            lines.append(f"Discussion points ({_dp_count})")
            lines.extend(_dp)
        lines.append("")

    def _section(title: str, items: list[dict]) -> None:
        if not items:
            return
        lines.append(f"{title} ({len(items)})")
        for r in items:
            status = _normalize_row_status(r)
            icon = _STATUS_ICON[status]
            lines.append(f"{icon} {r.get('requirement', '')}")
            # MATTGPT-248: supporting evidence per non-gap row. The report
            # is the artifact most likely to be forwarded to a second
            # reader, and it was the one surface listing verdicts with no
            # proof behind them. Three-space indent matches the gap note
            # below so evidence reads as support for the requirement
            # rather than as a peer of it.
            if status in ("strong", "partial"):
                for ev in (r.get("evidence") or [])[:2]:
                    if ev.get("evidence_type") == "profile":
                        rel = (ev.get("relevance") or "").strip()
                        if rel:
                            lines.append(f"   Profile: {rel}")
                    else:
                        ev_title = ev.get("story_title") or "Untitled"
                        ev_client = ev.get("client") or ""
                        suffix = f" ({ev_client})" if ev_client else ""
                        lines.append(f"   Project evidence: {ev_title}{suffix}")

            if _owes_explanation(status):
                gap = (r.get("gap_explanation") or "").strip()
                if gap:
                    # Indent only, no "Gap:" prefix. The LLM's gap_explanation
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

    # MATTGPT-248: plain-text key. Same argument as the export legend,
    # sharper here: a pasted email has no styling at all, so the glyphs
    # are the only structure the second reader gets.
    lines.append("Key:")
    for _entry in _legend_entries(surface="share"):
        lines.append(f"  {_entry}")

    lines.append("")
    lines.append(f"Explore Matt's full portfolio: {portfolio_url}")

    return "\n".join(lines).rstrip() + "\n"


def _build_export_html(result_payload: dict, profile: dict | None = None) -> str:
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
    # MATTGPT-248: category coercion aligned with services layer so
    # a row with an unrecognized category renders under 'required'
    # rather than being silently dropped from both sections.
    required: list[dict] = []
    preferred: list[dict] = []
    for r in results:
        if _normalize_row_category(r) == "required":
            required.append(r)
        else:
            preferred.append(r)

    def _render_section(title: str, items: list[dict]) -> str:
        if not items:
            return ""
        rows = []
        rows.append(f'<h2 class="section-title">{title} ({len(items)})</h2>')
        for r in items:
            # MATTGPT-248: coerce status through _normalize_row_status so
            # malformed rows render with the unassessed badge (not a "?"
            # sentinel and not silently coerced to gap). Log fires from
            # the normalizer.
            status = _normalize_row_status(r)
            icon = _STATUS_ICON[status]
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
                            f'<div class="evidence profile"><strong>Profile:</strong> {relevance}</div>'
                        )
                    else:
                        title_text = html.escape(ev.get("story_title") or "Untitled")
                        client = html.escape(ev.get("client") or "")
                        client_str = f" ({client})" if client else ""
                        rows.append(
                            f'<div class="evidence">{title_text}{client_str}</div>'
                        )

            gap = (r.get("gap_explanation") or "").strip()
            if _owes_explanation(status) and gap:
                # Class is `gap-note`, not `gap`, to avoid a same-specificity
                # collision with `.status.gap` on the badge: the bare `.gap`
                # rule below carries margin/font-size/color that would leak
                # onto any element also named `gap`, including the gap-status
                # badge span. The badge modifier stays `.status.gap`;
                # the note-block gets its own name.
                rows.append(f'<div class="gap-note"><em>{html.escape(gap)}</em></div>')

        return "\n".join(rows)

    required_html = _render_section("Required Qualifications", required)
    preferred_html = _render_section("Preferred Qualifications", preferred)

    # Summary section — appears above requirements in the export
    _ex_counts = compute_summary_counts(results)
    _ex_points = build_discussion_points(results)
    _ex_rc = _ex_counts["required"]
    _ex_pc = _ex_counts["preferred"]

    _ex_count_lines = [
        line
        for line in [
            _ex_count_line("Required", _ex_rc),
            _ex_count_line("Preferred", _ex_pc),
        ]
        if line
    ]
    _ex_dp_count = sum(
        1
        for p in _ex_points
        if not p.get("is_overflow_indicator") and not p.get("is_zero_case")
    )
    _ex_dp_count = sum(
        1
        for p in _ex_points
        if not p.get("is_overflow_indicator") and not p.get("is_zero_case")
    )
    _ex_point_rows = _dp_lines(_ex_points, surface="export")
    _ex_dp_html = (
        f"<p><strong>Discussion points ({_ex_dp_count})</strong></p>"
        f'<ul>{"".join(_ex_point_rows)}</ul>'
        if _ex_point_rows
        else ""
    )
    _ex_notice = _incomplete_notice_text(_ex_counts, len(results), surface="print")
    _ex_notice_html = (
        f'<p class="incomplete-notice">{html.escape(_ex_notice)}</p>'
        if _ex_notice
        else ""
    )

    # MATTGPT-248: the export carried bare ✓ ~ ✗ glyphs with nothing
    # explaining them. A printed assessment has no hover, no tooltip,
    # and no page to scroll back to, so the key has to travel with it.
    legend_export_html = (
        '<div class="legend"><strong>Key:</strong>'
        + "".join(_legend_entries(surface="export"))
        + "</div>"
    )

    summary_export_html = (
        '<div class="summary-section">'
        '<h2 class="section-title">SUMMARY</h2>'
        + f'<p class="summary-counts">{"  |  ".join(_ex_count_lines)}</p>'
        + _ex_dp_html
        + "</div>"
    )

    # MATTGPT-089: Location & Availability block above SUMMARY.
    # Fixed content, always renders (unless the profile is empty
    # and every cell is skipped). Parity with the share text
    # placement.
    _location_cells = _iter_location_cells(profile or _load_matt_profile_dict())
    location_html = _render_location_block_html(_location_cells)

    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Role Match: {role}</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; max-width: 900px; margin: 0 auto; color: #1F2937; }}
                h1 {{ color: #1F2937; font-size: 24px; margin-bottom: 4px; }}
                .meta {{ color: #6B7280; font-size: 14px; margin-bottom: 24px; }}
                .section-title {{ color: #8B5CF6; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin: 24px 0 12px 0; }}
                .summary-section {{ margin-bottom: 24px; padding: 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; }}
                .summary-counts {{ font-size: 13px; color: #6B7280; margin: 0 0 8px 0; }}
                {_LOCATION_BLOCK_CSS}
                .legend {{ display: flex; flex-wrap: wrap; align-items: center; gap: 16px; padding: 10px 14px; border: 1px solid #E5E7EB; border-radius: 10px; margin-bottom: 14px; font-size: 11px; color: #6B7280; }}
                .incomplete-notice {{ font-size: 12px; color: #6B7280; margin: 0 0 8px 0; }}
                .req {{ display: flex; gap: 10px; align-items: center; margin: 0 0 4px 0; padding: 12px 0 0 0; }}
                .req-text {{ font-size: 14px; font-weight: 500; color: #1F2937; line-height: 1.45; margin: 0; padding: 0; }}
                /* Status badge: explicit margin/padding zero and line-height
                   lock so the badge sits identically across strong/partial/gap
                   regardless of how the inner glyph (✓ ~ ✗) renders in the
                   browser's print font. */
                .status {{ display: inline-flex; flex-shrink: 0; width: 22px; height: 22px; border-radius: 50%; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: white; line-height: 1; margin: 0; padding: 0; box-sizing: border-box; text-align: center; }}
                .status.strong {{ background: #10B981; }}
                .status.partial {{ background: #F59E0B; }}
                .status.gap {{ background: #EF4444; }}
                .evidence {{ margin-left: 32px; margin-top: 6px; padding: 6px 10px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; font-size: 12px; color: #1F2937; }}
                .evidence.profile {{ background: rgba(139, 92, 246, 0.08); border-color: rgba(139, 92, 246, 0.2); }}
                /* Note block for any status that owes an explanation
                   (currently partial and gap; unassessed once Cycle 2's
                   producer ships). Named `gap-note` (not `.gap`) so the
                   rule can't collide with `.status.gap` on the badge
                   span at same specificity and leak margin/font-size/
                   color onto the badge. The class name is a historical
                   scar from the original gap-only version, not a
                   status filter. */
                .gap-note {{ margin-left: 32px; margin-top: 6px; font-size: 12px; color: #6B7280; }}

            </style>
        </head>
        <body>
            <h1>Role Match: {role}</h1>
            <div class="meta">{header_meta}</div>
            {_ex_notice_html}
            {legend_export_html}
            {location_html}
            {summary_export_html}
            {required_html}
            {preferred_html}
        </body>
        </html>
    """


def _render_results_header(result_payload: dict, include_actions: bool = True) -> None:
    """Render the results header bar: extracted role title + action buttons.

    The header is a flex container with the role title on the left and the
    shared Helpful / Share / Export buttons on the right (per story_detail
    pattern). Buttons appear only when there is a result to act on.

    MATTGPT-245 phase two: `include_actions` gates the three action
    buttons (Helpful, Share, Export). The interleaved submit path calls
    this with include_actions=False during the pre-fanout render because
    (a) results is an empty placeholder at that point, so share/export
    would produce truncated output, and (b) clicking any of the three
    triggers a Streamlit rerun that abandons the running fan-out. Same
    guard shape as Clear/Submit/textarea. Post-rerun the stable render
    via _render_results_panel uses the default (include_actions=True)
    and the buttons behave normally.
    """
    extraction = result_payload.get("extraction") or {}
    role = html.escape(extraction.get("role_title") or "Untitled Role")
    company = html.escape(extraction.get("company") or "")

    company_html = (
        f'<div class="role-match-results-company">{company}</div>' if company else ""
    )

    if not include_actions:
        # Pre-fanout render: title only, no buttons, no handlers.
        # An accidental click on Share/Export/Helpful during the ~20s
        # fan-out would trigger a rerun that abandons the running
        # assessment and leaves the panel with half its rings unfilled.
        st.markdown(
            f"""
            <div class="role-match-results-header">
                <div class="role-match-results-title-section">
                    <div class="role-match-results-title">{role}</div>
                    {company_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Stable per-assessment id so the helpful-confirmed flag resets on a new
    # assessment. id() is stable for the lifetime of the dict in session_state.
    assessment_id = id(result_payload)
    confirmed_key = f"role_match_helpful_{assessment_id}"
    is_helpful_confirmed = st.session_state.get(confirmed_key) == "up"

    buttons_html = get_action_buttons_html(
        button_id_prefix="btn-role-match",
        is_helpful_confirmed=is_helpful_confirmed,
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
        context="role_match",
    )


def _build_legend_screen_html() -> str:
    """MATTGPT-245 phase two: legend markup as a pure string, no
    Streamlit calls. Extracted from _render_results_panel so the
    interleaved submit path (pre-fanout render) and the stable
    _render_results_panel (post-rerun render) share one source.

    IMPORTANT: inline styles are load-bearing (not class selectors).
    An earlier class-based version rendered stacked vertically because
    Streamlit's markdown parser broke the inline-flex layout. Inline
    styles bypass the parser entirely."""
    return (
        '<div class="role-match-legend" '
        'style="display:flex;flex-wrap:wrap;align-items:center;gap:16px;'
        "padding:10px 14px;background:var(--bg-card);"
        "border:1px solid var(--border-color);border-radius:10px;"
        'margin-bottom:14px;font-size:11px;color:var(--text-secondary);">'
        + "".join(_legend_entries(surface="screen"))
        + "</div>"
    )


def _build_summary_screen_html(result_payload: dict) -> str:
    """MATTGPT-245 phase two: SUMMARY block markup as a pure string,
    no Streamlit calls. Extracted from _render_results_panel so the
    interleaved submit path (post-fanout render) and the stable
    _render_results_panel share one source. Handles the same three
    inputs as the inline version: counts (via compute_summary_counts),
    incomplete notice, and discussion points."""
    results = result_payload.get("results") or []
    _counts = compute_summary_counts(results)
    _points = build_discussion_points(results)
    _rc = _counts["required"]
    _pc = _counts["preferred"]

    _req_spans = _count_spans(_rc)
    _pref_spans = _count_spans(_pc)
    _section_parts = []
    if _req_spans:
        _section_parts.append(f"Required:&nbsp;{_req_spans}")
    if _pref_spans:
        _section_parts.append(f"Preferred:&nbsp;{_pref_spans}")
    _counts_line = (
        '<div class="role-match-summary-counts"'
        ' style="font-size:13px;color:var(--text-secondary);margin:6px 0 10px 0;">'
        + "&nbsp;&nbsp;|&nbsp;&nbsp;".join(_section_parts)
        + "</div>"
    )

    _notice = _incomplete_notice_text(_counts, len(results), surface="screen")
    _notice_html = (
        f'<div style="font-size:12px;color:var(--text-secondary);'
        f'margin:0 0 8px 0;">{html.escape(_notice)}</div>'
        if _notice
        else ""
    )

    _dp_count = sum(
        1
        for p in _points
        if not p.get("is_overflow_indicator") and not p.get("is_zero_case")
    )
    _point_items = _dp_lines(_points, surface="screen")
    _dp_html = (
        f'<div style="font-size:12px;font-weight:600;'
        f'color:var(--text-secondary);margin:8px 0 4px 0;">'
        f"Discussion points ({_dp_count})</div>"
        f'<ul style="margin:0;padding:0;font-size:13px;'
        f'color:var(--text-primary);">{"".join(_point_items)}</ul>'
        if _point_items
        else ""
    )
    return (
        '<div class="role-match-summary"'
        ' style="background:var(--bg-card);border:1px solid var(--border-color);'
        'border-radius:10px;padding:12px 16px;margin-bottom:14px;">'
        '<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.08em;color:var(--text-secondary);margin-bottom:6px;">SUMMARY</div>'
        + _notice_html
        + _counts_line
        + _dp_html
        + "</div>"
    )


def _build_location_screen_html_with_style() -> str:
    """MATTGPT-245 phase two: Location & Availability block markup
    (with the shared _LOCATION_BLOCK_CSS style block prefix) as a
    pure string. Extracted so the interleaved submit path and the
    stable _render_results_panel share one source. Returns empty
    string when the profile has no logistics cells."""
    _location_cells = _iter_location_cells(_load_matt_profile_dict())
    _location_block_html = _render_location_block_html(_location_cells)
    return (
        f"<style>{_LOCATION_BLOCK_CSS}</style>{_location_block_html}"
        if _location_block_html
        else ""
    )


def _render_results_panel(result_payload: dict, stories: list[dict]) -> None:
    """Render the full results panel — required + preferred sections.

    Per-requirement rendering loop. Each requirement card is emitted as its
    own st.markdown call so that hidden Streamlit buttons (for chip click
    handling) and an inline render_story_detail call (for the expanded chip,
    if any) can be interleaved between cards. The Cards-view pattern from
    My Work — see ui/pages/explore_stories.py:2393-2487 — was the
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

    # MATTGPT-245 phase two: legend markup extracted into
    # _build_legend_screen_html so the interleaved submit path (pre-fanout
    # render) and this stable render share one source. Behavior identical
    # to the previous inline version.
    st.markdown(_build_legend_screen_html(), unsafe_allow_html=True)

    # MATTGPT-089: Location & Availability block above SUMMARY. Style +
    # block concatenated into the same st.markdown call as _summary_html
    # so total call count is unchanged (screen layout tuning depends on
    # it, per CLAUDE.md). Both extracted into helpers (MATTGPT-245 phase
    # two) so the interleaved submit path can share them.
    st.markdown(
        _build_location_screen_html_with_style()
        + _build_summary_screen_html(result_payload),
        unsafe_allow_html=True,
    )

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
                # Wrap in a keyed container so the CSS gap-restore
                # rule (.st-key-role_match_ev_* stVerticalBlock)
                # has a DOM element to match. render_story_detail
                # doesn't create its own wrapping container — it
                # renders directly into the parent context.
                with st.container(
                    key=f"role_match_ev_{active_evidence_key}",
                ):
                    render_story_detail(
                        evidence_stories[active_evidence_key],
                        f"role_match_ev_{active_evidence_key}",
                        stories,
                        show_actions=False,
                    )


_DEMO_JD_PATH = Path(__file__).parent.parent.parent / "data" / "demo_jd.txt"


def _load_demo_jd() -> str:
    return _DEMO_JD_PATH.read_text(encoding="utf-8").strip()


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

    if st.session_state.get("active_dialog") == "why_agy":
        render_why_agy_dialog()
        st.session_state.pop("active_dialog", None)
    elif st.session_state.get("active_dialog") == "how_i_built":
        render_how_i_built_dialog()
        st.session_state.pop("active_dialog", None)

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
    margin: -2rem 0 0 0;
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
    border-radius: 50% !important;
    border: 4px solid white !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

@media (min-width: 768px) {
    .conversation-agy-avatar {
        width: 120px !important;
        height: 120px !important;
    }
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
[class*="st-key-why_agy_role_match_trigger"] {
    display: none !important;
}

div[data-testid="stElementContainer"]:has([class*="st-key-why_agy_role_match_trigger"]) {
    display: none !important;
}
[class*="st-key-lock_icon"] {
    display: none !important;
}
/* Clear -- st.button styled as a text link (inline affordance, not a
   CTA). Serves every rejection state: gate, retryable failure, and
   not-retryable failure. Sits directly below the banner so the
   rejection message is read first and the affordance follows. */
[class*="st-key-role_match_clear"] button {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    min-height: 0 !important;
    height: auto !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    color: var(--text-secondary) !important;
    cursor: pointer !important;
}
[class*="st-key-role_match_clear"] button:hover {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    text-decoration: underline !important;
}
/* MATTGPT-245: the base rule above uses !important on color/cursor,
   which masks Streamlit's default disabled visual. Restore the
   affordance explicitly so the disabled state reads. */
[class*="st-key-role_match_clear"] button:disabled {
    opacity: 0.4 !important;
    cursor: not-allowed !important;
    text-decoration: none !important;
}

/* MATTGPT-240: shared banner treatment. Used by the gate rejection in
   the left column and by the assessment-failure copy in the right panel.
   Matches -230's "quick breather" left-stripe bubble in explore_stories.py:
   --banner-info-bg fill, 4px --accent-purple left stripe, rounded on the
   right (0 8px 8px 0), --banner-info-text for the message. Container key
   selector applies the stripe/fill to the whole st.container so any
   inline button (the gate branch's ✕ Clear and paste again) lands
   visually inside the banner region.
   Margin: 12px above so the banner is not attached to the heading
   preceding it; 0 below so it sits directly against the following
   element. Both branches read the same on-screen. */
[class*="st-key-role_match_banner"] {
    background: var(--banner-info-bg);
    border-left: 4px solid var(--accent-purple);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 12px 0 0;
}
.role-match-banner-msg {
    color: var(--banner-info-text);
    font-size: 14px;
    font-weight: 600;
    line-height: 1.5;
    margin-bottom: 10px;
}

/* Demo JD and post-result CTA — outlined buttons, footer-matched treatment.
   5% accent-purple fill gives substance; 8px radius and font-weight: 600
   match the footer pill. Hover lifts to 10% fill + accent border. */
[class*="st-key-role_match_demo_jd"] button,
[class*="st-key-role_match_followup_cta"] button {
    background: rgba(139, 92, 246, 0.05) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
[class*="st-key-role_match_demo_jd"] button:hover,
[class*="st-key-role_match_followup_cta"] button:hover {
    background: rgba(139, 92, 246, 0.06) !important;
    border-color: var(--accent-purple) !important;
}
</style>
""",
        unsafe_allow_html=True,
    )

    # =========================================================================
    # HEADER
    # =========================================================================
    st.markdown(_HEADER_HTML, unsafe_allow_html=True)
    if st.button("trigger", key="why_agy_role_match_trigger"):
        st.session_state["active_dialog"] = "why_agy"
        st.rerun()
    import streamlit.components.v1 as components  # noqa: PLC0415

    components.html(
        """
<script>
(function() {
    function wireBadge() {
        var parentDoc = window.parent.document;
        var badge = parentDoc.getElementById('why-agy-badge-role-match');
        var btn = parentDoc.querySelector('[class*="st-key-why_agy_role_match_trigger"] button');
        if (badge && btn && !badge.dataset.wired) {
            badge.dataset.wired = 'true';
            badge.addEventListener('pointerdown', function(e) {
                e.preventDefault();
                btn.click();
            });
            return true;
        }
        return false;
    }
    if (!wireBadge()) {
        var attempts = 0;
        var iv = setInterval(function() {
            if (wireBadge() || ++attempts > 10) clearInterval(iv);
        }, 200);
    }
})();
</script>
""",
        height=0,
    )

    # =========================================================================
    # MOBILE GATE — Desktop only for v1 (≥ 1024px, iPad Pro and up)
    # =========================================================================
    # Threshold raised from 768 to 1024 (April 2026) after visual testing
    # confirmed that the two-column workspace is only legible at iPad Pro
    # width or wider. Tablets in the 768-1023px range previously slipped
    # through the gate and rendered the workspace in a cramped state.
    screen_width = st.session_state.get("_browser_screen_size", "")
    if not screen_width or int(screen_width) < 1024:
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
/* Restore default gap inside inline story detail expansions. The
   workspace-wide gap:0 rule above collapses spacing in the story
   detail's internal two-column layout (STAR content left, technologies
   right), crushing Task/Action/Result headings together.

   The story detail is the ONLY component in Role Match that creates
   NESTED stColumns — the main workspace has one level (input_col,
   results_col) while the story detail adds a second level inside the
   results column. So "stColumn inside stColumn" uniquely identifies
   the story detail's internal layout without needing a key selector. */
.st-key-role_match_workspace [data-testid="stColumn"] [data-testid="stColumn"] [data-testid="stVerticalBlock"] {
    gap: 1rem !important;
}
.st-key-role_match_workspace [data-testid="stColumn"] [data-testid="stColumn"] [data-testid="stLayoutWrapper"] {
    gap: normal !important;
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
.role-match-demo-hint {
    font-family: inherit;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 8px 0 0 0 !important;
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
.st-key-role_match_workspace [data-testid="stColumn"]:first-child
    [data-testid="stElementContainer"]:has(.role-match-demo-hint) {
    margin-bottom: 24px !important;
}
/* Right panel: tighten the gap between hint and CTA button.
   Scoped to .st-key-role_match_followup_block so the gap collapse only
   affects the hint+CTA container, not the entire results column block. */
.st-key-role_match_followup_block [data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
}
.st-key-role_match_followup_block
    [data-testid="stElementContainer"]:has(.role-match-demo-hint) {
    margin-bottom: 0 !important;
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

/* MATTGPT-245 phase two — pending row for the per-requirement st.empty()
   slot seeded before the fan-out. Hollow purple ring in the exact
   footprint of the resolved status badge (22px, same margin-top, same
   flex behavior) so nothing shifts when the on_row callback overwrites
   the slot with the finished-row markup. Deliberately not sharing the
   .role-match-status-badge selector -- pending is a distinct visual
   state, not a badge variant. Text uses --text-secondary (dimmer than
   the resolved --text-primary) as an intensity signal only -- no
   font-style change, so the only visual transition on resolve is the
   ring filling to a colored badge. */
.role-match-pending-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 4px 0;
}
@keyframes rmpr-pulse {
    0%, 100% { opacity: 0.35; }
    50%      { opacity: 1; }
}
.role-match-pending-ring {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: transparent;
    border: 2px solid var(--accent-purple, #8B5CF6);
    box-sizing: border-box;
    margin-top: 1px;
    animation: rmpr-pulse 1.4s infinite ease-in-out;
}
.role-match-pending-text {
    flex: 1;
    font-size: 13px;
    color: var(--text-secondary);
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

/* Expanded story detail container — bottom margin separates it from the
   next requirement card below. Starting value 16px; tune to taste. */
[class*="st-key-role_match_ev_"] {
    margin-bottom: 16px !important;
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
    background: var(--text-secondary);
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
/* .role-match-legend removed as dead code */


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
/* MATTGPT-245: the base rule above uses !important on
   background/color/cursor, which masks Streamlit's default disabled
   visual. Restore the affordance explicitly so the disabled state
   reads. transform: none prevents the hover scale from taking effect
   if a hover fires on a disabled state via touchscreen tap. */
.st-key-role_match_submit button:disabled {
    opacity: 0.4 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* =============================================================================
   PHASE 4 — SLICE 1: LOCK ICON (top-right of results panel)
   ============================================================================= */
/* The right column (results_col) is rendered by Streamlit as a flex container
   with flex-direction: column and align-items: start. The natural way to
   right-align a single child is align-self: flex-end on the child itself —
   no absolute positioning, no need to make the column a positioning context.
   The lock takes its natural position at the top of the column flow because
   we render it first; align-self pulls it to the right edge. */
[class*="st-key-lock_icon"] {
    align-self: flex-end !important;
    width: auto !important;     /* Defeat Streamlit's emotion-cache width:100%
                                   on stVerticalBlock. Without this, the lock
                                   container fills the column at full width
                                   and align-self has nothing to flex against
                                   — the visible glyph renders at the LEFT
                                   edge of the wide container. width:auto
                                   shrinks the container to content size so
                                   align-self: flex-end actually right-anchors
                                   the visible element. */
}
[class*="st-key-lock_icon"] button {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 18px !important;
    padding: 6px !important;
    min-height: unset !important;
}
[class*="st-key-lock_icon"] button:hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
}
/* Brand-aligned popover styling — scoped via widget keys on inner Streamlit
   elements. The popover body is portal-rendered (NOT a descendant of
   .st-key-lock_icon), so we cannot use a single ancestor selector. Instead
   we attach key= to the elements we need to style: lock_popover (container),
   lock_password_input (text_input), and rely on Streamlit's auto-generated
   FormSubmitter-<form_key>-<button_label> class for the submit button. */
/* Streamlit renders the visible "input box" border on the
   stTextInputRootElement WRAPPER, not the <input> itself. The wrapper
   has Streamlit auto-generated single-class rules (.st-dy/.st-dz/.st-e0/
   .st-e1) setting each border-{side}-color individually to the error
   red rgb(255, 75, 75). We override each side individually because
   Streamlit sets them individually — `border-color` shorthand doesn't
   always win the cascade. :focus-within on the wrapper matches when
   the inner input has focus. */
[class*="st-key-lock_password_input"] [data-testid="stTextInputRootElement"] {
    border-top-color: var(--border-color) !important;
    border-right-color: var(--border-color) !important;
    border-bottom-color: var(--border-color) !important;
    border-left-color: var(--border-color) !important;
}
[class*="st-key-lock_password_input"] [data-testid="stTextInputRootElement"]:focus-within {
    border-top-color: var(--accent-purple) !important;
    border-right-color: var(--accent-purple) !important;
    border-bottom-color: var(--accent-purple) !important;
    border-left-color: var(--accent-purple) !important;
    box-shadow: 0 0 0 2px var(--accent-purple-light) !important;
}
[class*="st-key-lock_popover"] [data-testid="InputInstructions"] {
    display: none !important;
}
/* Brand-purple submit button.
   NOTE: this selector encodes the submit button label "Unlock" — Streamlit
   generates the class from st.form("lock_password_form") + the button label.
   If the label changes, this selector breaks silently. */
[class*="st-key-FormSubmitter-lock_password_form-Unlock"] button {
    background: var(--accent-purple) !important;
    color: white !important;
    border: none !important;
}
[class*="st-key-FormSubmitter-lock_password_form-Unlock"] button:hover {
    background: var(--accent-purple-hover) !important;
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
            if st.session_state.pop("role_match_load_demo", False):
                st.session_state["role_match_jd_input"] = _load_demo_jd()
            if st.session_state.pop("role_match_clear_flag", False):
                st.session_state["role_match_jd_input"] = ""
                for _k in (
                    "role_match_result",
                    "role_match_matched_jd",
                    "role_match_jd_persisted",
                    "role_match_active_evidence",
                    "role_match_error",
                    "role_match_gate_error",
                ):
                    st.session_state.pop(_k, None)

            # MATTGPT-245: read the assessment-in-progress flag once per
            # render pass. True on the pass immediately after a passing
            # gate (the same pass that runs the blocking LLM call);
            # False on all other passes. Wires into disabled= on Clear
            # and Submit so an accidental click during the ~20s
            # assessment can't discard the JD or start a second run.
            # The consume pops the flag so it doesn't leak across
            # reruns.
            _assessment_in_progress = _consume_assessment_in_progress_flag()

            jd_preview = st.session_state.get("role_match_jd_input", "")
            gate_error_msg = st.session_state.get("role_match_gate_error")
            failure_error_msg = st.session_state.get("role_match_error")
            banner_msg = gate_error_msg or failure_error_msg
            st.markdown(
                '<p class="role-match-jd-hint">Paste a job description below.</p>',
                unsafe_allow_html=True,
            )

            # MATTGPT-240: one banner location for every rejection.
            # Gate (input problem), retryable failure, and not-retryable
            # failure all render here in the left column above the
            # textarea. Each state has its own copy (_GATE_REJECT_MSG,
            # _RETRYABLE_MSG, _NOT_RETRYABLE_MSG) -- different causes,
            # different words -- but the arrangement is identical:
            # hint -> banner -> ✕ Clear -> textarea. One position, one
            # control, one label. No inline action inside the banner;
            # the ✕ Clear below serves every rejection state.
            if banner_msg:
                _emoji_prefix = "🐾 "
                _msg_body = banner_msg
                if banner_msg.startswith(_emoji_prefix):
                    _msg_body = banner_msg[len(_emoji_prefix) :]
                with st.container(key="role_match_banner"):
                    st.markdown(
                        f'<div class="role-match-banner-msg">'
                        f'<span style="margin-right: 6px;">🐾</span>'
                        f'{html.escape(_msg_body)}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            # Top ✕ Clear: shown whenever there is text in the textarea,
            # regardless of banner state. Sits below the banner so the
            # rejection message is read first and the affordance follows.
            if jd_preview.strip():
                if st.button(
                    "✕ Clear",
                    key="role_match_clear",
                    disabled=_assessment_in_progress,
                ):
                    st.session_state["role_match_clear_flag"] = True
                    st.rerun()

            # MATTGPT-240: st.form wraps the textarea + submit so the widget
            # value commits atomically with the click -- kills the two-click
            # bug where uncommitted textarea content let the first click
            # consume the widget commit without registering as a submit.
            # Button is always enabled: validation lives in the on_click
            # callback (_handle_submit_click), which fires BEFORE the rerun
            # so any gate rejection is visible to input_col's banner code
            # on the same pass. The old word-count disable ate the click
            # silently below 30 words.
            _result_payload = st.session_state.get("role_match_result") or {}
            btn_label = (
                "Update Match 🐾"
                if _result_payload.get("results")
                else "Match this role 🐾"
            )
            with st.form(key="role_match_form", clear_on_submit=False, border=False):
                jd_text = st.text_area(
                    "Job description",
                    height=400,
                    key="role_match_jd_input",
                    label_visibility="collapsed",
                    disabled=_assessment_in_progress,
                )
                with st.container(key="role_match_submit"):
                    submit_clicked = st.form_submit_button(
                        btn_label,
                        type="primary",
                        use_container_width=True,
                        on_click=_handle_submit_click,
                        disabled=_assessment_in_progress,
                    )

            if not jd_text.strip():
                st.markdown(
                    '<p class="role-match-demo-hint">Don\'t have a job description handy?</p>',
                    unsafe_allow_html=True,
                )
                if st.button("Try an example 🔍", key="role_match_demo_jd"):
                    st.session_state["role_match_load_demo"] = True
                    st.rerun()

        # ----- RIGHT: results area — Agy thinking indicator during processing, results or empty state otherwise -----
        with results_col:
            # Click-to-render timing (DEBUG-gated): start captured inside the
            # submit branch below, stop computed after _render_results_panel
            # returns. Declared here so both siblings in this results_col
            # scope can see it. None on any pass where submit did not fire
            # (navigation-return, empty-state render), so the emit is
            # naturally suppressed on non-submit passes.
            _click_start = None

            # Phase 4 lock icon — always visible at top-right of the results
            # column so the user can unlock before submitting a JD. Local
            # import is intentional: keeps the Phase 4 component's growing
            # dependency chain (slices 2-3) out of role_match.py's
            # module-load graph. Don't promote to top-level.
            with st.container(key="lock_icon"):
                from ui.components.lock_icon import render_lock_icon

                render_lock_icon()

            # Process click first so the thinking indicator appears before results render.
            # MATTGPT-240: guard on role_match_gate_error -- _handle_submit_click
            # (form_submit_button on_click callback) sets that state BEFORE the
            # rerun that lands here, so a gate rejection short-circuits the LLM
            # path without a second pass. The gate is owned by the callback;
            # this branch is the LLM path only.
            if (
                submit_clicked
                and jd_text.strip()
                and not st.session_state.get("role_match_gate_error")
            ):
                # Click-to-render timing: capture start before run_assessment
                # so the full submit-branch + render span is measured. Stop is
                # computed after _render_results_panel returns below.
                _click_start = time.perf_counter()

                # MATTGPT-245 phase two: interleaved sequence replaces the
                # single blocking run_assessment call. Extraction runs
                # under the in-flow indicator; when it returns, the
                # indicator disappears and header + legend + Location +
                # N pending rows render. Fan-out then fills each slot in
                # place via the on_row callback. Post-fanout summary +
                # discussion render below the rows. All transient --
                # post-success rerun (below) redraws the full stable
                # panel via _render_results_panel.
                loading_container = st.empty()
                with loading_container:
                    render_thinking_indicator(mount="inline")
                # Height anchor kept from phase one for the brief window
                # between extraction return and pending-row render.
                # Rendered BEFORE the blocking extract_requirements call
                # so it's in the DOM (Streamlit renders incrementally).
                height_anchor = st.empty()
                height_anchor.markdown(
                    '<div style="min-height:400px;"></div>',
                    unsafe_allow_html=True,
                )
                try:
                    import asyncio as _asyncio

                    from services.jd_assessor import (
                        _fan_out_assessments,
                        _get_openai_client,
                        extract_requirements,
                    )

                    # Stage 1: extraction (indicator visible during this).
                    _client = _get_openai_client()
                    _extraction = extract_requirements(_client, jd_text)

                    # Flatten to submission-ordered requirement list. Same
                    # three-block order as run_assessment (required +
                    # preferred + implicit-to-required) so a shared
                    # invariant holds across both call paths.
                    _all_requirements = []
                    for _r in _extraction.get("required_qualifications", []) or []:
                        _all_requirements.append(
                            {"text": _r["requirement"], "category": "required"}
                        )
                    for _r in _extraction.get("preferred_qualifications", []) or []:
                        _all_requirements.append(
                            {"text": _r["requirement"], "category": "preferred"}
                        )
                    for _r in _extraction.get("implicit_requirements", []) or []:
                        _all_requirements.append(
                            {"text": _r["requirement"], "category": "required"}
                        )

                    # Hide indicator + height anchor; pending rows now
                    # provide real flow content.
                    loading_container.empty()
                    height_anchor.empty()

                    # Pre-fanout render: header + legend + Location.
                    # include_actions=False so Helpful/Share/Export don't
                    # render during the fan-out -- any click on those
                    # buttons triggers a Streamlit rerun that abandons
                    # the running assessment and leaves the panel with
                    # half its rings unfilled. The post-success rerun
                    # redraws the header via _render_results_panel (which
                    # uses the default include_actions=True) so the
                    # actions come back on the stable render.
                    _placeholder_payload = {
                        "extraction": _extraction,
                        "results": [],
                    }
                    _render_results_header(_placeholder_payload, include_actions=False)
                    st.markdown(_build_legend_screen_html(), unsafe_allow_html=True)
                    st.markdown(
                        _build_location_screen_html_with_style(),
                        unsafe_allow_html=True,
                    )

                    # Create per-requirement st.empty() slots, seeded
                    # with the pending-state HTML (hollow ring + text).
                    _slots = []
                    for _req in _all_requirements:
                        _slot = st.empty()
                        with _slot:
                            st.markdown(
                                _render_pending_row_html(_req["text"]),
                                unsafe_allow_html=True,
                            )
                        _slots.append(_slot)

                    # on_row closure: minimal in-slot render (badge +
                    # text only). Evidence chips and gap explanation
                    # come back on the post-success rerun when
                    # _render_results_panel takes over -- putting
                    # st.button-based chips inside a mid-fanout slot is
                    # untested territory and this isn't the moment to
                    # find out. Uses html.escape on the requirement text
                    # for the same reason _render_pending_row_html does.
                    def _on_row(idx, assessment):
                        _status = _normalize_row_status(assessment)
                        _icon = _STATUS_ICON[_status]
                        _req_html = html.escape(assessment.get("requirement", ""))
                        _slots[idx].empty()
                        with _slots[idx]:
                            st.markdown(
                                f'<div class="role-match-req-title-row">'
                                f'<div class="role-match-status-badge '
                                f'{_status}">{_icon}</div>'
                                f'<span class="role-match-req-title">'
                                f"{_req_html}</span></div>",
                                unsafe_allow_html=True,
                            )

                    # Stages 2+3: fan-out with per-completion callback.
                    _match_results = _asyncio.run(
                        _fan_out_assessments(
                            _client,
                            _all_requirements,
                            stories,
                            on_row=_on_row,
                        )
                    )

                    # Post-fanout: build result, persist to session
                    # state (same keys as before), render summary +
                    # discussion below the filled rows.
                    result = {
                        "extraction": _extraction,
                        "results": _match_results,
                    }
                    st.session_state["role_match_result"] = result
                    st.session_state["role_match_matched_jd"] = jd_text.strip()
                    # Persist the JD text in a NON-widget session key so
                    # we can restore the textarea after a navigation away
                    # and back. Streamlit garbage-collects widget state
                    # for widgets that aren't currently in the page tree
                    # (e.g., when the user navigates to Home), but
                    # role_match_result survives because it's a regular
                    # session_state key. Without this persisted copy the
                    # user comes back to an empty textarea sitting next
                    # to populated results, a confusing inconsistency.
                    st.session_state["role_match_jd_persisted"] = jd_text
                    st.session_state.pop("role_match_error", None)

                    st.markdown(
                        _build_summary_screen_html(result),
                        unsafe_allow_html=True,
                    )
                except Exception as e:  # noqa: BLE001
                    # MATTGPT-240: distinguish retryable from not in the
                    # UI copy; log with error-class granularity. str(e)
                    # never reaches the visitor (was the original -240
                    # defect -- see the failure-branch unit tests).
                    # Cleanup mirrors the gate branch. Pops
                    # role_match_gate_error too: gate rejection and
                    # assessment failure are mutually exclusive states.
                    # Persists jd_text so the visitor can retry without
                    # re-pasting after navigation-return -- same reason
                    # the success branch persists (see comment above).
                    for _k in (
                        "role_match_result",
                        "role_match_matched_jd",
                        "role_match_active_evidence",
                        "role_match_gate_error",
                    ):
                        st.session_state.pop(_k, None)
                    st.session_state["role_match_error"] = _handle_assessment_error(e)
                    st.session_state["role_match_jd_persisted"] = jd_text
                    _failure_needs_rerun = True
                else:
                    _failure_needs_rerun = False
                finally:
                    loading_container.empty()
                    height_anchor.empty()
                if _failure_needs_rerun:
                    # MATTGPT-240: failure banner lives in the left column;
                    # the state we just set is invisible to this pass
                    # because input_col has already rendered. Rerun so the
                    # left-column banner code picks it up on the fresh
                    # pass. Same reason on_click handles gate rejection --
                    # LLM path can't use on_click (needs the loading
                    # indicator), so rerun after the exception is the
                    # counterpart move.
                    st.rerun()

                # Log OUTSIDE try/except so a logging failure can't
                # interfere with the assessment result. Only log when
                # a result was successfully stored. MATTGPT-247: the
                # inline sum() block was extracted into
                # _log_role_match_success + _build_role_match_log_kwargs
                # so unassessed_count (Cycle 2 producer) enters the
                # log call and the arithmetic invariant
                # (strong+partial+gap+unassessed == required+preferred)
                # can be tested without a Streamlit fixture. Delayed
                # import removed -- the module-scope import at line 21
                # is what test 9 and test 10 patches bind to.
                if st.session_state.get("role_match_result"):
                    _log_role_match_success(st.session_state["role_match_result"])
                    # MATTGPT-245: rerun after success so input_col
                    # re-renders on a fresh pass. Without this, the
                    # pass that runs the LLM is also the pass that
                    # consumed the assessment_in_progress flag (True)
                    # and drew Clear + Submit disabled and the label
                    # "Match this role" -- and no subsequent rerun
                    # fires to redraw them enabled with "Update
                    # Match". Symmetric with _failure_needs_rerun
                    # above: both success and failure end with a
                    # rerun so state changes made mid-pass become
                    # visible on the fresh pass.
                    #
                    # Persist _click_start across the rerun so the
                    # click-to-render telemetry (fired inside
                    # _render_results_panel below on the fresh pass)
                    # still measures the full submit-branch + render
                    # span. Without the persist, the fresh pass sees
                    # _click_start = None (local) and skips the emit.
                    if _click_start is not None:
                        st.session_state["_role_match_click_start_pending"] = (
                            _click_start
                        )
                    st.rerun()
            # Render: results → empty state. MATTGPT-240: all three
            # rejection states (gate, retryable failure, not-retryable
            # failure) render as a banner in the left column above the
            # textarea, not here. The visitor experiences one thing on any
            # rejection -- something went wrong and the next action is on
            # the left -- so both error keys live at the left banner and
            # the right panel keeps its empty state, which is honest: no
            # assessment exists.
            if st.session_state.get("role_match_result"):
                _render_results_panel(st.session_state["role_match_result"], stories)
                # Click-to-render emit: fires on the submit-triggered pass
                # OR on the fresh pass that follows the MATTGPT-245
                # post-success rerun. On the submit-triggered pass,
                # _click_start is set locally (line inside the submit
                # branch above). On the fresh pass after the rerun,
                # _click_start is None (local) but the pre-rerun code
                # persisted it to session state; pop it here.
                # Navigation-return renders (result in state, no submit,
                # no pre-rerun persist) leave both None and skip the emit.
                _emit_start = _click_start or st.session_state.pop(
                    "_role_match_click_start_pending", None
                )
                if _emit_start is not None:
                    _total_ms = (time.perf_counter() - _emit_start) * 1000.0
                    _n_reqs = len(
                        st.session_state["role_match_result"].get("results") or []
                    )
                    _debug_print_click_to_render(_total_ms, _n_reqs)
                if st.session_state["role_match_result"].get("results"):
                    with st.container(key="role_match_followup_block"):
                        st.markdown(
                            '<p class="role-match-demo-hint">Explore Matt\'s experience in depth.</p>',
                            unsafe_allow_html=True,
                        )
                        if st.button("Ask Agy 🐾", key="role_match_followup_cta"):
                            st.session_state["active_tab"] = "Ask Agy"
                            st.rerun()
            else:
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; justify-content: center; min-height: 400px;">
                        <p style="color: var(--text-secondary); font-size: 16px; text-align: center; margin: 0; font-family: inherit;">
                            Agy will map each requirement to Matt's real project experience.
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
