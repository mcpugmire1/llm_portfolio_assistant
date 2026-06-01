"""
BDD step bindings for the Explore Stories default-state change (MATTGPT-098).

Red (scenarios) commit: the three scenarios are bound via the scenarios() loader
with NO step definitions yet, so every step resolves to undefined-step state
(StepDefinitionNotFoundError). Step definitions land in the Red (step defs)
commit; the explore_stories.py default filter + sort change lands in the Green
commit, per the CLAUDE.md testing protocol.

Assertions target the visible story rows (Table view's default rendering) —
Category column, Era column, and Start_Date ordering across consecutive rows.
DOM-observable only; no st.session_state reads.
"""

from pytest_bdd import scenarios

scenarios("../features/explore_stories_default_state.feature")
