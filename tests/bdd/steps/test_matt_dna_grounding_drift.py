"""
BDD step definitions for matt_dna_grounding_drift.feature (MATTGPT-207).
"""

import sys
from unittest.mock import MagicMock

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

from pytest_bdd import scenarios

scenarios("../features/matt_dna_grounding_drift.feature")
