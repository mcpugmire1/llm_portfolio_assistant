"""
BDD step bindings for the How I Built MattGPT deep-link surface (MATTGPT-102).

Red (step defs) commit: step definitions are bound; assertions target the
DOM landmarks that will be rendered by the Green implementation. Against
current production (no ui/pages/how_i_built.py, no ?route= handler, How I
Built section still on About Matt):
  - Scenarios 1-3: FAIL — ?route=how-i-built doesn't render a new page;
    visiting the URL lands on Home (or wherever active_tab points by default).
    The expected DOM landmarks (heading, deep-dive card, back link) won't be
    visible there.
  - Scenario 4: FAILS — My Profile page still contains the How I Built block
    (about_matt.py:159 has the heading).

The Green commit adds the new page, the ?route= handler, the back-link
component, and removes the block from about_matt.py.

URL-driven navigation uses Playwright's page.goto(); back-link locator
matches any element with text containing "Back to" (the Green render
will use a fixed shape like '<a class="back-link">← Back to {label}</a>').
"""

from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/how_i_built.feature")

# =============================================================================
# CONSTANTS
# =============================================================================

LONG_TIMEOUT = 30000
SHORT_WAIT = 200


def _wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


ASK_AGY_NAV_BTN = "[class*='st-key-topnav_Ask-Agy'] button"
LANDING_READY = "[class*='st-key-landing_input']"


# =============================================================================
# GIVEN / WHEN — Dialog entry path scenarios
# =============================================================================


@given(parsers.parse('I navigate to the "Ask Agy" page at viewport width {width:d}'))
def navigate_ask_agy_at_width(browser_page, app_url, width):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(
        ASK_AGY_NAV_BTN, state="attached", timeout=LONG_TIMEOUT
    )
    browser_page.locator(ASK_AGY_NAV_BTN).first.dispatch_event("click")
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_timeout(SHORT_WAIT)
    browser_page.wait_for_selector(LANDING_READY, timeout=LONG_TIMEOUT)


@given("the user is on the Ask Agy landing page")
def navigate_to_ask_agy_landing(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(
        ASK_AGY_NAV_BTN, state="attached", timeout=LONG_TIMEOUT
    )
    browser_page.locator(ASK_AGY_NAV_BTN).first.dispatch_event("click")
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_timeout(SHORT_WAIT)
    browser_page.wait_for_selector(LANDING_READY, timeout=LONG_TIMEOUT)


@given('I click the "i" badge on the Agy intro avatar')
def click_landing_body_badge(browser_page):
    badge = browser_page.locator(".main-avatar .why-agy-badge")
    badge.wait_for(state="attached", timeout=LONG_TIMEOUT)
    badge.click()
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_timeout(SHORT_WAIT)


@given('a dialog with title "Why Agy?" is visible')
def assert_why_agy_dialog_open(browser_page):
    browser_page.wait_for_selector(
        "[role='dialog'] :text('Why Agy?')", timeout=LONG_TIMEOUT
    )


@given('the user clicks the "How Agy searches" button')
def click_how_agy_searches_btn(browser_page):
    btn = browser_page.locator("button:has-text('How Agy searches'):visible").first
    btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
    btn.click()
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_timeout(SHORT_WAIT)


@given("the How Agy Searches dialog is visible")
def assert_how_agy_searches_dialog_open(browser_page):
    browser_page.wait_for_selector(
        "[role='dialog'] :text('How Agy searches')", timeout=LONG_TIMEOUT
    )


@when(parsers.parse('I click the button "{text}"'))
def click_button_in_dialog(browser_page, text):
    btn = browser_page.locator(f"[role='dialog'] button:has-text('{text}')").first
    btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
    btn.click()
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_timeout(SHORT_WAIT)


# =============================================================================
# GIVEN — Navigation (standalone page scenarios)
# =============================================================================


@given(parsers.parse('the user navigates to "{url_path}"'))
def navigate_to_url_path(browser_page, app_url, url_path):
    """Navigate to a URL path on the app — strip leading slash so the path
    appends cleanly to app_url. Used for ?route=how-i-built[&from=X] URLs.
    """
    # Strip leading slash if present, since app_url is typically a full URL
    # like http://localhost:8501 without a trailing slash.
    suffix = url_path.lstrip("/")
    full_url = app_url.rstrip("/") + "/" + suffix
    browser_page.goto(full_url)
    _wait_for_streamlit_rerun(browser_page)


@given("the user navigates to the My Profile page")
def navigate_to_my_profile(browser_page, app_url):
    """Open the app and click the My Profile nav button."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(
        "button:has-text('My Profile')", timeout=LONG_TIMEOUT
    )
    nav_button = browser_page.locator("button:has-text('My Profile'):visible").first
    nav_button.click()
    _wait_for_streamlit_rerun(browser_page)
    # My Profile page has a unique landmark; wait for the page to render.
    browser_page.wait_for_selector(
        ".am-section-title, .about-header", timeout=LONG_TIMEOUT
    )


# =============================================================================
# THEN — Heading + content visibility
# =============================================================================


@then('the "How I Built MattGPT" heading should be visible')
def assert_how_i_built_heading_visible(browser_page):
    heading = browser_page.locator("h2:has-text('How I Built MattGPT')").first
    try:
        heading.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "How I Built MattGPT heading not visible. MATTGPT-102: the "
            f"?route=how-i-built handler doesn't render the new page yet. "
            f"Underlying error: {exc}"
        ) from exc


@then('the "The Problem" deep-dive card should be visible')
def assert_the_problem_card_visible(browser_page):
    card = browser_page.locator(".deep-dive-card:has(h3:has-text('The Problem'))").first
    try:
        card.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "'The Problem' deep-dive card not visible on the How I Built "
            "surface. MATTGPT-102: content relocation from about_matt.py "
            f"is incomplete. Underlying error: {exc}"
        ) from exc


@then("the back link should be visible")
def assert_back_link_visible(browser_page):
    # The Green render will use a link/button with text containing "Back to".
    back_link = browser_page.locator("a.back-link").first
    try:
        back_link.wait_for(state="visible", timeout=LONG_TIMEOUT)
    except Exception as exc:
        raise AssertionError(
            "Back link not visible on the How I Built surface. MATTGPT-102: "
            "the back-link component isn't rendered yet. Expected an element "
            "with text containing 'Back to'. "
            f"Underlying error: {exc}"
        ) from exc


@then(parsers.parse('the back link text should contain "{expected_label}"'))
def assert_back_link_text(browser_page, expected_label):
    back_link = browser_page.locator("a.back-link").first
    back_link.wait_for(state="visible", timeout=LONG_TIMEOUT)
    text = back_link.inner_text()
    assert expected_label in text, (
        f"Back link text should contain {expected_label!r}, found: {text!r}. "
        f"MATTGPT-102: from-param → label mapping isn't wired correctly."
    )


# =============================================================================
# THEN — Dialog visibility (How I Built as @st.dialog)
# =============================================================================


@then(parsers.parse('a dialog with title "{title}" is visible'))
def assert_dialog_with_title_visible(browser_page, title):
    try:
        browser_page.wait_for_selector(
            f"[role='dialog'] :text('{title}')", timeout=LONG_TIMEOUT
        )
    except Exception as exc:
        raise AssertionError(
            f"Expected a dialog titled '{title}' but it was not found. "
            f"MATTGPT-102: render_how_i_built_dialog() not yet implemented."
        ) from exc


# =============================================================================
# THEN — Content removal from My Profile
# =============================================================================


@then('the "How I Built MattGPT" heading should NOT be visible on the My Profile page')
def assert_no_how_i_built_on_profile(browser_page):
    # Locate any heading on the page containing "How I Built MattGPT".
    headings = browser_page.locator(":text('How I Built MattGPT')")
    count = headings.count()
    assert count == 0, (
        f"My Profile page still contains {count} element(s) referencing 'How I "
        f"Built MattGPT'. MATTGPT-102: content should be relocated to the new "
        f"deep-link surface, not duplicated on My Profile."
    )
