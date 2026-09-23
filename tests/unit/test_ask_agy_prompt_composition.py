"""MATTGPT-250 Red: Ask Agy consumes profile_facts and injects rules 0a/0b.

Class C: citation rules 0a and 0b appear in the captured Agy system message.
Class G: with semantic_search returning a known profile_facts, Ask Agy's
  captured system message contains the four certifications and
  "French (B2, self-assessed)", positioned before **GROUNDING RULES:**.

All assertions inspect the Agy system message specifically. rag_answer may
make more than one OpenAI call; the fixture identifies the Agy call by
matching a stable persona line from the MATT_DNA template built by
generate_dynamic_dna() (`**Leadership Philosophy:**`) rather than by
assuming call order. If the anchor is ever removed from MATT_DNA, the
fixture's own "Agy response call not captured" check fails loudly and is
distinguishable from a Class C or Class G assertion failure.

Fixture failure modes ("Agy response call not captured" and "Multiple
Agy calls captured") name the fixture explicitly, so a Red result always
names the specific claim under test rather than the fixture.

Query used: "Tell me about Matt's payments work at JPMorgan" -- baseline
from Stage 1, known-answer path.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from utils.corpus_loader import load_stories

logging.getLogger("streamlit").setLevel(logging.ERROR)


# ---------------------------------------------------------------------------
# Constants: markers Green must produce
# ---------------------------------------------------------------------------

_TEST_PROFILE_FACTS_MARKER = (
    "TEST_MARKER_START\n"
    "He holds a Master's degree, Information Technology from American "
    "InterContinental University.\n"
    "Certifications: SAFe 4 Certified Agilist, Microsoft Certified "
    "Professional (MCP) - Oracle, AWS Launchpad Champion, AWS Certified "
    "Solutions Architect - Associate.\n"
    "Languages: English (native), French (B2, self-assessed).\n"
    "TEST_MARKER_END"
)

# Four certifications must appear verbatim in the Agy system message
# per acceptance query 1.
_CERTIFICATIONS_VERBATIM = [
    "SAFe 4 Certified Agilist",
    "Microsoft Certified Professional (MCP) - Oracle",
    "AWS Launchpad Champion",
    "AWS Certified Solutions Architect - Associate",
]

_LANGUAGES_VERBATIM = "French (B2, self-assessed)"

# Rule 0a and 0b wording from BACKLOG.md::MATTGPT-250 (ea20de2).
# 0a has two clauses. Both must reach the system message.
_RULE_0A_NO_INFERENCE = (
    "state what the block says, do not infer capability or meaning from it"
)
_RULE_0A_DIRECT_NO = "an item not in the list gets a direct no"
_RULE_0B_MARKER = "Nothing I know about Matt covers that"

_GROUNDING_HEADER = "**GROUNDING RULES:**"

# Stable Agy persona anchor -- present in the MATT_DNA template built by
# generate_dynamic_dna(). Used to identify the Agy call among any OpenAI
# calls rag_answer may make. If the anchor is ever removed, the fixture
# fails with "Agy response call not captured", which is distinguishable
# from a Class C or Class G assertion failure.
_AGY_ANCHOR = "**Leadership Philosophy:**"

_JPMORGAN_QUERY = "Tell me about Matt's payments work at JPMorgan"


# ---------------------------------------------------------------------------
# Shared fixture: capture Ask Agy's system message
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real_stories():
    return load_stories("echo_star_stories_nlp.jsonl")


@pytest.fixture
def captured_agy_system_message(real_stories):
    """Runs rag_answer with semantic_search mocked (happy path,
    profile_facts set) and openai.OpenAI patched globally to return a
    fake client. After rag_answer completes, searches
    create.call_args_list for the call whose system message contains
    the Agy persona anchor. Returns that system message.

    Does not assume how many OpenAI calls rag_answer makes or in what
    order. The anchor is what identifies Agy.

    Fails with distinct messages so Red output always names the true
    failure:
      - "Agy response call not captured" (zero anchor matches)
      - "Multiple Agy calls captured" (more than one anchor match)
    Neither string collides with Class C or Class G assertion strings.
    """
    fake_completion = MagicMock()
    fake_completion.choices = [MagicMock()]
    fake_completion.choices[0].message.content = "captured-prompt-test-response"
    fake_openai = MagicMock()
    fake_openai.chat.completions.create.return_value = fake_completion

    def _fake_search(query, filters, **kwargs):
        return {
            "results": [real_stories[0]],
            "confidence": "high",
            "top_score": 0.85,
            "profile_facts": _TEST_PROFILE_FACTS_MARKER,
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
        bs.rag_answer(_JPMORGAN_QUERY, {}, real_stories)

    # Find Agy's create() call by anchor match. Do not assume ordering
    # or count -- rag_answer may make any number of OpenAI calls.
    matching_system_messages: list[str] = []
    for call in fake_openai.chat.completions.create.call_args_list:
        messages = call.kwargs.get("messages", [])
        system_msgs = [
            m.get("content", "") for m in messages if m.get("role") == "system"
        ]
        for content in system_msgs:
            if _AGY_ANCHOR in content:
                matching_system_messages.append(content)

    if len(matching_system_messages) == 0:
        pytest.fail(
            f"Agy response call not captured -- no OpenAI call had a "
            f"system message containing anchor {_AGY_ANCHOR!r}. Total "
            f"OpenAI calls: {len(fake_openai.chat.completions.create.call_args_list)}. "
            f"This indicates rag_answer did not reach the Agy response "
            f"generator (possibly gated upstream) OR the anchor no longer "
            f"appears in MATT_DNA. Not a Class C or Class G failure."
        )
    if len(matching_system_messages) > 1:
        pytest.fail(
            f"Multiple Agy calls captured ({len(matching_system_messages)}) "
            f"-- anchor {_AGY_ANCHOR!r} matched more than one system "
            f"message. Fixture cannot uniquely identify the Agy call. "
            f"Not a Class C or Class G failure."
        )
    return matching_system_messages[0]


# ---------------------------------------------------------------------------
# Class C: rules 0a and 0b appear in the captured Agy system message
# ---------------------------------------------------------------------------


class TestCitationRulesInCapturedSystemMessage:
    """Rules 0a and 0b appear in the runtime Agy system prompt.

    0a has two clauses per the ticket: (a) no-inference (state what the
    block says, do not infer capability or meaning) and (b) direct-no
    (an item not in the list of a known category gets a direct no
    followed by what the list does contain -- this is what PMP
    acceptance depends on)."""

    def test_rule_0a_no_inference_clause_present_in_system_message(
        self, captured_agy_system_message
    ):
        assert _RULE_0A_NO_INFERENCE in captured_agy_system_message, (
            f"rule 0a no-inference clause {_RULE_0A_NO_INFERENCE!r} not "
            f"found in captured Agy system message. Head: "
            f"{captured_agy_system_message[:600]!r}"
        )

    def test_rule_0a_direct_no_clause_present_in_system_message(
        self, captured_agy_system_message
    ):
        """PMP acceptance depends on this clause: 'Does Matt have a PMP?'
        must return a direct no plus the list of certifications, which
        only fires if the rule is present."""
        assert _RULE_0A_DIRECT_NO in captured_agy_system_message, (
            f"rule 0a direct-no clause {_RULE_0A_DIRECT_NO!r} not found "
            f"in captured Agy system message. PMP acceptance depends on "
            f"this clause. Head: {captured_agy_system_message[:600]!r}"
        )

    def test_rule_0b_present_in_system_message(self, captured_agy_system_message):
        assert _RULE_0B_MARKER in captured_agy_system_message, (
            f"rule 0b marker {_RULE_0B_MARKER!r} not found in captured "
            f"Agy system message. Head: {captured_agy_system_message[:600]!r}"
        )


# ---------------------------------------------------------------------------
# Class G: Ask Agy consumes profile_facts into the Agy system message
# ---------------------------------------------------------------------------


class TestAskAgyConsumesProfileFacts:
    """The -250 fix itself: rag_answer takes profile_facts out of the
    search result and puts it into the prompt the LLM receives.

    All three tests assert on the Agy system message specifically. A
    Green that puts facts in the user message fails."""

    def test_system_message_contains_all_four_certifications_verbatim(
        self, captured_agy_system_message
    ):
        missing = [
            c for c in _CERTIFICATIONS_VERBATIM if c not in captured_agy_system_message
        ]
        assert not missing, (
            f"Agy system message missing verbatim certifications: {missing!r}. "
            f"Head: {captured_agy_system_message[:600]!r}"
        )

    def test_system_message_contains_languages_entry_verbatim(
        self, captured_agy_system_message
    ):
        assert _LANGUAGES_VERBATIM in captured_agy_system_message, (
            f"languages entry {_LANGUAGES_VERBATIM!r} not found in captured "
            f"Agy system message. Head: {captured_agy_system_message[:600]!r}"
        )

    def test_profile_block_precedes_grounding_rules_and_rules_follow(
        self, captured_agy_system_message
    ):
        """Full ordering asserted: profile block anchor < GROUNDING RULES
        header < rule 0a < rule 0b. A Green that reverses any of the three
        pairs fails."""
        block_pos = captured_agy_system_message.find(_LANGUAGES_VERBATIM)
        header_pos = captured_agy_system_message.find(_GROUNDING_HEADER)
        rule_0a_pos = captured_agy_system_message.find(_RULE_0A_NO_INFERENCE)
        rule_0b_pos = captured_agy_system_message.find(_RULE_0B_MARKER)

        assert (
            block_pos >= 0
        ), f"profile block anchor {_LANGUAGES_VERBATIM!r} not in Agy system message"
        assert (
            header_pos >= 0
        ), f"grounding rules header {_GROUNDING_HEADER!r} not in Agy system message"
        assert rule_0a_pos >= 0, "rule 0a marker not in Agy system message"
        assert rule_0b_pos >= 0, "rule 0b marker not in Agy system message"

        assert block_pos < header_pos, (
            f"profile block must appear before GROUNDING RULES header; "
            f"block at {block_pos}, header at {header_pos}"
        )
        assert header_pos < rule_0a_pos, (
            f"GROUNDING RULES header must appear before rule 0a; "
            f"header at {header_pos}, rule 0a at {rule_0a_pos}"
        )
        assert rule_0a_pos < rule_0b_pos, (
            f"rule 0a must appear before rule 0b; "
            f"rule 0a at {rule_0a_pos}, rule 0b at {rule_0b_pos}"
        )
