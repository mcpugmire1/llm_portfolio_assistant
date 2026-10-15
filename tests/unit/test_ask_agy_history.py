"""MATTGPT-273 Issue 2 Red: Ask Agy follow-ups carry conversation history.

The last two exchanges (four messages) of st.session_state["ask_transcript"]
reach the Agy gpt-4o call as prior user/assistant messages, between the
system message and the current user message. Retrieval is unchanged.

Class H (history builder): _build_history_messages() turns transcript
  entries into chat messages. Transcript entries use both "role" and
  "Role" keys (utils.push_user_turn vs push_conversational_answer), banner
  entries carry no answer text, and the current question is already the
  last transcript entry when send_to_backend() runs.
Class W (wiring): send_to_backend() reads ask_transcript and passes the
  built history to agy_answer() (MATTGPT-275; was rag_answer()).
"""

import logging
from unittest.mock import patch

from ui.pages.ask_mattgpt import backend_service as bs

logging.getLogger("streamlit").setLevel(logging.ERROR)

_FOLLOW_UP = "How big was the team?"


# ---------------------------------------------------------------------------
# Class H: transcript -> history messages
# ---------------------------------------------------------------------------


class TestBuildHistoryMessages:
    def test_reads_lowercase_and_capitalized_role_keys(self):
        transcript = [
            {"role": "user", "text": "q1"},
            {"type": "conversational", "Role": "assistant", "text": "a1"},
            {"role": "user", "text": "current question"},
        ]
        assert bs._build_history_messages(transcript) == [
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": "a1"},
        ]

    def test_drops_the_current_question(self):
        transcript = [
            {"role": "user", "text": "q1"},
            {"role": "assistant", "text": "a1"},
            {"role": "user", "text": "current question"},
        ]
        messages = bs._build_history_messages(transcript)
        assert {"role": "user", "content": "current question"} not in messages

    def test_skips_banner_entries(self):
        transcript = [
            {"role": "user", "text": "q1"},
            {
                "type": "banner",
                "Role": "assistant",
                "reason": "rule:nonsense",
                "query": "q1",
                "overlap": None,
            },
            {"role": "user", "text": "current question"},
        ]
        assert bs._build_history_messages(transcript) == [
            {"role": "user", "content": "q1"},
        ]

    def test_keeps_only_the_last_two_exchanges(self):
        transcript = []
        for i in range(1, 4):
            transcript.append({"role": "user", "text": f"q{i}"})
            transcript.append({"role": "assistant", "text": f"a{i}"})
        transcript.append({"role": "user", "text": "current question"})
        assert bs._build_history_messages(transcript) == [
            {"role": "user", "content": "q2"},
            {"role": "assistant", "content": "a2"},
            {"role": "user", "content": "q3"},
            {"role": "assistant", "content": "a3"},
        ]

    def test_first_turn_has_no_history(self):
        transcript = [{"role": "user", "text": "current question"}]
        assert bs._build_history_messages(transcript) == []

    def test_empty_transcript_has_no_history(self):
        assert bs._build_history_messages([]) == []


# ---------------------------------------------------------------------------
# Class W: send_to_backend passes the transcript's history to agy_answer
# ---------------------------------------------------------------------------


class TestSendToBackendHistory:
    def test_passes_transcript_history(self, sample_stories, mock_streamlit):
        mock_streamlit["ask_transcript"] = [
            {"role": "user", "text": "q1"},
            {"type": "conversational", "Role": "assistant", "text": "a1"},
            {"role": "user", "text": _FOLLOW_UP},
        ]
        with patch.object(bs, "agy_answer") as mock_agy_answer:
            mock_agy_answer.return_value = {"answer_md": "ok", "sources": []}
            bs.send_to_backend(
                prompt=_FOLLOW_UP, filters={}, ctx=None, stories=sample_stories
            )
        mock_agy_answer.assert_called_once_with(
            _FOLLOW_UP,
            sample_stories,
            history=[
                {"role": "user", "content": "q1"},
                {"role": "assistant", "content": "a1"},
            ],
            on_delta=None,
        )
