"""
BDD step bindings for the navbar desktop brand-left + space-between layout
(MATTGPT-106).

Red (scenarios) gate state: scenarios are discovered via the scenarios()
loader below. No step definitions exist yet — every scenario should report
StepDefinitionNotFoundError when this file is executed by pytest-bdd.
The Red (step defs) commit adds the @given/@when/@then bindings; the
Green commit lands the navbar.py CSS + brand-render changes.
"""

from pytest_bdd import scenarios

scenarios("../features/navbar_brand_layout.feature")
