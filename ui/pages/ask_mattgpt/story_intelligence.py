"""
Story Intelligence - Theme inference and context building for Agy V2

Maps Sub-category to the 6 Themes and builds theme-aware context for RAG.
Provides theme-specific voice guidance for Agy's response generation.
"""

from collections import Counter
from typing import Any

# The 6 Themes
THEME_EXECUTION = "Execution & Delivery"
THEME_STRATEGIC = "Strategic & Advisory"
THEME_ORG_TRANSFORM = "Org & Working-Model Transformation"
THEME_TALENT = "Talent & Enablement"
THEME_RISK = "Risk & Responsible Tech"
THEME_EMERGING = "Emerging Tech"

# Sub-category → Theme mapping
SUBCATEGORY_TO_THEME = {
    # Execution & Delivery
    "Cloud-Native Architecture": THEME_EXECUTION,
    "DevOps & CI/CD": THEME_EXECUTION,
    "Platform Engineering": THEME_EXECUTION,
    "API & Integration Architecture": THEME_EXECUTION,
    "Data Engineering & Analytics": THEME_EXECUTION,
    "Mobile & Web Development": THEME_EXECUTION,
    "Infrastructure & Operations": THEME_EXECUTION,
    # Strategic & Advisory
    "Technology Strategy & Advisory": THEME_STRATEGIC,
    "Digital Transformation": THEME_STRATEGIC,
    "Product Strategy & Roadmapping": THEME_STRATEGIC,
    "Business Architecture": THEME_STRATEGIC,
    "Technology Assessment": THEME_STRATEGIC,
    # Org & Working-Model Transformation
    "Agile Transformation": THEME_ORG_TRANSFORM,
    "Operating Model Design": THEME_ORG_TRANSFORM,
    "Change Management": THEME_ORG_TRANSFORM,
    "Process Improvement": THEME_ORG_TRANSFORM,
    "Culture & Ways of Working": THEME_ORG_TRANSFORM,
    # Talent & Enablement
    "Team Building & Leadership": THEME_TALENT,
    "Technical Coaching & Mentorship": THEME_TALENT,
    "Capability Building": THEME_TALENT,
    "Training & Development": THEME_TALENT,
    "Hiring & Talent Strategy": THEME_TALENT,
    # Risk & Responsible Tech
    "Security & Compliance": THEME_RISK,
    "Governance & Risk Management": THEME_RISK,
    "Responsible AI & Ethics": THEME_RISK,
    "Privacy & Data Protection": THEME_RISK,
    "Regulatory Compliance": THEME_RISK,
    # Emerging Tech
    "AI & Machine Learning": THEME_EMERGING,
    "Generative AI": THEME_EMERGING,
    "Innovation & Experimentation": THEME_EMERGING,
    "Research & Prototyping": THEME_EMERGING,
    "Emerging Technology Adoption": THEME_EMERGING,
}


def infer_story_theme(story: dict[str, Any]) -> str:
    """Infer the theme for a story based on Sub-category.

    Uses a three-tier fallback strategy:
    1. Sub-category lookup in SUBCATEGORY_TO_THEME mapping
    2. Explicit Theme field (if story was previously enriched)
    3. Default to Execution & Delivery

    Args:
        story: Story dictionary with metadata. Expected fields:
            - Sub-category (str): Primary lookup field
            - Theme (str, optional): Explicit theme override
            - Other story fields (Title, Client, etc.)

    Returns:
        One of the 6 canonical theme strings (THEME_* constants).

    Example:
        >>> story = {"Sub-category": "Platform Engineering", "Client": "JPMC"}
        >>> infer_story_theme(story)
        'Execution & Delivery'
    """
    # First try: Sub-category lookup
    sub_category = story.get("Sub-category", "")
    if sub_category in SUBCATEGORY_TO_THEME:
        return SUBCATEGORY_TO_THEME[sub_category]

    # Second try: Explicit Theme field (if already enriched)
    explicit_theme = story.get("Theme", "")
    if explicit_theme and explicit_theme in get_all_themes():
        return explicit_theme

    # Default to Execution & Delivery
    return THEME_EXECUTION


def get_theme_guidance(theme: str) -> str:
    """Get Agy voice guidance for a specific theme.

    Provides framing instructions that guide Agy's tone, positioning, and
    emphasis when discussing stories from this theme. Used in system prompts
    for _generate_agy_response().

    Args:
        theme: One of the 6 canonical theme strings (THEME_* constants).
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

    # Infer theme
    theme = infer_story_theme(story)

    # Build structured context
    context = f"""**{story.get('Title', 'Untitled')}**
Theme: {theme}
Client: {story.get('Client', 'Unknown')}
Role: {story.get('Role', '')}
Industry: {story.get('Industry', '')}
Domain: {story.get('Sub-category', '')}

Summary: {story.get('5PSummary', '') or story.get('5p_summary', '')}

WHY (Purpose/Situation):
{get_text('Purpose') or get_text('Situation')}
{get_text('Task') if not get_text('Purpose') else ''}

HOW (Process/Action):
{get_text('Process') or get_text('Action')}

WHAT (Performance/Result):
{get_text('Performance') or get_text('Result')}

Additional Context:
Person (Who): {get_text('Person') or get_text('Who')}
Place (Where): {get_text('Place') or get_text('Where')}
"""

    return context


def get_all_themes() -> list[str]:
    """
    Get list of all 6 themes.

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
    ]


def get_theme_distribution(stories: list[dict[str, Any]]) -> dict[str, int]:
    """Analyze theme distribution across a story collection.

    Useful for understanding portfolio coverage, identifying gaps,
    and validating that stories are distributed across all 6 themes.

    Args:
        stories: List of story dictionaries with Sub-category or Theme fields.

    Returns:
        Dictionary mapping theme names to occurrence counts.
        Keys are the 6 canonical theme strings, values are integers.

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
        theme: One of the 6 canonical theme strings (THEME_* constants).

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
    }
    return emoji_map.get(theme, "🏗️")
