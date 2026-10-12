"""
BDD Step Definitions for Ask Agy's streamed answer (MATTGPT-275 step 1).

Binds the 3 scenarios in tests/bdd/features/ask_streamed_answer.feature.
Step definitions are not written yet (Red, scenarios commit).

Run with: pytest tests/bdd/steps/test_ask_streamed_answer.py -v
(requires `streamlit run app.py` running on localhost:8501)
"""

from pytest_bdd import scenarios

scenarios("../features/ask_streamed_answer.feature")
