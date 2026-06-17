"""
BDD step bindings for MATTGPT-135: mobile navbar IIFE viewport gate.

The IIFE in ui/components/navbar.py runs unconditionally today, injecting
mobile-header, mobile-nav-overlay, and mobile-nav-dropdown into
window.parent.document on every Streamlit rerun regardless of viewport
width. On desktop this causes a double-Agy-avatar flash during page
transitions (stale elements from the destroy/recreate gap).

Fix: early-return guard at the very top of the IIFE when
window.innerWidth > 767, matching the existing CSS breakpoint.

Timing note for the desktop "not present" scenario:
  components.html renders via a srcdoc iframe -- no HTTP request -- so
  Playwright's networkidle can settle before the iframe executes its
  script. navigate_to_home waits for [class*="st-key-topnav_"], which
  confirms Streamlit has rendered and components.html has been
  instantiated. An additional IIFE_SETTLE_MS pause then gives the
  script time to have fired (and injected, if it was going to) before
  asserting absence.

Selectors used:
  #mobile-header        -- fixed mobile nav bar
  #mobile-nav-dropdown  -- slide-down nav menu
  #mobile-nav-overlay   -- tap-to-close backdrop

Verified: browser_page.locator() searches the main Streamlit document,
which is window.parent.document from the iframe's perspective.
test_role_match.py lines 405-406 already use this pattern for the same
IIFE-injected elements and those tests pass.
"""

from pytest_bdd import given, parsers, scenarios, then

scenarios("../features/navbar_mobile_viewport_gate.feature")

IIFE_SETTLE_MS = 500
LONG_WAIT = 15000


@given(parsers.parse("the viewport is {width:d}px wide"))
def set_viewport(browser_page, width):
    browser_page.set_viewport_size({"width": width, "height": 900})


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    # Confirms Streamlit has fully rendered and components.html is instantiated.
    # state="attached" not "visible" -- at mobile viewport (<768px) the desktop
    # nav buttons are CSS-offscreened (left:-9999px) so visible would time out.
    browser_page.wait_for_selector(
        '[class*="st-key-topnav_"]', state="attached", timeout=LONG_WAIT
    )


@then(parsers.parse('"{element_id}" should not exist in the parent document'))
def element_should_not_exist(browser_page, element_id):
    # Step 1: navigate_to_home already confirmed Streamlit rendered +
    #         components.html instantiated (see module docstring).
    # Step 2: explicit pause so the IIFE has time to fire before asserting absence.
    browser_page.wait_for_timeout(IIFE_SETTLE_MS)
    assert browser_page.locator(element_id).count() == 0, (
        f"Expected {element_id} to be absent on desktop (viewport > 767px) "
        f"after MATTGPT-135 viewport gate. IIFE injected it despite wide viewport."
    )


@then(parsers.parse('"{element_id}" should exist in the parent document'))
def element_should_exist(browser_page, element_id):
    # state="attached" not "visible" -- dropdown is in DOM but display:none
    # until hamburger is clicked.
    browser_page.locator(element_id).wait_for(state="attached", timeout=5000)
    assert browser_page.locator(element_id).count() > 0, (
        f"Expected {element_id} to be present on mobile (viewport <= 767px). "
        f"IIFE should inject mobile nav elements at this viewport width."
    )
