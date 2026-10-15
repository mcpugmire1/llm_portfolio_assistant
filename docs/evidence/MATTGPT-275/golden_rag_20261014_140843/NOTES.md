# MATTGPT-275: golden eval on rag_answer() (the last rag_answer() baseline)

Run: Oct 14, 2026, 14:08 to 14:26. HEAD 9b61baf7b8e5fe5c8ab37ece42660be744541af7 plus the working tree (worktree_diff.patch, worktree_status.txt; code as run in as_run/). Corpus and fixture checksums: inputs_sha256.txt.
Files: tests/eval_rag_quality.py, tests/test_agy_behavior.py, tests/test_structural_assertions.py, uncached. Loggers patched for the whole session by golden_plugin.py (log_query, log_offdomain, _log_borderline, _log_router_low_confidence); every rag_answer() call recorded to calls.jsonl.

Result (stdout.txt, junit.xml): 3 failed, 285 passed, 6 skipped in 1056.56s; 274 rag_answer() calls; no tracebacks in stderr.

## TestNoMetaCommentary::test_no_meta_commentary[Q17_meta]
- Query: What are Matt's core themes?
- Assertion: Meta-commentary found: ['highlights his']
- Answer:

    🐾 Here's what connects the dots across Matt's work.
    
    Matt's core themes revolve around Execution & Delivery, Org & Working-Model Transformation, and Talent & Enablement. These themes are evident in his leadership roles and the impact he has made across various industries. At **Accenture**, he built the Cloud Innovation Center from scratch, scaling it to over **150 professionals** and achieving **4x faster product delivery** with zero-defect deployments. This accomplishment highlights his focus on Execution & Delivery, as he consistently drove **\$100M**+ in repeat business through delivery excellence.
    
    In terms of Org & Working-Model Transformation, Matt has a track record of modernizing platforms and transforming engineering cultures. At **Norfolk Southern**, he addressed a quality crisis by implementing test-driven development and agile practices, which resulted in a significant reduction in defects and improved client confidence. His approach to transformation is not just about process change but also about consistent coaching and cultural shifts, ensuring that new practices are deeply embedded within teams.
    
    Talent & Enablement is another key theme in Matt's work. He has developed competency frameworks and transformation roadmaps to help teams transition to product-centric ways of working. By creating tailored training materials and delivering immersive coaching sessions, he has enabled teams to close competency gaps and improve retention rates. His efforts have resulted in high-trust engineering cultures where innovation thrives, as seen in his work at the Cloud Innovation Center.

## TestAgyVoice::test_agy_voice[Q45_voice]
- Query: What evidence shows Matt can operate at Director or VP level?
- Assertion: Agy voice violations: ['Missing #x1F43E emoji']
- Answer:

    At **Accenture**, he built the Cloud Innovation Center from scratch to a team of over **150 professionals**. This team consistently delivered at **4x velocity** with zero-defect deployments, earning over **\$100M** in repeat business through delivery excellence. His approach involved creating high-trust teams grounded in servant leadership and psychological safety, which fostered an environment where teams could thrive and deliver exceptional results.
    
    In his role as Director at **Capital One**, Matt faced the challenge of scaling development capacity to meet Federal Reserve Board-mandated compliance updates. By embedding Lean XP, pairing, and automation, his teams delivered defect-free code at **4x** the output of internal teams. This not only improved development efficiency but also secured additional engagements, proving the strategic impact of modern engineering practices.
    
    At **JP Morgan Chase**, Matt was brought in to stabilize and deliver the Asset Management Salesforce rollout across **12 countries**. He aligned regional stakeholders on a single roadmap, established governance across workstreams, and navigated complex compliance requirements. As a result, the platform was delivered on schedule with no scope renegotiations, leading to a **3x** increase in tracked sales opportunities. He took over a **\$8.5M** white-label card portal project in crisis and stabilized delivery within three months. His leadership avoided **\$500K** in penalties and delivered the program **3%** under budget with zero critical defects.

## Known misattribution (no test checks it)
- Q45 ("What evidence shows Matt can operate at Director or VP level?", the TestAgyVoice answer above): its last paragraph is under JP Morgan Chase, then says "He took over a **\$8.5M** white-label card portal project in crisis and stabilized delivery within three months. His leadership avoided **\$500K** in penalties and delivered the program **3%** under budget with zero critical defects." Those are Fiserv's card-portal figures (the Fiserv stories), credited to JP Morgan Chase. This is what production's old pipeline does today; no test in these three files checks client attribution in this answer. The agy_answer() run on the same tests shows whether the new path fixes it.

## TestCorpusLiterals::test_every_literal_is_allowed
- No model call. Fails on HEAD too: run at d04396b in the pre-fix worktree, the same 13 lines of output (diff empty). Not caused by this change.
