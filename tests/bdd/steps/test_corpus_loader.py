"""Step definitions for corpus_loader.feature."""

import json

import pytest
from pytest_bdd import given, scenarios, then, when

from utils.corpus_loader import load_stories, normalize_story
from utils.scoring import _keyword_score_for_story

scenarios("../features/corpus_loader.feature")


@pytest.fixture
def ctx():
    return {}


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------


@given("the corpus loader module is importable without Streamlit side effects")
def _importable():
    pass  # module-level import above is the assertion


# ---------------------------------------------------------------------------
# normalize_story: story dict fixtures
# ---------------------------------------------------------------------------


@given('a story dict with public_tags set to the string "cloud,aws"')
def _story_public_tags_string(ctx):
    ctx["story"] = {"id": "s1", "public_tags": "cloud,aws"}


@given('a story dict with public_tags set to the list ["cloud", "aws"]')
def _story_public_tags_list(ctx):
    ctx["story"] = {"id": "s1", "public_tags": ["cloud", "aws"]}


@given('a story dict with Performance set to the string "Reduced latency by 60%"')
def _story_performance_string(ctx):
    ctx["story"] = {"id": "s1", "Performance": "Reduced latency by 60%"}


@given("a story dict with no Competencies key")
def _story_no_competencies(ctx):
    ctx["story"] = {"id": "s1", "Title": "Test Story"}


# ---------------------------------------------------------------------------
# normalize_story: When / Then
# ---------------------------------------------------------------------------


@when("normalize_story processes the story")
def _when_normalize_story(ctx):
    ctx["result"] = normalize_story(ctx["story"])


@then('the story\'s public_tags is the list ["cloud", "aws"]')
def _then_public_tags_list(ctx):
    assert ctx["result"]["public_tags"] == ["cloud", "aws"]


@then('the story\'s Performance is the list ["Reduced latency by 60%"]')
def _then_performance_list(ctx):
    assert ctx["result"]["Performance"] == ["Reduced latency by 60%"]


@then("the story has no Competencies key")
def _then_no_competencies(ctx):
    assert "Competencies" not in ctx["result"]


# ---------------------------------------------------------------------------
# load_stories: JSONL file fixtures
# ---------------------------------------------------------------------------


@given(
    "a JSONL file containing one story with no id field", target_fixture="jsonl_path"
)
def _jsonl_no_id(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text(json.dumps({"Title": "Test"}) + "\n")
    return str(p)


@given(
    'a JSONL file containing one story with id set to ""', target_fixture="jsonl_path"
)
def _jsonl_empty_id(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text(json.dumps({"id": "", "Title": "Test"}) + "\n")
    return str(p)


@given(
    "a JSONL file containing one story with id set to 0", target_fixture="jsonl_path"
)
def _jsonl_zero_id(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text(json.dumps({"id": 0, "Title": "Test"}) + "\n")
    return str(p)


@given(
    'a JSONL file containing one story with id set to "  story-1  "',
    target_fixture="jsonl_path",
)
def _jsonl_whitespace_id(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text(json.dumps({"id": "  story-1  ", "Title": "Test"}) + "\n")
    return str(p)


@given(
    'a JSONL file containing one story with id set to "story-1"',
    target_fixture="jsonl_path",
)
def _jsonl_valid_id(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text(json.dumps({"id": "story-1", "Title": "Test"}) + "\n")
    return str(p)


@given(
    "a JSONL file containing a line that is not valid JSON", target_fixture="jsonl_path"
)
def _jsonl_malformed(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text("not valid json\n")
    return str(p)


@given(
    'a JSONL file containing one empty line followed by one story with id "story-1"',
    target_fixture="jsonl_path",
)
def _jsonl_empty_line(tmp_path):
    p = tmp_path / "stories.jsonl"
    p.write_text("\n" + json.dumps({"id": "story-1", "Title": "Test"}) + "\n")
    return str(p)


# ---------------------------------------------------------------------------
# load_stories: When / Then
# ---------------------------------------------------------------------------


@when("load_stories processes the file")
def _when_load_stories(ctx, jsonl_path):
    ctx["result"] = load_stories(jsonl_path)


@when("load_stories attempts to process the file")
def _when_load_stories_raises(ctx, jsonl_path):
    try:
        load_stories(jsonl_path)
        ctx["raised"] = None
    except json.JSONDecodeError as exc:
        ctx["raised"] = exc


@then("the result is an empty list")
def _then_empty_list(ctx):
    assert ctx["result"] == []


@then('the story\'s id equals "story-1"')
def _then_id_stripped(ctx):
    assert ctx["result"][0]["id"] == "story-1"


@then("the result contains exactly 1 story")
def _then_one_story(ctx):
    assert len(ctx["result"]) == 1


@then("a json.JSONDecodeError is raised")
def _then_json_decode_error(ctx):
    assert isinstance(ctx["raised"], json.JSONDecodeError)


# ---------------------------------------------------------------------------
# Scenario 12: normalization enables public_tags tokens to reach the scorer
# ---------------------------------------------------------------------------


@given(
    'a story where public_tags is the raw string "cloud" and no other field contains "cloud"'
)
def _story_raw_public_tags(ctx, tmp_path):
    raw = {"id": "scorer-1", "Title": "Test Story", "public_tags": "cloud"}
    ctx["raw_story"] = raw
    p = tmp_path / "scorer.jsonl"
    p.write_text(json.dumps(raw) + "\n")
    ctx["scorer_jsonl_path"] = str(p)


@when('_keyword_score_for_story runs with query "cloud" on the unnormalized story')
def _when_score_unnormalized(ctx):
    ctx["score_raw"] = _keyword_score_for_story(ctx["raw_story"], "cloud")


@then("the keyword score equals 0.0")
def _then_score_zero(ctx):
    assert ctx["score_raw"] == 0.0


@when(
    'load_stories normalizes the story and _keyword_score_for_story runs with query "cloud"'
)
def _when_score_normalized(ctx):
    stories = load_stories(ctx["scorer_jsonl_path"])
    assert stories, "load_stories returned no stories -- normalization did not run"
    ctx["score_normalized"] = _keyword_score_for_story(stories[0], "cloud")


@then("the keyword score equals 0.5")
def _then_score_half(ctx):
    assert ctx["score_normalized"] == 0.5
