"""
Unit tests for utils/scoring.py

Tests for hybrid scoring functionality combining semantic similarity
with keyword-based overlap scoring.
"""


class TestKeywordScoreForStory:
    """Tests for _keyword_score_for_story() function."""

    def test_perfect_match_returns_high_score(self):
        """Should return high score for perfect keyword match."""
        from utils.scoring import _keyword_score_for_story

        story = {
            "Title": "Platform Modernization",
            "Client": "JPMC",
            "Sub-category": "Platform Engineering",
        }
        score = _keyword_score_for_story(story, "platform modernization jpmc")
        assert score > 0.8  # Should be high due to all tokens matching

    def test_no_match_returns_zero(self):
        """Should return 0.0 for no keyword overlap."""
        from utils.scoring import _keyword_score_for_story

        story = {"Title": "Platform Modernization", "Client": "JPMC"}
        score = _keyword_score_for_story(story, "unrelated query terms")
        assert score == 0.0

    def test_partial_match_returns_proportional_score(self):
        """Should return proportional score for partial match."""
        from utils.scoring import _keyword_score_for_story

        story = {"Title": "Platform Modernization", "Client": "JPMC"}
        # Only "platform" matches
        score = _keyword_score_for_story(story, "platform database migration")
        assert 0.0 < score < 1.0

    def test_title_domain_weighted_twice(self):
        """Should weight title and domain matches twice."""
        from utils.scoring import _keyword_score_for_story

        # Match in title should score higher than match elsewhere
        story_title = {"Title": "Platform Engineering", "Client": "Other"}
        story_other = {"Title": "Other", "Role": "Platform Engineering"}

        score_title = _keyword_score_for_story(story_title, "platform")
        score_other = _keyword_score_for_story(story_other, "platform")

        assert score_title >= score_other

    def test_searches_competencies_field(self):
        """Should search Competencies list."""
        from utils.scoring import _keyword_score_for_story

        story = {"Competencies": ["Python", "AWS", "Docker"]}
        score = _keyword_score_for_story(story, "python aws")
        assert score > 0.0

    def test_searches_public_tags(self):
        """Should search public_tags list."""
        from utils.scoring import _keyword_score_for_story

        story = {"public_tags": ["agile", "transformation", "leadership"]}
        score = _keyword_score_for_story(story, "agile transformation")
        assert score > 0.0

    def test_searches_process_and_performance(self):
        """Should search Process and Performance lists."""
        from utils.scoring import _keyword_score_for_story

        story = {
            "Process": ["Migrated to microservices"],
            "Performance": ["Reduced latency by 60%"],
        }
        score = _keyword_score_for_story(story, "microservices latency")
        assert score > 0.0

    def test_uses_5p_summary(self):
        """Should search 5P summary text."""
        from utils.scoring import _keyword_score_for_story

        story = {"why": "Modernize legacy platform", "how": ["Migrated to AWS"]}
        # build_5p_summary will create summary text
        score = _keyword_score_for_story(story, "modernize legacy")
        assert score > 0.0

    def test_empty_query_returns_zero(self):
        """Should return 0.0 for empty query."""
        from utils.scoring import _keyword_score_for_story

        story = {"Title": "Some Story"}
        assert _keyword_score_for_story(story, "") == 0.0

    def test_handles_missing_fields(self):
        """Should handle missing fields gracefully."""
        from utils.scoring import _keyword_score_for_story

        story = {}
        score = _keyword_score_for_story(story, "some query")
        assert score == 0.0  # No fields to match

    def test_normalizes_to_max_1_0(self):
        """Should cap score at 1.0."""
        from utils.scoring import _keyword_score_for_story

        story = {
            "Title": "test test test",
            "Client": "test",
            "Sub-category": "test",
        }
        score = _keyword_score_for_story(story, "test")
        assert score <= 1.0


class TestHybridScore:
    """Tests for _hybrid_score() function."""

    def test_default_weights_use_semantic_only(self):
        """Should use only Pinecone score with default weights (1.0, 0.0)."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, 0.6)
        assert result == 0.8  # w_pc=1.0, w_kw=0.0 -> only pc_score

    def test_custom_weights_blend_scores(self):
        """Should blend scores with custom weights."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, 0.6, w_pc=0.5, w_kw=0.5)
        expected = (0.8 * 0.5) + (0.6 * 0.5)
        assert result == expected  # 0.7

    def test_handles_none_pc_score(self):
        """Should handle None pc_score gracefully."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(None, 0.6)
        assert result == 0.0  # None defaults to 0.0

    def test_handles_none_kw_score(self):
        """Should handle None kw_score gracefully."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, None)
        assert result == 0.8  # kw defaults to 0.0, w_kw=0.0

    def test_handles_invalid_pc_score_type(self):
        """Should handle invalid types for pc_score."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score("invalid", 0.5)
        assert result == 0.0  # Invalid defaults to 0.0

    def test_handles_invalid_kw_score_type(self):
        """Should handle invalid types for kw_score."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, "invalid")
        assert result == 0.8  # Invalid kw defaults to 0.0

    def test_both_zero_returns_zero(self):
        """Should return 0.0 when both scores are zero."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.0, 0.0)
        assert result == 0.0

    def test_both_one_with_equal_weights(self):
        """Should return 1.0 when both scores are 1.0 and weights sum to 1."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(1.0, 1.0, w_pc=0.6, w_kw=0.4)
        expected = (1.0 * 0.6) + (1.0 * 0.4)
        assert result == expected  # 1.0

    def test_keyword_only_weighting(self):
        """Should support keyword-only weighting (w_pc=0, w_kw=1)."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, 0.6, w_pc=0.0, w_kw=1.0)
        assert result == 0.6  # Only keyword score

    def test_weighted_sum_formula(self):
        """Should follow weighted sum formula correctly."""
        from utils.scoring import _hybrid_score

        pc, kw = 0.7, 0.4
        w_pc, w_kw = 0.8, 0.2

        result = _hybrid_score(pc, kw, w_pc=w_pc, w_kw=w_kw)
        expected = (pc * w_pc) + (kw * w_kw)

        assert result == expected  # (0.7 * 0.8) + (0.4 * 0.2) = 0.64


class TestScoringConstants:
    """Tests for scoring weight constants."""

    def test_default_weights_defined(self):
        """Should define W_PC and W_KW constants."""
        from utils.scoring import W_KW, W_PC

        assert isinstance(W_PC, float)
        assert isinstance(W_KW, float)

    def test_default_weights_favor_semantic(self):
        """Should favor semantic search by default (W_PC > W_KW)."""
        from utils.scoring import W_KW, W_PC

        assert W_PC >= W_KW  # Semantic preferred or equal
        assert W_PC == 1.0  # Full semantic weight
        assert W_KW == 0.0  # Keyword disabled by default
