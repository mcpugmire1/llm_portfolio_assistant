# MattGPT Backlog
<!-- last-backlog-sync: a6b427c -->
<!-- BEFORE EDITING: read CLAUDE.md § Backlog Maintenance for status enum, ticket lifecycle, and archiving rules -->
<!-- Next ticket ID: run grep -o 'MATTGPT-[0-9]*' BACKLOG.md | sort -t- -k2 -n | tail -1 to find current max, then add 1 -->

Work state for the MattGPT project. The matrix below is the scannable view. Detail blocks for each item follow, linked by ID. Completed items live in `CHANGELOG.md`. Architectural decisions live in `docs/ADR.md`. Current system state lives in `ARCHITECTURE.md`.

---

## Value Prioritized Roadmap (updated 2026-06-24)

**NOW**
1. **-075** — Validate debug-surface leak. Confirm `DEBUG=False` on Streamlit Cloud + prod check. Likely closes as add-missing-guards or no-op.
2. **-080** — `matt_profile.json` restructure. Blocker for -088: scorer and Agy chat need stable shared grounding before alignment work makes sense.
3. **-088** — Role Match scorer honesty, on top of -080. Biggest single credibility hit (CTO persona: AI contradicting itself). Gates -012 private-view quality.
4. **-094 probes** — CIC over-concentration + operational under-surfacing. In progress. Running before -080 — findings shape the restructure.
5. **-077 mitigation** — Query-side: strip "Matt" from embedded queries on technical-noun shapes. Protects primary free-text recruiter flow from MattGPT self-referential answers.
6. **-097** — Career-intent refresh. Timely for active outreach; makes "what's Matt looking for" keyword-searchable.
7. **-129 stories 1+2** — AT&T SE CRM + Fiserv expand-from-logged stories (no elicitation block yet). Operational depth pairing with -094 sub-hypothesis B.

**NEXT** (queued):
1. **-128** — Source faithfulness. Unlocked once -080 + -094 land. Second-biggest trust item: recruiter clicks to verify a claim, gets wrong source cards.
2. **-089** — Logistics filter class: location / work-model / availability. Atlanta + relocation-open status currently dropped silently.
3. **-015** — JPM Payments IQ differentiation. Cheap data pass; upstream of operational surfacing; cleaner signal for -094/-128/-088.
4. **-077 full fix** — Hybrid retrieval (BM25 + semantic). Handles severe-overlap nouns; closes -061 residual.
5. **-094 fixes** — Conditional on probe findings.
6. **-074** — Entity cluster synthesis forcing. "How did you build the CIC" returns a survey instead of depth on a marquee query.
7. **-096** — Methodology-context preservation. The methodology is what makes the metrics credible to an engineer.

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
| [MATTGPT-062](#mattgpt-062) | Semantic router cache silently uses stale embeddings when VALID_INTENTS changes | Open | Medium | Refactor | May 14, 2026 |
| [MATTGPT-063](#mattgpt-063) | Wrong-person queries with names outside nonsense regex produce confused-context RAG answers | Open | Medium | Issue | May 14, 2026 |
| [MATTGPT-070](#mattgpt-070) | Ask MattGPT — Suggestion button cursor pointer | Decided Against | Low | Issue | May 15, 2026 |
| [MATTGPT-072](#mattgpt-072) | `generate_public_tags.py` — case-insensitive tag dedup | Open | Low | Refactor | May 16, 2026 |
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
| [MATTGPT-088](#mattgpt-088) | Role Match scorer — align with Agy honesty (no Strong Match when chat would say no) | Open | High | Issue | May 28, 2026 |
| [MATTGPT-089](#mattgpt-089) | Role Match — parse location, work-model, availability as distinct filter class | Open | High | Issue | May 28, 2026 |
| [MATTGPT-090](#mattgpt-090) | System prompt — decline cleanly on comp / off-scope queries (no silent fallback) | Decided Against | Medium | Action | May 28, 2026 |
| [MATTGPT-091](#mattgpt-091) | Add a credible failure story to the corpus (sibling to -022 / -078 pattern) | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-094](#mattgpt-094) | Retrieval concentration audit — CIC over-weighting + operational story under-surfacing (hypotheses to verify) | In Progress | High | Investigation | May 28, 2026 |
| [MATTGPT-095](#mattgpt-095) | Anti-consulting bias in story framing — corpus reads "consulting" as default register when it shouldn't | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-096](#mattgpt-096) | Methodology context dropped during synthesis — TDD/BDD and ways-of-working substance gets compressed out of metric claims (hypothesis to verify) | Open | Medium | Issue | May 28, 2026 |
| [MATTGPT-097](#mattgpt-097) | Career-intent framing refresh — corpus predates current role taxonomy; refresh framing AND tighten register | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-099](#mattgpt-099) | Role Match — assess and decide comp handling on JDs that include comp expectations | Open | Medium | Investigation + Action | May 29, 2026 |
| [MATTGPT-103](#mattgpt-103) | Agy intro line — resolve "20+ years of work" inconsistency with stats bar (Years tile dropped) | Decided Against | Low | Refactor | May 30, 2026 |
| [MATTGPT-109](#mattgpt-109) | mattgpt-design-spec Jekyll site — sync UI refresh changes (nav labels, navbar, cards, How I Built, How Agy Searches, Why Agy modal, user journeys) | Open | High | Action | June 1, 2026 |
| [MATTGPT-115](#mattgpt-115) | Lock icon — browser console warning: password field not in native form (st.popover portal breaks form containment) | Open | Low | Issue | June 6, 2026 |
| [MATTGPT-120](#mattgpt-120) | CLAUDE.md restructure — Critical Rules fast-reference block + rules-first format throughout | Open | Medium | Action | June 9, 2026 |
| [MATTGPT-121](#mattgpt-121) | Why Agy dialog — mobile layout fix (375px viewport); title font-size override pending DevTools selector confirmation | Open | Medium | Bug | June 9, 2026 |
| [MATTGPT-122](#mattgpt-122) | My Work — Cards view BDD timing: test_view_switching_preserves_open_story_detail fails (components.html iframe listener not attached at click time) | Open | Low | Issue | June 10, 2026 |
| [MATTGPT-125](#mattgpt-125) | CLAUDE.md targeted fixes — confirmed bugs + confirmed gaps from June 12 audit | Open | Medium | Action | June 12, 2026 |
| [MATTGPT-126](#mattgpt-126) | Ask Agy landing — input border invisible on page load (CSS injection race) | Open | Low | Issue | June 12, 2026 |
| [MATTGPT-127](#mattgpt-127) | Replace hardcoded `ASSESSMENT_MODEL` in `jd_assessor.py` with `get_conf()` env var pattern | Open | Low | Refactor | June 12, 2026 |
| [MATTGPT-128](#mattgpt-128) | Displayed-source faithfulness — source cards must substantiate the claims in the answer | Open | High | Issue | June 14, 2026 |
| [MATTGPT-129](#mattgpt-129) | Content elaboration per era — expand 5 under-documented operational stories | Open | High | Action | June 14, 2026 |
| [MATTGPT-130](#mattgpt-130) | "practitioners" canonical everywhere — UI, eval golden set, corpus re-embed in lockstep | Open | Medium | Action | June 14, 2026 |
| [MATTGPT-131](#mattgpt-131) | BDD selector bug — `test_industry_and_capability_labels_visible_inline_on_mobile` fails in marathon run | Open | Low | Bug | June 15, 2026 |
| [MATTGPT-133](#mattgpt-133) | BDD skip — `test_ask_agy_works_from_table_view` skips when AgGrid iframe row interaction doesn't open detail panel | Decided Against | Low | Bug | June 16, 2026 |
| [MATTGPT-134](#mattgpt-134) | BDD skip — `test_deeplink_respects_view_mode` skips because deeplink navigation does not preserve pre-set view mode | Decided Against | Low | Bug | June 16, 2026 |
| [MATTGPT-136](#mattgpt-136) | Dark mode design system audit — --accent-purple not overridden in body.dark-theme | Open | Low | Refactor | June 18, 2026 |
| [MATTGPT-137](#mattgpt-137) | AgGrid bootstrap.min.css render-blocking on Ask Agy → My Work transition | Open | Low | Perf | June 18, 2026 |
| [MATTGPT-138](#mattgpt-138) | BDD: page teardown invariant + CLS budget guard (MATTGPT-018 regression lock) | Decided Against | Medium | Action | June 19, 2026 |
| [MATTGPT-140](#mattgpt-140) | Fix hardcoded model names in backend_service.py and jd_assessor.py — use constants.py | Open | Low | Refactor | June 20, 2026 |
| [MATTGPT-141](#mattgpt-141) | Remove dead ENTITY_GATE_THRESHOLD constant from config/constants.py | Open | Low | Refactor | June 22, 2026 |
| [MATTGPT-142](#mattgpt-142) | BDD sequential rejection test: wait_for_banner is not count-aware, assertion runs before second rejection renders | Open | Low | Bug | June 23, 2026 |
| [MATTGPT-143](#mattgpt-143) | BDD app_url fixture hardcodes port 8501 with no env-var override | Parked | Low | Bug | June 23, 2026 |
| [MATTGPT-144](#mattgpt-144) | AgGrid iframe re-init on filter rerun — blank/slow grid; possible shared root with the blep (-018) | Done | Medium | Investigation | Jun 24, 2026 |
| [MATTGPT-145](#mattgpt-145) | Mobile filter breakpoints overlap — r2-label show/hide depends on !important cascade order, not design | Open | Low | Refactor | Jun 24, 2026 |
| [MATTGPT-146](#mattgpt-146) | Professional Narrative stories leak into My Work via filter and search paths — must be excluded from all My Work paths | Open | Medium | Bug | Jun 25, 2026 |
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

**Private overlay spec update (June 11, 2026)**
- Wireframe v3 separates empty state (-066) and public populated state (-067) as distinct frames. Private state frame (-012) is preserved and labeled. The following supplements the Phase 4 spec with private overlay content logic.

**Evaluation grid — open design decision**
- Current wireframe: 2×2 grid, 4 equal-weight tiles (Overall fit / Recommendation / Comp alignment / Work mode).
- Problem: Overall fit and Recommendation are decisions. Comp alignment and Work mode are prerequisites. Equal visual weight misrepresents the hierarchy.
- Options: (A) Keep 2×2 as-is. (B) 2-tile top row (Overall fit + Recommendation) + logistics row (Comp alignment + Work mode) at reduced visual weight. Option B communicates the decision/prerequisite split.
- **Decision needed before implementation.**

**Strategic fit notes — content logic**
- Purpose: "so what" interpretation layer above the raw match data — why this role is or isn't a fit beyond the requirement checklist.
- Content categories: domain alignment signal (depth vs adjacent); scale/pattern parallels (where Matt's proof points map to role needs); gap contextualization (explainable vs blocking vs irrelevant).
- Inputs: match results + Opportunity Filter dimensions + How I Work and Lead positioning docs.
- Output shape: 2–4 prose bullets per assessment, generated per JD (not hardcoded).

**Action items — content logic**
- Purpose: concrete next steps if Matt decides to pursue. Decision support, not assessment.
- Content categories: channel recommendation (direct / network / referral); prep recommendations (which stories to lead with, which materials to create); network activation (connections at company from Notion target list); corrective actions (which asset type to fix per the six-type framework when a gap is addressable).
- Inputs: match results + company/role metadata + network data (Notion) + corrective actions framework.
- Output shape: 2–4 actionable bullets per assessment, generated per JD.

**Open: LLM-generated vs rule-based**
- Strategic fit notes → fully LLM-generated (requires synthesis across match data + positioning docs).
- Action items → partially rule-based: channel + network activation rule-based from Notion data; prep recommendations LLM-augmented.
- **Decision needed before implementation.**

**Public vs private state contract**
- Public (recruiter) sees: results header, legend, summary block, per-requirement cards with evidence chips and gap notes, post-result "Ask Agy a follow-up" CTA.
- Private (Matt authenticated) sees: everything in public, plus "My evaluation" block above summary: evaluation grid tiles, strategic fit notes, action items. Purple-tinted block with "PRIVATE · MATT ONLY" badge.
- Comp alignment tile → private only. Verdict/recommendation (Apply/Consider/Pass) → private only.
- Lock icon: `ti-lock` (closed) in public state; `ti-lock-open` (open) in private state with purple-tinted active state.

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

### MATTGPT-070
**Ask MattGPT — Suggestion button cursor pointer**

- **Status:** Decided Against — Not Reproducible (June 9, 2026)
- **Priority:** Low
- **Type:** Issue
- **Issue:** The 6 suggestion buttons on the Ask MattGPT landing page (`ui/pages/ask_mattgpt/landing_view.py:97-135`) are real `st.button(type="secondary")` calls. The CSS rule at `ui/pages/ask_mattgpt/styles.py:288-309` styles them as cards (border, background, padding, hover background) but **does not declare `cursor: pointer`**. Adjacent buttons in the same file DO declare it explicitly (lines 443, 1290, 1399), so it's not being relied upon to inherit from Streamlit defaults. Live testing (May 15, 2026) confirms the pointer does not change on hover — cards appear interactive (purple text, border) but the cursor stays as the default arrow.
- **Audience impact:** First-time visitor cannot visually confirm the cards are clickable until they actually click one. Cheap trust erosion at the first interaction moment.
- **Fix:** Add `cursor: pointer !important;` to the existing `button[key^="suggested_"]` rule at lines 288-309. ~1 line.
- **Closed June 9, 2026 — not reproducible.** DevTools inspection confirmed all 6 buttons already compute `cursor: pointer` from Streamlit's base stylesheet. Root cause: `button[key^="suggested_"]` is a dead selector — Streamlit renders the `key=` param as a class on the container (`.st-key-suggested_0`), not as an HTML attribute on the `<button>` element. The entire rule block at `styles.py:288-309` matches 0 elements in the live DOM. No fix needed; cursor is correct via Streamlit's own CSS.
- **Out of scope (closed per May 15 assessment):** Input field below the fold (the 6 suggestion buttons are themselves real CTAs that submit queries — input is the secondary path, defensible as-is); status bar developer-facing copy (design call for a technical-leaning portfolio); conversation export/share (already deferred to React migration per `conversation_helpers.py:470` TODO).
- **Logged:** May 15, 2026

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
- **Latency context (measured June 24, 2026, `jd_assessor.py`):** 1+N sequential gpt-4o calls; loop is linear in N requirements. `assess` dominates; `extract` is a large N-independent cost (~22s local on the demo JD). Parallelizing `assess` buys ~3-4x but `extract` is the floor. Relevant when evaluating whether scorer changes add meaningful latency.
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
- **Latency context (measured June 24, 2026, `jd_assessor.py`):** 1+N sequential gpt-4o calls; loop is linear in N requirements. `assess` dominates; `extract` is a large N-independent cost (~22s local on the demo JD). Parallelizing `assess` buys ~3-4x but `extract` is the floor. Relevant when deciding where comp handling sits in the call sequence.
- **Cross-references:**
  - MATTGPT-089 — sibling JD-parser ticket (location / work-model / availability); -089 explicitly excludes comp, -099 owns it
  - MATTGPT-090 — Decided Against, but its closure note points here for the Role Match-side gap; consistency with `services/semantic_router.py:192-209` is the cross-surface anchor
  - MATTGPT-088 — Role Match scorer honesty discipline (the "no Strong Match when chat would say no" principle applies here too: Role Match shouldn't silently disclose what chat declines)
- **Logged:** May 29, 2026

---

### MATTGPT-103
**Agy intro line — resolve "20+ years of work" inconsistency with stats bar (Years tile dropped)**

- **Status:** Decided Against (May 30, 2026)
- **Priority:** Low
- **Type:** Refactor
- **Decided Against (May 30, 2026):** The "inconsistency" framing was wrong. The stats bar and the Agy intro line are different surfaces doing different jobs. The stats bar is a credentialing surface (recruiter 5-second scan) where the anti-bias play matters most — that's why the Years tile was dropped in MATTGPT-092. The Agy intro line is grounding-the-AI-assistant copy — it tells the user that Agy has a real corpus of career experience to draw from. The "20+ years of work" token there reads as *corpus scope* (how much data the AI has), not as *personal positioning* (how old the candidate is). The anti-bias play that drove the Years tile drop doesn't transfer to a surface doing different work. Closing without a code change; the line stays as-is in `ui/components/hero.py:174`.
- **Earlier framing (superseded):** Home hero Agy intro line currently reads *"That's Agy, my Plott Hound and AI assistant, ready to track down insights from 20+ years of work."* The *"20+ years"* signal is the same one that was dropped from the stats bar's Years tile (May 29, 2026, MATTGPT-092) for ageism + non-positioning reasons. Leaving the years number in the Agy intro partially undoes that mitigation.
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

### MATTGPT-109
**mattgpt-design-spec Jekyll site — update as a first-class credibility artifact (not housekeeping)**

- **Status:** Open
- **Priority:** High
- **Type:** Action
- **Purpose (reframed June 1, 2026):** The spec is NOT the bottom rung of a technical-depth funnel. It is a **standalone credibility artifact** aimed squarely at the technical hiring manager or CTO doing due diligence — a full product blueprint proving product leadership, technical execution, and design thinking end-to-end. It also serves as a build-it-yourself guide for engineers who want to replicate the approach. This reframe changes both the urgency and the scope: drift is a credibility liability, not housekeeping. A sharp evaluator noticing the docs lag the product undercuts the entire message at the worst moment.
- **Origin context (why this matters):** MattGPT was built partly to reconstruct a professional record lost when Matt left Accenture — credentials, references, code, documents, all gone at notification. The STAR corpus was rebuilt from memory. The spec is the artifact that proves the reconstruction was deliberate and rigorous, not just "I built a RAG app." That story is currently invisible in the spec.
- **Active credibility liabilities (as of June 1, 2026):**
  - "Last Updated December 2025" timestamp — app has shipped 10+ significant changes since
  - Contact line still says "Digital Transformation Director" — stale title, wrong positioning
  - Nav labels throughout still say "About Matt", "Ask MattGPT", "Explore Stories" — old structure
  - Wireframes dated October 2025 — predate the entire `feature/ui-redesign` branch
  - No mention of Why Agy modal, How I Built standalone surface, or the three-tier disclosure model
- **Discoverability gap:** The spec is currently buried three hops deep (Agy → How I Built → footer link). The technical hiring manager it's built for has to dig the most to find it. Needs a direct, clearly labeled entry point — first-class link from My Profile signals panel and from How I Built.
- **Scope of content updates needed:**
  - **Positioning** — update "What This Demonstrates" and intro to reflect the reconstruction origin + deliberate credibility artifact framing
  - **Nav labels** — Home / My Work / Ask Agy / Role Match / My Profile throughout (MATTGPT-100)
  - **Navbar + cards** — reflect shipped redesign (MATTGPT-106, -107)
  - **How Agy Searches** — document migration to `@st.dialog`; remove Technical Details block (run-vs-build split)
  - **How I Built** — document as standalone surface (MATTGPT-102); tour-level content, not triplicate pipeline tellings
  - **Why Agy modal** — document new component + badge placement across 5 surfaces (MATTGPT-101)
  - **User journeys / wireframes** — update to reflect 9 current surfaces including secondary surfaces (Banking, Cross-Industry, How I Built) with back affordances
  - **ARCHITECTURE.md sync** — spec architecture docs should reflect current lean pipeline
  - **Timestamp + contact line** — "Last Updated" and positioning copy
- **Discoverability fix (in-app, separate from spec content):**
  - Add direct link to spec from My Profile signals panel (pending Profile v2 signals panel work)
  - Ensure How I Built's "View Design Specification →" link is prominent, not a footer afterthought
- **Timing:** Hold until in-flight app work stabilizes (-101, -102 mechanism, -105, -108). Then update spec in one deliberate pass — not piecemeal. The spec should reflect a stable, coherent state of the app, not a moving target.
- **Effort:** Medium-High (~4-6 hours). Content updates across 12 doc pages + wireframes + positioning copy. No structural changes to the Jekyll site itself, but the positioning rewrite (origin story, "What This Demonstrates") needs care.
- **Cross-references:**
  - **MATTGPT-101** — Why Agy modal (new surface to document in spec)
  - **MATTGPT-102** — How I Built standalone surface + content trim
  - **MATTGPT-100, -106, -107** — nav / navbar / cards changes already shipped
  - **MATTGPT-093** — About Matt strategic restructure; spec's About Matt wireframe needs to reflect Profile v2 direction
- **Logged:** June 1, 2026

---

---
### MATTGPT-115
**Lock icon — browser console warning: password field not in native form**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** Chrome fires `[DOM] Password field is not contained in a form` when the Role Match lock icon popover is open. `st.popover` uses a portal — it teleports its DOM nodes to a different location in the document. `st.form` creates a native `<form>` element, but the portal moves the children (including the `<input type="password">`) outside the form's DOM subtree. Chrome's password-manager detection fires because the containment check fails.
- **Functional impact:** None. Streamlit's form submission logic is Python-level. The password check, fail-closed behavior, and session state update all work correctly. The warning is purely Chrome's password manager saying it can't hook into the field.
- **Desirability of fix:** Low. Password manager NOT saving this internal access code is actually correct behavior. `autocomplete="new-password"` is already set by Streamlit on `type="password"` fields; the containment check fires before Chrome reads autocomplete.
- **Fix options (all non-trivial):**
  1. Replace `st.form` + `st.form_submit_button` with `st.text_input` + `st.button` + widget-key versioning for clear-on-submit. Does not fix the containment warning (still no native form wrapping).
  2. Replace the entire popover body with a `components.html` custom form — full control over HTML structure, native `<form>` wrapping possible, but requires a JS bridge to report submission back to Streamlit.
- **Affects:** `ui/components/lock_icon.py` — `st.popover` + `st.form` combination.
- **Logged:** June 6, 2026

---

### MATTGPT-121
**Why Agy dialog — mobile layout fix (375px viewport)**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug / Polish
- **Goal:** Fix cramped mobile layout on the Why Agy dialog at 375px. Dialog renders at 374×645px against a 661px viewport — 16px breathing room, no visible scroll affordance. Image floats right at 100px, leaving body text in a ~230px column at full desktop font size.
- **Fix already partially shipped (June 9, 2026):** `@media (max-width: 480px)` block added to `_CSS` in `ui/components/why_agy_dialog.py`:
  - `.why-agy-avatar-row` → `flex-direction: column; align-items: center` (stacks image above text)
  - `.why-agy-illustration` → `max-width: 70px` (shrinks image)
  - `.why-agy-body p` → `font-size: 14px` (reduces body copy from 16px)
  - `[role="dialog"]` → `max-height: 88vh; overflow-y: auto` (safety net)
- **Remaining:** Dialog title ("Hi, I'm Agy 🐾") still renders at 24px on mobile. Target is 20px. Selector is unknown — Streamlit renders the `@st.dialog` title as a `<p>` (not `<h2>`), but the exact selector was not confirmed via DevTools. `[role="dialog"] p:first-of-type` is risky (may match body paragraphs). Needs DevTools inspection to identify the correct selector before adding the title font-size override.
- **Logged:** June 9, 2026

---

### MATTGPT-122
**My Work — Cards view BDD timing failure: test_view_switching_preserves_open_story_detail**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **Issue:** `user_has_opened_specific_story` clicks a Cards view card via Playwright UI click, which must be caught by the `components.html` delegated JS listener to trigger the hidden `st.button`. After `wait_for_streamlit_rerun` (networkidle + 200ms), the listener may not yet be attached — the iframe is still loading — so the click goes unhandled, story detail never opens, and `verify_detail_open` asserts 0 headers.
- **Evidence:** Fix 1 assert surfaced: "Detail panel never opened after card click — DOM had: 0 header(s)". Live app confirmed working (Chrome Claude's direct `element.click()` on the button bypassed the listener entirely). Playwright's UI click goes through the iframe listener path, racing the iframe setup.
- **Fix shape:** After switching to Cards view, wait explicitly for the `components.html` iframe's JS to fire before clicking. Candidate: `wait_for_timeout(1000)` after cards appear, or wait for a zero-height `[data-testid='stCustomComponentV1']` iframe. Alternatively, add a retry loop around the click + wait_for_content.
- **Note:** This test was never green before MATTGPT-105 — it always failed at an earlier step for different reasons. -105 advanced the failure mode to expose the timing issue. Not a -105 regression.
- **Logged:** June 10, 2026
### MATTGPT-120
**CLAUDE.md restructure — Critical Rules fast-reference block + rules-first format throughout**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Goal:** Make CLAUDE.md scannable for new Claude Code sessions. Two parts: (1) Critical Rules fast-reference block at the top — 10-15 non-negotiable imperative rules, readable in 30 seconds; (2) Full restructure — rules-first format throughout, incident narratives moved to memory pointers, overlapping sections consolidated (CSS Rules + Streamlit Patterns → one section). Part 1 is one commit. Part 2 is a dedicated session.
- **Trigger:** Before the next feature sprint after the UI redesign deploy.
- **Logged:** June 9, 2026

### MATTGPT-125
**CLAUDE.md targeted fixes — confirmed bugs + confirmed gaps from June 12 audit**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Source:** 7-angle multi-agent audit of CLAUDE.md, June 12, 2026. 8 findings; 4 confirmed, 4 plausible.
- **Confirmed fixes (no design decision needed):**
  1. Screenshot example has unbound `label` variable (line 292) — crashes with NameError if copied literally. Fix: replace `label` with a concrete string or mark it as a placeholder.
  2. "Effort estimates without consulting padding" heading (line 384) reads as "don't consult anyone about padding" — opposite of intended meaning. Fix: rename to "Effort estimates — no padding" or similar.
  3. Backlog ARCHITECTURE.md flag scope too narrow (line 339) — only watches `ui/pages/`, `ui/components/`, `services/`. Changes to `utils/` and `config/` slip through silently. Fix: add those directories to the watched list.
  4. Backlog sync SHA fallback missing (line 333) — if `<!-- last-backlog-sync: SHA -->` is missing or the SHA is unresolvable, `git log <sha>..HEAD` either errors or diffs the entire history. No fallback defined. Especially critical in Cowork automated-agent context. Fix: add a fallback clause (e.g., prompt Matt if SHA is missing; default to last 20 commits if SHA is unresolvable).
- **Plausible fixes (need Matt's call before Executor touches):**
  5. CSS Rule 8 scope gap (line 77) — DevTools inspection gated on layout/alignment/positioning/sizing only. Color and typography have the same Streamlit wrapper-layer failure mode but are ungated. Fix: broaden the trigger list, or reframe as "any CSS property where the rendered value differs from what source code predicts."
  6. Three contradictory rule pairs — no tiebreaker stated:
     - Pre-flight ("research first, don't propose anything") vs "Execute the work, don't discuss it" (lines 257/261)
     - "Default is build-on-top-of" vs "Provide full file replacements" (lines 258/262)
     - "One go ships the full cycle" vs "Paste validation output and wait — treat as separate gates" (lines 285/275)
     These need precedence rules, not just rewording. Coordinate with MATTGPT-120 restructure.
- **Deferred (Cowork context needed):**
  - Sync anchor mechanism — "since last sync" is ambiguous without a stored reference point; risk of diffing entire history in automated agent context.
  - Agent trigger conditions — what qualifies as "resolved," handling of Decided Against items, HISTORY.md retirement ownership. Needs a dedicated session with Cowork context before writing into CLAUDE.md.
- **Relationship to MATTGPT-120:** Items 1-4 are standalone fixes that can ship before -120. Items 5-6 should be resolved as part of the -120 restructure (they require design decisions that the restructure will formalize).
- **Logged:** June 12, 2026

---

### MATTGPT-127
**Replace hardcoded `ASSESSMENT_MODEL` in `jd_assessor.py` with `get_conf()` env var pattern**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **File:** `services/jd_assessor.py`, `config/constants.py`
- **Logged:** June 12, 2026

**Issue:** `ASSESSMENT_MODEL = "gpt-4o"` is hardcoded at `jd_assessor.py:185` and passed directly to the OpenAI API at lines 205 and 287. Per CLAUDE.md config rules, model names that may change between environments belong as env vars read via `get_conf()`.

**Fix:** `ASSESSMENT_MODEL = get_conf("ASSESSMENT_MODEL") or "gpt-4o"` — one line. Same audit needed for `DEFAULT_CHAT_MODEL` in `constants.py`.

**Note:** `gpt-4o` is the correct value for production (mini produces subpar assessment reasoning). This is a configuration hygiene fix, not a model change.

---

### MATTGPT-126
**Ask Agy landing — input border invisible on page load (CSS injection race)**

- **Status:** Open
- **Priority:** Low
- **Type:** Issue
- **File:** `ui/styles/global_styles.py`
- **Logged:** June 12, 2026

**Symptom:** The Ask Agy landing page text input (`key="landing_input"`) renders without a visible border on initial page load, then the border appears after a brief flash. Intermittent — sometimes caught before CSS injects, sometimes not.

**Root cause:** CSS injection race. Streamlit's emotion CSS sets `border-*-style: none` on all four sides of the input (classes `.st-bh` through `.st-bl`). The override rule in `global_styles.py` (`div[data-testid="stTextInput"] input { border: 2px solid var(--border-color) }`) is injected via `st.markdown`, which runs after initial DOM render. Without `!important`, it loses to the already-applied emotion rules during the render window.

**Also noted:** A stale scoped rule targeting `.st-key-landing_input .st-bz, .st-c0, .st-c1, .st-c2 { border-color: transparent !important }` in the codebase is dead code — emotion class hashes have drifted. Safe to remove.

**Fix:** Add `!important` to the existing border rule in `global_styles.py`:
```css
div[data-testid="stTextInput"] input {
  border: 2px solid var(--border-color) !important;
}
```
`!important` is justified here — explicitly overriding Streamlit's own styling system is the stated purpose of the rule. Remove the stale `.st-bz/.st-c0/.st-c1/.st-c2` dead code in the same pass.

---

### MATTGPT-128
**Displayed-source faithfulness — source cards must substantiate the claims in the answer**

- **Status:** Open
- **Priority:** High
- **Type:** Issue
- **Logged:** June 14, 2026
- **Depends on:** MATTGPT-080 (positioning docs separated from STAR stories), MATTGPT-094 (retrieval diversity)

**Symptom (production-confirmed June 14, 2026):** Agy answered a Fiserv commercial-impact query with accurate numbers ($8.5M, 3% under budget, $500K penalties avoided) but the displayed source cards showed JP Morgan and Norfolk Southern — not the Fiserv STAR story. A recruiter who clicks to verify a claim finds the wrong sources. Observed across multiple probes: "Why Hire Matt" was cited as a source for a largest-team question AND an early-career telecom question, neither of which it substantiates.

**Root cause (design fork — must be resolved before implementation):**
Source cards currently display Pinecone retrieval top-k by score. That is a different set from what the LLM actually grounded the answer in. The likely Fiserv mechanism: the specific numbers came from the "Why Hire Matt" aggregate positioning doc (which summarizes wins across clients and ranks high on almost every query), while the Fiserv STAR story never entered the top-k. The cards honestly showed what was retrieved; the honest set was wrong.

Two design options:
- **Option A — Fix retrieval so the right story enters top-k.** Depends on -094 (retrieval diversity) and -080 (positioning docs separated so they can't crowd out STAR stories). Cards continue to show top-k; faithfulness improves as a consequence. No new display logic.
- **Option B — Display what the answer was grounded in.** Requires the LLM to emit provenance (story IDs it drew from) alongside the answer, then surface those as the source cards. Decouples display from retrieval ranking. More engineering; higher faithfulness ceiling.

**Acceptance criteria:**
- For a set of client-specific queries (Fiserv, RBC, Capital One, AT&T), the named client's STAR story appears in the displayed source cards.
- "Why Hire Matt" and MattGPT positioning docs do not appear as the sole sources for client-specific factual claims.

**Eval to add:**
For each client-specific probe query, assert `client_name in [s.get("Client") for s in displayed_sources]`. Mirrors the client-attribution pattern in Q15.

**Note:** Option A cannot be fully evaluated until -080 ships (STAR stories and positioning docs separated in the index). Do not close this ticket with Option B alone unless Option A is explicitly decided against.

---

### MATTGPT-129
**Content elaboration per era — expand 5 under-documented operational stories**

- **Status:** Open
- **Priority:** High
- **Type:** Action
- **Logged:** June 14, 2026

**Context:** Better retrieval diversity (-094) cannot surface depth that was never written. The five stories below are the strongest under-documented operational arc nodes — era-spread, no CIC, no JP Morgan. Each is tagged by effort mode. The two expand-from-logged ones can proceed immediately; the recovery ones route through elicitation.

**Stories, tagged by effort mode:**

1. **AT&T Southeast CRM Replacement (2005–2009)** — `expand-from-logged`
   Facts already in corpus, compressed: $5M program, 40,000 daily DSL orders protected, $1B annual revenue at risk, foundation for 22-state architecture. Lowest effort; highest arc value; anchors the earliest era with hard numbers.

2. **Fiserv $8.5M White-Label Card Portal recovery** — `expand-from-logged`
   Rich facts already logged: $8.5M, 3% under budget, $255K saved, 47 acceptance criteria, zero critical defects at launch, $45M in transactions processed, $500K in Q4 penalties avoided, $3M contract extension. Cleanest ownable recovery story in the corpus. Write to STAR depth.

3. **AT&T Mobility Service Delivery Platform** — `expand + light recovery`
   Asset is logged; outcome metrics need reconstruction. Elicitation prompt: what was the before/after on service delivery throughput or customer impact?

4. **Launchpad AWS enablement (200+ certifications)** — `expand + recovery`
   Feeds the prototyping/Innovation era (currently 6 stories — thinnest era). Also doubles as People-and-Culture evidence outside the CIC. Elicitation: what was the certification count, timeline, and downstream delivery impact?

5. **Capital One scaling development capacity** — `needs-recovery`
   Two thin stories currently; surfaced as a source in production probes but light on specifics. Full elicitation needed before expansion.

**Acceptance criteria:**
- Each story reaches STAR depth: Situation (context + stakes), Task (scope + constraints), Action (what Matt specifically did), Result (quantified outcome).
- No story references are expanded by paraphrasing existing thin content — only confirmed facts.
- Stories 1 and 2 (expand-from-logged) completed before Stories 3–5 (recovery-dependent).

**Sequencing:** Stories 3–5 are blocked on elicitation. Do not let recovery stories block Stories 1 and 2.

---

### MATTGPT-134
**BDD skip — `test_deeplink_respects_view_mode` — deeplink navigation does not preserve pre-set view mode**

- **Status:** Decided Against (June 24, 2026) — scenario deleted in MATTGPT-144 commit (`77dc1cb`). Confirmed non-feature: deeplinks intentionally start a fresh session with no view persistence. The scenario was testing behavior that doesn't exist and shouldn't.
- **Priority:** Low
- **Type:** Bug
- **Logged:** June 16, 2026

**Context:** Scenario skips at `pytest.skip("Cards view content not found")` in `tests/bdd/steps/test_explore_stories.py` (line 1294). The scenario sets Cards view preference (`Given the user preference is Cards view`), then navigates via deeplink (`When the user navigates to "?story=..."`). The `Then the view should be Cards view` step finds zero `.es-fixed-height-card` elements — the deeplink navigation reverts to Table (the default view) instead of preserving the pre-navigation Cards preference.

**Acceptance criterion:** Either (a) deeplink preserves the active view mode and the scenario passes end-to-end, or (b) the behavior is confirmed intentional (deeplinks always start in Table view) and the scenario is updated to match the confirmed behavior.

---

### MATTGPT-133
**BDD skip — `test_ask_agy_works_from_table_view` — AgGrid row click doesn't reliably expose Ask Agy button in headless Playwright**

- **Status:** Decided Against (June 24, 2026) — scenario deleted in MATTGPT-144 commit (`77dc1cb`). Canvas row-click is undriveable in headless Playwright (st.dataframe Glide Data Grid renders to canvas, not DOM). Redundant with `test_ask_agy_works_from_cards_view` which passes reliably and tests the same user behavior.
- **Priority:** Low
- **Type:** Bug
- **Logged:** June 16, 2026

**Context:** Scenario skips at `pytest.skip("Ask Agy button not found")` in `tests/bdd/steps/test_explore_stories.py` (line 546). The scenario follows: `Given the user is in Table view` → `When the user clicks on a story row`. After the row click, the step looks for `#btn-ask-story` inside the story detail panel, but the element is not reliably found. The AgGrid iframe interaction sequence (frame_locator → `.ag-row` click → detail panel open → Ask Agy button visible) is fragile in headless Playwright. The equivalent Cards-view scenario (`test_ask_agy_works_from_cards_view`) passes reliably.

**Acceptance criterion:** `test_ask_agy_works_from_table_view` passes reliably in isolation and as part of the full BDD suite, with no `pytest.skip` guard.

---

### MATTGPT-131
**BDD selector bug — `test_industry_and_capability_labels_visible_inline_on_mobile` fails in marathon run**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug (test only)
- **Logged:** June 15, 2026

**Context:** `test_industry_and_capability_labels_visible_inline_on_mobile` fails in the full BDD suite marathon run (52 passed, 1 failed). The feature is correct in both local and production at 375px — Chrome Claude confirmed `st-key-facet_industry_v2`, `stWidgetLabel`, `display: flex`, `visibility: visible`, bounding rect 48x14px fully within viewport. The label is present and Playwright-visible in the live app.

**Root cause:** Not yet confirmed. Candidates: (1) the selector hardcodes `facet_industry_v2` but `_widget_version_industry` in a fresh BDD session starts at 0 (`facet_industry_v0`), making the substring match fail; (2) marathon-run resource pressure causes the DOM assertion to fire before the label renders after a 375px viewport resize. Scenario 18 of 54, fires at 31 min into a 31-min run.

**Acceptance criterion:** Scenario passes in isolation (`pytest tests/bdd/steps/test_explore_stories.py::test_industry_and_capability_labels_visible_inline_on_mobile -v`) and in the full suite without flake.

---

### MATTGPT-130
**"practitioners" canonical everywhere — UI, eval golden set, corpus re-embed in lockstep**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Logged:** June 14, 2026

**Context:** "engineers" vs "practitioners" drifts across three coupled surfaces. The UI fix (category_cards.py, about_matt.py) landed June 14, 2026. The eval golden set and embedded corpus still say "engineers," so retrieval keeps returning it and the eval suite is desynced from the UI.

**Surfaces to update in lockstep:**
1. ~~UI suggested prompts and page copy~~ — done June 14, 2026.
2. **Eval golden set** — `tests/` canonical queries that reference "150+ engineers" → "practitioners". Grep: `grep -rn "150+ engineers\|engineers" tests/`.
3. **Corpus content** — any STAR story whose Action/Result text says "engineers" when referring to CIC practitioners. Stories whose text changes must be re-embedded (delete from Pinecone, re-upsert).

**Risk:** Changing only surface 1 leaves eval queries testing a term the UI no longer uses. Changing surfaces 2+3 without re-embedding leaves the index returning "engineers" on practitioner queries.

**Acceptance criterion:** `grep -rn "150+ engineers" ui/ tests/ data/` returns 0 hits (excluding code comments and regex patterns in backend_service.py).

---

### MATTGPT-136
**Dark mode design system audit — --accent-purple not overridden in body.dark-theme**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** June 18, 2026

**Context:** `body.dark-theme` in `global_styles.py` overrides `--accent-purple-text` to `#A78BFA` (lighter purple for dark backgrounds) but does NOT override `--accent-purple` or `--accent-purple-bg`. There are 41 usages of `var(--accent-purple)` across the stylesheet spanning text, borders, opaque backgrounds, and semi-transparent tints. In dark mode all 41 resolve to the same `#8B5CF6` as light mode, which may have contrast issues on dark backgrounds.

**Why deferred:** A blanket override of `--accent-purple` to `#A78BFA` in dark mode affects all 41 usages simultaneously. The usages split into three semantic categories with different risk profiles: (1) text/interactive — genuinely need lighter value for contrast; (2) opaque fills/buttons — design choice, either can work; (3) semi-transparent tints derived from the variable — hue change could look off. Changing blindly risks breaking categories 2 and 3 while fixing 1.

**Fix approach:** Visual audit in dark mode across all pages before adding the override. Document which of the 41 usages fall into each category. Override `--accent-purple` only if a majority of usages are category 1, or introduce a new `--accent-purple-accessible` variable for text contexts.

**Acceptance criterion:** Dark mode visual review complete, override decision documented, no contrast failures on text usages of --accent-purple in dark mode.

---

### MATTGPT-140
**Fix hardcoded model names in backend_service.py and jd_assessor.py**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** June 20, 2026

`constants.py` defines `DEFAULT_CHAT_MODEL = "gpt-4o"` and `DEFAULT_CLASSIFICATION_MODEL = "gpt-4o-mini"` with a usage comment pointing to `get_conf()`. Neither is imported in production callers:
- `backend_service.py` line 952: `model="gpt-4o"` hardcoded
- `backend_service.py` line 681: `model="gpt-4o-mini"` hardcoded
- `jd_assessor.py` line 185: `ASSESSMENT_MODEL = "gpt-4o"` hardcoded locally

`pinecone_service.py` and `semantic_router.py` correctly import `DEFAULT_EMBEDDING_MODEL`. Fix: import `DEFAULT_CHAT_MODEL` in `backend_service.py` and `jd_assessor.py` and replace the string literals. Also remove or repurpose `DEFAULT_CLASSIFICATION_MODEL` — the `classify_query_intent` LLM call it was built for was removed Jan 2026.

**Acceptance criteria:** No model name string literal in any production file outside `config/constants.py`.

---

### MATTGPT-141
**Remove dead ENTITY_GATE_THRESHOLD constant from config/constants.py**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** June 22, 2026

`ENTITY_GATE_THRESHOLD = 0.30` at line 62 of `config/constants.py` is never imported
or referenced outside that file. The Entity Gate was removed Jan 2026; this constant
is a leftover with a misleading history comment ("Lowered from 0.55 to allow narrative
queries"). Fix: delete the constant and its comment.

**Acceptance criteria:** `ENTITY_GATE_THRESHOLD` does not appear in any file in the repo.

---

### MATTGPT-138
**BDD: page teardown invariant + CLS budget guard (MATTGPT-018 regression lock)**

- **Status:** Decided Against
- **Priority:** Medium
- **Type:** Action
- **Logged:** June 19, 2026
- **Decided Against:** The tab-keyed container this guard was written to protect was reverted June 23, 2026 as a null probe (7807a2a). No fix mechanism exists to guard. If a real blep fix lands, file a new guard ticket at that time.

**Context:** The MATTGPT-018 blep root cause was stale Ask Agy DOM bleeding through onto My Work during navigation — two Agy avatars on screen at once because Streamlit reconciled the new page tree onto the old one instead of tearing it down. Fixed by wrapping each page's render in a tab-keyed `st.container` (`_page_slug` key). The `transition: all` animation sweep was a concurrent contributor, fixed by a `transition-property` constraint in `global_styles.py`. Neither fix has a regression guard. This ticket adds two: (1) a deterministic DOM teardown invariant, and (2) a calibrated CLS budget.

**Teardown invariant (implement first — deterministic, no thresholds):**
Navigate Ask Agy → My Work, wait for settle, assert `.st-key-intro_section` count is 0 and no Ask Agy DOM remains. Assert reverse direction. Catches "stale page survived the swap" — the regression that would reappear if the keyed container is stripped. Playwright, real Chromium. Two scenarios in `tests/bdd/features/page_teardown.feature`, steps in `tests/bdd/steps/test_page_teardown.py`. See Chrome Claude spec (June 19, 2026 session) for full scenario and step text.

**CLS budget guard (implement second — calibrated, not a placeholder):**
Cold-load CLS ceiling: 0.25 (observed ~0.24 in DevTools — locks "no worse than today," ratchet down toward 0.10 as CLS is fixed). Transition shift: MEASURE FIRST on post-fix state, then set ceiling just above that reading. Do NOT use the 1.00 placeholder from the spec as a real budget. Install a `PerformanceObserver` for `layout-shift` entries. Two distinct metrics: `read_cls` (filtered, `!hadRecentInput` — matches official CLS) and `read_transition_shift` (all entries including post-click — catches the avatar shift that CLS excludes because it happens within 500ms of a tab click). Helper in `tests/bdd/steps/vitals_helpers.py`, scenarios in `tests/bdd/features/web_vitals.feature`, steps in `tests/bdd/steps/test_web_vitals.py`.

**Honest catches:**
- Teardown tests inspect the settled DOM only — they cannot see the transient flash. The eye-on-the-transition is still the only confirmation the flash is gone.
- `TRANSITION_SHIFT_MAX = 1.00` in the spec is a measurement placeholder, not a real budget. Run the test pre-fix and post-fix, read the printed value, then set the ceiling just above the post-fix number.
- INP is out of scope: currently 0ms, lab INP is noisy, defer until a regression appears.

**Acceptance criteria:**
- `pytest tests/bdd -k "page_teardown"` — 2/2 passing, deterministic
- `pytest tests/bdd -k "web_vitals"` — 2/2 passing with `TRANSITION_SHIFT_MAX` set to a measured (not placeholder) value

---

### MATTGPT-137
**AgGrid bootstrap.min.css render-blocking on Ask Agy → My Work transition**

- **Status:** Open
- **Priority:** Low
- **Type:** Perf
- **Logged:** June 18, 2026

**Context:** `bootstrap.min.css` served by Streamlit Cloud's AgGrid component has `cache-control: public` with no `max-age`, causing 195ms server revalidation round-trips on every Ask Agy → My Work page transition. This contributes to the "blep" (layout shift / flash) on My Work load.

**What was tried:** `<link rel="preload">` tags added to the top of `_CSS` in `global_styles.py`. Failed: Streamlit's `st.markdown()` parser breaks when `<link>` tags precede `<style>` in the injected string — the entire CSS renders as visible text on the page. Reverted (`6b1ea2a`).

**Constraints:** Cache headers on Streamlit Cloud's component server are not configurable from the Python layer. The issue is upstream of the application.

**Potential approaches:** (1) `components.html` injection of a `<link rel="preload">` tag into `window.parent.document.head` — bypasses the st.markdown parser, injects directly into parent document head. (2) Accept as Streamlit Cloud infrastructure limitation and close. (3) Watch for Streamlit Cloud cache header improvements.

**Acceptance criterion:** Either bootstrap.min.css shows as `(from memory cache)` or `(disk cache)` on the Ask Agy → My Work transition DevTools Network tab, or ticket is closed as Decided Against with documented rationale.

---

### MATTGPT-143
**BDD: app_url fixture hardcodes port 8501 with no override**

- **Status:** Parked
- **Priority:** Low
- **Type:** Bug
- **Issue:** `tests/bdd/steps/conftest.py` line 78 returns `"http://localhost:8501"` with no mechanism to override. When two concurrent Streamlit sessions are running (e.g., during parallel feature development), BDD tests silently target the wrong app — tests may pass or fail against stale or unrelated state with no obvious error.
- **Fix:** Replace the hardcoded return with `os.environ.get("STREAMLIT_TEST_URL", "http://localhost:8501")` in `conftest.py`. All test files inherit automatically since they consume `app_url` from the shared fixture.
- **Why parked:** Low-frequency scenario; not blocking current work. Revisit when concurrent Streamlit sessions become a regular workflow.
- **Logged:** June 23, 2026

---

### MATTGPT-142
**BDD: sequential rejection test wait_for_banner not count-aware**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **Issue:** `test_sequential_rejections_swap_chip_sets_per_branch` fails because `wait_for_banner` waits for `.no-match-banner` to exist, not for a new one. After the first rejection renders a banner, subsequent `wait_for_banner` calls return immediately. The `all PERSONAL_CHIPS should be visible` assertion runs before the second rejection has processed, so `get_visible_chip_labels` sees only the first rejection's RULE_CHIPS (highest transcript_banner_N is still the first rejection's index).
- **Root cause:** `wait_for_banner` is not count-aware. `then_banner_displayed` also only checks `.no-match-banner` presence without verifying it is the banner for the current query.
- **Production behavior:** Correct. "Is Matt married?" returns "I'm focused on Matt's professional experience." and PERSONAL_CHIPS render as expected (confirmed manually June 23, 2026).
- **Fix:** In the sequential scenario, count existing `.no-match-banner` elements before submission and wait for that count to increase. Pass expected count into `wait_for_banner`, or add a dedicated `wait_for_nth_banner(n)` helper.
- **Affects:** `tests/bdd/steps/test_ask_mattgpt.py` — `test_sequential_rejections_swap_chip_sets_per_branch`
- **Logged:** June 23, 2026

---

### MATTGPT-145
**Mobile filter breakpoints overlap — r2-label show/hide works by cascade order, not by design**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** June 24, 2026
- **File:** `ui/styles/global_styles.py`

**Issue:** The mobile filter layout uses two overlapping media blocks that fight over the same property on the same elements. `@media (max-width: 767px)` (block ~2189-2325) sets the Client/Role/Domain (r2) filter labels to `display: none` (line ~2223) and injects the field name via `::before` instead (lines ~2227-2253). `@media (max-width: 480px)` (block ~2338-2396) sets those same r2 labels to `display: block` (line ~2376) to show real labels stacked above the dropdowns. Because `max-width: 767px` is an upper bound with no floor, it also matches every width <=480, so at phone widths BOTH rules apply to the same elements simultaneously. Both carry `!important` at equal specificity, so the winner is decided purely by source order. The 480px block currently sits later in the file, so `display: block` wins and the phone rendering is correct.

**Why it matters:** The behavior is correct today but only by accident of file order. There is no specificity margin protecting it (both sides are `!important`). If the stylesheet order shifts, a block moves, or the injection order changes, the 767px `display: none` would win and the r2 labels would silently vanish on phones. Silent failure, no error, surfaces later as a "why did mobile labels disappear" investigation. Validated working June 24, 2026 via Chrome Claude at the effective mobile width (note: Streamlit floors `window.innerWidth` at ~406px in this environment, so 375px and 430px both render at 406px; both the 480px and 767px blocks are active there).

**Intended three-tier design (correct; only the expression is fragile):**
- **>=768px (desktop):** full filter bar, inline labels. No mobile blocks apply.
- **481-767px (mid band):** r2 labels hidden; field name injected as `::before` pseudo-content on the select control (compact, label rides inside the control).
- **<=480px (narrow phone, the 375/406 reality):** r2 labels shown as real labels above the dropdowns; `::before` injection suppressed (block ~2328-2335, `content: none`); controls full-width; padding/gaps/fonts reduced. This is MORE compensation than the mid band, not the same.

The bug is that the mid-band rules have no lower bound, so they leak into the <=480 range where the phone tier explicitly reverses them.

**Fix (behavior-preserving — same rendered output at every width):**
1. Floor the conflicting mid-band rules so they stop reaching the phone range. Move ONLY these from `@media (max-width: 767px)` into a new bounded `@media (min-width: 481px) and (max-width: 767px)` block:
   - r2-label hide (`st-key-r2_{client,role,domain}_v ... stWidgetLabel { display: none }`, ~2220-2223)
   - `::before` field-name injection for r2 (`content: "Client"/"Role"/"Domain"`, ~2227-2246) and its paired "prevent ::before from crushing the value div" rule (~2255-2258)
2. With those floored at 481, they no longer apply at <=480, so the `content: none` suppression block (~2328-2335) becomes redundant — delete it.
3. **Do NOT rebound the rest of the 767px block.** The `stForm` label hide (~2191), the Industry/Capability label sizing (~2203), and the general mobile filter-bar layout are genuine all-mobile-widths compensation that must stay active at 375px. Only the three r2 rules the phone tier reverses get the floor. Mechanically: split block 2189-2325 into two — keep all-mobile rules at `max-width: 767px`, move the r2-hide + `::before`-injection rules into the new `min-width: 481px and max-width: 767px` block.

**Acceptance criteria:**
- r2 labels render `display: block` (real labels above) at <=480px and `display: none` + `::before` injection at 481-767px, with no two `!important` rules applying to the same element at the same width.
- Removing or reordering any single mobile block does not change r2-label visibility at any width (no cascade-order dependency).
- Industry/Capability labels and general mobile filter layout unchanged at 375px.
- Visual parity with current behavior confirmed at <=480 and in the 481-767 band.

**Cross-references:**
- The mobile filter CSS this refactors was added in the explore_stories mobile-fix work (validated and committed June 24, 2026). Do this as the opening move of any future session that touches mobile filter CSS — it makes the cascade safe before edits land on top of it.
- MATTGPT-123, MATTGPT-119 — prior mobile filter work that established the current block structure.

---

### MATTGPT-146
**Professional Narrative stories leak into My Work via filter and search paths**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **Logged:** June 25, 2026
- **File:** `ui/pages/explore_stories.py`

**Issue:** Professional Narrative stories (Category == "Professional Narrative") are Ask Agy content: they exist so Agy can answer questions about Matt in conversation (leadership journey, background, work philosophy, career intent, etc.). They are not projects and were never intended to appear in My Work, which is the project portfolio surface. The current implementation (MATTGPT-098) scoped the exclusion to the default view only (Path 3, no filters active). Filter-active path (Path 3 with `has_filters=True`) and semantic search paths (Path 1 and Path 2) do not apply the exclusion, so a recruiter filtering by Industry or searching My Work can surface "About Matt – My Leadership Journey" as if it were a browseable project.

**Corpus check (confirmed June 25, 2026):** 10 stories carry Category == "Professional Narrative" across 113 total. All 10 are genuinely Ask Agy narrative pieces (leadership journey, leadership philosophy, career intent, transition story, work philosophy, "Why Hire Matt?", etc.). No real projects are miscategorized. The fix is safe to apply.

**Intended behavior:** Professional Narrative category is excluded from the My Work corpus entirely, across all three paths:
- Path 3 default (already done in MATTGPT-098)
- Path 3 filter-active (currently leaks)
- Path 1 semantic search + Path 2 cached search (currently leak)

Professional Narrative stories remain fully available to Ask Agy's Pinecone retrieval — the exclusion is My Work surface only.

**Fix:** Move the exclusion from the per-path default-view check to the top of `render_explore_stories`, filtering `stories` before any path branches. Replace the two inline `[s for s in stories if s.get("Category") != "Professional Narrative"]` guards (lines ~904 and ~1084) with a single pre-filter applied to the `stories` list at the top of the view logic, so all three paths inherit it automatically. One place, one rule.

**Deeplink edge case (decide before implementing):** If someone has a direct `?story=about-matt-my-leadership-journey` deeplink, should My Work resolve it (render the detail) or redirect? Given the intent (narrative stories are not My Work projects), the story should not render as a My Work detail. Simplest behavior: deeplink to a narrative story on My Work silently shows the default view (story not found), consistent with how any unknown story ID resolves. No active redirect needed.

**Acceptance criteria:**
- Filtering My Work by any filter (Industry, Capability, Client, Role, Domain) never returns a Professional Narrative story.
- Searching My Work (semantic search) never returns a Professional Narrative story.
- Default My Work view (no filters, no search) continues to exclude Professional Narrative stories (existing behavior preserved).
- Professional Narrative stories remain retrievable by Ask Agy (Pinecone query path is unaffected).
- BDD: scenario asserting that searching My Work for "leadership journey" or "leadership philosophy" returns zero results (or a no-match banner), not the narrative story.

**Note:** Effort estimate intentionally omitted — small, but requires careful splitting. Validate in the browser after the change, not from source (source-order reasoning is exactly what's fragile here).
