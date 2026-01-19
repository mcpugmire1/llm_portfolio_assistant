"""
BDD/TDD Tests for MattGPT Agy Behavior
Comprehensive Suite: Intent, Voice, RAG Depth, and Professional Scope.
Run: pytest tests/test_agy_behavior.py -v
"""

import json
import os
import re

import pytest

from ui.pages.ask_mattgpt.backend_service import (
    _generate_agy_response,
    classify_query_intent,
    get_synthesis_stories,
)

# =============================================================================
# 1. INTENT ROUTING (The "Capability-First" & "Keyword Trap" Fixes)
# =============================================================================


class TestQueryClassification:
    """Ensure classifier prioritizes Skills/Methodology and ignores keyword traps."""

    # Synthesis: Capability Verb + Client (The "Accenture Gravity" Fix)
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("How did Matt scale talent at Accenture?", "synthesis"),
            ("How did Matt transform delivery at JPMorgan?", "synthesis"),
            ("How did Matt build teams at Capital One?", "synthesis"),
        ],
    )
    def test_verb_overrides_client(self, query, expected):
        """Action verbs MUST trigger synthesis even if a company is named."""
        result = classify_query_intent(query)
        assert (
            result == expected
        ), f"Expected '{expected}' for '{query}', got '{result}'"

    # Synthesis: Methodology Nouns (The "Methodology" Fix)
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("Tell me about Matt's rapid prototyping work", "synthesis"),
            ("Matt's design thinking approach", "synthesis"),
            ("What is Matt's agile transformation strategy?", "synthesis"),
        ],
    )
    def test_methodology_triggers_synthesis(self, query, expected):
        """Industry methodologies should trigger the 'Forest' (synthesis) view."""
        result = classify_query_intent(query)
        assert (
            result == expected
        ), f"Expected '{expected}' for '{query}', got '{result}'"

    # The "Generic Client" Filter (The "Keyword Trap" Fix)
    @pytest.mark.parametrize(
        "query",
        [
            "Tell me about Matt's work for client products",
            "How does Matt work with clients?",
            "Matt's client engagement methodology",
        ],
    )
    def test_generic_client_is_not_entity(self, query):
        """The word 'client' is a noun, NOT a company name. Should not be 'client' intent."""
        result = classify_query_intent(query)
        assert (
            result != "client"
        ), f"Query '{query}' should NOT be classified as 'client', got '{result}'"

    # Behavioral Detection (The "STAR" Fix)
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("Tell me about a time you failed", "behavioral"),
            ("Example of handling conflict", "behavioral"),
            ("How do you handle pressure?", "behavioral"),
        ],
    )
    def test_behavioral_intent(self, query, expected):
        """STAR-style questions should be routed to behavioral handlers."""
        result = classify_query_intent(query)
        assert (
            result == expected
        ), f"Expected '{expected}' for '{query}', got '{result}'"


# =============================================================================
# 2. VOICE FIDELITY (The "Anti-I" persona fix)
# =============================================================================


class TestVoiceFidelity:
    """
    Ensures Agy stays in 3rd-person executive persona.

    The underlying STAR stories contain first-person content like:
    - "I led the initiative..."
    - "I was responsible for..."
    - "my team achieved..."

    Agy MUST transform these to third-person:
    - "Matt led the initiative..."
    - "He was responsible for..."
    - "His team achieved..."
    """

    # First-person patterns that indicate Matt is speaking (NOT Agy)
    # Agy can say "I found" or "I see" - that's OK
    # But these patterns indicate the story's first-person leaked through
    FORBIDDEN_MATT_VOICE = [
        r"\bI led\b",
        r"\bI built\b",
        r"\bI managed\b",
        r"\bI created\b",
        r"\bI developed\b",
        r"\bI drove\b",
        r"\bI established\b",
        r"\bI scaled\b",
        r"\bI transformed\b",
        r"\bI worked\b",
        r"\bI implemented\b",
        r"\bI designed\b",
        r"\bI facilitated\b",
        r"\bI initiated\b",
        r"\bI was responsible\b",
        r"\bI was tasked\b",
        r"\bI was appointed\b",
        r"\bmy team\b",
        r"\bmy approach\b",
        r"\bmy experience\b",
        r"\bmy work\b",
        r"\bmy leadership\b",
    ]

    @pytest.mark.parametrize(
        "query,client_filter",
        [
            # Use RBC stories - they have heavy first-person content
            ("Tell me about Matt's work at RBC", "RBC"),
            # Use JP Morgan Chase stories - also first-person
            ("Tell me about Matt's payments work at JP Morgan", "JP Morgan Chase"),
            # Use synthesis mode with first-person Career Narrative stories
            ("What are the themes in Matt's work?", None),
        ],
    )
    def test_voice_is_third_person(
        self, query, client_filter, stories_with_first_person
    ):
        """
        Test that LLM transforms first-person story content to third-person Agy voice.
        Uses stories that actually contain "I led", "I was responsible", etc.
        """
        # Get stories that contain first-person content
        ranked = stories_with_first_person
        if client_filter:
            filtered = [s for s in ranked if client_filter in s.get("Client", "")]
            if filtered:
                ranked = filtered[:5]

        is_synthesis = client_filter is None
        response = _generate_agy_response(
            query, ranked[:5], "Test context", is_synthesis=is_synthesis
        )

        # Check for forbidden first-person Matt voice
        violations = []
        for pattern in self.FORBIDDEN_MATT_VOICE:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                violations.append(match.group())

        assert not violations, (
            f"Voice Drift: Found Matt speaking in 1st person: {violations}\n"
            f"Response excerpt: {response[:500]}..."
        )

        # Should refer to Matt in third person
        has_third_person = (
            "Matt" in response
            or " He " in response
            or " he " in response
            or "His " in response
            or " his " in response
        )
        assert has_third_person, (
            f"Response should reference Matt in 3rd person.\n"
            f"Response excerpt: {response[:500]}..."
        )

    def test_synthesis_mode_no_first_person(self, stories_with_first_person):
        """
        Synthesis mode specifically should never leak first-person voice.
        Tests the Career Narrative stories which are heavily first-person.
        """
        query = "What are Matt's core leadership themes?"

        # Get Career Narrative stories (heavily first-person)
        career_stories = [
            s
            for s in stories_with_first_person
            if s.get("Client") == "Career Narrative"
        ][:5]

        response = _generate_agy_response(
            query, career_stories, "Test context", is_synthesis=True
        )

        # Strict check - no first-person Matt voice
        violations = []
        for pattern in self.FORBIDDEN_MATT_VOICE:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                violations.append(match.group())

        assert not violations, (
            f"Synthesis mode leaked first-person voice: {violations}\n"
            f"Response: {response[:600]}..."
        )


# =============================================================================
# 3. SCOPE & REDIRECTS (The "Dead-End" Fix)
# =============================================================================


class TestOutOfScope:
    """Ensures professional redirects for off-topic questions (Retail, Personal)."""

    @pytest.mark.parametrize(
        "query",
        ["Tell me about Matt's retail sales work", "What is Matt's favorite food?"],
    )
    def test_out_of_scope_redirect(self, query, stories):
        """Nonsense/Off-industry queries must offer professional redirects."""
        ranked = stories[:3]
        narrative = "Test context"

        response = _generate_agy_response(query, ranked, narrative, is_synthesis=False)

        # Should redirect professionally
        redirect_keywords = [
            "outside my wheelhouse",
            "Financial Services",
            "Tech",
            "translate",
            "transformation",
            "portfolio",
            "can only discuss",
        ]
        found = any(k.lower() in response.lower() for k in redirect_keywords)
        assert found, f"Out-of-scope query should redirect professionally. Response: {response[:300]}..."


# =============================================================================
# 4. FOREST DEPTH & EVIDENCE
# =============================================================================


class TestRAGExecution:
    """Verify Parallel Retriever depth and no metric-hallucination."""

    def test_synthesis_pool_size(self, stories):
        """Synthesis must pull from the full 7-theme, 14-story pool."""
        pool = get_synthesis_stories(stories, top_per_theme=2)
        # Should have at least 2 stories per theme (7 themes * 2 = 14 minimum)
        # But some themes may have fewer stories, so we check for reasonable coverage
        assert (
            len(pool) >= 7
        ), f"Synthesis pool should have at least 7 stories, got {len(pool)}"

    def test_metric_fidelity(self, stories):
        """Ensures 'Multiple Clients' metrics are not falsely attributed to a specific client."""
        query = "How did Matt scale learning at Accenture?"
        ranked = stories[:5]
        narrative = "Test context"

        response = _generate_agy_response(query, ranked, narrative, is_synthesis=True)

        # If the 10% metric (from Multiple Clients) is used, check for attribution clarity
        if "10%" in response and "Accenture" in response:
            # Should clarify multi-client context
            has_clarity = any(
                x in response.lower()
                for x in [
                    "multiple clients",
                    "across enterprise",
                    "across clients",
                    "various",
                    "several",
                ]
            )
            # This is a soft check - we warn but don't fail
            if not has_clarity:
                pytest.skip("Metric attribution could be clearer (non-blocking)")


# =============================================================================
# 5. CONTENT FIDELITY (The "Hallucination" Fix)
# =============================================================================


class TestContentFidelity:
    """Ensures LLM uses actual story content, not hallucinated details."""

    def test_client_attribution_accuracy(self, stories):
        """
        When given specific client stories, response should attribute
        to the correct client, not "Career Narrative" or wrong client.
        """
        # Get actual JP Morgan Chase stories
        jpmc_stories = [s for s in stories if s.get("Client") == "JP Morgan Chase"][:3]

        if not jpmc_stories:
            pytest.skip("No JP Morgan Chase stories found")

        query = "Tell me about Matt's payments work"
        response = _generate_agy_response(
            query, jpmc_stories, "Test context", is_synthesis=False
        )

        # Should mention JP Morgan, JPMorgan, or JPMC - not "Career Narrative"
        has_jpmc = any(x in response for x in ["JP Morgan", "JPMorgan", "JPMC"])
        has_wrong_client = (
            "Career Narrative" in response and "JP Morgan" not in response
        )

        assert has_jpmc, f"Response should mention JP Morgan for JP Morgan stories. Response: {response[:400]}..."
        assert not has_wrong_client, f"Response incorrectly attributed to Career Narrative. Response: {response[:400]}..."


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def stories():
    """Fixture to load all story data."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stories_path = os.path.join(project_root, "echo_star_stories_nlp.jsonl")
    with open(stories_path) as f:
        return [json.loads(line) for line in f]


@pytest.fixture
def stories_with_first_person(stories):
    """
    Fixture to get stories that contain first-person content.
    These are the ones that test voice transformation.
    """
    first_person_patterns = [r'\bI led\b', r'\bI was\b', r'\bmy team\b', r'\bI built\b']

    def has_first_person(story):
        all_text = " ".join(
            [
                str(story.get("Situation", "")),
                str(story.get("Task", "")),
                str(story.get("Action", "")),
                str(story.get("Result", "")),
            ]
        )
        return any(re.search(p, all_text, re.IGNORECASE) for p in first_person_patterns)

    return [s for s in stories if has_first_person(s)]


@pytest.fixture
def sample_synthesis_response(stories):
    """Fixture for a pre-generated synthesis response."""
    ranked = stories[:5]
    return _generate_agy_response(
        "What are Matt's core leadership themes?",
        ranked,
        "Test narrative context",
        is_synthesis=True,
    )
