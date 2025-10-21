"""UI helper utilities - containers, debug output."""

import streamlit as st
from config.debug import DEBUG
import streamlit as st
from typing import Optional
from utils.formatting import _format_narrative, _format_key_points, _format_deep_dive
import os, re, time, textwrap, json


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
    sources: list[dict], *, title: str = "Sources", key_prefix: str = "srcbad_", stories: list,
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
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, (int, float)) else None

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
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, (int, float)) else None
        label = f"{pct} Match • {short}" if pct else short
        return label, safe_id

    for i, s in enumerate(items, 1):
        batch.append(s)
        if len(batch) == per_row or i == len(items):
            cols = container.columns(len(batch))
            for col, item in zip(cols, batch):
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
):
    """
    Unified yellow warning banner for 'no confident match' situations.
    Always shows a consistent message, suggestions, and optionally a Clear Filters button.
    """
    msg = "I couldn’t find anything confidently relevant to that query."
    debug_note = ""
    if DEBUG and reason:
        debug_note = f"  \n_Reason: {reason}"
        if overlap is not None:
            debug_note += f" (overlap={overlap:.2f})"
        debug_note += "_"
    msg += debug_note
    st.warning(msg)

    # Chips act as clean semantic prompts (no tag/domain filters)
    suggestions = [
        (
            "Payments modernization",
            "Tell me about your work modernizing payments platforms.",
        ),
        (
            "Generative AI in healthcare",
            "Tell me about applying Generative AI in healthcare.",
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
    cols = st.columns(len(suggestions))
    for i, (label, prompt_text) in enumerate(suggestions):
        with cols[i]:
            if st.button(
                label, key=f"{key_prefix}_suggest_no_match_{i}_{hash(label)%10000}"
            ):
                # Inject a new user turn with a concise prompt; rely on semantic search only
                st.session_state["__inject_user_turn__"] = prompt_text
                # Mark that this came from a suggestion chip to relax off-domain gating once
                st.session_state["__ask_from_suggestion__"] = True
                # Guarantee we build a compact answer panel even if retrieval is empty
                st.session_state["__ask_force_answer__"] = True
                st.session_state["ask_input"] = prompt_text
                st.session_state["active_tab"] = "Ask MattGPT"
                # Defer banner clearing to after a successful answer, avoiding duplicates
                st.session_state["__clear_banner_after_answer__"] = True
                st.rerun()

    # Show Clear Filters button if filters exist and are non-empty
    if filters:
        # Check if any filter is set (excluding 'q' and 'has_metric' for len check)
        any_active = any(
            (isinstance(v, list) and v)
            or (isinstance(v, str) and v.strip())
            or (isinstance(v, bool) and v)
            for k, v in filters.items()
            if k
            in ["personas", "clients", "domains", "roles", "tags", "has_metric", "q"]
        )
        if any_active:
            if st.button("Clear filters", key=f"{key_prefix}_clear_filters_no_match"):
                st.session_state["filters"] = {
                    "personas": [],
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                    "q": "",
                    "has_metric": False,
                }
                st.session_state["facet_domain_group"] = "All"
                st.session_state["page_offset"] = 0
                st.rerun()