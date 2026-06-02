"""
BDD step definitions for How Agy Searches @st.dialog migration (MATTGPT-110).

Red (step defs) commit: step definitions bound; assertions target DOM-observable
state. Against current production (inline expander, not @st.dialog):
  - Scenario 1: FAILS — no [role='dialog'] visible; content renders inline, not in overlay
  - Scenario 2: FAILS — no dialog to dismiss
  - Scenario 3: PASSES today (inline wrapper IS present) — becomes regression guard in Green
  - Scenario 4: FAILS — no footer "See how I built it" button exists today
  - Scenario 5: FAILS — same as scenario 1, on conversation view

Green: replaces inline expander with @st.dialog in landing_view.py and
conversation_view.py; rewrites get_how_agy_flow_html() content as native
Streamlit; removes Technical Details block; adds footer st.button.

DOM landmarks:
  - Dialog: [role='dialog'] (Streamlit @st.dialog renders this)
  - Dialog title: [role='dialog'] :text("How Agy searches")
  - Inline wrapper (old pattern): .how-agy-modal-wrapper
  - "How Agy searches" button: button:has-text("How Agy searches") visible
  - Footer button: [role='dialog'] button:has-text("See how I built it")
  - Conversation nav: submit a query first to reach conversation view
"""

from pytest_bdd import given, scenarios, then, when

scenarios("../features/how_agy_searches_dialog.feature")

# =============================================================================
# CONSTANTS — mirrors test_ask_mattgpt.py conventions
# =============================================================================

LONG_TIMEOUT = 30000
SHORT_WAIT = 500

ASK_AGY_NAV_SELECTOR = ".st-key-topnav_Ask-Agy button"
HOW_AGY_BTN = "button:has-text('How Agy searches'):visible"
DIALOG_SELECTOR = "[role='dialog']"
DIALOG_TITLE = "[role='dialog'] :text('How Agy searches')"
INLINE_WRAPPER = ".how-agy-modal-wrapper"
FOOTER_BTN = "[role='dialog'] button:has-text('See how I built it')"


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
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the Ask Agy landing page")
def navigate_to_ask_agy_landing(browser_page, app_url):
    _nav_to_ask_agy(browser_page, app_url)


@given("the user navigates to the Ask Agy conversation view")
def navigate_to_ask_agy_conversation(browser_page, app_url):
    _nav_to_ask_agy(browser_page, app_url)
    # Submit a starter query to reach conversation view
    landing_input = browser_page.locator(
        "[class*='st-key-landing_input'] input[type='text']"
    )
    landing_input.wait_for(state="visible", timeout=LONG_TIMEOUT)
    landing_input.fill("How did Matt build teams?")
    landing_input.press("Enter")
    _wait(browser_page)
    # Wait for conversation view (chat input appears)
    browser_page.wait_for_selector(
        "textarea, [data-testid='stChatInput']", timeout=LONG_TIMEOUT
    )


# =============================================================================
# WHEN — Interactions
# =============================================================================


@when('the user clicks the "How Agy searches" button')
def click_how_agy_searches(browser_page):
    btn = browser_page.locator(HOW_AGY_BTN).first
    btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
    btn.click()
    _wait(browser_page)


@when("the user dismisses the dialog")
def dismiss_dialog(browser_page):
    # Press Escape to dismiss — most reliable cross-surface close
    browser_page.keyboard.press("Escape")
    _wait(browser_page)


# =============================================================================
# THEN — Assertions
# =============================================================================


@then('a dialog titled "How Agy searches" should be visible')
def assert_dialog_visible(browser_page):
    try:
        browser_page.wait_for_selector(DIALOG_SELECTOR, timeout=LONG_TIMEOUT)
        browser_page.wait_for_selector(DIALOG_TITLE, timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected a @st.dialog overlay titled 'How Agy searches' but it was not found. "
            "MATTGPT-110: inline expander not yet replaced by @st.dialog."
        ) from exc


@then('the dialog should contain the text "{text}"')
def assert_dialog_contains_text(browser_page, text):
    locator = browser_page.locator(f"[role='dialog'] :text('{text}')")
    try:
        locator.first.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"Expected dialog to contain text {text!r} but it was not visible. "
            "MATTGPT-110: dialog content may not be rendering correctly."
        ) from exc


@then("the dialog should not be visible")
def assert_dialog_not_visible(browser_page):
    dialog = browser_page.locator(DIALOG_SELECTOR)
    try:
        dialog.wait_for(state="hidden", timeout=LONG_TIMEOUT)
    except Exception as exc:
        count = dialog.count()
        raise AssertionError(
            f"Expected dialog to be hidden after dismiss but found {count} dialog(s) visible. "
            "MATTGPT-110: dialog dismiss not working correctly."
        ) from exc


@then("no inline how-agy-modal-wrapper should be present in the page body")
def assert_no_inline_wrapper(browser_page):
    # Old pattern: .how-agy-modal-wrapper renders inline in the page body.
    # After migration this element must not exist.
    count = browser_page.locator(INLINE_WRAPPER).count()
    assert count == 0, (
        f"Found {count} .how-agy-modal-wrapper element(s) in page body. "
        "MATTGPT-110: inline expander wrapper still present — migration incomplete."
    )


@then('the dialog should contain a button with text "See how I built it"')
def assert_footer_button_present(browser_page):
    try:
        browser_page.wait_for_selector(FOOTER_BTN, timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected a 'See how I built it' button inside the dialog but it was not found. "
            "MATTGPT-110: footer st.button not yet added to How Agy Searches dialog."
        ) from exc
