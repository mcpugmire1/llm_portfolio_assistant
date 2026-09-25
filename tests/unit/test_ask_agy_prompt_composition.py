"""MATTGPT-250 Red: Ask Agy consumes profile_facts and injects rules 0a/0b.

Class C: citation rules 0a and 0b appear in the captured Agy system message,
  and rule 0a also appears in the captured Agy user message after the
  question.
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
    "Education: Master's degree, Information Technology, American "
    "InterContinental University.\n"
    "Certifications: AWS Certified Solutions Architect - Associate "
    "(issued 2020, expired 2023), AWS Certified Cloud Practitioner "
    "(issued 2019, expired 2023), SAFe 4 Certified Agilist (issued "
    "2017, expired), Oracle 8i DBA exams passed (OCP track): SQL and "
    "PL/SQL, Architecture and Administration, Backup and Recovery "
    "(2002).\n"
    "Languages: English (native), French (B2, self-assessed).\n"
    "TEST_MARKER_END"
)

# Four certifications must appear verbatim in the Agy system message
# per acceptance query 1. Wording updated Sept 24, 2026 (ticket 9d5f575):
# expiry dates included, none current, PMP still absent.
_CERTIFICATIONS_VERBATIM = [
    "AWS Certified Solutions Architect - Associate (issued 2020, expired 2023)",
    "AWS Certified Cloud Practitioner (issued 2019, expired 2023)",
    "SAFe 4 Certified Agilist (issued 2017, expired)",
    (
        "Oracle 8i DBA exams passed (OCP track): SQL and PL/SQL, "
        "Architecture and Administration, Backup and Recovery (2002)"
    ),
]

_LANGUAGES_VERBATIM = "French (B2, self-assessed)"

# Rule 0a and 0b wording from BACKLOG.md::MATTGPT-250 (9d5f575).
# 0a has three testable fragments; 0b has two.
_RULE_0A_NO_INFERENCE = (
    "state what the facts say, do not infer capability or meaning from it"
)
_RULE_0A_DIRECT_NO = "an item not in the list gets a direct no"
# New at 9d5f575: Agy must answer from the block only, not join facts to stories.
_RULE_0A_NO_STORY_CONNECT = (
    "Do not say what a fact indicates or connect it to a story unless asked"
)
# Added Sept 24, 2026 after the 0a-in-user-message acceptance run: source
# leaks ("According to the About Matt block"), paraphrased certifications,
# and French stated without its level.
_RULE_0A_NO_SOURCE = (
    "Never tell the visitor where a fact comes from. State it as a fact about Matt."
)
_RULE_0A_CERTS_EXACT = (
    "Quote each certification exactly as written, including its dates. "
    "None is current."
)
_RULE_0A_LANGUAGE_LEVEL = (
    "When stating a language, state its level in the same sentence."
)
# Opening no longer names the "About Matt" block (source-leak fix).
_RULE_0A_OPENING = (
    "The facts about Matt above are accurate; cite them directly and verbatim."
)
# Clause 1 narrowed Sept 25, 2026 (Phase 1 probe): "answer from these facts
# only" applies to questions about a fact about Matt, not to story answers.
_RULE_0A_FACTS_ONLY = (
    "When the question is about a fact about Matt, answer from these facts only."
)
# Removed Sept 25, 2026: the unscoped clause 1, and the no-note-wording
# clause (the AIU note in data/matt_profile.json is now neutral, so Agy
# may quote it). Asserted absent from both messages.
_RULE_0A_REMOVED = [
    "Answer from these facts only.",
    "Do not repeat requirement or eligibility wording from an education note.",
]
# MATTGPT-250 item 4: 0a tells Agy to put a category marker on its own line
# before the closer; post-processing strips it and the Sources fact row
# renders one card per category.
_RULE_0A_CATEGORY_MARKERS = [
    "[[profile:certifications]]",
    "[[profile:education]]",
    "[[profile:languages]]",
]
# Placement per mock #3b: markers sit on their own line before the closer.
_RULE_0A_MARKER_PLACEMENT = "on its own line before the closing line"
_RULE_0A_NEW_MARKERS = [
    _RULE_0A_OPENING,
    _RULE_0A_NO_SOURCE,
    _RULE_0A_CERTS_EXACT,
    _RULE_0A_LANGUAGE_LEVEL,
    _RULE_0A_FACTS_ONLY,
    *_RULE_0A_CATEGORY_MARKERS,
    _RULE_0A_MARKER_PLACEMENT,
]
_RULE_0B_MARKER = "Nothing I know about Matt covers that"
# New at 9d5f575: for absent categories, Agy must not pad the honest gap
# with story evidence.
_RULE_0B_REPLY_ONLY = "Reply with that sentence only"

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
    return _capture_agy_message(real_stories, "system")


@pytest.fixture
def captured_agy_user_message(real_stories):
    return _capture_agy_message(real_stories, "user")


def _capture_agy_message(real_stories, role):
    """Runs rag_answer with semantic_search mocked (happy path,
    profile_facts set) and openai.OpenAI patched globally to return a
    fake client. After rag_answer completes, searches
    create.call_args_list for the call whose system message contains
    the Agy persona anchor. Returns that call's message for `role`
    ("system" or "user").

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
    matching_role_messages: list[str] = []
    for call in fake_openai.chat.completions.create.call_args_list:
        messages = call.kwargs.get("messages", [])
        system_msgs = [
            m.get("content", "") for m in messages if m.get("role") == "system"
        ]
        role_msgs = [m.get("content", "") for m in messages if m.get("role") == role]
        for content in system_msgs:
            if _AGY_ANCHOR in content:
                matching_system_messages.append(content)
                matching_role_messages.append("\n".join(role_msgs))

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
    return matching_role_messages[0]


# ---------------------------------------------------------------------------
# Class C: rules 0a and 0b appear in the captured Agy system message
# ---------------------------------------------------------------------------


class TestRule0aInCapturedUserMessage:
    """Rule 0a is also carried in the Agy user message, after the
    question. The system-message copy (asserted below) stays."""

    def test_rule_0a_clauses_present_in_user_message_after_question(
        self, captured_agy_user_message
    ):
        question_pos = captured_agy_user_message.find(_JPMORGAN_QUERY)
        assert question_pos >= 0, (
            f"question {_JPMORGAN_QUERY!r} not in captured Agy user message. "
            f"Head: {captured_agy_user_message[:600]!r}"
        )
        for clause in (_RULE_0A_NO_STORY_CONNECT, _RULE_0A_NO_INFERENCE):
            clause_pos = captured_agy_user_message.find(clause)
            assert clause_pos > question_pos, (
                f"rule 0a clause {clause!r} not found after the question in "
                f"captured Agy user message (clause at {clause_pos}, "
                f"question at {question_pos}). Head: "
                f"{captured_agy_user_message[:600]!r}"
            )

    @pytest.mark.parametrize("marker", _RULE_0A_NEW_MARKERS)
    def test_rule_0a_new_marker_present_in_user_message_after_question(
        self, captured_agy_user_message, marker
    ):
        question_pos = captured_agy_user_message.find(_JPMORGAN_QUERY)
        marker_pos = captured_agy_user_message.find(marker)
        assert question_pos >= 0 and marker_pos > question_pos, (
            f"rule 0a marker {marker!r} not found after the question in "
            f"captured Agy user message (marker at {marker_pos}, question "
            f"at {question_pos})."
        )

    @pytest.mark.parametrize("removed", _RULE_0A_REMOVED)
    def test_rule_0a_removed_text_absent_from_user_message(
        self, captured_agy_user_message, removed
    ):
        assert (
            removed not in captured_agy_user_message
        ), f"removed rule 0a text {removed!r} still in captured Agy user message"


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

    def test_rule_0a_no_story_connect_clause_present_in_system_message(
        self, captured_agy_system_message
    ):
        """0a addition at 9d5f575: Agy answers from the block only and
        does not join a fact to a story unless asked. Blocks the class
        of over-inference PoC 1 caught ('AWS Launchpad Champion
        reflecting his role in leading cloud enablement programs')."""
        assert _RULE_0A_NO_STORY_CONNECT in captured_agy_system_message, (
            f"rule 0a no-story-connect clause {_RULE_0A_NO_STORY_CONNECT!r} "
            f"not found in captured Agy system message. Head: "
            f"{captured_agy_system_message[:600]!r}"
        )

    @pytest.mark.parametrize("marker", _RULE_0A_NEW_MARKERS)
    def test_rule_0a_new_marker_present_in_system_message(
        self, captured_agy_system_message, marker
    ):
        assert marker in captured_agy_system_message, (
            f"rule 0a marker {marker!r} not found in captured Agy system "
            f"message. Head: {captured_agy_system_message[:600]!r}"
        )

    @pytest.mark.parametrize("removed", _RULE_0A_REMOVED)
    def test_rule_0a_removed_text_absent_from_system_message(
        self, captured_agy_system_message, removed
    ):
        assert (
            removed not in captured_agy_system_message
        ), f"removed rule 0a text {removed!r} still in captured Agy system message"

    def test_rule_0b_reply_only_clause_present_in_system_message(
        self, captured_agy_system_message
    ):
        """0b addition at 9d5f575: for absent categories, Agy replies
        with the honest-gap sentence only and does not pad with story
        evidence. Blocks the SAP-style three-paragraph pad on 'no'
        answers (see MATTGPT-251)."""
        assert _RULE_0B_REPLY_ONLY in captured_agy_system_message, (
            f"rule 0b reply-only clause {_RULE_0B_REPLY_ONLY!r} not "
            f"found in captured Agy system message. Head: "
            f"{captured_agy_system_message[:600]!r}"
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
