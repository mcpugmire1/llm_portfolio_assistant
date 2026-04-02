"""
JD Assessor Service — Job Description Requirement Extraction and Matching

Core logic for the Role Match feature. Extracts structured requirements
from job descriptions and matches them against Matt's STAR stories in Pinecone.

Architecture: Three-step pipeline (see ADR 016)
  1. LLM extraction pass — JD text → structured requirements JSON
  2. Pinecone retrieval pass — per-requirement semantic search
  3. LLM assessment pass — requirements + candidate stories → match report
"""

import json
from pathlib import Path

# =============================================================================
# JD EXTRACTION PROMPT
# =============================================================================
# Used as the system prompt for Stage 1 of the two-step pipeline.
# Validated against 4 JD formats: structured, narrative, hybrid, mixed.
# See tests/jd_extraction_test.py for validation results.

JD_EXTRACTION_PROMPT = """You are analyzing a job description to extract structured requirements for a candidate fit assessment.

Extract the following as JSON:

{
  "role_title": "string",
  "company": "string",
  "required_qualifications": [
    {
      "requirement": "normalized requirement statement",
      "source_text": "original text from JD",
      "type": "experience | skill | education | domain"
    }
  ],
  "preferred_qualifications": [
    {
      "requirement": "normalized requirement statement",
      "source_text": "original text from JD",
      "type": "experience | skill | education | domain"
    }
  ],
  "implicit_requirements": [
    {
      "requirement": "inferred requirement",
      "inferred_from": "what text led to this inference",
      "confidence": "high | medium | low"
    }
  ],
  "key_responsibilities": ["string"],
  "seniority_signals": ["string"]
}

Rules:
- Normalize requirements into clear, testable statements
- Extract company name from anywhere in the full JD text including company description and closing sections. If truly undisclosed, use "Undisclosed"
- If no Required/Preferred split exists, classify based on language signals -- "must have", "required", "proven" = required; "plus", "preferred", "ideal" = preferred
- Extract implicit requirements from responsibilities when no explicit qualification covers them
- Do not invent requirements -- only extract what is stated or clearly implied
- Keep source_text short -- just enough to verify the extraction
- Output valid JSON only, no preamble"""

# =============================================================================
# JD ASSESSMENT PROMPT
# =============================================================================
# Used as the system prompt for Stage 3 of the three-step pipeline.
# Called once per extracted requirement with Pinecone-retrieved candidate stories.
# Produces per-requirement match status, evidence, and gap analysis.
# Grounding context (Matt DNA) is loaded from data/matt_profile.json at runtime.

JD_ASSESSMENT_PROMPT_TEMPLATE = """You are assessing how well Matt Pugmire's experience matches a specific job requirement.

{matt_profile}

You will be given:
- A single requirement from a job description
- A list of Matt's STAR stories retrieved as potential evidence, each with a Pinecone similarity score

Your task: assess the match using the provided stories AND verified facts from the grounding context above as evidence. Do not infer or fabricate anything beyond these sources.

{{
  "requirement": "the requirement text",
  "match_status": "strong | partial | gap",
  "evidence": [
    {{
      "evidence_type": "story | profile",
      "story_title": "string or null if evidence_type is profile",
      "client": "string or null if evidence_type is profile",
      "relevance": "one sentence explaining how this evidence addresses the requirement"
    }}
  ],
  "gap_explanation": "if partial or gap, explain specifically what's missing. Empty string if strong match.",
  "confidence": "high | medium | low"
}}

Rules:
- strong: clear direct evidence in the provided stories or grounding context
- partial: related evidence but doesn't fully cover the requirement
- gap: no provided story or grounding context meaningfully addresses the requirement
- confidence reflects how clearly the provided stories and grounding context demonstrate the requirement — high when evidence is direct and specific, medium when evidence is related but requires inference, low when the match is tenuous
- Include up to 2 evidence items maximum
- Use evidence_type "story" when citing a retrieved STAR story (include story_title and client)
- Use evidence_type "profile" when citing a verified fact from the grounding context (story_title and client should be null)
- Never fabricate -- only use what's in the provided stories or grounding context
- gap_explanation must be specific, not apologetic
- Output valid JSON only, no preamble"""


def load_matt_profile() -> str:
    """Load Matt's profile from data/matt_profile.json and build grounding context string."""
    profile_path = Path(__file__).parent.parent / "data" / "matt_profile.json"
    with open(profile_path) as f:
        profile = json.load(f)

    education_parts = []
    education_notes = []
    for e in profile["education"]:
        education_parts.append(f"{e['degree']} from {e['institution']}")
        if e.get("note"):
            education_notes.append(e["note"])
    education = " and ".join(education_parts)
    skills = ", ".join(profile["skills"])

    certs = ", ".join(profile.get("certifications", []))

    result = f"{profile['career_summary']} " f"He holds a {education}."
    for note in education_notes:
        result += f" {note}"
    result += f" Matt's verified skills include: {skills}."
    if certs:
        result += f" Certifications: {certs}."

    return result


def build_assessment_prompt() -> str:
    """Build the assessment prompt with dynamically loaded Matt profile."""
    profile = load_matt_profile()
    return JD_ASSESSMENT_PROMPT_TEMPLATE.format(matt_profile=profile)


# =============================================================================
# RECOMMENDATION LOGIC (Private View)
# =============================================================================
# Deterministic computation from match results — not an LLM call.
# Thresholds may be tuned after testing against real JDs.

RECOMMENDATION_STRONG_RATIO = 0.7  # 70% strong matches for Apply
RECOMMENDATION_COVERAGE_RATIO = 0.7  # 70% strong+partial for Consider
RECOMMENDATION_MAX_GAPS_CONSIDER = 1  # Max gaps allowed for Consider


def compute_recommendation(match_results: list[dict]) -> dict:
    """Compute Apply/Consider/Pass recommendation from match results.

    Only gaps in REQUIRED qualifications count toward thresholds.
    Gaps in preferred qualifications are tracked but don't block Apply/Consider.

    Args:
        match_results: List of assessment results, each with "match_status"
            and "category" ("required" | "preferred") fields.

    Returns:
        {"recommendation": "Apply|Consider|Pass", "fit_score": "High|Medium|Low",
         "strong_count": int, "partial_count": int, "gap_count": int,
         "required_gap_count": int, "preferred_gap_count": int}
    """
    total = len(match_results)
    if total == 0:
        return {
            "recommendation": "Pass",
            "fit_score": "Low",
            "strong_count": 0,
            "partial_count": 0,
            "gap_count": 0,
            "required_gap_count": 0,
            "preferred_gap_count": 0,
        }

    strong_count = sum(1 for r in match_results if r.get("match_status") == "strong")
    partial_count = sum(1 for r in match_results if r.get("match_status") == "partial")
    gap_count = sum(1 for r in match_results if r.get("match_status") == "gap")
    required_gap_count = sum(
        1
        for r in match_results
        if r.get("match_status") == "gap" and r.get("category") == "required"
    )
    preferred_gap_count = gap_count - required_gap_count

    strong_ratio = strong_count / total
    coverage_ratio = (strong_count + partial_count) / total

    # Only required gaps block Apply/Consider
    if required_gap_count == 0 and strong_ratio >= RECOMMENDATION_STRONG_RATIO:
        recommendation = "Apply"
        fit_score = "High"
    elif (
        required_gap_count <= RECOMMENDATION_MAX_GAPS_CONSIDER
        and coverage_ratio >= RECOMMENDATION_COVERAGE_RATIO
    ):
        recommendation = "Consider"
        fit_score = "Medium"
    else:
        recommendation = "Pass"
        fit_score = "Low"

    return {
        "recommendation": recommendation,
        "fit_score": fit_score,
        "strong_count": strong_count,
        "partial_count": partial_count,
        "gap_count": gap_count,
        "required_gap_count": required_gap_count,
        "preferred_gap_count": preferred_gap_count,
    }
