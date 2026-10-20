"""
BDD step definitions for agy_voice.feature (MATTGPT-345).

The voice rules run on answers a live acceptance run recorded
(tests/fixtures/agy_voice_answers.json), not on new model calls: no cost,
the same verdict on every run, and every recorded answer checked. The
fixture is as current as the last prompt ticket's acceptance run, which
refreshes it with scripts/build_agy_voice_fixture.py.

Each Then step checks every selected answer and names the ones that break
the rule.
"""

import json
import re
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenario, scenarios, then, when

from utils.client_utils import is_generic_client
from utils.corpus_loader import load_stories

FEATURE = "../features/agy_voice.feature"
FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "agy_voice_answers.json"
PAW = "🐾"

# Answers with no opener and no paw, tracked on MATTGPT-345.
XFAIL_345 = pytest.mark.xfail(
    reason="MATTGPT-345 baseline: 7 of 98 non-declined answers have no opener "
    "and no paw (9534aea)",
    strict=True,
)


@XFAIL_345
@scenario(FEATURE, "Exactly one paw emoji per response")
def test_exactly_one_paw_emoji_per_response():
    pass


@XFAIL_345
@scenario(FEATURE, "Paw emoji present in all response types")
def test_paw_emoji_present_in_all_response_types():
    pass


scenarios(FEATURE)


def _label(answer):
    return f"{answer['case']} t{answer['turn']} r{answer['run']}"


def _phrase(pattern):
    return re.compile(rf"(?<!\w){re.escape(pattern)}(?!\w)", re.IGNORECASE)


def _opening_line(text):
    return next((line for line in text.splitlines() if line.strip()), "")


def _offenders(answers, broken):
    """Labels of the answers for which broken(answer_md) is true."""
    return [_label(a) for a in answers if broken(a["answer_md"])]


@pytest.fixture
def ctx():
    return {}


@given("the answers recorded by the latest live acceptance run")
def recorded_answers(ctx):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    ctx["all"] = data["answers"]
    assert ctx["all"], f"{FIXTURE} holds no answers"


@when("I read every recorded answer")
def every_answer(ctx):
    ctx["answers"] = ctx["all"]


@when("I read every recorded first-turn answer")
def first_turn_answers(ctx):
    ctx["answers"] = [a for a in ctx["all"] if a["turn"] == 1]
    assert ctx["answers"]


@when("I read every recorded synthesis answer")
def synthesis_answers(ctx):
    ctx["answers"] = [a for a in ctx["all"] if a["intent_family"] == "synthesis"]
    assert ctx["answers"]


@when("I read every recorded answer that names a client")
def client_answers(ctx):
    clients = {
        s["Client"]
        for s in load_stories("echo_star_stories_nlp.jsonl")
        if s.get("Client") and not is_generic_client(s["Client"])
    }
    named = [_phrase(c) for c in clients]
    ctx["answers"] = [
        a for a in ctx["all"] if any(p.search(a["answer_md"]) for p in named)
    ]
    assert ctx["answers"]


@then(parsers.parse('every answer should refer to "Matt" or "he/his"'))
def refers_to_matt(ctx):
    third = re.compile(r"\b(?:Matt|he|his|him)\b", re.IGNORECASE)
    bad = _offenders(ctx["answers"], lambda t: not third.search(t))
    assert not bad, f"no Matt/he/his: {bad}"


@then("no answer should contain:")
def contains_none(ctx, datatable):
    patterns = [row[0] for row in datatable[1:]]
    found = {
        p: bad
        for p in patterns
        if (bad := _offenders(ctx["answers"], _phrase(p).search))
    }
    assert not found, f"banned patterns: {found}"


@then("no sentence should start with:")
def no_sentence_starts_with(ctx, datatable):
    patterns = [row[0] for row in datatable[1:]]
    found = {}
    for p in patterns:
        start = re.compile(rf"(?:^|[.!?]\s+|\n)\s*\**{re.escape(p)}\b")
        if bad := _offenders(ctx["answers"], start.search):
            found[p] = bad
    assert not found, f"sentence openers: {found}"


@then('no answer should use "we" as a subject pronoun')
def no_we(ctx):
    we = re.compile(
        r"(?:^|[.!?]\s+|\n)\s*We\b|\bWe(?:'re|'ve|'ll)\b"
        r"|\bwe (?:can|found|see|think|have|had|will|are|were|did|built|led)\b"
    )
    bad = _offenders(ctx["answers"], we.search)
    assert not bad, f"'we' as subject: {bad}"


@then("every answer should contain exactly one paw emoji")
def exactly_one_paw(ctx):
    bad = _offenders(ctx["answers"], lambda t: t.count(PAW) != 1)
    assert not bad, f"not exactly one {PAW}: {bad}"


@then("the paw emoji should be in the opening line")
def paw_in_opening_line(ctx):
    bad = _offenders(ctx["answers"], lambda t: PAW not in _opening_line(t))
    assert not bad, f"no {PAW} in the opening line: {bad}"


@then("every answer should start with a line containing the paw emoji")
def starts_with_paw_line(ctx):
    paw_in_opening_line(ctx)


@then("no answer should have an additional paw emoji")
def no_additional_paw(ctx):
    bad = _offenders(ctx["answers"], lambda t: t.count(PAW) > 1)
    assert not bad, f"more than one {PAW}: {bad}"
