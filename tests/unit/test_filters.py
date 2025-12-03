"""
Unit tests for utils/filters.py

Tests for story filtering functionality including industry, capability,
client, domain, role, tags, metrics, and keyword search filtering.
"""


class TestMatchesFilters:
    """Tests for matches_filters() function."""

    def test_returns_true_for_no_filters(self):
        """Should return True when no filters are active."""
        from utils.filters import matches_filters

        story = {"Title": "Test Story", "Client": "Test Client"}
        assert matches_filters(story, F={}) is True

    def test_filters_by_industry(self):
        """Should filter by single industry selection."""
        from utils.filters import matches_filters

        story_fs = {"Industry": "Financial Services", "Client": "JPMC"}
        story_hc = {"Industry": "Healthcare", "Client": "Mayo Clinic"}

        filters_fs = {"industry": "Financial Services"}
        filters_hc = {"industry": "Healthcare"}

        assert matches_filters(story_fs, filters_fs) is True
        assert matches_filters(story_fs, filters_hc) is False
        assert matches_filters(story_hc, filters_hc) is True
        assert matches_filters(story_hc, filters_fs) is False

    def test_filters_by_capability(self):
        """Should filter by single capability/offering selection."""
        from utils.filters import matches_filters

        story_platform = {"Solution / Offering": "Platform Engineering"}
        story_data = {"Solution / Offering": "Data & Analytics"}

        filters_platform = {"capability": "Platform Engineering"}
        filters_data = {"capability": "Data & Analytics"}

        assert matches_filters(story_platform, filters_platform) is True
        assert matches_filters(story_platform, filters_data) is False
        assert matches_filters(story_data, filters_data) is True

    def test_filters_by_clients_list(self):
        """Should filter by client list (OR logic)."""
        from utils.filters import matches_filters

        story_jpmc = {"Client": "JPMC"}
        story_google = {"Client": "Google"}
        story_amazon = {"Client": "Amazon"}

        filters = {"clients": ["JPMC", "Google"]}

        assert matches_filters(story_jpmc, filters) is True
        assert matches_filters(story_google, filters) is True
        assert matches_filters(story_amazon, filters) is False

    def test_filters_by_domains_list(self):
        """Should filter by Sub-category/domain list (OR logic)."""
        from utils.filters import matches_filters

        story_platform = {"Sub-category": "Platform Engineering"}
        story_cloud = {"Sub-category": "Cloud-Native Architecture"}
        story_data = {"Sub-category": "Data Engineering"}

        filters = {"domains": ["Platform Engineering", "Cloud-Native Architecture"]}

        assert matches_filters(story_platform, filters) is True
        assert matches_filters(story_cloud, filters) is True
        assert matches_filters(story_data, filters) is False

    def test_filters_by_roles_list(self):
        """Should filter by role list (OR logic)."""
        from utils.filters import matches_filters

        story_director = {"Role": "Director of Engineering"}
        story_consultant = {"Role": "Principal Consultant"}
        story_advisor = {"Role": "Technical Advisor"}

        filters = {"roles": ["Director of Engineering", "Principal Consultant"]}

        assert matches_filters(story_director, filters) is True
        assert matches_filters(story_consultant, filters) is True
        assert matches_filters(story_advisor, filters) is False

    def test_filters_by_tags_case_insensitive(self):
        """Should filter by tags with case-insensitive matching (OR logic)."""
        from utils.filters import matches_filters

        story_agile = {"public_tags": ["Agile", "Transformation"]}
        story_devops = {"public_tags": ["DevOps", "CI/CD"]}

        filters = {"tags": ["agile", "devops"]}  # Lowercase

        assert matches_filters(story_agile, filters) is True  # "Agile" matches "agile"
        assert (
            matches_filters(story_devops, filters) is True
        )  # "DevOps" matches "devops"

    def test_filters_by_tags_requires_at_least_one_match(self):
        """Should require at least one tag match."""
        from utils.filters import matches_filters

        story_with_tags = {"public_tags": ["Agile", "Transformation"]}
        story_no_match = {"public_tags": ["Unrelated", "Other"]}

        filters = {"tags": ["agile", "leadership"]}

        assert matches_filters(story_with_tags, filters) is True  # "Agile" matches
        assert matches_filters(story_no_match, filters) is False  # No matches

    def test_filters_by_has_metric(self):
        """Should filter stories with quantified metrics."""
        from utils.filters import matches_filters

        story_with_metric = {"what": ["Reduced latency by 60%"]}
        story_no_metric = {"what": ["Improved collaboration"]}

        filters_metric = {"has_metric": True}
        filters_no_metric = {"has_metric": False}

        assert matches_filters(story_with_metric, filters_metric) is True
        assert matches_filters(story_no_metric, filters_metric) is False
        assert matches_filters(story_with_metric, filters_no_metric) is True
        assert matches_filters(story_no_metric, filters_no_metric) is True

    def test_filters_by_keyword_query_token_match(self):
        """Should filter by keyword query using token-based matching."""
        from utils.filters import matches_filters

        story = {
            "Title": "Platform Modernization",
            "Client": "JPMC",
            "Sub-category": "Platform Engineering",
        }

        # All tokens match
        filters_match = {"q": "platform modernization"}
        assert matches_filters(story, filters_match) is True

        # Some tokens match
        filters_partial = {"q": "platform database"}
        assert matches_filters(story, filters_partial) is False  # "database" missing

        # No tokens match
        filters_no_match = {"q": "unrelated query"}
        assert matches_filters(story, filters_no_match) is False

    def test_keyword_query_fallback_substring(self):
        """Should fall back to substring match for non-tokenizable queries."""
        from utils.filters import matches_filters

        story = {"Title": "AI-ML Platform", "Client": "Test"}

        # Query has no 3+ char tokens, falls back to substring
        filters = {"q": "AI"}
        assert matches_filters(story, filters) is True

    def test_keyword_query_searches_multiple_fields(self):
        """Should search across Title, Client, Role, Purpose, Process, Performance, tags."""
        from utils.filters import matches_filters

        story = {
            "Title": "Project Alpha",
            "Client": "ClientCo",
            "Role": "Technical Lead",
            "Purpose": "Modernize infrastructure",
            "Process": ["Migrated to cloud"],
            "Performance": ["Reduced costs"],
            "public_tags": ["agile"],
        }

        # Each field should be searchable
        assert matches_filters(story, {"q": "alpha"}) is True
        assert matches_filters(story, {"q": "clientco"}) is True
        assert matches_filters(story, {"q": "technical"}) is True
        assert matches_filters(story, {"q": "modernize"}) is True
        assert matches_filters(story, {"q": "cloud"}) is True
        assert matches_filters(story, {"q": "costs"}) is True
        assert matches_filters(story, {"q": "agile"}) is True

    def test_combines_multiple_filters_with_and_logic(self):
        """Should apply AND logic across all filter types."""
        from utils.filters import matches_filters

        story = {
            "Industry": "Financial Services",
            "Client": "JPMC",
            "Sub-category": "Platform Engineering",
            "Role": "Director",
            "public_tags": ["agile"],
            "what": ["Reduced costs by 40%"],
        }

        # All filters match
        filters_all = {
            "industry": "Financial Services",
            "clients": ["JPMC", "Google"],
            "domains": ["Platform Engineering"],
            "roles": ["Director"],
            "tags": ["agile"],
            "has_metric": True,
        }
        assert matches_filters(story, filters_all) is True

        # One filter fails
        filters_fail = {
            "industry": "Financial Services",
            "clients": ["Google"],  # Wrong client
        }
        assert matches_filters(story, filters_fail) is False

    def test_handles_missing_story_fields(self):
        """Should handle stories with missing fields gracefully."""
        from utils.filters import matches_filters

        story = {}  # Empty story

        filters = {
            "industry": "Test",
            "clients": ["Test"],
            "has_metric": True,
        }

        assert matches_filters(story, filters) is False

    def test_handles_empty_filter_values(self):
        """Should treat empty/None filter values as inactive."""
        from utils.filters import matches_filters

        story = {"Industry": "Financial Services"}

        # Empty strings and None should be treated as inactive
        filters = {
            "industry": "",  # Empty - should be ignored
            "capability": None,  # None - should be ignored
            "clients": [],  # Empty list - should be ignored
        }

        assert matches_filters(story, filters) is True

    def test_normalizes_tag_whitespace(self):
        """Should normalize whitespace in tag matching."""
        from utils.filters import matches_filters

        story = {"public_tags": ["  Agile  ", "Leadership"]}
        filters = {"tags": ["agile", "  leadership  "]}

        assert matches_filters(story, filters) is True

    def test_persona_filter_not_used(self):
        """Should handle persona filter (field doesn't exist in data)."""
        from utils.filters import matches_filters

        story = {}
        filters = {"personas": ["Test Persona"]}

        # Should not crash, just return False (no match)
        assert matches_filters(story, filters) is False
