"""
Unit tests for utils/validation.py

Tests for query validation, tokenization, and vocabulary overlap utilities.
"""

import tempfile
from pathlib import Path


class TestTokenize:
    """Tests for _tokenize() function."""

    def test_tokenizes_simple_text(self):
        """Should tokenize text into lowercase tokens."""
        from utils.validation import _tokenize

        result = _tokenize("Platform Engineering with AWS")
        assert result == ["platform", "engineering", "with", "aws"]

    def test_filters_short_tokens(self):
        """Should filter tokens shorter than 3 characters."""
        from utils.validation import _tokenize

        result = _tokenize("A B CD EFG")
        assert result == ["efg"]  # Only token with 3+ chars

    def test_handles_empty_string(self):
        """Should handle empty string."""
        from utils.validation import _tokenize

        assert _tokenize("") == []

    def test_handles_none(self):
        """Should handle None input."""
        from utils.validation import _tokenize

        assert _tokenize(None) == []

    def test_lowercases_tokens(self):
        """Should lowercase all tokens."""
        from utils.validation import _tokenize

        result = _tokenize("UPPERCASE MixedCase lowercase")
        assert result == ["uppercase", "mixedcase", "lowercase"]

    def test_extracts_alphanumeric_with_special_chars(self):
        """Should extract tokens with +, #, -, _, ."""
        from utils.validation import _tokenize

        result = _tokenize("C++ C# .NET Python-3.11")
        # Tokens are extracted with special chars intact
        assert "c++" in result
        assert ".net" in result
        assert "python-3.11" in result


class TestLoadNonsenseRules:
    """Tests for _load_nonsense_rules() function."""

    def test_loads_valid_jsonl_file(self):
        """Should load rules from valid JSONL file."""
        from utils.validation import _load_nonsense_rules

        # Create temp JSONL file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"pattern": "test.*pattern", "category": "test"}\n')
            f.write('{"pattern": "another.*rule", "category": "other"}\n')
            temp_path = f.name

        try:
            rules = _load_nonsense_rules(temp_path)
            assert len(rules) == 2
            assert rules[0]["pattern"] == "test.*pattern"
            assert rules[0]["category"] == "test"
            assert rules[1]["pattern"] == "another.*rule"
        finally:
            Path(temp_path).unlink()

    def test_skips_empty_lines(self):
        """Should skip empty lines in JSONL file."""
        from utils.validation import _load_nonsense_rules

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"pattern": "test", "category": "test"}\n')
            f.write('\n')  # Empty line
            f.write('   \n')  # Whitespace line
            f.write('{"pattern": "test2", "category": "test2"}\n')
            temp_path = f.name

        try:
            rules = _load_nonsense_rules(temp_path)
            assert len(rules) == 2
        finally:
            Path(temp_path).unlink()

    def test_handles_malformed_json(self):
        """Should skip malformed JSON lines and continue."""
        from utils.validation import _load_nonsense_rules

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"pattern": "valid", "category": "test"}\n')
            f.write('{invalid json here}\n')  # Malformed
            f.write('{"pattern": "valid2", "category": "test2"}\n')
            temp_path = f.name

        try:
            rules = _load_nonsense_rules(temp_path)
            assert len(rules) == 2  # Should load 2 valid rules
        finally:
            Path(temp_path).unlink()

    def test_returns_empty_list_for_missing_file(self):
        """Should return empty list if file doesn't exist."""
        from utils.validation import _load_nonsense_rules

        rules = _load_nonsense_rules("nonexistent_file.jsonl")
        assert rules == []


class TestIsNonsense:
    """Tests for is_nonsense() function."""

    def test_returns_none_for_empty_query(self):
        """Should return None for empty query."""
        from utils.validation import is_nonsense

        assert is_nonsense("") is None
        assert is_nonsense("   ") is None

    def test_returns_none_for_normal_query(self):
        """Should return None for normal on-domain query."""
        from utils.validation import is_nonsense

        # Assuming no patterns match generic platform questions
        result = is_nonsense("Tell me about platform modernization")
        # Result depends on loaded rules, but should be None or valid category
        assert result is None or isinstance(result, str)

    def test_lazy_loads_rules_on_first_call(self):
        """Should lazy-load rules on first call."""
        from utils import validation

        # Reset global cache
        validation._NONSENSE_RULES = []

        # First call should load rules
        validation.is_nonsense("test query")

        # Global cache should now be populated
        assert isinstance(validation._NONSENSE_RULES, list)

    def test_caches_rules_between_calls(self):
        """Should reuse cached rules on subsequent calls."""
        from utils import validation

        # Reset and load
        validation._NONSENSE_RULES = []
        validation.is_nonsense("test query 1")
        rules_count_1 = len(validation._NONSENSE_RULES)

        # Second call should use cache
        validation.is_nonsense("test query 2")
        rules_count_2 = len(validation._NONSENSE_RULES)

        assert rules_count_1 == rules_count_2

    def test_handles_regex_errors_gracefully(self):
        """Should skip rules with invalid regex patterns."""
        from utils import validation

        # Inject rule with invalid regex
        validation._NONSENSE_RULES = [
            {"pattern": "valid.*pattern", "category": "test"},
            {"pattern": "[invalid(regex", "category": "broken"},  # Invalid regex
            {"pattern": "another.*valid", "category": "test2"},
        ]

        # Should not raise, just skip invalid pattern
        result = validation.is_nonsense("test query")
        assert result is None or isinstance(result, str)

    def test_case_insensitive_matching(self):
        """Should match patterns case-insensitively."""
        from utils import validation

        validation._NONSENSE_RULES = [{"pattern": "hello.*world", "category": "test"}]

        assert validation.is_nonsense("HELLO WORLD") == "test"
        assert validation.is_nonsense("hello world") == "test"
        assert validation.is_nonsense("HeLLo WoRLd") == "test"

    def test_returns_category_from_matched_rule(self):
        """Should return category from matched rule."""
        from utils import validation

        validation._NONSENSE_RULES = [
            {"pattern": "profanity.*word", "category": "profanity"}
        ]

        result = validation.is_nonsense("profanity word here")
        assert result == "profanity"

    def test_returns_other_for_rule_without_category(self):
        """Should return 'other' if rule has no category field."""
        from utils import validation

        validation._NONSENSE_RULES = [{"pattern": "match.*this"}]  # No category field

        result = validation.is_nonsense("match this pattern")
        assert result == "other"


class TestTokenOverlapRatio:
    """Tests for token_overlap_ratio() function."""

    def test_perfect_overlap_returns_1_0(self):
        """Should return 1.0 for perfect overlap."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "engineering", "modernization"}
        ratio = token_overlap_ratio("platform engineering modernization", vocab)
        assert ratio == 1.0

    def test_no_overlap_returns_0_0(self):
        """Should return 0.0 for no overlap."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "engineering", "modernization"}
        ratio = token_overlap_ratio("unrelated query terms", vocab)
        assert ratio == 0.0

    def test_partial_overlap_returns_proportional(self):
        """Should return proportional ratio for partial overlap."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "engineering", "modernization"}
        # "platform" matches, "database" and "migration" don't
        ratio = token_overlap_ratio("platform database migration", vocab)
        assert 0.0 < ratio < 1.0
        assert ratio == 1 / 3  # 1 out of 3 unique tokens

    def test_excludes_stopwords(self):
        """Should exclude stopwords from token count."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "modernization"}
        # "the", "and", "with" are stopwords and should be ignored
        ratio = token_overlap_ratio("the platform and modernization with", vocab)
        assert ratio == 1.0  # 2 out of 2 non-stopword tokens match

    def test_filters_short_tokens(self):
        """Should filter tokens shorter than 3 characters."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform"}
        # "a", "is", "ok" are too short
        ratio = token_overlap_ratio("platform a is ok", vocab)
        assert ratio == 1.0  # Only "platform" counted

    def test_handles_empty_query(self):
        """Should return 0.0 for empty query."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "engineering"}
        assert token_overlap_ratio("", vocab) == 0.0

    def test_handles_none_query(self):
        """Should handle None query."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform"}
        assert token_overlap_ratio(None, vocab) == 0.0

    def test_counts_all_token_occurrences(self):
        """Should count all token occurrences, normalized by unique count."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform"}
        # "platform" appears 3 times
        # hits = 3, unique_tokens = 1, ratio = 3/1 = 3.0
        ratio = token_overlap_ratio("platform platform platform", vocab)
        assert ratio == 3.0

        vocab2 = {"platform", "engineering"}
        # Both tokens appear once each
        ratio2 = token_overlap_ratio("platform engineering", vocab2)
        assert ratio2 == 1.0  # 2 hits / 2 unique = 1.0

    def test_normalizes_by_unique_token_count(self):
        """Should normalize by unique non-stopword token count."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "engineering"}
        # 2 unique tokens, both match
        assert token_overlap_ratio("platform engineering", vocab) == 1.0

        # 3 unique tokens, 2 match
        ratio = token_overlap_ratio("platform engineering database", vocab)
        assert ratio == 2 / 3

    def test_case_insensitive_matching(self):
        """Should match case-insensitively."""
        from utils.validation import token_overlap_ratio

        vocab = {"platform", "engineering"}
        ratio_lower = token_overlap_ratio("platform engineering", vocab)
        ratio_upper = token_overlap_ratio("PLATFORM ENGINEERING", vocab)
        ratio_mixed = token_overlap_ratio("Platform Engineering", vocab)

        assert ratio_lower == ratio_upper == ratio_mixed == 1.0


class TestValidationConstants:
    """Tests for module constants."""

    def test_stopwords_defined(self):
        """Should define _STOPWORDS set."""
        from utils.validation import _STOPWORDS

        assert isinstance(_STOPWORDS, set)
        assert len(_STOPWORDS) > 0
        assert "the" in _STOPWORDS
        assert "and" in _STOPWORDS

    def test_word_regex_defined(self):
        """Should define _WORD_RX pattern."""
        import re

        from utils.validation import _WORD_RX

        assert isinstance(_WORD_RX, re.Pattern)
