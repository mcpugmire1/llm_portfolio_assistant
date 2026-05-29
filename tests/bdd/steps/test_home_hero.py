"""
BDD step bindings for the Home hero recruiter-routing CTA (MATTGPT-087).

Red (scenarios) commit: the two scenarios are bound via the scenarios() loader
with NO step definitions yet, so every step resolves to undefined-step state
(StepDefinitionNotFoundError). Step definitions land in the Red (step defs)
commit, and the hero.py production change in the Green commit, per the CLAUDE.md
testing protocol.

Green-phase note: the "hero should show a CTA ..." step defs must scope their
locator to the hero region (e.g. a data-testid="hero" container) so a stray
"Ask Agy" button elsewhere on the page can't satisfy the assertion.
"""

from pytest_bdd import scenarios

scenarios("../features/home_hero.feature")
