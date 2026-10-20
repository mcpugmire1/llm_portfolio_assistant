"""MATTGPT-275: the no-dash writing rule, and no dashes in the prompts or
the fixed text visitors read.

NO_DASH_RULE (config.constants) is the line measured on Ask Agy's answers
(probes/output/MATTGPT-275/dash_arms_20261014_071542/: answers with a dash
went from 42 of 55 to 4 of 55, every one left a number range). It reaches
Ask Agy through build_answer_instructions(), so both the standard and
synthesis system prompts.

Role Match's prompts carry no rule: on gpt-4o its model-written text had no
dash with or without one (probes/output/MATTGPT-275/role_match_dashes_*/,
0 of 165 rows before, 0 of 167 after). Its source_text verbatim rule stays
as it is, since required and preferred rows show the JD's own words.

The prompts the models receive, and the source files that hold them,
contain no em or en dash of their own. Nor does the fixed text visitors read:
the rate-limit fallback (the colon copy Explore Stories and Role Match
already show), the suggestion chips, the source chip labels, the key points
"Scope:" line, the "Also relevant:" list, the Why Agy? paragraphs and the
cross-industry landing's call to action.
"""

import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config import constants
from services import jd_assessor
from ui.components import why_agy_dialog
from ui.pages.ask_mattgpt import backend_service as bs
from ui.pages.ask_mattgpt.prompts import (
    build_answer_instructions,
    build_tool_system_prompt,
)
from utils import formatting, ui_helpers

EM, EN = "\u2014", "\u2013"
REPO = Path(__file__).resolve().parents[2]

LINE = (
    "Don't use em dashes or en dashes; use a comma, a colon, parentheses or a "
    "separate sentence, whichever fits."
)
VERBATIM_SOURCE_TEXT = (
    "Copy source_text as the entire JD bullet or sentence, verbatim and "
    "complete. Do not shorten, summarize, or truncate."
)

EXTRACTION_PROMPTS = {
    "required": jd_assessor._REQUIRED_EXTRACTION_PROMPT,
    "preferred": jd_assessor._PREFERRED_EXTRACTION_PROMPT,
    "implicit": jd_assessor._IMPLICIT_EXTRACTION_PROMPT,
}


def _corpus_dna():
    stories = [
        json.loads(line)
        for line in (REPO / "echo_star_stories_nlp.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    return bs.generate_dynamic_dna(stories, bs.get_known_clients(stories))


def _agy_prompt(is_synthesis):
    return build_tool_system_prompt(
        is_synthesis=is_synthesis,
        matt_dna=_corpus_dna(),
        profile_facts=jd_assessor.load_matt_profile(),
        opening=(bs.SYNTHESIS_OPENERS if is_synthesis else bs.STANDARD_OPENERS)[0],
        focus_angle="",
    )


class TestTheSharedRule:
    def test_the_rule_is_the_measured_line(self):
        assert getattr(constants, "NO_DASH_RULE", None) == LINE


class TestAskAgy:
    @pytest.mark.parametrize(
        "is_synthesis", [False, True], ids=["standard", "synthesis"]
    )
    def test_the_system_prompt_carries_the_rule_once(self, is_synthesis):
        assert _agy_prompt(is_synthesis).count(LINE) == 1

    def test_the_answer_instructions_carry_the_rule(self):
        assert LINE in build_answer_instructions(opening_line="ZZZ", is_synthesis=False)

    @pytest.mark.parametrize(
        "is_synthesis", [False, True], ids=["standard", "synthesis"]
    )
    def test_the_system_prompt_has_no_dash_of_its_own(self, is_synthesis):
        prompt = _agy_prompt(is_synthesis)
        assert (prompt.count(EM), prompt.count(EN)) == (0, 0)


class TestRoleMatch:
    @pytest.mark.parametrize("section", ["required", "preferred"])
    def test_the_source_text_verbatim_rule_is_unchanged(self, section):
        assert VERBATIM_SOURCE_TEXT in EXTRACTION_PROMPTS[section]

    @pytest.mark.parametrize(
        "name", ["assessment", *EXTRACTION_PROMPTS], ids=lambda n: n
    )
    def test_the_prompt_has_no_dash_of_its_own(self, name):
        prompt = (
            jd_assessor.build_assessment_prompt()
            if name == "assessment"
            else EXTRACTION_PROMPTS[name]
        )
        assert (prompt.count(EM), prompt.count(EN)) == (0, 0)


class TestSourceFiles:
    @pytest.mark.parametrize(
        "path",
        [
            "services/jd_assessor.py",
            "ui/pages/ask_mattgpt/prompts.py",
            "config/constants.py",
            "ui/pages/ask_mattgpt/backend_service.py",
            "utils/ui_helpers.py",
            "utils/formatting.py",
            "ui/components/why_agy_dialog.py",
            "ui/pages/cross_industry_landing.py",
        ],
    )
    def test_the_file_has_no_literal_dash(self, path):
        data = (REPO / path).read_bytes()
        assert (data.count(EM.encode()), data.count(EN.encode())) == (0, 0)


_SOURCE = [{"id": "zzz-1", "client": "ZZZ Client", "title": "ZZZ Title"}]


def _no_dash(text):
    return (text.count(EM), text.count(EN)) == (0, 0)


class TestVisitorText:
    def test_every_rate_limit_fallback_is_the_colon_copy(self):
        src = (REPO / "ui/pages/ask_mattgpt/backend_service.py").read_text(
            encoding="utf-8"
        )
        copies = re.findall(r'"\U0001f43e I need a quick breather[^"]*"', src)
        assert copies
        assert set(copies) <= {
            '"\U0001f43e I need a quick breather: please try again in a moment!"',
            '"\U0001f43e I need a quick breather: try again in about 15 seconds!"',
        }
        assert all(_no_dash(c) for c in copies)

    @pytest.mark.parametrize(
        "chips", ["RULE_CHIPS", "PERSONAL_CHIPS", "OUT_OF_SCOPE_CHIPS"]
    )
    def test_suggestion_chip_labels_and_questions_have_no_dash(self, chips):
        for label, question in getattr(ui_helpers, chips):
            assert _no_dash(label) and _no_dash(question), (label, question)

    def test_static_source_badges_have_no_dash(self):
        mock_st = MagicMock()
        mock_st.session_state = {}
        with patch.object(ui_helpers, "st", mock_st):
            ui_helpers.render_sources_badges_static(_SOURCE)
        shown = " ".join(str(c) for c in mock_st.markdown.call_args_list)
        assert "ZZZ Client" in shown and "ZZZ Title" in shown
        assert _no_dash(shown)

    def test_source_chip_labels_have_no_dash(self):
        mock_st = MagicMock()
        mock_st.session_state = {}
        mock_st.button.return_value = False
        mock_st.container.return_value.columns.side_effect = lambda n: [
            MagicMock() for _ in range(n)
        ]
        with patch.object(ui_helpers, "st", mock_st):
            ui_helpers.render_sources_chips(_SOURCE, stories=[])
        labels = [c.args[0] for c in mock_st.button.call_args_list]
        assert len(labels) == 1
        assert "ZZZ Client" in labels[0] and "ZZZ Title" in labels[0]
        assert _no_dash(labels[0])

    def test_the_key_points_scope_line_has_no_dash(self):
        scope = formatting._format_key_points(_SOURCE[0]).splitlines()[0]
        assert scope.startswith("- **Scope:** ")
        assert "ZZZ Client" in scope and "ZZZ Title" in scope
        assert _no_dash(scope)

    def test_the_scope_line_without_a_client_is_the_title_alone(self):
        scope = formatting._format_key_points(
            {"title": "ZZZ Title", "client": ""}
        ).splitlines()[0]
        assert scope == "- **Scope:** ZZZ Title"

    def test_the_why_agy_paragraphs_have_no_dash(self):
        assert _no_dash(why_agy_dialog._BODY_HTML)

    def test_the_cross_industry_call_to_action_has_no_dash(self):
        src = (REPO / "ui/pages/cross_industry_landing.py").read_text(encoding="utf-8")
        ctas = re.findall(r'<p class="cta-subtext">(.*?)</p>', src)
        assert len(ctas) == 1
        assert "cross-industry transformation experience" in ctas[0]
        assert _no_dash(ctas[0])
