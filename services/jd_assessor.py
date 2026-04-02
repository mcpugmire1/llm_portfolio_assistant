"""
JD Assessor Service — Job Description Requirement Extraction and Matching

Core logic for the Role Match feature. Extracts structured requirements
from job descriptions and matches them against Matt's STAR stories in Pinecone.

Architecture: Three-step pipeline (see ADR 016)
  1. LLM extraction pass — JD text → structured requirements JSON
  2. Pinecone retrieval pass — per-requirement semantic search
  3. LLM assessment pass — requirements + candidate stories → match report
"""

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

JD_ASSESSMENT_PROMPT = """You are assessing how well Matt Pugmire's experience matches a specific job requirement.

Matt is a senior engineering and transformation leader with 18+ years at Accenture, most notably as Director of the Cloud Innovation Center (CIC), which he built from 0 to 150+ practitioners generating $100M+ in repeat business across 15+ Fortune 500 clients. His background spans platform engineering, agile transformation, financial services technology, and AI-assisted development.

You will be given:
- A single requirement from a job description
- A list of Matt's STAR stories retrieved as potential evidence, each with a Pinecone similarity score

Your task: assess the match using ONLY the provided stories as evidence. Do not infer or fabricate experience not present in the stories.

{
  "requirement": "the requirement text",
  "match_status": "strong | partial | gap",
  "evidence": [
    {
      "story_title": "string",
      "client": "string",
      "relevance": "one sentence explaining how this story addresses the requirement"
    }
  ],
  "gap_explanation": "if partial or gap, explain specifically what's missing. Empty string if strong match.",
  "confidence": "high | medium | low"
}

Rules:
- strong: clear direct evidence in the provided stories
- partial: related evidence but doesn't fully cover the requirement
- gap: no provided story meaningfully addresses the requirement
- confidence reflects how clearly the provided stories demonstrate the requirement — high when evidence is direct and specific, medium when evidence is related but requires inference, low when the match is tenuous
- Include up to 2 stories as evidence maximum
- Never fabricate -- only use what's in the provided stories
- gap_explanation must be specific, not apologetic
- Output valid JSON only, no preamble"""


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

    Args:
        match_results: List of assessment results, each with "match_status" field.

    Returns:
        {"recommendation": "Apply|Consider|Pass", "fit_score": "High|Medium|Low",
         "strong_count": int, "partial_count": int, "gap_count": int}
    """
    total = len(match_results)
    if total == 0:
        return {
            "recommendation": "Pass",
            "fit_score": "Low",
            "strong_count": 0,
            "partial_count": 0,
            "gap_count": 0,
        }

    strong_count = sum(1 for r in match_results if r.get("match_status") == "strong")
    partial_count = sum(1 for r in match_results if r.get("match_status") == "partial")
    gap_count = sum(1 for r in match_results if r.get("match_status") == "gap")

    strong_ratio = strong_count / total
    coverage_ratio = (strong_count + partial_count) / total

    if gap_count == 0 and strong_ratio >= RECOMMENDATION_STRONG_RATIO:
        recommendation = "Apply"
        fit_score = "High"
    elif (
        gap_count <= RECOMMENDATION_MAX_GAPS_CONSIDER
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
    }
