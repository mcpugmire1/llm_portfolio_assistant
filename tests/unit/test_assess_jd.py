"""Unit tests for scripts/assess_jd.py CLI wrapper.

Three tests covering the wrapper's contract surfaces:
- Empty stdin → error JSON, exit 1
- Missing STORIES_JSONL → graceful error JSON, exit 1
- Valid JD → JSON envelope with all expected keys (engine mocked in-process)

The success-path test patches `run_assessment` and `compute_recommendation`
inside the loaded `assess_jd` module's namespace via unittest.mock — the
engine is never actually called, so no OpenAI/Pinecone API traffic.

Hermeticity note: `_load_assess_jd()` triggers the engine import chain
(`services.jd_assessor` → `services.pinecone_service` → `load_dotenv()`
+ eager `Pinecone()` client construction when `VECTOR_BACKEND=pinecone`).
The eager init succeeds when env has `PINECONE_API_KEY` and friends
(client object is created but no API calls are made). If those env vars
are missing, the import raises `RuntimeError` at module load. Dev env
with a populated `.env` is the assumed runtime; CI / fresh checkout
without those vars will fail on import before the test runs.
"""

import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "assess_jd.py"


def _load_assess_jd():
    """Load scripts/assess_jd.py as a module via importlib.

    Importing executes `from services.jd_assessor import run_assessment,
    compute_recommendation` at module top, which transitively imports
    services.pinecone_service. We patch the engine functions inside the
    loaded `assess_jd` module's namespace per-test via
    unittest.mock.patch.object, so they're never actually called.
    """
    spec = importlib.util.spec_from_file_location("assess_jd", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_empty_stdin_returns_error_json():
    """Empty stdin → exit 1, stderr has JSON with 'error' key."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input="",
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1
    err = json.loads(result.stderr)
    assert "error" in err
    assert "No JD text" in err["error"]


def test_missing_jsonl_returns_graceful_error():
    """STORIES_JSONL pointing to a nonexistent file → exit 1, stderr has error JSON."""
    env = {**os.environ, "STORIES_JSONL": "/tmp/does_not_exist_assess_jd_test.jsonl"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        input="Some JD text here",
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
    )
    assert result.returncode == 1
    err = json.loads(result.stderr)
    assert "error" in err
    assert err["type"] == "FileNotFoundError"


def test_valid_jd_produces_envelope(tmp_path, capsys, monkeypatch):
    """Valid JD → exit 0, stdout has JSON envelope with all expected keys.

    Mocks run_assessment and compute_recommendation in the script's module
    namespace so the engine is never actually called. Validates the full
    envelope shape including the tricky nested evidence_type field.
    """
    # Provide a fake JSONL so load_stories() succeeds (2 stories so we can
    # assert stories_loaded == 2 in metadata)
    fake_jsonl = tmp_path / "stories.jsonl"
    fake_jsonl.write_text('{"Title": "Test Story 1"}\n{"Title": "Test Story 2"}\n')
    monkeypatch.setenv("STORIES_JSONL", str(fake_jsonl))

    # Pipe fake JD text into stdin
    monkeypatch.setattr("sys.stdin", io.StringIO("Sample JD text for testing"))

    # Fake engine returns — shape matches what services/jd_assessor.py
    # actually produces (verified via recon during triage agent setup).
    fake_assessment = {
        "extraction": {
            "jd_format": "narrative",
            "role_title": "Test Role",
            "company": "Test Co",
        },
        "results": [
            {
                "category": "required",
                "requirement": "Test requirement 1",
                "match_status": "strong",
                "evidence": [
                    {
                        "evidence_type": "story",
                        "story_title": "Test Story 1",
                        "client": "TestClient",
                        "relevance": "demonstrates X",
                    }
                ],
                "gap_explanation": "",
                "confidence": "high",
            },
            {
                "category": "preferred",
                "requirement": "Test requirement 2",
                "match_status": "gap",
                "evidence": [],
                "gap_explanation": "Note: not in evidence",
                "confidence": "low",
            },
        ],
    }
    fake_recommendation = {
        "recommendation": "Consider",
        "fit_score": "Medium",
        "strong_count": 1,
        "partial_count": 0,
        "gap_count": 1,
        "required_gap_count": 0,
        "preferred_gap_count": 1,
    }

    assess_jd = _load_assess_jd()
    with (
        patch.object(assess_jd, "run_assessment", return_value=fake_assessment),
        patch.object(
            assess_jd, "compute_recommendation", return_value=fake_recommendation
        ),
    ):
        exit_code = assess_jd.main()

    assert exit_code == 0
    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # Top-level envelope keys
    assert output["schema_version"] == 1
    assert "assessed_at" in output  # ISO timestamp string
    assert "recommendation" in output
    assert "match_results" in output  # renamed from engine's "results"
    assert "extraction" in output
    assert "metadata" in output

    # recommendation: all 7 keys from compute_recommendation()
    rec = output["recommendation"]
    for key in (
        "recommendation",
        "fit_score",
        "strong_count",
        "partial_count",
        "gap_count",
        "required_gap_count",
        "preferred_gap_count",
    ):
        assert key in rec, f"recommendation missing key: {key}"
    assert rec["recommendation"] == "Consider"
    assert rec["fit_score"] == "Medium"
    assert rec["strong_count"] == 1
    assert rec["preferred_gap_count"] == 1

    # match_results pass-through, with nested evidence_type accessible at
    # the documented path (result["evidence"][i]["evidence_type"], NOT
    # result["evidence_type"])
    assert len(output["match_results"]) == 2
    first = output["match_results"][0]
    assert first["category"] == "required"
    assert first["match_status"] == "strong"
    assert first["evidence"][0]["evidence_type"] == "story"
    assert first["evidence"][0]["story_title"] == "Test Story 1"
    assert first["evidence"][0]["client"] == "TestClient"
    assert "evidence_type" not in first, (
        "evidence_type must NOT be a top-level key on match_results entries — "
        "it lives inside the evidence array (see synthesis_prompt.md note)"
    )

    # extraction passed through in full
    assert output["extraction"]["jd_format"] == "narrative"
    assert output["extraction"]["role_title"] == "Test Role"

    # metadata fields
    md = output["metadata"]
    assert md["extraction_format"] == "narrative"
    assert md["requirement_count"] == 2
    assert md["required_count"] == 1
    assert md["preferred_count"] == 1
    assert md["stories_loaded"] == 2
