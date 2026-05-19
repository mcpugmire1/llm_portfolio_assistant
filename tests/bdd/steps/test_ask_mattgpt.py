"""
BDD Step Definitions for Ask MattGPT — Nonsense rejection banner + chip sets.

Wired scenarios: NONE — Red-A state intentionally.

All 10 scenarios in ask_mattgpt.feature are auto-bound via
pytest_bdd.scenarios() so pytest discovers them. They will report as
undefined-step errors until step definitions land under the MATTGPT-071
implementation gate (separate commit).

This file establishes the Red-A proof for the MATTGPT-071 BDD work:
scenarios discovered + all undefined-step. See MATTGPT-071 in BACKLOG.md
for the design rationale and the implementation plan.

Run with: pytest tests/bdd/steps/test_ask_mattgpt.py -v
"""

from pytest_bdd import scenarios

scenarios("../features/ask_mattgpt.feature")
