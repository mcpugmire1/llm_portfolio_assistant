"""
BDD step definitions for nonsense_filter_behavior.feature (MATTGPT-165 Cycle C).

Verifies is_nonsense returns None on the two target queries that Cycle C's
nonsense_filters.jsonl edits are designed to unblock (credit card portal work,
SWIFT payment rails), and returns the expected blocking category on the two
regression queries the narrower patterns must continue to catch (Taylor Swift
by full name, credit card number as PII).
"""

import sys
from unittest.mock import MagicMock

from pytest_bdd import scenarios

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/nonsense_filter_behavior.feature")
