"""MATTGPT-302: Role Match's calls move to gpt-6.1-sol.

DEFAULT_CHAT_MODEL (config.constants) is the one chat model constant Role
Match reads; ASK_ANSWER_MODEL stays Ask Agy's own. gpt-6.1-sol rejects
temperature=0.0 with a 400 ("Only the default (1) value is supported."), so
the four Role Match calls send reasoning_effort instead
(docs/evidence/MATTGPT-302/precheck_20261020_160414/,
temperature_20261020_172520/).

The client caps each read at ROLE_MATCH_READ_TIMEOUT_S and retries
ROLE_MATCH_MAX_RETRIES times. The slowest call in the live comparison took
24.6 s (live_20261020_172609/).
"""

import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest

from config import constants
from services import jd_assessor

REPO = Path(__file__).resolve().parents[2]


def _client():
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps({})))]
    )
    return client


_STORY = {
    "title": "ZZZ Title",
    "client": "ZZZ Client",
    "id": "zzz-1",
    "score": 0.5,
    "5PSummary": "ZZZ summary",
}

_CALLS = {
    "required": lambda c: jd_assessor._call_required(c, "ZZZ JD"),
    "preferred": lambda c: jd_assessor._call_preferred(c, "ZZZ JD"),
    "implicit": lambda c: jd_assessor._call_implicit(c, "ZZZ JD", {}, {}),
    "assess": lambda c: jd_assessor.assess_requirement(c, "ZZZ requirement", [_STORY]),
}


def _kwargs(stage):
    client = _client()
    _CALLS[stage](client)
    return client.chat.completions.create.call_args.kwargs


class TestModelConstants:
    def test_the_shared_chat_model_is_gpt_6_1_sol(self):
        assert constants.DEFAULT_CHAT_MODEL == "gpt-6.1-sol"

    def test_the_shared_reasoning_effort_is_medium(self):
        assert getattr(constants, "DEFAULT_REASONING_EFFORT", None) == "medium"

    def test_the_classification_model_constant_is_gone(self):
        assert not hasattr(constants, "DEFAULT_CLASSIFICATION_MODEL")

    def test_the_assessment_model_is_the_shared_chat_model(self):
        assert jd_assessor.ASSESSMENT_MODEL == constants.DEFAULT_CHAT_MODEL

    def test_the_assessment_temperature_constant_is_gone(self):
        assert not hasattr(jd_assessor, "ASSESSMENT_TEMPERATURE")


@pytest.mark.parametrize("stage", list(_CALLS))
class TestEachRoleMatchCall:
    def test_it_sends_the_shared_model(self, stage):
        assert _kwargs(stage)["model"] == "gpt-6.1-sol"

    def test_it_sends_no_temperature(self, stage):
        assert "temperature" not in _kwargs(stage)

    def test_it_sends_the_shared_reasoning_effort(self, stage):
        assert _kwargs(stage).get("reasoning_effort") == "medium"

    def test_it_still_asks_for_a_json_object(self, stage):
        assert _kwargs(stage)["response_format"] == {"type": "json_object"}


class TestClient:
    def test_the_retry_and_read_timeout_constants(self):
        assert getattr(constants, "ROLE_MATCH_MAX_RETRIES", None) == 2
        assert getattr(constants, "ROLE_MATCH_READ_TIMEOUT_S", None) == 60

    def test_the_client_retries_twice_and_waits_at_most_60_s_per_read(self):
        with patch.object(jd_assessor, "OpenAI") as openai_client:
            jd_assessor._get_openai_client()
        kwargs = openai_client.call_args.kwargs
        assert kwargs.get("max_retries") == 2
        assert kwargs.get("timeout") == httpx.Timeout(60, connect=5.0)


def _sentinel_profile():
    from services import matt_profile

    profile = matt_profile.load_profile_dict()
    profile["career_arc"] = {
        "progression": "ZZZ_SENTINEL progression",
        "employers": [
            {"name": "ZZZ_SENTINEL Employer A", "years": "1999-2000"},
            {
                "name": "ZZZ_SENTINEL Employer B",
                "years": "2001-2002",
                "note": "ZZZ_SENTINEL note",
            },
        ],
        "current": "ZZZ_SENTINEL current.",
    }
    return patch.object(matt_profile, "load_profile_dict", return_value=profile)


class TestCareerDates:
    """The assessment prompt carries each employer and its years from
    career_arc, so requirements stated in years have dates to be judged
    against. The progression and current lines stay out, and
    load_matt_profile() (Ask Agy's profile facts too) carries no arc:
    the dates are added in build_assessment_prompt() only."""

    def test_the_assessment_prompt_carries_each_employer_and_its_years(self):
        with _sentinel_profile():
            prompt = jd_assessor.build_assessment_prompt()
        lines = prompt.splitlines()
        assert "Employer: ZZZ_SENTINEL Employer A, 1999-2000." in lines
        assert (
            "Employer: ZZZ_SENTINEL Employer B, 2001-2002 (ZZZ_SENTINEL note)." in lines
        )

    def test_the_assessment_prompt_carries_no_progression_or_current_line(self):
        with _sentinel_profile():
            prompt = jd_assessor.build_assessment_prompt()
        assert "ZZZ_SENTINEL progression" not in prompt
        assert "ZZZ_SENTINEL current" not in prompt

    def test_the_shared_profile_facts_carry_no_employer(self):
        with _sentinel_profile():
            facts = jd_assessor.load_matt_profile()
        assert "ZZZ_SENTINEL Employer" not in facts

    def test_the_real_assessment_prompt_carries_the_real_employers(self):
        prompt = jd_assessor.build_assessment_prompt()
        assert (
            "Employer: Accenture, March 2005 - September 2023." in prompt.splitlines()
        )


def _module_assignment(path, name):
    tree = ast.parse((REPO / path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            return node.value
    raise AssertionError(f"{name} is not assigned at module level in {path}")


class TestOtherFiles:
    def test_probe_assessor_sends_no_temperature(self):
        source = (REPO / "probe_assessor.py").read_text(encoding="utf-8")
        assert "ASSESSMENT_TEMPERATURE" not in source
        assert "temperature=" not in source

    def test_probe_assessor_mirrors_the_reasoning_effort(self):
        source = (REPO / "probe_assessor.py").read_text(encoding="utf-8")
        assert "reasoning_effort=DEFAULT_REASONING_EFFORT" in source

    def test_the_embeddings_script_reads_the_shared_embedding_model(self):
        value = _module_assignment("build_custom_embeddings.py", "EMBEDDING_MODEL")
        assert isinstance(value, ast.Name) and value.id == "DEFAULT_EMBEDDING_MODEL"
