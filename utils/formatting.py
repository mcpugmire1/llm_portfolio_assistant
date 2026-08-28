"""Story formatting utilities - summaries, narratives, key points.

This module provides utilities for formatting story data into various presentation
modes: 5P summaries, key points, narratives, and deep dives. Includes metric
extraction and quantitative impact detection.
"""

import re
from typing import Any

# Metric detection pattern.
# MATTGPT-215 (Aug 27, 2026) widened to fix two capture bugs surfaced by the
# sidebar Key Metrics audit:
#   1. Decimal percentages: old \b\d{1,3}\s?% matched only "9%" of "99.9%"
#      because "." broke the word boundary. Added optional (?:\.\d+)?.
#   2. Currency with unit suffix: old \$\s?\d[\d,\.]*\b failed on "$100M+"
#      because \b after [\d,\.]* required a word boundary and letter M
#      is a word char. Added optional [KMB]?[+]? tail.
# Corpus-wide dry-run against real Performance/Result bullets: 35 strings
# improve (decimal precision restored, currency-with-unit captured), zero
# regressions (widened pattern is a strict superset of the previous form).
# See probe_215_metric_rx_widening.py for the runnable measurement; re-run
# after any further METRIC_RX change to confirm the direction still holds.
METRIC_RX = re.compile(
    r"(\b\d{1,3}(?:\.\d+)?\s?%|\$\s?\d[\d,\.]*[KMB]?[+]?|\b\d+x\b|\b\d+(?:\.\d+)?\s?(pts|pp|bps)\b)",
    re.I,
)


def story_has_metric(s: dict[str, Any]) -> bool:
    """Check if story contains quantified metrics.

    Searches both "what" and "star.result" fields for numeric metrics like
    percentages (50%), dollar amounts ($1M), multipliers (3x), or basis points (10bps).

    Args:
        s: Story dictionary with fields:
            - what (list[str], optional): Performance/outcome bullets
            - star.result (list[str], optional): STAR result bullets

    Returns:
        True if any metric pattern is found, False otherwise.

    Example:
        >>> story = {"what": ["Reduced latency by 60%"]}
        >>> story_has_metric(story)
        True
        >>> story = {"what": ["Improved team collaboration"]}
        >>> story_has_metric(story)
        False
    """
    for line in s.get("what") or []:
        if METRIC_RX.search(line or ""):
            return True
    for line in s.get("star", {}).get("result") or []:
        if METRIC_RX.search(line or ""):
            return True
    return False


def strongest_metric_line(s: dict[str, Any]) -> str | None:
    """Extract the most impactful metric from a story.

    Scans "what" and "star.result" fields for numeric metrics, scores each
    metric by magnitude (percentages get +1000 bonus), and returns the full
    text of the line containing the highest-scored metric.

    Args:
        s: Story dictionary with fields:
            - what (list[str], optional): Performance/outcome bullets
            - star.result (list[str], optional): STAR result bullets

    Returns:
        Full text of the line with the strongest metric, or None if no
        metrics found.

    Example:
        >>> story = {"what": ["Reduced cost by 50%", "Deployed 3x faster"]}
        >>> strongest_metric_line(story)
        'Reduced cost by 50%'
    """
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


def build_5p_summary(s: dict[str, Any], max_chars: int = 220) -> str:
    """Build neutral, recruiter-friendly one-liner summary.

    Creates a structured summary in the format:
    "Goal: <why>. Approach: <top 1-2 how>. Outcome: <strongest metric>."

    Prefers curated 5PSummary field if present; otherwise composes from
    story fields (why, how, what). Falls back to generic text if fields missing.

    Args:
        s: Story dictionary with fields:
            - 5PSummary/5p_summary (str, optional): Pre-written summary
            - why (str, optional): Purpose/goal
            - how (list[str], optional): Approach bullets (uses first 2)
            - what (list[str], optional): Outcome bullets
            - star.result (list[str], optional): STAR result bullets
        max_chars: Maximum character length for output. Truncates with ellipsis
            if exceeded. Defaults to 220 for list view cells.

    Returns:
        Formatted summary string, truncated to max_chars if necessary.

    Example:
        >>> story = {"why": "Modernize platform", "how": ["Migrated to AWS"],
        ...          "what": ["Reduced costs by 40%"]}
        >>> build_5p_summary(story, 100)
        'Goal: Modernize platform. Approach: Migrated to AWS. Outcome: Reduced costs by 40%.'
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


def _format_key_points(s: dict[str, Any]) -> str:
    """Format story as 3-4 bullet points covering scope, approach, outcomes.

    Creates a concise bullet list with:
    - Scope: Title and client
    - Approach: Top 2 "how" bullets
    - Outcome: Strongest metric or first "what" bullet
    - Domain: Sub-category

    Args:
        s: Story dictionary with fields:
            - title (str): Story title
            - client (str): Client name
            - how (list[str], optional): Approach bullets
            - what (list[str], optional): Outcome bullets
            - Sub-category (str, optional): Domain

    Returns:
        Formatted markdown string with 3-4 bullet points.

    Example:
        >>> story = {"title": "Platform Modernization", "client": "JPMC",
        ...          "how": ["Migrated to AWS"], "what": ["Reduced costs 40%"]}
        >>> print(_format_key_points(story))
        - **Scope:** Platform Modernization — JPMC
        - **Approach:** Migrated to AWS
        - **Outcome:** Reduced costs 40%
    """
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


def _extract_metric_value(text: str) -> tuple[float, str] | None:
    """Extract numeric metric value from text with scoring.

    Searches text for metrics using METRIC_RX pattern, assigns a numeric score
    based on magnitude (percentages get +1000 bonus to rank higher), and
    returns the highest-scored metric found.

    Args:
        text: Text to search for metrics (e.g., "Reduced latency by 60%").

    Returns:
        Tuple of (score, full_text) for the best metric found, or None if no
        metrics detected. Score is float (percentages: 1000 + value, others: value).

    Example:
        >>> _extract_metric_value("Reduced cost by 50%")
        (1050.0, 'Reduced cost by 50%')
        >>> _extract_metric_value("Deployed 3x faster")
        (3.0, 'Deployed 3x faster')
        >>> _extract_metric_value("No metrics here")
        None
    """
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


def _extract_metric_display(perf: str, label_max: int = 50) -> tuple[str, str] | None:
    """Extract metric value + display label from a Performance bullet.

    Returns None if the text contains no metric marker (percentage, currency,
    multiplier, pts/pp/bps). Otherwise returns (value, label):

    - value: the raw METRIC_RX match token (e.g., "99.9%", "$100M+", "4x")
    - label: the source text stripped of any leading "- " bullet prefix,
      truncated at the last word boundary within label_max characters

    For strings with multiple metric matches, returns the first match's
    token as value (leftmost is typically the primary claim).

    Ticket: MATTGPT-215. Replaces the buggy inline heuristic in
    story_detail.py's Key Metrics sidebar section, which extracted a bare
    number and 50-char hard-cut label from any string containing "x",
    "month", "week", or "%" as substrings.
    """
    if not perf or not perf.strip():
        return None
    match = METRIC_RX.search(perf)
    if not match:
        return None
    value = match.group(0)
    # Strip leading "- " bullet prefix (Excel authoring convention on
    # Performance) so the truncation window isn't wasted on the marker.
    label = perf.lstrip()
    if label.startswith("- "):
        label = label[2:]
    label = label.strip()
    if len(label) > label_max:
        cut = label[:label_max]
        last_space = cut.rfind(" ")
        if last_space > 0:
            label = cut[:last_space].rstrip()
        else:
            label = cut
    return value, label


def _format_narrative(s: dict[str, Any]) -> str:
    """Format story as 1-paragraph recruiter-friendly narrative.

    Creates a flowing paragraph with structure:
    "I led [Title] at [Client] in [Domain]. The aim was [goal].
    We focused on [approach]. Impact: [strongest metric]."

    For Professional Narrative stories (biographical/philosophical content),
    uses the 5PSummary directly instead of the "I led X at Y" template.

    Args:
        s: Story dictionary with fields:
            - Title (str): Story title
            - Client (str): Client name
            - Theme (str, optional): Story theme (checks for "Professional Narrative")
            - Sub-category (str, optional): Domain
            - why (str, optional): Purpose/goal
            - how (list[str], optional): Approach bullets (uses first 2)
            - what (list[str], optional): Outcome bullets for metrics

    Returns:
        Formatted narrative paragraph in markdown. Falls back to 5P summary
        if insufficient fields available.

    Example:
        >>> story = {"Title": "Platform Modernization", "Client": "JPMC",
        ...          "Sub-category": "Cloud-Native Architecture",
        ...          "why": "Reduce infrastructure costs",
        ...          "how": ["Migrated to AWS", "Implemented auto-scaling"],
        ...          "what": ["Reduced costs by 40%"]}
        >>> _format_narrative(story)
        'I led **Platform Modernization** at **JPMC** in **Cloud-Native Architecture**. The aim was reduce infrastructure costs. We focused on migrated to AWS, implemented auto-scaling. Impact: **Reduced costs by 40%**.'
    """
    # Professional Narrative stories - use summary directly, not "I led X at Y"
    if s.get("Theme") == "Professional Narrative":
        summary = s.get("5PSummary") or s.get("5p_summary") or ""
        if summary:
            return summary
        # Fall through to 5P summary builder if no summary field
        return build_5p_summary(s, 300)

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


def _format_deep_dive(s: dict[str, Any]) -> str:
    """Format story as detailed STAR breakdown without explicit labels.

    Creates a structured deep-dive with friendly section headers:
    - "What was happening" (Situation)
    - "Goal" (Task)
    - "What we did" (Action)
    - "Results" (Result)

    Args:
        s: Story dictionary with fields:
            - star (dict): STAR structure with optional fields:
                - situation (list[str]): Context bullets
                - task (list[str]): Goal/objective bullets
                - action (list[str]): Approach bullets
                - result (list[str]): Outcome bullets

    Returns:
        Formatted markdown string with sections separated by double newlines.
        Falls back to 5P summary if no STAR fields available.

    Example:
        >>> story = {"star": {
        ...     "situation": ["Legacy monolith causing delays"],
        ...     "task": ["Modernize to microservices"],
        ...     "action": ["Migrated to AWS", "Implemented CI/CD"],
        ...     "result": ["Reduced deployment time by 80%"]
        ... }}
        >>> print(_format_deep_dive(story))
        **What was happening**
        - Legacy monolith causing delays

        **Goal**
        - Modernize to microservices

        **What we did**
        - Migrated to AWS
        - Implemented CI/CD

        **Results**
        - Reduced deployment time by 80%
    """
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


# =============================================================================
# Tag normalization helpers (MATTGPT-216: moved from generate_public_tags.py
# so tests can exercise pure functions without triggering the script's eager
# OpenAI() client construction at module load. The script imports these
# helpers from here; behavior is unchanged.)
# =============================================================================

_SMALL_WORDS = {"and", "or", "the", "a", "an", "of", "for", "in", "to", "with"}


def _strip_paren_acronym(tag: str) -> str:
    """Collapse "phrase (ACRONYM)" tags to just the acronym.

    "large language models (LLM)" -> "LLM"
    "enterprise service bus (ESB)" -> "ESB"

    Fires only when the parenthetical at the end is a short all-caps token
    (acronym pattern). Non-acronym parentheticals are left alone.
    """
    m = re.match(r"^.+\s+\(([A-Z]{2,}[A-Z0-9]*)\)$", tag.strip())
    return m.group(1) if m else tag


def _normalize_tag_case(tag: str) -> str:
    """Title-case each word, preserving acronyms and mixed-case proper nouns.

    - "agile transformation" -> "Agile Transformation"
    - "AWS" -> "AWS" (all-caps preserved)
    - "DevOps" -> "DevOps" (any uppercase char -> preserve)
    - "cross-functional collaboration" -> "Cross-Functional Collaboration"
    - "CI/CD pipelines" -> "CI/CD Pipelines"
    - "Docker And Kubernetes" -> "Docker and Kubernetes" (standard title case)
    - "And Docker" -> "And Docker" (small word capitalized when first)

    Splits on spaces first, then further on hyphens and slashes so acronyms
    around those separators are preserved individually (CI/CD, cross-XYZ).
    Small words (and, or, the, a, an, of, for, in, to, with) are lowercased
    unless they are the first token of the tag; check applies to hyphen and
    slash segments too, so "Cross-And-Effect" -> "Cross-and-Effect". Small-word
    override wins over uppercase preservation, so "Docker AND Kubernetes"
    still normalizes to "Docker and Kubernetes".

    Rule is otherwise "preserve anything with an uppercase char" rather than
    "title-case unless all-caps" -- means a half-cased LLM output like "agile
    Transformation" stays half-cased. Not seen in practice; the models return
    either all-lower or already-cased.
    """

    def _norm_token(t: str, *, is_first: bool) -> str:
        if not t:
            return t
        if not is_first and t.lower() in _SMALL_WORDS:
            return t.lower()
        if any(c.isupper() for c in t):
            return t  # acronym or proper noun preserved
        return t[0].upper() + t[1:].lower()

    result_words = []
    first_seen = False
    for word in tag.split():
        parts = re.split(r"([-/])", word)
        out = []
        for p in parts:
            if p in "-/" or not p:
                out.append(p)
                continue
            out.append(_norm_token(p, is_first=not first_seen))
            first_seen = True
        result_words.append("".join(out))
    return " ".join(result_words)


def _drop_restated_fields(tags: list[str], story: dict) -> list[str]:
    """Drop tags that exactly restate the story's Industry, Sub-category,
    Category, or Project (case-insensitive).

    Those fields are separately filterable in the UI, so a tag that repeats
    them is a duplicate route to the same story and a wasted slot out of 15.
    Verified: "telecommunications" on a story whose Industry is
    Telecommunications; "career narrative" on a story whose Project is
    Career Narrative.
    """
    restated = {
        str(story.get(f, "") or "").strip().lower()
        for f in ("Industry", "Sub-category", "Category", "Project")
    }
    restated.discard("")
    return [t for t in tags if t.strip().lower() not in restated]


def _dedupe_title_case_wins(tags: list[str]) -> list[str]:
    """Case-insensitive dedup preferring the more uppercase-heavy variant.

    When two tags collide case-insensitively, keep the one with more uppercase
    characters. Handles both title-case-vs-lowercase ("Client Engagement" over
    "client engagement") and acronyms ("AWS" over "aws"). Ties keep first-seen.

    Known edge case: proper nouns whose official style is title case rather than
    all-caps -- e.g., Atlassian styles it "Jira", not "JIRA". This heuristic
    would pick "JIRA" over "Jira" (4 vs 1 uppercase). The master corpus is
    curated to the correct form; this note exists so a future generator run
    that emits both variants is understood as a known limitation, not a bug.
    """
    by_lower: dict[str, str] = {}
    for tag in tags:
        key = tag.lower()
        if key not in by_lower:
            by_lower[key] = tag
            continue
        current_upper = sum(1 for c in by_lower[key] if c.isupper())
        new_upper = sum(1 for c in tag if c.isupper())
        if new_upper > current_upper:
            by_lower[key] = tag
    return list(by_lower.values())


def _prompt_view(story: dict) -> dict:
    """The exact fields and projections the tag prompt reads.

    Returned by field name (e.g., "Project Scope / Complexity", "Use Case(s)")
    so change-detection can key lookups against the raw story dict. The tag
    prompt renders labels from this view.
    """
    return {
        "Era": story.get("Era", ""),
        "Title": story.get("Title", ""),
        "Role": story.get("Role", ""),
        "Industry": story.get("Industry", ""),
        "Theme": story.get("Theme", ""),
        "Category": story.get("Category", ""),
        "Sub-category": story.get("Sub-category", ""),
        "Project Scope / Complexity": story.get("Project Scope / Complexity", ""),
        "Competencies": story.get("Competencies", ""),
        "Use Case(s)": story.get("Use Case(s)", ""),
        "Situation": " ".join(story.get("Situation") or []),
        "Task": " ".join(story.get("Task") or []),
        "Action": " ".join(story.get("Action") or []),
        "Result": " ".join(story.get("Result") or []),
        "Process": " ".join(story.get("Process") or []),
        "Performance": " ".join(story.get("Performance") or []),
    }
