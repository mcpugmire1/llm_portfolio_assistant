"""
Diagnostic Script: Story Transformation with Client Gravity Test

Purpose: Diagnose why the LLM is failing Persona and Fidelity checks
despite the Agentic RAG routing working correctly.

Run: python diagnose_transformation.py
"""

import re

from ui.pages.ask_mattgpt.backend_service import _generate_agy_response

# =============================================================================
# TEST CASE: A synthetic story known to be in first-person with specific metrics
# =============================================================================
test_story = {
    "id": "test-001",
    "Client": "Multiple Clients",
    "Title": "Scaling Global Engineering Teams",
    "Theme": "Talent & Enablement",
    "Situation": "I led a team of 50 engineers to scale a global platform.",
    "Task": "I was responsible for building a mentoring program.",
    "Action": "I personally developed the mentoring program and coached senior engineers.",
    "Result": "This resulted in a 10% retention boost and improved team morale.",
}

# THE QUERY: One designed to trigger "Client Gravity"
query = "How did Matt scale talent at Accenture?"


def run_diagnostic():
    print("=" * 70)
    print("DIAGNOSTIC: Story Transformation with Client Gravity")
    print("=" * 70)

    print(f"\nQUERY: {query}")
    print(f"PROVIDED SOURCE CLIENT: {test_story['Client']}")
    print("\nRAW STORY CONTENT:")
    print(f"  Situation: {test_story['Situation']}")
    print(f"  Task: {test_story['Task']}")
    print(f"  Action: {test_story['Action']}")
    print(f"  Result: {test_story['Result']}")

    # Call the actual function with correct signature
    # _generate_agy_response(question, ranked_stories, answer_context, is_synthesis)
    response = _generate_agy_response(
        query,
        [test_story],  # ranked_stories
        "Test context",  # answer_context (fallback)
        is_synthesis=True,  # This is a synthesis query
    )

    print(f"\n{'=' * 70}")
    print("LLM RESPONSE")
    print("=" * 70)
    print(response)

    print(f"\n{'=' * 70}")
    print("ASSERTION CHECKS")
    print("=" * 70)

    # Check 1: Matt's first person leaked through (FAIL)
    matt_first_person = re.findall(
        r"\b(I led|I built|I personally|I was responsible|I developed|I coached|my team|my approach)\b",
        response,
        re.IGNORECASE,
    )

    # Check 2: Agy's first person usage (OK)
    agy_first_person = re.findall(
        r"\b(I see|I found|I can|Let me|I'll|I tracked)\b", response, re.IGNORECASE
    )

    # Check 3: Third-person transformation (PASS)
    matt_third_person = re.findall(
        r"\b(Matt led|Matt built|Matt developed|He led|He built|He developed|his team)\b",
        response,
        re.IGNORECASE,
    )

    print("\n[1] PERSONA - Matt's First-Person Leaked:")
    if matt_first_person:
        print(f"    ❌ FAIL: {matt_first_person}")
    else:
        print("    ✅ PASS: None found")

    print("\n[2] PERSONA - Agy's Own Voice (acceptable):")
    print(f"    {agy_first_person if agy_first_person else 'None used'}")

    print("\n[3] PERSONA - Third-Person Transformation:")
    if matt_third_person:
        print(f"    ✅ PASS: {matt_third_person}")
    else:
        print("    ⚠️  No explicit 'Matt led' found (check if 'He' used)")

    # Check 4: Fidelity - Client Hallucination
    print("\n[4] FIDELITY - Client Attribution:")
    print(f"    Source story client: '{test_story['Client']}'")
    print("    Query mentioned: 'Accenture'")

    mentions_accenture = "Accenture" in response
    mentions_multiple = (
        "Multiple Clients" in response or "multiple clients" in response.lower()
    )
    mentions_various = "various" in response.lower() or "across" in response.lower()

    if mentions_accenture and not mentions_multiple:
        print(
            "    ❌ FAIL - HALLUCINATED: LLM attributed 'Multiple Clients' story to 'Accenture'"
        )
    elif mentions_multiple or mentions_various:
        print("    ✅ PASS: Correctly attributed to multiple clients/various")
    else:
        print("    ⚠️  Ambiguous - Check response manually")

    # Check 5: Metric preservation
    print("\n[5] FIDELITY - Metric Preservation:")
    has_10_percent = "10%" in response
    has_50_engineers = "50" in response
    print(f"    '10% retention boost' preserved: {'✅' if has_10_percent else '❌'}")
    print(f"    '50 engineers' preserved: {'✅' if has_50_engineers else '❌'}")

    # Check 6: Hallucinated additional clients
    print("\n[6] FIDELITY - Hallucinated Additional Clients:")
    other_clients = [
        "JPMorgan",
        "JP Morgan",
        "Norfolk Southern",
        "RBC",
        "Capital One",
        "Fiserv",
        "AT&T",
    ]
    hallucinated_clients = [c for c in other_clients if c in response]
    if hallucinated_clients:
        print(f"    ❌ FAIL: LLM invented examples from: {hallucinated_clients}")
    else:
        print("    ✅ PASS: No hallucinated client examples")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    persona_pass = len(matt_first_person) == 0
    fidelity_pass = not (
        mentions_accenture and not mentions_multiple and not mentions_various
    )
    no_hallucinated_clients = len(hallucinated_clients) == 0

    print(
        f"""
    ┌─────────────────────────────────────────────────┐
    │ Persona (no Matt "I")       : {'✅ PASS' if persona_pass else '❌ FAIL'}       │
    │ Fidelity (no Accenture lie) : {'✅ PASS' if fidelity_pass else '❌ FAIL'}       │
    │ Fidelity (no extra clients) : {'✅ PASS' if no_hallucinated_clients else '❌ FAIL'}       │
    │ Metrics preserved           : {'✅ PASS' if has_10_percent and has_50_engineers else '❌ FAIL'}       │
    └─────────────────────────────────────────────────┘
    """
    )

    return {
        "persona_pass": persona_pass,
        "fidelity_pass": fidelity_pass,
        "no_hallucinated_clients": no_hallucinated_clients,
        "metrics_preserved": has_10_percent and has_50_engineers,
        "matt_first_person": matt_first_person,
        "hallucinated_clients": hallucinated_clients,
    }


if __name__ == "__main__":
    run_diagnostic()
