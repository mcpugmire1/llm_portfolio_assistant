"""Unit tests for services.semantic_router._classify_embedding (MATTGPT-216).

_classify_embedding is the pure part of is_portfolio_query_semantic --
given a query embedding and the map of intent-anchor embeddings, it picks
the best-matching intent, resolves its family, and applies the soft
threshold to produce is_valid. No network.

The end-to-end tests (embed via OpenAI, verify router picks the right
family for real queries) moved to tests/integration/test_semantic_router.py
in the same commit. Real-embedding tests are integration concerns; they
require an API key and OpenAI's semantic behavior, and can't be meaningfully
mocked without turning the test into a check of the mock.

These unit tests exercise the classification logic directly against
fixture vectors -- fast, hermetic, deterministic.
"""

import pytest

from services.semantic_router import (
    INTENT_TO_FAMILY,
    SOFT_ACCEPT,
    _classify_embedding,
)


def _v(*components: float) -> list[float]:
    """Build a fixture embedding vector of the given components."""
    return list(components)


class TestClassifyEmbeddingRanking:
    """Cosine-similarity ranking: best-matching intent wins."""

    def test_picks_intent_with_highest_similarity(self):
        # Query aligned with intent_b (identical vector -> similarity 1.0);
        # intent_a and intent_c are orthogonal.
        query = _v(0.0, 1.0, 0.0)
        anchors = {
            "intent_a": _v(1.0, 0.0, 0.0),
            "intent_b": _v(0.0, 1.0, 0.0),
            "intent_c": _v(0.0, 0.0, 1.0),
        }
        is_valid, score, intent, family = _classify_embedding(query, anchors)
        assert intent == "intent_b"
        assert score == pytest.approx(1.0)

    def test_identical_scores_first_iterated_wins(self):
        # Two anchors produce the same similarity; first key iterated wins.
        # Documents current behavior (dict iteration order = insertion order
        # in CPython 3.7+); test pins it so a future refactor to a different
        # tie-break rule surfaces the intent change.
        query = _v(1.0, 1.0, 0.0)
        anchors = {
            "first_intent": _v(1.0, 1.0, 0.0),
            "second_intent": _v(1.0, 1.0, 0.0),
        }
        _, _, intent, _ = _classify_embedding(query, anchors)
        assert intent == "first_intent"


class TestClassifyEmbeddingFamily:
    """INTENT_TO_FAMILY resolution."""

    def test_returns_family_mapped_from_best_intent(self):
        # Pick an intent known to be in INTENT_TO_FAMILY. Use an existing
        # anchor so we don't have to monkeypatch INTENT_TO_FAMILY.
        real_intent, real_family = next(iter(INTENT_TO_FAMILY.items()))
        anchors = {real_intent: _v(1.0, 0.0)}
        query = _v(1.0, 0.0)
        _, _, intent, family = _classify_embedding(query, anchors)
        assert intent == real_intent
        assert family == real_family

    def test_returns_unknown_family_for_intent_not_in_map(self):
        # Best intent isn't in INTENT_TO_FAMILY -> family defaults to "unknown".
        anchors = {"synthetic_intent_not_in_map": _v(1.0, 0.0)}
        assert "synthetic_intent_not_in_map" not in INTENT_TO_FAMILY
        query = _v(1.0, 0.0)
        _, _, _, family = _classify_embedding(query, anchors)
        assert family == "unknown"


class TestClassifyEmbeddingThreshold:
    """Soft-threshold gating: is_valid is score >= soft_threshold."""

    def test_is_valid_true_when_score_above_soft_threshold(self):
        # Aligned vectors -> similarity 1.0, well above default soft_threshold.
        query = _v(1.0, 0.0)
        anchors = {"intent_a": _v(1.0, 0.0)}
        is_valid, score, _, _ = _classify_embedding(query, anchors)
        assert score >= SOFT_ACCEPT
        assert is_valid is True

    def test_is_valid_false_when_score_below_soft_threshold(self):
        # Orthogonal vectors -> similarity 0.0, below any positive threshold.
        query = _v(1.0, 0.0)
        anchors = {"intent_a": _v(0.0, 1.0)}
        is_valid, score, _, _ = _classify_embedding(query, anchors)
        assert score < SOFT_ACCEPT
        assert is_valid is False

    def test_custom_soft_threshold_respected(self):
        # Score = 1.0; default soft would say valid. Custom soft=0.9 still
        # valid (score >= custom); custom soft=1.1 not valid (score < custom).
        query = _v(1.0, 0.0)
        anchors = {"intent_a": _v(1.0, 0.0)}
        is_valid_high, _, _, _ = _classify_embedding(query, anchors, soft_threshold=0.9)
        assert is_valid_high is True
        is_valid_unreachable, _, _, _ = _classify_embedding(
            query, anchors, soft_threshold=1.1
        )
        assert is_valid_unreachable is False

    def test_is_valid_true_at_exact_soft_threshold_boundary(self):
        # Score == soft_threshold should be valid (current logic is `>=`).
        # Boundary pins the >= vs > choice so a refactor to > surfaces.
        query = _v(1.0, 0.0)
        anchors = {"intent_a": _v(1.0, 0.0)}
        # Score will be 1.0; use soft=1.0 to exercise the exact-boundary case.
        is_valid, score, _, _ = _classify_embedding(query, anchors, soft_threshold=1.0)
        assert score == pytest.approx(1.0)
        assert is_valid is True


class TestClassifyEmbeddingEdgeCases:
    def test_empty_intent_embeddings_returns_zero_score_unknown(self):
        # No anchors to compare against -> score stays 0.0, best_intent is
        # empty string, family lookup misses -> "unknown", is_valid False.
        result = _classify_embedding(_v(1.0, 0.0), {})
        assert result == (False, 0.0, "", "unknown")

    def test_returns_four_tuple_of_correct_types(self):
        query = _v(1.0, 0.0)
        anchors = {"intent_a": _v(1.0, 0.0)}
        result = _classify_embedding(query, anchors)
        assert len(result) == 4
        is_valid, score, intent, family = result
        assert isinstance(is_valid, bool)
        assert isinstance(score, float)
        assert isinstance(intent, str)
        assert isinstance(family, str)
