"""
BDD step bindings for the Home hero recruiter-routing CTA (MATTGPT-087).

Red (step defs) commit: step definitions are implemented and bound via the
scenarios() loader. Against the current hero (Ask Agy primary, My Work
secondary, NO recruiter CTA) both scenarios fail with assertion errors — the
recruiter-routing CTA does not exist yet. The hero.py production change lands in
the Green commit per the CLAUDE.md testing protocol.

CTA-presence assertions are hero-scoped (.hero-content) so a stray "Ask Agy"
button elsewhere on the page (e.g. the Quick Question card) cannot satisfy them.
"""

import re

from pytest_bdd import given, scenarios, then, when

scenarios("../features/home_hero.feature")

SHORT_WAIT = 200  # ms


def wait_for_streamlit_rerun(page):
    """Wait for Streamlit to finish a rerun after an action."""
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(SHORT_WAIT)


# Label text is the contract (locked from the May 29 wireframe), not a CSS
# class — locators match on label so they survive styling drift.
RECRUITER_CTA_RE = re.compile(r"Match it|Recruiting for a role", re.I)
ASK_AGY_CTA_RE = re.compile(r"Ask Agy", re.I)


def _hero_cta(page, label_re):
    """A CTA (anchor or button) inside the hero whose label matches label_re."""
    return page.locator(".hero-content").locator("a, button").filter(has_text=label_re)


# =============================================================================
# GIVEN — Navigation
# =============================================================================


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    """Home is the default tab. Wait for the hero to render."""
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(".hero-content", timeout=30000)


# =============================================================================
# THEN — CTA presence (hero-scoped)
# =============================================================================


@then("the hero should show a CTA whose label names the recruiter's job")
def assert_recruiter_cta_present(browser_page):
    cta = _hero_cta(browser_page, RECRUITER_CTA_RE)
    assert cta.count() > 0, (
        "No recruiter-routing CTA found in the hero. MATTGPT-087: the hero must "
        "surface a CTA whose label names the recruiter's job "
        "(e.g. 'Recruiting for a role? Match it'), routing to Role Match."
    )


@then("the hero should show an Ask Agy CTA")
def assert_ask_agy_cta_present(browser_page):
    cta = _hero_cta(browser_page, ASK_AGY_CTA_RE)
    assert cta.count() > 0, "No Ask Agy CTA found in the hero."


# =============================================================================
# WHEN / THEN — Recruiter CTA navigation
# =============================================================================


@when("the user clicks the recruiter-routing CTA in the hero")
def click_recruiter_cta(browser_page):
    cta = _hero_cta(browser_page, RECRUITER_CTA_RE)
    assert cta.count() > 0, (
        "Recruiter-routing CTA not present in the hero to click — "
        "MATTGPT-087 hero CTA not implemented yet."
    )
    # Green contract: the visible hero anchor bridges to a hidden Streamlit
    # button (key hero_role_match) that sets active_tab='Role Match', mirroring
    # the #btn-ask / hero_ask pattern in hero.py. Click the hidden button
    # directly to bypass the JS bridge (same approach as test_home.py).
    btn = browser_page.locator("[class*='st-key-hero_role_match'] button").first
    btn.dispatch_event("click")
    wait_for_streamlit_rerun(browser_page)


@then("the Role Match surface should be shown")
def assert_role_match_shown(browser_page):
    # DOM-observable proxy for active_tab == 'Role Match': the Role Match
    # landing renders "Drop a job description..." (role_match.py:771).
    marker = browser_page.locator("text=/Drop a job description/i").first
    marker.wait_for(state="visible", timeout=15000)
    assert (
        marker.count() > 0
    ), "Role Match surface did not render after clicking the recruiter CTA."
