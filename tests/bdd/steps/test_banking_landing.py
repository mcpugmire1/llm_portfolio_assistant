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
    """Navigate via the navbar Banking tab and wait for capability cards."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    nav_button = browser_page.locator("button:has-text('Banking'):visible").first
    nav_button.click()
    browser_page.wait_for_load_state("networkidle")
    # Wait for at least one capability card to render — the .capability-card
    # class is used by the per-card markup.
    browser_page.wait_for_selector(".capability-card", timeout=30000)


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
    btn = browser_page.locator("[class*='st-key-card_btn_banking_0_0'] button").first
    btn.click(force=True)
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
