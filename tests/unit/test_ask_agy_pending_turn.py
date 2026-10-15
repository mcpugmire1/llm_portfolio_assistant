"""MATTGPT-275: the conversation view's exception path.

_answer_pending_turn() answers the pending question through send_to_backend().
If that call raises, the visitor gets ANSWER_ERROR_MESSAGE as Agy's turn: never
the exception text (the old chip path showed f"Error: {e}"), and the page
leaves the processing state and reruns, so the next question can be asked.

Streamlit is a MagicMock; st.rerun() raises, as the real one does, to end the
run.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from ui.pages.ask_mattgpt import conversation_view as cv

logging.getLogger("streamlit").setLevel(logging.ERROR)

_ERROR_MESSAGE = "Sorry, I couldn't generate an answer right now."
_EXCEPTION_TEXT = "ZZZ_SENTINEL upstream exploded"


class _Rerun(Exception):
    """Stands in for Streamlit's RerunException."""


def _answer_with_failing_backend():
    session = {
        "__processing_chip_injection__": {"query": "q", "step": "processing"},
        "ask_transcript": [],
    }
    mock_st = MagicMock()
    mock_st.session_state = session
    mock_st.rerun.side_effect = _Rerun
    push_assistant = MagicMock()
    push_answer = MagicMock()
    with (
        patch.object(cv, "st", mock_st),
        patch.object(
            cv, "send_to_backend", MagicMock(side_effect=RuntimeError(_EXCEPTION_TEXT))
        ),
        patch.object(cv, "render_thinking_indicator", MagicMock()),
        patch.object(cv, "_push_assistant_turn", push_assistant),
        patch.object(cv, "_push_conversational_answer", push_answer),
        pytest.raises(_Rerun),
    ):
        cv._answer_pending_turn("Tell me about his ledger work", None, [])
    return session, mock_st, push_assistant, push_answer


class TestBackendFailure:
    def test_the_visitor_gets_the_error_message_as_agys_turn(self):
        _, _, push_assistant, push_answer = _answer_with_failing_backend()
        push_assistant.assert_called_once_with(_ERROR_MESSAGE)
        push_answer.assert_not_called()

    def test_the_exception_text_never_reaches_the_page(self):
        _, mock_st, push_assistant, _ = _answer_with_failing_backend()
        shown = [str(c) for c in push_assistant.call_args_list]
        shown += [str(c) for c in mock_st.markdown.call_args_list]
        shown += [str(c) for c in mock_st.error.call_args_list]
        assert not any(_EXCEPTION_TEXT in text for text in shown)

    def test_the_turn_leaves_processing_and_reruns(self):
        session, mock_st, _, _ = _answer_with_failing_backend()
        assert session["__processing_chip_injection__"] is False
        mock_st.rerun.assert_called_once()
