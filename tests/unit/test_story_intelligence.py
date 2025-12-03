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

        # Conflict resolution story (has "Team Leadership" subcategory -> "Talent & Enablement" theme)
        conflict_story = sample_stories[4]
        theme = infer_story_theme(conflict_story)

        assert theme is not None
        assert isinstance(theme, str)
        # Should identify as Talent & Enablement theme
        assert "talent" in theme.lower() or "enablement" in theme.lower()

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

        context = build_story_context_for_rag(sample_stories[0])

        assert isinstance(context, str)

    def test_includes_story_content(self, sample_stories):
        """Should include relevant story content."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                build_story_context_for_rag,
            )
        except ImportError:
            pytest.skip("build_story_context_for_rag not available")

        context = build_story_context_for_rag(sample_stories[0])

        # Should contain some story-related content
        assert len(context) > 0

    def test_handles_empty_story(self):
        """Should handle empty story dict gracefully."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                build_story_context_for_rag,
            )
        except ImportError:
            pytest.skip("build_story_context_for_rag not available")

        context = build_story_context_for_rag({})

        assert isinstance(context, str)


class TestGetThemeGuidance:
    """Tests for get_theme_guidance() function."""

    def test_returns_guidance_for_theme(self):
        """Should return guidance string for a valid theme."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_guidance
        except ImportError:
            pytest.skip("get_theme_guidance not available")

        guidance = get_theme_guidance("Talent & Enablement")

        # Should return some guidance string
        assert guidance is not None
        assert isinstance(guidance, str)
        assert len(guidance) > 0

    def test_returns_default_for_unknown_theme(self):
        """Should return default guidance for unknown theme."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_guidance
        except ImportError:
            pytest.skip("get_theme_guidance not available")

        guidance = get_theme_guidance("Unknown Theme")

        # Should still return something (default to Execution & Delivery)
        assert guidance is not None
        assert isinstance(guidance, str)

    def test_guidance_contains_theme_specifics(self):
        """Guidance should contain theme-specific keywords."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_guidance
        except ImportError:
            pytest.skip("get_theme_guidance not available")

        # Check that each theme has distinct guidance
        talent_guidance = get_theme_guidance("Talent & Enablement")
        assert (
            "capability" in talent_guidance.lower()
            or "mentorship" in talent_guidance.lower()
        )

        execution_guidance = get_theme_guidance("Execution & Delivery")
        assert (
            "delivery" in execution_guidance.lower()
            or "production" in execution_guidance.lower()
        )

        emerging_guidance = get_theme_guidance("Emerging Tech")
        assert (
            "innovation" in emerging_guidance.lower()
            or "emerging" in emerging_guidance.lower()
        )


class TestGetAllThemes:
    """Tests for get_all_themes() function."""

    def test_returns_list_of_six_themes(self):
        """Should return all 6 canonical themes."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_all_themes
        except ImportError:
            pytest.skip("get_all_themes not available")

        themes = get_all_themes()

        assert isinstance(themes, list)
        assert len(themes) == 6

    def test_themes_are_strings(self):
        """All themes should be strings."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_all_themes
        except ImportError:
            pytest.skip("get_all_themes not available")

        themes = get_all_themes()

        for theme in themes:
            assert isinstance(theme, str)
            assert len(theme) > 0


class TestGetThemeDistribution:
    """Tests for get_theme_distribution() function."""

    def test_counts_themes_correctly(self, sample_stories):
        """Should count theme occurrences across stories."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_distribution
        except ImportError:
            pytest.skip("get_theme_distribution not available")

        distribution = get_theme_distribution(sample_stories)

        # Should return a dictionary
        assert isinstance(distribution, dict)

        # Should have counts for themes present in sample data
        assert "Execution & Delivery" in distribution
        assert "Talent & Enablement" in distribution

        # Counts should be positive integers
        for count in distribution.values():
            assert isinstance(count, int)
            assert count > 0

    def test_empty_list_returns_empty_dict(self):
        """Should handle empty story list."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_distribution
        except ImportError:
            pytest.skip("get_theme_distribution not available")

        distribution = get_theme_distribution([])

        assert isinstance(distribution, dict)
        assert len(distribution) == 0

    def test_all_same_theme(self):
        """Should handle stories all from one theme."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_distribution
        except ImportError:
            pytest.skip("get_theme_distribution not available")

        stories = [
            {"Sub-category": "Platform Engineering"},
            {"Sub-category": "Platform Engineering"},
            {"Sub-category": "Cloud-Native Architecture"},
        ]

        distribution = get_theme_distribution(stories)

        # All should map to Execution & Delivery
        assert distribution["Execution & Delivery"] == 3
        assert len(distribution) == 1


class TestGetThemeEmoji:
    """Tests for get_theme_emoji() function."""

    def test_returns_emoji_for_each_theme(self):
        """Should return emoji for all 6 themes."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                get_all_themes,
                get_theme_emoji,
            )
        except ImportError:
            pytest.skip("get_theme_emoji not available")

        themes = get_all_themes()

        for theme in themes:
            emoji = get_theme_emoji(theme)
            assert isinstance(emoji, str)
            assert len(emoji) > 0

    def test_returns_default_for_unknown_theme(self):
        """Should return default emoji for unknown theme."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import get_theme_emoji
        except ImportError:
            pytest.skip("get_theme_emoji not available")

        emoji = get_theme_emoji("Unknown Theme")

        # Should return default (Execution theme emoji)
        assert isinstance(emoji, str)
        assert emoji == "🏗️"

    def test_emojis_are_unique(self):
        """Each theme should have a distinct emoji."""
        try:
            from ui.pages.ask_mattgpt.story_intelligence import (
                get_all_themes,
                get_theme_emoji,
            )
        except ImportError:
            pytest.skip("get_theme_emoji not available")

        themes = get_all_themes()
        emojis = [get_theme_emoji(theme) for theme in themes]

        # All emojis should be unique
        assert len(set(emojis)) == len(emojis)
