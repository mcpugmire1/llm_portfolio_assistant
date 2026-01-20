"""
RAG Quality Evaluation Framework for MattGPT

Evaluates Agy's response quality across:
- Source Fidelity: Ground truth phrases from stories appear
- Voice: No banned corporate-speak phrases
- Accuracy: Correct client attribution
- Authenticity: Matt's real voice preserved

See docs/EVAL_FRAMEWORK.md for full specification.

Usage:
    pytest tests/eval_rag_quality.py -v
    pytest tests/eval_rag_quality.py -k "narrative" -v
    python tests/eval_rag_quality.py --report
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# =============================================================================
# CONSTANTS
# =============================================================================

BANNED_PHRASES = [
    "stagnant growth",
    "emerging market demands",
    "limited potential",
    "prioritize maintenance over innovation",
    "strategic mindset",
    "foster collaboration",
    "stakeholder alignment",
    "meaningful outcomes",
    # NOTE: "high-trust engineering cultures" REMOVED - it's Matt's actual language in 5PSummary
    "bridge the gap between strategy and execution",
]

# =============================================================================
# GOLDEN QUERIES
# =============================================================================

GOLDEN_QUERIES = {
    # Professional Narrative (10) - Voice Critical
    "narrative": [
        {
            "id": 1,
            "query": "Tell me about Matt's leadership journey",
            "ground_truth": ["builder", "modernizer", "complexity to clarity"],
            "min_matches": 2,
            "category": "narrative",
        },
        {
            "id": 2,
            "query": "Career Intent – What I'm Looking For Next",
            "ground_truth": [
                "build something from nothing",
                "not looking for a maintenance role",
                "build what's next",
            ],
            "min_matches": 2,
            "category": "narrative",
        },
        {
            "id": 3,
            "query": "How does Matt approach complex problems?",
            "ground_truth": ["ambiguous problems", "first principles"],
            "min_matches": 1,
            "category": "narrative",
        },
        {
            "id": 4,
            "query": "What's Matt's leadership philosophy?",
            "ground_truth": [
                "trust, clarity, and shared purpose",
                "high-trust cultures",
            ],
            "min_matches": 1,
            "category": "narrative",
        },
        {
            "id": 5,
            "query": "Why is Matt exploring opportunities?",
            "ground_truth": ["intentional transition", "step back", "reconnect"],
            "min_matches": 2,
            "category": "narrative",
        },
        {
            "id": 6,
            "query": "Where does Matt do his best work?",
            "ground_truth": ["psychological safety", "challenge the status quo"],
            "min_matches": 1,
            "category": "narrative",
        },
        {
            "id": 7,
            "query": "What did Matt learn about risk ownership?",
            "ground_truth": [
                "assumptions are risks in disguise",
                "raising a risk isn't owning it",
            ],
            "min_matches": 1,
            "category": "narrative",
        },
        {
            "id": 8,
            "query": "Why is early failure important?",
            "ground_truth": ["failure is a feature", "innovation", "experiment"],
            "min_matches": 2,
            "category": "narrative",
        },
        {
            "id": 9,
            "query": "What did Matt learn about sustainable leadership?",
            "ground_truth": ["sustainable", "burnout", "pace"],
            "min_matches": 2,
            "category": "narrative",
        },
        {
            "id": 10,
            "query": "Matt's career transition after Accenture",
            "ground_truth": ["intentional", "sabbatical", "reflect"],
            "min_matches": 2,
            "category": "narrative",
        },
    ],
    # Client Attribution (6) - Accuracy
    "client": [
        {
            "id": 11,
            "query": "Tell me about Matt's payments work at JPMorgan",
            "expected_client": "JP Morgan Chase",
            "client_variants": ["JPMorgan", "JP Morgan", "JPMC"],
            "category": "client",
        },
        {
            "id": 12,
            "query": "Matt's modernization work at RBC",
            "expected_client": "RBC",
            "client_variants": ["RBC", "Royal Bank"],
            "category": "client",
        },
        {
            "id": 13,
            "query": "How did Matt scale the CIC at Accenture?",
            "expected_client": "Accenture",
            "client_variants": ["Accenture"],
            "category": "client",
        },
        {
            "id": 14,
            "query": "Norfolk Southern transformation",
            "expected_client": "Norfolk Southern",
            "client_variants": ["Norfolk Southern", "Norfolk"],
            "category": "client",
        },
        {
            "id": 15,
            "query": "Matt's work at Fiserv",
            "expected_client": "Fiserv",
            "client_variants": ["Fiserv"],
            "category": "client",
        },
        {
            "id": 16,
            "query": "Tell me about scaling learning programs",
            "expected_client": "Multiple Clients",
            "client_variants": [
                "Multiple Clients",
                "various",
                "across clients",
            ],
            "is_multi_client": True,
            "category": "client",
        },
    ],
    # Intent Routing (5) - Routing Correctness
    "intent": [
        {
            "id": 17,
            "query": "What are Matt's core themes?",
            "expected_behavior": "synthesis",
            "min_clients": 3,
            "category": "intent",
        },
        {
            "id": 18,
            "query": "Tell me about a time Matt failed",
            "expected_behavior": "behavioral",
            "check_star_format": True,
            "category": "intent",
        },
        {
            "id": 19,
            "query": "What's Matt's cloud architecture experience?",
            "expected_behavior": "technical",
            "technical_terms": ["cloud", "AWS", "architecture", "platform"],
            "category": "intent",
        },
        {
            "id": 20,
            "query": "Who is Matt Pugmire?",
            "expected_behavior": "background",
            "category": "intent",
        },
        {
            "id": 21,
            "query": "Tell me about Matt's retail experience",
            "expected_behavior": "redirect",
            "check_graceful_redirect": True,
            "category": "intent",
        },
    ],
    # Edge Cases (4) - Robustness
    "edge": [
        {
            "id": 22,
            "query": "Matt's GenAI work",
            "expected_behavior": "thin_theme",
            "theme": "Emerging Tech",
            "category": "edge",
        },
        {
            "id": 23,
            "query": "Governance and compliance work",
            "expected_behavior": "risk_theme",
            "theme": "Risk & Responsible Tech",
            "category": "edge",
        },
        {
            "id": 24,
            "query": "Tell me about JPMorgan payments",
            "followup": "Tell me more about that project",
            "expected_behavior": "multi_turn",
            "category": "edge",
        },
        {
            "id": 25,
            "query": "How did Matt transform delivery at JPMorgan?",
            "expected_behavior": "synthesis_client_combo",
            "expected_client": "JP Morgan Chase",
            "category": "edge",
        },
    ],
}


# =============================================================================
# EVALUATION HELPERS
# =============================================================================


@dataclass
class EvalResult:
    """Result of a single query evaluation."""

    query_id: int
    query: str
    category: str
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    response: str = ""
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


def check_banned_phrases(response: str) -> tuple[bool, list[str]]:
    """Check if response contains any banned phrases.

    Returns:
        Tuple of (passed, list of found banned phrases)
    """
    response_lower = response.lower()
    found = [phrase for phrase in BANNED_PHRASES if phrase.lower() in response_lower]
    return len(found) == 0, found


def check_ground_truth(
    response: str, phrases: list[str], min_matches: int
) -> tuple[bool, int, list[str]]:
    """Check if response contains required ground truth phrases.

    Uses fuzzy matching - looks for key words from each phrase.

    Returns:
        Tuple of (passed, match_count, matched_phrases)
    """
    response_lower = response.lower()
    matched = []

    for phrase in phrases:
        phrase_lower = phrase.lower()
        # Exact match
        if phrase_lower in response_lower:
            matched.append(phrase)
            continue
        # Fuzzy: check if key words appear
        words = [w for w in phrase_lower.split() if len(w) > 3]
        if words and all(w in response_lower for w in words):
            matched.append(phrase)

    return len(matched) >= min_matches, len(matched), matched


def check_client_attribution(
    response: str, expected: str, variants: list[str], is_multi: bool = False
) -> tuple[bool, str | None, bool]:
    """Check if correct client is attributed.

    For multi-client queries, checks for "Multiple Clients", "various", or 3+ distinct companies.

    Returns:
        Tuple of (passed, found_client_or_reason, is_bolded)
    """
    response_lower = response.lower()

    if is_multi:
        # Check for multi-client indicators
        multi_indicators = [
            "multiple clients",
            "various",
            "across clients",
            "several clients",
        ]
        for indicator in multi_indicators:
            if indicator in response_lower:
                return True, indicator, True  # Boldness N/A for multi-client

        # Check for 3+ distinct company names
        known_clients = [
            "jpmorgan",
            "jp morgan",
            "rbc",
            "accenture",
            "fiserv",
            "norfolk southern",
            "at&t",
            "capital one",
            "american express",
            "hsbc",
        ]
        found_clients = [c for c in known_clients if c in response_lower]
        if len(found_clients) >= 3:
            return True, f"Found {len(found_clients)} clients", True  # Boldness N/A

        return False, "Single client attribution", False

    # Single client check
    for variant in variants:
        if variant.lower() in response_lower:
            # Check if bolded (markdown)
            bold_pattern = rf"\*\*{re.escape(variant)}\*\*"
            is_bolded = bool(re.search(bold_pattern, response, re.IGNORECASE))
            return True, variant, is_bolded

    return False, None, False


def check_synthesis_mode(response: str, min_clients: int = 3) -> tuple[bool, int]:
    """Check if response is in synthesis mode with multiple clients.

    Returns:
        Tuple of (passed, client_count)
    """
    response_lower = response.lower()
    known_clients = [
        "jpmorgan",
        "jp morgan",
        "rbc",
        "accenture",
        "fiserv",
        "norfolk southern",
        "at&t",
        "capital one",
        "american express",
        "hsbc",
        "takeda",
    ]
    found = [c for c in known_clients if c in response_lower]
    return len(found) >= min_clients, len(found)


def count_clients_mentioned(response: str) -> int:
    """Count distinct clients mentioned in response."""
    response_lower = response.lower()
    known_clients = [
        "jpmorgan",
        "jp morgan",
        "rbc",
        "accenture",
        "fiserv",
        "norfolk southern",
        "at&t",
        "capital one",
        "american express",
        "hsbc",
        "takeda",
        "level 3",
    ]
    # Dedupe jp morgan variants
    found = set()
    for c in known_clients:
        if c in response_lower:
            if "jp morgan" in c or "jpmorgan" in c:
                found.add("jpmorgan")
            else:
                found.add(c)
    return len(found)


# =============================================================================
# MAIN EVALUATION FUNCTION
# =============================================================================


def evaluate_query(
    query_spec: dict, rag_fn: callable, stories: list[dict]
) -> EvalResult:
    """Evaluate a single query against the RAG system.

    Args:
        query_spec: Query specification from GOLDEN_QUERIES
        rag_fn: Function to call RAG (signature: fn(query, filters, stories) -> dict)
        stories: Story corpus

    Returns:
        EvalResult with pass/fail and details
    """
    query = query_spec["query"]
    category = query_spec["category"]
    query_id = query_spec["id"]

    result = EvalResult(
        query_id=query_id,
        query=query,
        category=category,
        passed=False,
    )

    try:
        # Call RAG
        filters = {
            "industry": "",
            "capability": "",
            "era": "",
            "clients": [],
            "domains": [],
            "roles": [],
            "tags": [],
        }
        rag_result = rag_fn(query, filters, stories)
        response = rag_result.get("answer_md", "")
        result.response = response

        if not response:
            result.error = "Empty response"
            return result

        # Voice check (all queries)
        voice_pass, banned_found = check_banned_phrases(response)
        result.checks["voice"] = voice_pass
        if banned_found:
            result.details["banned_phrases_found"] = banned_found

        # Category-specific checks
        if category == "narrative":
            # Ground truth check
            gt_pass, match_count, matched = check_ground_truth(
                response,
                query_spec["ground_truth"],
                query_spec["min_matches"],
            )
            result.checks["ground_truth"] = gt_pass
            result.details["ground_truth_matches"] = match_count
            result.details["matched_phrases"] = matched
            result.passed = voice_pass and gt_pass

        elif category == "client":
            # Client attribution check
            is_multi = query_spec.get("is_multi_client", False)
            client_pass, found, is_bolded = check_client_attribution(
                response,
                query_spec["expected_client"],
                query_spec.get("client_variants", []),
                is_multi,
            )
            result.checks["client_attribution"] = client_pass
            result.details["found_client"] = found
            result.details["is_bolded"] = is_bolded

            # For single-client queries, require boldness
            if not is_multi and client_pass and not is_bolded:
                result.checks["client_bolded"] = False
                result.details["bold_required"] = True
                result.passed = False  # Fail if client found but not bolded
            else:
                result.checks["client_bolded"] = is_bolded or is_multi
                result.passed = voice_pass and client_pass

        elif category == "intent":
            behavior = query_spec["expected_behavior"]

            if behavior == "synthesis":
                synth_pass, client_count = check_synthesis_mode(
                    response, query_spec.get("min_clients", 3)
                )
                result.checks["synthesis_mode"] = synth_pass
                result.details["client_count"] = client_count
                result.passed = voice_pass and synth_pass

            elif behavior == "redirect":
                # Check for graceful redirect (doesn't claim expertise in retail)
                response_lower = response.lower()
                has_redirect = any(
                    phrase in response_lower
                    for phrase in [
                        "don't have",
                        "haven't worked",
                        "not an area",
                        "outside",
                        "limited experience",
                    ]
                )
                result.checks["graceful_redirect"] = has_redirect
                result.passed = voice_pass and has_redirect

            else:
                # Technical, behavioral, background - just voice check for now
                result.passed = voice_pass

        elif category == "edge":
            behavior = query_spec.get("expected_behavior", "")

            if behavior == "multi_turn":
                # For multi-turn, we'd need to call twice - skip for now
                result.checks["multi_turn"] = True
                result.details["note"] = "Multi-turn test requires separate handling"
                result.passed = voice_pass

            elif behavior == "synthesis_client_combo":
                # Check both synthesis and client
                client_pass, found, is_bolded = check_client_attribution(
                    response,
                    query_spec["expected_client"],
                    ["JPMorgan", "JP Morgan", "JPMC"],
                )
                result.checks["client_attribution"] = client_pass
                result.details["found_client"] = found
                result.details["is_bolded"] = is_bolded
                # Require boldness for client
                if client_pass and not is_bolded:
                    result.checks["client_bolded"] = False
                    result.passed = False
                else:
                    result.checks["client_bolded"] = is_bolded
                    result.passed = voice_pass and client_pass

            else:
                # thin_theme, risk_theme - just voice check
                result.passed = voice_pass

    except Exception as e:
        result.error = str(e)
        result.passed = False

    return result


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def stories():
    """Load story corpus."""
    import json
    from pathlib import Path

    story_path = Path(__file__).parent.parent / "echo_star_stories_nlp.jsonl"
    stories = []
    with open(story_path) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    return stories


@pytest.fixture(scope="module")
def rag_fn():
    """Get RAG function with mocked streamlit."""
    from unittest.mock import MagicMock, patch

    # Mock streamlit
    mock_st = MagicMock()
    mock_st.session_state = {}

    with patch("streamlit.session_state", mock_st.session_state):
        with patch("ui.pages.ask_mattgpt.backend_service.st", mock_st):
            from ui.pages.ask_mattgpt.backend_service import rag_answer

            return rag_answer


# =============================================================================
# PYTEST TESTS
# =============================================================================


class TestProfessionalNarrative:
    """Test Professional Narrative queries - voice critical."""

    @pytest.mark.parametrize(
        "query_spec", GOLDEN_QUERIES["narrative"], ids=lambda q: f"Q{q['id']}"
    )
    def test_narrative_query(self, query_spec, stories, rag_fn):
        """Test each Professional Narrative query."""
        result = evaluate_query(query_spec, rag_fn, stories)

        # Always check voice
        assert result.checks.get("voice", False), (
            f"Voice check failed - banned phrases found: "
            f"{result.details.get('banned_phrases_found', [])}"
        )

        # Check ground truth
        assert result.checks.get("ground_truth", False), (
            f"Ground truth check failed - matched {result.details.get('ground_truth_matches', 0)} "
            f"of {query_spec['min_matches']} required. "
            f"Matched: {result.details.get('matched_phrases', [])}"
        )


class TestClientAttribution:
    """Test client attribution accuracy."""

    @pytest.mark.parametrize(
        "query_spec", GOLDEN_QUERIES["client"], ids=lambda q: f"Q{q['id']}"
    )
    def test_client_query(self, query_spec, stories, rag_fn):
        """Test each client attribution query."""
        result = evaluate_query(query_spec, rag_fn, stories)

        assert result.checks.get("voice", False), (
            f"Voice check failed - banned phrases found: "
            f"{result.details.get('banned_phrases_found', [])}"
        )

        assert result.checks.get("client_attribution", False), (
            f"Client attribution failed for '{query_spec['expected_client']}' - "
            f"found: {result.details.get('found_client')}"
        )

        # For single-client queries, require boldness
        if not query_spec.get("is_multi_client", False):
            assert result.checks.get("client_bolded", False), (
                f"Client '{result.details.get('found_client')}' found but NOT bolded. "
                f"Expected **{query_spec['expected_client']}** in markdown."
            )


class TestIntentRouting:
    """Test query intent routing."""

    @pytest.mark.parametrize(
        "query_spec", GOLDEN_QUERIES["intent"], ids=lambda q: f"Q{q['id']}"
    )
    def test_intent_query(self, query_spec, stories, rag_fn):
        """Test each intent routing query."""
        result = evaluate_query(query_spec, rag_fn, stories)

        assert result.checks.get("voice", False), (
            f"Voice check failed - banned phrases found: "
            f"{result.details.get('banned_phrases_found', [])}"
        )

        if query_spec["expected_behavior"] == "synthesis":
            assert result.checks.get("synthesis_mode", False), (
                f"Synthesis mode failed - only {result.details.get('client_count', 0)} "
                f"clients mentioned, need {query_spec.get('min_clients', 3)}"
            )

        elif query_spec["expected_behavior"] == "redirect":
            assert result.checks.get("graceful_redirect", False), (
                "Graceful redirect failed - response should acknowledge limited "
                "experience in retail"
            )


class TestEdgeCases:
    """Test edge cases and robustness."""

    @pytest.mark.parametrize(
        "query_spec", GOLDEN_QUERIES["edge"], ids=lambda q: f"Q{q['id']}"
    )
    def test_edge_query(self, query_spec, stories, rag_fn):
        """Test each edge case query."""
        result = evaluate_query(query_spec, rag_fn, stories)

        assert result.checks.get("voice", False), (
            f"Voice check failed - banned phrases found: "
            f"{result.details.get('banned_phrases_found', [])}"
        )


class TestVoiceOnly:
    """Quick voice-only check across all queries."""

    @pytest.mark.parametrize(
        "query_spec",
        [q for queries in GOLDEN_QUERIES.values() for q in queries],
        ids=lambda q: f"Q{q['id']}_voice",
    )
    def test_no_banned_phrases(self, query_spec, stories, rag_fn):
        """Verify no banned phrases in any response."""
        result = evaluate_query(query_spec, rag_fn, stories)

        if result.error:
            pytest.skip(f"Query error: {result.error}")

        assert result.checks.get(
            "voice", False
        ), f"Banned phrases found: {result.details.get('banned_phrases_found', [])}"


# =============================================================================
# REPORT GENERATION
# =============================================================================


def generate_report(results: list[EvalResult]) -> dict:
    """Generate evaluation report from results."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "pass_rate": 0.0,
        "by_category": {},
        "failed_queries": [],
        "voice_failures": [],
    }

    if results:
        report["pass_rate"] = report["passed"] / report["total_queries"] * 100

    # Group by category
    for category in ["narrative", "client", "intent", "edge"]:
        cat_results = [r for r in results if r.category == category]
        if cat_results:
            report["by_category"][category] = {
                "total": len(cat_results),
                "passed": sum(1 for r in cat_results if r.passed),
                "pass_rate": sum(1 for r in cat_results if r.passed)
                / len(cat_results)
                * 100,
            }

    # Collect failures
    for r in results:
        if not r.passed:
            report["failed_queries"].append(
                {
                    "id": r.query_id,
                    "query": r.query,
                    "category": r.category,
                    "checks": r.checks,
                    "details": r.details,
                    "error": r.error,
                }
            )
        if not r.checks.get("voice", True):
            report["voice_failures"].append(
                {
                    "id": r.query_id,
                    "query": r.query,
                    "banned_found": r.details.get("banned_phrases_found", []),
                }
            )

    return report


def run_full_evaluation() -> dict:
    """Run full evaluation suite and return report."""
    import json
    from pathlib import Path
    from unittest.mock import MagicMock, patch

    # Load stories
    story_path = Path(__file__).parent.parent / "echo_star_stories_nlp.jsonl"
    stories = []
    with open(story_path) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))

    print(f"Loaded {len(stories)} stories")

    # Setup mocks
    mock_st = MagicMock()
    mock_st.session_state = {}

    results = []

    with patch("streamlit.session_state", mock_st.session_state):
        with patch("ui.pages.ask_mattgpt.backend_service.st", mock_st):
            from ui.pages.ask_mattgpt.backend_service import rag_answer

            # Run all queries
            all_queries = [q for queries in GOLDEN_QUERIES.values() for q in queries]

            for i, query_spec in enumerate(all_queries, 1):
                print(
                    f"[{i}/{len(all_queries)}] Q{query_spec['id']}: {query_spec['query'][:50]}..."
                )
                result = evaluate_query(query_spec, rag_answer, stories)
                results.append(result)
                status = "✅" if result.passed else "❌"
                print(f"  {status} passed={result.passed}")

    return generate_report(results)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="MattGPT RAG Quality Evaluation")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    parser.add_argument("--output", type=str, help="Output file for report JSON")
    args = parser.parse_args()

    if args.report:
        print("Running full evaluation...")
        report = run_full_evaluation()

        print("\n" + "=" * 60)
        print("EVALUATION REPORT")
        print("=" * 60)
        print(f"Total Queries: {report['total_queries']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Pass Rate: {report['pass_rate']:.1f}%")

        print("\nBy Category:")
        for cat, stats in report["by_category"].items():
            print(
                f"  {cat}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.1f}%)"
            )

        if report["voice_failures"]:
            print("\nVoice Failures (banned phrases):")
            for vf in report["voice_failures"]:
                print(f"  Q{vf['id']}: {vf['banned_found']}")

        if report["failed_queries"]:
            print(f"\nFailed Queries ({len(report['failed_queries'])}):")
            for fq in report["failed_queries"][:5]:
                print(f"  Q{fq['id']} [{fq['category']}]: {fq['query'][:40]}...")
                print(f"    Checks: {fq['checks']}")

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_path}")
    else:
        print("Use --report to run full evaluation")
        print("Or run: pytest tests/eval_rag_quality.py -v")


if __name__ == "__main__":
    main()
