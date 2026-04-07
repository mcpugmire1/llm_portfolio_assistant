"""
JD Pipeline End-to-End Validation

Runs the full three-step pipeline against the structured JD fixture:
  1. Extract requirements (JD_EXTRACTION_PROMPT + OpenAI)
  2. Retrieve candidate stories per requirement (Pinecone)
  3. Assess each requirement (JD_ASSESSMENT_PROMPT + OpenAI)
  4. Compute recommendation (compute_recommendation)

Pipeline functions live in services/jd_assessor.py — this script is a thin
runner that exercises them against a fixture and prints a human-readable
report. The UI calls run_assessment() directly from the same module.

Usage: python tests/jd_pipeline_validation.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from services.jd_assessor import (  # noqa: E402
    assess_requirement,
    compute_recommendation,
    extract_requirements,
    retrieve_stories,
)

# Load stories (same as app.py)
STORIES_FILE = "echo_star_stories_nlp.jsonl"


def load_stories():
    stories = []
    with open(STORIES_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                story = json.loads(line)
                if story.get("id"):
                    story["id"] = str(story["id"]).strip()
                    stories.append(story)
    return stories


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Load JD fixture
    jd_path = Path("tests/bdd/fixtures/jd_extraction/structured_jd.txt")
    jd_text = jd_path.read_text()

    # Load stories
    stories = load_stories()
    print(f"Loaded {len(stories)} stories\n")

    # Stage 1: Extract
    print("=" * 80)
    print("  STAGE 1: REQUIREMENT EXTRACTION")
    print("=" * 80)
    extraction = extract_requirements(client, jd_text)
    print(f"Role: {extraction.get('role_title')}")
    print(f"Company: {extraction.get('company')}")
    print(f"Required: {len(extraction.get('required_qualifications', []))}")
    print(f"Preferred: {len(extraction.get('preferred_qualifications', []))}")
    print(f"Implicit: {len(extraction.get('implicit_requirements', []))}")

    # Combine required + preferred for assessment
    all_requirements = []
    for r in extraction.get("required_qualifications", []):
        all_requirements.append({"text": r["requirement"], "category": "required"})
    for r in extraction.get("preferred_qualifications", []):
        all_requirements.append({"text": r["requirement"], "category": "preferred"})

    print(f"\nTotal requirements to assess: {len(all_requirements)}")

    # Stage 2 + 3: Retrieve and Assess each requirement
    print("\n" + "=" * 80)
    print("  STAGE 2+3: RETRIEVE AND ASSESS")
    print("=" * 80)

    match_results = []
    for i, req in enumerate(all_requirements, 1):
        print(f"\n{'─' * 70}")
        print(
            f"  [{i}/{len(all_requirements)}] {req['category'].upper()}: {req['text']}"
        )
        print(f"{'─' * 70}")

        # Stage 2: Retrieve
        candidates = retrieve_stories(req["text"], stories, top_k=3)
        if candidates:
            print(f"  Retrieved {len(candidates)} stories:")
            for c in candidates:
                print(f"    • {c['title']} ({c['client']}) — score: {c['score']:.3f}")
        else:
            print("  No stories retrieved")

        # Stage 3: Assess
        assessment = assess_requirement(client, req["text"], candidates)
        assessment["category"] = req["category"]
        match_results.append(assessment)

        status_icon = {"strong": "✓", "partial": "~", "gap": "✗"}.get(
            assessment.get("match_status", ""), "?"
        )
        print(
            f"\n  {status_icon} {assessment.get('match_status', 'unknown').upper()} (confidence: {assessment.get('confidence', '?')})"
        )

        for ev in assessment.get("evidence", []):
            print(f"    → {ev.get('story_title', '')} ({ev.get('client', '')})")
            print(f"      {ev.get('relevance', '')}")

        gap = assessment.get("gap_explanation", "")
        if gap:
            print(f"    ⚠ Gap: {gap}")

    # Stage 4: Recommendation
    print("\n" + "=" * 80)
    print("  RECOMMENDATION (Private View)")
    print("=" * 80)
    rec = compute_recommendation(match_results)
    print(f"\n  Fit Score:      {rec['fit_score']}")
    print(f"  Recommendation: {rec['recommendation']}")
    print(
        f"  Strong: {rec['strong_count']}  Partial: {rec['partial_count']}  Gap: {rec['gap_count']}"
    )
    print(
        f"  Required gaps: {rec['required_gap_count']}  Preferred gaps: {rec['preferred_gap_count']}"
    )
    print(f"  Total: {len(match_results)}")


if __name__ == "__main__":
    main()
