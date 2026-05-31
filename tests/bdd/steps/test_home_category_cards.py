"""
BDD step bindings for the home category cards redesign (MATTGPT-107).

Red (scenarios) gate state: scenarios are discovered via the scenarios()
loader below. No step definitions exist yet — every scenario should
report StepDefinitionNotFoundError when this file is executed by
pytest-bdd. The Red (step defs) commit adds the @given/@when/@then
bindings; the Green commit lands the category_cards.py CSS + HTML
restructure.
"""

from pytest_bdd import scenarios

scenarios("../features/home_category_cards.feature")
