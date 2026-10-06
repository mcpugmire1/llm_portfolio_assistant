"""MATTGPT-273 Issue 2 Red: Ask Agy follow-ups carry conversation history.

The last two exchanges (four messages) of st.session_state["ask_transcript"]
reach the Agy gpt-4o call as prior user/assistant messages, between the
system message and the current user message. Retrieval is unchanged.

Class H (history builder): _build_history_messages() turns transcript
  entries into chat messages. Transcript entries use both "role" and
  "Role" keys (utils.push_user_turn vs push_conversational_answer), banner
  entries carry no answer text, and the current question is already the
  last transcript entry when send_to_backend() runs.
Class P (captured prompt): rag_answer(..., history=...) sends the history
  as messages, in order, between the system message and the user message.
Class W (wiring): send_to_backend() reads ask_transcript and passes the
  built history to agy_answer() (MATTGPT-275; was rag_answer()).

The captured-prompt fixture identifies the Agy call by the MATT_DNA persona
anchor, as in test_ask_agy_prompt_composition.py.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from utils.corpus_loader import load_stories

logging.getLogger("streamlit").setLevel(logging.ERROR)

_AGY_ANCHOR = "**Leadership Philosophy:**"
_FOLLOW_UP = "How big was the team?"

_HISTORY = [
    {"role": "user", "content": "Tell me about Matt's JP Morgan payments work"},
    {"role": "assistant", "content": "ZZZ_SENTINEL_ANSWER_ONE"},
    {"role": "user", "content": "What did the platform do?"},
    {"role": "assistant", "content": "ZZZ_SENTINEL_ANSWER_TWO"},
]


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
# Class P: history reaches the Agy call as messages
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real_stories():
    return load_stories("echo_star_stories_nlp.jsonl")


def _capture_agy_messages(real_stories, history):
    """Run rag_answer with semantic_search mocked and openai.OpenAI patched;
    return the full messages list of the one call whose system message
    carries the Agy persona anchor."""
    fake_completion = MagicMock()
    fake_completion.choices = [MagicMock()]
    fake_completion.choices[0].message.content = "captured-history-test-response"
    fake_openai = MagicMock()
    fake_openai.chat.completions.create.return_value = fake_completion

    def _fake_search(query, filters, **kwargs):
        return {
            "results": [real_stories[0]],
            "confidence": "high",
            "top_score": 0.85,
            "profile_facts": "",
        }

    mock_st = MagicMock()
    mock_st.session_state = {}
    bs.sync_portfolio_metadata(real_stories)

    with (
        patch("streamlit.session_state", mock_st.session_state),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "DEBUG", False),
        patch.object(bs, "semantic_search", side_effect=_fake_search),
        patch("openai.OpenAI", return_value=fake_openai),
    ):
        bs.rag_answer(_FOLLOW_UP, {}, real_stories, history=history)

    agy_calls = [
        call.kwargs.get("messages", [])
        for call in fake_openai.chat.completions.create.call_args_list
        if any(
            m.get("role") == "system" and _AGY_ANCHOR in m.get("content", "")
            for m in call.kwargs.get("messages", [])
        )
    ]
    if len(agy_calls) != 1:
        pytest.fail(
            f"Agy response call not uniquely captured: {len(agy_calls)} calls "
            f"carried anchor {_AGY_ANCHOR!r}. Not a Class P failure."
        )
    return agy_calls[0]


class TestHistoryInAgyMessages:
    def test_prior_turns_sit_between_system_and_user(self, real_stories):
        messages = _capture_agy_messages(real_stories, _HISTORY)
        assert [m["role"] for m in messages] == [
            "system",
            "user",
            "assistant",
            "user",
            "assistant",
            "user",
        ]
        assert messages[1:5] == _HISTORY

    def test_current_question_is_the_last_message(self, real_stories):
        messages = _capture_agy_messages(real_stories, _HISTORY)
        assert messages[-1]["role"] == "user"
        assert f"User Question: {_FOLLOW_UP}" in messages[-1]["content"]

    def test_no_history_sends_system_and_user_only(self, real_stories):
        messages = _capture_agy_messages(real_stories, None)
        assert [m["role"] for m in messages] == ["system", "user"]


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
        )
