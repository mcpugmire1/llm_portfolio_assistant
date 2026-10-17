"""MATTGPT-250 Red: Ask Agy consumes profile_facts and injects rules 0a/0b.

Class C: citation rules 0a and 0b appear in the captured Agy system message.
Class G: Ask Agy's captured system message contains the four
  certifications and "French (B2, self-assessed)" from data/matt_profile.json,
  positioned before **GROUNDING RULES:**.

Query used: "Tell me about Matt's payments work at JPMorgan" -- baseline
from Stage 1, known-answer path.
"""

import logging
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from services import semantic_router
from ui.pages.ask_mattgpt import backend_service as bs
from utils.corpus_loader import load_stories

logging.getLogger("streamlit").setLevel(logging.ERROR)


# ---------------------------------------------------------------------------
# Constants: markers Green must produce
# ---------------------------------------------------------------------------

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
# MATTGPT-268 (Oct 4, 2026): the category-wide direct-no sentence made CS
# degree answers lead with a no (9/10 with it, 0/10 without;
# probe_268_output/20261004_095649/). Deleting it outright cost PMP its
# certifications marker in 8/20 runs. Scoped to certifications, PMP had 0
# failures in 20 ("does matt have a pmp" and "Does Matt have a PMP?", 10
# each: leading no, all four certifications, marker, no story pivot;
# probe_268_output/20261004_104755/) and CS led with a no in 8/50 on this
# tree (20261004_104606/ 1/10, 20261004_104903/ 3/20, 20261004_105523/ arm a
# 4/20), from the scoped sentence itself (105523: 4/20 with it, 0/20
# without). The category-wide form is asserted
# absent via _RULE_0A_REMOVED; the certifications form present via
# _RULE_0A_NEW_MARKERS.
_RULE_0A_DIRECT_NO = "For a category the profile holds"
_RULE_0A_CERTS_DIRECT_NO = (
    "For certifications, an item not in the list gets a direct no, "
    "followed by what the list does contain."
)
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
    _RULE_0A_DIRECT_NO,
    # MATTGPT-276: answers no longer end with a closer, so markers are not
    # placed relative to one.
    "on its own line before the closing line",
]
# MATTGPT-250 item 4: 0a tells Agy to put a category marker on its own line
# at the end of the response; post-processing strips it and the Sources fact
# row renders one card per category.
_RULE_0A_CATEGORY_MARKERS = [
    "[[profile:certifications]]",
    "[[profile:education]]",
    "[[profile:languages]]",
    "[[profile:location_availability]]",
]
# Placement: markers sit on their own line at the end of the response.
_RULE_0A_MARKER_PLACEMENT = "on its own line at the end of the response"
_RULE_0A_NEW_MARKERS = [
    _RULE_0A_OPENING,
    _RULE_0A_NO_SOURCE,
    _RULE_0A_CERTS_EXACT,
    _RULE_0A_LANGUAGE_LEVEL,
    _RULE_0A_FACTS_ONLY,
    *_RULE_0A_CATEGORY_MARKERS,
    _RULE_0A_MARKER_PLACEMENT,
    _RULE_0A_CERTS_DIRECT_NO,
]
_RULE_0B_MARKER = "decline in first person"
# New at 9d5f575: for absent categories, Agy must not pad the honest gap
# with story evidence. MATTGPT-322: the decline is written in Agy's voice
# (design spec doc 05), opening with the 🐾 and naming what is not on record.
_RULE_0B_REPLY_ONLY = "No guessing, no padding with story evidence, no excess apology"
_RULE_0B_VOICE = [
    "decline in first person, in one or two sentences, the first beginning with 🐾",
    "Name the topic in your own words",
]
# MATTGPT-322: the model can't vary across calls it can't see, so code picks
# one of two decline lines per turn; exactly one reaches the model.
_RULE_0B_DECLINE_LINES = [
    "🐾 I followed that trail and came up empty: Matt's stories don't cover [topic].",
    "🐾 I searched Matt's whole record, and it doesn't mention [topic].",
]
# MATTGPT-322: the fixed sentence came back bare, with no opener; the
# first voiced wording's own phrase ("nothing on record about what was
# asked") became the template every decline repeated; the model ignored
# "Examples to vary" and kept its own line.
_RULE_0B_REMOVED = [
    "Nothing I know about Matt covers that",
    "nothing on record about what was asked",
    "Two examples of the shape, not text to copy",
    "Examples to vary, not text to copy",
]

_GROUNDING_HEADER = "**GROUNDING RULES:**"

_JPMORGAN_QUERY = "Tell me about Matt's payments work at JPMorgan"


# ---------------------------------------------------------------------------
# Shared fixture: capture Ask Agy's system message
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real_stories():
    return load_stories("echo_star_stories_nlp.jsonl")


@pytest.fixture
def captured_agy_system_message(real_stories):
    return _capture_agy_system_message(real_stories)


def _capture_agy_system_message(real_stories):
    """Run agy_answer() with the nonsense rules, router, search and loggers
    faked and the Responses client replaced by a recorder that answers on
    the first call. Returns the system message the model received."""
    requests = []

    def _create(**kwargs):
        requests.append(kwargs)
        final = SimpleNamespace(
            status="completed", output=[], output_text="captured-prompt-test-response"
        )
        return iter([SimpleNamespace(type="response.completed", response=final)])

    client = SimpleNamespace(responses=SimpleNamespace(create=_create))
    mock_st = MagicMock()
    mock_st.session_state = {}
    bs.sync_portfolio_metadata(real_stories)
    with (
        patch.object(bs, "st", mock_st),
        patch.object(bs, "DEBUG", False),
        patch.object(bs, "_openai_client", return_value=client),
        patch.object(bs, "is_nonsense", return_value=None),
        patch.object(semantic_router, "_get_embedding", return_value=[0.0]),
        patch.object(semantic_router, "_get_intent_embeddings", return_value={}),
        patch.object(
            semantic_router,
            "_classify_embedding",
            return_value=(True, 0.6, "zzz-intent", "behavioral"),
        ),
        patch.object(semantic_router, "_log_borderline", MagicMock()),
        patch.object(semantic_router, "_log_router_low_confidence", MagicMock()),
        patch.object(bs, "semantic_search", MagicMock()),
        patch.object(bs, "log_query", MagicMock()),
        patch.object(bs, "log_offdomain", MagicMock()),
    ):
        bs.agy_answer(_JPMORGAN_QUERY, real_stories)
    assert len(requests) == 1, f"expected one model call, got {len(requests)}"
    system = requests[0]["input"][0]
    assert system["role"] == "system"
    return system["content"]


# ---------------------------------------------------------------------------
# Class C: rules 0a and 0b appear in the captured Agy system message
# ---------------------------------------------------------------------------


class TestCitationRulesInCapturedSystemMessage:
    """Rules 0a and 0b appear in the runtime Agy system prompt.

    0a's no-inference clause (state what the block says, do not infer
    capability or meaning) is asserted here. MATTGPT-268 scoped the
    direct-no clause to certifications: the category-wide form is asserted
    absent via _RULE_0A_REMOVED, the certifications form present via
    _RULE_0A_NEW_MARKERS."""

    def test_rule_0a_no_inference_clause_present_in_system_message(
        self, captured_agy_system_message
    ):
        assert _RULE_0A_NO_INFERENCE in captured_agy_system_message, (
            f"rule 0a no-inference clause {_RULE_0A_NO_INFERENCE!r} not "
            f"found in captured Agy system message. Head: "
            f"{captured_agy_system_message[:600]!r}"
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

    @pytest.mark.parametrize("fragment", _RULE_0B_VOICE)
    def test_rule_0b_voice_fragment_present_in_system_message(
        self, captured_agy_system_message, fragment
    ):
        """MATTGPT-322: the decline is one or two first-person sentences,
        opening with the 🐾, naming the topic in the model's own words."""
        assert fragment in captured_agy_system_message, (
            f"rule 0b voice fragment {fragment!r} not found in captured Agy "
            f"system message"
        )

    def test_exactly_one_decline_line_reaches_the_model(
        self, captured_agy_system_message
    ):
        """MATTGPT-322: code picks one decline line per turn; the model gets
        that one, not the list to choose from."""
        present = [
            line
            for line in _RULE_0B_DECLINE_LINES
            if line in captured_agy_system_message
        ]
        assert (
            len(present) == 1
        ), f"decline lines in the Agy system message: {present!r}"

    @pytest.mark.parametrize("removed", _RULE_0B_REMOVED)
    def test_rule_0b_removed_text_absent_from_system_message(
        self, captured_agy_system_message, removed
    ):
        """MATTGPT-322: 'Nothing I know about Matt covers that' overrode the
        opener, so the decline came back bare; 'nothing on record about what
        was asked' became the sentence every decline repeated."""
        assert (
            removed not in captured_agy_system_message
        ), f"removed rule 0b text {removed!r} still in captured Agy system message"


# ---------------------------------------------------------------------------
# Class G: Ask Agy consumes profile_facts into the Agy system message
# ---------------------------------------------------------------------------


class TestAskAgyConsumesProfileFacts:
    """agy_answer() puts the profile facts from data/matt_profile.json
    (load_matt_profile()) into the system message the model receives.

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


# ---------------------------------------------------------------------------
# MATTGPT-276: no random closer. Each closer was an offer ("There's more to
# this story if you're curious") picked by random.choice, inviting a
# follow-up the pipeline could not resolve.
# ---------------------------------------------------------------------------

_CLOSER_USER_INSTRUCTION = "End your response with this exact text"
_CLOSER_SYSTEM_INSTRUCTION = "End with the closing provided"


class TestNoCloser:
    def test_system_message_has_no_closer_instruction(
        self, captured_agy_system_message
    ):
        assert _CLOSER_SYSTEM_INSTRUCTION not in captured_agy_system_message

    def test_synthesis_system_prompt_has_no_closer_instruction(self):
        from ui.pages.ask_mattgpt.prompts import build_system_prompt

        assert _CLOSER_SYSTEM_INSTRUCTION not in build_system_prompt(True, "DNA")
