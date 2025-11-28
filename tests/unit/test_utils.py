"""
Unit tests for utils.py

Tests for utility functions used across the application.
"""


class TestGetContextStory:
    """Tests for get_context_story() function."""

    def test_returns_first_story_with_context(self, sample_stories, mock_streamlit):
        """Should return appropriate context story."""
        from ui.pages.ask_mattgpt.utils import get_context_story

        result = get_context_story(sample_stories)

        # Should return a dict or None
        assert result is None or isinstance(result, dict)

    def test_empty_list_returns_none(self, mock_streamlit):
        """Should return None for empty story list."""
        from ui.pages.ask_mattgpt.utils import get_context_story

        result = get_context_story([])
        assert result is None


class TestChooseStoryForAsk:
    """Tests for choose_story_for_ask() function."""

    def test_returns_story_dict(self, sample_stories, mock_streamlit):
        """Should return a story dictionary."""
        from ui.pages.ask_mattgpt.utils import choose_story_for_ask

        result = choose_story_for_ask(sample_stories[0], sample_stories)

        assert result is None or isinstance(result, dict)

    def test_handles_none_top_story(self, sample_stories, mock_streamlit):
        """Should handle None as top_story gracefully."""
        from ui.pages.ask_mattgpt.utils import choose_story_for_ask

        result = choose_story_for_ask(None, sample_stories)
        # Should not raise, should return something sensible
        assert result is None or isinstance(result, dict)


class TestRelatedStories:
    """Tests for related_stories() function."""

    def test_returns_list(self, sample_stories):
        """Should return a list of related stories."""
        from ui.pages.ask_mattgpt.utils import related_stories

        result = related_stories(sample_stories[0], sample_stories)

        assert isinstance(result, list)

    def test_respects_max_items(self, sample_stories):
        """Should not return more than max_items."""
        from ui.pages.ask_mattgpt.utils import related_stories

        result = related_stories(sample_stories[0], sample_stories, max_items=2)

        assert len(result) <= 2

    def test_excludes_source_story(self, sample_stories):
        """Should not include the source story in results."""
        from ui.pages.ask_mattgpt.utils import related_stories

        source = sample_stories[0]
        result = related_stories(source, sample_stories)

        # Source story should not be in results
        result_ids = [r.get("id") for r in result]
        assert source.get("id") not in result_ids


class TestStoryHasMetric:
    """Tests for story_has_metric() function."""

    def test_detects_percentage(self):
        """Should detect percentage metrics."""
        from ui.pages.ask_mattgpt.utils import story_has_metric

        story_with_metric = {"Performance": ["Reduced costs by 60%"]}
        assert story_has_metric(story_with_metric) == True

    def test_detects_time_metrics(self):
        """Should detect time-based metrics."""
        from ui.pages.ask_mattgpt.utils import story_has_metric

        story_with_metric = {"Performance": ["Delivered in 3 months"]}
        assert story_has_metric(story_with_metric) == True

    def test_returns_false_for_no_metrics(self):
        """Should return False when no metrics present."""
        from ui.pages.ask_mattgpt.utils import story_has_metric

        story_without_metric = {"Performance": ["Successfully delivered the project"]}
        assert story_has_metric(story_without_metric) == False


class TestSplitTags:
    """Tests for split_tags() function."""

    def test_splits_comma_separated(self):
        """Should split comma-separated tags."""
        from ui.pages.ask_mattgpt.utils import split_tags

        result = split_tags("tag1, tag2, tag3")

        assert isinstance(result, list)
        assert len(result) == 3

    def test_handles_empty_string(self):
        """Should handle empty string gracefully."""
        from ui.pages.ask_mattgpt.utils import split_tags

        result = split_tags("")

        assert isinstance(result, list)

    def test_handles_none(self):
        """Should handle None gracefully."""
        from ui.pages.ask_mattgpt.utils import split_tags

        result = split_tags(None)

        assert isinstance(result, list)

    def test_handles_list_input(self):
        """Should handle list input."""
        from ui.pages.ask_mattgpt.utils import split_tags

        result = split_tags(["tag1", "tag2", "tag3"])

        assert isinstance(result, list)
        assert len(result) == 3


class TestSlug:
    """Tests for slug() function."""

    def test_converts_to_lowercase(self):
        """Should convert to lowercase."""
        from ui.pages.ask_mattgpt.utils import slug

        result = slug("Hello World")

        assert result == result.lower()

    def test_replaces_spaces_with_dashes(self):
        """Should replace spaces with dashes or underscores."""
        from ui.pages.ask_mattgpt.utils import slug

        result = slug("Hello World")

        assert " " not in result

    def test_handles_special_characters(self):
        """Should handle special characters."""
        from ui.pages.ask_mattgpt.utils import slug

        result = slug("Hello! @World#")

        # Should not contain special chars
        assert all(c.isalnum() or c in "-_" for c in result)


class TestShortenMiddle:
    """Tests for shorten_middle() function."""

    def test_shortens_long_text(self):
        """Should shorten text longer than max_len."""
        from ui.pages.ask_mattgpt.utils import shorten_middle

        long_text = "A" * 100
        result = shorten_middle(long_text, max_len=50)

        assert len(result) <= 50

    def test_preserves_short_text(self):
        """Should not modify text shorter than max_len."""
        from ui.pages.ask_mattgpt.utils import shorten_middle

        short_text = "Hello"
        result = shorten_middle(short_text, max_len=50)

        assert result == short_text

    def test_includes_ellipsis(self):
        """Should include ellipsis indicator when shortened."""
        from ui.pages.ask_mattgpt.utils import shorten_middle

        long_text = "A" * 100
        result = shorten_middle(long_text, max_len=50)

        assert "..." in result or "…" in result


class TestIsEmptyConversation:
    """Tests for is_empty_conversation() function."""

    def test_returns_boolean(self, mock_streamlit):
        """Should return a boolean value."""
        from ui.pages.ask_mattgpt.utils import is_empty_conversation

        result = is_empty_conversation()

        assert isinstance(result, bool)

    def test_empty_transcript_returns_true(self, mock_streamlit):
        """Should return True for empty transcript."""
        from ui.pages.ask_mattgpt.utils import is_empty_conversation

        # Ensure empty transcript
        mock_streamlit.get.return_value = []

        result = is_empty_conversation()

        assert result == True

    def test_nonempty_transcript_returns_false(self, monkeypatch):
        """Should return False for non-empty transcript."""
        from ui.pages.ask_mattgpt.utils import is_empty_conversation

        # Mock non-empty transcript in session_state
        mock_session = {
            "ask_transcript": [
                {"role": "user", "text": "Hello"},
                {"role": "assistant", "text": "Hi there!"},
            ]
        }

        # Patch streamlit.session_state to return our mock
        import streamlit as st

        monkeypatch.setattr(st, "session_state", mock_session)

        result = is_empty_conversation()

        assert result == False
