"""BDD step definitions for MATTGPT-018 stale-hero suppression on navigation.

MutationObserver approach: observer is installed via page.evaluate() before the
navigation click and stashes results on window._staleObservations. This fires
synchronously when Streamlit sets data-stale="true", allowing getComputedStyle
to be read at the exact instant of staling, with no frame-guessing race.

Scenarios 1 and 2 assert the destination header is visible before reading
observations, so a silent navigation failure surfaces as a header-visible
failure rather than an empty/null observation misread as a pass.

Note: the two observer-installing Given steps both reset window._staleObservations
and stash window._staleObserver. They cannot coexist in one scenario; the second
would clobber the first. They are in separate scenarios today -- add a comment
here if that ever changes.
"""

from playwright.sync_api import expect as pw_expect
from pytest_bdd import given, scenarios, then, when

scenarios("../features/navigation_stale_hero.feature")

SHORT_WAIT = 300

ROLE_MATCH_NAV_SELECTOR = ".st-key-topnav_Role-Match button"
ROLE_MATCH_HEADER_SELECTOR = ".conversation-header h1"
ASK_AGY_NAV_SELECTOR = ".st-key-topnav_Ask-Agy button"


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
    # networkidle never settles in this app (continuous XHR from GDG canvas).
    # Use the Streamlit script-state readiness helper throughout.
    _wait_for_streamlit(browser_page)
    browser_page.locator(ASK_AGY_NAV_SELECTOR).first.click()
    _wait_for_streamlit(browser_page)
    browser_page.wait_for_selector("[class*='st-key-landing_input']", timeout=15000)


@given(
    "a mutation observer is recording computed visibility when containers gain data-stale"
)
def install_visibility_observer(browser_page):
    """Install observer scoped to hero containers (.main-intro-section / .ask-header-landing).

    Gate proof requirement: at Red, scenario 1 must fail on the visibility-value
    assertion ('hidden' expected, 'visible' got), NOT on the 'no observations'
    assertion. If observations is empty at Red, the harness is broken and must
    be fixed before the gate is committed.
    """
    browser_page.evaluate("""() => {
        window._staleObservations = [];
        const observer = new MutationObserver((mutations) => {
            for (const m of mutations) {
                if (m.type !== 'attributes' || m.attributeName !== 'data-stale') continue;
                const el = m.target;
                if (el.getAttribute('data-stale') !== 'true') continue;
                const hasHero = (
                    el.querySelector('.main-intro-section') !== null ||
                    el.querySelector('.ask-header-landing') !== null
                );
                if (!hasHero) continue;
                const vis = getComputedStyle(el).visibility;
                window._staleObservations.push({
                    cls: el.className,
                    visibility: vis,
                    timestamp: Date.now()
                });
            }
        });
        observer.observe(document.body, {
            subtree: true,
            attributes: true,
            attributeFilter: ['data-stale']
        });
        window._staleObserver = observer;
    }""")


@given("a mutation observer is watching for data-stale across the element tree")
def install_canary_observer(browser_page):
    """Install observer watching ANY element gaining data-stale='true'.

    Streamlit-upgrade canary: if a future version stops writing the literal
    attribute string, this observer records nothing and the canary scenario
    fails, surfacing the broken contract before the fix silently becomes a no-op.
    """
    browser_page.evaluate("""() => {
        window._staleObservations = [];
        const observer = new MutationObserver((mutations) => {
            for (const m of mutations) {
                if (m.type !== 'attributes' || m.attributeName !== 'data-stale') continue;
                if (m.target.getAttribute('data-stale') === 'true') {
                    window._staleObservations.push({
                        tag: m.target.tagName,
                        timestamp: Date.now()
                    });
                }
            }
        });
        observer.observe(document.body, {
            subtree: true,
            attributes: true,
            attributeFilter: ['data-stale']
        });
        window._staleObserver = observer;
    }""")


# =============================================================================
# WHEN
# =============================================================================


@when("the user navigates to Role Match")
def navigate_to_role_match(browser_page):
    browser_page.locator(ROLE_MATCH_NAV_SELECTOR).first.click()
    _wait_for_streamlit(browser_page)


# =============================================================================
# THEN
# =============================================================================


@then("the Role Match header should be visible")
def verify_role_match_header_visible(browser_page):
    header = browser_page.locator(ROLE_MATCH_HEADER_SELECTOR)
    assert (
        header.count() > 0
    ), "Role Match header not found: navigation may have silently failed"
    assert (
        header.first.is_visible()
    ), "Role Match header exists but is not visible: navigation did not complete"


@then(
    "the landing hero container was computed visibility hidden at the instant it became stale"
)
def verify_hero_hidden_when_stale(browser_page):
    observations = browser_page.evaluate("() => window._staleObservations || []")
    # If observations is empty here at the Red gate, the harness is broken:
    # the observer did not fire for the hero container. Fix the harness before
    # committing Red -- an empty-observations failure is not a valid Red gate.
    assert observations, (
        "MutationObserver recorded no hero containers gaining data-stale='true'. "
        "Harness failure: observer may not have been installed before navigation, "
        "or '.main-intro-section' / '.ask-header-landing' did not match any "
        "descendant of the stale container. Fix before committing Red."
    )
    for obs in observations:
        assert obs["visibility"] == "hidden", (
            f"Hero container gained data-stale='true' but computed visibility was "
            f"'{obs['visibility']}' (expected 'hidden'). The stale-hide CSS rule "
            f"is absent or not matching. Container class: {obs['cls']}"
        )


@then("at least one element container was marked data-stale during the transition")
def verify_stale_marking_occurred(browser_page):
    observations = browser_page.evaluate("() => window._staleObservations || []")
    assert observations, (
        "MutationObserver recorded zero elements gaining data-stale='true' during "
        "navigation. Streamlit may have changed its stale-marking contract. "
        "If so, the stale-hide CSS rule is a no-op and the blep may have returned. "
        "Re-examine the Streamlit frontend bundle before dismissing as flake."
    )


@then('a stElementContainer wraps a node with class "main-intro-section"')
def verify_main_intro_section_hook(browser_page):
    container = browser_page.locator(
        '[data-testid="stElementContainer"]:has(.main-intro-section)'
    )
    assert container.count() > 0, (
        "No stElementContainer wrapping .main-intro-section found. "
        "If landing_view.py was refactored and the class renamed or moved, "
        "the stale-hide CSS selector no longer targets the hero."
    )


@then('a stElementContainer wraps a node with class "ask-header-landing"')
def verify_ask_header_landing_hook(browser_page):
    container = browser_page.locator(
        '[data-testid="stElementContainer"]:has(.ask-header-landing)'
    )
    assert container.count() > 0, (
        "No stElementContainer wrapping .ask-header-landing found. "
        "If landing_view.py was refactored and the class renamed or moved, "
        "the stale-hide CSS selector no longer targets the header."
    )
