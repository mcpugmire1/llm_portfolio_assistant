"""Story formatting utilities - summaries, narratives, key points."""

import re
from typing import Optional

# Metric detection pattern
METRIC_RX = re.compile(
    r"(\b\d{1,3}\s?%|\$\s?\d[\d,\.]*\b|\b\d+x\b|\b\d+(?:\.\d+)?\s?(pts|pp|bps)\b)", re.I
)

def story_has_metric(s):
    """Check if story contains quantified metrics."""
    for line in s.get("what") or []:
        if METRIC_RX.search(line or ""):
            return True
    for line in s.get("star", {}).get("result") or []:
        if METRIC_RX.search(line or ""):
            return True
    return False

def strongest_metric_line(s: dict) -> Optional[str]:
    """Extract the most impactful metric from a story."""
    candidates = []
    for line in s.get("what") or []:
        v = _extract_metric_value(line or "")
        if v:
            candidates.append(v)
    for line in s.get("star", {}).get("result") or []:
        v = _extract_metric_value(line or "")
        if v:
            candidates.append(v)
    if not candidates:
        return None
    return max(candidates, key=lambda t: t[0])[1]

def build_5p_summary(s: dict, max_chars: int = 220) -> str:
    """
    Neutral, recruiter-friendly one-liner:
    Goal: <why>. Approach: <top 1-2 how>. Outcome: <strongest metric>.
    Uses curated 5PSummary if present; otherwise composes a clean line.
    """
    curated = (s.get("5PSummary") or s.get("5p_summary") or "").strip()
    if curated:
        # Keep curated text, but trim if super long for list views
        return (
            curated if len(curated) <= max_chars else (curated[: max_chars - 1] + "…")
        )

    goal = (s.get("why") or "").strip().rstrip(".")
    approach = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric_line = strongest_metric_line(s)
    outcome = (metric_line or "").strip().rstrip(".")

    parts = []
    if goal:
        parts.append(f"**Goal:** {goal}.")
    if approach:
        parts.append(f"**Approach:** {approach}.")
    if outcome:
        parts.append(f"**Outcome:** {outcome}.")

    text = " ".join(parts).strip()
    if not text:
        # last resort, try WHAT list
        what = "; ".join(s.get("what", [])[:2])
        text = what or "Impact-focused delivery across stakeholders."

    # Clamp for compact list cells
    return text if len(text) <= max_chars else (text[: max_chars - 1] + "…")

def _format_key_points(s: dict) -> str:
    """3–4 bullets: scope, approach, outcomes."""
    metric = strongest_metric_line(s)
    lines = []
    lines.append(f"- **Scope:** {s.get('title','')} — {s.get('client','')}".strip(" —"))
    top_how = (s.get("how") or [])[:2]
    if top_how:
        lines.append("- **Approach:** " + " / ".join(top_how))
    outs = s.get("what") or []
    if metric:
        lines.append(f"- **Outcome:** {metric}")
    elif outs:
        lines.append(f"- **Outcome:** {outs[0]}")
    dom = s.get("Sub-category")  # Use JSONL field name
    if dom:
        lines.append(f"- **Domain:** {dom}")
    return "\n".join(lines)


def _extract_metric_value(text: str):
    """Extract numeric metric value from text."""
    if not text:
        return None
    best = None
    for m in METRIC_RX.finditer(text):
        tok = m.group(0)
        if "%" in tok:
            try:
                num = float(tok.replace("%", "").strip())
            except Exception:
                num = 0.0
            score = 1000 + num
        else:
            digits = "".join([c for c in tok if c.isdigit() or c == "."])
            try:
                num = float(digits)
            except Exception:
                num = 0.0
            score = num
        item = (score, text)
        if best is None or item[0] > best[0]:
            best = item
    return best

def _format_narrative(s: dict) -> str:
    """1-paragraph, recruiter-friendly narrative from a single story."""
    title = s.get("Title", "")
    client = s.get("Client", "")
    domain = s.get("Sub-category", "")
    goal = (s.get("why") or "").strip().rstrip(".")
    how = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric = strongest_metric_line(s)
    bits = []
    if title or client:
        bits.append(
            f"I led **{title}** at **{client}**"
            if title
            else f"I led work at **{client}**"
        )
    if domain:
        bits[-1] += f" in **{domain}**."
    if goal:
        bits.append(f"The aim was {goal.lower()}.")
    if how:
        bits.append(f"We focused on {how.lower()}.")
    if metric:
        bits.append(f"Impact: **{metric}**.")
    return " ".join(bits) or build_5p_summary(s, 280)

def _format_deep_dive(s: dict) -> str:
    """Detail without saying STAR/5P explicitly: What was happening / Goal / What we did / Results."""
    st_blocks = s.get("star", {}) or {}
    situation = st_blocks.get("situation") or []
    task = st_blocks.get("task") or []
    action = st_blocks.get("action") or []
    result = st_blocks.get("result") or []
    parts = []
    if situation:
        parts.append(
            "**What was happening**\n" + "\n".join([f"- {x}" for x in situation])
        )
    if task:
        parts.append("**Goal**\n" + "\n".join([f"- {x}" for x in task]))
    if action:
        parts.append("**What we did**\n" + "\n".join([f"- {x}" for x in action]))
    if result:
        parts.append("**Results**\n" + "\n".join([f"- {x}" for x in result]))
    return "\n\n".join(parts) or build_5p_summary(s, 320)


# Add to utils/formatting.py

def _format_narrative(s: dict) -> str:
    """1-paragraph, recruiter-friendly narrative from a single story."""
    title = s.get("Title", "")
    client = s.get("Client", "")
    domain = s.get("Sub-category", "")
    goal = (s.get("why") or "").strip().rstrip(".")
    how = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric = strongest_metric_line(s)
    
    bits = []
    if title or client:
        bits.append(
            f"I led **{title}** at **{client}**"
            if title
            else f"I led work at **{client}**"
        )
    if domain:
        bits[-1] += f" in **{domain}**."
    if goal:
        bits.append(f"The aim was {goal.lower()}.")
    if how:
        bits.append(f"We focused on {how.lower()}.")
    if metric:
        bits.append(f"Impact: **{metric}**.")
    
    return " ".join(bits) or build_5p_summary(s, 280)


def _format_deep_dive(s: dict) -> str:
    """Detail without saying STAR/5P explicitly: What/Goal/Actions/Results."""
    st_blocks = s.get("star", {}) or {}
    situation = st_blocks.get("situation") or []
    task = st_blocks.get("task") or []
    action = st_blocks.get("action") or []
    result = st_blocks.get("result") or []
    
    parts = []
    if situation:
        parts.append(
            "**What was happening**\n" + "\n".join([f"- {x}" for x in situation])
        )
    if task:
        parts.append("**Goal**\n" + "\n".join([f"- {x}" for x in task]))
    if action:
        parts.append("**What we did**\n" + "\n".join([f"- {x}" for x in action]))
    if result:
        parts.append("**Results**\n" + "\n".join([f"- {x}" for x in result]))
    
    return "\n\n".join(parts) or build_5p_summary(s, 320)