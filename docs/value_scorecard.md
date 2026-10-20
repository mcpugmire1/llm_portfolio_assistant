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
| 1 | Semantic understanding | Yes (Matt, Oct 10, 2026) | Undefined | Failing on 2 of 20 pairs, Oct 10 on the old pipeline; not re-measured on 1095d2c |
| 2 | Conversational continuity | Yes | Per-turn only; aggregate undefined | Measured per turn in 1095d2c's acceptance run: new 386/450, 4 turns below bar |
| 3 | Trust and credibility | Yes | Partly | Failing (reproduced defects); golden eval on shipped code 4 failed of 282 (2e46a59) |
| 4 | Role Match | Yes | Partly | Not measured on the current pipeline; role_match BDD passing (1095d2c) |
| 5 | Evidence parity | Yes | One case only (CS degree) | Failing on that case; general parity not measured |
| 6 | Evidence discovery | Yes | Yes (BDD); search relevance undefined | Stale; two known failures |
| 7 | Operational reliability | Yes (Matt, Oct 10, 2026) | Undefined | Not measured |
| 8 | Professional demonstration | Yes | Goals with time budgets; measurement undefined | Not measured |

## 1. Semantic understanding

**Intended outcome (Matt, October 10, 2026):** Visitors find relevant
professional stories even when their terminology differs from the corpus:
synonyms, misspellings, missing punctuation and natural phrasing.

**Criteria:** undefined.

**Status:** failing on 2 of 20 pairs on Oct 10, on the old pipeline
(`rag_answer()`, code b2add9a; L5, held by design until
MATTGPT-251; L6, the confidence gate, which left the answer path in
1095d2c, MATTGPT-253 closed). Not yet re-measured on 1095d2c's
`agy_answer()` path. Threshold undefined.

**Evidence (Oct 10, 2026; `docs/evidence/semantic_checks/20261010_132625/`,
d66149f; code b2add9a, 124 stories, 2 runs per wording, health check
PASS):** 20 pairs, each a variant beside a control wording, through
`send_to_backend()`. 16 of 20 pass: synonyms 5/5, misspellings 5/5,
punctuation 4/4, loose phrasing 2/6. Every control was answered; both
runs agreed on every pair. Failures:
- L3 "When did Matt join Accenture?" (rule:general_knowledge) and L4
  "Tell me a story about Matt's leadership" (rule:creative_writing):
  fixed by MATTGPT-285 (017117f).
- L5 "Has Matt worked on trading platforms?" (rule:stocks_crypto): held
  until MATTGPT-251. Its control answer ("worked extensively on capital
  markets platforms" via ACCESS) is false too.
- L6 "where's he based these days": confidence gate, top Pinecone score
  0.185 < CONFIDENCE_LOW 0.2, still 0.185 on the 6ec9aec index:
  MATTGPT-253, closed: the gate left Ask Agy's answer path in 1095d2c.
  The wording is on MATTGPT-320's run list.

**Open tickets:** -283 (embedding model PoC), -185 (negation), -190
(tokenizer divergence), -171 (phrase matching), -177 (token_overlap_ratio
bound), -063 (wrong-person queries), -077
(pronoun and noun-overlap contamination), -195 (incident vocabulary
routing), -236 (re-scoped Oct 18: breadth for big-picture questions before the router comes out), -239 (router confidence floor,
Blocked), -062 (stale router embeddings), -167 (entity detection for
Project and Place, Parked), -304 (reranker spike).

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

**Status:** measured per turn on the shipped tool loop, Oct 15, 2026
(MATTGPT-275 gate rerun, `docs/evidence/MATTGPT-275/gate_20261015_093237/`, cited as 1095d2c's live acceptance). The
18 fixture conversations (609f903) plus extras x1 to x5 and x7, 45 live
turns, 10 runs per arm, scored blind (32 scorers, brief_v2):
- Total: new 386/450, opener 384/450, baseline 354/450 (`gate_result.json`).
- Turns below their bar: 4 (c03 t2, x1, x2, x4), each accepted as a known
  issue in 1095d2c. Required closings (c14 to c17) score 0/10 in every arm;
  275 stays open for them.
- Aggregate pass threshold: still **undefined**, so met or failing overall
  is undefined.

**Earlier evidence (stale, all before dacf2ff):**
- Tool vs pipeline: 101/110 vs 68/110 (5f9d9bf, scoring corrected in 50bc068).
- Lever 2: 56/65 follow-ups (f7c1de2).
- Oct 10 clean PoC: invalid as a controlled comparison.
- Golden eval multi-turn (Q24) and intent (Q18 to Q20) items pass
  automatically (`tests/eval_rag_quality.py`).

**Open tickets:** -275, -040 (follow-up eval
coverage), -281 (openers), -340 (restore the code-picked opener, used word for word), -280
(tone), -284 (synthesis mode decided in four places), -316 (blur submits the landing
question), -317 (Ask Agy About This dropped mid-answer).

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
- Golden eval on the shipped pipeline (Oct 16, 2026; 2e46a59, run on
  3d1f63d): 4 failed, 275 passed, 3 skipped of 282 tests, against 9
  failed on Oct 14. Failing: Q17 and Q65 (intent routing) and
  TestCorpusLiterals, as on Oct 14; Q6 newly (MATTGPT-304).
- Extras, same commit: MATTGPT-250's acceptance queries and MATTGPT-253's
  formerly refused queries, blind-scored: 30/30 single answers and 22/22
  conversation turns pass (52/52); Role Match equivalence note 2/2.
- MATTGPT-275 gate rerun, Oct 15 (`docs/evidence/MATTGPT-275/gate_20261015_093237/`, new arm, 450
  turns): invented figures, clients or dates 0; visible dashes 0 of 900 Sol
  answers (new and opener arms); runs with a contradicted claim 16 (x1 8,
  c10 3, c14 3, x7 2).
- Failing: the meta-commentary strip garbles answers, 6 of 130 in
  `docs/evidence/MATTGPT-275/candidate_20261009_085832/` (6d41ff8),
  including the production path. Unsupported claims (-251) and evaluative
  sentences (-252) are reproduced in their tickets.
- 275's surface-parity hedge: not measured.

**Open tickets:** -251, -252, -255, -128 (source cards substantiate
claims), -168 (slot 1 amplification), -257, -263, -278, -096, -217 (pronoun grammar), -286 (meta-commentary
strip deletes paragraphs), -290 (internal-content
extraction), -294 (split MATT_DNA by
responsibility, In Progress), -296 (closing offer in a prompt example), -297 (no dog humor in
answers), -300 (thinking indicator shows real progress), -301 (em dashes left in the repo), -306 (set store=False
after 275, Blocked), -307 (Key Metrics label cut), -310 (direct-reports
answer varies), -311 (no ongoing-period End_Date), -327 (rewritten quotations),
-328 (rule 0b decline follow-ups),
-341 (rows 20 and 27 with the "builder" revisit).

## Ask Agy (drivers 1 to 3, and 7): fitness functions and open decisions

Source: the change-governor's Ask Agy draft, checker-passed Oct 19, 2026 (relayed by Matt). The intent lines themselves stay in the design spec. Intent numbers: 1 no router in the answer path; 2 follow-up searches written by the model; 3 cards are the cited stories; 4 breadth on big-picture and named division or client questions; 5 profile facts as fact cards; 6 rule 0b decline; 7 voice; 8 every claim traceable; 9 failures visible; 10 wording variants.

**Fitness functions**

| Intent | Measure | Status | Latest result |
|---|---|---|---|
| 1 | Forced first search; nonsense rule fires with no model call | Exists (unit tests) | None recorded |
| 1 | No router call | Exists, xfailed until -236's Green (unit and BDD) | Router-off gate: A 524, B 532, C 531 of 610 |
| 2 | Model writes its own search; history placement | Exists (unit tests) | None for this measure; aggregate threshold undefined |
| 3 | Cards are the cited stories | Exists as an xfailed Red (5 tests) | None; `test_sources_are_the_stories_the_searches_returned` pins today's behavior |
| 3 | Cards back up the claims | Missing: -128's retrieval check ("Zero of the 65 eval queries") | None |
| 4 | Eras, projects, FS era presence over sources and cards shown | Exists, counts only (-338, no threshold) | None: no -338 run recorded |
| 4 | Breadth in the gate scorer; misattribution check | Missing: planned in -236's run | None |
| 5 | Fact cards come from the profile | Exists (unit tests) | None specific to fact cards |
| 5 | No story cards on a fact answer | Exists as an xfailed Red (-128) | None |
| 6 | Decline line reaches the model | Exists | -322 run 6: 79/80 declines pass |
| 6, 8 | Empty searches on work-history questions, every claim checked | Exists (-339 run, 26ffa39) | 7 of 11 claims supported; the 4 unsupported are the agriculture absence claim, a retrieval miss on -325. 0 of 10 natural runs had a zero-result search |
| 7 | Opener used word for word | Missing: planned on -340; a committed test currently asserts the opposite | None |
| 7 | No closing offer | Exists (gate c14 to c17, the -276 closers run) | 0 in every arm |
| 7 | Evaluative sentences | Exists on the final text; missing on raw text before the strip (-252) | 15 of 249 old vs 0 of 259 new (a lower bound) |
| 7 | No dashes | Exists | 0 of 450 gate turns |
| 8 | No invented figures, clients or dates | Exists (gate run) | None found; 16 runs with a contradicted claim |
| 9 | Breathers and error message | Exists (unit tests) | None recorded |
| 9 | Fallback is logged | Missing: planned on -292 | None |
| 10 | Wording variants vs controls | Exists on the old pipeline only; missing on `agy_answer()` | 2 of 20 pairs failing (Oct 10, old pipeline) |

**Open decisions**

| # | Question | Decide by |
|---|---|---|
| D1 | What makes a big-picture answer show more than 3 cards? Today `agy_answer()` sets the intent to None, so every answer gets at most 3. -236's target proposes the router's synthesis family as the signal. | -236's breadth decision, before -128's go |
| D2 | How is "cited" decided? Decided: option A, text match (Matt, Oct 19, 2026; recorded on -128). Still open on -128: where META-IND cards go, and the thin-answer shape. | -128's go |
| D3 | Breadth on big-picture questions: keep the synthesis pick, or replace it? Proposed (Matt, Oct 19): keep the router's synthesis family as the trigger, per -236's target; decided by -236's run. -332 waits on this. | Before -236's Green |
| D4 | Rows 20, 27 and 8: narrative stories on technical questions, the verbatim phrases, and Matt substitution in the search query. | -341's go, after -128's row 20 measurement; -077's re-wire-or-delete call before -287 deletes the functions |
| D5 | Row 14, the file-order fallback | -292's go |
| D6 | Row 13, empty searches on work-history questions | Resolved (Matt, Oct 19, 2026): -339 closed; row 13 accepted; the agriculture claims are on -325 |

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
- Over-claim rate, evidence selection, 90-second budget: **undefined**
  measurement.

**Status:**
- BDD role_match: 24 passed, 28 skipped (1095d2c, Oct 15); the five
  Sept 26 failures (53ef187) are fixed there.
- Not measured: over-claim rate on the current pipeline (the -244 baseline
  predates its fix); -160's after-measurement not recorded; the 90-second
  goal.
- Thought-leadership requirement: Strong, citing the thought leadership
  story (Matt's Role Match run, Oct 19, 2026; MATTGPT-272 closed).
- `compute_recommendation()` has no caller in `ui/`: the overall
  recommendation is not shown to visitors.
- Unbound: `jd_assessment.feature`, `jd_extraction.feature`.

**Open tickets:** -244 (In Progress), -160 (In Progress), -266, -249, -012 (In Progress), -014, -081, -099,
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
- General parity: not measured. Beyond the CS-degree case (-268), no run
  compares Ask Agy and Role Match on the same claims, metrics, cited
  stories or industries, so a parity gap elsewhere would not show up here.

**Open tickets:** -268, -309 (no match context in Ask Agy from Role
Match).

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

**Open tickets:** -146, -228, -204, -150, -122, -131, -197, -145,
-183, -210, -166, -083, -295 (Timeline era order), -308
(My Work first page is MattGPT stories), -324 (My Work profile facts, from -250), -325 (query-term mentions
missed under the cutoff or below the top 25), -331 (Home cards 3, 5 and 6 keep only their first Domain, High).

## 7. Operational reliability

**Intended outcome (Matt, October 10, 2026):** The product delivers its
experience reliably and sustainably; failures are visible, not silent.

**Criteria:** undefined.

**Status:**
- Not measured. The Sheet has cloud rows on Sep 20 and Oct 15 to 17.
  The Sep 20 to Oct 15 gap is explained: Matt purged the Sheet into an
  extract when the cloud/local split was added (MATTGPT-333, closed Oct 18,
  2026, not a bug). Cloud rows to date appear to be Matt's own sessions, so
  production visitor data is not yet a usable signal for the drivers.
- Unbound or stale tests reduce what a green run proves: 7 feature files
  unbound (`agy_voice`, `evidence_fidelity`, `mode_routing`,
  `entity_routing`, `jd_assessment`, `page_load_tracking`,
  `story_detail_feedback`), plus `search.feature` commented out (-345).

**Open tickets:**
- Alarms and telemetry: -222, -223 (My Work only).
- Latency: -299.
- Runtime and dependencies: -313 (Python 3.11 in prod, 3.13 local), -314 (pin pyarrow<25).
- Model retirement: -302 (gpt-4o family retires January 14, 2027).
- Silent failures: -292 (silent file-order fallback, High), -288 (Ask Agy ignores the Pinecone fallback signal).
- Regression gates and test reliability: -039, -233, -235, -206, -153,
  -084, -198, -035, -143 (Parked),
  -213, -342 (golden Q50 to Q52 send a placeholder question),
  -345 (7 unbound feature files: bind or delete).
- Architecture and maintainability: -258 (In Progress), -259, -260, -261, -262, -140,
  -214, -226, -343 (Era and Theme literals; extend -258's guard).
- Dead code and hygiene: -176, -241, -152 (Parked), -287 (docs
  describe a removed overlap gate), -332 (synthesis prompt path, after -236),
  -344 (uncalled functions, provisional).
- Process: -335 (governor skill pilot, advisory).
- Visible glitches: -229, -289 (MATTGPT-018 regression watch), -330 (Home to My Work half-emptied frame).

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
-022, -015, -095, -097, -154, -130, -156, -291 (role-play
requests, open decision), -298 (salary questions get the nonsense
banner), -312 (stream shows an unclosed bold marker), -315 (source-card
separators differ), -318 (ask_answer_model
fact), -321 (stale model comment and How Agy dialog copy), -337 (spec's golden-query count includes 11 queries the eval doesn't check).
