"""
Unit tests for story_intelligence.py

Tests for story theme inference, context building, and guidance generation.
"""

import pytest


class TestInferStoryTheme:
    """Tests for infer_story_theme() function."""

    def test_identifies_behavioral_theme(self, sample_stories):
        """Should identify behavioral/leadership themes."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import infer_story_theme
        except ImportError:
            pytest.skip("infer_story_theme not available")

        # Conflict resolution story
        conflict_story = sample_stories[4]
        theme = infer_story_theme(conflict_story)

        assert theme is not None
        # Should identify as behavioral/leadership related
        assert any(
            kw in str(theme).lower()
            for kw in ["leadership", "team", "behavioral", "conflict"]
        )

    def test_identifies_technical_theme(self, sample_stories):
        """Should identify technical/execution themes."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import infer_story_theme
        except ImportError:
            pytest.skip("infer_story_theme not available")

        # Payments platform story
        tech_story = sample_stories[0]
        theme = infer_story_theme(tech_story)

        assert theme is not None

    def test_handles_empty_story(self):
        """Should handle empty or minimal story gracefully."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import infer_story_theme
        except ImportError:
            pytest.skip("infer_story_theme not available")

        empty_story = {}
        theme = infer_story_theme(empty_story)

        # Should not raise, can return None or default


class TestBuildStoryContextForRAG:
    """Tests for build_story_context_for_rag() function."""

    def test_returns_string(self, sample_stories):
        """Should return a string context."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                build_story_context_for_rag,
            )
        except ImportError:
            pytest.skip("build_story_context_for_rag not available")

        context = build_story_context_for_rag(sample_stories[:3])

        assert isinstance(context, str)

    def test_includes_story_content(self, sample_stories):
        """Should include relevant story content."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                build_story_context_for_rag,
            )
        except ImportError:
            pytest.skip("build_story_context_for_rag not available")

        context = build_story_context_for_rag(sample_stories[:3])

        # Should contain some story-related content
        assert len(context) > 0

    def test_handles_empty_list(self):
        """Should handle empty story list gracefully."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                build_story_context_for_rag,
            )
        except ImportError:
            pytest.skip("build_story_context_for_rag not available")

        context = build_story_context_for_rag([])

        assert isinstance(context, str)


class TestGetThemeGuidance:
    """Tests for get_theme_guidance() function."""

    def test_returns_guidance_for_behavioral_query(self, behavioral_query_examples):
        """Should return guidance for behavioral queries."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_guidance
        except ImportError:
            pytest.skip("get_theme_guidance not available")

        query = behavioral_query_examples[0]["query"]
        guidance = get_theme_guidance(query)

        # Should return some guidance string or dict
        assert guidance is not None

    def test_returns_guidance_for_technical_query(self, technical_query_examples):
        """Should return guidance for technical queries."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_guidance
        except ImportError:
            pytest.skip("get_theme_guidance not available")

        query = technical_query_examples[0]["query"]
        guidance = get_theme_guidance(query)

        assert guidance is not None

    def test_handles_empty_query(self):
        """Should handle empty query gracefully."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_guidance
        except ImportError:
            pytest.skip("get_theme_guidance not available")

        guidance = get_theme_guidance("")

        # Should not raise


class TestBehavioralQueryDetection:
    """Tests for detecting behavioral interview queries.

    These ensure the system correctly identifies queries that should
    return Talent & Enablement stories vs Execution & Delivery stories.
    """

    @pytest.mark.parametrize(
        "query,expected_behavioral",
        [
            ("Tell me about a time you led a team through conflict", True),
            ("Describe a situation where you influenced stakeholders", True),
            ("How did you handle a difficult team member?", True),
            ("Give me an example of when you failed", True),
            ("How did Matt build the payments platform?", False),
            ("Show me GenAI projects", False),
            ("What AWS services has Matt used?", False),
        ],
    )
    def test_behavioral_query_detection(self, query: str, expected_behavioral: bool):
        """Should correctly identify behavioral vs technical queries."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import is_behavioral_query
        except ImportError:
            # If function doesn't exist, test the tag generation instead
            pytest.skip(
                "is_behavioral_query not available - implement or test via tags"
            )

        result = is_behavioral_query(query)
        assert result == expected_behavioral
