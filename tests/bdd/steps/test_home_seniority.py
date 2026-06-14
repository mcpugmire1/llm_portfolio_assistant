"""
BDD step bindings for the Home seniority anchor (MATTGPT-092).

Red (step defs) commit: step definitions are implemented and bound via the
scenarios() loader. Against current production:
  - Scenario 1 fails with an assertion error — the locked positioning clause
    "are part of the same job" is not present on the Home page yet.
  - Scenario 2 passes as a forward-guard — current production has no
    level-title tokens (Director / VP / Vice President / SVP) in the hero
    region or the stats bar, and the Green-phase band must preserve that.

The seniority-band production change lands in the Green commit per the
CLAUDE.md testing protocol.

Scoping notes:
- "the hero region" is used loosely. The seniority band is a SEPARATE
  component below the hero card per f0ad706; the clause assertion is
  page-scoped (body text) since the band's exact CSS scoping is not
  locked yet.
- The level-title guard is scoped to .hero-content (hero card) AND
  .stats-bar (stats row) — those are the two places the "Director · VP
  target" trap could leak in.
"""

import re

from pytest_bdd import given, scenarios, then

scenarios("../features/home_seniority.feature")


LOCKED_CLAUSE = "are part of the same job"
LEVEL_TITLE_TOKENS = re.compile(r"\b(Director|Vice President|VP|SVP)\b")


@given("the user navigates to the home page")
def navigate_to_home(browser_page, app_url):
    browser_page.goto(app_url)
    browser_page.wait_for_load_state("networkidle")
    browser_page.wait_for_selector(".hero-content", timeout=30000)


@then(
    'the hero region should contain the locked positioning clause '
    '"are part of the same job"'
)
def assert_positioning_clause_present(browser_page):
    body_text = browser_page.locator("body").inner_text()
    assert LOCKED_CLAUSE in body_text, (
        f"Locked positioning clause {LOCKED_CLAUSE!r} not found on the Home "
        "page. MATTGPT-092: the seniority band must carry the locked "
        "scope/outcome positioning claim (f0ad706, May 29, 2026)."
    )


@then(
    "no level-title token (Director, VP, Vice President, SVP) should appear "
    "in the hero region or the stats bar"
)
def assert_no_level_title_token(browser_page):
    hero_text = browser_page.locator(".hero-content").inner_text()
    stats_text = browser_page.locator(".stats-bar").inner_text()
    hero_match = LEVEL_TITLE_TOKENS.search(hero_text)
    stats_match = LEVEL_TITLE_TOKENS.search(stats_text)
    assert not hero_match, (
        f"Level-title token {hero_match.group(0)!r} found in hero region. "
        "MATTGPT-092: positioning is a scope/outcome anchor, NOT a title chip."
    )
    assert not stats_match, (
        f"Level-title token {stats_match.group(0)!r} found in stats bar. "
        "MATTGPT-092: stats Level tile must use scope/outcome copy "
        "(e.g. 'Senior leader' / '20+ years' / '0->150 scope'), not "
        "'Director . VP target' or similar title chip."
    )
