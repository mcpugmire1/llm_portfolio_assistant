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

from pytest_bdd import scenarios

scenarios("../features/navbar_mobile_viewport_gate.feature")
