"""
Timeline View Component for My Work - V3 (Era-based)

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
# RENDER FUNCTIONS
# =============================================================================


def render_story_card(story: dict, index: int) -> str:
    """Render a single story card HTML with role badge."""
    title = story.get("Title", "Untitled")
    client = story.get("Client", "")
    role = story.get("Role", "")
    theme = story.get("Theme", "")

    client_html = f'<span class="es-tl-client-badge">{client}</span>' if client else ""

    # Build meta line with role badge and theme
    meta_parts = []
    if role:
        meta_parts.append(f'<span class="es-tl-role-badge">{role}</span>')
    if theme:
        if meta_parts:
            meta_parts.append('<span class="es-story-meta-divider">•</span>')
        meta_parts.append(f'<span>{theme}</span>')

    meta_html = (
        f'<div class="es-story-meta">{"".join(meta_parts)}</div>' if meta_parts else ""
    )

    return f'<div class="es-story-card" data-story-index="{index}"><div class="es-story-header"><span class="es-story-title">{title}</span>{client_html}</div>{meta_html}</div>'


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
    explore_html = f'<div class="es-explore-all-link" data-era="{era}" data-group-index="{group_index}">Explore all {total_count} stories <span class="arrow">→</span></div>'

    # Subtitle HTML
    subtitle_html = f'<div class="es-era-subtitle">{subtitle}</div>' if subtitle else ""

    # Build group HTML (single line to avoid st.markdown parsing issues)
    group_header = f'<div class="es-group-header"><div class="es-era-badge"><span class="es-era-title">{era}</span><span class="es-era-dates">{date_range}</span></div><div class="es-timeline-dot"></div><div class="es-group-info"><div class="es-group-info-header"><span class="es-expand-icon">▶</span><span class="es-story-count"><strong>{total_count}</strong> stories</span></div>{subtitle_html}</div></div>'

    stories_container = (
        f'<div class="es-stories-container">{cards_html}{explore_html}</div>'
    )

    return f'<div class="es-timeline-group {expanded_class}" data-group-index="{group_index}">{group_header}{stories_container}</div>'


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

    # Build timeline HTML
    html = '<div class="es-timeline-container">'

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
            parentDoc.querySelectorAll('.es-group-header').forEach(function(header) {
                header.addEventListener('click', function(e) {
                    if (e.target.closest('.es-story-card') || e.target.closest('.es-explore-all-link')) return;
                    var group = this.closest('.es-timeline-group');
                    if (group) {
                        group.classList.toggle('expanded');
                    }
                });
            });

            // Story card clicks
            parentDoc.querySelectorAll('.es-story-card').forEach(function(card) {
                card.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var index = this.getAttribute('data-story-index');
                    if (index === null) return;

                    // Remove selected from all
                    parentDoc.querySelectorAll('.es-story-card').forEach(function(c) {
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
            parentDoc.querySelectorAll('.es-explore-all-link').forEach(function(link) {
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
