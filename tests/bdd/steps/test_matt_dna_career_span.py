"""
BDD step definitions for matt_dna_career_span.feature (MATTGPT-161).

Verifies career-span derivation from corpus dates and enforces that the
resulting values are NOT rendered into MATT_DNA prose. The derived constants
remain available for consumers that need the math (Role Match assessor
reasoning about JD tenure requirements).
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

scenarios("../features/matt_dna_career_span.feature")
