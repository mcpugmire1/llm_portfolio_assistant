"""
MATTGPT-158 single-condition assessor probe.

Runs production build_assessment_prompt() against frozen extraction caches.
The prior A/B design (Condition A: skills intact, Condition B: skills blanked)
closed with MATTGPT-080. Post-drop both profiles are identical on skills, so
Condition B was measuring new-versus-old grounding by accident. Removed to
halve runtime and cost per sweep.

Usage: set JD_PATH and OUTPUT_CSV below, then run. Extraction cache is reused
if present. Delete EXTRACTION_CACHE_PATH to force a fresh Stage 1 extraction.

Output: CSV at OUTPUT_CSV (req_num, category, requirement, mode, runs,
evidence_run1, special_watch).
"""

import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from openai import OpenAI

from services.jd_assessor import (
    ASSESSMENT_MODEL,
    ASSESSMENT_TEMPERATURE,
    _format_candidates_for_prompt,
    build_assessment_prompt,
    compute_recommendation,
    extract_requirements,
)
from services.pinecone_service import (
    PINECONE_NAMESPACE,
    _embed,
    _extract_match_fields,
    _init_pinecone,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_RUNS = 5
TOP_K = 5
JD_PATH = Path("tests/bdd/fixtures/jd_extraction/structured_jd.txt")
STORIES_JSONL = Path("echo_star_stories_nlp.jsonl")
OUTPUT_CSV = Path("probe_158_single_structured_jd_results.csv")
# Sidecar: saved once, reused on subsequent runs so requirement text is frozen.
# Delete this file to force a fresh Stage 1 extraction.
EXTRACTION_CACHE_PATH = Path(f"probe_extraction_{JD_PATH.stem}.json")

SPECIAL_WATCH_TERMS = [
    "machine learning",
    "ml",
    "nlp",
    "natural language",
    "cobol",
    "db2",
    "model lifecycle",
    "model development",
]
DATABASE_DETAIL_TERMS = [
    "database",
    "sql server",
    "postgresql",
    "postgres",
    "redis",
    "nosql",
    "relational",
]


# ---------------------------------------------------------------------------
# Corpus + Pinecone retrieval
# ---------------------------------------------------------------------------


def _load_corpus() -> dict:
    corpus = {}
    with open(STORIES_JSONL) as f:
        for line in f:
            s = json.loads(line)
            sid = s.get("id")
            if sid:
                corpus[str(sid)] = s
    return corpus


def _retrieve_candidates(idx, query: str, corpus: dict) -> list:
    # Bypasses pinecone_semantic_search to avoid Streamlit session_state
    # dependencies outside app context. TOP_K must be kept in sync with
    # DEFAULT_TOP_K in services/jd_assessor.py by hand — no shared constant.
    qvec = _embed(query)
    res = idx.query(
        vector=qvec,
        top_k=TOP_K,
        include_metadata=True,
        namespace=PINECONE_NAMESPACE,
        filter=None,
    )
    matches = getattr(res, "matches", []) or []

    candidates = []
    for m in matches:
        sid, score, _ = _extract_match_fields(m)
        story = corpus.get(str(sid))
        if not story:
            continue
        candidates.append(
            {
                "title": story.get("Title", ""),
                "client": story.get("Client", ""),
                "id": str(sid),
                "score": float(score),
                "5PSummary": story.get("5PSummary", ""),
                "Situation": story.get("Situation", []),
                "Action": story.get("Action", []),
                "Result": story.get("Result", []),
            }
        )

    return candidates[:TOP_K]


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------


def _assess(
    client: OpenAI, requirement: str, candidates: list, system_prompt: str
) -> dict:
    # Mirrors the OpenAI call in jd_assessor.py. If production moves to structured
    # outputs with a schema, changes response_format, or changes response parsing,
    # update this call to match or the probe measures a different call shape.
    user_message = (
        f"Requirement: {requirement}\n\n"
        f"Retrieved Stories:\n{_format_candidates_for_prompt(candidates)}"
    )
    response = client.chat.completions.create(
        model=ASSESSMENT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=ASSESSMENT_TEMPERATURE,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mode_verdict(runs: list) -> str:
    counts = Counter(r.get("match_status", "gap") for r in runs)
    return counts.most_common(1)[0][0]


def _evidence_summary(run: dict) -> str:
    ev = run.get("evidence", [])
    parts = []
    for e in ev:
        if e.get("evidence_type") == "story":
            parts.append(f"story: {(e.get('story_title') or '')[:40]}")
        else:
            parts.append("profile")
    return "; ".join(parts) if parts else "—"


def _is_special_watch(text: str) -> bool:
    lower = text.lower()
    return any(t in lower for t in SPECIAL_WATCH_TERMS)


def _is_database_req(text: str) -> bool:
    lower = text.lower()
    return any(t in lower for t in DATABASE_DETAIL_TERMS)


def _print_db_detail(req_num: int, req_text: str, candidates: list, run: dict):
    print(f"\n{'=' * 90}")
    print(f"DATABASE DETAIL — #{req_num}: {req_text}")
    print(f"{'=' * 90}")
    print("  Candidates retrieved:")
    for c in candidates:
        print(
            f"    score={c['score']:.4f}  [{c.get('client', '')}]  {c.get('title', '')[:70]}"
        )
    print(f"\n  match_status : {run.get('match_status', '?')}")
    summary = run.get("summary") or run.get("explanation") or ""
    print(f"  summary      : {summary[:200]}")
    ev = run.get("evidence") or []
    if ev:
        for e in ev:
            etype = e.get("evidence_type", "?")
            stitle = (e.get("story_title") or "")[:55]
            reasoning = e.get("reasoning") or e.get("explanation") or ""
            print(f"  [{etype:7}] {stitle}")
            if reasoning:
                print(f"             {reasoning[:250]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    system_prompt = build_assessment_prompt()

    print("Loading corpus...")
    corpus = _load_corpus()
    print(f"  {len(corpus)} stories")

    print("Loading JD...")
    jd_text = JD_PATH.read_text()

    print("Initialising Pinecone...")
    idx = _init_pinecone()
    if not idx:
        print("ERROR: Pinecone init failed.")
        sys.exit(1)

    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        project=os.getenv("OPENAI_PROJECT_ID"),
        organization=os.getenv("OPENAI_ORG_ID"),
    )

    # --- Stage 1: extract requirements (once, cached) ---
    # Cache freezes requirement text so Stage 2 Pinecone queries are identical
    # across probe runs. Delete EXTRACTION_CACHE_PATH to force re-extraction.
    print("\nExtracting JD requirements (Stage 1)...")
    if EXTRACTION_CACHE_PATH.exists():
        print(f"  [CACHED] Loading from {EXTRACTION_CACHE_PATH} — delete to re-extract")
        extraction = json.loads(EXTRACTION_CACHE_PATH.read_text())
    else:
        extraction = extract_requirements(openai_client, jd_text)
        EXTRACTION_CACHE_PATH.write_text(json.dumps(extraction, indent=2))
        print(f"  [FRESH]  Saved to {EXTRACTION_CACHE_PATH}")
    requirements = []
    for r in extraction.get("required_qualifications", []) or []:
        requirements.append({"text": r["requirement"], "category": "required"})
    for r in extraction.get("preferred_qualifications", []) or []:
        requirements.append({"text": r["requirement"], "category": "preferred"})
    for r in extraction.get("implicit_requirements", []) or []:
        requirements.append({"text": r["requirement"], "category": "required"})
    n_req = sum(1 for r in requirements if r["category"] == "required")
    n_pref = sum(1 for r in requirements if r["category"] == "preferred")
    print(f"  {len(requirements)} requirements: {n_req} required, {n_pref} preferred")

    # --- Stage 2: retrieve candidates per requirement ---
    print("\nRetrieving candidates (Stage 2)...")
    candidates_per_req = []
    for i, req in enumerate(requirements):
        candidates = _retrieve_candidates(idx, req["text"], corpus)
        candidates_per_req.append(candidates)
        print(
            f"  [{i+1:>2}/{len(requirements)}] {len(candidates)} candidates for: {req['text'][:60]}"
        )

    # --- Stage 3: assess, N_RUNS ---
    per_req_runs = [[] for _ in requirements]

    for run_idx in range(N_RUNS):
        print(f"\nAssessor run {run_idx + 1}/{N_RUNS}...")
        for req_idx, req in enumerate(requirements):
            cands = candidates_per_req[req_idx]
            result = _assess(openai_client, req["text"], cands, system_prompt)
            result["category"] = req["category"]
            per_req_runs[req_idx].append(result)
            verdict = result.get("match_status", "?")
            print(f"  [{req_idx+1:>2}] {verdict:<8}  {req['text'][:70]}")

    # --- Results table ---
    print("\n" + "=" * 100)
    print("RESULTS TABLE — mode of N_RUNS per requirement")
    print("=" * 100)
    print(f"{'#':>3}  {'Cat':>4}  {'Mode':>8}  {'Watch':>5}  Requirement")
    print("-" * 100)

    rows = []
    watches = []

    for i, req in enumerate(requirements):
        mode = _mode_verdict(per_req_runs[i])
        runs_str = "|".join(r.get("match_status", "?") for r in per_req_runs[i])
        watch = _is_special_watch(req["text"])
        ev = _evidence_summary(per_req_runs[i][0])

        watch_flag = "WATCH" if watch else ""
        print(
            f"{i+1:>3}  {req['category'][:4]:>4}  {mode:>8}  {watch_flag:>5}  {req['text'][:65]}"
        )

        if watch:
            watches.append({"num": i + 1, "requirement": req["text"], "mode": mode})

        rows.append(
            {
                "req_num": i + 1,
                "category": req["category"],
                "requirement": req["text"],
                "mode": mode,
                "runs": runs_str,
                "evidence_run1": ev,
                "special_watch": watch,
            }
        )

    print("=" * 100)

    # --- Recommendation (run 1 representative) ---
    results_r1 = [per_req_runs[i][0] for i in range(len(requirements))]
    rec = compute_recommendation(results_r1)
    print(
        f"\nRecommendation (run 1): {rec['recommendation']} / {rec['fit_score']} — strong={rec['strong_count']} partial={rec['partial_count']} gap={rec['gap_count']} (req gaps={rec['required_gap_count']})"
    )

    # --- Special watches ---
    print(f"\nSpecial watch ({len(watches)} matched):")
    if watches:
        for w in watches:
            print(f"  #{w['num']}  {w['mode']:<8}  {w['requirement'][:75]}")
    else:
        print("  (none matched)")

    # --- Database deep-dive ---
    db_reqs = [
        (i, req) for i, req in enumerate(requirements) if _is_database_req(req["text"])
    ]
    if db_reqs:
        for i, req in db_reqs:
            _print_db_detail(
                i + 1, req["text"], candidates_per_req[i], per_req_runs[i][0]
            )
    else:
        print("\n(no database requirements detected)")

    # --- CSV ---
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
