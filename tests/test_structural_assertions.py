"""
Structural Assertion Tests for MattGPT RAG Pipeline

Pre-refactoring baseline tests that verify:
1. No meta-commentary in responses
2. Agy voice consistency
3. Hardcoded constants match JSONL source of truth

Usage:
    pytest tests/test_structural_assertions.py -v
    pytest tests/test_structural_assertions.py -k "meta_commentary" -v
    python tests/test_structural_assertions.py --report
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import golden queries (must be after path setup)
from tests.eval_rag_quality import GOLDEN_QUERIES  # noqa: E402

# =============================================================================
# STRUCTURAL ASSERTION FUNCTIONS
# =============================================================================


def assert_no_meta_commentary(response: str) -> tuple[bool, list[str]]:
    """Check if response contains meta-commentary patterns.

    Meta-commentary is when the LLM talks ABOUT the story instead of
    answering the question. These patterns break Agy's voice.

    Args:
        response: The LLM response to check

    Returns:
        Tuple of (passed, list of found patterns)

    Fails if response contains patterns like:
        - "This demonstrates..."
        - "In essence..."
        - "Matt's ability to..."
        - "This reflects..."
        - "This story illustrates..."
        - "This example shows..."
        - "This reveals Matt's..."
    """
    META_PATTERNS = [
        # "This X" patterns - talking ABOUT the story
        r"\bThis demonstrates\b",
        r"\bThis reflects\b",
        r"\bThis illustrates\b",
        r"\bThis showcases\b",
        r"\bThis highlights\b",
        r"\bThis story demonstrates\b",
        r"\bThis story illustrates\b",
        r"\bThis story reflects\b",
        r"\bThis example shows\b",
        r"\bThis example demonstrates\b",
        r"\bThis reveals Matt's\b",
        r"\bThis reveals his\b",
        # "In essence" / "In summary" - academic tone
        r"\bIn essence,?\b",
        r"\bIn summary,?\b",
        r"\bEssentially,?\b",
        # "Matt's ability to" - generic praise
        r"\bMatt's ability to\b",
        r"\bhis ability to\b",
        # "demonstrates his" / "reflects his" - meta-commentary
        r"\bdemonstrates his\b",
        r"\breflects his\b",
        r"\bshowcases his\b",
        r"\bhighlights his\b",
        r"\breveals his pattern of\b",
    ]

    found = []
    for pattern in META_PATTERNS:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            found.append(match.group())

    return len(found) == 0, found


def assert_agy_voice(response: str) -> tuple[bool, list[str]]:
    """Check if response maintains Agy's voice consistency.

    Agy is a third-person narrator (she talks about Matt).
    Agy should NOT:
    - Use multiple 🐾 emojis (one per response is the standard)
    - Use "we" pronouns (Agy is singular)
    - Speak in third person about herself ("Agy thinks...", "As Agy,...")

    Args:
        response: The LLM response to check

    Returns:
        Tuple of (passed, list of violations)
    """
    violations = []

    # Check for multiple 🐾 emojis (should be exactly 1 at the start)
    paw_count = response.count("🐾")
    if paw_count > 1:
        violations.append(f"Multiple 🐾 emojis ({paw_count})")
    elif paw_count == 0:
        violations.append("Missing 🐾 emoji")

    # Check for "we" pronouns (Agy is singular, not plural)
    # Be careful: "we" can legitimately appear in quoted content or team context
    # Only flag standalone "we" as subject pronoun
    WE_PATTERNS = [
        r"^We\s",  # "We can see..."
        r"\.\s*We\s",  # ". We found..."
        r"!\s*We\s",  # "! We think..."
        r"\bWe're\b",  # "We're"
        r"\bWe've\b",  # "We've"
        r"\bWe'll\b",  # "We'll"
        r"\bour team\b",  # "our team" (Agy doesn't have a team)
        r"\bour analysis\b",  # "our analysis"
    ]
    for pattern in WE_PATTERNS:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            violations.append(f"'we' pronoun: {match.group()}")

    # Check for Agy speaking about herself in third person
    SELF_REFERENCE_PATTERNS = [
        r"\bAgy thinks\b",
        r"\bAgy believes\b",
        r"\bAgy knows\b",
        r"\bAgy found\b",
        r"\bAs Agy,\b",
        r"\bAgy can\b",
        r"\bAgy's perspective\b",
    ]
    for pattern in SELF_REFERENCE_PATTERNS:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            violations.append(f"Self-reference: {match.group()}")

    return len(violations) == 0, violations


def assert_no_hardcoded_drift(stories: list[dict]) -> tuple[bool, dict[str, list[str]]]:
    """Check if hardcoded constants match JSONL source of truth.

    Compares:
    - ENTITY_NORMALIZATION values → must exist in actual JSONL
    - Excluded clients list → must match pattern-based detection
    - Verbatim phrases → must exist in actual story content

    Args:
        stories: Story corpus from JSONL

    Returns:
        Tuple of (passed, dict of drift categories to mismatches)
    """
    from ui.pages.ask_mattgpt.backend_service import ENTITY_NORMALIZATION
    from utils.client_utils import is_generic_client

    drift = {
        "entity_normalization": [],
        "excluded_clients": [],
        "verbatim_phrases": [],
    }

    # === 1. Check ENTITY_NORMALIZATION ===
    # All normalized values should exist in JSONL
    all_entity_values = set()
    for s in stories:
        for field_name in ["Client", "Employer", "Division", "Project", "Place"]:
            val = s.get(field_name)
            if val:
                all_entity_values.add(val)

    for alias, normalized in ENTITY_NORMALIZATION.items():
        if normalized not in all_entity_values:
            drift["entity_normalization"].append(
                f"'{alias}' -> '{normalized}' (not in JSONL)"
            )

    # === 2. Verify pattern-based client filtering works ===
    # backend_service.py now uses is_generic_client() instead of hardcoded values
    # This check verifies the pattern catches actual generic clients in the data
    actual_clients = {s.get("Client") for s in stories if s.get("Client")}

    # Verify is_generic_client catches known generic patterns
    for client in actual_clients:
        # Clients ending in "Clients" or "Project" should be filtered
        if client.lower().endswith("clients") or client.lower().endswith("project"):
            if not is_generic_client(client):
                drift["excluded_clients"].append(
                    f"'{client}' should be filtered but is_generic_client() missed it"
                )

    # === 3. Check verbatim phrases exist in story content ===
    # These phrases should appear in Professional Narrative stories
    VERBATIM_PHRASES = [
        "builder",
        "modernizer",
        "complexity to clarity",
        "build something from nothing",
        "not looking for a maintenance role",
    ]

    # Collect all text from Professional Narrative stories
    narrative_text = ""
    for s in stories:
        if (
            s.get("Theme") == "Professional Narrative"
            or s.get("Client") == "Career Narrative"
        ):
            # Include 5PSummary, Situation, Task, Action, Result
            narrative_text += " " + str(s.get("5PSummary", ""))
            narrative_text += " " + str(s.get("Situation", ""))
            narrative_text += " " + str(s.get("Task", ""))
            narrative_text += " " + str(s.get("Action", ""))
            narrative_text += " " + str(s.get("Result", ""))
            narrative_text += " " + str(s.get("Title", ""))

    narrative_lower = narrative_text.lower()

    for phrase in VERBATIM_PHRASES:
        if phrase.lower() not in narrative_lower:
            drift["verbatim_phrases"].append(
                f"'{phrase}' not found in Professional Narrative stories"
            )

    # Calculate overall pass
    total_drift = sum(len(v) for v in drift.values())
    return total_drift == 0, drift


# =============================================================================
# COMBINED STRUCTURAL CHECK
# =============================================================================


@dataclass
class StructuralResult:
    """Result of structural assertion checks for a single response."""

    query_id: int
    query: str
    meta_passed: bool = True
    meta_violations: list[str] = field(default_factory=list)
    voice_passed: bool = True
    voice_violations: list[str] = field(default_factory=list)
    overall_passed: bool = True


def run_structural_checks(response: str, query_id: int, query: str) -> StructuralResult:
    """Run all structural checks on a response."""
    result = StructuralResult(query_id=query_id, query=query)

    # Meta-commentary check
    result.meta_passed, result.meta_violations = assert_no_meta_commentary(response)

    # Agy voice check
    result.voice_passed, result.voice_violations = assert_agy_voice(response)

    # Overall pass
    result.overall_passed = result.meta_passed and result.voice_passed

    return result


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def stories():
    """Load story corpus."""
    story_path = Path(__file__).parent.parent / "echo_star_stories_nlp.jsonl"
    stories = []
    with open(story_path) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    return stories


@pytest.fixture(scope="module")
def rag_fn(stories):
    """Get RAG function with mocked streamlit and synced metadata."""
    from unittest.mock import MagicMock, patch

    mock_st = MagicMock()
    mock_st.session_state = {}

    with patch("streamlit.session_state", mock_st.session_state):
        with patch("ui.pages.ask_mattgpt.backend_service.st", mock_st):
            from ui.pages.ask_mattgpt.backend_service import (
                rag_answer,
                sync_portfolio_metadata,
            )

            sync_portfolio_metadata(stories)
            return rag_answer


# =============================================================================
# PYTEST TESTS
# =============================================================================


class TestNoMetaCommentary:
    """Test that responses don't contain meta-commentary."""

    @pytest.mark.parametrize(
        "query_spec",
        [q for queries in GOLDEN_QUERIES.values() for q in queries],
        ids=lambda q: f"Q{q['id']}_meta",
    )
    def test_no_meta_commentary(self, query_spec, stories, rag_fn):
        """Verify no meta-commentary patterns in response."""
        query = query_spec["query"]
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

        if not response:
            pytest.skip("Empty response")

        passed, violations = assert_no_meta_commentary(response)
        assert passed, f"Meta-commentary found: {violations}"


class TestAgyVoice:
    """Test Agy voice consistency."""

    @pytest.mark.parametrize(
        "query_spec",
        [q for queries in GOLDEN_QUERIES.values() for q in queries],
        ids=lambda q: f"Q{q['id']}_voice",
    )
    def test_agy_voice(self, query_spec, stories, rag_fn):
        """Verify Agy voice consistency in response."""
        query = query_spec["query"]
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

        if not response:
            pytest.skip("Empty response")

        passed, violations = assert_agy_voice(response)
        assert passed, f"Agy voice violations: {violations}"


class TestHardcodedDrift:
    """Test that hardcoded constants match JSONL source of truth."""

    def test_no_hardcoded_drift(self, stories):
        """Verify hardcoded constants match JSONL."""
        passed, drift = assert_no_hardcoded_drift(stories)

        # Build detailed error message
        errors = []
        for category, items in drift.items():
            if items:
                errors.append(f"\n{category}:")
                for item in items:
                    errors.append(f"  - {item}")

        assert passed, f"Hardcoded drift detected:{' '.join(errors)}"


class TestAllStructuralChecks:
    """Combined structural checks across all queries."""

    @pytest.mark.parametrize(
        "query_spec",
        [q for queries in GOLDEN_QUERIES.values() for q in queries],
        ids=lambda q: f"Q{q['id']}_structural",
    )
    def test_structural_checks(self, query_spec, stories, rag_fn):
        """Run all structural checks on each query."""
        query = query_spec["query"]
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

        if not response:
            pytest.skip("Empty response")

        result = run_structural_checks(response, query_spec["id"], query)

        errors = []
        if not result.meta_passed:
            errors.append(f"Meta-commentary: {result.meta_violations}")
        if not result.voice_passed:
            errors.append(f"Voice violations: {result.voice_violations}")

        assert result.overall_passed, f"Structural failures: {errors}"


# =============================================================================
# REPORT GENERATION
# =============================================================================


def run_structural_baseline_report():
    """Run all structural checks and generate baseline report."""
    from unittest.mock import MagicMock, patch

    # Load stories
    story_path = Path(__file__).parent.parent / "echo_star_stories_nlp.jsonl"
    stories = []
    with open(story_path) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))

    print(f"Loaded {len(stories)} stories")

    # Setup mocks and sync metadata
    mock_st = MagicMock()
    mock_st.session_state = {}

    results = []
    drift_report = None

    with patch("streamlit.session_state", mock_st.session_state):
        with patch("ui.pages.ask_mattgpt.backend_service.st", mock_st):
            from ui.pages.ask_mattgpt.backend_service import (
                rag_answer,
                sync_portfolio_metadata,
            )

            sync_portfolio_metadata(stories)

            # 1. Run hardcoded drift check (once)
            print("\n" + "=" * 70)
            print("HARDCODED DRIFT CHECK")
            print("=" * 70)

            drift_passed, drift = assert_no_hardcoded_drift(stories)
            drift_report = {
                "passed": drift_passed,
                "details": drift,
            }

            if drift_passed:
                print("✅ No hardcoded drift detected")
            else:
                print("❌ DRIFT DETECTED:")
                for category, items in drift.items():
                    if items:
                        print(f"\n  {category}:")
                        for item in items:
                            print(f"    - {item}")

            # 2. Run structural checks on all queries
            print("\n" + "=" * 70)
            print("STRUCTURAL CHECKS (31 queries)")
            print("=" * 70)

            all_queries = [q for queries in GOLDEN_QUERIES.values() for q in queries]

            for i, query_spec in enumerate(all_queries, 1):
                query = query_spec["query"]
                query_id = query_spec["id"]

                print(f"\n[{i}/{len(all_queries)}] Q{query_id}: {query[:50]}...")

                filters = {
                    "industry": "",
                    "capability": "",
                    "era": "",
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                }

                try:
                    rag_result = rag_answer(query, filters, stories)
                    response = rag_result.get("answer_md", "")

                    if not response:
                        print("  ⚠️ Empty response")
                        continue

                    result = run_structural_checks(response, query_id, query)
                    results.append(result)

                    status = "✅" if result.overall_passed else "❌"
                    print(
                        f"  {status} meta={result.meta_passed}, voice={result.voice_passed}"
                    )

                    if not result.meta_passed:
                        print(f"    Meta violations: {result.meta_violations[:3]}")
                    if not result.voice_passed:
                        print(f"    Voice violations: {result.voice_violations[:3]}")

                except Exception as e:
                    print(f"  ⚠️ Error: {e}")

    # 3. Summary
    print("\n" + "=" * 70)
    print("BASELINE SUMMARY")
    print("=" * 70)

    total = len(results)
    structural_passed = sum(1 for r in results if r.overall_passed)
    meta_passed = sum(1 for r in results if r.meta_passed)
    voice_passed = sum(1 for r in results if r.voice_passed)

    print(f"\nTotal Queries: {total}")
    print(
        f"Structural Pass: {structural_passed}/{total} ({100*structural_passed/total:.1f}%)"
    )
    print(f"  - Meta-commentary: {meta_passed}/{total} ({100*meta_passed/total:.1f}%)")
    print(f"  - Agy Voice: {voice_passed}/{total} ({100*voice_passed/total:.1f}%)")
    print(f"\nHardcoded Drift: {'PASS' if drift_report['passed'] else 'FAIL'}")

    # 4. Failed queries detail
    failed = [r for r in results if not r.overall_passed]
    if failed:
        print(f"\n{'=' * 70}")
        print(f"FAILED QUERIES ({len(failed)})")
        print("=" * 70)

        for r in failed[:10]:  # Show first 10
            print(f"\nQ{r.query_id}: {r.query[:60]}...")
            if not r.meta_passed:
                print(f"  Meta: {r.meta_violations}")
            if not r.voice_passed:
                print(f"  Voice: {r.voice_violations}")

    # 5. Drift detail
    if not drift_report["passed"]:
        print(f"\n{'=' * 70}")
        print("DRIFT DETAILS")
        print("=" * 70)
        for category, items in drift_report["details"].items():
            if items:
                print(f"\n{category}:")
                for item in items:
                    print(f"  - {item}")

    return {
        "timestamp": datetime.now().isoformat(),
        "total_queries": total,
        "structural_passed": structural_passed,
        "meta_passed": meta_passed,
        "voice_passed": voice_passed,
        "hardcoded_drift": drift_report,
        "failed_queries": [
            {
                "id": r.query_id,
                "query": r.query,
                "meta_violations": r.meta_violations,
                "voice_violations": r.voice_violations,
            }
            for r in failed
        ],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MattGPT Structural Assertion Tests")
    parser.add_argument(
        "--report", action="store_true", help="Generate baseline report"
    )
    parser.add_argument("--output", type=str, help="Output file for report JSON")
    args = parser.parse_args()

    if args.report:
        report = run_structural_baseline_report()

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_path}")
    else:
        print("Use --report to generate baseline report")
        print("Or run: pytest tests/test_structural_assertions.py -v")
