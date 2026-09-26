"""
JD Assessor Service — Job Description Requirement Extraction and Matching

Core logic for the Role Match feature. Extracts structured requirements
from job descriptions and matches them against Matt's STAR stories in Pinecone.

Architecture: Three-step pipeline (see ADR 016)
  1. LLM extraction pass — JD text → structured requirements JSON
  2. Pinecone retrieval pass — per-requirement semantic search
  3. LLM assessment pass — requirements + candidate stories → match report
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path

from openai import OpenAI

from config.constants import PROFILE_LOCATION_AVAILABILITY_FIELDS
from config.debug import DEBUG
from services.pinecone_service import pinecone_semantic_search

logger = logging.getLogger(__name__)

# =============================================================================
# JD EXTRACTION PROMPT
# =============================================================================
# Used as the system prompt for Stage 1 of the two-step pipeline.
# Validated against 4 JD formats: structured, narrative, hybrid, mixed.
# See tests/jd_extraction_test.py for validation results.

# MATTGPT-160: Retained as the pre-split reference prompt so historical
# probes that measured against it (probe_159a_extraction.py,
# probe_159b_evidence.py, probe_159_long_context.py,
# probe_159d_parallel.py) remain runnable for before/after comparisons.
# Production extraction no longer uses this constant; see
# _REQUIRED_EXTRACTION_PROMPT / _PREFERRED_EXTRACTION_PROMPT /
# _IMPLICIT_EXTRACTION_PROMPT below and the two-wave extract_requirements
# implementation.
JD_EXTRACTION_PROMPT = """You are analyzing a job description to extract structured requirements for a candidate fit assessment.

Extract the following as JSON:

{
  "role_title": "string",
  "company": "string",
  "jd_format": "narrative | bulleted | hybrid",
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

- FIRST: Classify the JD format. Is there an explicit "Required:" or "Requirements:" section header followed by bullets? Is there a "Preferred:" or "Nice to have:" section? If YES, this is a bulleted JD -- follow the bullet structure rules below. If NO, this is a narrative JD -- mine the body paragraphs aggressively. Hybrid JDs (some bullets, some prose body content) should mine both.

- HANDLE NARRATIVE JDs: Many job descriptions are written as prose without explicit "Required:" or "Preferred:" sections. For these JDs, you MUST mine the body paragraphs for requirements. Do not stop at 2-3 explicit "must have" sentences -- a narrative JD with substantial body content should produce 5-12 requirements just like a bulleted JD would.

- MINE BODY PARAGRAPHS for these signal categories and extract each as a requirement:
  * Team scope: team size, team composition (e.g. "lead a team of 40 across AI, ML, data science") -> "Experience leading teams of N+ across X disciplines"
  * Technical scope: what they're building (e.g. "production-grade systems around large language models") -> "Experience building production-grade LLM systems"
  * Ownership level: strategy / architecture / hands-on / all-of-above -> "Experience owning strategy, architecture, AND hands-on delivery"
  * Stakeholder environment: who they partner with (e.g. "senior stakeholders who care deeply about ROI") -> "Experience partnering with senior business stakeholders on ROI-driven outcomes"
  * Domain context: industry, scale, regulatory environment (e.g. "asset management, trillions in AUM") -> "Experience in financial services / asset management at scale"
  * Specific responsibilities: incubation, transformation, modernization, scaling -> one requirement per distinct capability

- DO NOT extract logistics as requirements: location, work mode (onsite/remote/hybrid), salary, visa, interview process, start date. These are filters, not capability fit signals.

- TARGET COUNT FOR NARRATIVE JDs: A pure narrative JD (no Required/Preferred sections, content delivered as prose paragraphs) with substantial body content should produce 5-12 requirements via prose mining. Below 5 means you missed signals in the body paragraphs -- go back and mine more. The 12 ceiling exists to prevent fragmentation -- consolidate related signals into thematic requirements rather than producing 25 atomic micro-requirements.

- BULLETED JDs HAVE NO ARTIFICIAL CAP: When the JD has explicit Required: and/or Preferred: sections with bullet lists, follow the bullet structure. Consolidate bullets into thematic requirements when they describe related capabilities (e.g. three separate bullets about "delivery", "on-time", "within budget" become one "delivery accountability" requirement), but do NOT artificially cap the count to fit a 5-12 range. A bulleted JD with 15 legitimately distinct requirements should produce 15.

- PROTECT EXPLICIT REQUIRED BULLETS: When the JD has an explicit Required: section with bullets, EVERY bullet in that section MUST be extracted as a requirement in `required_qualifications`. Do not drop, omit, or reword-away explicit Required bullets even when body content covers similar themes. The body-mining rules ADD to the explicit Required list -- they NEVER replace or remove from it. If an explicit Required bullet and a body responsibility describe the same capability, extract BOTH as separate requirements (the explicit one in `required_qualifications`, the body-mined one in `implicit_requirements`). Dropping an explicit Required bullet because "the body covers it" is a violation of this rule.

- PROTECT EXPLICIT PREFERRED BULLETS: Same rule -- every bullet in an explicit Preferred section MUST be extracted to `preferred_qualifications`. Body mining never replaces explicit Preferred bullets.

- For narrative JDs, place mined requirements in `required_qualifications` (not `implicit_requirements`) UNLESS the JD has BOTH a clear Required section AND prose body content -- in which case mined-from-prose requirements go in `implicit_requirements`. The downstream assessment will treat all three lists equally.

- Extract implicit requirements from responsibilities when no explicit qualification covers them
- Do not invent requirements -- only extract what is stated or clearly implied
- Keep source_text short -- just enough to verify the extraction
- Output valid JSON only, no preamble"""


# =============================================================================
# SPLIT EXTRACTION PROMPTS -- MATTGPT-160
# =============================================================================
# Three section-scoped prompts, one per output section. Each carries a
# `=== SECTION: <name> ===` marker line so test dispatchers can identify
# which call is which without relying on schema-key substrings (the
# implicit prompt legitimately mentions the other sections when
# describing its wave-1 context, so a schema-key classifier would
# misclassify it).
#
# key_responsibilities and seniority_signals from the pre-split schema
# are intentionally omitted: nothing in services/ or ui/ reads them
# (grep-confirmed September 2026), and generating output nothing reads
# is directly against the count-stability mechanism this split targets.


_REQUIRED_EXTRACTION_PROMPT = """=== SECTION: required ===

You are analyzing a job description to extract the required qualifications and JD-level metadata for a candidate fit assessment.

Extract the following as JSON:

{
  "role_title": "string",
  "company": "string",
  "jd_format": "narrative | bulleted | hybrid",
  "required_qualifications": [
    {
      "requirement": "normalized requirement statement",
      "source_text": "original text from JD",
      "type": "experience | skill | education | domain"
    }
  ],
  "key_responsibilities": ["string"]
}

Rules:
- Extract company name from anywhere in the full JD text including company description and closing sections. If truly undisclosed, use "Undisclosed".
- Populate `key_responsibilities` with the JD's stated responsibilities (what the role does, not what the candidate must have). One item per distinct responsibility. Empty list if none are stated.
- Normalize requirements into clear, testable statements.
- Copy source_text as the entire JD bullet or sentence, verbatim and complete. Do not shorten, summarize, or truncate.
- Do not invent requirements -- only extract what is stated or clearly implied.
- DO NOT extract logistics as requirements: location, work mode (onsite/remote/hybrid), salary, visa, interview process, start date. These are filters, not capability fit signals.

Classify the JD format FIRST:
- Is there an explicit "Required:" or "Requirements:" section header followed by bullets? Is there a "Preferred:" or "Nice to have:" section?
- If YES, this is a bulleted JD -- follow the bullet structure rules.
- If NO, this is a narrative JD -- mine the body paragraphs aggressively.
- Hybrid JDs (some bullets, some prose body content) should mine both.

If no Required/Preferred split exists, classify based on language signals -- "must have", "required", "proven" = required.

HANDLE NARRATIVE JDs: Many job descriptions are written as prose without explicit "Required:" or "Preferred:" sections. For these JDs, you MUST mine the body paragraphs for requirements. Do not stop at 2-3 explicit "must have" sentences -- a narrative JD with substantial body content should produce 5-12 requirements just like a bulleted JD would.

MINE BODY PARAGRAPHS for these signal categories and extract each as a requirement:
- Team scope: team size, team composition (e.g. "lead a team of 40 across AI, ML, data science") -> "Experience leading teams of N+ across X disciplines"
- Technical scope: what they're building (e.g. "production-grade systems around large language models") -> "Experience building production-grade LLM systems"
- Ownership level: strategy / architecture / hands-on / all-of-above -> "Experience owning strategy, architecture, AND hands-on delivery"
- Stakeholder environment: who they partner with (e.g. "senior stakeholders who care deeply about ROI") -> "Experience partnering with senior business stakeholders on ROI-driven outcomes"
- Domain context: industry, scale, regulatory environment (e.g. "asset management, trillions in AUM") -> "Experience in financial services / asset management at scale"
- Specific responsibilities: incubation, transformation, modernization, scaling -> one requirement per distinct capability

TARGET COUNT FOR NARRATIVE JDs: A pure narrative JD (no Required/Preferred sections, content delivered as prose paragraphs) with substantial body content should produce 5-12 requirements via prose mining. Below 5 means you missed signals in the body paragraphs -- go back and mine more. The 12 ceiling exists to prevent fragmentation -- consolidate related signals into thematic requirements rather than producing 25 atomic micro-requirements.

BULLETED JDs HAVE NO ARTIFICIAL CAP: When the JD has an explicit Required: section with bullet lists, follow the bullet structure. Consolidate bullets into thematic requirements when they describe related capabilities (e.g. three separate bullets about "delivery", "on-time", "within budget" become one "delivery accountability" requirement), but do NOT artificially cap the count to fit a 5-12 range. A bulleted JD with 15 legitimately distinct required items should produce 15.

PROTECT EXPLICIT REQUIRED BULLETS: When the JD has an explicit Required: section with bullets, EVERY bullet in that section MUST be extracted as a requirement in `required_qualifications`. Do not drop, omit, or reword-away explicit Required bullets even when body content covers similar themes. The body-mining rules ADD to the explicit Required list -- they NEVER replace or remove from it. Dropping an explicit Required bullet because "the body covers it" is a violation of this rule.

For narrative JDs, place mined requirements in `required_qualifications`. For hybrid JDs that have BOTH a clear Required section AND prose body content, place explicit-bullet items in `required_qualifications` -- the separate implicit extraction call will handle body-mined items in that case.

Output valid JSON only, no preamble."""


_PREFERRED_EXTRACTION_PROMPT = """=== SECTION: preferred ===

You are analyzing a job description to extract the preferred qualifications for a candidate fit assessment.

Extract the following as JSON:

{
  "preferred_qualifications": [
    {
      "requirement": "normalized requirement statement",
      "source_text": "original text from JD",
      "type": "experience | skill | education | domain"
    }
  ]
}

Rules:
- Normalize requirements into clear, testable statements.
- Copy source_text as the entire JD bullet or sentence, verbatim and complete. Do not shorten, summarize, or truncate.
- Do not invent requirements -- only extract what is stated or clearly implied.
- DO NOT extract logistics as requirements: location, work mode (onsite/remote/hybrid), salary, visa, interview process, start date.

If no Required/Preferred split exists, classify based on language signals -- "plus", "preferred", "ideal", "nice to have" = preferred.

PROTECT EXPLICIT PREFERRED BULLETS: When the JD has an explicit Preferred: (or "Nice to have:") section with bullets, EVERY bullet in that section MUST be extracted as a requirement in `preferred_qualifications`. Do not drop, omit, or reword-away explicit Preferred bullets even when body content covers similar themes.

BULLETED JDs HAVE NO ARTIFICIAL CAP: When the JD has an explicit Preferred section, follow the bullet structure. Consolidate related bullets into thematic requirements but do NOT artificially cap the count.

If the JD has no Preferred section and no "plus / nice to have / ideal" language, return an empty list. Do not fabricate preferred qualifications where none exist.

Output valid JSON only, no preamble."""


_IMPLICIT_EXTRACTION_PROMPT = """=== SECTION: implicit ===

You are analyzing a job description to extract implicit requirements -- capabilities inferred from responsibilities that no explicit required or preferred qualification already covers.

You will receive:
- The full job description
- The list of already-extracted required qualifications
- The list of already-extracted preferred qualifications

Extract implicit requirements as JSON:

{
  "implicit_requirements": [
    {
      "requirement": "inferred requirement",
      "inferred_from": "what text led to this inference",
      "confidence": "high | medium | low"
    }
  ]
}

Rules:
- Extract implicit requirements from responsibilities when no explicit qualification already covers them. If a responsibility maps to an already-extracted required or preferred item, DO NOT re-extract it as implicit -- the dedup happens here at extraction time.
- Do not invent requirements -- only extract what is stated or clearly implied.
- DO NOT extract logistics as requirements: location, work mode (onsite/remote/hybrid), salary, visa, interview process, start date.

When to produce implicit requirements:
- Hybrid JDs with BOTH an explicit Required section AND substantive body content: body-mined items that aren't already in the explicit lists go here.
- Pure structured JDs with only bullet lists: usually produces an empty list; the bullets are the requirements.
- Pure narrative JDs: usually produces an empty list because the narrative body was already mined directly into the required list.

confidence:
- high: the responsibility text directly implies the requirement.
- medium: the requirement is a reasonable inference from context.
- low: the requirement is possible but not clearly indicated.

If there are no implicit requirements to add beyond what's already extracted, return an empty list. Do not force items into implicit that duplicate the explicit lists.

Output valid JSON only, no preamble."""

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
  "gap_explanation": "if partial or gap, format as 'Note: <what's missing>' in under 15 words. Focus on what's missing, NOT what's present. Empty string if strong match.",
  "confidence": "high | medium | low"
}}

Rules:
- strong: clear direct evidence in the provided stories or grounding context
- partial: related evidence but doesn't fully cover the requirement
- gap: no provided story or grounding context meaningfully addresses the requirement
- A "strong" match REQUIRES at least one cited piece of evidence (story OR profile). If you cannot cite specific evidence, the match status MUST be "partial" or "gap" -- NEVER "strong" with an empty evidence array. Asserting a strong match without evidence is a violation of this rule.
- confidence reflects how clearly the provided stories and grounding context demonstrate the requirement — high when evidence is direct and specific, medium when evidence is related but requires inference, low when the match is tenuous
- Include up to 2 evidence items maximum
- Use evidence_type "story" when citing a retrieved STAR story (include story_title and client)
- Use evidence_type "profile" when citing a verified fact from the grounding context (story_title and client should be null)
- Only discrete facts are citable as profile evidence: a degree, a certification, a specific credential. Prose characterizations of career history or experience are not citable as profile evidence. If no discrete fact in the grounding directly addresses the requirement, omit profile evidence entirely and let story evidence stand alone.
- Never fabricate -- only use what's in the provided stories or grounding context
- Recognize cloud-managed equivalents of open-source tools as the same capability: AWS ElastiCache IS Redis (and Memcached), Amazon RDS includes PostgreSQL/MySQL/SQL Server, Aurora is MySQL/PostgreSQL-compatible, Azure Cosmos DB supports MongoDB API, etc. Treat experience with the managed service as evidence for the underlying technology.
- gap_explanation must start with 'Note:' and stay under 15 words
- gap_explanation must describe ONLY what's missing — do NOT restate what's present (no "While Matt's profile confirms..." preambles)
- gap_explanation must be specific, not apologetic
- Output valid JSON only, no preamble"""


def load_matt_profile() -> str:
    """Load Matt's profile from data/matt_profile.json and build grounding
    context string.

    Each education entry renders on its own line so that per-entry notes
    (e.g., the Master's equivalence note, the UGA teaching note, the
    Queens abroad note) stay attached to the degree they describe rather
    than trailing after the last degree in a shared "notes" section.
    """
    profile_path = Path(__file__).parent.parent / "data" / "matt_profile.json"
    with open(profile_path) as f:
        profile = json.load(f)

    lines = []
    for e in profile.get("education", []):
        line = f"Education: {e['degree']}, {e['institution']}."
        if e.get("note"):
            line += f" {e['note']}"
        lines.append(line)

    certs = ", ".join(profile.get("certifications", []))
    if certs:
        lines.append(f"Certifications: {certs}.")

    languages = profile.get("languages", [])
    if languages:
        lines.append(f"Languages: {', '.join(languages)}.")

    # MATTGPT-250 step 2: Location & Availability (JSON key "logistics"),
    # one line per populated field in the shared field order. A field with
    # an empty value is omitted, as in Role Match's _iter_location_cells().
    location_availability = profile.get("logistics") or {}
    for field_key, label in PROFILE_LOCATION_AVAILABILITY_FIELDS:
        cell = location_availability.get(field_key) or {}
        value = str(cell.get("value", "")).strip()
        if not value:
            continue
        subline = str(cell.get("subline", "")).strip()
        lines.append(f"{label}: {value}." + (f" {subline}." if subline else ""))

    return "\n".join(lines)


def build_assessment_prompt() -> str:
    """Build the assessment prompt with dynamically loaded Matt profile."""
    profile = load_matt_profile()
    return JD_ASSESSMENT_PROMPT_TEMPLATE.format(matt_profile=profile)


# =============================================================================
# PIPELINE — Three-stage assessment (extract → retrieve → assess)
# =============================================================================
# These functions implement the production pipeline consumed by the Role Match
# UI. They were promoted from tests/jd_pipeline_validation.py so the UI and the
# validation script share a single source of truth.

ASSESSMENT_MODEL = "gpt-4o"
ASSESSMENT_TEMPERATURE = 0.0
DEFAULT_TOP_K = 5

# MATTGPT-248 Cycle 2: per-mode unassessed row copy. Populated on
# gap_explanation so a mixed run (retrieval up, one call rate-limited)
# is distinguishable from a total outage on the render surface. First
# person, no action clause, no paw emoji -- the "🐾 I couldn't get to
# N of these M requirements" incomplete notice above the summary
# carries the paw once, and these row-level messages travel into the
# export and share surfaces where the reader can't retry.
_MODE_1_GAP_TEXT = "I couldn't finish assessing this one."
_MODE_2_GAP_TEXT = "I couldn't reach Matt's work history for this one."

# MATTGPT-243: fan-out concurrency for the Stages 2+3 parallel loop.
# Chosen to sit well below OpenAI's rate-limit ceiling while giving the
# event loop enough in-flight work to hide per-call latency. Reasoning,
# not measurement.
#
# Measured effect on the AT&T JD at DEFAULT_TOP_K=5, three runs each:
#   Sequential (probe_159_att_output/summary.json): 125.5s mean.
#   Parallel   (probe_159d_output/summary.json):     31.0s mean.
# The -243 acceptance's 84.7s baseline is a separate Streamlit Cloud
# click-to-render measurement on demo_jd.txt and is not directly
# comparable to either.
_CONCURRENCY = 10


def _get_openai_client() -> OpenAI:
    """Build an OpenAI client using the same env-var pattern as the rest of the app."""
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        project=os.getenv("OPENAI_PROJECT_ID"),
        organization=os.getenv("OPENAI_ORG_ID"),
    )


def extract_requirements(client: OpenAI, jd_text: str) -> dict:
    """Stage 1 -- extract structured requirements from a job description
    as a two-wave split.

    Wave 1: required + preferred concurrently via asyncio.gather.
    Wave 2: implicit, seeded with wave 1 output in its user message so
    the LLM's dedup rule ("extract implicit requirements from
    responsibilities when no explicit qualification covers them") has
    the explicit lists to evaluate against.

    The split reduces requirement-count variance on long JDs; the
    driver of remaining variance has not been isolated by measurement,
    only characterized as summarization on dense multi-item bullets
    that is uncorrelated with input or output length in what's been
    measured.

    Section-failure semantics: any of the three calls raising raises
    out of this function. asyncio.gather without return_exceptions
    propagates wave 1 failures before wave 2 fires. Partial degradation
    is rejected because a missing section shrinks the recommendation-
    math denominator silently.

    Returns a dict with required_qualifications, preferred_qualifications,
    implicit_requirements, key_responsibilities, role_title, company,
    and jd_format. Return shape is compatible with the pre-split
    implementation.
    """
    result = asyncio.run(_extract_all_sections(client, jd_text))
    if DEBUG:
        # One line per requirement so source_text (and inferred_from for
        # implicit) are visible in the trace at the same granularity the
        # rest of the trace uses. req_idx here matches req_idx on
        # downstream assess_call_ms and retrieval [req N] lines because
        # the iteration order (required, preferred, implicit->required)
        # is the same order _flatten_extraction produces. Implicit rows
        # carry category='required' matching the flatten's category
        # assignment; the trailing field name (source_text vs
        # inferred_from) disambiguates implicit from required-proper for
        # a reader who needs the distinction.
        _idx = 0
        for _section, _src_field, _category in (
            ("required_qualifications", "source_text", "required"),
            ("preferred_qualifications", "source_text", "preferred"),
            ("implicit_requirements", "inferred_from", "required"),
        ):
            for _r in result.get(_section, []) or []:
                _req_text = _r.get("requirement", "")
                _src_text = _r.get(_src_field, "")
                print(
                    f"[jd_assessor] extraction_item req_idx={_idx} "
                    f"category={_category} requirement={_req_text!r} "
                    f"{_src_field}={_src_text!r}"
                )
                _idx += 1
    return result


async def _extract_all_sections(client: OpenAI, jd_text: str) -> dict:
    """Two-wave orchestration for extract_requirements. Wave 1's tasks
    are created explicitly and drained via return_exceptions=True
    after a failure so any completed-but-unretrieved sibling exception
    is consumed rather than left dangling (dangling exceptions print
    'Task exception was never retrieved' to stderr and would trip
    -222's operational alarms). Same shape as _fan_out_assessments'
    BaseException handler.

    task.cancel() before the drain is a best-effort at the async
    layer; it does NOT abort an in-flight to_thread HTTP request
    because Python threads aren't cancellable from the outside. If
    the sibling call is already inside client.chat.completions.create
    when cancel() fires, that HTTP request runs to completion and its
    result is discarded. The drain (return_exceptions=True gather) is
    the load-bearing part; the cancel just avoids scheduling more
    work at the async layer if the coroutine hasn't started its
    to_thread call yet."""
    required_task = asyncio.create_task(
        _to_thread_with_ctx(_call_required, client, jd_text)
    )
    preferred_task = asyncio.create_task(
        _to_thread_with_ctx(_call_preferred, client, jd_text)
    )
    try:
        required_result, preferred_result = await asyncio.gather(
            required_task, preferred_task
        )
    except BaseException:
        for task in (required_task, preferred_task):
            if not task.done():
                task.cancel()
        await asyncio.gather(required_task, preferred_task, return_exceptions=True)
        raise

    # Wave 2 fires only after wave 1 succeeded. A wave-1 failure raises
    # out of the gather above and this line is never reached, which is
    # what test_wave_1_failure_prevents_wave_2_and_propagates pins.
    implicit_result = await _to_thread_with_ctx(
        _call_implicit, client, jd_text, required_result, preferred_result
    )

    return {
        "role_title": required_result.get("role_title", ""),
        "company": required_result.get("company", "Undisclosed"),
        "jd_format": required_result.get("jd_format", ""),
        "required_qualifications": required_result.get("required_qualifications", [])
        or [],
        "preferred_qualifications": preferred_result.get("preferred_qualifications", [])
        or [],
        "implicit_requirements": implicit_result.get("implicit_requirements", []) or [],
        "key_responsibilities": required_result.get("key_responsibilities", []) or [],
    }


def _call_required(client: OpenAI, jd_text: str) -> dict:
    """Wave 1 required-section call. Carries role_title, company,
    jd_format metadata in addition to required_qualifications so a
    fourth metadata-only call isn't needed."""
    response = client.chat.completions.create(
        model=ASSESSMENT_MODEL,
        messages=[
            {"role": "system", "content": _REQUIRED_EXTRACTION_PROMPT},
            {"role": "user", "content": jd_text},
        ],
        temperature=ASSESSMENT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _call_preferred(client: OpenAI, jd_text: str) -> dict:
    """Wave 1 preferred-section call."""
    response = client.chat.completions.create(
        model=ASSESSMENT_MODEL,
        messages=[
            {"role": "system", "content": _PREFERRED_EXTRACTION_PROMPT},
            {"role": "user", "content": jd_text},
        ],
        temperature=ASSESSMENT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _call_implicit(
    client: OpenAI,
    jd_text: str,
    required_result: dict,
    preferred_result: dict,
) -> dict:
    """Wave 2 implicit-section call. Wave 1's requirement text lands in
    the user message so the LLM's dedup rule has the already-extracted
    lists to evaluate against."""
    user_message = (
        f"Job description:\n{jd_text}\n\n"
        f"Already-extracted qualifications (do not duplicate):\n"
        f"{_format_already_extracted(required_result, preferred_result)}"
    )
    response = client.chat.completions.create(
        model=ASSESSMENT_MODEL,
        messages=[
            {"role": "system", "content": _IMPLICIT_EXTRACTION_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=ASSESSMENT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _format_already_extracted(required_result: dict, preferred_result: dict) -> str:
    """Format wave 1 output as the 'already-extracted' block for the
    implicit call's user message."""
    lines = ["Required:"]
    for r in required_result.get("required_qualifications", []) or []:
        lines.append(f"- {r.get('requirement', '')}")
    lines.append("")
    lines.append("Preferred:")
    for r in preferred_result.get("preferred_qualifications", []) or []:
        lines.append(f"- {r.get('requirement', '')}")
    return "\n".join(lines)


def retrieve_stories(
    requirement_text: str,
    stories: list,
    top_k: int = DEFAULT_TOP_K,
    debug_tag: str | None = None,
) -> list:
    """Stage 2 — query Pinecone for candidate stories matching a requirement.

    Returns a list of trimmed story dicts (title, client, id, score, STAR fields)
    suitable for inclusion in the assessment prompt. Empty list if no hits.

    debug_tag threads a per-caller identifier (e.g. "[req 5]") into
    pinecone_semantic_search's DEBUG output so concurrent callers under
    the Role Match fan-out remain attributable when their lines interleave.
    """
    results = pinecone_semantic_search(
        query=requirement_text,
        filters={},
        stories=stories,
        top_k=top_k,
        debug_tag=debug_tag,
    )
    # MATTGPT-248 Cycle 2: propagate the None-on-failure signal from
    # pinecone_semantic_search rather than collapsing it into []. The
    # collapse (`if not results: return []`) once discarded the only
    # signal `_assess_one_with_index` had for telling a Pinecone
    # outage (None) apart from a real empty match ([]). Mode 2 needs
    # the distinction: None becomes an unassessed row with no LLM
    # call; [] proceeds to the LLM on the grounding-only path.
    if results is None:
        return None
    if not results:
        return []
    return [
        {
            "title": hit["story"].get("Title", ""),
            "client": hit["story"].get("Client", ""),
            "id": hit["story"].get("id", ""),
            "score": hit.get("pc_score", 0),
            "5PSummary": hit["story"].get("5PSummary", ""),
            "Situation": hit["story"].get("Situation", []),
            "Action": hit["story"].get("Action", []),
            "Result": hit["story"].get("Result", []),
        }
        for hit in results[:top_k]
    ]


def _format_candidates_for_prompt(candidate_stories: list) -> str:
    """Format retrieved stories as the user-message body for the assessment LLM."""
    out = ""
    for i, s in enumerate(candidate_stories, 1):
        out += f"\n--- Story {i} ---\n"
        out += f"Title: {s['title']}\n"
        out += f"Client: {s['client']}\n"
        out += f"Score: {s['score']:.3f}\n"
        out += f"Summary: {s['5PSummary']}\n"
        if s.get("Situation"):
            sit = s["Situation"]
            if isinstance(sit, list):
                sit = " ".join(sit)
            out += f"Situation: {sit}\n"
        if s.get("Action"):
            act = s["Action"]
            if isinstance(act, list):
                act = " ".join(act[:3])
            out += f"Action: {act}\n"
        if s.get("Result"):
            res = s["Result"]
            if isinstance(res, list):
                res = " ".join(res[:3])
            out += f"Result: {res}\n"
    return out


def assess_requirement(
    client: OpenAI, requirement: str, candidate_stories: list
) -> dict:
    """Stage 3 — assess match quality for a single requirement.

    Returns the parsed JSON object produced by JD_ASSESSMENT_PROMPT_TEMPLATE.
    """
    user_message = (
        f"Requirement: {requirement}\n\n"
        f"Retrieved Stories:\n{_format_candidates_for_prompt(candidate_stories)}"
    )

    response = client.chat.completions.create(
        model=ASSESSMENT_MODEL,
        messages=[
            {"role": "system", "content": build_assessment_prompt()},
            {"role": "user", "content": user_message},
        ],
        temperature=ASSESSMENT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def run_assessment(jd_text: str, stories: list[dict]) -> dict:
    """Run the full three-stage pipeline against a job description.

    Args:
        jd_text: Raw JD text pasted by the user.
        stories: Full story corpus loaded by app.py.

    Returns:
        {
            "extraction": {...},     # full JD extraction object
            "results": [             # one entry per requirement (required + preferred)
                {
                    "category": "required" | "preferred",
                    "requirement": "...",
                    "match_status": "strong" | "partial" | "gap",
                    "evidence": [...],
                    "gap_explanation": "...",
                    "confidence": "high" | "medium" | "low",
                },
                ...
            ],
        }

    The returned shape is compatible with compute_recommendation().
    """
    client = _get_openai_client()

    # Stage 1
    _t_extract_start = time.perf_counter()
    extraction = extract_requirements(client, jd_text)
    _t_extract_ms = (time.perf_counter() - _t_extract_start) * 1000.0

    all_requirements = _flatten_extraction(extraction)

    if DEBUG:
        print(
            f"[jd_assessor] extraction_ms={_t_extract_ms:.1f} "
            f"n_reqs={len(all_requirements)}"
        )

    # Stages 2 + 3 -- MATTGPT-243: parallel fan-out via asyncio.as_completed
    # at concurrency _CONCURRENCY, wrapping the sync OpenAI and Pinecone
    # clients with asyncio.to_thread. Sequential loop stays available in
    # git history if the rewrite ever needs to be reverted.
    _t_fanout_start = time.perf_counter()
    match_results = asyncio.run(_fan_out_assessments(client, all_requirements, stories))
    _t_fanout_ms = (time.perf_counter() - _t_fanout_start) * 1000.0

    if DEBUG:
        print(
            f"[jd_assessor] fan_out_ms={_t_fanout_ms:.1f} "
            f"n_reqs={len(all_requirements)}"
        )

    return {
        "extraction": extraction,
        "results": match_results,
    }


def _flatten_extraction(extraction: dict) -> list[dict]:
    """Flatten the three-block extraction into an ordered list of
    per-requirement dicts for retrieval + assessment.

    Text-field selection per section:
    - required, preferred: source_text (verbatim JD clause). The
      assessor judges match against the JD's own wording rather than
      the model's compressed restatement, which was the compression
      -244's rows 7 and 11 flagged. Falls back to requirement if
      source_text is missing or empty; the 234/234 verbatim rate
      measured September 2026 across three JDs (bulleted, hybrid,
      narrative) makes the fallback rare, but keeping it defensive
      avoids taking down the whole assessment for one anomalous row.
    - implicit: requirement (the model's inferred capability). Not
      inferred_from -- that field holds the text that led to the
      inference, not the requirement itself, so sending it would ask
      the assessor to judge evidence against a responsibility instead
      of against a capability.

    Category assignment: implicit rows carry category='required'
    (not a distinct 'implicit' category). Implicit is populated only
    for hybrid JDs that have BOTH an explicit Required section AND
    substantive body content -- pure narrative JDs route body-mined
    requirements directly into required_qualifications via the
    extraction prompt rules. Grouping implicit under required for the
    downstream fanout and recommendation math reflects that implicit
    is functionally an extension of required, not a third weighted
    class.

    Callers: run_assessment (service path) and ui/pages/role_match.py
    (progressive-fill UI path). The shared helper is what stops the
    two sites drifting apart -- a prior version had two copies of
    this block and they diverged."""
    out: list[dict] = []
    for r in extraction.get("required_qualifications", []) or []:
        text = r.get("source_text") or r.get("requirement", "")
        out.append({"text": text, "category": "required"})
    for r in extraction.get("preferred_qualifications", []) or []:
        text = r.get("source_text") or r.get("requirement", "")
        out.append({"text": text, "category": "preferred"})
    for r in extraction.get("implicit_requirements", []) or []:
        out.append({"text": r.get("requirement", ""), "category": "required"})
    return out


async def _to_thread_with_ctx(func, *args):
    """asyncio.to_thread with Streamlit's ScriptRunContext attached to
    the worker thread so it does not emit 'missing ScriptRunContext'
    warnings that would flood stderr and trip MATTGPT-222's alarms.

    Import is local rather than module-level so services.jd_assessor
    stays runnable outside Streamlit and unit tests do not inherit an
    internal-path dependency on streamlit.runtime.scriptrunner (same
    class of coupling as st-emotion-cache selectors -- Streamlit may
    rename it between minor versions). If Streamlit is not importable,
    or the caller lacks a ScriptRunContext, falls back to plain
    asyncio.to_thread. Verification: if the missing-ctx warnings still
    appear after Streamlit restart, ctx was None on this call path and
    the wrapper is a silent no-op."""
    try:
        import threading

        from streamlit.runtime.scriptrunner import (
            add_script_run_ctx,
            get_script_run_ctx,
        )

        ctx = get_script_run_ctx()
    except ImportError:
        ctx = None

    if ctx is None:
        return await asyncio.to_thread(func, *args)

    def _with_ctx():
        add_script_run_ctx(threading.current_thread(), ctx)
        return func(*args)

    return await asyncio.to_thread(_with_ctx)


def _unassessed_row(req: dict, gap_text: str) -> dict:
    """MATTGPT-248 Cycle 2: build an unassessed row for the producer-
    side partial-failure paths (Mode 1 assess-caught and Mode 2
    retrieval-returned-None).

    Category and requirement text come from the source req dict
    because the LLM's JSON never arrived -- nothing is inferred. The
    empty evidence list and per-mode gap_explanation land the row on
    the consumer surface via `_owes_explanation` (Cycle 1 follow-up),
    which routes any non-strong status through the note-block gate.
    Confidence is intentionally omitted: nothing downstream reads it,
    and stamping a value for a verdict we didn't reach would be a
    fabrication.

    `req["text"]` and `req["category"]` are bare subscripts (not
    `.get`) deliberately. `run_assessment`'s flattening loop builds
    the req dict locally at every append site with both keys
    populated, so a KeyError here would mean a future caller fed
    this an LLM-derived dict (which carries `"requirement"`, not
    `"text"`) and the crash is the right failure to surface. But
    this function runs inside an except handler in the fan-out
    loop, so any exception here propagates out and takes down the
    whole assessment. Only call `_unassessed_row` with a req dict
    built by the flattening loop."""
    return {
        "requirement": req["text"],
        "match_status": "unassessed",
        "evidence": [],
        "gap_explanation": gap_text,
        "category": req["category"],
    }


async def _assess_one_with_index(
    index: int,
    semaphore: asyncio.Semaphore,
    client: OpenAI,
    req: dict,
    stories: list[dict],
) -> tuple[int, dict]:
    """Retrieve candidates + assess one requirement, under the semaphore.

    Returns (submission_index, assessment_dict) so the caller can rebuild
    the ordered results list after asyncio.as_completed yields in
    completion order. Wraps sync retrieve_stories and assess_requirement
    via _to_thread_with_ctx so the event loop stays free during the
    blocking HTTP calls to Pinecone and OpenAI, and Streamlit's
    ScriptRunContext propagates to the worker threads.

    MATTGPT-248 Cycle 2: three per-call failure branches, each with a
    distinct log phrase so the causes stay grep-separable:

    - Mode 4 (`retrieval-raised`): retrieve_stories raised. Log and
      re-raise; the exception propagates through _fan_out_assessments'
      cancel-and-drain BaseException handler and out of run_assessment.
      `except Exception` (not BaseException) so cancellation reaches
      the fan-out handler unlogged rather than being reported as a
      retrieval bug. Deliberately different from Mode 2: an exception
      is a bug, a None return is an expected outage signal.
    - Mode 2 (`retrieval-returned-None`): pinecone_semantic_search
      returned None (outage). Emit an unassessed row directly without
      calling the LLM. During a total Pinecone outage on an
      N-requirement JD this avoids paying N gpt-4o calls that would
      each produce 'gap' verdicts the reader would have to disbelieve
      row-by-row.
    - Mode 1 (`assess-caught`): assess_requirement raised (rate limit,
      malformed JSON, transient 5xx). Caught per-call so a single
      failed requirement doesn't take down the whole assessment. Emit
      an unassessed row and continue."""
    async with semaphore:
        try:
            candidates = await _to_thread_with_ctx(
                retrieve_stories, req["text"], stories, DEFAULT_TOP_K, f"[req {index}]"
            )
        except Exception as exc:
            logger.warning(
                "[jd_assessor] retrieval-raised req_idx=%d req_text=%r exc=%r",
                index,
                req["text"],
                exc,
            )
            raise

        if candidates is None:
            logger.warning(
                "[jd_assessor] retrieval-returned-None req_idx=%d req_text=%r",
                index,
                req["text"],
            )
            return index, _unassessed_row(req, _MODE_2_GAP_TEXT)

        # Per-call timing (DEBUG-gated): wraps only the assess_requirement
        # await so the measurement excludes Pinecone retrieval and
        # excludes semaphore queuing (semaphore is acquired at the top of
        # this function, outside the timed region). It does NOT exclude
        # shared-endpoint contention: N calls in flight against the same
        # OpenAI endpoint have coupled latencies, so a per-call number
        # measured at concurrency 10 is not the same as one measured
        # alone. That matters when comparing arms of a concurrency probe.
        # Emit tagged with req_idx so N calls produce N grep-legible
        # samples for mean and spread analysis.
        #
        # MATTGPT-248 Cycle 2 note on sample count: Mode 2
        # (retrieval-returned-None) and Mode 4 (retrieval-raised)
        # return/raise before this timer is set, so no
        # assess_call_ms sample is emitted for a requirement that
        # never reached the LLM. That's correct -- the sample count
        # equals the number of requirements that actually called
        # gpt-4o, not the number of requirements submitted. A short
        # sample count during a Pinecone outage is honest, not a
        # dropped measurement. Mode 1 (assess-caught) DOES emit a
        # sample: a call that hangs for 30s then raises is exactly
        # the sample the distribution most needs, and silently
        # dropping it would bias the mean toward the fast tail.
        _t_assess_start = time.perf_counter()
        caught_exc: Exception | None = None
        try:
            assessment = await _to_thread_with_ctx(
                assess_requirement, client, req["text"], candidates
            )
        except Exception as exc:
            caught_exc = exc

        _t_assess_ms = (time.perf_counter() - _t_assess_start) * 1000.0
        if DEBUG:
            print(f"[jd_assessor] assess_call_ms={_t_assess_ms:.1f} req_idx={index}")

        if caught_exc is not None:
            logger.warning(
                "[jd_assessor] assess-caught req_idx=%d req_text=%r exc=%r",
                index,
                req["text"],
                caught_exc,
            )
            return index, _unassessed_row(req, _MODE_1_GAP_TEXT)

        assessment["category"] = req["category"]
        # MATTGPT-245 phase two: overwrite the LLM's
        # `assessment["requirement"]` (JSON output, not passthrough of
        # input) with `req["text"]` so the resolved row's requirement
        # text matches the pending row's within a single assessment
        # run. Without this, the progressive fill can flip requirement
        # wording as each row resolves (assess LLM sometimes copies
        # verbatim, sometimes paraphrases), producing the same
        # requirement reading two ways in the same panel. Removes the
        # assess-side source of paraphrase variance; extraction-side
        # nondeterminism is separately tracked in -160.
        #
        # Consistency notes:
        # - Mode 1 and Mode 2 unassessed rows already use req["text"]
        #   via _unassessed_row(req, ...), so those exit paths are
        #   already passthrough -- no symmetric change needed.
        # - _build_share_text and _build_export_html read
        #   `requirement` off the row, so they inherit this fix
        #   without further changes.
        assessment["requirement"] = req["text"]
        return index, assessment


async def _fan_out_assessments(
    client: OpenAI,
    all_requirements: list[dict],
    stories: list[dict],
    on_row=None,
) -> list[dict]:
    """Run per-requirement retrieve + assess concurrently at _CONCURRENCY.

    Returns a list of assessment dicts in submission order, independent
    of completion order. Exceptions propagate on the first task
    exception; pending tasks are cancelled and drained before the
    exception re-raises. MATTGPT-248 Cycle 2 ended up catching Mode 1
    (assess raise) and Mode 2 (retrieve None) per-call inside
    `_assess_one_with_index` rather than using
    `return_exceptions=True` here, so the only exceptions still
    reaching this loop are Mode 4 (retrieve raise) and cancellation.

    MATTGPT-245 phase two: `on_row(index, assessment)` is an optional
    per-completion callback. Fires in completion order (whichever task
    finished, whatever order that is) with the SUBMISSION index and
    the full assessment dict. The Role Match UI passes a closure that
    writes into a per-requirement st.empty() slot for progressive
    row-fill; the service stays Streamlit-free by taking a plain
    Python callable. Return value is unchanged whether on_row is
    provided or omitted -- the callback is a side channel, not a
    replacement (test 6 in TestFanOutOnRowCallback pins this).

    Mode 1 and Mode 2 unassessed rows fire the callback like any
    other completion (tests 4 and 5) -- otherwise the corresponding
    UI slot would stay in the pending state indefinitely. An
    exception raised inside on_row propagates through the loop and
    into the BaseException cancel-and-drain handler; the UI callback
    is expected to be a simple slot write and not raise."""
    semaphore = asyncio.Semaphore(_CONCURRENCY)
    tasks = [
        asyncio.create_task(_assess_one_with_index(i, semaphore, client, req, stories))
        for i, req in enumerate(all_requirements)
    ]

    results_by_index: dict[int, dict] = {}
    try:
        for done in asyncio.as_completed(tasks):
            index, assessment = await done
            results_by_index[index] = assessment
            if on_row is not None:
                on_row(index, assessment)
    except BaseException:
        # MATTGPT-243 + MATTGPT-248 Cycle 2: three things worth naming
        # at this raise site.
        #
        # 1. `except BaseException` is deliberate. asyncio.CancelledError
        #    no longer derives from Exception in modern Python, and the
        #    handler is cleanup followed by a bare `raise`. Narrowing to
        #    `Exception` would let a cancellation propagate through this
        #    loop without draining pending tasks, defeating the point of
        #    the whole block.
        #
        # 2. Cancel pending tasks before propagating. Abandoned tasks that
        #    later complete with an exception and no reader print
        #    "Task exception was never retrieved" to stderr, and
        #    MATTGPT-222's operational alarms read stderr. The
        #    asyncio.gather with return_exceptions=True below drains the
        #    cancelled tasks so their exceptions are consumed rather than
        #    left dangling.
        #
        # 3. Under asyncio.as_completed the exception surfaced from this
        #    loop is first-by-completion, not first-by-requirement-order.
        #    Cycle 2 narrows what can reach this handler: assess_requirement
        #    exceptions (Mode 1, rate limit / malformed JSON / transient
        #    5xx) are now caught per-call inside `_assess_one_with_index`
        #    and converted to unassessed rows, so the only remaining
        #    routes are Mode 4 (retrieve_stories raise) and cancellation.
        #    The trim is deliberate: the previous example about racing
        #    assess-side error types (RateLimit on req_3 vs BadRequest on
        #    req_7) no longer applies. Non-determinism still exists for
        #    two racing Mode 4 retrieval failures on different
        #    requirements, or for cancellation racing a Mode 4 raise --
        #    the banner is honest either way, but the ordering deserves
        #    the comment.
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    # Re-sort by submission index. This preserves the contract the loop
    # characterization test's reverse-sleep fixture asserts on: order
    # matches submission, independent of which task completes first.
    return [results_by_index[i] for i in range(len(all_requirements))]


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
