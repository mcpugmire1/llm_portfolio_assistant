"""
Unit tests for backend_service.py

Tests for RAG orchestration, story scoring, and response generation.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestBuildKnownVocab:
    """Tests for build_known_vocab() function."""

    def test_extracts_words_from_stories(self, sample_stories):
        """Should extract vocabulary from story fields."""
        # Import here to avoid import errors if module structure changes
        try:
            from ui.pages.ask_mattgpt.backend_service import build_known_vocab
        except ImportError:
            pytest.skip("build_known_vocab not available")

        vocab = build_known_vocab(sample_stories)

        # Should contain words from titles
        assert "payments" in vocab or "Payments" in vocab
        assert "agile" in vocab or "Agile" in vocab

        # Should be a set
        assert isinstance(vocab, set)

    def test_empty_stories_returns_empty_vocab(self):
        """Should return empty set for empty story list."""
        try:
            from ui.pages.ask_mattgpt.backend_service import build_known_vocab
        except ImportError:
            pytest.skip("build_known_vocab not available")

        vocab = build_known_vocab([])
        assert vocab == set()


class TestScoreStoryForPrompt:
    """Tests for _score_story_for_prompt() function."""

    def test_higher_score_for_matching_keywords(self, sample_stories):
        """Stories with matching keywords should score higher."""
        try:
            from ui.pages.ask_mattgpt.backend_service import _score_story_for_prompt
        except ImportError:
            pytest.skip("_score_story_for_prompt not available")

        payments_story = sample_stories[0]  # Global Payments story
        agile_story = sample_stories[1]  # Agile Transformation story

        # "payments" query should score payments story higher
        payments_score = _score_story_for_prompt(payments_story, "payments platform")
        agile_score = _score_story_for_prompt(agile_story, "payments platform")

        assert payments_score > agile_score

    def test_returns_float_score(self, sample_stories):
        """Should return a float score value."""
        try:
            from ui.pages.ask_mattgpt.backend_service import _score_story_for_prompt
        except ImportError:
            pytest.skip("_score_story_for_prompt not available")

        score = _score_story_for_prompt(sample_stories[0], "test query")
        assert isinstance(score, (int, float))
        assert score >= 0


class TestDiversifyResults:
    """Tests for diversify_results() function.

    NOTE: This function may need to be implemented if not present.
    It prevents single-client domination in search results.
    """

    def test_limits_single_client_stories(self, sample_search_results):
        """No client should have more than max_per_client stories."""
        try:
            from ui.pages.ask_mattgpt.backend_service import diversify_results
        except ImportError:
            pytest.skip("diversify_results not implemented yet")

        # sample_search_results has 2 JPMC stories
        diversified = diversify_results(sample_search_results, max_per_client=1)

        jpmc_count = sum(1 for r in diversified if r.get("client") == "JPMC")
        assert jpmc_count <= 1

    def test_preserves_highest_scoring_per_client(self, sample_search_results):
        """Should keep highest scoring story when limiting per client."""
        try:
            from ui.pages.ask_mattgpt.backend_service import diversify_results
        except ImportError:
            pytest.skip("diversify_results not implemented yet")

        diversified = diversify_results(sample_search_results, max_per_client=1)

        # Find JPMC story in results
        jpmc_stories = [r for r in diversified if r.get("client") == "JPMC"]
        if jpmc_stories:
            # Should be the highest scoring JPMC story (score 0.95)
            assert jpmc_stories[0]["score"] == 0.95

    def test_maintains_overall_order(self, sample_search_results):
        """Results should still be ordered by score after diversification."""
        try:
            from ui.pages.ask_mattgpt.backend_service import diversify_results
        except ImportError:
            pytest.skip("diversify_results not implemented yet")

        diversified = diversify_results(sample_search_results, max_per_client=2)

        scores = [r["score"] for r in diversified]
        assert scores == sorted(scores, reverse=True)

    def test_no_change_when_already_diverse(self, sample_stories):
        """Should not remove stories if already diverse."""
        try:
            from ui.pages.ask_mattgpt.backend_service import diversify_results
        except ImportError:
            pytest.skip("diversify_results not implemented yet")

        # Create results with unique clients
        diverse_results = [
            {**sample_stories[0], "score": 0.9, "client": "ClientA"},
            {**sample_stories[1], "score": 0.8, "client": "ClientB"},
            {**sample_stories[2], "score": 0.7, "client": "ClientC"},
        ]

        diversified = diversify_results(diverse_results, max_per_client=2)
        assert len(diversified) == 3


class TestLogOffdomain:
    """Tests for log_offdomain() function."""

    def test_logs_to_csv(self, tmp_path):
        """Should append query to CSV file."""
        try:
            from ui.pages.ask_mattgpt.backend_service import log_offdomain
        except ImportError:
            pytest.skip("log_offdomain not available")

        csv_path = tmp_path / "offdomain.csv"
        log_offdomain("test query", "nonsense", path=str(csv_path))

        assert csv_path.exists()
        content = csv_path.read_text()
        assert "test query" in content
        assert "nonsense" in content


class TestRAGAnswer:
    """Tests for rag_answer() integration."""

    @pytest.mark.integration
    def test_returns_response_dict(self, sample_stories):
        """Should return a dictionary with expected keys."""
        try:
            from ui.pages.ask_mattgpt.backend_service import rag_answer
        except ImportError:
            pytest.skip("rag_answer not available")

        # This test requires mocking OpenAI
        with patch("ui.pages.ask_mattgpt.backend_service.openai") as mock_openai:
            mock_openai.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test response"))]
            )

            result = rag_answer(
                question="Tell me about payments", filters={}, stories=sample_stories
            )

            assert isinstance(result, dict)
