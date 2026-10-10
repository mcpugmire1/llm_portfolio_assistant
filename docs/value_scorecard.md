# MattGPT Value Scorecard

The eight value drivers for MattGPT, each with its intended outcome, the
acceptance criteria that exist today (quoted with source), status, evidence,
and open tickets. This is the drivers' first written source.

**Status values:** met · failing · not measured. A criterion with no written
threshold is marked **undefined**; this file does not set thresholds.

**Tickets:** every Open, In Progress, Blocked or Parked ticket in BACKLOG.md
appears under exactly one primary driver. Other drivers a ticket affects are
noted in the ticket itself.

**Baseline:** collected Oct 10, 2026 (main at 3d0da24) and the design spec
repo. Evaluator fixture: `tests/fixtures/evaluator_conversations.md` at
609f903 (18 conversations). Corpus: dacf2ff.

## Summary

| # | Value driver | Outcome written? | Criteria | Status |
|---|---|---|---|---|
| 1 | Semantic understanding | Yes (Matt, Oct 10, 2026) | Undefined | Not measured |
| 2 | Conversational continuity | Yes | Per-turn only; aggregate undefined | Not measured (no valid run on 609f903) |
| 3 | Trust and credibility | Yes | Partly | Failing (reproduced defects); golden eval count unsettled |
| 4 | Role Match | Yes | Partly | Not measured on the current pipeline; BDD failing |
| 5 | Evidence parity | Yes | One case only (CS degree) | Failing on that case; general parity not measured |
| 6 | Evidence discovery | Yes | Yes (BDD); search relevance undefined | Stale; two known failures |
| 7 | Operational reliability | Yes (Matt, Oct 10, 2026) | Undefined | Not measured; production logging unverified |
| 8 | Professional demonstration | Yes | Goals with time budgets; measurement undefined | Not measured |

## 1. Semantic understanding

**Intended outcome (Matt, October 10, 2026):** Visitors find relevant
professional stories even when their terminology differs from the corpus:
synonyms, misspellings, missing punctuation and natural phrasing.

**Criteria:** undefined.

**Status:** not measured.

**Open tickets:** -285 (nonsense filter rejects portfolio questions), -283
(embedding model PoC), -185 (negation), -190
(tokenizer divergence), -171 (phrase matching), -177 (token_overlap_ratio
bound), -199 (AT&T content-kw gate), -063 (wrong-person queries), -077
(pronoun and noun-overlap contamination), -195 (incident vocabulary
routing), -236 (router topical families), -239 (router confidence floor,
Blocked), -062 (stale router embeddings), -167 (entity detection for
Project and Place, Parked).

## 2. Conversational continuity

**Intended outcome:**
- "A strong implementation should demonstrate that it can answer from
  profile and conversation when appropriate, retrieve when necessary, and
  use retrieved stories as evidence rather than as a mandatory script."
  (`tests/fixtures/evaluator_conversations.md`, Acceptance Criteria)
- "Ask Agy is a conversational system, and retrieval is an evidence step
  inside it, not the system." (`docs/ADR.md`, ADR 040, Planned)

**Criteria:**
- Fixture: per-turn expected answers for 18 conversations, scored on
  "Answered", "Honest" and "Remembered context". "'Answered' means the
  correct referent and materially correct facts, not matching the expected
  wording." Aggregate pass threshold: **undefined**.
- MATTGPT-275 Acceptance: the fixture "with its approved expected answers
  (0f6a465)". That is the 9-conversation version; the current fixture is
  609f903.
- Run count: "at least 2 runs per query" (CLAUDE.md, Testing Protocol).
  Repeated-run reliability rate: **undefined**.

**Status:** not measured. No valid evaluator run exists on 609f903.

**Evidence (stale, all before dacf2ff):**
- Tool vs pipeline: 101/110 vs 68/110 (5f9d9bf, scoring corrected in 50bc068).
- Lever 2: 56/65 follow-ups (f7c1de2).
- Oct 10 clean PoC: invalid as a controlled comparison.
- Golden eval multi-turn (Q24) and intent (Q18 to Q20) items pass
  automatically (`tests/eval_rag_quality.py`).

**Open tickets:** -275, -253 (Blocked on -275), -040 (follow-up eval
coverage), -282 (answering model beyond gpt-4o), -281 (openers), -280
(tone), -284 (synthesis mode decided in four places).

## 3. Trust and credibility

**Intended outcome:**
- "Proof over claims. Every claim traces to a real, sourced story. If it
  cannot cite its evidence, it does not reach a user." (design spec
  `index.md`)
- "Honest before impressive. The system says when it does not know and will
  not inflate a match." (design spec `index.md`)
- "Every answer is anchored to specific sourced projects" (design spec
  `docs/01-product-vision.md`)

**Criteria:**
- Golden eval: "≥ 95% (61+/64)" pre-merge, "≥ 98% (63+/64)" production
  deploy; "conventions, not automated checks" (design spec
  `docs/11-testing-and-quality.md`).
- `docs/EVAL_FRAMEWORK.md` Target Metrics: Professional Narrative Fidelity
  95%+, Client Attribution Accuracy 100%, Voice (No Banned Phrases) 100%,
  Overall Pass Rate 90%+.
- MATTGPT-275: "Surface parity with My Work: a question in the 0.20-0.25
  band ... is answered, with an explicit hedge when the evidence is thin";
  "Do not change `CONFIDENCE_HIGH`".
- MATTGPT-250: "'Is Matt certified?' returns all four certifications
  verbatim with their issued/expired status. Nothing is presented as
  current."
- Unsupported claims (-251) and evaluative sentences (-252): **undefined**
  (no threshold).

**Status:**
- Golden eval: 63/65, Q59 the expected xfail (d0b6376, Oct 7). The gates
  are written against /64, and the count appears as 70/70, 65/65, /64 and
  63/65 across sources. Met or failing is **undefined** until the count is
  settled.
- Failing: the meta-commentary strip garbles answers, 6 of 130 in
  `docs/evidence/MATTGPT-275/candidate_20261009_085832/` (6d41ff8),
  including the production path. Unsupported claims (-251) and evaluative
  sentences (-252) are reproduced in their tickets.
- 275's surface-parity hedge: not measured.

**Open tickets:** -251, -252, -255, -128 (source cards substantiate
claims), -168 (slot 1 amplification), -250 (profile facts in Ask Agy, In
Progress), -257, -263, -278, -279, -096, -217 (pronoun grammar), -286 (meta-commentary
strip deletes paragraphs), -290 (internal-content
extraction).

## 4. Role Match

**Intended outcome:**
- "Role Match scores honestly, not generously." (design spec `index.md`)
- "Answer 'Can he do the job?' and 'Can we hire him?' in under 90 seconds."
  (design spec `docs/03-ux-design-process.md`, J1)

**Criteria:**
- `services/jd_assessor.py`: `RECOMMENDATION_STRONG_RATIO = 0.7`,
  `RECOMMENDATION_COVERAGE_RATIO = 0.7`,
  `RECOMMENDATION_MAX_GAPS_CONSIDER = 1`; "Thresholds may be tuned after
  testing against real JDs."
- Assessor prompt: "A 'strong' match REQUIRES at least one cited piece of
  evidence"; "Never fabricate".
- MATTGPT-244: "Demo JD row 22 ... no longer returns SUPPORTED with a
  Build-Measure-Learn citation"; "`confidence` field absent from assessment
  prompt, response schema, and all downstream consumers."
- MATTGPT-160: "Count spread on the AT&T fixture narrows to 1-2 across five
  cold-path runs"; "No wall-clock target."
- MATTGPT-272: "Role Match no longer returns a blanket gap on the
  thought-leadership requirement."
- Over-claim rate, evidence selection, 90-second budget: **undefined**
  measurement.

**Status:**
- Failing: BDD 19 passed, 29 skipped, 5 failed (53ef187, Sept 26).
- Not measured: over-claim rate on the current pipeline (the -244 baseline
  predates its fix); -160's after-measurement not recorded; the 90-second
  goal.
- -272: awaiting validation. A thought leadership story landed in ab65efc
  (Oct 9); re-embed and the Acceptance run are not recorded.
- `compute_recommendation()` has no caller in `ui/`: the overall
  recommendation is not shown to visitors.
- Unbound: `jd_assessment.feature`, `jd_extraction.feature`.

**Open tickets:** -244 (In Progress), -160 (In Progress), -266, -249, -272
(awaiting validation), -254, -012 (In Progress), -014, -017, -081, -099,
-173, -079, -264, -267.

## 5. Evidence parity (Ask Agy and Role Match)

**Intended outcome:**
- Failure mode: "Role Match vs Ask Agy inconsistency (credibility hit)"
  (design spec `docs/03-ux-design-process.md`, J3).

**Criteria:**
- MATTGPT-268: "CS phrasings no longer lead with a no; PMP still produces a
  no; story controls unchanged."
- General parity (claims, metrics, cited stories, industries): **undefined**.

**Status:**
- -268: failing (open). Only paired run:
  `docs/evidence/MATTGPT-268/20260925_092116/step1_output.txt`, with
  differently worded inputs.
- General parity: not measured.

**Open tickets:** -268.

## 6. Evidence discovery

**Intended outcome:**
- "I want to browse and filter Matt's transformation stories"
  (`tests/bdd/features/explore_stories.feature`)
- "the first impression represents Matt's project portfolio rather than
  career-narrative meta-stories"
  (`tests/bdd/features/explore_stories_default_state.feature`)
- "any card visible on the page leads to a non-empty My Work result"
  (`tests/bdd/features/banking_landing.feature`)

**Criteria:**
- `explore_stories.feature` scenarios; default view "corpus total minus the
  10 Professional Narrative stories".
- MATTGPT-146 (no Professional Narrative story in filtered results),
  MATTGPT-228 (deep link consumed, in-app escape).
- Search relevance: `search.feature` has diversity thresholds but its
  binding is commented out (`tests/bdd/steps/test_steps.py`). **Undefined**
  as an active criterion.
- Timeline accuracy: **undefined**.

**Status:**
- Stale: `explore_stories` 59/59 (a2e7e7a, Sept 2); full BDD suite 256
  passed, 15 failed (7850ed2, Oct 6).
- Not measured: filter correctness, sort order and row content (the
  `st.dataframe` canvas constraint); no record of the manual check.
- Failing: -146, -228 (open bugs).
- The career-narrative field differs by surface (Theme, Era, Category).

**Open tickets:** -146, -228, -204, -196, -150, -122, -131, -197, -145,
-183, -187, -210, -166, -083, -271.

## 7. Operational reliability

**Intended outcome (Matt, October 10, 2026):** The product delivers its
experience reliably and sustainably; failures are visible, not silent.

**Criteria:** undefined.

**Status:**
- Not measured. Production logging is unverified: the Sheet has no cloud
  rows after Sep 20.
- Unbound or stale tests reduce what a green run proves: 7 feature files
  unbound (`agy_voice`, `evidence_fidelity`, `mode_routing`,
  `entity_routing`, `jd_assessment`, `jd_extraction`,
  `story_detail_feedback`), plus `search.feature` commented out.

**Open tickets:**
- Alarms and telemetry: -222, -223.
- Silent failures: -288 (Ask Agy ignores the Pinecone fallback signal).
- Regression gates and test reliability: -039, -233, -235, -206, -153,
  -274, -084, -180, -277, -198, -035, -060, -082, -143 (Parked), -203,
  -209, -213.
- Architecture and maintainability: -258, -259, -260, -261, -262, -140,
  -201, -202, -214, -226, -256.
- Dead code and hygiene: -176, -232, -241, -152 (Parked), -270, -287 (docs
  describe a removed overlap gate).
- Visible glitches: -229, -289 (MATTGPT-018 regression watch).

## 8. Professional demonstration

**Intended outcome:**
- "Replace 'I'm experienced' with 'Here's exactly what I did, how I did it,
  and the measurable results.'" (design spec `docs/01-product-vision.md`,
  Mission)
- J1: "in under 90 seconds"; J2: "Six facts, 30 seconds. No digging
  required."; J3: "Commit to a 30-minute screening call with a sharp
  agenda, or amplify as a secondary referrer." (design spec
  `docs/03-ux-design-process.md`)

**Criteria:**
- The journey time budgets and the screening-call outcome: **undefined**
  measurement.
- Numeric portfolio metrics were removed from the design spec in 72172e5
  (design spec repo, Dec 2025).

**Status:** not measured. Contact and LinkedIn clicks, referral copy, and
Ask Agy feedback are not logged.

**Open tickets:** -045 (analytics dashboard), -129, -078, -091, -155,
-022, -015, -095, -097, -154, -130, -156.
