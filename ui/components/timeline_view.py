"""
Timeline View Component for Explore Stories - V3 (Era-based)

Era-based timeline with progressive disclosure.
- Groups stories by Era (career phase), not Role
- Excludes "Leadership & Professional Narrative" stories
- Shows 6 most recent stories per era when expanded
- "Explore all [Era] stories" links to filtered Table view
- Most recent era expanded by default
- Role shown as badge on story cards
- Click story to show detail panel
"""

from collections.abc import Callable

import streamlit as st
import streamlit.components.v1 as components

# =============================================================================
# ERA CONFIGURATION
# =============================================================================

# Eras in chronological order (most recent first for display)
ERA_ORDER = [
    "Independent Product Development",
    "Enterprise Innovation & Transformation",
    "Cloud-Native Prototyping & Product Shaping",
    "Financial Services Platform Modernization",
    "Integration & Platform Foundations",
]

# Era subtitles (short, muted descriptions)
ERA_SUBTITLES = {
    "Independent Product Development": "Portfolio development, RAG architecture, product design",
    "Enterprise Innovation & Transformation": "Cloud Innovation Center, enterprise delivery, GenAI, DevSecOps",
    "Cloud-Native Prototyping & Product Shaping": "Liquid Studio, lean product shaping, rapid experimentation",
    "Financial Services Platform Modernization": "Payments, platform architecture, global deployments",
    "Integration & Platform Foundations": "Enterprise integration, SOA, technical foundations",
}

# Era to exclude from Timeline (still appears in Table/Cards)
EXCLUDED_ERA = "Leadership & Professional Narrative"

MAX_STORIES_PER_ERA = 6


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def parse_year(date_str: str | None) -> int | None:
    """Extract year from date string (YYYY-MM or YYYY format)."""
    if not date_str:
        return None
    try:
        if "-" in str(date_str):
            return int(str(date_str).split("-")[0])
        return int(date_str)
    except (ValueError, TypeError):
        return None


def get_era_sort_key(era: str) -> int:
    """Get sort key for era ordering (lower = more recent)."""
    try:
        return ERA_ORDER.index(era)
    except ValueError:
        return len(ERA_ORDER)


def get_era_date_range(stories: list[dict]) -> str:
    """Calculate date range string from stories (e.g., '2019 – 2023')."""
    years = []
    for story in stories:
        start_year = parse_year(story.get("Start_Date"))
        end_year = parse_year(story.get("End_Date"))
        if start_year:
            years.append(start_year)
        if end_year:
            years.append(end_year)

    if not years:
        return ""

    min_year = min(years)
    max_year = max(years)

    if min_year == max_year:
        return str(min_year)
    return f"{min_year} – {max_year}"


def group_stories_by_era(stories: list[dict]) -> dict[str, dict]:
    """
    Group stories by Era and calculate date ranges.
    Excludes Leadership & Professional Narrative stories.

    Returns dict like:
    {
        "Enterprise Innovation & Transformation": {
            "stories": [...],  # sorted by Start_Date desc, limited to MAX_STORIES_PER_ERA
            "all_stories": [...],  # all stories for this era
            "date_range": "2019 – 2023",
            "total_count": 63,
            "subtitle": "Cloud Innovation Center, enterprise delivery..."
        },
        ...
    }
    """
    grouped: dict[str, list[dict]] = {}

    for story in stories:
        era = story.get("Era", "").strip()

        # Skip excluded era
        if era == EXCLUDED_ERA or not era:
            continue

        if era not in grouped:
            grouped[era] = []
        grouped[era].append(story)

    result = {}

    # Sort eras by defined order
    sorted_eras = sorted(grouped.keys(), key=get_era_sort_key)

    for era in sorted_eras:
        era_stories = grouped[era]

        # Sort stories by Start_Date descending (most recent first)
        sorted_stories = sorted(
            era_stories, key=lambda s: s.get("Start_Date", "") or "", reverse=True
        )

        date_range = get_era_date_range(era_stories)
        subtitle = ERA_SUBTITLES.get(era, "")

        result[era] = {
            "stories": sorted_stories[:MAX_STORIES_PER_ERA],
            "all_stories": sorted_stories,
            "date_range": date_range,
            "total_count": len(sorted_stories),
            "subtitle": subtitle,
        }

    return result


# =============================================================================
# CSS STYLES
# =============================================================================


def get_timeline_css() -> str:
    """Return CSS for collapsible timeline view using app's CSS variables."""
    return """
    <style>
    /* =============================================================================
       TIMELINE VIEW - COLLAPSIBLE GROUPS (ERA-BASED)
       Uses app's existing CSS variables from global_styles.py
       ============================================================================= */

    .timeline-container {
        position: relative;
        max-width: 900px;
        margin: 0 auto;
        padding-left: 220px;
        font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main vertical line */
    .timeline-container::before {
        content: '';
        position: absolute;
        left: 200px;
        top: 20px;
        bottom: 20px;
        width: 3px;
        background: linear-gradient(to bottom, #8b5cf6, #a78bfa, #c4b5fd);
        border-radius: 2px;
    }

    /* Timeline Group */
    .timeline-group {
        position: relative;
        margin-bottom: 24px;
    }

    /* Group Header */
    .group-header {
        position: relative;
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 8px 0;
        cursor: pointer;
        user-select: none;
    }

    /* Timeline dot */
    .timeline-dot {
        position: absolute;
        left: -24px;
        width: 14px;
        height: 14px;
        background: var(--bg-card);
        border: 3px solid var(--accent-purple);
        border-radius: 50%;
        z-index: 2;
        transition: all 0.2s;
    }

    .timeline-group.expanded .timeline-dot {
        background: var(--accent-purple);
        box-shadow: 0 0 0 4px var(--accent-purple-light);
    }

    .group-header:hover .timeline-dot {
        transform: scale(1.2);
    }

    /* Era Badge - positioned to left of timeline */
    .era-badge {
        position: absolute;
        left: -220px;
        width: 190px;
        text-align: right;
        padding-right: 20px;
        line-height: 1.3;
    }

    .era-title {
        display: block;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }

    .era-dates {
        display: block;
        font-size: 12px;
        color: var(--accent-purple);
        font-weight: 500;
    }

    /* Group info box */
    .group-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 12px 16px;
        background: var(--bg-surface);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        transition: all 0.2s;
        min-width: 200px;
    }

    .group-info-header {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .group-header:hover .group-info {
        border-color: var(--accent-purple);
        background: var(--bg-hover);
    }

    .expand-icon {
        font-size: 12px;
        color: var(--text-muted);
        transition: transform 0.2s;
    }

    .timeline-group.expanded .expand-icon {
        transform: rotate(90deg);
    }

    .story-count {
        font-size: 14px;
        color: var(--text-secondary);
    }

    .story-count strong {
        color: var(--text-primary);
    }

    .era-subtitle {
        font-size: 12px;
        color: var(--text-muted);
        font-style: italic;
    }

    /* Stories container - hidden by default */
    .stories-container {
        display: none;
        padding-left: 20px;
        padding-top: 12px;
    }

    .timeline-group.expanded .stories-container {
        display: block;
    }

    /* Individual story card */
    .story-card {
        position: relative;
        padding: 16px 20px;
        margin-bottom: 12px;
        margin-left: 30px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .story-card::before {
        content: '';
        position: absolute;
        left: -30px;
        top: 50%;
        width: 20px;
        height: 2px;
        background: var(--border-color);
    }

    .story-card::after {
        content: '';
        position: absolute;
        left: -14px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background: var(--bg-card);
        border: 2px solid var(--accent-purple-light);
        border-radius: 50%;
    }

    .story-card:hover {
        border-color: var(--accent-purple);
        background: var(--bg-hover);
        box-shadow: var(--hover-shadow);
        transform: translateX(4px);
    }

    .story-card.selected {
        border-color: var(--accent-purple);
        background: var(--accent-purple-bg);
        box-shadow: 0 0 0 3px var(--accent-purple-light);
    }

    .story-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 8px;
    }

    .story-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.4;
        flex: 1;
    }

    .client-badge {
        background: var(--accent-purple-bg);
        color: var(--accent-purple);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap;
    }

    .story-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: var(--text-muted);
    }

    .role-badge {
        background: var(--bg-surface);
        color: var(--text-secondary);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
    }

    .story-meta-divider {
        color: var(--border-color);
    }

    /* Explore all link */
    .explore-all-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-left: 30px;
        margin-top: 8px;
        padding: 10px 16px;
        font-size: 13px;
        font-weight: 500;
        color: var(--accent-purple);
        background: transparent;
        border: 1px dashed var(--accent-purple-light);
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .explore-all-link:hover {
        background: var(--accent-purple-bg);
        color: var(--accent-purple-hover);
    }

    /* =============================================================================
       MOBILE RESPONSIVE - Single-column layout
       Standard pattern: line on left, all content to right
       ============================================================================= */

    @media (max-width: 767px) {
        .timeline-container {
            padding-left: 40px;
            max-width: 100%;
        }

        .timeline-container::before {
            left: 15px;
        }

        /* Era badge moves above the card, not to the left */
        .era-badge {
            position: relative;
            left: 0;
            width: 100%;
            text-align: left;
            padding-right: 0;
            padding-left: 0;
            margin-bottom: 4px;
        }

        .era-title {
            font-size: 14px;
            font-weight: 600;
            display: inline;
        }

        .era-dates {
            font-size: 12px;
            display: inline;
            margin-left: 8px;
        }

        .timeline-dot {
            left: -29px;
            width: 12px;
            height: 12px;
        }

        .group-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }

        .group-info {
            width: 100%;
        }

        .timeline-group {
            margin-bottom: 20px;
        }

        .story-card {
            padding: 12px 16px;
            margin-left: 0;
            margin-right: 0;
        }

        .story-card::before,
        .story-card::after {
            display: none;
        }

        /* Stack header vertically on mobile */
        .story-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .story-title {
            font-size: 14px;
            /* Limit to 2 lines */
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .client-badge {
            font-size: 10px;
            padding: 3px 8px;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Stack meta vertically too */
        .story-meta {
            flex-wrap: wrap;
            gap: 4px 8px;
        }

        .explore-all-link {
            margin-left: 0;
            font-size: 12px;
            padding: 10px 12px;
        }
    }

    /* =============================================================================
       HIDDEN TRIGGER BUTTONS
       ============================================================================= */

    [class*="st-key-timeline_story_"],
    [class*="st-key-timeline_explore_"],
    [class*="st-key-timeline_toggle_"] {
        position: absolute !important;
        left: -9999px !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================


def render_story_card(story: dict, index: int) -> str:
    """Render a single story card HTML with role badge."""
    title = story.get("Title", "Untitled")
    client = story.get("Client", "")
    role = story.get("Role", "")
    theme = story.get("Theme", "")

    client_html = f'<span class="client-badge">{client}</span>' if client else ""

    # Build meta line with role badge and theme
    meta_parts = []
    if role:
        meta_parts.append(f'<span class="role-badge">{role}</span>')
    if theme:
        if meta_parts:
            meta_parts.append('<span class="story-meta-divider">•</span>')
        meta_parts.append(f'<span>{theme}</span>')

    meta_html = (
        f'<div class="story-meta">{"".join(meta_parts)}</div>' if meta_parts else ""
    )

    return f'<div class="story-card" data-story-index="{index}"><div class="story-header"><span class="story-title">{title}</span>{client_html}</div>{meta_html}</div>'


def render_timeline_group(
    era: str, data: dict, group_index: int, start_index: int, is_expanded: bool = False
) -> str:
    """Render a collapsible era group."""
    stories = data["stories"]
    date_range = data["date_range"]
    total_count = data["total_count"]
    subtitle = data.get("subtitle", "")

    expanded_class = "expanded" if is_expanded else ""

    # Build story cards HTML
    cards_html = ""
    for i, story in enumerate(stories):
        cards_html += render_story_card(story, start_index + i)

    # Explore link
    explore_html = f'<div class="explore-all-link" data-era="{era}" data-group-index="{group_index}">Explore all {total_count} stories <span class="arrow">→</span></div>'

    # Subtitle HTML
    subtitle_html = f'<div class="era-subtitle">{subtitle}</div>' if subtitle else ""

    # Build group HTML (single line to avoid st.markdown parsing issues)
    group_header = f'<div class="group-header"><div class="era-badge"><span class="era-title">{era}</span><span class="era-dates">{date_range}</span></div><div class="timeline-dot"></div><div class="group-info"><div class="group-info-header"><span class="expand-icon">▶</span><span class="story-count"><strong>{total_count}</strong> stories</span></div>{subtitle_html}</div></div>'

    stories_container = (
        f'<div class="stories-container">{cards_html}{explore_html}</div>'
    )

    return f'<div class="timeline-group {expanded_class}" data-group-index="{group_index}">{group_header}{stories_container}</div>'


def render_timeline_view(
    stories: list[dict],
    on_story_click: Callable[[dict], None] | None = None,
    on_explore_era: Callable[[str], None] | None = None,
) -> None:
    """
    Render the collapsible timeline view grouped by Era.

    Args:
        stories: List of filtered story dictionaries
        on_story_click: Callback when a story card is clicked
        on_explore_era: Callback when "Explore all" is clicked (receives era name)
    """
    grouped = group_stories_by_era(stories)

    if not grouped:
        st.info("No stories found matching your filters.")
        return

    # Inject CSS
    st.markdown(get_timeline_css(), unsafe_allow_html=True)

    # Build timeline HTML
    html = '<div class="timeline-container">'

    card_index = 0
    story_map = {}
    era_list = list(grouped.keys())

    for group_idx, era in enumerate(era_list):
        data = grouped[era]
        # First era (most recent) expanded by default
        is_expanded = group_idx == 0

        html += render_timeline_group(era, data, group_idx, card_index, is_expanded)

        # Track stories for click handling
        for i, story in enumerate(data["stories"]):
            story_map[card_index + i] = story

        card_index += len(data["stories"])

    html += '</div>'

    # Render timeline
    st.markdown(html, unsafe_allow_html=True)

    # Hidden buttons for story clicks
    for idx, story in story_map.items():
        if st.button("", key=f"timeline_story_{idx}"):
            if on_story_click:
                on_story_click(story)
            else:
                st.session_state["active_story"] = story.get("id")
                st.session_state["active_story_obj"] = story
                st.rerun()

    # Hidden buttons for explore clicks
    for group_idx, era in enumerate(era_list):
        if st.button("", key=f"timeline_explore_{group_idx}"):
            if on_explore_era:
                on_explore_era(era)
            else:
                # Use prefilter pattern
                # explore_stories.py needs to handle prefilter_era
                st.session_state["prefilter_era"] = era
                st.session_state["prefilter_view_mode"] = "Table"
                st.rerun()

    # Hidden buttons for toggle clicks (for future use if needed)
    for group_idx in range(len(era_list)):
        if st.button("", key=f"timeline_toggle_{group_idx}"):
            # Toggle is handled by JS, but button exists for potential server-side state
            pass

    # JavaScript for interactivity
    js_code = """
    <script>
    (function() {
        // Wait for DOM to be ready
        setTimeout(function() {
            var parentDoc = window.parent.document;

            // Toggle group expand/collapse
            parentDoc.querySelectorAll('.group-header').forEach(function(header) {
                header.addEventListener('click', function(e) {
                    if (e.target.closest('.story-card') || e.target.closest('.explore-all-link')) return;
                    var group = this.closest('.timeline-group');
                    if (group) {
                        group.classList.toggle('expanded');
                    }
                });
            });

            // Story card clicks
            parentDoc.querySelectorAll('.story-card').forEach(function(card) {
                card.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var index = this.getAttribute('data-story-index');
                    if (index === null) return;

                    // Remove selected from all
                    parentDoc.querySelectorAll('.story-card').forEach(function(c) {
                        c.classList.remove('selected');
                    });
                    this.classList.add('selected');

                    var btn = parentDoc.querySelector('[class*="st-key-timeline_story_' + index + '"] button');
                    if (btn) {
                        btn.click();
                    } else {
                        console.log('Button not found for index:', index);
                    }
                });
            });

            // Explore all clicks
            parentDoc.querySelectorAll('.explore-all-link').forEach(function(link) {
                link.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var groupIndex = this.getAttribute('data-group-index');
                    if (groupIndex === null) return;

                    var btn = parentDoc.querySelector('[class*="st-key-timeline_explore_' + groupIndex + '"] button');
                    if (btn) btn.click();
                });
            });
        }, 100);
    })();
    </script>
    """
    components.html(js_code, height=0)
