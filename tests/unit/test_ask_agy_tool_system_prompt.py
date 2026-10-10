"""MATTGPT-275: the tool-path system prompt contract.

build_tool_system_prompt() states the lever 2 contract as one document:
Agy's identity and voice, grounding in Matt's facts and the returned stories,
conversational behavior (follow-ups inherit context, topic switches reset it),
and the tool contract (the app forces a search every turn; the model writes
the query, resolving references to the conversation).

These tests pin that the contract's sections are present, each shared rule
appears once, and the old pipeline's language is gone: primary and preloaded
stories, deciding whether to search, an opening provided as exact text,
closers, the unpopulated client list, "stories below", and invented example
facts under a real client name. The old rag_answer() prompts (BASE_PROMPT,
STANDARD_DELTA, SYNTHESIS_DELTA, OFF_TOPIC_GUARD) are not under test here.
"""

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from ui.pages.ask_mattgpt.prompts import build_tool_system_prompt

pytestmark = pytest.mark.xfail(
    reason="MATTGPT-275; remove in the 275 Green commit",
    strict=False,
)

_DNA = (
    "## ZZZ_SENTINEL facts\n- ZZZ career arc\n\n"
    "**GROUNDING RULES:**\n1. ZZZ_OLD_GROUNDING_RULE\n"
)
_PROFILE = "Education: ZZZ_PROFILE_FACT"
_STANDARD_OPENERS = ["🐾 ZZZ standard opener one.", "🐾 ZZZ standard opener two."]
_SYNTHESIS_OPENERS = ["🐾 ZZZ synthesis opener one.", "🐾 ZZZ synthesis opener two."]
_FOCUS = "ZZZ focus angle."


def _standard():
    return build_tool_system_prompt(
        is_synthesis=False,
        matt_dna=_DNA,
        profile_facts=_PROFILE,
        opener_examples=_STANDARD_OPENERS,
        focus_angle=_FOCUS,
    )


def _synthesis():
    return build_tool_system_prompt(
        is_synthesis=True,
        matt_dna=_DNA,
        profile_facts=_PROFILE,
        opener_examples=_SYNTHESIS_OPENERS,
        focus_angle=_FOCUS,
    )


_BOTH = pytest.mark.parametrize(
    "build", [_standard, _synthesis], ids=["standard", "synthesis"]
)


class TestContractSectionsPresent:
    @_BOTH
    def test_sections_in_order(self, build):
        prompt = build()
        order = [
            "## YOUR JOB",
            "## HOW EACH TURN WORKS",
            "## THE CONVERSATION",
            "## WHAT YOU DO",
            "## WHAT YOU NEVER DO",
            "## BANNED PHRASES",
            "## VOICE",
            "## PRONOUN TRANSFORMATION",
            "ZZZ_SENTINEL facts",
            "**About Matt (attested facts):**",
            "## GROUNDING",
            "FACT-PAIRING RULE",
            "CONTEXT ISOLATION",
            "## ANSWER SHAPE",
            "## OFF-TOPIC GUARD",
        ]
        positions = [prompt.find(marker) for marker in order]
        assert -1 not in positions, dict(zip(order, positions, strict=False))
        assert positions == sorted(positions)

    @_BOTH
    def test_tool_contract(self, build):
        prompt = build()
        assert "Before every answer you search Matt's stories" in prompt
        assert "put the client, project or topic it refers to in the query" in prompt
        assert "each in its own <story> tag" in prompt
        assert "Use the ones that answer the question." in prompt

    @_BOTH
    def test_conversation_contract(self, build):
        prompt = build()
        assert "A follow-up is about what the previous answer discussed." in prompt
        assert "the new question sets the topic" in prompt
        assert "answer for each of them, or ask which one" in prompt

    @_BOTH
    def test_grounding_rule_3_names_both_sources(self, build):
        assert (
            "NEVER invent outcomes, fabricate proof points, or mention clients "
            "not in the facts about Matt or the returned stories" in build()
        )

    @_BOTH
    def test_reflection_paragraph_ban_is_kept(self, build):
        assert "End with a reflection paragraph about Matt's qualities" in build()

    @_BOTH
    def test_off_topic_guard_uses_the_approved_redirect(self, build):
        assert (
            "🐾 I'm focused on Matt's professional experience, including the "
            "projects, teams, and outcomes." in build()
        )

    @_BOTH
    def test_facts_and_profile_without_the_old_grounding_list(self, build):
        prompt = build()
        assert "ZZZ_PROFILE_FACT" in prompt
        assert "ZZZ_OLD_GROUNDING_RULE" not in prompt
        assert "**GROUNDING RULES:**" not in prompt


class TestEachRuleOnce:
    @_BOTH
    @pytest.mark.parametrize(
        "rule",
        [
            "0a. The facts about Matt above are accurate",
            "0b. If the question is about a category the profile has no key for",
            "**Bold ALL client names and numbers.**",
            "Write natural prose paragraphs.",
            "State facts. Do not evaluate Matt.",
        ],
    )
    def test_appears_exactly_once(self, build, rule):
        assert build().count(rule) == 1


class TestOldPipelineLanguageGone:
    @_BOTH
    @pytest.mark.parametrize(
        "phrase",
        [
            "primary story",
            "Draw on all the stories",
            "opening provided",
            "Start your response with this exact text",
            "Want me to dig deeper",
            "No stories are preloaded",
            "when the question needs evidence",
            "standalone",
            "Only cite these clients",
            "the clients shown in the stories",
            "stories below",
            "stories provided",
            "## INSTRUCTIONS",
            "**TOOLS:**",
            "STANDARD MODE",
            "SYNTHESIS MODE",
            "JP Morgan",
            "12 countries",
            "I can only discuss Matt's transformation experience",
        ],
    )
    def test_absent(self, build, phrase):
        assert phrase not in build()


class TestModeShapes:
    def test_standard_shape(self):
        prompt = _standard()
        assert "## ANSWER SHAPE: SPECIFIC QUESTION" in prompt
        assert "## ANSWER SHAPE: BIG-PICTURE QUESTION" not in prompt
        assert (
            "A direct question (team size, how long, yes or no, a follow-up asking "
            "for one fact) gets a direct answer first, in a few sentences." in prompt
        )
        assert (
            "A question asking for the story ('Tell me about…', 'How did he…') "
            "follows the WHY → HOW → WHAT flow below." in prompt
        )
        assert "Story answers: 200-350 words" in prompt
        assert "For factual queries" not in prompt
        assert f"**FOCUS:** {_FOCUS}" in prompt

    def test_synthesis_shape(self):
        prompt = _synthesis()
        assert "## ANSWER SHAPE: BIG-PICTURE QUESTION" in prompt
        assert "## ANSWER SHAPE: SPECIFIC QUESTION" not in prompt
        assert "Lead with the Themes" in prompt
        assert "250-400 words" in prompt
        assert "**FOCUS:**" not in prompt

    @pytest.mark.parametrize(
        "build, own, other",
        [
            (_standard, _STANDARD_OPENERS, _SYNTHESIS_OPENERS),
            (_synthesis, _SYNTHESIS_OPENERS, _STANDARD_OPENERS),
        ],
        ids=["standard", "synthesis"],
    )
    def test_opener_examples_sit_in_the_answer_shape(self, build, own, other):
        prompt = build()
        shape = prompt[prompt.index("## ANSWER SHAPE") :]
        assert "Examples of how Agy opens" in shape
        assert prompt.count("Examples of how Agy opens") == 1
        for opener in own:
            assert opener in shape
        for opener in other:
            assert opener not in prompt


class TestWiredIntoAgyAnswer:
    """agy_answer() sends this contract as its system prompt."""

    def _first_call(self, family):
        from tests.unit.test_ask_agy_tool_answer import _response, _run

        _, fake, _, _, _ = _run([_response("ok")], family=family)
        return fake.requests[0]

    def test_standard_turn(self):
        call = self._first_call("behavioral")
        system = call["messages"][0]["content"]
        assert "## HOW EACH TURN WORKS" in system
        assert "## ANSWER SHAPE: SPECIFIC QUESTION" in system
        assert bs.STANDARD_OPENERS[0] in system
        assert bs.SYNTHESIS_OPENERS[0] not in system
        assert "## INSTRUCTIONS" not in system

    def test_synthesis_turn(self):
        system = self._first_call("synthesis")["messages"][0]["content"]
        assert "## ANSWER SHAPE: BIG-PICTURE QUESTION" in system
        assert bs.SYNTHESIS_OPENERS[0] in system
        assert bs.STANDARD_OPENERS[0] not in system

    def test_query_description_is_not_standalone(self):
        call = self._first_call("behavioral")
        query = call["tools"][0]["function"]["parameters"]["properties"]["query"]
        assert "standalone" not in query["description"]
