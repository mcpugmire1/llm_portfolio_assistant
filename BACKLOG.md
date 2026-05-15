# MattGPT Backlog

Work state for the MattGPT project. The matrix below is the scannable view. Detail blocks for each item follow, linked by ID. Completed items live in `CHANGELOG.md`. Architectural decisions live in `docs/ADR.md`. Current system state lives in `ARCHITECTURE.md`.

---

## Matrix

| ID | Title | Status | Priority | Type | Logged |
|---|---|---|---|---|---|
| [MATTGPT-012](#mattgpt-012) | Role Match — Phase 4: Private View | In Progress | High | Action | Apr 2026 |
| [MATTGPT-014](#mattgpt-014) | Audit + split skipped Role Match BDD scenarios (BDD for structure, evals for content) | Open | High | Action | Apr 28, 2026 |
| [MATTGPT-015](#mattgpt-015) | JPM Payments IQ Differentiation | Open | High | Action | Mar 2026 |
| [MATTGPT-016](#mattgpt-016) | Semantic Router — Wrong-Person Query Detection | Decided Against | High | Issue | Apr 2026 |
| [MATTGPT-017](#mattgpt-017) | Wire skipped Role Match logging BDD scenarios (Playwright click + mocked Sheets write) | Open | Medium | Action | Apr 28, 2026 |
| [MATTGPT-018](#mattgpt-018) | Page-Load Flicker | Open | Medium | Issue | Pre-Apr 2026 |
| [MATTGPT-019](#mattgpt-019) | Story Count Copy — Replace "130+" with "Over 100" | Open | Low | Refactor | Pre-Apr 2026 |
| [MATTGPT-020](#mattgpt-020) | Simplify backend_service.py | Decided Against | Medium | Refactor | Pre-Jan 2026 |
| [MATTGPT-021](#mattgpt-021) | diversify_results() Pinning Bug | Open | Medium | Issue | Apr 2026 |
| [MATTGPT-022](#mattgpt-022) | Data Quality Cleanup Journey Story | Open | Medium | Action | Mar 2026 |
| [MATTGPT-039](#mattgpt-039) | Automated Regression Detection (GitHub Actions) | Open | Medium | Action | Apr 29, 2026 |
| [MATTGPT-040](#mattgpt-040) | Eval Coverage Gaps — Follow-up Queries | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-023](#mattgpt-023) | LLM Meta-Commentary on Q20 (Stochastic) | Decided Against | Low | Issue | Apr 2026 |
| [MATTGPT-024](#mattgpt-024) | Clarify Hybrid Scoring | Decided Against | Low | Refactor | Pre-2026 |
| [MATTGPT-025](#mattgpt-025) | Add Error Handling Tests | Decided Against | Low | Action | Pre-2026 |
| [MATTGPT-026](#mattgpt-026) | Clarify Layer Ownership | Decided Against | Low | Refactor | Pre-2026 |
| [MATTGPT-027](#mattgpt-027) | Quarterly Intent Review | Decided Against | Low | Action | Jan 2026 |
| [MATTGPT-028](#mattgpt-028) | Share Link Copy Functionality | Decided Against | Low | Issue | Pre-2026 |
| [MATTGPT-029](#mattgpt-029) | Low-Confidence Banner Edge Cases | Decided Against | Low | Issue | Pre-2026 |
| [MATTGPT-031](#mattgpt-031) | Semantic Router Error Path Coverage | Decided Against | Low | Action | Pre-2026 |
| [MATTGPT-032](#mattgpt-032) | LLM Response Broken Markdown | Decided Against | Low | Issue | Pre-2026 |
| [MATTGPT-033](#mattgpt-033) | Ask Agy Button Shifts on Focus | Open | Low | Issue | Pre-2026 |
| [MATTGPT-035](#mattgpt-035) | Eval Modernization — Semantic Scoring | Open | Low | Spike | Pre-2026 |
| [MATTGPT-041](#mattgpt-041) | 5P Dimensional Drill-Down | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-042](#mattgpt-042) | 5P Pattern Taxonomy | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-043](#mattgpt-043) | Humane Framing — Intent-to-Tone Mapping | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-044](#mattgpt-044) | Pattern Insights — Structured Templates | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-045](#mattgpt-045) | Analytics Dashboard | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-046](#mattgpt-046) | Latency Benchmarks | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-047](#mattgpt-047) | Cost Tracking | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-058](#mattgpt-058) | Replace dark-theme setInterval polling with MutationObserver | Decided Against | Low | Refactor | May 12, 2026 |
| [MATTGPT-059](#mattgpt-059) | Add Theme-based prefilter dimension to category cards | Decided Against | Low | Spike | May 12, 2026 |
| [MATTGPT-060](#mattgpt-060) | BDD coverage gap — assert post-navigation page state, not just navigation | Open | Medium | Action | May 12, 2026 |
| [MATTGPT-061](#mattgpt-061) | MattGPT portfolio story contaminating organizational leadership queries | Open | Medium | Issue | May 13, 2026 |
| [MATTGPT-062](#mattgpt-062) | Semantic router cache silently uses stale embeddings when VALID_INTENTS changes | Open | Medium | Refactor | May 14, 2026 |
| [MATTGPT-063](#mattgpt-063) | Wrong-person queries with names outside nonsense regex produce confused-context RAG answers | Open | Medium | Issue | May 14, 2026 |
| [MATTGPT-064](#mattgpt-064) | Explore Stories — Table row hover/cursor doesn't apply to data cells (AgGrid selector fix) | Open | Low | Issue | May 15, 2026 |
| [MATTGPT-065](#mattgpt-065) | Explore Stories — Polish bundle (filter UX, empty states, story details) | Open | Medium | Action | May 15, 2026 |
| [MATTGPT-066](#mattgpt-066) | Role Match — Sample JD / "Try a sample role" cold-start affordance | Open | Medium | Action | May 15, 2026 |
| [MATTGPT-067](#mattgpt-067) | Role Match — Result panel and input polish bundle | Open | Low | Action | May 15, 2026 |
| [MATTGPT-068](#mattgpt-068) | About Matt — Content polish bundle (clickable questions, code expander, anchor nav, stat consolidation) | Open | Medium | Action | May 15, 2026 |
| [MATTGPT-069](#mattgpt-069) | Home — Stats label contrast (light mode WCAG AA) | Open | Low | Issue | May 15, 2026 |
| [MATTGPT-070](#mattgpt-070) | Ask MattGPT — Suggestion button cursor pointer | Open | Low | Issue | May 15, 2026 |
| [MATTGPT-071](#mattgpt-071) | Nonsense rejection banner — redirect chips + hint text (branch-aware copy) | Open | Medium | Action | May 15, 2026 |
| [MATTGPT-010](#mattgpt-010) | Cross-Browser Testing | Decided Against | Low | Action | Pre-2026 |
| [MATTGPT-048](#mattgpt-048) | Portfolio Integration (Notion, LinkedIn sync) | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-049](#mattgpt-049) | Job Fit Broader Scope (cover letter export, LinkedIn auto-extract) | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-036](#mattgpt-036) | Entity Cluster Promotion Override | Decided Against | — | — | Pre-2026 |
| [MATTGPT-037](#mattgpt-037) | Score Gap Override (Generic-Above-Named) | Decided Against | — | — | Pre-2026 |
| [MATTGPT-038](#mattgpt-038) | Centralize Constants (Duplicate of legacy #7) | Decided Against | — | — | Pre-2026 |
| [MATTGPT-050](#mattgpt-050) | Dynamic Intent Expansion | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-051](#mattgpt-051) | User Feedback Loop — Closed-Loop Retraining | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-052](#mattgpt-052) | A/B Testing on Thresholds | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-053](#mattgpt-053) | A/B Testing Framework | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-054](#mattgpt-054) | Query Rewriting and Spell-check | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-055](#mattgpt-055) | PWA Capabilities | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-056](#mattgpt-056) | True Wireflows (Miro) | Decided Against | — | — | Apr 29, 2026 |

---

## Schema

Each detail block uses these fields. Not every field is required for every item.

- **Status:** Open / In Progress / Done / Parked / Decided Against
- **Priority:** High / Medium / Low
- **Type:** Issue / Action / Spike / Refactor
- **Issue:** What's wrong or what needs to happen
- **Root cause:** Why (when known)
- **Fix:** Approach
- **Affects:** What's currently broken or impacted
- **Dependencies:** What needs to happen first
- **Logged:** Date diagnosed
- **Resolved:** Date + commit hash (when Done — moves to CHANGELOG.md)

---

## Detail Blocks

### MATTGPT-012
**Role Match — Phase 4: Private View**

- **Status:** In Progress
- **Priority:** High
- **Type:** Action
- **Spec:** `docs/specs/role-match.md`
- **Issue:** Phase 4 (private fit assessment, lock icon, password gate) not yet implemented. Phases 1-3 are in production.
- **Fix:** Build the private view with overall fit score (High/Medium/Low), gap section, recommendation (Apply/Consider/Pass), password-gated via discreet lock icon in nav bar far right. Agentic access bypasses UI gate via environment secret.
- **Dependencies:** BDD scenarios for password gate behavior must be written and committed before implementation (per CLAUDE.md testing protocol)
- **Logged:** April 2026

**Phase 4 progress (May 4, 2026)**
- BDD scenarios committed as `0d6285b` — 20 scenarios appended to `tests/bdd/features/role_match.feature` covering: password gate edge cases (4), lock icon affordances (4), session persistence (3), agentic bypass (3), recommendation matrix (4), locked↔unlocked transitions (2). Total Phase 4 scenarios in the design contract: 28 (8 prior + 20 new).
- **Recommendation thresholds anchor to `compute_recommendation()` in `services/jd_assessor.py:367`.** All branches present (Apply / Consider / Pass + 0-requirements edge case); no missing branches to flag.
- **Bypass mechanism:** `X-Mattgpt-Bypass-Token` request header compared against `MATTGPT_PRIVATE_BYPASS_TOKEN` env var. Both are referenced as named constants in code per CLAUDE.md (no magic strings in guards). Refresh re-locks; tab-scoped; env var unset fails closed silently.
- **Step definitions deferred.** Scenarios are unbound (no `@scenario(...)` decorators yet). Implementation slices co-author with step definitions and bindings per CLAUDE.md testing protocol — implement password gate, then bind those scenarios; implement bypass header, then bind those; etc.

**Placement decision (May 5, 2026)**
- Lock icon mounts on the Role Match page (top-right of results panel), NOT in the navbar.
- **Why:** Proximity. The lock pertains to the results experience — locked state shows recruiter view, unlocked adds the private fit assessment overlay. UI controls should sit visually adjacent to what they control.
- **History:** Decision was made in a prior conversation, lost during slice 1 implementation (which placed the lock in the navbar), and surfaced again during visual review of the running app. Slice 1 commit `5c48567` was amended (not pushed) to fix the placement. Documented here as the durable record.

**Production deployment dependency (May 6, 2026)**
- Slice 1 (and all subsequent Phase 4 slices) requires `MATTGPT_PRIVATE_BYPASS_TOKEN` set in Streamlit Cloud secrets to function in production.
- Without it, the lock icon renders, the popover opens, but submission is a silent no-op (fail-closed by design — production state must not leak).
- Set via Streamlit Cloud dashboard → Settings → Secrets, NOT committed to repo.
- Local dev uses inline env var or shell export (e.g. `MATTGPT_PRIVATE_BYPASS_TOKEN=test-bypass-token streamlit run app.py`); production uses the Streamlit Cloud secret manager.

---

### MATTGPT-014
**Audit + split skipped Role Match BDD scenarios (BDD for structure, evals for content)**

- **Status:** Open
- **Priority:** High
- **Type:** Action
- **Issue:** 17 BDD scenarios in `test_role_match.py` skipped because they depend on OpenAI + Pinecone calls. Coverage area: match results, evidence chips, profile evidence, preferred qualifications, gap explanations, no-fit-score in recruiter view.
- **Decision (May 14, 2026 rationalization):** The original three-option framing (mock / real backends / snapshot) was wrong. It assumed BDD was the right tool for all 17 scenarios. It isn't. The 17 are a mix of two test shapes that need different tools:
  - **Structural rendering** (does the chip render? does the recruiter view hide the fit score? does the page navigate correctly?) → BDD with mocked OpenAI/Pinecone responses. Deterministic, fast, validates UI plumbing.
  - **Response content quality** (does the gap explanation correctly identify what's missing? does the right story surface as evidence?) → Eval framework (`tests/eval_rag_quality.py` pattern). Concept-cluster assertions, accepts LLM stochasticity.
- **Why this resolves the stuck spike:** Trying to BDD content questions is the trap — mocks lie about LLM behavior, real backends are slow/costly, snapshots brittle against LLM drift. The right answer is to *not* BDD the content questions at all.
- **Concrete next action (Action, not Spike):**
  1. Audit the 17 skipped scenarios. Categorize each as **Structural** or **Content**.
  2. Structural ones (likely 8-10 of 17): rewrite with mocked OpenAI/Pinecone fixtures, unskip, include in the pre-commit pytest gate.
  3. Content ones (likely 5-7 of 17): convert to entries in `tests/eval_rag_quality.py` (concept clusters, min_matches), delete the BDD versions.
  4. Anything that doesn't fit either bucket: delete or escalate as its own ticket.
- **Affects:** 17 skipped tests in `test_role_match.py`. Also blocks the pytest-in-pre-commit gate goal (a multi-minute test run isn't viable for pre-commit).
- **Logged:** April 28, 2026 / **Reframed:** May 14, 2026

---

### MATTGPT-015
**JPM Payments IQ Differentiation**

- **Status:** Open
- **Priority:** High
- **Type:** Action
- **Issue:** JP Morgan payments stories lack differentiation in Situation/Use Case fields — Pinecone can't distinguish them from other JPM work.
- **Fix:** Data quality pass on JPM payments stories in Excel master, similar to CIC/Leadership differentiation done in March 2026.
- **Logged:** March 2026

---

### MATTGPT-016
**Semantic Router — Wrong-Person Query Detection**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** High (was)
- **Type:** Issue
- **Why not:** May 14, 2026 investigation surfaced two facts that invalidated the ticket's framing:
  1. **Production already rejects these queries** via `nonsense_filters.jsonl` regex (catches `elon musk`, `jeff bezos`, `tell me a joke`, etc.) — completely upstream of the semantic router. The 3 failing unit tests call `is_portfolio_query_semantic()` in isolation, bypassing the actual production pipeline. The tests were aimed at the wrong gate.
  2. **The proposed canonical-phrases fix doesn't generalize.** During implementation, added wrong-person phrases to `out_of_scope` + family-based `is_valid` logic. Made the 3 specific tests pass. But the query "What's it like to work with Donald Trump?" still produced a confused-context RAG answer in BOTH production and local-with-fix — Trump isn't in the nonsense regex AND the canonical phrases don't generalize to the "What's it like to work with X" structural shape. So the fix adds redundant coverage for exact shapes already covered upstream while failing to address the real failure mode (names outside the regex with structural shapes outside the canonical phrases).
- **Real unsolved problem:** filed separately as MATTGPT-063 with the Trump query as evidence.
- **Action taken:** code changes from the in-progress fix reverted. Test scaffold from Step 1 (commit `bc280a2`) remains in main; cleanup of the 3 wrong-layer test cases + Step 1 speculative scaffolding deferred to a future small commit.
- **Original ticket context (preserved below for history):**
- **Issue:** Queries about other people score high against valid intent families. Bezos leadership query scores 0.664 as "leadership" — strong match to a wrong subject.
- **Root cause:** Semantic router has no entity/person detection. Only checks embedding similarity to intent families.
- **Fix (rejected):** Add canonical wrong-person phrases to `out_of_scope` family. Same mechanism that already handles off-topic queries — fills a gap, not a new gate layer.
- **Rejected approaches:** Person-name detection before routing (adds gate layer, history shows added gates create complexity and get backed out); lower SOFT_ACCEPT threshold (tried before, caused false rejections on legitimate queries).
- **Affects:** 3 failing tests (Bezos, Elon Musk, "Tell me a joke" scoring 0.429 as "behavioral")
- **Logged:** April 2026 test audit / **Closed:** May 14, 2026

---

### MATTGPT-017
**Wire skipped Role Match logging BDD scenarios (Playwright click + mocked Sheets write)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** 6 BDD scenarios in `test_role_match_logging.py` skipped because they require Streamlit's button click and session state machinery at runtime. Covers chip interactions (2), action button wiring (3), session correlation across interaction types (1).
- **Decision (May 14, 2026 rationalization):** Original Spike framing is no longer accurate. Since April 28, we've quietly proven the runtime-testing pattern across other work — Banking landing scenarios, Cross-Industry landing scenarios, Home page card click scenarios, chip CX scenarios — all run Playwright against a live Streamlit instance, click hidden buttons via `dispatch_event("click")`, and assert post-rerun state. Streamlit runtime testing isn't an open question anymore.
- **What these 6 scenarios add beyond the existing pattern:** the assertion target is a **Google Sheets logging write**, not a UI state change. The wrinkle is mocking the Sheets writer so the test doesn't hit the real sheet. Same shape as `tests/unit/test_query_logger.py` (committed May 13, 2026), which mocks `Thread` to assert log-call payloads without writing to Google Sheets.
- **Concrete next action (Action, not Spike):**
  1. For each of the 6 skipped scenarios, identify the logging call path (`log_role_match_action`, `log_role_match_chip_click`, `log_role_match_assessment`, etc.).
  2. Apply the existing Playwright pattern for the click interaction (dispatch_event on hidden Streamlit button keyed for the action).
  3. Mock `services.query_logger._append_row` (or the underlying `Thread` call — same pattern as `test_query_logger.py::TestLogQueryBotFilter`) to capture the would-be-written payload without hitting the real sheet.
  4. Assert payload structure matches the BDD scenario's contract (event type, session id, action label, etc.).
- **Affects:** 6 skipped tests in `test_role_match_logging.py`. Test coverage for analytics correctness (chip click → log payload, action button → log payload, session id correlation across event types).
- **Logged:** April 28, 2026 / **Reframed:** May 14, 2026

---

### MATTGPT-018
**Page-Load Flicker**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** Streamlit rerun cycle on first page load causes a visible blank/gray frame between two valid renders. Pre-existing in committed code, confirmed via Performance recording (CLS = 0, so it's a paint issue, not a layout shift).
- **Root cause:** `streamlit_js_eval` iframe creates a second rerun on first load. The DOM clears between consecutive reruns, producing the flash.
- **Failed fixes (April 28):** Removing `st.rerun()` after screen-size capture caused a navbar→hero gap regression (iframe stays in DOM). Adding CSS background+min-height to `stAppViewContainer` caused the same gap.
- **Next approach:** Move `streamlit_js_eval` call to bottom of `app.py` (after all page rendering). Iframe would render below footer instead of between navbar and hero.
- **Logged:** Pre-April 2026, investigated April 28, 2026

---

### MATTGPT-019
**Story Count Copy — Replace "130+" with "Over 100"**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Issue:** Code references "130+" stories in multiple places (hero copy, status bar, prompt cards, loading messages, About Matt narrative). Actual corpus is currently 113 stories (May 14, 2026 measurement). The exact number drifts as stories are added/removed, but no copy gets updated to match.
- **Audience reality:** Recruiters don't count stories — they scan and click. "Over 100" reads the same as "113" or "130+" to a human visitor; all three signal "lots of stories." The exact figure invites scrutiny it doesn't need.
- **Fix (May 15, 2026 — simpler than original framing):** Find-and-replace every "130+" with "Over 100" (or "100+" where the format fits — e.g., "100+ stories indexed"). No runtime calculation, no JSONL load, no constant to maintain. Always accurate regardless of corpus size, no sync issue across pages.
  - Rationale for *not* doing runtime calc: deriving from JSONL at load time is a real engineering cost (caching, refresh, cross-page sync) for zero audience value. The drift problem is solved entirely by removing the false precision from the copy.
- **Scope:** Find every "130+" reference across `ui/`, prompts, and any other source-of-truth copy. ~5-10 locations expected.
- **Logged:** Pre-April 2026 / **Rationalized:** May 14, 2026 / **Simplified:** May 15, 2026

---

### MATTGPT-020
**Simplify backend_service.py**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Medium (was)
- **Type:** Refactor
- **Why not:** No concrete pain point driving the refactor. The file is large (2,034 lines as of May 14) but functional. Past extractions (prompts.py in Jan 26 `c47ad1f`; Entity Gate / classify_query_intent in Jan 29) addressed earlier shape concerns; subsequent feature work (Role Match, story intelligence) brought the line count back up. Without a specific module wanting to escape or a specific bug attributable to the size, this is a refactor-for-refactor's-sake ticket — exactly the kind of work CLAUDE.md's "80/20 rule" and "don't add abstractions beyond what the task requires" rules push against. Re-open if a specific module wants to escape backend_service.py with a clear functional driver (e.g., "Role Match logic doesn't belong here because X").
- **Original framing (preserved):**
- **Issue:** 2,034 lines, imports from 4+ modules. Candidates for extraction: entity detection, prompt building.
- **Status note (Jan 29, 2026):** Entity Gate removed, classify_query_intent removed. Still large — grew significantly with Role Match, story intelligence, and prompt architecture work.
- **Logged:** Pre-January 2026 / **Closed:** May 14, 2026

---

### MATTGPT-021
**diversify_results() Pinning Bug**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** Two related bugs in `diversify_results()`. (1) Pinned story (result #1) is not counted toward `max_per_client` limit — a client can appear `max_per_client + 1` times. (2) Client diversity reordering breaks score ordering guarantee — test expects descending scores but diversification shuffles order.
- **Root cause:** Pinning logic (line ~1313 in backend_service.py) tracks `seen_clients` but doesn't include the pinned result in the count.
- **Fix:** Count pinned client toward limit, then restore score ordering after diversification pass.
- **Affects:** 2 failing tests (`test_limits_single_client_stories`, `test_maintains_overall_order`)
- **Logged:** April 2026 test audit

---

### MATTGPT-022
**Data Quality Cleanup Journey Story**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** The March 2026 data quality work (CIC pairing, IQ differentiation, Situation enrichment across 85+ stories) is a compelling story about systematic data improvement for AI systems. Not yet captured as a STAR story.
- **Fix:** Write as STAR story for portfolio. Covers pattern recognition, data quality discipline, measurable impact on retrieval accuracy.
- **Cross-reference (May 14, 2026 rationalization):** Assess this jointly with MATTGPT-061 (MattGPT portfolio stories over-ranking on organizational leadership queries). Adding this story would be a fifth MattGPT-meta story in the corpus and could worsen the 061 retrieval-overweighting problem. Decide both tickets together — either ship 022 with a 061-aware scope/tagging strategy, or defer 022 until 061's retrieval-quality issue is addressed.
- **Logged:** March 2026

---

### MATTGPT-039
**Automated Regression Detection (GitHub Actions)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Eval suite and unit tests are run locally only. No CI pipeline runs them on every PR or push. Drift can land before being detected — production deploys via Streamlit Cloud auto-deploy on push to main with no test gate in front of it.
- **Tiered CI design (added May 14, 2026):** Don't write a "run everything on every PR" workflow — eval suite hits OpenAI (~60 golden queries × per-call cost = real money per run). Cost-vs-coverage trade-off requires tiering:
  - **Every PR:** unit tests + BDD structural tests (mocked backends). Cheap, fast, catches code regressions.
  - **Push to main:** above + eval suite. Paid, but catches RAG drift before it reaches users.
  - **Manual trigger:** full suite for major releases or before significant retrieval-affecting changes.
- **Soft dependencies (do these first):**
  - **MATTGPT-014** (reframed May 14 2026 as Action) — audit + split the 17 skipped Role Match BDD scenarios into structural (mocked) and content (evals). Until that lands, CI either fails on skipped tests or skips them silently — neither outcome is useful protection.
  - **MATTGPT-017** (reframed May 14 2026 as Action) — same shape; 6 skipped logging BDD scenarios need wiring before CI can include them.
- **Fix:** After 014 + 017 land, wire `eval_rag_quality.py` and `tests/unit/` + BDD into a tiered GitHub Actions workflow. Spec has example YAML at `11-testing-and-quality.md` lines 502-512 (use as starting point; layer the tiers above on top).
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026 / **Refined:** May 14, 2026

---

### MATTGPT-040
**Eval Coverage Gaps — Follow-up Queries**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Eval suite validates first-turn behavior at 98.1% but has zero coverage of multi-turn conversation context. The `multi_turn` test case exists with `"followup": "Tell me more about that project"` but is explicitly skipped (see `eval_rag_quality.py` lines 1057-1060: "For multi-turn, we'd need to call twice - skip for now").
- **Root cause:** Multi-turn evaluation requires simulating conversation state — prior query + response feeding into follow-up. Current harness is single-shot.
- **Fix:** Build multi-turn eval harness that runs first query, captures response and source state, then runs follow-up query with that state, evaluates final response against ground truth.
- **Affects:** Eval coverage of "Ask Agy About This" button flow, Related Projects follow-ups, conversational drilling.
- **Priority calibration (May 14, 2026):** Dropped Medium → Low. No observed multi-turn failures in production; single-shot eval already at 98.1%. This is "we should test it" not "we know it's broken." Promote if a multi-turn failure is observed.
- **Logged:** April 29, 2026 / **Rationalized:** May 14, 2026

---

### MATTGPT-023
**LLM Meta-Commentary on Q20 (Stochastic)**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Issue
- **Why not:** Stochastic LLM-response flake. "Monitor — if it becomes consistent" was the framing, but nothing actively monitored — the ticket just sat. As of May 14 2026, Q20 isn't in the eval baseline's tracked stochastic failures (Q15 Fiserv and Q55 TDD are the current trackers); the issue may have settled, or just hasn't tripped recently. Accepted as LLM-response cost. The eval suite catches it implicitly if it ever becomes consistent — at which point re-file with concrete reproduction. No standing ticket needed for a known-flake.
- **Original framing (preserved):**
- **Issue:** "Who is Matt Pugmire?" sometimes generates meta-commentary ("showcases his") instead of direct biographical content. Stochastic — passes on some runs, fails on others.
- **Root cause:** LLM occasionally ignores the "never evaluate Matt" prompt instruction for broad biographical queries.
- **Fix:** Monitor — if it becomes consistent, add Q20-specific prompt reinforcement.
- **Logged:** April 2026 test audit / **Closed:** May 14, 2026

---

### MATTGPT-024
**Clarify Hybrid Scoring**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Refactor
- **Why not:** "Hybrid scoring" framing is itself stale — there is no hybrid scoring. W_KW = 0.0, the pipeline is pure semantic via Pinecone (this was the false claim corrected by MATTGPT-057 alignment work, May 11). What the ticket actually described is that Pinecone returns 0.0-1.0 similarity and our confidence thresholds (CONFIDENCE_HIGH=0.25, CONFIDENCE_LOW=0.15) sit in a narrow band of that range — that's just thresholds operating on raw similarity, not a scoring-system conflict. The proposed fix ("document or align") was vague with no clear audience for the documentation or concrete pain driving the alignment. Close. If a real question about threshold calibration emerges in production (false confidence labels, gate firing wrong), file a new ticket with concrete evidence.
- **Original framing (preserved):**
- **Issue:** Pinecone scores (0.0-1.0) don't map clearly to confidence buckets (0.15-0.25).
- **Fix:** Document or align the scoring systems.
- **Closed:** May 14, 2026

---

### MATTGPT-025
**Add Error Handling Tests**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** Error handling already exists in production code (FAIL OPEN patterns in semantic_router.py:350, try/except in query_logger.py, etc.). The gap is "tests for those paths," not "the handling itself." No production bugs traceable to missing error-path tests. "Add tests for error paths" is a coding norm/habit, not a discrete ticket — opportunistically add error-path unit tests when wiring up broader test coverage (e.g., during MATTGPT-014 / MATTGPT-017 work). Standing ticket for an undriven coverage gap was just backlog cruft.
- **Original framing (preserved):**
- **Issue:** Test suite only covers happy path.
- **Fix:** Add tests for rate limits, timeouts, embedding failures.
- **Closed:** May 14, 2026

---

### MATTGPT-026
**Clarify Layer Ownership**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Refactor
- **Why not:** Vague refactor with no concrete pain driver. During May 14 rationalization, the ticket author couldn't recall what specific problem this was originally pointing at — strongest possible signal that it's cruft. Same family as MATTGPT-020 / MATTGPT-024 / MATTGPT-025: pre-2026 "improve the code somehow" tickets without a concrete scope. Re-file if a specific contract or boundary problem emerges in real work.
- **Original framing (preserved):**
- **Issue:** Ranking, intent classification, and formatting split across multiple files.
- **Fix:** Document contracts or refactor boundaries.
- **Closed:** May 14, 2026

---

### MATTGPT-027
**Quarterly Intent Review**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** "Schedule quarterly review" was 3.5 months overdue at May 14 with no enforced cadence. Reality: intent review is reactive — canonical phrases get touched when actual issues surface (chip CX work, MATTGPT-061 over-ranking, MATTGPT-063 wrong-person), not on a calendar. The reactive model is what's actually working. A standing "schedule review" ticket without a mechanism (calendar reminder? recurring ticket? who owns it?) is just aspirational and aged into cruft.
- **Original framing (preserved):**
- **Issue:** 15 intent families with ~20 phrases each in `semantic_router.py`. Phrases drift relevance over time.
- **Fix:** Schedule quarterly review.
- **Last review:** January 29, 2026
- **Closed:** May 14, 2026

---

### MATTGPT-028
**Share Link Copy Functionality**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Issue
- **Why not:** "Verify works across browsers" was a QA verification task without an owner or schedule — same shape as Quarterly Intent Review (MATTGPT-027). Share functionality exists in `action_buttons.py:179` and is wired into Story Detail and Role Match. No production bug reports. If a real cross-browser failure surfaces, re-file as a concrete bug ticket with the failing browser + reproduction. Standing "verify someday" tickets are cruft.
- **Original framing (preserved):**
- **Issue:** Verify share link copy-to-clipboard works correctly across browsers.
- **Closed:** May 14, 2026

---

### MATTGPT-029
**Low-Confidence Banner Edge Cases**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Issue
- **Why not:** Logged in April 2026 test audit sweep as "sometimes triggers incorrectly" — no specific failing query, no reproduction. Thresholds (CONFIDENCE_HIGH=0.25, CONFIDENCE_LOW=0.15) have been stable since January 2026 with no production failures attributable to misfires. Same pattern as MATTGPT-027 (passive monitoring without a mechanism = cruft). Historical context preserved in **docs/ADR.md ADR 018 — Confidence Threshold Calibration for Pinecone Semantic Search**, which captures the December 2025 calibration history and edge cases to watch. If a specific banner misfire surfaces with a reproduction, re-file as a concrete bug ticket.
- **Original framing (preserved):**
- **Issue:** Low-confidence banner sometimes triggers incorrectly. Review threshold logic.
- **Closed:** May 14, 2026

---

### MATTGPT-031
**Semantic Router Error Path Coverage**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** Same shape as MATTGPT-025 (Add Error Handling Tests, killed May 14): semantic_router.py already has FAIL OPEN error handling at line 350. The gap is tests for it, not the handling itself. No production driver. Opportunistically add error-path tests when wiring up broader coverage during MATTGPT-014 / MATTGPT-017 work; standing "test coverage gap" tickets without a driver are backlog cruft.
- **Original framing (preserved):**
- **Issue:** Limited test coverage for semantic router error handling paths.
- **Closed:** May 14, 2026

---

### MATTGPT-032
**LLM Response Broken Markdown**

- **Status:** Decided Against (May 15, 2026)
- **Priority:** Low (was)
- **Type:** Issue
- **Why not:** No current production reproduction. Production responses tested May 15 (Scale a CIC, How did Matt achieve 4x faster delivery, etc.) all render bolded text cleanly — `**4X **` trailing-space pattern not observable. Ticket dates to Pre-2026; LLM and post-processing behavior have evolved since. An attempted fix May 15 introduced regression in legitimate bolded text (5 missing-space patterns: "over150", "at4x", "withNorfolk", "bothAccenture", "atCapital") and was reverted; mechanism not fully traced. Same anti-pattern as MATTGPT-027 / -028 / -029 — "watch for this someday" without a forcing function. If the trailing-space `**X **` pattern ever shows up reproducibly in production, file fresh with the actual failing query.
- **Original framing (preserved):**
- **Issue:** LLM outputs `**4X **` instead of `**4X**` — space before closing asterisks breaks bold rendering.
- **Fix:** Post-process regex: `r'\*\*([^*]+)\s+\*\*'` → `**\1**`
- **Closed:** May 15, 2026 (after attempted fix introduced regressions; lesson preserved in `feedback_check_production_before_treating_test_failure_as_bug.md`)

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Button shifts position when focused. CSS fix for focus state needed.

---

### MATTGPT-035
**Eval Modernization — Semantic Scoring**

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
- **Issue:** Current eval uses keyword matching. Semantic similarity or LLM-as-Judge would be more robust.
- **Trade-off:** More expensive per run, harder to debug failures. Current concept-cluster approach (Q2/Q5 style) may be good enough.
- **Don't act on this now (May 14, 2026 rationalization):** The two remaining eval failures (Q15 Fiserv naming, Q55 TDD ranking, per Mar 5 baseline at 61/63 = 96.8%) may be retrieval signal rather than scoring noise — Q15 tests client attribution (`expected_client: "Fiserv"`) and Q55 may interact with the MATTGPT-061 over-ranking pattern (BDD/MattGPT-meta stories potentially outranking the actual TDD story). A semantic scorer would risk masking those signals. Revisit only if the suite grows significantly or new false-negative patterns emerge that concept clusters consistently miss.

---

### MATTGPT-041
**5P Dimensional Drill-Down**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Spike
- **Why not:** No traffic evidence supports building this. Query log audit (May 13, 2026) showed zero queries asking for 5P-dimension drill-down. Same pattern as MATTGPT-040 (eval coverage for follow-up queries) — "we should think about it" not "users are asking for it." Re-file with concrete evidence if dimension-shaped follow-ups start appearing in real query logs.
- **Original framing (preserved):**
- **Issue:** Voice guide describes 5P (Person/Place/Purpose/Process/Performance) as a metadata framework for pattern recognition and deep dives. The spec envisions Agy offering to drill into a specific dimension on demand (e.g., "Want me to dig deeper into the process?"). This conversational affordance doesn't exist — Agy can't currently zoom into a single 5P dimension by request.
- **Current state:** 5P data integration is substantially implemented. `story_intelligence.py` uses all five 5P fields as STAR fallbacks in context assembly. `5PSummary` is embedded in vectors (influences retrieval). Verbatim phrase extraction works via `prompts.py`. What's missing is the *conversational* use — the ability to drill into one dimension.
- **Spike question:** Is dimension-specific drill-down worth building? Would users ask "tell me more about the process" or "what was Matt's role" as follow-ups? If so, this is a multi-turn conversational feature, not a prompt structure change.
- **Note:** The voice guide does NOT describe a 5P narrative arc for response structure. It describes 5P as input enrichment and a lens for pattern recognition — not as a replacement for WHY→HOW→WHAT output structure.
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-042
**5P Pattern Taxonomy**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Spike
- **Why not (informed):** Not a "no traffic evidence" close — a "we already tried this direction" close. The prescribed-taxonomy approach (By Outcome / By Methodology / By Challenge) was originally implemented as `theme_guidance` / `get_theme_guidance()` per the Nov 2025 archetype exercise. **Removed in commit `c47ad1f` (Jan 26, 2026 BASE_PROMPT + DELTA refactor) specifically because it generated meta-commentary and evaluation language** — the exact problem the refactor was solving. Re-introducing prescribed pattern categories would regress that fix. Current open-ended `SYNTHESIS_DELTA` approach at 98.4% eval pass rate is good enough; entity cluster promotion handles cross-story synthesis organically. If a specific synthesis-quality complaint surfaces that prescribed taxonomy would clearly address (without re-triggering meta-commentary), re-file with that evidence.
- **Original framing (preserved):**
- **Issue:** Voice guide describes structured pattern templates ("By Outcome," "By Methodology," "By Challenge") with explicit category labels for cross-story synthesis. Production synthesis is more open-ended — gives the LLM the stories and asks for patterns via WHY→HOW→WHAT, but doesn't prescribe categories.
- **Spike question:** Does prescribed taxonomy improve pattern recognition responses, or is the open-ended approach better?
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-043
**Humane Framing — Intent-to-Tone Mapping**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Spike
- **Why not (informed):** Same pattern as MATTGPT-042 — the ticket itself flagged the risk that "implementing deterministic intent-to-tone mapping risks reintroducing meta-commentary patterns that the current architecture deliberately removed." The previous `theme_guidance` architecture was closer to this vision and was removed in commit `c47ad1f` (Jan 26, 2026 BASE_PROMPT + DELTA refactor) for anti-meta-commentary discipline. The Spike question ("worth the risk?") has the same answer as 042: no, given the previous attempt regressed into the exact problem the refactor fixed. If specific intent-tone failures surface in production with evidence that prescribed mapping (without meta-commentary regression) would fix them, re-file.
- **Original framing (preserved):**
- **Issue:** Voice guide describes intent-specific response framing — Agy detects why someone is asking (interview prep vs. vetting vs. curiosity vs. hiring pitch vs. networking) and adapts tone, framing language, and offers accordingly. Specific intent-to-tone mapping is not implemented.
- **Current state:** Spirit exists via random focus angles in `_generate_agy_response()` (lines 888-896) which inject emphasis on human impact, methodology, scale, leadership, outcomes, or innovation. But this is random, not intent-driven.
- **Tradeoff:** Implementing deterministic intent-to-tone mapping risks reintroducing meta-commentary patterns that the current architecture deliberately removed. The previous prompt architecture had a `theme_guidance` variable closer to this vision but was replaced for anti-meta-commentary discipline (see commented-out prompt at `backend_service.py` lines 1040-1164).
- **Spike: Evaluate whether deterministic intent-to-tone mapping is worth the anti-meta-commentary risk.**
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-044
**Pattern Insights — Structured Templates**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Spike
- **Why not:** Duplicate of MATTGPT-042 (5P Pattern Taxonomy) — same Voice Guide Implementation Audit source, same "By Outcome / By Methodology / By Challenge" prescribed templates, same spike question. Close per 042's informed-rejection rationale: previous `theme_guidance` architecture was removed in commit `c47ad1f` (Jan 26, 2026) for anti-meta-commentary discipline; re-introducing prescribed taxonomy risks regressing that fix.
- **Original framing (preserved):**
- **Issue:** Voice guide describes Agy identifying cross-story patterns by outcome, methodology, and challenge with explicit pattern templates. Synthesis mode finds patterns through `SYNTHESIS_DELTA` instructions and entity cluster promotion, but doesn't structure them by prescribed categories.
- **Spike question:** Does adding structured pattern templates ("By Outcome," "By Methodology," "By Challenge") improve synthesis quality, or is the LLM-driven open-ended approach better?
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-045
**Analytics Dashboard**

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Issue:** No visualization layer over the query logger data. Logger captures usage signals (queries, rejections, intent distribution, UTM) but data lives in Google Sheets without aggregation or visualization.
- **Fix:** Build a dashboard (Looker Studio, Streamlit page, or similar) that visualizes rejection reasons, borderline cases, intent distribution, query volume over time.
- **Dependencies:** MATTGPT-013 (logger schema extension) should be complete first.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-046
**Latency Benchmarks**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** Single-user portfolio with low organic traffic (~7 organic queries in 30 days per May 13 query log audit). No SLA, no performance commitments, no production performance issues observed. Latency tracking is critical for high-traffic systems but overkill here. Would produce sparse, unactionable data. Re-file if traffic scales significantly or if a specific latency complaint surfaces.
- **Original framing (preserved):**
- **Issue:** No latency tracking exists. No `time.time()`, no `perf_counter()`, no duration fields in the logger schema. Can't detect performance regressions over time.
- **Fix:** Wrap OpenAI API calls and Pinecone search in timing blocks. Add duration column to logger schema. Build reporting view over accumulated data for p50/p95 tracking.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-047
**Cost Tracking**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** Same family as MATTGPT-045 (analytics dashboard) and MATTGPT-046 (latency benchmarks) — operational visibility for a low-traffic single-user portfolio. Cost concerns surfaced today (cache regen, eval API costs) were spot questions answerable ad-hoc without per-query tracking. Low organic traffic (~7 queries in 30 days per May 13 audit) = trivial monthly OpenAI bill = no spike to detect. Re-file if cost surprises appear or traffic scales.
- **Original framing (preserved):**
- **Issue:** No per-query cost tracking in production. OpenAI response includes `usage.prompt_tokens` and `usage.completion_tokens` but `backend_service.py` doesn't read them. Cost estimates exist only in offline batch scripts (`generate_use_cases.py`, `generate_public_tags.py`).
- **Fix:** Read token usage from OpenAI response object, log per-query token counts and computed cost. Fold into MATTGPT-013 logger schema work — minimal incremental work if done alongside.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026 / **Closed:** May 14, 2026

---

### MATTGPT-010
**Cross-Browser Testing**

- **Status:** Decided Against (May 15, 2026)
- **Priority:** Low (was)
- **Why not:** Trigger expired. Original framing parked this until "React migration" (originally targeted Q1 2026). Q1 has passed; still on Streamlit with no active migration work. If React migration ever happens, cross-browser testing falls out naturally as part of that work — no need for a standing ticket waiting on an uncertain trigger. Streamlit currently handles most cross-browser concerns adequately.
- **Original reason:** Low priority until React migration. Streamlit handles most cross-browser issues.
- **Closed:** May 15, 2026

---

### MATTGPT-048
**Portfolio Integration (Notion, LinkedIn sync)**

- **Status:** Decided Against (May 15, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** Framing significantly out of date and points at the wrong scope. The April 29 ticket envisioned outbound sync of the MattGPT story corpus to Notion/LinkedIn. The actual workstream that matured (Job Search System, design decisions compiled in Notion May 10) is a different shape entirely — JD ingestion → Notion + engine assessment → back to Notion, with Cowork as the orchestration layer. The explicit Job Search System decision is **"MattGPT chat is portfolio, NOT operational tool"** — meaning the integration work has its proper home in Notion's Job Search System design docs, not in MattGPT's BACKLOG. Closing here. The active work lives where it belongs.
- **Original framing (preserved):**
- **Proposed:** Programmatic sync between MattGPT story corpus and external systems (Notion job tracker, LinkedIn experience sections).
- **Reason parked:** Real idea, no urgency, no foundation work started. Notion sync was already noted as out-of-scope for Role Match v1 ("manual copy of fit score acceptable"). Revisit when traffic patterns or use cases create a forcing function.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026 / **Closed:** May 15, 2026

---

### MATTGPT-049
**Job Fit Broader Scope (cover letter export, LinkedIn URL auto-extract)**

- **Status:** Decided Against (May 15, 2026)
- **Priority:** Low (was)
- **Type:** Action
- **Why not:** Both features are out of step with the Job Search System design decisions (Notion, May 10). LinkedIn intake is handled via Gmail-routed alerts in the actual plan — not URL scraping. Cover letter export isn't in the design at all. Adding either to Role Match would push back against the explicit "MattGPT chat is portfolio, NOT operational tool" decision — they're operational features that belong in the Job Search System workstream if they're built. Same monitoring-without-mechanism pattern as the other Decided-Against tickets from this rationalization pass.
- **Original framing (preserved):**
- **Proposed:** Extensions to Role Match: cover letter export from match results, LinkedIn URL parsing to auto-extract job descriptions.
- **Reason parked:** Natural extensions to Role Match Phase 4, but no user demand signal yet, no architectural hooks. Revisit if Role Match usage signals demand for these features.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026 / **Closed:** May 15, 2026

---

### MATTGPT-036
**Entity Cluster Promotion Override**

- **Status:** Decided Against
- **Proposed:** Override synthesis mode when 3+ stories from the same entity are in the Pinecone pool (e.g., "How did you build the CIC?" gets 10 CIC stories → forces synthesis).
- **Why not:** Overriding would break legitimate synthesis queries like "Tell me about all your CIC work." The real fix is better data differentiation so the right story ranks clearly #1, not routing logic.

---

### MATTGPT-037
**Score Gap Override (Generic-Above-Named)**

- **Status:** Decided Against
- **Proposed:** Boost named client stories over "Fortune 500 Clients" generic stories in Pinecone results.
- **Why not:** Adds a ranking layer on top of semantic search. Better to fix at the data level — enrich generic stories with distinguishing context, or merge them into named client stories where appropriate.

---

### MATTGPT-038
**Centralize Constants (Duplicate)**

- **Status:** Decided Against
- **Proposed:** Separate request to centralize constants.
- **Why not:** Duplicate. Consolidated into `config/constants.py` as the single source of truth (see CHANGELOG.md, January 2026).

---

### MATTGPT-050
**Dynamic Intent Expansion**

- **Status:** Decided Against
- **Proposed:** Use LLM to generate new canonical examples from accepted queries, dynamically expanding the semantic router's intent family phrases rather than hardcoding them.
- **Why not:** Architectural constraint. The data pipeline (Excel → JSONL → embeddings → Pinecone) is one-directional by design — no write-back path. Dynamic expansion would require building a feedback-to-pipeline bridge that doesn't exist. Manual curation at 15 families is working (98.1% eval pass rate). Eval suite validates router changes more reliably than automated derivation would. Spec assumed a different architecture (database-backed React migration); current architecture deliberately avoids that.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-051
**User Feedback Loop — Closed-Loop Retraining**

- **Status:** Decided Against
- **Proposed:** "Was this answer helpful?" → retrain router. Closed-loop machine learning where thumbs-up/thumbs-down data flows back into the semantic router to automatically adjust thresholds, expand intents, or shift family assignments.
- **Why not:** Architectural constraint. Read-only data layer doesn't support closed-loop retraining. Data pipeline is one-directional by design. Feedback collection IS implemented (`log_feedback()` in `query_logger.py`, helpful/export buttons wired) and provides observable signal for manual eval-driven iteration. Closed-loop retraining assumes a writable data layer that doesn't exist.
- **Note:** Feedback collection is the valuable half and is implemented. Only the automated retraining half is unbuildable on current architecture.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-052
**A/B Testing on Thresholds**

- **Status:** Decided Against
- **Proposed:** A/B testing infrastructure to experiment with confidence threshold values (e.g., 0.40 vs 0.45 for soft accept).
- **Why not:** Thresholds tuned through eval-driven iteration (SOFT_ACCEPT 0.72 → 0.40, etc.) at 98.1% eval pass rate. A/B testing infrastructure not justified at current traffic volume — insufficient signal for statistical significance. Eval suite validates threshold changes more reliably than user-traffic A/B tests.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-053
**A/B Testing Framework**

- **Status:** Decided Against
- **Proposed:** General testing infrastructure for prompt variants, threshold variants, etc.
- **Why not:** Same reasoning as MATTGPT-052. Insufficient traffic for statistical significance, eval suite is the better validation tool. Note: this is essentially a duplicate of MATTGPT-052 from a different spec section.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-054
**Query Rewriting and Spell-check**

- **Status:** Decided Against
- **Proposed:** Preprocess user queries to fix typos and rewrite ambiguous queries before they hit the RAG pipeline.
- **Why not:** Embedding-based semantic routing already handles typos and ambiguous queries. Validated by `UGLY_BUT_VALID` test suite in semantic router unit tests (e.g., `"Tell me abot Matts backgroun"`, `"Whats Matt's experiance with agile?"` — all pass). Embedding model handles misspellings via subword tokenization. LLM-based query rewriting would add latency and cost without measurable improvement.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-055
**PWA Capabilities**

- **Status:** Decided Against
- **Proposed:** Progressive Web App features — manifest.json, service worker, offline support.
- **Why not:** Portfolio app requires live API calls (OpenAI, Pinecone) for core functionality. Offline support via service worker would only cache static UI shells — the RAG pipeline cannot function offline. Mobile responsive design covers the actual use case.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-056
**True Wireflows (Miro)**

- **Status:** Decided Against
- **Proposed:** Screen-to-screen UI interaction diagrams maintained in Miro, with export pipeline (SVG, embed, or screenshots) into the design spec.
- **Why not:** Screen-to-screen interaction flows documented using Mermaid diagrams in Jekyll pages. Miro-based wireflows replaced by in-repo diagrams that version with the codebase.
- **Source:** Cross-reference triage, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-058
**Replace dark-theme setInterval polling with MutationObserver**

- **Status:** Decided Against
- **Priority:** Low
- **Type:** Refactor
- **Why not (May 13, 2026):** Reframed after the May 12 dead-closure card-click investigation. The `setInterval(detectTheme, 500)` polling lives inside a `components.html` iframe, and Streamlit destroys and recreates that iframe on every rerun. A `MutationObserver` attached from inside the iframe loses its callback closure the moment the iframe is recreated, leaving the theme class to drift out of sync — same dead-closure bug shape that caused the Cross-Industry card-click failure. The 500ms polling is iframe-rewire defense: it re-asserts the class from a live closure regardless of how many iframe destroy/create cycles have happened. The `how_agy_modal.py` MutationObserver pattern referenced in the original analysis works there because that observer is attached to a long-lived parent-doc element from a context that survives reruns differently — not transferable to this iframe. Polling is the correct pattern here.
- **What lives in code now:** an explanatory comment at `ui/components/category_cards.py` near the `setInterval(detectTheme, 500)` line, warning future readers not to "replace polling with MutationObserver" without understanding the iframe lifecycle.
- **Original analysis (preserved):** `category_cards.py` (line 506) and `navbar.py` (line 238) each run `setInterval(detectTheme, 500)` that reads parent body's computed background color and toggles `body.dark-theme` class. Polling was introduced in commit `548f1bf` (Dec 8 2025: "enhance dark mode support") as a FOUC remediation. The duplication with `navbar.py` is defense-in-depth: if either iframe fails, the other keeps the class maintained.
- **Lesson:** Understand WHY a pattern exists before proposing a replacement. Same lesson as the theme detection research that triggered this ticket — both times the "anti-pattern" was actually a defense against a specific failure mode.
- **Logged:** May 12, 2026 / **Closed:** May 13, 2026

---

### MATTGPT-059
**Add Theme-based prefilter dimension to category cards**

- **Status:** Decided Against (May 14, 2026)
- **Priority:** Low (was)
- **Type:** Spike
- **Why not:** Ticket author couldn't recall the framing or intent during May 14 rationalization — strongest signal that it's cruft (same call as MATTGPT-026). Adjacent context: the data-derived landing card refactor (Banking + Cross-Industry Phase 1+2, May 11-12) addresses "chips communicate scope" via tiered Core/Specialized cards mapped to Solution/Offering — different path, but covers much of the UX pressure the Theme dimension was meant to relieve. No traffic demand on Explore Stories filters per May 13 query log audit. Re-file if Theme-level filtering becomes a concrete user-driven need with evidence.
- **Original framing (preserved):**
- **Context:** Current `prefilter_domains` filters against the `Sub-category` field (45 unique values in data, most have 1-5 stories). Result: cards have to choose between many chips for adequate story coverage or few chips with sparse coverage. The `Theme` field has 7 broader buckets — Execution & Delivery (50), Org & Working-Model Transformation (22), Strategic & Advisory (13), Professional Narrative (10), Talent & Enablement (10), Emerging Tech (5), Risk & Responsible Tech (3) — that could deliver high coverage with few chips.
- **Why not done now (UX blockers, not implementation cost):**
  - Two chips on a card landing looks sparse. Chips communicate scope ("here's what this view covers") — two doesn't do that job for a recruiter scanning quickly.
  - Theme labels are more abstract than Sub-category labels. "Org & Working-Model Transformation" is harder to parse at a glance than "Agile Transformation & Leadership Enablement." May need a friendly-alias layer.
  - Path A (surgical Sub-category trim) ships the immediate Card 3 + Card 5 fix without new infrastructure (MATTGPT-current).
- **What it would take (small implementation):**
  - `prefilter_theme` key handling in `explore_stories.py` (~10 lines)
  - Theme dropdown widget in the filter UI (~20 lines)
  - Theme filter logic in `utils/filters.py` (~3 lines)
  - Decision on chip presentation: render underlying Sub-category chips, or a single high-level "Filtered by Theme: X" chip
- **Recommendation:** Hold until a UX pass solves the chip-density and label-abstraction problems. Theme filtering is the right architectural foundation but the chip display needs more thought before it ships.
- **Logged:** May 12, 2026

---

### MATTGPT-060
**BDD coverage gap — assert post-navigation page state, not just navigation**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Card 3 (Product Innovation & Strategy) on the home page set `prefilter_capability = "Product Leadership"` — a value that didn't exist in any story's `Solution / Offering` field. The Capability dropdown widget silently sanitized the invalid value to "All", showing 113 unfiltered stories instead of the curated product slice. The regression shipped because BDD verified that clicking the button navigated to Explore Stories — and it did — but never asserted what state the page should be in after arrival.
- **Why it matters:** "Did we land on the right page?" passes when the prefilter is broken. The acceptance criteria assumed correct filtering but never wrote it down as a check. Human-centered exploratory testing catches what scripted assertions miss when the asserted condition is narrower than the user expectation.
- **Proposed BDD scenario shape:**
  ```gherkin
  Given I am on the home page
  When I click "View Product Work" on the Product Innovation & Strategy card
  Then Explore Stories should be the active tab
   And the Domain filter should include the expected product sub-categories
   And the result count should be less than 113
  ```
- **Current state (May 14, 2026 validation):** `home.feature` has 11 scenarios total. 4 already wired in `test_home.py`: Card 3 regression, plus 3 chip scenarios added during May 13 chip CX work (Ask Agy button no-prefill, chip auto-fire, chip ↗ affordance). 7 still pending step defs.
- **Coverage targets — pending step defs (7 scenarios):**
  - Card 1 (Banking) — subpage navigation + page-specific content present
  - Card 2 (Cross-Industry) — subpage navigation + page-specific content present
  - Card 4 (Application Modernization) — `prefilter_capability` applied, result count < total
  - Card 5 (Consulting & Transformation) — `prefilter_domains` applied, result count < total
  - Card 6 (Teams & Talent Development) — `prefilter_domains` applied, result count < total
  - Ask Agy chip CX — Session state cleared after auto-fire (refresh doesn't re-fire)
  - Ask Agy chip CX — Ask MattGPT renders default landing when no chip clicked
- **Lesson framing:** "Verifying the link works isn't the same as verifying the destination state is correct." Every prefilter-triggering button needs a state assertion, not just a navigation assertion.
- **Related:** MATTGPT-014 (audit + split 17 skipped Role Match BDD scenarios) and MATTGPT-017 (wire 6 skipped logging BDD scenarios) — same thematic cluster: fill in BDD step defs for already-existing acceptance criteria. All three blocked the same "BDD has gaps where manual testing fills in" problem.
- **Root-cause incident:** May 12, 2026 — Card 3 prefilter discovered broken; Path A fix landed in same session. Pre-existing regression; ship date unknown.
- **Logged:** May 12, 2026 / **Refreshed:** May 14, 2026

---

### MATTGPT-061
**MattGPT portfolio story contaminating organizational leadership queries**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** MattGPT-related stories (Building MattGPT, Strangler Fig refactor, portfolio-narrative voice) surface as top results for organizational-leadership / change-management queries where they are the wrong answer. This is a **longstanding, recurring pattern** — not a single incident. The May 13, 2026 chip CX testing is the trigger for filing the ticket; the underlying retrieval bias has been observed repeatedly. The MattGPT stories have broad semantic overlap with queries about "transformation", "stakeholders", "value proposition", "scale", and "challenge" — so Pinecone ranks them highly for queries that are not about building MattGPT or about Matt's portfolio-building narrative.
- **Evidence (May 13, 2026 chip CX testing):**
  - **Query:** *"How does Matt handle resistance in large-scale transformations?"*
    - Response opened with the MattGPT refactor story (strangler fig pattern, 5,765 → 1,014 lines), instead of organizational change-management stories. The Norfolk Southern legacy-mainframe resistance story and JP Morgan Dynamics CRM stabilization story — both of which directly answer the query — were not surfaced.
  - **Query:** *"How does Matt bring skeptical stakeholders along during large-scale change programs?"*
    - Response opened with "convincing recruiters of value" framing pulled from the MattGPT portfolio-building narrative, with CIC scaling stats grafted in as evidence. The query is about stakeholder change management; the response is about Matt's career marketing.
  - **Counter-example (works):** *"How does Matt manage resistance when leading enterprise transformation programs?"* — the rephrase that adds "enterprise" + "programs" pulled the right stories (Norfolk Southern + JP Morgan). This is the workaround currently shipped as chip 3 on Home (May 13, 2026).
- **Hypothesized root cause:** The MattGPT story uses high-frequency leadership vocabulary ("stakeholders", "transformation", "scale", "challenge", "value proposition") describing the META-narrative of *building MattGPT to demonstrate Matt's value to recruiters* — vocabulary that semantically overlaps with queries about Matt's enterprise leadership work. The semantic router doesn't distinguish technical-transformation (refactoring, architecture) from organizational-transformation (change management, capability building), so the highest-ranked story wins regardless of which sense of "transformation" the query intended.
- **Affected query shape:** Anything containing "transformation", "stakeholders", "resistance", "value", or "scale" without an entity (client name, division) or a domain-specific qualifier ("technical", "engineering", "platform") to anchor retrieval.
- **Not affected:** Queries with entities ("How did Matt transform JP Morgan payments?") — entity filter dominates, MattGPT story is excluded.
- **Workaround currently shipped:** Chip 3 phrasing changed from "handle resistance in large-scale transformations" to "manage resistance when leading enterprise transformation programs" — empirically pulls the right stories. Stop-gap, not a fix.
- **Fix options (open — leave for someone with the right answer):**
  - **A.** Demote or exclude the MattGPT story from organizational-leadership query results — add a metadata tag or post-filter that suppresses it unless the query explicitly names MattGPT/portfolio/refactor.
  - **B.** Extend the semantic router with a technical-vs-organizational transformation disambiguation — new intent family or sub-classifier.
  - **C.** Edit the MattGPT story copy to reduce overlap with org-leadership vocabulary — narrow the "stakeholders" / "value proposition" framing so it only matches portfolio/build queries.
  - **D.** Same shape as the diversify_results() pinning bug (MATTGPT-021) — pin and re-rank instead of letting raw Pinecone scores decide.
- **Related:** MATTGPT-021 (diversify_results pinning), MATTGPT-016 (semantic router wrong-person detection — closed Decided Against May 14 2026). Same broader theme: retrieval over-ranking on semantic overlap without semantic intent disambiguation.
- **Cross-reference with MATTGPT-022 (added May 14, 2026):** Writing another MattGPT-meta story for the corpus (MATTGPT-022 "Data Quality Cleanup Journey Story") could worsen this ticket's over-ranking problem by adding a fifth MattGPT-narrative story competing for retrieval space. Decide 022 jointly with this ticket.
- **Logged:** May 13, 2026

---

### MATTGPT-062
**Semantic router cache silently uses stale embeddings when VALID_INTENTS changes**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor
- **Issue:** `services/semantic_router.py::_get_intent_embeddings()` (lines 270-285) loads `data/intent_embeddings.json` if it exists and returns immediately — no drift check. If new canonical phrases are added to `VALID_INTENTS` without first deleting the cache file, the new phrases are silently absent from the embeddings map. The router iterates over cache keys only (line 335), so the new phrases are never checked against incoming queries. No error, no warning — the only signal is "the fix doesn't work and tests still fail."
- **Why it matters:** The current contract is documented in the module docstring ("If you modify VALID_INTENTS, you MUST delete data/intent_embeddings.json to regenerate"), but it's a "you must remember" footgun, not a guardrail. Easy to skip during the wrong-person fix (MATTGPT-016) and produce a fix that compiles but doesn't take effect.
- **Recurring impact:** Every future change to `VALID_INTENTS` carries this drift risk. The cache file is also ~4.3 MB and currently committed to git, so each regeneration creates a substantial commit diff (see commit `a0e7d58` for prior example, and the MATTGPT-016 commit that will follow).
- **Fix options:**
  - **A.** Drift-aware cache load — at load time, compare cached keys against the current `ALL_VALID_INTENTS` set. If any phrase is missing or extra, log a warning and regenerate from scratch (full rebuild, current ~30-60 second cost on first call).
  - **B.** Incremental top-up — compute embeddings only for phrases missing from the cache; write the updated cache back to disk. Cheaper than full regen; preserves embeddings for unchanged phrases.
  - **C.** Hash-based cache key — derive the cache filename from a hash of `VALID_INTENTS` contents (e.g., `intent_embeddings.<sha256>.json`). A cache miss is automatic and unambiguous when the inputs change. Old cache files can be garbage-collected on a schedule.
- **Recommendation:** Option B is the right long-term shape — cheap, transparent, no silent stale state. Option A is a one-line safety net that could ship first as a guard.
- **Out of scope for MATTGPT-016:** The current wrong-person fix follows the existing "delete and regenerate" workflow (the documented contract) and commits a regenerated cache. This ticket addresses the underlying fragility, not the immediate fix.
- **Logged:** May 14, 2026 (surfaced during MATTGPT-016 implementation scoping)

---

### MATTGPT-063
**Wrong-person queries with names outside nonsense regex produce confused-context RAG answers**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** When a wrong-person query reaches the RAG pipeline (i.e., the person's name isn't in `nonsense_filters.jsonl` and the query's structural shape doesn't trigger an `out_of_scope` route), Pinecone returns semantically-adjacent Matt stories, and the LLM faithfully relays them as the answer. The response is technically accurate about Matt but doesn't address the question's actual subject. Brand risk: a polished-but-tangential answer reads as if Matt has experience he doesn't, or as if his principles applied to a context they didn't.
- **Evidence (May 14, 2026):**
  - **Query:** *"What's it like to work with Donald Trump?"*
  - **Response (production AND local with the in-progress MATTGPT-016 fix applied):** Opened with Matt's general work-environment principles from Accenture — "Matt thrives in environments that prioritize psychological safety, clear purpose, and the freedom to challenge existing norms..." Did NOT explicitly claim Matt worked with Trump, but the response framed Matt's principles as if they answered the question.
  - **Actual chain:** semantic router classified into leadership/behavioral family (the question shape matches "what's [X]'s leadership style?") → Pinecone retrieved Matt's principle-stories (work environment / leadership match Matt's actual corpus) → LLM was given those stories with no signal that Trump isn't a corpus entity → LLM relayed Matt's principles as the answer.
  - **What the system did NOT do:** fabricate that Matt worked with Trump. The failure mode is *tangential retrieval presented as direct answer* — the Trump-ness of the query was lost between retrieval and generation. Neither layer treats "the question mentions a person who isn't in the corpus" as a signal.
- **Why this isn't fixable by MATTGPT-016's approach:**
  - 5 wrong-person canonical phrases added to `out_of_scope` cover shapes like "Tell me about X" and "What's X's leadership style?" — Trump query's "What's it like to work with X?" shape didn't match closely enough for embedding similarity to dominate over the legitimate-leadership-question shape.
  - Adding more canonical phrases per shape is whack-a-mole.
- **Rejected approaches (carried forward):**
  - Person-name detection as a separate gate layer — history: added gates create complexity and get backed out.
  - Lower SOFT_ACCEPT threshold — tried before, caused false rejections on legitimate queries.
- **History note (May 14, 2026 investigation):** A prompt-level subject-refusal instruction existed in the pre-Jan-26 inline prompt in `backend_service.py` ("If the query is about shopping, weather, celebrities, or anything unrelated to Matt's professional work, respond ONLY with: 🐾 I can only discuss Matt's transformation experience..."). Removed in commit `c47ad1f` (Jan 26, 2026 BASE_PROMPT + DELTA refactor). Matt's recollection: the prompt-level refusal wasn't reliable enough on its own — the team built the nonsense filter (regex layer) and semantic router's `out_of_scope`/`personal` families (embedding-similarity layer) as more deterministic replacements. Loss of the prompt guard in the refactor was implicit acceptance that the downstream layers were carrying the load.
- **Catch-all architecture note:** The pipeline is positive-classification all the way down — every layer matches to known categories (nonsense regex categories, semantic router intent families, Pinecone top-K retrieval). When a query matches NO known pattern at any layer, the default behavior is "best-effort answer." The Trump query is what that long-tail looks like. None of the layers has a "I don't know what this is" reject path; they all assume positive classification will catch what needs catching. This is the architectural shape, not a bug — and changing it adds false-rejection risk to legitimate queries.
- **Possible directions (open — needs prototyping, no guaranteed solution):**
  - **A. Post-retrieval subject-mismatch check (most concrete option).** After Pinecone returns top stories, extract proper-noun candidates from the question. If any proper noun in the question doesn't appear in the retrieved stories, refuse with "I don't have stories about that." Deterministic, no embeddings, no canonical phrase maintenance. Edge cases to think through: queries mentioning places vs people, queries mentioning Matt's collaborators (already in stories), queries with novel-but-legitimate proper nouns.
  - **B. Prompt-level refusal (re-prototype).** Restore the pre-Jan-26 subject-refusal instruction in BASE_PROMPT, possibly with stronger phrasing. Historical evidence is mixed — wasn't reliable on the older model, but GPT-4o-mini's instruction-following is better than what the original was tuned for. Worth empirical retest against the Trump query and similar shapes.
  - **C. Retrieval-confidence floor (harden existing partial implementation).** Currently low confidence shows a warning banner but answers anyway. Could be hardened to refuse when top-story relevance is below a threshold. Risk: legit niche queries might fall below the threshold and get rejected.
  - **D. Extend nonsense regex periodically.** Manually add high-profile names as they appear in query logs. Manual but tractable for low-volume traffic.
  - **E. Defer.** Accept the long-tail failure rate; monitor query logs and revisit when frequency/brand-damage warrants action. Current de facto state.
- **Related:** MATTGPT-016 (Decided Against — same root concern, wrong fix shape), MATTGPT-061 (MattGPT story over-ranking), MATTGPT-021 (diversify_results pinning).
- **Logged:** May 14, 2026

---

### MATTGPT-064
**Explore Stories — Table row hover/cursor doesn't apply to data cells (AgGrid selector fix)**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** `global_styles.py:372-384` already defines `cursor: pointer !important` and hover background/border styling for `.ag-theme-streamlit .ag-row`. In production the cursor changes on column headers but **not** on data cells. Diagnosis (May 15, 2026): the rule never wins because (a) `.ag-cell` sits on top of `.ag-row` and the cursor is determined by the topmost element under the pointer, and (b) AgGrid manages hover state via a `.ag-row-hover` class rather than the browser `:hover` pseudo-class — `:hover` on `.ag-row` may never fire reliably because cells consume the pointer events.
- **Fix:** Selector adjustment, NOT specificity escalation. The existing `!important` declarations are fine.
  - Change cursor target from `.ag-theme-streamlit .ag-row` to `.ag-theme-streamlit .ag-row .ag-cell`.
  - Change hover selector from `.ag-theme-streamlit .ag-row:hover` to `.ag-theme-streamlit .ag-row.ag-row-hover`.
- **Effort:** ~5-10 lines in `global_styles.py:372-384`.
- **Audience impact:** High-intent recruiter scanning the Table view to find a specific story may not realize rows are clickable until they accidentally click one. Original UX agent flagged this as a "missing CSS" problem; actual root cause is "existing CSS doesn't apply to data cells" — different bug, different fix.
- **Logged:** May 15, 2026

---

### MATTGPT-065
**Explore Stories — Polish bundle (filter UX, empty states, story details)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Items (all in `ui/pages/explore_stories.py` unless noted):**
  - **Reset Filters conditional render** — currently always visible (line 1890). Compute `any_filter_active = bool(F["q"]) or F["industry"] or F["capability"] or F["domains"] or F["clients"] or F["roles"] ...` and wrap render in `if any_filter_active:`. ~3 lines.
  - **Empty zero-results state — Table view** — Cards view has Clear filters button (lines 2417-2421), Table view text-only (lines 2122-2132). Copy Cards-view pattern to Table block. ~5 lines.
  - **Card truncation "Read more →" affordance** — `.card-desc` uses CSS ellipsis (lines 2466-2476), no visual cue. Append `<span class="card-read-more">Read more →</span>` + small CSS rule. ~3 lines.
  - **Back-to-list from story detail (Table view only)** — Cards view has "✕ Close"; Table view inline detail has no close button (deselecting works by clicking row again, not obvious). Add "← Close detail" at top of Table-view detail. ~5-10 lines.
  - **Advanced Filters label rename** — currently `"▾ Advanced Filters"` / `"▸ Advanced Filters"` (lines 1882-1883). Rename to `"Filter by Client, Role & Domain"`. ~2 lines.
  - **Export tooltip** — `ui/components/action_buttons.py:154` Export button has no tooltip. Add `title="Export as PDF"`. ~1 line.
  - **Story title truncation tooltip** — table cell titles truncate without reveal. Add `title="{full_title}"` attribute on the cell. ~1 line.
- **Out of scope:** Table row hover/cursor (filed as MATTGPT-064 — different layer, different fix). SHOW dropdown / pagination separation (won't fix per May 15 decision — per-view design is intentional).
- **Verify-first item:** SHOW per-page resetting (UX agent claim that selection resets across renders). Code at line 2202 uses `st.session_state.get("page_size_select", ...)` — likely already persists. 30-second eye-test before fixing; may be a non-issue.
- **Effort:** ~25-50 lines total, single file, all low-risk. Natural single-PR bundle.
- **Logged:** May 15, 2026

---

### MATTGPT-066
**Role Match — Sample JD / "Try a sample role" cold-start affordance**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Empty Role Match page (`role_match.py:1294-1300`) shows only a hint paragraph + textarea with placeholder `"Paste job description here..."`. A recruiter arriving speculatively — without a specific JD in hand — has nothing to engage with. Highest-impact cold-start fix on this page per May 15 UX assessment.
- **Fix:** Add 1-3 sample JD buttons below the textarea. Clicking pre-fills the textarea via prefilter pattern (set `st.session_state["role_match_jd_input"]` BEFORE the textarea renders to avoid `StreamlitAPIException`).
- **Implementation notes:**
  - Define sample JD strings as a module-level constant (e.g., `SAMPLE_JDS = {"Director of Platform Engineering": "...", ...}`). Drift-prone if inlined per CLAUDE.md "no hardcoded enums."
  - Use prefilter pattern (see `banking_landing.py` → `explore_stories.py` for cross-state reference).
  - Optional alternative: widget-key versioning if the prefilter approach hits Streamlit state issues.
- **Effort:** ~30-50 lines, single file. Risk: medium — widget state ordering is the gotcha.
- **Audience impact:** Direct conversion improvement for speculative recruiter visits (Director/VP recruiters who arrive to "see what the tool does" before they have a specific role). Removes the empty-state barrier for first-time visitors.
- **Logged:** May 15, 2026

---

### MATTGPT-067
**Role Match — Result panel and input polish bundle**

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Items (all in `ui/pages/role_match.py`):**
  - **Loading message** — `render_thinking_indicator()` at line 1330 is called bare → uses random dog-themed phrases from `THINKING_MESSAGES`. Pass specific message: `render_thinking_indicator(message="Agy is reviewing over 100 stories…")`. Function already accepts a `message` parameter (see `thinking_indicator.py:39`). ~1 line. Aligns with MATTGPT-019 "Over 100" copy standard.
  - **Post-result follow-up CTA** — `_render_results_panel` ends after the Preferred section (line 628) with no follow-up affordance. Add "Ask Agy a follow-up →" link/button that navigates to Ask MattGPT. ~10-15 lines.
  - **Disabled state on empty textarea** — submit button (line 1303) is always enabled; current behavior shows `st.warning("Paste a job description first.")` on empty click (line 1324). Replace with `disabled=not jd_text.strip()` (pattern at `ui/pages/ask_mattgpt/landing_view.py:225-231`). ~2 lines.
  - **Clear textarea button** — no native Streamlit clear control. Add a small "Clear" button rendered BEFORE the textarea; on click pops `role_match_jd_input` from session_state. Must render before textarea per Streamlit widget state rules. ~5-10 lines.
- **Story count copy:** Use "over 100" per MATTGPT-019's "Over 100" standard, not "130+".
- **Effort:** ~20-30 lines total, single file. Natural pair with MATTGPT-066 (same area, same audience).
- **Logged:** May 15, 2026

---

### MATTGPT-068
**About Matt — Content polish bundle**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Decisions locked May 15, 2026 (after UX assessment with multiple agents):**
  - **Sample questions clickable** — 4 questions at `about_matt.py:1199-1204` currently `<li>` plain text in a single `st.markdown` block. Convert to 4 `st.button` calls using the existing chip→Ask pattern: `seed_prompt` + `__ask_from_suggestion__` + `active_tab="Ask MattGPT"` + `st.rerun()` (see `category_cards.py:55-57` and `story_detail.py:203-218` — the pattern is used in 2 existing call sites). Define the four question strings as a module-level constant `ABOUT_MATT_SEED_QUESTIONS` for BDD/eval reuse. Requires splitting the existing markdown blob into pre / button container / post pieces, plus scoped CSS to keep the buttons visually consistent with the styled `<div class="cta-card">`.
  - **Remove redundant footer (lines 1205-1208)** — once questions are clickable, the "Head to Ask MattGPT in the navigation above to try it yourself" line AND the "Real AI assistant • 130+ projects • Instant answers • Available 24/7" bullets become redundant. The paragraph above already carries every signal. Remove entirely; section ends with the four buttons.
  - **Code block in `<details><summary>`** — RAG pipeline code at lines 1062-1091 is a wall of Python mid-page. Wrap in native HTML `<details><summary>Show code</summary>...</details>` inside the existing markdown (no st.expander → no markdown-block split needed). Serves both audiences: technical readers expand it, non-technical readers skip past. ~3 lines.
  - **4x stat — relocate to Career Evolution timeline** — currently in stats bar (line 884) as a 5th stat, inconsistent with Home stats bar (4 stats only — see `hero.py:298-311`). Remove from About Matt stats bar; surface in Career Evolution timeline where the CIC story provides context.
  - **Merge DevOps & Quality card into CI/CD Pipeline card** — `.details-grid` is 2-column (`about_matt.py:316`), 7 cards → bottom row has 1 orphan (DevOps & Quality, lines 1157-1164). Merge its content into the CI/CD Pipeline card (lines 1129-1137) — both reference CI/CD already, so the merge removes both the orphan and the redundancy in one move.
  - **Anchor navigation** — page is 3,000+ words. Add `id="career"`, `id="mattgpt"`, `id="competencies"`, `id="philosophy"` to section headers at lines 896, 957, 1218, 1303. Render a nav block (`Career · MattGPT · Competencies · Philosophy`) right after the hero. ~15-20 lines.
- **Closed per May 15 assessment:** "View Design Specification" format indicator (minor, low ROI for the audience), explicit two-audience signposting labels (anchor nav handles implicitly).
- **Effort:** ~50-80 lines total, single file. Natural single-PR bundle.
- **Logged:** May 15, 2026

---

### MATTGPT-069
**Home — Stats label contrast (light mode WCAG AA fix)**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Stats bar labels in `ui/components/hero.py:262-267` use `color: var(--text-muted)`. In light mode (`ui/styles/global_styles.py:47`), `--text-muted` resolves to `#9CA3AF`. On the white background, the contrast ratio is ~2.85:1 — **fails WCAG AA** (needs 4.5:1 for 14px text). Dark mode (`#6B7280` on dark, line 99) passes at ~4.6:1.
- **Audience impact:** A recruiter scanning the home page may register the stat numbers (20+, 130+, 300+, 15+) but miss the labels entirely — losing the credibility signal of "Years Experience / Projects Delivered / Professionals Trained / Enterprise Clients."
- **Fix:** Switch the stats label color from `--text-muted` to `--text-secondary` (`#6B7280` in light mode → ~4.7:1, passes AA). ~1 line. Optional: also bump weight from default to 500 for additional emphasis.
- **Out of scope (closed per May 15 assessment):** Hero CTA weight rebalance (already done — Ask Agy is primary, Explore is secondary in `hero.py:168-173`); name vs tagline visual prominence (design call — tagline is intentional H1 anchor); explicit seniority signal at hero (design call — recruiters arriving from LinkedIn have context, stats bar reinforces 20+ years).
- **Logged:** May 15, 2026

---

### MATTGPT-070
**Ask MattGPT — Suggestion button cursor pointer**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** The 6 suggestion buttons on the Ask MattGPT landing page (`ui/pages/ask_mattgpt/landing_view.py:97-135`) are real `st.button(type="secondary")` calls. The CSS rule at `ui/pages/ask_mattgpt/styles.py:288-309` styles them as cards (border, background, padding, hover background) but **does not declare `cursor: pointer`**. Adjacent buttons in the same file DO declare it explicitly (lines 443, 1290, 1399), so it's not being relied upon to inherit from Streamlit defaults. Live testing (May 15, 2026) confirms the pointer does not change on hover — cards appear interactive (purple text, border) but the cursor stays as the default arrow.
- **Audience impact:** First-time visitor cannot visually confirm the cards are clickable until they actually click one. Cheap trust erosion at the first interaction moment.
- **Fix:** Add `cursor: pointer !important;` to the existing `button[key^="suggested_"]` rule at lines 288-309. ~1 line.
- **Out of scope (closed per May 15 assessment):** Input field below the fold (the 6 suggestion buttons are themselves real CTAs that submit queries — input is the secondary path, defensible as-is); status bar developer-facing copy (design call for a technical-leaning portfolio); conversation export/share (already deferred to React migration per `conversation_helpers.py:470` TODO).
- **Logged:** May 15, 2026

---

### MATTGPT-071
**Nonsense rejection banner — redirect chips + hint text (branch-aware copy)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Current `render_no_match_banner` (`utils/ui_helpers.py:304`) rejects nonsense/inappropriate queries with copy only — no affordance for the user to recover with a real query. A recruiter who mistypes or fat-fingers gets a dead end. Personal-intent and out-of-scope branches were differentiated in March 2026, but no redirect mechanism was added to either.
- **Design (locked May 15, 2026 — ready to implement):**

  **Ask MattGPT — Nonsense branch:**
  - Banner copy: *🐾 Wrong trail. I'm a Plott Hound trained to track Matt's transformation work. Give me a real scent to follow.*
  - Four chips beneath the banner:
    - `[Scale a CIC to 150+ engineers]`
    - `[Build teams that ship like startups]`
    - `[Lead enterprise transformation]`
    - `[Modernize payments at scale]`

  **Ask MattGPT — Inappropriate branch:**
  - Banner copy: *🐾 That's not a trail I'll follow. Ask me about Matt's work instead.*
  - No chips. Banner stands alone (deliberate — don't reward the query shape with engagement scaffolding).

  **Explore Stories — Nonsense branch:**
  - Banner + hint line: *"Try transformation work, scaling teams, payments modernization, or enterprise leadership."*
  - No clickable chips (Explore Stories uses filter UI, not seed prompts) — hint text only.

  **Explore Stories — Inappropriate branch:**
  - No hint text. Banner stands alone.

- **Implementation notes:**
  - Chip click pattern: reuse the existing chip→Ask flow (`seed_prompt` + `__ask_from_suggestion__` + `__ask_force_answer__=True` to bypass the nonsense filter on the canonical chip text + rerun). See `category_cards.py:55-57`, `story_detail.py:203-218` — third call site of the same pattern.
  - Branch detection: `render_no_match_banner` already receives a `reason` parameter that differentiates nonsense vs. personal vs. out_of_scope vs. inappropriate. Extend the function to render chips conditionally on `reason == "nonsense"` AND `page == "ask_mattgpt"`.
  - Define chip strings as a module-level constant (e.g., `NONSENSE_REDIRECT_CHIPS = [...]`) for BDD/eval reuse, never inline.
- **Out of scope:** Changing the rejection logic itself (nonsense filter regex, semantic router branches). This ticket is purely the recovery affordance on top of existing branches.
- **Effort:** ~30-50 lines across `utils/ui_helpers.py` (banner rendering) + chip handler wiring. Single file plus a constants reference.
- **Audience impact:** Reduces dead-end conversion loss when a recruiter's first query misfires. The four chips also surface high-signal capability themes for users who arrived without a specific question.
- **Logged:** May 15, 2026 (design carried over from May 14 session)
