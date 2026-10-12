# MATTGPT-282 probe: PoC answering model, gpt-4o vs gpt-6.1-sol

Run: Oct 11, 2026, corpus 6ec9aec, fixture 609f903. Both arms are the PoC from fixes rerun 2 (frozen e4426f5); the only change is the answering call (changes_vs_fixes2.diff). Planner gpt-4o in both arms. Subset: c03, c04, c09, x3, x4, plus c12 and x1 as no-regress controls; 10 runs each, arms interleaved; 280 live turns, no errors, 8 health checks passed. Scored blind by 4 fresh subagents with the fixes2 brief and prompts; all 280 scores saved before the key was read.

Resolved models (response.model, every call):
- gpt-4o arm: answering gpt-4o-2024-08-06 (138 calls; 2 clarify turns rendered by code, no call), Chat Completions; planner gpt-4o-2024-08-06.
- Sol arm: answering gpt-6.1-sol (140 calls), Responses API, reasoning effort medium (the default); planner gpt-4o-2024-08-06.

API path: gpt-6.1-sol on Chat Completions rejects function tools unless reasoning_effort is "none", and rejects "none"; it rejects max_tokens and temperature on both paths (temperature fixed at 1.0). So the Sol arm uses the Responses API: messages converted to input items, tool_calls/tool messages to function_call/function_call_output, tools flattened with strict false, max_output_tokens 4000 (reasoning tokens count against it). The gpt-4o arm keeps temperature 0.2/0.4 and max_tokens 700. Production answers only through Chat Completions with temperature, so a production switch is a code change, not a constant.

Cost and latency (cost_summary.py; standard pricing, $/M tokens: gpt-4o 2.50 input, 1.25 cached, 10 output; gpt-6.1-sol 2.00, 0.10, 10):
- gpt-4o arm: $0.0227 per turn (answering $0.0181, planner $0.0049); answering call median 1.88 s, p90 2.96 s; whole turn mean 3.52 s.
- Sol arm: $0.0193 per turn (answering $0.0142, planner $0.0051); answering call median 7.14 s, p90 10.73 s; whole turn mean 9.17 s. Mean output 330 tokens, 50 of them reasoning (max 194).
- Time to first token was not measured (calls are not streamed); the latencies are whole-call.

Result (gate.json): gpt-4o 94/140, Sol 131/140. Sol is not below gpt-4o on any turn.
- c03 t2: 1 vs 9. c04 t2: 0 vs 10. x3: 0 vs 7. x4: 0 vs 10. c09 t4: 7 vs 8. c12 t1: 9 vs 10.
- Equal: c03 t1, c04 t1, c04 t3, c09 t1 to t3 (c09 t3 7 vs 7), c12 t2, x1 (10 vs 10).
- The gpt-4o arm reproduces fixes rerun 2 on the shared turns (c03 t2 1 vs 2, c04 t2 0 vs 0, c09 t3 7 vs 6, x3 0 vs 0, x4 0 vs 0, x1 10 vs 10).

Observed:
- Gap path: gpt-4o repeated the code-rendered opening in its own text again (13 drops leaving a bare opening, 8 doubled openings). Sol: 0 drops, 0 bare, 0 doubled. On c04 t2 every Sol answer said no PMP and listed the profile's certifications (kept by the profile-marker rule, not the closest-work prefix).
- c03 t2: the planner's fallbacks were the same mix in both arms (answer_from_referent 6 vs 7); Sol passed 9 of 10 from that evidence, gpt-4o 1 of 10 (scorer: reframed successes as failures).
- c09 t3: both 7/10. The gpt-4o planner chose JP Morgan ACCESS/RBC referents in some runs of both arms (gpt-4o arm r6 to r8; Sol arm r5, r9), and those Sol runs carried payments in; Sol's third fail (r6) used the Liquid Studio prototyping story, not an example of the style. Planner referent drift is not touched by the answering model.
- x3: Sol's 3 fails (r2, r3, r7) all said trading isn't on record and labelled ACCESS correctly; each failed only rule 3, not naming Cendian's webMethods B2B Trading Networks. No Sol x3 answer made a trading-platform claim.

Limits: one run of 10 per turn; one scorer per group; Sol differs from gpt-4o in temperature (fixed 1.0), reasoning and output cap as well as model, so the result is the model as it can be called, not the model alone. Lever 2 was not in this run; comparisons with lever 2 are across runs.
