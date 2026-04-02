"""
JD Pipeline End-to-End Validation

Runs the full three-step pipeline against the structured JD fixture:
  1. Extract requirements (JD_EXTRACTION_PROMPT + OpenAI)
  2. Retrieve candidate stories per requirement (Pinecone)
  3. Assess each requirement (JD_ASSESSMENT_PROMPT + OpenAI)
  4. Compute recommendation (compute_recommendation)

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
    JD_EXTRACTION_PROMPT,
    build_assessment_prompt,
    compute_recommendation,
)
from services.pinecone_service import pinecone_semantic_search  # noqa: E402

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


def extract_requirements(client: OpenAI, jd_text: str) -> dict:
    """Stage 1: Extract structured requirements from JD."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": JD_EXTRACTION_PROMPT},
            {"role": "user", "content": jd_text},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def retrieve_stories(requirement_text: str, stories: list, top_k: int = 3) -> list:
    """Stage 2: Query Pinecone for candidate stories matching a requirement."""
    results = pinecone_semantic_search(
        query=requirement_text,
        filters={},
        stories=stories,
        top_k=top_k,
    )
    if not results:
        return []
    # pinecone_semantic_search returns [{"story": dict, "pc_score": float, "score": float}]
    return [
        {
            "title": hit["story"].get("Title", ""),
            "client": hit["story"].get("Client", ""),
            "id": hit["story"].get("id", ""),
            "score": hit.get("pc_score", 0),
            "5PSummary": hit["story"].get("5PSummary", ""),
            "Situation": hit["story"].get("Situation", []),
            "Action": hit["story"].get("Action", []),
            "Result": hit["story"].get("Result", []),
        }
        for hit in results[:top_k]
    ]


def assess_requirement(
    client: OpenAI, requirement: str, candidate_stories: list
) -> dict:
    """Stage 3: Assess match quality for a single requirement."""
    # Format stories for the prompt
    stories_text = ""
    for i, s in enumerate(candidate_stories, 1):
        stories_text += f"\n--- Story {i} ---\n"
        stories_text += f"Title: {s['title']}\n"
        stories_text += f"Client: {s['client']}\n"
        stories_text += f"Score: {s['score']:.3f}\n"
        stories_text += f"Summary: {s['5PSummary']}\n"
        if s.get("Situation"):
            sit = s["Situation"]
            if isinstance(sit, list):
                sit = " ".join(sit)
            stories_text += f"Situation: {sit}\n"
        if s.get("Action"):
            act = s["Action"]
            if isinstance(act, list):
                act = " ".join(act[:3])
            stories_text += f"Action: {act}\n"
        if s.get("Result"):
            res = s["Result"]
            if isinstance(res, list):
                res = " ".join(res[:3])
            stories_text += f"Result: {res}\n"

    user_message = f"Requirement: {requirement}\n\nRetrieved Stories:\n{stories_text}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": build_assessment_prompt()},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


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
