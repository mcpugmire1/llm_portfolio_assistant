"""Unit tests for Ask Agy button CSS rules (MATTGPT-033).

The landing button focus ring cannot be exercised via E2E Playwright: the
on_change callback navigates away on any text commit, making :focus-visible
unreachable without racing the navigation. CSS unit assertions are
deterministic and cover what E2E cannot.

Checks:
- :focus-visible rule is present with the purple focus color
- :focus-visible rule does not reference Streamlit's default red color
- transition is explicit (not `all`) so unintended properties don't animate
"""

import re

from ui.pages.ask_mattgpt.styles import get_landing_css

_CSS = get_landing_css()

PURPLE_FOCUS = "139, 92, 246"
RED_STREAMLIT = "255, 75, 75"


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


_COLLAPSED = _collapse(_CSS)


def test_landing_ask_focus_visible_has_purple_ring():
    """The :focus-visible rule must set a purple box-shadow on the landing button."""
    assert "focus-visible" in _COLLAPSED, (
        "No :focus-visible rule found for landing_ask button in get_landing_css(). "
        "MATTGPT-033 fix requires a purple focus ring override."
    )
    assert PURPLE_FOCUS in _COLLAPSED, (
        f"Purple color ({PURPLE_FOCUS}) not found in landing CSS. "
        "The :focus-visible box-shadow must use the purple focus color."
    )


def test_landing_ask_focus_visible_no_red_ring():
    """The CSS must not set Streamlit's default red focus color on the landing button."""
    assert RED_STREAMLIT not in _COLLAPSED, (
        f"Red Streamlit color ({RED_STREAMLIT}) found in landing CSS. "
        "Streamlit's default red :focus-visible ring must be suppressed."
    )


def test_landing_ask_transition_is_explicit():
    """transition must list explicit properties, not `all`, to prevent unintended animations."""
    # Use button[key="landing_ask"] as the anchor — it always leads the multi-selector
    # block and is not repeated in sub-rules (:hover, :disabled, etc.).
    match = re.search(r'button\[key="landing_ask"\][^{]*\{([^}]+)\}', _CSS, re.DOTALL)
    assert match, 'Could not locate button[key="landing_ask"] rule block'
    rule_block = match.group(1)
    assert "transition: all" not in rule_block, (
        "transition: all found in the landing_ask button rule — must use explicit "
        "properties (background-color, transform, box-shadow) to prevent unintended "
        "property animations on focus."
    )
