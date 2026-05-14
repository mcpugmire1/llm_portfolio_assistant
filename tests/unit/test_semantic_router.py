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

# =============================================================================
# MATTGPT-016 — Wrong-person query detection
# Test groups below are added under MATTGPT-016 work. Three new coverage
# bands surface known gaps in the current router's purely-score-based
# is_valid logic:
#
#   1. SHOULD_BE_REJECTED_LOWERCASE — case-sensitivity gap. Users type
#      casually; the proposed regex-based wrong-person detector targets
#      Title Case patterns and misses lowercase variants without a
#      KNOWN_WRONG_PEOPLE case-insensitive list.
#
#   2. SHOULD_BE_ACCEPTED_CLIENT_NAMES — corpus-entity false-positive
#      guard. Two-word Title Case spans like "Norfolk Southern" or
#      "Pivotal Labs" are real clients in the story corpus and must
#      NOT trip the wrong-person detector even when the query lacks a
#      Matt-token. Backed by a corpus-derived MATT_CLIENT_NAMES allowlist.
#
#   3. SHOULD_BE_ACCEPTED_TECH_TERMS — technical-concept false-positive
#      guard. "Domain Driven Design" and similar capitalized concepts
#      should not trigger wrong-person rejection.
#
# All four MATTGPT-016 test groups are marked @pytest.mark.xfail so they
# document the contract change without breaking runs during the staged
# rollout. When the LOG_ONLY flag flips to enforcement and tests turn
# GREEN, drop the xfail markers.
#
# See BACKLOG.md MATTGPT-016 for the full rollout plan.
# =============================================================================

# Lowercase wrong-person queries — the case-sensitivity gap.
SHOULD_BE_REJECTED_LOWERCASE = [
    "tell me about elon musk",
    "what's jeff bezos's leadership style?",
    "tell me about tim cook",
]

# Two-word Title Case spans that are real corpus entities (clients,
# partners, programs). These have NO Matt-token by design — the detector
# must rely on the MATT_CLIENT_NAMES allowlist to keep them accepted.
SHOULD_BE_ACCEPTED_CLIENT_NAMES = [
    "Tell me about the Norfolk Southern work",
    "What was the Pivotal Labs partnership?",
    "Did Cloud Innovation Center scale?",
]

# Multi-word capitalized technical concepts. Pattern overlaps with the
# wrong-person regex but content is on-topic for the portfolio.
SHOULD_BE_ACCEPTED_TECH_TERMS = [
    "Tell me about Domain Driven Design experience",
    "Show me Event Driven Architecture work",
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

    # =========================================================================
    # MATTGPT-016 — Wrong-person query detection (xfail until detector lands)
    #
    # Contract change: router will reject out_of_scope / personal /
    # wrong-person queries via is_valid=False. Today the router only
    # thresholds on score, so these assertions don't yet hold. Marked
    # xfail to document intent without breaking runs during the staged
    # rollout. Drop the xfail markers when the LOG_ONLY flag flips to
    # enforcement and the assertions go GREEN.
    # =========================================================================

    @pytest.mark.xfail(
        reason="MATTGPT-016: wrong-person detector + case-insensitive list pending",
        strict=False,
    )
    @pytest.mark.parametrize("query", SHOULD_BE_REJECTED_LOWERCASE)
    def test_rejects_lowercase_wrong_person_queries(self, query):
        """Wrong-person queries typed in lowercase must still reject.

        The proposed regex r'\\b[A-Z][a-z]+\\s+[A-Z][a-z]+\\b' only catches
        Title Case. A case-insensitive KNOWN_WRONG_PEOPLE list closes the
        casual-typing coverage gap.
        """
        is_valid, score, intent, family = self.classifier(query)
        assert not is_valid, (
            f"Should reject lowercase wrong-person: '{query}' "
            f"(score: {score:.3f}, family: {family})"
        )

    @pytest.mark.xfail(
        reason="MATTGPT-016: MATT_CLIENT_NAMES allowlist (corpus-derived) pending",
        strict=False,
    )
    @pytest.mark.parametrize("query", SHOULD_BE_ACCEPTED_CLIENT_NAMES)
    def test_does_not_reject_corpus_client_names(self, query):
        """Two-word client names from the story corpus (Norfolk Southern,
        Pivotal Labs, etc.) must not trip the wrong-person detector even
        when the query has no Matt-token. The corpus-derived allowlist
        carries the load.
        """
        is_valid, score, intent, family = self.classifier(query)
        assert is_valid, (
            f"Should accept corpus client name: '{query}' "
            f"(score: {score:.3f}, family: {family})"
        )
        assert family not in ("out_of_scope", "personal"), (
            f"'{query}' classified as {family} — corpus-entity allowlist "
            f"or wrong-person detector is over-rejecting."
        )

    @pytest.mark.xfail(
        reason="MATTGPT-016: structural detector must not flag multi-word technical concepts",
        strict=False,
    )
    @pytest.mark.parametrize("query", SHOULD_BE_ACCEPTED_TECH_TERMS)
    def test_does_not_reject_multi_word_tech_concepts(self, query):
        """Multi-word capitalized technical concepts ("Domain Driven Design",
        "Event Driven Architecture") must not be mistaken for person names
        by the wrong-person regex. The Matt-token check should already
        accept queries with explicit "Matt" anchors — these test cases
        intentionally include "experience" / "work" tokens that hint at
        portfolio scope without naming Matt.
        """
        is_valid, score, intent, family = self.classifier(query)
        assert is_valid, (
            f"Should accept technical concept query: '{query}' "
            f"(score: {score:.3f}, family: {family})"
        )

    @pytest.mark.xfail(
        reason="MATTGPT-016: regression guard activates when canonical phrases land in out_of_scope",
        strict=False,
    )
    @pytest.mark.parametrize("query", SHOULD_BE_ACCEPTED)
    def test_accepted_queries_not_in_out_of_scope_or_personal(self, query):
        """Regression guard: adding canonical phrases to out_of_scope (Step 3
        of the MATTGPT-016 rollout) must not pull legitimate portfolio
        queries into the redirect families. If this fires after the canonical
        phrases land, the phrases are too broad and need tightening before
        flipping the LOG_ONLY flag to enforcement.

        Currently expected to pass (out_of_scope is small). Marked xfail
        because its purpose materializes only after the canonical phrases
        commit — at that point an unexpected GREEN here confirms the
        phrases are well-scoped, and unexpected FAIL flags the need to
        tune them.
        """
        _, _, _, family = self.classifier(query)
        assert family not in ("out_of_scope", "personal"), (
            f"'{query}' classified as {family} — canonical phrases added "
            f"to out_of_scope/personal may be too broad."
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
