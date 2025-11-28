"""
Story Intelligence - Theme inference and context building for Agy V2

Maps Sub-category to the 6 Themes and builds theme-aware context for RAG.
"""

from collections import Counter

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


def infer_story_theme(story: dict) -> str:
    """
    Infer the theme for a story based on Sub-category.

    Falls back to explicit Theme field, then Execution & Delivery if not recognized.

    Args:
        story: Story dictionary with metadata

    Returns:
        One of the 6 theme strings
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
    """
    Get Agy voice guidance for a specific theme.

    Returns framing instructions for how Agy should talk about this type of story.

    Args:
        theme: One of the 6 theme strings

    Returns:
        Voice guidance text for the system prompt
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


def build_story_context_for_rag(story: dict) -> str:
    """
    Build theme-aware context for a single story to pass to RAG/Agy.

    Intelligently pulls from BOTH STAR and 5P fields.

    Args:
        story: Story dictionary with all fields

    Returns:
        Formatted context string for RAG
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


def get_theme_distribution(stories: list[dict]) -> dict[str, int]:
    """
    Analyze theme distribution across a story collection.

    Useful for understanding portfolio coverage.

    Args:
        stories: List of story dictionaries

    Returns:
        Dictionary mapping theme names to counts
    """
    themes = [infer_story_theme(s) for s in stories]
    return dict(Counter(themes))


def get_theme_emoji(theme: str) -> str:
    """
    Get emoji representation for a theme.

    Args:
        theme: Theme name

    Returns:
        Emoji string
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
