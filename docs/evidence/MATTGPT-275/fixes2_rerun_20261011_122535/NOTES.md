# MATTGPT-275 fixes rerun 2: gap opening rendered by code, clarify limited

Run: Oct 11, 2026, corpus 6ec9aec, fixture 609f903, same harness and guards. PoC arm: fixes 1 to 3 (fixes_rerun_20261011_110055) plus two changes (changes_vs_fixes1.diff):
1. gap: code renders "That isn't in Matt's stories." as the opening; the answering call runs without MATT_DNA and may add only a line starting "The closest work on record is" (stories) or profile facts with their [[profile:...]] markers; other text is dropped and logged.
2. clarify: allowed only when the latest turn used 2+ distinct engagements and the question matches REFERS_BACK; otherwise answer_from_referent on the latest turn's engagements, or search if it used none.
Lever 2 unchanged. Subset: c01, c03, c04, c05, c08, c09, c11, c12 and x1 to x5, 10 runs each, both arms; 520 live turns, no errors, 12 health checks passed. Scored blind by 5 fresh subagents; all 520 scores saved before the key was read.

Gate: lever 2 218/260, PoC 208/260; PoC below lever 2 on 7 turns (c01 t3, c03 t2, c04 t2, c08 t1, c08 t2, c09 t3, c09 t4). x1 real estate 10/10 (was 1/10). c04 t2 PMP 0/10 (was 8/10).

Gap coverage (gap_coverage.json, judged by a separate subagent against the whole corpus and the profile): 43 PoC gap plans (PMP 10, real estate 10, SAP 10, trading 3, gaming 10); 0 covered by a story, 0 covered only by the profile; all 43 true gaps.

Known limit, REFERS_BACK: it is a word list ("that/this/those/these" + project, engagement, program, one, work, client, team, role; "the team/project/engagement/program"; "there"; "which one/was/is/were"; "both"). It misses other ways of referring back, e.g. "How long did that take?", "how big was his teams", "What went wrong?", so clarify is never allowed on those wordings.

Observed defects:
- The model repeats the code-rendered opening at the start of its own text in 17 answers. When that text also cites a profile marker it is kept, and the opening appears twice; otherwise the whole added text is dropped because it doesn't start with the closest-work prefix (21 drops), leaving the bare opening.
- c04 t2: the model's added line was "The closest work on record is his role in establishing PMOs..." in every run (the PMO pivot the fixture names as a fail); no run listed the profile's certifications.
- c03 t2: disallowed clarifies fell back to search (5 runs, evidence led by the MattGPT "flattering chatbot" story, used as the leadership-failure example) or to answer_from_referent on CIC/career engagements (3 runs, no failure story in that evidence); only synthesize plans (2) passed.
- c09 t3/t4: in r7 to r9 the planner chose answer_from_referent on JP Morgan ACCESS and RBC for "Give me an example." (payments carried into the leadership example), then reported the ACCESS team.
