"""
BDD step bindings for the wireframe-locked navigation label rename (MATTGPT-100).

Red (scenarios) commit: the three scenarios are bound via the scenarios() loader
with NO step definitions yet, so every step resolves to undefined-step state
(StepDefinitionNotFoundError). Step definitions land in the Red (step defs)
commit, and the coordinated rename (display labels + session_state["active_tab"]
values) in the Green commit, per the CLAUDE.md testing protocol.
"""

from pytest_bdd import scenarios

scenarios("../features/nav_labels.feature")
