"""UI helper utilities - containers, debug output."""

import re

import streamlit as st

from config.debug import DEBUG
from utils.formatting import _format_deep_dive, _format_key_points, _format_narrative

# ============================================================================
# Branch-aware rejection chip sets — LOCKED May 19, 2026 (MATTGPT-071)
#
# Each chip is (label, click-injected prompt). Step definitions in
# tests/bdd/steps/test_ask_mattgpt.py read these constants as the
# single source of truth.
#
# Production validation log lives in BACKLOG.md MATTGPT-071 "Chip-prompt
# validation log". See MATTGPT-077 for the phrasing-sensitivity findings
# that informed the rule:* chip swap ("Modernize legacy systems" replaced
# "Modernize monoliths into microservices" because the latter triggered
# MattGPT/Strangler Fig self-referential responses).
#
# As of Red-B commit, render_no_match_banner does not yet consume these
# constants — branch-aware rendering lands in the Blue commit.
# ============================================================================

RULE_CHIPS = [
    ("Scale an org from 0 to 150+", "How did Matt scale the CIC to 150+ engineers?"),
    (
        "Build teams like a startup",
        "How does Matt build teams that ship like startups?",
    ),
    ("Modernize legacy systems", "How does Matt approach legacy system modernization?"),
    (
        "Modernize payments at scale",
        "Tell me about Matt's payments modernization at scale.",
    ),
]

PERSONAL_CHIPS = [
    ("What kind of leader is Matt?", "What kind of leader is Matt?"),
    ("How does Matt handle pressure?", "How does Matt show up when things go wrong?"),
    ("Why does Matt do this work?", "What drives Matt — why does he do this work?"),
    (
        "What do former colleagues say?",
        "How would Matt's former teammates describe him?",
    ),
]

OUT_OF_SCOPE_CHIPS = [
    ("Payments at JP Morgan", "Tell me about Matt's payments work at JP Morgan."),
    (
        "Cloud Innovation Center",
        "How did Matt establish and scale the Cloud Innovation Center?",
    ),
    ("Scaling teams 4 → 150+", "How did Matt scale engineering teams from 4 to 150+?"),
    (
        "Modernizing legacy platforms",
        "Tell me about Matt's work modernizing legacy enterprise platforms.",
    ),
]

BANNER_COPY = {
    "rule": "🐾 Wrong trail. I'm a Plott Hound trained to track Matt's transformation work. Give me a real scent to follow.",
    "personal": "🐾 I'm focused on Matt's professional experience.",
    "out_of_scope": "🐾 That's outside Matt's experience.",
    "low_confidence": "🐾 I picked up a scent but lost the trail. Try rephrasing your question and I'll track it down.",
}


def dbg(*args):
    """Debug output to sidebar (only when DEBUG=True)."""
    if DEBUG:
        try:
            st.sidebar.write("🧪", *args)
        except Exception:
            pass


def safe_container(*, border: bool = False):
    """
    Streamlit compatibility helper for bordered containers.

    Older Streamlit versions don't support border kwarg.
    """
    try:
        return st.container(border=border)
    except TypeError:
        return st.container()


def render_sources_badges(
    sources: list[dict],
    *,
    title: str = "Sources",
    key_prefix: str = "srcbad_",
    stories: list,
):
    """Backward-compatible alias: render interactive chips and stay on Ask."""
    return render_sources_chips(
        sources, title=title, stay_here=True, key_prefix=key_prefix, stories=stories
    )


def render_sources_badges_static(
    sources: list[dict], title: str = "Sources", key_prefix: str = "srcbad_"
):
    """Render non-interactive mock-style badges under a small 'Sources' header.
    This avoids nested layout/columns and matches the mock_ask_hybrid DOM exactly.
    """
    if not sources:
        return

    # Normalize + prune empties
    items = []
    for s in sources:
        sid = str(s.get("id") or s.get("story_id") or "").strip()
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        if not (sid or client or title_txt):
            continue
        items.append({"id": sid, "client": client, "title": title_txt})
    if not items:
        return

    # Tight section header (no extra paragraph margins)
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)

    chips_html = []
    _scores = st.session_state.get("__pc_last_ids__", {}) or {}
    for s in items:
        label_full = f"{s['client']} — {s['title']}" if s['client'] else s['title']
        _score_key = str(s.get("id") or "")
        sc = _scores.get(_score_key)
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, int | float) else None

        text = _shorten_middle(label_full, 96)
        if pct:
            text = f"{pct} Match • {text}"

        # Static badge (no icon) to match the mock capsule style
        chips_html.append(
            f"<span class='badge' title='Semantic relevance'>{text}</span>"
        )

    st.markdown(
        f"<div class='badge-row'>{''.join(chips_html)}</div>", unsafe_allow_html=True
    )


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-") or "x"


def story_modes(s: dict) -> dict:
    """Return the three anchored views for a single story."""
    return {
        "narrative": _format_narrative(s),
        "key_points": _format_key_points(s),
        "deep_dive": _format_deep_dive(s),
    }


def _shorten_middle(text: str, max_len: int = 64) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    keep = max_len - 1
    left = keep // 2
    right = keep - left
    return text[:left] + "… " + text[-right:]


def render_sources_chips(
    sources: list[dict],
    title: str = "Sources",
    *,
    stay_here: bool = False,
    key_prefix: str = "",
    stories: list,
):
    """Render Sources as compact, 2-line chips.
    - stay_here=True: switch the active story + modes inline on Ask (no tab jump)
    - stay_here=False: legacy behavior (navigate to Explore Stories)
    """
    if not sources:
        return

    # Normalize + prune empties, but accept story_id as fallback and try to infer from title/client if missing
    items = []
    for s in sources:
        # prefer 'id', fall back to 'story_id' (common from LLM/backend)
        sid = str(s.get("id") or s.get("story_id") or "").strip()
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        # If no id was provided, try to infer from STORIES by title/client
        if not sid and (title_txt or client):
            cand = None
            low_title = title_txt.lower()
            low_client = client.lower()
            for x in stories:
                xt = (x.get("title") or "").strip().lower()
                xc = (x.get("client") or "").strip().lower()
                if (
                    low_title
                    and xt == low_title
                    and (not low_client or xc == low_client)
                ):
                    cand = x
                    break
            if cand:
                sid = str(cand.get("id") or "").strip()
        # Skip if we still don't have an id and no visible label
        if not sid and not (title_txt or client):
            continue
        # Keep the item even if id is still blank, so click can resolve by title/client
        items.append(
            {
                "id": sid or "",
                "client": client,
                "title": title_txt,
            }
        )
    if not items:
        return

    # tighter, non-<p> header + zero top gap container
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div data-mpg-srcchips class='pill-container sources-tight sources-grid'>",
        unsafe_allow_html=True,
    )

    # Lay out chips in rows using Streamlit columns (3-up per row)
    per_row = 3
    container = st.container()
    batch: list[dict] = []

    def _chip_label(item: dict, idx: int) -> tuple[str, str]:
        sep = " \u2009— "
        base = (
            f"{item['client']}{sep}{item['title']}" if item["client"] else item["title"]
        )
        short = _shorten_middle(base, 72)
        safe_id = item.get("id") or _slug(base) or str(idx)
        _scores = st.session_state.get("__pc_last_ids__", {}) or {}
        sc = _scores.get(str(safe_id) or str(item.get("id") or ""))
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, int | float) else None
        label = f"{pct} Match • {short}" if pct else short
        return label, safe_id

    for i, s in enumerate(items, 1):
        batch.append(s)
        if len(batch) == per_row or i == len(items):
            cols = container.columns(len(batch))
            for col, item in zip(cols, batch, strict=False):
                with col:
                    label, safe_id = _chip_label(item, i)
                    btn_key = f"{key_prefix}srcchip_{safe_id}"
                    if st.button(
                        label,
                        key=btn_key,
                        use_container_width=False,
                        help="Semantic relevance to your question (higher = stronger match)",
                    ):
                        st.session_state["active_story"] = item.get("id") or ""
                        st.session_state["active_story_title"] = item.get("title")
                        st.session_state["active_story_client"] = item.get("client")
                        st.session_state["show_ask_panel"] = True

                        # ➜ ADD THIS (one-shot lock)
                        st.session_state["__ctx_locked__"] = True

                        if stay_here:
                            # resolve and pin the selected story context
                            target = None
                            sid_norm = (item.get("id") or "").strip()
                            if sid_norm:
                                target = next(
                                    (
                                        x
                                        for x in stories
                                        if str(x.get("id")) == str(sid_norm)
                                    ),
                                    None,
                                )
                            if not target:
                                tgt_title = (item.get("title") or "").strip().lower()
                                tgt_client = (item.get("client") or "").strip().lower()
                                if tgt_title:
                                    for x in stories:
                                        xt = (x.get("title") or "").strip().lower()
                                        xc = (x.get("client") or "").strip().lower()
                                        if xt == tgt_title and (
                                            not tgt_client or xc == tgt_client
                                        ):
                                            target = x
                                            break
                            if not target:
                                lr = st.session_state.get("last_results") or []
                                for x in lr:
                                    cand = (
                                        x.get("story") if isinstance(x, dict) else None
                                    )
                                    if not isinstance(cand, dict):
                                        cand = x if isinstance(x, dict) else None
                                    if not isinstance(cand, dict):
                                        continue
                                    xid = str(
                                        cand.get("id") or cand.get("story_id") or ""
                                    ).strip()
                                    xt = (cand.get("title") or "").strip().lower()
                                    xc = (cand.get("client") or "").strip().lower()
                                    if (sid_norm and xid and xid == sid_norm) or (
                                        (
                                            item.get("title")
                                            and xt
                                            == (item.get("title") or "").strip().lower()
                                        )
                                        and (
                                            not item.get("client")
                                            or xc
                                            == (item.get("client") or "")
                                            .strip()
                                            .lower()
                                        )
                                    ):
                                        target = cand
                                        break
                            if target:
                                st.session_state["active_story_obj"] = target
                                st.session_state["answer_modes"] = story_modes(target)
                                cur = st.session_state.get("answer_mode", "narrative")
                                st.session_state["answer_mode"] = (
                                    cur
                                    if cur in ("narrative", "key_points", "deep_dive")
                                    else "narrative"
                                )
                                st.session_state["last_sources"] = [
                                    {
                                        "id": target.get("id")
                                        or target.get("story_id"),
                                        "title": target.get("title"),
                                        "client": target.get("client"),
                                    }
                                ]
                            else:
                                st.session_state["last_sources"] = [
                                    {
                                        "id": item.get("id") or item.get("story_id"),
                                        "title": item.get("title"),
                                        "client": item.get("client"),
                                    }
                                ]
                        else:
                            st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()
            batch = []

    st.markdown("</div>", unsafe_allow_html=True)


def render_no_match_banner(
    reason: str,
    query: str,
    overlap: float | None = None,
    suppressed: bool = False,
    filters: dict | None = None,
    *,
    key_prefix: str = "banner",
    context: str = "ask",  # "ask" or "explore"
):
    """
    Unified warning banner for 'no confident match' situations.

    Args:
        context: "ask" for Ask MattGPT (shows suggestion chips),
                 "explore" for Explore Stories (simpler message, no chips)
    """
    # Primary message — differentiate by intent family.
    # Reads from BANNER_COPY (LOCKED May 19, 2026 per MATTGPT-071). The
    # fallback string preserves the legacy catch-all for unknown reasons
    # (defensive — every known reason value has an explicit branch).
    if reason == "semantic_router:personal":
        msg = BANNER_COPY["personal"]
    elif reason == "semantic_router:out_of_scope":
        msg = BANNER_COPY["out_of_scope"]
    elif reason.startswith("rule:"):
        msg = BANNER_COPY["rule"]
    elif reason == "low_confidence":
        msg = BANNER_COPY["low_confidence"]
    else:
        msg = "🐾 I can't help with that. I'm trained on Matt's transformation work."

    # Add debug info if in debug mode
    debug_text = ""
    if DEBUG and reason:
        debug_text = f"Debug: {reason}"
        if overlap is not None:
            debug_text += f" (overlap={overlap:.2f})"

    st.markdown(
        """
        <style>
        /* Rejection banner — design spec per rejection_banner_wireframe.html
           (May 21, 2026). Three contracts:
             1. Chips render INSIDE the lavender bubble (containment fix).
             2. Responsive grid: 4 columns ≥1280px, 2 columns 768-1279px,
                1 column <768px.
             3. Text wraps with uniform chip height via flex centering +
                min-height — no truncation. */

        /* Bubble container — Streamlit container with key=
           {key_prefix}_rejection_bubble gets the lavender backdrop. Chips
           and banner text both render as children of this container.
           Uses --banner-info-* CSS variables from global_styles.py which
           carry both light- and dark-mode values automatically. */
        [class*='_rejection_bubble'] {
            background: var(--banner-info-bg);
            border-radius: 12px;
            padding: 14px 16px;
            margin: 16px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Banner text styling. Font size 16px for readability
           (HCD assessment May 22, 2026). */
        .no-match-banner-msg {
            color: var(--banner-info-text);
            font-weight: 500;
            font-size: 16px;
            line-height: 1.5;
            margin-bottom: 6px;
        }
        .no-match-banner-debug {
            color: var(--banner-info-text);
            font-size: 13px;
            opacity: 0.8;
            font-style: italic;
            margin-top: 8px;
        }
        .no-match-banner-hint {
            color: var(--banner-info-text);
            font-size: 13px;
            margin-top: 8px;
        }

        /* Chip grid — work WITH Streamlit's flex layout rather than
           overriding to grid (which May 22, 2026 visual test confirmed
           gets beaten by Streamlit's inline display:flex). Use flex-wrap
           on the row + flex-basis on each column to control responsive
           breakpoints (4 → 2 → 1).
           Default (≥1280px): 4 columns, each ~25% wide.
           1280-769px: wrap to 2 columns (50% each).
           ≤768px: wrap to 1 column (100%). */
        [class*='_chip_grid'] [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 8px !important;
        }
        [class*='_chip_grid'] [data-testid="stHorizontalBlock"] [data-testid="column"] {
            flex: 1 1 calc(25% - 8px) !important;
            min-width: 0 !important;
            max-width: none !important;
            width: auto !important;
        }
        @media (max-width: 1280px) {
            [class*='_chip_grid'] [data-testid="stHorizontalBlock"] [data-testid="column"] {
                flex-basis: calc(50% - 8px) !important;
            }
        }
        @media (max-width: 768px) {
            [class*='_chip_grid'] [data-testid="stHorizontalBlock"] [data-testid="column"] {
                flex-basis: 100% !important;
            }
        }

        /* Chip button — spec colors, text wrap, uniform height via
           min-height + flex centering. !important needed to override
           Streamlit's default secondary-button cascade. */
        /* Chip button — uses CSS variables so light/dark mode is handled
           automatically by global_styles.py. --bg-card flips white →
           dark-purple between modes; --banner-info-border flips purple
           shades to maintain contrast; --banner-info-text flips deep →
           light purple. No hardcoded hex anywhere. */
        [class*='_suggest_no_match_'] button {
            background: var(--bg-card) !important;
            border: 1px solid var(--banner-info-border) !important;
            color: var(--banner-info-text) !important;
            border-radius: 8px !important;
            padding: 9px 12px !important;
            font-family: 'Source Sans Pro', 'Source Sans 3', sans-serif !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            text-align: center !important;
            white-space: normal !important;
            min-height: 56px !important;
            width: 100% !important;
            line-height: 1.3 !important;
        }
        /* Lock inner text-element styling — Streamlit wraps button text
           in a <p> or <div> that carries its own theme-derived styles. */
        [class*='_suggest_no_match_'] button p,
        [class*='_suggest_no_match_'] button div {
            color: var(--banner-info-text) !important;
            font-family: 'Source Sans Pro', 'Source Sans 3', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            letter-spacing: normal !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Wrap banner text + chips in a single Streamlit container so chips
    # render INSIDE the lavender bubble (per wireframe spec). The container's
    # st-key class drives the bubble background; banner text and chip
    # widgets are children of the same container, visually contained.
    with st.container(key=f"{key_prefix}_rejection_bubble"):
        # Banner HTML — wrapped in <div class="no-match-banner"> as a
        # presence marker for BDD selectors (the lavender background comes
        # from the outer Streamlit container, not this inner div).
        banner_html = (
            f'<div class="no-match-banner">'
            f'<div class="no-match-banner-msg">{msg}</div>'
        )

        if debug_text:
            banner_html += f'<div class="no-match-banner-debug">{debug_text}</div>'

        # Ask MattGPT context: no hint text — chips speak for themselves.
        # Explore Stories context: branch-aware hint text (no chips render
        # there, so the hint is the only follow-up affordance).
        if context != "ask":
            if reason == "semantic_router:personal":
                banner_html += '<div class="no-match-banner-hint">Try searching for his transformation work, platform engineering, or how he builds teams.</div>'
            else:
                banner_html += '<div class="no-match-banner-hint">Try searching for clients, technologies, or project types from Matt\'s portfolio.</div>'

        banner_html += "</div>"
        st.markdown(banner_html, unsafe_allow_html=True)

        # Chips render INSIDE the bubble. Branch-aware chip selection;
        # low_confidence shows no chips (spec).
        if context == "ask" and reason != "low_confidence":
            if reason.startswith("rule:"):
                suggestions = RULE_CHIPS
            elif reason == "semantic_router:personal":
                suggestions = PERSONAL_CHIPS
            elif reason == "semantic_router:out_of_scope":
                suggestions = OUT_OF_SCOPE_CHIPS
            else:
                # Unknown reason — legacy generic chip set as defensive fallback
                suggestions = [
                    (
                        "Payments modernization",
                        "Tell me about your work modernizing payments platforms.",
                    ),
                    (
                        "Platform engineering & modernization",
                        "Tell me about your work modernizing platforms and engineering foundations.",
                    ),
                    (
                        "Cloud-native architecture",
                        "Tell me about your cloud-native architecture work.",
                    ),
                    (
                        "Innovation in digital products",
                        "Tell me about driving innovation in digital products.",
                    ),
                ]
            # Nested container so the chip-grid CSS Grid override scopes
            # only to these columns, not to other Streamlit columns on the
            # page.
            with st.container(key=f"{key_prefix}_chip_grid"):
                cols = st.columns(len(suggestions))
                for i, (label, prompt_text) in enumerate(suggestions):
                    with cols[i]:
                        if st.button(
                            label,
                            key=f"{key_prefix}_suggest_no_match_{i}_{hash(label) % 10000}",
                            use_container_width=True,
                        ):
                            st.session_state["__inject_user_turn__"] = prompt_text
                            st.session_state["__ask_from_suggestion__"] = True
                            st.session_state["__ask_force_answer__"] = True
                            st.session_state["ask_input"] = prompt_text
                            st.session_state["__clear_banner_after_answer__"] = True
                            st.rerun()
