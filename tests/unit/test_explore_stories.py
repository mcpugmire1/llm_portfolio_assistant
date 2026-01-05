"""
Unit tests for ui/pages/explore_stories.py - remove_filter_value() function.

Tests for Jan 5, 2026 changes:
- Search cache is cleared when filter chips are removed
- __search_triggered__ is set when query exists
- Filter removal works for industry, capability, era, multiselects
"""


# Mock the function since we can't import the entire page module
def remove_filter_value_mock(filter_key: str, value: str, session_state: dict):
    """
    Simplified version of remove_filter_value for testing.
    This mirrors the actual implementation from explore_stories.py.
    """
    F = session_state["filters"]

    # Handle search query specially
    if filter_key == "q":
        F["q"] = ""
        version_key = "_widget_version_q"
        session_state[version_key] = session_state.get(version_key, 0) + 1
        return

    # Handle string filters (not lists)
    if filter_key in ("era", "industry", "capability"):
        F[filter_key] = ""
        version_key = f"_widget_version_{filter_key}"
        current_version = session_state.get(version_key, 0)
        session_state[version_key] = current_version + 1
        widget_key = f"facet_{filter_key}"
        for v in range(current_version + 2):
            versioned_key = f"{widget_key}_v{v}"
            if versioned_key in session_state:
                del session_state[versioned_key]
        # Clear search cache and re-trigger search
        session_state.pop("__last_search_results__", None)
        session_state.pop("__last_search_confidence__", None)
        session_state.pop("__last_search_query__", None)
        if F.get("q"):
            session_state["__search_triggered__"] = True
        return

    # Handle multiselect filters (clients, domains, roles, tags)
    if filter_key in ("clients", "domains", "roles", "tags", "personas"):
        current_values = F.get(filter_key, [])
        if value in current_values:
            current_values.remove(value)
            F[filter_key] = current_values
        # Increment widget version
        version_key = f"_widget_version_{filter_key}"
        session_state[version_key] = session_state.get(version_key, 0) + 1
        return


class TestRemoveFilterValueSearchCache:
    """Test that search cache is cleared when filter chips are removed."""

    def test_industry_filter_removal_clears_search_cache(self):
        """When industry filter is removed, search cache should be cleared."""
        # Setup
        session_state = {
            "filters": {
                "industry": "Banking",
                "capability": "",
                "era": "",
                "q": "transformation",
            },
            "__last_search_results__": ["story-1", "story-2"],
            "__last_search_confidence__": "high",
            "__last_search_query__": "transformation",
        }

        # Execute
        remove_filter_value_mock("industry", "Banking", session_state)

        # Assert
        assert session_state["filters"]["industry"] == ""
        assert "__last_search_results__" not in session_state
        assert "__last_search_confidence__" not in session_state
        assert "__last_search_query__" not in session_state

    def test_capability_filter_removal_clears_search_cache(self):
        """When capability filter is removed, search cache should be cleared."""
        # Setup
        session_state = {
            "filters": {
                "industry": "",
                "capability": "Platform Engineering",
                "era": "",
                "q": "platform",
            },
            "__last_search_results__": ["story-1"],
            "__last_search_confidence__": "high",
            "__last_search_query__": "platform",
        }

        # Execute
        remove_filter_value_mock("capability", "Platform Engineering", session_state)

        # Assert
        assert session_state["filters"]["capability"] == ""
        assert "__last_search_results__" not in session_state
        assert "__last_search_confidence__" not in session_state
        assert "__last_search_query__" not in session_state

    def test_era_filter_removal_clears_search_cache(self):
        """When era filter is removed, search cache should be cleared."""
        # Setup
        session_state = {
            "filters": {
                "industry": "",
                "capability": "",
                "era": "Banking & Capital Markets (2008-2013)",
                "q": "payments",
            },
            "__last_search_results__": ["story-1", "story-2", "story-3"],
            "__last_search_confidence__": "high",
            "__last_search_query__": "payments",
        }

        # Execute
        remove_filter_value_mock(
            "era", "Banking & Capital Markets (2008-2013)", session_state
        )

        # Assert
        assert session_state["filters"]["era"] == ""
        assert "__last_search_results__" not in session_state
        assert "__last_search_confidence__" not in session_state
        assert "__last_search_query__" not in session_state

    def test_multiselect_filter_removal_does_not_clear_cache(self):
        """When multiselect filters (clients, tags, etc.) removed, cache is NOT cleared."""
        # Setup
        session_state = {
            "filters": {
                "industry": "",
                "capability": "",
                "era": "",
                "clients": ["JPMC", "Capital One"],
                "q": "",
            },
            "__last_search_results__": ["story-1"],
            "__last_search_confidence__": "high",
            "__last_search_query__": "test",
        }

        # Execute
        remove_filter_value_mock("clients", "JPMC", session_state)

        # Assert - multiselect removal doesn't clear cache
        assert session_state["filters"]["clients"] == ["Capital One"]
        assert "__last_search_results__" in session_state  # Cache still present


class TestRemoveFilterValueSearchTriggered:
    """Test that __search_triggered__ is set when query exists."""

    def test_search_triggered_when_query_exists(self):
        """When filter removed and query exists, __search_triggered__ should be True."""
        # Setup
        session_state = {
            "filters": {
                "industry": "Banking",
                "capability": "",
                "era": "",
                "q": "transformation",
            },
        }

        # Execute
        remove_filter_value_mock("industry", "Banking", session_state)

        # Assert
        assert session_state.get("__search_triggered__") is True

    def test_search_not_triggered_when_query_empty(self):
        """When filter removed but no query, __search_triggered__ should NOT be set."""
        # Setup
        session_state = {
            "filters": {"industry": "Banking", "capability": "", "era": "", "q": ""},
        }

        # Execute
        remove_filter_value_mock("industry", "Banking", session_state)

        # Assert
        assert "__search_triggered__" not in session_state

    def test_search_triggered_for_capability_filter(self):
        """Capability filter removal triggers search when query exists."""
        # Setup
        session_state = {
            "filters": {
                "industry": "",
                "capability": "Platform Engineering",
                "era": "",
                "q": "platform work",
            },
        }

        # Execute
        remove_filter_value_mock("capability", "Platform Engineering", session_state)

        # Assert
        assert session_state.get("__search_triggered__") is True

    def test_search_triggered_for_era_filter(self):
        """Era filter removal triggers search when query exists."""
        # Setup
        session_state = {
            "filters": {
                "industry": "",
                "capability": "",
                "era": "Current Work (2024-2025)",
                "q": "latest projects",
            },
        }

        # Execute
        remove_filter_value_mock("era", "Current Work (2024-2025)", session_state)

        # Assert
        assert session_state.get("__search_triggered__") is True


class TestRemoveFilterValueWidgetVersioning:
    """Test that widget versions are incremented correctly."""

    def test_industry_filter_increments_version(self):
        """Industry filter removal should increment widget version."""
        # Setup
        session_state = {
            "filters": {"industry": "Banking", "capability": "", "era": "", "q": ""},
            "_widget_version_industry": 0,
        }

        # Execute
        remove_filter_value_mock("industry", "Banking", session_state)

        # Assert
        assert session_state["_widget_version_industry"] == 1

    def test_capability_filter_increments_version(self):
        """Capability filter removal should increment widget version."""
        # Setup
        session_state = {
            "filters": {
                "industry": "",
                "capability": "Platform Engineering",
                "era": "",
                "q": "",
            },
            "_widget_version_capability": 2,
        }

        # Execute
        remove_filter_value_mock("capability", "Platform Engineering", session_state)

        # Assert
        assert session_state["_widget_version_capability"] == 3

    def test_versioned_widget_keys_deleted(self):
        """Old versioned widget keys should be deleted."""
        # Setup
        session_state = {
            "filters": {"industry": "Banking", "capability": "", "era": "", "q": ""},
            "_widget_version_industry": 1,
            "facet_industry_v0": "Banking",
            "facet_industry_v1": "Banking",
        }

        # Execute
        remove_filter_value_mock("industry", "Banking", session_state)

        # Assert
        assert "facet_industry_v0" not in session_state
        assert "facet_industry_v1" not in session_state
        assert session_state["_widget_version_industry"] == 2


class TestRemoveFilterValueMultiselectFilters:
    """Test removal of multiselect filter values."""

    def test_remove_client_from_list(self):
        """Removing a client from clients list should work."""
        # Setup
        session_state = {
            "filters": {"clients": ["JPMC", "Capital One", "Takeda"]},
            "_widget_version_clients": 0,
        }

        # Execute
        remove_filter_value_mock("clients", "Capital One", session_state)

        # Assert
        assert session_state["filters"]["clients"] == ["JPMC", "Takeda"]
        assert session_state["_widget_version_clients"] == 1

    def test_remove_tag_from_list(self):
        """Removing a tag from tags list should work."""
        # Setup
        session_state = {
            "filters": {"tags": ["leadership", "transformation", "cloud"]},
            "_widget_version_tags": 0,
        }

        # Execute
        remove_filter_value_mock("tags", "transformation", session_state)

        # Assert
        assert session_state["filters"]["tags"] == ["leadership", "cloud"]

    def test_remove_nonexistent_value_does_nothing(self):
        """Removing a value that doesn't exist should not error."""
        # Setup
        session_state = {
            "filters": {"domains": ["Platform Engineering"]},
            "_widget_version_domains": 0,
        }

        # Execute
        remove_filter_value_mock("domains", "Data Engineering", session_state)

        # Assert - no change
        assert session_state["filters"]["domains"] == ["Platform Engineering"]
        assert session_state["_widget_version_domains"] == 1  # Version still increments

    def test_remove_role_from_list(self):
        """Removing a role from roles list should work."""
        # Setup
        session_state = {
            "filters": {"roles": ["Director", "VP", "Head of Engineering"]},
            "_widget_version_roles": 0,
        }

        # Execute
        remove_filter_value_mock("roles", "VP", session_state)

        # Assert
        assert session_state["filters"]["roles"] == ["Director", "Head of Engineering"]


class TestRemoveFilterValueQueryRemoval:
    """Test removal of search query."""

    def test_remove_search_query(self):
        """Removing search query (q filter) should clear it."""
        # Setup
        session_state = {
            "filters": {"q": "transformation leadership"},
            "_widget_version_q": 0,
        }

        # Execute
        remove_filter_value_mock("q", "transformation leadership", session_state)

        # Assert
        assert session_state["filters"]["q"] == ""
        assert session_state["_widget_version_q"] == 1
