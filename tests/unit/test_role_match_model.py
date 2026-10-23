"""MATTGPT-302: Role Match's calls move to gpt-5.6-terra at low effort.

DEFAULT_CHAT_MODEL (config.constants) is the one chat model constant Role
Match reads; ASK_ANSWER_MODEL stays Ask Agy's own. gpt-5.6-terra rejects
temperature=0.0 with a 400 ("Only the default (1) value is supported."), so
the four Role Match calls send reasoning_effort instead
(docs/evidence/MATTGPT-302/model_ping_20261022_161813/).

The client caps each read at ROLE_MATCH_READ_TIMEOUT_S and retries
ROLE_MATCH_MAX_RETRIES times. The calls are not streamed, so the read
timeout covers the whole call: with a 3 s read timeout the AT&T required
extraction failed at 3.32 s, and with 30 s it finished in 9.11 s
(read_timeout_20261023_134509/). The slowest gpt-5.6-terra call at low
effort, over 722 calls in two full-pipeline runs, was that extraction, on
the longest JD in the test data, at 10.35 s (terra_20261022_165617/,
dash_rule_20261023_130917/).
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
    def test_the_shared_chat_model_is_gpt_5_6_terra(self):
        assert constants.DEFAULT_CHAT_MODEL == "gpt-5.6-terra"

    def test_the_shared_reasoning_effort_is_low(self):
        assert getattr(constants, "DEFAULT_REASONING_EFFORT", None) == "low"

    def test_the_classification_model_constant_is_gone(self):
        assert not hasattr(constants, "DEFAULT_CLASSIFICATION_MODEL")

    def test_the_assessment_model_is_the_shared_chat_model(self):
        assert jd_assessor.ASSESSMENT_MODEL == constants.DEFAULT_CHAT_MODEL

    def test_the_assessment_temperature_constant_is_gone(self):
        assert not hasattr(jd_assessor, "ASSESSMENT_TEMPERATURE")


@pytest.mark.parametrize("stage", list(_CALLS))
class TestEachRoleMatchCall:
    def test_it_sends_the_shared_model(self, stage):
        assert _kwargs(stage)["model"] == "gpt-5.6-terra"

    def test_it_sends_no_temperature(self, stage):
        assert "temperature" not in _kwargs(stage)

    def test_it_sends_the_shared_reasoning_effort(self, stage):
        assert _kwargs(stage).get("reasoning_effort") == "low"

    def test_it_still_asks_for_a_json_object(self, stage):
        assert _kwargs(stage)["response_format"] == {"type": "json_object"}


class TestClient:
    def test_the_retry_and_read_timeout_constants(self):
        assert getattr(constants, "ROLE_MATCH_MAX_RETRIES", None) == 2
        assert getattr(constants, "ROLE_MATCH_READ_TIMEOUT_S", None) == 30

    def test_the_client_retries_twice_and_waits_at_most_30_s_per_read(self):
        with patch.object(jd_assessor, "OpenAI") as openai_client:
            jd_assessor._get_openai_client()
        kwargs = openai_client.call_args.kwargs
        assert kwargs.get("max_retries") == 2
        assert kwargs.get("timeout") == httpx.Timeout(30, connect=5.0)


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
