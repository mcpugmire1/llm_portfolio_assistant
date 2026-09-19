"""MATTGPT-245 phase one: render_thinking_indicator gains a mount kwarg.

Default `mount="overlay"` preserves today's HTML for the 5 unchanged
callers (Ask Agy conversation_view x3, Ask Agy landing_view, Explore
Stories). `mount="inline"` skips the .thinking-backdrop div and adds
.thinking-inline to the modal class list for the Role Match
results-column mount, where the CSS rule then overrides
position: fixed to static and drops the centering transform.

Rotating messages, get_thinking_message(), the keyframes, and the
ball are explicitly out of scope for phase one -- test 5 pins that
they are not touched by the mount branch.

Test 1 is a regression pin (passes on Red because it pins the
existing default). Tests 3, 4, 5 fail on Red because `mount=` is
not a valid kwarg today.
"""

from unittest.mock import patch


class TestOverlayDefaultUnchanged:
    """Regression pin. If Green changes what render_thinking_indicator()
    with no arguments emits, five other callers (Ask Agy conversation,
    Ask Agy landing, Explore Stories) lose their backdrop scrim
    silently."""

    def test_default_no_args_includes_thinking_backdrop_div(self):
        """Test 1. render_thinking_indicator() with no args writes HTML
        containing <div class="thinking-backdrop"></div>. The 5 existing
        callers depend on this default; Green must not change it."""
        from ui.components import thinking_indicator

        with (
            patch.object(
                thinking_indicator, "get_thinking_message", return_value="test-msg"
            ),
            patch.object(thinking_indicator.st, "markdown") as mock_md,
        ):
            thinking_indicator.render_thinking_indicator()

        assert mock_md.call_count == 1, (
            f"expected exactly one st.markdown call from "
            f"render_thinking_indicator(); got {mock_md.call_count}"
        )
        html = mock_md.call_args.args[0]
        assert '<div class="thinking-backdrop"></div>' in html, (
            f"default (no args) must emit the .thinking-backdrop div "
            f"-- 5 external callers depend on this. Got HTML:\n{html}"
        )


class TestInlineMount:
    """New behavior for the Role Match results-column mount. Drops
    the backdrop scrim (which was blocking clicks on everything under
    the viewport) and adds a class modifier the CSS uses to override
    position: fixed to static."""

    def test_inline_omits_thinking_backdrop(self):
        """Test 3. mount='inline' writes HTML that does NOT contain
        .thinking-backdrop. Load-bearing negative: the whole point of
        the inline mount is removing the scrim so nav, form controls,
        and other page elements remain interactive during the
        assessment."""
        from ui.components import thinking_indicator

        with (
            patch.object(
                thinking_indicator, "get_thinking_message", return_value="test-msg"
            ),
            patch.object(thinking_indicator.st, "markdown") as mock_md,
        ):
            thinking_indicator.render_thinking_indicator(mount="inline")

        html = mock_md.call_args.args[0]
        assert "thinking-backdrop" not in html, (
            f"mount='inline' must not emit any .thinking-backdrop "
            f"markup -- that's the scrim the inline mount exists to "
            f"remove. Got HTML:\n{html}"
        )

    def test_inline_modal_carries_thinking_inline_class(self):
        """Test 4. mount='inline' writes HTML where the modal div
        carries both 'thinking-modal' and 'thinking-inline' classes.
        The CSS rule targets .thinking-inline specifically to override
        position: fixed to static and drop the centering transform."""
        from ui.components import thinking_indicator

        with (
            patch.object(
                thinking_indicator, "get_thinking_message", return_value="test-msg"
            ),
            patch.object(thinking_indicator.st, "markdown") as mock_md,
        ):
            thinking_indicator.render_thinking_indicator(mount="inline")

        html = mock_md.call_args.args[0]
        assert (
            'class="thinking-modal thinking-inline"' in html
            or 'class="thinking-inline thinking-modal"' in html
        ), (
            f"mount='inline' must carry both 'thinking-modal' and "
            f"'thinking-inline' classes on the modal div. The CSS "
            f"rule targets .thinking-inline for the position override. "
            f"Got HTML:\n{html}"
        )

    def test_inline_still_invokes_get_thinking_message(self):
        """Test 5. mount='inline' still calls get_thinking_message()
        and includes the returned message in the output. Protects the
        'don't touch rotating messages' scope rule -- if a Green
        refactor drops the message call from the inline branch,
        this catches it."""
        from ui.components import thinking_indicator

        sentinel_msg = "SENTINEL_THINKING_MESSAGE_9f3b"
        with (
            patch.object(
                thinking_indicator, "get_thinking_message", return_value=sentinel_msg
            ),
            patch.object(thinking_indicator.st, "markdown") as mock_md,
        ):
            thinking_indicator.render_thinking_indicator(mount="inline")

        html = mock_md.call_args.args[0]
        assert sentinel_msg in html, (
            f"mount='inline' must include the rotating message from "
            f"get_thinking_message() in the output. Sentinel "
            f"{sentinel_msg!r} not found in HTML:\n{html}"
        )
