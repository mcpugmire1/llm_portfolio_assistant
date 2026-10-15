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
Class S (the call, MATTGPT-282): every model call is a streamed Responses
  API call on ASK_ANSWER_MODEL (gpt-6.1-sol, pinned by name; no dated
  snapshot is listed) at reasoning effort medium with max_output_tokens
  4000, no temperature and no max_tokens, as the lever2_sol arm of
  docs/evidence/MATTGPT-282/sol_arms_20261011_211830/ sent it. Answer text
  deltas reach on_delta as they arrive; answer_md is the post-processed
  whole text (stream, then swap).

The model is a scripted fake at openai.OpenAI whose responses.create
returns a stream of events. Stories are invented fixtures, not corpus
titles.
"""

import json
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest

from config import constants
from ui.pages.ask_mattgpt import backend_service as bs

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


def _response(content=None, tool_query=None, chunks=None, status="completed"):
    """One streamed Responses API reply: delta events, then the terminal
    event carrying the whole response. content is answer text (streamed in
    `chunks` when given); tool_query makes it a search_stories call."""
    events = []
    output = []
    if tool_query is not None:
        arguments = json.dumps({"query": tool_query})
        events.append(
            SimpleNamespace(
                type="response.function_call_arguments.delta", delta=arguments
            )
        )
        output.append(
            SimpleNamespace(
                type="function_call",
                call_id="call_zzz",
                name="search_stories",
                arguments=arguments,
            )
        )
    if content is not None:
        for piece in chunks or [content]:
            events.append(
                SimpleNamespace(type="response.output_text.delta", delta=piece)
            )
        output.append(SimpleNamespace(type="message", role="assistant"))
    final = SimpleNamespace(
        status=status,
        model="gpt-6.1-sol",
        output=output,
        output_text=content or "",
    )
    terminal = "response.completed" if status == "completed" else f"response.{status}"
    events.append(SimpleNamespace(type=terminal, response=final))
    return events


class _FakeOpenAI:
    """Scripted Responses model. Records every request; replays streamed
    replies in order, repeating the last one when the script runs out."""

    def __init__(self, script):
        self.script = list(script)
        self.requests = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs, default=str)))
        events = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        return iter(list(events))


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
    on_delta=None,
    session_state=None,
    search_effect=None,
):
    """Run agy_answer with the model, router, search and loggers faked.
    session_state seeds st.session_state (e.g. a chip's flags).
    Returns (result, fake_model, search_mock, log_query_mock, session)."""
    fake = _FakeOpenAI(script)
    session = dict(session_state or {})
    mock_st = MagicMock()
    mock_st.session_state = session
    search_mock = MagicMock(return_value=search or _search_result([_STORY_A]))
    if search_effect is not None:
        search_mock.side_effect = lambda *a, **k: search_effect(session)
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
        result = bs.agy_answer(question, _STORIES, history=history, on_delta=on_delta)
    return result, fake, search_mock, log_query_mock, session


def _system(request):
    first = request["input"][0]
    assert first["role"] == "system"
    return first["content"]


def _tool_outputs(request):
    return [i for i in request["input"] if i.get("type") == "function_call_output"]


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
            on_delta=None,
        )

    def test_send_to_backend_passes_on_delta_through(self):
        def on_delta(text):
            return None

        mock_st = MagicMock()
        mock_st.session_state = {"ask_transcript": []}
        with (
            patch.object(bs, "st", mock_st),
            patch.object(bs, "agy_answer") as mock_agy,
        ):
            mock_agy.return_value = {"answer_md": "ok", "sources": []}
            bs.send_to_backend("q", {}, None, _STORIES, on_delta=on_delta)
        mock_agy.assert_called_once()
        assert mock_agy.call_args.kwargs["on_delta"] is on_delta


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
        assert result["intent_family"] == family
        assert session["ask_last_reason"] == f"semantic_router:{family}"
        assert result["answer_md"].startswith("🐾")
        assert fake.requests == []
        search.assert_not_called()

    def test_a_suggestion_chip_is_answered_past_the_nonsense_rules_and_router(self):
        """Landing chips set __ask_force_answer__: their fixed questions are
        answered even when a rule or the router would redirect them."""
        result, fake, _, _, session = _run(
            [_response(tool_query="ledger"), _response("Here is the ledger work.")],
            family="out_of_scope",
            router_score=0.96,
            nonsense="joke",
            session_state={"__ask_force_answer__": True},
        )
        assert result["rejection_reason"] is None
        assert "ask_last_reason" not in session
        assert result["answer_md"].startswith("Here is the ledger work")
        assert len(fake.requests) == 2
        assert (
            "__ask_force_answer__" not in session
        ), "the flag must not outlive its turn"

    def test_without_the_chip_flag_the_same_question_is_redirected(self):
        result, fake, _, _, _ = _run(
            [_response("unused")], family="out_of_scope", router_score=0.96
        )
        assert result["rejection_reason"] == "semantic_router:out_of_scope"
        assert fake.requests == []


# ---------------------------------------------------------------------------
# Class T: the tool loop
# ---------------------------------------------------------------------------


class TestToolLoop:
    def test_offers_the_search_stories_tool_as_lever_2_measured_it(self):
        _, fake, _, _, _ = _run([_response("He has no PMP.")])
        assert fake.requests[0]["tools"] == [
            {
                "type": "function",
                "name": "search_stories",
                "description": (
                    "Semantic search over Matt's STAR career stories. "
                    "Returns the top 5 stories."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A standalone search query.",
                        }
                    },
                    "required": ["query"],
                },
                "strict": False,
            }
        ]

    def test_first_call_is_a_forced_search(self):
        # MATTGPT-275 contract: every turn retrieves; the model never decides
        # whether to search (test_ask_agy_turn_contract.py pins the full contract).
        _, fake, _, _, _ = _run([_response(tool_query="ledger"), _response("ok")])
        assert fake.requests[0].get("tool_choice") == "required"

    def test_tool_call_searches_with_the_models_query(self):
        result, fake, search, _, _ = _run(
            [
                _response(tool_query="ledger settlement team size"),
                _response("He led 40 engineers."),
            ]
        )
        assert search.call_args.args[0] == "ledger settlement team size"
        calls = [
            i for i in fake.requests[1]["input"] if i.get("type") == "function_call"
        ]
        assert calls == [
            {
                "type": "function_call",
                "call_id": "call_zzz",
                "name": "search_stories",
                "arguments": json.dumps({"query": "ledger settlement team size"}),
            }
        ]
        outputs = _tool_outputs(fake.requests[1])
        assert len(outputs) == 1
        assert outputs[0]["call_id"] == "call_zzz"
        assert "ZZZ Sentinel Ledger Rebuild" in outputs[0]["output"]
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
        assert fake.requests[0].get("tool_choice") == "required"
        assert fake.requests[-1].get("tool_choice") == "none"
        assert all(r.get("tool_choice") == "auto" for r in fake.requests[1:-1])

    def test_history_sits_between_system_and_current_question(self):
        history = [
            {"role": "user", "content": "ZZZ_PRIOR_Q"},
            {"role": "assistant", "content": "ZZZ_PRIOR_A"},
        ]
        _, fake, _, _, _ = _run([_response("ok")], history=history)
        items = fake.requests[0]["input"]
        assert items[0]["role"] == "system"
        assert items[1:3] == history
        assert items[3] == {"role": "user", "content": "Tell me about his ledger work"}


# ---------------------------------------------------------------------------
# Class V: Agy's voice carries over
# ---------------------------------------------------------------------------


class TestVoiceCarriesOver:
    def test_system_prompt_has_dna_and_profile(self):
        _, fake, _, _, _ = _run([_response("ok")])
        system = _system(fake.requests[0])
        assert _DNA_SENTINEL in system
        assert "**About Matt (attested facts):**" in system

    def test_per_answer_voice_instructions_reach_the_model(self):
        # MATTGPT-275: the instruction block moved to the system prompt with
        # the openers as examples; the user message is the question as asked.
        _, fake, _, _, _ = _run([_response("ok")])
        system = _system(fake.requests[0])
        assert "Examples of how Agy opens" in system
        assert "**FOCUS:**" in system
        assert "Write natural prose paragraphs" in system
        assert "**Bold ALL client names and numbers.**" in system
        assert "State facts. Do not evaluate Matt." in system
        user = fake.requests[0]["input"][-1]["content"]
        assert user == "Tell me about his ledger work"
        assert "Start your response with this exact text" not in system + user

    @pytest.mark.parametrize("family", ["behavioral", "synthesis"])
    def test_every_opener_line_is_an_example_synthesis_first(self, family):
        # As measured: one example list, synthesis openers then standard ones,
        # in both modes.
        _, fake, _, _, _ = _run([_response("ok")], family=family)
        examples = "; ".join(
            f'"{o}"' for o in bs.SYNTHESIS_OPENERS + bs.STANDARD_OPENERS
        )
        assert f"Examples of how Agy opens: {examples}." in _system(fake.requests[0])

    def test_synthesis_voice_follows_the_router(self):
        _, fake, _, _, _ = _run([_response("ok")], family="synthesis")
        system = _system(fake.requests[0])
        assert "## SYNTHESIS MODE" in system
        assert "## STANDARD MODE" not in system

    def test_standard_voice_otherwise(self):
        _, fake, _, _, _ = _run([_response("ok")], family="behavioral")
        system = _system(fake.requests[0])
        assert "## STANDARD MODE" in system

    def test_professional_narrative_result_carries_the_verbatim_requirement(self):
        _, fake, _, _, _ = _run(
            [_response(tool_query="who is Matt"), _response("Matt is a builder.")],
            search=_search_result([_STORY_PN]),
        )
        tool_content = _tool_outputs(fake.requests[1])[0]["output"]
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


# ---------------------------------------------------------------------------
# Class S: the call (Responses API, streamed, model pinned)
# ---------------------------------------------------------------------------


class TestTheCall:
    def test_ask_answer_model_is_one_constant_pinned_by_name(self):
        from config import constants

        assert getattr(constants, "ASK_ANSWER_MODEL", None) == "gpt-6.1-sol"

    def test_every_call_is_a_streamed_responses_call_with_the_measured_settings(self):
        _, fake, _, _, _ = _run([_response(tool_query="ledger"), _response("ok")])
        assert len(fake.requests) == 2
        for request in fake.requests:
            assert request["model"] == "gpt-6.1-sol"
            assert request["stream"] is True
            assert request["reasoning"] == {"effort": "medium"}
            assert request["max_output_tokens"] == 4000
            for absent in ("temperature", "max_tokens", "messages"):
                assert absent not in request

    def test_answer_deltas_reach_on_delta_in_order(self):
        received = []
        _run(
            [
                _response(tool_query="ledger"),
                _response(
                    "He led 40 engineers.", chunks=["He led ", "40 ", "engineers."]
                ),
            ],
            on_delta=received.append,
        )
        assert "".join(received) == "He led 40 engineers."

    def test_answer_md_is_the_post_processed_whole_text(self):
        # Stream, then swap: the visitor sees raw deltas while the answer
        # arrives; the transcript keeps the post-processed text.
        result, _, _, _, _ = _run(
            [
                _response(tool_query="ledger"),
                _response(
                    "The budget was $2M. [[profile:certifications]]",
                    chunks=["The budget was $2M. ", "[[profile:certifications]]"],
                ),
            ],
            on_delta=lambda text: None,
        )
        assert "\\$" in result["answer_md"]
        assert "[[" not in result["answer_md"]
        assert result["profile_categories"] == ["certifications"]

    def test_an_incomplete_response_still_answers_with_its_text(self):
        # max_output_tokens counts reasoning tokens; a capped reply keeps
        # whatever text it produced.
        result, _, _, _, _ = _run(
            [_response(tool_query="ledger"), _response("He led", status="incomplete")]
        )
        assert result["answer_md"] == "He led"
        assert result.get("degraded") is False

    def test_without_on_delta_the_answer_is_unchanged(self):
        result, _, _, _, _ = _run([_response(tool_query="ledger"), _response("ok")])
        assert result["answer_md"] == "ok"


# ---------------------------------------------------------------------------
# Class E: model errors
# ---------------------------------------------------------------------------


_ERROR_MESSAGE = "Sorry, I couldn't generate an answer right now."


class _FailingOpenAI:
    """Raises on the first call, or after replaying `script` (one streamed
    reply per call) when given one."""

    def __init__(self, error, script=()):
        self.error = RuntimeError(error) if isinstance(error, str) else error
        self.script = list(script)
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        if self.script:
            return iter(list(self.script.pop(0)))
        raise self.error


def _run_failing(error, script=()):
    mock_st = MagicMock()
    mock_st.session_state = {}
    with (
        patch("openai.OpenAI", return_value=_FailingOpenAI(error, script)),
        patch.object(bs, "st", mock_st),
        patch.object(
            bs, "semantic_search", MagicMock(return_value=_search_result([_STORY_A]))
        ),
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
        return bs.agy_answer("Tell me about his ledger work", _STORIES)


class TestModelErrors:
    def test_rate_limit_returns_the_breather_message_with_no_sources(self):
        result = _run_failing("Error code: 429 rate_limit_exceeded")
        assert "breather" in result["answer_md"]
        assert result["sources"] == []

    def test_other_errors_return_the_error_message_with_no_sources(self):
        result = _run_failing("upstream exploded")
        assert result["answer_md"] == _ERROR_MESSAGE
        assert result["sources"] == []
        assert result["degraded"] is True

    def test_a_generic_error_is_logged_with_its_traceback(self, caplog):
        with caplog.at_level(logging.ERROR, logger=bs.logger.name):
            _run_failing("upstream exploded")
        records = [
            r for r in caplog.records if "agy_answer fatal error" in r.getMessage()
        ]
        assert records, "the fatal error was not logged"
        assert records[0].exc_info is not None, "logged without its traceback"

    def test_the_error_answer_carries_no_story_text(self):
        result = _run_failing("upstream exploded")
        shown = [result["answer_md"], *result.get("modes", {}).values()]
        for story in _STORIES:
            for field in ("5PSummary", "Title"):
                assert not any(
                    story[field] in text for text in shown
                ), f"story {field} {story[field]!r} reached the visitor"

    def test_a_connection_timeout_returns_the_error_message(self):
        import httpx
        import openai

        timeout = openai.APITimeoutError(
            request=httpx.Request("POST", "https://api.openai.com/v1/responses")
        )
        result = _run_failing(timeout)
        assert result["answer_md"] == _ERROR_MESSAGE
        assert result["sources"] == []

    def test_an_error_after_a_search_returns_no_sources(self):
        result = _run_failing(
            "upstream exploded", script=[_response(tool_query="ledger rebuild")]
        )
        assert result["answer_md"] == _ERROR_MESSAGE
        assert result["sources"] == []

    @pytest.mark.parametrize("event", ["response.failed", "error"])
    def test_a_stream_that_fails_mid_answer_ends_on_the_error_message(
        self, event, caplog
    ):
        """Text has already streamed when the stream reports a failure: the
        finished turn is the error message (it replaces the streamed text),
        with no sources, and the server log names the failure event."""
        failing = [
            SimpleNamespace(type="response.output_text.delta", delta="Matt led "),
            SimpleNamespace(type="response.output_text.delta", delta="a team of"),
            SimpleNamespace(type=event, response=None),
        ]
        deltas = []
        with caplog.at_level(logging.ERROR, logger=bs.logger.name):
            result, _, _, _, _ = _run(
                [_response(tool_query="ledger"), failing], on_delta=deltas.append
            )
        assert "".join(deltas) == "Matt led a team of"
        assert result["answer_md"] == _ERROR_MESSAGE
        assert result["sources"] == []
        assert result["degraded"] is True
        assert (
            f"answer call failed: {event}" in caplog.text
        ), f"server log does not name {event!r}"


class _BreakingOpenAI:
    """Replays one streamed reply per call. A reply given as (events, error)
    yields its events, then raises the error mid-stream, as a dropped or
    stalled connection does (MATTGPT-303: httpx.ReadError and ReadTimeout
    raised from the stream body, outside the SDK's own retries)."""

    def __init__(self, script):
        self.script = list(script)
        self.requests = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.requests.append(json.loads(json.dumps(kwargs, default=str)))
        reply = self.script.pop(0)
        events, error = reply if isinstance(reply, tuple) else (reply, None)

        def stream():
            yield from events
            if error is not None:
                raise error

        return stream()


def _run_breaking(script, on_delta=None):
    fake = _BreakingOpenAI(script)
    mock_st = MagicMock()
    mock_st.session_state = {}
    with (
        patch("openai.OpenAI", return_value=fake),
        patch.object(bs, "st", mock_st),
        patch.object(
            bs, "semantic_search", MagicMock(return_value=_search_result([_STORY_A]))
        ),
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
        result = bs.agy_answer(
            "Tell me about his ledger work", _STORIES, on_delta=on_delta
        )
    return result, fake


_BREAKS = {
    "ReadError": httpx.ReadError("[Errno 54] Connection reset by peer"),
    "ReadTimeout": httpx.ReadTimeout("The read operation timed out"),
    "RemoteProtocolError": httpx.RemoteProtocolError("peer closed connection"),
}
_STARTED = [SimpleNamespace(type="response.created")]
_ANSWER = "Matt rebuilt the ledger."


class TestBrokenStreams:
    @pytest.mark.parametrize("error", list(_BREAKS))
    @pytest.mark.parametrize("call", ["search", "answer"])
    def test_a_stream_broken_before_any_text_is_sent_again_once(self, call, error):
        broken = (_STARTED, _BREAKS[error])
        search, answer = _response(tool_query="ledger"), _response(content=_ANSWER)
        script = (
            [broken, search, answer] if call == "search" else [search, broken, answer]
        )
        result, fake = _run_breaking(script)
        assert "rebuilt the ledger" in result["answer_md"]
        assert len(fake.requests) == 3
        assert (
            fake.requests[1 if call == "search" else 2]
            == fake.requests[0 if call == "search" else 1]
        )

    @pytest.mark.parametrize("case", ["after text", "on the second try"])
    def test_a_broken_stream_is_not_sent_again(self, case):
        """After text has streamed, the visitor has seen part of the answer:
        the turn ends on the error message. A second break before text ends
        it too (one retry only)."""
        error = _BREAKS["ReadError"]
        if case == "after text":
            broken = [
                (
                    [
                        SimpleNamespace(
                            type="response.output_text.delta", delta="Matt led a team"
                        )
                    ],
                    error,
                )
            ]
        else:
            broken = [(_STARTED, error), (_STARTED, error)]
        script = [
            _response(tool_query="ledger"),
            *broken,
            _response(content="ZZZ never sent"),
        ]
        deltas = []
        result, fake = _run_breaking(script, on_delta=deltas.append)
        assert result["answer_md"] == _ERROR_MESSAGE
        assert result["sources"] == []
        assert result["degraded"] is True
        assert len(fake.requests) == 1 + len(broken)
        assert "".join(deltas) == ("Matt led a team" if case == "after text" else "")


class TestClientTimeout:
    def test_the_client_waits_at_most_the_measured_read_timeout(self):
        assert getattr(constants, "ASK_ANSWER_READ_TIMEOUT_S", None) == 30
        with patch("openai.OpenAI") as openai_client:
            bs._openai_client()
        assert openai_client.call_args.kwargs["timeout"] == httpx.Timeout(
            30, connect=5.0
        )


_BREATHER = "\U0001f43e I need a quick breather: please try again in a moment!"


def _embedding_fails(session):
    # pinecone_semantic_search() on an embedding failure (MATTGPT-162).
    session["__embed_failure__"] = True
    return _search_result([], top_score=0.0)


def _run_with_embedding_failure():
    return _run(
        [_response(tool_query="ledger"), _response(content="ZZZ unsourced answer")],
        search_effect=_embedding_fails,
    )


class TestEmbeddingFailure:
    """When the search's embedding call fails, the visitor gets the breather
    with no sources, not an answer written without stories, and the flag is
    cleared so the next question isn't affected (MATTGPT-162 on the tool path)."""

    def test_the_visitor_gets_the_breather_with_no_sources(self):
        result, *_ = _run_with_embedding_failure()
        assert result["answer_md"] == _BREATHER
        assert result["sources"] == []

    def test_the_model_is_not_asked_to_answer_after_the_failure(self):
        _, fake, *_ = _run_with_embedding_failure()
        assert len(fake.requests) == 1

    def test_the_flag_is_cleared(self):
        *_, session = _run_with_embedding_failure()
        assert "__embed_failure__" not in session


_RETRIEVED_THREE = _search_result([_STORY_A, _STORY_B, _STORY_PN])


@pytest.mark.xfail(
    reason="MATTGPT-128: source cards should show the stories the answer "
    "cited, not every story the searches returned. How 'cited' is decided "
    "is open (BACKLOG -128, items 1 to 5); each case here quotes a fact "
    "found in exactly one story. Rewritten from the 220d14d cap Red when "
    "rag_answer() was removed (MATTGPT-275). Remove when -128 ships.",
    strict=False,
)
class TestSourcesAreTheCitedStories:
    def _source_ids(self, answer):
        result, *_ = _run(
            [_response(tool_query="ledger"), _response(content=answer)],
            search=_RETRIEVED_THREE,
        )
        return [s["id"] for s in result["sources"]]

    def test_an_answer_citing_one_story_shows_only_that_story(self):
        ids = self._source_ids("Matt rebuilt the ledger. Settlement ran in 2 hours.")
        assert ids == ["zzz-story-a"]

    def test_an_answer_citing_two_stories_shows_both_in_retrieval_order(self):
        ids = self._source_ids("Releases resumed. Settlement ran in 2 hours.")
        assert ids == ["zzz-story-a", "zzz-story-b"]

    def test_a_profile_fact_answer_shows_no_story_cards(self):
        ids = self._source_ids(
            "Matt is based in Atlanta, GA.\n[[profile:location_availability]]"
        )
        assert ids == []

    def test_a_retrieved_but_uncited_narrative_story_is_not_shown(self):
        ids = self._source_ids("Settlement ran in 2 hours.")
        assert "zzz-story-pn" not in ids

    def test_an_off_topic_refusal_shows_no_source_cards(self):
        ids = self._source_ids(
            "\U0001f43e I can only discuss Matt's transformation experience. Ask me "
            "about application modernization, digital innovation, agile "
            "transformation, or leadership."
        )
        assert ids == []


# ---------------------------------------------------------------------------
# Class D: dashes (MATTGPT-275 step 6). The model's em and en dashes are
# replaced by one deterministic rule, in the stream and in the final text:
# em dash (spaced or not) -> ", "; en dash between digits -> " to "; spaced
# en dash -> ", "; unspaced en dash between words -> "-". A replacement comma
# never doubles an existing comma and is dropped before . ! ? or a line end.
# Dashes are written as escapes: the repo's hooks reject a literal em dash.
# ---------------------------------------------------------------------------

EM = "\u2014"
EN = "\u2013"


class TestDashRule:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            (
                f"transaction histories{EM}all while live",
                "transaction histories, all while live",
            ),
            (f"growth {EM} then decline", "growth, then decline"),
            (f"**Fiserv**{EM}the team", "**Fiserv**, the team"),
            (f"spent 70{EN}80% of his time", "spent 70 to 80% of his time"),
            (f"from 2009{EN}2016", "from 2009 to 2016"),
            (f"from 70 {EN} 80 people", "from 70 to 80 people"),
            (f"growth {EN} then decline", "growth, then decline"),
            (f"senior{EN}junior pairings", "senior-junior pairings"),
            (f"payments, {EM} and treasury", "payments, and treasury"),
            (f"payments {EM}, and treasury", "payments, and treasury"),
            (f"he delivered{EM}.", "he delivered."),
            (f"was it worth it{EM}?", "was it worth it?"),
            (f"the first line{EM}\nThe next line", "the first line\nThe next line"),
            (f"the answer ends{EM}", "the answer ends"),
            (
                "a well-known re-platform, with no dashes",
                "a well-known re-platform, with no dashes",
            ),
        ],
    )
    def test_the_rule(self, raw, expected):
        assert bs.normalize_dashes(raw) == expected

    def test_applying_it_twice_changes_nothing(self):
        once = bs.normalize_dashes(f"growth {EM} then 70{EN}80%{EM}.")
        assert bs.normalize_dashes(once) == once


class TestDashesInTheAnswer:
    _CHUNKS = [
        "The team grew ",
        EM,
        " fast, from 70",
        EN,
        "80% of releases",
        f" on time{EM}",
        ".",
    ]
    _SHOWN = "The team grew, fast, from 70 to 80% of releases on time."

    def _answer(self, chunks):
        deltas = []
        result, _, _, _, _ = _run(
            [_response(tool_query="ledger"), _response("".join(chunks), chunks=chunks)],
            on_delta=deltas.append,
        )
        return result, deltas

    def test_the_stream_shows_no_dash_even_when_one_is_split_across_chunks(self):
        _, deltas = self._answer(self._CHUNKS)
        assert not any(EM in d or EN in d for d in deltas), deltas
        assert "".join(deltas) == self._SHOWN

    def test_a_space_before_a_dash_at_a_chunk_end_is_not_left_before_the_comma(self):
        """Stream text is append-only, so a space already shown before a dash
        that arrives in the next chunk would read "grew , fast"."""
        _, deltas = self._answer(["The team grew ", f"{EM} fast."])
        assert "".join(deltas) == "The team grew, fast."

    def test_a_dash_at_the_very_end_of_the_stream_is_resolved(self):
        _, deltas = self._answer(["The answer ends", EM])
        assert "".join(deltas) == "The answer ends"

    def test_the_finished_answer_has_no_dash(self):
        result, _ = self._answer(self._CHUNKS)
        assert EM not in result["answer_md"] and EN not in result["answer_md"]

    def test_the_swap_keeps_the_streamed_wording(self):
        """The finished answer adds bolding only: with ** removed it reads as
        the stream did."""
        result, deltas = self._answer(self._CHUNKS)
        assert result["answer_md"].replace("**", "") == "".join(deltas)
