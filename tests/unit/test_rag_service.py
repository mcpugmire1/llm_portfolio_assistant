"""
Unit tests for services/rag_service.py - semantic_search() function.

Tests for Jan 5, 2026 changes:
- relaxed_count when filters block all results
- active_filters list when industry/capability filters applied
- No regression for normal search behavior
"""

from unittest.mock import MagicMock, patch

import pytest

from services.rag_service import semantic_search


@pytest.fixture
def mock_st():
    """Mock streamlit session_state."""
    mock = MagicMock()
    mock.session_state = {}
    return mock


@pytest.fixture
def sample_stories_with_industry():
    """Sample stories with Industry and Solution/Offering fields."""
    return [
        {
            "id": "story-1|jpmc",
            "Title": "Payments Platform",
            "Client": "JPMC",
            "Industry": "Banking",
            "Solution / Offering": "Platform Engineering",
            "5PSummary": "Transformed global payments infrastructure",
        },
        {
            "id": "story-2|capital-one",
            "Title": "Agile Transformation",
            "Client": "Capital One",
            "Industry": "Banking",
            "Solution / Offering": "Agile Coaching",
            "5PSummary": "Led agile transformation across 150+ person org",
        },
        {
            "id": "story-3|takeda",
            "Title": "GenAI Implementation",
            "Client": "Takeda",
            "Industry": "Healthcare",
            "Solution / Offering": "AI/ML Solutions",
            "5PSummary": "Built GenAI RAG pipeline for regulatory docs",
        },
    ]


@pytest.fixture
def mock_pinecone_hits():
    """Mock Pinecone search results with high confidence scores."""
    return [
        {
            "story": {
                "id": "story-1|jpmc",
                "Title": "Payments Platform",
                "Industry": "Banking",
                "Solution / Offering": "Platform Engineering",
            },
            "pc_score": 0.85,
            "snippet": "Transformed global payments",
        },
        {
            "story": {
                "id": "story-2|capital-one",
                "Title": "Agile Transformation",
                "Industry": "Banking",
                "Solution / Offering": "Agile Coaching",
            },
            "pc_score": 0.72,
            "snippet": "Led agile transformation",
        },
        {
            "story": {
                "id": "story-3|takeda",
                "Title": "GenAI Implementation",
                "Industry": "Healthcare",
                "Solution / Offering": "AI/ML Solutions",
            },
            "pc_score": 0.68,
            "snippet": "Built GenAI pipeline",
        },
    ]


class TestSemanticSearchRelaxedCount:
    """Test relaxed_count feature when filters block all results."""

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_relaxed_count_when_industry_filter_blocks_all(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """When industry filter blocks all results, return relaxed_count of matches without industry filter."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        # Filter for Retail industry (no stories match - should block all)
        filters = {
            "industry": "Retail",  # Changed from Healthcare to Retail (no matches)
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="leadership transformation",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert result["results"] == []  # All results blocked by industry filter
        assert result["confidence"] == "high"  # Top score is 0.85
        assert "relaxed_count" in result
        assert (
            result["relaxed_count"] == 3
        )  # All 3 stories would match without industry filter
        assert "active_filters" in result
        assert ("industry", "Retail") in result["active_filters"]

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_relaxed_count_when_capability_filter_blocks_all(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """When capability filter blocks all results, return relaxed_count."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        # Filter for Data Engineering (no stories match)
        filters = {
            "industry": "",
            "capability": "Data Engineering",  # Changed to non-matching capability
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="agile transformation",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert result["results"] == []
        assert "relaxed_count" in result
        assert (
            result["relaxed_count"] == 3
        )  # All 3 stories would match without capability filter
        assert ("capability", "Data Engineering") in result["active_filters"]

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_relaxed_count_with_both_filters(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """When both industry and capability filters applied, active_filters contains both."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        filters = {
            "industry": "Retail",  # No retail stories
            "capability": "Data Engineering",  # No data engineering stories
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="transformation",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert result["results"] == []
        assert "active_filters" in result
        assert len(result["active_filters"]) == 2
        assert ("industry", "Retail") in result["active_filters"]
        assert ("capability", "Data Engineering") in result["active_filters"]

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_no_relaxed_count_when_results_exist(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """When filters don't block all results, relaxed_count should NOT be returned."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        filters = {
            "industry": "Banking",  # Matches 2 stories
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="transformation",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert len(result["results"]) == 2  # Banking stories returned
        assert "relaxed_count" not in result  # Should NOT be present
        assert "active_filters" not in result

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_no_relaxed_count_when_no_industry_capability_filters(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """When industry/capability filters not used, no relaxed_count even if results empty."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        # Other filters only (no industry/capability)
        filters = {
            "industry": "",
            "capability": "",
            "era": "2030-2035",  # Future era with no stories
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="transformation",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert - No relaxed_count because industry/capability not in use
        assert "relaxed_count" not in result
        assert "active_filters" not in result


class TestSemanticSearchNoRegression:
    """Ensure normal search behavior still works (no regression from Jan 5 changes)."""

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_normal_search_returns_results(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """Normal search with no filters returns all high-confidence results."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="transformation leadership",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert len(result["results"]) == 3
        assert result["confidence"] == "high"  # Top score 0.85 >= 0.25
        assert result["top_score"] == 0.85
        assert all("pc" in story for story in result["results"])  # Scores attached

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_low_confidence_search(
        self, mock_st, mock_pinecone, sample_stories_with_industry
    ):
        """Search with low confidence (0.15-0.25) returns 'low' confidence."""
        # Setup
        mock_st.session_state = {}
        low_confidence_hits = [
            {
                "story": {
                    "id": "story-1|jpmc",
                    "Title": "Payments Platform",
                    "Industry": "Banking",
                },
                "pc_score": 0.18,  # Between CONFIDENCE_LOW (0.15) and CONFIDENCE_HIGH (0.25)
                "snippet": "Some match",
            }
        ]
        mock_pinecone.return_value = low_confidence_hits

        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="vague query",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert result["confidence"] == "low"
        assert result["top_score"] == 0.18
        assert len(result["results"]) >= 1

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_no_results_confidence_none(
        self, mock_st, mock_pinecone, sample_stories_with_industry
    ):
        """When Pinecone returns no hits, falls back to local keyword filtering with 'low' confidence."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = []  # No hits

        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="unrelated query",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert - when Pinecone returns nothing, it falls back to local filtering
        # Local results get "low" confidence if any exist, "none" if zero results
        assert result["confidence"] in ("low", "none")  # Depends on keyword match
        assert result["top_score"] == 0.0  # No Pinecone score

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_empty_query_returns_no_results(
        self, mock_st, mock_pinecone, sample_stories_with_industry
    ):
        """Empty query returns no results without calling Pinecone."""
        # Setup
        mock_st.session_state = {}

        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        result = semantic_search(
            query="",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert
        assert result["results"] == []
        assert result["confidence"] == "none"
        assert result["top_score"] == 0.0
        mock_pinecone.assert_not_called()  # Should not call Pinecone for empty query

    @patch("services.rag_service.pinecone_semantic_search")
    @patch("services.rag_service.st")
    def test_session_state_updated_with_scores(
        self, mock_st, mock_pinecone, sample_stories_with_industry, mock_pinecone_hits
    ):
        """Verify session_state is updated with Pinecone scores and snippets."""
        # Setup
        mock_st.session_state = {}
        mock_pinecone.return_value = mock_pinecone_hits

        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }

        # Execute
        semantic_search(
            query="transformation",
            filters=filters,
            stories=sample_stories_with_industry,
        )

        # Assert session_state was updated
        assert "__pc_last_ids__" in mock_st.session_state
        assert "__pc_snippets__" in mock_st.session_state
        assert "__last_ranked_sources__" in mock_st.session_state

        # Check specific values
        assert mock_st.session_state["__pc_last_ids__"]["story-1|jpmc"] == 0.85
        assert (
            "Transformed global payments"
            in mock_st.session_state["__pc_snippets__"]["story-1|jpmc"]
        )
        assert "story-1|jpmc" in mock_st.session_state["__last_ranked_sources__"]
