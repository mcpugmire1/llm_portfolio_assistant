# MATTGPT-275 rerun: clean PoC vs lever 2

Run: Oct 11, 2026, under docs/working/MATTGPT-275_poc_protocol.md with Matt's five amendments (see the protocol's Amendments). Corpus 5620dfc (124 stories, 46 engagements); fixture 609f903; worktree b55f9ce plus the lever 2 diff and the egress fix (worktree_code_diff.txt). Sequential, one process, arms interleaved per run. 670 live turns, no aborts, no errors; Pinecone health check passed before, every 50 turns and after (15 checks). Scored blind by 7 fresh subagents (scores/), all 670 scores saved before the key (key/) was read.

## Fixture scorecard (305 turns per arm)

Lever 2 210/305, PoC 245/305. A regression is any turn where the PoC passes fewer runs than lever 2 (the protocol's gate); a 1-run difference is within the noise the protocol describes and is listed all the same.

| Turn | Lever 2 | PoC | |
|---|---|---|---|
| c01 t1 | 10/10 | 10/10 |  |
| c01 t2 | 10/10 | 10/10 |  |
| c01 t3 | 10/10 | 9/10 | regression |
| c02 t1 | 5/5 | 5/5 |  |
| c02 t2 | 0/5 | 0/5 |  |
| c03 t1 | 5/5 | 5/5 |  |
| c03 t2 | 4/5 | 4/5 |  |
| c04 t1 | 5/5 | 5/5 |  |
| c04 t2 | 5/5 | 4/5 | regression |
| c04 t3 | 5/5 | 5/5 |  |
| c05 t1 | 5/5 | 5/5 |  |
| c05 t2 | 2/5 | 1/5 | regression |
| c06 t1 | 5/5 | 5/5 |  |
| c06 t2 | 4/5 | 5/5 |  |
| c07 t1 | 10/10 | 10/10 |  |
| c07 t2 | 8/10 | 9/10 |  |
| c08 t1 | 5/5 | 5/5 |  |
| c08 t2 | 5/5 | 4/5 | regression |
| c09 t1 | 5/5 | 5/5 |  |
| c09 t2 | 5/5 | 5/5 |  |
| c09 t3 | 5/5 | 2/5 | regression |
| c09 t4 | 5/5 | 2/5 | regression |
| c10 t1 | 10/10 | 10/10 |  |
| c10 t2 | 0/10 | 8/10 |  |
| c10 t3 | 0/10 | 10/10 |  |
| c11 t1 | 10/10 | 8/10 | regression |
| c11 t2 | 7/10 | 7/10 |  |
| c11 t3 | 0/10 | 8/10 |  |
| c12 t1 | 10/10 | 0/10 | regression |
| c12 t2 | 10/10 | 6/10 | regression |
| c13 t1 | 10/10 | 10/10 |  |
| c13 t2 | 10/10 | 10/10 |  |
| c14 t1 | 0/10 | 8/10 |  |
| c15 t1 | 0/10 | 10/10 |  |
| c16 t1 | 0/10 | 1/10 |  |
| c17 t2 | 0/10 | 4/10 |  |
| c18 t1 | 10/10 | 10/10 |  |
| c18 t2 | 10/10 | 10/10 |  |
| c18 t3 | 0/10 | 10/10 |  |

## MATTGPT-251 extras (5 runs per arm, nonsense filter skipped in both)

| Extra | Lever 2 | PoC |
|---|---|---|
| x1 | 5/5 | 1/5 |
| x2 | 5/5 | 5/5 |
| x3 | 0/5 | 0/5 |
| x4 | 0/5 | 0/5 |
| x5 | 5/5 | 5/5 |

x6 (capital markets) is dropped from the result: Matt, Oct 11, 2026, a written control, not a visitor question. Its scores stay in scores_g7.json. The brief gave the scorers "ACCESS is a capital-markets platform" as a stated fact; Matt corrected that the same day (ACCESS is treasury services and cash management; capital-markets and trading questions get "not on record"). Under the corrected fact all 10 x6 answers fail.

## Post-hoc notes (recorded after the key was read; scores unchanged, per Matt)

Judgment calls the scorers flagged, kept as scored. The other reading, for the record (lever 2 / PoC passes):
- c02 t2, whether the answer must explain the Master's degree: as scored 0/0; lenient 2/0.
- c11 t2, "improved client satisfaction" (in no story) fails Honest: as scored 7/7; not failed 10/10.
- c16, About Matt and LinkedIn both required: as scored 0/1; one pointer enough 0/9.
- c17, any supported offer meets the required closing: as scored 0/4; engage close only 0/0.

The sentence "In active search for a role where building the product engineering organization, establishing the culture, and delivering results are part of the same job" (9 PoC answers) is sourced: MATT_DNA in backend_service.py and the Home hero. The scorers had only the corpus and profile and passed it as a paraphrase; passing was correct.

## Regressions, as observed (diagnosis pending, read-only)

- c12 t1: the planner chose synthesize with no referents; get_synthesis_stories() returned four JP Morgan stories and no Fiserv story in all 10 runs.
- c09 t3/t4: clarify plans (no evidence gathered) whose answers gave content anyway, including an unsourced "team of 40 engineers" for an "access management platform".
- x1: the gap action's search returned no stories; answers named Accredited and Cendant and called the work real estate.
