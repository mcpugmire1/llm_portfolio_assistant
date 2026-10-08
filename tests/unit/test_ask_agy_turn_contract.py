"""MATTGPT-275 Red: the Ask Agy turn contract.

Every conversational turn performs contextual retrieval: the answering model
writes the search query from the current turn plus the conversation, evidence
is retrieved, and the answer is grounded in it. Not "decide whether to
search": the first model call of every turn is a forced search.

The four unit assertions:
  1. Every turn's first model call is a forced search (tool_choice
     "required"), follow-ups included.
  2. The search runs on the query the model wrote, not the visitor's words.
  3. That query is generated with the conversation in view: the forced first
     call carries the history and the current question as-is.
  4. Evidence comes before the answer: semantic_search() runs before the
     model call that writes the answer.
Plus the voice placement: the per-answer voice rules sit in the system prompt
with Matt's opener lines as examples, never as exact text to copy. The full
system-prompt contract is in test_ask_agy_tool_system_prompt.py.

The behavioral half is evidenced by the lever 2 acceptance run
(docs/evidence/MATTGPT-275/lever2_20261007_211535/, f7c1de2): searched
125/125, follow-ups 56/65, topic switch 15/15, 10.3 and PMP 5/5. These tests
pin the shape that run measured. Fixtures are the invented ZZZ_SENTINEL
stories from test_ask_agy_tool_answer.py.
"""

import json
from unittest.mock import MagicMock, patch

from tests.unit.test_ask_agy_tool_answer import (
    _DNA_SENTINEL,
    _STORIES,
    _STORY_A,
    _response,
    _search_result,
)
from ui.pages.ask_mattgpt import backend_service as bs

_HISTORY = [
    {"role": "user", "content": "Tell me about his payments work."},
    {"role": "assistant", "content": "ZZZ_SENTINEL answer about the ledger rebuild."},
]
_FOLLOW_UP = "What went wrong?"


class _LoggingOpenAI:
    """Scripted chat model that logs each request into a shared event list."""

    def __init__(self, script, events):
        self.script = list(script)
        self.events = events
        self.requests = []
        self.chat = MagicMock()
        self.chat.completions.create = self._create

    def _create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs, default=str)))
        self.events.append(("model", len(self.requests) - 1))
        if len(self.script) > 1:
            return self.script.pop(0)
        return self.script[0]


def _turn(question, history, script):
    events = []
    fake = _LoggingOpenAI(script, events)
    search = MagicMock(
        side_effect=lambda *a, **k: events.append(("search", a[0]))
        or _search_result([_STORY_A])
    )
    session = {}
    mock_st = MagicMock()
    mock_st.session_state = session
    with (
        patch("openai.OpenAI", return_value=fake),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "semantic_search", search),
        patch.object(
            bs,
            "is_portfolio_query_semantic",
            return_value=(True, 0.6, "zzz-intent", "behavioral"),
        ),
        patch.object(bs, "is_nonsense", return_value=None),
        patch.object(bs, "log_query", MagicMock()),
        patch.object(bs, "log_offdomain", MagicMock()),
        patch.object(bs, "MATT_DNA", _DNA_SENTINEL),
    ):
        result = bs.agy_answer(question, _STORIES, history=history)
    return result, fake, search, events


_SEARCH_THEN_ANSWER = [
    _response(tool_query="ZZZ ledger rebuild challenges"),
    _response("The ledger could not settle overnight."),
]


class TestEveryTurnRetrievesInContext:
    def test_first_turn_first_call_is_a_forced_search(self):
        _, fake, _, _ = _turn(
            "Tell me about his payments work.", [], _SEARCH_THEN_ANSWER
        )
        assert fake.requests[0].get("tool_choice") == "required"

    def test_follow_up_first_call_is_a_forced_search(self):
        _, fake, _, _ = _turn(_FOLLOW_UP, _HISTORY, _SEARCH_THEN_ANSWER)
        assert fake.requests[0].get("tool_choice") == "required"

    def test_search_runs_on_the_models_query_not_the_visitors_words(self):
        _, _, search, _ = _turn(_FOLLOW_UP, _HISTORY, _SEARCH_THEN_ANSWER)
        queries = [c.args[0] for c in search.call_args_list]
        assert queries == ["ZZZ ledger rebuild challenges"]
        assert _FOLLOW_UP not in queries

    def test_forced_call_carries_the_conversation_and_the_question_as_asked(self):
        _, fake, _, _ = _turn(_FOLLOW_UP, _HISTORY, _SEARCH_THEN_ANSWER)
        msgs = fake.requests[0]["messages"]
        assert msgs[0]["role"] == "system"
        assert msgs[1:3] == _HISTORY
        assert msgs[3] == {"role": "user", "content": _FOLLOW_UP}

    def test_evidence_is_retrieved_before_the_answer_is_written(self):
        result, fake, _, events = _turn(_FOLLOW_UP, _HISTORY, _SEARCH_THEN_ANSWER)
        answer_call = ("model", len(fake.requests) - 1)
        assert ("search", "ZZZ ledger rebuild challenges") in events
        assert events.index(("search", "ZZZ ledger rebuild challenges")) < events.index(
            answer_call
        )
        assert "settle overnight" in result["answer_md"]


class TestVoicePlacement:
    def test_voice_rules_are_in_the_system_prompt(self):
        _, fake, _, _ = _turn(_FOLLOW_UP, _HISTORY, _SEARCH_THEN_ANSWER)
        system = fake.requests[0]["messages"][0]["content"]
        for line in (
            "**FOCUS:**",
            "Write natural prose paragraphs",
            "**Bold ALL client names and numbers.**",
            "State facts. Do not evaluate Matt.",
        ):
            assert line in system, f"{line!r} missing from the system prompt"

    def test_openers_are_examples_not_exact_text(self):
        _, fake, _, _ = _turn(_FOLLOW_UP, _HISTORY, _SEARCH_THEN_ANSWER)
        everything = " ".join(
            m.get("content") or "" for r in fake.requests for m in r["messages"]
        )
        assert "Start your response with this exact text" not in everything
        system = fake.requests[0]["messages"][0]["content"]
        assert "Examples of how Agy opens" in system
        assert system.count("🐾") >= 2, "expected several opener lines as examples"
