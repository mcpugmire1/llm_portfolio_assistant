"""Unit tests for global_styles.py.

Floor-level guard: asserts the MATTGPT-018 stale-hide rule is present in the
CSS block as a contiguous selector+declaration unit. Proves nothing about DOM
behavior (that is the BDD suite's job) but catches accidental deletion or
mutation of the rule during refactors.

Note: imports _CSS directly, the only available handle. If _CSS is ever renamed
or wrapped in a function, this test breaks on import; update the import path
rather than treating the import error as a rule-deletion failure.
"""

import re

from ui.styles.global_styles import _CSS


def _collapse(text):
    """Collapse all whitespace runs to a single space for whitespace-tolerant matching."""
    return re.sub(r"\s+", " ", text).strip()


# Selectors and declaration as a unit, whitespace-free canonical form.
# Asserting both selectors together with the hiding declaration means a body
# change to visibility: visible (or any no-op value) fails this test, while
# a selector-only assertion would stay green through such a mutation.
_STALE_HIDE_RULE = _collapse(
    '[data-testid="stElementContainer"][data-stale="true"]:has(.main-intro-section),'
    ' [data-testid="stElementContainer"][data-stale="true"]:has(.ask-header-landing)'
    " { visibility: hidden !important; }"
)


def test_stale_hero_hide_rule_present():
    """The stale-hide rule for .main-intro-section and .ask-header-landing must
    be present in the injected CSS with the correct visibility: hidden declaration.
    Selector presence alone is not sufficient: a body change to visibility: visible
    or any other value would break the blep fix while leaving selector-only
    assertions green.
    """
    assert _STALE_HIDE_RULE in _collapse(_CSS), (
        "MATTGPT-018 stale-hide rule missing or mutated in global_styles._CSS. "
        "Expected both selectors with 'visibility: hidden !important' as a unit. "
        "The cross-navigation avatar blep fix may have been accidentally removed "
        "or the declaration body changed to a no-op value."
    )
