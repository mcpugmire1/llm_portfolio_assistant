"""MATTGPT-250 Red: post-processing additions in _generate_agy_response.

Class E: number_patterns bolds scale units. Three inputs run through
  _generate_agy_response with the LLM output mocked; assertions inspect
  the post-processed string.
    E1: pre-bolded "**16 weeks**" -- must survive intact, no split.
    E2: pre-bolded "**150+ practitioners**" -- must survive intact,
        no split.
    E3: unbolded "150 professionals" -- must bold on Green (word
        "professionals" not in current pattern list).

Class F: META_COMMENTARY_REGEX_PATTERNS strip additions. Each input is
  one verbatim observed sentence followed by a benign neighbor. The
  observed sentence must be stripped; the neighbor must survive
  (F6 rule: neighbor survives in every F case, folded into each
  assertion pair).

Class S: _extract_profile_markers strips [[profile:*]] markers and returns
  the known categories (MATTGPT-250 item 4).

Every E/F test uses _run_agy_with_llm_text so the whole post-processing
pipeline runs. No pattern-in-list checks.
"""

import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from ui.pages.ask_mattgpt import backend_service as bs
from utils.corpus_loader import load_stories

logging.getLogger("streamlit").setLevel(logging.ERROR)


_NEIGHBOR = "The rollout finished on schedule."


# ---------------------------------------------------------------------------
# Shared fixture: run _generate_agy_response with a controlled LLM output
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real_story():
    """First story from the corpus. Satisfies _generate_agy_response's
    story-context builder; LLM output is mocked, so the story choice
    does not affect assertions."""
    return load_stories("echo_star_stories_nlp.jsonl")[0]


def _run_agy_with_llm_text(llm_text: str, real_story: dict) -> str:
    """Run _generate_agy_response with openai.OpenAI patched to return
    the given text as completion content. Returns the post-processed
    response string.

    Environment variables satisfy the OpenAI() constructor path before
    the mock intercepts the actual construction.
    """
    fake_completion = MagicMock()
    fake_completion.choices = [MagicMock()]
    fake_completion.choices[0].message.content = llm_text
    fake_openai = MagicMock()
    fake_openai.chat.completions.create.return_value = fake_completion

    env = {
        "OPENAI_API_KEY": "test-key",
        "OPENAI_PROJECT_ID": "test-proj",
        "OPENAI_ORG_ID": "test-org",
    }

    with (
        patch.dict(os.environ, env, clear=False),
        patch("openai.OpenAI", return_value=fake_openai),
        patch.object(bs, "DEBUG", False),
    ):
        return bs._generate_agy_response(
            question="What scale of teams has Matt led?",
            ranked_stories=[real_story],
            answer_context="fallback context (unused when LLM call succeeds)",
        )


# ---------------------------------------------------------------------------
# Class E: number_patterns coverage
# ---------------------------------------------------------------------------


class TestNumberPatternsBoldScaleUnits:
    def test_e1_sixteen_weeks_survives_prebolding_no_split(self, real_story):
        """LLM already bolded '16 weeks'. Current regex rejects the '1'
        start via lookbehind, restarts at '6', backs off the trailing
        's' to satisfy the closing lookahead, and produces
        '**1**6 week**s**'. Green must not split it."""
        llm_text = "The pilot ran **16 weeks** end to end."
        result = _run_agy_with_llm_text(llm_text, real_story)
        assert "**16 weeks**" in result, (
            f"'**16 weeks**' not present in post-processed result. "
            f"Result: {result!r}"
        )
        assert "**1**6" not in result, (
            f"malformed split '**1**6' found in result -- number pattern "
            f"broke '16' apart. Result: {result!r}"
        )

    def test_e2_one_fifty_plus_practitioners_survives_prebolding_no_split(
        self, real_story
    ):
        """Same shape as E1 for '150+ practitioners': expected Red result
        is '**1**50+ practitioner**s**'."""
        llm_text = "The center grew to **150+ practitioners** in two years."
        result = _run_agy_with_llm_text(llm_text, real_story)
        assert "**150+ practitioners**" in result, (
            f"'**150+ practitioners**' not present in post-processed "
            f"result. Result: {result!r}"
        )
        assert "**1**50" not in result, (
            f"malformed split '**1**50' found in result -- number pattern "
            f"broke '150' apart. Result: {result!r}"
        )

    def test_e3_one_fifty_professionals_gets_bolded(self, real_story):
        llm_text = "scaling it from 0 to over 150 professionals."
        result = _run_agy_with_llm_text(llm_text, real_story)
        assert "**150 professionals**" in result, (
            f"'**150 professionals**' not present in post-processed "
            f"result. Result: {result!r}"
        )

    def test_e4_pre_bolded_percent_plus_stays_unchanged(self, real_story):
        """LLM pre-bolds '**40%+**'. The current number_patterns lookbehind
        `(?<!\\*\\*)` rejects the '4' start (chars before are '**') but the
        `\\d+%\\+?` alternative can start at '0' (char before is '4', not
        '**'), match '0%' by backing off '+' to satisfy the closing
        `(?!\\*\\*)`, and emit '**4**0%**+**' (the band-aid then rejoins
        to '**40%**+**', still broken because '+' escapes the bold).
        Green must not touch a pre-bolded percent+plus phrase."""
        llm_text = "Adoption reached **40%+** last quarter."
        result = _run_agy_with_llm_text(llm_text, real_story)
        assert "**40%+**" in result, (
            f"'**40%+**' not present in post-processed result. " f"Result: {result!r}"
        )
        assert "**4**0" not in result, (
            f"malformed split '**4**0' found in result -- number pattern "
            f"broke '40' apart. Result: {result!r}"
        )


# ---------------------------------------------------------------------------
# Class F: META_COMMENTARY_REGEX_PATTERNS strip additions
# ---------------------------------------------------------------------------


class TestMetaCommentaryStripAdditions:
    """Each test feeds one verbatim observed sentence plus the neighbor
    sentence. The observed sentence must be absent from post-processed
    output; the neighbor must survive (F6: neighbor survives in every
    F case, folded into each test's assertion pair)."""

    def _assert_stripped_and_neighbor_survives(
        self, observed: str, real_story: dict
    ) -> None:
        llm_text = f"{observed} {_NEIGHBOR}"
        result = _run_agy_with_llm_text(llm_text, real_story)
        assert observed not in result, (
            f"observed sentence still present after post-processing. "
            f"Observed: {observed!r}. Result: {result!r}"
        )
        assert _NEIGHBOR in result, (
            f"neighbor sentence {_NEIGHBOR!r} did not survive "
            f"post-processing -- strip regex over-matched. "
            f"Observed: {observed!r}. Result: {result!r}"
        )

    def test_f1_demonstrates_a_pattern_and_is_evident_stripped(self, real_story):
        observed = (
            "His work consistently demonstrates a pattern of impact "
            "across industries, from financial services to "
            "telecommunications, and his readiness to tackle senior "
            "leadership roles in platform engineering and enterprise "
            "modernization is evident."
        )
        self._assert_stripped_and_neighbor_survives(observed, real_story)

    def test_f2_showcases_his_stripped(self, real_story):
        observed = (
            "This project showcases his commitment to clean architecture "
            "and maintainability, which are essential principles in "
            "open-source contributions."
        )
        self._assert_stripped_and_neighbor_survives(observed, real_story)

    def test_f3_these_experiences_highlight_matts_stripped(self, real_story):
        observed = (
            "These experiences highlight Matt's involvement in "
            "modernizing mainframe systems."
        )
        self._assert_stripped_and_neighbor_survives(observed, real_story)

    def test_f4_is_evident_sap_sentence_stripped(self, real_story):
        observed = (
            "While SAP is not mentioned in his stories, Matt's expertise "
            "in integrating complex systems and modernizing legacy "
            "applications is evident across his engagements."
        )
        self._assert_stripped_and_neighbor_survives(observed, real_story)

    def test_f5_highlight_matts_real_estate_sentence_stripped(self, real_story):
        observed = (
            "These engagements highlight Matt's involvement in real "
            "estate-related projects."
        )
        self._assert_stripped_and_neighbor_survives(observed, real_story)

    def test_s9_reflect_his_certifications_sentence_stripped(self, real_story):
        """Observed Sept 25, 2026 (acceptance_0a3): plural "reflect his"
        slips past the singular \\breflects his\\b pattern."""
        observed = (
            "These certifications reflect his engagement with cloud and "
            "database technologies."
        )
        self._assert_stripped_and_neighbor_survives(observed, real_story)


# ---------------------------------------------------------------------------
# Class S: profile category markers (MATTGPT-250 item 4)
# ---------------------------------------------------------------------------
# _extract_profile_markers(text) -> (clean_text, categories). Rule 0a puts
# each marker on its own line before the closer; the extractor removes it,
# returns the category, and leaves no blank-line gap where the line was.

_OPENER = "🐾 Found it!"
_BODY = "Matt holds four certifications."
_CLOSER = "What else can I track down for you?"
_CLEAN = f"{_OPENER}\n\n{_BODY}\n\n{_CLOSER}"


def _with_marker_line(marker: str) -> str:
    return f"{_OPENER}\n\n{_BODY}\n\n{marker}\n\n{_CLOSER}"


def _assert_marker_line_removed(clean_text: str) -> None:
    assert "[[" not in clean_text, f"marker residue left: {clean_text!r}"
    assert (
        "\n\n\n" not in clean_text
    ), f"blank-line gap left where the marker line was: {clean_text!r}"
    assert clean_text == _CLEAN, f"expected {_CLEAN!r}, got {clean_text!r}"


class TestProfileMarkerExtraction:
    @pytest.mark.parametrize(
        "marker, category",
        [
            ("[[profile:certifications]]", "certifications"),
            ("[[profile:education]]", "education"),
            ("[[profile:languages]]", "languages"),
            ("[[profile:location_availability]]", "location_availability"),
        ],
    )
    def test_s1_s3_category_marker_line_stripped_and_category_returned(
        self, marker, category
    ):
        clean_text, categories = bs._extract_profile_markers(_with_marker_line(marker))
        _assert_marker_line_removed(clean_text)
        assert categories == [category]

    @pytest.mark.parametrize("marker", ["[[profile:patents]]", "[[profile-only]]"])
    def test_s5_unknown_marker_line_stripped_no_category(self, marker):
        clean_text, categories = bs._extract_profile_markers(_with_marker_line(marker))
        _assert_marker_line_removed(clean_text)
        assert categories == [], f"unknown marker {marker!r} produced {categories!r}"

    def test_s6_inline_marker_stripped_sentence_intact(self):
        text = (
            f"{_OPENER}\n\nMatt holds four certifications [[profile:certifications]] "
            f"from AWS, SAFe and Oracle.\n\n{_CLOSER}"
        )
        clean_text, categories = bs._extract_profile_markers(text)
        assert clean_text == (
            f"{_OPENER}\n\nMatt holds four certifications from AWS, SAFe and "
            f"Oracle.\n\n{_CLOSER}"
        ), f"sentence not intact: {clean_text!r}"
        assert categories == ["certifications"]

    def test_s7_no_markers_text_unchanged(self):
        text = (
            f"{_OPENER}\n\nMatt holds four certifications:\n\n"
            "  - AWS Certified Solutions Architect - Associate\n"
            "  - SAFe 4 Certified Agilist\n\n"
            f"{_CLOSER}"
        )
        clean_text, categories = bs._extract_profile_markers(text)
        assert clean_text == text, f"unmarked text altered: {clean_text!r}"
        assert categories == []

    @pytest.mark.parametrize("sep", [", ", " "], ids=["comma", "space"])
    @pytest.mark.parametrize("placement", ["after_closer", "own_line"])
    def test_s8_marker_run_removed_with_separators(self, sep, placement):
        """Two markers in a run, separated by a comma or spaces. Observed
        Sept 25, 2026: the LLM put "[[profile:education]], [[profile:languages]]"
        inline after the closer and the comma survived stripping."""
        run = f"[[profile:education]]{sep}[[profile:languages]]"
        if placement == "after_closer":
            text = f"{_OPENER}\n\n{_BODY}\n\n{_CLOSER} {run}"
        else:
            text = f"{_OPENER}\n\n{_BODY}\n\n{run}\n\n{_CLOSER}"
        clean_text, categories = bs._extract_profile_markers(text)
        assert clean_text == _CLEAN, f"expected {_CLEAN!r}, got {clean_text!r}"
        assert not clean_text.rstrip("?").endswith(
            (",", " ", "\t")
        ), f"trailing separator left: {clean_text!r}"
        assert categories == ["education", "languages"]
