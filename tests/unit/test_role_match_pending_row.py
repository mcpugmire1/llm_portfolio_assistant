"""MATTGPT-245 phase two: _render_pending_row_html helper.

Renders the pending state for one requirement slot. Each st.empty()
seeded with this HTML shows a hollow purple ring (same footprint as
the resolved status badge) plus the requirement text. When the LLM
completes for that requirement, the on_row callback overwrites the
slot with the finished-row HTML.

The pending state must be visually distinct from the unassessed
terminal state (⋯ badge). A visitor seeing a hollow ring reads
"in progress"; a visitor seeing ⋯ reads "failed." Confusing the
two would misrepresent a still-running call as already completed.

Tests fail on Red with NotImplementedError from the stub.
"""

import html as html_module


class TestPendingRowContents:
    """Positive checks: the pending-row HTML carries what it needs to
    render (escaped requirement text + a class marker for the hollow
    ring)."""

    def test_pending_row_contains_html_escaped_requirement_text(self):
        """Test 7a. The requirement text is html.escape'd (ampersand
        becomes &amp;, etc.). Same convention as
        _render_location_block_html and _build_export_html use for
        text emitted into HTML."""
        from ui.pages import role_match

        requirement_text = "Senior Engineer & Manager"
        pending_html = role_match._render_pending_row_html(requirement_text)

        expected_escaped = html_module.escape(requirement_text)
        assert expected_escaped in pending_html, (
            f"expected html.escape'd requirement text {expected_escaped!r} "
            f"in pending-row HTML; got:\n{pending_html}"
        )

    def test_pending_row_contains_pending_ring_marker(self):
        """Test 7b. The pending-row HTML includes the hollow-ring
        marker class (role-match-pending-ring). The CSS rule targets
        this class to draw the 22px, 2px --accent-purple border,
        transparent-fill circle in the same footprint as the resolved
        status badges."""
        from ui.pages import role_match

        pending_html = role_match._render_pending_row_html("any requirement")

        assert "role-match-pending-ring" in pending_html, (
            f"expected 'role-match-pending-ring' class marker in "
            f"pending-row HTML (the CSS hook for the hollow ring); "
            f"got:\n{pending_html}"
        )


class TestPendingRowNegatives:
    """Load-bearing negatives: the pending state must not accidentally
    render the finished shape (badge, evidence chips, gap explanation)
    or the unassessed terminal state (⋯ glyph)."""

    def test_pending_row_omits_status_badge_class(self):
        """Test 8a. The pending state must not emit the
        .role-match-status-badge class. That class is reserved for
        resolved rows (strong / partial / gap / unassessed). If the
        pending row carried it, the CSS would try to style the
        hollow ring as a badge and the visual affordance would
        collapse."""
        from ui.pages import role_match

        pending_html = role_match._render_pending_row_html("any requirement")

        assert "role-match-status-badge" not in pending_html, (
            f"pending-row HTML must not emit .role-match-status-badge "
            f"(that's the resolved-row class). Got:\n{pending_html}"
        )

    def test_pending_row_omits_unassessed_ellipsis_glyph(self):
        """Test 8b. The pending state must not contain the ⋯ glyph
        (U+22EF, _STATUS_ICON['unassessed']). Unassessed is a real
        terminal state -- Mode 1 assess-caught, Mode 2
        retrieval-returned-None -- with its own badge. A visitor
        seeing ⋯ reads 'failed'; a still-running call must not be
        mistakable for that. This test is the tripwire between the
        two visual states."""
        from ui.pages import role_match

        pending_html = role_match._render_pending_row_html("any requirement")

        assert "⋯" not in pending_html, (
            f"pending-row HTML must not contain the ⋯ glyph (U+22EF) "
            f"-- that's the unassessed terminal-state badge. A pending "
            f"row rendered with ⋯ reads to the visitor as 'failed' "
            f"while the call is still running. Got:\n{pending_html}"
        )
