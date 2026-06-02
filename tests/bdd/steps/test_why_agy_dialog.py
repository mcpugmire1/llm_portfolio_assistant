"""
BDD step definitions — MATTGPT-101: Why Agy? badge + dialog.

Red (step defs) gate: all steps bound; assertions target DOM state that
does not yet exist. Against current production (no badge, no Why Agy dialog):

  Scenarios 1-8  (badge presence): FAIL — .why-agy-badge / .why-agy-badge--header
                  do not exist in any surface.
  Scenarios 9-12 (dialog content): FAIL — no [role='dialog'] with title 'Why Agy?'.
  Scenario 13    (sequential):     FAIL — same, no dialog to interact with.

Green: creates ui/components/why_agy_dialog.py (@st.dialog), adds badge HTML
+ hidden st.button + JS bridge to hero.py, landing_view.py,
ask_mattgpt_header.py, banking_landing.py, cross_industry_landing.py; wires
active_dialog == "why_agy" elif blocks in landing_view.py and
conversation_view.py.

CSS class contract (implementation must match):
  .why-agy-badge          — body/hero badges; always visible all viewports
  .why-agy-badge--header  — header badges; CSS hides at ≤768px via media query

DOM selectors:
  Hero badge:             .hero-gradient-wrapper .why-agy-badge
  Landing body badge:     .main-avatar .why-agy-badge
  Ask Agy header badge:   [class*='ask-header'] .why-agy-badge--header
  Banking/CI header badge:.why-agy-badge--header  (one per page — unambiguous)
  Dialog:                 [role='dialog']
  Dialog title:           [role='dialog'] :text('Why Agy?')
  Italic closing line:    [role='dialog'] em  or  [role='dialog'] i

Dual step registration: steps that appear as both And-after-Given (Given type)
and as When or Then are registered with multiple decorators so pytest-bdd's
keyword-type resolver finds them in both contexts.
"""

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/why_agy_dialog.feature")

# =============================================================================
# CONSTANTS
# =============================================================================

LONG_TIMEOUT = 30_000
SHORT_WAIT = 500

# Navigation
HOME_READY = ".hero-gradient-wrapper"
ASK_AGY_BTN = "[class*='st-key-topnav_Ask-Agy'] button"
LANDING_READY = "[class*='st-key-landing_input']"
BANKING_CARD_BTN = "[class*='st-key-card_btn_banking'] button"
BANKING_READY = ".capability-card"
CROSS_CARD_BTN = "[class*='st-key-card_btn_cross_industry'] button"
CROSS_READY = ".capability-card"

# Badge selectors
BADGE_HERO = ".hero-gradient-wrapper .why-agy-badge"
BADGE_LANDING_BODY = ".main-avatar .why-agy-badge"
BADGE_ASK_AGY_HEADER = "[class*='ask-header'] .why-agy-badge--header"
BADGE_HEADER = ".why-agy-badge--header"  # unambiguous on Banking / Cross-Industry

# Dialog
DIALOG_TITLE = "[role='dialog'] :text('Why Agy?')"


# =============================================================================
# HELPERS
# =============================================================================


def _wait(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


def _nav_home(page, app_url, width):
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(app_url)
    _wait(page)
    page.wait_for_selector(HOME_READY, timeout=LONG_TIMEOUT)


def _nav_ask_agy(page, app_url, width):
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    # At mobile viewports (≤767px) the desktop topnav buttons are moved off-screen
    # via CSS (position: absolute; left: -9999px). Use state="attached" + dispatch_event
    # to fire the click regardless of visibility — same pattern as Banking card nav.
    page.wait_for_selector(ASK_AGY_BTN, state="attached", timeout=LONG_TIMEOUT)
    page.locator(ASK_AGY_BTN).first.dispatch_event("click")
    _wait(page)
    page.wait_for_selector(LANDING_READY, timeout=LONG_TIMEOUT)


def _nav_banking(page, app_url, width):
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(BANKING_CARD_BTN, state="attached", timeout=LONG_TIMEOUT)
    page.locator(BANKING_CARD_BTN).first.dispatch_event("click")
    _wait(page)
    page.wait_for_selector(BANKING_READY, timeout=LONG_TIMEOUT)


def _nav_cross(page, app_url, width):
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(app_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(CROSS_CARD_BTN, state="attached", timeout=LONG_TIMEOUT)
    page.locator(CROSS_CARD_BTN).first.dispatch_event("click")
    _wait(page)
    page.wait_for_selector(CROSS_READY, timeout=LONG_TIMEOUT)


# =============================================================================
# GIVEN — Background
# =============================================================================


@given(parsers.parse('the MattGPT app is running at "{url}"'))
def app_is_running(url):
    # No-op — app_url fixture provides the URL; step is documentation only.
    pass


# =============================================================================
# GIVEN — Navigation (with viewport width)
# =============================================================================


@given(parsers.parse("I navigate to the Home page at viewport width {width:d}"))
def navigate_home_viewport(browser_page, app_url, width):
    _nav_home(browser_page, app_url, width)


@given(parsers.parse('I navigate to the "Ask Agy" page at viewport width {width:d}'))
def navigate_ask_agy_viewport(browser_page, app_url, width):
    _nav_ask_agy(browser_page, app_url, width)


@given(
    parsers.parse("I navigate to the Banking landing page at viewport width {width:d}")
)
def navigate_banking_viewport(browser_page, app_url, width):
    _nav_banking(browser_page, app_url, width)


@given(
    parsers.parse(
        "I navigate to the Cross-Industry landing page at viewport width {width:d}"
    )
)
def navigate_cross_viewport(browser_page, app_url, width):
    _nav_cross(browser_page, app_url, width)


# =============================================================================
# GIVEN / WHEN — Badge click
# Registered as both @given and @when: the step appears as "When" in scenario 9
# and as "And" (Given-type) in scenarios 10-13.
# =============================================================================


@given('I click the "i" badge on the Agy intro avatar')
@when('I click the "i" badge on the Agy intro avatar')
def click_landing_body_badge(browser_page):
    badge = browser_page.locator(BADGE_LANDING_BODY)
    badge.wait_for(state="attached", timeout=LONG_TIMEOUT)
    badge.click()
    _wait(browser_page)


# =============================================================================
# GIVEN / THEN — Dialog visible (precondition in scenario 13, assertion in 9)
# =============================================================================


@given('a dialog with title "Why Agy?" is visible')
@then('a dialog with title "Why Agy?" is visible')
def assert_why_agy_dialog_visible(browser_page):
    try:
        browser_page.wait_for_selector(DIALOG_TITLE, timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected [role='dialog'] with title 'Why Agy?' but it was not found. "
            "MATTGPT-101: why_agy_dialog.py not yet wired."
        ) from exc


# =============================================================================
# WHEN — Footer button click
# =============================================================================


@when(parsers.parse('I click the button "{text}"'))
def click_dialog_button(browser_page, text):
    btn = browser_page.locator(f"[role='dialog'] button:has-text('{text}')")
    btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
    btn.click()
    _wait(browser_page)


# =============================================================================
# THEN — Badge assertions
# =============================================================================


@then('the Home hero illustration wrapper has a visible "i" badge')
def assert_hero_badge_visible(browser_page):
    badge = browser_page.locator(BADGE_HERO)
    try:
        badge.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected .why-agy-badge inside .hero-gradient-wrapper to be visible "
            "but it was not found. MATTGPT-101: badge not yet added to hero.py."
        ) from exc


@then('the Agy intro avatar has a visible "i" badge')
def assert_landing_body_badge_visible(browser_page):
    badge = browser_page.locator(BADGE_LANDING_BODY)
    try:
        badge.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected .why-agy-badge inside .main-avatar to be visible "
            "but it was not found. MATTGPT-101: badge not yet added to landing_view.py."
        ) from exc


@then('the Ask Agy header avatar has a visible "i" badge')
def assert_ask_agy_header_badge_visible(browser_page):
    badge = browser_page.locator(BADGE_ASK_AGY_HEADER)
    try:
        badge.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected .why-agy-badge--header inside [class*='ask-header'] to be visible "
            "but it was not found. MATTGPT-101: badge not yet added to ask_mattgpt_header.py."
        ) from exc


@then('the Ask Agy header avatar does not have a visible "i" badge')
def assert_ask_agy_header_badge_hidden_mobile(browser_page):
    badge = browser_page.locator(BADGE_ASK_AGY_HEADER)
    # Badge may be present in the DOM but CSS hides it at ≤768px (display: none).
    # is_visible() returns False for display:none elements.
    is_visible = badge.count() > 0 and badge.first.is_visible()
    assert not is_visible, (
        "Expected .why-agy-badge--header inside ask-header to be hidden at mobile "
        "viewport (≤768px) but it was visible. "
        "MATTGPT-101: mobile CSS exclusion not applied to header badge."
    )


@then('the header avatar has a visible "i" badge')
def assert_header_badge_visible(browser_page):
    # Shared assertion for Banking and Cross-Industry landing pages.
    # Each page has at most one .why-agy-badge--header so the selector is unambiguous.
    badge = browser_page.locator(BADGE_HEADER)
    try:
        badge.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected a .why-agy-badge--header on the landing page header to be visible "
            "but it was not found. MATTGPT-101: badge not yet added to the landing header."
        ) from exc


# =============================================================================
# THEN — Dialog content assertions
# =============================================================================


@then(parsers.parse('the dialog body contains "{text}"'))
def assert_dialog_contains(browser_page, text):
    locator = browser_page.locator(f"[role='dialog'] :text('{text}')")
    try:
        locator.first.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"Expected [role='dialog'] to contain text {text!r} but it was not visible. "
            "MATTGPT-101: Why Agy dialog content incomplete."
        ) from exc


@then(
    parsers.parse(
        'the dialog contains an italic element with text beginning "{prefix}"'
    )
)
def assert_italic_closing_line(browser_page, prefix):
    # Match <em> or <i> elements — both are valid italic HTML.
    italic = browser_page.locator(
        f"[role='dialog'] em:has-text('{prefix}'), "
        f"[role='dialog'] i:has-text('{prefix}')"
    )
    try:
        italic.first.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"Expected italic <em> or <i> containing {prefix!r} inside the dialog "
            "but it was not found. MATTGPT-101: italic closing line not rendered."
        ) from exc


@then(parsers.parse('the dialog contains a button with text "{text}"'))
def assert_dialog_footer_button(browser_page, text):
    btn = browser_page.locator(f"[role='dialog'] button:has-text('{text}')")
    try:
        btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            f"Expected a button with text {text!r} inside the dialog but it was not visible. "
            "MATTGPT-101: footer button not yet added to why_agy_dialog.py."
        ) from exc


@then('no dialog with title "Why Agy?" is visible')
def assert_why_agy_dialog_gone(browser_page):
    dialog = browser_page.locator(DIALOG_TITLE)
    try:
        dialog.wait_for(state="hidden", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Expected 'Why Agy?' dialog to be hidden after footer button click "
            "but it was still visible. "
            "MATTGPT-101: sequential dialog not closing correctly."
        ) from exc
