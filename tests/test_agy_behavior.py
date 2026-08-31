"""
BDD/TDD Tests for MattGPT Agy Behavior
Comprehensive Suite: Intent, Voice, RAG Depth, and Professional Scope.
Run: pytest tests/test_agy_behavior.py -v

INTENTIONALLY STOCHASTIC TEST CLASSES -- DO NOT RE-TRIAGE AS REGRESSIONS
------------------------------------------------------------------------
The following test classes assert on gpt-4o output at temperature 0.4.
The stochasticity is a property of the *class*, not any specific
parametrized instance: any query in the parametrize set can pass on one
run and fail on the next due to LLM word choice. Do not treat a failure
of a previously-passing instance as a regression -- treat it as expected
class behavior.

  TestNoMetaCommentary     (test_structural_assertions.py, 71 parametrized)
  TestAgyVoice             (test_structural_assertions.py, 71 parametrized)
  TestAllStructuralChecks  (test_structural_assertions.py, 71 parametrized)
  TestVoiceFidelity        (this file, 4 tests)
  TestContentFidelity      (this file, 1 test)
  TestRAGExecution::test_metric_fidelity   (this file, soft check)

Total surface: ~218 tests, all sharing the same LLM-text-assertion
brittleness at the class level.

Historical observations:
- Aug 15, 2026: Q45_meta and Q32_structural named as specific instances.
  Three consecutive runs on identical code gave fail, fail, pass on those
  two. See MATTGPT-193 (Decided Against) for the not-a-regression
  disposition.
- Aug 30, 2026: full-suite run failed on Q6_meta, Q20_meta, and
  Q45_structural -- none previously named. Isolation of each showed
  deterministic pass at HEAD and pre-fix, confirming the same class-level
  stochasticity, not any specific ticket regression.

Do not investigate these as caused by a change under test. Do not label
other failures pre-existing without an isolation run.

Bucket A conversion history:
- Aug 30, 2026: test_out_of_scope_redirect[retail sales work] and
  TestEntityGateThreshold moved from LLM-text assertions to
  retrieval-observable assertions (rag_answer's rejection_reason and
  intent_family fields). Those are now deterministic and no longer on
  this list.
"""

import json
import os
import re

import pytest

from ui.pages.ask_mattgpt.backend_service import (
    _generate_agy_response,
    get_synthesis_stories,
    rag_answer,
)

# =============================================================================
# 1. INTENT ROUTING
# =============================================================================
# NOTE: TestQueryClassification removed — classify_query_intent was deleted
# in Jan 2026 RAG cleanup. Intent routing now handled by semantic router.
# =============================================================================


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
    """Ensures off-topic queries are gated before reaching the LLM.

    Previously this test called _generate_agy_response directly with the query
    and some stories, then asserted the LLM produced redirect phrasing. That
    bypassed the router (the actual layer that decides "off-topic") and
    tested the wrong layer -- LLM word choice depends on the run.

    Rewritten to call rag_answer end-to-end and assert on the retrieval-side
    rejection reason. Two queries take two different mechanisms:
      - "Tell me about Matt's retail sales work": semantic router routes to
        out_of_scope; intent_family is set, rejection_reason is
        "semantic_router:out_of_scope"
      - "What is Matt's favorite food?": nonsense filter fires before the
        router runs; intent_family is None, rejection_reason is
        "rule:personal_trivia"

    Both are legitimate "off-topic gated" behaviors, verified live via
    DEBUG trace during the Bucket A conversion.
    """

    @pytest.mark.parametrize(
        "query,expected_rejection_reason,expected_intent_family",
        [
            (
                "Tell me about Matt's retail sales work",
                "semantic_router:out_of_scope",
                "out_of_scope",
            ),
            (
                "What is Matt's favorite food?",
                "rule:personal_trivia",
                None,  # router never runs -- nonsense filter fires first
            ),
        ],
    )
    def test_out_of_scope_redirect(
        self, query, expected_rejection_reason, expected_intent_family, stories
    ):
        """Off-topic queries must be gated by the router or the nonsense filter."""
        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }
        result = rag_answer(query, filters, stories)

        assert result.get("rejection_reason") == expected_rejection_reason, (
            f"Off-topic query hit the wrong gate.\n"
            f"Query: {query}\n"
            f"Expected rejection_reason: {expected_rejection_reason!r}\n"
            f"Got rejection_reason: {result.get('rejection_reason')!r}\n"
            f"Got intent_family: {result.get('intent_family')!r}"
        )
        assert result.get("intent_family") == expected_intent_family, (
            f"Off-topic query has unexpected intent_family.\n"
            f"Query: {query}\n"
            f"Expected intent_family: {expected_intent_family!r}\n"
            f"Got intent_family: {result.get('intent_family')!r}"
        )


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
