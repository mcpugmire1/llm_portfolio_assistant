# MATTGPT-275 clean PoC: test protocol

Lifecycle: working protocol for the clean turn-design PoC against lever 2. Delete when the turn design's Green ships or the result is recorded in a commit message. Revised Oct 10, 2026, with Matt's decisions D1 to D9. Nothing below has run. No code and no runs until Matt approves it.

**Fixture, frozen:** `tests/fixtures/evaluator_conversations.md` at commit `609f903`: conversations 1 to 18. `00ee9dd` added conversation 11 and scored conversation 10's duration turn on the dates of the work the second turn described; `609f903` added the design doc's cases as conversations 12 to 18. The probe aborts if the file differs from that commit. Section 3 quotes its expected answers verbatim. Where this protocol scores a turn differently (D4, D5), the line is marked **Protocol** and the protocol governs.

**Design doc:** `docs/working/MATTGPT-275_turn_design.md`, Sections 2, 3, 5 and 6.

## 1. What the PoC changes vs lever 2

The result measures the combined design (D1). These are all the differences; nothing else differs (Section 2).

1. **Planner with turn_type:** a forced `plan_turn` call before answering, on gpt-4o (D3), using the strict schema (`turn_type`, `action`, `referents`, `query`, `clarify_question`, `reason`). It replaces lever 2's forced first `search_stories` call.
   - Validation checks shape only: referents are index keys; clarify names 2+ candidates and a question; query is present where required; reason and turn_type are present. An invalid plan falls back to search on the model's query.
   - The one rule: a `follow_up` that synthesizes with no referents falls back to `answer_from_referent` on the latest turn's engagements.
   - Every fallback is logged.
2. **Discussion record:** one entry per assistant turn holding the action, the referents, the engagements the answer used and the open offer. The planner and the answering call see the latest turn's engagements as default referents; earlier turns are listed for reference only.
3. **Evidence by action:** the PoC chooses the evidence path, and that choice is part of the design under test.
   - `answer_from_referent`: the referent engagements' stories by id, up to 6 per engagement.
   - `search` and `gap`: `semantic_search()` top 5 on the planner's query.
   - `synthesize`: the referents' stories, up to 3 per engagement, or `get_synthesis_stories(top_per_theme=1)` when there are no referents.
   - `clarify`: none.
   - `profile`: the profile only.
4. **Dates in context:** each story block carries its `Start_Date` and `End_Date`, and the engagement index carries each engagement's range.
5. **Closing with valid index keys:** the answering call returns `closing` (none, explore, engage). Code keeps `explore` only with an index key, and keeps `engage` only with a quote found in the visitor's words. Contact and LinkedIn come from `footer.py`, since the profile has no contact entry yet.
6. **Turn block in the answering prompt (D1):**
   - the action and referents;
   - "earlier answers are conversation, not evidence" (decision a);
   - the dates sentence (span from the dates, no extra precision);
   - the no-level-labels sentence;
   - the clarify and gap action rules;
   - the record rendered in the system prompt.
7. **Single forced answering call (D2):** the PoC answers in one forced `respond` call with no further search. Lever 2 answers in a loop: the forced first search, any further `search_stories` calls, then `tool_choice="none"`. An outcome is credited to the bundle, not to planning alone.

## 2. What stays identical

- **Fixture:** the commit above, in both arms.
- **Corpus:** `dacf2ff` (`echo_star_stories.jsonl` and `echo_star_stories_nlp.jsonl`), 124 stories, 46 engagements, in both arms. The Pinecone index is shared and refreshed at `dacf2ff`.
- **Code base:** both arms run in one worktree at `b55f9ce` plus `lever2_20261007_211535/green_working_tree.diff`, with the corpus files checked out from `dacf2ff`. Lever 2's arm adds the forced first search (tool_choice "required") and instructions in the system prompt (`moved()`), as frozen.
- **Answering model and base prompt:**
  - Model: gpt-4o (`DEFAULT_CHAT_MODEL`). Temperature: 0.2 for synthesis, 0.4 otherwise, as in `agy_answer()`. `max_tokens=900`.
  - Base prompt: `build_system_prompt()` and `build_user_message()` with the same opener and focus angle (`_choose_opening_and_focus()`), and the same history (`_build_history_messages()`). The PoC adds only difference 6.
  - Evidence is passed as a `search_stories` tool result in the same story-block format, apart from the `[DATES]` line (difference 4).
- **Same retrieval:**
  - The search implementation and its settings stay fixed in both arms: `semantic_search()`, `SEARCH_TOP_K`, top 5 to the model, the same Pinecone index, embedding model and confidence thresholds (`config/constants.py`), and the same `get_synthesis_stories()`.
  - The nonsense filters and the router rejection run before the turn in both arms.
  - Which evidence path the PoC chooses is difference 3, not a retrieval change.
- **Post-processing:** `_postprocess_agy_text()` from the same tree, on the answer text, in both arms.
- **API path:** Chat Completions for answering in both arms. The planner (PoC only) runs through Chat Completions on gpt-4o at temperature 0. The Responses API was needed only for gpt-6.1-sol, which is out of this run (D3).

**Not identical, by construction:**
- **Conversation 17's seed:** lever 2 gets the same seeded text, but no record and no open offer (it has neither).
- **Synthesis:** the frozen lever 2 build predates the settled synthesis retrieval (`candidate_20261009_085832`, `6d41ff8`), so neither arm has that design's promotion of client-broad turns. Router synthesis turns behave the same in both.

## 3. Cases and expected outcomes

Fixture wording where the fixture has the case; design doc Section 5 wording otherwise. Every turn is also subject to the rules in Section 4, and a turn with no written outcome is scored on those alone.

### Fixture conversations (all 18, D8)

Each conversation's turns and expected answers are quoted verbatim from the fixture at `609f903`. Conversations 12 to 18 are the design doc's cases 3, 4, 7, 8, 9, 10 and 16. Turns the fixture gives no expected answer for are scored on the fixture's first-turn rule (Section 4). Lines marked **Protocol** are rules this protocol adds; they are not in the fixture.

**1. Payments experience.** “Tell me about his payments work.” → “How big was the team?” → “What went wrong?”
- "How big was the team?": the team on the engagement just described. For JP Morgan ACCESS, a blended onshore/offshore team of 40+ across Accenture and JP Morgan. Fails if it gives a different engagement's team.
- "What went wrong?": what went wrong on that same engagement, from its story (for ACCESS, the WebSeries platform could not meet JP Morgan's needs out of the box; he owned Sev-1 production incident response). If the story records no failure, it says so. Fails if it narrates a different engagement, such as the anonymized Fortune 500 data-exposure story.
- **Protocol:** When the first turn discussed several engagements, a clarifying question naming them passes on both follow-up turns (D4).

**2. Education.** “Does he have a CS degree?” → “Why shouldn’t that worry me?”
- "Why shouldn't that worry me?": explains the missing CS degree from the profile (Master's in Information Technology, American InterContinental University, a recognized Computer Science-related discipline that exceeds a Bachelor's) plus his technical track record, stated as facts. Fails if it inflates, evaluates, or ignores the degree.

**3. Leadership.** “What’s his leadership style?” → “Give me an example where that didn’t work.”
- "Give me an example where that didn't work.": one story the corpus presents as a shortfall or failure under his leadership, described honestly. Fails if it reframes a success as a failure or gives no example.

**4. Certifications.** “Is he certified?” → “What about PMP?” → “Are any of those current?”
- "What about PMP?": no PMP, then the certifications from the profile. Fails if it pivots to PMO stories in place of the answer.
- "Are any of those current?": no, all are expired (AWS Solutions Architect Associate expired 2023, AWS Cloud Practitioner expired 2023, SAFe 4 Agilist expired, Oracle 8i exams 2002). Fails if it implies any are current.

**5. Career motivation.** “Why is he looking?” → “Why should we hire him over someone who stayed in-house?”
- "Why should we hire him over someone who stayed in-house?": answers the in-house comparison directly from the corpus (what consulting breadth across clients brings), stated as facts. Fails if it disparages in-house candidates, invents claims, or gives a generic pitch that ignores the comparison.

**6. Healthcare experience.** “Has he worked in healthcare?” → “What did he actually do there?”
- "What did he actually do there?": his role and actions in the healthcare work (AI-powered chronic disease management and responsible AI governance for patient data privacy, for a major U.S. health system). Fails if generic or about non-healthcare work.

**7. Location.** “Where is he based?” → “Would he relocate?”
- "Would he relocate?": yes, open to relocation and travel (based in Atlanta, GA). Fails if it hedges, deflects, or invents conditions.
- **Protocol:** "Would he relocate?" is also an over-asking control (design doc case 6): any clarifying question fails.

**8. Failure and growth.** “Tell me about a time he failed.” → “What did he change afterward?”
- "What did he change afterward?": the changes from that incident's own story (IAM validation, environment verification, PII scrubbing, and risk ownership as day-one responsibilities). Fails if it presents a different engagement as a consequence of the incident; mentioning one plainly as separate is not a fail on its own.

**9. Topic switch.** “Tell me about his payments work.” → “What’s his leadership style?” → “Give me an example.” → “How big was the team on that project?”
- "What's his leadership style?": leadership style with no payments carry-over.
- "Give me an example.": an example of the leadership style just described, not payments.
- "How big was the team on that project?": the team size of the project used as the example in the previous turn (for the Cloud Innovation Center, 150+, grown from a 10-person pilot). If that story gives no size, it says so. Fails if it reports the payments team or an unrelated project.

**10. Accepting an offer.** “Tell me about his Norfolk Southern work.” → “Sure, the deep dive on that one.” → “How long did that take?”
- "Sure, the deep dive on that one.": more depth on the same Norfolk Southern engagement from its story (his role, the approach, the outcomes), not a repeat of the first answer and not a different engagement. If the first answer ended with an offer, this delivers what was offered, for that story.
- "How long did that take?": the duration of the work the second turn described, from that story's dates, stated approximately, or a clarifying question if the second turn covered stories with different ranges. Norfolk Southern's engagement runs 2019-11 to 2023-09; the quality-crisis story runs 2020-01 to 2020-12. Fails if it conflates the two timelines, says the duration is not on record, gives the CIC Academy's six months as the whole, gives another project's timeline, or invents precision.
- **Protocol:** The first turn is also subject to the closing rules (Section 4).

**11. Ambiguous follow-up after a topic change.** “How did Matt scale engineering teams from 4 to 150+ people?” → “Tell me about his payments work” → “how big was his teams”
- "how big was his teams": the teams from the previous answer: JP Morgan ACCESS (40+) and RBC (its size if the story records one; if not, it says so), or a clarifying question asking which. Fails if it answers about the Cloud Innovation Center or another engagement not in the previous answer.
- **Protocol:** "Tell me about his payments work" sets a new topic: it fails Remembered context if it carries the first turn's scaling topic into the payments answer.
- **Protocol:** "how big was his teams" is scored against the engagements that run's second answer actually discussed, not the fixture's fixed JP Morgan ACCESS and RBC, and every fact is checked against the corpus (D5). With that substitution the fixture's pass and fail apply: their team sizes from their stories (or a statement that a story records none), or a clarifying question asking which; fails on the Cloud Innovation Center or any engagement the second answer didn't discuss.

**12. Comparing two engagements.** (design doc case 3) “Compare his Fiserv and JP Morgan ACCESS work.” → “Which was bigger?”
- "Compare his Fiserv and JP Morgan ACCESS work.": both engagements from their stories. Fails if it leaves out either engagement.
- "Which was bigger?": asks bigger by what (team, budget, reach), or names the dimension and compares both engagements accurately on it. The stories hold: Fiserv, a 45-person team and an $8.5M program; ACCESS, a blended team of 40+ and 135,000+ clients. Fails if it picks one without naming the dimension, compares on a dimension inaccurately, or leaves out one engagement.

**13. Unambiguous follow-up.** (design doc case 4) “Tell me about his Fiserv work.” → “How big was the team?”
- "How big was the team?": the Fiserv team size from its story (45). Fails if it asks a clarifying question or gives another figure.
- **Protocol:** An over-asking control: any clarifying question fails.

**14. Evaluating for a role.** (design doc case 7) “I’m hiring a VP of Platform Engineering. Would Matt be a fit?”
- "I'm hiring a VP of Platform Engineering. Would Matt be a fit?": the facts relevant to the role's scope from the stories (organization size, platforms, delivery), with no level label ("VP-level", "Director-level", "Senior Director"), no vouching ("a strong fit"), and no refusal because of the VP title. It closes with an offer to run Role Match against the job description. Fails if it asserts or denies a level, evaluates fit itself, or has no Role Match close.
- **Protocol:** A required closing (D9). In the PoC this is the engage close with Role Match.

**15. Getting in touch.** (design doc case 8) “How do I get in touch with Matt?”
- "How do I get in touch with Matt?": a close carrying Contact and LinkedIn links that work in the conversation view. Fails if either link is missing or invented.
- **Protocol:** A required closing (D9). The links working in the conversation view needs a browser check, which this probe can't do: the links are scored on being present and correct, and the view is reported as not tested.

**16. Résumé.** (design doc case 9) “Can I see his résumé?”
- "Can I see his résumé?": points to About Matt (his profile) and LinkedIn. Fails if it invents a file or a link.
- **Protocol:** A required closing (D9).

**17. Accepting a seeded offer.** (design doc case 10) (seeded answer) → “Sure.”

The first assistant turn is seeded with this answer, verbatim, so every run starts from the same offer:

> 🐾 Found it! Matt was brought in roughly seven months into **Fiserv**'s 14-month, **$8.5M** white-label card portal program, the shared platform behind branded credit card sites for **2M+** cardholders across **15** financial institutions. The **45-person** globally dispersed team had missed multiple consecutive deadlines, and client stakeholders were threatening contract cancellation. He recovered a Q4 release that was **3 weeks** behind, avoiding **$500K** in penalties, and the program was delivered **3%** under budget with zero critical defects at launch.
>
> Want to hear how he moved that team from 6-month waterfall releases to 2-week sprints?

- "Sure.": delivers the offered thread, how he moved the Fiserv team from 6-month waterfall releases to 2-week sprints, from its story. Fails if it gives a different thread, a different engagement, or a repeat of the seeded answer.
- **Protocol:** A required closing (D9). Both arms get the same seeded text; the PoC also gets the seed's record entry and open offer, which lever 2 has no place for.

**18. Earlier topic competing with the latest.** (design doc case 16) “Tell me about his Norfolk Southern work.” → “Tell me about his RBC work.” → “How long did that take?”
- "Tell me about his RBC work.": a new topic, answered from the RBC stories with no Norfolk Southern carry-over.
- "How long did that take?": RBC's duration from its dates (June 2012 to June 2013, about a year), or a clarifying question between Norfolk Southern and RBC. Fails if it says the duration is not on record, gives Norfolk Southern's six months (the CIC Academy course) or any other Norfolk Southern figure (2019-11 to 2023-09; 2020-01 to 2020-12), or invents precision (days, weeks, an exact month count, or dates the corpus doesn't hold).
- **Protocol:** Scored against RBC's dates (D7). Lever 2 has no dates in context, so it can pass only by clarifying.

**Not in this set:** design doc cases 1, 2, 5, 6 and 11 to 15 (5 and 6 are covered as fixture conversations 1 and 7).

## 4. Scoring

**Rubric, both arms, per turn:** pass or fail against Section 3's expected outcome, applying the fixture's scoring rule, quoted verbatim:

> "Answered" means the correct referent and materially correct facts, not matching the expected wording. Score on correct referent, materially correct facts, honest uncertainty, and contextual continuity; allow natural variation in wording. First turns are scored on Answered and Honest; Remembered context passes unless the answer imports unrelated context. A fact must be backed by a story or the profile: a figure that only the assistant's context asserts fails Honest.

**Protocol:** a turn that sets a new topic (conversation 11's second turn, conversation 18's second turn) is scored like a first turn, plus a Remembered context fail if it carries the earlier topic in.

**Protocol: every turn also fails on any of these:**
- **Remembered context:** it carries the previous topic into a new one, or answers a follow-up about the wrong engagement.
- **Closing (D9):** an inappropriate or unsupported closing, whether rendered by the closing step or written into the answer text. The same rule applies to both arms.
  - Inappropriate: an engage close (Role Match, About Matt, contact, LinkedIn) without an evaluating signal or a contact or résumé request in the visitor's own words; or an offer unrelated to what the visitor asked.
  - Unsupported: an offer the stories can't deliver, or one asserting a fact the stories don't hold.
  - A turn with no closing never fails on the closing, except where Section 3 requires one (conversations 14 to 17).

**Required closings (D9):** scored in conversations 14, 15, 16 and 17 as written in Section 3. Lever 2 has no closing step, so it can pass these only if its answer text happens to carry the close. A fail there is reported as by construction, not as a regression.

**Runs:**
- 10 per case per arm for the judgment-call cases (design doc Section 6): fixture conversations 1, 7, 10, 11 and 12 to 18.
- 5 per case per arm for the rest: fixture conversations 2, 3, 4, 5, 6, 8 and 9.
- At 5 runs, Q45 moved between 3 of 5 and 4 of 5 on identical retrieval.

**Blind:**
- **Packets:** each (case, run) becomes one packet with both arms' full transcripts, labelled A and B. The order is randomized per packet with a fixed seed, and the key is written to a separate file.
- **What a packet shows:** the visitor's turns and each arm's `answer_md` (answer text plus rendered closing). No plan, record, evidence or timing.
- **What the scorer sees:** the packets, Section 3's expected outcomes, Section 4's rules, and the corpus at `dacf2ff` and `data/matt_profile.json` (to check facts), and nothing else.
- **Who scores:** a fresh subagent with no access to the key. Scores are saved per turn with a one-line reason before the key is read. Matt reads the transcripts and can overturn any score.
- **Limitation:** the arms are distinguishable by style. The PoC can clarify and close; lever 2 never closes. Blinding hides the label, not the design.

**Regression:** a turn where the PoC's pass count is below lever 2's on the same turn, per the design doc's gate ("every existing fixture turn at or above the lever 2 arm"). A 1-run difference at 10 runs is within the noise seen at 5. It's reported as a regression all the same, with that note, and not argued away. An over-asking control (conversation 13, and conversation 7's second turn) regresses on any clarifying question in any run.

**Before the live runs (deterministic, in the probe, abort on failure):**
- The fixture file matches `609f903` (`git diff --quiet 609f903 -- tests/fixtures/evaluator_conversations.md`).
- The probe's parser reads all 18 conversations from the fixture: 18 conversations, numbered 1 to 18, each with the visitor turns quoted in the fixture and the expected-answer lines under its number. For conversation 17 it reads the `(seeded answer)` turn and the blockquoted seed, and the seed it gives both arms equals the fixture's text (answer and offer). It prints each conversation's number, title and turns, and aborts on any mismatch.
- Both arms report corpus `dacf2ff` (124 stories), answering model gpt-4o, and the same `SEARCH_TOP_K` and confidence thresholds.
- Every RBC story block the PoC builds contains 2012-06 and 2013-06; no lever 2 block does.
- The seeded turn's text is identical in both arms.

## 5. What gets reported

1. **Per-turn scorecard:** case, turn, lever 2 passes of N, PoC passes of N, a regression flag, and the scorer's one-line reason for each fail.
2. **Full transcripts:** every turn of every run, both arms side by side, on the existing page ([Agy Turn Design PoC](https://claude.ai/artifact/Xf1wxPMELg9XHULitpUtgK)).
   - The PoC side shows its plan (turn_type, action, referents, query, reason), every validator fallback, the record and the closing.
   - The scores sit next to each turn, added after reveal.
3. **Also recorded, not scored:**
   - Validation failures and fallbacks, by count.
   - The planner's action and evidence-path distribution.
   - Latency per call: plan, answer and total, against lever 2's.
   - The PoC's live offer rate outside conversation 17.
4. **Not tested:** the browser check of engage links (conversation 15), cost per turn, and any second model (MATTGPT-282).

Output goes to `probes/output/275/poc_clean_<timestamp>/`: each arm's JSON, the packets, the key, the scores, stdout and stderr.

## Build notes (Oct 10, 2026, found while building the probe)

The approved text above stands. Where the code differs from it, the code was matched to lever 2's frozen build or to Matt's build instruction, as follows. Probe: `probes/probe_275_poc_clean.py` in the frozen worktree (untracked).

- **max_tokens:** Section 2 says 900. Lever 2's `agy_answer()` uses 700, so the PoC's answering call uses 700, and every answer's `finish_reason` is logged.
- **Synthesis:** Section 2 says router synthesis turns behave the same in both arms. In lever 2, a router synthesis turn changes the prompt and the temperature, and its evidence comes from `search_stories` (`agy_answer()` never calls `get_synthesis_stories()`). The PoC's synthesis prompt and temperature come from the router only, as in lever 2. `get_synthesis_stories()` is used only by its `synthesize` action, which is difference 3.
- **Fallback rule removed:** the follow_up-synthesize-with-no-referents fallback in difference 1 never fired in the last PoC run (0 of 48 plans), so it is not built ("no rule that hasn't fired"). The validator checks shape only.
- **Story blocks:** they carry `engagement="<key>"` beside the title, so the closing can name an index key (difference 5).
- **Tools note:** the PoC's TOOLS line says evidence was gathered before answering, in place of lever 2's "call search_stories" note (part of difference 7).

## Amendments (Oct 11, 2026, approved by Matt before the rerun)

1. **Corpus and egress:** the worktree's corpus files come from the run's corpus commit (`5620dfc` for the rerun), and the egress fix (`3d0da24`: Pinecone queries request ids and scores only) is applied in the worktree. Both arms share it. Section 2's `dacf2ff` is replaced by the run's commit.
2. **Sequential:** one process; arms interleaved per (case, run), the order alternating by run number.
3. **Aborts:** the run stops on Pinecone returning None or [], a local fallback (`fallback:pinecone_unavailable`), a failed synthesis theme query, `_degraded_fallback`, or an embed failure (MATTGPT-292). The health check runs before, every 50 turns and after.
4. **MATTGPT-251 extras:** single-turn, 5 runs per arm: real estate, SAP, trading platforms, ROI, gaming, capital markets. The nonsense filter is skipped for them in both arms, since this tree has the pre-MATTGPT-285 rules. Scored on the MATTGPT-251 rules: per-claim supported / contradicted / unsupported; absence answers say "not on record", never "Matt has not worked with X"; trading names Cendian's B2B Trading Networks with no trading-platform claim.
5. **Blinding:** unchanged (A/B packets, key in a separate file, fresh scorers, scores saved before the key is read).

## Run record

- `poc_clean_20261010_093712`: **invalid as a controlled comparison.** Retrieval degraded unevenly mid-run (local fallback on 158 lever 2 turns, 26 PoC turns). Scorecard (PoC 211/305, lever 2 170/305) and artifacts kept as the record of that run; they don't establish which design performs better with healthy retrieval. See `INVALID.md` in the run directory.
- `poc_rerun_20261011_084138` (corpus `5620dfc`, amendments 1 to 5): valid, no aborts. Fixture: PoC 245/305, lever 2 210/305, with 10 turns where the PoC passes fewer runs than lever 2 (c12 t1 0/10 vs 10/10; c09 t3 and t4 2/5 vs 5/5; c12 t2 6/10 vs 10/10; c11 t1 8/10 vs 10/10; five 1-run differences). The PoC does not meet the gate. Extras x1 to x5: lever 2 15/25, PoC 11/25; x6 dropped as a written control. Evidence, post-hoc notes and the regressions as observed: `docs/evidence/MATTGPT-275/poc_rerun_20261011_084138/NOTES.md`.
- `extras_rerun_20261011_103058` (corpus `6ec9aec`, x1 to x5 only, same harness): lever 2 14/25, PoC 11/25. Trading (x3) still 0/5 in both arms after the corpus correction. `docs/evidence/MATTGPT-275/extras_rerun_20261011_103058/NOTES.md`.

## What this test shows

This test shows whether the bundled PoC beats lever 2. It doesn't show which change caused the difference.
