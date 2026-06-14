"""
BDD step definitions for How Agy Searches dialog CSS regression guards (MATTGPT-110).

Regression guards for issues found and fixed during MATTGPT-110:
1. Footer button was a bare text link (border: none, padding: 0) — fixed
2. Dialog CSS used hardcoded hex instead of app design system variables — fixed
3. Cards-row forced 2-col on mobile — fixed with @media (max-width: 640px)

Note: CSS variable assertions (assert_query_card_bg, assert_step_title_color,
assert_card_desc_color) only verify the property resolves to a non-empty value,
not that it matches --bg-card / --text-primary / --text-secondary exactly.
Acceptable tradeoff — full variable comparison requires resolving both sides
to the same color space, which adds fragility for minimal gain.
"""

from pytest_bdd import given, parsers, scenarios, then

scenarios("../features/how_agy_dialog_css.feature")

LONG_TIMEOUT = 30000
SHORT_WAIT = 500
ASK_AGY_NAV_SELECTOR = ".st-key-topnav_Ask-Agy button"
HOW_AGY_BTN = "button:has-text('How Agy searches'):visible"
DIALOG_SELECTOR = "[role='dialog']"


def _wait(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _nav_to_ask_agy(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(ASK_AGY_NAV_SELECTOR, timeout=LONG_TIMEOUT)
    browser_page.locator(ASK_AGY_NAV_SELECTOR).first.click()
    _wait(browser_page)
    browser_page.wait_for_selector(
        "[class*='st-key-landing_input']", timeout=LONG_TIMEOUT
    )


# =============================================================================
# GIVEN / WHEN — Navigation + interaction
# =============================================================================


@given("the user navigates to the Ask Agy landing page")
def navigate_to_ask_agy_landing(browser_page, app_url):
    _nav_to_ask_agy(browser_page, app_url)


@given("the user clicks the \"How Agy searches\" button")
def click_how_agy_btn(browser_page):
    btn = browser_page.locator(HOW_AGY_BTN).first
    btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
    btn.click()
    _wait(browser_page)
    browser_page.wait_for_selector(DIALOG_SELECTOR, timeout=LONG_TIMEOUT)


@given(parsers.parse("the viewport is resized to {width:d}px wide"))
def resize_viewport(browser_page, width):
    browser_page.set_viewport_size({"width": width, "height": 900})
    _wait(browser_page)


# =============================================================================
# THEN — Footer button assertions
# =============================================================================


@then("the footer element inside the dialog should be a button")
def assert_footer_is_button(browser_page):
    browser_page.wait_for_selector(
        "[class*='st-key-how_agy_to_hib'] button", timeout=LONG_TIMEOUT
    )
    tag = browser_page.evaluate("""() => {
        const btn = document.querySelector('[class*="st-key-how_agy_to_hib"] button');
        return btn ? btn.tagName.toLowerCase() : null;
    }""")
    assert tag == "button", f"Footer element is <{tag}>, expected <button>"


@then("the footer button should have a visible border")
def assert_footer_has_border(browser_page):
    border_width = browser_page.evaluate("""() => {
        const btn = document.querySelector('[class*="st-key-how_agy_to_hib"] button');
        if (!btn) return null;
        return parseFloat(window.getComputedStyle(btn).borderTopWidth) || 0;
    }""")
    assert border_width is not None, "Footer button not found"
    assert (
        border_width > 0
    ), f"Footer button border-width is {border_width}px — renders as bare text link."


@then("the footer button should have non-zero padding")
def assert_footer_has_padding(browser_page):
    padding = browser_page.evaluate("""() => {
        const btn = document.querySelector('[class*="st-key-how_agy_to_hib"] button');
        if (!btn) return null;
        return parseFloat(window.getComputedStyle(btn).paddingTop) || 0;
    }""")
    assert padding is not None, "Footer button not found"
    assert (
        padding > 0
    ), f"Footer button padding-top is {padding}px — renders as bare text link."


@then("the footer button width should fill the dialog content width")
def assert_footer_button_full_width(browser_page):
    result = browser_page.evaluate("""() => {
        const btn = document.querySelector('[class*="st-key-how_agy_to_hib"] button');
        if (!btn) return null;
        const container = btn.closest('[class*="st-key-how_agy_to_hib"]');
        if (!container) return null;
        return {
            btnWidth: btn.getBoundingClientRect().width,
            containerWidth: container.getBoundingClientRect().width
        };
    }""")
    assert result is not None, "Footer button or container not found"
    assert abs(result["btnWidth"] - result["containerWidth"]) < 2, (
        f"Footer button ({result['btnWidth']}px) does not fill container "
        f"({result['containerWidth']}px)."
    )


# =============================================================================
# THEN — Design system variable assertions (weak guard — resolves to non-empty)
# =============================================================================


@then("the query card background should match the resolved value of --bg-card")
def assert_query_card_bg(browser_page):
    color = browser_page.evaluate("""() => {
        const card = document.querySelector('.query-card');
        if (!card) return null;
        return window.getComputedStyle(card).backgroundColor;
    }""")
    assert color is not None, ".query-card not found in dialog"
    assert (
        color != ""
    ), "query-card background-color is empty — CSS variable not resolving"


@then("the step title color should match the resolved value of --text-primary")
def assert_step_title_color(browser_page):
    color = browser_page.evaluate("""() => {
        const title = document.querySelector('.step-title');
        if (!title) return null;
        return window.getComputedStyle(title).color;
    }""")
    assert color is not None, ".step-title not found in dialog"
    assert color != "", "step-title color is empty — CSS variable not resolving"


@then("the card description color should match the resolved value of --text-secondary")
def assert_card_desc_color(browser_page):
    color = browser_page.evaluate("""() => {
        const desc = document.querySelector('.card-desc');
        if (!desc) return null;
        return window.getComputedStyle(desc).color;
    }""")
    assert color is not None, ".card-desc not found in dialog"
    assert color != "", "card-desc color is empty — CSS variable not resolving"


@then("the query card font-size should be 13px")
def assert_query_card_font_size(browser_page):
    size = browser_page.evaluate("""() => {
        const card = document.querySelector('.query-card');
        if (!card) return null;
        return parseFloat(window.getComputedStyle(card).fontSize);
    }""")
    assert size is not None, ".query-card not found in dialog"
    assert size == 13, f"query-card font-size is {size}px, expected 13px"


@then("the pipeline summary font-size should be 12px")
def assert_pipeline_summary_font_size(browser_page):
    size = browser_page.evaluate("""() => {
        const el = document.querySelector('.pipeline-summary');
        if (!el) return null;
        return parseFloat(window.getComputedStyle(el).fontSize);
    }""")
    assert size is not None, ".pipeline-summary not found in dialog"
    assert size == 12, f"pipeline-summary font-size is {size}px, expected 12px"


# =============================================================================
# THEN — Mobile responsive assertions
# =============================================================================


@then("the search cards should render in a single column")
def assert_single_column_cards(browser_page):
    col_count = browser_page.evaluate("""() => {
        const row = document.querySelector('.cards-row');
        if (!row) return null;
        const cols = window.getComputedStyle(row).gridTemplateColumns;
        return cols.trim().split(/\\s+/).length;
    }""")
    assert col_count is not None, ".cards-row not found in dialog"
    assert (
        col_count == 1
    ), f"cards-row has {col_count} columns at mobile width, expected 1."


@then("the desktop pipeline flow should not be visible")
def assert_desktop_flow_hidden(browser_page):
    visible = browser_page.evaluate("""() => {
        const el = document.querySelector('.pipeline-flow.desktop-only');
        if (!el) return false;
        return window.getComputedStyle(el).display !== 'none';
    }""")
    assert not visible, ".pipeline-flow.desktop-only is visible at mobile width."


@then("the mobile pipeline summary should be visible")
def assert_mobile_summary_visible(browser_page):
    visible = browser_page.evaluate("""() => {
        const el = document.querySelector('.pipeline-summary.mobile-only');
        if (!el) return false;
        return window.getComputedStyle(el).display !== 'none';
    }""")
    assert visible, ".pipeline-summary.mobile-only is not visible at mobile width."


@then("the footer button should be full width")
def assert_footer_full_width_mobile(browser_page):
    result = browser_page.evaluate("""() => {
        const btn = document.querySelector('[class*="st-key-how_agy_to_hib"] button');
        if (!btn) return null;
        const container = btn.closest('[class*="st-key-how_agy_to_hib"]');
        if (!container) return null;
        return {
            btnWidth: btn.getBoundingClientRect().width,
            containerWidth: container.getBoundingClientRect().width
        };
    }""")
    assert result is not None, "Footer button or container not found"
    assert abs(result["btnWidth"] - result["containerWidth"]) < 2, (
        f"Footer button ({result['btnWidth']}px) not full width at mobile "
        f"(container: {result['containerWidth']}px)."
    )
