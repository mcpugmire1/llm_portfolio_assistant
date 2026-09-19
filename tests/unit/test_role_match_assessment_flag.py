"""MATTGPT-245 phase one: assessment-in-progress session flag for the
Role Match Clear + Submit guard.

The in-flow indicator removes the backdrop scrim that was blocking
clicks during the ~20s assessment. Two controls need a disabled=
guard to preserve the behavior the scrim provided by accident:

  Submit -- second assessment over the first is never intended
  Clear  -- destroys the pasted JD and the partial results with it

Nav stays live (leaving mid-assessment is a legitimate user choice).
Report/Export/Helpful already render only on a completed result.

Wiring:

  _handle_submit_click (callback, fires BEFORE rerun):
      when the gate passes -> set role_match_assessment_in_progress = True
      when the gate rejects -> do NOT set the flag

  Render code (runs on the same rerun, before the blocking LLM call):
      _consume_assessment_in_progress_flag() -- reads AND clears
      the flag in one step (session_state.pop, not .get). Return value
      wires into disabled= on Clear and Submit.

Test 8 is the load-bearing one: if the helper reads with .get() instead
of .pop(), the flag persists across reruns and Clear + Submit stay
disabled forever after the first assessment.

Test 6 fails on Red: callback doesn't set the flag yet.
Test 7 is a regression pin: callback doesn't touch the flag on Red,
so the flag is absent, and .get(..., False) returns False -> passes.
Test 8 fails on Red: _consume_assessment_in_progress_flag stub
raises NotImplementedError.
"""

from unittest.mock import patch

# 30-word JD with a shape term ("role"). Passes both _MIN_JD_WORDS (30)
# and _looks_like_jd (matches "role" on a word boundary).
_VALID_JD_30_WORDS = (
    "We are hiring a Senior Python engineer to build backend services. "
    "This role requires strong experience with distributed systems, API "
    "design, testing, and production operations. Remote-friendly with "
    "quarterly onsites required."
)

# 3-word non-JD paste. Fails on both word count and shape check.
_REJECTED_INPUT = "Chocolate cake recipe"


class TestFlagSetOnGatePass:
    """Callback path when the JD is valid. Flag must be set so the
    render pass that follows sees True and renders Clear + Submit
    with disabled=True."""

    def test_flag_set_when_gate_passes(self):
        """Test 6. _handle_submit_click sets
        role_match_assessment_in_progress = True when the JD passes
        both _MIN_JD_WORDS and _looks_like_jd."""
        from ui.pages import role_match

        with patch.object(role_match, "st") as mock_st:
            mock_st.session_state = {"role_match_jd_input": _VALID_JD_30_WORDS}
            role_match._handle_submit_click()

        assert mock_st.session_state.get("role_match_assessment_in_progress") is True, (
            f"expected role_match_assessment_in_progress=True after a "
            f"gate-passing callback; got "
            f"{mock_st.session_state.get('role_match_assessment_in_progress')!r}. "
            f"Full session_state: {dict(mock_st.session_state)!r}"
        )


class TestFlagNotSetOnGateReject:
    """Callback path when the gate rejects the input. Flag must not
    be set -- otherwise the next render pass would render Clear +
    Submit disabled with no assessment running, and the visitor would
    be locked out of clearing their rejected input."""

    def test_flag_not_set_when_gate_rejects_short_non_jd(self):
        """Test 7. _handle_submit_click does NOT set the flag when the
        gate rejects the input. Load-bearing: a rejected visitor must
        still be able to click Clear to try again."""
        from ui.pages import role_match

        with (
            patch.object(role_match, "st") as mock_st,
            patch.object(role_match, "is_bot", return_value=False),
            patch.object(role_match, "log_role_match_gate_rejection"),
        ):
            mock_st.session_state = {"role_match_jd_input": _REJECTED_INPUT}
            role_match._handle_submit_click()

        assert (
            mock_st.session_state.get("role_match_assessment_in_progress", False)
            is False
        ), (
            f"expected role_match_assessment_in_progress to be absent "
            f"or False after a gate rejection; got "
            f"{mock_st.session_state.get('role_match_assessment_in_progress')!r}. "
            f"Full session_state: {dict(mock_st.session_state)!r}"
        )
        assert mock_st.session_state.get("role_match_gate_error") is not None, (
            f"sanity check: the gate should have rejected _REJECTED_INPUT "
            f"and set role_match_gate_error; got "
            f"{mock_st.session_state.get('role_match_gate_error')!r}. If "
            f"this fails, the test fixture no longer triggers the gate "
            f"and test 7 no longer proves what it claims."
        )


class TestFlagClearedOnConsume:
    """Load-bearing: the helper must POP the flag, not GET it. If the
    flag persists across reruns, Clear + Submit stay disabled forever
    after the first assessment -- the worst failure mode of this
    feature."""

    def test_consume_returns_true_first_then_false(self):
        """Test 8. _consume_assessment_in_progress_flag must clear the
        flag on read. First call returns True (the render pass that
        runs the LLM); second call returns False (any subsequent
        rerun). If both return True, production uses .get() instead
        of .pop() and the guard never releases."""
        from ui.pages import role_match

        with patch.object(role_match, "st") as mock_st:
            mock_st.session_state = {"role_match_assessment_in_progress": True}
            first = role_match._consume_assessment_in_progress_flag()
            second = role_match._consume_assessment_in_progress_flag()

        assert first is True, (
            f"first read should return True (flag was set by callback); "
            f"got {first!r}"
        )
        assert second is False, (
            f"second read should return False -- first read must clear "
            f"the flag. Got {second!r}. If this is True, production "
            f"uses .get() instead of .pop() and Clear + Submit stay "
            f"disabled forever after the first assessment."
        )
