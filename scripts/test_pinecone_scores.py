#!/usr/bin/env python3
"""
Quick test to check Pinecone scores for various queries.
Validates that garbage queries score below threshold and valid queries score above.

Usage:
    python scripts/test_pinecone_scores.py
"""

import os
import sys

from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

import json  # noqa: E402

from services.pinecone_service import pinecone_semantic_search  # noqa: E402
from services.rag_service import CONFIDENCE_HIGH, CONFIDENCE_LOW  # noqa: E402


# Load stories from JSONL
def load_stories():
    stories = []
    jsonl_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "echo_star_stories_nlp.jsonl"
    )
    with open(jsonl_path) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    return stories


STORIES = load_stories()
print(f"Loaded {len(STORIES)} stories")

# Test queries
GARBAGE_QUERIES = [
    "peanut butter",
    "Madonna's bra",
    "weather today",
    "how to cook pasta",
    "Bitcoin price",
    "Elon Musk",
    "quantum physics",
    "Super Bowl winner",
]

VALID_QUERIES = [
    "Tell me about Matt's background",
    "What are Matt's themes",
    "JPMorgan payments",
    "platform modernization",
    "cloud migration",
    "team scaling",
    "Tell me about a time Matt failed",
    "agile transformation",
]

SYNTHESIS_QUERIES = [
    "What are common themes across Matt's work?",
    "What patterns do you see in Matt's approach?",
    "What makes Matt different from other candidates?",
    "What problems does Matt consistently solve?",
]


def test_query(query: str) -> tuple[float, str]:
    """Test a single query and return (score, top_match_title)."""
    try:
        results = pinecone_semantic_search(query, filters={}, stories=STORIES, top_k=3)
        if results:
            score = results[0].get("pc_score", 0.0)
            title = results[0].get("Title", "Unknown")
            return score, title
        return 0.0, "No results"
    except Exception as e:
        return 0.0, f"Error: {e}"


def main():
    print("=" * 80)
    print("PINECONE SCORE VALIDATION")
    print("=" * 80)
    print(
        f"Thresholds: CONFIDENCE_HIGH={CONFIDENCE_HIGH}, CONFIDENCE_LOW={CONFIDENCE_LOW}"
    )
    print()

    # Test garbage queries
    print("=" * 80)
    print(f"GARBAGE QUERIES (should score < {CONFIDENCE_LOW:.2f})")
    print("=" * 80)
    garbage_failures = []
    for query in GARBAGE_QUERIES:
        score, title = test_query(query)
        status = "✅" if score < CONFIDENCE_LOW else "❌"
        conf = (
            "none"
            if score < CONFIDENCE_LOW
            else ("low" if score < CONFIDENCE_HIGH else "high")
        )
        print(f"{status} {score:.3f} [{conf:4}] | {query[:30]:<30} | {title[:40]}")
        if score >= CONFIDENCE_LOW:
            garbage_failures.append((query, score))

    # Test valid queries
    print()
    print("=" * 80)
    print(f"VALID QUERIES (should score >= {CONFIDENCE_LOW:.2f})")
    print("=" * 80)
    valid_failures = []
    for query in VALID_QUERIES:
        score, title = test_query(query)
        status = "✅" if score >= CONFIDENCE_LOW else "❌"
        conf = (
            "none"
            if score < CONFIDENCE_LOW
            else ("low" if score < CONFIDENCE_HIGH else "high")
        )
        print(f"{status} {score:.3f} [{conf:4}] | {query[:30]:<30} | {title[:40]}")
        if score < CONFIDENCE_LOW:
            valid_failures.append((query, score))

    # Test synthesis queries
    print()
    print("=" * 80)
    print(f"SYNTHESIS QUERIES (should score >= {CONFIDENCE_LOW:.2f})")
    print("=" * 80)
    synthesis_failures = []
    for query in SYNTHESIS_QUERIES:
        score, title = test_query(query)
        status = "✅" if score >= CONFIDENCE_LOW else "❌"
        conf = (
            "none"
            if score < CONFIDENCE_LOW
            else ("low" if score < CONFIDENCE_HIGH else "high")
        )
        print(f"{status} {score:.3f} [{conf:4}] | {query[:30]:<30} | {title[:40]}")
        if score < CONFIDENCE_LOW:
            synthesis_failures.append((query, score))

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(
        f"Garbage:   {len(GARBAGE_QUERIES) - len(garbage_failures)}/{len(GARBAGE_QUERIES)} correctly rejected"
    )
    print(
        f"Valid:     {len(VALID_QUERIES) - len(valid_failures)}/{len(VALID_QUERIES)} correctly accepted"
    )
    print(
        f"Synthesis: {len(SYNTHESIS_QUERIES) - len(synthesis_failures)}/{len(SYNTHESIS_QUERIES)} correctly accepted"
    )

    if garbage_failures:
        print("\n❌ GARBAGE QUERIES THAT PASSED (should be rejected):")
        for query, score in garbage_failures:
            print(f"   {score:.3f} | {query}")

    if valid_failures:
        print("\n❌ VALID QUERIES THAT FAILED (should be accepted):")
        for query, score in valid_failures:
            print(f"   {score:.3f} | {query}")

    if synthesis_failures:
        print("\n❌ SYNTHESIS QUERIES THAT FAILED (should be accepted):")
        for query, score in synthesis_failures:
            print(f"   {score:.3f} | {query}")

    total_failures = (
        len(garbage_failures) + len(valid_failures) + len(synthesis_failures)
    )
    if total_failures == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(
            f"\n💥 {total_failures} TESTS FAILED - consider adjusting CONFIDENCE_LOW threshold"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
