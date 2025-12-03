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
            "Title": "Global Payments Platform Transformation",
            "Client": "JPMC",
            "Category": "Execution & Delivery",
            "Sub-category": "Platform Engineering",
            "Situation": "Legacy payment system couldn't scale.",
            "Task": "Lead modernization of global payments infrastructure.",
            "Action": "Designed microservices architecture, led 50-person team.",
            "Result": "Reduced transaction time by 60%, saved $2M annually.",
            "Performance": ["Reduced transaction time by 60%", "Saved $2M annually"],
            "tags": ["platform", "payments", "transformation", "leadership"],
        },
        {
            "id": "story_002",
            "Title": "Agile Transformation at Scale",
            "Client": "Capital One",
            "Category": "Talent & Enablement",
            "Sub-category": "Coaching & Mentorship",
            "Situation": "Teams struggling with waterfall methodology.",
            "Task": "Transform 150+ person org to agile practices.",
            "Action": "Trained scrum masters, coached leadership, facilitated retrospectives.",
            "Result": "Increased velocity 40%, improved team satisfaction scores.",
            "Performance": [
                "Increased velocity 40%",
                "Improved team satisfaction scores",
            ],
            "tags": ["agile", "coaching", "leadership", "transformation"],
        },
        {
            "id": "story_003",
            "Title": "Healthcare GenAI Implementation",
            "Client": "Takeda",
            "Category": "Execution & Delivery",
            "Sub-category": "AI/ML Solutions",
            "Situation": "Manual document review taking weeks.",
            "Task": "Implement GenAI solution for regulatory document analysis.",
            "Action": "Built RAG pipeline, fine-tuned models, deployed to production.",
            "Result": "Reduced review time from 3 weeks to 2 days.",
            "Performance": ["Reduced review time from 3 weeks to 2 days"],
            "tags": ["genai", "healthcare", "automation", "innovation"],
        },
        {
            "id": "story_004",
            "Title": "Cross-Functional Stakeholder Alignment",
            "Client": "JPMC",
            "Category": "Talent & Enablement",
            "Sub-category": "Stakeholder Management",
            "Situation": "Conflicting priorities between business and tech.",
            "Task": "Align stakeholders on shared roadmap.",
            "Action": "Facilitated workshops, created shared OKRs, built trust.",
            "Result": "Achieved consensus, delivered project 2 months early.",
            "Performance": ["Delivered project 2 months early"],
            "tags": ["stakeholder", "leadership", "communication", "conflict"],
        },
        {
            "id": "story_005",
            "Title": "Team Conflict Resolution",
            "Client": "American Express",
            "Category": "Talent & Enablement",
            "Sub-category": "Team Building & Leadership",
            "Situation": "Senior engineers in heated disagreement over architecture.",
            "Task": "Resolve conflict and unify team direction.",
            "Action": "Individual 1:1s, facilitated decision framework, built consensus.",
            "Result": "Team aligned, relationship repaired, project back on track.",
            "Performance": ["Team aligned", "Relationship repaired"],
            "tags": ["conflict", "leadership", "team", "behavioral"],
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
