"""BDD step definitions: Ask Agy button alignment and focus ring (MATTGPT-033).

Landing page: landing_ask button sits in a column adjacent to the text input.
Streamlit's stBaseButton-primary applies margin-top: 10px by default, pushing
the button down.

Conversation page: stChatInputSubmitButton sits inside an absolutely-positioned
40px-tall wrapper inside Streamlit's stChatInput widget. Streamlit applies
transform: translateY(0.5px) as a baseline nudge.

Focus ring coverage is in tests/unit/test_ask_agy_button_css.py:
- Landing button: Tab triggers on_change navigation before :focus-visible is readable.
- Conversation submit button: Streamlit intercepts Tab in the textarea; focus
  drops to BODY instead of moving to the submit button.
"""

from playwright.sync_api import expect as pw_expect
from pytest_bdd import given, scenarios, then

scenarios("../features/ask_agy_button_alignment.feature")

SHORT_WAIT = 300
ASK_AGY_NAV_SELECTOR = ".st-key-topnav_Ask-Agy button"
LANDING_BUTTON_SELECTOR = ".st-key-landing_ask button"
LANDING_INPUT_SELECTOR = "[class*='st-key-landing_input'] input"
CHAT_SUBMIT_SELECTOR = "button[data-testid='stChatInputSubmitButton']"
CHAT_TEXTAREA_SELECTOR = "textarea[data-testid='stChatInputTextArea']"


def _wait_for_streamlit(page, timeout=15000):
    stapp = page.locator('[data-testid="stApp"]')
    try:
        pw_expect(stapp).to_have_attribute(
            "data-test-script-state", "running", timeout=2000
        )
    except Exception:
        pass
    pw_expect(stapp).to_have_attribute(
        "data-test-script-state", "notRunning", timeout=timeout
    )
    page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# GIVEN
# =============================================================================


@given("the user navigates to the Ask Agy landing page")
def navigate_to_ask_agy(browser_page, app_url):
    browser_page.goto(app_url)
    _wait_for_streamlit(browser_page)
    browser_page.locator(ASK_AGY_NAV_SELECTOR).first.click()
    _wait_for_streamlit(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)


@given("the user navigates to the Ask Agy conversation page")
def navigate_to_ask_agy_conversation(browser_page, app_url):
    browser_page.goto(app_url)
    _wait_for_streamlit(browser_page)
    browser_page.locator(ASK_AGY_NAV_SELECTOR).first.click()
    _wait_for_streamlit(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)
    # fill + Tab commits the value via on_change → landing_input_submitted=True →
    # Streamlit navigates to conversation automatically. No button click needed.
    browser_page.locator(LANDING_INPUT_SELECTOR).fill("Tell me about Matt")
    browser_page.locator(LANDING_INPUT_SELECTOR).press("Tab")
    _wait_for_streamlit(browser_page, timeout=45000)
    browser_page.wait_for_selector(CHAT_SUBMIT_SELECTOR, timeout=15000)


# =============================================================================
# THEN — landing button
# =============================================================================


@then("the landing Ask button computed margin-top is 0px")
def verify_landing_button_margin_top(browser_page):
    margin = browser_page.evaluate(
        f"""() => {{
            const btn = document.querySelector('{LANDING_BUTTON_SELECTOR}');
            return window.getComputedStyle(btn).marginTop;
        }}"""
    )
    assert margin == "0px", f"Expected margin-top 0px, got {margin!r}"


@then("the landing Ask button computed min-height is 44px")
def verify_landing_button_min_height(browser_page):
    min_height = browser_page.evaluate(
        f"""() => {{
            const btn = document.querySelector('{LANDING_BUTTON_SELECTOR}');
            return window.getComputedStyle(btn).minHeight;
        }}"""
    )
    assert min_height == "44px", f"Expected min-height 44px, got {min_height!r}"


# =============================================================================
# THEN — conversation submit button
# =============================================================================


@then("the conversation submit button computed min-height is auto")
def verify_chat_submit_min_height(browser_page):
    # The button sits in a position:absolute 40px-tall wrapper; any min-height
    # greater than 40px causes upward overflow. Leave Streamlit's layout in control.
    min_height = browser_page.evaluate(
        f"""() => {{
            const btn = document.querySelector("{CHAT_SUBMIT_SELECTOR}");
            return window.getComputedStyle(btn).minHeight;
        }}"""
    )
    assert min_height == "auto", f"Expected min-height auto, got {min_height!r}"


@then("the conversation submit button transform Y translation is zero")
def verify_chat_submit_no_translate_y(browser_page):
    ty = browser_page.evaluate(
        f"""() => {{
            const btn = document.querySelector("{CHAT_SUBMIT_SELECTOR}");
            const matrix = window.getComputedStyle(btn).transform;
            // matrix(a,b,c,d,tx,ty) — ty is the 6th value; none means no translation
            const match = matrix.match(/matrix\\(([^)]+)\\)/);
            if (!match) return 0;
            const values = match[1].split(',').map(Number);
            return values[5];
        }}"""
    )
    assert ty == 0, (
        f"Expected Y translation 0, got {ty!r} — "
        "Streamlit's translateY(0.5px) nudge not overridden"
    )
