# BACKLOG

---

## Completed (March 2026)

### diversify_results Pinning Fix
**Issue:** `diversify_results()` was reordering stories and displacing the primary story (e.g., D&F query: Row 40 ranked #1 but LLM talked about Row 28/AmEx)
**Resolution:** Fixed pinning logic so primary story stays #1 after diversification

### CIC Entity Alias
**Issue:** "CIC" acronym not recognized by entity detector — embedding model doesn't connect "CIC" to "Cloud Innovation Center"
**Resolution:** Added `ENTITY_ALIASES` to `config/constants.py`, alias check in `detect_entity()`. "CIC" now resolves to Division: Cloud Innovation Center.

### SYNTHESIS_DELTA Reconciliation
**Issue:** SYNTHESIS_DELTA still had old "reference each story" framing, not aligned with WHY→HOW→WHAT
**Resolution:** Rewrote with tension-first flow (WHY 30-40%, HOW 40-50%, WHAT 10-20%), coverage rule changed to "lead with 2-3 most relevant, don't force-fit"

### Voice Guide V2 Update
**Issue:** Voice Guide V2 in design spec conflicted with prompts.py — WHY meant "outcomes" in one, "tension" in the other
**Resolution:** Reconciled across `05-agy-voice-guide.md`, `prompts.py`, `ARCHITECTURE.md`. WHY=tension/stakes everywhere.

### IQ Differentiation (Leadership + CIC)
**Issue:** Leadership and CIC stories lacked differentiation in Situation/Use Case fields — Pinecone couldn't distinguish them
**Resolution:** Data quality pass on Excel master — enriched Situation fields with resistance narratives, specific context

### TDD/BDD Story Rewrite
**Issue:** TDD methodology story had weak Situation field, BDD story surfacing instead for TDD queries
**Resolution:** Rewrote Situation with resistance narrative, re-ingested data

### 2. Eval Cases for "Tell me more about: [Title]" ✅
**Was:** No test coverage for Related Projects "tell me more" pattern
**Resolution:** Q53-Q57 added as regression guards covering title-based and entity-based queries. Title soft-filtering working correctly.

### 5. Delete META_SENTENCE_PATTERNS Regex ✅
**Was:** Band-aid for prompt conflict; monitoring period complete
**Resolution:** Prompt rewrite (#1) eliminated the root cause. No meta-commentary violations in eval.

### 6. Remove boost_narrative_matches() ✅
**Was:** Title now embedded in Pinecone, function potentially dead code
**Resolution:** Semantic search handles narrative story ranking naturally. Function removed.

### 7. Centralize Hardcoded Values ✅
**Was:** Thresholds, model names, token limits scattered across 6+ files
**Resolution:** `config/constants.py` created as single source of truth. All files import from there.

### 18. Pinecone Index as Env Var ✅
**Was:** `index_name="portfolio-stories"` hardcoded
**Resolution:** Moved to environment variable via `get_conf()` pattern.

### 30. Fix "Builder/Modernizer" Verbatim Quoting ✅
**Was:** Agy quoting poetic language from 5PSummary verbatim in synthesis responses
**Resolution:** Data fix — updated 5PSummary to concrete language in Excel master, re-indexed.

### 31-35. New Development Stories ✅
**Was:** 5 story ideas (RAG Pipeline Cleanup, State Management Debugging, Building MattGPT, Eval-Driven Development, AI-Assisted Development)
**Resolution:** All 5 stories added in Feb 3 session (#39). 130 stories total.

### 8. Dead Code Cleanup (Partial) ✅
**Remaining:** Audit `services/query_logger.py` (orphaned Google Sheets logger — dependencies removed, kept for potential re-integration), `utils/scoring.py` for unused functions, sweep old TODO/FIXME comments

---

## Completed (February 2026)

### 38. Excel→JSONL Script Bug Fixes ✅
Fixed `normalize()` for pandas NaN, `split_bullets()` for Excel escape apostrophe.

### 39. New MattGPT Development Stories ✅
Added 5 stories: Why Hire Matt, Entity Gate Removal, Eval-Driven Development, BDD, AI-Assisted Workflows. 130 total.

### 40. Design Spec Testing Docs Consolidation ✅
Consolidated into `docs/11-testing-and-quality.md` covering 3-layer strategy.

### 23. Stale Story on Return to Explore Stories ✅
Widget version incrementing in `_clear_explore_state()`. Fixed Feb 1.

### 25. BDD/E2E Tests for Explore Stories State Machine ✅
43 BDD scenarios using pytest-bdd + Playwright. All passing. Feb 1-2.

---

## Completed (January 2026)

### RAG Pipeline Cleanup (Jan 29)
- Entity Gate removed (was causing false rejections)
- `classify_query_intent` LLM removed (redundant with semantic router)
- Eval improved from 96.4% to 98.1%

### 1. Fix Prompt Conflict ✅ (Jan 26)
Created `prompts.py` with BASE_PROMPT + DELTA architecture. Meta-commentary failures reduced from 10/31 → 1-2/31.

### 9. Semantic Router Fail-Open Handling ✅ (Jan 26)
Verified fail-open behavior: returns `(True, 1.0, "", "error_fallback")` on exception.

### 10. Threshold Calibration ✅ (Jan 26)
Lowered SOFT_ACCEPT from 0.72 to 0.40. Entity Gate removed entirely Jan 29.

### 11. Remove ENTITY_NORMALIZATION Hardcoded Map ✅ (Jan 26)
Semantic search handles variations naturally. Removed map and fuzzy matching.

### 12. Add Observability Logging ✅ (Jan 26)
Added `[QUERY_REJECTED]` and `[API_ERROR_DETECTED]` log tags.

### 14. Fix SEARCH_TOP_K Conflict ✅ (Jan 30)
Centralized to `config/constants.py` with value 10.

### 20. Deeplink Regression ✅ (Jan 30)
Fixed page offset calculation for story deeplinks.

### 21. Search State Clearing ✅ (Jan 30)
Surgical fix: only clear `active_story` when query actually changes.

### 22. "Ask Agy About This" Regression ✅ (Jan 30)
Fixed by surgical state clearing in #21.

### 24. 6 Sources on Surgical Queries ✅ (Jan 31)
Added query_intent check: synthesis gets 6 sources, surgical gets 3.

### 4. Audit Excel Master for Corporate Filler ✅ (Jan 28)
Deleted BANNED_PHRASES entirely — was testing for imaginary problems.

### Sovereign Backlog #1: Multi-Field Entity Blind Spot ✅ (Jan 22)
Entity filter now searches 6 fields with Pinecone `$or` operator.

### Sovereign Backlog #3: Dynamic Prompting ✅ (Jan 22)
`generate_dynamic_dna()` derives clients by industry from story data.

### UI Metrics Hydration ✅ (Jan 22)
All project/client counts derived dynamically from JSONL across 4 files.

---

## Open — Next Up

### JD Match and Fit Assessment
**Priority:** HIGH
**Status:** Groomed, design decisions resolved — ready for implementation spec

**User Stories:**
- As a recruiter or hiring manager, I want to paste a job description and see how Matt's experience maps to the requirements, so I can quickly assess fit without reading an entire resume
- As Matt, I want to privately assess my fit against a role before deciding to apply, so I can prioritize time on highest-fit opportunities and update my Notion tracker

**Acceptance Criteria — Recruiter view:**
- Text area accepts a pasted job description
- Output shows required/preferred qualifications with match status (✓ strong / ~ partial / ✗ gap)
- Each matched qualification links to 1-2 supporting STAR stories by title and client
- Partial matches explain what matches and what is missing
- Story links expand inline using `render_story_detail()` (same pattern as Related Projects in Ask MattGPT)
- Match count shown (e.g., "7/7 req") — factual, not scored
- NO fit score or recommendation in recruiter view — let the evidence speak
- Output is clean, scannable, professional — no conversational filler

**Acceptance Criteria — Private view (Matt only):**
- Same structured output plus overall fit score: High / Medium / Low
- "Strong match" / "Partial match" / "Weak match" headline label
- Gap section shows requirements with no supporting stories
- Recommendation: Apply / Consider / Pass
- Password-gated via discreet lock icon in nav bar far right — recruiter never sees the prompt
- Agentic access bypasses UI gate via environment secret (for Notion automation)

**Acceptance Criteria — Both:**
- New navigation tab: "Role Match" (5th tab, between Ask MattGPT and About Matt)
- Two-column layout: paste JD left, read results right
- Three-step pipeline: LLM extraction → per-requirement Pinecone retrieval via pinecone_service.py → LLM assessment (see ADR 016). Uses shared Pinecone infrastructure, not Ask MattGPT RAG pipeline.
- Story evidence is specific: title and client, not just theme
- Works across varied JD formats (bulleted, narrative, mixed)

**Mobile:** Desktop-only for v1. Feature hidden or shows "best on desktop" message at mobile breakpoints. Consistent with existing Share/Export behavior. Recruiter fit assessment is a desk task.

**Out of scope for v1:**
- LinkedIn URL scraping
- Automatic Notion API sync — manual copy of fit score acceptable
- Multiple JD comparison
- Side-by-side resume comparison
- Mobile-optimized layout

**Resolved design decisions (Mar 25, 2026):**
- Tab name: "Role Match"
- Lock icon: nav bar far right, subtle, recruiter doesn't notice
- Recruiter view: evidence only, no score — match count (7/7) is factual, fit label is private
- Story evidence: inline expansion via `render_story_detail()`, not navigation to Explore Stories
- Layout: two-column (paste left, results right)

**Open questions:**
- Agentic access token mechanism — environment variable or Streamlit secret
- Technology stack matching — extraction prompt `type` field (experience | skill | education | domain) doesn't distinguish technology-specific requirements. A `.NET Core` requirement vs a `cloud-native experience` requirement need different match confidence. Consider adding `technical_stack` type so Stage 2 matching can differentiate: (1) language/paradigm match — transferable but not primary stack, (2) framework match — specific framework gap is harder to bridge, (3) transferable — cloud, CI/CD, databases where the concept transfers regardless of vendor. This affects private gap view accuracy.

**Size:** Large
**Dependencies:** Existing RAG pipeline, Pinecone index, story corpus, LLM extraction prompt (design session required before implementation)

### JPM Payments IQ Differentiation
**Priority:** HIGH
**Issue:** JP Morgan payments stories lack differentiation in Situation/Use Case fields — Pinecone can't distinguish them from other JPM work
**Fix:** Data quality pass on JPM payments stories in Excel master, similar to CIC/Leadership differentiation done in March

### Story Count Code Fix
**Priority:** MEDIUM
**Issue:** Code references "130+" stories in multiple places — this number will drift as stories are added/removed
**Fix:** Remove hardcoded "130+" and derive count from JSONL at runtime, or remove the number entirely

### 3. Simplify backend_service.py
**Priority:** MEDIUM
**Issue:** 600+ lines, imports from 4+ modules. Candidates for extraction: entity detection, prompt building.
**Status (Jan 29):** Entity Gate removed, classify_query_intent removed. Still large.

### Analytics Integration
**Priority:** HIGH
**Story ID:** MATTGPT-011
**Issue:** No visibility into who's using the app, what queries they're asking, or which stories get viewed. Need usage data to prioritize improvements.
**Blocker:** `streamlit-analytics2` caused `AttributeError` on `st.session_state` — wrapper runs before Streamlit initializes session state (Jan 12, 2026). Backed out same day.
**Fix:** Add wrapper AFTER session state init in `app.py`, or use manual `gtag.js` injection via `st.components.html()` as fallback.
**Existing code:** `services/query_logger.py` (Google Sheets logger, orphaned but intact — could complement GA4)

### Data Quality Cleanup Journey Story
**Priority:** MEDIUM
**Issue:** The March 2026 data quality work (CIC pairing, IQ differentiation, Situation enrichment across 85+ stories) is a compelling story about systematic data improvement for AI systems
**Action:** Write as STAR story for portfolio — covers pattern recognition, data quality discipline, measurable impact on retrieval accuracy

### Semantic Router: Wrong-Person Query Detection
**Priority:** HIGH
**Issue:** Queries about other people ("What's Jeff Bezos's leadership style?", "Tell me about Elon Musk") score high against valid intent families because the router matches semantic content (leadership, biography) without checking WHO the query is about. Bezos leadership query scores 0.664 as "leadership" — a strong match to a wrong subject.
**Root cause:** Semantic router has no entity/person detection. It only checks embedding similarity to intent families.
**Fix options:**
1. Add person-name detection before routing — if query mentions a name that isn't Matt/he/him, classify as out_of_scope
2. Add canonical "wrong person" phrases to out_of_scope family ("Tell me about [other person]", "[celebrity name]'s leadership")
3. Lower SOFT_ACCEPT threshold — risky, could reject legitimate queries
**Affects:** 3 failing tests (Bezos, Elon Musk, "Tell me a joke" — joke scores 0.429 as "behavioral")
**Diagnosed:** Apr 2026 test audit

### diversify_results() Pinning Bug
**Priority:** MEDIUM
**Issue:** Two related bugs in `diversify_results()`:
1. Pinned story (result #1) is not counted toward `max_per_client` limit — a client can appear max_per_client + 1 times
2. Client diversity reordering breaks score ordering guarantee — test expects descending scores but diversification shuffles order
**Root cause:** Pinning logic (line ~1313 in backend_service.py) tracks seen_clients but doesn't include the pinned result in the count
**Fix:** Count pinned client toward limit, then restore score ordering after diversification pass
**Affects:** 2 failing tests (test_limits_single_client_stories, test_maintains_overall_order)
**Diagnosed:** Apr 2026 test audit

### LLM Meta-Commentary on Q20 (Stochastic)
**Priority:** LOW
**Issue:** "Who is Matt Pugmire?" sometimes generates meta-commentary ("showcases his") instead of direct biographical content. Stochastic — passes on some runs, fails on others.
**Root cause:** LLM occasionally ignores the "never evaluate Matt" prompt instruction for broad biographical queries
**Fix:** Monitor — if it becomes consistent, add Q20-specific prompt reinforcement
**Diagnosed:** Apr 2026 test audit

---

## Open — Low Priority

### 15. Clarify Hybrid Scoring
**Issue:** Pinecone scores (0.0-1.0) don't map clearly to confidence buckets (0.15-0.25)
**Fix:** Document or align the scoring systems

### 16. Add Error Handling Tests
**Issue:** Test suite only covers happy path
**Fix:** Add tests for rate limits, timeouts, embedding failures

### 17. Clarify Layer Ownership
**Issue:** Ranking, intent classification, and formatting split across multiple files
**Fix:** Document contracts or refactor boundaries

### 19. Quarterly Intent Review
**Issue:** 13 intent families with ~20 phrases each in semantic_router.py
**Fix:** Schedule quarterly review for relevance
**Last review:** Jan 29, 2026

### 26. Share Link Copy Functionality
**Issue:** Verify share link copy-to-clipboard works correctly across browsers

### 27. Low-Confidence Banner Edge Cases
**Issue:** Low-confidence banner sometimes triggers incorrectly. Review threshold logic.

### 28. Related Projects Selection State
**Issue:** Edge cases in purple highlight, close toggle, rapid clicks

### 29. Semantic Router Error Path Coverage
**Issue:** Limited test coverage for semantic router error handling paths

### 36. LLM Response Broken Markdown
**Issue:** LLM outputs `**4X **` instead of `**4X**` — space before closing asterisks breaks bold
**Fix:** Post-process regex: `r'\*\*([^*]+)\s+\*\*'` → `**\1**`

### 37. Ask Agy Button Shifts on Focus
**Issue:** Button shifts position when focused. CSS fix for focus state.

### 8. Dead Code Cleanup (Remaining)
**Issue:** Audit `services/query_logger.py` (orphaned but kept), `utils/scoring.py` for unused functions, sweep old TODO/FIXME comments.

### Sovereign Backlog #4: Eval Modernization — Semantic Scoring
**Issue:** Current eval uses keyword matching. Semantic similarity or LLM-as-Judge would be more robust.
**Trade-off:** More expensive per run, harder to debug failures. Current concept-cluster approach (Q2/Q5 style) may be good enough.

---

## Parked

### Cross-Browser Testing
**Story ID:** MATTGPT-010
**Reason:** Low priority until React migration. Streamlit handles most cross-browser issues.

---

## Decided Against

### Entity Cluster Promotion Override
**What:** Override synthesis mode when 3+ stories from the same entity are in the Pinecone pool (e.g., "How did you build the CIC?" gets 10 CIC stories → forces synthesis)
**Why not:** Overriding would break legitimate synthesis queries like "Tell me about all your CIC work." The real fix is better data differentiation so the right story ranks clearly #1, not routing logic.

### Score Gap Override (Generic-Above-Named)
**What:** Boost named client stories over "Fortune 500 Clients" generic stories in Pinecone results
**Why not:** Adds a ranking layer on top of semantic search. Better to fix at the data level — enrich generic stories with distinguishing context, or merge them into named client stories where appropriate.

### 13. Centralize Constants (Duplicate)
**What:** Separate request to centralize constants
**Why not:** Duplicate of #7. Consolidated there. `config/constants.py` is the single source of truth.
