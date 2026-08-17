"""
BDD step definitions for cluster_promotion_kw.feature (MATTGPT-074).

Tests that entity cluster promotion is suppressed when kw scores are
dispersed across the entity pool (signaling a specific query), and
fires when kw is uniform (signaling a broad entity query).
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

scenarios("../features/cluster_promotion_kw.feature")
