"""
Utility Functions for Ask MattGPT

Shared helper functions for story selection, transcript management,
and UI component rendering.
"""

import re

import streamlit as st

from config.debug import DEBUG
from utils.formatting import (
    _format_deep_dive,
    _format_key_points,
    _format_narrative,
    build_5p_summary,
)

# ========== STORY HELPERS ==========


def get_context_story(stories: list[dict]) -> dict | None:
    """
    Get the active context story from session state.

    Tries multiple fallback strategies to resolve the story:
    1. Explicit story object
    2. Story ID lookup
    3. Title/client match
    4. Substring match
    5. Last results payload

    Args:
        stories: All available stories

    Returns:
        Story dict or None
    """
    # Highest priority: explicitly stored story object
    obj = st.session_state.get("active_story_obj")
    if isinstance(obj, dict) and (obj.get("id") or obj.get("Title")):
        return obj

    # Try story ID lookup
    sid = st.session_state.get("active_story")
    if sid:
        for s in stories:
            if str(s.get("id")) == str(sid):
                return s

    # Fallback: match by title/client
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()

    if at:
        # Exact match
        for s in stories:
            stitle = (s.get("Title") or "").strip().lower()
            sclient = (s.get("Client") or "").strip().lower()
            if stitle == at and (not ac or sclient == ac):
                return s

        # Substring match
        for s in stories:
            stitle = (s.get("Title") or "").strip().lower()
            if at in stitle or stitle in at:
                return s

    # Last resort: check last_results payloads
    lr = st.session_state.get("last_results") or []
    for x in lr:
        if not isinstance(x, dict):
            continue
        cand = x.get("story") if isinstance(x.get("story"), dict) else x
        if not isinstance(cand, dict):
            continue
        xid = str(cand.get("id") or cand.get("story_id") or "").strip()
        xt = (cand.get("Title") or "").strip().lower()
        xc = (cand.get("Client") or "").strip().lower()
        if (sid and xid and str(xid) == str(sid)) or (
            at and xt == at and (not ac or xc == ac)
        ):
            return cand

    return None


def choose_story_for_ask(top_story: dict | None, stories: list[dict]) -> dict | None:
    """
    Choose which story to use for Ask MattGPT.

    Prefer Pinecone top result unless a one-shot context lock is set.

    Args:
        top_story: Top-ranked story from semantic search
        stories: All stories

    Returns:
        Selected story or None
    """
    if st.session_state.get("__ctx_locked__"):
        ctx = get_context_story(stories)
        return ctx or top_story
    return top_story


def story_modes(s: dict) -> dict:
    """
    Return the three presentation modes for a single story.

    Args:
        s: Story dictionary

    Returns:
        Dict with keys: narrative, key_points, deep_dive
    """
    return {
        "narrative": _format_narrative(s),
        "key_points": _format_key_points(s),
        "deep_dive": _format_deep_dive(s),
    }


def related_stories(s: dict, stories: list[dict], max_items: int = 3) -> list[dict]:
    """
    Find related stories using simple heuristic.

    Scoring:
    - Same client: +3
    - Same sub-category: +2
    - Shared tags: +1 per tag

    Args:
        s: Current story
        stories: All stories
        max_items: Maximum number to return

    Returns:
        List of related story dicts
    """
    cur_id = s.get("id")
    dom = s.get("Sub-category", "")
    client = s.get("Client", "")
    tags = set(s.get("tags", []) or [])

    scored = []
    for t in stories:
        if t.get("id") == cur_id:
            continue
        score = 0
        if client and t.get("Client") == client:
            score += 3
        if dom and t.get("Sub-category") == dom:
            score += 2
        if tags:
            score += len(tags & set(t.get("tags", []) or []))
        if score:
            scored.append((score, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:max_items]]


def story_has_metric(s: dict) -> bool:
    """
    Check if story has quantifiable metrics.

    Args:
        s: Story dictionary

    Returns:
        True if metrics found
    """
    perf = s.get("Performance", [])
    if isinstance(perf, list):
        text = " ".join(str(p) for p in perf)
    else:
        text = str(perf or "")

    # Look for numbers, percentages, time periods
    has_numbers = bool(
        re.search(r'\d+[%xX]|\d+\s*(?:days?|weeks?|months?|years?)', text)
    )
    return has_numbers


# ========== TRANSCRIPT MANAGEMENT ==========


def push_user_turn(text: str):
    """
    Add user message to Ask MattGPT transcript.

    Args:
        text: User's message
    """
    st.session_state["ask_transcript"].append({"role": "user", "text": text})
    st.session_state["__asked_once__"] = True


def push_assistant_turn(text: str):
    """
    Add assistant message to Ask MattGPT transcript.

    Args:
        text: Assistant's message
    """
    st.session_state["ask_transcript"].append({"role": "assistant", "text": text})


def push_conversational_answer(
    answer_text: str, sources: list[dict], query_intent: str | None = None
):
    """
    Add conversational AI response to transcript with sources.

    Args:
        answer_text: Agy's response
        sources: Related story sources
        query_intent: Intent type ("synthesis", "client", etc.) for card rendering
    """
    st.session_state["ask_transcript"].append(
        {
            "type": "conversational",
            "Role": "assistant",
            "text": answer_text,
            "sources": sources,
            "query_intent": query_intent,
        }
    )


def push_card_snapshot_from_state(stories: list[dict]):
    """
    Append a static answer card snapshot to transcript from current state.

    Args:
        stories: All stories (for ID lookup)
    """
    modes = st.session_state.get("answer_modes", {}) or {}
    sources = st.session_state.get("last_sources", []) or []
    sel = st.session_state.get("answer_mode", "narrative")

    if not sources:
        return

    sid = str(sources[0].get("id", ""))
    primary = next((s for s in stories if str(s.get("id")) == sid), None)

    if not primary:
        return

    content_md = modes.get(sel) if modes else st.session_state.get("last_answer", "")

    # Capture confidence scores
    scores = st.session_state.get("__pc_last_ids__", {}) or {}
    confidence = scores.get(sid)

    if DEBUG:
        print(f"DEBUG _push_card_snapshot: sid={sid}, confidence={confidence}")

    # Store confidence for all sources
    source_confidences = {}
    for src in sources:
        src_id = str(src.get("id", ""))
        if src_id in scores:
            source_confidences[src_id] = scores[src_id]

    entry = {
        "type": "card",
        "story_id": primary.get("id"),
        "title": primary.get("Title"),
        "one_liner": build_5p_summary(primary, 9999),
        "content": content_md,
        "sources": sources,
        "confidence": confidence,
        "source_confidences": source_confidences,
    }

    st.session_state["ask_transcript"].append(entry)


def clear_ask_context():
    """Remove sticky story context for next general-purpose Ask."""
    st.session_state.pop("active_story", None)
    st.session_state.pop("__ctx_locked__", None)
    st.session_state.pop("seed_prompt", None)
    st.rerun()


# ========== FORMATTING HELPERS ==========


def split_tags(s):
    """
    Split comma-separated tags into list.

    Args:
        s: Tag string or list

    Returns:
        List of tag strings
    """
    if not s:
        return []
    if isinstance(s, list):
        return [str(x).strip() for x in s if str(x).strip()]
    return [t.strip() for t in str(s).split(",") if t.strip()]


def slug(s):
    """
    Create URL-safe slug from string.

    Args:
        s: Input string

    Returns:
        Slugified string
    """
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-") or "x"


def shorten_middle(text: str, max_len: int = 50) -> str:
    """
    Shorten text by replacing middle with ellipsis.

    Args:
        text: Input text
        max_len: Maximum length

    Returns:
        Shortened text
    """
    if len(text) <= max_len:
        return text

    keep = (max_len - 3) // 2
    return f"{text[:keep]}...{text[-keep:]}"


def ensure_ask_bootstrap():
    """Guarantee the Ask transcript starts with assistant opener once per session."""
    if "ask_transcript" not in st.session_state:
        st.session_state["ask_transcript"] = []
    if not st.session_state["ask_transcript"]:
        st.session_state["ask_input_value"] = ""


def is_empty_conversation() -> bool:
    """
    Check if conversation is empty (should show landing page).

    Returns:
        True if conversation is empty or only has bootstrap message
    """
    transcript = st.session_state.get("ask_transcript", [])

    # Empty transcript
    if not transcript:
        return True

    # Only has bootstrap "Ask anything." message
    if len(transcript) == 1 and transcript[0].get("text") == "Ask anything.":
        return True

    return False
