"""
BDD Step Definitions for Banking Landing Page Capability Cards.

Currently only the regression scenario is wired up — it pins the contract
that the data-derivation refactor (Phase 2, May 12 2026) is supposed to
guarantee: every visible capability card on the Banking landing leads to a
non-empty Explore Stories result. If any card has 0 backing stories, the
data-derivation broke or someone added a hardcoded card.

Other scenarios in banking_landing.feature are documented acceptance
criteria; step defs are pending (see MATTGPT-060 in BACKLOG.md).

Run with: pytest tests/bdd -k banking_landing
"""

import re

from pytest_bdd import given, parsers, scenario, then, when

# Mirrors timing helpers in test_explore_stories.py and test_home.py.
SHORT_WAIT = 200


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# REGRESSION SCENARIO — wired up
# =============================================================================


@scenario(
    "../features/banking_landing.feature",
    "Clicking a capability card lands on Explore Stories scrolled to the top",
)
def test_banking_capability_click_resets_scroll():
    """Regression test for the landing → Explore scroll-position bug (May 12 2026).

    Streamlit preserves scroll across reruns by default. Before the fix,
    explore_stories.py reset scroll only inside the prefilter_era branch, so
    Timeline → Explore worked but landing-card → Explore (which sets
    prefilter_capability / prefilter_domains / prefilter_industry) inherited
    the landing page's scrolled-down position. Users landed on Explore Stories
    with the hero and filter strip above the viewport. Fix hoists the
    scrollTo(0,0) call out so it fires for ANY consumed prefilter.
    """


@scenario(
    "../features/banking_landing.feature",
    "Clicking the top Core capability card lands on a filtered Explore Stories with results",
)
def test_top_banking_capability_lands_with_results():
    """Regression test for the data-derivation refactor.

    Prior to the refactor: banking_landing.py rendered a hardcoded list of 15
    capability cards, 4 of which had zero matching banking stories. Clicking
    those broken cards (Compliance & Risk Solutions, Cloud Transformation,
    Application Modernization, Adoption Enablement) landed users on Explore
    Stories with the capability filter silently sanitized to "All" — showing
    113 unfiltered stories instead of the promised banking slice.

    After the refactor: cards are derived from build_landing_cards(), which
    pulls Solution/Offering values that have >=1 banking story. By construction
    no broken card can exist. This test pins that contract end-to-end.
    """


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the Banking landing page")
def navigate_to_banking_landing(browser_page, app_url):
    """Navigate via the Home page Banking card.

    Banking landing isn't in the navbar — it's reached by clicking the
    Banking capability card on the Home page (category_cards.py Card 1),
    which sets active_tab="Banking" and reruns. We click the hidden
    Streamlit button keyed card_btn_banking directly to bypass the JS
    click-bridge layer (isolates the test from that bridge's wiring).
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # The hidden Streamlit button behind the Banking card is intentionally
    # hidden via CSS (position: absolute; left: -9999px). Use state="attached"
    # to wait for it to exist in DOM rather than be visible.
    browser_page.wait_for_selector(
        "[class*='st-key-card_btn_banking'] button",
        state="attached",
        timeout=30000,
    )
    # dispatch_event("click") fires the click without Playwright's visibility
    # check. The hidden button is moved off-screen via CSS but is still active
    # in the DOM — a native click event still triggers Streamlit's handler.
    browser_page.locator(
        "[class*='st-key-card_btn_banking'] button"
    ).first.dispatch_event("click")
    browser_page.wait_for_load_state("networkidle")
    # Wait for at least one capability card to render — the .capability-card
    # class is used by the per-card markup on the Banking landing.
    browser_page.wait_for_selector(".capability-card", timeout=30000)


@given("the user has scrolled down to view a capability card")
def scroll_landing_down(browser_page):
    """Scroll the main content area down to simulate a user who scrolled to
    view cards before clicking. Without this, Playwright's dispatch_event
    fires the click without moving the viewport, so the scroll position
    stays at 0 across the rerun — masking the bug we're testing for.

    Selector note: `section[data-testid="stMain"]` is the actual scrollable
    element in current Streamlit. The legacy `section.main` selector no
    longer exists. Landing pages (banking_landing.py, cross_industry_landing.py,
    landing_view.py) all use this same selector for their on-arrival scroll
    reset.

    600px puts the scroll well below the hero, into the Core Capabilities
    grid territory on a typical viewport. The exact value doesn't matter as
    long as it's > the post-fix tolerance (50px).

    Timing: the landing page has its own setTimeout(100ms) scroll-reset that
    fires after render to ensure on-arrival the page is scrolled to top.
    We must wait long enough for that timer to fire BEFORE scrolling down,
    otherwise the landing's reset undoes our scroll and the test silently
    starts at scrollTop=0 (false GREEN — bug we hit during scroll-position
    BDD authoring, May 12 2026).
    """
    browser_page.wait_for_timeout(500)  # let landing's setTimeout(100) fire first
    browser_page.evaluate(
        'document.querySelector(\'section[data-testid="stMain"]\').scrollTop = 600'
    )
    browser_page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# WHEN — Click the top capability card
# =============================================================================


@when("the user clicks the top capability card")
def click_top_capability_card(browser_page):
    """Click the first capability card.

    Cards render with a visible <div class="capability-card"> and a hidden
    Streamlit button (key=card_btn_banking_<i>_<j>) that handles the click.
    We click the hidden Streamlit button directly with force=True to isolate
    the test from the JS click-bridge layer.
    """
    browser_page.locator(
        "[class*='st-key-card_btn_banking_core_0'] button"
    ).first.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# THEN — State assertions
# =============================================================================


@then(parsers.parse('the active tab should be "{tab_name}"'))
def assert_active_tab(browser_page, tab_name):
    """Verify navigation landed on the expected tab.

    For Explore Stories: .results-count is unique to that page; its presence
    is a reliable proxy for active_tab == "Explore Stories".
    """
    if tab_name == "Explore Stories":
        browser_page.wait_for_selector(".results-count", timeout=15000)


@then("the Explore Stories page should be scrolled to the top")
def assert_explore_scrolled_to_top(browser_page):
    """Verify the Explore Stories page loaded at the top.

    Streamlit preserves scroll across reruns by default. The fix in the
    prefilter handler block of explore_stories.py forces the main content
    area scrollTop to 0 when any prefilter is consumed (was previously only
    the prefilter_era branch, and that branch targeted the legacy
    `section.main` selector which no longer exists — silently no-op'd).

    Selector: `section[data-testid="stMain"]` matches the other landing
    pages' scroll-reset implementation.

    Tolerance: ≤ 50px allows minor sub-pixel rendering variance without
    masking a real bug — the broken state lands users ~600px down (the
    landing page's pre-click scroll position).
    """
    scroll_top = browser_page.evaluate(
        'document.querySelector(\'section[data-testid="stMain"]\')?.scrollTop ?? 0'
    )
    assert scroll_top <= 50, (
        f"stMain scrollTop is {scroll_top}px after landing-card click — "
        f"Explore Stories inherited the landing page's scroll position "
        f"instead of resetting to top. Fix lives in the prefilter handler "
        f"block in explore_stories.py — scroll-to-top must fire for ANY "
        f"consumed prefilter and target [data-testid='stMain']."
    )


@then(parsers.parse("the result count should be greater than {floor:d}"))
def assert_result_count_above(browser_page, floor):
    """Verify the prefilter narrowed results to at least one story.

    If the count is 0, the card we clicked has no backing banking stories —
    a broken card slipped through the data-derivation contract.
    """
    count_el = browser_page.locator(".results-count").first
    count_el.wait_for(state="visible", timeout=10000)
    text = count_el.inner_text()
    # Pattern: "Showing 1–N of TOTAL projects" — extract TOTAL.
    match = re.search(r"of\s+(\d+)\s+project", text)
    assert match, f"Could not parse total count from results-count text: {text!r}"
    actual = int(match.group(1))
    assert actual > floor, (
        f"Expected result count > {floor}, got {actual}. The capability card "
        f"that was clicked has no backing banking stories — a broken card "
        f"slipped through the data-derivation contract."
    )
