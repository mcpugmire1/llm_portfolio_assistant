# BACKLOG

## January 25, 2026 - Tech Debt from RAG Audit

### 1. Fix Prompt Conflict
**Priority:** HIGH
**Issue:** System prompt says "Emphasize X" but also "NEVER meta-commentary" — LLM can't satisfy both
**Evidence:** `META_SENTENCE_PATTERNS` regex fires frequently catching violations
**Fix:** Rewrite prompt to remove conflicting instructions

### 2. Add Eval Cases for "Tell me more about: [Title]"
**Priority:** MEDIUM
**Issue:** No test coverage for the Related Projects "tell me more" pattern
**Fix:** Add 3-5 eval cases like "Tell me more about: Platform Modernization at JPMC"

### 3. Simplify backend_service.py
**Priority:** MEDIUM
**Issue:** 800+ lines, imports from 6+ modules, unclear ownership boundaries
**Fix:** Extract intent classification, entity detection, and mode logic into separate modules

### 4. Audit Excel Master for Corporate Filler
**Priority:** LOW
**Issue:** BANNED_PHRASES list keeps growing; should fix at source
**Fix:** Grep Excel master for "meaningful outcomes", "foster collaboration", etc. and rewrite

### 5. Delete META_SENTENCE_PATTERNS Regex
**Priority:** MEDIUM (blocked by #1)
**Issue:** Band-aid for prompt conflict; should be unnecessary after #1
**Fix:** After fixing prompt, monitor for 1 week, then delete if no violations

### 6. Remove boost_narrative_matches()
**Priority:** LOW
**Issue:** Title is now embedded in Pinecone, so semantic search naturally finds narrative stories
**Status:** Function still exists but may be dead code
**Fix:** Verify with eval, then delete from `rag_service.py`

### 7. Centralize Hardcoded Values
**Priority:** MEDIUM
**Issue:** 11 categories of hardcoded values scattered across 6+ files (see RAG Audit in ARCHITECTURE.md)
**Fix:** Create `config/constants.py` with all thresholds, model names, client lists

### 8. Dead Code Cleanup
**Priority:** LOW
**Files to audit:**
- `services/query_logger.py` - orphaned Google Sheets logger
- `utils/scoring.py` - may have unused functions
- Any `# TODO` or `# FIXME` comments older than 30 days

---

### 10. Cross-Browser Testing
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

### January 21, 2026 - RAG Eval Quality Sprint

#### Sovereign Backlog (Real Issues for Next Sprint)

**1. Multi-Field Entity Blind Spot** ✅ DONE
- ~~System treats `Client` as only source of truth~~
- ~~Need entity detection across `Employer`, `Division`, `Project`, `Place`~~
- ~~Example: Accenture stories where Client="Confidential Healthcare Provider" should still be discoverable as Accenture work~~
- **Implementation (Jan 22, 2026):**
  - Updated `pinecone_service.py:189-216` to use Pinecone `$or` operator
  - Entity filter now searches across all 5 fields: `client`, `employer`, `division`, `project`, `place`
  - Applied correct casing per field (lowercase for division/employer/project/place, PascalCase for client)
  - Eval: 100% pass rate (31/31) - no regression

**3. Dynamic Prompting - Hardcoded Client Names** ✅ DONE
- ✅ Synthesis prompt now derives clients dynamically
- ✅ MATT_DNA now derives all client names from JSONL (banking, telecom, transport)
- ✅ Fixed "JPMorgan" → "JP Morgan Chase" (now matches JSONL source)
- ✅ Removed phantom industries from `cross_industry_landing.py` (Manufacturing, Retail & Consumer Goods)
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
| `banking_landing.py` | Project count, client counts, capability areas | ✅ Dynamic |
| `cross_industry_landing.py` | Project count, industry count, capability areas | ✅ Dynamic |
| `category_cards.py` | Banking/Cross-industry project counts, client pills | ✅ Dynamic |
| `home.py` | Now passes STORIES to category_cards | ✅ Wired |

**Backend (FIXED):**
| File | Status |
|------|--------|
| `backend_service.py` MATT_DNA | ✅ Dynamic from JSONL |
| `backend_service.py` Synthesis prompt | ✅ Dynamic from JSONL |
| `backend_service.py` Entity normalization | ✅ Alias map (intentional) |
| `cross_industry_landing.py` industry pills | ✅ Fixed (removed phantom industries) |

---

## 📊 Analytics Integration (Paused)

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
| Eval stable at 90%+ | ~92% (56/61 passed) |
| Double-filtering bug fixed | ✓ |
| Core RAG architecture stable | ✓ (Q17 synthesis diversity is known gap) |

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
