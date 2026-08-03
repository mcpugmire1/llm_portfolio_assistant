"""
Probe: database extraction stripping + full-text vs stripped retrieval/assessment.

Steps:
  1. Run extract_requirements() on structured JD, confirm what text #7 produces.
  2. Run both phrasings through Pinecone at top-40; report full rank list with
     TICARA / AT&T Network Eng / Octane highlighted.
  3. Run assess_requirement() 3x per phrasing, Condition B (skills=[]).
  4. Report verdict + cited evidence per run; flag rank movement as the tell.

Prediction: TICARA was rank 18 (score 0.32) with database-dense Use Cases and
tech names moved scores by ~0.006. Expect full-text to leave ranks roughly where
they were and verdict to still gap -> corpus-shape / honest gap.
"""

import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".env"))

from openai import OpenAI  # noqa: E402

from services.jd_assessor import (  # noqa: E402
    ASSESSMENT_MODEL,
    ASSESSMENT_TEMPERATURE,
    JD_ASSESSMENT_PROMPT_TEMPLATE,
    _format_candidates_for_prompt,
    extract_requirements,
    retrieve_stories,
)
from services.pinecone_service import pinecone_semantic_search  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

JD_PATH = Path("tests/bdd/fixtures/jd_extraction/structured_jd.txt")
CORPUS_PATH = Path("echo_star_stories_nlp.jsonl")
SCRATCH_PROFILE_PATH = Path("data/scratch_profile_no_skills.json")

TOP_40 = 40
RUNS = 3

TARGET_FRAGS = ["ticara", "network engineering", "project octane", "octane"]

STRIPPED = "Experience with modern relational and NoSQL databases"
FULL_TEXT = (
    "Experience with modern relational and NoSQL databases "
    "such as SQL Server, PostgreSQL, or Redis"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_corpus():
    stories = []
    with open(CORPUS_PATH) as f:
        for line in f:
            stories.append(json.loads(line))
    return stories


def build_condition_b_grounding() -> str:
    """Return load_matt_profile() output with skills array blanked."""
    with open(SCRATCH_PROFILE_PATH) as f:
        profile = json.load(f)

    education_parts = []
    education_notes = []
    for e in profile["education"]:
        education_parts.append(f"{e['degree']} from {e['institution']}")
        if e.get("note"):
            education_notes.append(e["note"])
    education = " and ".join(education_parts)
    skills = ", ".join(profile.get("skills") or [])

    certs = ", ".join(profile.get("certifications", []))
    result = f"{profile['career_summary']} He holds a {education}."
    for note in education_notes:
        result += f" {note}"
    if skills:
        result += f" Matt's verified skills include: {skills}."
    if certs:
        result += f" Certifications: {certs}."
    return result


def is_target(hit: dict) -> str | None:
    story = hit.get("story", hit)
    sid = (story.get("id") or "").lower()
    title = (story.get("Title") or "").lower()
    for frag in TARGET_FRAGS:
        if frag in sid or frag in title:
            return frag
    return None


def run_top40(query: str, stories: list) -> list:
    return (
        pinecone_semantic_search(query=query, filters={}, stories=stories, top_k=TOP_40)
        or []
    )


def print_top40(label: str, hits: list):
    print(f"\n{'='*72}")
    print(f"TOP-40 — {label}")
    print(f"{'='*72}")
    print(f"  {'Rank':<5} {'Score':<8} {'Client':<22} Title")
    print(f"  {'-'*5} {'-'*8} {'-'*22} {'-'*38}")
    for i, h in enumerate(hits, 1):
        story = h.get("story", h)
        title = story.get("Title", "")[:38]
        client = story.get("Client", "")[:20]
        score = h.get("pc_score", 0)
        tag = is_target(h)
        flag = f"  <-- TARGET ({tag})" if tag else ""
        print(f"  {i:<5} {score:.4f}   {client:<22} {title}{flag}")


def run_assessor_3x(
    client: OpenAI, label: str, req_text: str, candidates: list, grounding_b: str
):
    """Run assess_requirement 3x in Condition B; print verdicts + evidence."""
    print(f"\n{'='*72}")
    print(f"ASSESSOR 3x — {label}")
    print(f"  Requirement: {req_text}")
    print("\n  Candidates retrieved (top-3):")
    for c in candidates:
        print(f"    score={c['score']:.4f}  [{c['client']}] {c['title'][:55]}")
    print(f"{'='*72}")

    sys_prompt = JD_ASSESSMENT_PROMPT_TEMPLATE.format(matt_profile=grounding_b)
    verdicts = []

    for run in range(1, RUNS + 1):
        user_message = (
            f"Requirement: {req_text}\n\n"
            f"Retrieved Stories:\n{_format_candidates_for_prompt(candidates)}"
        )
        resp = client.chat.completions.create(
            model=ASSESSMENT_MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=ASSESSMENT_TEMPERATURE,
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content)
        verdict = result.get("match_status", "?")
        evidence = result.get("evidence", [])
        gap = result.get("gap_explanation", "")
        verdicts.append(verdict)

        print(f"\n  Run {run}: {verdict.upper()}")
        for e in evidence:
            etype = e.get("evidence_type", "?")
            stitle = e.get("story_title") or ""
            rel = e.get("relevance", "")[:110]
            print(f"    [{etype}] {stitle[:40]}  {rel}")
        if verdict in ("gap", "partial") and gap:
            print(f"    GAP NOTE: {gap}")

    mode = max(set(verdicts), key=verdicts.count)
    print(f"\n  Mode (3 runs): {mode.upper()}  ({', '.join(verdicts)})")
    return mode, verdicts


def find_target_rank(hits: list, frag: str) -> tuple[int | None, float | None]:
    for i, h in enumerate(hits, 1):
        if is_target(h) == frag:
            return i, h.get("pc_score")
    return None, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading corpus...")
    stories = load_corpus()
    print(f"  {len(stories)} stories")

    print("Building Condition B grounding (skills=[])...")
    grounding_b = build_condition_b_grounding()
    skills_present = (
        "verified skills include:" in grounding_b
        and len(grounding_b.split("verified skills include:")[-1].strip()) > 2
    )
    print(f"  Skills clause present: {skills_present}  (should be False)")

    client = OpenAI()

    # ------------------------------------------------------------------
    # Step 1: Confirm extractor output for #7
    # ------------------------------------------------------------------
    print(f"\n{'='*72}")
    print("STEP 1 — Extractor: what text does #7 actually produce?")
    print(f"{'='*72}")
    jd_text = JD_PATH.read_text()
    print("  Running extract_requirements()...")
    extraction = extract_requirements(client, jd_text)

    all_reqs = []
    for r in extraction.get("required_qualifications", []) or []:
        all_reqs.append(("required", r))
    for r in extraction.get("preferred_qualifications", []) or []:
        all_reqs.append(("preferred", r))

    print(f"\n  Extracted requirements ({len(all_reqs)}):")
    db_req_text = None
    for i, (cat, r) in enumerate(all_reqs, 1):
        req = r.get("requirement", "")
        src = r.get("source_text", "")
        is_db = any(
            t in req.lower() for t in ["database", "nosql", "relational", "sql"]
        )
        flag = "  <-- DATABASE" if is_db else ""
        print(f"  [{i:>2}] [{cat}] {req[:72]}{flag}")
        if is_db:
            print(f"        source_text: {src[:80]}")
            db_req_text = req

    print(f"\n  Hardcoded STRIPPED:   '{STRIPPED}'")
    print(f"  Extractor produced:   '{db_req_text}'")
    if db_req_text:
        stripped = db_req_text.strip().lower() == STRIPPED.strip().lower()
        print(
            f"  Tech names stripped:  {'YES — confirmed' if stripped else 'NO — check manually'}"
        )

    # ------------------------------------------------------------------
    # Step 2: Top-40 retrieval for both phrasings
    # ------------------------------------------------------------------
    print(f"\n{'='*72}")
    print("STEP 2 — Top-40 retrieval: stripped vs full-text")
    print(f"{'='*72}")

    hits_stripped = run_top40(STRIPPED, stories)
    hits_full = run_top40(FULL_TEXT, stories)

    print_top40(f"STRIPPED  '{STRIPPED[:50]}'", hits_stripped)
    print_top40(f"FULL TEXT '{FULL_TEXT[:50]}'", hits_full)

    print("\n  TARGET RANK SUMMARY")
    print(f"  {'Frag':<28} {'Stripped rank/score':<24} {'Full-text rank/score'}")
    print(f"  {'-'*28} {'-'*24} {'-'*24}")
    any_target_found = False
    for frag in TARGET_FRAGS:
        r_s, sc_s = find_target_rank(hits_stripped, frag)
        r_f, sc_f = find_target_rank(hits_full, frag)
        if r_s or r_f:
            any_target_found = True
            s_str = f"{r_s}/{sc_s:.4f}" if r_s else "absent"
            f_str = f"{r_f}/{sc_f:.4f}" if r_f else "absent"
            print(f"  {frag:<28} {s_str:<24} {f_str}")
    if not any_target_found:
        print("  All target stories absent from top-40 under both phrasings.")

    # ------------------------------------------------------------------
    # Step 3: Assessor 3x per phrasing — Condition B
    # ------------------------------------------------------------------
    print(f"\n{'='*72}")
    print("STEP 3 — Assessor 3x per phrasing (Condition B: skills=[])")
    print(f"{'='*72}")

    cands_stripped = retrieve_stories(STRIPPED, stories, top_k=3)
    cands_full = retrieve_stories(FULL_TEXT, stories, top_k=3)

    mode_s, runs_s = run_assessor_3x(
        client, "STRIPPED", STRIPPED, cands_stripped, grounding_b
    )
    mode_f, runs_f = run_assessor_3x(
        client, "FULL TEXT", FULL_TEXT, cands_full, grounding_b
    )

    # ------------------------------------------------------------------
    # Step 4: Interpretation
    # ------------------------------------------------------------------
    print(f"\n{'='*72}")
    print("INTERPRETATION")
    print(f"{'='*72}")

    ticara_s, ticara_sc_s = find_target_rank(hits_stripped, "ticara")
    ticara_f, ticara_sc_f = find_target_rank(hits_full, "ticara")

    print(
        f"  TICARA rank:   stripped={ticara_s or 'absent'}, full-text={ticara_f or 'absent'}"
    )
    print(f"  Verdict mode:  stripped={mode_s.upper()}, full-text={mode_f.upper()}")

    if mode_s == "gap" and mode_f not in ("gap",):
        print("\n  EXTRACTION IS THE CAUSE: full-text phrasing lifts the verdict.")
        print("  Fix: preserve tech-name examples in the text sent to Pinecone.")
    elif mode_s == "gap" and mode_f == "gap":
        rank_moved = ticara_s and ticara_f and abs(ticara_s - ticara_f) > 3
        if rank_moved:
            print("\n  PARTIAL EXTRACTION EFFECT: full-text moves TICARA meaningfully")
            print("  but verdict stays gap. Root cause is corpus-shape.")
        else:
            print(
                "\n  CORPUS-SHAPE / HONEST GAP: full-text does not move verdict or rank."
            )
            print(
                "  Extraction fix would not change the outcome. Database gap is honest."
            )
    else:
        print(f"\n  Unexpected: stripped={mode_s}, full={mode_f}. Review manually.")


if __name__ == "__main__":
    main()
