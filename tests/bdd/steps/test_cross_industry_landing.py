"""
BDD Step Definitions for Cross-Industry Landing Page Capability Cards.

Two scenarios wired up:
1. Tier-header presence — pins the post-refactor structure (Core Capabilities
   section header must render). Intentionally fails against the pre-refactor
   flat-grid layout, providing the meaningful RED state before implementation.
2. Top-card click flow — pins the click bridge / prefilter handoff.

Other scenarios in cross_industry_landing.feature are documented acceptance
criteria; step defs pending (see MATTGPT-060 in BACKLOG.md).

Run with: pytest tests/bdd -k cross_industry_landing
"""

import re

from pytest_bdd import given, parsers, scenario, then, when

SHORT_WAIT = 200


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to complete a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# REGRESSION SCENARIOS — wired up
# =============================================================================


@scenario(
    "../features/cross_industry_landing.feature",
    "Cross-Industry landing displays the Core Capabilities tier header",
)
def test_cross_industry_landing_has_core_capabilities_header():
    """Pins the post-refactor structure.

    Pre-refactor: Cross-Industry landing renders a flat 11-card grid with no
    tier sections. This test fails against that state (RED). After the refactor
    introduces the Core/Specialized hierarchy via build_landing_cards(), the
    section header renders and this test passes (GREEN).
    """


@scenario(
    "../features/cross_industry_landing.feature",
    "Clicking the top Core capability card lands on a filtered My Work with results",
)
def test_top_cross_industry_capability_lands_with_results():
    """Pins the click bridge / prefilter flow post-refactor."""


@scenario(
    "../features/cross_industry_landing.feature",
    "Clicking a capability card lands on My Work scrolled to the top",
)
def test_cross_industry_capability_click_resets_scroll():
    """Same regression contract as banking_landing — see that file's docstring
    on test_banking_capability_click_resets_scroll for the full rationale.
    Pinned on both landing pages because the bug is in the shared
    prefilter-handler block of explore_stories.py — either landing page can
    reproduce it.
    """


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the Cross-Industry landing page")
def navigate_to_cross_industry_landing(browser_page, app_url):
    """Navigate via the Home page Cross-Industry card.

    Cross-Industry isn't in the navbar — it's reached by clicking the
    Cross-Industry Transformation card on the Home page (category_cards.py
    Card 2), which sets active_tab="Cross-Industry" and reruns. The hidden
    Streamlit button (key=card_btn_cross_industry) is dispatched via
    native click event to bypass Playwright's visibility check on hidden
    elements.
    """
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(
        "[class*='st-key-card_btn_cross_industry'] button",
        state="attached",
        timeout=30000,
    )
    browser_page.locator(
        "[class*='st-key-card_btn_cross_industry'] button"
    ).first.dispatch_event("click")
    browser_page.wait_for_load_state("networkidle")
    # Wait for the capability cards to render — .capability-card is the
    # per-card class used by Cross-Industry landing markup.
    browser_page.wait_for_selector(".capability-card", timeout=30000)


@given("the user has scrolled down to view a capability card")
def scroll_landing_down(browser_page):
    """Simulate a user scrolled down to view cards before clicking. See
    test_banking_landing.py::scroll_landing_down for full rationale on
    selector choice, 600px scroll amount, and the pre-scroll wait."""
    browser_page.wait_for_timeout(500)  # let landing's setTimeout(100) fire first
    browser_page.evaluate(
        'document.querySelector(\'section[data-testid="stMain"]\').scrollTop = 600'
    )
    browser_page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# WHEN — Click the top capability card
# =============================================================================


@when("the user clicks the top capability card")
def click_top_cross_industry_capability(browser_page):
    """Click the first Core capability card.

    Post-refactor button key: card_btn_cross_industry_core_0 (first Core
    tier card). Pre-refactor key: card_btn_cross_industry_0_0. The selector
    is post-refactor; this step is part of the scenario that intentionally
    expects post-refactor structure.
    """
    browser_page.locator(
        "[class*='st-key-card_btn_cross_industry_core_0'] button"
    ).first.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


# =============================================================================
# THEN — State assertions
# =============================================================================


@then(parsers.parse('the page should display a "{header_text}" section header'))
def assert_section_header_present(browser_page, header_text):
    """Assert a tier section header is rendered on the page.

    Post-refactor: cross_industry_landing.py renders <div class="tier-header">Core Capabilities</div>
    and <div class="tier-header">Specialized Capabilities</div>. The selector
    matches any element with the expected text — pre-refactor pages won't
    have these headers, producing the RED state we want before implementation.
    """
    locator = browser_page.locator(f".tier-header:has-text('{header_text}')").first
    try:
        locator.wait_for(state="visible", timeout=10000)
    except Exception as exc:
        raise AssertionError(
            f"No section header with text '{header_text}' is visible on the "
            f"Cross-Industry landing page. Pre-refactor page rendered a flat "
            f"grid without tier headers — this is expected RED state until "
            f"the data-derivation refactor lands."
        ) from exc


@then(parsers.parse('the active tab should be "{tab_name}"'))
def assert_active_tab(browser_page, tab_name):
    """Verify navigation landed on the expected tab."""
    if tab_name == "My Work":
        browser_page.wait_for_selector(".results-count", timeout=15000)


@then("the My Work page should be scrolled to the top")
def assert_explore_scrolled_to_top(browser_page):
    """Verify the My Work page loaded at the top — same contract as
    test_banking_landing.py. Tolerance: ≤ 50px allows sub-pixel variance.
    """
    scroll_top = browser_page.evaluate(
        'document.querySelector(\'section[data-testid="stMain"]\')?.scrollTop ?? 0'
    )
    assert scroll_top <= 50, (
        f"stMain scrollTop is {scroll_top}px after landing-card click — "
        f"My Work inherited the landing page's scroll position. Fix "
        f"lives in the prefilter handler block in explore_stories.py."
    )


@then(parsers.parse("the result count should be greater than {floor:d}"))
def assert_result_count_above(browser_page, floor):
    """Verify the prefilter narrowed results to at least one story."""
    count_el = browser_page.locator(".results-count").first
    count_el.wait_for(state="visible", timeout=10000)
    text = count_el.inner_text()
    match = re.search(r"of\s+(\d+)\s+project", text)
    assert match, f"Could not parse total count from results-count text: {text!r}"
    actual = int(match.group(1))
    assert actual > floor, (
        f"Expected result count > {floor}, got {actual}. The capability card "
        f"that was clicked has no backing cross-industry stories — a broken "
        f"card slipped through the data-derivation contract."
    )
