"""
Story Intelligence - Theme inference and context building for Agy V2

Maps Sub-category to the 6 Themes and builds theme-aware context for RAG.
Provides theme-specific voice guidance for Agy's response generation.
"""

from collections import Counter
from typing import Any

# The 7 Themes (constants for consistency)
THEME_EXECUTION = "Execution & Delivery"
THEME_STRATEGIC = "Strategic & Advisory"
THEME_ORG_TRANSFORM = "Org & Working-Model Transformation"
THEME_TALENT = "Talent & Enablement"
THEME_RISK = "Risk & Responsible Tech"
THEME_EMERGING = "Emerging Tech"
THEME_PROFESSIONAL = "Professional Narrative"

# Default theme when not specified in story data
DEFAULT_THEME = THEME_EXECUTION

# Pattern phrases for synthesis mode - prevents voice drift to theme names
THEME_TO_PATTERN = {
    THEME_EXECUTION: "He ships.",
    THEME_STRATEGIC: "He advises.",
    THEME_ORG_TRANSFORM: "He transforms how teams work.",
    THEME_TALENT: "He builds people.",
    THEME_RISK: "He manages risk.",
    THEME_EMERGING: "He explores pragmatically.",
    THEME_PROFESSIONAL: "He knows who he is.",
}


def infer_story_theme(story: dict[str, Any]) -> str:
    """Get the theme for a story from its Theme field.

    Args:
        story: Story dictionary with metadata. Expected fields:
            - Theme (str): The story's theme
            - Other story fields (Title, Client, etc.)

    Returns:
        The story's Theme field, or THEME_EXECUTION as default.

    Example:
        >>> story = {"Theme": "Talent & Enablement", "Client": "JPMC"}
        >>> infer_story_theme(story)
        'Talent & Enablement'
    """
    return story.get("Theme", THEME_EXECUTION)


def get_theme_guidance(theme: str) -> str:
    """Get Agy voice guidance for a specific theme.

    Provides framing instructions that guide Agy's tone, positioning, and
    emphasis when discussing stories from this theme. Used in system prompts
    for _generate_agy_response().

    Args:
        theme: One of the 7 canonical theme strings (THEME_* constants).
            Examples: "Execution & Delivery", "Strategic & Advisory", etc.

    Returns:
        Multi-line voice guidance text formatted for inclusion in system prompts.
        Includes emphasis points, voice patterns, positioning, proof points,
        and thematic patterns. Falls back to THEME_EXECUTION guidance if
        theme is unrecognized.

    Example:
        >>> guidance = get_theme_guidance("Talent & Enablement")
        >>> "capability building" in guidance.lower()
        True
    """
    guidance = {
        THEME_EXECUTION: """🏗️ EXECUTION & DELIVERY stories:
- Emphasize: scale, velocity, production quality, technical complexity
- Voice: "Matt delivered [system] at scale for [client]..."
- Position: Executive who ships production software
- Proof points: deployment metrics, system performance, reliability outcomes
- Pattern: Technical execution + operational excellence""",
        THEME_STRATEGIC: """🧠 STRATEGIC & ADVISORY stories:
- Emphasize: thought partnership, strategic framing, business alignment
- Voice: "Matt shaped [strategy] by bridging [business need] with [technical approach]..."
- Position: Trusted advisor and strategic thought partner
- Proof points: business outcomes, alignment achieved, decisions influenced
- Pattern: Strategic thinking + business translation""",
        THEME_ORG_TRANSFORM: """🔄 ORG & WORKING-MODEL TRANSFORMATION stories:
- Emphasize: culture change, process improvement, sustainable practices
- Voice: "Matt transformed how [team/org] worked by introducing [approach]..."
- Position: Change agent and organizational architect
- Proof points: adoption rates, velocity improvements, cultural shifts
- Pattern: Change leadership + sustainable transformation""",
        THEME_TALENT: """👥 TALENT & ENABLEMENT stories:
- Emphasize: capability building, mentorship impact, sustainable skills
- Voice: "Matt built [capability] by coaching [team] on [skill]..."
- Position: Teacher, mentor, capability builder
- Proof points: team growth, skill development, career progression
- Pattern: Human development + capability multiplication""",
        THEME_RISK: """🛡️ RISK & RESPONSIBLE TECH stories:
- Emphasize: governance frameworks, compliance, ethical considerations
- Voice: "Matt established [governance approach] to ensure [outcome]..."
- Position: Responsible tech advocate and risk manager
- Proof points: compliance achieved, risks mitigated, trust established
- Pattern: Risk management + responsible innovation""",
        THEME_EMERGING: """🚀 EMERGING TECH stories:
- Emphasize: innovation, experimentation, cutting-edge exploration
- Voice: "Matt pioneered [technology] by exploring [approach]..."
- Position: Innovation leader and technology scout
- Proof points: experiments run, insights gained, future capabilities unlocked
- Pattern: Innovation leadership + pragmatic exploration""",
        THEME_PROFESSIONAL: """🧭 PROFESSIONAL NARRATIVE stories:
- Personal and reflective — this is about who Matt is, not just what he did
- First-person positioning with confidence, not arrogance
- Philosophy-forward: share how Matt thinks, what drives him, what he values
- Honest about transitions, growth, and lessons learned
- Grounded in experience but forward-looking
- Warm and authentic — this is Matt speaking about himself
- Avoid corporate-speak; be direct and human""",
    }

    return guidance.get(theme, guidance[THEME_EXECUTION])


def build_story_context_for_rag(story: dict[str, Any]) -> str:
    """Build theme-aware context for a single story to pass to RAG/Agy.

    Intelligently pulls from BOTH STAR (Situation, Task, Action, Result) and
    5P (Person, Place, Purpose, Performance, Process) fields, using the most
    complete data available for each section.

    Args:
        story: Story dictionary with all fields. Supports both STAR and 5P schemas:
            - Title (str): Story title
            - Client (str): Client name
            - Role (str): Matt's role on the project
            - Industry (str): Industry domain
            - Sub-category (str): Subcategory for theme inference
            - STAR fields: Situation, Task, Action, Result
            - 5P fields: Person, Place, Purpose, Performance, Process
            - 5PSummary/5p_summary (str): Optional summary

    Returns:
        Multi-line formatted context string with sections:
        - Header: Title, Theme, Client, Role, Industry, Domain
        - Summary: 5P summary if available
        - WHY: Purpose/Situation (what drove this work)
        - HOW: Process/Action (how it was accomplished)
        - WHAT: Performance/Result (outcomes achieved)
        - Additional Context: Person and Place

    Example:
        >>> story = {"Title": "Platform Modernization", "Client": "JPMC",
        ...          "Situation": "Legacy system", "Result": "60% faster"}
        >>> context = build_story_context_for_rag(story)
        >>> "Platform Modernization" in context
        True
        >>> "JPMC" in context
        True
    """

    def get_text(field: str) -> str:
        """Extract text from field (handles both string and list)."""
        value = story.get(field, '')
        if isinstance(value, list):
            return ' '.join(str(v) for v in value if v)
        return str(value) if value else ''

    # Infer theme and get pattern phrase to prevent voice drift
    theme = infer_story_theme(story)
    pattern_phrase = THEME_TO_PATTERN.get(theme, theme)

    # Check for personal project - add warning to prevent fictional stakeholders
    client = story.get('Client', '')
    personal_project_warning = ""
    if client in ('Independent', 'Career Narrative'):
        personal_project_warning = """⚠️ **PERSONAL PROJECT - NO FICTIONAL STAKEHOLDERS**
This is Matt's personal project. Do NOT mention "job seekers", "engineers", or anyone "struggling".
Frame the WHY as: "Matt wanted to..." or "Matt recognized..." based on the story content below.

"""

    # Build structured context with field-aware headers
    # For Professional Narrative stories, mark summary as verbatim anchor
    summary = story.get('5PSummary', '') or story.get('5p_summary', '')
    if story.get('Theme') == 'Professional Narrative' and summary:
        summary = f"[[MATT'S CORE BRAND DNA - USE VERBATIM: {summary}]]"

    # Build field-aware context lines, omitting empty fields
    lines = []

    if personal_project_warning:
        lines.append(personal_project_warning.strip())

    # Title and pattern
    lines.append(f"[TITLE]: {story.get('Title', 'Untitled')}")
    lines.append(f"[PATTERN]: {pattern_phrase}")

    # Core metadata fields
    client_val = story.get('Client', '')
    if client_val:
        lines.append(f"[CLIENT]: {client_val}")

    role_val = story.get('Role', '')
    if role_val:
        lines.append(f"[ROLE]: {role_val}")

    industry_val = story.get('Industry', '')
    if industry_val:
        lines.append(f"[INDUSTRY]: {industry_val}")

    domain_val = story.get('Sub-category', '')
    if domain_val:
        lines.append(f"[DOMAIN]: {domain_val}")

    if summary:
        lines.append(f"[SUMMARY]: {summary}")

    # STAR fields with 5P fallbacks
    situation_val = get_text('Situation') or get_text('Purpose')
    if situation_val:
        lines.append(f"[SITUATION]: {situation_val}")

    task_val = get_text('Task')
    if task_val:
        lines.append(f"[TASK]: {task_val}")

    action_val = get_text('Action') or get_text('Process')
    if action_val:
        lines.append(f"[ACTION]: {action_val}")

    result_val = get_text('Result') or get_text('Performance')
    if result_val:
        lines.append(f"[RESULT]: {result_val}")

    # Additional context (optional)
    person_val = get_text('Person') or get_text('Who')
    if person_val:
        lines.append(f"[PERSON]: {person_val}")

    place_val = get_text('Place') or get_text('Where')
    if place_val:
        lines.append(f"[PLACE]: {place_val}")

    return "\n".join(lines)


def get_all_themes() -> list[str]:
    """
    Get list of all 7 themes.

    Returns:
        List of theme strings
    """
    return [
        THEME_EXECUTION,
        THEME_STRATEGIC,
        THEME_ORG_TRANSFORM,
        THEME_TALENT,
        THEME_RISK,
        THEME_EMERGING,
        THEME_PROFESSIONAL,
    ]


def get_theme_distribution(stories: list[dict[str, Any]]) -> dict[str, int]:
    """Analyze theme distribution across a story collection.

    Useful for understanding portfolio coverage, identifying gaps,
    and validating that stories are distributed across all 7 themes.

    Args:
        stories: List of story dictionaries with Sub-category or Theme fields.

    Returns:
        Dictionary mapping theme names to occurrence counts.
        Keys are the 7 canonical theme strings, values are integers.

    Example:
        >>> stories = [
        ...     {"Sub-category": "Platform Engineering"},
        ...     {"Sub-category": "Platform Engineering"},
        ...     {"Sub-category": "Coaching & Mentorship"},
        ... ]
        >>> dist = get_theme_distribution(stories)
        >>> dist["Execution & Delivery"]
        2
        >>> dist["Talent & Enablement"]
        1
    """
    themes = [infer_story_theme(s) for s in stories]
    return dict(Counter(themes))


def get_theme_emoji(theme: str) -> str:
    """Get emoji representation for a theme.

    Provides consistent emoji icons for UI display, tags, and navigation.

    Args:
        theme: One of the 7 canonical theme strings (THEME_* constants).

    Returns:
        Single emoji character as string. Falls back to 🏗️ (Execution theme)
        if theme is unrecognized.

    Example:
        >>> get_theme_emoji("Talent & Enablement")
        '👥'
        >>> get_theme_emoji("Emerging Tech")
        '🚀'
    """
    emoji_map = {
        THEME_EXECUTION: "🏗️",
        THEME_STRATEGIC: "🧠",
        THEME_ORG_TRANSFORM: "🔄",
        THEME_TALENT: "👥",
        THEME_RISK: "🛡️",
        THEME_EMERGING: "🚀",
        THEME_PROFESSIONAL: "🧭",
    }
    return emoji_map.get(theme, "🏗️")
