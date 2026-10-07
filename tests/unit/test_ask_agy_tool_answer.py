"""MATTGPT-275 Red: Ask Agy answers through a tool-calling loop.

agy_answer(question, stories, history) replaces rag_answer() behind
send_to_backend(). The model gets the system prompt (persona, MATT_DNA,
profile), the conversation, and the same per-answer voice instructions as
today, plus a search_stories tool backed by semantic_search(). It answers
directly or searches first; nothing refuses on search confidence.

Class W (wiring): send_to_backend() calls agy_answer() with the history.
Class R (rejections kept): nonsense rules and router out_of_scope / personal
  still reject before any model call (decision 1).
Class T (tool loop): no search when the model answers directly; a tool call
  runs semantic_search() with the model's query and returns story context;
  a weak search is answered, not refused; search rounds are capped and the
  last call must answer.
Class V (voice): the same instructions reach the model (opener, focus angle,
  prose, bolding, state facts), the synthesis voice follows the router, and
  Professional Narrative stories carry the verbatim requirement.
Class P (post-processing and contract): profile markers become
  profile_categories, clients of the stories used and numbers are bolded,
  $ is escaped, sources are the stories the searches returned, log_query
  runs once.

The model is a scripted fake at openai.OpenAI, as in
test_ask_agy_history.py. Stories are invented fixtures, not corpus titles.
"""

import json
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from ui.pages.ask_mattgpt.prompts import STANDARD_DELTA, SYNTHESIS_DELTA

logging.getLogger("streamlit").setLevel(logging.ERROR)

# MATT_DNA is "" until sync_portfolio_metadata() runs; patch an invented
# sentinel so the system-prompt assertion does not depend on test order.
_DNA_SENTINEL = "ZZZ_SENTINEL_MATT_DNA"

_STORY_A = {
    "id": "zzz-story-a",
    "Title": "ZZZ Sentinel Ledger Rebuild",
    "Client": "Zephyrine Bank",
    "Theme": "Execution & Delivery",
    "Situation": ["The ledger could not settle overnight."],
    "Task": ["Rebuild settlement."],
    "Action": ["Matt led a team of 40 engineers."],
    "Result": ["Settlement ran in 2 hours."],
    "5PSummary": "Rebuilt a ledger.",
}
_STORY_B = {
    "id": "zzz-story-b",
    "Title": "ZZZ Sentinel Portal Recovery",
    "Client": "Quillmark Telecom",
    "Theme": "Execution & Delivery",
    "Situation": ["The portal was failing."],
    "Task": ["Recover it."],
    "Action": ["Matt stabilized releases."],
    "Result": ["Releases resumed."],
    "5PSummary": "Recovered a portal.",
}
_STORY_PN = {
    "id": "zzz-story-pn",
    "Title": "ZZZ Sentinel Career Narrative",
    "Client": "Independent Project",
    "Theme": "Professional Narrative",
    "Situation": ["Matt reflected on his career."],
    "Task": ["Name what he does."],
    "Action": ["He wrote it down."],
    "Result": ["A clear statement."],
    "5PSummary": "I'm a builder who likes to build something from nothing.",
}
_STORIES = [_STORY_A, _STORY_B, _STORY_PN]


def _response(content=None, tool_query=None):
    tool_calls = None
    if tool_query is not None:
        tool_calls = [
            SimpleNamespace(
                id="call_zzz",
                type="function",
                function=SimpleNamespace(
                    name="search_stories",
                    arguments=json.dumps({"query": tool_query}),
                ),
            )
        ]
    message = SimpleNamespace(content=content, tool_calls=tool_calls, role="assistant")
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=message,
                finish_reason="tool_calls" if tool_calls else "stop",
            )
        ]
    )


class _FakeOpenAI:
    """Scripted chat model. Records every request; replays responses in order,
    repeating the last one when the script runs out."""

    def __init__(self, script):
        self.script = list(script)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs, default=str)))
        if len(self.script) > 1:
            return self.script.pop(0)
        return self.script[0]


def _search_result(results, top_score=0.42, confidence="high"):
    return {
        "results": results,
        "top_score": top_score,
        "confidence": confidence,
        "profile_facts": "",
    }


def _run(
    script,
    question="Tell me about his ledger work",
    family="behavioral",
    router_score=0.6,
    search=None,
    history=None,
    nonsense=None,
):
    """Run agy_answer with the model, router, search and loggers faked.
    Returns (result, fake_model, search_mock, log_query_mock, session)."""
    fake = _FakeOpenAI(script)
    session = {}
    mock_st = MagicMock()
    mock_st.session_state = session
    search_mock = MagicMock(return_value=search or _search_result([_STORY_A]))
    log_query_mock = MagicMock()
    with (
        patch("openai.OpenAI", return_value=fake),
        patch.object(bs, "st", mock_st),
        patch.object(bs, "semantic_search", search_mock),
        patch.object(
            bs,
            "is_portfolio_query_semantic",
            return_value=(True, router_score, "zzz-intent", family),
        ),
        patch.object(bs, "is_nonsense", return_value=nonsense),
        patch.object(bs, "log_query", log_query_mock),
        patch.object(bs, "log_offdomain", MagicMock()),
        patch.object(bs, "MATT_DNA", _DNA_SENTINEL),
    ):
        result = bs.agy_answer(question, _STORIES, history=history)
    return result, fake, search_mock, log_query_mock, session


def _tool_messages(request):
    return [m for m in request["messages"] if m.get("role") == "tool"]


# ---------------------------------------------------------------------------
# Class W: send_to_backend() delegates to agy_answer()
# ---------------------------------------------------------------------------


class TestWiring:
    def test_send_to_backend_calls_agy_answer_with_history(self):
        transcript = [
            {"role": "user", "text": "q1"},
            {"type": "conversational", "Role": "assistant", "text": "a1"},
            {"role": "user", "text": "current question"},
        ]
        mock_st = MagicMock()
        mock_st.session_state = {"ask_transcript": transcript}
        with (
            patch.object(bs, "st", mock_st),
            patch.object(bs, "agy_answer") as mock_agy,
            patch.object(bs, "rag_answer") as mock_rag,
        ):
            mock_agy.return_value = {"answer_md": "ok", "sources": []}
            bs.send_to_backend("current question", {}, None, _STORIES)
        mock_agy.assert_called_once_with(
            "current question",
            _STORIES,
            history=[
                {"role": "user", "content": "q1"},
                {"role": "assistant", "content": "a1"},
            ],
        )
        mock_rag.assert_not_called()


# ---------------------------------------------------------------------------
# Class R: rejections before any model call
# ---------------------------------------------------------------------------


class TestRejectionsKept:
    def test_nonsense_rule_rejects_without_a_model_call(self):
        result, fake, search, _, session = _run([_response("unused")], nonsense="joke")
        assert result["rejection_reason"] == "rule:joke"
        assert session["ask_last_reason"] == "rule:joke"
        assert result["answer_md"] == ""
        assert fake.requests == []
        search.assert_not_called()

    @pytest.mark.parametrize("family", ["personal", "out_of_scope"])
    def test_router_redirect_rejects_without_a_model_call(self, family):
        result, fake, search, _, session = _run(
            [_response("unused")], family=family, router_score=0.96
        )
        assert result["rejection_reason"] == f"semantic_router:{family}"
        assert session["ask_last_reason"] == f"semantic_router:{family}"
        assert result["answer_md"].startswith("🐾")
        assert fake.requests == []
        search.assert_not_called()


# ---------------------------------------------------------------------------
# Class T: the tool loop
# ---------------------------------------------------------------------------


class TestToolLoop:
    def test_offers_the_search_stories_tool(self):
        _, fake, _, _, _ = _run([_response("He has no PMP.")])
        tools = fake.requests[0]["tools"]
        assert [t["function"]["name"] for t in tools] == ["search_stories"]

    def test_answers_directly_without_searching(self):
        result, fake, search, _, session = _run([_response("He has no PMP.")])
        assert "He has no PMP." in result["answer_md"]
        assert result["sources"] == []
        assert result["rejection_reason"] is None
        assert "ask_last_reason" not in session
        search.assert_not_called()
        assert len(fake.requests) == 1

    def test_tool_call_searches_with_the_models_query(self):
        result, fake, search, _, _ = _run(
            [
                _response(tool_query="ledger settlement team size"),
                _response("He led 40 engineers."),
            ]
        )
        assert search.call_args.args[0] == "ledger settlement team size"
        tool_msgs = _tool_messages(fake.requests[1])
        assert len(tool_msgs) == 1
        assert "ZZZ Sentinel Ledger Rebuild" in tool_msgs[0]["content"]
        assert "He led" in result["answer_md"]

    def test_weak_search_is_answered_not_refused(self):
        result, _, _, _, session = _run(
            [
                _response(tool_query="anything"),
                _response("I don't have a story that shows that."),
            ],
            search=_search_result([_STORY_B], top_score=0.05, confidence="none"),
        )
        assert result["rejection_reason"] is None
        assert "ask_last_reason" not in session
        assert "I don't have a story that shows that." in result["answer_md"]

    def test_search_rounds_are_capped_and_the_last_call_must_answer(self):
        # The fake keeps asking to search; the loop must stop it.
        result, fake, search, _, _ = _run([_response(tool_query="again")])
        # Three search rounds, then one call that may not search.
        assert search.call_count == 3
        assert len(fake.requests) == 4
        assert fake.requests[-1].get("tool_choice") == "none"
        assert all("tool_choice" not in r for r in fake.requests[:-1])

    def test_history_sits_between_system_and_current_question(self):
        history = [
            {"role": "user", "content": "ZZZ_PRIOR_Q"},
            {"role": "assistant", "content": "ZZZ_PRIOR_A"},
        ]
        _, fake, _, _, _ = _run([_response("ok")], history=history)
        msgs = fake.requests[0]["messages"]
        assert msgs[0]["role"] == "system"
        assert msgs[1:3] == history
        assert msgs[3]["role"] == "user"
        assert "Tell me about his ledger work" in msgs[3]["content"]


# ---------------------------------------------------------------------------
# Class V: Agy's voice carries over
# ---------------------------------------------------------------------------


class TestVoiceCarriesOver:
    def test_system_prompt_has_dna_and_profile(self):
        _, fake, _, _, _ = _run([_response("ok")])
        system = fake.requests[0]["messages"][0]["content"]
        assert _DNA_SENTINEL in system
        assert "**About Matt (attested facts):**" in system

    def test_per_answer_voice_instructions_reach_the_model(self):
        _, fake, _, _, _ = _run([_response("ok")])
        user = fake.requests[0]["messages"][-1]["content"]
        assert "Start your response with this exact text:" in user
        assert "**FOCUS:**" in user
        assert "Write natural prose paragraphs after the opening." in user
        assert "**Bold ALL client names and numbers.**" in user
        assert "State facts. Do not evaluate Matt." in user

    def test_synthesis_voice_follows_the_router(self):
        _, fake, _, _, _ = _run([_response("ok")], family="synthesis")
        system = fake.requests[0]["messages"][0]["content"]
        assert SYNTHESIS_DELTA.strip()[:80] in system
        assert STANDARD_DELTA.strip()[:80] not in system

    def test_standard_voice_otherwise(self):
        _, fake, _, _, _ = _run([_response("ok")], family="behavioral")
        system = fake.requests[0]["messages"][0]["content"]
        assert STANDARD_DELTA.strip()[:80] in system

    def test_professional_narrative_result_carries_the_verbatim_requirement(self):
        _, fake, _, _, _ = _run(
            [_response(tool_query="who is Matt"), _response("Matt is a builder.")],
            search=_search_result([_STORY_PN]),
        )
        tool_content = _tool_messages(fake.requests[1])[0]["content"]
        assert "VERBATIM REQUIREMENT" in tool_content
        assert '"builder"' in tool_content


# ---------------------------------------------------------------------------
# Class P: post-processing and the result contract
# ---------------------------------------------------------------------------


class TestPostProcessingAndContract:
    def test_profile_markers_become_profile_categories(self):
        result, _, _, _, _ = _run(
            [_response("He has no PMP. [[profile:certifications]]")]
        )
        assert result["profile_categories"] == ["certifications"]
        assert "[[" not in result["answer_md"]

    def test_known_clients_and_numbers_are_bolded(self):
        # Today's rule: get_known_clients() returns the _KNOWN_CLIENTS cache
        # that sync_portfolio_metadata() fills from the whole corpus, so any
        # known client is bolded, searched or not. Patched so the test does
        # not depend on test order.
        with patch.object(bs, "_KNOWN_CLIENTS", {"Zephyrine Bank"}):
            result, _, _, _, _ = _run(
                [_response("At Zephyrine Bank he led 40 engineers.")]
            )
        assert "**Zephyrine Bank**" in result["answer_md"]
        assert "**40 engineers**" in result["answer_md"]

    def test_dollar_sign_is_escaped(self):
        result, _, _, _, _ = _run([_response("The budget was $2M.")])
        assert "\\$" in result["answer_md"]

    def test_sources_are_the_stories_the_searches_returned(self):
        result, _, _, _, _ = _run(
            [_response(tool_query="ledger"), _response("ok")],
            search=_search_result([_STORY_A, _STORY_B]),
        )
        assert result["sources"] == [
            {
                "id": "zzz-story-a",
                "title": "ZZZ Sentinel Ledger Rebuild",
                "client": "Zephyrine Bank",
            },
            {
                "id": "zzz-story-b",
                "title": "ZZZ Sentinel Portal Recovery",
                "client": "Quillmark Telecom",
            },
        ]

    def test_result_contract_for_the_ui(self):
        result, _, _, _, _ = _run([_response("ok")])
        assert result["modes"] == {"narrative": result["answer_md"]}
        assert result["default_mode"] == "narrative"

    def test_log_query_runs_once_with_the_source_count(self):
        result, _, _, log_query_mock, _ = _run(
            [_response(tool_query="ledger"), _response("ok")],
            search=_search_result([_STORY_A, _STORY_B]),
        )
        assert log_query_mock.call_count == 1
        assert log_query_mock.call_args.kwargs["result_count"] == 2
