"""
Unit tests for utils/filters.py

Tests for story filtering functionality including industry, capability,
client, domain, role, tags, and keyword search filtering.

Stories come from the corpus via load_stories(), picked by field value, so
the tests read the fields production reads.
"""

import pytest

from utils.corpus_loader import load_stories


@pytest.fixture(scope="module")
def stories():
    return load_stories("echo_star_stories_nlp.jsonl")


def _first(stories, pred):
    return next(s for s in stories if pred(s))


def _distinct(stories, field, n):
    """The first n stories with pairwise different values of field."""
    picked = []
    for s in stories:
        if all(s[field] != p[field] for p in picked):
            picked.append(s)
        if len(picked) == n:
            return picked
    raise AssertionError(f"corpus has fewer than {n} distinct {field} values")


class TestMatchesFilters:
    """Tests for matches_filters() function."""

    def test_returns_true_for_no_filters(self, stories):
        """Should return True when no filters are active."""
        from utils.filters import matches_filters

        assert matches_filters(stories[0], F={}) is True

    def test_filters_by_industry(self, stories):
        """Should filter by single industry selection."""
        from utils.filters import matches_filters

        story_a, story_b = _distinct(stories, "Industry", 2)

        filters_a = {"industry": story_a["Industry"]}
        filters_b = {"industry": story_b["Industry"]}

        assert matches_filters(story_a, filters_a) is True
        assert matches_filters(story_a, filters_b) is False
        assert matches_filters(story_b, filters_b) is True
        assert matches_filters(story_b, filters_a) is False

    def test_filters_by_capability(self, stories):
        """Should filter by single capability/offering selection."""
        from utils.filters import matches_filters

        story_a, story_b = _distinct(stories, "Solution / Offering", 2)

        filters_a = {"capability": story_a["Solution / Offering"]}
        filters_b = {"capability": story_b["Solution / Offering"]}

        assert matches_filters(story_a, filters_a) is True
        assert matches_filters(story_a, filters_b) is False
        assert matches_filters(story_b, filters_b) is True

    def test_filters_by_clients_list(self, stories):
        """Should filter by client list (OR logic)."""
        from utils.filters import matches_filters

        story_a, story_b, story_c = _distinct(stories, "Client", 3)

        filters = {"clients": [story_a["Client"], story_b["Client"]]}

        assert matches_filters(story_a, filters) is True
        assert matches_filters(story_b, filters) is True
        assert matches_filters(story_c, filters) is False

    def test_filters_by_domains_list(self, stories):
        """Should filter by Sub-category/domain list (OR logic)."""
        from utils.filters import matches_filters

        story_a, story_b, story_c = _distinct(stories, "Sub-category", 3)

        filters = {"domains": [story_a["Sub-category"], story_b["Sub-category"]]}

        assert matches_filters(story_a, filters) is True
        assert matches_filters(story_b, filters) is True
        assert matches_filters(story_c, filters) is False

    def test_filters_by_roles_list(self, stories):
        """Should filter by role list (OR logic)."""
        from utils.filters import matches_filters

        story_a, story_b, story_c = _distinct(stories, "Role", 3)

        filters = {"roles": [story_a["Role"], story_b["Role"]]}

        assert matches_filters(story_a, filters) is True
        assert matches_filters(story_b, filters) is True
        assert matches_filters(story_c, filters) is False

    def test_filters_by_tags_case_insensitive(self, stories):
        """Should filter by tags with case-insensitive matching (OR logic)."""
        from utils.filters import matches_filters

        story_a = stories[0]
        tag_a = story_a["public_tags"][0]
        story_b = _first(stories, lambda s: tag_a not in s["public_tags"])
        tag_b = next(
            t for t in story_b["public_tags"] if t not in story_a["public_tags"]
        )

        filters = {"tags": [tag_a.lower(), tag_b.lower()]}

        assert matches_filters(story_a, filters) is True
        assert matches_filters(story_b, filters) is True

    def test_filters_by_tags_requires_at_least_one_match(self, stories):
        """Should require at least one tag match."""
        from utils.filters import matches_filters

        story_with_tag = stories[0]
        tag = story_with_tag["public_tags"][0]
        story_no_match = _first(stories, lambda s: tag not in s["public_tags"])

        filters = {"tags": [tag.lower(), "zzz_sentinel_tag"]}

        assert matches_filters(story_with_tag, filters) is True
        assert matches_filters(story_no_match, filters) is False

    def test_filters_by_keyword_query_token_match(self, stories):
        """Should filter by keyword query using token-based matching."""
        from utils.filters import matches_filters
        from utils.validation import _tokenize

        story = _first(stories, lambda s: len(_tokenize(s["Title"])) >= 2)
        title_toks = _tokenize(story["Title"])

        # All tokens match
        filters_match = {"q": f"{title_toks[0]} {title_toks[1]}"}
        assert matches_filters(story, filters_match) is True

        # Some tokens match
        filters_partial = {"q": f"{title_toks[0]} zzzsentinel"}
        assert matches_filters(story, filters_partial) is False

        # No tokens match
        filters_no_match = {"q": "zzzsentinel qqqsentinel"}
        assert matches_filters(story, filters_no_match) is False

    def test_keyword_query_fallback_substring(self, stories):
        """Should fall back to substring match for non-tokenizable queries."""
        from utils.filters import matches_filters

        story = stories[0]

        # Two characters: no 3+ char tokens, so substring match applies
        filters = {"q": story["Title"][:2]}
        assert matches_filters(story, filters) is True

    def test_keyword_query_searches_multiple_fields(self, stories):
        """Should search across Title, Client, Role, Purpose, Process, Performance, tags."""
        from utils.filters import matches_filters
        from utils.validation import _tokenize

        story = stories[0]
        fields = {
            "Title": story["Title"],
            "Client": story["Client"],
            "Role": story["Role"],
            "Purpose": story["Purpose"],
            "Process": " ".join(story["Process"]),
            "Performance": " ".join(story["Performance"]),
            "public_tags": " ".join(story["public_tags"]),
        }

        # Each field should be searchable
        for field, text in fields.items():
            token = _tokenize(text)[0]
            assert matches_filters(story, {"q": token}) is True, field

    def test_combines_multiple_filters_with_and_logic(self, stories):
        """Should apply AND logic across all filter types."""
        from utils.filters import matches_filters

        story, other = _distinct(stories, "Client", 2)

        # All filters match
        filters_all = {
            "industry": story["Industry"],
            "clients": [story["Client"], other["Client"]],
            "domains": [story["Sub-category"]],
            "roles": [story["Role"]],
            "tags": [story["public_tags"][0]],
        }
        assert matches_filters(story, filters_all) is True

        # One filter fails
        filters_fail = {
            "industry": story["Industry"],
            "clients": [other["Client"]],  # Wrong client
        }
        assert matches_filters(story, filters_fail) is False

    def test_handles_missing_story_fields(self):
        """Should handle stories with missing fields gracefully."""
        from utils.filters import matches_filters

        story = {}  # Empty story

        filters = {
            "industry": "Test",
            "clients": ["Test"],
        }

        assert matches_filters(story, filters) is False

    def test_handles_empty_filter_values(self, stories):
        """Should treat empty/None filter values as inactive."""
        from utils.filters import matches_filters

        story = stories[0]

        # Empty strings and None should be treated as inactive
        filters = {
            "industry": "",  # Empty - should be ignored
            "capability": None,  # None - should be ignored
            "clients": [],  # Empty list - should be ignored
        }

        assert matches_filters(story, filters) is True

    def test_normalizes_tag_whitespace(self, stories):
        """Should normalize whitespace in filter tags."""
        from utils.filters import matches_filters

        story = stories[0]
        filters = {"tags": [f"  {story['public_tags'][0].lower()}  "]}

        assert matches_filters(story, filters) is True
