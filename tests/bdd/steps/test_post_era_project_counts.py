"""
BDD step bindings for the landing page + Home card project-count alignment
to the post-Era convention (MATTGPT-104).

Red (scenarios) commit: scenarios are bound via the scenarios() loader
with NO step definitions yet, so every step resolves to undefined-step
state (StepDefinitionNotFoundError). Step definitions land in the
Red (step defs) commit; the post-Era count source change to
banking_landing.py / cross_industry_landing.py / category_cards.py
lands in the Green commit, per the CLAUDE.md testing protocol.
"""

from pytest_bdd import scenarios

scenarios("../features/post_era_project_counts.feature")
