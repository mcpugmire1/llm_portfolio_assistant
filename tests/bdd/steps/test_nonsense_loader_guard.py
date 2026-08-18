"""
BDD step definitions for nonsense_loader_guard.feature (MATTGPT-165 loader hardening).

Tests that _load_nonsense_rules raises ValueError at load time on:
- duplicate (category, pattern) pairs
- non-dict rules (bare strings, lists)
- dicts missing required category or pattern fields
- dicts with uncompilable regex patterns

And that app.py invokes preload_nonsense_rules unconditionally at module top
level so guard failures fire at startup instead of first-query time.
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

scenarios("../features/nonsense_loader_guard.feature")
