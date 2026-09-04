# Changelog

Shipped work for the MattGPT project, organized by month. For open work, see `BACKLOG.md`. For architectural decisions, see `docs/ADR.md`.

---

## September 2026

### My Work

**September 2, 2026 — personal branch HARD_ACCEPT gate + My Work zero-result routing (MATTGPT-234)** -- `4c3cde3`, `a2e7e7a`, `824e59e`

Generic off-topic queries (bananas, world series) were scoring low on the `personal` family (0.223) and hitting the personal hard-stop before `overlap:0.00` could run, returning "I'm focused on Matt's professional experience" -- copy that implied the query was personal rather than off-topic. Fix (same one-line pattern as MATTGPT-219): HARD_ACCEPT gate at both personal branch call sites. Score 0.223 does not clear 0.80, so the hard-stop does not fire and the query falls through to the overlap gate. Rejection eval run before and after; all eight real personal queries still clear 0.80; no legitimate rejections lifted.

Second scope item in the same ticket: after the gate fix, off-topic queries reaching `confidence == "none"` at My Work PATH 1b (~line 1130) were landing on `_render_confidence_banner` with an empty grid and a phantom cell rather than on `render_no_match_banner` with the browsable corpus underneath. Routed PATH 1b through the standard rejection renderer; default corpus now renders beneath the banner. Known interim: low-confidence fell-through queries see trail copy ("I picked up a scent but lost the trail") over 112 stories -- correct structure, interim copy. MATTGPT-239 splits the `low_confidence` reason and assigns the right copy to each case.

Three-commit Green: `4c3cde3` (helper impl + Ask Agy wiring), `a2e7e7a` (explore_stories.py extraction + PATH 1b routing + filter suppression), `824e59e` (chip unlock).

---

**September 2, 2026 — My Work fallback banner made honest during Pinecone downtime (MATTGPT-230)** -- `013d9ac`

Query log verified a 3:37 upstream outage window on September 1 (15:47:18 to 15:50:55): "why should i hire matt" returned zero results with "Matt may not have worked with this client or topic." The fallback was indistinguishable from a correct no-results response. Fix: preserved the `None` vs `[]` distinction that `pinecone_semantic_search` already returns but `rag_service.py:81` was flattening away. `None` (Pinecone failed) vs `[]` (ran, found nothing) now routes two honest banner shapes off the same branch. Fallback with rows: breather banner above keyword results ("🐾 I need a quick breather: please try again in a moment!"); "Showing closest matches, relevance may be low" removed. Fallback with nothing: breather only; story count, grid, and affordance lines suppressed so the page does not confidently describe an empty result set. Red `b8c6caa`; Green `013d9ac`. MATTGPT-222 Alarm 1 will read the same signal to fire an operational alarm on upstream failure.

---

**September 2, 2026 — Streamlit theme defaults coverage: focus borders, wrapper backgrounds, widget labels (MATTGPT-242)** -- `3adf12d`

`config.toml`'s `[theme]` block was removed September 2 to fix a font regression, dropping the app back to Streamlit defaults (`#FF4B4B` focus borders, `#F0F2F6` wrapper backgrounds, `#31333F` widget labels). Fix in `ui/styles/global_styles.py`: `div[data-baseweb="input"]:focus-within` and `div[data-baseweb="select"] > div:focus-within` get `border-color: var(--accent-purple)` and matching `box-shadow`; selectbox wrappers get `--bg-surface`; widget labels and values get `--text-primary`. Rules placed in both `:root` blocks (light and dark). `div[data-baseweb="base-input"]` deliberately left uncovered -- it tracks Streamlit's secondary background and is the right behavior.

Verified in both modes via computed-style scan of 401 visible elements under `[data-testid="stApp"]`: zero `#FF4B4B`, `#F0F2F6`, or `#31333F` hits in light or dark. Focus border resolves `#8B5CF6` (`--accent-purple`) on real click in both themes. Dark mode: selects and input wrapper `#262633` (`--bg-surface`), labels `#E5E7EB` (`--text-primary`). Light mode: selects and input wrapper `#F9FAFB`, labels `#1F2937`. `body.dark-theme` confirmed: one element, all descendants inherit dark tokens.

Two findings added to MATTGPT-226 scope: `section[data-testid="stAppViewContainer"]` matches nothing; the block at `global_styles.py:330-350` is inert. Token reads must come from `document.body`, not `documentElement` (`getComputedStyle(document.documentElement)` reports `:root` light values in both themes).

---

**September 2, 2026 — Surface project count as a distinct metric across landing pages; hero stat restructure (MATTGPT-144)** -- `c6b6786`

Full inventory found four buckets. Bucket A (4 broken filter-banner sites counting stories under a "projects" label) shipped earlier in the session by Matt. Bucket B (Project as Pinecone/JSONL entity name) and Bucket C (env/config) untouched. Bucket D (visitor-facing copy using "projects" as a synonym for stories) resolved by surfacing the missing metric rather than renaming.

`utils/landing_cards.py`: card dict now carries `project_count` as a distinct count from story count (`len({s["Project"] for s in group})`). `banking_landing.py`: renamed `total_projects` to `total_stories` (variable now matches what it measures); added `num_projects` (distinct Project values across banking stories); restored `num_clients`; deleted dead capabilities block; header now reads "N stories across M projects and C clients" with inline pluralization for all three. `cross_industry_landing.py`: same rename; added `num_projects`; client count deliberately absent because cross-industry stories attribute to anonymized placeholders -- a filtered derivation would surface the anonymization as a wrong-looking number. Card meta elision rule (both pages): 1 story shows "1 story"; N stories where projects == stories shows "N stories" (plus client count if >1); N stories where projects < stories shows "N projects · N stories" (plus client count if >1).

`hero.py`: reshuffled hand-authored career stats to drop "Projects Delivered" (was story count under a project-count label, same category of error as the landing pages). Replaced with "150+ Team Scaled" and "$100M+ Repeat Business." Rule: hand-authored career claims stay editorial; corpus-derived stats must match their label.

`tests/unit/test_landing_cards.py`: fixtures gain a `Project` field on every story so `build_landing_cards`'s new `project_count` derivation does not KeyError. 10/10 pass.

---

**September 2, 2026 — Below-SOFT_ACCEPT router logging probe (MATTGPT-238)** -- `a43ee80`

`_log_borderline` in `services/semantic_router.py` was widened to capture decisions below SOFT_ACCEPT (0.40) in addition to the 0.40-0.80 middle band already logged. Probed 10 queries: junk topped at 0.255, legitimate queries started at 0.326. Value as shipped: local development tool only. Streamlit Cloud's container filesystem is ephemeral; any CSV written in production is unreadable by the next request. The probe established the 0.07 gap and the candidate 0.30 threshold; it did not produce a production data surface. Production router score distribution requires MATTGPT-223 (Sheet integration). MATTGPT-239's confidence-floor threshold decision blocks on -223, not on this ticket.

---

**September 2, 2026 — My Work detail-pane empty state: dashed slot replaces paw banner (MATTGPT-237)** -- `31f20c9`

`story_detail.py:261` previously rendered "🐾 Check a row or click a card above to view details." as a banner with an accent stripe and square corners. Three problems: Agy's voice used for furniture, "or click a card" stale in Table view, and the icon-margin span and corner radius that were fixed at the other five banner sites were never applied here. Replaced with a 140px dashed empty-state slot (1px dashed `--border-color`, 8px border-radius, centered 15px `--text-secondary` text: "Select a story above to read the full detail"). Purple rule above the detail region removed from the same file -- the slot already separates grid from footer. Mockup settled September 2 (option 1b); shipped values 140px / 15px / `--text-secondary` approved against live grid, differing from the 200px / 14px / `--text-muted` mockup defaults.

---

**September 1, 2026 — Explore Stories rejection no longer blanks the browsing context (MATTGPT-224)** -- `92370b3`

`st.stop()` in both rejection branches of `explore_stories.py` halted execution before the story grid rendered (~line 1373). A single off-topic query replaced 123 browsable stories with a one-line banner above ~900px of white space -- no grid, no pagination, no escape except retyping. Because `render_no_match_banner` suppresses chips in the "explore" context, there was nothing else on screen either. Fix: removed both `st.stop()` calls. The banner renders; the grid renders underneath with filter state intact. Visitor sees the rejection message above work they can still browse.

Eight-phase production shakeout confirmed September 1, 2026. Red commit `fbcbb7e`; reverted incomplete Green attempt `664dd03`, `841a961`; final Green `92370b3`.

---

## August 2026

### Ask Agy

**August 31, 2026 — Landing page chat input border fixed; dead `.main` selector audit filed (MATTGPT-225, MATTGPT-226; also closes MATTGPT-126)**

Root cause (MATTGPT-225): Streamlit's emotion atomic classes `.st-bz` and `.st-c2` migrated onto the `<input>` element itself on a version bump. An existing CSS rule `.st-key-landing_input .st-bz, .st-c2 { border-*-color: transparent }` -- written to strip BaseWeb wrapper chrome -- matched the input and overrode the intended `2px solid var(--border-color)` border at higher specificity. Computed border color was `rgba(0,0,0,0)`: width present, color transparent.

Fix: deleted the hashed selector group; replaced with stable `data-baseweb` selectors for wrapper chrome suppression and `div[data-testid="stTextInput"] input` for the border rule. Shakeout confirmed six-of-six: amex (3 American Express stories, Virtual Payments Platform narrative), AT&T (Network Engineering Platform + Order Management both cited), Norfolk Southern (revenue modernization, CIC Academy, mainframe hybrid, microservices all threaded), on-call rotations (reached JPM Dynamics stabilization + AT&T CRM incident response; LLM surfaced adjacent operational-continuity work rather than hedging with "not explicitly mentioned"), raspberry pi (Liquid Studio connected-devices, robotic bartender and container-breach callouts), retail (correctly hard-stops at 0.835, above HARD_ACCEPT). No unexpected regressions.

MATTGPT-226 filed alongside: the diagnosis exposed 31 dead `.main`-anchored selectors (~299 declarations) in `ui/styles/` that match zero DOM elements since the `.main → .stMain` refactor. Silent now but misled the -225 investigation. Audit and guard planned.

---

**August 30, 2026 — Score gate: out_of_scope rejection now requires HARD_ACCEPT; five answerable queries restored (MATTGPT-219)** -- `b8bd59b`

`backend_service.py:1777` fired the "I don't have experience in that industry" hard stop for any query classified as `out_of_scope`, regardless of confidence. Five queries were failing live: "Tell me about Matt's amex work" (0.696, failing since 2026-03-24 -- five months), "Tell me about Matt's AT&T work" (0.666), "Tell me about Matt's Norfolk Southern work" (0.624), "Has Matt run on-call rotations?" (0.546), and "Tell me about Matt's experience with raspberry pi" (0.611). None cleared the 0.80 `HARD_ACCEPT` threshold. The rejection ignored its own confidence.

Fix: do not fire the rejection unless the score clears `HARD_ACCEPT`. One condition, no taxonomy change. Three xfailed tests (amex, AT&T, Norfolk Southern) go XPASS with this commit. Alarm 3 in MATTGPT-222 is now covered by this gate.

Log context: across twelve months of production, eight visitor questions the corpus could have answered and did not. Six were fixed by targeted work before August 30. The remaining two were these score gate cases.

Known limitation (no ticket): "Tell me more about the Pivotal Labs partnership" retrieves cleanly at 0.423 and returns a fluent paragraph about Accenture's Georgia Tech innovation hub. It never fabricates a Pivotal relationship, and it never says it does not have one. Pivotal is a deliberate corpus gap. The answer is confidently non-responsive -- a third category, not a routing bug and not fixable by a threshold.

---

**August 30, 2026 — Router topical taxonomy inventory complete; three-commit remediation plan documented (MATTGPT-220)**

The router's 15 anchor families were inventoried against their actual consumers. Finding: 9 of 11 topical families serve only two set-membership tests (`_PN_EXCLUDED_FAMILIES` and `SUBSTITUTION_FAMILIES`), and three reach nothing at all. No branch reads a topical family label for its topic. Both set memberships proxy for questions the code never asks directly: is this query about the work, or about who Matt is?

Remediation plan (three commits, handed to Code): (1) delete the 3 inert families (`leadership`, `stakeholders`, `innovation`); (2) rewire `_PN_EXCLUDED_FAMILIES` to an entity-detection rule and `SUBSTITUTION_FAMILIES` to the same or unconditional, measured by `probe_163_substitution_impact.py`; (3) remove the 6 topic-axis families after replay diff confirms safe redistribution. Anchors surviving: `background`, `behavioral`, `synthesis`, `narrative`, `personal`, `out_of_scope` -- the query-shape axis, legitimately hand-maintained.

Inventory finding also exposed MATTGPT-219's true fix: the score gate, not the taxonomy. Logged separately.

---

**August 30, 2026 — "Why hire Matt?" synthesis pool restored; Title soft-filter ported to `get_synthesis_stories` (MATTGPT-218)** -- `9395a68`, `3c5d00a`, `1633ae4`, `ffac391`, `040b785`

`f1285f1` (Jan 30, 2026) added Title-entity detection and made `rag_answer` treat a Title match as a soft filter: pin the story, keep the pool. `get_synthesis_stories` was not updated at the time; it treated Title like Client and applied it as a hard per-theme filter. The bug was latent until Feb 3 when "Why Hire Matt?" was added to the corpus. From that point, the query "Why hire Matt?" matched the substring and collapsed the synthesis pool to one story. "Why should I hire Matt" (no substring match) continued to return a normal 21-story pool. Same code, different phrasing.

Fix: ported the soft-filter case from `rag_answer` into `get_synthesis_stories` so both paths apply the same principle -- scope the search, do not reject the query. `pool_size` also pinned in the `rag_answer` return dict. Q65 ("Why hire Matt?") added to the eval suite.

`9395a68` (Red) and `3c5d00a` (Green): Bucket A conversion prep. Pinned four retrieval observables in the `rag_answer` return dict so test suites can assert on router decisions without proxying through LLM-response text: `intent_family` (router family, or None if router did not run), `entity_match` (detected entity, or None), `confidence` (router score), and `pool_size` (stories reaching the LLM). `TestRagAnswerRetrievalObservables` added at `9395a68`; fields populated in all code paths at `3c5d00a`.

---

**August 28, 2026 — Embedding failure now surfaces correct API error message instead of no-match banner (MATTGPT-162)** -- `e4ddad3`, `d2216c0`

`_embed` in `services/pinecone_service.py` previously caught OpenAI failures and returned a null 1536-dim vector, which reached Pinecone as a real query, produced `pool_size=115` with `top_score=0.000`, and fired `[QUERY_REJECTED] reason=low_pinecone`. Visitors saw the no-match banner ("I could not find anything") when the actual failure was an upstream API outage.

`_embed` now propagates the OpenAI exception. Narrow catches at three call sites set `st.session_state["__embed_failure__"] = True` and return the empty-shape signal: `pinecone_semantic_search` (before Pinecone is called); `get_synthesis_stories` query embed (line 518); and `get_synthesis_stories` theme embed (line 522, previously uncovered -- the pre-existing theme `try/except` started at line 524, after the embed call). A post-`executor.map` check was also added so callers outside `rag_answer` cannot silently consume partial results when one theme's embed raised.

`rag_answer` pops `__embed_failure__` immediately after `semantic_search` returns and again after `get_synthesis_stories`, short-circuiting to the existing January "quick breather" API error response. Pop, not read -- the flag cannot leak into the next query as a false error. Pinecone-side failures continue to return `None` without setting the flag, remaining distinct from embed failures.

Call sites examined, no change made: `probe_assessor.py:96` uses `_embed`; exception now propagates and crashes the probe run loudly (intended -- silent zero-vector probes were producing meaningless rankings). `build_custom_embeddings.py` does not use `_embed`; uses its own `get_openai_embeddings`, not affected.

`d2216c0`: eval sweep owed by MATTGPT-163 (Aug 27 behavior change without corresponding eval update). Q60 moved to `blocked` expected behavior; `blocked` framework support added; `GRACEFUL_REDIRECT_PHRASES` extracted to module-level constant; stale "retail"-hardcoded assertion message fixed. Eval: 70/70 (up from 69/70).

---

**August 26-27, 2026 — Unit test gate added to pre-push hook and CI; hermetic suite; router refactor (MATTGPT-216)** -- `86e114f`, `6c01218`, `646b4da`, `8d1f4ce`, `332b772`

Five-commit scope. `86e114f`: local pre-push hook (`.pre-commit-config.yaml` local stage) added to run `python -m pytest tests/unit/ -q` on push; xfail markers applied to the 5 remaining known-failure tests so they register as expected rather than silently degrading. Hook install is opt-in per clone: `pre-commit install --hook-type pre-push`. `6c01218`: hermetic unit suite (network calls stubbed so tests pass without live credentials), router refactor extracting `_classify_embedding` as a named "network boundary" helper, GitHub Actions workflow (`.github/workflows/test.yml`) enforcing the same gate on every push to main, and a bare-mode config fix uncovered during hermeticity work. Hermetic run: 362 passed, 5 xfailed, 2.23s. `646b4da`: CI fix -- added `requirements-dev.txt` install step so pytest is available in the workflow (requirements.txt is runtime only). `8d1f4ce`: made suite genuinely hermetic by moving module-load side effects out of scope; introduced `network` pytest marker so tests requiring live credentials are excluded without being deleted; widened hook scope to `tests/unit/ tests/integration/ -m "not network"` (safe because the marker gates the network-bound tests). `332b772`: trimmed CI cold-cache install from ~2m to <20s via `requirements-ci.txt` (stripped torch/CUDA/faiss/nvidia wheels not needed for unit tests).

Architecture Sync candidates for Code: two-class split in `_init_pinecone()` (misconfiguration raises at startup, runtime failure returns None); `_classify_embedding` extraction as a "network boundary" pattern for future router work.

---

**August 26, 2026 — Key Metrics sidebar bogus renders fixed; metric detection consolidated to METRIC_RX (MATTGPT-215)** -- `402ff30`, `099e6ee`

Replaced the sidebar's inline metric heuristic in `story_detail.py:641-668` with `METRIC_RX` from `utils/formatting.py`. All five failure categories resolved: Cendian bogus render eliminated (bare-x false positive); JP Morgan ACCESS 2011 no longer surfaces as a metric (year-as-metric); value precision preserved for `$100M+` and `4X` (currency, multipliers, decimals now captured); counted nouns ("15+ Fortune 500 engagements") no longer trigger (no metric marker). Label truncation fixed with word-boundary truncation and leading `- ` strip. Range display (`3-4x` → `4x`) acceptable per ticket.

Consolidation: `story_has_metric` in `ui/pages/ask_mattgpt/utils.py` deleted -- zero production callers confirmed. `METRIC_RX` in `utils/formatting.py` is now the single source of truth for metric detection across the codebase. Downstream behavior shift: time-duration inputs ("3 months") no longer count as metrics; no user-facing impact because the deleted function had no callers. 12 unit tests for `_extract_metric_display` at `402ff30`.

Verified in production: Cendian section absent (no real metric); JP Morgan ACCESS 2011 eliminated; CIC positive cases render `$100M+` and `4X` with full precision and clean word-boundary labels.

---

**August 26, 2026 — Personal-query guard false positive fixed; professional org questions now route correctly (MATTGPT-163)** -- `9a05af0`

Two bugs fixed. (1) "How many direct reports did Matt have" scored 0.616 / personal and was blocked. Fix A1 added five team_scaling anchors carrying "Matt" in the anchor text; the query now scores 1.000 / team_scaling and answers with the 11-13 direct reports and the flat two-layer structure. (2) "How much money did Matt make at Accenture" scored 0.789 / narrative and was reaching retrieval. Fix B added two personal_compensation patterns to `nonsense_filters.jsonl`: bare compensation nouns, and a "how much money" plus earning-verb idiom bounded to a 25-character gap so it does not catch "how much money did Matt save the client." The query now blocks via is_nonsense. Verified in production after push.

Methodology finding (August 26, 2026): The salary bug only reproduced on the ticket's full-form string. "How much money did Matt make" (shorter form) scored 0.921 personal and blocked correctly -- testing that form would have closed the ticket while the bug stayed live. The router embeds the exact string; a few words changes the measurement. Any router work needs the verbatim failing query, not a paraphrase.

`probe_163_substitution_impact.py` committed as `b9cd2ef` -- measures substitution impact across five queries (Jaccard 0.25 to 0.67). Re-runnable benchmark for MATTGPT-077 Phase 2/Phase 3.

---

**August 26, 2026 — Story detail sidebar: Core Competencies as wrapping pills; Export tag cap removed (MATTGPT-212)** -- `a653b05`

Core Competencies section in `story_detail.py` rendered as a single-column list with no cap; the Cendian story's 28 competencies pushed the sidebar to ~900px. Replaced with a flex wrapping pill container using outlined pills (outlined rather than filled to stay visually distinct from `public_tags`). Two new design tokens in `global_styles.py`: `--pill-outline-border` and `--pill-outline-text`, with separate light/dark values. Design deviation from ticket spec: light-mode `--pill-outline-text` shipped as `#6B7280` (matching `--text-secondary`) instead of the specified `#4B5563`. Production filled pills are grey-on-grey-tint, not purple as the 3E mock implied; using the same text color as the filled variant would have produced no fill/outline hierarchy. Also removed `[:10]` tag cap in the Export/print render (`story_detail.py:372`): the cap silently dropped the tail of the alphabet from a document that reads as complete, with no ellipsis or count. `test_global_styles_no_cdn` (asserting a feature removed in `2cbe5f5`) deleted in `e307d6d`; remaining 5 tests in `test_base64_precomputation.py` verified still guarding live base64 embedding.

---

**August 26, 2026 — Tag generator: skip-unchanged partition, discovery-vocabulary prompt, post-processing normalization, backup defect fixed (MATTGPT-072, MATTGPT-211)** -- `3bb3691`

MATTGPT-072: Four changes shipped together. (1) Skip-unchanged partition: `_prompt_view` is now the single source of truth for LLM inputs; when a story's prompt-relevant fields hash to the same value as the prior run, the API call is skipped and existing tags are copied. Cost drops from ~$0.36 (full corpus) to $0.00 when nothing changed. Partition categories recorded at partition time: no prior tags / Excel cleared / content changed. (2) Discovery-vocabulary system prompt: tags are asserted as search terms a reader might type, not capability claims. Capability is captured separately in Competencies. `maxItems=15` enforced via JSON schema with `strict:true`. (3) Post-processing normalization applied to all tags from both Excel and LLM: acronym-parenthetical stripping, title-case with small-word rule (and/or/the/a/an/of/for/in/to/with lowercased except when first token; applies to hyphen and slash segments), case-insensitive dedup preferring uppercase-heavy variant. (4) Excel-authoritative for `public_tags`: removed the preserve-on-blank rule in `_merge_with_existing` (blank Excel now produces blank JSONL); removed `public_tags` from the diff-loop exclusion so changes appear in the ingest report.

MATTGPT-211: Backup step at `generate_public_tags.py:184` was calling `shutil.copy(INPUT_FILE, backup_file)` -- copying `echo_star_stories.jsonl` under a filename that implied it was snapshotting the NLP output. Fixed: backup source is now `OUTPUT_FILE` (`echo_star_stories_nlp.jsonl`). Existence guard added for first runs when no prior output exists. Every previous run had been destroying the prior NLP state with no recoverable snapshot.

Architecture sync candidates (Code to document in ARCHITECTURE.md from commit range): skip-unchanged partition and `_prompt_view` as LLM input source of truth; discovery-vocabulary framing for `public_tags`; post-processing normalization pipeline; Excel-authoritative ingest behavior for `public_tags`. ARCHITECTURE.md also has an unstaged modification predating this ticket; separate question whether to fold into the same sync pass.

---

**August 24, 2026 — Career-shaped query retrieval fixed for broad queries; Case B decided against (MATTGPT-208)** -- `75e3be5`, `4309b38`

Case A (broad career queries, no temporal marker): SEARCH_TOP_K raised from 10 to 25 (`75e3be5`). `diversify_results` gained a `family="background"` branch that groups by Era instead of Client, with a kind cap of at most one Professional Narrative story and at most one Independent Project story (`4309b38`). Ten unit tests. Eval 70/70 at push gate. Before: "tell me about Matt's career" returned 2 distinct eras, 6 of 7 slots from Technical Foundations, 4 of those WellFound engagements under different Client values. After: 5 distinct eras in the first five, three engagement stories, one positioning anchor.

Case B (chronology queries with temporal marker) decided against. Three reasons: (1) Correctness already handled -- "what did Matt do before Accenture" returns the right answer today from MATT_DNA Career Arc rows, not retrieval; verified in production August 24. (2) Fix would undermine Case A -- era diversity is what makes the broad career query work; depth-in-one-era overrides the rule Case A depends on, requiring a router family and a second diversify branch to undo the branch just added. (3) Text placement cannot close the gap -- measured twice; moving the chronology sentence moved scores by 5-7 thousandths against a 0.018 gap (STRATCOM rank 44). The lever does not exist on the retrieval side.

Discovery gap filed as MATTGPT-210: stories like STRATCOM are perfectly retrievable by their own vocabulary but invisible on broad career queries. Fix is rotating suggestion chips on the Ask Agy landing page, not a ranker change.

---

**August 22-24, 2026 — MATT_DNA grounding overhaul; nine early-career stories ingested; ingestion pipeline (MATTGPT-207, MATTGPT-181)** -- `d2618f3`, `4c8d900`

MATTGPT-207 (`d2618f3`): MATT_DNA restructured. Career Arc rows now one per employer with dates (four employers: WellFound Technology 2000-2002, Lockheed Martin / Cendian 2002-2005, Accenture 2005-2023, Independent 2023-present). Career Eras first row names pre-Accenture organizations explicitly. "What Matt is NOT" block removed. Currently line replaced with hero copy. Flat client list replaced with clients grouped by employer. WellFound added to grounding as a named pre-Accenture employer. Drift guards added in `utils/validation.py`. Fixed a production fabrication: "what did Matt do before Accenture?" was returning AT&T as a pre-Accenture employer (misread of an Accenture-AT&T engagement). Known gap in drift guards filed as MATTGPT-209.

MATTGPT-181 (`4c8d900`): Nine early-career STAR stories ingested covering 2000-2005: Sparkfly (pre-Accenture individual contributor anchor), F-22 / WellFound (ETL, PL/SQL, TIBCO), STRATCOM / Lockheed Martin (real-time Gantt, TDD and pairing verbatim from 2005 resume), Cendant Mortgage, Accredited Home Lenders, AIU (adjunct professor), and three Cendian B2B/EDI stories (ASC X12, WebMethods, multi-modal logistics -- Norfolk Southern ancestor). Corpus: 123 stories, 17 clients, five employers. Career span now reads 2000-2026; `_CAREER_START_YEAR` derived correctly from JSONL as intended by MATTGPT-161. Era "Technical Foundations & Enterprise Integration, 2000-2005" added to `ERA_ORDER` in `timeline_view.py`.

Architecture standing rule (for Code to document in ARCHITECTURE.md): The Employer field carries two meanings -- who employed Matt during the work, and what period the story covers. For engagement stories these coincide. For arc stories they do not: "Why Hire Matt", "Transition Story", and "Career Intent" all carry `Employer=Accenture` but span dates beyond 2023. Any derivation driven by Employer must filter `Theme == "Professional Narrative"` to avoid returning stale end dates. Verified: that filter produces Accenture 2005-03 to 2023-09; unfiltered derivation returns 2026-08. Same principle applies to placeholder Client values (`Fortune 500 Clients`, `Independent Project`): deliberate, not mis-tagged.

---

**August 19, 2026 — Career span derived from corpus; hardcoded year-count removed from MATT_DNA (MATTGPT-161)** -- `79f6d90`

`_CAREER_START_YEAR`, `_CAREER_END_YEAR`, and `_CAREER_SPAN_YEARS` are now derived in `sync_portfolio_metadata()` from the JSONL at startup alongside `SYNTHESIS_THEMES` and `_KNOWN_CLIENTS`. `MATT_DNA` prose updated: "18+ years" removed from the Accenture line; "+ years" removed from the Career Arc line. Accenture date range preserved. Debug print updated to read derived values.

When MATTGPT-181 (early-career story slate) lands, `_CAREER_START_YEAR` moves from 2005 to 2000 automatically -- no code change needed at that point.

Surfaces not touched: home hero (already clean -- "my full project history" framing, no year count), `test_home_seniority.py:72` (out of scope per MATTGPT-103 carve-out), README.md, mattgpt_system_prompt.md, design-spec repo.

BDD: `tests/bdd/features/matt_dna_career_span.feature`, 4/4 scenarios passing. Red scenarios `7c5049d`, Red step defs `2c4f5e2`, Green `79f6d90`.

---

**August 18, 2026 — nonsense_filters.jsonl deduplicated; loader hardened; two narrowings fixed (MATTGPT-165)** -- `a6d5145`, `766a138`, `7566a13`

Three-commit sequence resolving a multi-generation filter file and two active query-blocking defects.

Commit A (`a6d5145`, `766a138`) -- Loader hardening and eager preload. `_load_nonsense_rules` in `utils/validation.py` gains three load-time guards: duplicate guard (raises `ValueError` on any duplicate `(category, pattern)` tuple, keying on parsed tuple not raw bytes to catch JSON-key-order variants), type guard (raises on non-dict rules -- bare strings and lists that would cause `AttributeError` in `is_nonsense` at query time), and regex guard (`re.compile` on load to catch patterns that would raise at query time). `app.py` now calls the loader eagerly at startup so a corrupt file fails at boot rather than on the first visitor's query.

Commit B (`a6d5145`) -- 26-line dedup. The file had three blocks: block 1 (lines 1-27, original generation), block 2 (lines 28-55, second generation), block 3 (lines 56-79, new categories). Block 2 duplicates most of block 1. Removed 21 byte-identical (or JSON-key-order-only-different) duplicate pairs by deleting the block-1 originals, and removed 5 block-1 originals where block-2 was a superset widening. Behavior-neutral: all 21 pairs shared identical category and pattern; the 5 widenings are set-supersets. Eval held at 70/70. File: 79 lines → 53 lines.

Commit C (`7566a13`) -- Two narrowings fixed. Line 1 of the 53-line file (`personal_sensitive`, `credit card` bare token) was broader than its block-2 counterpart (`credit card number`) and blocked "Tell me about the credit card portal work" -- four Fiserv card-portal stories were unreachable. Deleted. Line 2 (`celebrity` bare tokens `swift|gaga|...`) blocked SWIFT payment rails queries; `\bswift\b` matches `SWIFT` in `SWIFT/NACHA` because `/` is a word boundary. Edited to remove `|swift` from the alternation; the other seven bare tokens and the full-name block-3 counterpart (line 56: `taylor swift`, etc.) remain. Taylor Swift queries stay blocked. SWIFT payment rails queries now reach retrieval. File confirmed at 52 lines post-edit.

Corpus grep verified before commit C: "credit card" appears in exactly one story (Fiserv white-label card portal); "swift" appears in exactly one story (JPM Gateway, `SWIFT/NACHA Messaging Standards` in Competencies). No unexpected surface area.

BDD: three cycles, one feature file. Cycle A: six loader-guard scenarios. Cycle B: dedup behavior-neutral checks. Cycle C: both narrowing fix scenarios plus celebrity and nonsense regression guards.

---

**August 17, 2026 — Entity cluster promotion gate refined: content-kw uniformity replaces count-only heuristic (MATTGPT-074)** -- `c67c8b7`

Two-iteration fix. The original gate promoted any entity query to synthesis mode when Pinecone returned 3+ stories from the same entity, treating corpus density as a proxy for user intent. Depth questions ("How did you build the CIC?", "Who reported to Matt at the CIC?") were force-promoted to thematic survey responses.

Refinement: the gate now strips entity tokens -- canonical value plus the union of all matching alias keys -- from the retrieval query, recomputes `_keyword_score_for_story` per entity story against what remains, and promotes only when those content-kw values are uniform. Empty content tokens after stripping is trivially uniform and promotes. The 3-story count check is retained; both conditions apply.

Iteration 1 (`771828b`): read stored kw values. Suppressed promotion on broad queries when a story title contained the entity name ("What did Matt do at liquid studio?" -- kw [1.0, 0.5, 0.5, 0.5, 0.5, 0.0]). Title-entity matching carries no specificity signal.

Iteration 2 (`c67c8b7`): strip entity name before measuring. Fixes the title-contamination in iteration 1.

Prerequisite: `services/rag_service.py` now propagates `kw_score` into story dicts alongside `pc_score`. The gate recomputes rather than reading that field -- confirm whether `story["kw"]` has any remaining consumer.

Verified in app (Aug 17): "What did Matt do at liquid studio?" -- uniform → synthesis. "Tell me about Matt's work at Fiserv" -- uniform → synthesis. "Tell me about a production incident at AT&T" -- content_kw [0.5,0,0,0,0] → standard. "What did Matt do at RBC?" -- uniform → synthesis. "What did Matt do at amex?" -- uniform, alias stripped → synthesis. "What did Matt do at AT&T?" -- uniform → synthesis.

BDD: `tests/bdd/features/cluster_promotion_kw.feature`, 8 scenarios, Red `f6b84a8`, step defs `eb7e5cb`, Green `c67c8b7`. Full BDD 241 passed / 3 failed / 36 skipped; 3 failures pre-existing or ticketed (MATTGPT-197/-198). Unit 569 passed / 13 failed; all pre-existing or ticketed. Eval: 70/70 after Q36 correction.

---

**August 17, 2026 — Entity aliases expanded; AT&T client rename; Fiserv DevOps vocabulary; Q36 corrected** -- `f090e8f`

`ENTITY_ALIASES` additions: "jp morgan" (→ Client "JP Morgan Chase") and "liquid studio" (→ Division "Atlanta Liquid Studio"). Header comment rewritten -- the table now holds acronyms and shortened forms of longer canonical values, not acronyms alone.

AT&T Mobility: client value changed from "AT&T Mobility" to "AT&T". The business unit was Cingular at the time and later became AT&T Mobility; recording it as a separate client made the story unreachable on AT&T entity queries. Story ID changed from `building-att-mobilitys-service-delivery-platform|att-mobility` to `building-atts-service-delivery-platform|att`. AT&T entity queries now return 6 stories.

Fiserv DevOps: Change Failure Rate Reduction, Production Stability, and Incident Prevention added to Competencies; Use Case extended to name the hotfix-and-rollback cycle. Both backed by existing Situation and Result content.

Q36 (eval): asserted that partial names should not scope -- stale given that client values are canonical long forms and aliases cover shortened forms. Q36 now expects `("Client", "JP Morgan Chase")`. `test_proper_nouns_do_scope` renamed to `test_entities_do_scope`.

---

**August 17, 2026 — Dead ENTITY_GATE_THRESHOLD constant removed from config/constants.py (MATTGPT-141)** -- `3fcb447`

`ENTITY_GATE_THRESHOLD = 0.30` was never imported outside `config/constants.py`. The Entity Gate was removed January 2026; the constant was a leftover with a misleading inline comment ("Used by backend_service.py to decide if a query passes the semantic gate" -- false). Verified clean: `grep -rn "ENTITY_GATE_THRESHOLD" --include="*.py" .` returns zero matches outside venv. Constant and comment deleted.

---

**August 17, 2026 — Professional Narrative exclusion from technical-query pools; ten-story scope confirmed (MATTGPT-169)** -- `6a581d5`

Professional Narrative stories (ten total) are now excluded from the candidate pool in standard-mode retrieval when `intent_family` is in `_PN_EXCLUDED_FAMILIES = frozenset({"technical", "delivery", "domain_payments", "domain_healthcare", "agile_transformation"})`. Implemented at the top of the standard-mode else block in `backend_service.py`, before entity pinning. Guard: if the filter would empty the pool, it does not apply. Narrative and synthesis paths are untouched -- they have their own branches at lines 1850 and 1944.

Allowlist rather than denylist by design. The semantic router misclassifies frequently -- ten incident-management queries landed across six different families on Aug 16; "Tell me about a production incident at AT&T" classified as `family=innovation` at 0.389 invalid. An allowlist means a misrouted query keeps prior behavior rather than losing ten positioning stories.

Scope correction: ten Professional Narrative stories, not seven as prior notes in this ticket stated. The three not previously listed -- "What I Learned About Assumptions", "What I Learned About Sustainable Leadership", "Why Early Failure Is a Feature, Not a Bug" -- include the story that was leading the production-incident query at 0.451; their inclusion matters.

Corpus-side fix disconfirmed as a lever: AT&T Southeast CRM was given outage vocabulary on Aug 17 and registered kw=0.333 against 0.000 for the other four AT&T stories on incident queries, but still lost to positioning stories at 0.417 vs. 0.451 on a career-phrased query. Query shape, not vocabulary absence, favored positioning content. The code exclusion was the required fix.

Verified in app (DEBUG, Aug 17): "How does Matt do platform refactoring?" (technical) -- pool of 10, zero PN stories, Rail leads at 0.599. Three controls (synthesis, narrative x2) correctly bypass the filter. Verified by probe harness: PN in pool=0, PN in sources=0 on technical query; PN in sources 1-2 on all three controls. Artifact `probe_pn_exclusion.py` retained -- deterministic, re-runnable after any retrieval change.

BDD: `tests/bdd/features/pn_exclusion.feature`, 3 scenarios, 3/3 green. Eval: 70/70 before and after. MATTGPT-168 (slot-1 amplification) remains open.

---

**August 15, 2026 — Eval/probe harnesses normalized; public_tags contributes keyword tokens in measurement (MATTGPT-182)** -- `275ff1f`

Nine call sites in `tests/eval_rag_quality.py` and four probe scripts bypassed `app.py`'s `_split_tags()` normalization, loading corpus stories via raw `json.loads`. `public_tags` reached `_keyword_score_for_story` as a comma-separated string; `.join()` over a string character-separates it; every resulting token failed the `len >= 3` filter. Tags contributed zero keyword tokens in every eval and probe run since October 2025, while contributing normally in production.

Fix: `_split_tags()` and `_ensure_list()` extracted into a shared corpus loader; all nine call sites updated to use it. 12/12 BDD passing. Eval re-baselined at 70/70. P5 keyword gap narrowed from 3-1 to 3-2 post-normalization (P5/P8 still LEAD; results in MATTGPT-077 findings). MATTGPT-077 Phase 2 unblocked.

Measurement boundary: eval and probe numbers recorded before 275ff1f were produced with tags dark and do not compare to numbers after it. This includes the E1-E4 evidence behind W_KW=0.15 (f5641e7) and the MATTGPT-077 Step 0 baseline. Re-baselined Aug 15; treat prior figures as a separate regime.

---

**August 15, 2026 — Corpus vocabulary edits: Rail, AT&T Mobility, Fiserv Recovering (MATTGPT-077 / MATTGPT-168)**

Three stories rewritten for query vocabulary alignment:

Norfolk Southern Rail (MATTGPT-077 Phase 1): "platform refactoring" added explicitly to Use Case. pc on P5 ("How did Matt approach platform refactoring?") 0.484 → 0.526; pc on P8 ("What does Matt's experience with platform refactoring look like?") 0.506 → 0.549. P5/P8 now answer from Norfolk Southern.

AT&T Mobility: "Sev defect management" vocabulary strengthened to "Sev-1 defect and incident response" with on-call tags and one Interview Question added. Story was absent from the Sev-1 query pool before the edit; now reaches rank 3.

Fiserv Recovering: Sev-1 handling moved into its own sentence, parenthetical cross-reference to another story's title removed (that title was embedding in Fiserv's vector). pc on Q1 ("how did Matt handle a Sev-1 defect?") 0.317 → 0.326. Q1 still fails -- chatbot leads at 0.360 vs 0.326. Ranking fix continues in MATTGPT-168.

---

**August 2026 — evidence_fidelity BDD suite: no hallucinated clients, metrics traceable, no cross-contamination**

The `evidence_fidelity.feature` suite validated three properties across the Ask Agy pipeline: (1) no hallucinated clients -- answers cite only clients from the retrieved story pool; (2) metrics traceable to source -- figures in responses map back to a specific story's data; (3) no cross-contamination -- stories do not bleed evidence from adjacent stories. All three pass. Strongest BDD evidence of response fidelity in the repo; surfaced during a targeted investigation rather than routine coverage work.

---

**August 13, 2026 — _tokenize stopword fix; keyword noise tokens eliminated from scoring (MATTGPT-178)** -- `049e203`

`_STOPWORDS` was defined thirty lines above `_tokenize` in `utils/validation.py` and used only by `token_overlap_ratio` -- an accident of the October 2025 Phase 3 extraction, never a decision. Dormant for nine months while `W_KW = 0.0` made it inert; live since MATTGPT-157 re-enabled keyword scoring on August 8. Fix: one line -- `_tokenize` now applies `_STOPWORDS` before the `len >= 3` filter.

Validated against Q1 ("how did Matt handle a Sev-1 defect?"): keyword scores inverted -- Fiserv 0.250 (sev-1, defect match), chatbot 0.125 (how, matt). pc remains the controlling factor; pc gap work continues in MATTGPT-168.

The character-set divergence between `_tokenize` (keeps `+#-.`) and `token_overlap_ratio` (splits on non-`\w`) is a separate defect filed as MATTGPT-190.

---

**August 13, 2026 — W_KW trace payload corrected; weights centralized in constants.py (MATTGPT-175)** -- `d8dcbe7`

W_PC and W_KW added to `config/constants.py` as the single authoritative source. `utils/scoring.py` updated to import from constants rather than define defaults. `pinecone_service.py` lines 97-98 (module-local W_KW=0.0 shadow copy) deleted; import added so line 281's trace payload now reads the live value. No ranking behavior change -- the fix corrects the instrument, not the weight. Arithmetic proof: pc=0.580, kw=0.667, blend=0.680 confirmed `0.580 + 0.15 × 0.667 = 0.680` before the fix; trace reported 0.0.

Step 4 (docstring and stale assertion cleanup) shipped in the same commit: `_hybrid_score` Returns and Example block updated for W_KW=0.15; four `test_scoring.py` assertions updated (`test_default_weights_use_semantic_only`, `test_handles_none_pc_score`, `test_handles_invalid_pc_score_type`, `test_default_weights_favor_semantic`) -- these were correct when written against W_KW=0.0 and went stale when f5641e7 raised the weight. A `test_weights_have_single_source` regression guard was also added (not in the original ticket scope) to prevent future silent divergence between the constants source and any module-local copy.

---

**August 13, 2026 — Top Score column added to query logger; confidence gate mechanism confirmed (MATTGPT-174)** -- `bc72fba`

Investigation confirmed the confidence gate reads `max(h["score"] for h in hits)` -- pure Pinecone cosine similarity, keyword term never enters the gate. Production query log (532 rows): 512 high, 12 low, 8 none; 96% high; every low/none row is a greeting, test string, or gibberish. Both constants sat below the operating range (real pools bottom at ~0.30; CONFIDENCE_LOW=0.20 prunes nothing, CONFIDENCE_HIGH=0.25 is cleared by everything). Gate was functioning as a second nonsense filter, not a match-strength signal.

Fix: added "Top Score" column to `services/query_logger.py` so production traffic accumulates the pc distribution. First value logged post-deploy: 0.358673066 for "how did Matt handle a Sev-1 defect?" 8/8 BDD passing. Threshold redesign (two-factor gate using level and spread) waits on data from this column accumulating. Also resolved MATTGPT-157 step 4 outright: raising W_KW cannot shift the gated value; no recalibration needed from that source.

---

**August 8, 2026 — W_KW re-enabled at tested weight; keyword scoring live in hybrid retrieval (MATTGPT-157 / MATTGPT-170)** -- `f5641e7`

Investigation (MATTGPT-157) completed per the predict-then-test method: blended scores computed arithmetically from existing trace values at candidate weights before any code change; holdout run against a working query (P&L), an operational query (Sev-1), a name-bearing query, and the "innovation" canary. Prediction confirmed -- specific-term class improved, canary held, name-bearing queries did not inflate narrative stories. Code change proceeded.

Implementation record (MATTGPT-170, closed on creation): W_KW re-enabled in `services/pinecone_service.py` at the tested weight. E2 pre-registration was struck during the holdout (flat weighting at the initial candidate value did not cleanly separate specific from generic overlap); E3 was re-filed with a revised weight that passed. Shipped at f5641e7.

Revert lever: set `W_KW=0.0` in `pinecone_service.py`. This returns the system to pure-semantic mode (W_PC=1.0). The `_keyword_score_for_story` function remains wired and functional at 0.0 -- no code removal needed, one constant change.

Known residual (filed as MATTGPT-171): stopword-only phrases (e.g., "I do, we do, you do") reduce to an empty token set after stopword removal. Token-overlap score is zero regardless of W_KW weight. This is an investigation item, not a regression -- behavior was identical before and after the re-enable.

---

### Role Match

**August 5, 2026 — -088 investigation closed; condition in ticket title no longer exists (MATTGPT-088)**

Three findings on closure:

(1) The May 2026 contradiction -- Role Match marking "in-house engineering org of 60+" as Strong Match while Agy correctly said no -- resolved through corpus changes rather than a targeted fix. Both surfaces now agree. The condition in the ticket title is falsified.

(2) The duration-inference inconsistency hypothesis (assessor infers duration from bounded ranges but not open-ended floors) was falsified by matched-pair test. Identical five-story pools across phrasing variants; structured requirement 3 ("5+ years managing managers") moved from partial to strong once the management story existed in the corpus. The variable was content availability, not phrasing sensitivity. Requirement 2 ("10+ years of professional software development") stays partial: a corpus content gap (career starts 2005 at Solution Architect level; pre-2005 hands-on development is undocumented), not an assessor defect.

(3) The remaining evidence-divergence finding -- surfaces reaching the same verdict from different stories -- has a confirmed mechanism, now split across two active tickets: MATTGPT-077 (retrieval contamination pulling Why Hire Matt to slot 1 on management queries) and MATTGPT-168 (slot-1 binding instructing the LLM to build its entire answer around that story and resist correction). The fix lives there.

Baselines (`probe_158_single_*.csv`, repo root) generated August 3 predate the management story added August 5. Structured requirement 3 has moved from partial to strong since. Note in `probe_assessor.py` at the extraction cache declaration.

---

## July 2026

### Ask Agy

**July 31, 2026 — Profile grounding restructured; fabricated citations eliminated (MATTGPT-158)** — `45abd91`

Root cause was structural, not a prompt defect. `career_summary` prose in the grounding was a citable surface, and the model paraphrased it into evidence strings with no traceable source. An earlier traceability rule failed because a paraphrase of prose does trace to prose -- the rule was correct in form but the wrong instrument for the problem.

Fix: `load_matt_profile()` now emits discrete facts only -- education and certifications. `career_summary` excluded from assessment grounding entirely, not relabeled or fenced. Prompt rule replaced: only discrete facts are citable as profile evidence. The counterfactual clause ("omitting profile evidence must not change the verdict") deleted as unenforceable -- it asks the model to evaluate a run it cannot make.

Validation: three JDs, five runs each, frozen extraction. 62 requirements, zero verdict variance except one. Fabricated citations gone on every JD. Three profile citations remain, all degrees, all traceable to the education field. Pre-registered expectations held: structured tenure stayed partial, demo tenure moved strong to partial, degree unchanged.

Finding worth carrying forward: two requirements moved that never held a profile citation -- structured #3 (managing managers, strong to partial) and #13 (insurance domain, partial to gap). The prose was doing ambient work beyond citation. The harness invariant "removing profile grounding may only affect profile-cited requirements" was wrong. Grounding is in the prompt whether cited or not.

Shipped alongside: UI label "Verified skill" changed to "Profile" with a neutral dot (the label asserted verification and called a degree a skill). Year count and unresolved revenue figure removed from `career_summary`.

Follow-ons: MATTGPT-088 (tenure inference from story dates, reproducible pair identified), MATTGPT-160 (extractor clause-dropping), MATTGPT-159 (sequential assessor calls). All previously filed.

**July 31, 2026 — `matt_profile.json` skills array drop complete (MATTGPT-080)**

Skills array removed from `matt_profile.json`; `load_matt_profile()` updated to handle the absent key cleanly; assessment prompt verified facts-only. BDD-first cycle completed before implementation. No re-embed required (profile is not embedded).

Validated across three JDs (demo, structured, Fiserv) at TOP_K=5: zero recommendation flips across all conditions. Complete picture:

| JD | Pre-drop A | Pre-drop B | Post-drop A | Post-drop B |
|---|---|---|---|---|
| Demo | Apply/High | Apply/High | Apply/High | Apply/High |
| Structured | Apply/High | Apply/High | Apply/High | Apply/High |
| Fiserv | Consider/Medium | Consider/Medium | Consider/Medium | Consider/Medium |

Three findings recorded on closure: (1) The TOP_K=5 baseline supersedes all TOP_K=3 data from this session; a "Consider/Medium" figure circulated mid-session from a pre-parity run and should not be read as current. (2) The array's demonstrated effect was one requirement out of 60: database #7 on the structured JD moving from strong to partial in condition A. That is the only proven contribution across three JDs -- true finding, smaller than the session effort implied. (3) Exit criterion passed with two honest gaps standing: product-company experience (demo JD) and COBOL/IBM template noise (Fiserv). Neither is a corpus defect. -088 is now unblocked.

**July 29, 2026 — Corpus em dash cleanup complete (MATTGPT-151)**

All em dashes removed from master Excel (MPugmire - STAR Stories - 28JUL26v1.xlsx), verified across all 29 fields and all rows. Pipeline is unidirectional (master → JSONL), so the scrub is permanent. Re-ingest and push to production stays with Matt. Confirmed clean by Code session cross-checking the saved file.

**July 16, 2026 — Retrieval concentration investigation closed (MATTGPT-094)**

Investigation into two retrieval-bias hypotheses, both resolved.

Sub-A (CIC over-concentration on broad queries): disproven. Probe data showed CIC absent from top results on broad queries. What leads vague queries is the Professional Narrative cluster (Why Hire Matt, About Matt), which recedes as queries get specific. `diversify_results` self-corrects downstream. No retrieval fix needed.

Sub-B (operational story under-surfacing): confirmed vocabulary gap. Terms like "Sev-1" and "on-call" were absent from the corpus despite the substance existing in JPM and AT&T CRM stories. Tagged both stories with operational vocabulary. Verified in prod: "Matt's experience with Sev-1 resolution" now surfaces both clients and synthesizes a pattern. Fix confirmed.

Spawned follow-on: MATTGPT-154 (operational-breadth tagging pass -- remaining corpus stories where operational vocabulary anchors are still missing).

**July 1, 2026 — Ask Agy button alignment + focus ring fix (MATTGPT-033)** — `1be5953`
Fixed two related visual defects on the Ask Agy landing and conversation pages. Alignment: `styles.py` landing Ask button set to `margin-top: 0; min-height: 44px`; conversation submit button `min-height: auto`, `translateY` override removed; `ask_mattgpt_header.py` `.ask-header-conversation` `margin-top` adjusted `-48px → -32px`. Focus ring: replaced Streamlit's inherited red `box-shadow` ring with a purple-matched `rgba(139, 92, 246, 0.5)` ring scoped to `.st-key-landing_ask button:focus-visible`. BDD: 5 new scenarios in `ask_agy_button_alignment.feature` + unit tests in `test_ask_agy_button_css.py`. Bundled BDD hardening (no production code): `test_navbar_css_scope.py` wait state fix; `test_role_match.py` `networkidle` → `data-test-script-state` pattern; count-parse regex fix in `test_banking_landing.py`, `test_cross_industry_landing.py`, `test_home.py`; dead AgGrid `.ag-cell` selectors replaced in `test_explore_stories_default_state.py`. 197/197 passing, 36 skips unchanged.

## June 2026

### Process

**June 2026 — CLAUDE.md restructure + targeted fixes (MATTGPT-120, MATTGPT-125)**
Shipped together; -125 targeted fixes were prerequisites for or resolved by the -120 restructure.

-120 (restructure): Critical Rules fast-reference block at top — 17 incident-tied imperative rules, readable in 30 seconds. Full rules-first format throughout — narrative stripped to one-line incident citations, CSS Rules and Streamlit Patterns trimmed, Working with Claude section removed, stale content removed.

-125 (targeted fixes, all 6 items resolved): Unbound `label` variable in screenshot example fixed (concrete string). "Effort estimates without consulting padding" heading renamed. ARCHITECTURE.md watch list broadened to include `utils/` and `config/`. SHA fallback added (prompt Matt if anchor missing). CSS Rule 8 DevTools trigger broadened to cover color and typography. Three contradictory rule pairs resolved by the restructure: pre-flight vs. execute addressed by pre-implementation reasoning gate; build-on-top-of vs. replace addressed by explicit "name why it fails" rule; one-go vs. separate gates resolved by the Red/Green cycle as the defined gate structure. Deferred sync anchor and agent trigger conditions resolved in the Backlog Maintenance and Architecture Sync section restructure.

### Design Spec (mattgpt-design-spec Jekyll)

**June 2026 — Design spec nav label fixes + story_count_label floor correction (MATTGPT-109)**
Closed the remaining spec drift from the June 15-16 audit pass. Nav labels in docs 08 and 09 corrected (Explore Stories -> My Work, Ask MattGPT -> Ask Agy). Stale wireframes dropped — they had no links from any published page, so removal is zero user-facing impact. Discoverability fix (My Profile spec link) ruled a leftover: the How I Built dialog already has a "Read the design spec" card, closing the gap. Positioning addition scratched: `index.md` already opens with "Read it as the audit, not the pitch" — an explicit framing paragraph risks tipping into the register it avoids. `extract_facts.py` floor corrected: `story_count_label` now uses a 100-step floor (`// 100 * 100`) so the label stays "100+" until 200 stories rather than incrementing at each 10-story threshold. `_data/facts.yml` reverted from "110+" to "100+". Commits: Jekyll nav labels rebased onto `d99da4c`; app repo `6f0957f`; Jekyll facts `54ac532`.

### CSS Architecture

**June 2026 — "How Agy Works" modal mobile layout fix (MATTGPT-076)**
Fix Option C applied: replaced `components.html` iframes with fixed pixel heights (`height=1180`, `height=850`) with native Streamlit `stMarkdown` / `stMarkdownContainer` elements. Modal now reflows correctly on mobile — cards stack single-column, content scrolls within the modal, no viewport overflow. Desktop two-column grid unaffected. Validated at 390×844 (iPhone) and desktop.

**June 2026 — Page-load blep: re-add visibility:hidden on Ask Agy stale hero during nav (MATTGPT-018)** — `a6b427c`
Re-added CSS rule to `global_styles.py` hiding Ask Agy landing hero containers during the Streamlit stale-element retention window on navigation. Both selectors (`.main-intro-section`, `.ask-header-landing`) with `visibility: hidden !important`. Mechanism comment restored including deliberate `.ask-header-conversation` exclusion. Unit test added in `tests/unit/test_global_styles.py`: whitespace-tolerant assertion that selectors and `visibility: hidden !important` are present as a unit in `_CSS`, catching both rule deletion and mutation to a no-op value. 3/3 BDD scenarios passing.

### My Work

**June 2026 — My Work Table view: migrate from st_aggrid (iframe) to st.dataframe / Glide Data Grid (MATTGPT-144)** -- `77dc1cb` -- **Reopened August 31, 2026: count-noun fix incomplete; see BACKLOG**
Replaced st_aggrid with st.dataframe (Glide Data Grid) in the My Work Table view. Eliminates the AgGrid custom-component iframe re-init on filter rerun (the -144 symptom) and removes the AgGrid bootstrap.min.css 195ms revalidation round-trip on page nav. BDD: 55/55 passing, 0 skipped. Key test changes: removed all AgGrid iframe / `.ag-row` / `frame_locator` assertions; added `st.dataframe` canvas-mount proxy (`data-grid-canvas`); replaced `networkidle` waits with `wait_for_streamlit_rerun` (Glide Data Grid's continuous XHR never settles networkidle); converted empty `pass` stubs to count-direction logic via `_read_count()`; added Cards-view-switch fallback in `click_story_card` (3 scenarios now run instead of skip); added Share "Copied!" confirmation scenario. Deleted 2 scenarios: Table-row Ask Agy (canvas row-click undriveable, redundant with Cards) and deeplink-respects-view-mode (non-feature: deeplinks intentionally start fresh session). Guard proof: breaking `no_story_results_shown` fails both rejection scenarios; non-vacuous.

**June 2026 — AgGrid bootstrap.min.css render-blocking resolved as side effect of st.dataframe migration (MATTGPT-137)**
`st_aggrid` removed from all `ui/` files as part of MATTGPT-144. The bootstrap.min.css 195ms server revalidation round-trip on Ask Agy → My Work transitions no longer occurs because the AgGrid custom component and its bundled assets are gone. No direct fix required.

### Ask Agy Performance

**June 2026 — Ask Agy landing chips: st.button → static HTML + JS bridge (MATTGPT-139)** — `4e8e461`, `722972b`
Converted 6 `st.button` chips + `st.columns` on the Ask Agy landing page to static HTML with a hidden receiver JS bridge (pattern from `category_cards.py`). Reduced navigation span window from ~667ms to ~400ms (40% reduction); FunctionCall cost from ~105ms to 82.5ms. Desktop and mobile paths both converted. Disabled state added via CSS pointer-events on the grid container during query submission. `.suggested-chips-grid` / `.suggested-chip` rules moved to `global_styles.py`. BDD: 14/14 scenarios passing. The 400ms floor is the practical limit of the chip-conversion approach — blep is narrower but not eliminated (see MATTGPT-018).

### My Profile

**June 2026 — My Profile visual-language reconciliation (MATTGPT-093)** — `4bbdb46`
About Matt strategic restructure resolved as a visual-language reconciliation. CTO and recruiter persona findings (May 27) drove a surface redesign that retained the single-page structure while improving the recruiter-facing conversion moment. 19/19 BDD scenarios passing.

**June 8 — My Profile — Copy snippet + Download PDF buttons (MATTGPT-118)** — `223aabf`
Added Copy snippet and Download PDF affordances. Copy uses delegated parentDoc listener + navigator.clipboard. PDF uses hidden st.button bridge + window.open/print. 20/20 BDD scenarios passing.

### How I Built

**June 8 — How I Built dialog — BDD coverage for "See It In Action" prompt buttons (MATTGPT-117)** — `97c7d51`, `3278128`
Added 2 BDD scenarios to `how_i_built.feature`: section visibility + 4-chip count, and chip-click → Ask Agy routing (first chip). 8/8 passing. Closes coverage gap left when MATTGPT-068 scenarios were removed from `about_matt.py` during MATTGPT-093.

### CSS Architecture

**June 17 — Gate mobile navbar IIFE behind viewport check (MATTGPT-135)** — `f818469`, `74ce328`
The mobile navbar IIFE in `navbar.py` ran on every Streamlit rerun regardless of viewport width, causing wasted DOM work and a double-avatar flash on desktop during page transitions. Fix: `if (window.parent.innerWidth > 767) return;` guard at the top of the IIFE. Must use `window.parent.innerWidth` not `window.innerWidth` — the IIFE runs inside a srcdoc iframe whose own viewport width differs from the parent page. Follow-up commit `74ce328` fixed a desktop dark mode regression introduced by the guard placement. BDD: 2 scenarios in `navbar_mobile_viewport_gate.feature` passing.

**June 14 — Page-transition Agy avatar flash — HTML constraints + mousedown pre-hide (MATTGPT-018)** — `bda7ba8`, `3659173`
Fixed 330px Agy avatar flash during Ask Agy → other page transitions. Root cause: `agy_avatar.png` renders at natural size during the window where Streamlit removes the old page's CSS from the CSSOM before clearing the DOM. Two-layer fix: (1) HTML `width`/`height` attributes on all Agy `<img>` elements in `ask_mattgpt_header.py` and `landing_view.py` prevent natural-size render without CSS constraints. (2) `mousedown`+`capture:true` JS listener in `navbar.py` sets `opacity:0` on avatar elements before React's synthetic `onClick` fires the Streamlit rerun — gives browser 50-200ms to commit the hide. Mobile hamburger `link.onclick` handlers got inline pre-hide logic before the `btn.click()` bridge. Global `agiAvatarReveal` fade-in animation in `global_styles.py` (0.15s ease-out, 0.15s delay) covers programmatic navigation paths where the mousedown listener doesn't fire.

**June 13 — Mobile header consistency — min-height floor + avatar alignment across 6 pages (MATTGPT-114)** — `9658e02`
Resolved via a min-height floor approach rather than the original shared-CSS-class plan. Added `min-height: 145.59px` to all purple header mobile blocks (`.conversation-header`, `.about-header`, `.ask-header-landing`, `.ask-header-conversation`) so all pages share a consistent header height regardless of content length. Fixed Banking and Cross-Industry page-level `min-height: auto !important` overrides that were blocking the global floor. Fixed CSS cascade in `ask_mattgpt_header.py` — moved `@media (max-width: 768px)` block after the global `.status-bar` reset so mobile `margin-top` wins. Aligned Ask Agy header to match `.conversation-header` structure (no negative margin bleed); inner flex gap `24px → 12px`. `about_matt.py`: `.about-header-avatar` class applied, badge absolutely positioned (`top: 50%; transform: translateY(-50%); right: 32px`), subtitle shortened, `deep-dive-card h3` `8px → 18px`. `global_styles.py`: avatar base rule, mobile badge hidden, orphaned duplicate avatar rules removed.

**June 13 — Home category cards — descriptive meta copy for all 6 cards (MATTGPT-108)** — `ff6c788`
Revised approach: replaced dynamic `{N} projects · {client list}` strings with static descriptive copy across all 6 cards. Original plan (add counts to the 4 non-industry cards) rejected as the wrong signal — counts were volume noise, not quality signal. Instead, Banking and Cross-Industry had their count/client strings replaced with capability-scoped descriptions matching the other four cards, achieving parity by subtracting rather than adding. One or two tight sentences per card, core message first. Removed now-unused computation variables (`banking_clients_inline`, `cross_industry_inline`, `cross_industry_stories` and upstream dependencies).

**June 12 — Story count copy — confirmed "130+" has no user-facing runtime references (MATTGPT-019)**
Audit confirmed zero user-facing `130+` references in active production code. All UI Python files already use `100+` or derive counts dynamically. Remaining `130+` occurrences are in dead code (`mobile_overrides.py` — never imported), design docs (`ARCHITECTURE.md`, `WIREFRAMES.md`), and `mattgpt_system_prompt.md` (not read at runtime). Ticket closed as resolved.

**June 9 — Bundle 1 CSS polish — back-link dark mode, How Agy scroll-to-top, stats label contrast (MATTGPT-111, -112, -069)** — `c8ce37d`
Three low-priority CSS/JS fixes shipped in one commit. Back-link breadcrumb pill (`explore_stories.py`): replaced hardcoded hex colors with CSS variables (`--bg-card`, `--accent-purple`, `--border-color`) — fixes white-pill-on-dark-background in dark mode (MATTGPT-111). How Agy Searches dialog (`how_agy_dialog.py`): scroll-to-top JS selector fixed from `[role="dialog"] > div` (overflow: visible, never scrolls) to `[role="dialog"]` (actual scrollable container, confirmed via DevTools); switched from fixed 100ms `setTimeout` to self-retrying IIFE (MATTGPT-112). Hero stats labels (`hero.py`): `var(--text-muted)` fails WCAG AA in both light (2.54:1) and dark (3.91:1) modes; swapped to `var(--text-secondary)` which passes in both (4.83:1 light, 7.44:1 dark), confirmed via DevTools CSSOM (MATTGPT-069).

**June 10 — Consolidate CSS to global_styles.py; fix rerun regression (MATTGPT-105)** — `191032b`
All `st.markdown()` CSS injections across `footer.py`, `thinking_indicator.py`, `timeline_view.py`, `story_detail.py`, and `explore_stories.py` relocated to `global_styles.py` with `es-*` HTML class namespace. Eliminates the rerun garbage-collection bug where inline `<style>` blocks injected inside render functions were stripped from the DOM during Streamlit's mid-rerun pause. Also fixed a live production JS bug: the delegated click listener in `explore_stories.py` was still targeting `.fixed-height-card` after the HTML rename, silently breaking card clicks in Cards view. BDD selectors updated across 7 step-def files to match renamed HTML classes.


### Ask Agy

**June 13 — Ask Agy landing — mobile chip grid redesign + dialog fixes (MATTGPT-113)** — `ff175e9`, `b7f88d5`
Mobile seed question chips redesigned as pill-shaped flex-wrap chips with short labels. Python mobile branch skips `st.columns()` on mobile (eliminates the stHorizontalBlock nuclear CSS rule conflict); desktop keeps 2-column grid with full questions. 3-tuples `(icon, short_label, full_question)` added to each chip. CSS: `.st-key-chip_grid` flex-wrap container with doubled-class specificity trick to beat global `stVerticalBlock gap: 4px` rule. Header height absolute-positioning fix shipped in `e7e079a`. Bonus fixes: Implementation Details grid (`details-grid`) single-column collapse on mobile corrected (two `1fr` rules → `repeat(2, 1fr)`); `deep-dive-card h3` font-size typo `8px` → `18px`.

**June 10 — How Agy dialog — mobile height compaction + stMain scroll reset (MATTGPT-110 follow-up)** — `8f9a1b5`, `be2872e`
Mobile viewport fix for the How Agy Searches dialog. CSS compaction across 5 selectors inside `@media (max-width: 640px)` in `_CSS` — `.search-card`, `.result-card`, `.result-wrapper`, `.cards-row`, `.pipeline-summary` padding/margin reductions totaling ~96px savings, bringing content from ~968px to ~872px against a ~595px usable area (Sections 1–2 fully visible on open; Section 3 reachable with one scroll). Scroll-to-top fix: `stMain.scrollTop = 0` added alongside existing `el.scrollTop = 0` in the scroll IIFE — `[data-testid="stMain"]` is Streamlit's real scroll container (confirmed via Chrome Claude DevTools; `window.scrollY` is always 0 under Streamlit's full-viewport flex layout). BDD regression guard: 2 scenarios covering scroll-to-top behavior added and passing.

**June 2 — How Agy Searches — migrate inline expander to `@st.dialog`, remove Technical Details block (MATTGPT-110)** — `37806a7`, `e24c1cb`
Replaced the inline collapsible expander on Ask Agy (Landing + Conversation views) with a `@st.dialog` overlay. Technical Details block removed — near-verbatim build content already covered in How I Built, sitting inside the runtime trust story where it didn't belong. Button label toggle and close-wiring JS removed from `ask_mattgpt_header.py`; `@st.dialog`'s built-in X / Escape / backdrop handles close. Bridge link added at bottom: "Want the technical details? See how I built it →". `show_how_modal` session state key and `render_modal_wrapper_start/end()` calls removed from both page files. BDD: 5/5 passing. CSS regression guards for navbar scope added in follow-up commit `e24c1cb`.

### Role Match

**June 2026 — Role Match sample JD cold-start affordance (MATTGPT-066)** — `6c39d8c`
Bundled with MATTGPT-067. See MATTGPT-067 entry below for full details — "Sample JD affordance" in the input controls section covers this ticket's scope.

**June 11–12 — Result panel + input polish bundle (MATTGPT-067)** — `6c39d8c`, `ac3d3dd`, `a2d002b`
Input controls: 30-word gate disables submit until sufficient JD text; Clear button (text link) empties textarea and pops all 5 session-state keys; Sample JD affordance ("Don't have a job description handy? / Try an example"). Summary block between legend and requirements: counts line (Required / Preferred tallies) + Discussion points (required gaps + partials + preferred gaps; preferred partials excluded). Legend relabeled "project evidence" / "verified skill"; card copy updated to "Verified skill" throughout. Post-result CTA copy changed to "Explore Matt's experience in depth." — honest framing that doesn't imply Agy has result context. UI fixes: right-column height anchor (`height_anchor = st.empty()`) prevents layout collapse during blocking LLM call; followup CTA gap rule scoped to `role_match_followup_block` container (was collapsing all inter-card gaps when results showed); `role_match_ev_*` expansion container gets 16px bottom margin to prevent overlay on next requirement card. BDD: 23/23 passing. Unit: 30/30 (`test_summary_block.py`).

### Explore Stories

**June 9 — My Work two-row permanent filter bar (MATTGPT-065)** — `765c14e`, `3015942`
Added a permanent two-row filter bar to My Work desktop. Row 1: Search / Industry / Capability. Row 2: Client / Role / Domain + Reset (always visible on desktop, CSS-hidden on mobile). `st.container(key="r2_row")` with border-top separator. `label_visibility="collapsed"` alone insufficient (label still takes vertical space) — Row 2 labels hidden via CSS as well. Mobile counterpart filed as MATTGPT-119.

**June 18 — AG Grid Client badge rendering — cellRenderer rewrite + Enterprise bundle drop (MATTGPT-132)** — `a809c57`
Fixed the AgGrid Client column badge in My Work Table view. Root cause: function-based `cellRenderer` fails in the st_aggrid React stack — the reconciler replaces the return value on rerender, losing the DOM node. Fix: class-based `ClientBadgeRenderer` using AG Grid 29's `init(params)` / `getGui()` contract, which returns the DOM element directly and bypasses React's reconciler. Also dropped `enable_enterprise_modules=False` to eliminate the license warning. Dark mode: Python-side detection via `st.get_option("theme.base")` passes hardcoded color values into `custom_css` at render time (CSS variables don't cross the AgGrid iframe boundary). Brief theme-toggle lag accepted as Streamlit architectural limitation.

**June 10 — AgGrid Table view — row cursor + purple hover color, dark-mode selector fix (MATTGPT-064)** — `3a5e1bc`, `6590450`
Two-part fix for AgGrid Table view styling. Root cause: CSS rules in `global_styles.py` cannot reach AgGrid's iframe — the iframe boundary blocks parent-doc stylesheets. Fix 1: Python `rowStyle = {"cursor": "pointer"}` on `GridOptionsBuilder` (bypasses iframe entirely). Fix 2: `components.html` JS injection reaching into `iframe.contentDocument` to set `--ag-row-hover-color: rgba(167,139,250,0.15)` and `--ag-selected-row-background-color: rgba(167,139,250,0.2)`. Dark-mode fix: guard selector changed from `.ag-theme-streamlit` (null in dark mode — actual class is `.ag-theme-streamlit-dark`) to `.ag-root-wrapper` (theme-agnostic). Three-fire timing pattern (immediate + 500ms + 1500ms) covers iframe load delay and post-rerun iframe recreation. Dead CSS removed from `global_styles.py`. Pattern documented in ARCHITECTURE.md as Pattern 5.

**June 10 — Retire how_i_built.py standalone route (MATTGPT-116)** — `9a55fbd`
Deleted `ui/pages/how_i_built.py` (standalone deep-link page fully superseded by `how_i_built_dialog.py`). Removed `?route=how-i-built` handler and `elif "How I Built"` render block from `app.py`; cleaned up `how_i_built_from` / `_deeplink_route` session state pops from `?nav=` handler. Removed 3 standalone-route BDD scenarios from `how_i_built.feature`; 5 dialog scenarios retained and passing. Items 2+3 (failing `test_desktop_shows_full_interface` + two-file revert) resolved as no-op — revert prescription was wrong; `window.innerWidth` + `screen_size_capture` approach is correct and test passes cleanly with current code.

**June 10 — My Work mobile — filter layout compaction (MATTGPT-123)** — `40aeb8e`
CSS-only changes to `global_styles.py`. Industry and Capability filters: label + dropdown inline on one row (`flex-direction: row` on the selectbox). Client/Role/Domain Row 2: 3-column grid, Streamlit labels hidden (`display: none`), field names injected via `::before` pseudo-element on the select control with `overflow: hidden` to suppress stray SVG title text. Reset filters button demoted to borderless underlined text link. Filters toggle made full-width via `stLayoutWrapper` + `stElementContainer` + `stButton` chain. Column stacker gained 5th `:not(:has([class*="st-key-r2_client_v2"]))` exclusion to preserve the 3-col grid. Search button alignment: `align-items: center` on stForm horizontal block, `gap: 0` on submit button column's vertical block, `margin-top: 3px` on `stForm`. stForm `align-items` split from `r2_row` rule (stForm → center; r2_row → flex-end). 4/4 BDD scenarios passing.

**June 10 — My Work mobile — "Filters ▾" toggle for Row 2 (Client, Role, Domain) (MATTGPT-119)** — `b65900e`
Added a "Filters ▾" toggle button to My Work, visible only on mobile (hidden on desktop via CSS). Tapping it toggles Row 2 visibility (Client, Role, Domain dropdowns) via `es_mobile_r2_open` session state; container key swap (`r2_row` ↔ `r2_row_open`) drives CSS show/hide without widget state loss. Required three CSS cascade fixes: (1) column-stacker rule gained 4th `:not(:has([data-testid="stFormSubmitButton"]))` exclusion — specificity (0,3,1) was overriding the stForm `flex-direction: row !important` rule; (2) facet rule gained same exclusion to prevent `flex-wrap: wrap` applying to the search form; (3) `[data-testid="stForm"] [data-testid="stColumn"]:last-child` rule added to block Streamlit's `min-width: calc(100% - 1.5rem)` from squeezing the submit button. BDD: 4/4 new scenarios passing, 2 regression guards confirmed.

---

## May 2026

### RAG Pipeline

**May 18 — Remove last_primary_client cross-query session state (MATTGPT-073)** — `3773c6b`
Option E applied. Removed `_last_primary_client` from `diversify_results` in `backend_service.py`. The mechanism stored the previous query's pinned client in session state and used it to demote stories on subsequent queries — making retrieval output for query N dependent on queries 1…N-1. Production log analysis (82 queries, 24 sessions) showed 45% of consecutive pairs were demotion-eligible. Post-removal eval: 70/70 (100%). Architectural decision recorded as ADR 019.

**May 18 — diversify_results() pinning bug resolved as side effect of MATTGPT-073 (MATTGPT-021)**
The `diversify_results()` rewrite during MATTGPT-073 corrected the two original bugs: slot #1 is now pinned unconditionally (no client-count toward the diversity limit), and score ordering is preserved after the diversity pass. The `_last_primary_client` cross-query session state mechanism that was the root cause is gone. Confirmed in `backend_service.py:1242-1315` — no session state written, no demotion applied to slot #1.

**May 18 — MattGPT portfolio story contamination in leadership queries resolved (MATTGPT-061)** — `02f6c79`
The dominant contamination mechanism — session-state demotion in MATTGPT-073 — removed. Validated against 12 production-traffic leadership queries: 11/12 clean responses (91.7%). 61-query eval suite 100% passing. Single residual failure (Q2 "transformations" polysemy) is a structural semantic search limit scoped to hybrid retrieval (see BACKLOG).

### Ask Agy

**May 25 — Nonsense rejection banner — branch-aware copy + contextual chip sets (MATTGPT-071)** — `c642575`
Differentiated copy and chip sets across all four reason branches in `render_no_match_banner`. Each rejection reason (rule:*, personal, out_of_scope) gets contextually appropriate copy and chips rather than a uniform fallback. Production-validated May 26: all branches render correct copy on both Ask Agy and My Work surfaces.

### UI Redesign Sprint

**May 27 — About Matt content polish bundle (MATTGPT-068)** — `efd6e00`
Sample questions converted from `<li>` text to `st.button` chips routing to Ask Agy via `seed_prompt` + `__ask_from_suggestion__` pattern. Code block wrapped in `<details><summary>` expander (collapsed by default). DevOps card merged into CI/CD Pipeline card. CTA card rendered as `st.container(key="about_matt_cta_card")` for true DOM nesting of chip buttons. BDD: Red/Red/Green cycle completed.

**May 29-30 — Home hero CTA inversion + seniority signal (MATTGPT-087 + MATTGPT-092)** — `ef133b2`
Role Match promoted to primary hero CTA; Ask Agy demoted to secondary. Explore Stories CTA removed from hero (reached via nav). Recruiter persona finding: Role Match was invisible when Ask Agy was primary. Seniority signal added to My Profile as a "LEVEL: Senior leader" signals panel — scope/outcome anchor, not a title chip, to avoid the title trap.

**May 29 — Explore Stories default state: exclude Professional Narrative + sort by date (MATTGPT-098)** — `856c908`
On default load, exclude Category == "Professional Narrative" (10 stories) and sort by Start_Date descending. Mirrors Timeline's EXCLUDED_ERA behavior. Behavioral stories remain reachable via Category filter. Applied to both Table and Cards views. Prerequisite for MATTGPT-104 math reconciliation.

**May 30 — Navigation labels rename (MATTGPT-100)** — `3c97d97`
Renamed tabs to: Home / My Work / Ask Agy / Role Match / My Profile. Updated across ~50 files: app.py tab definitions, navbar.py, session_state active_tab values, BDD fixtures, and landing page routing references. Mobile nav required separate handling (Streamlit transforms key spaces to dashes in CSS class names).

**May 30 — Why Agy? modal + "?" badge on Agy avatar (MATTGPT-101)** — `e1c2699`
New `why_agy_dialog.py` using `@st.dialog`. Badge wired across 7 surfaces: hero (Home), header + landing body (Ask Agy), banking header, cross-industry header, My Work header, Role Match header. Desktop-only in headers (30px mobile avatar too small); body/hero avatars show badge on all viewports. Sequential dialog pattern (`elif` not `if`) prevents StreamlitAPIException when Why Agy and How I Built open in sequence.

**May 30 — How I Built MattGPT dialog (MATTGPT-102)** — `b6ab8ae`
Replaced standalone `how_i_built.py` page with `@st.dialog` component. Removed `?route=how-i-built`, `?nav=`, `?from=` handlers from `app.py`; deleted standalone page; cleaned up `SECONDARY_SURFACES` and related session state keys. Content: subtitle, The Problem card, Tech Stack 6-item grid, System Architecture Flow (5-step lifecycle), Runtime Pipeline (numbered purple circles), Detail cards, CTA row.

**May 30 — Banking + Cross-Industry story count math reconciliation (MATTGPT-104)** — `19e03ba`
Landing hero/stats and Home card meta aligned to post-Era counts (32 Banking, 48 Cross-Industry), matching Timeline and My Work (post MATTGPT-098). Depended on MATTGPT-098 shipping first to establish post-Era as the cross-surface convention.

**May 31 — Navbar desktop layout: brand-left + space-between (MATTGPT-106)** — `3c97d97`
Added MattGPT brand element to desktop navbar left. Layout changed from `justify-content: space-evenly` (5 nav items full-width) to `space-between` (brand left, 5 items right). Brings desktop into structural alignment with mobile navbar and wireframe.

**May 31 — Home category cards redesign: 3-column grid + unified card treatment (MATTGPT-107)** — `19e03ba`
Redesigned from 2-column to 3-column grid. Unified light-bg treatment across all 6 cards (purple gradient removed from Banking/Cross-Industry top cards). Compact content (~3 lines vs ~5). Card itself is click target — inline buttons and italic example-question lines removed.

### Documentation Alignment

**May 11 — Align how_agy_modal + about_matt pipeline depictions to current code (MATTGPT-057)** — `ee730de`, `ec351a3`, `9a0c0e8`
Replaced stale architecture descriptions in user-facing pages with the current 5-stage pipeline shape (nonsense filters → semantic router → Pinecone → confidence gate → LLM). Dropped factually-false claims: "Semantic + keyword hybrid scoring" (W_KW = 0.0; pipeline is pure semantic), "GitHub Actions / CI/CD pipeline" (no CI exists — see MATTGPT-039), and unverified "6 Industries" stat. Touched `ui/pages/about_matt.py` "How I Built MattGPT" pseudocode, `ui/components/how_agy_modal.py` 3-stage framing expanded to 5-stage. Follow-up commits restyled the modal (pipeline as hero, demoted result pills) and stripped emojis from about_matt + footer for visual weight on deep-dive cards.

### Triage Agent (Cowork-orchestrated JD triage — new)

**May 10 — Initial scaffold for Cowork-orchestrated JD triage**
Enables Cowork (Claude Desktop) to drive JD triage against the existing engine by exposing it as a CLI surface and putting orchestration assets in version control as source of truth. `scripts/assess_jd.py` wraps `run_assessment()` + `compute_recommendation()` from `services/jd_assessor.py`, reads JD from stdin, and emits a schema-versioned JSON envelope; self-bootstraps `sys.path` so it works regardless of invocation context (subprocess, Cowork shell, pytest). `agent/triage/synthesis_prompt.md` carries the three-layer assessment logic (capability + filter + thin fit) with Pass-mode voice for high-volume discovery readiness; `agent/triage/filter_config.json` encodes Matt's hard rules (geographic, comp) + redline phrases. `agent/README.md` documents the layout and the Cowork setup checklist. `agent/discovery/` reserved as a placeholder for v2 ATS-based push-model discovery. `tests/unit/test_assess_jd.py` covers three contract surfaces: empty stdin (error JSON), missing JSONL (graceful error JSON), and valid-JD envelope shape (engine mocked in-process via `unittest.mock`). Architecture follow-up to update `mattgpt-design-spec/architecture.md` pending separately.

### Infrastructure

**May 2026 — secrets.toml local-prod parity + dead private_access_code cleanup (MATTGPT-085)**
`MATTGPT_PRIVATE_BYPASS_TOKEN` added to local `.streamlit/secrets.toml`; dead `private_access_code` entry removed. Local BDD suite now passes the 7 lock-glyph Role Match scenarios without environment variable prefix workarounds. `test_role_match.py` docstring updated (two locations) to remove the rejected command-line env-var prefix workflow and point at `secrets.toml` parity as the convention.

**May 6 — Reduce log noise on Streamlit Cloud (file watcher → poll)**
Streamlit's default watchdog (inotify) file watcher exhausted the kernel's per-host inotify instance limit on Streamlit Cloud's multi-tenant VMs, spamming the production log with non-fatal `OSError: [Errno 24] inotify instance limit reached` tracebacks (one per watched directory). Added `.streamlit/config.toml` with `fileWatcherType = "poll"` — no inotify overhead on Cloud (which never benefited from file watching anyway, since deploys come from git push), and the "Source file changed" toast still fires locally via polling. `"none"` rejected because it would silently disable the local toast.

### Role Match (Phase 4 in flight — see MATTGPT-012)

**May 4 — Committed 20 BDD scenarios for Role Match Phase 4** — `0d6285b`
Design contract for the private view: password gate edge cases, lock icon affordances, session persistence, agentic bypass (`X-Mattgpt-Bypass-Token` / `MATTGPT_PRIVATE_BYPASS_TOKEN`), recommendation matrix anchored to `compute_recommendation()` in `services/jd_assessor.py`, and locked↔unlocked transitions. Implementation deferred to a future session — step definitions co-author with implementation slices per CLAUDE.md testing protocol.

---

## April 2026

### Process & Infrastructure

**Apr 28 — Fix Playwright sync/async clash in BDD test suite** — `c889ab2`
Both `test_explore_stories.py` and `test_role_match.py` defined their own session-scoped Playwright fixtures with their own `_playwright_instance` globals. Running them in the same pytest session caused the second `sync_playwright().start()` call to clash with the asyncio event loop already owned by the first. Moved shared fixtures to `tests/bdd/steps/conftest.py`. BDD suite went from 10 failures to 3 (remaining 3 are pre-existing).

**Apr 28 — Add commit/push separate-gates rule to CLAUDE.md** — `1a2902c`
Replaced the previous "never push without confirmation" rule with a more specific version: commit and push are two separate gates requiring two separate approvals. Combining `git commit && git push` is not acceptable. Includes April 2026 incident reference.

### Role Match Feature (Phases 1-3 Complete)

**Apr — Role Match logging — assessment, chip click, and action button events** — `a3b3d84`
**Apr — BDD scenarios for Role Match logging (14 scenarios)** — `0dd2ee9`
**Apr — Fix AgGrid compatibility with Streamlit 1.50.0** — `fca174d`
Pre-import components submodule.

**Apr — Fix story detail STAR section spacing inside Role Match inline expansion** — `99053ee`
**Apr — Fix Role Match textarea persistence across page navigation** — `8386d8d`
Option A prefilter pattern.

**Apr — Improve JD extraction** — `455cac3`
Narrative prose mining, implicit requirements consumption, strong-without-evidence enforcement, explicit-bullet protection.

**Apr — Rebuild Role Match results panel — v3 design + Report button + UTM attribution** — `5e01460`
**Apr — Update Role Match BDD scenarios for mockup v2 design lock** — `211d04a`
**Apr — Fix Role Match chip toggle bug** — `c81dc35`
Refactor from JS bridge to `st.button` pattern. Roughly 100 lines of JS bridge code eliminated.

**Apr — Update Role Match mobile gate threshold from 768px to 1024px** — `f033c64`
Update BDD scenario wording.

**Apr — Add show_actions kwarg to render_story_detail** — `f6b1f71`
Default True, backwards compatible.

**Apr — BDD scenarios for Role Match story chip inline expansion (6 scenarios)** — `80024de`
**Apr — Fix navbar/hero gap regression caused by extra st.markdown call** — `af09041`
Documented layout spacing rule in CLAUDE.md.

**Apr — Phase 3 checkpoint: action buttons, share/export, BDD step definitions** — `9da8b59`
**Apr — BDD scenarios for Role Match action buttons (6 scenarios)** — `37786bb`
**Apr — Add Role Match page with recruiter view and pipeline wiring** — `9aec1a3`
**Apr — Promote JD pipeline functions into services/jd_assessor.py** — `119441d`
**Apr — BDD scenarios for Role Match page (27 scenarios)** — `043e6ba`
**Apr — Distinguish required vs preferred gaps in recommendation logic** — `8a6b203`
**Apr — Add matt_profile.json, dynamic grounding, evidence_type, entity aliases** — `8e24799`
**Apr — Add JD assessment prompt v1, BDD scenarios, and recommendation logic** — `7f3ddc0`

### Analytics — Logger Schema Extension (MATTGPT-013 Complete)

**Apr — 32-column query logger schema shipped to production** — `a3b3d84` and subsequent commits
Expanded `services/query_logger.py` from initial implementation to full 32-column schema. Captures event types (query, feedback, redirect, role_match_assessment, role_match_chip_click, role_match_action), query metadata (intent family, confidence, result count), user/session signals (user-agent, screen width, timezone, referrer), UTM attribution (source, medium, campaign, content, term), Role Match outcomes (role title, company, JD format, required/preferred/strong/partial/gap counts, session ID, story title, client), and feedback ratings. Write-only to Google Sheets. Downstream analytics work tracked separately (MATTGPT-045 dashboard, MATTGPT-046 latency, MATTGPT-047 cost tracking).

### Other April Work

**Apr — Add Chrome/103.0.0.0 stale bot UA to MONITORING_BOT_SIGNATURES** — `cfe1704`
**Apr — Add HeadlessChrome to MONITORING_BOT_SIGNATURES** — `2f42057`
**Apr — Add dark mode override for thinking indicator backdrop opacity (0.4 → 0.6)** — `a07ab06`
**Apr — Fix mobile gate false positive on Streamlit Cloud** — `dd4314d`
Use `screen.width` instead of `innerWidth`.

**Apr — Fix navbar column squishing caused by Explore Stories CSS leak** — `1a1e86e`
**Apr — Update wrong-person backlog: recommend Option 2 (canonical phrases)** — `63eb7f2`
**Apr — Fix 2 test bugs, update sacred vocabulary, backlog 6 code bugs** — `66818d7`

---

## March 2026

### Data Quality

**Mar — diversify_results Pinning Fix**
`diversify_results()` was reordering stories and displacing the primary story (e.g., D&F query: Row 40 ranked #1 but LLM talked about Row 28/AmEx). Fixed pinning logic so primary story stays #1 after diversification.

**Mar — IQ Differentiation (Leadership + CIC)**
Leadership and CIC stories lacked differentiation in Situation/Use Case fields — Pinecone couldn't distinguish them. Data quality pass on Excel master enriched Situation fields with resistance narratives and specific context.

**Mar — TDD/BDD Story Rewrite**
TDD methodology story had weak Situation field, BDD story surfacing instead for TDD queries. Rewrote Situation with resistance narrative, re-ingested data.

### RAG & Voice

**Mar — CIC Entity Alias**
"CIC" acronym not recognized by entity detector. Added `ENTITY_ALIASES` to `config/constants.py`, alias check in `detect_entity()`. "CIC" now resolves to Division: Cloud Innovation Center.

**Mar — SYNTHESIS_DELTA Reconciliation**
Rewrote with tension-first flow (WHY 30-40%, HOW 40-50%, WHAT 10-20%), coverage rule changed to "lead with 2-3 most relevant, don't force-fit."

**Mar — Voice Guide V2 Update**
Reconciled WHY=tension/stakes across `05-agy-voice-guide.md`, `prompts.py`, `ARCHITECTURE.md`.

### Eval & Code

**Mar — Eval Cases for "Tell me more about: [Title]"** (legacy #2)
Q53-Q57 added as regression guards covering title-based and entity-based queries. Title soft-filtering working correctly.

**Mar — Delete META_SENTENCE_PATTERNS Regex** (legacy #5)
Band-aid for prompt conflict; monitoring period complete. Prompt rewrite eliminated the root cause.

**Mar — Remove boost_narrative_matches()** (legacy #6)
Title now embedded in Pinecone. Semantic search handles narrative story ranking naturally.

**Mar — Centralize Hardcoded Values** (legacy #7)
Thresholds, model names, token limits scattered across 6+ files. `config/constants.py` created as single source of truth.

**Mar — Pinecone Index as Env Var** (legacy #18)
`index_name="portfolio-stories"` was hardcoded. Moved to environment variable via `get_conf()` pattern.

**Mar — Fix "Builder/Modernizer" Verbatim Quoting** (legacy #30)
Agy was quoting poetic language from 5PSummary verbatim in synthesis responses. Data fix — updated 5PSummary to concrete language in Excel master, re-indexed.

**Mar — New Development Stories** (legacy #31-35)
5 stories added in Feb 3 session. 130 stories total.

**Mar — Dead Code Cleanup (Partial)** (legacy #8)
Initial sweep complete. Remaining work tracked in BACKLOG.

---

## February 2026

**Feb — Excel→JSONL Script Bug Fixes** (legacy #38)
Fixed `normalize()` for pandas NaN, `split_bullets()` for Excel escape apostrophe.

**Feb 3 — New MattGPT Development Stories** (legacy #39)
Added 5 stories: Why Hire Matt, Entity Gate Removal, Eval-Driven Development, BDD, AI-Assisted Workflows. 130 total.

**Feb — Design Spec Testing Docs Consolidation** (legacy #40)
Consolidated into `docs/11-testing-and-quality.md` covering 3-layer strategy.

**Feb 1 — Stale Story on Return to Explore Stories** (legacy #23)
Widget version incrementing in `_clear_explore_state()`.

**Feb 1-2 — BDD/E2E Tests for Explore Stories State Machine** (legacy #25)
43 BDD scenarios using pytest-bdd + Playwright. All passing.

---

## January 2026

### RAG Pipeline Cleanup (Jan 29)
- Entity Gate removed (was causing false rejections)
- `classify_query_intent` LLM removed (redundant with semantic router)
- Eval improved from 96.4% to 98.1%

### Individual Items

**Jan 22 — Multi-Field Entity Blind Spot** (Sovereign Backlog #1)
Entity filter now searches 6 fields with Pinecone `$or` operator.

**Jan 22 — Dynamic Prompting** (Sovereign Backlog #3)
`generate_dynamic_dna()` derives clients by industry from story data.

**Jan 22 — UI Metrics Hydration**
All project/client counts derived dynamically from JSONL across 4 files.

**Jan 26 — Fix Prompt Conflict** (legacy #1)
Created `prompts.py` with BASE_PROMPT + DELTA architecture. Meta-commentary failures reduced from 10/31 → 1-2/31.

**Jan 26 — Semantic Router Fail-Open Handling** (legacy #9)
Verified fail-open behavior: returns `(True, 1.0, "", "error_fallback")` on exception.

**Jan 26 — Threshold Calibration** (legacy #10)
Lowered SOFT_ACCEPT from 0.72 to 0.40. Entity Gate removed entirely Jan 29.

**Jan 26 — Remove ENTITY_NORMALIZATION Hardcoded Map** (legacy #11)
Semantic search handles variations naturally. Removed map and fuzzy matching.

**Jan 26 — Add Observability Logging** (legacy #12)
Added `[QUERY_REJECTED]` and `[API_ERROR_DETECTED]` log tags.

**Jan 28 — Audit Excel Master for Corporate Filler** (legacy #4)
Deleted BANNED_PHRASES entirely — was testing for imaginary problems.

**Jan 30 — Fix SEARCH_TOP_K Conflict** (legacy #14)
Centralized to `config/constants.py` with value 10.

**Jan 30 — Deeplink Regression** (legacy #20)
Fixed page offset calculation for story deeplinks.

**Jan 30 — Search State Clearing** (legacy #21)
Surgical fix: only clear `active_story` when query actually changes.

**Jan 30 — "Ask Agy About This" Regression** (legacy #22)
Fixed by surgical state clearing in legacy #21.

**Jan 31 — 6 Sources on Surgical Queries** (legacy #24)
Added `query_intent` check: synthesis gets 6 sources, surgical gets 3.
