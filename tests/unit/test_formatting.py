"""
Unit tests for utils/formatting.py

Tests for story formatting utilities including metric detection,
summary generation, and presentation mode formatting.
"""


class TestStoryHasMetric:
    """Tests for story_has_metric() function."""

    def test_detects_percentage_in_what(self):
        """Should detect percentage metrics in 'what' field."""
        from utils.formatting import story_has_metric

        story = {"what": ["Reduced latency by 60%"]}
        assert story_has_metric(story) is True

    def test_detects_dollar_amount(self):
        """Should detect dollar amounts."""
        from utils.formatting import story_has_metric

        story = {"what": ["Saved $2.5M annually"]}
        assert story_has_metric(story) is True

    def test_detects_multiplier(self):
        """Should detect multiplier metrics (3x, 10x, etc.)."""
        from utils.formatting import story_has_metric

        story = {"what": ["Increased velocity 3x"]}
        assert story_has_metric(story) is True

    def test_detects_metric_in_star_result(self):
        """Should detect metrics in star.result field."""
        from utils.formatting import story_has_metric

        story = {"star": {"result": ["Reduced deployment time by 80%"]}}
        assert story_has_metric(story) is True

    def test_returns_false_for_no_metrics(self):
        """Should return False when no metrics present."""
        from utils.formatting import story_has_metric

        story = {"what": ["Improved team collaboration"]}
        assert story_has_metric(story) is False

    def test_handles_empty_story(self):
        """Should handle empty story dict."""
        from utils.formatting import story_has_metric

        assert story_has_metric({}) is False

    def test_handles_none_values(self):
        """Should handle None values in fields."""
        from utils.formatting import story_has_metric

        story = {"what": None, "star": {"result": None}}
        assert story_has_metric(story) is False


class TestStrongestMetricLine:
    """Tests for strongest_metric_line() function."""

    def test_returns_percentage_over_multiplier(self):
        """Should prioritize percentage metrics (get +1000 bonus)."""
        from utils.formatting import strongest_metric_line

        story = {"what": ["Deployed 3x faster", "Reduced cost by 50%"]}
        result = strongest_metric_line(story)
        assert result == "Reduced cost by 50%"

    def test_returns_highest_multiplier(self):
        """Should return highest multiplier when no percentages."""
        from utils.formatting import strongest_metric_line

        story = {"what": ["Deployed 3x faster", "Scaled to 10x capacity"]}
        result = strongest_metric_line(story)
        assert result == "Scaled to 10x capacity"

    def test_searches_star_result_field(self):
        """Should search star.result field."""
        from utils.formatting import strongest_metric_line

        story = {"star": {"result": ["Reduced latency by 75%"]}}
        result = strongest_metric_line(story)
        assert result == "Reduced latency by 75%"

    def test_returns_none_for_no_metrics(self):
        """Should return None when no metrics found."""
        from utils.formatting import strongest_metric_line

        story = {"what": ["Improved collaboration"]}
        assert strongest_metric_line(story) is None

    def test_handles_empty_story(self):
        """Should handle empty story dict."""
        from utils.formatting import strongest_metric_line

        assert strongest_metric_line({}) is None


class TestBuild5PSummary:
    """Tests for build_5p_summary() function."""

    def test_uses_curated_5p_summary_if_present(self):
        """Should prefer curated 5PSummary field."""
        from utils.formatting import build_5p_summary

        story = {
            "5PSummary": "Curated summary text",
            "why": "Some goal",
            "how": ["Some approach"],
        }
        result = build_5p_summary(story)
        assert result == "Curated summary text"

    def test_uses_5p_summary_lowercase_field(self):
        """Should support lowercase 5p_summary field."""
        from utils.formatting import build_5p_summary

        story = {"5p_summary": "Lowercase field summary"}
        result = build_5p_summary(story)
        assert result == "Lowercase field summary"

    def test_builds_from_why_how_what_fields(self):
        """Should compose summary from why/how/what fields."""
        from utils.formatting import build_5p_summary

        story = {
            "why": "Modernize platform",
            "how": ["Migrated to AWS", "Implemented CI/CD"],
            "what": ["Reduced costs by 40%"],
        }
        result = build_5p_summary(story, max_chars=300)
        assert "**Goal:**" in result
        assert "Modernize platform" in result
        assert "**Approach:**" in result
        assert "Migrated to AWS" in result
        assert "**Outcome:**" in result
        assert "Reduced costs by 40%" in result

    def test_truncates_to_max_chars(self):
        """Should truncate output to max_chars with ellipsis."""
        from utils.formatting import build_5p_summary

        long_text = "A" * 300
        story = {"5PSummary": long_text}
        result = build_5p_summary(story, max_chars=50)
        assert len(result) <= 50
        assert result.endswith("…")

    def test_falls_back_to_generic_text(self):
        """Should provide generic fallback when fields missing."""
        from utils.formatting import build_5p_summary

        story = {}
        result = build_5p_summary(story)
        assert len(result) > 0  # Should return something

    def test_handles_empty_lists(self):
        """Should handle empty lists in how/what fields."""
        from utils.formatting import build_5p_summary

        story = {"why": "Goal text", "how": [], "what": []}
        result = build_5p_summary(story)
        assert "**Goal:**" in result
        assert "Goal text" in result


class TestFormatKeyPoints:
    """Tests for _format_key_points() function."""

    def test_includes_scope_section(self):
        """Should include Scope: title — client."""
        from utils.formatting import _format_key_points

        story = {"title": "Platform Modernization", "client": "JPMC"}
        result = _format_key_points(story)
        assert "**Scope:**" in result
        assert "Platform Modernization" in result
        assert "JPMC" in result

    def test_includes_approach_from_how(self):
        """Should include Approach from top 2 'how' bullets."""
        from utils.formatting import _format_key_points

        story = {"how": ["Migrated to AWS", "Implemented CI/CD", "Third item"]}
        result = _format_key_points(story)
        assert "**Approach:**" in result
        assert "Migrated to AWS" in result
        assert "Implemented CI/CD" in result
        assert "Third item" not in result  # Only first 2

    def test_includes_strongest_metric_in_outcome(self):
        """Should show strongest metric in Outcome."""
        from utils.formatting import _format_key_points

        story = {"what": ["Reduced cost by 50%", "Deployed 3x faster"]}
        result = _format_key_points(story)
        assert "**Outcome:**" in result
        assert "Reduced cost by 50%" in result

    def test_includes_domain_from_subcategory(self):
        """Should include Domain from Sub-category field."""
        from utils.formatting import _format_key_points

        story = {"Sub-category": "Platform Engineering"}
        result = _format_key_points(story)
        assert "**Domain:**" in result
        assert "Platform Engineering" in result

    def test_handles_missing_fields(self):
        """Should gracefully handle missing fields."""
        from utils.formatting import _format_key_points

        story = {}
        result = _format_key_points(story)
        assert isinstance(result, str)
        assert len(result) > 0


class TestFormatNarrative:
    """Tests for _format_narrative() function."""

    def test_creates_flowing_paragraph(self):
        """Should create narrative paragraph with structure."""
        from utils.formatting import _format_narrative

        story = {
            "Title": "Platform Modernization",
            "Client": "JPMC",
            "Sub-category": "Cloud-Native Architecture",
            "why": "Reduce infrastructure costs",
            "how": ["Migrated to AWS", "Implemented auto-scaling"],
            "what": ["Reduced costs by 40%"],
        }
        result = _format_narrative(story)
        assert "I led **Platform Modernization** at **JPMC**" in result
        assert "Cloud-Native Architecture" in result
        assert "reduce infrastructure costs" in result
        assert "migrated to aws" in result.lower()
        assert "Impact:" in result

    def test_handles_missing_title(self):
        """Should handle missing title gracefully."""
        from utils.formatting import _format_narrative

        story = {"Client": "JPMC"}
        result = _format_narrative(story)
        assert "JPMC" in result

    def test_lowercases_goal_and_approach(self):
        """Should lowercase 'why' and 'how' text for readability."""
        from utils.formatting import _format_narrative

        story = {
            "Title": "Test",
            "Client": "Client",
            "why": "UPPERCASE GOAL",
            "how": ["UPPERCASE APPROACH"],
        }
        result = _format_narrative(story)
        assert "uppercase goal" in result
        assert "uppercase approach" in result

    def test_falls_back_to_5p_summary(self):
        """Should fall back to 5P summary if insufficient fields."""
        from utils.formatting import _format_narrative

        story = {"5PSummary": "Fallback summary"}
        result = _format_narrative(story)
        assert "Fallback summary" in result


class TestFormatDeepDive:
    """Tests for _format_deep_dive() function."""

    def test_formats_full_star_structure(self):
        """Should format all STAR sections with friendly headers."""
        from utils.formatting import _format_deep_dive

        story = {
            "star": {
                "situation": ["Legacy monolith causing delays"],
                "task": ["Modernize to microservices"],
                "action": ["Migrated to AWS", "Implemented CI/CD"],
                "result": ["Reduced deployment time by 80%"],
            }
        }
        result = _format_deep_dive(story)
        assert "**What was happening**" in result
        assert "Legacy monolith causing delays" in result
        assert "**Goal**" in result
        assert "Modernize to microservices" in result
        assert "**What we did**" in result
        assert "Migrated to AWS" in result
        assert "**Results**" in result
        assert "Reduced deployment time by 80%" in result

    def test_formats_partial_star_structure(self):
        """Should handle missing STAR sections."""
        from utils.formatting import _format_deep_dive

        story = {"star": {"action": ["Did something"], "result": ["Got result"]}}
        result = _format_deep_dive(story)
        assert "**What we did**" in result
        assert "**Results**" in result
        assert "**What was happening**" not in result
        assert "**Goal**" not in result

    def test_uses_bullet_points(self):
        """Should format items as bullet points."""
        from utils.formatting import _format_deep_dive

        story = {"star": {"action": ["First action", "Second action"]}}
        result = _format_deep_dive(story)
        assert "- First action" in result
        assert "- Second action" in result

    def test_separates_sections_with_double_newlines(self):
        """Should separate sections with double newlines."""
        from utils.formatting import _format_deep_dive

        story = {
            "star": {
                "task": ["Goal"],
                "action": ["Action"],
            }
        }
        result = _format_deep_dive(story)
        assert "\n\n" in result

    def test_falls_back_to_5p_summary(self):
        """Should fall back to 5P summary if no STAR data."""
        from utils.formatting import _format_deep_dive

        story = {"5PSummary": "Fallback summary"}
        result = _format_deep_dive(story)
        assert "Fallback summary" in result

    def test_handles_empty_star_dict(self):
        """Should handle empty star dict."""
        from utils.formatting import _format_deep_dive

        story = {"star": {}}
        result = _format_deep_dive(story)
        assert isinstance(result, str)
        assert len(result) > 0


class TestExtractMetricValue:
    """Tests for _extract_metric_value() helper function."""

    def test_extracts_percentage(self):
        """Should extract percentage metrics."""
        from utils.formatting import _extract_metric_value

        result = _extract_metric_value("Reduced cost by 50%")
        assert result is not None
        score, text = result
        assert score > 1000  # Percentages get +1000 bonus
        assert text == "Reduced cost by 50%"

    def test_extracts_multiplier(self):
        """Should extract multiplier metrics."""
        from utils.formatting import _extract_metric_value

        result = _extract_metric_value("Deployed 3x faster")
        assert result is not None
        score, text = result
        assert score == 3.0
        assert text == "Deployed 3x faster"

    def test_extracts_dollar_amount(self):
        """Should extract dollar amounts."""
        from utils.formatting import _extract_metric_value

        result = _extract_metric_value("Saved $2.5M")
        assert result is not None

    def test_returns_none_for_no_metrics(self):
        """Should return None when no metrics found."""
        from utils.formatting import _extract_metric_value

        assert _extract_metric_value("No metrics here") is None

    def test_handles_empty_string(self):
        """Should handle empty string."""
        from utils.formatting import _extract_metric_value

        assert _extract_metric_value("") is None

    def test_returns_highest_metric_when_multiple(self):
        """Should return highest-scored metric from text."""
        from utils.formatting import _extract_metric_value

        # Percentage should win over multiplier
        result = _extract_metric_value("Deployed 3x faster with 50% cost reduction")
        assert result is not None
        score, _ = result
        assert score > 1000  # Percentage score
