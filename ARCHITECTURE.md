# Architecture Documentation

## Table of Contents

### 📋 Overview
- [Executive Summary](#executive-summary)
- [Component-Based Refactoring](#component-based-refactoring-october-2025)
- [Current Architecture](#current-architecture-november-7-2025)

### 🏗️ Architecture Decision Records (ADRs)
- [ADR-001: Component Scoping](#adr-001-component-scoping)
- [ADR-002: Theme Constants (Evolved)](#adr-002-theme-constants-evolved)
- [ADR-003: Global vs. Component Styles](#adr-003-global-vs-component-styles)
- [ADR-004: Emotion-Cache Override Strategy](#adr-004-emotion-cache-override-strategy)
- [ADR-005: CSS Variable System for Dark Mode](#adr-005-css-variable-system-for-dark-mode)
- [ADR-006: Avatar Sizing Standards](#adr-006-avatar-sizing-standards)

### 🚀 Migration History
- [Migration Strategy](#migration-strategy)
  - [Phase 1: Infrastructure](#phase-1-infrastructure--complete)
  - [Phase 2: Page Extraction](#phase-2-page-extraction--complete-october-21-2025)
  - [Phase 3: Massive Cleanup](#phase-3-massive-cleanup--complete-october-22-2025)
  - [Phase 5: Dead Code Elimination](#phase-5-dead-code-elimination--complete-november-7-2025)
- [File Size Summary](#file-size-summary)
- [Refactoring Impact](#refactoring-impact)

### 📊 Data Pipeline & RAG
- [Data Pipeline & RAG Architecture](#data-pipeline--rag-architecture)
  - [Pipeline Overview](#pipeline-overview)
  - [Stage 1: Excel to JSONL](#stage-1-excel-to-jsonl)
  - [Stage 2: Manual Enrichment](#stage-2-manual-enrichment)
  - [Stage 3: Embedding Generation](#stage-3-embedding-generation)
  - [Production RAG Pipeline](#production-rag-pipeline)
  - [Key Services](#key-services)
  - [Cost & Performance](#cost--performance)
  - [Data Refresh Workflow](#data-refresh-workflow)
  - [Environment Configuration](#environment-configuration)
  - [Deployment](#deployment)

### 🎨 CSS Architecture
- [CSS Scoping Patterns](#css-scoping-patterns)
- [Streamlit-Specific Challenges](#streamlit-specific-challenges)

### 💡 Key Features
- [Component Catalog](#component-catalog)
- [Services Layer](#services-layer)
- [Utilities](#utilities)

### 📱 Mobile & Responsive Design
- [Mobile Responsiveness Roadmap](#mobile-responsiveness-roadmap)
  - [Known Mobile Issues](#known-mobile-issues)
  - [CSS Breakpoint Strategy](#recommended-css-breakpoint-strategy)
  - [Testing Approach](#testing-approach)
  - [Implementation Priority](#implementation-priority)

### 🔮 Future Work
- [Future Enhancements](#future-enhancements)
- [Interview Talking Points](#interview-talking-points)

---

## Executive Summary

**Project:** MattGPT Portfolio Assistant - AI-powered career story search and chat interface
**Tech Stack:** Streamlit, OpenAI GPT-4o-mini, Pinecone vector DB, Python 3.11+
**Data Corpus:** 130+ STAR-formatted transformation project stories
**Last Updated:** December 9, 2024

### Key Achievements

**95.1% Code Reduction in Core Router**
- `app.py`: 5,765 lines → 284 lines
- Eliminated 1,400+ lines of dead code (zombie functions, commented blocks, unused imports)
- Modularized monolithic `ask_mattgpt.py` (4,696 lines) into 8-file directory structure

**Modern CSS Architecture**
- Implemented CSS variables for light/dark mode support
- Standardized avatar sizing (64px headers, 60px chat)
- Solved Streamlit emotion-cache override challenges
- Consistent purple brand (#8B5CF6) across all views

**Component-Based Structure**
- 8 reusable UI components (142 KB)
- 4 business logic services (28 KB)
- 6 shared utility modules (27 KB)
- Zero circular dependencies

### Current State (December 2024)

**Ask MattGPT Modular Architecture:**
- Landing view with capability cards and sample queries
- Conversation view with RAG-powered responses
- Unified header component across all views
- "How Agy Searches" modal with 3-step flow visualization
- Dark mode support via CSS variables

**Core Features:**
- Semantic search across 130+ project stories
- Query validation via semantic router
- Context-aware follow-up questions
- Story intelligence (theme/persona inference)
- Responsive chat UI with thinking indicators

### What This Document Contains

1. **Current Architecture:** File structure, components, services (as of Dec 2024)
2. **ADRs 1-6:** Design decisions with rationale and trade-offs
3. **Migration History:** Refactoring phases, metrics, achievements (Oct-Nov 2025)
4. **CSS Architecture:** Scoping patterns, emotion-cache strategies, dark mode
5. **Future Roadmap:** Mobile responsiveness, analytics, performance optimizations

---

## Component-Based Refactoring (October 2025)

### Problem Statement

The original implementation suffered from:
- **Monolithic structure**: 5,765 line `app.py`, 2,100+ line `ui/components.py`
- **CSS bleeding**: Broad selectors affected unintended elements across pages
- **Poor maintainability**: Difficult to locate bugs, make isolated changes
- **Unprofessional appearance**: Not suitable for Director/VP-level code review

### Solution: Component-Based Architecture

Refactored to a modular structure with clear separation of concerns:

---

### Current Architecture (November 7, 2025)
```
llm_portfolio_assistant/
├── app.py                          # Pure router (284 lines) ✅ Minimal & clean
│
├── config/
│   ├── __init__.py
│   ├── debug.py                    # Centralized DEBUG flag
│   └── settings.py                 # Configuration helpers
│   # Note: theme.py was removed - superseded by CSS variables in global_styles.py
│
├── utils/                          # Shared utilities
│   ├── __init__.py
│   ├── formatting.py               # build_5p_summary, _format_* helpers
│   ├── validation.py               # is_nonsense, token_overlap_ratio
│   ├── scoring.py                  # _keyword_score, _hybrid_score
│   ├── filters.py                  # matches_filters
│   ├── ui_helpers.py               # safe_container, render_no_match_banner, dbg
│   └── search.py                   # Search utilities (placeholder)
│
├── services/                       # Business logic & external APIs
│   ├── __init__.py
│   ├── pinecone_service.py         # Pinecone client & vector search
│   ├── rag_service.py              # Semantic search orchestration
│   ├── semantic_router.py          # ✅ Query routing & validation (11.4 KB)
│   └── story_service.py            # Story retrieval logic (placeholder)
│
├── ui/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── navbar.py                  # Top navigation (80 lines)
│   │   ├── footer.py                  # Footer (60 lines)
│   │   ├── story_detail.py            # Story Detail Component - Shared Renderer (329 lines)
│   │   ├── ask_mattgpt_header.py      # ✨ Unified Ask MattGPT header (47.5 KB)
│   │   ├── how_agy_modal.py           # ✨ "How Agy Searches" modal (28.6 KB)
│   │   ├── category_cards.py          # Landing page capability cards (19 KB)
│   │   ├── hero.py                    # Hero section component (8 KB)
│   │   └── thinking_indicator.py      # ✨ Loading/processing indicator (3 KB)
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                    # Home page (38 lines)
│   │   ├── explore_stories.py         # Stories browser (1,306 lines)
│   │   ├── ask_mattgpt/               # ✅ Modular structure (Dec 2024)
│   │   │   ├── __init__.py            # Router (1.9 KB)
│   │   │   ├── landing_view.py        # Landing page UI (9.8 KB)
│   │   │   ├── conversation_view.py   # Chat conversation UI (15.4 KB)
│   │   │   ├── conversation_helpers.py # Message rendering (26.9 KB)
│   │   │   ├── backend_service.py     # RAG pipeline integration (43.2 KB)
│   │   │   ├── styles.py              # CSS definitions (39.0 KB)
│   │   │   ├── story_intelligence.py  # Theme/persona inference (11.6 KB)
│   │   │   ├── shared_state.py        # Session state management (7.9 KB)
│   │   │   └── utils.py               # Shared utilities (9.4 KB)
│   │   ├── about_matt.py              # About page (467 lines)
│   │   ├── banking_landing.py         # Banking landing (413 lines)
│   │   └── cross_industry_landing.py  # Cross-industry landing (413 lines)
│   │
│   ├── styles/
│   │   ├── __init__.py
│   │   └── global_styles.py        # Shared CSS overrides
│   │
│   └── legacy_components.py        # Legacy monolith (2,100 lines) - TO BE DELETED
│
├── data/
│   ├── echo_star_stories_nlp.jsonl # Story corpus (130+ stories)
│   ├── nonsense_filters.jsonl      # Off-domain query rules
│   └── offdomain_queries.csv       # Query telemetry log
│
├── assets/
│   └── (images, SVGs, diagrams)
│
└── .streamlit/
    └── config.toml                 # Streamlit theme config
```

---

## Architecture Decision Records

### ADR-001: Component Scoping

**Decision:** Each UI component manages its own CSS in isolation.

**Problem:** Broad CSS selectors like `div[data-testid="stHorizontalBlock"]` were affecting:
- ✅ Navigation bar (intended)
- ❌ Filter sections on Explore Stories page (unintended)
- ❌ Other horizontal layouts throughout app (unintended)

**Solution:**
```python
# ui/components/navbar.py
def render_navbar(current_tab):
    # Scoped CSS - only affects navigation
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"]:first-child > div:first-child {
        background: #2c3e50 !important;  /* Only first block */
    }
    </style>
    """)
```

**Benefits:**
- CSS changes don't break other pages
- Each component can be tested in isolation
- Clear ownership of styling

---

### ADR-002: Theme Constants (Evolved)

**Original Decision:** Centralize colors, typography, spacing in `config/theme.py`.

**Problem:** Hardcoded values scattered across 20+ files:
- `#667eea` appears 47 times
- `padding: 24px` repeated 32 times
- Inconsistent values (sometimes `24px`, sometimes `20px`)

**Original Solution:**
```python
# config/theme.py (deprecated)
COLORS = {
    "primary_purple": "#8B5CF6",
    "dark_navy": "#2c3e50",
}
```

**Evolution (Dec 2024):** Replaced with CSS variables in `global_styles.py`

**Why the change:**
- Python theme constants were over-engineered for Streamlit
- CSS variables provide native browser support
- Better dark mode support via `:root` and `body.dark-theme`
- No Python-to-CSS bridging required
- Streamlit just injects CSS once

**Current Approach:** See ADR-005 for CSS Variable System

**Benefits:**
- Single source of truth (still maintained)
- Native dark mode via variable overrides
- No template interpolation needed
- Cleaner separation of concerns

---

### ADR-003: Global vs. Component Styles

**Decision:** Split CSS into global (shared) and component-specific.

**Global styles** (`ui/styles/global_styles.py`):
- Streamlit overrides (hide header/menu)
- Metrics containers
- Form controls (select boxes, inputs)
- AgGrid tables
- Generic buttons

**Component styles** (`ui/components/navbar.py`, etc.):
- Component-specific layout
- Hover states
- Active states
- Component-level responsiveness

**Rule of thumb:**
- If it's used on 3+ pages → global
- If it's specific to one component → scoped

---

## Migration Strategy

### Phase 1: Infrastructure ✅ COMPLETE
- [x] Create directory structure
- [x] Extract `theme.py` constants
- [x] Create `global_styles.py`
- [x] Extract `navbar.py` component
- [x] Extract `footer.py` component

### Phase 2: Page Extraction ✅ COMPLETE (October 21, 2025)
- [x] Extract Explore Stories page (1,306 lines)
- [x] Extract Ask MattGPT page (1,885 lines)
- [x] Extract About Matt page (467 lines)
- [x] Create landing page stubs (28 lines)

**Total extracted: 3,686 lines**

### Phase 3: Massive Cleanup ✅ COMPLETE (October 22, 2025)
- [x] Centralize DEBUG flag to config/debug.py
- [x] Move shared helpers to utils/ (formatting, validation, scoring, filters, ui_helpers)
- [x] Extract Pinecone logic to services/pinecone_service.py
- [x] Extract RAG logic to services/rag_service.py
- [x] Remove ALL duplicate functions across files (12 duplicates eliminated)
- [x] Delete dead zombie functions (~700 lines of never-called legacy code)
- [x] Delete ALL commented-out legacy code (~430 lines)
- [x] Consolidate imports and remove redundant variables
- [x] Fix 3 critical bugs (search validation, filter pills, reset filters)
- [x] Remove DEMO_STORIES fallback data

**🎉 Phase 3 Achievement: 2,220 lines removed in one day (68.6% reduction in app.py)**
**✅ app.py reduced to: 1,014 lines, 31 functions**

### Phase 5: Dead Code Elimination ✅ COMPLETE (November 7, 2025)

Major cleanup session removing unused code identified through static analysis:

**What Was Removed (511 lines total):**

1. **Duplicate Code (3 instances):**
   - Duplicate `import streamlit as st`
   - Duplicate `apply_global_styles()` call
   - Duplicate first-mount guard block

2. **Large Commented Blocks (~200 lines):**
   - Commented avatar constants (ASSIST_AVATAR, USER_AVATAR)
   - 90-line sidebar navigation with option_menu (lines 203-293)
   - Query param navigation code (lines 633-638)
   - Badge color functions (_BADGE_PALETTE, _badge_color, _DOT_EMOJI)

3. **Dead Functions (20+ functions removed):**
   - `STAR()`, `FIVEP_SUMMARY()`, `story_modes()`
   - `_related_stories()`, `_summarize_index_stats()`
   - `_clear_ask_context()` (duplicate definition)
   - `_dot_for()`, `_shorten_middle()`, `render_list()`
   - `build_known_vocab()`, `log_offdomain()`
   - `_sanitize_answer()`, `_fmt_score()`, `_matched_caption()`
   - `_ensure_ask_bootstrap()`, `_push_user_turn()`, `_push_assistant_turn()`
   - `_init_pinecone()`, `_load_jsonl()`, `_slug()`

4. **Unused Imports (25+ imports removed):**
   - `quote_plus` from urllib.parse
   - `csv`, `datetime` from standard library
   - `List`, `Optional` from typing
   - `safe_container`, `dbg`, `_safe_json`
   - `_format_narrative`, `_format_key_points`, `_format_deep_dive`, `build_5p_summary`
   - `is_nonsense`, `token_overlap_ratio`, `_tokenize`
   - `render_hero`, `render_stats_bar`, `render_section_title`, `render_category_cards`
   - `AgGrid`, `GridOptionsBuilder`, `GridUpdateMode`
   - `option_menu` from streamlit_option_menu

5. **Unused Constants (15+ constants removed):**
   - `PINECONE_MIN_SIM`, `_DEF_DIM`
   - `W_PC`, `W_KW` (hybrid score weights)
   - `SEARCH_TOP_K`
   - `_PINECONE_API_KEY`, `_PINECONE_INDEX`, `_PC`, `_PC_INDEX`
   - `_ext_render_sources_chips`, `_ext_render_sources_badges_static`
   - `_HAS_AGGRID`, `_HAS_OPTION_MENU`
   - `_KNOWN_VOCAB`

**Impact:**
- **Lines removed:** 511 lines (520 deletions - 9 insertions for formatting)
- **app.py reduction:** 1,014 → 473 lines (53% additional reduction)
- **Total reduction from original:** 5,765 → 473 lines (92% reduction!)
- **Result:** Clean, maintainable router with zero dead code

**Testing Approach:**
- User tested incrementally while commenting out code
- All functionality preserved and verified working
- No regressions introduced

**Commit:** `refactor: remove 350+ lines of dead code from app.py` (November 7, 2025)

### Phase 5B: Additional Duplicate Functions ✅ COMPLETE (November 7, 2025)

User review discovered 3 additional duplicate functions that static analysis missed:

**What Was Removed (142 lines total):**

1. **render_no_match_banner() (86 lines)** - app.py:649-853
   - Real version: utils/ui_helpers.py
   - Used by: ask_mattgpt.py, explore_stories.py
   - Unified yellow warning banner for no-match situations

2. **on_ask_this_story() (18 lines)** - app.py:134
   - Real version: explore_stories.py:192
   - Called at: explore_stories.py:532
   - Sets story context and navigates to Ask MattGPT

3. **field_value() (38 lines)** - app.py:153
   - Real version: ask_mattgpt.py:3954
   - Called at: ask_mattgpt.py:3867-3869
   - Safe field accessor with domain/tag aliasing

**Impact:**
- **Lines removed:** 142 lines
- **app.py reduction:** 473 → 330 lines (30% additional reduction)
- **Total reduction from original:** 5,765 → 330 lines (94.3% reduction!)
- **Result:** Absolute minimal router achieved

**Detection Method:**
- User manually reviewed app.py and suspected duplicates
- Used grep to verify function definitions across codebase
- Confirmed orphaned versions were never imported or called

**Commit:** `refactor: remove 3 duplicate functions from app.py (142 lines)` (November 7, 2025)

### Phase 5C: Duplicate Config & Unused Imports ✅ COMPLETE (November 7, 2025)

Further dead code removal through import analysis:

**What Was Removed (46 lines total):**

1. **Duplicate Pinecone Configuration (40 lines)** - lines 34-71
   - VECTOR_BACKEND, OPENAI_API_KEY, PINECONE_API_KEY, etc.
   - Pinecone guard validation
   - pinecone_index initialization
   - **Real version:** services/pinecone_service.py
   - **Reason:** Pages import from pinecone_service, never from app.py

2. **Unused Imports (3 lines)**
   - `import textwrap` - never used in app.py
   - `import time` - never used in app.py
   - `import pandas as pd` - never used in app.py
   - Ask MattGPT and Explore Stories import these directly

3. **Unused Constants (2 lines)**
   - `TAB_NAMES` - never referenced
   - `USE_SIDEBAR_NAV` - obsolete comment

4. **Comment cleanup (1 line)**

**Impact:**
- **Lines removed:** 46 lines
- **app.py reduction:** 330 → 284 lines (14% additional reduction)
- **Total reduction from original:** 5,765 → 284 lines (95.1% reduction!)
- **Result:** Absolute minimal router - config lives in services

**Detection Method:**
- grep analysis to find if anything imports from app.py (nothing does)
- Verified all Pinecone config is defined in services/pinecone_service.py
- Confirmed pages import from services, not app.py

**Commit:** `refactor: remove duplicate Pinecone config and unused imports (46 lines)` (November 7, 2025)

**✅ app.py is now an absolute minimal router: 284 lines (95.1% reduction from original!)**

### Phase 4: Final Polish & UI Consistency ✅ COMPLETE (October 28, 2025)

#### Phase 4A: Filter Redesign & Data Layer ✅
- [x] Refactor data loader to use raw JSONL fields (Title-case)
- [x] Add Industry and Capability filters (primary filters)
- [x] Redesign Explore Stories filter UI (progressive disclosure)
- [x] Implement pre-filtered navigation from landing pages
- [x] Update all consumers to use Title-case field names

#### Phase 4B: Detail Panel Redesign ✅
- [x] Match explore_stories_table_wireframe.html specification
- [x] Implement full STAR narrative display
- [x] Add sidebar with tech tags, competencies, metrics
- [x] Verify 100% JSONL-sourced data (zero fabrication)

#### Phase 4C: Button Styling Unification ✅
- [x] Implement purple theme (#8B5CF6) across all pages
- [x] Solve Streamlit emotion-cache CSS override issue
- [x] Create JavaScript workaround for button styling
- [x] Add varied button text (not all "View Projects →")
- [x] Unify button padding and hover states

#### Phase 4D: Table View Wireframe Matching ✅
- [x] Add client badge styling (blue pills)
- [x] Add domain tag styling (gray text)
- [x] Implement AgGrid custom cell renderers
- [x] Style selected rows (purple background + border)
- [x] Match all table elements to wireframe

#### Phase 4E: Landing Page Completion ✅
- [x] Rewrite banking_landing.py with purple theme
- [x] Rewrite cross_industry_landing.py with purple theme
- [x] Add varied button text for all capability cards
- [x] Implement purple footer buttons

**Remaining Phase 4 Tasks:**
- [ ] Delete ui/legacy_components.py entirely (2,100 lines) - **HOME PAGE CONTENT STILL IN USE**
- [ ] Move css_once() to ui/styles/css_injection.py
- [ ] Add docstrings to all public functions
- [ ] Add type hints consistently
- [ ] Set up pre-commit hooks (black, isort, mypy)
- [ ] Remove debug markers from home.py and category_cards.py

**Expected final app.py size: ~1,000 lines (pure routing + minimal bootstrapping)**

---

## Refactoring Impact (October 18 - November 7, 2025)

### Quantitative Improvements
- **Code reduction:** 5,481 lines eliminated in app.py alone
- **app.py transformation:**
  - **Started:** 5,765 lines, 150+ functions (October 18)
  - **After Phase 2:** 3,234 lines, 69 functions (October 21)
  - **After Phase 3:** 1,014 lines, 31 functions (October 22)
  - **After Phase 5A:** 473 lines (November 7)
  - **After Phase 5B:** 330 lines (November 7)
  - **After Phase 5C:** 284 lines, minimal router (November 7) ✅
  - **Total reduction:** 5,481 lines (-95.1%!)
- **Duplicate elimination:** 100% (from 20+ duplicates to 0)
- **Dead code elimination:** 100% (commented code, zombie functions, unused imports/constants, duplicate config)
- **New modular structure:** 10 new files created
  - 5 utils modules (548 lines)
  - 2 services modules (479 lines)
  - 3 config modules (120 lines)

### Qualitative Improvements
- ✅ **app.py is now a pure router** (no business logic, no duplicate functions, no duplicate config)
- ✅ No circular dependencies
- ✅ Clear separation of concerns (config in services, not in router)
- ✅ Every function has single source of truth
- ✅ Pages can be modified independently
- ✅ Ready for React migration (1:1 module mapping)
- ✅ **Professional architecture for GitHub portfolio**
- ✅ **Interview-ready codebase**

### Daily Progress Summary

**October 18-21:** Phase 1 & 2 - Infrastructure + Page Extraction
- Extracted 3,686 lines to ui/pages/
- Created modular structure (utils/, services/, config/)
- app.py: 5,765 → 3,234 lines (-44%)

**October 22:** Phase 3 Complete - Massive Cleanup Session 🚀 (Zombie Functions & Duplicates)
- **Fixed 3 critical bugs:**
  - Search validation (vocab initialization)
  - Filter pill removal (versioned keys)
  - Reset filters (version counter preservation)
- **Deleted 12 duplicate functions** already extracted to utils/services:
  - build_5p_summary, strongest_metric_line, story_has_metric (→ utils/formatting.py)
  - is_nonsense, token_overlap_ratio, _tokenize (→ utils/validation.py)
  - matches_filters (→ utils/filters.py)
  - _get_embedder, _embed, _extract_match_fields (→ services/pinecone_service.py)
  - _keyword_score, _hybrid_score (→ utils/scoring.py)
  - semantic_search, pinecone_semantic_search (→ services/rag_service.py & pinecone_service.py)
- **Deleted 8 zombie functions** (never called, legacy compatibility):
  - rag_answer, send_to_backend, render_ask_panel (dead Ask MattGPT wrappers)
  - retrieve_stories, semantic_search (unused compatibility shims)
  - render_compact_context_banner (2 duplicate definitions)
  - _clear_ask_context (duplicate)
- **Deleted 430 lines of commented-out legacy code:**
  - Old filter implementations
  - Old search logic
  - Deprecated rendering functions
- **Consolidated imports** and removed dead variables (_loaded_from, DEMO_STORIES)
- **Result: app.py: 3,234 → 1,014 lines (68.6% reduction in one day!)**
- **Functions: 69 → 31 (clean router achieved)**

**November 7:** Phase 5 Complete - Dead Code Elimination 🧹 (Three Sessions)
- **Phase 5A:** Removed 511 lines (imports, constants, commented blocks, zombie functions)
  - app.py: 1,014 → 473 lines
- **Phase 5B:** Removed 142 lines (duplicate functions: render_no_match_banner, on_ask_this_story, field_value)
  - app.py: 473 → 330 lines
- **Phase 5C:** Removed 46 lines (duplicate Pinecone config, unused imports: textwrap/time/pandas)
  - app.py: 330 → 284 lines
- **Phase 5 Total:** 699 lines removed across 3 commits
- **Result: app.py: 1,014 → 284 lines (72% additional reduction)**
- **Total reduction from original: 95.1% (5,765 → 284 lines)**

### Key Commit History

**Phase 3 (October 22, 2025) - 12 atomic commits:**
1. `fix: resolve search validation and filter reset issues`
2. `chore: remove verbose debug output from explore stories`
3. `chore: remove unused _loaded_from variable`
4. `refactor: remove obsolete DEMO_STORIES fallback data`
5. `refactor: remove unused personas logic and fix show_sources call`
6. `chore: consolidate duplicate imports at top of app.py`
7. `chore: remove disabled legacy navigation code blocks`
8. `refactor: remove unused F() function duplicate`
9. `refactor: remove formatting function duplicates from app.py`
10. `refactor: remove dead Ask MattGPT functions from app.py` (532 lines)
11. `refactor: remove duplicate embedding and scoring functions` (135 lines)
12. `chore: delete all commented-out legacy code after testing` (430 lines)

**Phase 5 (November 7, 2025) - 3 commits:**
13. `refactor: remove 350+ lines of dead code from app.py` (511 lines)
14. `refactor: remove 3 duplicate functions from app.py` (142 lines)
15. `refactor: remove duplicate Pinecone config and unused imports` (46 lines)

### File Size Summary

**After Phase 5 Completion (November 7, 2025):**

| File/Module | Lines | Change from Start | Status |
|-------------|-------|-------------------|--------|
| **app.py** | **284** | **-5,481 (-95.1%)** | ✅ **Absolute minimal router** |
| explore_stories.py | 1,306 | -854 (-40%) | ✅ Modularized |
| ask_mattgpt/ (dir) | 164 KB | Replaced 4,696-line monolith | ✅ **Modular** (8 files) |
| about_matt.py | 467 | - | ✅ Extracted |
| components/ | 142 KB | +8 components | ✅ **Reusable** |
| utils/*.py | ~27 KB | +6 modules | ✅ Shared utilities |
| services/*.py | ~28 KB | +4 services | ✅ Business logic |
| config/*.py | ~1 KB | +2 modules | ✅ Configuration |
| **Total** | **~5,550** | **-5,481 from app.py** | ✅ |

**Key Achievements:**
- ✅ Eliminated ALL duplicate functions (was 20+ duplicates)
- ✅ Eliminated ALL duplicate config (Pinecone init moved to services)
- ✅ Eliminated ALL dead code (1,400+ lines total: zombie functions, commented blocks, unused imports/config)
- ✅ Zero circular dependencies
- ✅ **app.py is now 284 lines - an absolute minimal router (95.1% reduction!)**
- ✅ Clear separation of concerns (pages/utils/services/config)
- ✅ **Portfolio-ready architecture for technical interviews**

---

### ADR-004: Streamlit Emotion-Cache Override

**Decision:** Use JavaScript `components.html()` to override Streamlit's emotion-cache button styles.

**Problem:** Streamlit generates dynamic CSS classes like `.st-emotion-cache-7lqsib` with higher specificity than custom CSS. Even with `!important`, custom styles cannot override emotion-cache classes.

**Evidence:**
```html
<!-- Streamlit renders buttons with emotion classes -->
<button class="st-emotion-cache-7lqsib e8vg11g2" data-testid="stBaseButton-secondary">
    View Projects →
</button>
```

Custom CSS fails:
```css
button.st-emotion-cache-7lqsib {
    background: #8B5CF6 !important;  /* IGNORED */
}
```

**Solution:** JavaScript injection via iframe to apply inline styles:

```python
import streamlit.components.v1 as components

components.html("""
<script>
(function() {
    function applyPurpleButtons() {
        const parentDoc = window.parent.document;
        const buttons = parentDoc.querySelectorAll('[class*="st-key-btn_"] button');

        buttons.forEach(function(button) {
            if (!button.dataset.purpled) {
                button.dataset.purpled = 'true';
                button.style.cssText = 'background: white !important; color: #8B5CF6 !important;';

                button.addEventListener('mouseenter', function() {
                    this.style.cssText = 'background: #8B5CF6 !important; color: white !important;';
                });
            }
        });
    }

    // Run immediately and on intervals
    setTimeout(applyPurpleButtons, 100);
    setTimeout(applyPurpleButtons, 500);
    setInterval(applyPurpleButtons, 2000);
})();
</script>
""", height=0)
```

**Why This Works:**
- `window.parent.document` accesses Streamlit page from iframe context
- `style.cssText` applies inline styles (highest CSS specificity)
- `dataset.purpled` flag prevents re-styling same button
- Multiple `setTimeout` calls handle async rendering
- `setInterval` catches dynamically added buttons
- Event listeners maintain hover states

**Trade-offs:**
- **Pro:** Complete control over button styling
- **Pro:** Works across all Streamlit versions
- **Pro:** No modifications to Streamlit source
- **Con:** Adds ~0.5KB per page
- **Con:** Timing-dependent (100ms, 500ms delays)
- **Con:** Must handle button lifecycle (mount/unmount)

**Alternatives Considered:**
1. ❌ Pure CSS with `!important` - Doesn't work (emotion classes win)
2. ❌ Custom Streamlit component - Too heavyweight for buttons
3. ❌ Fork Streamlit - Maintenance nightmare
4. ✅ JavaScript inline styles - Pragmatic solution

**Usage Pattern:**
```python
# Apply to specific button keys
components.html(f"""
<script>
const buttons = window.parent.document.querySelectorAll('.st-key-{key}');
// ... styling logic
</script>
""", height=0)
```

**Lessons:**
- Streamlit's emotion-cache is by design (CSS-in-JS)
- Inline styles have maximum specificity (1,0,0,0)
- Timing matters: Streamlit renders async
- Always use dataset flags to avoid duplicate listeners

---

### ADR-005: CSS Variable System for Dark Mode

**Decision:** Use CSS custom properties (`--variable-name`) for all colors, with light/dark mode variants.

**Problem:**
- No dark mode support
- Hardcoded colors throughout components
- Difficult to maintain consistent theming

**Solution:** Define CSS variables in `ui/styles/global_styles.py`:

```css
/* Light Mode (default) */
:root {
    /* Brand */
    --accent-purple: #8B5CF6;
    --accent-purple-hover: #7C3AED;

    /* Backgrounds */
    --bg-card: #FFFFFF;
    --bg-surface: #F9FAFB;
    --bg-primary: #FFFFFF;

    /* Text */
    --text-heading: #111827;
    --text-primary: #1F2937;
    --text-secondary: #6B7280;

    /* Chat */
    --chat-ai-bg: #F9FAFB;
    --chat-ai-border: #8B5CF6;
    --chat-user-bg: #FBFBFC;

    /* Borders */
    --border-color: #E5E7EB;
}

/* Dark Mode (override) */
body.dark-theme {
    --bg-card: #1E1E2E;
    --bg-surface: #262633;
    --bg-primary: #0E1117;

    --text-heading: #F9FAFB;
    --text-primary: #E5E7EB;
    --text-secondary: #9CA3AF;
    --accent-purple-text: #A78BFA;  /* Lighter for dark BG */

    --chat-ai-bg: #1E1E2E;
    --chat-user-bg: #282435;  /* Purple-tinted dark */

    --border-color: #374151;
}
```

**Usage in Components:**
```css
.chat-message {
    background: var(--chat-ai-bg);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}
```

**Benefits:**
- Automatic dark mode via variable overrides
- Single source of truth for colors
- No Python-to-CSS bridging
- Native browser support
- Fallback values supported: `var(--bg-card, #FFFFFF)`

**Trade-offs:**
- **Pro:** Clean separation of concerns
- **Pro:** Easy to add new color schemes
- **Pro:** Works with Streamlit's theme system
- **Con:** Must test both light and dark modes for every change
- **Con:** Older browsers need fallbacks (not an issue for modern stack)

**Supersedes:** ADR-002 (Python theme.py approach)

---

### ADR-006: Avatar Sizing Standards

**Decision:** Standardize avatar sizes across all contexts with inline styles.

**Problem:**
- Inconsistent avatar sizes (50px, 60px, 64px variations)
- Streamlit emotion-cache classes override CSS
- Users notice size differences between views

**Solution:**

**Header Avatars:** 64px
```html
<img src="...agy_avatar.png"
     width="64" height="64"
     style="width: 64px; height: 64px; border-radius: 50%; ..."
     alt="Agy">
```

**Chat Avatars:** 60px
```css
/* Agy avatar */
.stChatMessage > img[alt="assistant avatar"] {
    width: 60px !important;
    height: 60px !important;
    border-radius: 50% !important;
}

/* User avatar (emoji) */
.stChatMessage > div[contains(@class, 'st-emotion-cache')] {
    width: 60px !important;
    height: 60px !important;
    font-size: 28px !important;
}
```

**Rationale:**
- Headers need visual prominence → 64px
- Chat needs balanced sizing → 60px (not too large, not too small)
- Inline styles required to override emotion-cache

**Consistency Rules:**
- All landing page headers: 64px
- All conversation headers: 64px
- All About Matt avatars: 64px
- All in-chat avatars: 60px

---

## Data Pipeline & RAG Architecture

### Pipeline Overview

The data engineering flow transforms Excel-based STAR stories into vector embeddings that power semantic search:

```
Excel Master Sheet
      ↓
[generate_jsonl_from_excel.py]
      ↓
echo_star_stories.jsonl (raw)
      ↓
[Manual enrichment + LLM processing]
      ↓
echo_star_stories_nlp.jsonl (enriched)
      ↓
[build_custom_embeddings.py]
      ↓
OpenAI text-embedding-3-small (1536 dims)
      ↓
Pinecone Index (matt-portfolio-v2)
      ↓
[Production App - services/pinecone_service.py]
      ↓
Semantic Search Results → RAG → GPT-4o-mini → User
```

---

### Stage 1: Excel to JSONL

**Script:** `generate_jsonl_from_excel.py` (259 lines, root-level)

**Purpose:** Convert Excel master sheet to structured JSONL format while preserving existing data.

**Input:**
- Excel file: `MPugmire - STAR Stories - [DATE].xlsx`
- Sheet: `"STAR Stories - Interview Ready"`

**Output:**
- `echo_star_stories.jsonl` (130+ records)

**Key Features:**
- **Merge strategy:** Preserves existing `public_tags`, `content`, `id` fields
- **Backup:** Auto-creates `.bak` file before overwriting
- **Normalization:** Slug-based key matching (`Title|Client`)
- **Dry-run mode:** Preview changes before committing

**Fields Extracted:**
```python
{
    "id": "story_123",
    "Title": "Scaled Engineering Team from 4 to 150+",
    "Client": "Fortune 500 Bank",
    "Industry": "Financial Services",
    "Domain": "Platform Engineering",
    "Role": "Head of Engineering",
    "Situation": "Rapid growth, technical debt...",
    "Task": "Scale team while maintaining quality...",
    "Action": "Implemented hiring pipeline, mentorship...",
    "Result": "150+ engineers, 40% faster delivery...",
    "Theme": "Team Scaling & Leadership",
    "Sub-category": "Organizational Design",
    "Tags": "scaling, leadership, hiring",
    "public_tags": ["Team Scaling", "Engineering Leadership"]
}
```

**Environment:**
```bash
INPUT_EXCEL_FILE="MPugmire - STAR Stories - 01DEC25.xlsx"
SHEET_NAME="STAR Stories - Interview Ready"
DRY_RUN=False  # Set to True for preview
```

---

### Stage 2: Manual Enrichment

**Script:** `generate_public_tags.py` (171 lines, root-level)

**Purpose:** Add semantic metadata and public-facing tags.

**Enrichment Process:**
1. **Persona Tagging** - Map stories to interview personas (e.g., "Product Leader", "Technical Architect")
2. **5P Summaries** - Generate concise 5-paragraph summaries for quick scanning
3. **Public Tags** - Create user-friendly tags from technical metadata
4. **Theme Assignment** - Categorize stories by transformation themes

**Output:**
- `echo_star_stories_nlp.jsonl` (enriched with semantic metadata)

---

### Stage 3: Embedding Generation

**Script:** `build_custom_embeddings.py` (291 lines, root-level)

**Purpose:** Generate vector embeddings and upsert to Pinecone for semantic search.

**Input:**
- `echo_star_stories_nlp.jsonl` (enriched stories)

**Output:**
- Pinecone index: `matt-portfolio-v2`
- Namespace: `default`
- Dimensions: 1536 (OpenAI text-embedding-3-small)

**Embedding Strategy:**

**Text Composition for Embedding:**
```python
def build_embedding_text(story):
    """
    Combines multiple fields into rich semantic representation:
    - Theme + Industry + Sub-category (behavioral context)
    - 5P Summary (concise overview)
    - STAR fields: Situation, Task, Action, Result (2-3 items each)
    - Process details (max 3 items)
    - Public tags (comma-separated)

    Result: ~200-400 token text optimized for behavioral queries
    """
```

**Why This Approach:**
- **Behavioral focus:** Theme/Industry/Sub-category surface in behavioral interviews
- **Balanced detail:** Full STAR fields would dilute semantic signal
- **Tag inclusion:** Public tags capture essence without verbosity
- **Process field:** Critical for "how did you..." questions

**Migration History:**
- **v1:** MiniLM-L6-v2 (384 dims) - Fast but limited semantic understanding
- **v2:** OpenAI text-embedding-3-small (1536 dims) - Better behavioral query matching

**Metadata Stored in Pinecone:**
```python
{
    "id": "story_123",
    "title": "Scaled Engineering Team...",
    "client": "Fortune 500 Bank",
    "industry": "Financial Services",
    "domain": "Platform Engineering",
    "role": "Head of Engineering",
    "theme": "Team Scaling & Leadership",
    "tags": ["Team Scaling", "Engineering Leadership"],
    "embedding": [0.023, -0.045, ...],  # 1536-dimensional vector
}
```

**Processing Stats:**
- ~130 stories in ~30 seconds
- Cost: $0.0008 per full re-index
- OpenAI API: text-embedding-3-small @ $0.02 per 1M tokens

**Environment:**
```bash
STORIES_JSONL=echo_star_stories_nlp.jsonl
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=matt-portfolio-v2
PINECONE_NAMESPACE=default
```

---

### Production RAG Pipeline

**Query Flow:**

```
User Question: "How did Matt scale engineering teams?"
      ↓
[Query Preprocessing - services/semantic_router.py]
- Validate query (not nonsense)
- Route to appropriate handler
      ↓
[Semantic Search - services/pinecone_service.py]
- Embed query with text-embedding-3-small
- Vector search in Pinecone (top 10, similarity > 0.75)
- Apply metadata filters (Industry, Domain, Role)
      ↓
[Hybrid Ranking - utils/scoring.py]
- Vector similarity score (0-1)
- Keyword matching score (0-1)
- Weighted combination (70% vector, 30% keyword)
      ↓
[Context Assembly - ui/pages/ask_mattgpt/backend_service.py]
- Select top 3-5 stories
- Build prompt with STAR narratives
- Include metadata (Client, Industry, Theme)
      ↓
[LLM Generation - OpenAI GPT-4o-mini]
- System prompt: "Answer using STAR format..."
- Context: Top-ranked stories
- User query
      ↓
[Response Formatting - ui/pages/ask_mattgpt/conversation_helpers.py]
- Extract answer + sources
- Render with citations
- Display expandable story details
      ↓
User receives cited, STAR-formatted answer
```

---

### Key Services

#### 1. Pinecone Service ([services/pinecone_service.py](services/pinecone_service.py))

**Purpose:** Vector search and embedding management.

**Key Functions:**
```python
def semantic_search(query: str, top_k: int = 10, filters: dict = None):
    """
    1. Embed query with OpenAI
    2. Query Pinecone index
    3. Return top_k results with scores
    4. Apply optional metadata filters
    """

def get_pinecone_index():
    """Initialize Pinecone client and return index"""
```

**Search Parameters:**
- `top_k`: 10 (retrieve top 10 matches)
- `min_similarity`: 0.75 (filter low-quality matches)
- `namespace`: "default"

**Metadata Filters:**
```python
filters = {
    "industry": "Financial Services",
    "domain": "Platform Engineering"
}
```

---

#### 2. RAG Service ([services/rag_service.py](services/rag_service.py))

**Purpose:** Orchestrate semantic search + LLM generation.

**Key Functions:**
```python
def answer_question(query: str, filters: dict = None):
    """
    1. Semantic search → top stories
    2. Build context window
    3. Call GPT-4o-mini with system prompt
    4. Return answer + source citations
    """
```

**Context Window Strategy:**
- Max 3-5 stories (to fit within token limits)
- Prioritize highest similarity scores
- Include full STAR narratives

---

#### 3. Semantic Router ([services/semantic_router.py](services/semantic_router.py))

**Purpose:** Route queries to appropriate handlers based on intent.

**Key Functions:**
```python
def route_query(query: str):
    """
    Detect query type:
    - Behavioral (STAR stories)
    - Factual (resume data)
    - Off-topic (reject politely)
    - Clarification needed (ask follow-up)
    """
```

**Routing Logic:**
- Behavioral keywords: "How did you...", "Tell me about a time...", "Show me examples..."
- Factual keywords: "What is...", "Where did...", "When did..."
- Off-topic: Technical trivia, non-career questions

---

### Cost & Performance

#### Embedding Generation
- **Model:** text-embedding-3-small (1536 dims)
- **Cost:** $0.02 per 1M tokens
- **130 stories @ ~300 tokens each** = ~39K tokens
- **Total cost:** ~$0.0008 per full re-index
- **Time:** ~30 seconds for full corpus

#### Query Pipeline
- **Embedding:** 1 query = 10-20 tokens = $0.0000002
- **Pinecone:** Free tier (up to 100K queries/month)
- **GPT-4o-mini:** ~500 tokens per response = $0.00015
- **Total per query:** ~$0.0002 (negligible)

#### Pinecone Index
- **Dimensions:** 1536
- **Records:** 130
- **Storage:** ~0.7 MB (tiny)
- **Queries/month:** ~1,000 (well within free tier)

---

### Data Refresh Workflow

**When to Re-Index:**

1. **Add new stories** (Excel → JSONL → Pinecone)
2. **Update existing stories** (Edit Excel → re-run pipeline)
3. **Change embedding strategy** (Switch models → rebuild)
4. **Modify metadata fields** (Add filters → re-process)

**Full Refresh Steps:**

```bash
# 1. Update Excel master sheet
# 2. Export to JSONL
python generate_jsonl_from_excel.py

# 3. Enrich with LLM (manual or scripted)
python generate_public_tags.py

# 4. Generate embeddings and upsert
python build_custom_embeddings.py

# 5. Verify Pinecone index
python scripts/validate_pinecone_data.py

# 6. Test in app
streamlit run app.py
```

**Estimated time:** 5-10 minutes for full pipeline

---

### Environment Configuration

**Required Environment Variables:**

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=matt-portfolio-v2
PINECONE_NAMESPACE=default

# Data
STORIES_JSONL=echo_star_stories_nlp.jsonl

# Debug (optional)
DEBUG=False
```

**`.env` File Structure:**
```bash
# .env (not committed to git)
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=matt-portfolio-v2
PINECONE_NAMESPACE=default
STORIES_JSONL=data/echo_star_stories_nlp.jsonl
```

---

### Deployment

**Streamlit Cloud Configuration:**

**App URL:** https://askmattgpt.streamlit.app/

**Secrets (Streamlit Cloud):**
```toml
[default]
OPENAI_API_KEY = "sk-..."
PINECONE_API_KEY = "pcsk_..."
PINECONE_INDEX_NAME = "matt-portfolio-v2"
PINECONE_NAMESPACE = "default"
```

**Python Version:** 3.11+

**Requirements:**
```txt
streamlit>=1.28.0
openai>=1.0.0
pinecone-client>=2.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
```

---

## CSS Scoping Patterns

### Pattern 1: First-Child Selector (Navigation)
```css
/* Target ONLY first vertical block */
div[data-testid="stVerticalBlock"]:first-child > div:first-child {
    background: #2c3e50;
}
```

**Use when:** Component is always first on page (navbar)

---

### Pattern 2: Class-Based Scoping (Cards)
```python
st.markdown("""
<div class="banking-capability-card">
    {content}
</div>
<style>
.banking-capability-card {
    background: white;
    border: 1px solid #e5e5e5;
}
</style>
""")
```

**Use when:** Component appears multiple times, needs unique styling

---

### Pattern 3: Data Attributes (Future)
```python
st.markdown('<div data-component="navbar">', unsafe_allow_html=True)

# CSS
[data-component="navbar"] {
    background: #2c3e50;
}
```

**Use when:** Need semantic targeting without affecting DOM structure

---

## Testing Strategy (Future)

### Unit Tests
```python
def test_navbar_renders_correct_tab():
    render_navbar("Home")
    # Assert Home button is disabled
```

### Integration Tests
```python
def test_page_navigation():
    # Click Banking card
    # Assert Banking page loads
    # Assert navbar shows "Home" active
```

### CSS Regression Tests
```python
def test_navbar_doesnt_affect_filters():
    # Render Explore Stories
    # Assert filter section has correct background
```

---

## Mobile Responsiveness Roadmap

### Current State: Desktop-Optimized

The application is currently designed and tested for desktop viewports (1280px+). While functional on mobile browsers, the experience is not optimized.

### Known Mobile Issues

#### 1. **Navigation Bar**
- **Current:** Horizontal tabs (Home | Explore Stories | Ask MattGPT | About Matt)
- **Issue:** Won't fit on mobile widths (< 768px)
- **Proposed Solution:** Hamburger menu or bottom navigation bar
- **Streamlit Note:** Sidebar becomes hamburger automatically, but horizontal tabs need manual handling

#### 2. **Ask MattGPT Header**
- **Current:** 64px avatar + title + tagline + "How Agy searches" button in horizontal row
- **Issue:** Too wide for mobile (375-480px viewports)
- **Proposed Solution:**
  - Stack vertically on mobile
  - Hide/shrink "How Agy searches" button text to icon-only
  - Reduce avatar to 48px on mobile

#### 3. **Chat Avatars**
- **Current:** 60px avatars in conversation view
- **Issue:** Consumes too much horizontal space on mobile
- **Proposed Solution:** Reduce to 40-48px on mobile breakpoints
- **CSS Pattern:**
  ```css
  @media (max-width: 768px) {
      .stChatMessage > img[alt="assistant avatar"] {
          width: 48px !important;
          height: 48px !important;
      }
  }
  ```

#### 4. **Chat Message Bubbles**
- **Current:** `padding: 24px` on AI messages, `16px` on user messages
- **Issue:** Large padding wastes space on narrow screens
- **Proposed Solution:** Reduce to `16px/12px` on mobile
- **Font Size:** May need to reduce from `15px` to `14px` for readability

#### 5. **Chat Input Box**
- **Current:** "Ask Agy 🐾" button with full text placeholder
- **Issue:** May overflow on narrow screens (< 375px)
- **Proposed Solution:** Shorten placeholder text or use icon-only on mobile

#### 6. **"How Agy Searches" Modal**
- **Current:** Fixed heights, 3-column flow grid for steps
- **Issue:** Won't fit mobile viewport, horizontal scrolling
- **Proposed Solution:**
  - Stack 3-step flow vertically on mobile
  - Make modal full-screen with scrollable content
  - Adjust `max-height` for smaller screens

#### 7. **Related Projects Grid**
- **Current:** 3-column layout for related stories
- **Issue:** Columns too narrow on tablet/mobile
- **Proposed Solution:**
  ```css
  @media (max-width: 768px) {
      .related-projects-grid {
          grid-template-columns: 1fr; /* Stack to single column */
      }
  }
  ```

#### 8. **Status Bar**
- **Current:** "Semantic search active | Pinecone index ready | 130+ stories indexed"
- **Issue:** Text too long for mobile, may wrap awkwardly
- **Proposed Solution:** Abbreviate to "130+ stories | Search active" on mobile

### Recommended CSS Breakpoint Strategy

```css
/* Mobile-first approach */

/* Base styles (mobile) */
.chat-message {
    padding: 12px;
    font-size: 14px;
}

/* Tablet (768px and up) */
@media (min-width: 768px) {
    .chat-message {
        padding: 16px;
        font-size: 15px;
    }
}

/* Desktop (1024px and up) */
@media (min-width: 1024px) {
    .chat-message {
        padding: 24px;
        font-size: 15px;
    }
}
```

**Standard Breakpoints:**
- Mobile: `< 768px`
- Tablet: `768px - 1023px`
- Desktop: `1024px+`

**Test Devices:**
- iPhone SE: 375px (smallest modern phone)
- iPhone 14: 390px
- iPad: 768px
- Desktop: 1280px+

### Testing Approach

1. **Chrome DevTools:** Toggle Device Toolbar (`Cmd+Shift+M`)
2. **Test Viewports:**
   - iPhone SE (375px)
   - iPhone 14 (390px)
   - iPad (768px)
   - Desktop (1280px)
3. **Test Both Modes:** Light and dark mode at each breakpoint
4. **Real Device Testing:** Check touch targets, scroll behavior, input focus

### Streamlit Mobile Quirks

- **Sidebar:** Automatically converts to hamburger menu on mobile
- **st.columns():** Does NOT auto-stack on mobile - requires manual CSS overrides
- **Chat Input:** Sticky positioning may behave differently on mobile browsers
- **Touch Targets:** Must be minimum 44x44px (Apple Human Interface Guidelines)
- **Emotion Cache:** May generate different class names on mobile, test thoroughly

### Implementation Priority

**Phase 1: Critical Fixes (Mobile Usability)**
1. Stack navigation tabs vertically on mobile
2. Reduce chat avatar sizes to 48px on mobile
3. Adjust chat bubble padding for mobile
4. Make "How Agy Searches" modal full-screen on mobile

**Phase 2: Polish (Enhanced Experience)**
5. Optimize status bar text for mobile
6. Stack related projects grid to single column
7. Adjust header layout for mobile (stack vertically)
8. Test and refine touch targets

**Phase 3: Testing & Refinement**
9. Cross-browser testing (Safari iOS, Chrome Android)
10. Real device testing
11. Accessibility audit (VoiceOver, TalkBack)
12. Performance testing on slower connections

### Future Work: Progressive Web App (PWA)

Once mobile responsiveness is solid, consider:
- Add manifest.json for "Add to Home Screen"
- Service worker for offline support
- Push notifications for story updates
- Native app-like experience

---

## Future Enhancements

### Short-term (Next 2 weeks)
1. ~~Complete Phase 4 cleanup~~ ✅ Done (Phase 5 completed Nov 7, 2025)
2. ~~Add docstrings and type hints~~ (Partially done)
3. ~~Set up pre-commit hooks~~ ✅ Done (black, ruff, mypy)
4. **NEW:** Begin mobile responsiveness Phase 1 (critical fixes)

### Medium-term (Next month)
4. Add unit tests for components
5. Implement proper error boundaries
6. Add logging and observability
7. Complete mobile responsiveness testing

### Long-term (3-6 months)
8. Migrate to Next.js + React (mobile-first from start)
9. Replace Streamlit with FastAPI backend
10. Add proper state management (Redux/Zustand)
11. Consider PWA implementation

---

## Lessons Learned

### What Worked Well
✅ Component isolation fixed CSS bleeding immediately  
✅ Theme constants made color updates trivial  
✅ Clear file structure makes code reviews easier  
✅ Shows engineering maturity to hiring managers  
✅ **Systematic refactoring over 5 days prevented regression**  
✅ **Modular structure makes React migration straightforward**  
✅ **Daily commits with clear messages create excellent audit trail**  
✅ **Testing incrementally (commenting first) prevented breaking changes**

### What Was Challenging
❌ Streamlit's CSS specificity is difficult to override  
❌ Refactoring took 5 focused days  
❌ Managing circular dependencies during extraction  
❌ Finding all duplicate functions scattered across files  
❌ Distinguishing between dead code and legacy compatibility layers

### What We'd Do Differently
- Start with component architecture from day 1
- Use React instead of Streamlit for pixel-perfect UI
- Write tests alongside implementation
- Set up linting/formatting from the beginning
- Use automated tools to detect duplicates earlier

---

## Interview Talking Points

When presenting this codebase to potential employers:

### Architecture Highlights
- "**Reduced a 5,765-line monolith to a 284-line minimal router**"
- "**95.1% code reduction through systematic refactoring (5,481 lines removed)**"
- "**Zero circular dependencies, zero duplicates, zero dead code**"
- "Clear separation: pages for UI, services for logic, utils for helpers"
- "Config lives in services, not in the router - true separation of concerns"

### Process Highlights
- "**15 cleanup commits across two phases (October 22, November 7)**"
- "Phase 5 alone removed 699 lines across 3 sessions (imports, duplicates, config)"
- "Tested incrementally - commented code first, then deleted after validation"
- "Created comprehensive architecture documentation as refactoring guide"
- "Ready for team collaboration - modular, documented, maintainable"
- "Used static analysis + grep verification to identify all dead code systematically"

### Technical Depth
- "Extracted Pinecone semantic search to isolated service"
- "Built reusable validation and scoring utilities"
- "Implemented proper configuration management"
- "Can discuss trade-offs between Streamlit and React"

---

## UI/UX Polish Sessions (October-November 2025)

### Overview
Multiple focused sessions to fix UI bugs and polish the user experience across Explore Stories and Ask MattGPT pages.

---

### Session 1: Explore Stories Fixes (October 2025)

**Issues Fixed:**

1. **White Header Band Issue** ✅
   - **Problem:** White band appearing above dark navy navbar
   - **Root Cause:** Streamlit header element had white background
   - **Solution:** Force transparent background on all header elements
   - **File:** `ui/styles/global_styles.py` (lines 31-46)
   ```css
   header[data-testid="stHeader"],
   header[data-testid="stHeader"] * {
       background: rgba(0,0,0,0) !important;
   }
   ```

2. **Detail Pane Stuck Issue** ✅
   - **Problem:** Story detail pane from Ask MattGPT persisted when switching to Explore Stories
   - **Root Cause:** `active_story` session state not cleared on tab navigation
   - **Solution:** Flag-based cleanup using `_just_switched_to_explore`
   - **Files:**
     - `ui/components/navbar.py` (lines 87-89) - Set flag on navigation
     - `ui/pages/explore_stories.py` (lines 500-510) - Clear state when flag detected

3. **Card View Switching Issue** ✅
   - **Problem:** Switching to card view cleared the selected story from Ask MattGPT
   - **Root Cause:** Same as #2 - aggressive state cleanup
   - **Solution:** `_just_switched_to_explore` flag ensures cleanup only happens on actual tab switch

4. **Banner Showing Raw HTML** ✅
   - **Problem:** No-match banner rendering as raw HTML instead of styled component
   - **Root Cause:** Banner CSS not being applied in chat context
   - **Solution:** Inline CSS with proper markdown rendering
   - **File:** `utils/ui_helpers.py` (lines 319-360)

**Status:** All confirmed fixed by user

---

### Session 2: Story Detail Component Extraction (October 2025)

**New Component Created:** `ui/components/story_detail.py` (untracked file)

**Purpose:** Shared story detail renderer used by both Explore Stories and Ask MattGPT

**Key Functions:**
- `render_story_detail()` - Full STAR narrative display with sidebar
- `on_ask_this_story()` - Navigation handler for "Ask Agy About This" button
- `_smart_list_detection()` - Parses nested lists and bullet points from JSONL data

**Benefits:**
- DRY principle - single source of truth for story detail rendering
- Consistent UX across Explore Stories and Ask MattGPT
- Easier maintenance - fix once, applies everywhere

**Integration Points:**
- Explore Stories: Story detail panel (lines 500-600)
- Ask MattGPT: Source expanders in conversation view (lines 3800-3900)

**Status:** Created but not yet tracked in git

---

### Session 3: Transition Indicator Visibility (November 9, 2025)

**Problem:** The "🐾 Tracking down insights..." transition indicator was washing out during page transitions from Explore Stories to Ask MattGPT, making it hard for users to see progress feedback.

**Root Cause:** Initial styling used semi-transparent backgrounds and medium gray text, which lost contrast when the page "whited out" during Streamlit reruns.

**Solution Evolution (7 iterations):**

1. **Initial attempt:** Darker text color `#6B7280` + opacity lock
   - Result: Still too light during transition

2. **Second attempt:** Even darker text `#1F2937` + bold weight
   - Result: No visible improvement, needed Streamlit restart

3. **Third attempt:** Purple-tinted background with stronger opacity
   - Result: User feedback: "worse than before" - wrong color approach

4. **Fourth attempt:** Neutral gray with transparency `rgba(243, 244, 246, 0.95)`
   - Result: Still insufficient contrast during whiteout

5. **Final solution:** Solid colors with maximum contrast
   ```css
   .transition-indicator-bottom {
       background: #F3F4F6 !important;     /* Solid gray, not transparent */
       color: #374151 !important;          /* Dark gray text */
       border: 1px solid #D1D5DB !important;
       padding: 12px 24px;                 /* Increased from 10px 18px */
       border-radius: 24px;                /* Increased from 20px */
       box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
   }
   ```

**Files Modified:**
- `ui/pages/ask_mattgpt.py` (lines 2879-2899) - Transition indicator styling

**Key Learnings:**
- Transparent backgrounds don't work during Streamlit page transitions
- Solid colors with high contrast are essential for visibility during reloads
- Visual weight (padding, shadow) matters as much as color contrast
- Iterative user feedback is critical for CSS refinements

**Status:** ✅ Improved visibility, awaiting user feedback for final validation

---

### Known Outstanding Issues (Future Work)

From SESSION_HANDOFF_SESSION10.md - Ask MattGPT Conversation View:

1. **Navbar Position** - Conversation view navbar sits lower than landing page
2. **"How Agy searches" Button** - Header button not triggering modal
3. **Status Bar Alignment** - Doesn't match landing page styling
4. **Action Buttons** - Helpful/Copy/Share buttons not functional
5. **Purple Left Border** - AI messages missing 4px purple border from wireframe
6. **Input/Footer Overlap** - Chat input renders after footer, causing overlap

**Recommendation:** Address these in future session with structural code changes, not CSS-only fixes.

---

### Session 4: About Matt Timeline Visualization (November 10, 2025)

**Objective:** Implement Career Timeline section matching wireframe specifications exactly.

**Wireframe Reference:** https://mcpugmire1.github.io/mattgpt-design-spec/wireframes/about_matt_wireframe.html

**Implementation Details:**

**1. Timeline Structure (7 Career Positions)**
- Data structure: year, title (with emoji), company, single-line description
- Timeline spans: 2023–Present through 2000–2005
- Content aligned with wireframe exactly (no deviations)

**2. CSS Implementation** (`ui/pages/about_matt.py`, lines 158-226)

**Timeline Container:**
```css
.timeline {
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    padding-left: 40px;
}
```

**Vertical Purple Gradient Line:**
```css
.timeline::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;  /* Increased from 3px to match wireframe */
    background: linear-gradient(to bottom, #8B5CF6, #7C3AED);
}
```

**Circular Dot Markers:**
```css
.timeline-item::before {
    content: '';
    position: absolute;
    left: -50px;
    top: 4px;
    width: 20px;   /* Increased from 14px for better visibility */
    height: 20px;
    background: white;
    border: 4px solid #8B5CF6;  /* Increased from 3px */
    border-radius: 50%;
}
```

**Typography Styling:**
- `.timeline-year`: 14px, weight 700, purple (#8B5CF6), 8px margin-bottom
- `.timeline-title`: 18px, weight 600, dark gray (#2c3e50), 6px margin-bottom
- `.timeline-company`: 14px, gray (#7f8c8d), 8px margin-bottom
- `.timeline-desc`: 14px, dark gray (#555), line-height 1.6

**3. Rendering Approach**

**Challenge:** Streamlit wraps each `st.markdown()` call in full-width container divs, breaking the 900px max-width constraint.

**Solution:** Build complete HTML in single string before rendering:
```python
timeline_items = []
for item in timeline_data:
    timeline_items.append(f"""
    <div class="timeline-item">
        <div class="timeline-card">
            <div class="timeline-year">{item["year"]}</div>
            <div class="timeline-title">{item["title"]}</div>
            <div class="timeline-company">{item["company"]}</div>
            <div class="timeline-desc">{item["desc"]}</div>
        </div>
    </div>""")

timeline_html = '<div class="timeline">' + ''.join(timeline_items) + '</div>'
st.markdown(timeline_html, unsafe_allow_html=True)
```

**4. Key Technical Decisions**

- **No card backgrounds:** Cards use `transparent` background to match wireframe's minimal design
- **CSS pseudo-elements:** Vertical line and dots render via `::before` selectors
- **Single HTML block:** Prevents Streamlit container wrapping issues
- **Inline concatenation:** Avoids f-string escaping problems

**5. Iterations Required**

1. Initial: Used card backgrounds (white) - removed to match wireframe
2. Circle size: 14px → 20px for better visual weight
3. Line width: 3px → 4px to match wireframe prominence
4. HTML rendering: Multiple `st.markdown()` calls → single consolidated block
5. Avatar: Replaced "MP" initials with Agy logo from brand kit

**Files Modified:**
- `ui/pages/about_matt.py` (lines 158-364) - Timeline CSS and rendering

**Status:** ✅ Complete - Timeline matches wireframe exactly

**Visual Verification:**
- Purple vertical gradient line visible
- Larger circular dots (20px) properly positioned
- 7 career positions with correct content
- Clean minimal design without card backgrounds
- Max-width 900px centered layout

---

**Last Updated:** November 10, 2025
**Author:** Matt Pugmire
**Review Status:** ✅ **Phase 5 Complete + UI Polish Sessions**
**GitHub:** Ready to share with hiring managers and technical interviewers
**Key Metric:** 95.1% code reduction (5,765 → 284 lines in app.py)