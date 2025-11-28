"""
Home Page - MattGPT Landing

Hero section with portfolio overview, category cards, and CTAs.
This is the main landing page users see when they first visit.
"""

from ui.components.category_cards import render_category_cards
from ui.components.footer import render_footer
from ui.components.hero import render_hero, render_section_title, render_stats_bar


def render_home_page():
    """
    Render the homepage with hero, stats, category cards, and footer.

    Structure:
    1. Hero section with logo and CTAs
    2. Portfolio statistics bar
    3. Section title
    4. Category exploration cards
    5. Footer with contact information
    """

    # Hero section
    render_hero()

    # Stats bar
    render_stats_bar()

    # Section title
    render_section_title("What would you like to explore?")

    # Category cards
    render_category_cards()

    # === ADD FOOTER ===

    render_footer()
