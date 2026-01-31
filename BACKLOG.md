# BACKLOG

## January 29, 2026 - RAG Pipeline Cleanup

### Entity Gate Removal ✅ DONE
**Priority:** HIGH
**Issue:** Entity Gate was causing false rejections on legitimate queries
**Resolution (Jan 29, 2026):**
- Removed `ENTITY_GATE_THRESHOLD` and related gating logic from `backend_service.py`
- Entity detection still runs for Pinecone filtering, but no longer blocks queries
- Eval improved from 96.4% to 98.1%

### classify_query_intent LLM Removal ✅ DONE
**Priority:** HIGH
**Issue:** Extra LLM call for intent classification was redundant with semantic router
**Resolution (Jan 29, 2026):**
- Removed `classify_query_intent()` function entirely
- Synthesis detection moved to semantic router (`synthesis` intent family)
- Out-of-scope detection moved to semantic router (`out_of_scope` intent family)
- Reduces latency and API costs

---

## January 25, 2026 - Tech Debt from RAG Audit

### 1. Fix Prompt Conflict ✅ DONE
**Priority:** HIGH
**Issue:** System prompt says "Emphasize X" but also "NEVER meta-commentary" — LLM can't satisfy both
**Evidence:** `META_SENTENCE_PATTERNS` regex fires frequently catching violations
**Fix:** Rewrite prompt to remove conflicting instructions
**Resolution (Jan 26, 2026):**
- Created `prompts.py` with BASE_PROMPT + SYNTHESIS_DELTA + STANDARD_DELTA architecture
- Removed `get_theme_guidance()` which had conflicting "Emphasize:" instructions
- Removed `BANNED_PHRASES_CLEANUP` post-processing bandaid
- Meta-commentary failures reduced from 10/31 → 1-2/31 (LLM variance)

### 9. Semantic Router Fail-Open Handling ✅ DONE
**Priority:** MEDIUM
**Issue:** When semantic router has connection error, system falls back to off-topic guard
**Evidence:** "Semantic router error: Connection error." → "I can't help with that..."
**Expected:** Skip intent classification, proceed with RAG, return actual results
**Resolution (Jan 26, 2026):**
- Verified `is_portfolio_query_semantic()` already returns `(True, 1.0, "", "error_fallback")` on exception
- Added clearer logging: "FAILING OPEN" message with network error hints
- `semantic_valid=True` + `score=1.0` ensures query proceeds to entity detection and RAG
- No special handling for `error_fallback` in backend_service.py that would reject

### 10. Threshold Calibration ✅ DONE
**Priority:** HIGH
**Issue:** Legitimate queries like "Tell me about the CIC" (score 0.41) and "What problems does Matt solve?" (score 0.38) were being rejected
**Evidence:** Score analysis showed garbage queries at 0.11-0.27, legitimate queries at 0.30+
**Resolution (Jan 26, 2026):**
- Lowered SOFT_ACCEPT from 0.72 to 0.40 in `semantic_router.py`
- Entity Gate removed entirely (Jan 29, 2026) - no threshold needed
- Added threshold boundary tests in `test_structural_assertions.py` to catch regressions

### 11. Remove ENTITY_NORMALIZATION Hardcoded Map ✅ DONE
**Priority:** MEDIUM
**Issue:** Hardcoded alias map ("jpmorgan"→"JP Morgan Chase", "amex"→"American Express") was drifting from JSONL data
**Evidence:** Attempting fuzzy matching led to false positives ("matt" matching "MattGPT Product Development")
**Resolution (Jan 26, 2026):**
- Tested and proved semantic search handles variations naturally ("JPMC", "amex", "CIC" all return correct stories)
- Removed ENTITY_NORMALIZATION map and fuzzy matching functions from `backend_service.py`
- Entity detection now uses exact case-insensitive matching only

### 12. Add Observability Logging ✅ DONE
**Priority:** MEDIUM
**Issue:** No visibility into why queries get "I can't help with that" response in production
**Resolution (Jan 26, 2026):**
- Added `[QUERY_REJECTED]` log tag for low-pinecone rejections (includes router_family, router_score, pinecone_score)
- Added `[API_ERROR_DETECTED]` log tag for router failures with "breather" message fallback
- Logs help diagnose whether rejections are from semantic router or Pinecone confidence

### 13. Centralize Constants ✅ DUPLICATE
**Priority:** MEDIUM
**Issue:** Thresholds, model names, token limits scattered across 6+ files
**Status:** Duplicate of #7 (Centralize Hardcoded Values) - consolidated there

---

## Open Items

### 2. Add Eval Cases for "Tell me more about: [Title]"
**Priority:** MEDIUM
**Issue:** No test coverage for the Related Projects "tell me more" pattern
**Fix:** Add 3-5 eval cases like "Tell me more about: Platform Modernization at JPMC"
**Status (Jan 29, 2026):** Eval now at 98.1% (60/61 cases). Title soft-filtering implemented - titles detected but semantic search ranks naturally. Still need specific "tell me more" eval cases.

### 3. Simplify backend_service.py
**Priority:** MEDIUM
**Issue:** 600+ lines (was 800+ before cleanup), imports from 4+ modules
**Fix:** Extract entity detection and mode logic into separate modules
**Status (Jan 29, 2026):** Entity Gate removed, classify_query_intent removed. Still candidates for extraction: entity detection, prompt building.

### 5. Delete META_SENTENCE_PATTERNS Regex
**Priority:** MEDIUM (unblocked — #1 is done)
**Issue:** Band-aid for prompt conflict; should be unnecessary after #1
**Fix:** After fixing prompt, monitor for 1 week, then delete if no violations
**Status (Jan 29, 2026):** #1 completed Jan 26. Monitoring period complete. Ready to delete if eval confirms no meta-commentary issues.

### 6. Remove boost_narrative_matches()
**Priority:** LOW
**Issue:** Title is now embedded in Pinecone, so semantic search naturally finds narrative stories
**Status:** Function still exists but may be dead code
**Fix:** Verify with eval, then delete from `rag_service.py`

### 7. Centralize Hardcoded Values
**Priority:** MEDIUM
**Issue:** Hardcoded values scattered across files
**Categories identified (RAG Audit):**
- Thresholds: CONFIDENCE_HIGH, CONFIDENCE_LOW, SOFT_ACCEPT
- Model names: text-embedding-3-small, gpt-4o-mini
- Token limits: MAX_TOKENS, context windows
- Pinecone: index name, top_k values
**Fix:** Create `config/constants.py` with all configurable values

### 8. Dead Code Cleanup
**Priority:** LOW
**Files to audit:**
- `services/query_logger.py` - orphaned Google Sheets logger
- `utils/scoring.py` - may have unused functions
- Any `# TODO` or `# FIXME` comments older than 30 days

### 14. Fix SEARCH_TOP_K Conflict ✅ DONE
**Priority:** MEDIUM
**Issue:** `SEARCH_TOP_K = 100` in pinecone_service.py, `SEARCH_TOP_K = 7` in backend_service.py
**Resolution (Jan 30, 2026):** Centralized to `config/constants.py` with value 10 (headroom for reranking)

### 15. Clarify Hybrid Scoring
**Priority:** MEDIUM
**Issue:** Pinecone scores (0.0-1.0) don't map clearly to confidence buckets (0.15-0.25)
**Fix:** Document or align the scoring systems

### 16. Add Error Handling Tests
**Priority:** MEDIUM
**Issue:** Test suite only covers happy path
**Fix:** Add tests for rate limits, timeouts, embedding failures

### 17. Clarify Layer Ownership
**Priority:** LOW
**Issue:** Ranking, intent classification, and formatting split across multiple files
**Fix:** Document contracts or refactor boundaries

### 18. Pinecone Index as Env Var
**Priority:** LOW
**Issue:** `index_name="portfolio-stories"` hardcoded
**Fix:** Move to environment variable

### 19. Quarterly Intent Review
**Priority:** LOW
**Issue:** 13 intent families (was 11) with ~20 phrases each in semantic_router.py
**Families:** background, behavioral, delivery, team_scaling, leadership, technical, domain_payments, domain_healthcare, stakeholders, innovation, agile_transformation, narrative, synthesis, out_of_scope
**Fix:** Schedule quarterly review for relevance
**Last review:** Jan 29, 2026

---

## January 29-30, 2026 - Explore Stories Bugs

### 20. Deeplink Regression ✅ FIXED
**Priority:** HIGH
**Issue:** Share deeplink `?story=story-id` opens Cards view but doesn't display story detail
**Evidence:** `http://localhost:8501/?story=driving-cloud-native-innovation-through-ticara-framework%7Caccenture` shows Cards view, no detail panel
**Resolution (Jan 30, 2026):**
- Root cause: Story not on page 1, detail only renders if story is in visible page
- Fix: Calculate correct page offset in `explore_stories.py` based on story index in full list
- Rerun if offset needs to change, set `active_story_obj` for `get_context_story()`
**Files:** `explore_stories.py` (DEEPLINK PAGINATION FIX section)

### 21. Search State Clearing ✅ FIXED
**Priority:** HIGH
**Issue:** Searching in Explore Stories didn't clear previous `active_story`, causing wrong story detail to display
**Evidence:** Search "TICARA" → correct results → detail panel showed "Scaling Talent..." from previous selection
**Resolution (Jan 30, 2026):**
- Initial fix was too aggressive (cleared on every state change, broke "Ask Agy About This")
- Surgical fix: Only clear `active_story` in PATH 1 when query actually changes (`current_query != previous_query`)
- Preserves `active_story` for: filter changes, view switching, deeplinks, "Ask Agy About This"
**Files:** `explore_stories.py` (SURGICAL FIX comment in search logic)

### 22. "Ask Agy About This" Regression ✅ FIXED
**Priority:** HIGH
**Issue:** "Ask Agy About This" button stuck on loading spinner, never redirected to Ask MattGPT
**Root cause:** Aggressive state clearing from #21 initial fix was clearing `active_story` needed for navigation
**Resolution (Jan 30, 2026):** Surgical fix in #21 preserves `active_story` for "Ask Agy About This" flow

### 23. Stale Story on Return to Explore Stories
**Priority:** LOW
**Issue:** Returning to Explore Stories from another tab shows previously selected story
**Status:** Open - low priority, doesn't break core functionality

### 24. 6 Sources on Surgical Queries ✅ FIXED
**Priority:** MEDIUM
**Issue:** "Ask Agy About This" returns 6 sources, should be 3 for surgical/tree search
**Resolution (Jan 31, 2026):** Added query_intent check in conversation_helpers.py - synthesis gets 6 sources (forest), surgical gets 3 (tree)

### 25. BDD/E2E Tests for Explore Stories State Machine
**Priority:** HIGH (Tech Debt)
**Issue:** No automated tests for Explore Stories interactive state
**Effort:** 3-4 hours
**Coverage needed:**
- Search flow (clears stale state, opens correct detail, empty results)
- "Ask Agy About This" flow (Table, Cards views)
- Deeplink flow (valid/invalid story IDs)
- View switching (preserves detail, query, filters)
- Navigation return
- Filter combinations (Industry, Capability, Advanced)
- Pagination
- Reset behavior
**Widgets:** Find stories, Industry, Capability, Advanced Filters, Client/Role/Domain multiselects, Reset, Page size, View toggle, Pagination
**Recommendation:** Playwright for Streamlit widget interaction

### 26. Share Link Copy Functionality
**Priority:** LOW
**Issue:** Verify share link copy-to-clipboard works correctly
**Fix:** Test across browsers (Chrome, Safari, Firefox)

### 27. Low-Confidence Banner Edge Cases
**Priority:** LOW
**Issue:** Low-confidence banner sometimes triggers incorrectly
**Fix:** Review threshold logic and test with edge case queries

### 28. Related Projects Selection State
**Priority:** LOW
**Issue:** Edge cases in Related Projects selection (purple highlight, close toggle)
**Fix:** Verify single-selection behavior, test rapid clicks

### 29. Semantic Router Error Path Coverage
**Priority:** MEDIUM
**Issue:** Limited test coverage for semantic router error handling paths
**Fix:** Add tests for connection errors, timeout, malformed responses

### 36. LLM Response Broken Markdown
**Priority:** LOW
**Issue:** LLM outputs `**4X **` instead of `**4X**` - space before closing asterisks breaks bold rendering
**Fix:** Post-process regex: `r'\*\*([^*]+)\s+\*\*'` → `**\1**`

### 37. Ask Agy Button Shifts on Focus
**Priority:** LOW
**Issue:** Ask Agy button shifts position when focused
**Fix:** CSS fix for button focus state

### 30. Fix "Builder/Modernizer" Verbatim Quoting (Data Fix)
**Priority:** MEDIUM
**Issue:** Agy quotes "I'm a builder, a modernizer..." verbatim in synthesis responses
**Root Cause:** The "About Matt – My Leadership Journey" story has poetic language in 5PSummary field
**Fix:**
1. Edit Excel master → update 5PSummary to concrete language
2. Regenerate JSONL: `python scripts/generate_jsonl_from_excel.py`
3. Re-index Pinecone: `python scripts/index_to_pinecone.py`
**Note:** This is a DATA fix, not a code fix

---

## New Stories to Add (from Jan 28-30 Sessions)

**Priority:** LOW (content creation, not bugs)
**Purpose:** Director/VP-relevant stories demonstrating leadership + technical depth

### 31. RAG Pipeline Cleanup / Entity Gate Removal
- **Situation:** Multiple overlapping LLM gates causing false rejections (TICARA bug)
- **Task:** Simplify architecture while maintaining quality
- **Action:** Removed 132 lines, consolidated to semantic router, implemented soft filtering
- **Result:** 98% eval, faster queries, cleaner code
- **Signals:** Architectural decision-making, knowing when to remove vs. add

### 32. State Management Debugging
- **Situation:** "Ask Agy About This" and deeplinks broken by well-intentioned fix
- **Task:** Fix search bug without breaking other flows
- **Action:** Surgical state clearing (only when query changes), deeplink pagination fix
- **Result:** All core flows working, identified need for BDD tests
- **Signals:** System thinking, debugging complex interactions, prioritization

### 33. Building MattGPT as Product Differentiator
- **Situation:** Job search in competitive market
- **Task:** Stand out from other Director/VP candidates
- **Action:** Built AI-powered portfolio from scratch (RAG, embeddings, Streamlit)
- **Result:** "Interview me before you interview me" - recruiters can explore 20 years of work
- **Signals:** Product thinking, initiative, modern tech fluency

### 34. Eval-Driven Development
- **Situation:** Non-deterministic LLM outputs, hard to test
- **Task:** Create reliable quality checks
- **Action:** 52+ golden queries, automated eval, confidence scoring
- **Result:** Catch regressions before deploy, 98% pass rate
- **Signals:** Quality engineering, testing strategy for non-deterministic systems

### 35. AI-Assisted Development Meta-Story
- **Situation:** Using Claude/Claude Code to build Claude-powered product
- **Task:** Navigate AI tooling while building AI product
- **Action:** Multi-agent workflow, context management, knowing when to revert
- **Result:** Lessons on AI collaboration, when to trust vs. verify
- **Signals:** Future of work, AI collaboration, meta-awareness

---

## Closed/Resolved Items

### 4. Audit Excel Master for Corporate Filler ✅ DONE
**Priority:** LOW
**Issue:** BANNED_PHRASES list keeps growing; should fix at source
**Fix:** Grep Excel master for "meaningful outcomes", "foster collaboration", etc. and rewrite
**Resolution (Jan 28, 2026):** Deleted BANNED_PHRASES entirely - was testing for imaginary problems that never appeared in responses. "meaningful outcomes" was Matt's actual words being quoted correctly.

---

## January 21, 2026 - RAG Eval Quality Sprint

#### Sovereign Backlog (Real Issues for Next Sprint)

**1. Multi-Field Entity Blind Spot** ✅ DONE
- ~~System treats `Client` as only source of truth~~
- ~~Need entity detection across `Employer`, `Division`, `Project`, `Place`~~
- ~~Example: Accenture stories where Client="Confidential Healthcare Provider" should still be discoverable as Accenture work~~
- **Implementation (Jan 22, 2026):**
  - Updated `pinecone_service.py:189-216` to use Pinecone `$or` operator
  - Entity filter now searches across all 6 fields: `client`, `employer`, `division`, `project`, `place`, `title`
  - Applied correct casing per field (lowercase for division/employer/project/place, PascalCase for client)
  - Eval: 100% pass rate (31/31) - no regression

**3. Dynamic Prompting - Hardcoded Client Names** ✅ DONE
- Synthesis prompt now derives clients dynamically
- MATT_DNA now derives all client names from JSONL (banking, telecom, transport)
- Fixed "JPMorgan" → "JP Morgan Chase" (now matches JSONL source)
- Removed phantom industries from `cross_industry_landing.py` (Manufacturing, Retail & Consumer Goods)
- Eval: 100% pass rate (31/31)

**Implementation (Jan 22, 2026):**
- `generate_dynamic_dna()` derives clients by industry from story data
- Banking clients: derived from `Industry = "Financial Services / Banking"`
- Telecom clients: derived from `Industry = "Telecommunications"`
- Transport clients: derived from `Industry = "Transportation & Logistics"`

**4. Eval Modernization - Semantic Scoring**
- Current: Exact string match for ground_truth
- Problem: "Whack-A-Mole" with LLM stochasticity
- Solution: Semantic similarity or LLM-as-Judge scoring
- Files: `eval_rag_quality.py` check functions

##### UI Content Classification

**Intentionally Curated (NOT tech debt):**
| File | Content | Reason |
|------|---------|--------|
| `landing_view.py` | Suggested questions | Curated UX showcase, covered by eval |
| `about_matt.py` | Timeline, company names | Curated CV/resume |

**UI Metrics Hydration (Jan 22, 2026):** ✅ DONE
All project/client counts now derived dynamically from JSONL:

| File | Hydrated | Status |
|------|----------|--------|
| `banking_landing.py` | Project count, client counts, capability areas | Dynamic |
| `cross_industry_landing.py` | Project count, industry count, capability areas | Dynamic |
| `category_cards.py` | Banking/Cross-industry project counts, client pills | Dynamic |
| `home.py` | Now passes STORIES to category_cards | Wired |

**Backend (FIXED):**
| File | Status |
|------|--------|
| `backend_service.py` MATT_DNA | Dynamic from JSONL |
| `backend_service.py` Synthesis prompt | Dynamic from JSONL |
| `cross_industry_landing.py` industry pills | Fixed (removed phantom industries) |

---

## Analytics Integration (Paused)

**Story ID:** MATTGPT-011
**Priority:** LOW (blocked on RAG stability)
**Status:** Paused - removed Jan 12, 2026

### Background

| Date | Action | Outcome |
|------|--------|---------|
| Jan 10, 2026 | Added `streamlit-analytics2` | Working initially (3 pageviews logged) |
| Jan 12, 2026 | Production failure | `AttributeError: st.session_state has no attribute "session_data"` |
| Jan 12, 2026 | Removed analytics | Quick fix to restore production stability |

**Root Cause:** The `streamlit-analytics2` wrapper ran before Streamlit initialized session state. The `with streamlit_analytics.track():` executes at import time, but `app.py` session state setup (lines 46-54: `render_navbar()`, `setdefault("active_tab")`) hadn't completed yet.

### Prerequisites

| Prerequisite | Status |
|--------------|--------|
| Eval stable at 90%+ | 98.1% (60/61 passed) |
| Double-filtering bug fixed | Done |
| Core RAG architecture stable | Done (Entity Gate removed, pipeline simplified) |

### Action Plan

1. Create branch `feature/analytics-retry`
2. `pip install streamlit-analytics2`
3. Add wrapper to `app.py` **AFTER** session state initialization:
   ```python
   import streamlit_analytics2 as streamlit_analytics

   # ... existing session state setup (lines 46-54) ...

   # AFTER all st.session_state initialization:
   with streamlit_analytics.track():
       # page rendering code (lines 283+)
   ```
4. Test locally — document what breaks (if anything)
5. If working, implement custom events:
   - `page_view` — tab navigation
   - `search` — Explore Stories query
   - `ask_query` — Ask MattGPT query + intent
   - `story_view` — story detail opened
   - `related_project_click` — Related Projects card clicked
6. If broken, **document root cause** (session state key, stack trace, timing)

**Fallback:** Manual `gtag.js` injection via `st.components.html()` if `streamlit-analytics2` doesn't work.

### Acceptance Criteria

- [ ] Analytics wrapper doesn't break session state
- [ ] Page views tracked across all tabs
- [ ] Search queries logged with result counts
- [ ] Ask MattGPT queries logged with intent classification
- [ ] Story detail opens tracked
- [ ] No performance degradation

### Reference

- `ARCHITECTURE.md` Analytics section
- Commit `2398354` (removal commit, Jan 12, 2026)

---

### Existing Code: Google Sheets Query Logger

**File:** `services/query_logger.py`
**Status:** Orphaned - dependencies removed, file kept for future use

**What it does:**
- Logs queries to Google Sheets using `gspread`
- Sheet ID: `1Xxsh7hBx6yh8K2Vn1r6ST6JTACIblUBOGbQ2QBvrAk4`
- Requires `st.secrets["gcp_service_account"]` for auth

**Why backed out:**
- Caused errors in Streamlit Cloud
- Dependencies (`gspread`, `google-auth`) removed from `requirements.txt`
- File kept intact for future re-integration

**To re-enable:**
1. Add to `requirements.txt`:
   ```
   gspread
   google-auth
   ```
2. Configure `st.secrets["gcp_service_account"]` in Streamlit Cloud
3. Import and call from Ask MattGPT:
   ```python
   from services.query_logger import log_query
   log_query(user_query, page="Ask Agy")
   ```
4. Test in Streamlit Cloud (local won't have secrets configured)

**Note:** This is separate from `streamlit-analytics2` (GA4). Could run both - Sheets for query content, GA4 for pageviews/events.

---

## Cross-Browser Testing
**Story ID:** MATTGPT-010
**Priority:** LOW

**User Story:**
As a user on any browser, I want consistent styling and functionality.

**Acceptance Criteria:**
- [ ] Test on Chrome
- [ ] Test on Safari
- [ ] Test on Firefox
- [ ] Test on Edge
- [ ] Fix any CSS inconsistencies
