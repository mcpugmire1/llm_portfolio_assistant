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

        # Should contain words from titles (lowercased)
        assert "payments" in vocab
        assert "agile" in vocab

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

    def test_filters_short_tokens(self, sample_stories):
        """Should exclude tokens shorter than 3 characters."""
        try:
            from ui.pages.ask_mattgpt.backend_service import build_known_vocab
        except ImportError:
            pytest.skip("build_known_vocab not available")

        # Add story with short tokens
        stories = [
            {
                "Title": "AI ML Platform",  # "AI" and "ML" should be excluded
                "Client": "XY Corp",  # "XY" should be excluded
                "Role": "Director",
                "Industry": "Tech",
                "Sub-category": "Platform",
            }
        ]

        vocab = build_known_vocab(stories)

        # Short tokens should be filtered
        assert "ai" not in vocab
        assert "ml" not in vocab
        assert "xy" not in vocab

        # Valid tokens should be included
        assert "platform" in vocab
        assert "director" in vocab

    def test_handles_missing_fields(self):
        """Should handle stories with missing fields gracefully."""
        try:
            from ui.pages.ask_mattgpt.backend_service import build_known_vocab
        except ImportError:
            pytest.skip("build_known_vocab not available")

        stories = [{"Title": "Test Story"}]  # Missing other fields
        vocab = build_known_vocab(stories)

        assert "test" in vocab
        assert "story" in vocab


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

    def test_zero_score_for_no_matches(self):
        """Should return 0.0 for queries with no matching keywords."""
        try:
            from ui.pages.ask_mattgpt.backend_service import _score_story_for_prompt
        except ImportError:
            pytest.skip("_score_story_for_prompt not available")

        story = {
            "Title": "Platform Engineering",
            "Client": "JPMC",
            "Industry": "Banking",
            "public_tags": "microservices,cloud",
        }

        score = _score_story_for_prompt(story, "unrelated query xyz")
        assert score == 0.0

    def test_case_insensitive_matching(self):
        """Should match keywords case-insensitively."""
        try:
            from ui.pages.ask_mattgpt.backend_service import _score_story_for_prompt
        except ImportError:
            pytest.skip("_score_story_for_prompt not available")

        story = {"Title": "JPMC Platform", "Client": "JPMC"}

        score_lower = _score_story_for_prompt(story, "jpmc")
        score_upper = _score_story_for_prompt(story, "JPMC")
        score_mixed = _score_story_for_prompt(story, "JpMc")

        assert score_lower == score_upper == score_mixed
        assert score_lower > 0


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

        jpmc_count = sum(1 for r in diversified if r.get("Client") == "JPMC")
        assert jpmc_count <= 1

    def test_preserves_highest_scoring_per_client(self, sample_search_results):
        """Should keep highest scoring story when limiting per client."""
        try:
            from ui.pages.ask_mattgpt.backend_service import diversify_results
        except ImportError:
            pytest.skip("diversify_results not implemented yet")

        diversified = diversify_results(sample_search_results, max_per_client=1)

        # Find JPMC story in results
        jpmc_stories = [r for r in diversified if r.get("Client") == "JPMC"]
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
            {**sample_stories[0], "score": 0.9, "Client": "ClientA"},
            {**sample_stories[1], "score": 0.8, "Client": "ClientB"},
            {**sample_stories[2], "score": 0.7, "Client": "ClientC"},
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

    def test_creates_file_with_headers(self, tmp_path):
        """Should create file with headers if it doesn't exist."""
        try:
            from ui.pages.ask_mattgpt.backend_service import log_offdomain
        except ImportError:
            pytest.skip("log_offdomain not available")

        csv_path = tmp_path / "new_offdomain.csv"
        log_offdomain("first query", "rule:profanity", path=str(csv_path))

        content = csv_path.read_text()
        lines = content.strip().split("\n")

        # Should have header + 1 data row
        assert len(lines) == 2
        assert "ts_utc" in lines[0]
        assert "query" in lines[0]
        assert "reason" in lines[0]

    def test_appends_to_existing_file(self, tmp_path):
        """Should append to existing file without adding new headers."""
        try:
            from ui.pages.ask_mattgpt.backend_service import log_offdomain
        except ImportError:
            pytest.skip("log_offdomain not available")

        csv_path = tmp_path / "append_test.csv"

        # Log first query
        log_offdomain("query 1", "reason 1", path=str(csv_path))

        # Log second query
        log_offdomain("query 2", "reason 2", path=str(csv_path))

        content = csv_path.read_text()
        lines = content.strip().split("\n")

        # Should have 1 header + 2 data rows
        assert len(lines) == 3
        assert "query 1" in content
        assert "query 2" in content


class TestIsQueryOnTopicLLM:
    """Tests for is_query_on_topic_llm() LLM-based classification."""

    def test_accepts_professional_queries(self):
        """Should return True for queries about professional work."""
        try:
            from ui.pages.ask_mattgpt.backend_service import is_query_on_topic_llm
        except ImportError:
            pytest.skip("is_query_on_topic_llm not available")

        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="YES"))]
            )

            result = is_query_on_topic_llm("Tell me about agile transformation")
            assert result is True

    def test_rejects_offtopic_queries(self):
        """Should return False for off-topic queries."""
        try:
            from ui.pages.ask_mattgpt.backend_service import is_query_on_topic_llm
        except ImportError:
            pytest.skip("is_query_on_topic_llm not available")

        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="NO"))]
            )

            result = is_query_on_topic_llm("What's the weather today?")
            assert result is False

    def test_fails_open_on_error(self):
        """Should return True (fail-open) if API call fails."""
        try:
            from ui.pages.ask_mattgpt.backend_service import is_query_on_topic_llm
        except ImportError:
            pytest.skip("is_query_on_topic_llm not available")

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai_class.side_effect = Exception("API Error")

            result = is_query_on_topic_llm("any query")
            assert result is True  # Fail-open behavior


class TestGenerateAgyResponse:
    """Tests for _generate_agy_response() function."""

    def test_generates_agy_voiced_response(self, sample_stories):
        """Should generate response with Agy voice characteristics."""
        try:
            from ui.pages.ask_mattgpt.backend_service import _generate_agy_response
        except ImportError:
            pytest.skip("_generate_agy_response not available")

        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_response = "🐾 Let me show you Matt's platform work at JPMC..."
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content=mock_response))]
            )

            response = _generate_agy_response(
                "Tell me about platform work",
                sample_stories[:3],
                "fallback context",
            )

            assert "🐾" in response
            assert isinstance(response, str)

    def test_uses_fallback_on_api_failure(self, sample_stories):
        """Should use fallback context if OpenAI API fails."""
        try:
            from ui.pages.ask_mattgpt.backend_service import _generate_agy_response
        except ImportError:
            pytest.skip("_generate_agy_response not available")

        with patch("openai.OpenAI") as mock_openai_class:
            mock_openai_class.side_effect = Exception("API Error")

            fallback = "This is fallback context"
            response = _generate_agy_response(
                "test query", sample_stories[:3], fallback
            )

            assert fallback in response
            assert "🐾" in response


class TestSendToBackend:
    """Tests for send_to_backend() legacy wrapper."""

    def test_delegates_to_rag_answer(self, sample_stories, mock_streamlit):
        """Should delegate to rag_answer() function."""
        try:
            from ui.pages.ask_mattgpt.backend_service import (
                rag_answer,
                send_to_backend,
            )
        except ImportError:
            pytest.skip("send_to_backend not available")

        with patch(
            "ui.pages.ask_mattgpt.backend_service.rag_answer"
        ) as mock_rag_answer:
            mock_rag_answer.return_value = {
                "answer_md": "test",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

            result = send_to_backend(
                prompt="test", filters={}, ctx=None, stories=sample_stories
            )

            # Should have called rag_answer with correct args (ctx dropped)
            mock_rag_answer.assert_called_once_with("test", {}, sample_stories)
            assert result["answer_md"] == "test"


class TestRAGAnswer:
    """Tests for rag_answer() integration."""

    @pytest.mark.integration
    def test_returns_response_dict(self, sample_stories, mock_streamlit):
        """Should return a dictionary with expected keys."""
        try:
            from ui.pages.ask_mattgpt.backend_service import rag_answer
        except ImportError:
            pytest.skip("rag_answer not available")

        # This test requires mocking OpenAI
        with patch("openai.OpenAI") as mock_openai_class:
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test response"))]
            )

            result = rag_answer(
                question="Tell me about payments", filters={}, stories=sample_stories
            )

            assert isinstance(result, dict)
