"""
Pytest fixtures for Ask MattGPT tests.

Shared fixtures for mock data, test clients, and common setup.
"""

from typing import Any

import pytest

# =============================================================================
# MOCK STORY DATA
# =============================================================================


@pytest.fixture
def sample_stories() -> list[dict[str, Any]]:
    """Sample story data for testing search and display functions."""
    return [
        {
            "id": "story_001",
            "title": "Global Payments Platform Transformation",
            "client": "JPMC",
            "category": "Execution & Delivery",
            "subcategory": "Platform Engineering",
            "situation": "Legacy payment system couldn't scale.",
            "task": "Lead modernization of global payments infrastructure.",
            "action": "Designed microservices architecture, led 50-person team.",
            "result": "Reduced transaction time by 60%, saved $2M annually.",
            "themes": ["platform", "payments", "transformation", "leadership"],
        },
        {
            "id": "story_002",
            "title": "Agile Transformation at Scale",
            "client": "Capital One",
            "category": "Talent & Enablement",
            "subcategory": "Coaching & Mentorship",
            "situation": "Teams struggling with waterfall methodology.",
            "task": "Transform 150+ person org to agile practices.",
            "action": "Trained scrum masters, coached leadership, facilitated retrospectives.",
            "result": "Increased velocity 40%, improved team satisfaction scores.",
            "themes": ["agile", "coaching", "leadership", "transformation"],
        },
        {
            "id": "story_003",
            "title": "Healthcare GenAI Implementation",
            "client": "Takeda",
            "category": "Execution & Delivery",
            "subcategory": "AI/ML Solutions",
            "situation": "Manual document review taking weeks.",
            "task": "Implement GenAI solution for regulatory document analysis.",
            "action": "Built RAG pipeline, fine-tuned models, deployed to production.",
            "result": "Reduced review time from 3 weeks to 2 days.",
            "themes": ["genai", "healthcare", "automation", "innovation"],
        },
        {
            "id": "story_004",
            "title": "Cross-Functional Stakeholder Alignment",
            "client": "JPMC",
            "category": "Talent & Enablement",
            "subcategory": "Stakeholder Management",
            "situation": "Conflicting priorities between business and tech.",
            "task": "Align stakeholders on shared roadmap.",
            "action": "Facilitated workshops, created shared OKRs, built trust.",
            "result": "Achieved consensus, delivered project 2 months early.",
            "themes": ["stakeholder", "leadership", "communication", "conflict"],
        },
        {
            "id": "story_005",
            "title": "Team Conflict Resolution",
            "client": "American Express",
            "category": "Talent & Enablement",
            "subcategory": "Team Leadership",
            "situation": "Senior engineers in heated disagreement over architecture.",
            "task": "Resolve conflict and unify team direction.",
            "action": "Individual 1:1s, facilitated decision framework, built consensus.",
            "result": "Team aligned, relationship repaired, project back on track.",
            "themes": ["conflict", "leadership", "team", "behavioral"],
        },
    ]


@pytest.fixture
def sample_search_results(sample_stories) -> list[dict[str, Any]]:
    """Search results with scores (simulating Pinecone response)."""
    return [
        {**sample_stories[0], "score": 0.95},
        {**sample_stories[3], "score": 0.88},  # Another JPMC story
        {**sample_stories[1], "score": 0.82},
        {**sample_stories[2], "score": 0.78},
        {**sample_stories[4], "score": 0.75},
    ]


@pytest.fixture
def behavioral_query_examples() -> list[dict[str, str]]:
    """Example behavioral interview queries with expected categories."""
    return [
        {
            "query": "Tell me about a time you led a team through conflict",
            "expected_category": "Talent & Enablement",
            "keywords": ["conflict", "leadership", "team"],
        },
        {
            "query": "Describe a situation where you had to influence stakeholders",
            "expected_category": "Talent & Enablement",
            "keywords": ["stakeholder", "influence", "communication"],
        },
        {
            "query": "How did you handle a difficult team member?",
            "expected_category": "Talent & Enablement",
            "keywords": ["team", "conflict", "leadership"],
        },
        {
            "query": "Give me an example of when you failed and what you learned",
            "expected_category": "Talent & Enablement",
            "keywords": ["failure", "learning", "growth"],
        },
    ]


@pytest.fixture
def technical_query_examples() -> list[dict[str, str]]:
    """Example technical queries with expected categories."""
    return [
        {
            "query": "How did Matt build the payments platform?",
            "expected_category": "Execution & Delivery",
            "keywords": ["platform", "payments", "architecture"],
        },
        {
            "query": "Show me GenAI projects in healthcare",
            "expected_category": "Execution & Delivery",
            "keywords": ["genai", "healthcare", "ai"],
        },
    ]


# =============================================================================
# NONSENSE FILTER TEST DATA
# =============================================================================


@pytest.fixture
def nonsense_queries() -> list[str]:
    """Queries that should be filtered as nonsense."""
    return [
        "asdfghjkl",
        "test test test",
        "hello hello hello hello",
        "???",
        "12345",
        "a",
        "",
        "   ",
    ]


@pytest.fixture
def valid_queries() -> list[str]:
    """Queries that should NOT be filtered as nonsense."""
    return [
        "How did Matt transform global payments?",
        "Tell me about leadership experience",
        "Show me healthcare projects",
        "What agile transformations has Matt led?",
        "Describe a time Matt resolved conflict",
    ]


# =============================================================================
# MOCK SERVICES (for integration tests)
# =============================================================================


@pytest.fixture
def mock_streamlit(monkeypatch):
    """Mock streamlit session_state for testing."""
    from unittest.mock import MagicMock

    mock_session_state = {}

    # Create a mock that behaves like a dict
    mock = MagicMock()
    mock.get = lambda key, default=None: mock_session_state.get(key, default)
    mock.__getitem__ = lambda _self, key: mock_session_state[key]
    mock.__setitem__ = lambda _self, key, value: mock_session_state.__setitem__(
        key, value
    )
    mock.__contains__ = lambda _self, key: key in mock_session_state
    mock.pop = lambda key, default=None: mock_session_state.pop(key, default)

    # Patch streamlit.session_state
    monkeypatch.setattr("streamlit.session_state", mock)

    return mock


@pytest.fixture
def mock_pinecone_response(sample_search_results):
    """Mock Pinecone query response structure."""
    return {
        "matches": [
            {
                "id": r["id"],
                "score": r["score"],
                "metadata": {k: v for k, v in r.items() if k not in ["id", "score"]},
            }
            for r in sample_search_results
        ]
    }
