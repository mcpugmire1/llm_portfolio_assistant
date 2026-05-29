"""
BDD step bindings for the Home seniority anchor (MATTGPT-092).

Red (scenarios) commit: the two scenarios are bound via the scenarios() loader
with NO step definitions yet, so every step resolves to undefined-step state
(StepDefinitionNotFoundError). Step definitions land in the Red (step defs)
commit, and the seniority-band production change in the Green commit, per the
CLAUDE.md testing protocol.
"""

from pytest_bdd import scenarios

scenarios("../features/home_seniority.feature")
