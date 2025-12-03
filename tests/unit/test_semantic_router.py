"""
Test Harness for Semantic Router

Validates that the intent classifier correctly accepts/rejects queries.
Run this after any changes to thresholds or canonical intents.

Usage:
    pytest tests/test_semantic_router.py -v

Or standalone:
    python tests/test_semantic_router.py

CI:
    Add to GitHub Actions or pre-commit hook
"""

import sys
from pathlib import Path

import pytest

# =============================================================================
# TEST DATA
# =============================================================================

SHOULD_BE_ACCEPTED = [
    # Background / overview - CRITICAL (recruiters ask these first)
    "Give me a quick overview of Matt's experience",
    "Tell me about Matt's background",
    "Tell me about Matt's background and leadership journey",
    "Walk me through Matt's career",
    "What has Matt accomplished?",
    "Who is Matt?",
    # Behavioral interview questions - CRITICAL (recruiters love these)
    "Tell me about a time Matt failed",
    "Tell me about a time you failed",
    "Tell me about a time you disagreed with leadership",
    "Tell me about a time Matt resolved team conflict",
    "How do you handle conflict?",
    "Give me an example of when Matt showed leadership",
    "Describe a difficult situation Matt handled",
    "Tell me about a challenge Matt overcame",
    # Delivery & execution
    "How did Matt achieve 4x faster delivery?",
    "How does Matt ensure teams deliver faster and with higher quality?",
    "Show me Matt's biggest delivery wins",
    # Team building
    "How did Matt scale teams from 4 to 150+?",
    "Tell me about Matt's team building experience",
    # Leadership
    "What's Matt's leadership style?",
    "How does Matt lead teams?",
    # Technical
    "What is Matt's experience with modern engineering and cloud platforms?",
    "Show me Matt's platform engineering work",
    "Tell me about Matt's cloud projects",
    "What's Matt's GenAI experience?",
    # Domain
    "Show me Matt's payments modernization work",
    "Tell me about Matt's financial services experience",
    # Stakeholders
    "How does Matt handle difficult stakeholders?",
    # Innovation
    "What's Matt's approach to innovation leadership?",
    # Agile / transformation
    "How did Matt scale agile across organizations?",
    "Tell me about Matt's transformation work",
]

SHOULD_BE_REJECTED = [
    # Weather / sports / news
    "What's the weather in Atlanta?",
    "Who won the Super Bowl?",
    "What's happening in the news?",
    # Random trivia
    "What's the capital of France?",
    "How tall is the Eiffel Tower?",
    "Explain quantum physics",
    # Creative requests
    "Write me a poem about cats",
    "Tell me a joke",
    "Write a story about dragons",
    # Unrelated topics
    "How do I cook pasta?",
    "What's Bitcoin worth?",
    "Recommend a good movie",
    # Other people
    "Tell me about Elon Musk",
    "What's Jeff Bezos's leadership style?",
]

# "Ugly" real-world inputs - typos, vague, overly polite
UGLY_BUT_VALID = [
    # Typos
    "Tell me abot Matts backgroun",
    "Whats Matt's experiance with agile?",
    "How did matt handle stakholders?",
    # Short / vague but on-topic
    "Matt's leadership?",
    "agile experience?",
    "payments work",
    "conflict resolution",
    # Overly polite / wordy
    "Could you maybe tell me a little about Matt's experience?",
    "I was wondering if you could share some information about Matt's background?",
    "Would it be possible to hear about Matt's leadership style?",
    # Mixed case
    "TELL ME ABOUT MATT'S BACKGROUND",
    "tell me about matt's background",
    "Tell Me About Matt's Background",
    # With filler words
    "So like what's Matt's experience with cloud stuff?",
    "Um, can you tell me about his leadership?",
]


# =============================================================================
# PYTEST TESTS
# =============================================================================


class TestSemanticRouter:
    """Test suite for semantic router intent classification."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Import the semantic router."""
        try:
            from semantic_router_v2 import is_portfolio_query_semantic

            self.classifier = is_portfolio_query_semantic
        except ImportError:
            try:
                from services.semantic_router import is_portfolio_query_semantic

                self.classifier = is_portfolio_query_semantic
            except ImportError:
                pytest.skip("semantic_router not found")

    @pytest.mark.parametrize("query", SHOULD_BE_ACCEPTED)
    def test_accepts_valid_queries(self, query):
        """Valid portfolio queries should be accepted."""
        is_valid, score, intent, family = self.classifier(query)
        assert (
            is_valid
        ), f"Should accept: '{query}' (score: {score:.3f}, family: {family})"

    @pytest.mark.parametrize("query", SHOULD_BE_REJECTED)
    def test_rejects_invalid_queries(self, query):
        """Off-topic queries should be rejected."""
        is_valid, score, intent, family = self.classifier(query)
        assert (
            not is_valid
        ), f"Should reject: '{query}' (score: {score:.3f}, family: {family})"

    @pytest.mark.parametrize("query", UGLY_BUT_VALID)
    def test_handles_ugly_inputs(self, query):
        """Typos, vague, and overly polite queries should still be accepted."""
        is_valid, score, intent, family = self.classifier(query)
        # More lenient - just log failures, don't fail the test
        if not is_valid:
            print(
                f"⚠️  Ugly input rejected (may need threshold tuning): '{query}' (score: {score:.3f})"
            )

    def test_returns_correct_tuple_shape(self):
        """Should return (is_valid, score, intent, family)."""
        result = self.classifier("Tell me about Matt")
        assert len(result) == 4
        is_valid, score, intent, family = result
        assert isinstance(is_valid, bool)
        assert isinstance(score, float)
        assert isinstance(intent, str)
        assert isinstance(family, str)

    def test_score_in_valid_range(self):
        """Score should be between 0 and 1."""
        _, score, _, _ = self.classifier("Tell me about Matt's background")
        assert 0.0 <= score <= 1.0

    def test_family_is_known(self):
        """Family should be a known intent family."""
        try:
            from semantic_router_v2 import get_intent_families
        except ImportError:
            from services.semantic_router import get_intent_families
        known_families = get_intent_families() + ["unknown", "error_fallback"]

        _, _, _, family = self.classifier("Tell me about Matt's leadership")
        assert family in known_families


# =============================================================================
# STANDALONE RUNNER
# =============================================================================


def run_standalone_tests():
    """Run tests without pytest for quick validation."""
    # Try to import
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from semantic_router_v2 import (
            HARD_ACCEPT,
            SOFT_ACCEPT,
            is_portfolio_query_semantic,
        )
    except ImportError:
        try:
            from services.semantic_router import (
                HARD_ACCEPT,
                SOFT_ACCEPT,
                is_portfolio_query_semantic,
            )
        except ImportError:
            print("❌ Could not import semantic_router. Check your path.")
            return 1

    print("=" * 70)
    print("SEMANTIC ROUTER TEST HARNESS")
    print("=" * 70)
    print(f"Thresholds: HARD_ACCEPT={HARD_ACCEPT}, SOFT_ACCEPT={SOFT_ACCEPT}")
    print()

    all_passed = True

    # Test accepted queries
    print("=" * 70)
    print("SHOULD BE ACCEPTED")
    print("=" * 70)

    accepted_failures = []
    for query in SHOULD_BE_ACCEPTED:
        is_valid, score, intent, family = is_portfolio_query_semantic(query)
        zone = (
            "HARD"
            if score >= HARD_ACCEPT
            else ("SOFT" if score >= SOFT_ACCEPT else "REJECT")
        )
        status = "✅" if is_valid else "❌"
        print(f"{status} [{zone:6}] {score:.3f} | {family:20} | {query[:50]}")
        if not is_valid:
            accepted_failures.append((query, score, family))
            all_passed = False

    # Test rejected queries
    print("\n" + "=" * 70)
    print("SHOULD BE REJECTED")
    print("=" * 70)

    rejected_failures = []
    for query in SHOULD_BE_REJECTED:
        is_valid, score, intent, family = is_portfolio_query_semantic(query)
        zone = (
            "HARD"
            if score >= HARD_ACCEPT
            else ("SOFT" if score >= SOFT_ACCEPT else "REJECT")
        )
        status = "✅" if not is_valid else "❌"
        print(f"{status} [{zone:6}] {score:.3f} | {family:20} | {query[:50]}")
        if is_valid:
            rejected_failures.append((query, score, family))
            all_passed = False

    # Test ugly inputs
    print("\n" + "=" * 70)
    print("UGLY BUT VALID (typos, vague, polite)")
    print("=" * 70)

    ugly_failures = []
    for query in UGLY_BUT_VALID:
        is_valid, score, intent, family = is_portfolio_query_semantic(query)
        zone = (
            "HARD"
            if score >= HARD_ACCEPT
            else ("SOFT" if score >= SOFT_ACCEPT else "REJECT")
        )
        status = "✅" if is_valid else "⚠️"
        print(f"{status} [{zone:6}] {score:.3f} | {family:20} | {query[:50]}")
        if not is_valid:
            ugly_failures.append((query, score, family))
            # Don't fail overall for ugly inputs - just warn

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Accepted: {len(SHOULD_BE_ACCEPTED) - len(accepted_failures)}/{len(SHOULD_BE_ACCEPTED)} passed"
    )
    print(
        f"Rejected: {len(SHOULD_BE_REJECTED) - len(rejected_failures)}/{len(SHOULD_BE_REJECTED)} passed"
    )
    print(
        f"Ugly:     {len(UGLY_BUT_VALID) - len(ugly_failures)}/{len(UGLY_BUT_VALID)} passed (warnings only)"
    )

    if accepted_failures:
        print("\n❌ CRITICAL: Should accept but rejected:")
        for query, score, family in accepted_failures:
            print(f"   {score:.3f} [{family}] | {query}")

    if rejected_failures:
        print("\n❌ CRITICAL: Should reject but accepted:")
        for query, score, family in rejected_failures:
            print(f"   {score:.3f} [{family}] | {query}")

    if ugly_failures:
        print("\n⚠️  WARNINGS: Ugly inputs rejected (consider tuning):")
        for query, score, family in ugly_failures:
            print(f"   {score:.3f} [{family}] | {query}")

    if all_passed:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        return 0
    else:
        print(
            f"\n💥 {len(accepted_failures) + len(rejected_failures)} CRITICAL TESTS FAILED"
        )
        return 1


if __name__ == "__main__":
    exit_code = run_standalone_tests()
    sys.exit(exit_code)
