"""
BDD Step Definitions for About Matt — Content polish bundle (MATTGPT-068).

Red (scenarios) gate state: scenarios are bound via the scenarios() loader
below, but NO step definitions are implemented yet. Running this file should
discover all 7 scenarios and report all 7 in undefined-step state
(StepDefinitionNotFoundError). That is the expected pass criterion for the
Red (scenarios) commit per CLAUDE.md Testing Protocol.

Step definitions will land in the next commit (Red, step defs gate), at
which point the scenarios will run end-to-end and fail with assertion
errors against the unchanged About Matt page.

Run with: pytest tests/bdd/steps/test_about_matt.py -v
(once step defs land, requires `streamlit run app.py` on localhost:8501)
"""

from pytest_bdd import scenarios

# Auto-bind all 7 scenarios from the .feature file
scenarios("../features/about_matt.feature")
