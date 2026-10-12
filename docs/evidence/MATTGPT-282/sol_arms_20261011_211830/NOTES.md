# MATTGPT-282 run 2: four arms on gpt-6.1-sol

Run: Oct 11, 2026, corpus 6ec9aec, fixture 609f903, worktree b55f9ce. One interleaved run, arm order rotated per run:
- poc_4oplan: PoC (fixes rerun 2), planner gpt-4o, answerer Sol medium (the 282 Sol arm; control for the planner change)
- poc_sol: PoC, planner and answerer Sol medium
- poc_sollow: PoC, planner and answerer Sol low
- lever2_sol: lever 2 (send_to_backend), every answering call on Sol medium via a Responses shim behind lever2_client (forced search on round 1 kept; temperature and max_tokens dropped)
Subset approved by Matt: c01, c03, c04, c09, c11, c12 (5 runs; c09 10) and x1 to x5 (5 runs); 130 turns per arm, 520 live turns, no errors, 12 health checks passed. Every Sol call streamed on the Responses API. Scored blind by 5 fresh subagents (four labels per packet, shuffled; fixes2 brief and prompts); all 520 scores saved before the key was read. Probe diff: changes_vs_282.diff.

Reading rule (Matt): c09 has 10 runs and is read as the gate reads it. At 5 runs a turn is "below lever 2" only on a gap of 2 or more; a 1-run gap is flagged as noise and not counted.

Result (gate.json): poc_sol 124/130, lever2_sol 123/130, poc_4oplan 119/130, poc_sollow 119/130.
- poc_sol below lever2_sol: x3 0 vs 3. Ahead: x1 4 vs 1. Equal on every other turn (c12 t2 5 vs 4 is a 1-run difference).
- poc_sollow below lever2_sol: x3 0 vs 3; x1 0 vs 1 is noise.
- poc_4oplan below lever2_sol: c09 t3 7 vs 10, c12 t2 2 vs 4; noise: c03 t2, c12 t1, x3.
- Sol as planner (poc_4oplan vs poc_sol): c09 t3 7 -> 10, c12 t2 2 -> 5; x1 5 -> 4 and x3 2 -> 0.

Observed:
- c09 t3: with the gpt-4o planner, 3 fails (r2, r4 search; r8 answer_from_referent on ACCESS and RBC). Both Sol-planner arms 10/10; lever2_sol 10/10.
- x3: every fail in every arm is rule 3 only (Cendian's webMethods B2B Trading Networks not named); no answer made a trading-platform claim or mislabelled ACCESS. In the PoC arms, gap plans write the closest-work line about JP Morgan ACCESS and never Cendian; Cendian appears only on search answers (poc_4oplan r1, r3; lever2_sol r1, r2, r4).
- x1: the code-rendered gap opening passes whenever the planner chooses gap (all 9 gap plans across the PoC arms pass). The low-effort planner chose search on all 5 x1 runs (and gap on 6 turns in all, vs 20 to 23 in the other PoC arms), and those answers open "Yes, Matt has worked in mortgage lending", a contradicted real-estate claim; lever2_sol does the same in 4 of 5. Lever 2 on gpt-4o scored x1 10/10 in fixes rerun 2 (a different run).
- c12 t2: the poc_4oplan fails are answers ranking Fiserv's 45 above ACCESS's 40+ as the "larger stated team"; the scorer flagged this as a strict reading (a lenient reading passes all five).
- Gap opening: 0 doubled openings and 0 dropped added lines in all arms (all answering on Sol).
- Sol answers contain em dashes ("Yes—Matt has worked..."), which reach visitors after post-processing.

Cost and latency (cost_latency.txt; standard pricing): total $10.09.
- poc_4oplan $0.0200/turn; first visible token median 4.06 s (p90 5.22); whole turn median 9.13 s.
- poc_sol $0.0221/turn; first visible 6.10 s (p90 8.13); whole turn 11.90 s.
- poc_sollow $0.0221/turn; first visible 4.57 s (p90 5.49); whole turn 10.84 s; ~1 reasoning token per call.
- lever2_sol $0.0134/turn (2.06 calls/turn, round 2 largely cached input); first visible 4.13 s (p90 5.74); whole turn 9.35 s.
- First visible token is measured from turn start to the first output delta of the call that produces the visible answer (PoC: after planner and evidence gathering; lever 2: after the forced search round). Production does not stream today.

Limits: 5 runs per turn except c09; one scorer per group; Sol runs at temperature 1.0, so the Sol planner is no longer deterministic (gpt-4o planner ran at 0); comparisons with lever 2 on gpt-4o are across runs.
