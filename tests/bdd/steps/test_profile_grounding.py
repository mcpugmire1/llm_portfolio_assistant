"""
BDD step definitions for profile_grounding.feature.

Pure unit tests -- no Playwright, no API calls. Patches builtins.open with a
synthetic fixture so tests are hermetic and independent of the real
matt_profile.json. Runs in milliseconds.

MATTGPT-080: Confirms load_matt_profile() ignores the skills key.
MATTGPT-158: Confirms load_matt_profile() excludes career_summary prose and
retains only discrete facts (education + certifications). Confirms the
discrete-facts-only rule is present in the built prompt and the counterfactual
verdict clause is absent.
"""

import json
from unittest.mock import mock_open, patch

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/profile_grounding.feature")

SENTINEL = "ZZZ_SENTINEL_SKILL_DO_NOT_USE"

CAREER_SUMMARY = (
    "Matt is a senior technology executive and transformation leader "
    "with a track record of building high-performing engineering organizations."
)

EDUCATION = [
    {
        "degree": "Bachelor of Science in Computer Science",
        "institution": "University of Utah",
    }
]

CERTIFICATIONS = ["AWS Certified Solutions Architect"]

DISCRETE_FACTS_FRAGMENT = "Only discrete facts are citable as profile evidence"
COUNTERFACTUAL_CLAUSE = "Omitting profile evidence must not change the verdict"


def _make_profile():
    return {
        "name": "Matt Pugmire",
        "career_summary": CAREER_SUMMARY,
        "education": EDUCATION,
        "skills": [SENTINEL, "Platform Modernization", "Cloud-Native Architecture"],
        "certifications": CERTIFICATIONS,
    }


@pytest.fixture
def context():
    return {}


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------


@given(f'a profile whose skills array contains "{SENTINEL}"')
def profile_with_sentinel(context):
    context["profile"] = _make_profile()


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when("load_matt_profile is called")
def call_load_matt_profile(context):
    profile_data = json.dumps(context["profile"])
    with patch("builtins.open", mock_open(read_data=profile_data)):
        from services.jd_assessor import load_matt_profile

        context["result"] = load_matt_profile()


@when("build_assessment_prompt is called")
def call_build_assessment_prompt(context):
    profile_data = json.dumps(context["profile"])
    with patch("builtins.open", mock_open(read_data=profile_data)):
        from services.jd_assessor import build_assessment_prompt

        context["result"] = build_assessment_prompt()


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------


@then(f'the output does not contain "{SENTINEL}"')
def output_omits_sentinel(context):
    assert SENTINEL not in context["result"], (
        f"Output must not contain skills array content "
        f"(sentinel '{SENTINEL}' found):\n{context['result']}"
    )


@then("the output does not contain the career summary text")
def output_excludes_summary(context):
    assert CAREER_SUMMARY not in context["result"], (
        f"career_summary prose must be excluded from assessment grounding.\n"
        f"Found: {CAREER_SUMMARY!r}\n"
        f"In: {context['result']}"
    )


@then("the output contains both the degree and the institution text")
def output_has_education(context):
    edu = EDUCATION[0]
    assert (
        edu["degree"] in context["result"]
    ), f"Degree '{edu['degree']}' missing from output:\n{context['result']}"
    assert (
        edu["institution"] in context["result"]
    ), f"Institution '{edu['institution']}' missing from output:\n{context['result']}"


@then("the output contains the certifications text")
def output_has_certifications(context):
    assert (
        CERTIFICATIONS[0] in context["result"]
    ), f"Certification '{CERTIFICATIONS[0]}' missing from output:\n{context['result']}"


@then('the output contains "match_status" and "gap_explanation"')
def output_has_template_keys(context):
    assert (
        "match_status" in context["result"]
    ), "Output missing 'match_status' -- template may not have been applied"
    assert (
        "gap_explanation" in context["result"]
    ), "Output missing 'gap_explanation' -- template may not have been applied"


@then("the output contains the discrete facts profile rule")
def output_has_discrete_facts_rule(context):
    assert DISCRETE_FACTS_FRAGMENT in context["result"], (
        f"Discrete-facts-only rule missing from built prompt.\n"
        f"Expected fragment: {DISCRETE_FACTS_FRAGMENT!r}\n"
        f"Got: {context['result']}"
    )


@then("the output does not contain the counterfactual verdict clause")
def output_lacks_counterfactual_clause(context):
    assert COUNTERFACTUAL_CLAUSE not in context["result"], (
        f"Counterfactual clause must be absent from prompt.\n"
        f"Found: {COUNTERFACTUAL_CLAUSE!r}\n"
        f"In: {context['result']}"
    )
