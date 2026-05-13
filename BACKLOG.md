# MattGPT Backlog

Work state for the MattGPT project. The matrix below is the scannable view. Detail blocks for each item follow, linked by ID. Completed items live in `CHANGELOG.md`. Architectural decisions live in `docs/ADR.md`. Current system state lives in `ARCHITECTURE.md`.

---

## Matrix

| ID | Title | Status | Priority | Type | Logged |
|---|---|---|---|---|---|
| [MATTGPT-012](#mattgpt-012) | Role Match — Phase 4: Private View | In Progress | High | Action | Apr 2026 |
| [MATTGPT-014](#mattgpt-014) | Pipeline Test Strategy Decision | Open | High | Spike | Apr 28, 2026 |
| [MATTGPT-015](#mattgpt-015) | JPM Payments IQ Differentiation | Open | High | Action | Mar 2026 |
| [MATTGPT-016](#mattgpt-016) | Semantic Router — Wrong-Person Query Detection | Open | High | Issue | Apr 2026 |
| [MATTGPT-017](#mattgpt-017) | Streamlit Runtime Test Strategy | Open | Medium | Spike | Apr 28, 2026 |
| [MATTGPT-018](#mattgpt-018) | Page-Load Flicker | Open | Medium | Issue | Pre-Apr 2026 |
| [MATTGPT-019](#mattgpt-019) | Story Count Code Fix | Open | Medium | Refactor | Pre-Apr 2026 |
| [MATTGPT-020](#mattgpt-020) | Simplify backend_service.py | Open | Medium | Refactor | Pre-Jan 2026 |
| [MATTGPT-021](#mattgpt-021) | diversify_results() Pinning Bug | Open | Medium | Issue | Apr 2026 |
| [MATTGPT-022](#mattgpt-022) | Data Quality Cleanup Journey Story | Open | Medium | Action | Mar 2026 |
| [MATTGPT-039](#mattgpt-039) | Automated Regression Detection (GitHub Actions) | Open | Medium | Action | Apr 29, 2026 |
| [MATTGPT-040](#mattgpt-040) | Eval Coverage Gaps — Follow-up Queries | Open | Medium | Action | Apr 29, 2026 |
| [MATTGPT-057](#mattgpt-057) | Architecture documentation alignment | Open | Medium | Action | May 11, 2026 |
| [MATTGPT-023](#mattgpt-023) | LLM Meta-Commentary on Q20 (Stochastic) | Open | Low | Issue | Apr 2026 |
| [MATTGPT-024](#mattgpt-024) | Clarify Hybrid Scoring | Open | Low | Refactor | Pre-2026 |
| [MATTGPT-025](#mattgpt-025) | Add Error Handling Tests | Open | Low | Action | Pre-2026 |
| [MATTGPT-026](#mattgpt-026) | Clarify Layer Ownership | Open | Low | Refactor | Pre-2026 |
| [MATTGPT-027](#mattgpt-027) | Quarterly Intent Review | Open | Low | Action | Jan 2026 |
| [MATTGPT-028](#mattgpt-028) | Share Link Copy Functionality | Open | Low | Issue | Pre-2026 |
| [MATTGPT-029](#mattgpt-029) | Low-Confidence Banner Edge Cases | Open | Low | Issue | Pre-2026 |
| [MATTGPT-030](#mattgpt-030) | Related Projects Selection State | Open | Low | Issue | Pre-2026 |
| [MATTGPT-031](#mattgpt-031) | Semantic Router Error Path Coverage | Open | Low | Action | Pre-2026 |
| [MATTGPT-032](#mattgpt-032) | LLM Response Broken Markdown | Open | Low | Issue | Pre-2026 |
| [MATTGPT-033](#mattgpt-033) | Ask Agy Button Shifts on Focus | Open | Low | Issue | Pre-2026 |
| [MATTGPT-034](#mattgpt-034) | Dead Code Cleanup (Remaining) | Open | Low | Refactor | Pre-2026 |
| [MATTGPT-035](#mattgpt-035) | Eval Modernization — Semantic Scoring | Open | Low | Spike | Pre-2026 |
| [MATTGPT-041](#mattgpt-041) | 5P Dimensional Drill-Down | Open | Low | Spike | Apr 29, 2026 |
| [MATTGPT-042](#mattgpt-042) | 5P Pattern Taxonomy | Open | Low | Spike | Apr 29, 2026 |
| [MATTGPT-043](#mattgpt-043) | Humane Framing — Intent-to-Tone Mapping | Open | Low | Spike | Apr 29, 2026 |
| [MATTGPT-044](#mattgpt-044) | Pattern Insights — Structured Templates | Open | Low | Spike | Apr 29, 2026 |
| [MATTGPT-045](#mattgpt-045) | Analytics Dashboard | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-046](#mattgpt-046) | Latency Benchmarks | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-047](#mattgpt-047) | Cost Tracking | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-058](#mattgpt-058) | Replace dark-theme setInterval polling with MutationObserver | Decided Against | Low | Refactor | May 12, 2026 |
| [MATTGPT-059](#mattgpt-059) | Add Theme-based prefilter dimension to category cards | Open | Low | Spike | May 12, 2026 |
| [MATTGPT-060](#mattgpt-060) | BDD coverage gap — assert post-navigation page state, not just navigation | Open | Medium | Action | May 12, 2026 |
| [MATTGPT-061](#mattgpt-061) | MattGPT portfolio story contaminating organizational leadership queries | Open | Medium | Issue | May 13, 2026 |
| [MATTGPT-010](#mattgpt-010) | Cross-Browser Testing | Parked | Low | Action | Pre-2026 |
| [MATTGPT-048](#mattgpt-048) | Portfolio Integration (Notion, LinkedIn sync) | Parked | Low | Action | Apr 29, 2026 |
| [MATTGPT-049](#mattgpt-049) | Job Fit Broader Scope (cover letter export, LinkedIn auto-extract) | Parked | Low | Action | Apr 29, 2026 |
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
**Pipeline Test Strategy Decision**

- **Status:** Open
- **Priority:** High
- **Type:** Spike
- **Issue:** 17 BDD scenarios in `test_role_match.py` skipped pending decision on how to test scenarios that depend on OpenAI + Pinecone. Covers match results, evidence chips, profile evidence, preferred qualifications, gap explanations, no-fit-score in recruiter view.
- **Options:** (1) Mock OpenAI/Pinecone — deterministic, fast, doesn't validate real LLM output. (2) Run against real backends — validates real behavior, slow/costly/non-deterministic. (3) Snapshot testing — capture known-good response, test rendering against it.
- **Affects:** 17 skipped tests in `test_role_match.py`
- **Logged:** April 28, 2026

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

- **Status:** Open
- **Priority:** High
- **Type:** Issue
- **Issue:** Queries about other people score high against valid intent families. Bezos leadership query scores 0.664 as "leadership" — strong match to a wrong subject.
- **Root cause:** Semantic router has no entity/person detection. Only checks embedding similarity to intent families.
- **Fix:** Add canonical wrong-person phrases to `out_of_scope` family. Same mechanism that already handles off-topic queries — fills a gap, not a new gate layer.
- **Rejected approaches:** Person-name detection before routing (adds gate layer, history shows added gates create complexity and get backed out); lower SOFT_ACCEPT threshold (tried before, caused false rejections on legitimate queries).
- **Affects:** 3 failing tests (Bezos, Elon Musk, "Tell me a joke" scoring 0.429 as "behavioral")
- **Logged:** April 2026 test audit

---

### MATTGPT-017
**Streamlit Runtime Test Strategy**

- **Status:** Open
- **Priority:** Medium
- **Type:** Spike
- **Issue:** 6 BDD scenarios in `test_role_match_logging.py` skipped because they require Streamlit's button click and session state machinery at runtime. Covers chip interactions (2), action button wiring (3), session correlation across interaction types (1).
- **Affects:** 6 skipped tests in `test_role_match_logging.py`
- **Logged:** April 28, 2026

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
**Story Count Code Fix**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor
- **Issue:** Code references "130+" stories in multiple places. Number drifts as stories are added/removed.
- **Fix:** Remove hardcoded "130+" and derive count from JSONL at runtime, or remove the number entirely.
- **Logged:** Pre-April 2026

---

### MATTGPT-020
**Simplify backend_service.py**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor
- **Issue:** 2,034 lines, imports from 4+ modules. Candidates for extraction: entity detection, prompt building.
- **Status note (Jan 29, 2026):** Entity Gate removed, classify_query_intent removed. Still large — grew significantly with Role Match, story intelligence, and prompt architecture work.
- **Logged:** Pre-January 2026

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
- **Logged:** March 2026

---

### MATTGPT-039
**Automated Regression Detection (GitHub Actions)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Eval suite and unit tests are run locally only. No CI pipeline runs them on every PR or push. Drift can land before being detected.
- **Fix:** Wire `eval_rag_quality.py` and `tests/unit/` into a GitHub Actions workflow. Spec has example YAML at `11-testing-and-quality.md` lines 502-512. No architectural blockers — just hasn't been done.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

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
- **Logged:** April 29, 2026

---

### MATTGPT-057
**Architecture documentation alignment**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Scope:** Align stale architecture descriptions across user-facing pages and design spec with current pipeline.
- **Items:**
  - `ui/pages/about_matt.py` — Update "How I Built MattGPT" pseudocode to depict current pipeline (Query → Nonsense Filters → Semantic Router → out_of_scope check → Pinecone → Confidence Gate → LLM). Keep pseudocode form; function names stay illustrative.
  - `ui/components/how_agy_modal.py` — Expand 3-stage framing to match same pipeline shape.
  - `mattgpt-design-spec` — Update "System Architecture Flow" and "5-Stage RAG Pipeline" pages.
  - Factual fixes: drop "Semantic + keyword hybrid scoring" claim (W_KW = 0.0), remove "GitHub Actions" and "CI/CD pipeline" from Tech Stack (MATTGPT-039 still open), verify or drop "6 Industries" stat.
- **History:** First flagged Feb 3, 2026. Parked. Re-surfaced May 11, 2026.
- **Logged:** May 11, 2026

---

### MATTGPT-023
**LLM Meta-Commentary on Q20 (Stochastic)**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** "Who is Matt Pugmire?" sometimes generates meta-commentary ("showcases his") instead of direct biographical content. Stochastic — passes on some runs, fails on others.
- **Root cause:** LLM occasionally ignores the "never evaluate Matt" prompt instruction for broad biographical queries.
- **Fix:** Monitor — if it becomes consistent, add Q20-specific prompt reinforcement.
- **Logged:** April 2026 test audit

---

### MATTGPT-024
**Clarify Hybrid Scoring**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Issue:** Pinecone scores (0.0-1.0) don't map clearly to confidence buckets (0.15-0.25).
- **Fix:** Document or align the scoring systems.

---

### MATTGPT-025
**Add Error Handling Tests**

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Issue:** Test suite only covers happy path.
- **Fix:** Add tests for rate limits, timeouts, embedding failures.

---

### MATTGPT-026
**Clarify Layer Ownership**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Issue:** Ranking, intent classification, and formatting split across multiple files.
- **Fix:** Document contracts or refactor boundaries.

---

### MATTGPT-027
**Quarterly Intent Review**

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Issue:** 15 intent families with ~20 phrases each in `semantic_router.py`. Phrases drift relevance over time.
- **Fix:** Schedule quarterly review.
- **Last review:** January 29, 2026

---

### MATTGPT-028
**Share Link Copy Functionality**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Verify share link copy-to-clipboard works correctly across browsers.

---

### MATTGPT-029
**Low-Confidence Banner Edge Cases**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Low-confidence banner sometimes triggers incorrectly. Review threshold logic.

---

### MATTGPT-030
**Related Projects Selection State**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Edge cases in purple highlight, close toggle, rapid clicks.

---

### MATTGPT-031
**Semantic Router Error Path Coverage**

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Issue:** Limited test coverage for semantic router error handling paths.

---

### MATTGPT-032
**LLM Response Broken Markdown**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** LLM outputs `**4X **` instead of `**4X**` — space before closing asterisks breaks bold rendering.
- **Fix:** Post-process regex: `r'\*\*([^*]+)\s+\*\*'` → `**\1**`

---

### MATTGPT-033
**Ask Agy Button Shifts on Focus**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Button shifts position when focused. CSS fix for focus state needed.

---

### MATTGPT-034
**Dead Code Cleanup (Remaining)**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Issue:** Audit `services/query_logger.py` (was orphaned; see MATTGPT-013 for current state), `utils/scoring.py` for unused functions, sweep old TODO/FIXME comments.

---

### MATTGPT-035
**Eval Modernization — Semantic Scoring**

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
- **Issue:** Current eval uses keyword matching. Semantic similarity or LLM-as-Judge would be more robust.
- **Trade-off:** More expensive per run, harder to debug failures. Current concept-cluster approach (Q2/Q5 style) may be good enough.

---

### MATTGPT-041
**5P Dimensional Drill-Down**

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
- **Issue:** Voice guide describes 5P (Person/Place/Purpose/Process/Performance) as a metadata framework for pattern recognition and deep dives. The spec envisions Agy offering to drill into a specific dimension on demand (e.g., "Want me to dig deeper into the process?"). This conversational affordance doesn't exist — Agy can't currently zoom into a single 5P dimension by request.
- **Current state:** 5P data integration is substantially implemented. `story_intelligence.py` uses all five 5P fields as STAR fallbacks in context assembly. `5PSummary` is embedded in vectors (influences retrieval). Verbatim phrase extraction works via `prompts.py`. What's missing is the *conversational* use — the ability to drill into one dimension.
- **Spike question:** Is dimension-specific drill-down worth building? Would users ask "tell me more about the process" or "what was Matt's role" as follow-ups? If so, this is a multi-turn conversational feature, not a prompt structure change.
- **Note:** The voice guide does NOT describe a 5P narrative arc for response structure. It describes 5P as input enrichment and a lens for pattern recognition — not as a replacement for WHY→HOW→WHAT output structure.
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-042
**5P Pattern Taxonomy**

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
- **Issue:** Voice guide describes structured pattern templates ("By Outcome," "By Methodology," "By Challenge") with explicit category labels for cross-story synthesis. Production synthesis is more open-ended — gives the LLM the stories and asks for patterns via WHY→HOW→WHAT, but doesn't prescribe categories.
- **Spike question:** Does prescribed taxonomy improve pattern recognition responses, or is the open-ended approach better?
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-043
**Humane Framing — Intent-to-Tone Mapping**

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
- **Issue:** Voice guide describes intent-specific response framing — Agy detects why someone is asking (interview prep vs. vetting vs. curiosity vs. hiring pitch vs. networking) and adapts tone, framing language, and offers accordingly. Specific intent-to-tone mapping is not implemented.
- **Current state:** Spirit exists via random focus angles in `_generate_agy_response()` (lines 888-896) which inject emphasis on human impact, methodology, scale, leadership, outcomes, or innovation. But this is random, not intent-driven.
- **Tradeoff:** Implementing deterministic intent-to-tone mapping risks reintroducing meta-commentary patterns that the current architecture deliberately removed. The previous prompt architecture had a `theme_guidance` variable closer to this vision but was replaced for anti-meta-commentary discipline (see commented-out prompt at `backend_service.py` lines 1040-1164).
- **Spike: Evaluate whether deterministic intent-to-tone mapping is worth the anti-meta-commentary risk.**
- **Source:** Voice Guide Implementation Audit, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-044
**Pattern Insights — Structured Templates**

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
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

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Issue:** No latency tracking exists. No `time.time()`, no `perf_counter()`, no duration fields in the logger schema. Can't detect performance regressions over time.
- **Fix:** Wrap OpenAI API calls and Pinecone search in timing blocks. Add duration column to logger schema. Build reporting view over accumulated data for p50/p95 tracking.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-047
**Cost Tracking**

- **Status:** Open
- **Priority:** Low
- **Type:** Action
- **Issue:** No per-query cost tracking in production. OpenAI response includes `usage.prompt_tokens` and `usage.completion_tokens` but `backend_service.py` doesn't read them. Cost estimates exist only in offline batch scripts (`generate_use_cases.py`, `generate_public_tags.py`).
- **Fix:** Read token usage from OpenAI response object, log per-query token counts and computed cost. Fold into MATTGPT-013 logger schema work — minimal incremental work if done alongside.
- **Dependencies:** Coordinate with MATTGPT-013 to avoid double-touching the schema.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-010
**Cross-Browser Testing**

- **Status:** Parked
- **Priority:** Low
- **Reason:** Low priority until React migration. Streamlit handles most cross-browser issues.

---

### MATTGPT-048
**Portfolio Integration (Notion, LinkedIn sync)**

- **Status:** Parked
- **Priority:** Low
- **Type:** Action
- **Proposed:** Programmatic sync between MattGPT story corpus and external systems (Notion job tracker, LinkedIn experience sections).
- **Reason parked:** Real idea, no urgency, no foundation work started. Notion sync was already noted as out-of-scope for Role Match v1 ("manual copy of fit score acceptable"). Revisit when traffic patterns or use cases create a forcing function.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

---

### MATTGPT-049
**Job Fit Broader Scope (cover letter export, LinkedIn URL auto-extract)**

- **Status:** Parked
- **Priority:** Low
- **Type:** Action
- **Proposed:** Extensions to Role Match: cover letter export from match results, LinkedIn URL parsing to auto-extract job descriptions.
- **Reason parked:** Natural extensions to Role Match Phase 4, but no user demand signal yet, no architectural hooks. Revisit if Role Match usage signals demand for these features.
- **Source:** Cross-reference of design spec vs. implementation, April 29, 2026
- **Logged:** April 29, 2026

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

- **Status:** Open
- **Priority:** Low
- **Type:** Spike
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
- **Coverage targets (one scenario each):**
  - Card 1 (Banking) — subpage navigation + page-specific content present
  - Card 2 (Cross-Industry) — subpage navigation + page-specific content present
  - Card 3 (Product Innovation) — `prefilter_domains` applied, result count < total
  - Card 4 (Application Modernization) — `prefilter_capability` applied, result count < total
  - Card 5 (Consulting & Transformation) — `prefilter_domains` applied, result count < total
  - Card 6 (Teams & Talent Development) — `prefilter_domains` applied, result count < total
- **Lesson framing:** "Verifying the link works isn't the same as verifying the destination state is correct." Every prefilter-triggering button needs a state assertion, not just a navigation assertion.
- **Root-cause incident:** May 12, 2026 — Card 3 prefilter discovered broken; Path A fix landed in same session. Pre-existing regression; ship date unknown.
- **Logged:** May 12, 2026

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
- **Related:** MATTGPT-021 (diversify_results pinning), MATTGPT-016 (semantic router wrong-person detection). Same broader theme: retrieval over-ranking on semantic overlap without semantic intent disambiguation.
- **Logged:** May 13, 2026
