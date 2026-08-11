"""
BDD step definitions for fatal_fallback_handler.feature.

Tests that rag_answer's fatal handler (except Exception at line 1751) marks
the response degraded=True and logs the exception unconditionally via the
module logger, regardless of the DEBUG flag.
"""

import sys
from unittest.mock import MagicMock

from pytest_bdd import scenarios

# Mock streamlit before any backend_service imports at collection time.
if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/fatal_fallback_handler.feature")
