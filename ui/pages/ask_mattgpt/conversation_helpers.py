"""
Conversation View Helper Functions

Rendering helpers specific to Ask MattGPT conversation view.
Extracted from monolithic ask_mattgpt.py in Phase 5.1.
"""

import math

import streamlit as st

from config.debug import DEBUG
from ui.components.story_detail import render_story_detail

# Import from existing modules
from ui.pages.ask_mattgpt.story_intelligence import THEME_TO_PATTERN
from ui.pages.ask_mattgpt.utils import get_context_story, story_modes
from utils.formatting import build_5p_summary
from utils.ui_helpers import (
    render_no_match_banner,
    render_sources_badges_static,
    render_sources_chips,
    safe_container,
)

# ============================================================================
# SOURCES DISPLAY CONFIG
# ============================================================================
SOURCES_LABEL = "SOURCES"
SOURCES_COLS_PER_ROW = 3
SOURCES_MAX_SYNTHESIS = 6  # Broad queries: show more sources (forest view)
SOURCES_MAX_SURGICAL = 3  # Targeted queries: show fewer sources (tree view)

# ============================================================================
# STATE MANAGEMENT
# ============================================================================


def set_answer(resp: dict):
    """
    Update session state with answer response.

    State-only update; UI renders chips separately to avoid double-render / layout conflicts.

    Args:
        resp: Response dict from backend with answer_md, sources, modes
    """
    st.session_state["last_answer"] = resp.get("answer_md") or resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", []) or []
    st.session_state["answer_modes"] = resp.get("modes", {}) or {}
    st.session_state["answer_mode"] = resp.get("default_mode", "narrative")


# ============================================================================
# CONTEXT BANNER
# ============================================================================


def render_compact_context_banner(stories: list[dict]):
    """
    Single-line context breadcrumb showing active story context.

    Args:
        stories: All stories (for context lookup)
    """
    ctx = get_context_story(stories)
    if not ctx:
        return

    client = (ctx.get("Client") or "").strip()
    domain_full = (ctx.get("Sub-category") or "").strip()
    domain_short = domain_full.split(" / ")[-1] if " / " in domain_full else domain_full

    st.markdown(
        f"""
   <div style='font-size: 13px; color: var(--text-muted); margin-bottom: 16px; padding: 8px 12px; background: var(--bg-surface); border-radius: 6px;'>
    Context: {client} | {domain_short}
    </div>
    """,
        unsafe_allow_html=True,
    )


# ============================================================================
# BADGE RENDERING
# ============================================================================

_DOT_EMOJI = [
    "🟦",
    "🟩",
    "🟥",
    "🟧",
    "🟦",
    "🟪",
    "🟩",
    "🟧",
    "🟪",
    "🟦",
]  # stable palette-ish


def _dot_for(label: str) -> str:
    """Get colored dot emoji for a label based on hash."""
    if not label:
        return "•"
    idx = sum(ord(c) for c in label) % len(_DOT_EMOJI)
    return _DOT_EMOJI[idx]


def render_badges_static(s: dict):
    """
    Render a single flowing row of small badges for personas + tags.
    Matches the mock badge styling already defined in CSS (.badge-row, .badge).
    Safe no-op if nothing to show.

    Args:
        s: Story dictionary
    """
    try:
        personas = s.get("personas") or []
        tags = s.get("tags") or []
    except Exception:
        personas, tags = [], []

    # Normalize to strings and prune empties
    personas = [str(p).strip() for p in personas if str(p).strip()]
    tags = [str(t).strip() for t in tags if str(t).strip()]

    if not personas and not tags:
        return

    chips = []

    # Personas first
    for p in personas:
        dot = _dot_for(p)
        chips.append(f"<span class='badge' title='Persona'>{dot} {p}</span>")

    # Then tags
    for t in tags:
        dot = _dot_for(t)
        chips.append(f"<span class='badge' title='Tag'>{dot} {t}</span>")

    html = "".join(chips)
    st.markdown(f"<div class='badge-row'>{html}</div>", unsafe_allow_html=True)


def show_persona_tags(s: dict):
    """Simple alias for personas/tags badges for a single story (non-interactive)."""
    return render_badges_static(s)


# ============================================================================
# SOURCE RENDERING
# ============================================================================


def show_sources(
    srcs: list[dict],
    *,
    interactive: bool = False,
    key_prefix: str = "src_",
    title: str = "Sources",
    stories: list[dict],
):
    """
    Render Sources row using a single call site.

    Args:
        srcs: List of source story dicts
        interactive: True for clickable chips (Ask), False for static badges (Explore/Details)
        key_prefix: Unique key prefix for buttons
        title: Section title
        stories: All stories (for interactive mode)
    """
    if not srcs:
        return
    if interactive:
        return render_sources_chips(
            srcs, title=title, stay_here=True, key_prefix=key_prefix, stories=stories
        )
    return render_sources_badges_static(srcs, title=title, key_prefix=key_prefix)


# ============================================================================
# FOLLOW-UP SUGGESTIONS
# ============================================================================


def render_followup_chips(primary_story: dict, query: str = "", key_suffix: str = ""):
    """
    Generate contextual follow-up suggestions based on the answer, adhering to the Agy Voice Guide.

    Args:
        primary_story: Current story being discussed
        query: User's query (unused currently)
        key_suffix: Unique suffix for button keys
    """
    if not primary_story:
        return

    # Focus on themes that trigger good semantic searches
    tags = set(str(t).lower() for t in (primary_story.get("tags") or []))

    suggestions = []

    # Theme-based suggestions that match Agy Voice Guide examples
    if any(t in tags for t in ["stakeholder", "collaboration", "communication"]):
        suggestions = [
            # Use official suggestion as priority, mix with contextually relevant existing questions
            "🎯 What's your approach to stakeholder management?",  # Official Guide Theme
            "👥 How do you scale agile across large organizations?",
            "Tell me about cross-functional collaboration",
        ]
    elif any(t in tags for t in ["cloud", "architecture", "platform", "technical"]):
        suggestions = [
            "⚡ Show me your platform engineering experience",  # Official Guide Theme
            "Show me examples with cloud architecture",
            "How do you modernize legacy systems?",
        ]
    elif any(t in tags for t in ["agile", "process", "delivery"]):
        suggestions = [
            "👥 How do you scale agile across large organizations?",  # Official Guide Theme
            "How do you accelerate delivery?",
            "💡 How have you driven innovation in your career?",
        ]
    elif any(t in tags for t in ["healthcare", "health"]):
        suggestions = [
            "🏥 How did you apply GenAI in a healthcare project?",  # Official Guide Theme
            "Tell me about the challenges of technology in the healthcare space",
            "Show me examples with measurable impact",
        ]
    else:
        # Default/Generic suggestions, prioritizing the official voice guide prompts
        suggestions = [
            "🚀 Tell me about leading a global payments transformation",  # Official Guide Prompt
            "💡 How have you driven innovation in your career?",  # Official Guide Prompt
            "Show me examples with measurable impact",
        ]

    if not suggestions:
        return

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    # Only display the top 3 suggestions
    cols = st.columns(len(suggestions[:3]))
    for i, suggest in enumerate(suggestions[:3]):
        with cols[i]:
            # Make key unique by including card index and suggestion index
            unique_key = (
                f"followup_{key_suffix}_{i}"
                if key_suffix
                else f"followup_{hash(suggest)%10000}_{i}"
            )
            if st.button(suggest, key=unique_key, use_container_width=True):
                st.session_state["__inject_user_turn__"] = suggest
                st.session_state["__ask_force_answer__"] = True
                st.rerun()


# ============================================================================
# TRANSCRIPT RENDERING (The Big One)
# ============================================================================


def _render_ask_transcript(stories: list[dict]):
    """
    Render conversation transcript in strict order so avatars / order never jump.

    Handles three message types:
    - "card": Static answer card snapshot with view modes
    - "banner": Nonsense/off-domain detection banner
    - "conversational": AI response with Related Projects
    - Default: Simple user/assistant text bubbles

    Args:
        stories: All stories (for context and source lookups)
    """
    for i, m in enumerate(st.session_state.get("ask_transcript", [])):
        # Static snapshot card entry
        if m.get("type") == "card":
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                # Snapshot with the same visual shell as the live answer card
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                with safe_container(border=True):
                    title = m.get("Title", "")
                    one_liner = m.get("one_liner", "")
                    sid = m.get("story_id")
                    story = next(
                        (s for s in stories if str(s.get("id")) == str(sid)), None
                    )
                    # If the user clicked a Source after this snapshot was created,
                    use_ctx = bool(st.session_state.get("__ctx_locked__"))
                    _ctx = get_context_story(stories) if use_ctx else None
                    if isinstance(_ctx, dict) and (_ctx.get("id") or _ctx.get("Title")):
                        story = _ctx or story
                    # If we resolved to a different story via Source click, update the header text, too
                    if isinstance(story, dict):
                        title = story.get("Title", title)
                        try:
                            one_liner = build_5p_summary(story, 9999)
                        except Exception:
                            one_liner = one_liner

                    # Title
                    if title:
                        st.markdown(f"### {title}")

                    # Metadata: Client, Role, Domain
                    if isinstance(story, dict):
                        client = story.get("Client", "")
                        role = story.get("Role", "")
                        domain = story.get("Sub-category", "")

                        # Create metadata line with role and domain
                        meta_parts = []
                        if client:
                            meta_parts.append(f"<strong>{client}</strong>")
                        if role or domain:
                            role_domain = " • ".join([x for x in [role, domain] if x])
                            if role_domain:
                                meta_parts.append(role_domain)

                        if meta_parts:
                            st.markdown(
                                f"<div style='font-size: 13px; color: var(--text-muted); margin-bottom: 12px;'>{' | '.join(meta_parts)}</div>",
                                unsafe_allow_html=True,
                            )

                    # Confidence indicator (check if story changed via source click)
                    confidence = m.get(
                        "confidence"
                    )  # Original confidence from snapshot
                    if DEBUG:
                        print(
                            f"DEBUG render: card_id={m.get('story_id')}, current_story_id={story.get('id') if story else None}, confidence={confidence}"
                        )

                    # If user clicked a different source, get that story's confidence from stored data
                    if isinstance(story, dict) and str(story.get("id")) != str(
                        m.get("story_id")
                    ):
                        # Story was changed via source click - use stored source confidences
                        source_confidences = m.get("source_confidences", {}) or {}
                        story_id = str(story.get("id"))
                        if story_id in source_confidences:
                            confidence = source_confidences[story_id]
                        if DEBUG:
                            print(
                                f"DEBUG render: switched story, new confidence={confidence}"
                            )

                    if confidence:
                        conf_pct = int(float(confidence) * 100)
                        # Color gradient: red -> orange -> green
                        if conf_pct >= 70:
                            bar_color = "#238636"  # green
                        elif conf_pct >= 50:
                            bar_color = "#ff8c00"  # orange
                        else:
                            bar_color = "#f85149"  # red

                        st.markdown(
                            f"""
                        <div style='display: flex; align-items: center; gap: 8px; font-size: 12px; color: #7d8590; margin-bottom: 12px;'>
                            <span>Match confidence</span>
                                <div style='width: 60px; height: 4px; background: var(--bg-surface); border-radius: 2px; overflow: hidden;'>
                                <div style='height: 100%; width: {conf_pct}%; background: {bar_color}; border-radius: 2px;'></div>
                            </div>
                            <span style='color: {bar_color}; font-weight: 600;'>{conf_pct}%</span>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    # 5P Summary
                    if one_liner:
                        st.markdown(
                            f"<div class='fivep-quote fivep-unclamped'>{one_liner}</div>",
                            unsafe_allow_html=True,
                        )

                    # View pills (Narrative / Key Points / Deep Dive) — clean CX
                    mode_key = f"card_mode_{i}"
                    st.session_state.setdefault(mode_key, "narrative")
                    if story:
                        modes = story_modes(story)
                        labels = [
                            ("narrative", "Narrative"),
                            ("key_points", "Key Points"),
                            ("deep_dive", "Deep Dive"),
                        ]
                        current = st.session_state.get(mode_key, "narrative")

                        # Prefer segmented control when available
                        if hasattr(st, "segmented_control"):
                            label_map = {b: a for a, b in labels}
                            default_label = next(
                                (b for a, b in labels if a == current), "Narrative"
                            )
                            chosen = st.segmented_control(
                                "View mode",  # ← Non-empty label
                                [b for _, b in labels],
                                selection_mode="single",
                                default=default_label,
                                key=f"seg_{mode_key}",
                                label_visibility="collapsed",  # ← Hide it
                            )
                            new_mode = label_map.get(chosen, "narrative")
                            if new_mode != current:
                                st.session_state[mode_key] = new_mode
                                st.rerun()
                        else:
                            # Fallback: left‑aligned pill buttons styled by .pill-container CSS
                            st.markdown(
                                f'<div class="pill-container" data-mode="{current}">',
                                unsafe_allow_html=True,
                            )
                            for key, text in labels:
                                class_name = {
                                    "narrative": "pill-narrative",
                                    "key_points": "pill-keypoints",
                                    "deep_dive": "pill-deepdive",
                                }[key]
                                st.markdown(
                                    f'<div class="{class_name}">',
                                    unsafe_allow_html=True,
                                )
                                if st.button(
                                    text,
                                    key=f"snap_pill_{i}_{key}",
                                    disabled=(current == key),
                                ):
                                    st.session_state[mode_key] = key
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
                        sel = st.session_state.get(mode_key, "narrative")
                        body = modes.get(sel, modes.get("narrative", ""))
                        st.markdown(body)

                    # Sources inside the bubble for symmetry (interactive chips)
                    srcs = m.get("sources", []) or []
                    if srcs:
                        st.markdown(
                            '<div class="sources-tight">', unsafe_allow_html=True
                        )
                        render_sources_chips(
                            srcs,
                            title="Sources",
                            stay_here=True,
                            key_prefix=f"snap_{i}_",
                            stories=stories,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Add follow-up suggestion chips
                        if story:
                            render_followup_chips(
                                story,
                                st.session_state.get("ask_input", ""),
                                key_suffix=f"snap_{i}",
                            )

                # Action buttons (Helpful/Copy/Share) - HIDDEN for Streamlit version
                # TODO: Re-enable for React version

                st.markdown('</div>', unsafe_allow_html=True)
            continue

        # Banner (nonsense/off-domain detection)
        if m.get("type") == "banner":
            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                render_no_match_banner(
                    reason=m.get("reason", ""),
                    query=m.get("query", ""),
                    overlap=m.get("overlap", None),
                    suppressed=st.session_state.get("__pc_suppressed__", False),
                    filters=st.session_state.get("filters", {}),
                    key_prefix=f"transcript_banner_{i}",
                )
            continue

        # Conversational answer with Related Projects (wireframe style)
        if m.get("type") == "conversational":
            # Generate a stable message ID based on content hash (not index)
            # This prevents key collisions when messages shift
            msg_hash = hash(m.get("text", "")[:50]) % 100000

            with st.chat_message(
                "assistant",
                avatar="https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg",
            ):
                # Show conversational response text
                st.markdown(m.get("text", ""))

                # Show Related Projects in wireframe style
                sources = m.get("sources", []) or []
                if sources:
                    st.markdown(
                        f'''
                    <div class="sources-tight">
                        <div class="source-links-title">{SOURCES_LABEL}</div>
                    </div>
                    ''',
                        unsafe_allow_html=True,
                    )

                    # Use regular buttons instead of forms to avoid rerun issues
                    # Style them to look like the original form buttons
                    # Get currently expanded story ID for selected state styling
                    current_expanded_id = st.session_state.get(
                        "transcript_source_expanded_id"
                    )

                    st.markdown(
                        """
                        <style>
                        /* Force source card row to not stretch columns */
                        [class*="st-key-sources_grid"] .stHorizontalBlock {
                            align-items: flex-start !important;
                        }
                        /* Force columns to not stretch to full height */
                        [class*="st-key-sources_grid"] .stColumn {
                            height: auto !important;
                            align-self: flex-start !important;
                        }
                        [class*="st-key-sources_grid"] .stColumn > .stVerticalBlock {
                            height: auto !important;
                            justify-content: flex-start !important;
                        }
                        /* Remove gap inside button containers (fixes style tag gap issue) */
                        [class*="st-key-container_related_proj"] {
                            gap: 0 !important;
                            row-gap: 0 !important;
                        }

                        /* Related Projects button styling */
                        [class*="st-key-container_related_proj"] button,
                        [class*="st-key-related_proj"] button {
                            background: var(--bg-surface) !important;
                            border: 1px solid var(--border-color) !important;
                            color: var(--accent-purple) !important;
                            font-size: 14px !important;
                            font-weight: 500 !important;
                            padding: 6px 12px !important;
                            border-radius: 8px !important;
                            width: 100% !important;
                            height: auto !important;
                            min-height: 56px !important;
                            transition: all 0.2s ease !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                        }
                        [class*="st-key-container_related_proj"] button:hover,
                        [class*="st-key-related_proj"] button:hover {
                            background: var(--bg-hover) !important;
                            border-color: var(--accent-purple) !important;
                        }
                        [class*="st-key-container_related_proj"] button p,
                        [class*="st-key-related_proj"] button p {
                            color: var(--accent-purple) !important;
                            font-size: 14px !important;
                            margin: 0 !important;
                            line-height: 1.4 !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Dynamic grid based on query type:
                    # - Synthesis (broad themes): 6 sources (forest view)
                    # - Surgical (specific story): 3 sources (tree view)
                    msg_query_intent = m.get("query_intent")
                    is_synthesis = msg_query_intent == "synthesis"
                    max_sources = (
                        SOURCES_MAX_SYNTHESIS if is_synthesis else SOURCES_MAX_SURGICAL
                    )
                    display_sources = sources[:max_sources]
                    rows_needed = math.ceil(len(display_sources) / SOURCES_COLS_PER_ROW)

                    with st.container(key=f"sources_grid_{i}_{msg_hash}"):
                        for row in range(rows_needed):
                            cols = st.columns(SOURCES_COLS_PER_ROW)
                            for col_idx in range(SOURCES_COLS_PER_ROW):
                                src_idx = row * SOURCES_COLS_PER_ROW + col_idx
                                if src_idx >= len(display_sources):
                                    continue  # No more sources

                                src = display_sources[src_idx]
                                title = src.get("title") or src.get("Title", "")
                                client = src.get("client") or src.get("Client", "")
                                story_id = src.get("id") or src.get("ID", "")

                                # For synthesis mode, use pattern phrase instead of client
                                # This matches the response structure ("He ships" not "JPMorgan")
                                # Read from message's stored intent, not global state (fixes re-render bug)
                                msg_query_intent = m.get("query_intent")
                                is_synthesis_mode = msg_query_intent == "synthesis"
                                if is_synthesis_mode:
                                    theme = src.get("theme") or src.get("Theme", "")
                                    pattern = THEME_TO_PATTERN.get(theme, theme)
                                    # Use short pattern prefix for cleaner labels
                                    label = (
                                        f"{pattern} {title}"
                                        if pattern and title
                                        else title
                                    )
                                else:
                                    label = (
                                        f"{client} - {title}"
                                        if client and title
                                        else title
                                    )

                                with cols[col_idx]:
                                    # Use stable key based on message index + hash + source index + story ID
                                    stable_key = f"related_proj_{i}_{msg_hash}_{src_idx}_{story_id}"
                                    # Escape CSS special characters (pipe, etc.) for selector
                                    css_safe_key = stable_key.replace(
                                        "|", "\\|"
                                    ).replace(":", "\\:")

                                    # Check if this card is the selected one
                                    is_selected = current_expanded_id == story_id

                                    with st.container(key=f"container_{stable_key}"):
                                        # Add selected indicator styling inline
                                        if is_selected:
                                            st.markdown(
                                                f"""
                                                <style>
                                                [class*="st-key-{css_safe_key}"] button {{
                                                    background: #8B5CF6 !important;
                                                    border: 2px solid #7C3AED !important;
                                                    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.3) !important;
                                                }}
                                                [class*="st-key-{css_safe_key}"] button p {{
                                                    color: white !important;
                                                    font-weight: 600 !important;
                                                }}
                                                </style>
                                                """,
                                                unsafe_allow_html=True,
                                            )

                                        # When selected, show "✕ Close" - otherwise show link icon + label
                                        button_label = (
                                            "✕ Close" if is_selected else f"🔗 {label}"
                                        )

                                        if st.button(
                                            button_label,
                                            key=stable_key,
                                            use_container_width=True,
                                        ):
                                            # Use story_id as the expanded key (stable across reruns)
                                            expanded_key = f"expanded_{story_id}"
                                            current_expanded = st.session_state.get(
                                                "transcript_source_expanded"
                                            )

                                            # Preserve active_tab before any state changes
                                            if "active_tab" not in st.session_state:
                                                st.session_state["active_tab"] = (
                                                    "Ask MattGPT"
                                                )

                                            if current_expanded == expanded_key:
                                                # Clicking same source - close it
                                                st.session_state[
                                                    "transcript_source_expanded"
                                                ] = None
                                                st.session_state[
                                                    "transcript_source_expanded_id"
                                                ] = None
                                            else:
                                                # Open this source (closes any other)
                                                st.session_state[
                                                    "transcript_source_expanded"
                                                ] = expanded_key
                                                st.session_state[
                                                    "transcript_source_expanded_id"
                                                ] = story_id
                                                # Store msg_hash instead of index for matching
                                                st.session_state[
                                                    "transcript_source_expanded_msg"
                                                ] = msg_hash

                                            st.rerun()

                    # Render the expanded story detail below buttons for this message
                    expanded_key = st.session_state.get("transcript_source_expanded")
                    expanded_id = st.session_state.get("transcript_source_expanded_id")
                    expanded_msg = st.session_state.get(
                        "transcript_source_expanded_msg"
                    )

                    # Match using msg_hash instead of index i
                    if expanded_key and expanded_id and expanded_msg == msg_hash:
                        # Find the story object
                        story_obj = next(
                            (
                                s
                                for s in stories
                                if str(s.get("id")) == str(expanded_id)
                            ),
                            None,
                        )

                        if story_obj:
                            # Ensure story detail breaks out of narrow container on mobile
                            st.markdown(
                                """
                                <style>
                                /* Force story detail to full width on mobile */
                                @media (max-width: 767px) {
                                    [class*="st-key-transcript_expanded_"] {
                                        width: 100vw !important;
                                        max-width: 100vw !important;
                                        margin-left: -16px !important;
                                        margin-right: -16px !important;
                                        padding: 0 16px !important;
                                    }
                                    [class*="st-key-transcript_expanded_"] .story-detail-pane {
                                        width: 100% !important;
                                        max-width: 100% !important;
                                    }
                                }
                                </style>
                                <div style='margin-top: 16px;'></div>
                                """,
                                unsafe_allow_html=True,
                            )

                            render_story_detail(
                                story_obj, f"transcript_expanded_{expanded_id}", stories
                            )

                # Action buttons (wireframe style) - HIDDEN for Streamlit version
                # TODO: Re-enable for React version

            continue

        # Default chat bubble (user/assistant text)
        role = "assistant" if m.get("Role") == "assistant" else "user"

        # Set custom avatars
        if role == "assistant":
            avatar = "https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/svg/agy_icon_color.svg"
        else:
            avatar = "https://mcpugmire1.github.io/mattgpt-design-spec/brand-kit/chat_avatars/MattCartoon-Transparent.png"

        with st.chat_message(role, avatar=avatar):
            st.write(m.get("text", ""))
