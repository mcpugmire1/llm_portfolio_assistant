"""
Unit tests for utils/scoring.py

Tests for hybrid scoring functionality combining semantic similarity
with keyword-based overlap scoring.

Keyword-score stories come from the corpus via load_stories(), picked by
field value, so the tests read the fields production reads.
"""

import pytest

from utils.corpus_loader import load_stories
from utils.validation import _tokenize


@pytest.fixture(scope="module")
def stories():
    return load_stories("echo_star_stories_nlp.jsonl")


def _toks(*texts):
    return set(_tokenize(" ".join(texts)))


class TestKeywordScoreForStory:
    """Tests for _keyword_score_for_story() function."""

    def test_perfect_match_returns_high_score(self, stories):
        """Should return high score for perfect keyword match."""
        from utils.scoring import _keyword_score_for_story

        story = stories[0]
        score = _keyword_score_for_story(story, story["Title"])
        assert score > 0.8  # Should be high due to all tokens matching

    def test_no_match_returns_zero(self, stories):
        """Should return 0.0 for no keyword overlap."""
        from utils.scoring import _keyword_score_for_story

        score = _keyword_score_for_story(stories[0], "zzzsentinel qqqsentinel")
        assert score == 0.0

    def test_partial_match_returns_proportional_score(self, stories):
        """Should return proportional score for partial match."""
        from utils.scoring import _keyword_score_for_story

        story = stories[0]
        # Only the title token matches
        title_tok = _tokenize(story["Title"])[0]
        score = _keyword_score_for_story(story, f"{title_tok} zzzsentinel qqqsentinel")
        assert 0.0 < score < 1.0

    def test_title_domain_weighted_twice(self, stories):
        """Should weight title and domain matches twice."""
        from utils.scoring import _keyword_score_for_story

        # Match in title should score higher than match elsewhere
        story_title = stories[0]
        token = _tokenize(story_title["Title"])[0]
        story_other = next(
            s
            for s in stories
            if token in _toks(*s["Process"], *s["Performance"])
            and token not in _toks(s["Title"], s["Sub-category"])
        )

        score_title = _keyword_score_for_story(story_title, token)
        score_other = _keyword_score_for_story(story_other, token)

        assert score_title >= score_other

    def test_searches_competencies_field(self, stories):
        """Should search Competencies list."""
        from utils.scoring import _keyword_score_for_story

        story = stories[0]
        query = " ".join(_tokenize(" ".join(story["Competencies"]))[:2])
        score = _keyword_score_for_story(story, query)
        assert score > 0.0

    def test_searches_public_tags(self, stories):
        """Should search public_tags list."""
        from utils.scoring import _keyword_score_for_story

        story = stories[0]
        query = " ".join(_tokenize(" ".join(story["public_tags"]))[:2])
        score = _keyword_score_for_story(story, query)
        assert score > 0.0

    def test_searches_process_and_performance(self, stories):
        """Should search Process and Performance lists."""
        from utils.scoring import _keyword_score_for_story

        story = stories[0]
        process_tok = _tokenize(" ".join(story["Process"]))[0]
        performance_tok = _tokenize(" ".join(story["Performance"]))[0]
        score = _keyword_score_for_story(story, f"{process_tok} {performance_tok}")
        assert score > 0.0

    def test_uses_5p_summary(self, stories):
        """Should search the curated 5PSummary text."""
        from utils.formatting import build_5p_summary
        from utils.scoring import _keyword_score_for_story

        # A token of the summary text the scorer reads (build_5p_summary(s, 400),
        # which cuts longer 5PSummary text) that no other scored field holds
        def only_in_summary(s):
            others = _toks(
                s["Title"],
                s["Client"],
                s["Role"],
                s["Sub-category"],
                *s["Competencies"],
                *s["public_tags"],
                *s["Process"],
                *s["Performance"],
            )
            return sorted(_toks(build_5p_summary(s, 400)) - others)

        story = next(s for s in stories if only_in_summary(s))
        score = _keyword_score_for_story(story, only_in_summary(story)[0])
        assert score > 0.0

    def test_empty_query_returns_zero(self, stories):
        """Should return 0.0 for empty query."""
        from utils.scoring import _keyword_score_for_story

        assert _keyword_score_for_story(stories[0], "") == 0.0

    def test_handles_missing_fields(self):
        """Should handle missing fields gracefully."""
        from utils.scoring import _keyword_score_for_story

        story = {}
        score = _keyword_score_for_story(story, "some query")
        assert score == 0.0  # No fields to match

    def test_normalizes_to_max_1_0(self, stories):
        """Should cap score at 1.0."""
        from utils.scoring import _keyword_score_for_story

        story = stories[0]
        score = _keyword_score_for_story(story, story["Title"])
        assert score <= 1.0


class TestHybridScore:
    """Tests for _hybrid_score() function."""

    def test_default_weights_use_semantic_only(self):
        """Should blend scores with default weights (W_PC=1.0, W_KW=0.15)."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, 0.6)
        assert result == 0.89  # 0.8 * 1.0 + 0.6 * 0.15 = 0.89

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
        assert result == 0.09  # pc=0.0, kw=0.6: 0.0 * 1.0 + 0.6 * 0.15 = 0.09

    def test_handles_none_kw_score(self):
        """Should handle None kw_score gracefully."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score(0.8, None)
        assert result == 0.8  # kw defaults to 0.0, w_kw=0.0

    def test_handles_invalid_pc_score_type(self):
        """Should handle invalid types for pc_score."""
        from utils.scoring import _hybrid_score

        result = _hybrid_score("invalid", 0.5)
        assert result == 0.075  # pc=0.0, kw=0.5: 0.0 * 1.0 + 0.5 * 0.15 = 0.075

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
        assert W_KW == 0.15  # Keyword weight (raised from 0.0 Aug 8, 2026 -- f5641e7)

    def test_weights_have_single_source(self):
        """W_KW and W_PC must be the same object in all consumers.

        Regression guard for MATTGPT-175: pinecone_service.py previously
        defined W_KW=0.0 locally while scoring.py ran at 0.15, causing the
        trace payload to report the wrong weight. Any redefinition will
        break this test.
        """
        from config.constants import W_KW as c_kw, W_PC as c_pc
        from services.pinecone_service import W_KW as p_kw, W_PC as p_pc
        from utils.scoring import W_KW as s_kw, W_PC as s_pc

        assert c_kw == s_kw == p_kw
        assert c_pc == s_pc == p_pc
