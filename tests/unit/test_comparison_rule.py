"""MATTGPT-275: the comparison rule.

COMPARISON_RULE (config.constants) is the line measured on Ask Agy's answers
to "Which was bigger?" after a comparison of Matt's Fiserv and JP Morgan
ACCESS work (probes/output/MATTGPT-275/control_iso_20261015_065005/: 3 of
10 answers passed without it, 10 of 10 with it; the c01 and c12 t1 controls
stayed at 10 of 10). It reaches Ask Agy through build_answer_instructions(),
on the line after NO_DASH_RULE, so both the standard and synthesis system
prompts.
"""

import pytest

from config import constants
from ui.pages.ask_mattgpt.prompts import (
    build_answer_instructions,
    build_tool_system_prompt,
)

LINE = (
    "When asked which of two things was bigger or better, compare only on a "
    "measure the stories give for both, in the same units. If their figures "
    "can't settle it (an open-ended figure against an exact one, or two "
    "different measures), say the stories don't establish which is larger."
)


def _agy_prompt(is_synthesis):
    return build_tool_system_prompt(
        is_synthesis=is_synthesis,
        matt_dna="## ZZZ_SENTINEL facts\n- ZZZ career arc\n",
        profile_facts="Education: ZZZ_PROFILE_FACT",
        opening="🐾 ZZZ opener one.",
        focus_angle="",
    )


class TestTheRule:
    def test_the_rule_is_the_measured_line(self):
        assert getattr(constants, "COMPARISON_RULE", None) == LINE


class TestAskAgy:
    @pytest.mark.parametrize(
        "is_synthesis", [False, True], ids=["standard", "synthesis"]
    )
    def test_the_system_prompt_carries_the_rule_once(self, is_synthesis):
        assert _agy_prompt(is_synthesis).count(LINE) == 1

    def test_the_rule_is_on_the_line_after_the_dash_rule(self):
        instructions = build_answer_instructions(opening_line="ZZZ", is_synthesis=False)
        assert constants.NO_DASH_RULE + "\n" + LINE in instructions
