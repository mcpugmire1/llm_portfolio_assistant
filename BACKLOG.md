# MattGPT Backlog
<!-- last-backlog-sync: d2216c0 -->
<!-- BEFORE EDITING: read CLAUDE.md § Backlog Maintenance for status enum, ticket lifecycle, and archiving rules -->
<!-- Next ticket ID: run grep -o 'MATTGPT-[0-9]*' BACKLOG.md | sort -t- -k2 -n | tail -1 to find current max, then add 1 -->

Work state for the MattGPT project. The matrix below is the scannable view. Detail blocks for each item follow, linked by ID. Completed items live in `CHANGELOG.md`. Architectural decisions live in `docs/ADR.md`. Current system state lives in `ARCHITECTURE.md`.

---

## Value Prioritized Roadmap (updated 2026-08-28)

**NOW**
1. **-129 stories 3-5** — Capital One elicitation, Launchpad timeline and downstream impact, Lean Innovation depth. Blocked on elicitation.
2. **-128** — Source faithfulness. Never run. Last unverified thing on the runway; gates Role Match since Role Match is evidence-backed ratings.

**NEXT** — Role Match, once the runway clears
-160 (extractor dropping qualifiers on 7 of 23) · -173 (malformed and comp-only JD behavior) · -159 (sequential gpt-4o loop) · -014 (34 skipped integration scenarios) · -089 (location, work-model, availability) · -012 (Private View Phase 4) · -081 (corrective actions by asset type) · -099 (comp handling) · -017 (logging scenarios)

**LATER — tier 1:** real defects with known fixes
-177 (bound violation) · -190 (tokenizer divergence) · -187 (max_per_client) · -166 (arc story reframe) · -196 (defensive skips masking regressions) · -180 (fixture blind spot) · -063 (wrong-person queries) · -188 (off-topic people) · -195 (incident vocabulary routing hygiene) · -146 (PN leaks into My Work) · -202 (id-skip predicate divergence) · -206 (eval suite stochastic Q28)

**LATER — tier 2:** corpus work
Register passes batched as one edit cycle: -154, -095, -097, -015, -130
New stories: -078, -091, -155, -022 (-181 closed Aug 19)
Meta: -079, -156, -096

**LATER — tier 3:** blocked or dependent
-168 (needs Top Score distribution) · -077 (re-measure after -181) · -171 (coupled to -190) · -185 (negation)

**LATER — tier 4:** hygiene
Dead code: -176, -183, -199, -201 · Hidden error: -204
BDD flakes: -122, -131, -142, -145, -197, -198, -205
Wrong-assertion test: -203 · -209 (drift guard searches wrong scope)
Small refactors: -140, -153, -086, -062, -082, -083, -084, -150, -060, -217 (pronoun grammar in substitution)
BDD structure: -213 (shared step definitions)
Correctness audit: -214 (parameters, comments, constants, copied blocks)
Infrastructure: -035, -039, -040, -045

---

## Matrix

| ID | Title | Status | Priority | Type | Logged |
|---|---|---|---|---|---|
| [MATTGPT-012](#mattgpt-012) | Role Match — Phase 4: Private View | In Progress | High | Action | Apr 2026 |
| [MATTGPT-014](#mattgpt-014) | Audit + split skipped Role Match BDD scenarios (BDD for structure, evals for content) | Open | High | Action | Apr 28, 2026 |
| [MATTGPT-015](#mattgpt-015) | JPM Payments IQ Differentiation | Open | High | Action | Mar 2026 |
| [MATTGPT-017](#mattgpt-017) | Wire skipped Role Match logging BDD scenarios (Playwright click + mocked Sheets write) | Open | Medium | Action | Apr 28, 2026 |
| [MATTGPT-022](#mattgpt-022) | Data Quality Cleanup Journey Story | Open | Medium | Action | Mar 2026 |
| [MATTGPT-035](#mattgpt-035) | Eval Modernization — Semantic Scoring | Open | Low | Spike | Pre-2026 |
| [MATTGPT-039](#mattgpt-039) | Automated Regression Detection (GitHub Actions) | Open | Medium | Action | Apr 29, 2026 |
| [MATTGPT-040](#mattgpt-040) | Eval Coverage Gaps — Follow-up Queries | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-045](#mattgpt-045) | Analytics Dashboard | Open | Low | Action | Apr 29, 2026 |
| [MATTGPT-060](#mattgpt-060) | BDD coverage gap — assert post-navigation page state, not just navigation | Open | Medium | Action | May 12, 2026 |
| [MATTGPT-062](#mattgpt-062) | Semantic router cache silently uses stale embeddings when VALID_INTENTS changes | Open | Medium | Refactor | May 14, 2026 |
| [MATTGPT-063](#mattgpt-063) | Wrong-person queries with names outside nonsense regex produce confused-context RAG answers | Open | Medium | Issue | May 14, 2026 |
| [MATTGPT-077](#mattgpt-077) | Subject-pronoun + noun-overlap retrieval contamination — "Matt + X" pulls MattGPT/Strangler Fig stories when X overlaps their vocabulary | Open | Medium-High | Issue | May 19, 2026 |
| [MATTGPT-078](#mattgpt-078) | New corpus story — "AI Enablement Before It Had a Name" (resume Option E retrieval anchor) | Open | Medium | Action | May 21, 2026 |
| [MATTGPT-079](#mattgpt-079) | Role Match coverage gaps — corpus story anchors needed (meta-ticket) | Open | Medium | Action | May 21, 2026 |
| [MATTGPT-081](#mattgpt-081) | Role Match engine — corrective-actions output by asset type (story / resume / LinkedIn / positioning / network / real skill) | Open | Medium | Enhancement | May 21, 2026 |
| [MATTGPT-082](#mattgpt-082) | Q15 eval assertion is over-specified — checks literal client name presence rather than response correctness | Open | Medium | Refactor | May 22, 2026 |
| [MATTGPT-083](#mattgpt-083) | Spinner inconsistency — Explore Stories doesn't show thinking indicator for rejected queries (Ask MattGPT does) | Open | Medium | Issue | May 23, 2026 |
| [MATTGPT-084](#mattgpt-084) | Ask MattGPT BDD scenarios — chip-click + low_confidence banner-render timing flakes under full-suite load | Open | Medium | Issue | May 23, 2026 |
| [MATTGPT-086](#mattgpt-086) | Query logger — add environment annotation column + filter dev/test traffic out of production analytics | Open | Low | Issue | May 23, 2026 |
| [MATTGPT-089](#mattgpt-089) | Role Match — parse location, work-model, availability as distinct filter class | Open | High | Issue | May 28, 2026 |
| [MATTGPT-091](#mattgpt-091) | Add a credible failure story to the corpus (sibling to -022 / -078 pattern) | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-095](#mattgpt-095) | Anti-consulting bias in story framing — corpus reads "consulting" as default register when it shouldn't | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-096](#mattgpt-096) | Methodology context dropped during synthesis — TDD/BDD and ways-of-working substance gets compressed out of metric claims (hypothesis to verify) | Open | Medium | Issue | May 28, 2026 |
| [MATTGPT-097](#mattgpt-097) | Career-intent framing refresh — corpus predates current role taxonomy; refresh framing AND tighten register | Open | Medium | Action | May 28, 2026 |
| [MATTGPT-099](#mattgpt-099) | Role Match — assess and decide comp handling on JDs that include comp expectations | Open | Medium | Investigation + Action | May 29, 2026 |
| [MATTGPT-122](#mattgpt-122) | My Work — Cards view BDD timing: test_view_switching_preserves_open_story_detail fails (components.html iframe listener not attached at click time) | Open | Low | Issue | June 10, 2026 |
| [MATTGPT-126](#mattgpt-126) | Ask Agy landing — input border flash on load; emotion-class guard retained as insurance | Parked | Low | Issue | June 12, 2026 |
| [MATTGPT-128](#mattgpt-128) | Displayed-source faithfulness — source cards must substantiate the claims in the answer | Open | High | Issue | June 14, 2026 |
| [MATTGPT-129](#mattgpt-129) | Content elaboration per era — expand 5 under-documented operational stories | Open | High | Action | June 14, 2026 |
| [MATTGPT-130](#mattgpt-130) | "practitioners" canonical everywhere — UI, eval golden set, corpus re-embed in lockstep | Open | Medium | Action | June 14, 2026 |
| [MATTGPT-131](#mattgpt-131) | BDD selector bug — `test_industry_and_capability_labels_visible_inline_on_mobile` fails in marathon run | Open | Low | Bug | June 15, 2026 |
| [MATTGPT-140](#mattgpt-140) | Fix hardcoded model names in backend_service.py and jd_assessor.py — use constants.py | Open | Low | Refactor | June 20, 2026 |
| [MATTGPT-142](#mattgpt-142) | BDD sequential rejection test: wait_for_banner is not count-aware, assertion runs before second rejection renders | Open | Low | Bug | June 23, 2026 |
| [MATTGPT-143](#mattgpt-143) | BDD app_url fixture hardcodes port 8501 with no env-var override | Parked | Low | Bug | June 23, 2026 |
| [MATTGPT-145](#mattgpt-145) | Mobile filter breakpoints overlap — r2-label show/hide depends on !important cascade order, not design | Open | Low | Refactor | Jun 24, 2026 |
| [MATTGPT-146](#mattgpt-146) | Professional Narrative stories leak into My Work via filter and search paths — must be excluded from all My Work paths | Open | Medium | Bug | Jun 25, 2026 |
| [MATTGPT-150](#mattgpt-150) | MATTGPT-144 test fallout — decouple BDD assertions from display copy and stranded AgGrid selectors | Open | Medium | Refactor / Test | July 1, 2026 |
| [MATTGPT-152](#mattgpt-152) | Move debug output from UI sidecar to terminal log only | Parked | Low | Refactor | July 16, 2026 |
| [MATTGPT-153](#mattgpt-153) | Q64 eval stochastic — replace phrase-cluster with concept-cluster robust to story-selection variance | Open | Low | Refactor / Test | July 16, 2026 |
| [MATTGPT-154](#mattgpt-154) | Operational-breadth tagging pass — surface operational ownership into all corpus stories where it's genuinely true | Open | Medium | Action | July 16, 2026 |
| [MATTGPT-155](#mattgpt-155) | New corpus story — sell-side commercial story (HSBC-anchored): pricing/costing, resourcing, outcome-based contracting | Open | Medium | Action | July 29, 2026 |
| [MATTGPT-156](#mattgpt-156) | Vendor commercial/spend management gap — decide whether corpus-zero on invoice/rate-card/procurement is a real claim or honest gap | Open | Low | Investigation | July 29, 2026 |
| [MATTGPT-159](#mattgpt-159) | Role Match performance — parallelize per-requirement assessor calls; sequential gpt-4o loop is the bottleneck | Open | Medium | Performance | July 31, 2026 |
| [MATTGPT-160](#mattgpt-160) | JD extractor clause-dropping — 7 of 23 requirements on demo JD lose qualifiers during extraction | Open | Medium | Bug | July 31, 2026 |
| [MATTGPT-166](#mattgpt-166) | Arc stories with placeholder client metadata excluded from entity-scoped queries -- tradeoff, not defect | Open | Medium | Issue | August 3, 2026 |
| [MATTGPT-167](#mattgpt-167) | Widen entity detection to Project and Place — specification complete, no confirmed failing case currently | Parked | Medium | Action | August 3, 2026 |
| [MATTGPT-168](#mattgpt-168) | Slot 1 is amplified without regard to margin -- tie or near-tie at slot 1 gets 80% of the answer | Open | High | Bug | August 5, 2026 |
| [MATTGPT-171](#mattgpt-171) | Phrase-aware matching: stopword-only phrases invisible to token-overlap scorer at any W_KW weight | Open | Low | Investigation | August 8, 2026 |
| [MATTGPT-173](#mattgpt-173) | Role Match JD validation: no defined behavior for malformed or comp-only JD inputs | Open | Medium | Issue | August 8, 2026 |
| [MATTGPT-176](#mattgpt-176) | Dead code: zero-caller function, 200-line commented block, duplicate typed-alias map | Open | Low | Refactor | August 11, 2026 |
| [MATTGPT-177](#mattgpt-177) | token_overlap_ratio bound violation — repeated in-vocab tokens inflate ratio above 1.0; docstring example independently wrong | Open | Medium | Bug | August 11, 2026 |
| [MATTGPT-180](#mattgpt-180) | Test fixture blind spot: test_formatting.py, test_filters.py, test_scoring.py build on phantom schema and pass against it | Open | High | Bug | August 11, 2026 |
| [MATTGPT-183](#mattgpt-183) | has_metric filter dead -- nothing in UI sets it to True; remove rather than fix | Open | Low | Refactor | August 13, 2026 |
| [MATTGPT-185](#mattgpt-185) | Query negation unsupported -- "outside of MattGPT" returns MattGPT stories | Open | Medium | Enhancement | August 13, 2026 |
| [MATTGPT-187](#mattgpt-187) | diversify_results max_per_client parameter is documented but never implemented | Open | Medium | Bug | August 13, 2026 |
| [MATTGPT-188](#mattgpt-188) | Semantic router accepts off-topic queries about other people | Open | Medium | Bug | August 13, 2026 |
| [MATTGPT-190](#mattgpt-190) | Tokenizer character-set divergence: _tokenize keeps +#-. while token_overlap_ratio splits on non-\w | Open | Medium | Bug | August 16, 2026 |
| [MATTGPT-195](#mattgpt-195) | Production incident queries scatter across six intent families -- delivery family has no incident vocabulary | Open | Medium | Bug | August 16, 2026 |
| [MATTGPT-196](#mattgpt-196) | Defensive pytest.skip in test_explore_stories.py masks UI regressions as green runs | Open | Medium | Bug | August 16, 2026 |
| [MATTGPT-197](#mattgpt-197) | BDD suite-order flake: test_tapping_filters_toggle_shows_row_2_on_mobile fails in marathon, passes in isolation | Open | Low | Bug | August 17, 2026 |
| [MATTGPT-198](#mattgpt-198) | BDD suite-order flake: test_clicking_a_nav_label_still_routes_to_its_surface_no_regression fails in marathon, passes in isolation | Open | Low | Bug | August 17, 2026 |
| [MATTGPT-199](#mattgpt-199) | Entity-name-untrimmable hole in MATTGPT-074 content-kw gate: AT&T tokenizes to empty set, strip never fires | Open | Low | Bug | August 17, 2026 |
| [MATTGPT-201](#mattgpt-201) | Entity pin for Client/Employer uses blend order while code comment and debug label state pc-order intent | Open | Low | Refactor | August 17, 2026 |
| [MATTGPT-202](#mattgpt-202) | id-skip predicate copied verbatim in app.py and corpus_loader.py -- divergence risk, no shared source | Open | Medium | Bug | August 18, 2026 |
| [MATTGPT-203](#mattgpt-203) | Chip grid disable test asserts the wrong mechanism | Open | Low | Bug (Test) | August 18, 2026 |
| [MATTGPT-204](#mattgpt-204) | Two Explore Stories blank-state defects: corpus-load failure silent; Table view missing empty-state guard | Open | Low | Bug | August 18, 2026 |
| [MATTGPT-205](#mattgpt-205) | BDD marathon flake: test_error_state_extraction_failure fails in marathon, passes in isolation | Open | Low | Bug (Test) | August 19, 2026 |
| [MATTGPT-206](#mattgpt-206) | Eval suite ~1-in-70 stochastic flap; Q28 confirmed non-deterministic | Open | Medium | Bug (Test) | August 19, 2026 |
| [MATTGPT-209](#mattgpt-209) | MATT_DNA drift guard passes for wrong reason: employer check searches whole string, not Career Arc block | Open | Low | Bug (Test) | August 24, 2026 |
| [MATTGPT-210](#mattgpt-210) | Ask Agy landing page suggestion chips are static; stories like STRATCOM invisible on career queries | Open | Low | Enhancement | August 24, 2026 |
| [MATTGPT-213](#mattgpt-213) | BDD suite: navigation step definitions duplicated across modules; no shared step module | Open | Low | Refactor / Test | August 26, 2026 |
| [MATTGPT-214](#mattgpt-214) | Targeted audit: parameters never referenced, comments asserting absent behavior, constants unused, copied blocks with stale variable names | Open | Low | Refactor | August 26, 2026 |
| [MATTGPT-217](#mattgpt-217) | `_substitute_matt_subject` produces subject pronoun in object position ("reported to he at the CIC") | Open | Low | Bug | August 26, 2026 |

---

## Decided Against

> **Read only — do not add tickets here directly.**
> Rows are moved here from the Active Matrix above when a ticket's status changes to Decided Against. New tickets always start in the Active Matrix. The AI agent (or Matt) moves a row here as part of the status transition. See CLAUDE.md § Backlog Maintenance for the full lifecycle.

| ID | Title | Status | Priority | Type | Logged |
|---|---|---|---|---|---|
| [MATTGPT-010](#mattgpt-010) | Cross-Browser Testing | Decided Against | Low | Action | Pre-2026 |
| [MATTGPT-016](#mattgpt-016) | Semantic Router — Wrong-Person Query Detection | Decided Against | High | Issue | Apr 2026 |
| [MATTGPT-020](#mattgpt-020) | Simplify backend_service.py | Decided Against | Medium | Refactor | Pre-Jan 2026 |
| [MATTGPT-023](#mattgpt-023) | LLM Meta-Commentary on Q20 (Stochastic) | Decided Against | Low | Issue | Apr 2026 |
| [MATTGPT-024](#mattgpt-024) | Clarify Hybrid Scoring | Decided Against | Low | Refactor | Pre-2026 |
| [MATTGPT-025](#mattgpt-025) | Add Error Handling Tests | Decided Against | Low | Action | Pre-2026 |
| [MATTGPT-026](#mattgpt-026) | Clarify Layer Ownership | Decided Against | Low | Refactor | Pre-2026 |
| [MATTGPT-027](#mattgpt-027) | Quarterly Intent Review | Decided Against | Low | Action | Jan 2026 |
| [MATTGPT-028](#mattgpt-028) | Share Link Copy Functionality | Decided Against | Low | Issue | Pre-2026 |
| [MATTGPT-029](#mattgpt-029) | Low-Confidence Banner Edge Cases | Decided Against | Low | Issue | Pre-2026 |
| [MATTGPT-031](#mattgpt-031) | Semantic Router Error Path Coverage | Decided Against | Low | Action | Pre-2026 |
| [MATTGPT-032](#mattgpt-032) | LLM Response Broken Markdown | Decided Against | Low | Issue | Pre-2026 |
| [MATTGPT-036](#mattgpt-036) | Entity Cluster Promotion Override | Decided Against | — | — | Pre-2026 |
| [MATTGPT-037](#mattgpt-037) | Score Gap Override (Generic-Above-Named) | Decided Against | — | — | Pre-2026 |
| [MATTGPT-038](#mattgpt-038) | Centralize Constants (Duplicate of legacy #7) | Decided Against | — | — | Pre-2026 |
| [MATTGPT-041](#mattgpt-041) | 5P Dimensional Drill-Down | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-042](#mattgpt-042) | 5P Pattern Taxonomy | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-043](#mattgpt-043) | Humane Framing — Intent-to-Tone Mapping | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-044](#mattgpt-044) | Pattern Insights — Structured Templates | Decided Against | Low | Spike | Apr 29, 2026 |
| [MATTGPT-046](#mattgpt-046) | Latency Benchmarks | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-047](#mattgpt-047) | Cost Tracking | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-048](#mattgpt-048) | Portfolio Integration (Notion, LinkedIn sync) | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-049](#mattgpt-049) | Job Fit Broader Scope (cover letter export, LinkedIn auto-extract) | Decided Against | Low | Action | Apr 29, 2026 |
| [MATTGPT-050](#mattgpt-050) | Dynamic Intent Expansion | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-051](#mattgpt-051) | User Feedback Loop — Closed-Loop Retraining | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-052](#mattgpt-052) | A/B Testing on Thresholds | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-053](#mattgpt-053) | A/B Testing Framework | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-054](#mattgpt-054) | Query Rewriting and Spell-check | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-055](#mattgpt-055) | PWA Capabilities | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-056](#mattgpt-056) | True Wireflows (Miro) | Decided Against | — | — | Apr 29, 2026 |
| [MATTGPT-058](#mattgpt-058) | Replace dark-theme setInterval polling with MutationObserver | Decided Against | Low | Refactor | May 12, 2026 |
| [MATTGPT-059](#mattgpt-059) | Add Theme-based prefilter dimension to category cards | Decided Against | Low | Spike | May 12, 2026 |
| [MATTGPT-070](#mattgpt-070) | Ask MattGPT — Suggestion button cursor pointer | Decided Against | Low | Issue | May 15, 2026 |
| [MATTGPT-075](#mattgpt-075) | Developer debug surfaces leak to user-facing UI (sidebar print, telemetry badge) | Decided Against | Medium | Issue | May 18, 2026 |
| [MATTGPT-090](#mattgpt-090) | System prompt — decline cleanly on comp / off-scope queries (no silent fallback) | Decided Against | Medium | Action | May 28, 2026 |
| [MATTGPT-103](#mattgpt-103) | Agy intro line — resolve "20+ years of work" inconsistency with stats bar (Years tile dropped) | Decided Against | Low | Refactor | May 30, 2026 |
| [MATTGPT-115](#mattgpt-115) | Lock icon — browser console warning: password field not in native form (st.popover portal breaks form containment) | Decided Against | Low | Issue | June 6, 2026 |
| [MATTGPT-121](#mattgpt-121) | Why Agy dialog — mobile layout fix (375px viewport); one rule remaining: title font-size 24px → 20px, selector confirmed | Decided Against | Low | Bug | June 9, 2026 |
| [MATTGPT-127](#mattgpt-127) | Replace hardcoded `ASSESSMENT_MODEL` in `jd_assessor.py` with `get_conf()` env var pattern | Decided Against | Low | Refactor | June 12, 2026 |
| [MATTGPT-133](#mattgpt-133) | BDD skip — `test_ask_agy_works_from_table_view` skips when AgGrid iframe row interaction doesn't open detail panel | Decided Against | Low | Bug | June 16, 2026 |
| [MATTGPT-134](#mattgpt-134) | BDD skip — `test_deeplink_respects_view_mode` skips because deeplink navigation does not preserve pre-set view mode | Decided Against | Low | Bug | June 16, 2026 |
| [MATTGPT-136](#mattgpt-136) | Dark mode design system audit — --accent-purple not overridden in body.dark-theme | Decided Against | Low | Refactor | June 18, 2026 |
| [MATTGPT-138](#mattgpt-138) | BDD: page teardown invariant + CLS budget guard (MATTGPT-018 regression lock) | Decided Against | Medium | Action | June 19, 2026 |
| [MATTGPT-147](#mattgpt-147) | Stale `@pytest.mark.skip` on `test_mobile_desktop_only_message` — decorator predates step def | Decided Against | Low | Bug | July 1, 2026 |
| [MATTGPT-148](#mattgpt-148) | `.main` selector sweep — 36 dead selectors in `global_styles.py` need swapping to `.stMain` | Decided Against | Low | Refactor | July 1, 2026 |
| [MATTGPT-149](#mattgpt-149) | Rejection bubble dark mode — `[class*='_rejection_bubble']` uses `var(--banner-info-bg)` with no dark mode override | Decided Against | Low | Bug | July 1, 2026 |
| [MATTGPT-164](#mattgpt-164) | Wrong-person queries reach retrieval — Satya Nadella passes all gates, returns Accenture content | Decided Against | High | Bug | August 3, 2026 |

| [MATTGPT-172](#mattgpt-172) | CIC-cluster consolidation: CIC is 52/114 (46%) of corpus; Division concentration causes cluster-drift dominance on broad queries | Decided Against | Medium | Action | August 8, 2026 |
| [MATTGPT-179](#mattgpt-179) | Dead formatters in formatting.py — both entrances orphaned, phantom schema in unreachable code; consider folding into MATTGPT-176 | Decided Against | Low | Refactor | August 11, 2026 |
| [MATTGPT-184](#mattgpt-184) | ask_mattgpt/utils.py module audit -- six dead functions, four duplicating live helpers elsewhere | Decided Against | Low | Refactor | August 13, 2026 |
| [MATTGPT-191](#mattgpt-191) | test_synthesis_pool_size fails because SYNTHESIS_THEMES is never populated in test context | Decided Against | Low | Bug | August 16, 2026 |
| [MATTGPT-192](#mattgpt-192) | Semantic router returns out_of_scope for entity-scoped queries (amex) | Decided Against | Medium | Bug | August 16, 2026 |
| [MATTGPT-193](#mattgpt-193) | LLM-output tests are stochastic at temperature 0.4 | Decided Against | Low | Test | August 16, 2026 |
| [MATTGPT-194](#mattgpt-194) | slugify defined three times across three modules -- consolidate to one | Decided Against | Low | Refactor | August 16, 2026 |
| [MATTGPT-200](#mattgpt-200) | top_per_theme=3 caps synthesis pool when all entity stories share one Theme; AT&T returns 3 of 6 stories | Decided Against | Medium | Bug | August 17, 2026 |

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

### Active Tickets

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

### MATTGPT-022
**Data Quality Cleanup Journey Story**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Issue:** The March 2026 data quality work (CIC pairing, IQ differentiation, Situation enrichment across 85+ stories) is a compelling story about systematic data improvement for AI systems. Not yet captured as a STAR story.
- **Fix:** Write as STAR story for portfolio. Covers pattern recognition, data quality discipline, measurable impact on retrieval accuracy.
- **Logged:** March 2026

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
- **Priority review note (July 29, 2026):** Warranted before any next VALID_INTENTS change. That change happened (MATTGPT-163, 9a05af0, August 26, 2026) and followed the manual delete-and-rebuild workflow cleanly -- footgun did not fire. Underlying fix still worth doing to remove the remember-to-do-it step.
- **Out of scope for MATTGPT-016:** The current wrong-person fix follows the existing "delete and regenerate" workflow (the documented contract) and commits a regenerated cache. This ticket addresses the underlying fragility, not the immediate fix.
- **Status note (July 29, 2026):** Staleness risk confirmed active -- no longer hypothetical. VALID_INTENTS changes occurred during July 2026 -080 validation sessions. Priority review warranted before next VALID_INTENTS change.
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
- **Design connection to MATTGPT-077 (August 8, 2026):** The Phase 1 strip work in -077 built `_substitute_matt_subject`, a token-level detector that classifies each query token as "Matt-or-a-variant" or "not." That detector is one branch away from -063's trigger: asking "is this a name token that isn't Matt?" is the same detection logic with a different branch outcome -- instead of substituting, emit a mismatch response ("I only have Matt's work; did you mean...?"). When -063 is picked up, `_substitute_matt_subject`'s token layer is the right starting point. Do not build a separate name detector; extend what's already there. This is not scope for -077's ship -- it's a handoff note for whoever opens -063 next.
- **Related:** MATTGPT-016 (Decided Against -- same root concern, wrong fix shape), MATTGPT-021 (diversify_results pinning), MATTGPT-077 (strip implementation whose token layer is the starting point for -063's fix).
- **Logged:** May 14, 2026

---


### MATTGPT-077
**Subject-pronoun + noun-overlap retrieval contamination — "Matt + X" pulls MattGPT/Strangler Fig stories when X overlaps their vocabulary**

- **Status:** Open
- **Priority:** Medium-High
- **Type:** Issue
- **Execution split (May 28, 2026; updated August 12, 2026 — see Value Prioritized Roadmap at top of BACKLOG.md):**
  - **Phase 1 — Query-side mitigation (done, Green at 627f6f4).** Strip "Matt" from embedded queries on technical-noun shapes; preserve "Matt" in the prompt sent to the LLM. Cheap, reversible, sufficient for moderate-overlap nouns (monolith, MVP). NOT sufficient for severe-overlap nouns (refactoring). Maps to Fix-path option 2 below.
  - **Phase 2 — Cluster cull / rewrite (NOW).** Scope determined by P5/P8 Step 0 measurement. MATTGPT-182 closed (275ff1f, August 15) -- re-baseline run August 13; P5/P8 still LEAD (findings in post-182 section below). Phase 2 is unblocked. **Benchmark artifact (August 26, 2026):** `probe_163_substitution_impact.py` (committed b9cd2ef) measures substitution impact across five queries. Jaccard similarity 0.25 to 0.67; the direct-reports query is the strongest case: seven of ten portfolio-narrative stories without substitution, ten of ten org-delivery stories with it. Re-runnable as a before-and-after benchmark when Phase 2 or Phase 3 lands.
  - **Phase 3 — Full hybrid retrieval.** BM25 + semantic; keyword weighting on "client", "Fortune 500", "enterprise" pushes named-client stories above MattGPT for queries containing those keywords. Handles severe-overlap nouns. **Lowest empirical risk path** given the May 16 story-side rewrite backfire (see Finding 3 caveat). Also addresses MATTGPT-061 residual. Maps to Fix-path option 3 below. **Note (August 13, 2026): BM25 cannot reach P5/P8's specific problem.** P5 and P8 query "platform refactoring." Rearchitecting Live Railroad Systems does not contain "refactoring" -- its title says "Rearchitecting" and its prose uses "rearchitecture" and "refactor." No enterprise story whose subject is restructuring uses the query's exact vocabulary. A term-matching mechanism has nothing to match. BM25 plus a stemmer would address the no-stemming limitation in MATTGPT-178 and would help queries whose vocabulary the corpus does carry -- but Phase 3 should not be scoped as the fix for P5/P8.
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

  **Finding 3 caveat (August 13, 2026):** The density numbers above predate the 22cede2 corpus edit and were measured against `build_embedding_text` output rather than raw JSONL fields. Re-measure before using them to scope any corpus rewrite.
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
  - **MATTGPT-073** — cross-query session-state fix (closed). -077 is independent of session state (reproduces on cold sessions).
  - **MATTGPT-071** — chip set validation; the locked chip set was rescued from -077's trap during May 19 production spot-checks.
- **Discovered during:** May 19, 2026 MATTGPT-071 chip prompt validation against production. The rule:* chip prompt *"How does Matt modernize monoliths into microservices?"* produced 3/3 contaminated responses with Strangler Fig contamination. Investigation expanded to characterize the pattern across 8 probe queries.
- **New evidence (July 29, 2026):** Narrative/MattGPT over-concentration observed again across 18 example queries captured during the -080 validation sessions. Query list to be attached when available. Confirms the pattern is not limited to the original 8 probe queries.
- **Trace session findings (August 3, 2026):**
  - Why Hire Matt is a broad career-shape attractor independent of name. Rank 1 on "What did Matt build at Accenture" (entity filter applied, score 0.601) and "Has Matt directly managed engineering teams?" (no entity, score 0.521). Confirms the narrative-cluster dominance pattern on broad management queries. Primary home for this finding: MATTGPT-169 (positioning-story attractor, different mechanism from -077 Findings 1-3).
  - Building CIC surfaces in entity-triggered synthesis (named directly, rank 2) but is absent from the pool entirely on broader management queries. Not diversified out -- not retrieved. Distinct from the CIC over-concentration finding in MATTGPT-094 (closed); that was CIC dominating, this is CIC missing on a class of query where it would be relevant.
  - Diversification behaves better on natural-register queries than earlier imperative traces suggested. On a management query it promoted AT&T, Capital One, and Norfolk Southern over reflective stories. The reflective-story dominance pattern was partly an artifact of unnatural phrasing in the earlier probes.
- **Probe resolutions (August 8, 2026):**
  - **Q1 closed.** Revenue Competencies story edit plus W_KW re-enable (commit f5641e7) together resolved the Q1 retrieval contamination. The story edit reduced vocabulary overlap; W_KW adding keyword signal moved specific-term stories above the contaminating cluster for this probe. No further action on Q1.
  - **Q4 closed as probe-phrasing defect.** The failing assertion was testing a bare "service boundaries" phrasing that does not represent realistic query shape. Probe was producing a false signal, not a real retrieval problem. Residue: add a grep to the eval suite for bare "service boundaries" queries and update or remove any that lack a realistic context clause. Suite-hygiene item, not a retrieval fix.
- **Scope note -- stranger-name queries (August 8, 2026):** The Phase 1 strip (`_substitute_matt_subject`) does not fix, and does not worsen, wrong-person query behavior. "How does Nadella approach microservices" retrieves Matt's stories and answers fluently with nothing flagging the mismatch -- the strip is unaffected either way, because the embedded query still returns semantically relevant Matt stories regardless of whether "Matt" is present. This was briefly characterized as benign; that characterization was wrong. Retrieval producing a coherent answer about the wrong person, with nothing signaling the mismatch, is a trust defect -- the same family as the confidence problems this work addresses elsewhere. It is MATTGPT-063's live defect, not a side effect of the strip, and out of -077's scope. The strip neither fixes nor worsens it.
- **Step A probe results (August 11, 2026):**
  - **"Matt?" -- pre-existing contamination, now filed as MATTGPT-174.** Router scored 0.797 valid, family=background. Confidence gate passed at pc 0.291 (high). Pool flat 0.20–0.29; 5 of 10 pool hits and 4 of 7 LLM stories self-referential Independent Project stories. Router measures on-topic-ness -- a bare name is maximally on-topic with zero retrievable intent, so the router correctly routes and the confidence gate becomes the only protection. Gate does not catch it: 0.291 clears CONFIDENCE_HIGH=0.25 (noise-floor calibration, not match-strength calibration). Filed as MATTGPT-174.
  - **"he?" -- gate-caught cleanly.** Router scored 0.255 invalid, confidence none, QUERY_REJECTED low_pinecone. No contamination.
  - **Structural protection confirmed:** "Matt?" routes to family=background, which is in the never-strip list. The substitution gate cannot produce a bare-pronoun degenerate query in production from this path. The never-strip list is the protection here, not the confidence gate.
  - **W_KW property (context for MATTGPT-174, not a -077 defect):** Single-token queries trivially max keyword overlap (kw=1.0 on "Matt?"), which elects the lead story on degenerate queries. This is a degenerate-query artifact of flat keyword scoring, not a retrieval-quality regression from the W_KW re-enable. Recorded here for provenance; the confidence ticket owns the design response.
  - **Belt-and-suspenders correction (August 11, 2026 -- supersedes "structural protection confirmed" above):** Gate-caught behavior demonstrated for "he?" (router invalid 0.255, confidence none, QUERY_REJECTED low_pinecone). The family-gate belt -- "Matt?" routes to background, a never-substitute family -- is demonstrated for that single string only. Router stability across bare-name variants (Matt, matt?, Matthew?, Pugmire?) is undemonstrated pending the router-probe rider in step E. Do not read the prior note as establishing general prevention across the variant class.
- **Router-position note (August 11, 2026):** Probes substituted upstream of the router; production substitutes downstream of it, by design. This is an improvement over the tested configuration, not a compromise: the router classifies the real query, removing the probes' classify-on-transformed-input circularity, while the retrieval-signal configuration (substituted string to embedding and keyword scorer) is identical to arm C.
- **Implementation naming and config facts (August 11, 2026):** Constant shipped as `SUBSTITUTION_FAMILIES` (renamed from STRIP_FAMILIES pre-consumer; name matched to behavior after the deletion design lost the A/B/C experiment framing). Substitution is case-insensitive (`re.IGNORECASE`, decided August 11) with a 14th BDD scenario covering lowercase. Capitalization applies only when the substitution lands at string position zero.
- **Post-182 Step 0 re-baseline findings (August 13, 2026):**
  - **P5 keyword gap narrowed.** Verified August 13 after MATTGPT-182 fix (loader normalization applied). On P5, Rearchitecting Live Railroad Systems scored kw=0.250 vs. kw=0.125 in the August 12 raw-dict reproduction. One additional token, consistent with a "Refactoring" public_tag reaching the scorer that the story's own prose never contains -- the title says "Rearchitecting" and the tokenizer does no stemming. Speed-Win held at kw=0.375 across both runs: "refactoring" already reached the scorer via its Process bullet, and the scorer intersects token sets, so a duplicate tag adds nothing. Net: P5 keyword gap narrowed from 3-1 to 3-2; blend gap from ~0.078 to ~0.060. Status unchanged at LEAD.
  - **General shape of tag impact:** Tags only move a score where they introduce vocabulary the other eight haystack fields lack. Expect small, concentrated corpus-wide impact rather than broad drift.
  - **Subject substitution disconfirmed as lever for these probes.** Across all four probe pairs (P1/P6, P4/P7, P5/P8, P2/P3), the "How does Matt..." and "How do you..." variants produced identical status. This disconfirms subject substitution (`_substitute_matt_subject`) as the lever for these probes. P5/P8 identity re-confirms the May 19 finding; P1/P6 and P4/P7 are new. It does not rule out query rewriting generally -- a rewrite that adds vocabulary rather than removing a name is untested by this probe set.
- **Sequencing note (August 13, 2026):** Demoted to NEXT, behind -181. Phase 1 shipped (627f6f4). Phase 2 target is the MattGPT / Independent Project cluster (9 stories each, 3.8x their corpus share) -- distinct from the CIC cull that was -172's scope. -172 was parked (premise disconfirmed: CIC leads 26% of queries against 46% corpus share, under-represented not dominant). Phase 2's premise is intact; the MattGPT cluster is still overrepresented. Phase 3 (BM25) cannot reach P5/P8: the query says "platform refactoring," Rearchitecting Live Railroad Systems says "rearchitecting" / "rearchitecture" -- no stemmer, no match. Re-measure P5/P8 after -181 corpus additions. If the additions change pool composition, the problem may partly dissolve; if not, Phase 2 scoping proceeds and Phase 3 addresses the vocabulary gap.
- **Status note:** Phase 1 Green landed at 627f6f4. Phase 2 (MattGPT cluster cull) premise intact -- awaiting -181 re-measurement before scoping.
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
- **Gap status values:** `[Open]` = no decision made; `[Decided]` = fix path chosen, work pending; `[Written]` = story drafted or corpus addition made.
- **Known gaps (May 2026)** — surfaced during the NiCE Manager Solutions Architecture JD assessment (May 19, 2026):
  - `[Open]` Node.js production work (no anchor)
  - `[Open]` SDK / library development (no anchor)
  - `[Open]` Specific AI/ML framework experience in enterprise client context (anchors exist via MattGPT solo project; weak in client work) — **MATTGPT-080 candidate first, story only if structured assertion insufficient**
  - `[Open]` Managing multiple concurrent AI projects (no anchor; large-scale single-project anchors strong)
  - `[Open]` Leading teams composed of AI Engineers / Software Developers / ML+LLM specialists (CIC anchors team-leadership broadly, not specifically composed of AI/ML specialists)
  - `[Open]` Direct conflict resolution / employee relations experience (no anchor; tangential evidence in leadership stories) — **likely (b) resume/LinkedIn fix, not corpus**
- **Decision per gap — use MATTGPT-081's corrective-actions taxonomy:** Before writing a new story for a known gap, decide whether the right fix is:
  - (a) New STAR story → file a sibling ticket (MATTGPT-022 / MATTGPT-078 style)
  - (b) Resume / LinkedIn / positioning-doc update → not a corpus issue
  - (c) MATTGPT-080 `matt_profile.json` restructure → some gaps may be better addressed by structured skill assertions with provenance, not narrative stories
  - (d) Real skill gap → corpus is honest, no story needed; ignore in this thread
- **Candidate additions (July 29, 2026 -080 session):** CIC-era hands-on technical stories are under-written. Candidates include:
  - `[Open]` Spring Boot (if hands-on) — evaluate whether structured assertion or new story is the right fix before filing sibling ticket.
  - `[Open]` AI-enablement work outside Liquid Studio/CIC scope (distinct from MATTGPT-078's framing) — same evaluation needed.
- **Coverage gaps with identified source material (August 5, 2026 -- surfaced during MATTGPT-088 diagnostic on structured JD):**
  - `[Decided]` **"10+ years of professional software development experience" -- partial, 5/5.** Corpus starts in 2005 at Solution Architect level. Source material: the 2005 resume shows 1997-2005 individual-contributor engineering across Cendian, Well Found Technology, Lockheed Martin, GE Power Systems, and others, plus Oracle Certified Professional 8i certification. **Decision: (a) new STAR stories.** Three-item slate with drafts pending: Well Found Technology / F-22 origin; Lockheed Martin STRATCOM (carries the 2002 TDD and pairing conviction); Cendian B2B/EDI (Norfolk Southern ancestor). Adjunct-professor work folds in, placement TBD. Record starts at 2000 by Matt's ruling. No de-aging; the history is the pitch. Drafts from Matt's firsthand account with the 2005 resume as evidence backbone. Filed as **MATTGPT-181**.
  - `[Open]` **Insurance or risk management domain knowledge -- gap, 5/5.** Previously recorded as an honest corpus limit. Source material now identified: the CIC FY23 deck shows two Nationwide engagements: a Transformer application modernization and a ways-of-working academy. Corpus verdict is currently correct (no story exists), but this is not a permanent gap -- material is available. Decision path: (a) new STAR story using Nationwide as anchor.
- **Additional gaps from archived 080 doc, section 5 (August 12, 2026):**
  - `[Open]` **D18 Strategic Partnerships.** Confirmed corpus gap as of the June 30 check. Blocked pending verification of the resume claim it sources. No decision on fix path until that verification is done.
  - `[Open]` **Norfolk Southern Conway's Law / product mindset.** Marked "needs decision, explicit go/no-go pending" since January. "The CIC's First Engagement" is adjacent but does not own the frame. Explicit go/no-go required before any story work is filed.
- **Workflow:** When a new Role Match assessment surfaces a gap not in this list, append it to the "Known gaps" section above with the surfacing JD context. When a gap is prioritized for action, file the sibling ticket (story / profile / resume) and link it back here.
- **Cross-references:**
  - **MATTGPT-080** — `matt_profile.json` restructure; addresses gaps better fit for structured skill assertions
  - **MATTGPT-081** — Role Match engine corrective-actions output; categorizes gaps systematically going forward
  - **MATTGPT-022** — Data Quality Cleanup Journey Story (sibling story-writing ticket)
  - **MATTGPT-078** — AI Enablement Before It Had a Name (sibling story-writing ticket; addresses AI enablement gap surfaced during resume Option E work)
  - **MATTGPT-181** — Early-career story slate (Well Found / F-22, Lockheed STRATCOM, Cendian B2B/EDI); sibling ticket for the Decided gap above
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
- **Logged:** May 28, 2026 (original); re-scoped May 28, 2026 (post-persona-review reconciliation)

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

### MATTGPT-126
**Ask Agy landing — input border flash on load; emotion-class guard retained as insurance**

- **Status:** Parked
- **Priority:** Low
- **Type:** Issue
- **File:** `ui/pages/ask_mattgpt/styles.py` (original ticket had wrong file: global_styles.py)
- **Logged:** June 12, 2026

**Symptom:** Ask Agy landing input (`key="landing_input"`) intermittently renders without a visible border on initial page load. Not reproducible as of June 2026 — parked until it reappears.

**Code-reviewed June 2026 (Chrome Claude):**
- The `div[data-testid="stTextInput"] input` rule lives in `styles.py` line 348, not `global_styles.py`.
- `!important` is already on the border rule at line 352. The originally proposed fix was already shipped before the ticket was filed.
- If the flash returns, investigate `div[data-baseweb="input"]` wrapper border suppression (`styles.py` lines 373–378), not the `<input>` border rule.

**On the .st-bz/.st-c0/.st-c1/.st-c2 block (`styles.py` lines 388–396):**
Originally flagged as removable dead code (emotion hashes drift between builds and may not currently match live DOM classes). Reversal: do NOT remove. The original comment "Kill Streamlit's atomic border classes" documents that something was alive and needed killing — a pink/red inner border that required multi-iteration remediation. Streamlit upgrades can regenerate hashes that collide with old ones; an unmatched selector is a no-op, but an absent guard when the hashes return means re-paying the remediation cost. Comment updated in commit `598b14c` to document the intent explicitly. Block stays.

---


### MATTGPT-128
**Displayed-source faithfulness — source cards must substantiate the claims in the answer**

- **Status:** Open
- **Priority:** High
- **Type:** Issue
- **Logged:** June 14, 2026
- **Depends on:** ~~MATTGPT-080~~ (shipped)

**Symptom (production-confirmed June 14, 2026):** Agy answered a Fiserv commercial-impact query with accurate numbers ($8.5M, 3% under budget, $500K penalties avoided) but the displayed source cards showed JP Morgan and Norfolk Southern — not the Fiserv STAR story. A recruiter who clicks to verify a claim finds the wrong sources. Observed across multiple probes: "Why Hire Matt" was cited as a source for a largest-team question AND an early-career telecom question, neither of which it substantiates.

**Root cause (design fork — must be resolved before implementation):**
Source cards currently display Pinecone retrieval top-k by score. That is a different set from what the LLM actually grounded the answer in. The likely Fiserv mechanism: the specific numbers came from the "Why Hire Matt" aggregate positioning doc (which summarizes wins across clients and ranks high on almost every query), while the Fiserv STAR story never entered the top-k. The cards honestly showed what was retrieved; the honest set was wrong.

Two design options:
- **Option A — Fix retrieval so the right story enters top-k.** Depends on -094 (retrieval diversity). -080 (positioning docs separated from STAR stories) has shipped; that blocker is cleared. Cards continue to show top-k; faithfulness improves as a consequence. No new display logic.
- **Option B — Display what the answer was grounded in.** Requires the LLM to emit provenance (story IDs it drew from) alongside the answer, then surface those as the source cards. Decouples display from retrieval ranking. More engineering; higher faithfulness ceiling.

**Acceptance criteria:**
- For a set of client-specific queries (Fiserv, RBC, Capital One, AT&T), the named client's STAR story appears in the displayed source cards.
- "Why Hire Matt" and MattGPT positioning docs do not appear as the sole sources for client-specific factual claims.

**Eval to add:**
For each client-specific probe query, assert `client_name in [s.get("Client") for s in displayed_sources]`. Mirrors the client-attribution pattern in Q15.

**Note:** -080 has shipped (STAR stories and positioning docs now separated in the index). Option A is unblocked on that dependency. Do not close this ticket with Option B alone unless Option A is explicitly decided against.

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
- Stories 1 and 2 (expand-from-logged) completed before Stories 3–5 (recovery-dependent). **[Met -- August 12, 2026.]** AT&T SE CRM and Fiserv both confirmed at STAR depth against corpus. All key facts from the ticket present and quantified.

**Sequencing:** Stories 3–5 are blocked on elicitation. Stories 1 and 2 done; do not conflate their status with 3–5.

**Candidate additions (July 29, 2026 -080 session):** CIC-era hands-on technical stories flagged as under-written: Spring Boot (if hands-on); AI-enablement work outside Liquid Studio/CIC scope (distinct from MATTGPT-078). Evaluate for addition to this list or as separate story tickets before next elaboration pass.

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

### MATTGPT-131
**BDD selector bug — `test_industry_and_capability_labels_visible_inline_on_mobile` fails in marathon run**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug (test only)
- **Run note (August 16, 2026):** Single run showed 233 passed, no failure here -- consistent with this being a marathon-only timing issue (scenario 18 of 54, at ~31 min). Cannot disposition from a single run. Needs 3-4 repeated full-suite runs to characterize pass/fail distribution.
- **Logged:** June 15, 2026

**Context:** `test_industry_and_capability_labels_visible_inline_on_mobile` fails in the full BDD suite marathon run (52 passed, 1 failed). The feature is correct in both local and production at 375px — Chrome Claude confirmed `st-key-facet_industry_v2`, `stWidgetLabel`, `display: flex`, `visibility: visible`, bounding rect 48x14px fully within viewport. The label is present and Playwright-visible in the live app.

**Root cause:** Not yet confirmed. Candidates: (1) the selector hardcodes `facet_industry_v2` but `_widget_version_industry` in a fresh BDD session starts at 0 (`facet_industry_v0`), making the substring match fail; (2) marathon-run resource pressure causes the DOM assertion to fire before the label renders after a 375px viewport resize. Scenario 18 of 54, fires at 31 min into a 31-min run.

**Acceptance criterion:** Scenario passes in isolation (`pytest tests/bdd/steps/test_explore_stories.py::test_industry_and_capability_labels_visible_inline_on_mobile -v`) and in the full suite without flake.

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

**Note (from MATTGPT-127):** `gpt-4o` is the correct model for `jd_assessor.py` in production — `gpt-4o-mini` produces subpar assessment reasoning. Do not substitute mini when replacing the literal.

**Acceptance criteria:** No model name string literal in any production file outside `config/constants.py`.

---

### MATTGPT-142
**BDD: sequential rejection test wait_for_banner not count-aware**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **Run note (August 16, 2026):** Passed in the August 16 run. Cannot disposition from a single pass -- need to confirm whether the underlying code was fixed (would close Done) or the test structure changed (Parked/DA). Verify before closing.
- **Issue:** `test_sequential_rejections_swap_chip_sets_per_branch` fails because `wait_for_banner` waits for `.no-match-banner` to exist, not for a new one. After the first rejection renders a banner, subsequent `wait_for_banner` calls return immediately. The `all PERSONAL_CHIPS should be visible` assertion runs before the second rejection has processed, so `get_visible_chip_labels` sees only the first rejection's RULE_CHIPS (highest transcript_banner_N is still the first rejection's index).
- **Root cause:** `wait_for_banner` is not count-aware. `then_banner_displayed` also only checks `.no-match-banner` presence without verifying it is the banner for the current query.
- **Production behavior:** Correct. "Is Matt married?" returns "I'm focused on Matt's professional experience." and PERSONAL_CHIPS render as expected (confirmed manually June 23, 2026).
- **Fix:** In the sequential scenario, count existing `.no-match-banner` elements before submission and wait for that count to increase. Pass expected count into `wait_for_banner`, or add a dedicated `wait_for_nth_banner(n)` helper.
- **Affects:** `tests/bdd/steps/test_ask_mattgpt.py` — `test_sequential_rejections_swap_chip_sets_per_branch`
- **Logged:** June 23, 2026

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

### MATTGPT-145
**Mobile filter breakpoints overlap — r2-label show/hide works by cascade order, not by design**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** June 24, 2026
- **File:** `ui/styles/global_styles.py`
- **Run note (August 16, 2026):** Mobile filter rendering passed in August 16 BDD run. Cannot disposition from a single run -- need to verify whether the CSS cascade fragility was resolved by a code change or whether the test is not exercising the fragile path. Manual visual check at 375px and 481-767px range before closing.

**Issue:** The mobile filter layout uses three overlapping media blocks that fight over the same properties at phone widths. Code-reviewed against the repo June 2026 — line numbers confirmed exact.

- **Block A** `@media (max-width: 767px)` lines 2189–2325: sets r2 labels to `display: none !important` (line 2223); injects field name via `::before` (lines 2227–2253); "prevent crushing" rule at lines 2255–2260.
- **Block B** `@media (max-width: 767px)` lines 2327–2335: a standalone second 767px block (not a 480px block). Comment: "::before suppression must come AFTER the 767px block that injects content". Sets `::before` to `content: none !important` and `display: none !important` — cancels Block A's injection. Also fires at ≤480px, making the cascade three-deep at phone widths.
- **Block C** `@media (max-width: 480px)` lines 2338–2396: sets r2 labels to `display: block !important` (line 2376).

All three fire simultaneously at ≤480px. All carry `!important` at equal specificity — source order decides. Block C sits last, so `display: block` currently wins and phone rendering is correct, but only by accident of file position.

**Why it matters:** Silent failure mode. If any block moves or the file order shifts, the 767px `display: none` wins and r2 labels silently vanish on phones — no error, surfaces later as a mystery regression. Validated working June 24, 2026 via Chrome Claude (note: Streamlit floors `window.innerWidth` at ~406px, so 375px and 430px both render at 406px; all three blocks are active there).

**Intended three-tier design (correct; only the expression is fragile):**
- **>=768px (desktop):** full filter bar, inline labels. No mobile blocks apply.
- **481-767px (mid band):** r2 labels hidden; field name injected as `::before` pseudo-content (compact, label rides inside the control).
- **<=480px (narrow phone):** r2 labels shown as real labels above dropdowns; `::before` injection suppressed; controls full-width; padding/gaps/fonts reduced.

The bug is that Blocks A and B have no lower bound, so they leak into the ≤480px range where Block C explicitly reverses them.

**Fix (behavior-preserving — same rendered output at every width):**
1. Floor the conflicting mid-band rules by moving ONLY these from Block A into a new `@media (min-width: 481px) and (max-width: 767px)` block:
   - r2-label hide (lines ~2220–2223)
   - `::before` field-name injection for r2 (lines ~2227–2246) and paired "prevent crushing" rule (lines ~2255–2260)
2. With the injection floored at 481px, Block B (the standalone 767px suppression block at lines 2327–2335) becomes redundant — it exists only to cancel the injection at ≤480px, and the injection no longer fires there. Delete it. Note: Block B is a 767px block, not a 480px block — don't go looking for it in the 480px section.
3. **Do NOT rebound the rest of Block A.** `stForm` label hide (~2191), Industry/Capability label sizing (~2203), and general mobile filter-bar layout are genuine all-mobile compensation that must stay active at 375px. Only the three r2 rules that Block C reverses get the floor.

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

**Related -- code adjacency:** MATTGPT-166 (Arc stories invisible to entity-scoped queries via Fortune 500 Clients / Cross-Division placeholder metadata) is a different symptom but touches the same metadata-driven filtering code. Whoever works either ticket will be in the same module. Read both detail blocks before starting either.

---

### MATTGPT-150
**MATTGPT-144 test fallout — decouple BDD assertions from display copy and stranded AgGrid selectors**

- **Status:** Open
- **Priority:** Medium
- **Type:** Refactor / Test
- **Logged:** July 1, 2026
- **Dependencies:** None. MATTGPT-144 Done.

**Issue:** The AgGrid → st.dataframe migration left three coupling problems in the BDD suite caught reactively during a full-suite run. Production functionality is confirmed working. This ticket addresses the test debt.

**Finding 1: Count noun is not a shared constant.**
`explore_stories.py:1219` renders the noun `stories` as an inline literal inside the `.es-results-count` HTML string. Three tests (`test_banking_landing.py`, `test_cross_industry_landing.py`, `test_home.py`) match against it with the regex prefix `of\s+(\d+)\s+stor`. A copy change in that one line breaks all three tests silently. Additionally, `test_home.py:146` has a stale docstring still reading "projects" from before the migration.

Action: extract the noun to a named constant in `explore_stories.py`, import and reference it in the three test files. Fix the stale docstring in `test_home.py:146`.

**Partial progress (commit `1be5953`):** Regex fixed in all three test files (`of\s+(\d+)\s+project` → `of\s+(\d+)\s+stor`). Constant extraction and `test_home.py:146` docstring fix still open.

**Finding 2: Sort-order assertion is now a canvas-mount check only.**
`test_explore_stories_default_state.py::assert_sort_descending` (lines 158–169) was rewritten to wait for `[data-testid="stDataFrame"]` and `[data-testid="data-grid-canvas"]`. It no longer verifies sort order — that is a manual visual check per the ARCHITECTURE.md canvas constraint. Production sort confirmed working visually.

Action: add a data-layer assertion in `test_explore_stories_default_state.py` that verifies `Start_Date` values in `view_paginated` are descending before the dataframe receives them. The corpus is already loaded in that file. This covers the behavior without touching the canvas.

**Finding 3: Stranded `.ag-root-wrapper` / `.ag-row` waits in a silent `try/except`.**
`test_explore_stories_default_state.py:123–124` still waits for `.ag-root-wrapper` and `.ag-row` inside a `try/except` that swallows the timeout. These selectors will never match now that `st.dataframe` replaced AgGrid. They produce a ~30s silent wait on every run of that test.

Action: replace with `wait_for_selector("[data-testid='stDataFrame']")` consistent with the rest of the file. Remove the `try/except` — the dataframe mount is the correct gate and should fail loudly if it times out.

**Sweep:** `grep tests/bdd/steps/ -r` for `.ag-`, `stCustomComponentV1`, and `frame_locator` to confirm no other stranded AgGrid selectors remain across the full suite.

**Acceptance criteria:**
- Count noun extracted to a constant; three test files reference it; stale docstring in `test_home.py:146` corrected.
- `assert_sort_descending` asserts actual sort order at the data layer, not just canvas mount.
- `.ag-root-wrapper` / `.ag-row` waits replaced with `stDataFrame` selector; `try/except` removed.
- Full BDD suite passes with 0 failed, skip count unchanged.

---


### MATTGPT-152
**Move debug output from UI sidecar to terminal log only**

- **Status:** Parked
- **Priority:** Low
- **Type:** Refactor
- **File:** `utils/ui_helpers.py`, `services/backend_service.py`, `ui/pages/ask_mattgpt/conversation_view.py`
- **Logged:** July 16, 2026

**Issue:** Debug output currently appears in the Streamlit UI sidebar as well as the terminal. When `DEBUG=True`, `dbg()` in `utils/ui_helpers.py` calls `st.sidebar.write("🧪", *args)` at four call sites in `backend_service.py` (lines 1400, 1502, 1694, 1936). A second debug block in `conversation_view.py` (lines 140-152) renders a static `st.caption` showing `VECTOR_BACKEND`, `PINECONE_INDEX_NAME`, and `PINECONE_NAMESPACE`. Goal is terminal-only.

**Proposed change (3 files, confirmed low-risk):**

1. `utils/ui_helpers.py:75` -- `st.sidebar.write("🧪", *args)` to `print("🧪", *args)`. Redirects all four `dbg()` call sites to stdout.
2. `services/backend_service.py` -- add `PINECONE_INDEX_NAME`, `VECTOR_BACKEND` to the `pinecone_service` import and log them in the startup sanity check block (after DNA Status line), so the config values that are currently sidecar-only land in the terminal instead.
3. `conversation_view.py:140-152` -- remove the entire `# DEBUG INFO` block. After step 2, these values are in the terminal log and the sidecar block is redundant.

**Constraint:** `__ask_dbg_*` session state writes in `backend_service.py` are orphan keys (set, never rendered) -- leave untouched.

**No BDD cycle needed:** debug-mode-only output, no DOM-observable behavior changes.

**Parked because:** 080 is higher priority. Revisit when 080 closes.

---

### MATTGPT-153
**Q64 eval stochastic -- replace phrase-cluster with concept-cluster robust to story-selection variance**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor / Test
- **Sibling:** MATTGPT-082 (same root cause: eval checking the wrong thing)
- **Logged:** July 16, 2026

**Issue:** Q64 ("How does Matt manage resistance when leading enterprise transformation programs?") is stochastic. The LLM alternates between surfacing CloudFirst/Ways of Working (which contains "resistance" but not "Norfolk" or "stabilize") and other stories, producing variable phrase-match counts across runs. The test requires 2 of 5 phrases; variable story selection means the threshold is not reliably met.

**Evidence:**
- Failing in July 16, 2026 eval (68/70). Failure documented in test comment at line 218.
- Prior passing run: July 15, 2026 (70/70).
- Stochastic behavior first noted May 23, 2026.
- July 31, 2026: failing again. Full-suite run matched 1/2 phrases ("resistance"); isolation run matched 0/2. Two runs minutes apart, different phrase hit counts. Confirms story-selection variance as root cause.

**Fix shape (two options, pick one before implementing):**

1. Same approach as Q2/Q5/Q55: replace phrase-cluster check with a concept-cluster that's robust to story-selection variance. Concepts like "resistance", "enterprise transformation", "stakeholder alignment" should pass regardless of which story the LLM pulls.
2. Verify whether CloudFirst/Ways of Working is actually a correct answer for this query (resistance in enterprise transformation). If yes, update ground truth vocabulary to include its terminology so either story path passes.

**Pre-flight before implementing:** check what the Q2/Q5/Q55 concept-cluster pattern looks like and apply the same structure here.

---

### MATTGPT-154
**Operational-breadth tagging pass -- surface operational ownership into all corpus stories where it's genuinely true**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Spawned from:** MATTGPT-094 (retrieval concentration investigation, Sub-B finding)
- **Logged:** July 16, 2026

**Issue:** The MATTGPT-094 investigation confirmed that operational stories were under-surfacing due to a vocabulary gap: terms like "Sev-1" and "on-call" were absent from the corpus. The fix in -094 tagged AT&T CRM and JPM stories, and prod verified those two stories now surface correctly on operational queries. But one or two examples isn't enough density. There are additional corpus stories where operational ownership is genuinely true and the vocabulary anchors are still missing.

**Scope:** Audit the corpus for stories where Matt had real operational accountability (on-call, incident response, enterprise release ownership, Sev-1 involvement, production stability) that isn't currently tagged with operational vocabulary. Add the vocabulary where the substance is real. Do not add it where it isn't.

**Constraints:**
- Vocabulary additions must reflect actual story substance. No inflation.
- AT&T CRM and JPM stories are already done (in prod as of MATTGPT-094). Don't re-touch them.
- After tagging, run the Sub-B probe set to confirm surfacing improves: "Tell me about a Sev-1 Matt handled", "Has Matt run on-call rotations?", "Tell me about Matt's experience with global enterprise releases", "What's Matt's operational background?"

**Not in scope:** Re-writing story framing (that's MATTGPT-095). Not a corpus content quality pass, purely a vocabulary/tagging pass so retrieval matches the substance that's already there.

**Additional finding -- payments vocabulary gap (August 18, 2026):**

Same mechanism as the operational gap above: vocabulary absent from corpus stories that carry the substance.

- **Gap:** SWIFT and cross-border payment specifics under-documented across banking stories.
- **Verified August 18, 2026:** `grep -r '\bSWIFT\b'` across the corpus returns exactly one hit -- Gateway story, `Competencies[5]`. Matt confirms SWIFT was also part of JPM ACCESS and RBC engagements; neither story mentions it.
- **User impact:** Query "has Matt ever worked with SWIFT payments?" reaches retrieval; ranker picks ACCESS on payments proximity; Agy correctly admits "the story does not specifically mention SWIFT." Visitor sees "sort of" instead of "yes, on 3+ engagements."
- **Fix:** Audit banking stories (JPM ACCESS, RBC, HSBC, others) for cross-border payment specifics -- SWIFT, wire, ACH, FX, correspondent banking -- and add explicit mentions to Situation/Action/Competencies where the substance is real. Same audit likely surfaces adjacent gaps (ISO 20022, SEPA, etc.).
- **Probe additions:** "Has Matt worked with SWIFT payments?", "Tell me about Matt's cross-border payment experience", "Does Matt know ACH/wire/FX?"

---

### MATTGPT-155
**New corpus story -- sell-side commercial story (HSBC-anchored): pricing/costing, resourcing, outcome-based contracting**

- **Status:** Open
- **Priority:** Medium
- **Type:** Action
- **Logged:** July 29, 2026

**Issue:** The corpus has a buy-side commercial story ("Owning the P&L...") but zero sell-side commercial substance. Matt's sell-side experience -- pricing/costing with CFM, LCR/UCR resourcing, estimating, managing CRs and SOW expansions, transitioning from hours-times-rate to outcome-based contracting -- is a distinct and material capability. HSBC is the anchor client: $10M SOW built via ROM, pricing model, and staffing plan.

**Do not bundle with the buy-side P&L story.** These are different commercial motions (sell to client vs. manage margin on a delivery). Keep as a separate story.

**Story scope:**
- Pricing and costing using CFM (commercial financial model)
- LCR/UCR resourcing and rate-card discipline
- Estimating at proposal stage; managing CRs and SOW expansions in delivery
- Transition from hours-times-rate to outcome-based contracting
- Anchor: HSBC $10M SOW -- ROM, pricing model, staffing plan

**Elicitation note:** Follow the same elicitation-first approach as -078/-129. Do not write the story without a session to pull the specific numbers and decision moments.

---

### MATTGPT-156
**Vendor commercial/spend management gap -- decide whether corpus-zero on invoice/rate-card/procurement is a real claim or honest gap**

- **Status:** Open
- **Priority:** Low
- **Type:** Investigation
- **Logged:** July 29, 2026

**Issue:** The corpus has zero content on invoice approval, rate-card management, third-party spend, procurement, or vendor governance. This is distinct from the existing Vendor Management (coordination/relationship) skill in the corpus. The question to answer before writing anything: does Matt have real claims here worth a story, or is this an honest gap?

**Decision gate:** If yes, a story or structured assertion belongs in the corpus. If no, record as a documented honest gap so it doesn't re-surface as a question each session.

**Scope of the gap:** invoice/rate-card management, third-party spend oversight, procurement process, vendor governance (budget accountability, not just relationship management).

**Constraint:** Do not conflate with the existing Vendor Management (coordination) skill, which covers vendor selection, relationship, and delivery oversight. This is specifically about the commercial/spend side.

**Partial resolution (July 29, 2026):** Confirmed real claim: Matt reviewed and approved contract fee and cost submissions from Bottomline Technologies to JP Morgan across the ACCESS program, with authority to reject items before payment. Now in the corpus as an Action bullet and a `Vendor Invoice Review & Approval` competency on "Building the Payment Engine Behind JP Morgan ACCESS." Deliberately not surfaced into that story's Use Case(s) -- the story's thesis is payments engineering and the field is already at 473 of 600 characters.

**Remaining question:** Whether vendor commercial management warrants its own story. Evidence is currently Action/Competencies-level on one story, so it will not retrieve on a vendor-spend query. Rate-card management, procurement process, and vendor governance remain corpus-zero. RBC confirmed not applicable; the invoice review was ACCESS only.

---

### MATTGPT-159
**Role Match performance -- parallelize per-requirement assessor calls; sequential gpt-4o loop is the bottleneck**

- **Status:** Open
- **Priority:** Medium
- **Type:** Performance
- **File:** `services/jd_assessor.py`
- **Surfaced:** June 16, 2026 (during -067 release-gate work; classified backend optimization, kept out of that gate)
- **First documented:** June 26, 2026 backlog prioritization session
- **Logged:** July 31, 2026

**Issue:** `jd_assessor.py` makes one sequential `gpt-4o` call per JD requirement. The demo JD has roughly 23 requirements. The `assess` loop dominates; `extract` is a large N-independent cost (~22s local on the demo JD) and is the floor regardless of parallelism.

**Historical measurement:** 336 seconds end to end, measured June 16, 2026 at TOP_K=3. This predates the TOP_K=5 change made July 31, 2026, which increases context per call. The current sequential cost is higher than the recorded figure. Re-measure before optimizing; do not quote 336s as the current number.

**Root cause and fix:** Sequential per-requirement calls with `gpt-4o` is the confirmed root cause. The fix is concurrency -- parallelize the `assess` calls using `asyncio` or a `ThreadPoolExecutor` -- not a model downgrade. Per-requirement reasoning with `gpt-4o` is what makes the scorer credible (confirmed in MATTGPT-088 scope work: mini produces subpar assessment reasoning). Dropping to mini would make -088 worse, not better. Estimated improvement after parallelization: two to three minutes down to fifteen to twenty seconds (June 2026 estimate; re-validate after implementation).

**Why this went unfiled twice:** Surfaced June 16, 2026 during -067 release-gate work and classified as backend optimization rather than UI polish -- correctly kept out of that gate, but not filed. Sat as a latency reference note in -088 and -099 without an owner through June 26, when it was identified as unfiled in a backlog prioritization session and still not filed. Same pattern as MATTGPT-155 (sell-side story) and MATTGPT-156 (vendor spend): context notes in other tickets are not tickets, and findings without an owner evaporate. Filed here so it has one.

**Perceived-performance half (independent of the concurrency fix):** What the user sees during a two-minute wait -- whether it looks like progress or like a hang -- is a separate concern that can land even if concurrency work slips. Connects to MATTGPT-083 (spinner inconsistency). Worth addressing regardless of when the async fix ships.

**Constraints:**
- Do not swap `gpt-4o` for `gpt-4o-mini`. This is a concurrency change, not a prompt or scoring change.
- Keep per-requirement judgment logic identical.
- Re-run all three JDs to confirm verdicts are unchanged after parallelization.

**Cross-references:**
- Latency context noted (not ticketed) in MATTGPT-088 and MATTGPT-099 detail blocks.
- MATTGPT-083 -- spinner inconsistency; perceived-performance half connects here.
- MATTGPT-160 -- extraction clause-dropping; separate defect in the same file.

---

### MATTGPT-160
**JD extractor clause-dropping -- 7 of 23 requirements on demo JD lose qualifiers during extraction**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `services/jd_assessor.py` (`extract_requirements()`)
- **Logged:** July 31, 2026

**Issue:** `extract_requirements()` drops qualifiers from JD requirements during extraction. On the demo JD, 7 of 23 requirements lost qualifiers -- the extracted text is narrower than what the JD actually requires. Downstream effect: the assessor evaluates a stripped version of the requirement, which can produce verdicts (strong, partial, gap) that don't reflect what the hiring manager wrote.

**Probe script:** `probe_db_extraction.py` (repo root) contains tooling for investigating this defect. It runs `extract_requirements()` on the structured JD, compares extracted text to source, and tests full-text vs stripped retrieval through Pinecone at top-40. Re-use this rather than building a new probe.

**Constraint:** This is a separate defect from MATTGPT-157 (W_KW keyword weighting). The clause-dropping happens at extraction time, before retrieval scoring. Do not conflate.

---


### MATTGPT-166
**Arc stories with placeholder client metadata excluded from entity-scoped queries -- tradeoff, not defect**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Logged:** August 3, 2026

**Reframing (August 19, 2026):** The original framing called this a defect. It isn't. `Fortune 500 Clients` and `Cross-Division` are intentional placeholders -- used for stories that cover NDA-protected engagements or multi-client patterns where no single client name applies. Putting a placeholder in the field was the right call; the code then needed to know that placeholder values are not real entity names. `is_generic_client()` in `client_utils.py` exists for exactly this reason. The exclusion from entity-filtered queries is a consequence of a deliberate authoring decision, not a gap.

**The real question:** Whether arc stories should bypass entity filters -- not because they were miscategorized, but because they document patterns that are genuinely relevant to named-client queries even though no specific client is listed. "Owning the P&L" covers financial accountability across JP Morgan, RBC, Fiserv, and HSBC engagements. A visitor asking about JP Morgan can't find it by client filter because there is no JP Morgan entry to match.

**Concrete example:** "Owning the P&L" -- P&L ownership, commercial accountability, cross-engagement financial governance. Relevant to any large named-client query. Unreachable via entity filter because `Client: Fortune 500 Clients` does not match any entity value.

**Decision required -- three paths (do not implement before choosing):**
- **A. Accept the tradeoff.** Arc stories are corpus-wide by design; entity filtering is for single-engagement precision. The two modes are intentionally separate. No fix.
- **B. Wildcard arc-story metadata.** Entity filters pass arc stories alongside entity-specific stories when `is_generic_client()` returns True. Simpler implementation; risk is surfacing arc stories on narrow queries where they reduce precision.
- **C. Compound metadata.** Arc stories carry both the placeholder AND a list of the specific clients they cover. Entity filters match against the compound list. Most precise; most implementation effort; requires a corpus audit to populate the client lists.

**Recommendation:** Evaluate Option A honestly first. If arc stories genuinely document patterns that are client-agnostic, excluding them from client-scoped queries is correct behavior. If they are materially relevant to named-client queries (as the P&L story is), Option B is the lowest-risk fix. Option C is only worth the corpus work if precision matters enough to justify it.

**Related -- code adjacency:** MATTGPT-146 (Professional Narrative stories leak into My Work via filter and search paths) is a different symptom but touches the same metadata-driven filtering code. Whoever works either ticket will be in the same module. Read both detail blocks before starting either.

---

### MATTGPT-167
**Widen entity detection to Project and Place -- specification complete, no confirmed failing case currently**

- **Status:** Parked
- **Priority:** Medium
- **Type:** Action
- **Logged:** August 3, 2026

**Issue:** Entity detection currently covers four fields: Client, Employer, Division, Title. Project and Place appear as queryable dimensions across the corpus but are not in `ENTITY_DETECTION_FIELDS`. Queries like "who worked on the White-Label Card Portal" or "what did Matt work on in Chicago" cannot benefit from entity-anchored retrieval.

**Specification (complete -- ready to implement if activated):**
- Widen `ENTITY_DETECTION_FIELDS` from four to five fields, adding Project and Place.
- Replace the single `EXCLUDED_DIVISION_VALUES` set with a per-field exclusion map:
  - Project exclusions: Innovation, Methodology, Platform Modernization, Personal Growth, Career Narrative, Accelerated Delivery (generic project labels that appear in many stories and would over-constrain retrieval)
  - Place exclusions: Career Narrative, Personal (Sabbatical) (non-geographic place values)
- 34 distinct Project values and 15 distinct Place values confirmed in corpus audit (August 3, 2026).

**Pre-registered probes:**
- "Who worked on the White-Label Card Portal" -- should trigger Project entity detection on White-Label Card Portal
- "What did Matt work on in Chicago" -- should trigger Place entity detection on Chicago

**Why parked:** The motivating case from the August 3 trace session resolved differently (via a different retrieval path). No confirmed failing probe exists at time of filing. The specification is complete and pre-registered probes are defined -- re-activate when a concrete failing case is confirmed in production.

**Prior art -- read before unparking:** MATTGPT-036 (Entity Cluster Promotion Override, Decided Against) and MATTGPT-037 (Score Gap Override, Decided Against) are both retrieval-override mechanisms that were rejected. The DA rationale for each may apply to the per-field exclusion map approach in this ticket. Read both DA blocks and confirm the objection does not carry over before activating this work.

---

### MATTGPT-168
**Slot 1 is amplified without regard to margin -- tie or near-tie at slot 1 gets 80% of the answer**

- **Status:** Open (rewritten August 13, 2026 -- original premise disconfirmed; see investigation below)
- **Priority:** High
- **Type:** Bug
- **Files:** `ui/pages/ask_mattgpt/prompts.py` (line 171), `ui/pages/ask_mattgpt/backend_service.py` (line 829)
- **Logged:** August 5, 2026

**Issue:** `ranked_stories[0]` is wrapped in `<primary_story>` and `prompts.py:171` requires at least 80% of the response to come from it, forbidding the model from building around a supporting story. Nothing in the pipeline checks whether slot 1's win was decisive. A story that leads by 0.000 gets the same treatment as one leading by 0.072.

**Exhibit 1 (August 3, 2026):** "Has Matt directly managed engineering teams?" Why Hire Matt and the management story both scored 0.476 -- a tie. Why Hire Matt held slot 1 by Pinecone ordering. The model built the entire answer around it; the result was a Professional Narrative response to a direct operational question.

**Exhibit 2 (August 13, 2026):** "how did Matt handle a Sev-1 defect?" Pool spanned 0.298 to 0.352. Leader was 0.020 clear of second in a 0.054-wide band. Slot 1 was a MattGPT story; the Fiserv story with actual Sev-1 evidence sat at rank 5, reached the LLM at position 2, and was capped at 20% by the floor.

Compare a clean case: the Fiserv entity query led at 0.580 with a 0.072 gap to second. Same pin, same 80% floor, decisively different margin.

**What will not fix it:** Lowering the 80% floor. On both exhibits the response would still be mostly the wrong story. Only a different slot 1 changes the answer.

**Floor consistency note:** The floor does not always bind. On "Tell me about a Sev-1 Matt handled" (August 13), MattGPT led at 0.303 and the model answered from Fiserv at slot 3 anyway. The floor's effect is inconsistent and not fully characterized.

**Corrected history (August 13, 2026):** The original ticket stated the design gap was introduced in `1c96315` (Jan 23, 2026) and never fixed. That is wrong. February traces showed `diversify_results` genuinely promoting named clients over better-scored generic stories -- AmEx (0.501) to slot 1 over Row 40 (0.672), Capital One bumping Row 103 to slot 4 -- because the function partitions by client bucket without reading scores. The original -168 premise was describing real pre-March behavior. The fix was `3aa3050` (March 2026): "slot 1 is sacred, pin the top Pinecone score, diversify 2-5." That commit added `pinned = stories[0]` unconditionally and is why slot 1 is now always the top-scored story. The 80% floor was reasoning about that pin: "slot 1 is the best retrieval match; instruct the model to build 80% around it." Pin and floor were designed as a pair for the fixed world.

What -168 originally named was real in February and fixed in March. What survives is what the pin-and-amplify pair assumes: slot 1 deserves it. In February that assumption was violated by diversification. Now it's violated by ties and near-ties.

**Do not fix by re-pinning:** The pin (`stories[0]` unconditionally) was the March fix. Re-proposing it is a no-op.

**Disposition options (August 13, 2026):**
- **Do nothing.** Ties and near-ties mean the two stories are genuinely close; picking either is defensible. Consistent with the subtraction principle.
- **Conditional pin.** When the gap between slot 1 and slot 2 is below a threshold, drop the 80% floor and let the model use both. Not a new retrieval gate -- a softening of an existing prompt instruction. Requires a threshold, which needs the Top Score distribution that MATTGPT-174 is now accumulating. Block behind that data.
- ~~**Cheap probe.** Remove the "resist supporting stories" sentence.~~ **Tested August 14 -- ruled out.**
- ~~**Soften the 80% floor.**~~ **Tested August 14 -- ruled out, and possibly counterproductive.**

**Prompt experiment 1 (August 14, 2026): resist-line removal**

Removing the "resist" line from the CONTEXT ISOLATION block had no effect on either exhibit. Q1 still answers entirely from the chatbot story at slot 1.

Observed in the same run: the 80% rule is not reliably followed in either direction:
- "Tell me about a Sev-1 Matt handled" -- model bypassed slot 1, answered from slot 3 (correct).
- "Has Matt directly managed engineering teams?" -- bypassed slot 1, answered from slot 4 (also correct).
- "how did Matt handle a Sev-1 defect?" -- stayed on slot 1 (wrong).

Compliance is inconsistent and uncorrelated with correctness. **Working hypothesis:** the model overrides the primary when the primary cannot answer the question, and stays on it when it can. The chatbot story is a genuine defect story (32.3% failure rate, root cause diagnosis, structural fix) -- it closes the content gap that would otherwise force a fall-through.

**Prompt experiment 2 (August 14, 2026): floor softening**

Changed "at least 80% of your response must come from this story. Do NOT build your response around a supporting story" to "it should be the main subject of your response. Draw on supporting content where it answers more directly." 6 runs of Q1 -- all 6 answered from the chatbot story. Before the change: 1 in 4 correct. After: 0 in 6.

Hypothesis: the hard floor ("do NOT") was the explicit permission-to-deviate framing that the soft version removed. With "draw on supporting where it answers more directly," the model sees no reason to leave the chatbot story -- because the chatbot story IS about fixing a defect. It's topically correct, just the wrong context.

**Sample size caveat:** 0/6 vs 1/4 at these sample sizes is not strong evidence softening made things worse. The defensible claim is that it did not fix Q1. Controls held on both experiments: P5 answered from Norfolk Southern, Sev-1 on-call from AT&T, "Tell me about a Sev-1" from Fiserv.

Prompt reverted to original. Two experiments now closed, both negative.

**Hardened conclusion:** No prompt edit reaches this. The chatbot story leads pc 0.360 to 0.326 and the model behaves consistently with that gap. The fix must be ranking: Fiserv needs to lead the pool.

**Proposed ranking fix (August 14, 2026):** Strengthen Fiserv's Use Case in the corpus. Current Use Case is 414 chars and buries the defect vocabulary in a trailing clause: "while resolving Sev-1 defects in live payment processing." Rail went from 0.484 to 0.526 by leading its Use Case with the query vocabulary. Same pattern applies. Proposed edit (verified to stay within the story's honest claim -- the Action already notes the deployment fix is a companion story):

> "Recover a failing $8.5M multi-vendor platform program: stabilize delivery, manage SOA transition from mainframe to API architecture, and coordinate globally dispersed teams through crisis to completion. Own the $8.5M program budget through the recovery, delivering under budget and avoiding contractual penalties on a rescued release. Handle Sev-1 defects in live payment processing: triage, resolve, and drive production quality recovery on a platform serving 2M+ cardholders."

After stopword fix: keyword scores already inverted correctly (Fiserv 0.250, chatbot 0.125). pc is the remaining gap (0.363 vs 0.317, difference 0.046). Rail's Use Case edit moved its pc ~0.040 -- same order of magnitude. Worth trying before concluding anything needs cutting.

**Fiserv Use Case edit result (August 15, 2026):** Edit applied. Sev-1 handling moved into its own sentence; a parenthetical cross-reference to another story's title was removed (that title was embedding in Fiserv's vector, adding noise). pc moved 0.317 → 0.326. Chatbot still leads (pc 0.360 vs 0.326, gap now 0.034, down from 0.046). Q1 still fails -- chatbot answers. Direction confirmed correct; gap insufficient to flip the pool. The next intervention must be larger or different.

**Where margin information could live:** The confidence gate (MATTGPT-174 shipped Top Score logging). The only stage currently positioned to carry spread as well as level.

**Cross-references:** MATTGPT-174 (gate calibration -- Top Score distribution is what any conditional-pin threshold must be derived from), MATTGPT-077 (noun-overlap contamination), MATTGPT-169 (closed -- PN exclusion shipped at 6a581d5; positioning-story attractor finding documented in CHANGELOG), MATTGPT-178 (closed -- stopword fix inverted keyword scores at 049e203; pc gap is the remaining work in this ticket), MATTGPT-190 (character-set divergence, split from -178).

---

### MATTGPT-171
**Phrase-aware matching: short-token filter leaves single stopword token for instructional phrases; scorer behavior under-characterized**

- **Status:** Open
- **Priority:** Low
- **Type:** Investigation
- **Logged:** August 8, 2026
- **Mechanism corrected:** August 11, 2026 (see below)

**Mechanism correction (August 11, 2026 -- supersedes original framing):** The original issue stated that `_tokenize` "filters stopwords before computing overlap" and that "I do, we do, you do" reduces to an empty token set. Both claims are wrong.

Verified: `_tokenize("I do, we do, you do")` returns `['you']`. `_tokenize` does not filter stopwords -- `_STOPWORDS` is used only by `token_overlap_ratio`, not by `_tokenize`. The real filter is `len >= 3`: "I" (len 1), "do" (len 2), "we" (len 2) are dropped; "you" (len 3) survives.

The phrase is not invisible to keyword scoring. It scores on a single stopword token ("you"), which can match stories that contain "you."

**Revised consequence:** The original test instruction ("confirm W_KW=0 and W_KW=current produce identical rankings") may not hold, since "you" is a real scoring token. The affected query class is not zero-token phrases but single-token phrases where the surviving token is a stopword with broad corpus distribution.

**Coupling to MATTGPT-178 (closed):** MATTGPT-178 raised the question of whether `_STOPWORDS` was intended to apply to `_tokenize` as well as `token_overlap_ratio`. That question is resolved: -178 shipped at 049e203 (August 13, 2026) and `_tokenize` now applies `_STOPWORDS`. As a consequence, "you" now drops from the example above, and the original empty-token-set framing becomes retroactively true for any phrase where all tokens are stopwords or shorter than 3 chars. The mechanism this ticket is investigating has shifted -- see revised scope below.

**Investigation scope (updated August 16, 2026):** (1) With "you" now filtered by `_STOPWORDS`, re-verify what `_tokenize("I do, we do, you do")` returns. (2) Determine whether single-surviving-stopword queries that are now fully invisible to keyword scoring surface retrieval problems in production. (3) Assess whether the -178 fix changes the severity of this ticket -- if phrases that previously scored on a stopword now score zero, that may improve or worsen real query behavior depending on the phrase class.

---


### MATTGPT-173
**Role Match JD validation: no defined behavior for malformed or atypical JD inputs**

- **Status:** Open
- **Priority:** Medium
- **Type:** Issue
- **Logged:** August 8, 2026

**Issue:** Role Match's JD intake has no validation layer. The pipeline assumes a well-formed JD with requirements, qualifications, and role context. Observed failure modes and undefined behaviors:

- **Comp-only JDs or JDs leading with salary ranges:** MATTGPT-099 (closed as Decided Against) established that the chatbot handles comp decline correctly. The Role Match assessment path is separate -- behavior on a JD where comp dominates the text is unverified. May silently drop, hallucinate a match, or emit a confusing assessment.
- **Extremely short JDs:** A one-paragraph job post has insufficient signal for the extractor. Current behavior on extraction failure is unverified.
- **Non-JD input:** Pasting a company overview, a recruiter note, or a requirements doc instead of a JD. Extractor may return requirements; assessment may proceed with misleading output.

**Investigation first:** Before designing validation, run the three failure-mode inputs (comp-heavy JD, short JD, non-JD text) through the current pipeline and document actual behavior. The fix depends on what the pipeline does, not what it's assumed to do.

**Fix shape (after investigation):** Likely a pre-extraction validation gate that checks minimum text length, presence of requirement-shaped language, and optionally warns the user if comp-only content is detected. Should not silently proceed with an extraction the gate suspects is malformed.

**Cross-references:** MATTGPT-089 (location/work-model/availability parsing -- adjacent input-handling gap), MATTGPT-099 (closed DA -- comp handling on chatbot side; Role Match side is distinct).

---

### MATTGPT-176
**Dead code: zero-caller function, 200-line commented block, duplicate typed-alias map**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Files:** `ui/pages/ask_mattgpt/utils.py` (line 237), `ui/pages/ask_mattgpt/backend_service.py` (lines 1044-1243, 1412-1421), `ui/pages/ask_mattgpt/conversation_view.py` (line 305)
- **Logged:** August 11, 2026

**Three items -- work independently, ship together or separately:**

1. **Dead function:** `push_card_snapshot_from_state` at `utils.py:237` has zero callers. Confirmed via grep. Remove the function and any imports that exist solely for it.

2. **Commented-out legacy block:** `_generate_agy_response` at `backend_service.py:1044-1243` -- 200 lines of legacy response-generation logic, commented out. Survived the `6cba8d9` cleanup pass that removed 430 similar lines from the same file. Note for whoever picks this up: `6cba8d9` claimed to have cleared this class of commented-out legacy code; this block's survival was not intentional, it was missed. Remove. If git history is needed, it is in the commit log; commented-out code in a live module is not a backup strategy.

3. **Duplicate typed-alias map:** `backend_service.py:1412-1421` contains a typed-alias map independent of the one at `conversation_view.py:305`. Two implementations of the same feature with no documented reason for divergence. Before removing either copy: (a) confirm both maps are identical in content; if they differ, the divergence is a separate bug to file. (b) Identify which call path uses which copy and make `conversation_view.py:305` the canonical one, or document why the backend copy must exist.

**Note on `_format_narrative`:** An earlier claim in this investigation that `_format_narrative` output "poisons every query" was retracted. Verified: `_format_narrative` feeds `answer_context`, used only at `backend_service.py:1041`, the API-failure fallback path. It does not enter the LLM prompt on normal query paths. No ticket warranted; noted here for provenance since the retraction happened in the same investigation session.

---

### MATTGPT-177
**token_overlap_ratio bound violation -- repeated in-vocab tokens inflate ratio above 1.0; docstring example independently wrong**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `utils/validation.py` (last two lines of `token_overlap_ratio`)
- **Failing test:** `tests/unit/test_scoring_contracts.py::test_token_overlap_ratio_stays_within_unit_interval` (failing by design -- pre-registers the expected fix)
- **Logged:** August 11, 2026

**Issue:** `hits = sum(1 for t in toks if t in vocab)` iterates the non-deduped token list. Dividing by `max(1, len(set(toks)))` dedupes the denominator but not the numerator. Any repeated in-vocab token inflates the ratio above the documented [0.0, 1.0] range.

**Verified:**
- `token_overlap_ratio("aws aws aws", {"aws"})` returns 3.0
- `token_overlap_ratio("platform platform", {"platform"})` returns 2.0

**Docstring bug (independent of the bound violation):** The docstring's third example documents `"platform and some unrelated words"` as returning 0.5. Actual return value is 0.25. The docstring is wrong regardless of which bug is fixed first.

**Fix (two edits, ship together):**
1. Change the numerator to dedupe before counting: `sum(1 for t in set(toks) if t in vocab)`. The denominator `len(set(toks))` is then consistent with the numerator and the ratio stays within [0.0, 1.0].
2. Correct the docstring's third example: `"platform and some unrelated words"` is documented as 0.5, actual return is 0.25. The input has no repeated tokens (4 unique non-stopword tokens, 4 total), so the fix cannot change this result -- 0.25 is correct unconditionally. Write 0.25 into the docstring directly.

**Severity gate (verify before closing):** Grep all callers of `token_overlap_ratio`. If any caller gates on a value near 1.0 (e.g., `if ratio > 0.8: reject`), an inflated ratio passes a gate it shouldn't. That would upgrade severity from Medium to High. If no caller thresholds against a near-1.0 value, the defect is a correctness issue without a confirmed downstream behavioral consequence.

**Cross-references:** MATTGPT-190 (character-set divergence in the same function -- fix both together; they interact at the character-class level before this arithmetic runs). MATTGPT-178 closed -- stopword fix shipped at 049e203; character-set issue is now -190.

---


### MATTGPT-180
**Test fixture blind spot: test_formatting.py, test_filters.py, test_scoring.py:85 pass against phantom schema**

- **Status:** Open
- **Priority:** High
- **Type:** Bug
- **Logged:** August 11, 2026

**Issue:** Three test files build fixtures using the phantom field names (`why`, `how`, `what`, `star.situation`, etc.) rather than the verified JSONL schema (`Purpose`, `Process`, `Performance`, `Situation`, etc.). Because the tests operate on their own in-memory dicts, they pass against the phantom schema with no coverage of the actual data the production code reads.

Specific location: `test_scoring.py:85` constructs a fixture dict using phantom field names. `test_formatting.py` and `test_filters.py` do the same throughout.

**Why this matters:** This is not a cleanup item. It is the reason the `formatting.py` phantom schema defect was invisible -- a passing test suite is meaningless if the fixtures do not match production data shape. Any refactor or fix that passes these tests is unverified.

**Recurrence prevention rule:** Story fixtures must be built by calling `utils.corpus_loader.load_stories()` (reads from `echo_star_stories_nlp.jsonl` at repo root, applies full normalization) and selecting by index, Client, Domain, or Era. Do not call `app.py`'s `load_star_stories()` from tests -- it fires `st.set_page_config()` at import. Inline fixture dicts built from field names guessed from code are not valid. This rule applies to all three files and any future test file that handles story objects.

**Work items:**
1. Rebuild fixtures in `test_formatting.py`, `test_filters.py`, and `test_scoring.py:85` using `utils.corpus_loader.load_stories()`.
2. Confirm previously-passing tests still pass after fixture replacement (a test that breaks on correct fixtures was never actually testing the thing it claimed to test -- investigate each failure before discarding).

---

### MATTGPT-183
**has_metric filter dead -- remove rather than fix**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** August 13, 2026

**Issue:** `has_metric` is initialized to `False` at `explore_stories.py:129` and `:725`, read at `:362` and `:1069`, and cleared at `:411`. Nothing in the UI ever sets it to `True`. The chip at line 362 can never render. The filter key is dead.

`utils/filters.py` imports `story_has_metric` from `formatting.py` to gate this branch. `story_has_metric` reads phantom field names (`what`, `star.result`) and returns False for every story -- but that doesn't matter, because the branch is unreachable regardless. The defect is the dead filter, not the broken function.

**Note -- second story_has_metric:** `ui/pages/ask_mattgpt/utils.py:168` has a sibling implementation that reads `s.get("Performance", [])` correctly. That one is unaffected. `filters.py` imports from `formatting.py`, not from `utils.py`.

**Fix (removal, not repair):**
1. Remove the `has_metric` branch from `matches_filters` in `utils/filters.py`.
2. Remove the chip and clear logic from `explore_stories.py` (lines 362-363, 410-411).
3. Remove `has_metric` key from both filter initializers (`explore_stories.py:129`, `:725`).
4. Delete `test_filters.py:116` (tests the dead branch against a phantom-schema fixture; passing tells you nothing).
5. `story_has_metric` in `formatting.py` then has no importer and becomes dead code -- delete it inline as part of this ticket. MATTGPT-179 is DA; do not route this to that ticket's deletion list.

**Note -- personas:** `personas` in `filters.py` is already self-documented as dead ("not used -- field doesn't exist in data"). `conversation_helpers.py:121` reads it for badge rendering; the badges never render because the field is absent from corpus stories. Same class; not in scope for this ticket but worth a cleanup pass alongside it.

**Cross-references:** MATTGPT-180 (test_filters.py:116 is a phantom-schema fixture that should be deleted, not rebuilt). Note: MATTGPT-179 is DA -- the three dead formatters (`_format_narrative`, `_format_key_points`, `_format_deep_dive`) are documented there as a finding; `story_has_metric` deletion is in scope for this ticket as step 5 above.

---


### MATTGPT-185
**Query negation unsupported -- "outside of MattGPT" returns MattGPT stories**

- **Status:** Open
- **Priority:** Medium
- **Type:** Enhancement
- **Logged:** August 13, 2026

**Issue:** Verified August 13, 2026 from query_log_parsed.csv. Three consecutive attempts to steer retrieval away from the Independent Project cluster, all returned MattGPT-led results:

| Query | top_score | spread | Result |
|---|---|---|---|
| "Talk to me more about matt's experience in Iterative Development?" | 0.589 | 0.111 | mattgpt_led |
| "outside of MattGPT, does matt have experience with Iterative Development?" | 0.581 | 0.136 | mattgpt_led |
| "Do NOT TALK about MattGPT -- but rather tell me about projects where Matt did Iterative Development?" | 0.584 | 0.121 | mattgpt_led |

**Mechanism:** Embeddings do not represent negation. "Do not talk about MattGPT" embeds close to MattGPT content, so escalating the exclusion makes the semantic match stronger, not weaker. No prompt or ranking change can fix this -- the excluded stories are the ones retrieval surfaces.

**Available mechanism:** Pinecone metadata filters support `$ne` and `$nin`. The codebase already builds `$or` entity filters across six fields (ARCHITECTURE.md §entity filtering). An exclusion filter is the same shape inverted. The hard part is detection, not filtering: recognizing "outside of X", "not X", "other than X", "besides X", "excluding X", "aside from X" and resolving X against known entity values. `detect_entity()` already does substring matching against `ENTITY_DETECTION_FIELDS` and `ENTITY_ALIASES`, so the resolution half exists.

**Tension to resolve before building:** This adds a detection layer with a phrase list, which is the pattern the Jan-Feb 2026 simplification work removed (entity gate, `classify_query_intent`, banned phrases -- each removal improved eval). Counter-argument: this changes what retrieval searches rather than correcting retrieval's output, which puts it closer to the entity filter that was kept than the entity gate that was removed. Decide that before scoping the build.

**User impact:** A visitor who notices the portfolio leaning on a side project and tries to redirect gets the same answer, more emphatically, each time they try.

**Cross-references:** MATTGPT-077 (Independent Project / MattGPT vocabulary concentration is why MattGPT dominates these pools in the first place), MATTGPT-172 (CIC consolidation -- reducing Independent Project density is the upstream lever; this ticket handles the explicit-exclusion case).

---

### MATTGPT-187
**diversify_results max_per_client parameter is documented but never implemented**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `ui/pages/ask_mattgpt/backend_service.py:1246-1319`
- **Logged:** August 13, 2026

**Issue:** The signature takes `max_per_client: int = 1` and the docstring says "Limiting stories per client." The parameter is never referenced in the body. Stories beyond the first per client go into `duplicate_overflow` and are concatenated onto the result rather than dropped.

Two failing tests assert the documented contract:
- `test_limits_single_client_stories` -- asserts `jpmc_count <= 1`, gets 2. Input `[JPMC, JPMC, Capital One, Takeda, AmEx]` returns `[JPMC, Capital One, Takeda, AmEx, JPMC]`.
- `test_maintains_overall_order` -- asserts descending score order, gets `[0.95, 0.82, 0.78, 0.75, 0.88]`. The duplicate JPMC at 0.88 is bumped to the end.

**Decision required before fixing:** Is the intent to drop duplicates or to demote them? The tests assert drop. The code demotes. Callers pass `max_per_client=3` at `backend_service.py:1937`, which only means something under the drop interpretation.

Note the second test also asserts score ordering, which the function cannot preserve by design -- it partitions by client bucket and never reads a score. That assertion may be testing the wrong contract regardless of how the first question is resolved.

**Cross-references:** MATTGPT-168 (records this finding in its body -- this is the ticket that owns it), MATTGPT-177 (covers the first of the six untracked failures; this covers two more).

---

### MATTGPT-188
**Semantic router accepts off-topic queries about other people**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `services/semantic_router.py`
- **Logged:** August 13, 2026

**Issue:** Three `test_rejects_invalid_queries` cases fail. The router scores queries about other people against intent phrases matched on question shape rather than subject:

| Query | Score | Family |
|---|---|---|
| "Tell me a joke" | 0.429 | behavioral |
| "Tell me about Elon Musk" | 0.401 | technical |
| "What's Jeff Bezos's leadership style?" | 0.664 | leadership |

All clear `SOFT_ACCEPT = 0.40`.

**Not fixable by raising the threshold.** Logged production behavioral queries score 0.499 to 0.605 (query_log_parsed.csv), so a threshold above 0.664 would reject legitimate traffic. The router has no signal distinguishing "Matt's leadership style" from "Bezos's leadership style" -- the phrasings embed nearly identically.

**Live behavior, not just a test failure:** `semantic_valid` is not a rejection gate (see MATTGPT-174, closed), so these queries proceed to Pinecone regardless of score. Determine what a visitor asking about Bezos actually receives before scoping a fix.

Note: the eval suite already contains "Tell me about Elon Musk" as a golden query, so whatever the intended behavior is, it is specified somewhere.

**Cross-references:** MATTGPT-174 (closed -- three thresholds now found outside their operating range: CONFIDENCE_HIGH too low, HARD_ACCEPT too high, SOFT_ACCEPT here), MATTGPT-063 (wrong-person query detection -- same failure mode, different ticket).

---


### MATTGPT-190
**Tokenizer character-set divergence: _tokenize keeps +#-. while token_overlap_ratio splits on non-\w**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `utils/validation.py`
- **Descended from:** MATTGPT-178 (closed -- stopword fix shipped at 049e203; character-set issue separated into this ticket)
- **Related:** MATTGPT-177 (bound violation in the same function)
- **Logged:** August 16, 2026

**Issue:** The two tokenizers in `utils/validation.py` use incompatible character sets:
- `_tokenize` uses `_WORD_RX = [A-Za-z0-9+#\-_.]+` -- keeps `+`, `#`, `-`, `.` as word characters.
- `token_overlap_ratio` uses `re.split(r"[^\w]+")` where `\w = [A-Za-z0-9_]` -- those same characters become separators.

**Verified divergence:**

| Input | `_tokenize` output | `token_overlap_ratio` tokens |
|---|---|---|
| `c++` | `['c++']` | `[]` |
| `.net` | `['.net']` | `['net']` |
| `node.js` | `['node.js']` | `['node']` |
| `ci/cd` | `[]` | `[]` |

**Consequence:** Technical terms containing these characters are tokenized differently on the indexing side (`_tokenize` builds the vocab) vs. the scoring side (`token_overlap_ratio` does the overlap calculation). Queries containing `c++`, `.net`, `node.js` etc. undercount technical-term overlap against stories that contain them.

**Prerequisite (verify before fixing):** Confirm that `initialize_vocab` builds the vocab using `_tokenize`. The docstring asserts this; the function itself was not read during investigation. The answer determines which tokenizer is wrong: if vocab is built with `_tokenize`, fix `token_overlap_ratio` to use the same regex. If vocab is built with `re.split(r"[^\w]+")`, fix `_tokenize` (and accept that `c++` becomes `['c']`).

**Cross-references:** MATTGPT-177 (bound violation in the same function -- fix both together; they interact at the character-class level), MATTGPT-178 (closed -- stopword fix; this ticket carries the remaining character-set finding).

---





### MATTGPT-195
**Production incident queries scatter across six intent families -- delivery family has no incident vocabulary**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `services/semantic_router.py` (`VALID_INTENTS["delivery"]`)
- **Logged:** August 16, 2026

**Issue:** Ten queries about production incidents, tested across two probe batches, landed in six distinct intent families: behavioral, background, narrative, technical, leadership, stakeholders. No query landed in delivery. Family determines substitution eligibility, the pin rule applied in `prompts.py`, and retrieval emphasis. The same question receives different pipeline treatment depending on phrasing.

**Ten-query family scatter (August 16, 2026):**

| Query | Family | Score | Valid |
|---|---|---|---|
| Walk me through the last major production incident you owned | behavioral | 0.454 | yes |
| What's the root cause, and what systemic fix prevents this class of failure permanently? | behavioral | 0.445 | yes |
| How long did it take between detection, engagement, and resolution? | behavioral | 0.339 | no |
| What was the actual customer impact and blast radius? | behavioral | 0.316 | no |
| Who is running point on the incident command, and what's the external communication status? | leadership | 0.305 | no |
| Walk me through a major production incident Matt owned | background | 0.667 | yes |
| How does Matt approach root cause analysis and preventing repeat failures? | narrative | 0.603 | yes |
| How does Matt handle incident detection and resolution time? | narrative | 0.570 | yes |
| Tell me about a production outage and its customer impact | technical | 0.409 | yes |
| How does Matt run incident command during a major outage? | stakeholders | 0.552 | yes |

**Root cause:** `VALID_INTENTS["delivery"]` contains six phrases focused on delivery acceleration and team velocity. No phrase covers production incidents, Sev-1 response, on-call ownership, or resolution. The absence is total, not present-but-underweighted.

**Confidence gate note:** All ten queries returned `confidence=high` from Pinecone and would pass the gate regardless of `semantic_valid`. The consequence of wrong-family routing is retrieval mismatch and phrasing variance, not rejection.

**Two retrieval gaps confirmed in probe:**
1. "Production incident" without "outage" retrieves Fortune 500/Assumptions story (delivery language, not incident-specific). The Aug 15 corpus edits to AT&T and Fiserv improved the vocabulary but were insufficient.
2. "Root cause / systemic fix / prevent failures" retrieves the chatbot story -- same mechanism as MATTGPT-168's Sev-1 failure. The chatbot story is explicitly about root cause analysis and preventing repeat failures; it is topically correct but the wrong context.

**Proposed fix:** Add 6-8 phrases to `VALID_INTENTS["delivery"]` covering production incident vocabulary. Requires deleting `data/intent_embeddings.json` to regenerate the cache. Requires eval run before commit -- phrase additions shift scores across all families, not just delivery.

**Complexity budget note:** Adding phrases is the same shape as what Jan-Feb subtraction work removed (Entity Gate, classify_query_intent, banned phrases). The subtraction history does not block this fix, but it raises the standard: eval pass/fail gate required, not visual inspection.

**Retrieval consequence (August 17, 2026):** `background` and `delivery` are functionally identical in the pipeline. `grep -n 'intent_family ==' backend_service.py` shows branching on `out_of_scope`, `personal`, `synthesis`, `behavioral`, `error_fallback`, and `narrative` only -- `background` and `delivery` both fall through to standard mode with entity pin and diversify. Fixing -195 changes a logged label and nothing downstream. It is routing hygiene, not a retrieval lever. Do not work this ticket expecting a query-outcome change. The actual levers for incident-query quality are MATTGPT-169 (closed -- PN exclusion shipped at 6a581d5) and MATTGPT-168 (slot-1 amplification).

**Cross-references:** MATTGPT-168 (slot 1 amplification -- chatbot root-cause contamination is the same mechanism), MATTGPT-192 (amex router failure -- same router layer), MATTGPT-154 (operational vocabulary tagging -- corpus side of the same gap), MATTGPT-169 (closed -- PN exclusion shipped at 6a581d5; positioning-story attractor was the lever).

---

### MATTGPT-196
**Defensive pytest.skip in test_explore_stories.py masks UI regressions as green runs**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **File:** `tests/bdd/steps/test_explore_stories.py`
- **Logged:** August 16, 2026

**Issue:** Four `pytest.skip()` calls in step definitions convert missing UI elements into skips rather than failures. A card grid that fails to render, a missing button, or absent timeline links would all appear as additional skips in the run total rather than test failures. Real UI regressions become invisible.

**Confirmed locations (August 16, 2026 BDD run):**
- Line 240: `pytest.skip("No clickable story elements found")` -- in the `@when` step that clicks a card. A missing card grid is a regression, not an environment constraint.
- Line 555: `pytest.skip("No close button or selected card found")` -- tries to close a detail panel; skips if nothing to close.
- Line 586: `pytest.skip("Ask Agy button not found")` -- missing Ask Agy button becomes a skip.
- Line 693: `pytest.skip("No Timeline explore links found")` -- absent timeline links become a skip.

**The correct pattern is already in the file:** Line 589 (`click_share`) uses `pytest.fail("Share button not found after 15s")` -- same situation, right outcome.

**Exception:** Line 1247 (`pytest.skip` for clipboard API) is a genuine headless Chromium constraint (clipboard requires HTTPS or a browser flag). This one stays as skip.

**Fix:** Change lines 240, 555, 586, 693 from `pytest.skip(...)` to `pytest.fail(...)`. No logic change -- only the outcome when the element is absent changes from skip to fail.

**Acceptance criteria:**
- Running the BDD suite with cards not rendering produces a failure, not an additional skip.
- Line 1247 clipboard skip unchanged.
- All currently-passing scenarios still pass.

**Cross-references:** MATTGPT-122 (Cards view BDD timing -- line 240 is the same step; if -122 is fixed, line 240 becomes safe to convert without risk of false red).

---

### MATTGPT-197
**BDD suite-order flake: test_tapping_filters_toggle_shows_row_2_on_mobile fails in marathon, passes in isolation**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **File:** `tests/bdd/steps/test_explore_stories.py`
- **Logged:** August 17, 2026

**Observation (August 17, 2026):** Fails in full BDD suite run (`pytest tests/bdd/steps/`, 3 failed / 241 passed / 36 skipped, 19-minute run at commit `eb7e5cb` + MATTGPT-074 refinement uncommitted at that run; MATTGPT-074 has since closed at c67c8b7). Passes on isolation retry with the same code.

**Suspected mechanism:** A prior scenario in the suite leaves Streamlit session state or viewport in a condition that suppresses row-2 rendering. The test is not measuring a code defect -- it is sensitive to suite execution order.

**Related:** MATTGPT-145 (mobile filter breakpoint cascade -- same CSS surface), MATTGPT-131 (BDD selector bug in marathon run -- same class of marathon-only flake). Both need 3-4 repeated runs to characterize before disposition.

**Acceptance criterion:** Passes consistently in the full suite without isolation, or root cause confirmed and documented.

---

### MATTGPT-198
**BDD suite-order flake: test_clicking_a_nav_label_still_routes_to_its_surface_no_regression fails in marathon, passes in isolation**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **File:** `tests/bdd/steps/test_navbar_brand_layout.py:98`
- **Logged:** August 17, 2026

**Observation (August 17, 2026):** Fails in full BDD suite with `AssertionError: Nav button labeled 'My Work' not found`. MATTGPT-100 renamed Explore Stories → My Work; MATTGPT-106 must preserve the label. Passes on isolation retry -- the label exists and the selector logic is correct.

**Diagnosed (August 17, 2026):** The test navigates by URL (e.g., `/my_work`) rather than clicking the nav label. Streamlit routing does not respond to arbitrary URL paths in this manner; navigation does not land where the test expects. The marathon failure is likely this URL routing gap, not session state mutation.

**Related:** MATTGPT-100 (Explore Stories → My Work rename), MATTGPT-106 (navbar refactor). Same marathon-run failure class as MATTGPT-142, MATTGPT-145, MATTGPT-197 -- four instances.

**Evidence:** Full-suite failure at `eb7e5cb` + MATTGPT-074 refinement uncommitted at that run (MATTGPT-074 has since closed at c67c8b7); isolation-run pass with gate refactor restored.

**Acceptance criterion:** Passes consistently in the full suite without isolation, or root cause confirmed and documented.

---

### MATTGPT-199
**Entity-name-untrimmable hole in MATTGPT-074 content-kw gate: AT&T tokenizes to empty set, strip never fires**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **File:** `ui/pages/ask_mattgpt/backend_service.py` (content-kw gate, ~line 1638), `utils/validation.py:62`
- **Logged:** August 17, 2026

**Issue:** The content-kw gate strips `entity_toks = set(_tokenize(entity_value))` from `retrieval_q` before recomputing kw. For entities whose canonical name tokenizes to `set()`, nothing gets stripped, so any content token disperses kw and suppresses synthesis -- identical to the broad-query behavior the gate was designed to catch.

**Verified August 17, 2026:** `_WORD_RX = re.compile(r"[A-Za-z0-9+#\-_.]+")` at `utils/validation.py:62` does not include `&`. `_tokenize("AT&T")` splits into `["at", "t"]`, both dropped by the `len(t) >= 3` filter at line 94. `entity_toks = set()`.

**Consequence:** AT&T is the only current corpus entity affected. Any entity whose canonical name is ≤2 chars or contains `&` (or other non-`[A-Za-z0-9+#\-_.]` punctuation) has the same behavior. Hypothetical: "L3", "T&E", etc.

**Test impact (August 17, 2026):** MATTGPT-074 scenario 2 (content tokens beyond entity name still disperse kw) passes at both Red and Green for the wrong reason -- AT&T `entity_toks` are empty either way, so the gate cannot differentiate a broad AT&T query from a specific one. The scenario is a regression guard on content-kw dispersion generally, not a proof of AT&T entity stripping. Documented in scenario comment. MATTGPT-074 has since closed (c67c8b7, August 17).

**Fix options (for later scoping):**
1. Widen `_WORD_RX` to preserve `&` -- corpus-wide effect on all scoring; requires its own gate and eval run.
2. Add a per-entity alias (`at&t` → `att`) that gets stripped instead.
3. Detect that entity value contains chars `_WORD_RX` drops and fall back to a substring strip rather than a token strip.

**Cross-references:** MATTGPT-190 (tokenizer character-set divergence -- `_tokenize` keeps `+#-.` while `token_overlap_ratio` splits on non-`\w`; same tokenizer, adjacent gap).

---

### MATTGPT-201
**Entity pin for Client/Employer uses blend order while code comment and debug label state pc-order intent**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **File:** `ui/pages/ask_mattgpt/backend_service.py`
- **Logged:** August 17, 2026

**Issue:** The entity pin for Client/Employer takes `entity_candidates[0]`, assuming the list arrives pc-sorted. The comment at lines 1948-1949 states "For Client/Employer, Pinecone score ordering is already semantically correct..." and the debug label at lines 1978-1979 reads "using top Pinecone score:". But the list actually arrives blend-sorted, so `[0]` is the top-blend story, not the top-pc story.

**Verified August 17, 2026:** AT&T incident trace pinned Southeast CRM (pc=0.481, blend=0.531) over Defining System Interfaces (pc=0.497, blend=0.497). Southeast CRM has kw=0.333 from the Aug 17 corpus edit; that inflated its blend above the pc-preferred story. Comment and behavior disagree.

**Historical note:** The pool likely arrived pc-sorted from an older `pinecone_service` and shifted to blend-sorted without the pin code being audited. Confirm by tracing when `pinecone_service` began sorting by blend.

**Behavior is correct; the label is wrong.** The AT&T incident trace shows Southeast CRM was the right pin. Verified August 17, 2026.

**Fix (option 1):** Update the comment at lines 1948-1949 and the debug label at lines 1978-1979 from "top Pinecone score" to "top blend score." No behavior change. Requires confirming blend-order pinning is the intended semantic for Client/Employer entities generally before committing.

**Cross-references:** MATTGPT-168 (slot-1 amplification -- which story gets pinned determines what takes 80% of the response; this ticket affects the pin selection, not the 80% floor).

---

### MATTGPT-202
**id-skip predicate copied verbatim in app.py and corpus_loader.py -- divergence risk, no shared source**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug
- **Files:** `app.py` (`load_star_stories`), `corpus_loader.py` (`load_stories`)
- **Logged:** August 18, 2026

**Issue:** Both `load_star_stories` in `app.py` and `load_stories` in `corpus_loader.py` implement the same id-enforcement predicate: `story_id in (None, "", 0)`, `str(story_id).strip()`, and a call to `normalize_story`. The predicate is byte-for-byte identical in both files with no shared source. If someone fixes a bug in one path they must remember to update the other -- the same class of silent divergence that MATTGPT-182 fixed in the normalize_story call.

**What this is not:** An incomplete extraction. The `corpus_loader` module was created August 13 specifically for non-Streamlit call sites (tests, probes). The Green commit message explicitly documented the intentional split: `load_star_stories` retains a `json.JSONDecodeError` try/except that surfaces `st.warning` in the Streamlit UI; `corpus_loader.load_stories` raises on malformed lines. That behavioral difference belongs in `app.py` (Streamlit context) and not in the shared library. The error-handling separation is correct.

**The actual risk:** Only the id-skip predicate. It has no shared source and sits in both files as a copy-paste. A future bug fix to the predicate (new skip condition, edge case in `str(story_id).strip()`) hits one file without automatically flagging the other.

**Fix:** Extract the id-enforcement predicate into a single shared helper -- e.g., `is_valid_story_id(story_id)` in `corpus_loader.py` or `utils/`. Both `load_star_stories` and `load_stories` call the helper. Error handling and debug output remain where they are; only the skip-logic ownership changes.

**Naming caution:** A leading underscore on the helper (e.g., `_is_valid_story_id`) signals private to the module, but `app.py` would import it -- a convention violation. Either use a public name (no leading underscore) or document the deliberate violation in a comment. Decide before implementing.

**Pre-flight before implementing:** Read both functions in full and trace current callers of each before proposing a helper location or signature. `corpus_loader.py` line 58 docstring says "Replicates app.py id enforcement" -- that comment should be removed or updated when the helper is in place.

**Cross-references:** MATTGPT-182 (same class: normalize_story divergence across call sites; fixed August 15 at 275ff1f).

---

### MATTGPT-204
**Two Explore Stories blank-state defects: corpus-load failure silent; Table view missing empty-state guard**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **Files:** `app.py:228`, `global_styles.py:190-196`, `ui/pages/explore_stories.py` (Table branch)
- **Logged:** August 18, 2026
- **Verified:** August 18, 2026 against `explore_stories.py`

**Defect 1 -- corpus-load failure is a blank page:**

`load_star_stories` at `app.py:228` calls `st.error` on JSON parse failure or file-not-found. `global_styles.py:190-196` hides `.stAlert` unless it contains a thinking-ball element. The error renders into a hidden element; the visitor sees a blank page with no indication the corpus failed to load.

Fix: mirror the design-1A `st.markdown` block used in the startup handler, with `corpus_load` as the correlation handle. Do not touch the `.stAlert` CSS rule -- suppressing alerts globally is intentional on this surface.

**Defect 2 -- Table view missing empty-state guard:**

When no stories match the active filters, Cards view returns early with "No stories match your filters yet." and a Clear filters button (`if not view_window`); Timeline does the same (`if not view`). Table has no equivalent guard. It falls through to render an empty `st.dataframe`, which produces a GDG placeholder cell. This is a regression from the AgGrid→st.dataframe swap: AgGrid had a configurable empty-state overlay; `st.dataframe` does not. The empty-state behavior existed and was lost in the swap, not a feature that was never built. The row hint "🐾 Check any row to read the full story." also fires because it is gated on `active_story` being unset, not on row count -- so a visitor with zero results sees an empty grid and a row hint pointing at nothing.

Fix (incremental): add the same early-return empty-state guard to the Table branch before the row hint and before `st.dataframe`. Same copy and Clear filters button as Cards/Timeline. `render_pagination` already no-ops at ≤1 page; no change needed there.

Fix (full): Cards and Timeline both use `st.info` for the empty-state message, which is also suppressed by the same `.stAlert` CSS rule at `global_styles.py:190-196`. The Clear filters button renders because it is a `st.button`, not an alert -- so both views have been showing a button with invisible text and nobody noticed because the button alone is enough to be usable. Adding the guard to Table produces three views with invisible text, not three views with a working empty state. The complete fix replaces `st.info` with `st.markdown` across all three views. Implement the guard first to unblock Table; follow immediately with the `st.markdown` conversion across all three. Do not close this ticket on the guard alone.

**Surfaced during:** MATTGPT-165 Cycle A session (August 18, 2026). Out of scope for -165.

**Cross-references:** MATTGPT-202 (`load_star_stories` error handling -- the Streamlit-context concern intentionally kept in `app.py`; defect 1 is that handling being broken).

---


### MATTGPT-209
**MATT_DNA drift guard passes for wrong reason: employer check searches whole string, not Career Arc block**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug (Test)
- **File:** `utils/validation.py` (drift guard assertions)
- **Logged:** August 24, 2026

**Issue:** The drift guard's Employer check searches the entire MATT_DNA string. An employer that is also a client (Cendian, AIU) passes the check via the client list without appearing in the Career Arc section. The assertion is satisfied for the wrong reason -- it cannot distinguish "employer appears in Career Arc" from "employer appears anywhere in the string."

**Verified August 24, 2026:** Cendian and AIU currently pass this way. The Career Arc may or may not list them correctly; the guard cannot tell.

**Fix:** Scope the assertion to the Career Arc or Career Eras block specifically. Parse or slice the relevant section before checking.

**Cross-references:** MATTGPT-207 (drift guards shipped here; this is the known gap in that work).

### MATTGPT-210
**Ask Agy landing page suggestion chips are static; stories like STRATCOM invisible on career queries**

- **Status:** Open
- **Priority:** Low
- **Type:** Enhancement
- **File:** `ui/pages/ask_mattgpt/landing_view.py` (suggestion chip rendering)
- **Logged:** August 24, 2026

**Issue:** The six suggestion chips on the Ask Agy landing page are static. Stories that are perfectly retrievable by their own vocabulary are invisible on broad career queries because they are too specific to appear in top-k results for a generic prompt, and no static chip surfaces them. STRATCOM is the observed example: ranks 1 on "STRATCOM", 1 on "operational plans", and 1 on "military work" -- perfectly retrievable by its own terms -- but a visitor asking "tell me about Matt's career" will never see it.

**Discovery context (August 24, 2026):** Surfaced during MATTGPT-208 Case B analysis. Text placement and ranker changes cannot close the score gap (STRATCOM sits at rank 44 with a 0.018 gap to the pool, three to four times larger than any corpus text edit has produced). The right mechanism is discovery, not ranking.

**Proposed fix:** Rotate the suggestion chips across a curated set so that each session surfaces different entry points into the corpus. A rotating set would expose stories nobody knows to ask about without changing retrieval logic.

**Scope:** Landing page chip rendering only. Does not touch retrieval, diversify logic, or MATT_DNA.

**Cross-references:** MATTGPT-208 (discovery context).

---


### MATTGPT-213
**BDD suite: navigation step definitions duplicated across modules; no shared step module**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor / Test
- **File:** `tests/bdd/steps/` (all step modules)
- **Logged:** August 26, 2026

**Issue:** The BDD suite has no shared step-definition module. Navigation steps are identical across modules and get copied rather than reused. Concretely: "the user navigates to the My Work page", "the page has finished loading", and "the user has opened story {id}" all live in `tests/bdd/steps/test_explore_stories.py`. Any new module testing a story detail surface needs them; the current answer is to paste them in. Surfaced August 26 during MATTGPT-212 when a third copy was about to be created.

**Cost:** When the page changes, every copy needs finding and updating. A stale copy fails for a reason unrelated to what it tests.

**Pre-scope inventory required:** How many step definitions are duplicated across modules, and how many copies of each. That number determines whether this is worth doing.

**pytest-bdd resolution finding (August 26, 2026):** pytest-bdd does not resolve step definitions across modules via import. Path B experiment confirmed: importing `navigate_with_params` from `test_explore_stories.py` into `test_story_detail_sidebar.py` failed to register the step -- only the collecting module's namespace is scanned. This rules out a simple import-based fix; shared steps must live in a module that pytest-bdd collects, i.e., `conftest.py` or a file explicitly loaded via `conftest.py`. The third copy of the "navigate to My Work + open story via deeplink" pattern now exists in `tests/bdd/steps/test_story_detail_sidebar.py`; a docstring in that file references this ticket to catch a fourth-copy attempt.

**Likely fix:** Move shared steps into `conftest.py` or a `common_steps.py` loaded from there. Structural change to how the suite is organized -- not a small ticket.

**Pattern context (August 26, 2026):** Instance of the broader pattern of code that gets replicated because it was there. Other instances this week: `max_per_client` documented and never implemented (MATTGPT-187), tag generator backing up the wrong file because the line was copied from three sibling scripts where it was correct (MATTGPT-211), `public_tags` excluded from the ingestion diff report.

---

### MATTGPT-214
**Targeted audit: parameters never referenced, comments asserting absent behavior, constants unused, copied blocks with stale variable names**

- **Status:** Open
- **Priority:** Low
- **Type:** Refactor
- **Logged:** August 26, 2026

**Issue:** A pattern surfaced this week: code that reads correctly and isn't, or gets replicated because it was there. Instances: `max_per_client` accepted and never referenced (MATTGPT-187), tag generator backup copying the wrong file because the line was copied from three sibling scripts where it was correct (MATTGPT-211), `public_tags` excluded from the ingestion diff report so a cleared column reported "no changes detected." Each was greppable and none required judgment; they were found by inspection only when a related symptom appeared.

**Scope:** A targeted grep-driven pass over the codebase for:
1. Parameters accepted by functions and never referenced in the body
2. Comments asserting behavior the code does not have (documented contracts that aren't implemented)
3. Constants defined in `config/` and never imported
4. Copied blocks where a variable name survived a context change and now refers to the wrong thing

**Output:** A list of findings with file and line. No fix within this ticket -- each finding is evaluated separately for risk before touching.

**Pattern context (August 26, 2026):** Suggested alongside MATTGPT-213. Both are instances of the same class as MATTGPT-187 and MATTGPT-211.

---



### MATTGPT-217
**`_substitute_matt_subject` produces subject pronoun in object position**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug
- **File:** `services/rag_service.py` or `backend_service.py` (`_substitute_matt_subject`)
- **Logged:** August 26, 2026

**Issue:** The substitution produces "reported to he at the CIC" -- subject pronoun ("he") used in object position (should be "him"). Cosmetic today: only the embedding sees the substituted query, and the August 26, 2026 probe confirms retrieval is unaffected. Filed rather than deferred on "if a future path leaks retrieval_q to a user-facing surface" -- that condition is not checked for at change time.

**Discovery context:** Surfaced during MATTGPT-163 session, August 26, 2026.

---

### MATTGPT-205
**BDD marathon flake: test_error_state_extraction_failure fails in marathon, passes in isolation**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug (Test)
- **File:** `tests/bdd/steps/test_role_match.py:890`, `tests/bdd/features/role_match.feature:535-542`
- **Logged:** August 19, 2026

**Issue:** `test_error_state_extraction_failure` passes in isolation and at file scope but fails intermittently in the full BDD marathon. Same class as MATTGPT-197, MATTGPT-198, MATTGPT-203 -- browser tests with suite-order sensitivity.

**Bisect artifact (August 19, 2026):** Pre-Green marathon at HEAD=2c4f5e2 (b9nw3kuyv): PASSED. Post-Green marathon run 1 (boysul2ff): FAILED. Post-Green marathon run 2 (bf1npksc5): PASSED. Same command, same HEAD; working tree diff = Green applied vs stashed. Failure was intermittent, not deterministic with Green. Isolation retry with Green applied: PASSES (9.96s). Confirms suite-order sensitivity, not a Green regression.

**Mechanism not measured.** See MATTGPT-197 and MATTGPT-198 for prior work on the same class.

---

### MATTGPT-206
**Eval suite ~1-in-70 stochastic flap; Q28 confirmed non-deterministic**

- **Status:** Open
- **Priority:** Medium
- **Type:** Bug (Test)
- **File:** `tests/eval_rag_quality.py` (ground-truth concept-cluster assertions)
- **Logged:** August 19, 2026

**Issue:** The eval suite has an observed ~1-in-70 flap rate on ground-truth-match queries. Q28 is confirmed stochastic -- it failed in both pre-Green and post-Green runs on different days, ruling out a regression cause.

**Evidence (August 19, 2026, MATTGPT-161 verification):**
- Pre-Green run 1 (bi4s8nlke): 70/70
- Pre-Green run 2 (bha0kkcrp): 70/70
- Pre-Green run 3 (bbo7aajay): 69/70 -- Q28 failed
- Post-Green run 1 (bh3mfbbnw): 69/70 -- Q64 failed
- Post-Green run 2 (bjtxaif0r): 69/70 -- Q28 failed

**Q28 pattern:** Asserts ground-truth concept cluster for "rapid prototyping for client products." Matched `prototype` alone in failing runs; second required phrase absent. Root cause is retrieval non-determinism or LLM sampling variance in concept-match extraction.

**Q64 pattern:** 3 pre-Green passes, 1 post-Green fail, 1 post-Green pass -- inconclusive. Per eval discipline, 1 fail + 1 pass = noise. Not attributable to MATTGPT-161.

**Q44 pattern (August 24, 2026 -- observed once, unconfirmed):** During MATTGPT-208 Case A verification, Q44_landing failed once in the third of three eval runs (69/70) with the same concept-cluster mechanism as Q28. Required 2 matches from ['permit to fail', 'psychological safety', 'failure', 'resistance', 'early failure']; LLM produced only 'permit to fail'. Runs 1 and 2 on identical code both passed Q44 in 70/70. One data point; not a pattern until reproduced across multiple states.

**Gate reliability consequence:** A single clean 70/70 run does not prove correctness; a single failure does not prove regression. The eval gate requires multiple runs to be meaningful for any ticket that touches retrieval or LLM paths.

**Context:** The eval suite now has three tests with documented stochastic behavior: Q1_voice, Q45_structural (marked in `tests/test_structural_assertions.py` header per f0d8870), and Q28 (this finding). Not a MATTGPT-161 regression -- Q28 failed in pre-Green runs.

---

### MATTGPT-203
**Chip grid disable test asserts the wrong mechanism**

- **Status:** Open
- **Priority:** Low
- **Type:** Bug (Test)
- **Files:** `tests/bdd/features/landing_page.feature:51-55`, `tests/bdd/steps/test_landing_page.py:213-221`
- **Logged:** August 18, 2026

**Issue:** The scenario "Chip grid is not interactive during processing" waits for `.thinking-modal`, then asserts each of the six hidden receiver buttons (`st-key-suggested_0` through `_5`) carries the `disabled` attribute. The assertion tests an implementation detail that is not the actual mechanism.

**Verified manually in the app (August 18, 2026):** Clicking a chip during processing disables the entire Ask Agy landing page. Three rapid clicks produced one request -- the double-submit guard works. It does not operate by setting `disabled` on those six receivers.

**Consequence:** The assertion can pass or fail without telling you whether a double-submit is possible. A green result here is not evidence of guard correctness; a red result may reflect a DOM timing artifact rather than a broken guard.

**Fix:** Rewrite the scenario to assert what was manually verified -- a second chip click during processing produces no second request -- or delete it. Either is acceptable. Do not repair the existing `disabled`-attribute assertion; it is the wrong check regardless of whether it passes.

**Distinction from MATTGPT-197 and MATTGPT-198:** Those are timing flakes on scenarios with valid assertions. This scenario has an invalid assertion. The intermittency observed in pre-A1 and post-A1+B full BDD runs is incidental to the wrong-assertion problem; fixing the timing would not fix what the scenario is actually testing.

---

### MATTGPT-200
**top_per_theme=3 caps synthesis pool when all entity stories share one Theme; AT&T returns 3 of 6 stories**

- **Status:** Decided Against (August 17, 2026)
- **Why not:** Matt judged the AT&T 3-of-6 behavior acceptable given the corpus. Filed for the record; fix options documented.
- **Priority:** Medium
- **Type:** Bug
- **File:** `ui/pages/ask_mattgpt/backend_service.py` (`get_synthesis_stories`)
- **Logged:** August 17, 2026

**Issue:** Synthesis iterates themes and takes up to 3 stories per theme. When all entity stories carry the same Theme, the pool caps at 3 regardless of how many entity stories exist. Entities with theme diversity get proportionally more coverage: RBC (Strategic & Advisory + Execution & Delivery) yields 3+3=6; AT&T (all Execution & Delivery) yields 3 out of 6.

**Verified August 17, 2026 (production debug trace):** "What did Matt do at AT&T?" -- synthesis pool: 3 unique stories across 7 themes on a 6-story entity pool. Southeast CRM (arguably the most substantial AT&T story) is dropped because its pc for that broad phrasing ranked 6th in the pool.

**Origin note:** The `top_per_theme=3` cap predates MATTGPT-074 (closed, c67c8b7, August 17). That refinement made the cap reachable on AT&T because the previous kw-uniformity gate had suppressed AT&T promotion. Not caused by the gate change; surfaced by it.

**Fix options (later scoping):**
1. Raise the per-theme cap when the entity pool is theme-uniform.
2. Second-pass backfill: after theme-capped selection, fill remaining slots up to `N_TOTAL` from the entity pool by pc.
3. Scale cap by number of themes present (`cap = max(3, N_TOTAL // num_themes)`).

**Acceptance criterion:** "What did Matt do at AT&T?" synthesis pool includes all 6 AT&T stories (or at minimum the top-pc stories are not excluded by a theme uniformity artifact).

---

### Decided Against

> **Read only -- do not add blocks here directly.**
> Blocks are moved here from Active Tickets above when a ticket's status changes to Decided Against. New tickets always start in Active Tickets. See CLAUDE.md § Backlog Maintenance for the full lifecycle.

### MATTGPT-194
**slugify defined three times across three modules -- consolidate to one**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Slugify copies in scripts; no queued consolidation. Finding preserved here.
- **Priority:** Low
- **Type:** Refactor
- **Logged:** August 16, 2026

**Issue:** A slug-generating function exists in three places:
- `scripts/utils.py:10` -- `slugify`
- `generate_jsonl_from_excel.py:65` -- `slugify`
- `ui/pages/ask_mattgpt/utils.py:315` -- `slug` (dead; duplicates `utils/ui_helpers._slug`, the live version called at `ui_helpers.py:246`)

The `utils/ui_helpers._slug` is the live production instance. The `scripts/utils.py` and `generate_jsonl_from_excel.py` copies are standalone script utilities and may not be identical in behavior.

**Fix:** Audit all three against `utils/ui_helpers._slug`. Consolidate to a single shared utility or leave scripts self-contained with a comment noting the canonical version.

**Note:** The dead `slug` in `ask_mattgpt/utils.py:315` is already in scope for MATTGPT-184's deletion list.

**Cross-references:** MATTGPT-184 (ask_mattgpt/utils.py module audit -- the dead `slug` function is in scope for deletion there; this ticket covers the scripts copies), MATTGPT-176 (dead code bundle).

---

### MATTGPT-193
**LLM-output tests are stochastic at temperature 0.4**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Stochastic at temperature 0.4; not a regression. Tests remain red by design -- failing runs are sampling variance, not defects. Not triaging further.
- **Priority:** Low
- **Type:** Test
- **Logged:** August 16, 2026

**Issue:** Three tests assert on gpt-4o output and pass or fail randomly:
- `test_out_of_scope_redirect[retail sales work]`
- `test_no_meta_commentary[Q45_meta]`
- `test_structural_checks[Q32_structural]`

**Verified August 15, 2026:** Three consecutive runs of the first test on identical code gave: fail, fail, pass. The meta-commentary tests hit different query IDs on different runs.

These are not regressions and should not be triaged as such. Any future failure of these three tests is sampling variance until proven otherwise by a reproducible deterministic failure.

**Note:** No xfail is queued. Tests are red by design. If a future session decides to mark them xfail(strict=False) to suppress re-triage noise, that is a one-line change at each test site.

**Cross-references:** MATTGPT-153 (Q64 eval stochastic -- same category, known stochastic flap set).

---

### MATTGPT-192
**Semantic router returns out_of_scope for entity-scoped queries (amex)**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Pre-existing; confidence gate intercepts before visitor impact on confirmed queries. Not queued pending concrete evidence of visitor impact.
- **Priority:** Medium
- **Type:** Bug
- **Logged:** August 16, 2026

**Issue:** `test_legitimate_queries_pass[amex]` fails: "Tell me about Matt's amex work" routes to `out_of_scope` at score 0.696, despite entity detection firing on `Client=American Express`.

**Verified pre-existing:** Confirmed August 15, 2026 by stash run against pre-MATTGPT-178 code.

**Live consequence unclear:** `semantic_valid` is advisory and the Pinecone confidence gate is what rejects low-confidence queries. All confirmed amex queries returned `confidence=high` from Pinecone, so they would pass the gate regardless of router verdict. Determine what a visitor asking this actually receives before scoping a fix.

**Cross-references:** MATTGPT-188 (router accepts off-topic queries -- same router layer, opposite failure mode), MATTGPT-195 (incident vocabulary routing -- router classification inconsistency, same category).

---

### MATTGPT-191
**test_synthesis_pool_size fails because SYNTHESIS_THEMES is never populated in test context**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Test setup flaw; no production consequence. Not queued.
- **Priority:** Low
- **Type:** Bug
- **Logged:** August 16, 2026

**Issue:** `SYNTHESIS_THEMES` is `[]` at module init in `backend_service.py:115` and is only populated by `sync_portfolio_metadata()` via `_bootstrap_agy()`. The test fixture never calls it, so `executor.map(search_theme, [])` produces an empty pool and the pool-size assertion fails.

**Verified pre-existing:** Confirmed August 15, 2026 by stash run against pre-MATTGPT-178 code.

**Fix:** Either an autouse fixture that bootstraps themes from the corpus, or convert to an integration-style test that runs the bootstrap.

**Cross-references:** MATTGPT-180 (test fixture blind spot -- same pattern: tests assuming runtime initialization that doesn't happen in test context).

---


### MATTGPT-184
**ask_mattgpt/utils.py module audit -- six dead functions, four duplicating live helpers elsewhere**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Six dead functions documented; no queued deletion work. Backlog is a queue, not a record. Finding preserved here.
- **Priority:** Low
- **Type:** Refactor
- **Logged:** August 13, 2026

**Issue:** Verified August 13, 2026 by recursive grep from repo root (excluding venv and archive). Each of the following six functions appears only at its own definition and in `tests/unit/test_utils.py`. No production caller.

| Function | Location | Notes |
|---|---|---|
| `choose_story_for_ask` | `utils.py:89` | Dead |
| `related_stories` | `utils.py:128` | Dead -- not the Related Projects feature. That feature is live in `conversation_helpers.py:629`, built from `sources`/`src_idx`, not this function. |
| `story_has_metric` | `utils.py:168` | Dead -- reads `Performance` correctly (unlike the `formatting.py` sibling), but has no caller. See MATTGPT-183. |
| `split_tags` | `utils.py:298` | Dead -- duplicates `utils/corpus_loader._split_tags` (live, see MATTGPT-182) |
| `slug` | `utils.py:315` | Dead -- duplicates `utils/ui_helpers._slug` (live, called at `:246`). Note: a separate `slugify` function exists twice more (`scripts/utils.py:10`, `generate_jsonl_from_excel.py:65`) -- out of scope here but worth a consolidation pass. |
| `shorten_middle` | `utils.py:328` | Dead -- duplicates `utils/ui_helpers._shorten_middle` (live, called at `:137`, `:245`) |

Confirmed live, do not delete: `get_context_story`, `story_modes`, `is_empty_conversation`, `ensure_ask_bootstrap`, `push_assistant_turn`, `push_conversational_answer`, `push_user_turn`. Imported by `conversation_view.py:39`, `conversation_helpers.py:18`, `__init__.py:24`.

**Work:** Delete the six dead functions and their corresponding test classes in `tests/unit/test_utils.py`.

**Framing note:** This module was a local grab-bag that was partly superseded as shared helpers moved to `utils/`. The deletion is cleanup; it does not address the accumulation pattern.

**Cross-references:** MATTGPT-180 (tests passing against code production never exercises -- same pattern), MATTGPT-176 (dead code bundle, consider folding), MATTGPT-183 (`story_has_metric` in `formatting.py` becomes fully dead once -183 removes the `has_metric` branch -- unrelated to the sibling in this module).

---

### MATTGPT-179
**formatting.py dead formatters -- both entrances orphaned, phantom schema in unreachable code; consider folding into MATTGPT-176**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Dead code finding; no queued deletion work. Finding documented via Architecture Sync handoff. MATTGPT-183 sequencing note is self-contained -- when -183 ships, Code adds inline deletion without a standing ticket.
- **Priority:** Low
- **Type:** Refactor
- **Logged:** August 11, 2026

**Issue:** Both entrances to `formatting.py`'s formatter functions are confirmed orphaned:

- Typed alias map at `conversation_view.py:305-312`: originates in the September 2025 monolith, carried through modularization with no design intent. Not reachable by any user-facing path.
- Deep Dive pill at `conversation_helpers.py:395`: does not render in the UI. Confirmed by inspection August 11, 2026.

Nothing a visitor can reach exercises `_format_narrative`, `_format_key_points`, or `_format_deep_dive`. These three are dead code. The module stays -- `build_5p_summary` is imported by `utils/scoring.py:11` as one of the nine haystack parts in `_keyword_score_for_story`; `strongest_metric_line` is called by `build_5p_summary` at line 120 and is therefore also live; `story_has_metric` is imported by `utils/filters.py` (see MATTGPT-183).

**Consider folding into MATTGPT-176** (dead code bundle). They are separate only because the phantom schema finding adds context about what the correct fields are, preserved below in case this code is ever revived.

**Schema mapping (verified August 11, 2026 against corpus):**

| Code field | JSONL field | Type |
|---|---|---|
| `why` | `Purpose` | str |
| `how` | `Process` | list |
| `what` | `Performance` | list |
| `title` | `Title` | str |
| `client` | `Client` | str |
| `star.situation` | `Situation` | list |
| `star.task` | `Task` | list |
| `star.action` | `Action` | list |
| `star.result` | `Result` | list |

All list fields are already lists in the JSONL. The mismatch is field naming only, not structure.

**Severity correction for `_format_narrative` (do not escalate):** `_format_narrative` output feeds `answer_context`, used only at `backend_service.py:1041` -- the API-failure fallback path. It does not enter the LLM prompt on normal query paths. An earlier claim that it "poisons every query" was retracted and verified false. The orphaned-entrances finding above is the correct framing.

**Work items:**
1. Delete the three dead functions from `formatting.py`: `_format_narrative`, `_format_key_points`, `_format_deep_dive`. Do not touch `build_5p_summary` (live -- imported by `utils/scoring.py:11`), `strongest_metric_line` (live -- called by `build_5p_summary` at line 120), or `story_has_metric` (live defect -- see MATTGPT-183). The module stays.

**Sequencing note:** MATTGPT-183 removes the `has_metric` filter branch, which removes `story_has_metric`'s only importer. Once -183 lands, `story_has_metric` in `formatting.py` becomes dead and moves to this ticket's deletion list. Until -183 lands, leave `story_has_metric` alone.

---

### MATTGPT-172
**CIC-cluster consolidation: Division concentration causes cluster-drift dominance on broad queries**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Premise disconfirmed by three measurements; unpark condition (leading-story column in logger) has no implementation timeline. Evidence preserved in this block.
- **Priority:** Medium
- **Type:** Action
- **Logged:** August 8, 2026

**Parked (August 13, 2026):** The ticket asserts CIC density (46% of corpus) causes cluster-drift dominance on broad queries. Two measurements disconfirm this; a third is directionally consistent.

1. **July 2, 2026 raw retrieval probe.** Tested directly across four broad queries. CIC was absent from the cloud-transformation top ten and rank 7 on leadership. Cosine similarity is scale-invariant; CIC's greater story length could not inflate its score, and the data confirmed it did not. If CIC was over-surfacing, the cause had to be downstream (pinning, synthesis assembly, diversify_results), not raw retrieval.

2. **August 13, 2026 live traces.** Zero CIC stories in the Sev-1 query pool; six of ten were Independent Project.

3. **August 13 count over query_log_parsed.csv (43 rows), leading story by Division:**

   | Division | Leading queries | Corpus share |
   |---|---|---|
   | Sabbatical | 13 | 9 stories, 8% |
   | Cloud Innovation Center | 11 | 52 stories, 46% |
   | Cross-Division | 9 | 9 stories, 8% |
   | Technology | 5 | -- |
   | Financial Services Technology Consulting | 3 | -- |
   | Atlanta Liquid Studio | 2 | -- |

   CIC leads 26% of queries against 46% corpus share. Under-represented, not dominant.

The downstream mechanisms the July probe could not measure have since been fixed: CIC normalization (March 2026) and the diversify_results pinning bug (MATTGPT-021, closed May 2026 via MATTGPT-073). The ticket's own supporting evidence, MATTGPT-094, dates from May 2026 and predates both fixes.

**Sample limitation (recorded, not resolved):** The 43 rows in query_log_parsed.csv are a 7% slice of the 609-query production log and skew toward queries typed during testing. The Google Sheet log carries no leading-story column, so the Division count cannot be run over full traffic. Measurement 3 is supporting evidence, not decisive. Measurements 1 and 2 stand on their own.

**Actual overrepresentation:** The Independent Project / MattGPT cluster (MATTGPT-077) and the Professional Narrative cluster (MATTGPT-169). Nine stories each, 8% of corpus each, together leading 51% of queries in the sampled rows.

**Reopen condition:** Leading-story column added to the query logger (MATTGPT-174 shipped this for top_score; a leading-story / Division column is the next step) and full-traffic analysis shows CIC leading disproportionately.

**Verified corpus counts (August 13, 2026, preserved for reference):**
- Cloud Innovation Center: 52 of 114 stories (46%) corpus-wide
- Era "Enterprise Innovation & Transformation": 56 of 114 (49%)
- Cross-tab: 51 of that Era's 56 stories are CIC

The concentration is real. The retrieval dominance claim is not supported by the evidence.

**Cross-references:** MATTGPT-094 (closed -- documented the CIC dominance pattern in May 2026, predates the downstream fixes), MATTGPT-077 and MATTGPT-169 (now carry the actual concentration finding), MATTGPT-181 (early-career story slate was listed here as consolidation lever (c); stands on its own merits, unaffected by this parking).

---

### MATTGPT-010
**Cross-Browser Testing**

- **Status:** Decided Against (May 15, 2026)
- **Priority:** Low (was)
- **Why not:** Trigger expired. Original framing parked this until "React migration" (originally targeted Q1 2026). Q1 has passed; still on Streamlit with no active migration work. If React migration ever happens, cross-browser testing falls out naturally as part of that work — no need for a standing ticket waiting on an uncertain trigger. Streamlit currently handles most cross-browser concerns adequately.
- **Original reason:** Low priority until React migration. Streamlit handles most cross-browser issues.
- **Closed:** May 15, 2026

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
- **Action taken:** code changes from the in-progress fix reverted. Test scaffold from Step 1 (commit `bc280a2`) remains in main; cleanup of the 3 wrong-layer test cases + Step 1 speculative scaffolding deferred to a future small commit. Partial cleanup landed August 26, 2026 (e307d6d): 3 wrong-layer test cases removed. Remaining: ~80 lines of xfail scaffolding (SHOULD_BE_REJECTED_LOWERCASE, SHOULD_BE_ACCEPTED_CLIENT_NAMES, SHOULD_BE_ACCEPTED_TECH_TERMS lists, 3 xfail test methods, MATTGPT-016 comment block) intentionally left in place -- can land in its own small commit; not gating anything.
- **Original ticket context (preserved below for history):**
- **Issue:** Queries about other people score high against valid intent families. Bezos leadership query scores 0.664 as "leadership" — strong match to a wrong subject.
- **Root cause:** Semantic router has no entity/person detection. Only checks embedding similarity to intent families.
- **Fix (rejected):** Add canonical wrong-person phrases to `out_of_scope` family. Same mechanism that already handles off-topic queries — fills a gap, not a new gate layer.
- **Rejected approaches:** Person-name detection before routing (adds gate layer, history shows added gates create complexity and get backed out); lower SOFT_ACCEPT threshold (tried before, caused false rejections on legitimate queries).
- **Affects:** 3 failing tests (Bezos, Elon Musk, "Tell me a joke" scoring 0.429 as "behavioral")
- **Logged:** April 2026 test audit / **Closed:** May 14, 2026

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
- **August 11, 2026 annotation -- two facts in this block are now false:**
  1. "There is no hybrid scoring. W_KW = 0.0." W_KW was re-enabled at 0.15 on August 8 (commit f5641e7, MATTGPT-157 closed). Hybrid scoring is live.
  2. "CONFIDENCE_LOW = 0.15." `constants.py` now has CONFIDENCE_LOW = 0.20.
  The DA reasoning stands -- the ticket was vague and the closure was correct. But the architecture description it used to justify closure is no longer accurate and should not be read as a current statement.
  The revival condition this ticket wrote ("if a real question about threshold calibration emerges in production, file a new ticket with concrete evidence") is exactly MATTGPT-174, filed August 11. -024 predicted its own successor. -174 is the live ticket.
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
- **August 11, 2026 annotation -- one fact in this block is now false:** "CONFIDENCE_LOW=0.15 have been stable since January 2026." `constants.py` now has CONFIDENCE_LOW=0.20. The DA reasoning stands. The revival condition ("specific banner misfire with reproduction, re-file as a concrete bug ticket") is met by MATTGPT-174's three evidence cases ("I do, we do, you do" at 0.260, "Matt?" at 0.291, -162 null-vector shape). -174 is the live ticket.
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

### MATTGPT-075
**Developer debug surfaces leak to user-facing UI**

- **Status:** Decided Against (June 24, 2026) — not a defect. Both reported surfaces (sidebar "Loaded N stories" print, telemetry badge) are gated on `DEBUG`, which is hardcoded `False` in `config/debug.py` and ships False to prod. Parity scan of Ask MattGPT, About Matt, Explore Stories, and Role Match found no ungated user-facing debug surface; the one debug line in Explore Stories is DEBUG-gated and prints to server logs, not the UI. May 18 sighting was a local DEBUG=True session, not a prod leak. No code change.
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

### MATTGPT-103
**Agy intro line — resolve "20+ years of work" inconsistency with stats bar (Years tile dropped)**

- **Status:** Decided Against (May 30, 2026)
- **Priority:** Low
- **Type:** Refactor
- **Decided Against (May 30, 2026):** The "inconsistency" framing was wrong. The stats bar and the Agy intro line are different surfaces doing different jobs. The stats bar is a credentialing surface (recruiter 5-second scan) where the anti-bias play matters most — that's why the Years tile was dropped in MATTGPT-092. The Agy intro line is grounding-the-AI-assistant copy — it tells the user that Agy has a real corpus of career experience to draw from. The "20+ years of work" token there reads as *corpus scope* (how much data the AI has), not as *personal positioning* (how old the candidate is). The anti-bias play that drove the Years tile drop doesn't transfer to a surface doing different work. Closing without a code change. Note (August 19, 2026): `hero.py:174` is a stale reference -- the hero copy has been rewritten; line 174 is now a `</div>` closing tag. Current framing is "my full project history" at approximately line 182, with no year count. The year-count copy this ticket was filed about no longer exists.
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

### MATTGPT-127
**Replace hardcoded `ASSESSMENT_MODEL` in `jd_assessor.py` with `get_conf()` env var pattern**

- **Status:** Decided Against — superseded by MATTGPT-140, which covers the same file and all other hardcoded model literals in the same pass. The `get_conf()` env var approach is also superseded: -140 uses `constants.py` imports, which is simpler and consistent with how `DEFAULT_EMBEDDING_MODEL` is already handled.
- **Priority:** Low
- **Type:** Refactor
- **File:** `services/jd_assessor.py`, `config/constants.py`
- **Logged:** June 12, 2026

**Note preserved for -140:** `gpt-4o` is the correct model for `jd_assessor.py` in production. `gpt-4o-mini` produces subpar assessment reasoning. Do not substitute mini when replacing the literal.

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

### MATTGPT-134
**BDD skip — `test_deeplink_respects_view_mode` — deeplink navigation does not preserve pre-set view mode**

- **Status:** Decided Against (June 24, 2026) — scenario deleted in MATTGPT-144 commit (`77dc1cb`). Confirmed non-feature: deeplinks intentionally start a fresh session with no view persistence. The scenario was testing behavior that doesn't exist and shouldn't.
- **Priority:** Low
- **Type:** Bug
- **Logged:** June 16, 2026

**Context:** Scenario skips at `pytest.skip("Cards view content not found")` in `tests/bdd/steps/test_explore_stories.py` (line 1294). The scenario sets Cards view preference (`Given the user preference is Cards view`), then navigates via deeplink (`When the user navigates to "?story=..."`). The `Then the view should be Cards view` step finds zero `.es-fixed-height-card` elements — the deeplink navigation reverts to Table (the default view) instead of preserving the pre-navigation Cards preference.

**Acceptance criterion:** Either (a) deeplink preserves the active view mode and the scenario passes end-to-end, or (b) the behavior is confirmed intentional (deeplinks always start in Table view) and the scenario is updated to match the confirmed behavior.

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

### MATTGPT-164
**Wrong-person queries reach retrieval -- Satya Nadella passes all gates, returns Accenture content**

- **Status:** Decided Against (duplicate of MATTGPT-063)
- **Priority:** High (was)
- **Type:** Bug
- **Why not:** Confirmed duplicate of MATTGPT-063, "Wrong-person queries with names outside nonsense regex produce confused-context RAG answers," which is open and covers exactly this class of failure. The Satya Nadella trace from August 3, 2026 is a valid exhibit for -063 and should be added there when that ticket is picked up.
- **CRITICAL note preserved:** The MATTGPT-016 Decided Against reasoning ("production already handles this via celebrity regex") is falsified by the Nadella trace. The celebrity regex does not cover names outside its finite list. Any executor picking up MATTGPT-063 must read -016's DA rationale critically and treat the regex-based approach as insufficient for the full class of wrong-person queries.
- **Logged:** August 3, 2026

---

### MATTGPT-115
**Lock icon — browser console warning: password field not in native form**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Console warning only; password manager not saving the access code is correct behavior. No functional impact; fix options (HTML form bridge) are non-trivial for no user-visible gain.
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

- **Status:** Decided Against (August 16, 2026)
- **Why not:** One-line mobile polish (confirmed selector documented in body); not scheduled.
- **Priority:** Low
- **Type:** Bug / Polish
- **File:** `ui/components/why_agy_dialog.py`
- **Logged:** June 9, 2026

**Already shipped (commit `ad3b72f`):** `@media (max-width: 480px)` block in `why_agy_dialog.py` lines 107–124:
- `[role="dialog"]` → `max-height: 88vh; overflow-y: auto` (scroll safety)
- `.why-agy-avatar-row` → `flex-direction: column; align-items: center; gap: 12px` (stacks image above text)
- `.why-agy-illustration` → `max-width: 70px; width: 70px !important` (shrinks image)
- `.why-agy-body p` → `font-size: 14px; line-height: 1.6` (reduces body copy)

Note: image is in a flex row (`display: flex; gap: 20px; flex-shrink: 0`), not a float — ticket originally said "floats right," which was wrong.

**Remaining — one CSS rule:** Dialog title `"Hi, I'm Agy 🐾"` (renamed in commit `56230f2`, before the mobile fix) renders at 24px, font-weight 600 on mobile. Target: 20px.

Selector confirmed via live DOM inspection (Chrome Claude, June 2026). Title `<p>` sits inside `[data-testid="stMarkdownContainer"]` in the dialog's title area, structurally separate from `.why-agy-body` paragraphs. Safe selector:

```css
[role="dialog"] [data-testid="stMarkdownContainer"] p {
    font-size: 20px !important;
}
```

Add this to the existing `@media (max-width: 480px)` block. `[role="dialog"] p:first-of-type` (original proposal) is fragile and should not be used.

---

### MATTGPT-136
**Dark mode design system audit — --accent-purple not overridden in body.dark-theme**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Dark mode audit requires visual review of 41 usages across three semantic categories before any override can be made safely. Not scheduled.
- **Priority:** Low
- **Type:** Refactor
- **Logged:** June 18, 2026

**Context:** `body.dark-theme` in `global_styles.py` overrides `--accent-purple-text` to `#A78BFA` (lighter purple for dark backgrounds) but does NOT override `--accent-purple` or `--accent-purple-bg`. There are 41 usages of `var(--accent-purple)` across the stylesheet spanning text, borders, opaque backgrounds, and semi-transparent tints. In dark mode all 41 resolve to the same `#8B5CF6` as light mode, which may have contrast issues on dark backgrounds.

**Why deferred:** A blanket override of `--accent-purple` to `#A78BFA` in dark mode affects all 41 usages simultaneously. The usages split into three semantic categories with different risk profiles: (1) text/interactive — genuinely need lighter value for contrast; (2) opaque fills/buttons — design choice, either can work; (3) semi-transparent tints derived from the variable — hue change could look off. Changing blindly risks breaking categories 2 and 3 while fixing 1.

**Fix approach:** Visual audit in dark mode across all pages before adding the override. Document which of the 41 usages fall into each category. Override `--accent-purple` only if a majority of usages are category 1, or introduce a new `--accent-purple-accessible` variable for text contexts.

**Acceptance criterion:** Dark mode visual review complete, override decision documented, no contrast failures on text usages of --accent-purple in dark mode.

---

### MATTGPT-147
**Stale `@pytest.mark.skip` on `test_mobile_desktop_only_message` — decorator predates step def**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Stale skip; step def exists (lines 403-416). One-line delete + isolation run. Not scheduled.
- **Priority:** Low
- **Type:** Bug
- **File:** `tests/bdd/steps/test_role_match.py`
- **Logged:** July 1, 2026

**Issue:** `test_mobile_desktop_only_message` is skipped by a stale decorator at lines 170–175. The skip reason says "Needs hamburger interaction" — but that interaction was implemented at lines 403–416 (`given_viewport_at_explicit_width`). The decorator was written before the step def existed and was never removed.

**Action:** Remove the `@pytest.mark.skip` decorator at lines 170–175. Run in isolation:
```
pytest tests/bdd/steps/test_role_match.py::test_mobile_desktop_only_message -v
```
If it passes, commit. If it fails, the step def has a bug — diagnose before committing.

**Acceptance criteria:**
- `test_mobile_desktop_only_message` passes in isolation and in the full suite with no skip decorator.

---

### MATTGPT-148
**`.main` selector sweep — 36 dead selectors in `global_styles.py` need swapping to `.stMain`**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** 36 dead .main selectors; layout works through other means. Swap path (grep + review + .stMain) documented. Not scheduled.
- **Priority:** Low
- **Type:** Refactor
- **File:** `ui/styles/global_styles.py`
- **Logged:** July 1, 2026

**Issue:** `.main` does not exist in current Streamlit. The correct selector is `.stMain`. `global_styles.py` contains 36 rules scoped to `.main[^a-zA-Z]` — all dead selectors that match nothing. Any layout or spacing rules under these selectors are silently not applying.

**Action:**
1. Confirm count: `grep -n "\.main[^a-zA-Z]" ui/styles/global_styles.py`
2. Review each occurrence — verify intent is `.stMain` before swapping (some may be legitimate class names that happen to start with `.main`).
3. Swap confirmed dead selectors to `.stMain`.
4. Smoke-test desktop and mobile after change — dead selectors becoming live may reveal previously masked layout shifts.

**Acceptance criteria:**
- Zero `.main` selectors in `global_styles.py` that should be `.stMain`.
- No visual regression at desktop and 375px mobile after the swap.

---

### MATTGPT-149
**Rejection bubble dark mode — `[class*='_rejection_bubble']` missing dark mode override**

- **Status:** Decided Against (August 16, 2026)
- **Why not:** Dark mode visual; dark mode not actively tested. Fix path (body.dark-theme override for --banner-info-bg) documented. Not scheduled.
- **Priority:** Low
- **Type:** Bug
- **File:** `ui/styles/global_styles.py` (or wherever `_rejection_bubble` is defined)
- **Logged:** July 1, 2026

**Issue:** The rejection bubble component uses `var(--banner-info-bg)` for its background. There is no `body.dark-theme` override for this variable or this selector, so the bubble renders with the light-mode background color in dark mode.

**Fix:** Add a `body.dark-theme` override — either for `--banner-info-bg` directly (if it's safe to change globally) or scoped to `[class*='_rejection_bubble']` specifically. Confirm the override value against the dark mode palette in `global_styles.py` before applying.

**Acceptance criteria:**
- Rejection bubble background is visually appropriate in both light and dark mode.
- No other surfaces that use `var(--banner-info-bg)` are unintentionally affected.

---

