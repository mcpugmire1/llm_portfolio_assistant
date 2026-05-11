#!/usr/bin/env python3
"""
CLI wrapper around services/jd_assessor.py for Cowork orchestration.

Reads a job description from stdin, runs the existing engine
(run_assessment + compute_recommendation), and prints structured
JSON to stdout. Intended to be invoked by Cowork via shell.

Usage:
    cat jd.txt | python scripts/assess_jd.py > result.json

    # Or directly:
    python scripts/assess_jd.py < jd.txt

Environment:
    Required env vars (loaded from .env via services.pinecone_service on import):
      OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_NAMESPACE
    Optional:
      STORIES_JSONL — path to STAR story corpus JSONL
                      (default: echo_star_stories_nlp.jsonl)

Exit codes:
    0 = success, JSON on stdout
    1 = error, error JSON on stderr

Drop this file at scripts/assess_jd.py inside the MattGPT repo.
The sys.path bootstrap below makes the script work regardless of how it
is invoked (subprocess, Cowork shell, pytest) — no PYTHONPATH gymnastics
needed on the caller side.
"""

import json
import os
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

# Self-bootstrap: ensure the repo root is on sys.path so the engine import
# below works regardless of how the script is invoked. Python adds the
# script's own dir (scripts/) to sys.path by default, NOT the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Engine imports — services.pinecone_service calls load_dotenv() at module
# import time, so env vars resolve via the repo's .env automatically.
from services.jd_assessor import compute_recommendation, run_assessment  # noqa: E402


def load_stories() -> list[dict]:
    """Load STAR stories from the JSONL file the engine expects.

    run_assessment() does not load stories itself — it requires them
    as a second argument. The Streamlit app loads them at startup;
    the CLI wrapper has to do the same here.
    """
    jsonl_path = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")
    with open(jsonl_path) as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> int:
    jd_text = sys.stdin.read()

    if not jd_text.strip():
        print(
            json.dumps({"error": "No JD text provided on stdin"}),
            file=sys.stderr,
        )
        return 1

    try:
        stories = load_stories()

        # Layer 1: capability (matcher + recommender)
        assessment = run_assessment(jd_text, stories)
        results = assessment.get("results", [])
        extraction = assessment.get("extraction", {})
        recommendation = compute_recommendation(results)

        # Compose the structured payload Cowork's synthesis prompt consumes.
        # `extraction` is passed through in full so the synthesis layer can
        # reference jd_format, extracted requirement metadata, etc.
        output = {
            "schema_version": 1,
            "assessed_at": datetime.now(UTC).isoformat(),
            "recommendation": recommendation,
            "match_results": results,
            "extraction": extraction,
            "metadata": {
                "extraction_format": extraction.get("jd_format"),
                "requirement_count": len(results),
                "required_count": sum(
                    1 for r in results if r.get("category") == "required"
                ),
                "preferred_count": sum(
                    1 for r in results if r.get("category") == "preferred"
                ),
                "stories_loaded": len(stories),
            },
        }

        print(json.dumps(output, indent=2))
        return 0

    except Exception as exc:  # noqa: BLE001 — surface any engine error to caller
        print(
            json.dumps(
                {
                    "error": str(exc),
                    "type": type(exc).__name__,
                    "trace": traceback.format_exc(),
                }
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
