# MATTGPT-275 fixes rerun: three PoC fixes vs lever 2

Run: Oct 11, 2026, corpus 6ec9aec (124 stories, 46 engagements), fixture 609f903, same harness and guards as poc_rerun_20261011_084138. The PoC arm runs probe_275_poc_clean.py with three fixes (fixes.diff against the frozen probe); lever 2 is unchanged. Subset Matt approved: c01, c03, c04, c05, c08, c09, c11, c12 and extras x1, x2, x3, x5; 10 runs each, both arms; 500 live turns, no errors, 12 health checks passed. Scored blind by 5 fresh subagents; all 500 scores saved before the key was read.

Fixes:
1. clarify: the planner's question is rendered as the answer, with no answering call.
2. gap (option a): if the planner's query finds nothing, retry with the visitor's full question; an empty gap after that answers without MATT_DNA under "Say it isn't on record. You may add only facts from the profile above; nothing else."
3. synthesize with no referents: when the question names 2+ clients (corpus client names plus client aliases), one search per client, filtered to that client, top 3 each.

Mechanics, observed: all 18 clarify plans rendered; c12 t1 evidence held Fiserv and JP Morgan stories in 10 of 10 runs; fix 2's retry found stories on all 47 gap turns, so the empty-gap path never ran.

## Gate (every turn at or above lever 2)

Lever 2 217/250, PoC 204/250. Not met: the PoC is below lever 2 on 8 turns.

| Turn | Lever 2 | PoC | |
|---|---|---|---|
| c01 t1 | 10/10 | 8/10 | below |
| c01 t2 | 10/10 | 10/10 |  |
| c01 t3 | 10/10 | 10/10 |  |
| c03 t1 | 10/10 | 10/10 |  |
| c03 t2 | 10/10 | 0/10 | below |
| c04 t1 | 10/10 | 10/10 |  |
| c04 t2 | 10/10 | 8/10 | below |
| c04 t3 | 10/10 | 9/10 | below |
| c05 t1 | 10/10 | 10/10 |  |
| c05 t2 | 3/10 | 5/10 |  |
| c08 t1 | 10/10 | 10/10 |  |
| c08 t2 | 5/10 | 9/10 |  |
| c09 t1 | 10/10 | 10/10 |  |
| c09 t2 | 10/10 | 10/10 |  |
| c09 t3 | 10/10 | 7/10 | below |
| c09 t4 | 10/10 | 9/10 | below |
| c11 t1 | 10/10 | 9/10 | below |
| c11 t2 | 10/10 | 10/10 |  |
| c11 t3 | 0/10 | 9/10 |  |
| c12 t1 | 10/10 | 10/10 |  |
| c12 t2 | 9/10 | 10/10 |  |
| x1 t1 | 10/10 | 1/10 | below |
| x2 t1 | 10/10 | 10/10 |  |
| x3 t1 | 0/10 | 0/10 |  |
| x5 t1 | 10/10 | 10/10 |  |

## Observed causes of the two large gaps

- c03 t2 ("Give me an example where that didn't work"): the planner chose clarify in 10 of 10 runs; with fix 1 the question is the whole answer, and the protocol allows no clarifying question on this turn. In the frozen run a clarify plan usually answered anyway and passed.
- x1 (real estate): the full-question retry returned 5 stories (including Cendant) in every run, so the gap had evidence and the normal path ran (MATT_DNA, "then what is"). 9 of 10 answers led with Cendant as the answer and did not say real estate is not on record.

## Scorer notes (kept as scored)

- The c11/c12 scorer did not fail vague claims such as "client satisfaction" (the poc_rerun scorer did); both arms here had the same scorer, so the within-run gate is fair, but c11 t2 is not comparable with poc_rerun.
- c09 t4: two runs reported the payments team after a turn 3 that had wrongly used the payments example; passed on turn 4 (the error was scored once, on turn 3). A literal reading would fail them.
- c08 t2: six answers say "data masking and email interception" were added afterward; the story lists them as missing controls and says "corrective controls" after. Passed as a close inference; a strict reading would fail them.
- Three scorers wrote helper scripts one folder above the blind folder (writes only; nothing outside the folder was read).
