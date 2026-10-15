# MATTGPT-275: golden eval on agy_answer(), paired with the rag_answer() baseline

Run: Oct 14, 2026, 15:09 to 16:09. HEAD plus the working tree (worktree_diff.patch, worktree_status.txt; code as run in as_run/). Same three files as the baseline (docs/evidence/MATTGPT-275/golden_rag_20261014_140843/), migrated to agy_answer() with the rag_fn adapter; test_agy_behavior.py's four _generate_agy_response() tests ported with search_stories returning the stories they used to pass; test_synthesis_pool_size deleted. Uncached; loggers patched by golden_plugin.py (GOLDEN_SIDE=agy); every agy_answer() call recorded to calls.jsonl, the four ported tests included.

Result (stdout.txt, junit.xml): 9 failed, 281 passed, 3 skipped in 3559.32s; 280 agy_answer() calls; no tracebacks in stderr. paired_review.json pairs every test with its baseline outcome and both answers.

Pairs (baseline -> agy): passed->passed 276, passed->failed 8, failed->passed 2, skipped->passed 3, skipped->skipped 3, failed->failed 1 (TestCorpusLiterals, fails on HEAD too), passed->absent 1 (test_synthesis_pool_size, deleted).

Per-call time: rag_answer() median 3.8 s (p90 5.0); agy_answer() median 12.9 s (p90 17.1), test overhead included.

Answers without the paw: rag_answer() 1 of 249 answered; agy_answer() 9 of 261.

Q45 misattribution (baseline NOTES): agy_answer()'s Q45 answer does not mention the Fiserv $8.5M figures; the misattribution is not present.

"Where does Matt live?" (Q59): rag_answer() rejected it as low_confidence in all four tests (empty answer); agy_answer() answers "Matt lives in Atlanta, GA." The same low_confidence gate blocked the two garbage queries on rag_answer(); agy_answer() has no such gate, so they reach the model.
