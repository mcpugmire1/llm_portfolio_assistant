"""
BDD step definitions for navbar CSS scope regression guard (MATTGPT-110 fix).

These are regression guards: the production code is already fixed. They pass
now and will fail if someone reintroduces a broad gap-zeroing CSS rule that
hits the chip grid's left column.

The bug: navbar.py had "stHorizontalBlock > stColumn:first-child stVerticalBlock
{ gap: 0 }" with no scope guard, zeroing row-gap on the chip grid left column.
Fix: added :has([class*="st-key-topnav_"]) guard. This test enforces that guard.
"""

from pytest_bdd import given, scenarios, then

scenarios("../features/navbar_css_scope.feature")

LONG_TIMEOUT = 30000
SHORT_WAIT = 500
ASK_AGY_NAV_SELECTOR = ".st-key-topnav_Ask-Agy button"


def _wait(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


@given("the user navigates to the Ask Agy landing page")
def navigate_to_ask_agy(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(ASK_AGY_NAV_SELECTOR, timeout=LONG_TIMEOUT)
    browser_page.locator(ASK_AGY_NAV_SELECTOR).first.click()
    _wait(browser_page)
    browser_page.wait_for_selector(
        "[class*='st-key-landing_input']", timeout=LONG_TIMEOUT
    )
    browser_page.wait_for_selector(
        "[class*='st-key-suggested_0']", timeout=LONG_TIMEOUT
    )


@then("the left chip column row-gap should equal the right chip column row-gap")
def assert_chip_columns_equal_gap(browser_page):
    left_gap = browser_page.evaluate("""() => {
        const chip = document.querySelector('[class*="st-key-suggested_0"]');
        if (!chip) return null;
        const col = chip.closest('[data-testid="stColumn"]');
        if (!col) return null;
        const vblock = col.querySelector('[data-testid="stVerticalBlock"]');
        if (!vblock) return null;
        return parseFloat(window.getComputedStyle(vblock).rowGap) || 0;
    }""")
    right_gap = browser_page.evaluate("""() => {
        const chip = document.querySelector('[class*="st-key-suggested_1"]');
        if (!chip) return null;
        const col = chip.closest('[data-testid="stColumn"]');
        if (!col) return null;
        const vblock = col.querySelector('[data-testid="stVerticalBlock"]');
        if (!vblock) return null;
        return parseFloat(window.getComputedStyle(vblock).rowGap) || 0;
    }""")
    assert left_gap is not None, "Could not find left chip column stVerticalBlock"
    assert right_gap is not None, "Could not find right chip column stVerticalBlock"
    assert left_gap == right_gap, (
        f"Chip grid columns have unequal row-gap: left={left_gap}px, right={right_gap}px. "
        "Likely a broad CSS gap-zeroing rule without :has([class*='st-key-topnav_']) guard."
    )


@then("the left chip column row-gap should be greater than 0px")
def assert_left_chip_gap_nonzero(browser_page):
    left_gap = browser_page.evaluate("""() => {
        const chip = document.querySelector('[class*="st-key-suggested_0"]');
        if (!chip) return null;
        const col = chip.closest('[data-testid="stColumn"]');
        if (!col) return null;
        const vblock = col.querySelector('[data-testid="stVerticalBlock"]');
        if (!vblock) return null;
        return parseFloat(window.getComputedStyle(vblock).rowGap) || 0;
    }""")
    assert left_gap is not None, "Could not find left chip column stVerticalBlock"
    assert left_gap > 0, (
        f"Left chip column row-gap is {left_gap}px — chip grid spacing collapsed. "
        "A CSS rule is zeroing gap on the left column's stVerticalBlock."
    )


@then("the navbar brand column row-gap should be 0px")
def assert_navbar_brand_gap_zero(browser_page):
    navbar_gap = browser_page.evaluate("""() => {
        const navbar = document.querySelector('[class*="st-key-topnav_"]');
        if (!navbar) return null;
        const block = navbar.closest('[data-testid="stHorizontalBlock"]');
        if (!block) return null;
        const firstCol = block.querySelector('[data-testid="stColumn"]');
        if (!firstCol) return null;
        const vblock = firstCol.querySelector('[data-testid="stVerticalBlock"]');
        if (!vblock) return null;
        return parseFloat(window.getComputedStyle(vblock).rowGap) || 0;
    }""")
    assert navbar_gap is not None, "Could not find navbar brand column stVerticalBlock"
    assert navbar_gap == 0, (
        f"Navbar brand column row-gap should be 0px but is {navbar_gap}px. "
        "The navbar gap-zeroing rule is not applying correctly."
    )
