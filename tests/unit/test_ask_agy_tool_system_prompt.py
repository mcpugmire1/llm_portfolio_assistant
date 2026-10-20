"""MATTGPT-275: the tool-path system prompt, in the shape lever 2 measured.

build_tool_system_prompt() is the system prompt the lever 2 runs sent
(docs/evidence/MATTGPT-275/lever2_20261007_211535/ on gpt-4o;
docs/evidence/MATTGPT-282/sol_arms_20261011_211830/, arm lever2_sol, on
gpt-6.1-sol): the old pipeline's system prompt for the mode, then the
tool note, then the per-answer instruction block that used to end the user
message. The run gave Matt's opener lines as examples; since MATTGPT-340
the opener picked in code is given word for word instead, as before
1095d2c. Those runs built it by splitting the wrapped user message in
a probe patch; this function builds the same text directly.

These tests pin that composition: the mode's system prompt first and
unchanged, the "**TOOLS:**" note, then build_answer_instructions() with the
picked opener line, the focus angle on standard answers only, and citation
rule 0a when profile facts are present. The parity test holds it to the text
run 2's lever2_sol arm sent for one standard and one synthesis turn
(tests/fixtures/ask_agy_lever2_sol_system_prompts.json, with the inputs that
path received), plus the dash edits arm D of the four-arm dash run measured:
the prompt's own em dashes rewritten by hand and NO_DASH_RULE added, then
COMPARISON_RULE on the line after it (the fixture's "edited" field).
"""

import json
from pathlib import Path

import pytest

from ui.pages.ask_mattgpt.prompts import (
    build_answer_instructions,
    build_system_prompt,
    build_tool_system_prompt,
)

_DNA = "## ZZZ_SENTINEL facts\n- ZZZ career arc\n"
_PROFILE = "Education: ZZZ_PROFILE_FACT"
_OPENERS = ["🐾 ZZZ opener one.", "Got it! 🐾 ZZZ", "🐾 ZZZ opener three..."]
_FOCUS = "ZZZ focus angle."
_DECLINE = "🐾 ZZZ decline line about [topic]."

# The tool note as the lever 2 runs sent it; the opener line as MATTGPT-340
# gives the picked opener.
_TOOL_NOTE = (
    "No stories are preloaded. Call search_stories when the question needs "
    "evidence from Matt's work history. Answer directly from the facts about "
    "Matt above or from the conversation when they already answer it."
)
_OPENING = "🐾 ZZZ picked opener."
_OPENER_LINE = f'Begin with this line, word for word: "{_OPENING}"'


def _prompt(is_synthesis, profile_facts=_PROFILE, focus_angle=_FOCUS, decline_line=""):
    return build_tool_system_prompt(
        is_synthesis=is_synthesis,
        matt_dna=_DNA,
        profile_facts=profile_facts,
        opener_examples=_OPENERS,
        focus_angle=focus_angle,
        decline_line=decline_line,
    )


class TestComposition:
    @pytest.mark.parametrize("is_synthesis", [False, True])
    def test_is_the_mode_prompt_then_the_tool_note_then_the_instructions(
        self, is_synthesis
    ):
        expected = (
            build_system_prompt(
                is_synthesis=is_synthesis, matt_dna=_DNA, profile_facts=_PROFILE
            )
            + "\n\n**TOOLS:** "
            + _TOOL_NOTE
            + "\n\n"
            + build_answer_instructions(
                opening_line=_OPENER_LINE,
                is_synthesis=is_synthesis,
                focus_angle=_FOCUS if not is_synthesis else "",
                profile_facts=_PROFILE,
            )
        )
        assert _prompt(is_synthesis) == expected

    def test_without_profile_facts_there_is_no_rule_0a(self):
        prompt = _prompt(False, profile_facts="")
        assert "**About Matt (attested facts):**" not in prompt
        assert "0a. The facts about Matt above are accurate" not in prompt


class TestOpeners:
    """MATTGPT-340: the opener picked in code, used word for word, in both
    modes; no list of opener lines as examples."""

    @pytest.mark.parametrize("is_synthesis", [False, True])
    def test_the_picked_opener_is_given_word_for_word(self, is_synthesis):
        assert _OPENER_LINE in _prompt(is_synthesis)

    @pytest.mark.parametrize("is_synthesis", [False, True])
    def test_no_opener_lines_are_given_as_examples(self, is_synthesis):
        assert "Examples of how Agy opens" not in _prompt(is_synthesis)

    @pytest.mark.parametrize("is_synthesis", [False, True])
    def test_no_opener_is_given_as_exact_text(self, is_synthesis):
        assert "Start your response with this exact text" not in _prompt(is_synthesis)


class TestModes:
    def test_standard_answers_get_the_standard_mode_and_the_focus_angle(self):
        prompt = _prompt(False)
        assert "## STANDARD MODE" in prompt
        assert "## SYNTHESIS MODE" not in prompt
        assert f"**FOCUS:** {_FOCUS}" in prompt

    def test_standard_mode_does_not_say_go_deep_on_one_story(self):
        # MATTGPT-340 (ADR 061 row 26).
        prompt = _prompt(False)
        assert "This is a specific question." in prompt
        assert "Go deep on the primary story" not in prompt

    def test_synthesis_answers_get_the_synthesis_mode_and_no_focus_angle(self):
        prompt = _prompt(True)
        assert "## SYNTHESIS MODE" in prompt
        assert "## STANDARD MODE" not in prompt
        assert "**FOCUS:**" not in prompt


class TestDeclineLine:
    """MATTGPT-322: the decline line picked in code reaches the model as the
    shape to use if it declines, in both modes, never as exact text."""

    @pytest.mark.parametrize("is_synthesis", [False, True])
    def test_the_decline_line_is_given_as_a_shape(self, is_synthesis):
        prompt = _prompt(is_synthesis, decline_line=_DECLINE)
        assert (
            "**IF YOU DECLINE:** Begin with this line, filling in the topic in your own words: "
            f'"{_DECLINE}"'
        ) in prompt

    def test_no_decline_line_means_no_decline_instruction(self):
        assert "**IF YOU DECLINE:**" not in _prompt(False, decline_line="")


_RUN2 = json.loads(
    (
        Path(__file__).parents[1]
        / "fixtures"
        / "ask_agy_lever2_sol_system_prompts.json"
    ).read_text()
)["turns"]


class TestParityWithRun2:
    @pytest.mark.parametrize(
        "turn",
        _RUN2,
        ids=[
            ("synthesis-" if t["is_synthesis"] else "standard-")
            + t["source"][-6:].replace(" ", "-")
            for t in _RUN2
        ],
    )
    def test_equals_the_system_prompt_run_2_sent(self, turn):
        prompt = build_tool_system_prompt(
            is_synthesis=turn["is_synthesis"],
            matt_dna=turn["matt_dna"],
            profile_facts=turn["profile_facts"],
            opener_examples=turn["opener_examples"],
            focus_angle=turn["focus_angle"],
            decline_line=turn["decline_line"],
        )
        assert prompt == turn["system_prompt"]
