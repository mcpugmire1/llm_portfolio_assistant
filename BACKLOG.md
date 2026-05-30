# MattGPT Backlog

Work state for the MattGPT project. The matrix below is the scannable view. Detail blocks for each item follow, linked by ID. Completed items live in `CHANGELOG.md`. Architectural decisions live in `docs/ADR.md`. Current system state lives in `ARCHITECTURE.md`.

---

## Value Prioritized Roadmap (updated 2026-05-28)

**NOW** (suggested order of execution):
1. **-087 + -092** — Hero code pass: CTA routing + seniority signal bundled (~2 hours, one commit)
2. **-077 mitigation** — Query-side mitigation: strip "Matt" from embedded queries on technical-noun shapes (hours, not days; full hybrid retrieval lives in NEXT)
3. **-094 probes** — CIC over-concentration + operational under-surfacing probes; parallel-runnable, read-only; informs NEXT content work
4. **-088** — Role Match scorer alignment (loose dependency on -077 mitigation: do cleaner if you can, not wait until you can)
5. **-097** — Career-intent refresh (active recruiter failure earns NOW slot)

(MATTGPT-090 removed from NOW — closed as Decided Against May 29, 2026. Personal Intent Family in `services/semantic_router.py:192-209` already handles comp queries with the warm decline; no system prompt edit needed.)

**NEXT** (queued):
1. **-015** — JPM Payments IQ differentiation (high-priority since March; upstream of operational surfacing)
2. **-077 full fix** — Hybrid retrieval (BM25 + semantic); handles severe-overlap nouns and addresses -061 residual
3. **-089** — Role Match location / work-model / availability parsing
4. **-074** — Entity cluster forcing synthesis (depth side of CIC; pairs with -094 for over/under pattern)
5. **-091 audit phase** — Does existing failure content surface on probe queries? Fold into -077/-094 or return Phase 3 write as LATER
6. **-093** — About Matt strategic restructure toward one-pager direction (multi-week, strategically significant)

(Everything else defaults to LATER.)

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
| [MATTGPT-061](#mattgpt-061) | MattGPT portfolio story contaminating organizational leadership queries | Resolved | Medium | Issue | May 13, 2026 |
| [MATTGPT-062](#mattgpt-062) | Semantic router cache silently uses stale embeddings when VALID_INTENTS changes | Open | Medium | Refactor | May 14, 2026 |
| [MATTGPT-063](#mattgpt-063) | Wrong-person queries with names outside nonsense regex produce confused-context RAG answers | Open | Medium | Issue | May 14, 2026 |
| [MATTGPT-064](#mattgpt-064) | Explore Stories — Table row hover/cursor doesn't apply to data cells (AgGrid selector fix) | Open | Low | Issue | May 15, 2026 |
| [MATTGPT-065](#mattgpt-065) | Explore Stories — Polish bundle (filter UX, empty states, story details) | Open | Medium | Action | May 15, 2026 |
| [MATTGPT-066](#mattgpt-066) | Role Match — Sample JD / "Try a sample role" cold-start affordance | Open | Medium | Action | May 15, 2026 |
| [MATTGPT-067](#mattgpt-067) | Role Match — Result panel and input polish bundle | Open | Low | Action | May 15, 2026 |
| [MATTGPT-068](#mattgpt-068) | About Matt — Content polish bundle (clickable questions, code expander, DevOps card merge) | Done | Medium | Action | May 15, 2026 |
| [MATTGPT-069](#mattgpt-069) | Home — Stats label contrast (light mode WCAG AA) | Open | Low | Issue | May 15, 2026 |
| [MATTGPT-070](#mattgpt-070) | Ask MattGPT — Suggestion button cursor pointer | Open | Low | Issue | May 15, 2026 |
| [MATTGPT-071](#mattgpt-071) | Nonsense rejection banner — branch-aware copy + contextual chip sets | Done | Medium | Action | May 15, 2026 |
| [MATTGPT-072](#mattgpt-072) | `generate_public_tags.py` — case-insensitive tag dedup | Open | Low | Refactor | May 16, 2026 |
| [MATTGPT-073](#mattgpt-073) | `last_primary_client` session state produces order-dependent retrieval within multi-turn sessions | Resolved | High | Issue | May 18, 2026 |
| [MATTGPT-074](#mattgpt-074) | Entity cluster promotion forces synthesis mode when users want depth (e.g., "How did you build the CIC?") | Open | Medium | Issue | May 18, 2026 |
| [MATTGPT-075](#mattgpt-075) | Developer debug surfaces leak to user-facing UI (sidebar print, telemetry badge) | Open | Medium | Issue | May 18, 2026 |
| [MATTGPT-076](#mattgpt-076) | "How Agy Works" modal iframe overflows / does not resize correctly on mobile | Open | Medium | Issue | May 18, 2026 |
| [MATTGPT-077](#mattgpt-077) | Subject-pronoun + noun-overlap retrieval contamination — "Matt + X" pulls MattGPT/Strangler Fig stories when X overlaps their vocabulary | Open | Medium-High | Issue | May 19, 2026 |
| [MATTGPT-078](#mattgpt-078) | New corpus story — "AI Enablement Before It Had a Name" (resume Option E retrieval anchor) | Open | Medium | Action | May 21, 2026 |
| [MATTGPT-079](#mattgpt-079) | Role Match coverage gaps — corpus story anchors needed (meta-ticket) | Open | Medium | Action | May 21, 2026 |
| [MATTGPT-080](#mattgpt-080) | `matt_profile.json` — restructure into parallel evidence sources (identity / skills with provenance / STAR corpus / positioning) | Open | Medium | Architecture | May 21, 2026 |
| [MATTGPT-081](#mattgpt-081) | Role Match engine — corrective-actions output by asset type (story / resume / LinkedIn / positioning / network / real skill) | Open | Medium | Enhancement | May 21, 2026 |
| [MATTGPT-082](#mattgpt-082) | Q15 eval assertion is over-specified — checks literal client name presence rather than response correctness | Open | Medium | Refactor | May 22, 2026 |
| [MATTGPT-083](#mattgpt-083) | Spinner inconsistency — Explore Stories doesn't show thinking indicator for rejected queries (Ask MattGPT does) | Open | Medium | Issue | May 23, 2026 |
| [MATTGPT-084](#mattgpt-084) | Ask MattGPT BDD scenarios — chip-click + low_confidence banner-render timing flakes under full-suite load | Open | Medium | Issue | May 23, 2026 |
| [MATTGPT-085](#mattgpt-085) | `secrets.toml` `MATTGPT_PRIVATE_BYPASS_TOKEN` parity + dead `private_access_code` cleanup + doc drift | Open | Medium | Refactor | May 23, 2026 |
| [MATTGPT-086](#mattgpt-086) | Query logger — add environment annotation column + filter dev/test traffic out of production analytics | Open | Low | Issue | May 23, 2026 |
| [MATTGPT-087](#mattgpt-087) | Home hero — recruiter-routing CTA to Role Match | Open | High | Action | May 28, 2026 |
| [MATTGPT-088](#mattgpt-088) | Role Match scorer — align with Agy honesty (no Strong Match when chat would say no) | Open | High | Issue | May 28, 2026 |
| [MATTGPT-089](#mattgpt-089) | Role Match — parse location, work-model, availability as distinct filter class | Open | High | Issue | May 28, 2026 |
| [MATTGPT-090](#mattgpt-090) | System prompt — decline cleanly on comp / off-scope queries (no silent fallback) | Decided Against | Medium | Action | May 28, 2026 |
| [MATTGPT-091](#mattgpt-091) | Add a credible failure story to the corpus (sibling to -022 / -078 pattern) | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-092](#mattgpt-092) | Hero — explicit seniority signal (supersedes May 15 design-call closure) | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-093](#mattgpt-093) | About Matt — strategic restructure (split / fold / reframe meta-question) | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-094](#mattgpt-094) | Retrieval concentration audit — CIC over-weighting + operational story under-surfacing (hypotheses to verify) | Open | High | Investigation | May 28, 2026 |
| [MATTGPT-095](#mattgpt-095) | Anti-consulting bias in story framing — corpus reads "consulting" as default register when it shouldn't | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-096](#mattgpt-096) | Methodology context dropped during synthesis — TDD/BDD and ways-of-working substance gets compressed out of metric claims (hypothesis to verify) | Open | Medium | Issue | May 28, 2026 |
| [MATTGPT-097](#mattgpt-097) | Career-intent framing refresh — corpus predates current role taxonomy; refresh framing AND tighten register | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-098](#mattgpt-098) | Explore Stories default state — exclude Professional Narrative + sort Start_Date desc (match Timeline behavior) | Open | Medium | Action | May 29, 2026 |
| [MATTGPT-099](#mattgpt-099) | Role Match — assess and decide comp handling on JDs that include comp expectations | Open | Medium | Investigation + Action | May 29, 2026 |
| [MATTGPT-100](#mattgpt-100) | Navigation labels — rename to Home / My Work / Ask Agy / Role Match / My Profile (wireframe-locked) | Open | Medium | Refactor | May 30, 2026 |
| [MATTGPT-101](#mattgpt-101) | Why Agy? modal + "?" badge on Agy avatar (uniform placement) | Open | Medium | Action | May 30, 2026 |
| [MATTGPT-102](#mattgpt-102) | How I Built MattGPT — relocate from About Matt section to standalone deep-link surface (no main nav entry) | Open | Medium | Action | May 30, 2026 |
| [MATTGPT-103](#mattgpt-103) | Agy intro line — resolve "20+ years of work" inconsistency with stats bar (Years tile dropped) | Open | Low | Refactor | May 30, 2026 |
| [MATTGPT-104](#mattgpt-104) | Banking + Cross-Industry landing pages — math reconciliation bug (33 vs 32 vs 48 vs 57 inconsistency) | Open | Medium | Issue | May 30, 2026 |
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
- **Additional symptom captured May 18, 2026 — Explore Stories specifically:**
  - On navigation to Explore Stories, the **page header renders correctly** ("Project Stories & Insights" with the gradient banner), but the **content area briefly renders the entire Ask MattGPT intro** — "Ask MattGPT" subheader, the large Agy-with-headphones avatar, "Hi, I'm Agy 🐾", suggestion chips — before the actual AgGrid hydrates. Captured in Chrome DevTools Performance recording.
  - **Diagnosis:** This is NOT a "large Agy icon placeholder" as I initially described. It's the **wrong page's content rendering briefly under the right page's header.** The Ask MattGPT page's render output is appearing in Explore Stories' content area during a transient state, then getting replaced by the correct AgGrid + filter UI.
  - **Likely cause:** Streamlit's page-switching state management. When `active_tab` changes from "Ask MattGPT" → "Explore Stories", the navbar/header renders the new page header on the first rerun, but the previous page's content body is still mounted in the DOM until the new page's content fully renders. Possible mechanisms:
    - `active_tab` toggle triggers a rerun where header re-renders but content body is mid-transition
    - The Explore Stories page's slow-to-hydrate components (AgGrid JS bootstrap, Pinecone-related fetches) leave a render gap
    - Streamlit's cached content from the previous page may not be cleared until the new page's first paint is complete
  - **Investigation entry points:**
    - `app.py` page routing logic — how does it decide which page to render on `active_tab` change?
    - The navigation pattern in `category_cards.py:on_chip_click()` and similar cross-page seed_prompt navigation — these set `active_tab` and `st.rerun()`. The rerun may produce the transient state.
    - Compare against Streamlit's "single page app" page-switch idioms — there are known patterns for cleanly clearing content between page changes.
  - **Production evidence:** Chrome DevTools Performance recording captured May 18, 2026 immediately after the MATTGPT-073/-061 deploy. Reproducible (intermittent) by navigating from Ask MattGPT → Explore Stories.
  - **Core Web Vitals from DevTools Performance Insights (May 18, 2026):**
    - **CLS = 0.69** — "Poor" range (Core Web Vitals threshold for "Poor" is > 0.25). Confirms the wrong-content flash is a real layout shift, not a paint artifact. The original MATTGPT-018 framing said "CLS = 0, so it's a paint issue" — that was true for the blank-frame symptom but NOT for this new wrong-page-content symptom. The two symptoms have different mechanisms.
    - **LCP = 46ms** — excellent (target < 2500ms). Rules out slow loading as root cause; the page renders fast but renders wrong content during the transition.
    - **INP** — not measured in this recording (no interaction during capture).
  - **DevTools timeline observations:**
    - **30+ cascading CSS animations** during the transition window: scrollbar-color (12 instances), opacity (8 instances), border-left-color / border-top-color / border-bottom-color / border-right-color, background-color. Pattern indicates the entire page tree is re-mounting rather than just the changed pieces.
    - **Named Streamlit animation `animation-1wgitoe`** firing as part of the page swap — this is Streamlit's auto-generated fade-in class for new content.
  - **Related insights surfaced (separate issues, not blocking the flicker fix):**
    - Image delivery: ~1.4 MB potential savings (apy_explore_stories.png, apy_avatar.png larger than needed)
    - 3rd-party telemetry to webhooks.fivetran.com (not relevant to the flicker)
  - **Three distinct visual artifacts captured during the same Ask MattGPT → Explore Stories transition (May 18, 2026):**
    1. **Wrong-page-content flash** — Ask MattGPT intro (Agy avatar, "Hi, I'm Agy 🐾", suggestion chips) renders under the "Project Stories & Insights" Explore Stories header. Captured in DevTools Performance recording frame.
    2. **Blank-AgGrid state** — Explore Stories page header + filter UI ("Find stories", Industry/Capability dropdowns, Advanced Filters, "Showing 1-20 of 113 projects") render correctly, but the AgGrid content area is empty white space. Purple gradient placeholders visible at the bottom. AgGrid JS bootstrap hasn't completed yet.
    3. **Agy icon above hero banner** — a small Agy avatar renders transiently at the very top of the page, above the navbar/hero banner. Different location and size than the avatars rendered in normal page layouts.
  - **Interpretation:** All three are facets of the same page-transition mechanism (page-tree re-mount + cascading animations) but represent different snapshot moments in the render sequence. A fix targeting the root cause (transition state management) should resolve all three.
- **Logged:** Pre-April 2026, investigated April 28, 2026 (blank-frame symptom); supplemented May 18, 2026 (Explore Stories Agy-icon-flash symptom)

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

- **Status:** Resolved (May 18, 2026)
- **Resolution summary:** The session-state contamination mechanism that drove the most visible user-facing failures was removed via MATTGPT-073. Validated empirically against 12 production-traffic queries with 11 of 12 producing clean user-visible responses; the single residual failure (Q2 "transformations" polysemy) is a documented structural limit of pure semantic search, scoped to hybrid retrieval (NEXT roadmap), not corpus work.
- **Empirical evidence base for the resolution (May 18, 2026):**
  - **12 production-traffic queries tested.** Sources: top-frequency leadership/behavioral queries from the production query log (Apr 13 to May 18) plus Matt's diagnostic set.
    - Q1 "What kind of leader is Matt?" (5x in production) — clean
    - Q2 "How does Matt handle resistance in large-scale transformations?" (3x in production) — ❌ contaminated (Strangler Fig wins Pinecone #1 on "transformation" polysemy)
    - Q3 "How does Matt show up when things go wrong?" (5x) — clean
    - Q4 "Tell me about MattGPT's product vision?" (regression check) — clean
    - Q5 "How does Matt manage resistance when leading enterprise transformation programs?" (2x) — clean
    - Q-Scale "Scale a CIC to 150+ engineers" (3x) — clean (entity filter excludes MattGPT)
    - Q-Skeptical "How does Matt bring skeptical stakeholders along during large-scale change programs?" (2x) — clean (this was the May 13 contamination case; now resolved)
    - Q-Teammates "How would Matt's former teammates describe him?" (2x) — clean DESPITE Pinecone returning 4 MattGPT stories in top 8 (LLM correctly filters)
    - Q-Equip "How did Matt equip teams for New IT ways of working" — clean
    - Q-Monolith "How do you modernize monoliths into microservices" — clean
    - Q-Prototype "How did Matt approach rapid prototyping" — clean
    - Q-4x "How do you achieve 4x faster delivery?" — clean
    - Q-CrossFn "How do you align cross-functional teams?" — clean
  - **11 of 12 = 91.7% clean responses on real production-traffic queries.**
  - **61-query eval suite passing 100% post resolution** (validated twice; first run 69/70 was LLM stochasticity on Q64 that cleared on rerun).
  - **Q-Teammates is the strongest single signal.** Pinecone top 8 contained 4 MattGPT stories (Product Vision at #3, UX Design at #5, Strangler Fig at #6, RAG Architecture at #7), yet the LLM response contained no MattGPT mention and led with Accenture CIC + servant leadership + $100M+ business. Direct evidence that LLM-level filtering closes the gap between Pinecone-score-level contamination and user-visible response contamination.
- **Why corpus work alone could not fix the residual Q2 case:**
  - Saturday's reductive enrichment of Story 69 raised its Q1 score from 0.341 to 0.380 (wrong direction).
  - The MattGPT stories' content (vision, roadmap, OKRs, scope) is genuinely semantically adjacent to "leadership" concepts. The embedding model correctly identifies this similarity.
  - "Transformation" is polysemic: technical refactoring vs. organizational change management. Pinecone cannot disambiguate without keyword anchoring.
  - Three iterations of corpus-side edits demonstrated the ceiling. Additional editorial work risks distorting story content without closing the polysemy gap.
- **What was actually fixed:**
  - The cross-query `last_primary_client` session-state mechanism (the dominant user-visible failure pattern). Closed via MATTGPT-073. See ADR 019.
  - Story 69 body rewrite + Theme change (cleaner story, even if Pinecone score went the wrong way).
  - Strangler Fig title and body rewrite ("I Built a Monolith by Accident. Here's How I Fixed It"), tag cleanup.
  - NS Mainframe / "The CIC's First Engagement" rewrite to align with servant-leadership voice across portfolio.
  - `generate_public_tags.py` Era-aware prompt that prevents future enrichment runs from re-adding contaminating tags to Independent Product Development stories.
- **What remains (out of scope for -061; tracked separately):**
  - **Q2 polysemy on "transformations"** — Strangler Fig wins Pinecone #1, leads contaminated response. Structural to pure semantic search. Fixable via hybrid retrieval (NEXT roadmap) or accepted as known tail-quality edge case. Q2's exact phrasing is a diagnostic query, not a frequent production pattern; Q5 (same intent in slightly different words) works cleanly.
  - **Subject-pronoun + noun-overlap free-text contamination** — MATTGPT-077 (May 19, 2026). The broader retrieval-bias pattern that -061's session-state fix did not address: "Matt + [MattGPT/Strangler Fig-overlap noun]" reliably contaminates retrieval; severe-overlap nouns ("refactoring") contaminate even with "you" phrasing. Validated May 19 2026 across 8 production probe queries. -077 gives -061's open structural residual a reproducible mechanism and broader scope.
  - **Entity cluster promotion forces synthesis on depth queries** — MATTGPT-074 captures this design tension (e.g., "How did you build the CIC?" gets breadth-synthesis instead of depth). Independent of -061.
  - **diversify_results pinning/limit bugs** — MATTGPT-021, pre-existing.
  - **Pinecone debug panel leaking to user UI** — MATTGPT-075, surfaced May 18 2026 during production query replay.
- **Architectural decisions captured:** ADR 019 (no cross-query session state in diversify_results).
- **(Original Status / Priority / Type before resolution: Open / Medium / Issue)**

---

**Original ticket content preserved below for historical context** (May 13–16, 2026):

- **Issue:** MattGPT-related stories (Building MattGPT, Strangler Fig refactor, portfolio-narrative voice) surface as top results for organizational-leadership / change-management queries where they are the wrong answer. This is a **longstanding, recurring pattern** — not a single incident. The May 13, 2026 chip CX testing is the trigger for filing the ticket; the underlying retrieval bias has been observed repeatedly. The MattGPT stories have broad semantic overlap with queries about "transformation", "stakeholders", "value proposition", "scale", and "challenge" — so Pinecone ranks them highly for queries that are not about building MattGPT or about Matt's portfolio-building narrative.
- **Evidence (May 13, 2026 chip CX testing):**
  - **Query:** *"How does Matt handle resistance in large-scale transformations?"*
    - Response opened with the MattGPT refactor story (strangler fig pattern, 5,765 → 1,014 lines), instead of organizational change-management stories. The Norfolk Southern legacy-mainframe resistance story and JP Morgan Dynamics CRM stabilization story — both of which directly answer the query — were not surfaced.
  - **Query:** *"How does Matt bring skeptical stakeholders along during large-scale change programs?"*
    - Response opened with "convincing recruiters of value" framing pulled from the MattGPT portfolio-building narrative, with CIC scaling stats grafted in as evidence. The query is about stakeholder change management; the response is about Matt's career marketing.
  - **Counter-example (works):** *"How does Matt manage resistance when leading enterprise transformation programs?"* — the rephrase that adds "enterprise" + "programs" pulled the right stories (Norfolk Southern + JP Morgan). This is the workaround currently shipped as chip 3 on Home (May 13, 2026).
- **Evidence (May 16, 2026 — fresh production reproduction during MATTGPT-071 chip validation):**
  - **Query:** *"What kind of leader is Matt?"* (proposed `personal` branch chip in MATTGPT-071)
    - Response correctly opened with CIC scaling, servant leadership, psychological safety, and enterprise client work. But the **fourth paragraph** contaminated the answer: *"During his sabbatical, Matt continued to lead by example, building MattGPT, an AI-powered portfolio assistant. This project demonstrated his product thinking and technical capabilities, further solidifying his leadership narrative."*
    - **Why it's wrong:** an internal sabbatical portfolio project is Matt-as-builder, not Matt-as-org-leader. The query is asking what kind of leader Matt is in professional contexts (teams, clients, transformations); the MattGPT story has no organizational-leadership content. The phrase *"solidifying his leadership narrative"* is meta-commentary about the portfolio's purpose, not actual leadership evidence.
    - **Pattern match:** identical to the May 13 captures — MattGPT story's high-frequency leadership vocabulary ("leadership narrative", "product thinking", "technical capabilities") wins on semantic similarity against broad org-leadership queries.
    - **Blocking impact:** This contamination directly damages MATTGPT-071's value. The chip "What kind of leader is Matt?" was designed to redirect users into a credible leadership answer; instead it surfaces a sabbatical-project name-drop. Recruiters who click the chip see Matt's career-marketing meta-narrative when they wanted Matt's leadership substance. -071 chip effectiveness depends on -061 being resolved first.
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

**May 16, 2026 — Deep investigation + three iteration cycles**

A full-day session walked through corpus enrichment as the proposed fix. Three iterations produced concrete empirical findings that change the recommendation.

**Two contamination mechanisms identified empirically:**

Capture from 7 diagnostic queries with DEBUG mode on. Pinecone scores and full LLM context tracked across iterations.

| Mechanism | Description | Example |
|---|---|---|
| **A — `diversify_results()` promotion** | Pinecone returns mostly on-topic stories; `diversify_results` pulls a sub-optimal off-topic story up to break client homogeneity. The "right" story is demoted out of the final LLM context. | Q1 ("What kind of leader is Matt?"): top 5 Pinecone hits are all on-topic Accenture leadership stories. MattGPT Product Vision sits at #6 with a 0.006 score gap below #5. `diversify_results` promotes it to LLM slot #2 to break the Accenture run, demoting "Sustainable Leadership" out of the LLM context. |
| **B — Pinecone over-ranks meta-narrative outright** | Pinecone ranks meta-narrative stories at #1 or #2 due to genuine semantic similarity. `diversify_results` doesn't need to promote anything — they're already at the top. | Q2 ("How does Matt handle resistance in large-scale transformations?"): MattGPT Strangler Fig ranks at Pinecone #1 (0.437) — tied with Why Hire Matt. AI-Assisted Dev Workflows at #4 (0.418). |

**Three corpus-enrichment iterations and their outcomes:**

1. **Story 69 (MattGPT Product Vision) body rewrite + Theme change.** Removed "Strategic Positioning" / "Portfolio Differentiation" / "differentiate in senior-level market" framing; Theme changed from `Strategic & Advisory` to `Execution & Delivery`. **Result:** Story 69's Pinecone score on Q1 went UP from 0.341 to 0.377 — the body rewrite concentrated technical product-leadership vocabulary that the embedding model treats as semantically close to "what kind of leader" queries. BUT the LLM produced clean Q1, Q3, Q4 responses despite Story 69 being in context. **Net: validated at user-visible response level on first run; failed on Pinecone-score-reduction goal.**

2. **Competencies cleanup (`Strategic Roadmapping` → `Product Roadmapping`).** Same iteration; no measurable score change.

3. **Strangler Fig story rewrite (new title "I Built a Monolith by Accident. Here's How I Fixed It") + NS Mainframe rewrite ("The CIC's First Engagement: Coaching Modern Engineering at Norfolk Southern").** **Result:** Strangler Fig score barely moved (0.437 → 0.434). NS Mainframe DROPPED from #5 to #7 (0.414 → 0.394) because the softer "coaching" framing removed "resistance/transformation" vocabulary. Story quality improved (servant-leadership voice consistent across portfolio); Q2 retrieval worsened.

**Structural finding (revised May 18, 2026 after follow-up traces):**

Reductive enrichment of contaminating stories alone is insufficient when combined with `is_generic_client`-driven `generic_overflow` placement and session-state-dependent `diversify_results` behavior. Three iterations of reductive-only enrichment produced corpus quality improvements but not full retrieval cleanup. Bidirectional enrichment of legitimate Class 1 stories (sharpening Why Hire Matt / About Matt / Sustainable Leadership with specific client dynamics) and the session-state `diversify_results` behavior remain open.

**What May 18 follow-up traces revealed (corrected from Saturday's framing):**

- **`Project == "Independent Project"` is treated as generic by `is_generic_client`.** MattGPT stories land in `generic_overflow`, not `named_diverse`. Saturday's proposed score-gap fix on `named_diverse[0]` would never trigger on Q1. The fix needs to compare against `(named_diverse + generic_overflow)[0]` to address the slot #2 promotion path.
- **Q3 "regression" between Saturday morning and evening was session-state, not LLM stochasticity.** A fresh-session Q3 run on May 18 produced a clean response (Why Hire Matt + NS Quality Crisis at LLM slots #1 and #2). The Saturday-evening contamination fired because `last_primary_client = Accenture` from a prior query in the session triggered the line 1293 demotion (gap of 0.001 between Why Hire Matt and MattGPT Product Vision). Filed separately as MATTGPT-073.
- **The corpus rewrites did materially improve retrieval.** Saturday's Story 69, Strangler Fig, and NS Mainframe rewrites moved Q3 from "leads with MattGPT contamination" to "leads cleanly with NS Quality Crisis" once the session-state bug is excluded. The "diminishing returns" framing was wrong — corpus quality work paid off, and the session-state bug was masquerading as a corpus failure.

**Current Q1 gap state (May 18 measurement):**

- pinned = Why Hire Matt (Accenture, 0.433)
- slot-#2 candidate from `generic_overflow` = MattGPT Product Vision (IP, 0.380)
- best duplicate-of-pinned = About Matt Leadership Journey (Accenture, 0.411)
- gap = 0.411 - 0.380 = **0.031**

A 0.05-threshold gap guard does not trigger at this gap. Bidirectional enrichment to widen the gap from below (raise Class 1 story scores) is the prerequisite that would make the gap-guard fix meaningful for Q1.

**Q2 polysemy diagnosis (verified):**

"Transformation" is polysemic. Strangler Fig is a *technical transformation* (code refactoring); Norfolk Southern Mainframe is an *organizational transformation* (change management). Pure-semantic embedding doesn't distinguish them. Even after rewriting both stories, Strangler Fig still wins Q2 retrieval because its technical-transformation vocabulary genuinely overlaps with the query's surface form. **This is a retrieval-strategy problem, not a corpus problem.**

**The W_KW=0.0 investigation:**

Verified that `utils/scoring.py` has hybrid scoring infrastructure (`_hybrid_score` function) but `W_KW = 0.0` disables the keyword component. The change happened in commit `2209afd` (Nov 10, 2025) buried inside a multi-purpose refactor. The decision was deliberate — a documented architectural simplification away from hybrid scoring after the `_KNOWN_VOCAB` maintenance burden became unreliable in October 2025. The keyword infrastructure remains but is intentionally disabled. **Re-enabling W_KW = 0.2 would be a partial implementation of the NEXT roadmap hybrid retrieval and could regress eval baseline (96.8%, per ADR 018) without proper recalibration.** Captured to prevent future whack-a-mole loops.

**Workaround validated but not durable:**

Chip 3 wording "How does Matt manage resistance when leading enterprise transformation programs?" still pulls the right Norfolk Southern stories — the specific words "enterprise" + "programs" narrow the embedding neighborhood. This works for the SPECIFIC chip wording, not for general queries that don't use those words.

**Fix options — re-scored after May 16 investigation:**

| Option | Mechanism A | Mechanism B | Verdict after empirical testing |
|---|---|---|---|
| **A. Metadata-based exclusion** of `Project == "MattGPT Product Development"` for broad behavioral intent_family queries | ✓ Excluded before diversify | ✓ Excluded before Pinecone returns | **Most reliable.** Originally rejected on "no compensation logic" principle; that principle was about not papering over upstream bugs. The Story 69 contamination is not a bug — it's a fundamental property of embedding models with topically-adjacent meta-narrative. A code gate that says "MattGPT stories don't answer broad behavioral leadership questions" is product taxonomy, not compensation. Worth reconsidering. |
| **B. Router disambiguation** | ✗ Router already classifies correctly | ✗ Not a classification problem | Doesn't apply. Verified empirically. |
| **C. Corpus enrichment** | Partial; relies on LLM filtering | Partial; doesn't eliminate Pinecone signal | **Has structural ceiling.** Demonstrated across three iterations. Improves story quality but can't fully solve retrieval. LLM stochasticity introduces variance. |
| **D. Rework `diversify_results` (MATTGPT-021)** | ✓ Fixes promotion logic | ✗ Can't fix "Strangler Fig at Pinecone #1" | Helpful for Mechanism A only. Independent fix on its own merits. |
| **E. Hybrid retrieval (NEXT roadmap)** | ✓ Keyword anchoring helps | ✓ Keyword anchoring helps | **Architectural fix.** Real work. Real value. Punts the immediate problem until the roadmap item ships. |

**Open question for next session:** (A) hard exclusion gate vs (E) wait for hybrid retrieval architecture work. Pure (C) corpus enrichment is now empirically ruled out as a complete solution.

**What today produced (story-quality wins independent of retrieval outcome):**

- Story 69 (MattGPT Product Vision) body is genuinely cleaner; "I Built a Monolith by Accident" replaces the verbose "Strangler Fig Refactoring" title; NS Mainframe voice now consistent with servant-leadership arc across portfolio
- Theme change for Story 69 (Strategic & Advisory → Execution & Delivery) corrects a miscategorization
- W_KW=0.0 history excavated and documented (avoids future whack-a-mole)
- Empirical floor identified for corpus enrichment as a fix mechanism

**Logged:** May 13, 2026 / **Deep investigation:** May 16, 2026

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

- **Status:** Done — shipped May 27, 2026 in commit `aac9cf8`. Followed the canonical Red (scenarios) → Red (step defs) → Green → spec-amendment-during-Green cycle. Two locked decisions were reversed after live design review against `about_matt_wireframe.html`; the chip-containment fix was tightened to require true DOM nesting inside the CTA card.
- **Priority:** Medium
- **Type:** Action
- **Logged:** May 15, 2026

**Locked decisions (May 15, 2026) — six items, after UX assessment with multiple agents:**
  - **Sample questions clickable** — 4 questions at `about_matt.py:1199-1204` currently `<li>` plain text in a single `st.markdown` block. Convert to 4 `st.button` calls using the existing chip→Ask pattern: `seed_prompt` + `__ask_from_suggestion__` + `active_tab="Ask MattGPT"` + `st.rerun()` (see `category_cards.py:55-57` and `story_detail.py:203-218`). Define the four question strings as a module-level constant `ABOUT_MATT_SEED_QUESTIONS` for BDD/eval reuse.
  - **Remove redundant footer (lines 1205-1208)** — once questions are clickable, the "Head to Ask MattGPT in the navigation above to try it yourself" line AND the "Real AI assistant • 130+ projects • Instant answers • Available 24/7" bullets become redundant.
  - **Code block in `<details><summary>`** — RAG pipeline code at lines 1062-1091 wrapped in native HTML `<details><summary>Show code</summary>...</details>`. Collapsed by default.
  - **4x stat — drop from About Matt stats bar** — match Home hero (4 stats). **REVERSED May 27.**
  - **Merge DevOps & Quality card into CI/CD Pipeline card** — remove the bottom-row orphan in the 2-column details grid.
  - **Anchor navigation** — add `id="career"` / `id="mattgpt"` / `id="competencies"` / `id="philosophy"` to section headers and render a post-hero nav block. **REVERSED May 27.**
- **Closed per May 15 assessment:** "View Design Specification" format indicator (low ROI), explicit two-audience signposting labels (originally handled by anchor nav; now moot).

**May 27, 2026 amendments (during Green) — `about_matt_wireframe.html` review:**
  - **Anchor nav reversed.** Doesn't work reliably in Streamlit without JS hackery; no validated user need. Section header ids reverted. Post-hero nav block removed.
  - **Stats bar parity reverted.** The 5-card stats bar with `4x Delivery Acceleration` is restored on About Matt. The inconsistency with Home's 4-card bar is accepted — the 4x metric earns its keep on this page where the CIC narrative provides context. Driving factor was visual: the 4-card layout in a 5-column grid was stretching the cards in a way Matt flagged as "looks bad".
  - **Chip containment tightened.** The first Green pass rendered chip buttons as visual-only siblings below the `.cta-card` div (Streamlit's per-`st.markdown` DOM isolation prevented true nesting). Refactored to render the CTA card via `st.container(key="about_matt_cta_card")` styled via `[class*='st-key-about_matt_cta_card']` so the four `st.button` widgets render as true DOM children of the card container.
  - **"Try asking questions like:" label removed.** Chips speak for themselves per the wireframe; the label was redundant.
  - **Chip palette unified.** Buttons reuse `var(--banner-info-border)` / `var(--banner-info-text)` (same variables as the rejection-banner chip set in `utils/ui_helpers.py`) for visual consistency and automatic dark-mode handling.

**BDD scenario contract evolution:**
  - Red (scenarios) shipped 7 scenarios (`9599bf3`).
  - Red (step defs) shipped step bindings; all 7 assertion-failed against unchanged production (`81bba31`).
  - Green + amendments dropped to 5 scenarios (`aac9cf8`):
    - Deleted Scenario 1 (stats bar = 4 cards) — superseded by stats-bar rollback.
    - Deleted Scenario 5 (anchor nav + section ids) — superseded by anchor nav reversal.
    - Tightened Scenarios 2/3 chip locator to scope inside the `[class*='st-key-about_matt_cta_card']` container — enforces DOM-nested containment.
  - Final gate: **5 / 5 scenarios passing.**

**What shipped (production):**
  - 4 clickable sample-question buttons in the See It In Action card, rendering DOM-nested inside an `st.container` styled as `.cta-card`. `on_chip_click` plumbing reused from `category_cards.py`.
  - "Try asking questions like:" label removed.
  - Old redundant footer (`Head to Ask MattGPT...` / `Real AI assistant • 130+ projects...`) removed.
  - DevOps & Quality card merged into CI/CD Pipeline card.
  - 5-Stage RAG Pipeline code block wrapped in collapsed `<details>` with a "Show code" affordance (`▸` → `▾`).
  - `ABOUT_MATT_SEED_QUESTIONS` module-level constant exposed for BDD/eval reuse.
  - 5-card stats bar (`Delivery Acceleration` retained on About Matt only).

**What did NOT ship:**
  - Anchor nav block + section header ids — reversed.
  - 4x stat removed from About Matt stats bar — reversed.

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
**Nonsense rejection banner — branch-aware copy + contextual chip sets**

- **Status:** Done — shipped May 25, 2026 (rule:* divergence fix on Explore Stories completed the cross-surface parity; Ask MattGPT side shipped earlier in the cycle). Production-validated May 26, 2026: rule:* / personal / out_of_scope branches all render correct branch-aware copy on both surfaces.
- **Priority:** Medium
- **Type:** Action
- **Dependency cleared (May 19, 2026):** MATTGPT-061's dominant user-visible contamination mechanism closed via MATTGPT-073 session-state fix. -061's residual structural mechanism (subject-pronoun + noun-overlap retrieval bias) filed as MATTGPT-077. With session-state mechanism removed and the chip-prompt swap informed by -077, today's production spot-check of all four rule:* chip prompts produced clean responses. Implementation unblocked.

**Scope:** Differentiate copy and chip sets across all four reason branches in `render_no_match_banner` (`utils/ui_helpers.py:304-427`). Each rejection reason gets contextually-earned copy and chips rather than a single uniform treatment.

**Current branching today** (verified May 15, 2026):
```python
if reason == "semantic_router:personal": ...
elif reason == "semantic_router:out_of_scope": ...
else:  # rule:*, low_confidence, unknown all fall through to generic copy
    msg = "🐾 I can't help with that. I'm trained on Matt's transformation work."
```
Chip rendering today is gated ONLY on `context == "ask"` — every Ask MattGPT rejection shows the same 4 generic chips regardless of reason.

**Change — explicit 4-branch message layer + reason-aware chip rendering:**
```python
# Message layer
if reason == "semantic_router:personal":
    msg = "🐾 I'm focused on Matt's professional experience."  # unchanged
elif reason == "semantic_router:out_of_scope":
    msg = "🐾 That's outside Matt's experience."  # unchanged
elif reason.startswith("rule:"):
    msg = "🐾 Wrong trail. I'm a Plott Hound trained to track Matt's transformation work. Give me a real scent to follow."  # new
elif reason == "low_confidence":
    msg = "🐾 I picked up a scent but lost the trail. Try rephrasing your question and I'll track it down."  # new
else:
    msg = "🐾 I can't help with that. I'm trained on Matt's transformation work."  # unchanged fallback

# Rendering layer (Ask MattGPT side) — chips and subtitle suppressed for low_confidence
show_chips = context == "ask" and reason != "low_confidence"
show_subtitle = context == "ask" and reason != "low_confidence"
```

**Net behavior matrix:**

| Context | Branch | Banner copy | Subtitle/Hint | Chips |
|---|---|---|---|---|
| Ask MattGPT | `semantic_router:personal` | Unchanged | "Ask me about:" | **New personal chip set** |
| Ask MattGPT | `semantic_router:out_of_scope` | Unchanged | "Ask me about:" | **New out_of_scope chip set** |
| Ask MattGPT | `rule:*` | **"Wrong trail. I'm a Plott Hound…"** | "Ask me about:" | **New rule:* chip set** |
| Ask MattGPT | `low_confidence` | **"I picked up a scent but lost the trail. Try rephrasing…"** | **None** | **None** |
| Ask MattGPT | unknown | Unchanged generic | "Ask me about:" | Unchanged 4 generic chips (or rule:* set — decide at implementation) |
| Explore Stories | `personal` | Unchanged | Unchanged tailored hint | None |
| Explore Stories | `out_of_scope` | Unchanged | Unchanged generic hint | None |
| Explore Stories | `rule:*` | **"Wrong trail…"** | **"Try transformation work, scaling teams, payments modernization, or enterprise leadership."** | None |
| Explore Stories | `low_confidence` | (not emitted today — Explore Stories has no confidence gate) | — | — |

**Differentiation logic across chip sets:**
- **`rule:*` chips** answer *"what does Matt DO?"* — capability themes (verbs: scale, build, lead, modernize) for users who came in with nothing on-topic
- **`personal` chips** answer *"who is Matt PROFESSIONALLY?"* — character, leadership, working approach for users curious about Matt-the-person
- **`out_of_scope` chips** answer *"where does Matt WORK?"* — concrete named anchors (clients, projects) for users who asked about scope Matt doesn't cover
- **`low_confidence`** — no chips, just the rephrase prompt; the user's query was probably on-topic, they need to refine not pivot

---

## LOCKED (May 19, 2026)

### Chip sets (production-validated)

**`RULE_CHIPS`** (`rule:*` branch — capability themes):
| Label | Click-injected prompt |
|---|---|
| Scale a CIC to 150+ engineers | How did Matt scale the CIC to 150+ engineers? |
| Build teams that ship like startups | How does Matt build teams that ship like startups? |
| Modernize legacy systems | How does Matt approach legacy system modernization? |
| Modernize payments at scale | Tell me about Matt's payments modernization at scale. |

**`PERSONAL_CHIPS`** (`personal` branch — character through work):
| Label | Click-injected prompt |
|---|---|
| What kind of leader is Matt? | What kind of leader is Matt? |
| How does Matt handle pressure? | How does Matt show up when things go wrong? |
| Why does Matt do this work? | What drives Matt — why does he do this work? |
| What do former colleagues say? | How would Matt's former teammates describe him? |

**`OUT_OF_SCOPE_CHIPS`** (`out_of_scope` branch — concrete named anchors):
| Label | Click-injected prompt |
|---|---|
| Payments at JP Morgan | Tell me about Matt's payments work at JP Morgan. |
| Cloud Innovation Center | How did Matt establish and scale the Cloud Innovation Center? |
| Scaling teams 4 → 150+ | How did Matt scale engineering teams from 4 to 150+? |
| Modernizing legacy platforms | Tell me about Matt's work modernizing legacy enterprise platforms. |

### BANNER_COPY dict (keyed by reason)

```python
BANNER_COPY = {
    "rule": "🐾 Wrong trail. I'm a Plott Hound trained to track Matt's transformation work. Give me a real scent to follow.",
    "personal": "🐾 I'm focused on Matt's professional experience.",  # unchanged from current code
    "out_of_scope": "🐾 That's outside Matt's experience.",  # unchanged from current code
    "low_confidence": "🐾 I picked up a scent but lost the trail. Try rephrasing your question and I'll track it down.",
}
```

**Explicit:** `low_confidence` renders banner copy + rephrase prompt only. **NO chips.**

### Chip-prompt validation log (May 19, 2026 production runs)

**`rule:*` chip prompts (all CLEAN after the May 19 swap):**
- *"How did Matt scale the CIC to 150+ engineers?"* → CLEAN (Accenture CIC, 4x velocity, $100M repeat business, servant leadership)
- *"How does Matt build teams that ship like startups?"* → CLEAN (high-trust, psychological safety, Lean XP, near-zero attrition)
- *"How does Matt approach legacy system modernization?"* → CLEAN (Fortune 500, DDD, event storming, 12/15-Factor, CI/CD)
- *"Tell me about Matt's payments modernization at scale"* → CLEAN (JPM ACCESS, 135K+ clients, Coalition Greenwich #1)

**Earlier rejected `rule:*` prompts that didn't survive validation:**
- *"Tell me about Matt's enterprise transformation work"* — verdict **"underwhelming"** (sprawling, no specific named engagement). "Lead enterprise transformation" chip → dropped.
- *"What's Matt's signature transformation engagement?"* — verdict **"wow these are off"** (CIC scaling instead of a specific named engagement)
- *"How does Matt modernize monoliths into microservices?"* — **CONTAMINATED 3/3** with Strangler Fig (Independent Project) instead of Accenture CIC modernization. Root cause: "Matt + monolith" hits MATTGPT-077's noun-overlap trap. **Pivot:** replaced with "Modernize legacy systems" / "How does Matt approach legacy system modernization?" — verified CLEAN.

**`out_of_scope` chip prompts (all CLEAN — production-validated May 19):**
- *"Tell me about Matt's payments work at JP Morgan"* → CLEAN (ACCESS platform, 135K+ corps, 180+ countries, Coalition Greenwich #1)
- *"How did Matt establish and scale the Cloud Innovation Center?"* → CLEAN (10-person pilot → 150+, $100M repeat business, 5 US locations)
- *"How did Matt scale engineering teams from 4 to 150+?"* → CLEAN (Lean XP, "I do, we do, you do" learning model)
- *"Tell me about Matt's work modernizing legacy enterprise platforms"* → CLEAN (DDD, microservices, CI/CD — same anchor as legacy systems chip, no Strangler Fig contamination)

**`personal` chip prompts:**
- *"What kind of leader is Matt?"* → CLEAN (post-MATTGPT-073 fix: CIC scaling, servant leadership, $100M repeat, sustainable practices). The May 16 contamination that originally parked this ticket is fixed.

**Phrasing-sensitivity finding (documented as MATTGPT-077):** "Matt + monolith" pulls Strangler Fig 3/3; "you + monolith" pulls Accenture CIC 2/2 CLEAN. Same noun, different pronoun, completely different result. Severe-overlap nouns (refactoring) contaminate regardless of pronoun. This is why the rule:* chip set was rescued from "monoliths into microservices" → "legacy systems."

### Discovery findings (May 19, 2026)

Code reading before Red-B revealed the true delta is significantly smaller than the original scope assumed:

- `render_no_match_banner` (`utils/ui_helpers.py:304-427`) already has partial branch-awareness for `personal` and `out_of_scope` banner copy
- `low_confidence` reason is **already produced** in `backend_service.py:1663,1722` — not a new classification
- Chip-click plumbing **already exists** and is well-tested: `__inject_user_turn__` + `__ask_force_answer__` + `__ask_from_suggestion__` + `__clear_banner_after_answer__`. Coverage at `tests/unit/test_category_cards.py` + `tests/bdd/steps/test_home.py`
- `context="explore"` **already suppresses** chips for Explore Stories (`utils/ui_helpers.py:397`)
- The existing generic 4-chip suggestion list at `ui/ui_helpers.py:398-415` is what the locked branch-aware constants replace

**Actual delta:** ~50 lines. (1) Extract chips to module constants (`RULE_CHIPS`, `PERSONAL_CHIPS`, `OUT_OF_SCOPE_CHIPS`, `BANNER_COPY`). (2) Make chip selection branch-aware on `reason`. (3) Add `low_confidence` banner copy + chip suppression. (4) Refine `rule:*` banner copy to the Plott Hound metaphor.

### Scope decisions (May 20, 2026 — Blue triage)

Blue validation produced 5/10 passing on first run and surfaced three test failures that exposed product/scope questions, not implementation gaps. Decided:

- **Banner clearing after chip click — DEFERRED (not implemented in Blue).** The chip-click handler in `utils/ui_helpers.py:507` sets `__clear_banner_after_answer__ = True`, but **no production code anywhere reads this flag**. The locked spec assumed the banner would clear after the chip's response generated, but the flag has been dead code since the original chip handler was written. After triage, accepted the production behavior as correct conversation design: rejection banners persist in the transcript scrollback alongside user messages and responses, the same way the full conversation history is preserved. Wiring a banner-clear consumer would add complexity for zero user-visible benefit at this point. BDD scenario "Chip click clears the rejection banner" marked deferred via `@deferred` tag in the .feature file + `pytest_bdd_apply_tag` hook in `conftest.py` that auto-skips with a code reference. Scenario kept in the .feature as design intent for a future ticket if the behavior is ever wanted.

- **Sequential rejections, chip leakage from older banners — TEST BUG, not product bug.** Streamlit's conversation view shows all prior banners and their chip sets in the scrollback — that's correct behavior, the same as showing previous user messages and assistant responses. The BDD scenario "Sequential rejections swap chip sets per branch" originally asserted "no RULE_CHIPS should be visible" against the entire DOM, but the rule:* chips are still visible in the older transcript message (correctly). Fix: scoped `get_visible_chip_labels` to return chips from the LATEST `transcript_banner_<N>` only (highest N wins). All chip-visibility assertions now read latest-banner semantics, which matches the scenario intent ("after the personal pivot, the LATEST chip set should be PERSONAL_CHIPS, not RULE_CHIPS").

- **Chip-click → user-message-injection timing — TEST-SIDE FIX.** Three scenarios asserting the chip's prompt appears as the next user message were failing because the test polled too quickly after `dispatch_event("click")`, before Streamlit's rerun had populated the new message in the DOM. Fix: updated `then "that chip's prompt should appear as the next user message"` to `wait_for_function` polling until `stChatMessage` count >= 2 with a 15-second timeout. Production behavior is correct; test was racing.

### Scenarios → constants map

BDD scenarios in `tests/bdd/features/ask_mattgpt.feature` reference these constants via step definitions (no inline literals):

- `BANNER_COPY` drives scenarios **1, 3, 5, 7** (banner copy assertion per branch)
- `RULE_CHIPS` / `PERSONAL_CHIPS` / `OUT_OF_SCOPE_CHIPS` drive scenarios **1, 3, 5** (chip visibility per branch)
- `@regression` tag applied to scenarios **2, 4, 6, 8, 10** — these test pre-existing infrastructure (chip-click plumbing on 3 click scenarios, the banner-clear flag on scenario 8, context-aware chip suppression on scenario 10) rather than new MATTGPT-071 logic

### Commit trail

- **f9cc421** — Original `ask_mattgpt.feature` (10 scenarios, design contract)
- **dc2296b** — `test_ask_mattgpt.py` + pytest-bdd binding (Red-A proof: 10 scenarios discovered, all undefined-step)
- **5fd0eb0** — CLAUDE.md Testing Protocol amendment (Red-Blue-Green validation gates formalized)
- **11e3e19** — Scenario refinements: banner-copy assertions, @regression tags, BANNER_COPY mention in feature header, `regression` marker registration in pytest.ini

### Cross-links

- **MATTGPT-077** — phrasing-sensitivity findings that informed the rule:* chip swap ("Modernize legacy systems" replacing "Modernize monoliths into microservices"). Three confirmed findings (noun-overlap spectrum + subject-pronoun modifier, product self-reference recursion, concentration mechanism).
- **MATTGPT-073** — closed the dominant user-visible contamination mechanism that had blocked -071. Cross-query session-state fix in `diversify_results`.
- **MATTGPT-061** — Resolved. Original blocker for -071. Residual structural mechanism is MATTGPT-077.

---

**Implementation notes:**

- Click-handler pattern stays as-is (same-page session injection: `__inject_user_turn__` + `__ask_from_suggestion__` + `__ask_force_answer__` + `ask_input` + `__clear_banner_after_answer__`). Only labels, prompts, and per-reason chip-set selection change.
- This banner does **not** use the cross-page chip→Ask pattern at `category_cards.py:55-57` / `story_detail.py:203-218` (those navigate via `seed_prompt` + `active_tab="Ask MattGPT"`). User is already on Ask MattGPT when this fires — session injection is correct.
- Define each chip set as a module-level constant (e.g., `RULE_CHIPS`, `PERSONAL_CHIPS`, `OUT_OF_SCOPE_CHIPS`) so BDD scenarios and any future eval entries reference the same source-of-truth strings, not inline literals. Per CLAUDE.md "no hardcoded enums for data-derived values."
- Chip-set selection happens once based on reason; render loop is unchanged.

**Out of scope:**
- Adding new reason values (no inappropriate/nonsense severity split — `rule:*` branch handles all 33 categories uniformly).
- Touching `nonsense_filters.jsonl`, the semantic router, or any retrieval/classification logic. Pure rendering change.
- Migrating to the cross-page chip→Ask pattern.
- Fixing MATTGPT-061 (separate ticket, blocks resumption of this one).

**Effort:** ~50-70 lines in `utils/ui_helpers.py` + three small chip-set constants. Single file, low risk on the code side. Chip copy validation is the gating step, not the implementation.

**BDD scenarios required before implementation (per CLAUDE.md Testing Protocol):**
- Ask MattGPT — `rule:*` reason → "Wrong trail" copy + 4 rule:* chips render with correct labels.
- Ask MattGPT — `semantic_router:personal` reason → existing copy + 4 personal chips render.
- Ask MattGPT — `semantic_router:out_of_scope` reason → existing copy + 4 out_of_scope chips render.
- Ask MattGPT — `low_confidence` reason → "Picked up a scent but lost the trail" copy, no subtitle, no chips.
- Explore Stories — `rule:*` reason → "Wrong trail" copy + new hint text, no chips.
- Explore Stories — `semantic_router:personal` reason → unchanged hint (regression guard).
- Explore Stories — `semantic_router:out_of_scope` reason → unchanged hint (regression guard).
- Clicking a chip in any branch triggers the existing session-injection handler with the correct prompt text.

**Audience impact:** Each rejection reason gets a contextually-earned re-engagement palette. A user who hit `rule:*` gets capability themes; a user who hit `personal` gets character pivots; a user who hit `out_of_scope` gets concrete in-scope anchors; a user who hit `low_confidence` gets honest "rephrase" guidance instead of misleading "wrong trail" copy.

**History:**
- Original ticket framed as "no chips exist today" — wrong; chips have rendered since March 2026.
- May 15, 2026 grounding pass uncovered three independent branching layers and the actual chip-rendering logic.
- May 15 reframe dropped a proposed nonsense-vs-inappropriate severity split (overengineered for actual audience).
- May 16, 2026 expanded scope from "rule:* only" to "all four branches" after recognizing chip vocabulary should be contextual to reason, not uniform.
- May 16 parked pending MATTGPT-061 after live validation of *"What kind of leader is Matt?"* surfaced the MattGPT-story contamination pattern. Chip text is sound; underlying retrieval needs the fix first.
- May 19, 2026 unparked: MATTGPT-073 closed -061's session-state mechanism; production spot-check of chip prompts surfaced MATTGPT-077 (phrasing sensitivity); rule:* chip set rescued by swapping "monoliths into microservices" → "legacy systems"; all four locked chip sets and banner copy production-validated; BDD scenarios written + bound + refined; Red-A complete.

**Logged:** May 15, 2026 (full spec finalized May 16, 2026; chip sets + banner copy LOCKED May 19, 2026 — Red-B pending)

---

### MATTGPT-072
**`generate_public_tags.py` — case-insensitive tag dedup**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Issue:** The merge logic in `generate_public_tags.py` (lines 141-147) uses Python `set()` for dedup, which is exact-string-match only. Case variants of the same concept survive as separate tags. Across multiple enrichment cycles (with LLM casing variation across runs), duplicates accumulate.
- **Concrete example (NS Mainframe story, May 16, 2026):** the `public_tags` field carries all of: `Agile Transformation` + `agile transformation`, `CI/CD Automation` + `CI/CD automation` (and `CI/CD Pipelines` as a third variant), `Continuous Improvement` + `continuous improvement`, `Lean Engineering` + `lean engineering`, `Developer Enablement` + `developer enablement`, `Test-Driven Development` + `test-driven development`, `Culture Shift` + `cultural change` + `culture change`. 31 tags where ~16 unique concepts would suffice.
- **Impact:** Not a contamination bug (none of these tags introduce retrieval contamination on their own), but inflates the embedding's keyword surface area for the same concept, creating duplicate semantic weight. Over time, the corpus accumulates noise.
- **Fix:** Replace `all_tags = set(new_tag_list + existing_tag_list)` with case-insensitive dedup that preserves a canonical casing (e.g., first-seen wins):
  ```python
  seen = {}
  for tag in new_tag_list + existing_tag_list:
      key = tag.lower()
      if key not in seen:
          seen[key] = tag  # preserve original casing
  all_tags = sorted(seen.values(), key=lambda t: t.lower())
  ```
- **Scope:** ~5 lines in `generate_public_tags.py`. Single change. No tests beyond a unit test for the dedup helper (if extracted).
- **Cleanup propagation:** After landing the script fix, a one-time pass over `echo_star_stories_nlp.jsonl` to dedupe existing case-variant tags would clean up the corpus state. Could be a small standalone script (`tools/dedupe_case_variants.py`) that runs once, OR can be folded into the next regular `generate_public_tags.py` invocation if the dedup logic processes existing tags as well as new ones.
- **Out of scope:**
  - Changing the additive-merge contract (`set()` behavior is what's intentional — preserve all distinct tags). This ticket only addresses the case-sensitivity flaw within that contract.
  - Cleaning up the Excel master tags — those will get normalized on next enrichment pass once the script is fixed.
- **Discovered during:** MATTGPT-061 deep investigation (May 16, 2026) when reviewing the NS Mainframe story's public_tags. Matt asked: *"Is the script duplicating? I thought it was comparing and appending if missing."* Investigation confirmed the script DOES dedupe — but only on exact string match, missing case variants.
- **Logged:** May 16, 2026

---

### MATTGPT-073
**`last_primary_client` session state produces order-dependent retrieval within multi-turn sessions**

- **Status:** Resolved (May 18, 2026 — commit `cf1cb2f`)
- **Resolution:** Option E applied. The `_last_primary_client` cross-query session state was removed from `diversify_results`. Within-query diversity for slots #2+ is preserved.
- **Empirical evidence base for the removal:**
  - **Production log analysis (Apr 13 to May 18, 82 queries, 24 inferred sessions):** 85.4% of queries occur in multi-turn sessions where the mechanism could fire. 45% of consecutive query pairs in those sessions were demotion-eligible (same pinned_client across pairs). The full firing rate is bounded by additional score-gap and client-mismatch conditions but the demotion-eligible upper bound establishes high production reach.
  - **Saturday May 16 Q3 "regression" root cause confirmed.** Diagnostic reproduction May 18 showed `last_primary_client = Accenture` from a prior query triggering the line 1293 demotion on a 0.001 score gap (Why Hire Matt at 0.350 vs. MattGPT Product Vision at 0.349), promoting MattGPT Product Vision to slot #1. Fresh sessions produced clean responses. The Saturday "LLM stochasticity" attribution was wrong; this bug was the cause.
  - **Mechanism had no documented justification** beyond a one-line docstring. No ADR, no tests pinning behavior, no design doc, no commit-message-level rationale. The W_KW=0.0 archaeology pattern (digging through git for missing decision context) was repeating.
  - **Production user behavior actively contradicted the mechanism's design intent.** A six-query session captured Apr 13 (real user drilling into resistance/transformation/scaling) was exactly the case where session-state "diversification" works against user intent.
  - **Post-removal eval validation (2 runs):** Run 1: 69/70 (98.6%). Run 2: 70/70 (100%). Both runs improved on the 61/63 (96.8%) baseline per ADR 018. The single Run 1 failure (Q64) was LLM stochastic variance that cleared on rerun.
  - **Diagnostic queries post-removal (5 queries, fresh session):** Q1, Q3, Q4, Q5 all produced clean responses. Q2 contamination unchanged (separate issue under MATTGPT-061: pure-semantic polysemy on "transformation," not addressable through diversify changes).
- **Architectural decision recorded as ADR 019** (May 18, 2026).
- **Original Issue:** `diversify_results` (`backend_service.py:1276-1305`) stored `last_primary_client` in session state and used it on the next query to decide whether to demote the new pinned story. **This means the retrieval output for query N depends on queries 1...N-1 within a session.** Real users have multi-turn sessions, so a user who asks "What kind of leader is Matt?" first and then "How does Matt show up when things go wrong?" gets a different (and worse) result than a user who asks Q3 cold. The session-state behavior is almost certainly not the intended design — the mechanism was added to break cross-query client repetition, but in practice it creates order-dependent and order-sensitive responses to the same query.
- **Compounding issue — too aggressive on near-tied scores:** The line 1293 threshold (`< 0.05`) treats a 0.001 score gap (Pinecone noise) the same as a 0.04 gap (meaningfully different alternative). When the gap is essentially noise, demoting the legitimately-correct top story amplifies that noise into user-visible response variance.
- **(Original Status / Priority / Type before resolution: Open / High / Issue)**
- **Issue:** `diversify_results` (`backend_service.py:1276-1305`) stores `last_primary_client` in session state and uses it on the next query to decide whether to demote the new pinned story. **This means the retrieval output for query N depends on queries 1...N-1 within a session.** Real users have multi-turn sessions, so a user who asks "What kind of leader is Matt?" first and then "How does Matt show up when things go wrong?" gets a different (and worse) result than a user who asks Q3 cold. The session-state behavior is almost certainly not the intended design — the mechanism was added to break cross-query client repetition, but in practice it creates order-dependent and order-sensitive responses to the same query.
- **Compounding issue — too aggressive on near-tied scores:** The line 1293 threshold (`< 0.05`) treats a 0.001 score gap (Pinecone noise) the same as a 0.04 gap (meaningfully different alternative). When the gap is essentially noise, demoting the legitimately-correct top story amplifies that noise into user-visible response variance.
- **Evidence (May 18, 2026 — surfaced during MATTGPT-061 follow-up investigation):**
  - **Session context:** User runs Q1 *"What kind of leader is Matt?"*. Pinned = Why Hire Matt (Accenture). `last_primary_client = "Accenture"` gets stored.
  - **Query:** Same session, user runs Q3 *"How does Matt show up when things go wrong?"*. Pinecone returns:
    - #1: Why Hire Matt (Accenture, pc=0.350)
    - #2: MattGPT Product Vision (Independent Project, pc=0.349)
    - Score gap = **0.001**
  - **Demotion fires** (line 1293): `pinned_client == last_primary_client` (both Accenture) AND `gap < 0.05` AND `rest[0].Client != last_primary_client`. Why Hire Matt is demoted to slot #2; MattGPT Product Vision becomes the new pinned at slot #1.
  - **Response contamination:** LLM context now leads with MattGPT Product Vision. Response opens *"During Matt's sabbatical, he embarked on a personal project to build MattGPT..."* — a sabbatical-build story dominating a "how does Matt handle adversity" question.
  - **Reproduction:** runs cleanly in a FRESH session (no `last_primary_client` state). The bug is specifically intra-session and ordering-dependent.
- **Why the existing logic is too aggressive:** A 0.001 score gap is essentially Pinecone-noise — it means the two stories are functionally tied as the top answer. The current logic interprets this as "promote the alternative for diversity," but a near-tie is actually the case where the original pinned story has the strongest legitimacy claim (it consistently ranks #1 across different queries with similar topic). Demoting it amplifies retrieval noise into user-visible response variance.
- **What the existing logic gets right:** Larger gaps (e.g., 0.04) — where the alternative is a meaningfully-different story — are a more defensible case for cross-query diversity. The mechanism in shape is correct; the threshold is mis-tuned for the very-narrow-gap case.
- **Fix options:**
  - **A.** Tighten the demotion threshold (e.g., 0.02 instead of 0.05). Only demote when there's a meaningful gap, not Pinecone-noise. Risk: changes baseline behavior across other queries; needs eval validation.
  - **B.** Don't demote when the pinned story is the same `id` as the previous query's pinned (i.e., when Pinecone consistently identifies the same story as the top answer across consecutive queries, treat that as a strong signal and respect it).
  - **C.** Add a minimum gap floor: only demote when `0.01 ≤ gap < 0.05`. Below 0.01 the stories are too close to call; demoting introduces noise.
  - **D.** Per-session story-id deduplication instead of client-level: track which story `id` was pinned last, demote ONLY if the current pinned has the same `id` (genuinely the same story being repeated). Demote less, not more.
- **Recommendation:** Option B is the cleanest in shape (respect Pinecone's signal when it's consistent across queries). Option A is the smallest code change but needs eval validation. Either way, requires running the 61-query eval suite to confirm no regression on intended cross-query diversity cases.
- **Related to MATTGPT-061:** The Saturday-evening Q3 contamination that prompted the "did Q3 regress?" diagnosis was actually this bug firing, not corpus-side enrichment failure. Fixing this bug would resolve one of the apparent symptoms of -061's broader contamination pattern. Different mechanism, different fix.
- **Effort:** ~5-10 lines if Option A (threshold change); ~15-20 lines if Option B (track previous pinned id in session state). Eval validation required regardless.
- **Discovered during:** May 18, 2026 follow-up trace of Q3 "How does Matt show up when things go wrong?" using fresh session vs. carried-over session state. Fresh session produced clean response (Why Hire Matt + Norfolk Southern Quality Crisis); Saturday-evening session with prior `last_primary_client = Accenture` produced contaminated response (MattGPT Product Vision led).
- **Logged:** May 18, 2026

---

### MATTGPT-074
**Entity cluster promotion forces synthesis mode when users want depth (e.g., "How did you build the CIC?")**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** The entity cluster promotion logic in `backend_service.py:1617-1629` automatically converts a query to synthesis mode when Pinecone returns 3+ stories from the same entity. The intent is to handle broad client/division questions ("What did Matt do at RBC?") by narrating across all stories rather than focusing on one. But the same mechanism fires for questions where the user wants DEPTH on the primary story, not BREADTH across the corpus.
- **Concrete failure case (from MEMORY.md):**
  - **Query:** *"How did you build the CIC?"*
  - **Expected behavior:** depth on the primary "Building Cloud Innovation Centers" story (the founding narrative), with supporting details from the CIC scaling work
  - **Actual behavior:** entity cluster promotion fires (10 CIC stories detected), synthesis mode activates, response spans CIC scaling + Atlanta hub + capability development + cross-functional teams + culture work — a thematic survey instead of the foundational depth the question asks for
- **Code location:** `backend_service.py:1617-1629`
  ```python
  # Entity cluster promotion: if Pinecone returned 3+ stories from the
  # detected entity, the user is asking about a client/division broadly
  if entity_match and not is_synthesis:
      ef, ev = entity_match
      entity_pool_count = sum(1 for s in pool if s.get(ef) == ev)
      if entity_pool_count >= 3:
          is_synthesis = True
  ```
- **Why the heuristic is wrong:** "3+ entity stories in pool" is a property of CORPUS COMPOSITION, not USER INTENT. A user can ask a depth-question about a client with many stories AND get force-promoted to synthesis because the pool happens to be large. The mechanism is detecting an artifact (corpus density) and treating it as a signal (user intent for breadth).
- **Affected entities (per corpus audit):** Any client/division with ≥3 stories. Most likely to fire: Accenture (37 stories under Cloud Innovation Center project), JP Morgan Chase (multiple stories under ACCESS Next Generation and Asset Management), Norfolk Southern (multiple stories under Revenue and Shipment Planning), Fiserv (multiple stories under White-Label Card Portal). Any depth-question about these gets converted to synthesis.
- **Fix options (open):**
  - **A.** Raise the threshold. 3+ is too low — for Accenture's 37 stories or CIC's 10+ stories, the pool will hit 3+ on almost any broad-leaning Accenture query. Higher threshold (5? 7?) would only force synthesis on the most clearly-breadth queries.
  - **B.** Use intent_family instead of pool size. Promote to synthesis only when `intent_family == "synthesis"` (already in semantic router) or when the question is structurally a survey ("what did Matt do at X", "tell me about X's work"). Depth questions ("how did you build X", "walk me through X's design") should NOT promote.
  - **C.** Query-shape detection. Heuristic: "How did you build X" / "Walk me through X" / "Why did you choose X" suggest depth. "What did Matt do at X" / "Tell me about X" / "Show me X's work" suggest breadth. Could be regex-based or another semantic router intent.
  - **D.** Remove the promotion entirely. Trust the semantic router's intent_family classification. If `intent_family == "synthesis"`, run synthesis mode. Otherwise, run standard mode with the natural entity-anchored pool. The depth-vs-breadth decision moves entirely to the router.
- **Recommendation:** Likely **B or D** based on the same "no compensation logic on top of Pinecone" principle that's been guiding -061. The router already classifies queries; promoting based on pool composition is a layered compensation that fires in ways the router didn't intend. Eval the router's behavior on depth queries against the affected entities before deciding.
- **Eval validation required:** Sample of CIC depth queries, RBC depth queries, JPM depth queries — measure response quality (depth vs breadth) before and after any fix. The 61-query golden suite may not cover this case; add depth-specific queries if not.
- **Related:** MATTGPT-061 (broader retrieval contamination), MATTGPT-021 (diversify_results pinning bugs), MATTGPT-073 (session-state contamination, same file). Same module (`backend_service.py`); same broader theme of compensation-layer mechanisms with side effects beyond their stated intent.
- **Discovered during:** Originally observed during the January 2026 pipeline cleanup (per MEMORY.md "Known Open Issues"). Re-surfaced May 18, 2026 during MATTGPT-073 investigation when Matt asked whether the agentic multi-story-per-client design was being touched by the diversify changes. Confirmed it isn't — but the entity cluster mechanism has its own known issue worth filing as a distinct ticket.
- **Logged:** May 18, 2026

---

### MATTGPT-075
**Developer debug surfaces leak to user-facing UI**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** Dev-facing debug output is visible in the user-facing UI on the Ask MattGPT page (and possibly other pages). Two specific surfaces observed May 18, 2026 during production query replay:
  - **Sidebar debug print:** `DEBUG • Loaded 113 stories from echo_star_stories_nlp.jsonl.` rendered at the top of the page above the navbar. Looks like a developer console message in user space.
  - **Telemetry badge:** `🧪 vector=pinecone, index=matt-portfolio-v2, ns=default, has_last=True` rendered as a status badge near the conversation. Exposes implementation detail (vendor name, index name, namespace) to end users.
- **Why it matters:** This is a portfolio app targeting Director/VP-level recruiters. Dev-debug surfaces leaking into the user UI undermine the polish credibility the rest of the app projects. The badge in particular tells recruiters how the system is built rather than what it does for them.
- **Suspected cause:** Debug surfaces gated on the `DEBUG` flag in `config/debug.py`. If `DEBUG=True` is set in the local environment or accidentally in production, these render. Need to confirm: (a) are they gated at all, (b) is `DEBUG` actually True in production, or (c) are they always-on independent of the flag.
- **Out of scope (separate concerns):**
  - The "130+ stories indexed" text in the status bar is the hardcoded story count tracked in MATTGPT-019.
  - The Pinecone debug JSON panel (full retrieval debug with match preview, scores, weights) is a developer dashboard that's been useful during investigation; whether it should ship to production needs its own decision.
- **Fix shape (open):** Audit all debug surfaces on the Ask MattGPT page (and About Matt, Explore Stories, Role Match for parity). Confirm each is gated on the `DEBUG` flag. Verify `DEBUG=False` in the production Streamlit Cloud environment. If gating is missing, add it.
- **Effort:** ~30 min audit + small code changes to add `if DEBUG:` guards where missing. Low risk, high recruiter-perceived-polish payoff.
- **Discovered during:** May 18, 2026 production query replay with Streamlit running locally. Matt's reaction on seeing the debug surfaces: *"we'll need to figure out how to fix the following: [debug output]"*.
- **Logged:** May 18, 2026

---

### MATTGPT-076
**"How Agy Works" modal iframe overflows / does not resize correctly on mobile**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** On mobile viewports, the "How Agy Works" modal (`ui/components/how_agy_modal.py`) does not size its content iframes correctly. Observed May 18, 2026 in production after the latest deploy. Two failure modes visible:
  - **Modal content overflows the viewport.** Detail cards inside the modal (Filters input, Detects intent, Retrieves grounded stories, Refuses weak matches, Synthesizes response) render at desktop heights inside a mobile viewport. Bottom cards get cut off or push the page layout downward awkwardly.
  - **Status bar layout breaks at the bottom.** The status bar (`Semantic search active · Pinecone index ready · 130+ stories indexed`) is positioned at the bottom of the modal area but conflicts with the Streamlit "Manage app" floating menu, creating visual collision and partial occlusion.
- **Likely cause:** The modal renders its content via `components.html(get_how_agy_flow_html(), height=1180)` and `components.html(get_technical_details_html(), height=850)`. These fixed pixel heights are tuned for desktop. Streamlit's `components.html` iframe doesn't auto-resize to mobile content height, so:
  - Below desktop width, the iframe still claims 1180 / 850px of vertical space
  - Content inside the iframe wraps and overflows because its CSS isn't mobile-responsive within the constrained iframe width
- **Out of scope (separate concerns):**
  - The "130+ stories indexed" copy still hardcoded — tracked under MATTGPT-019.
  - The dev-debug surfaces visible in the same screenshots — tracked under MATTGPT-075.
- **Fix shape (open):**
  - **A.** Replace fixed-pixel `height=` with a mobile-aware breakpoint (e.g., compute height conditionally based on `st.session_state["_browser_screen_size"]` if available).
  - **B.** Re-author the iframe HTML to be responsive (media queries inside the `get_how_agy_flow_html()` content + a JS auto-height observer that posts the measured height to the parent).
  - **C.** Replace the iframe-based approach with native Streamlit components (st.markdown + st.container with CSS) so Streamlit's own responsive layout handles mobile. Biggest refactor; cleanest result.
- **Audience impact:** "How Agy Works" is a credibility-building modal targeting technical hiring managers and curious recruiters. Visible layout breakage on mobile undermines the polish the rest of the app projects. Mobile is a meaningful share of recruiter traffic.
- **Effort estimate:** A) ~30 min, low fidelity. B) ~2 hours, moderate fidelity. C) ~4-6 hours, highest fidelity but largest refactor.
- **Discovered during:** May 18, 2026 spot-check of production immediately after the MATTGPT-073/-061 push. Matt clicked into "How Agy Works" while in mobile mode (Chrome desktop with mobile viewport) and observed the iframe sizing issue.
- **Logged:** May 18, 2026

---

### MATTGPT-077
**Subject-pronoun + noun-overlap retrieval contamination — "Matt + X" pulls MattGPT/Strangler Fig stories when X overlaps their vocabulary**

- **Status:** Open
- **Priority:** Medium-High
- **Type:** Issue
- **Execution split (May 28, 2026 — see Value Prioritized Roadmap at top of BACKLOG.md):**
  - **Phase 1 — Query-side mitigation (NOW).** Strip "Matt" from embedded queries on technical-noun shapes; preserve "Matt" in the prompt sent to the LLM. Cheap, reversible, sufficient for moderate-overlap nouns (monolith, MVP). NOT sufficient for severe-overlap nouns (refactoring). Hours of work, not days. Maps to Fix-path option 2 below.
  - **Phase 2 — Full hybrid retrieval (NEXT).** BM25 + semantic; keyword weighting on "client", "Fortune 500", "enterprise" pushes named-client stories above MattGPT for queries containing those keywords. Handles severe-overlap nouns. **Lowest empirical risk path** given the May 16 story-side rewrite backfire (see Finding 3 caveat). Also addresses MATTGPT-061 residual. Maps to Fix-path option 3 below.
  - The detailed Fix-path ordering section below remains the canonical reference for option specifics; this annotation adds sequencing decisions made during the May 28, 2026 prioritization pass.
- **Finding 1 (noun-overlap spectrum + subject-pronoun modifier):** Free-text queries with "Matt" as the subject systematically contaminate retrieval when the noun overlaps MattGPT or Strangler Fig story vocabulary. Subject pronoun is a *modifier*, not a binary gate — moderate-overlap nouns are rescued by switching "Matt" → "you"; severe-overlap nouns are not.

  Probe results (May 19, 2026 — production, fresh sessions):

  | Query | Result | Lead anchor |
  |---|---|---|
  | *How does Matt modernize monoliths into microservices?* (3x) | Contaminated 3/3 | Strangler Fig |
  | *How does Matt approach microservices?* | Clean | Accenture CIC / DDD |
  | *How does Matt handle legacy modernization?* | Clean | Fortune 500 / DDD |
  | *How does Matt build MVPs?* | Contaminated | MattGPT product story |
  | *How does Matt do platform refactoring?* | Contaminated | Strangler Fig |
  | *How do you modernize monoliths into microservices?* (2x) | Clean 2/2 | Accenture CIC |
  | *How do you build MVPs?* | Clean | Accenture CIC / Lean Product |
  | *How do you do platform refactoring?* | **Contaminated** | Strangler Fig |

  The "you + refactoring" disconfirmation (probe 8) is decisive: subject pronoun is NOT solely sufficient to rescue retrieval. "refactoring" appears densely in Strangler Fig's title, body, and metric language (*"5,765 lines", "82% reduction", "12 atomic Git commits"*); the pronoun switch cannot outvote that concentration.
- **Finding 2 (product self-reference / recursion):** When retrieval pulls the MattGPT or Strangler Fig stories, the LLM response **names the product's own UI pages as portfolio evidence**. Example from *"How do you do platform refactoring?"*: *"Each major page, such as Explore Stories and Ask MattGPT, was pulled out into standalone modules."* This is a product-integrity failure distinct from retrieval correctness — even if the surfaced story is technically valid as a refactoring case study, a recruiter is being told *the tool they are currently using* is Matt's portfolio evidence. The chatbot recommends itself. That breaks the recruiter mental model: they are being shown the tool, not the work.
- **Finding 3 (concentration mechanism, May 19, 2026 corpus audit):** A `refactor*` vocabulary audit against the actual embedding text (`build_embedding_text` output in `build_custom_embeddings.py`, NOT just STAR fields — embedding models see a flat concatenated string, not field structure) disconfirms the initial "vocabulary scarcity" hypothesis. Four stories use `refactor*` vocabulary in the embedded text. Three measurable signals concentrate retrieval on Strangler Fig:

  | Story | Client | refactor count | Density per 1k chars | First-mention position | Total length |
  |---|---|---:|---:|---:|---:|
  | I Built a Monolith by Accident (Strangler Fig) | Independent Project | **11** | **2.137** | **3% (front-loaded)** | 5,148 |
  | Delivering Multi-Client Customization (White-Lab) | Fiserv | 4 | 1.051 | 22.6% | 3,805 |
  | Behavior & Test-Driven Development: Zero-Defect Code | Fortune 500 Clients | 4 | 0.580 | **56.8% (back-half)** | 6,898 |
  | Building Effective AI-Assisted Development Workflows | Independent Project | 1 | 0.278 | 37.0% | 3,594 |

  Strangler Fig outranks Fortune 500 BDD on three signals simultaneously: **2.75× count** (11 vs 4), **3.7× density per 1k chars** (2.137 vs 0.580), and **front-loaded first-mention** (3% of doc vs 56.8% — Strangler's "refactor" lands in the title/theme/Use Cases zone where `build_embedding_text` notes Use Cases as the "strongest retrieval signal"; Fortune 500 BDD's first mention is buried in the back half). Note Fortune 500 BDD is actually the *longer* document (6,898 vs 5,148 chars), so Strangler's win is pure concentration, not length asymmetry. Note also that `build_embedding_text` truncates list-typed STAR fields via `_to_text(..., max_items=2 or 3)`, meaning vocabulary buried beyond those positions never reaches the embedding — earlier raw-STAR-field audits will under-count instances visible to the embedding model.
- **Hypothesized mechanism:**
  - "Matt" as a query token embeds the query closer to stories where Matt-the-person is a named protagonist in the story body (MattGPT, Strangler Fig). Accenture/JPM/Capital One stories have less first/third-person "Matt" salience — they describe team and client work.
  - Noun-overlap sits on a spectrum. When the noun appears densely in the contaminating story body (e.g., "refactoring" in Strangler Fig), the semantic concentration outvotes the subject-pronoun signal entirely.
- **Affected query shape:**
  - *"How does Matt [verb] [noun]?"* where noun ∈ {monolith, MVP, refactor*} (current known set; likely larger).
  - *"How do you [verb] [noun]?"* where noun has severe overlap (refactoring confirmed; other candidates untested).
  - **Unaffected:** queries with entities ("at JP Morgan", "at the CIC"); queries with non-overlapping nouns ("microservices", "legacy modernization"); queries that don't name Matt as subject for moderate-overlap nouns.
- **Operational impact:** Free-text recruiter queries on three of Matt's most marketable verbs — *modernize*, *build (MVPs)*, *refactor* — silently surface MattGPT-self-referential responses. Failures are silent: responses read articulate and confident, but anchor on the wrong work. A senior recruiter is *more* likely to use "Matt + verb + technical noun" phrasing than a casual user, because they're cognitively framing the question around Matt-as-candidate. That's the primary user flow. The locked MATTGPT-071 chip set is curated and empirically clean; the free-text path has no protection.
- **Fix-path ordering (open):**
  1. **Story-side rewriting / re-embedding — bidirectional, with empirical caveat.** Concrete moves derived from the Finding 3 audit:
     - **(1a) Reduce Strangler Fig refactor count from 11 → 3-4** (matching named-client density) AND move first-mention out of the front-loaded title/theme/Use Cases zone. Substitute *code cleanup / monolith decomposition / modular extraction* vocabulary; reduce first/third-person "Matt did X" framing in favor of work-as-subject framing.
     - **(1b) Boost Fortune 500 BDD refactor count from 4 → 7-8** AND move first mention into Use Cases or 5PSummary so it lands in the front-loaded zone instead of the back half (currently 56.8% into the document).

     Builds on the May 16 corpus pass (which addressed organizational/stakeholder leakage but did not address noun concentration / position). **Empirical caveat:** the May 16 Story 69 (MattGPT Product Vision) rewrite raised its Q1 Pinecone score 0.341 → 0.380 (wrong direction — the rewrite intended to reduce contamination but the score got worse). Story-side rewrites of MattGPT/Strangler Fig have empirically backfired once; any future rewrite must be A/B tested against the specific failing query before acceptance.
  2. **Query-side rewriting.** Strip or normalize "Matt" out of the embedded query at retrieval time; preserve it in the prompt sent to the LLM. Cheap, reversible, sufficient for moderate-overlap nouns (monolith, MVP). **NOT sufficient** for severe-overlap nouns (refactoring) — would need to be paired with #1.
  3. **Hybrid retrieval (BM25 + semantic).** Keyword weighting on "client", "Fortune 500", "enterprise" pushes named-client stories above MattGPT for queries that contain those keywords. Largest build, but **lowest empirical risk** given the May 16 backfire — touches retrieval scoring without touching the corpus. Addresses both this and Q2 polysemy (MATTGPT-061 residual). Currently on NEXT roadmap.
- **Operational guidance for chip / eval designers:**
  - Default to "you" phrasing in chip prompts where the noun has moderate MattGPT/Strangler Fig overlap.
  - **Avoid severe-overlap nouns entirely in chip prompts** until the corpus-side fix lands. The current MATTGPT-071 rule:* chip set already does this — *"Modernize legacy systems / How does Matt approach legacy system modernization?"* replaced *"Modernize monoliths into microservices / How does Matt modernize monoliths into microservices?"* specifically because of this trap.
  - Eval queries containing "Matt + monolith/MVP/refactor" patterns may produce contaminated responses — distinguish whether the eval is testing the gate or the underlying retrieval.
- **Open questions / future probes:**
  - Is the May 16 `TECHNICAL_ONLY_ERAS` prompt-context note (in `generate_public_tags.py`) inadvertently making Independent Project era stories MORE retrieval-attractive on technical queries by sharpening their technical vocabulary cluster? Would require A/B test with the context note temporarily removed. *(Hypothesis only, untested. May 19 2026.)*
  - Does the pattern extend to other "Matt + [first-person product verb]" combinations beyond modernize/build/refactor?
  - Does the same density-asymmetry pattern (Finding 3) show up for "monolith" and "MVP" vocabulary? A parallel audit across those nouns would confirm whether the fix needs to be applied broadly or whether "refactor" is uniquely concentrated in Strangler Fig.
- **Related:**
  - **MATTGPT-061** — MattGPT portfolio story contaminating organizational leadership queries. -077 gives -061's open structural residual a reproducible mechanism and broader scope. -061's session-state fix (via -073) closed the dominant *user-visible* failure pattern; -077 documents the remaining structural retrieval-bias failure mode.
  - **MATTGPT-073** — cross-query session-state fix that closed -061's dominant visible mechanism. -077 is independent of session state (reproduces on cold sessions).
  - **MATTGPT-071** — chip set validation; the locked chip set was rescued from -077's trap during May 19 production spot-checks.
- **Discovered during:** May 19, 2026 MATTGPT-071 chip prompt validation against production. The rule:* chip prompt *"How does Matt modernize monoliths into microservices?"* produced 3/3 contaminated responses with Strangler Fig contamination. Investigation expanded to characterize the pattern across 8 probe queries.
- **Logged:** May 19, 2026

---

### MATTGPT-078
**New corpus story — "AI Enablement Before It Had a Name" (resume Option E retrieval anchor)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Why it's needed:** A new resume summary option (Option E) was created targeting Senior Director / VP **AI Enablement** and **AI Transformation** roles. When MattGPT is queried about AI enablement experience, it currently surfaces the MattGPT solo development story and the healthcare AI pilot but **misses the CloudFirst capability transformation work**, which is the strongest evidence for this role type. The CloudFirst and CIC capability stories exist in the corpus but are tagged under talent development and delivery methodology, not AI adoption or enablement. This synthesis story is needed to create a **retrieval anchor** that connects those bodies of work to AI enablement queries specifically.
- **Target query patterns** (story should surface for):
  - AI enablement
  - AI adoption
  - Organizational readiness
  - Capability transfer
  - Change management
  - AI transformation
- **Draft (May 21, 2026 — needs final polish + 5P + STAR field mapping before corpus add):**

  > **Story Title:** AI Enablement Before It Had a Name
  >
  > **Situation:** Organizations investing in emerging technology consistently underestimate the adoption problem. The technology works. The organization doesn't absorb it. Throughout my career at Accenture, this pattern repeated across clients, practices, and technology waves — from agile transformation to cloud-native development to AI. The gap between what technology could do and what organizations could actually sustain was always the harder problem.
  >
  > **Task:** I was repeatedly the person brought in to close that gap. Not to build the technology, but to build the capability around it — so that when the engagement ended, the organization could carry it forward without us.
  >
  > **Action:** Across CloudFirst and the Cloud Innovation Center, I built the infrastructure that made new ways of working stick. Designed competency frameworks and skill gap diagnostics used across 300+ professionals. Ran dojo cohorts, 1:1 coaching labs, and immersive training programs that shifted cross-functional teams from traditional IT delivery to product-centric ways of working. Embedded human-centered design, TDD, and discovery practices into client teams so deeply that clients sustained them independently after engagements ended. Piloted production AI systems in healthcare and financial services, including a generative AI chronic disease management platform with HIPAA-compliant data pipelines, building executive confidence for broader implementation. Deepened hands-on AI expertise independently, building a production RAG system using LLMs, vector databases, and eval-driven development.
  >
  > **Result:** 300+ professionals reskilled across CloudFirst NA. 150+ practitioners scaled across the CIC. AI pilots that shifted client organizations from reactive to proactive decision-making. A consistent track record of capability transfer that outlasted every engagement — clients adopted practices independently, extended engagements without prompting, and built on foundations we laid without needing us in the room.
  >
  > **Through-line:** The discipline is the same regardless of the technology wave. Identify where the capability gap is. Build the adoption methodology. Coach teams through the change. Make it stick. I have been doing AI enablement since before it had that name.
- **Engineering work to operationalize (after the STAR is finalized):**
  1. Add to `echo_star_stories.jsonl` with appropriate Title / Client / Era / Theme / Industry metadata (likely Era = "Enterprise Innovation & Transformation" or new cross-era "Capability Transformation" framing; Client likely "Multiple Clients" or "Career Narrative")
  2. Run `generate_public_tags.py` to enrich with NLP-derived tags + Use Cases + Interview Questions
  3. Run `build_custom_embeddings.py` to re-embed and upsert to Pinecone
  4. Validate retrieval against the 6 target query patterns above — confirm this story surfaces in the top-3 for each
  5. Add eval-suite entries to `tests/eval_rag_quality.py` for any of the 6 target patterns not already covered, pinning retrieval quality
- **Sibling tickets (story-writing thread):**
  - **MATTGPT-022** — Data Quality Cleanup Journey Story. Different scope (data quality narrative vs AI enablement narrative); same shape (write STAR → add to corpus → enrich → re-embed). Reviewing the two together helps keep corpus expansion thematically balanced.
- **Cross-references:**
  - **MATTGPT-077** (subject-pronoun + noun-overlap retrieval contamination) — when adding the story, audit for the same noun-overlap concerns. "AI" is a high-frequency term in the MattGPT product story; ensure the new story's "AI" vocabulary doesn't get out-competed by Independent-Project-era stories on AI-enablement queries. **Lower retrieval-overweighting risk than MATTGPT-022** because -078 is named-client work (CloudFirst / CIC), not Matt-as-builder content — the noun-overlap with MattGPT/Strangler Fig stories is narrower.
  - **MATTGPT-072** (case-insensitive tag dedup in `generate_public_tags.py`) — relevant if enrichment surfaces tag collisions.
  - **MATTGPT-079** — meta-ticket tracking known Role Match coverage gaps. -078 is one of the named sibling story-writing tickets that may close gaps surfaced by -079.
- **Out of scope for this ticket:**
  - Resume Option E content (lives separately in resume materials)
  - Re-tagging existing CloudFirst / CIC stories with AI vocabulary (separate ticket if needed; this story is the retrieval anchor, not a re-tagging pass)
- **Logged:** May 21, 2026

---

### MATTGPT-079
**Role Match coverage gaps — corpus story anchors needed (meta-ticket)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Context:** Role Match assessments surface specific skill/technology/role-archetype gaps where the corpus has no STAR story anchor. Filed as a meta-ticket to track discovery — each gap becomes a candidate for a sibling story-writing ticket (MATTGPT-022 / MATTGPT-078 style) when prioritized for writing.
- **Known gaps (May 2026)** — surfaced during the NiCE Manager Solutions Architecture JD assessment (May 19, 2026):
  - Node.js production work (no anchor)
  - SDK / library development (no anchor)
  - Specific AI/ML framework experience in enterprise client context (anchors exist via MattGPT solo project; weak in client work) — **MATTGPT-080 candidate first, story only if structured assertion insufficient**
  - Managing multiple concurrent AI projects (no anchor; large-scale single-project anchors strong)
  - Leading teams composed of AI Engineers / Software Developers / ML+LLM specialists (CIC anchors team-leadership broadly, not specifically composed of AI/ML specialists)
  - Direct conflict resolution / employee relations experience (no anchor; tangential evidence in leadership stories) — **likely (b) resume/LinkedIn fix, not corpus**
- **Decision per gap — use MATTGPT-081's corrective-actions taxonomy:** Before writing a new story for a known gap, decide whether the right fix is:
  - (a) New STAR story → file a sibling ticket (MATTGPT-022 / MATTGPT-078 style)
  - (b) Resume / LinkedIn / positioning-doc update → not a corpus issue
  - (c) MATTGPT-080 `matt_profile.json` restructure → some gaps may be better addressed by structured skill assertions with provenance, not narrative stories
  - (d) Real skill gap → corpus is honest, no story needed; ignore in this thread
- **Workflow:** When a new Role Match assessment surfaces a gap not in this list, append it to the "Known gaps" section above with the surfacing JD context. When a gap is prioritized for action, file the sibling ticket (story / profile / resume) and link it back here.
- **Cross-references:**
  - **MATTGPT-080** — `matt_profile.json` restructure; addresses gaps better fit for structured skill assertions
  - **MATTGPT-081** — Role Match engine corrective-actions output; categorizes gaps systematically going forward
  - **MATTGPT-022** — Data Quality Cleanup Journey Story (sibling story-writing ticket)
  - **MATTGPT-078** — AI Enablement Before It Had a Name (sibling story-writing ticket; addresses AI enablement gap surfaced during resume Option E work)
- **Logged:** May 21, 2026

---

### MATTGPT-080
**`matt_profile.json` — restructure into parallel evidence sources**

- **Status:** Open
- **Priority:** Medium
- **Type:** Architecture
- **Context:** `matt_profile.json` currently does three unrelated jobs: identity grounding (name, certs, education), skill enumeration (flat 70+ item list), and positioning narrative (career summary). The matcher LLM treats all of it as undifferentiated context, which is why Role Match returns "missing evidence" for skills that are real but lack STAR story anchors.
- **Work:** Split into four separate grounding sources:
  1. **Identity facts** — stable credentials, certs, education
  2. **Skill assertions with provenance** — technology / methodology / tool + which roles + recency. Skill assertions need provenance attached, not bare claims. Example: *"Kubernetes — CIC platform engineering, 2020-2024."*
  3. **STAR story corpus** — unchanged, already exists (`echo_star_stories.jsonl`)
  4. **Positioning docs** — *How I Work and Lead*, *Opportunity Filter* — currently absent from grounding entirely
- **Dependencies:** Informs **MATTGPT-079** — some "missing evidence" gaps that -079 would otherwise fix via new stories may be better addressed here instead. Decide per gap before writing stories.
- **Cross-references:**
  - **MATTGPT-079** — meta-ticket tracking Role Match coverage gaps; -080 changes the decision framework for some of those gaps
  - **MATTGPT-081** — restructured sources make corrective-action attribution more accurate
- **Logged:** May 21, 2026

---

### MATTGPT-081
**Role Match engine — corrective-actions output by asset type**

- **Status:** Open
- **Priority:** Medium
- **Type:** Enhancement
- **Context:** Current `compute_recommendation()` produces Apply / Consider / Pass against the story corpus only. A gap result doesn't tell you whether the fix is a new story, a resume update, a LinkedIn keyword, a positioning doc change, a network move, or an actual skill to acquire. These have wildly different effort profiles.
- **Work:** Add a corrective-actions layer to engine output. Per gap, attribute to one of:
  - (a) **Story corpus** — no STAR anchor exists
  - (b) **Resume** — claim missing or buried
  - (c) **LinkedIn** — keyword or bullet absent
  - (d) **Positioning docs** — *How I Work and Lead* doesn't claim it
  - (e) **Network** — no contacts at this company / role type
  - (f) **Real skill gap** — corpus is honest, acquire it

  Output surfaces with the existing recommendation, not as a separate call.
- **Cross-references:**
  - **MATTGPT-080** — restructured `matt_profile.json` sources make attribution more accurate (clearer signal for which asset type a gap belongs to)
  - **MATTGPT-079** — meta-ticket tracking known gaps; -081 is the engine that categorizes them systematically going forward
- **Logged:** May 21, 2026

---

### MATTGPT-082
**Q15 eval assertion is over-specified — checks literal client name presence rather than response correctness**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor
- **Issue:** The Q15 test in `tests/eval_rag_quality.py:285-290` checks whether the literal string `"Fiserv"` appears in the response to the query `"Matt's work at Fiserv"`. It currently fails because the LLM describes the Fiserv work in granular detail (white-label card portal, $8.5M project, 47 acceptance criteria, $45M transactions, ADA/AODA compliance, DevOps modernization with Hudson + SonarQube) but doesn't echo the literal client name.
- **Why this is an eval problem, not a product problem (May 22, 2026 production validation):** Matt tested the query against production and assessed the response as correct and useful for a recruiter — the response accurately describes the Fiserv engagement with specific metrics and project anchors. A recruiter asking *"Matt's work at Fiserv"* gets a substantively correct, detailed answer about that exact engagement. The literal-name match is a poor proxy for response quality.
- **Mischaracterization in memory:** MEMORY.md previously listed this as `"Q15 Fiserv — LLM doesn't name 'Fiserv' in response. Pre-existing, low priority."` This framing treated it as a product defect (LLM should name the client) that was just deprioritized. Wrong framing — it's a test-quality issue (eval is checking the wrong thing). The "pre-existing low priority" label was never validated as a defect; it was carried forward as a self-citation across sessions until Matt's May 22 production check surfaced the actual response quality.
- **Fix shape:** Restructure Q15 to check for **response correctness** (does the response describe the Fiserv engagement?) rather than literal client name presence. Approaches:
  - **(A) Project-anchor check** — assert response contains 2+ of these Fiserv-engagement signature phrases: `"white-label"`, `"card portal"`, `"$8.5M"`, `"47 acceptance"`, `"VisionPLUS"`, `"ADA/AODA"`. Mirrors the concept-cluster pattern used by Q2 / Q5 / Q55 for the same reason: avoid LLM stochasticity on literal-string match.
  - **(B) Loosen the `client_variants` list** — accept project anchors as variants. Less clean; conflates "name the client" with "describe the engagement."
  - **(C) Remove Q15 entirely** — if literal client-name attribution isn't a quality signal, the test serves no purpose. Less safe because we lose any regression coverage on this category.
- **Recommendation:** (A) — project-anchor concept cluster. Same pattern as Q55 and the other recently-added surgical tests. Preserves regression coverage while testing the right thing.
- **Cross-references:**
  - MEMORY.md "Eval Baseline" section updated in the same commit to remove the "pre-existing" framing on Q15 and document the validation discipline going forward.
  - Concept cluster pattern documented in MEMORY.md "Architecture Decisions (Stable)": *"Q2/Q5 use keyword clusters with min_matches instead of verbatim phrases. Reduces LLM stochasticity failures."* — applies directly here.
- **Discovered during:** May 22, 2026 eval run before push of MATTGPT-071 + -078..-081 stack. Matt reviewed the production response to "Matt's work at Fiserv" and assessed it as substantively correct, surfacing the eval-quality framing. The deeper failure — citing memory entries as "tracked issues" without verifying against BACKLOG — prompted the MEMORY.md cleanup landed in the same commit.
- **Logged:** May 22, 2026

---

### MATTGPT-083
**Spinner inconsistency — Explore Stories doesn't show thinking indicator for rejected queries (Ask MattGPT does)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** The thinking indicator (`render_thinking_indicator()`) appears for **all queries** on Ask MattGPT — rejected and successful — but only appears for **non-rejected queries** on Explore Stories. Visual inconsistency between the two surfaces.
- **Root cause:**
  - **Ask MattGPT** (`ui/pages/ask_mattgpt/conversation_view.py:198-204`): spinner rendered BEFORE the entire `send_to_backend()` call. The backend call contains all the gates (nonsense_check, semantic_router, Pinecone, LLM), so the spinner covers everything including rejections.
  - **Explore Stories** (`ui/pages/explore_stories.py:1962-2022`): spinner rendered AFTER the rejection gates. Specifically, `is_nonsense()` check and semantic_router check both fire BEFORE the spinner code at line 1999. When either rejects the query, `st.stop()` or `return` exits the script before the spinner is reached.
- **User-facing impact:** On Explore Stories, rejected queries appear to "snap" to the banner with no transition. On Ask MattGPT, the same query type shows the spinner briefly before the banner appears. Inconsistent UX across surfaces.
- **Fix shape:** Move the spinner code BEFORE the rejection gates in `explore_stories.py`. Wrap all three (nonsense_check, semantic_router, semantic_search) inside the spinner block. Subtleties to handle:
  - `st.stop()` calls in the current rejection branches skip `finally` blocks — flip those to early-return or restructure the flow so `search_container.empty()` always runs.
  - Need to ensure the spinner appears even for very-fast rejections (~10ms regex match) so the user perceives the system "thinking" before saying no.
- **BDD coverage analysis (May 23, 2026):**
  - 2 existing scenarios in `tests/bdd/features/explore_stories.feature:311-321` for personal + out_of_scope rejection — neither has step definitions. They're documented-but-pending under the MATTGPT-060 pattern.
  - **Zero scenarios** anywhere assert spinner-during-rejection behavior. Coverage gap.
  - This ticket should land with new BDD scenarios that explicitly assert spinner presence during rejection on Explore Stories, AND optionally bind the 2 existing rejection-banner scenarios that have been pending step defs.
- **Cross-references:**
  - **MATTGPT-060** — BDD coverage gap for post-navigation page state. The 2 unbound rejection-banner scenarios fit that ticket's pattern; -083 could close them as a side effect.
  - **MATTGPT-071** — the BANNER_COPY work surfaced the visual rendering on Explore Stories, which led to this observation when the rule:* divergence (also being addressed) was being verified.
- **Discovered during:** May 23, 2026 — Matt noticed during post-deploy shake-out that the spinner wasn't showing for rejected queries on Explore Stories. Compared to Ask MattGPT behavior; confirmed the inconsistency by tracing both code paths.
- **Logged:** May 23, 2026

---

### MATTGPT-084
**Ask MattGPT BDD scenarios — chip-click + low_confidence banner-render timing flakes under full-suite load**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** Two BDD scenarios in `tests/bdd/steps/test_ask_mattgpt.py` timeout intermittently when the full BDD suite runs back-to-back (~30 min) against local Streamlit:
  - **`test_clicking_a_personal_chip_injects_its_prompt`** — `AssertionError: Expected chat history to contain the original query + the chip prompt as a user message after click; found 1 message(s). assert 1 >= 2`. The chip-click → `__inject_user_turn__` → rerun → user-message-render cycle exceeds the 15s `wait_for_function` timeout in `then_chip_prompt_in_chat`.
  - **`test_low_confidence_rejection_shows_rephrase_prompt_and_no_chips`** — `playwright._impl._errors.TimeoutError: Page.wait_for_selector ".no-match-banner" Timeout 3000ms exceeded`. Gibberish query (`qzwxvnpfrk plmqcvjxk floogerblerg`) → Pinecone (~1-2s) → low_confidence gate → banner render; 3s ceiling tight when Streamlit is under load from concurrent tests.
- **Recurrence history:** First seen during MATTGPT-071 Blue iteration (May 20-22, 2026); both passed on re-run. The Blue commit message flagged: *"If recurrence rate is meaningful across future runs, file separately."* Recurred during May 23 full-suite validation — second recurrence in 4 days qualifies as meaningful.
- **Fix-path options:**
  - **(A) Bump timeouts.** `then_chip_prompt_in_chat` 15s → 30s. `wait_for_banner` `LONG_WAIT` 3000ms → 8000ms. Smallest change.
  - **(B) Change wait strategy.** Poll session_state flags (`__inject_user_turn__` consumed, `ask_last_reason` set) rather than DOM state. More robust against rendering variance but requires test-side helper to inspect Streamlit state.
  - **(C) Mark these scenarios for isolated runs** via pytest marker so they don't compete with full-suite load. Defeats the single-suite goal.
- **Recommendation:** (A) first (cheap). If timeouts continue to flake at 30s / 8s, escalate to (B).
- **Cross-references:** MATTGPT-071 Blue commits `8b96ab0` + `d3b0663` (original flake observations and commit-message flag).
- **Logged:** May 23, 2026

---

### MATTGPT-085
**`secrets.toml` `MATTGPT_PRIVATE_BYPASS_TOKEN` local-prod parity + dead `private_access_code` cleanup + doc drift**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor
- **Issue:** Four related doc/config drift problems surfaced during May 23 full-suite BDD validation:
  1. **`MATTGPT_PRIVATE_BYPASS_TOKEN` missing from local `.streamlit/secrets.toml`.** The env var was introduced in MATTGPT-012 slice 1 (commit `329a8bf`, May 5-6 2026) — but never added to the local secrets file. CI sets it; local doesn't. Result: 7 lock-glyph BDD tests in `test_role_match.py` fail locally with `Expected '🔓', got '🔒'`.
  2. **`test_role_match.py` docstring documents a decided-against workflow.** The docstring (line 63 area + line 564 area) tells the reader to run `MATTGPT_PRIVATE_BYPASS_TOKEN=test-bypass-token streamlit run app.py` — that command-line env-var prefix approach was decided against in favor of `secrets.toml` parity. Future readers / sessions would follow the rejected workflow.
  3. **Dead `private_access_code` entry in `secrets.toml`.** MATTGPT-012 slice 1 replaced this with `MATTGPT_PRIVATE_BYPASS_TOKEN` but the old entry was never removed. Confusing for future maintainers.
  4. **No `secrets.example.toml` template exists.** New developers / future sessions have no checked-in way to discover what secrets are needed without reading production code or asking.
- **Fix shape:**
  - Add `MATTGPT_PRIVATE_BYPASS_TOKEN = "test-bypass-token"` to local `.streamlit/secrets.toml` (file is gitignored — Matt to do)
  - Remove dead `private_access_code` line from local `secrets.toml` (Matt to do)
  - Update `test_role_match.py` docstring (2 locations): remove decided-against env-var prefix workflow; point at `secrets.toml` as the parity convention (this ticket)
  - Create checked-in `.streamlit/secrets.example.toml` template documenting required keys with placeholder values (this ticket)
- **Cross-references:** MATTGPT-012 (slice 1 where the new env var was introduced without the local migration); `project_jd_match.md` memory references the new var name.
- **Discovered during:** May 23, 2026 full-suite BDD validation. Surfaced when Matt questioned whether `MATTGPT_PRIVATE_BYPASS_TOKEN` was supposed to still exist — exposing both the missing-secret config AND the docstring drift. Also surfaced an inadvertent exposure of the GCP service account private key in the conversation log (separate, urgent action item: rotate the key).
- **Logged:** May 23, 2026

---

### MATTGPT-086
**Query logger — add environment annotation column + filter dev/test traffic out of production analytics**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** The Google Sheets query log mixes traffic from all environments — production (real users at `askmattgpt.streamlit.app`), local dev (Matt's testing), BDD test runs (Playwright submitting queries against local Streamlit) — with no column distinguishing the source. Conversion / bounce / usage analytics on the log can't separate signal from noise.
- **Existing precedent:** Bot filter already removes UptimeRobot, HeadlessChrome, and Chrome/103 probes via `MONITORING_BOT_SIGNATURES` in `config/constants.py`. This is the same shape of concern — local dev + test traffic should be filtered or annotated for production analytics integrity.
- **Fix-path options:**
  - **(A) Add `env` column to query_logger schema.** Detect environment via Streamlit Cloud env var (e.g., `STREAMLIT_ENV`) OR via request hostname (`askmattgpt.streamlit.app` vs `localhost:8501`). Write `prod` / `local` / `ci` per row. Analytics filter on the column. Schema becomes 33 columns.
  - **(B) Skip logging when env is not prod.** No new column; local + test runs simply don't write to the Sheet. Loses local-debug observability but cleanest for production analytics.
  - **(C) Use a separate Sheet for non-prod traffic.** Add env-aware Sheet selection in query_logger. Cleanest separation but doubles maintenance overhead.
- **Recommendation:** (A) — preserves all data, adds discriminator that analytics can filter on. (B) is acceptable if local-debug Sheets observability has low value.
- **Stop-gap until prioritized:** Manually delete test/dev rows from the Sheet during analytics work.
- **What counts as "junk":** TBD during ticket work. Likely includes BDD test queries (e.g., "Tell me a joke about Matt's career" submitted by Playwright during pytest runs), local dev exploration queries during feature work, manual test queries.
- **Discovered during:** May 23, 2026 — Matt verified GCP service account key rotation worked locally by triggering a real query and confirming the row appeared in the Sheet. Observed the broader Sheets log filling up with local + test traffic indistinguishable from production user traffic.
- **Logged:** May 23, 2026

---

### MATTGPT-087
**Home hero — recruiter-routing CTA to Role Match**

- **Status:** Open
- **Priority:** High
- **Type:** Action
- **Issue:** Home page hero currently routes all visitors to "Ask Agy" as the primary CTA, with Explore Stories as secondary. Recruiter persona testing (May 27, 2026) showed that recruiters triaging at 90 seconds per profile completely missed Role Match — even though Role Match would have done ~70 sec of the 90-sec job for them. Role Match is buried as the fourth nav item with no visual weight, despite being the surface that actually serves the recruiter's placement-decision job.
- **Audience impact:** Direct conversion loss. Recruiters bounce or revert to LinkedIn-only sourcing because they never encounter the tool built specifically for their workflow.
- **Evidence:** Recruiter persona, verbatim: *"The biggest finding from the session isn't about Agy or Role Match individually. It's that the site has a routing problem. A recruiter lands on the homepage and the most prominent CTA is 'Ask Agy' — which is the wrong first surface for the recruiter job. Role Match is buried as the fourth nav item with no visual weight, and it's the surface that actually serves the placement decision."*
- **Fix (CTA structure locked from May 29, 2026 wireframe):** Hero carries two CTAs — **Role Match as the primary CTA**, label *"Recruiting for a role? Match it →"* (verb-led, names the recruiter's job, routes to Role Match), and **Ask Agy as the secondary CTA** (*"Want to dig deeper? Ask Agy"*). **No Explore Stories CTA in the hero** — Explore is reached via the top nav ("My Work"). The label *"Recruiting for a role? Match it →"* is locked from the wireframe (not a proposal).
- **Supersedes:** the May 28, 2026 "tertiary CTA, weight below the primary Ask Agy" framing is retired. The May 29 wireframe inverts it — recruiter routing is the **primary** CTA, not a tertiary one, and there is no Explore Stories CTA in the hero.
- **Effort:** ~1 hour. Single change in `ui/components/hero.py` CTA section.
- **Cross-references:**
  - MATTGPT-066 — Role Match cold-start affordance (complements: addresses what happens once on Role Match without a JD; -087 addresses how recruiter gets there in the first place)
  - Closes the gap left open by the May 15, 2026 "Hero CTA weight rebalance" assessment (which only considered Ask Agy vs Explore, not Role Match)
- **Logged:** May 28, 2026

---

### MATTGPT-088
**Role Match scorer — align with Agy honesty (no Strong Match when chat would say no)**

- **Status:** Open
- **Priority:** High
- **Type:** Issue
- **Scope clarification (May 29, 2026):** This ticket is specifically about **cross-surface consistency on the same factual question** (Role Match scorer vs Agy chat answer), not about general scoring strictness or model granularity. Two adjacent concerns that get conflated and should NOT be folded in here: (a) "scoring inflates one tier" critiques (binary Strong/Partial/Gap can't carry "Strong-with-nuance" distinctions like Director-vs-VP tenure) — that's a model-granularity concern, separate work; (b) verdict-line / overall-fit summaries — separate UX decision, see MATTGPT-089 area work. -088's audit produces downgraded Notes that plug into the existing Partial-with-Note rendering pattern; no UI changes required for -088 itself.
- **Issue:** Role Match scorer over-claims relative to what Agy honestly returns in chat. Specific evidence: Role Match marks *"experience running an in-house engineering organization of 60+ as a direct accountable leader"* as **Strong Match**, while Agy correctly responds that Matt has **not** directly managed an in-house product engineering organization. Same factual question, two surfaces, contradictory answers. The Role Match scorer is the inconsistent one.
- **Audience impact:** CTO persona (May 27, 2026 test) called this the single biggest credibility hit on the entire site. Quote: *"That inconsistency in his own AI is the kind of thing I'd raise on the call, because if he doesn't see it, that's a signal."* Translated to interview prep: *"Which one is right, and what does the inconsistency tell me about how you'd present your team's work?"* — a defensive answer to that question kills the candidacy.
- **Counterintuitive insight:** Tightening the scorer to be MORE honest INCREASES credibility, not less. Quote from CTO: *"The 7-out-of-10 partials with specific gap notes are what made the whole artifact credible. A victory-lap scorer would have killed it."*
- **Fix:** Audit the Role Match scoring logic that maps qualifications to Strong / Partial / Gap. For each Strong Match output, validate against what Agy would return in chat for the equivalent question. Where the scorer is more generous than Agy, downgrade to Partial with the honest reframing as the "Note." Consider routing the scorer's qualification analysis through the same LLM context that drives Agy's chat answers, so the two surfaces share a single source of truth on what the corpus supports.
- **Effort:** Medium. Requires understanding the existing Role Match scoring path + an audit pass against Agy's actual chat responses for the same JD requirements.
- **Cross-references:**
  - MATTGPT-077 — Subject-pronoun + noun-overlap retrieval contamination (upstream — better story differentiation in retrieval makes scorer evaluation easier; -077 fixes which stories get pulled, -088 fixes how the scorer reports on them)
  - MATTGPT-015 — JPM Payments IQ Differentiation (upstream: better-differentiated stories give the scorer more reliable signal)
  - MATTGPT-079 — Role Match coverage gaps meta-ticket (related but distinct: -079 tracks coverage gaps where no story exists; -088 is about scorer calibration on existing claims)
- **Logged:** May 28, 2026

---

### MATTGPT-089
**Role Match — parse location, work-model, availability as distinct filter class**

- **Status:** Open
- **Priority:** High
- **Type:** Issue
- **Issue:** Role Match's JD parser drops location, work-model, and availability requirements silently. Recruiter persona pasted a JD with *"Hybrid in NYC, SF, or Atlanta (3 days/week onsite)"* — Role Match parsed 11 qualifications and dropped that one entirely. Other JD requirements all came through clean. The tool answers *"can he do the job"* but not *"can we hire him"* — which means a hiring manager doing first-pass filtering gets an incomplete picture.
- **Audience impact:** Recruiter persona: *"It is strong at experience matching, blind to logistical filters (location, comp, availability, work model). Those are exactly the filters that get a candidate moved or killed at first pass."* Atlanta-based + "Open to Atlanta and beyond" in the footer would have been a perfect location-match flag if the parser had caught it.
- **Fix:** Extend Role Match JD parser to recognize a distinct filter class for logistical requirements:
  - Location / geographic constraints
  - Work model (remote / hybrid / on-site)
  - Availability / notice period
  - Visa / work authorization
  - (Skip comp — see MATTGPT-090 for separate handling)

  Match these against Matt's profile data (Atlanta + relocation openness from `data/matt_profile.json` or footer copy). Output as a separate section in the Role Match results panel so the hiring manager sees both *"can he do the job"* AND *"can we hire him"* without scrolling.
- **Effort:** Medium. Parser extension + result panel layout addition + profile data plumbing.
- **Cross-references:**
  - MATTGPT-067 — Role Match result panel polish bundle (could fold this in or land as sibling)
  - MATTGPT-079 — coverage gaps meta (location/work-model are profile data, not story-anchored — different fix path)
  - MATTGPT-090 — chatbot-side of the same logistical-data gap (comp specifically declined cleanly there; location/work-model surfaced as match output here)
- **Logged:** May 28, 2026

---

### MATTGPT-090
**System prompt — decline cleanly on comp / off-scope queries (no silent fallback)**

- **Status:** Decided Against (May 29, 2026)
- **Priority:** Medium
- **Type:** Action
- **Decided Against (May 29, 2026):** Production behavior already handles this cleanly. The `personal` intent family in `services/semantic_router.py:192-209` includes salary canonical phrases (*"What's Matt's salary"*, *"How much does Matt make"*) alongside age/identity/etc., and produces the warm-decline pivot (*"🐾 I'm focused on Matt's professional experience"*). Production-verified May 29, 2026 during wireframe review — the silent-fallback failure mode described in the original Issue does not reproduce. The ticket's premise that comp needs a *different* decline copy than age/identity (because comp IS legitimately answered elsewhere) is theoretically defensible but didn't survive the production check — the existing warm pivot is sufficient. **The remaining asymmetry** splits into two tickets: MATTGPT-089 (parse location / work-model / availability as a distinct filter class — explicitly excludes comp) and **MATTGPT-099** (assess and decide Role Match's comp handling on JDs that include comp expectations — different fix path because comp can't be matched against profile data, only declined). The earlier framing that pointed all of the asymmetry at -089 was wrong; -089's body explicitly says *"Skip comp — see MATTGPT-090 for separate handling,"* so a separate ticket was needed once -090 itself was closed.
- **Issue (original framing — superseded):** When Agy is asked something Matt shouldn't answer publicly (e.g., comp expectation), it currently produces a soft non-answer rather than a clean decline. Recruiter persona example: asked target role + comp + geo, got 4 paragraphs of narrative — comp went **silent**, relocation got a *"the story does not provide specific details… however, his focus on the right org fit suggests he might consider relocation"* (a dressed-up guess). The silent failure mode is worse than an honest decline because the recruiter can't tell whether the data is missing or being withheld.
- **Audience impact:** Recruiter persona, verbatim: *"For a recruiter this is the single biggest miss. I cannot pitch Matt to a hiring manager without a comp anchor; I'll burn a screening call to get it... The bot's failure mode there is the real finding: it should decline cleanly ('Matt handles comp conversations directly — reach out') instead of going silent and letting the recruiter guess whether the data is missing or being withheld."*
- **Fix:** System prompt addition (`prompts.py` or wherever Agy's primary system instruction lives) covering:
  - **Comp:** Decline with a clear redirect to direct conversation. Suggested: *"Matt handles compensation conversations directly. Reach out at [contact link]."*
  - **Other off-scope but answerable-elsewhere queries:** Decline with redirect (relocation specifics, references, etc.).

  This is distinct from the existing `personal` intent family handling — those are queries that shouldn't be answered at all (age, religion, etc.). The comp/logistics class IS legitimately answered, just not on the site. Different decline copy required.
- **Effort:** Small. One-line system prompt addition + 1-2 BDD scenarios to validate the decline shape vs the silent fallback.
- **Cross-references:**
  - Existing `personal` intent family in semantic router (different fix path, similar shape)
  - MATTGPT-089 — location/work-model parsing on Role Match side; this is the chatbot side of the same logistical-data gap
- **Logged:** May 28, 2026

---

### MATTGPT-091
**Failure stories — audit existing corpus content first, then write only if needed (re-scoped May 28, 2026)**

- **Status:** Open (re-scoped May 28, 2026 — see Reconciliation note below)
- **Priority:** Medium
- **Type:** Investigation + conditional Action
- **Reconciliation (May 28, 2026):** Original framing assumed failure stories needed to be written from scratch. Matt's review of persona findings flagged that some failure content may already exist in the corpus but not surface on failure-shaped queries — which would make this primarily a retrieval / surfacing problem (MATTGPT-094 family) rather than a write-from-scratch problem. Ticket scope re-structured into phased work: audit existing content first, then either close-and-redirect to -094 OR proceed to write-task. Original write-task content preserved as Phase 3 fallback below.
- **Issue (original framing):** None of the 113 STAR stories obviously surfaces a failure, a hire that didn't work, an architecture call that was wrong, a program that got killed, or a leadership decision in hindsight when queried directly. Every arc on Agy reads positive. The only nod to failure is "early failure and experimentation approach" as a suggested chat prompt — neutered language for what should be a leadership lesson with specifics.
- **Audience impact:** CTO persona flagged this as a structural leadership blind-spot signal: *"Senior leaders who don't talk about who they fought with, what they killed, or who didn't make it on their team are often leaders who avoid the hard conversation. In a VP Eng seat that translates to tolerating mediocre senior reports too long, postponing performance conversations, and protecting reputations over the team's pace."* VP-of-People persona (forwarded scenario, also from CTO transcript) picked up the same signal independently as a hiring concern.
- **Phased scope (May 28, 2026 re-scope):**
  - **Phase 1 — Audit existing corpus** for stories tagged with or containing failure / hard-decision / lesson-learned / hire-that-didn't-work / killed-program content. Catalog what's there with a short note on craft strength.
  - **Phase 2 — Diagnose via probe queries** on failure-shaped topics:
    - *"Tell me about a time Matt's approach didn't work"*
    - *"Has Matt had to remove a senior hire?"*
    - *"Tell me about a program Matt killed"*
    - *"What's a leadership decision Matt would make differently in hindsight?"*

    Compare retrieved content to Phase 1 catalog. Two outcomes:
    - **Surfacing problem** (existing failure content exists AND passes craft bar AND doesn't surface): close -091, re-file as a sub-investigation under MATTGPT-094 (retrieval / surfacing family).
    - **Content problem** (failure content doesn't exist, OR exists but doesn't pass craft bar): proceed to Phase 3.
  - **Phase 3 — Write (original scope, conditional on Phase 2 outcome):** Write one (or more) STAR story documenting a real failure or hard call:
    - The hire that didn't work and what was missed in the first 90 days
    - The architecture call that was wrong and how the team unwound it
    - A program or initiative that was killed and why
    - A performance conversation that should have happened sooner

    Has to be self-aware without being self-deprecating. Has to name what would be done differently. Same craft bar as the existing strongest stories. Goal: one story is enough — proof that Matt CAN write the failure mode honestly, which neutralizes the structural blind-spot read.
- **Effort:** Phase 1 audit + Phase 2 probe: ~1-2 hours. Phase 3 write (if needed): ~3-5 hours per story.
- **Cross-references:**
  - MATTGPT-022, MATTGPT-078 — sibling story-writing tickets (Phase 3 pattern if write-task scope returns)
  - MATTGPT-079 — Role Match coverage gaps meta (track this story addition as it closes the "failure narrative" gap, whether by surfacing or by write)
  - **MATTGPT-094** (added May 28, 2026) — retrieval / surfacing family; if Phase 2 reveals existing failure content doesn't surface, the fix belongs there
- **Logged:** May 28, 2026 (original); re-scoped May 28, 2026 (post-persona-review reconciliation)

---

### MATTGPT-092
**Hero — explicit seniority signal (supersedes May 15 design-call closure)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Hero copy *"Hi, I'm Matt Pugmire / Interview me before you interview me / I build products, platforms, and teams"* does not anchor Matt at a specific leadership level. A recruiter triaging in 5 seconds cannot tell whether he's an IC architect, a Director, a VP, or an SVP. The supporting headline on LinkedIn (*"Engineering Leader | Builds Engineering Organizations from Zero | Enterprise Platform Modernization | AI"*) has the same problem — 4 buzzwords stacked with no level anchor.
- **Audience impact:** Recruiter persona, verbatim: *"4 buzzwords stacked, no anchor... 'Engineering Leader' could be Director, VP, SVP, CTO. 'From Zero' reads consultancy/services, not in-house product engineering. 'Enterprise Platform Modernization' reads consulting again. 'AI' reads bolted on. I cannot place him on a level in 5 seconds."*
- **Why this reopens a closed decision:** May 15, 2026 UX assessment closed "explicit seniority signal at hero" as a design call: *"recruiters arriving from LinkedIn have context, stats bar reinforces 20+ years."* That assumption was contradicted by direct evidence from a recruiter persona triage. The closure was made without persona testing data; this ticket reopens with that data.
- **Fix shape (principle locked May 29, 2026 — scope/outcome anchor, NOT a title chip):** Add a scope/outcome anchor in the hero. Do **not** add a level chip or concrete title claim. The recruiter "can't place in 5 seconds" finding is solved by narrowing the range through scope (org built, tenure, function), not by declaring Director-vs-VP — Matt's actual target taxonomy is broader (VP / Head of Engineering / Director of Platform Engineering / Field CTO / AI Enablement Lead / Internal AI or Cloud Innovation Center leadership), and naming two titles forecloses the rest.
  - **Prose-block copy (locked):** *"In active search for a role where building the engineering organization, establishing the culture, and delivering results are part of the same job."* The load-bearing clause *"are part of the same job"* is the positioning claim — it signals builder-operator (vs strategy-only) without naming a level. Replaces the earlier wireframe placeholder *"currently in active search for VP and Head of Engineering roles"* which had the title trap.
  - **Stats "Level" tile (apply same principle, not locked copy):** No concrete title chips like *"Director · VP target"*. Options that satisfy the principle: *"Senior leader"* (function), *"20+ years"* (tenure), *"0→150 scope"* (outcome). Pick one; all three solve the recruiter finding without the title trap.
  - **Subtitle:** *"Senior engineering leader"* (already in wireframe) is fine — it's one notch sharper than the LinkedIn *"Engineering Leader"* the recruiter persona flagged as too vague, but still range-friendly.
  - **Earlier "three options" framing retired:** Original ticket body listed sub-headline / tagline-beneath-name / level-chip-near-avatar as design options. The level-chip option is now explicitly out. The principle (scope/outcome anchor) supersedes the option list.
- **Effort:** Small (~1 hour for any of the above options).
- **Cross-references:**
  - May 15, 2026 closure inside MATTGPT-068 detail block — this ticket supersedes that closure
  - MATTGPT-087 — hero CTA work (related surface area; both touch the hero)
- **Logged:** May 28, 2026

---

### MATTGPT-093
**About Matt — strategic restructure (split / fold / reframe meta-question)**

- **Status:** Open — strategic question, not a polish ticket
- **Priority:** Medium (not Urgent — MATTGPT-068 polish + dim fix shipped May 28; this is the longer-arc question that follows)
- **Type:** Action / Enhancement
- **Issue:** About Matt is competing with itself. The page tries to be both (a) deep narrative for the engaged reader who wants the full 3,000-word story, and (b) a conversion surface for the skeptic / decision-maker who needs proof-of-value in 5 seconds. Those audiences are at opposite ends of the funnel and the current single-page structure compromises both.
- **Evidence:** Two persona transcripts (May 27, 2026):
  - CTO persona: *"I came close to closing the tab in the first three seconds"* (hero friction); *"You've spent 90 minutes refining four button labels on a page that the wrong audience reads."*
  - Recruiter persona: *"The site is built around exploration, not extraction"* — the page actively works against the 90-second scan job.
- **Strategic options (not yet decided):**
  1. **Split** — Two surfaces: "Quick interview" (skeptic / time-constrained entry; opens with a worked Agy example interaction) + "Full story" (engaged-reader deep narrative). Each surface optimizes for its audience without compromise.
  2. **Fold** — Kill the About Matt page entirely. Push the bio into Home as a progressive-disclosure block. Let Ask MattGPT carry the narrative load through interactive exploration rather than static read.
  3. **Reframe in place** — Keep the page but move the conversion moment (sample questions, worked Agy example) above the narrative, demoting the long-form to "for those who want more."
- **Why this is a meta-ticket, not an implementation ticket:** Each option above is a multi-week project with separate UX, content, and routing implications. This ticket captures the strategic question for prioritization; the implementation ticket gets filed once a direction is chosen.
- **Related findings worth surfacing during the strategic decision:**
  - "Interview Matt before you interview him" is the strongest framing on the site and lives only on the Home hero — the About Matt reframe should reinforce it, not duplicate or contradict
  - The site's medium-is-the-message asset (MattGPT itself demonstrating Matt's AI competence) is currently underused on About Matt
  - The pre-rendered Agy example interaction discussed in earlier strategic notes is a candidate for the "Quick interview" surface in Option 1
  - **TL;DR + export-button pattern** (leveraging existing `action_buttons.py` infrastructure on Story Detail / Role Match): candidate implementation path under Options 1 and 2. The strategic direction decision shapes whether the export lives on a new About Matt one-pager (Option 1's "Quick interview" surface) or as a standalone `/recruiter` route. Originally discussed as a separate "MATTGPT-094" candidate during May 28, 2026 persona-finding review; folded here for traceability. Same canonical content serves three audiences (warm decision-maker quick orientation, referrer enablement for warm intros, recruiter triage), with primary value in the first two — the third is Matt's strategic circumvention target via networking.
- **Effort:** Strategic decision: 1-2 hours of conversation + alignment. Implementation: depends on option chosen (small for Reframe in place; large for Split or Fold).
- **Cross-references:**
  - MATTGPT-068 — closed May 28, 2026 (the polish + dim fix; this ticket is the longer-arc question)
  - MATTGPT-077 — MattGPT self-referential responses (related: content-side of the same medium-is-the-message asset)
- **Logged:** May 28, 2026

---

### MATTGPT-094
**Retrieval concentration audit — CIC over-weighting + operational story under-surfacing (hypotheses to verify)**

- **Status:** Open — hypotheses to verify before committing to a fix
- **Priority:** High
- **Type:** Investigation
- **Issue:** Two related retrieval-bias hypotheses surfaced during May 28, 2026 review of persona-test results plus Matt's own corpus insight. Both point at retrieval concentration / surfacing failures rather than corpus content quality.

  **Sub-hypothesis A — CIC over-concentration on broad queries.** The CIC flagship story ("Building Cloud Innovation Centers (CIC)") may over-dominate retrieval results for broad-experience queries (target role, leadership work, transformation work) at the expense of other real client work (JPM, RBC, Fiserv, Capital One, AT&T). Evidence from persona transcripts: the recruiter's landing-view answer was CIC-dominated; the "has Matt managed in-house eng" answer led with CIC (0→150, 4X, $100M); the career-intent answer again centered CIC. Concrete testable mechanism: the CIC flagship had a prior embedding dilution fix that boosted retrieval; the boost may have over-corrected past correct into over-concentration.

  **Sub-hypothesis B — operational stories exist but don't surface.** Matt has JPM stories with big enterprise releases, Sev-1 defects, global rollouts, up-to-5am on-call work that EXIST in the corpus but don't surface on operational queries. The fix isn't writing new content (that's MATTGPT-091's adjacent question); it's making sure the operational substance that's already there gets retrieved when operational queries arrive.
- **Why these are framed as hypotheses to verify (not confirmed bugs):** Same discipline as MATTGPT-077. Multiple anecdotal data points across persona transcripts AND owner-knowledge suggest the pattern is real, but probe queries are needed to confirm the mechanism before designing a fix.
- **Audience impact:** If sub-A is confirmed, decision-makers querying broadly read Matt as "one-big-thing leader" (CIC) rather than "18-year-range portfolio across financial services, telecom, and technology waves." If sub-B is confirmed, recruiters/CTOs querying operationally don't see the Sev-1 / on-call / enterprise-release substance that addresses their "can he run incidents?" question. Both are credibility-reducing in different ways.
- **Important context from existing backlog:** Line 1622 in BACKLOG.md (-078 detail) framed CIC as having **lower retrieval-overweighting risk** because it's named-client work. This ticket is a deliberate re-examination of that framing in light of persona evidence — not a contradiction, a check on whether that framing still holds at the queries we now know matter.
- **Investigation plan (probe-test methodology, same shape as MATTGPT-077):**
  - **Probe set A (CIC concentration):**
    - *"What's Matt's experience?"*
    - *"Tell me about Matt's leadership work"*
    - *"Tell me about Matt's transformation work"*
    - *"What banks has Matt worked with?"* (CIC should NOT dominate; JPM/RBC/Capital One/Fiserv should)
    - *"Tell me about Matt's experience at JP Morgan"* (should pull JPM stories, NOT CIC)
  - **Probe set B (operational under-surfacing):**
    - *"Tell me about a Sev-1 Matt handled"*
    - *"Has Matt run on-call rotations?"*
    - *"Tell me about Matt's experience with global enterprise releases"*
    - *"What's Matt's operational background?"*
  - For each probe: check top-3 retrieval results + assess whether CIC dominates (A) or operational stories surface (B).
  - Document findings as a probe results table (same format as -077's findings table).
- **Fix path (conditional on investigation results):**
  - If sub-A confirmed: retune CIC story's embedding weight / retrieval boost; may need treatment similar to -077's chip-prompt swap pattern at the chip level
  - If sub-B confirmed: investigate whether operational JPM stories have weak vocabulary anchors that don't match operational query terms, OR retrieval scoring prioritizes other content
  - If neither confirmed: close as "verified, not a problem"
  - If sub-A and sub-B point at same root cause (e.g., retrieval scoring heuristics favor named-client + scale metrics over operational-detail content): single fix may address both
- **Effort:** Investigation 2-3 hours (probe runs + analysis). Fix effort depends on findings.
- **Cross-references:**
  - MATTGPT-077 — same retrieval-bias family (different stories, different sub-mechanism); methodology pattern for this investigation
  - MATTGPT-061 — story-selection variance in same retrieval cluster
  - MATTGPT-021, MATTGPT-022 — earlier retrieval-bias work
  - MATTGPT-079 — Role Match coverage gaps meta-ticket (sub-B's "operational stories don't surface" overlaps with -079's gap-tracking concept)
  - MATTGPT-091 — adjacent question (whether failure stories are a write problem or surfacing problem); if Phase 2 of -091 reveals existing failure content doesn't surface, the fix moves here
- **Logged:** May 28, 2026

---

### MATTGPT-095
**Anti-consulting bias in story framing — corpus reads "consulting" as default register when it shouldn't**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** 20 years at a consultancy means consultants worked for Matt; engineering organizations Matt led; Fortune 500 clients chose Matt's teams over alternatives. That's not a negative position. But the current corpus framing across multiple stories lets the consulting context read as the default register — emphasis on engagements, methodologies, client relationships, advisory work — when the underlying substance (people Matt hired, technology Matt shipped, organizations Matt built) is often closer to in-house engineering leadership than the framing suggests.
- **Preserve-consulting-reality guardrail:** This is NOT a ticket to erase consulting context, hide that Matt's career is consulting-heavy, or rewrite stories to falsely present as in-house work. Consulting IS Matt's career; the work IS real; the clients ARE the engagements. The fix is FRAMING within that reality — surface the engineering substance (org built, code shipped, incidents owned, people hired) as the primary signal, with the consulting context as the deployment vehicle, not vice versa. Anything that pretends the consulting context didn't exist would be misrepresentation and is explicitly out of scope.
- **Audience impact:** CTO persona's specific concern about *"20 years at Accenture means frameworks, programs, and operating-model thinking are his defaults"* reads partly from the corpus framing. Recruiter persona's observation that *"every project is consulting"* is a fair read of the surface, but understates the leadership/engineering depth underneath. Decision-makers screening for VP Eng / SVP Eng roles need to see the engineering-leader substance; the current corpus framing makes them work too hard to extract it.
- **Distinct from existing tickets:**
  - MATTGPT-043 (Decided Against — Humane Framing intent-to-tone mapping) is about response-tone shaping at LLM-output time. -095 is about how the underlying corpus stories are FRAMED. Different layer.
  - MATTGPT-077 is about retrieval contamination (wrong stories surface). -095 is about how the CORRECTLY-retrieved stories read.
  - MATTGPT-097 (career-intent framing refresh) is about ONE specific story class. -095 is the systemic question across the corpus.
- **Fix shape:** Audit corpus stories for places where the leadership/engineering substance is positioned as supporting evidence FOR a consulting narrative rather than the primary substance with consulting as context. Rewrite framing — not facts — to surface the engineering/leadership substance first. Examples (illustrative, not exhaustive):
  - *"Led Accenture's CIC delivering for Fortune 500 clients"* → emphasizes consulting deployment
  - vs. *"Built and led an engineering organization that scaled to 150+ engineers, $100M+ practice revenue; deployed at Fortune 500 clients"* → emphasizes engineering substance with consulting as context

  Both are true; the second positions Matt where his actual decision-making time was spent.
- **Effort:** Medium-craft writing work. ~4-6 hours of corpus audit + targeted reframing. Affects multiple stories. Should NOT be a one-pass rewrite; iterative against persona-test follow-ups to confirm the reframing actually shifts how Agy responds.
- **Cross-references:**
  - MATTGPT-077 — distinct (retrieval bias vs framing bias) but sibling concerns
  - MATTGPT-091 — adjacent (failure story addition can model "engineering substance first" framing)
  - MATTGPT-097 — narrower scope (career-intent stories specifically); -095 is the broader corpus question
- **Logged:** May 28, 2026

---

### MATTGPT-096
**Methodology context dropped during synthesis — TDD/BDD and ways-of-working substance gets compressed out of metric claims (hypothesis to verify)**

- **Status:** Open — hypothesis to verify before fix
- **Priority:** Medium
- **Type:** Issue
- **Issue:** Top-line corpus metrics (*"4x faster delivery," "zero production defects across 150 engineers," "82% reduction in defect-escape rate"*) are not standalone consulting-deck claims — they're outcomes produced by specific methodology (TDD, BDD, pair programming, hypothesis-driven development, "New Ways of Working" capability development). The methodology IS the story; the numbers are the proof. But when Agy synthesizes responses for queries about delivery acceleration, engineering practices, or transformation outcomes, the numbers tend to surface as headline claims while the methodology context that makes them credible gets compressed out. Result: numbers read as marketing-deck headers rather than evidence-of-substance.
- **Hypothesis-to-verify framing:** The loss could be happening at either (or both) of two layers:
  - **Retrieval layer:** story chunks that contain the methodology context may not surface alongside chunks that contain the metrics, OR the retrieval scoring weights metric-bearing sentences higher than methodology-bearing sentences
  - **Synthesis layer:** the LLM compresses methodology context out during response synthesis even when both methodology and metrics are present in the retrieved context

  Different layer = different fix. Investigation needs to determine which before committing to an approach.
- **Sharpening note relative to CTO persona's "metric hygiene" finding:** The CTO persona prescribed adding baselines + methodology footnotes to top-line stats as a presentation fix. -096 is sharper: the methodology footnotes EXIST in the corpus (the stories document TDD/BDD/pair-programming context); they're being dropped. The fix isn't to ADD them at the surface; it's to PRESERVE them through retrieval and synthesis.
- **Audience impact:** Engineering hiring CTOs reading the metric-as-headline format see consulting-deck claims; reading the metric-with-methodology format see evidence of substance. The CTO persona caught this: *"$300M revenue is consulting revenue not product revenue"* / *"4x faster than a Fortune 500 baseline is a low bar."* Those reactions soften if the methodology context comes through — because the substance is what makes the numbers credible to an engineer.
- **Investigation plan:**
  - Probe queries:
    - *"How did Matt achieve 4x delivery acceleration?"*
    - *"What practices did Matt use at the CIC?"*
    - *"Tell me about Matt's approach to test-driven development"*
    - *"What's the methodology behind Matt's zero-defect claims?"*
  - For each probe: capture full retrieved context (what chunks did Pinecone return) AND the synthesized response. Compare:
    - Does the retrieved context include methodology language? If no → retrieval-layer problem
    - If retrieved context includes methodology language but response doesn't → synthesis-layer problem
    - If both layers drop it → both fixes needed
  - Document findings in a probe results table; expected output for each query at each layer.
- **Fix path (conditional):**
  - **Retrieval-layer fix:** retune chunking / embedding to keep methodology + metric language anchored together; possibly add methodology-anchor metadata for re-ranking
  - **Synthesis-layer fix:** system prompt addition that specifies "when surfacing metric claims, retain the methodology context that produced them"
  - Both layers: combine both fixes
- **Effort:** Investigation 2-3 hours. Fix effort depends on layer (synthesis-layer fix is small; retrieval-layer fix could be substantial).
- **Cross-references:**
  - MATTGPT-077 — retrieval-bias family (different mechanism, same investigation discipline)
  - MATTGPT-088 — Role Match scorer alignment (different surface; -096 is the Ask MattGPT chat side of related credibility concern)
  - CTO persona "metric hygiene" finding — adjacent but distinct fix path (footnotes vs methodology preservation)
  - MATTGPT-094 — same investigation discipline (probe-test before fix design)
- **Logged:** May 28, 2026

---

### MATTGPT-097
**Career-intent framing refresh — corpus predates current role taxonomy; refresh framing AND tighten register**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Career-intent stories in the corpus (*Independent Project – Career Intent – What I'm Looking For Next*, *Accenture – Transition Story – Why I'm Exploring Opportunities*, possibly others) predate the role taxonomy Matt has been building/refining in 2026 (the target role thinking that's downstream of MATTGPT-078 — AI Enablement Option E and related resume options). Result: when Agy is asked *"what's Matt looking for,"* the response uses stale framing — abstract values (*"clarity, empathy, and purpose"*), aspirational language (*"scale products, modernize platforms, and elevate engineering culture"*) — that doesn't reflect the more concrete role-target thinking Matt has since developed.
- **Subsumes earlier prose-register concern:** During May 28, 2026 persona-test review, a separate "career-intent prose register" concern was discussed (informally referenced as a "MATTGPT-094" candidate at that point). That concern — that the career-intent stories are written in pitch-register prose rather than scannable concrete preferences — is the SAME stories with overlapping fix work. Both problems should be addressed in the same refresh pass; treating them as two separate tickets would risk one happening without the other. -097 explicitly covers both the framing problem (stale role targets) AND the register problem (pitch prose).
- **Audience impact:** Recruiter persona's *"clarity, empathy, and purpose"* complaint — *"pitch language, not keyword-searchable signal. I can't paste that into a Boolean string"* — is the register problem. The framing problem (stale role targets) is one Matt observed independently and is at least as important for hiring conversations where Matt's specific target list matters.
- **Distinct from existing tickets:**
  - MATTGPT-078 — adds ONE new story (AI Enablement). -097 refreshes EXISTING career-intent stories. Different stories, different work, related but distinct.
  - MATTGPT-094 (this ticket batch) — retrieval-bias investigation. -097 is content-quality work on the surfaced stories.
  - MATTGPT-093 — About Matt strategic restructure. -097's content output may feed -093's reimagining of About Matt (whatever direction it takes will need refreshed career-intent content as the source-of-truth).
  - MATTGPT-095 — broader anti-consulting bias question across the corpus. -097 is narrower scope (career-intent stories specifically).
- **Fix scope:**
  - **Framing refresh** — update career-intent stories to reflect the current role taxonomy:
    - Specific target titles (Director / VP / SVP Engineering, Head of Platform, Field CTO, AI Enablement leader, etc.)
    - Specific company stages / industries (regulated B2B fintech, enterprise modernization, AI CoE programs)
    - Concrete preferences (0-to-1 vs steady-state, hands-on vs strategy-only, etc.) over abstract values
  - **Register tighten** — replace pitch-register prose with scannable, fact-anchored preferences:
    - *"Clarity, empathy, and purpose"* → *"hands-on with engineers and PMs, not strategy decks; 0-to-1 builder vs steady-state operator"*
    - *"Scale products, modernize platforms, and elevate engineering culture"* → *"platform engineering at 1000-5000 person enterprise modernizing legacy banking systems, OR AI Innovation Center build at F500"*
  - Keep Matt's voice; optimize for scan-time AND keyword-searchability.
- **Effort:** Medium-craft writing work. ~3-5 hours including STAR field updates and embedding regeneration.
- **Cross-references:**
  - MATTGPT-078 — sibling story-writing work (different story, related role-taxonomy work)
  - MATTGPT-079 — Role Match coverage gaps meta (-097 may close coverage gaps surfaced for current target roles)
  - MATTGPT-093 — About Matt restructure (-097's refreshed content feeds whatever direction -093 takes)
  - MATTGPT-095 — broader corpus framing question; -097 is the career-intent slice
- **Logged:** May 28, 2026

---

### MATTGPT-098
**Explore Stories default state — exclude Professional Narrative + sort Start_Date desc (match Timeline behavior)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Explore Stories Table and Cards views default to alphabetical title sort with no Category exclusion. Result: "About Matt: My Leadership Journey" and other behavioral/narrative stories surface at the top of an A-Z list, giving a recruiter or hiring manager landing on the surface a weak first impression that doesn't represent Matt's project work. UX research (Baymard, others) is clear that alphabetical default sort on content corpora is anti-pattern when the initial sample doesn't represent the category — users discard the surface because it doesn't look relevant at first sight.
- **Current behavior asymmetry:** Timeline view already handles this correctly via `EXCLUDED_ERA = "Leadership & Professional Narrative"` (see `ui/components/timeline_view.py:42`) — the 10 behavioral stories are excluded from the era-grouped timeline. Table and Cards views do not apply the same exclusion, so the same 10 stories pollute the default browse.
- **Data shape (verified May 29, 2026):**
  - `Category == "Professional Narrative"` = 10 stories
  - `Era == "Leadership & Professional Narrative"` = same 10 stories (1:1 overlap)
  - `Start_Date` is `YYYY-MM` string format — directly sortable, no parsing needed
  - 113 stories total → 103 project stories after exclusion
- **Fix:**
  - On default load of Explore Stories, filter out stories where `Category == "Professional Narrative"` (or use Era-based exclusion for consistency with Timeline)
  - Sort remaining stories by `Start_Date` descending (most recent first)
  - Behavioral stories remain reachable via Category filter in Advanced Filters — user can opt in
  - Apply to BOTH Table and Cards views (Timeline already correct)
  - Sortable columns continue to work as today — this only changes the default state, not the available sorts
- **Why Start_Date desc, not End_Date desc:** Simpler. Start_Date is the project's start, which aligns with how Matt narrates the work ("In 2019, I joined CIC and..."). End_Date desc was considered but introduces edge cases for long-running or ongoing projects.
- **Why not change in this ticket:**
  - No filter architecture change (Advanced Filters stays as-is — UX research supports the progressive-disclosure pattern)
  - No view switcher or pagination change
  - No detail pane change (auto-scroll already handles spatial connection)
  - This is one default-state change, not a redesign
- **Effort:** Small. Two-file change (Table view sort/filter, Cards view sort/filter). No wireframe needed — the visual surface is unchanged; only the initial story set and order differ.
- **Cross-references:**
  - `ui/components/timeline_view.py:42` — existing `EXCLUDED_ERA` pattern to mirror
  - MATTGPT-065 — polish bundle (consider folding this in if -065 hasn't shipped yet, or ship standalone if -065 is already scoped)
- **Logged:** May 29, 2026

---

### MATTGPT-099
**Role Match — assess and decide comp handling on JDs that include comp expectations**

- **Status:** Open
- **Priority:** Medium
- **Type:** Investigation + Action
- **Issue:** Role Match's JD parser currently has no defined behavior for JDs that include comp expectations (e.g., *"Salary: $200-280K base + equity"*). Likely current behavior is silent drop (consistent with how location / work-model / availability are silently dropped per MATTGPT-089's findings), but this is unverified — could also be hallucinated match, surfaced as a gap, or treated as a qualification requiring an answer. No ticket previously owned this — MATTGPT-089 explicitly excluded comp (*"Skip comp — see MATTGPT-090 for separate handling"*), and MATTGPT-090 (closed Decided Against May 29, 2026) only covered the chatbot-side comp decline. The Role Match-side gap fell between the two tickets.
- **Why this is its own ticket (not folded into -089):** Comp can't be **matched** against profile data — only **declined** — because Matt doesn't disclose comp publicly (per the Personal Intent Family decision codified in `services/semantic_router.py:192-209`). Location / work-model / availability (the -089 scope) can match against profile data (Atlanta + relocation openness from `data/matt_profile.json` or footer copy). Different UX shape, different fix path.
- **Working direction (May 29, 2026 — exact language TBD):** Surface comp as a recognized JD requirement with a non-disclosure treatment — e.g., *"Not assessed publicly — direct conversation"* — rather than silently dropping it (which produces the same recruiter confusion as the chat-side silent fallback that drove the original -090 framing). Exact copy and result-panel placement are open design calls.
- **Phased scope:**
  - **Phase 1 — Audit current behavior:** Paste 3-5 JDs that include comp into Role Match. Capture exactly what happens: silently dropped, hallucinated match, surfaced as gap, or other. Document in a probe results note.
  - **Phase 2 — Design call:** Pick the non-disclosure pattern. Options to consider: (a) surface-with-note in the Match results panel (treating comp like location/work-model with a "not publicly assessed" label); (b) route to chat where Personal Intent Family handles the decline; (c) inline note in the qualifications list without a dedicated tile; (d) something else. Cross-surface consistency matters — whatever pattern lands should align with how chat declines comp (warm pivot, not silent).
  - **Phase 3 — Implementation:** Small parser extension + result panel addition once design lands. Likely similar scope to -089 (small, scoped change in the Role Match JD parser + result rendering).
- **Audience impact:** Recruiter persona finding (May 27, 2026) called out comp as *"the single biggest miss"* on the chat side. Now closed there (-090 Decided Against). But the Role Match side has the same recruiter sitting there with the same expectation — paste a JD, get a complete answer to "can we hire him." Silent drop on comp on Role Match reintroduces the same recruiter-confusion failure mode that the chat side now correctly avoids.
- **Effort:** Phase 1 audit: ~30 min. Phase 2 design call: short conversation. Phase 3 implementation: ~1-2 hours.
- **Cross-references:**
  - MATTGPT-089 — sibling JD-parser ticket (location / work-model / availability); -089 explicitly excludes comp, -099 owns it
  - MATTGPT-090 — Decided Against, but its closure note points here for the Role Match-side gap; consistency with `services/semantic_router.py:192-209` is the cross-surface anchor
  - MATTGPT-088 — Role Match scorer honesty discipline (the "no Strong Match when chat would say no" principle applies here too: Role Match shouldn't silently disclose what chat declines)
- **Logged:** May 29, 2026

---

### MATTGPT-100
**Navigation labels — rename to Home / My Work / Ask Agy / Role Match / My Profile (wireframe-locked)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor
- **Issue:** Current navigation labels (Home / Explore Stories / Ask MattGPT / Role Match / About Matt) do not match the wireframe-locked labels (Home / **My Work** / **Ask Agy** / Role Match / **My Profile**). The new labels were locked during the May 29, 2026 design pass and reflect the recruiter-framing direction: *"My Work"* reads as portfolio scope (not a generic verb), *"Ask Agy"* centers on the assistant's brand identity (per Why Agy modal work), *"My Profile"* matches recruiter conventions (LinkedIn-shaped framing).
- **Why now:** Other wireframe-driven work (Why Agy modal, How I Built deep-link surface) routes from these labels. Renaming late risks broken cross-surface links and stale routing references.
- **Fix:** Mechanical find-and-replace across:
  - Primary nav config / `app.py` tab definitions
  - `ui/components/navbar.py` (if labels are defined there)
  - Any hardcoded label strings in landing pages or modals that reference old names
  - BDD test fixtures that assert nav-label text (e.g., `tests/bdd/features/home.feature` and any `home_*.feature` or `nav_*.feature` that match on labels)
  - Any session-state values keyed on tab names (`active_tab` values must update if they encode the label text)
- **Effort:** Small (~30-60 min). Mechanical but touches multiple files; verification needs a clickthrough on all 5 nav items + any cross-surface routing.
- **Cross-references:**
  - MATTGPT-093 — About Matt strategic restructure. -100 is JUST the label rename; -093's structural decision (split / fold / reframe) is independent.
  - MATTGPT-101 — Why Agy modal (the "Ask Agy" rename anchors the assistant's brand identity that the modal explains)
- **Logged:** May 30, 2026

---

### MATTGPT-101
**Why Agy? modal + "?" badge on Agy avatar (uniform placement)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Wireframe lock (May 29, 2026) introduces a brand-identity modal that answers *"Why is the assistant called Agy?"* — Plott Hound origin + breed-to-RAG mapping (*"Plott Hounds are bred for tracking: determined, loyal, hard to shake. Those same traits define how I work..."*). Modal is triggered by a *"?"* badge placed on Agy's avatar wherever the avatar appears (Home, Ask Agy Landing, Ask Agy Conversation, Banking, Cross-Industry).
- **Why bundled (modal + badge in one ticket):** The badge IS the modal's trigger. Splitting them creates a half-shipped state — badge with nowhere to go, or modal with no entry point. Single ticket keeps the entry-to-content pair atomic.
- **Locked content (from May 29, 2026 wireframe):**
  - Headline: *"Why Agy?"*
  - Body: *"I'm named for Matt's Plott Hound. Plott Hounds are bred for tracking: determined, loyal, hard to shake. Those same traits define how I work: I track down the right stories from 130+ projects across 20+ years, hold onto the trail when the question gets tricky, and don't pretend to know what isn't in the corpus."*
  - Italicized companion line: *"It felt right to keep his name part of the work we loved doing together."*
  - Footer link: *"Curious how I was built? Read the technical deep-dive"* → routes to How I Built MattGPT surface (MATTGPT-102)
- **Content notes:** The locked body references "130+ projects" and "20+ years" — both should align with MATTGPT-019's standardization (currently shifting to "100+") and MATTGPT-103's Agy-intro decision. If those land first, this ticket inherits the resolved copy.
- **Fix shape:**
  - New component: `ui/components/why_agy_modal.py` (mirrors `ui/components/how_agy_modal.py` structure where applicable)
  - New "?" badge: small CSS overlay positioned top-right of the Agy avatar wherever it renders; clickable, with `data-testid` for BDD selectors. New CSS tokens in `global_styles.py` (badge size, color, positioning) — no hex fallbacks, use CSS variables only per CLAUDE.md
  - Wire badge → modal open across the 5 surfaces (Home, Ask Agy Landing, Ask Agy Conversation, Banking Landing, Cross-Industry Landing) where Agy avatar appears
  - Modal close: X button, backdrop click, Escape key. Desktop overlay pattern; mobile bottom-sheet pattern.
  - No state navigation — modal is overlay only, returns user to the surface they were on
- **Effort:** Small-medium (~2-3 hours). New component with locked content + new CSS for badge + wiring across 5 surfaces.
- **Cross-references:**
  - MATTGPT-102 — How I Built MattGPT (modal's footer link routes there)
  - MATTGPT-076 — How Agy Searches modal mobile fix (sibling modal; check whether mobile bottom-sheet pattern can be shared)
  - MATTGPT-019 — Story count copy ("130+" in locked content should align)
  - MATTGPT-103 — Agy intro line copy decision ("20+ years" in locked content should align)
- **Logged:** May 30, 2026

---

### MATTGPT-102
**How I Built MattGPT — relocate from About Matt section to standalone deep-link surface (no main nav entry)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** Wireframe lock (May 29, 2026) relocates the "How I Built MattGPT" technical deep-dive content from its current home (a section within the About Matt page) to a standalone deep-link surface. The surface is NOT in the main nav — it's reached only via Why Agy modal footer link (MATTGPT-101), Profile signals panel, or other contextual entry points. Once relocated, the "How I Built" block must be removed from About Matt to avoid duplicate content.
- **Why a surface, not a modal:** Content is substantial (system architecture diagram, tech stack grid, 5-stage RAG pipeline detail, CI/CD pipeline detail, "See It In Action" sample questions). Too much for a focused modal — a scrollable modal of this length reads as a misuse of the modal pattern.
- **Why no main nav entry:** This is a credibility-building credential for engaged readers (technical hiring managers, curious recruiters), not a primary surface for cold visitors. Deep-link-only entry preserves the "not the main attraction" framing while still letting it ship as a real page.
- **Fix shape:**
  - New page: `ui/pages/how_i_built.py` (relocates existing content from About Matt's "How I Built" section as-is — no rewriting in this ticket)
  - Page renders without active nav-tab state (deep-link only); navbar still renders for orientation but no tab is highlighted
  - "← Back to X" context-aware affordance at top-left of page, using `session_state.previous_tab` (same pattern as Banking + Cross-Industry landings)
  - Fallback when `previous_tab` is None: "← Back to Home"
  - About Matt: remove the How I Built block to avoid duplicate content (separate edit, same commit)
  - Routing: Why Agy modal footer link routes here (handled in MATTGPT-101)
- **Effort:** Medium (~2-3 hours). Content extraction is mechanical; back-button logic is small; routing wiring is straightforward.
- **Cross-references:**
  - MATTGPT-101 — Why Agy modal (entry point)
  - MATTGPT-093 — About Matt strategic restructure. -102's relocation is locked independent of -093's strategic direction (split / fold / reframe). The How I Built block leaves About Matt regardless of which structural option -093 picks.
  - Banking + Cross-Industry landings — reference implementation for the "no nav tab + back affordance" pattern
- **Logged:** May 30, 2026

---

### MATTGPT-103
**Agy intro line — resolve "20+ years of work" inconsistency with stats bar (Years tile dropped)**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Issue:** Home hero Agy intro line currently reads *"That's Agy, my Plott Hound and AI assistant, ready to track down insights from 20+ years of work."* The *"20+ years"* signal is the same one that was dropped from the stats bar's Years tile (May 29, 2026, MATTGPT-092) for ageism + non-positioning reasons. Leaving the years number in the Agy intro partially undoes that mitigation.
- **Decision (open — three working options):**
  1. **Drop the number:** *"That's Agy, my Plott Hound and AI assistant, ready to track down insights from across Matt's career."*
  2. **Swap to project count + sector breadth:** *"That's Agy, my Plott Hound and AI assistant, ready to track down insights from 100+ projects across financial services and enterprise platforms."* (Also aligns with MATTGPT-019's "100+" standardization.)
  3. **Leave as-is** — read the line as functional/corpus scope (telling the user how big Agy's data set is) rather than personal positioning. The years here describe the data, not Matt's age.
- **Fix:** Once decision lands, one-line copy change in `ui/components/hero.py`.
- **Effort:** Trivial (~5 min once decision lands).
- **Cross-references:**
  - MATTGPT-019 — Story count copy. Option (b) would align the Agy intro with the broader find/replace pass.
  - MATTGPT-092 — Hero seniority signal. -092 established the principle that the Years signal was dropped from positioning surfaces; -103 is the consistency check on the Agy intro line.
  - MATTGPT-101 — Why Agy modal locked content also references "20+ years" — whatever -103 decides should propagate to the modal copy.
- **Logged:** May 30, 2026

---

### MATTGPT-104
**Banking + Cross-Industry landing pages — math reconciliation bug (33 vs 32 vs 48 vs 57 inconsistency)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Issue:** During the May 29, 2026 wireframe pass, project/story counts on the Banking landing page displayed inconsistent numbers across different rendering points (observed: 33 vs 32 vs 48 vs 57). Similar inconsistency observed on the Cross-Industry landing. Root cause is a bug in the dynamic-generation code that produces these counts, not a corpus tagging issue or wireframe specification gap (Matt's call during the wireframe review).
- **Why a separate ticket (not folded into MATTGPT-065):** MATTGPT-065 is scoped specifically to Explore Stories polish (filter UX, empty states, story details). Banking + Cross-Industry landing pages are different surfaces with their own count-generation logic and dynamic story-rendering paths. The earlier framing during the May 29 wireframe pass that this would fold into -065 was wrong.
- **Audience impact:** Recruiters land on the Banking page expecting to see Matt's banking work. Inconsistent counts read as data-quality issues — undermines the polish that the rest of the site projects. *"Why does the page say 33 projects in one place and 57 in another?"* is the kind of thing a hiring manager flags on a call.
- **Fix shape:**
  - **Investigate** the four count values (33 / 32 / 48 / 57) — trace each to its source (filter query, story tag aggregation, hardcoded value, prefilter routing artifact, etc.)
  - **Reconcile to single source of truth** — same filter query / same aggregation logic, consistent across all display points on a given page
  - **Apply to both** Banking and Cross-Industry landings (same pattern likely produces the same bug shape on Cross-Industry)
  - **Verify** the corrected counts match the actual filtered-story count when the user clicks into Explore Stories with the same filter applied
- **Effort:** Small-medium (~1-2 hours including investigation + fix + verification across both surfaces).
- **Cross-references:**
  - MATTGPT-065 — Explore Stories polish bundle (sibling polish work but different surface; this ticket explicitly does NOT fold into -065)
  - MATTGPT-019 — Story count copy (different concern — that's about hardcoded "130+"; this is about dynamic counts on landing pages)
- **Logged:** May 30, 2026
