#!/usr/bin/env python3
"""
Direct Pinecone score test - bypasses Streamlit session state.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI  # noqa: E402
from pinecone import Pinecone  # noqa: E402

# Config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

# Thresholds (must match rag_service.py)
CONFIDENCE_HIGH = 0.25
CONFIDENCE_LOW = 0.20  # Updated value

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
idx = pc.Index(PINECONE_INDEX_NAME)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def embed(text: str) -> list[float]:
    """Generate embedding for text."""
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[text])
    return response.data[0].embedding


def query_pinecone(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    """Query Pinecone and return [(score, title), ...]."""
    qvec = embed(query)
    res = idx.query(
        vector=qvec,
        top_k=top_k,
        include_metadata=True,
        namespace=PINECONE_NAMESPACE,
    )
    results = []
    for m in res.matches:
        score = m.score
        title = m.metadata.get("Title", m.metadata.get("title", "Unknown"))
        results.append((score, title))
    return results


# Test queries
GARBAGE_QUERIES = [
    "peanut butter",
    "Madonna's bra",
    "weather today",
    "how to cook pasta",
    "Bitcoin price",
    "quantum physics",
]

VALID_QUERIES = [
    "Tell me about Matt's background",
    "What are Matt's themes",
    "JPMorgan payments",
    "platform modernization",
    "Tell me about a time Matt failed",
    "agile transformation",
]

SYNTHESIS_QUERIES = [
    "What are common themes across Matt's work?",
    "What patterns do you see in Matt's approach?",
    "What makes Matt different from other candidates?",
]


def main():
    print("=" * 80)
    print("DIRECT PINECONE SCORE TEST")
    print("=" * 80)
    print(f"Index: {PINECONE_INDEX_NAME}, Namespace: {PINECONE_NAMESPACE}")
    print(f"Thresholds: HIGH={CONFIDENCE_HIGH}, LOW={CONFIDENCE_LOW}")
    print()

    # Test garbage
    print("=" * 80)
    print(f"GARBAGE (should score < {CONFIDENCE_LOW})")
    print("=" * 80)
    garbage_pass = 0
    for query in GARBAGE_QUERIES:
        results = query_pinecone(query)
        if results:
            score, title = results[0]
            status = "✅" if score < CONFIDENCE_LOW else "❌"
            if score < CONFIDENCE_LOW:
                garbage_pass += 1
            print(f"{status} {score:.3f} | {query[:25]:<25} | {title[:35]}")
        else:
            print(f"✅ 0.000 | {query[:25]:<25} | No results")
            garbage_pass += 1

    # Test valid
    print()
    print("=" * 80)
    print(f"VALID (should score >= {CONFIDENCE_LOW})")
    print("=" * 80)
    valid_pass = 0
    for query in VALID_QUERIES:
        results = query_pinecone(query)
        if results:
            score, title = results[0]
            status = "✅" if score >= CONFIDENCE_LOW else "❌"
            if score >= CONFIDENCE_LOW:
                valid_pass += 1
            print(f"{status} {score:.3f} | {query[:25]:<25} | {title[:35]}")
        else:
            print(f"❌ 0.000 | {query[:25]:<25} | No results")

    # Test synthesis
    print()
    print("=" * 80)
    print(f"SYNTHESIS (should score >= {CONFIDENCE_LOW})")
    print("=" * 80)
    synth_pass = 0
    for query in SYNTHESIS_QUERIES:
        results = query_pinecone(query)
        if results:
            score, title = results[0]
            status = "✅" if score >= CONFIDENCE_LOW else "❌"
            if score >= CONFIDENCE_LOW:
                synth_pass += 1
            print(f"{status} {score:.3f} | {query[:25]:<25} | {title[:35]}")
        else:
            print(f"❌ 0.000 | {query[:25]:<25} | No results")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Garbage:   {garbage_pass}/{len(GARBAGE_QUERIES)} correctly rejected")
    print(f"Valid:     {valid_pass}/{len(VALID_QUERIES)} correctly accepted")
    print(f"Synthesis: {synth_pass}/{len(SYNTHESIS_QUERIES)} correctly accepted")

    total = garbage_pass + valid_pass + synth_pass
    expected = len(GARBAGE_QUERIES) + len(VALID_QUERIES) + len(SYNTHESIS_QUERIES)

    if total == expected:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n💥 {expected - total} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
