"""
BDD step definitions for cluster_promotion_kw.feature (MATTGPT-074).

Tests that the entity cluster promotion gate computes content-kw by
stripping entity tokens (canonical + alias key) from the retrieval query,
then checking uniformity across the entity pool.
"""

import sys

from pytest_bdd import scenarios

if "streamlit" not in sys.modules:
    from unittest.mock import MagicMock

    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/cluster_promotion_kw.feature")
