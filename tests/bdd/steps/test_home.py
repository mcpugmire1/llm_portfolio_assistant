"""
BDD Step Definitions for Home Page Category Cards.

Currently only Card 3 (Product Innovation & Strategy) is fully implemented —
this is the regression test for the May 12, 2026 broken-prefilter bug.

The other 5 card scenarios are documented in home.feature as acceptance
criteria. Step definitions are pending — see MATTGPT-060 in BACKLOG.md for
the rollout plan. Until those land, only the Card 3 scenario is loaded via
@scenario to avoid false failures on unbound steps.

Install Playwright with: pip install playwright && playwright install chromium
Run with: pytest tests/bdd -k home
"""

import re

from pytest_bdd import given, parsers, scenario, then, when

# =============================================================================
# WAIT UTILITIES (mirrors test_explore_stories.py)
# =============================================================================

SHORT_WAIT = 200  # ms — quick UI updates
MEDIUM_WAIT = 500  # ms — component renders


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# CARD 3 SCENARIO — Product Innovation prefilter regression test
# Loads only this scenario from home.feature. Other scenarios in the same
# feature file are documented acceptance criteria and will run once their
# step defs land (see MATTGPT-060).
# =============================================================================


@scenario(
    "../features/home.feature",
    "Card 3 — Product Innovation prefilters to product Sub-categories",
)
def test_card3_product_innovation_prefilter():
    """Regression test for the May 12, 2026 broken-prefilter bug.

    Prior to fix: card set prefilter_capability='Product Leadership' which is
    not a valid Solution/Offering value. The Capability dropdown widget
    silently sanitized the invalid value to "All", showing 113 unfiltered
    stories. The card's promise was broken — a recruiter saw the entire
    corpus instead of the curated product slice.

    After fix: card sets prefilter_domains with 5 valid Sub-category values
    targeting product work (~10 stories). Result count should be far less
    than 113, and at least one expected product domain chip must be visible.
    """


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    """Home is the default tab when the app loads — no navigation needed.

    Waits for the "View Product Work" anchor to render, which signals the
    category cards section has finished loading.
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # The Card 3 anchor is a stable target proving category cards have rendered.
    browser_page.wait_for_selector("a#btn-product", timeout=30000)


# =============================================================================
# WHEN — Card click
# =============================================================================


@when('the user clicks "View Product Work" on the Product Innovation card')
def click_view_product_work(browser_page):
    """Click Card 3.

    The visible link is <a id="btn-product">; its click is bridged via JS in
    category_cards.py to a hidden st.button(key="card_btn_product"). We click
    the hidden Streamlit button directly with force=True — bypasses the JS
    bridge and isolates the test to the prefilter business logic (the JS
    bridge is a separate concern with its own coverage).
    """
    btn = browser_page.locator("[class*='st-key-card_btn_product'] button").first
    btn.click(force=True)
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# THEN — State assertions
# =============================================================================


@then(parsers.parse('the active tab should be "{tab_name}"'))
def assert_active_tab(browser_page, tab_name):
    """Verify navigation landed on the expected tab.

    For Explore Stories: the .results-count element is unique to that page,
    so its presence is a reliable proxy for active_tab == "Explore Stories".
    """
    if tab_name == "Explore Stories":
        browser_page.wait_for_selector(".results-count", timeout=15000)
    else:
        # Other tabs (Banking, Cross-Industry, Home) — assertion stubbed
        # until those scenarios get full step defs (MATTGPT-060).
        pass


@then(parsers.parse("the result count should be less than {limit:d}"))
def assert_result_count_below(browser_page, limit):
    """Verify the prefilter narrowed results below the unfiltered corpus size.

    The .results-count text renders as "Showing N–M of TOTAL projects". We
    extract TOTAL and assert it's below the limit. If the prefilter silently
    fails (the May 12 bug shape), TOTAL would be 113 — the full corpus —
    and this assertion fires.
    """
    count_el = browser_page.locator(".results-count").first
    count_el.wait_for(state="visible", timeout=10000)
    text = count_el.inner_text()
    # Pattern: "Showing 1–10 of 10 projects" — extract the number after "of".
    match = re.search(r"of\s+(\d+)\s+project", text)
    assert match, f"Could not parse total count from results-count text: {text!r}"
    actual = int(match.group(1))
    assert actual < limit, (
        f"Expected result count < {limit}, got {actual}. "
        f"Card 3 prefilter did not apply — the entire corpus is showing. "
        f"This is the May 12, 2026 regression shape."
    )


@then(parsers.parse('a filter chip "{value}" should be visible'))
def assert_filter_chip_visible(browser_page, value):
    """Verify the expected prefilter value rendered as an active filter chip.

    Filter chips render as elements with "✕ {value}" text. The existing
    pattern in test_explore_stories.py uses two fallback selectors (button or
    p element) to handle different render paths. We mirror that.
    """
    chip = browser_page.locator(f"button:has-text('✕'):has-text('{value}')").first
    if chip.count() == 0:
        chip = browser_page.locator(f"p:has-text('✕'):has-text('{value}')").first
    assert chip.count() > 0, (
        f"No filter chip with text {value!r} is visible on Explore Stories. "
        f"Card 3 prefilter did not apply the expected Sub-category — the "
        f"page may show 'All' as the active filter state instead."
    )
