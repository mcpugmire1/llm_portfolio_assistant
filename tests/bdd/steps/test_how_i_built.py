"""
BDD step bindings for the How I Built MattGPT deep-link surface (MATTGPT-102).

Red (scenarios) commit: scenarios are bound via the scenarios() loader with
NO step definitions yet, so every step resolves to undefined-step state
(StepDefinitionNotFoundError). Step definitions land in the Red (step defs)
commit; the new ui/pages/how_i_built.py + the relocation from about_matt.py
+ the ?route=how-i-built query param handler in app.py land in the Green
commit, per the CLAUDE.md testing protocol.
"""

from pytest_bdd import scenarios

scenarios("../features/how_i_built.feature")
