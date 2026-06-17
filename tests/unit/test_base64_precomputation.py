"""
Unit tests: verify pre-computed HTML/CSS module-level constants embed base64 image data.

Red phase: all 8 tests fail with AttributeError — the module-level constants don't exist yet.
  Strings are computed at call time via .replace() or f-string interpolation inside render
  functions. No module-level constant captures the final pre-computed HTML at import time.

Green phase: after refactoring to module-level pre-computation, all 8 constants exist and
  contain inline base64 data URIs (data:image/webp;base64,...) — no CDN fetches at render time.
"""

B64_MARKER = "data:image/webp;base64"


def test_global_styles_no_cdn():
    """global_styles._CSS must be pre-computed at module level with base64 Chase sprites."""
    from ui.styles import global_styles

    assert B64_MARKER in global_styles._CSS


def test_hero_no_cdn():
    """hero._HERO_HTML must be pre-computed at module level with base64 hero image."""
    from ui.components import hero

    assert B64_MARKER in hero._HERO_HTML


def test_why_agy_dialog_no_cdn():
    """why_agy_dialog._BODY_HTML must be pre-computed at module level with base64 illustration."""
    from ui.components import why_agy_dialog

    assert B64_MARKER in why_agy_dialog._BODY_HTML


def test_about_matt_no_cdn():
    """about_matt._ABOUT_HTML must be pre-computed at module level with base64 avatar."""
    from ui.pages import about_matt

    assert B64_MARKER in about_matt._ABOUT_HTML


def test_role_match_no_cdn():
    """role_match._HEADER_HTML must be pre-computed at module level with base64 avatar."""
    from ui.pages import role_match

    assert B64_MARKER in role_match._HEADER_HTML


def test_loading_animation_no_cdn():
    """styles._LOADING_ANIMATION_CSS must be pre-computed at module level with base64 sprites."""
    from ui.pages.ask_mattgpt import styles

    assert B64_MARKER in styles._LOADING_ANIMATION_CSS
