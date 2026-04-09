"""
Regression test for the Role Match chip expansion toggle.

The chip expansion toggle uses a `st.button(key=f"evidence_btn_{composite_key}")`
pattern with a session-state-based same-key-closes / different-key-switches
toggle. This was the locked-in fix for the April 2026 chip expansion bug
(see CLAUDE.md "Interactive Click Handling — STOP, Read This First").

When the visual treatment of the chip is restyled (label format, CSS, etc.)
the underlying button key pattern and toggle logic MUST remain untouched.
This test asserts the contract by source-inspecting role_match.py.
"""

import re
from pathlib import Path

ROLE_MATCH_PY = Path(__file__).resolve().parents[2] / "ui" / "pages" / "role_match.py"


def _read_source() -> str:
    return ROLE_MATCH_PY.read_text()


class TestChipToggleContract:
    """Source-inspection regression checks for the locked toggle pattern."""

    def test_button_key_pattern_unchanged(self):
        """The st.button key MUST be `evidence_btn_{composite_key}`."""
        src = _read_source()
        assert 'key=f"evidence_btn_{composite_key}"' in src, (
            "The button key pattern `evidence_btn_{composite_key}` is the "
            "locked fix for the April 2026 chip expansion bug. Do not "
            "rename or change it. See CLAUDE.md."
        )

    def test_composite_key_still_built_from_req_and_ev_idx(self):
        """composite_key is built from req_idx and ev_idx, not anything else."""
        src = _read_source()
        assert 'composite_key = f"{req_idx}_{ev_idx}"' in src, (
            "composite_key must remain `f\"{req_idx}_{ev_idx}\"` so the "
            "active-evidence session-state value can be parsed back into "
            "a req_idx for inline detail rendering."
        )

    def test_session_state_toggle_logic_intact(self):
        """Same-key closes, different-key switches — both branches present."""
        src = _read_source()
        # Whitespace-tolerant: ruff may reflow long lines across multiple
        # lines when the toggle block is deeply indented (e.g., when
        # nested inside an evidence-row st.container).
        normalized = re.sub(r"\s+", " ", src)
        # Open / switch branch
        assert 'st.session_state["role_match_active_evidence"]' in normalized, (
            "The toggle handler must set role_match_active_evidence on the "
            "open / switch branch."
        )
        # Close branch — match `pop(... "role_match_active_evidence", None)`
        # tolerant to internal whitespace.
        assert re.search(
            r'st\.session_state\.pop\(\s*"role_match_active_evidence",\s*None\s*\)',
            src,
        ), (
            "The toggle handler must pop role_match_active_evidence on the "
            "same-chip-clicked-twice (close) branch."
        )
        # Same-key comparison guard
        assert (
            'st.session_state.get("role_match_active_evidence")' in normalized
            and "== composite_key" in normalized
        ), (
            "The toggle handler must compare the stored active key against "
            "composite_key to decide between close and switch."
        )

    def test_st_rerun_is_called_after_toggle(self):
        """The toggle handler must end with st.rerun() so the UI updates."""
        src = _read_source()
        # Find the LAST `st.session_state.pop(... role_match_active_evidence ...)`
        # — the panel-level reset is on a single line earlier, the toggle
        # handler's pop is the deeper-indented multi-line one. Use a
        # whitespace-tolerant regex so reflowed code still matches.
        matches = list(
            re.finditer(
                r'st\.session_state\.pop\(\s*"role_match_active_evidence",\s*None\s*\)',
                src,
            )
        )
        assert matches, "Toggle close branch missing"
        # The toggle handler (in _render_requirement_card) is defined
        # BEFORE _render_results_panel in the file, so it's matches[0].
        # The panel-level reset is the second match.
        first = matches[0]
        tail = src[first.start() : first.start() + 800]
        assert "st.rerun()" in tail, (
            "st.rerun() must be called after the toggle handler so the "
            "expanded story detail re-renders on the next pass."
        )

    def test_active_key_drives_inline_detail_rendering(self):
        """The inline render_story_detail call is gated on active_evidence_key."""
        src = _read_source()
        assert (
            "render_story_detail(" in src
        ), "render_story_detail must still be called for inline expansion."
        # active_evidence_key.split("_")[0] is how we resolve which req
        # owns the active chip — this is the locked parsing pattern.
        assert 'active_evidence_key.split("_")[0]' in src, (
            "Inline detail placement depends on parsing req_idx out of "
            "the composite_key. Do not change this without also changing "
            "the composite_key format."
        )
