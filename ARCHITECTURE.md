# Architecture Documentation

## Table of Contents

### 📋 Overview
- [Executive Summary](#executive-summary)
- [System Overview](#system-overview)
  - [Current Architecture](#current-architecture)
  - [Startup Sequence](#startup-sequence-apppy)

### 📚 History & Context
- [Refactoring History](#refactoring-history)

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

### 📋 Data Governance
- [Data Governance & Master Source](#data-governance--master-source)
  - [Principle](#principle)
  - [Hybrid Sovereignty Model](#hybrid-sovereignty-model)
  - [January 2026 Sovereignty Patterns](#january-2026-sovereignty-patterns)
    - [Dynamic Identity (MATT_DNA)](#1-dynamic-identity-matt_dna)
    - [Multi-Field Entity Gate](#2-multi-field-entity-gate)
    - [UI Hydration](#3-ui-hydration)
  - [Master Data Source](#master-data-source)
  - [Ingestion Workflow](#ingestion-workflow)
  - [What Derives from JSONL](#what-derives-from-jsonl-at-runtime)
  - [Curated Content](#curated-content-intentionally-static)
  - [Anti-Patterns](#anti-patterns-dont-do-this)
  - [Warning: No Manual JSONL Surgery](#️-warning-no-manual-jsonl-surgery)

### 🎨 CSS Architecture
- [CSS Scoping Patterns](#css-scoping-patterns)
- [Streamlit-Specific Challenges](#streamlit-specific-challenges)

### 📱 Mobile & Responsive Design
- [Mobile Responsiveness Roadmap](#mobile-responsiveness-roadmap)
  - [Known Mobile Issues](#known-mobile-issues)
  - [CSS Breakpoint Strategy](#recommended-css-breakpoint-strategy)
  - [Testing Approach](#testing-approach)
  - [Implementation Priority](#implementation-priority)

### 🔮 Future Work
- [Future Enhancements](#future-enhancements)

### 📊 Appendix: RAG Pipeline Audit
- [RAG Pipeline Audit (January 2026)](#rag-pipeline-audit-january-2026)
  - [Data Flow Map](#data-flow-map)
  - [Embedding Analysis](#embedding-analysis)
  - [Ranking Pipeline Order of Operations](#ranking-pipeline-order-of-operations)
  - [Test Coverage Analysis](#test-coverage-analysis)
  - [Architecture Issues](#architecture-issues)
  - [Hardcoded Values Audit](#hardcoded-values-audit)
  - [Summary Findings](#summary-findings)

---

## Executive Summary

**Project:** MattGPT Portfolio Assistant - AI-powered career story search and chat interface
**Tech Stack:** Streamlit, OpenAI GPT-4o, Pinecone vector DB, Python 3.11+
**Data Corpus:** 130+ STAR-formatted transformation project stories
**Last Updated:** January 24, 2026

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
- Minimal circular dependencies (one deferred import for `sync_portfolio_metadata`)

### Current State (January 2026)

**RAG Quality Sprint (Jan 21-24, 2026) — 100% eval pass rate (31/31):**
- Model upgrade: GPT-4o-mini → GPT-4o (temperature 0.4 standard / 0.2 synthesis)
- XML Context Isolation: `<primary_story>` / `<supporting_story>` tags prevent cross-story bleed
- Narrative skip-diversity: narrative queries trust Pinecone semantic ranking (no diversity reorder)
- Entity pinning: detected entities pin matching story to #1 in standard mode
- Multi-Field Entity Gate: searches across 5 entity fields via Pinecone `$or`
- Dynamic MATT_DNA + SYNTHESIS_THEMES: derived from JSONL at startup (Single Source of Truth)
- Fact-pairing + texture rules: metrics stay pinned to source, distinctive phrases preserved verbatim
- UI Hydration: all landing page counts derived dynamically from story data
- Breadcrumb chip navigation, compact filter chips, updated about/modal pages

**Ask MattGPT Modular Architecture:**
- Landing view with capability cards and sample queries
- Conversation view with RAG-powered responses
- Unified header component across all views
- "How Agy Searches" modal with 3-step flow visualization
- Dark mode support via CSS variables

**Core Features:**
- Semantic search across 130+ project stories
- Query validation via nonsense filter + Pinecone confidence gating
- Context-aware follow-up questions
- Story intelligence (theme/persona inference)
- Responsive chat UI with thinking indicators

### What This Document Contains

1. **System Overview:** Current file structure, components, services (as of Jan 2026)
2. **Data Pipeline:** Excel → JSONL → Embeddings → Pinecone → RAG
3. **CSS Architecture:** Scoping patterns, emotion-cache strategies, dark mode
4. **Mobile Roadmap:** Known issues, breakpoint strategy, implementation phases
5. **Future Enhancements:** Short, medium, and long-term roadmap

**For migration history and refactoring details,** see [REFACTORING_HISTORY.md](REFACTORING_HISTORY.md)

---


## System Overview

### Current Architecture

The MattGPT Portfolio Assistant is built with a component-based architecture emphasizing separation of concerns and modularity.

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
│   │   ├── thinking_indicator.py      # ✨ Loading/processing indicator (3 KB)
│   │   └── timeline_view.py           # Era-based timeline for Explore Stories
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                    # Home page (38 lines)
│   │   ├── explore_stories.py         # Stories browser (1,306 lines)
│   │   ├── ask_mattgpt/               # ✅ Modular structure (Dec 2025)
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
├── echo_star_stories.jsonl         # Raw story corpus (130 stories)
├── echo_star_stories_nlp.jsonl     # NLP-enriched story corpus (production)
├── nonsense_filters.jsonl          # Off-domain query rules
│
├── data/
│   ├── offdomain_queries.csv       # Query telemetry log (generated)
│   └── borderline_queries.csv      # Edge case queries for testing
│
├── assets/
│   └── (images, SVGs, diagrams)
│
└── .streamlit/
    └── config.toml                 # Streamlit theme config


---

### Startup Sequence (`app.py`)

The application initialization order is critical—later steps depend on earlier outputs:

```
┌──────────────────────────────────────────────────────────────┐
│  1. load_star_stories(DATA_FILE)                             │
│     - Reads echo_star_stories_nlp.jsonl                      │
│     - Returns STORIES list (130+ dicts)                      │
│     - Enforces stable IDs, normalizes list fields            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  2. initialize_vocab(STORIES)                                │
│     - Builds corpus vocabulary for search scoring            │
│     - Lives in: services/rag_service.py                      │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  3. sync_portfolio_metadata(STORIES)                         │
│     - Derives SYNTHESIS_THEMES from story Theme fields       │
│     - Derives _KNOWN_CLIENTS from story Client fields        │
│     - Generates MATT_DNA prompt via generate_dynamic_dna()   │
│     - Lives in: ui/pages/ask_mattgpt/backend_service.py      │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  4. build_facets(STORIES)                                    │
│     - Extracts filter options (industries, capabilities,     │
│       clients, domains, roles, tags)                         │
│     - Used by Explore Stories filter widgets                  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│  5. Page Rendering                                           │
│     - Routes to active_tab page                              │
│     - Landing pages receive STORIES for hydration            │
│     - Ask MattGPT uses synced metadata for RAG              │
└──────────────────────────────────────────────────────────────┘
```

**Key Invariant:** Steps 1-3 run on every Streamlit rerun but are idempotent. `sync_portfolio_metadata()` regenerates globals each time, ensuring any JSONL change is picked up without restart.

---

### Shared Components (`ui/components/`)

Reusable UI components shared across multiple pages.

| Component | Job | Used By | Key Functions |
|-----------|-----|---------|---------------|
| **navbar.py** | Top navigation bar (desktop + mobile hamburger) | All pages via app.py | `render_navbar()` |
| **footer.py** | Contact info, availability, "Ask MattGPT" CTA | All pages | `render_footer()` |
| **hero.py** | Gradient hero section with stats | Home | `render_hero()`, `render_stats_bar()`, `render_section_title()` |
| **category_cards.py** | Industry/capability exploration cards | Home | `render_category_cards()` |
| **story_detail.py** | Full STAR narrative with sidebar | Explore Stories, Ask MattGPT (Related Projects) | `render_story_detail(detail, key_suffix, stories)` |
| **timeline_view.py** | Era-based timeline with collapsible sections | Explore Stories | `render_timeline_view(stories, on_story_click)` |
| **ask_mattgpt_header.py** | Unified header + "How Agy Searches" button | Ask MattGPT (Landing + Conversation) | `render_ask_header()`, `get_ask_header_css()` |
| **how_agy_modal.py** | "How Agy Finds Your Stories" modal content | Ask MattGPT | `get_how_agy_flow_html()`, `get_how_agy_modal_html()` |
| **thinking_indicator.py** | Animated loading indicator | Ask MattGPT, Explore Stories | `render_thinking_indicator()` |

**story_detail.py Key Pattern:**
```python
# "Ask Agy About This" button flow (see Cross-Page Navigation section)
def handle_ask_about_this(detail: dict):
    st.session_state["seed_prompt"] = f"Tell me more about: {detail.get('Title')}"
    st.session_state["active_story"] = detail.get("id")
    st.session_state["active_story_obj"] = detail
    st.session_state["__ctx_locked__"] = True
    st.session_state["__ask_from_suggestion__"] = True
    st.session_state["active_tab"] = "Ask MattGPT"
    st.rerun()
```

**timeline_view.py Key Pattern:**
```python
# Era configuration
ERA_ORDER = [
    "Independent Product Development",           # 2024-2025
    "Enterprise Innovation & Transformation",    # 2019-2023
    "Cloud-Native Prototyping & Product Shaping", # 2018-2019
    "Financial Services Platform Modernization", # 2008-2018
    "Integration & Platform Foundations",        # 2005-2008
]
EXCLUDED_ERA = "Leadership & Professional Narrative"  # Not shown in timeline
MAX_STORIES_PER_ERA = 6

# "View in Explore" navigation
st.session_state["prefilter_era"] = era_name
st.session_state["prefilter_view_mode"] = "table"
st.session_state["active_tab"] = "Explore Stories"
```

---

## Refactoring History

This codebase underwent a systematic component-based refactoring from October 18 - November 7, 2025. The refactoring reduced `app.py` from 5,765 lines to 284 lines (95.1% reduction) through:

- **Component extraction**: Modularized monolithic `ask_mattgpt.py` (4,696 lines) into 8-file directory structure
- **Duplicate elimination**: Removed 20+ duplicate functions scattered across files
- **Dead code removal**: Eliminated 1,400+ lines (zombie functions, commented blocks, unused imports/config)
- **Architectural improvements**: Zero circular dependencies, clear separation of concerns

**Key Metrics:**
- 95.1% code reduction in app.py (5,765 → 284 lines)
- 5-day systematic migration (Oct 18 - Nov 7, 2025)
- 15 atomic commits with clear audit trail
- Zero regressions through incremental testing

**For complete details** including migration phases, commit history, lessons learned, and interview talking points, see [REFACTORING_HISTORY.md](REFACTORING_HISTORY.md).

---

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
Semantic Search Results → RAG → GPT-4o → User
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
[Intent Classification - backend_service.py]
- Semantic router intent_family (embedding-based, 11 families)
- Entity detection → (field, value) for scoped retrieval
- classify_query_intent() fallback for edge cases
      ↓
[Retrieval Strategy - based on intent]
- STANDARD MODE: entity pin → diversify_results() → top 7 with client variety
- NARRATIVE MODE: sort by Pinecone score (skip diversity)
- SYNTHESIS MODE: theme-filtered parallel search → named-clients-first (up to 9)
      ↓
[Context Assembly - ui/pages/ask_mattgpt/backend_service.py]
- XML isolation: <primary_story> + <supporting_story> tags
- Build prompt with STAR narratives + theme guidance
- Include MATT_DNA ground truth (dynamic from JSONL)
      ↓
[LLM Generation - OpenAI GPT-4o]
- STANDARD: Primary story focus, human stakes → methodology → outcomes
- SYNTHESIS: Theme/pattern → evidence across projects → insight
- Temperature: 0.4 (standard) / 0.2 (synthesis)
      ↓
[Response Formatting - ui/pages/ask_mattgpt/conversation_helpers.py]
- Extract answer + sources
- Render with citations
- Display expandable story details
      ↓
User receives cited, STAR-formatted answer
```

---

### Synthesis Mode (Updated January 2026)

**Problem:** RAG retrieves individual stories well but struggles with big-picture questions like "What are common themes?" or "What patterns do you see?" — these need holistic context, not a single story.

**Solution:** Intent-aware retrieval that changes strategy based on query type, with entity-first classification.

**Intent Classification (Hybrid: Semantic Router + Entity Detection):**

Primary classification uses the embedding-based semantic router (`services/semantic_router.py`) which maps queries to intent families without LLM cost. Entity detection runs in parallel to identify company/project mentions.

```
Query → Semantic Router (embedding similarity)
      → Entity Detection (substring matching against known entities)
      → Intent Family Resolution:
        1. ENTITY ANCHOR: Company/Project mentioned → client (overrides verbs)
        2. BIOGRAPHICAL ANCHOR: Narrative fragments → narrative
        3. SYNTHESIS: No entity + cross-cutting question → synthesis
        4. BEHAVIORAL: STAR-style questions → behavioral
        5. TECHNICAL: Technology without company → technical
        6. BACKGROUND: Career history → background
        7. OUT_OF_SCOPE: Industries Matt hasn't worked in → out_of_scope
        8. GENERAL: Everything else → general
```

**Key Rule:** Entity detection OVERRIDES verb patterns.
- "How did Matt scale at Accenture?" → `client` (not synthesis)
- "What are Matt's core themes?" → `synthesis` (no entity)

**Retrieval Strategies:**

| Intent | Stories Retrieved | Retrieval Method |
|--------|-------------------|------------------|
| synthesis | 7-9 (up to 3 per theme) | Theme-filtered search, named-clients-first sorting |
| narrative | 7 | Sort by Pinecone score (skip diversity) |
| client | 7 | Entity pin to #1 → diversify_results() |
| behavioral | 7 | Entity pin (if detected) → diversify_results() |
| technical | 7 | Entity pin (if detected) → diversify_results() |
| background | 7 | Entity pin (if detected) → diversify_results() |
| general | 7 | Entity pin (if detected) → diversify_results() |

**Synthesis Retrieval (get_synthesis_stories):**
1. Embed USER's actual query (not fixed theme keywords)
2. For each theme: Pinecone query with `filter={"Theme": theme}` + user embedding
3. If entity detected: Add entity filter (e.g., `{"Division": "Cloud Innovation Center"}`)
4. Up to 3 stories per theme, skip themes with no entity-scoped results
5. Sort by score, then named-clients-first (JP Morgan/RBC beat "Independent")
6. Return top 9 stories

**Entity Detection (Multi-Field):**
Checks fields in order: Client, Employer, Division, Project, Place
- "CIC" normalizes to Division: "Cloud Innovation Center"
- "JPMorgan" normalizes to Client: "JP Morgan Chase"
- Excludes generic values: "Multiple Clients", "Independent"

**Synthesis Prompt Mode:**
- Different system prompt focused on patterns/themes
- Asks for breadth across stories, not depth on one
- Structure: Theme → Evidence from 2-4 clients → Insight
- Dynamic client list derived from retrieved stories (no hardcoded names)
- Longer responses (250-400 words)

**Cost:**
- Intent classification: ~$0.0000002 per query (embedding similarity, no LLM call)
- LLM generation: GPT-4o (~$0.01-0.02 per query, 700 max tokens)
- Total per query: ~$0.02

**Self-Maintenance:**
- Semantic router handles novel phrasings via embedding similarity
- New story themes automatically picked up via `sync_portfolio_metadata()` at startup
- MATT_DNA prompt regenerated on each deploy with current client/theme data

---

## Component Contracts (Updated January 2026)

This section defines the **job, rules, and constraints** for each retrieval component. Update this when changing retrieval logic.

### Layer 1: Validation (Fast, Free)

#### Nonsense Filters
- **Job:** Regex-based rejection of obvious off-topic queries (weather, sports, crypto)
- **Lives in:** `nonsense_filters.jsonl` + `utils/validation.py:is_nonsense()`
- **Cost:** Zero (pure regex, no API calls)
- **Rule:** Runs FIRST before any embedding or LLM cost

#### Semantic Router
- **Job:** Embedding-based intent classification to reject borderline off-topic queries
- **Lives in:** `services/semantic_router.py`
- **Thresholds:** HARD_ACCEPT=0.80, SOFT_ACCEPT=0.72
- **Intent Families:** 11 categories (background, behavioral, delivery, team_scaling, leadership, technical, domain_payments, domain_healthcare, stakeholders, innovation, agile_transformation)
- **Cost:** ~$0.0000002 per query (one embedding)
- **Rule:** Fail-open on errors (accept query if embedding fails)
- **Do not remove:** Saves LLM cost, prevents garbage-in

### Layer 2: Intent Classification (Hybrid)

#### Semantic Router Intent Family (Primary)
- **Job:** Map query to intent family via embedding similarity (no LLM cost)
- **Lives in:** `services/semantic_router.py`
- **Families:** narrative, behavioral, delivery, team_scaling, leadership, technical, etc.
- **Cost:** Free (reuses embedding from validation step)

#### LLM Intent Classifier (Fallback)
- **Job:** Route queries to synthesis/client/narrative/behavioral/technical/background/out_of_scope/general
- **Lives in:** `ui/pages/ask_mattgpt/backend_service.py:classify_query_intent()`
- **Model:** gpt-4o-mini (~$0.0001 per query, only called when semantic router insufficient)
- **Priority Hierarchy:**
  1. **ENTITY ANCHOR** (Company/Project name) → `client`
  2. **BIOGRAPHICAL ANCHOR** (narrative fragments) → `narrative`
  3. **SYNTHESIS** (no entity + cross-cutting question) → `synthesis`
  4. **BEHAVIORAL** (STAR-style questions) → `behavioral`
  5. **TECHNICAL** (technology questions without company) → `technical`
  6. **BACKGROUND** (career history) → `background`
  7. **OUT_OF_SCOPE** (industries Matt hasn't worked in) → `out_of_scope`
  8. **GENERAL** (everything else) → `general`
- **Rule:** Entity detection OVERRIDES verb patterns ("How did Matt scale at Accenture?" → `client`, not `synthesis`)
- **Do not add more intents** without updating this doc and the eval suite

#### Entity Detection
- **Job:** Detect company/project/division mentions in query for scoped retrieval
- **Lives in:** `ui/pages/ask_mattgpt/backend_service.py:detect_entity()`
- **Fields checked (in order):** Client, Employer, Division, Project, Place
- **Normalization:** "jpmorgan" → "JP Morgan Chase", "cic" → "Cloud Innovation Center", etc.
- **Exclusions:** "Multiple Clients", "Independent", "Career Narrative" (too generic to filter)
- **Returns:** `(field_name, entity_value)` tuple or `None`

#### Multi-Field Entity Gate (January 2026)
- **Job:** Search across ALL entity fields when entity detected, not just the primary field
- **Lives in:** `services/pinecone_service.py:189-216`
- **Implementation:** Uses Pinecone `$or` operator to search across 5 fields simultaneously
- **Fields searched:** `client`, `employer`, `division`, `project`, `place`
- **Casing rules:**
  - **Lowercase fields:** `division`, `employer`, `project`, `place` → `.lower()` applied
  - **PascalCase fields:** `client` → preserve original casing
- **Example:** Query "Accenture work" searches:
  ```python
  {"$or": [
      {"client": {"$eq": "Accenture"}},
      {"employer": {"$eq": "accenture"}},
      {"division": {"$eq": "accenture"}},
      {"project": {"$eq": "accenture"}},
      {"place": {"$eq": "accenture"}}
  ]}
  ```
- **Why:** Fixes "entity blind spot" where stories with `Client="Confidential"` but `Employer="Accenture"` weren't found

#### Entity Normalization Map

Common aliases normalized to canonical JSONL values before entity matching.

**Lives in:** `backend_service.py:315-323` (`ENTITY_NORMALIZATION` constant)

| Alias (user input) | Normalized Value | Field |
|---------------------|-----------------|-------|
| `jpmorgan`, `jp morgan`, `jpmorgan chase` | `JP Morgan Chase` | Client |
| `amex` | `American Express` | Client |
| `at&t mobility` | `AT&T Mobility` | Client |
| `cic` | `Cloud Innovation Center` | Division |
| `liquid studio` | `Atlanta Liquid Studio` | Division |

**Matching Logic:** Aliases checked first (case-insensitive substring). If alias found, the normalized value is used to identify the correct field from story data. Falls back to `Client` if entity not found in any field.

#### Excluded Entities & Clients

Two related constants prevent overly generic values from triggering entity filters or appearing in UI:

**`EXCLUDED_ENTITIES`** — Values too generic to filter on in Pinecone queries.
**Lives in:** `backend_service.py:302-312`

| Value | Reason |
|-------|--------|
| `Multiple Clients` | Would match too broadly |
| `Multiple Financial Services Clients` | Same |
| `Independent` | Personal projects, not a real client |
| `Career Narrative` | Meta-content, not a client |
| `Sabbatical` | Not a work engagement |
| `Various`, `N/A`, `""`, `None` | Empty/placeholder values |

**`EXCLUDED_CLIENTS` / `_EXCLUDED_CLIENTS`** — Values excluded from UI counts and pills.
**Lives in:** `backend_service.py:44-49`, `banking_landing.py:16-22`, `category_cards.py:17-23`

| Value | Appears In |
|-------|------------|
| `Independent` | All |
| `Career Narrative` | All |
| `Multiple Clients` | All |
| `Personal` | backend_service.py |
| `Various` | All |
| `Multiple Financial Services Clients` | Landing pages |
| `Financial Services Client` | Landing pages |

**Note:** These constants are defined separately in each file. If a new exclusion is needed, update all locations.

### Layer 3: Retrieval

#### Confidence Gating
- **Job:** Reject queries where Pinecone returns low-confidence results
- **Lives in:** `services/rag_service.py:semantic_search()`
- **Thresholds:**
  - `CONFIDENCE_HIGH = 0.25` → "Found X stories"
  - `CONFIDENCE_LOW = 0.20` → Filter threshold
  - Below 0.20 → `confidence="none"` (reject)
- **Rule:** Trust semantic router for high-confidence behavioral matches (score ≥ 0.80)

#### Standard Mode
- **Job:** Answer specific questions about one story/client/topic
- **Triggers:** Intent = client, behavioral, technical, background, general
- **Retrieval:**
  1. User query → OpenAI embedding
  2. Pinecone vector search (top 100) with multi-field entity filter if detected
  3. Confidence gating
  4. **Entity pinning:** If entity detected, pin matching story to #1 (title substring match for Division/Project, Pinecone score for Client/Employer)
  5. `diversify_results()` on remaining stories → named clients first, max 1 per client
- **Lives in:** `services/rag_service.py` + `backend_service.py:rag_answer()`
- **Story limit:** 7 stories to LLM context

#### Narrative Mode
- **Job:** Answer biographical/philosophy questions (leadership journey, early failure, etc.)
- **Triggers:** Intent family = `narrative` (from semantic router)
- **Retrieval:**
  1. Same as Standard (steps 1-3)
  2. **Skip diversity:** If `pool[0]` is Professional Narrative, preserve it at #1
  3. Diversify remaining stories
- **Lives in:** `backend_service.py:rag_answer()` (narrative branch)
- **Rationale:** Title is now embedded in Pinecone, so semantic search naturally finds narrative stories. The `intent_family == "narrative"` branch protects against diversity demotion.

#### Synthesis Mode
- **Job:** Answer "what are Matt's themes/patterns/philosophy" questions
- **Triggers:** Intent = `synthesis` (no entity + cross-cutting question)
- **Retrieval:**
  1. User query → OpenAI embedding (NOT fixed theme keywords)
  2. For each theme: Pinecone query with `filter={"Theme": theme}` + user embedding
  3. If entity detected: Add entity filter (e.g., `{"Theme": theme, "Client": "Accenture"}`)
  4. Up to 3 stories per theme
  5. Skip themes with no results for detected entity
  6. **Named-clients-first:** Sort named clients (JP Morgan, RBC) above generic (Independent, Career Narrative)
- **Lives in:** `backend_service.py:get_synthesis_stories()`
- **Story limit:** 9 stories to LLM context
- **MUST use:** User's actual query embedding for semantic relevance
- **MUST NOT:** Ignore user's query for fixed theme keywords (previous bug)

### Layer 4: Response Generation

#### Agy Voice Generator
- **Job:** Transform retrieved stories into WHY→HOW→WHAT narrative with Agy personality
- **Lives in:** `backend_service.py:_generate_agy_response()`
- **Model:** GPT-4o
- **Persona:** Agy 🐾 — Matt Pugmire's Plott Hound assistant (named after his late dog Agador Spartacus)
- **Temperature:** 0.2 (synthesis) / 0.4 (standard) — low to reduce hallucination and preserve texture
- **Max tokens:** 700
- **Word target:** 250-400 words (up from 200-300)

**Response Structure:**
- **Standard mode:** Human stakes → How Matt tackled it → What changed → Pattern insight
- **Synthesis mode:** Name patterns → Prove with client examples → Connect the thread

**Python-Driven Randomization** (for variety):
- 10 standard mode openings ("🐾 Found it!", "🐾 Great question!", etc.)
- 5 synthesis mode openings ("🐾 Looking across Matt's portfolio...", etc.)
- 8 standard closings ("Want me to dig deeper?", etc.)
- 4 synthesis closings ("Which pattern would you like to explore?", etc.)
- 6 focus angles: human impact, methodology, scale, leadership, outcomes, innovation

**MATT_DNA Ground Truth** (dynamically generated from JSONL — January 2026):

The `MATT_DNA` grounding prompt is now generated dynamically via `generate_dynamic_dna()` in `backend_service.py:160-273`. Client names are derived from the JSONL story data, ensuring the prompt never drifts from the source of truth.

**Dynamic Elements (derived from JSONL):**
- **Banking clients:** Derived from stories where `Industry = "Financial Services / Banking"`
- **Telecom clients:** Derived from stories where `Industry = "Telecommunications"`
- **Transport clients:** Derived from stories where `Industry = "Transportation & Logistics"`

**Static Elements (curated):**
```
Identity: "I build what's next, modernize what's not, and grow teams along the way."

Career Arc: Software Engineer → Solution Architect → Director → CIC Leader
- Accenture: March 2005 - September 2023 (18+ years)
- Built CIC from 0 to 150+ practitioners

Themes of Matt's Work (dynamically derived from JSONL Theme field):
1. Execution & Delivery (PRIMARY) — shipping production systems at scale
2. Strategic & Advisory — thought partnership, executive influence
3. Org & Working-Model Transformation — culture change, agile adoption
4. Talent & Enablement — coaching, mentorship, capability building
5. Risk & Responsible Tech — governance, compliance
6. Emerging Tech — GenAI/ML exploration with production value
7. Professional Narrative — philosophy, leadership identity
(Note: count and names auto-update from JSONL via sync_portfolio_metadata())

GROUNDING RULES:
1. ONLY cite clients/projects/metrics from retrieved stories
2. If unsure, say "In one engagement..." instead of naming client
3. NEVER invent outcomes or mention unlisted clients
4. For revenue impact, emphasize delivery excellence (not sales)
5. For synthesis, lead with Themes + diverse client examples
```

**Why Dynamic:** Previously had hardcoded "JPMorgan, Capital One, Fiserv" which drifted from JSONL canonical names ("JP Morgan Chase"). Now uses Single Source of Truth pattern.

**Banned Corporate Filler Phrases:**
- "meaningful outcomes" → use actual outcomes
- "strategic mindset" → describe what Matt did
- "foster collaboration" → describe specific collaboration
- "stakeholder alignment" → name actual stakeholders
- "bridge the gap" → describe specific connection
- "execution excellence" → say "he ships"
- "high-trust engineering cultures" → be specific
- "modern development practices" → name the actual practices from the story
- "significant challenges" → describe the actual challenge
- "adapt to new approaches" → name what they adapted to
- "rapidly evolving digital landscape" → name the specific market pressure
- "fostering a culture of" → describe what actually happened
- "agile methodologies" → name the specific methodology (Lean XP, TDD, etc.)
- "remain competitive" → describe the specific business pressure
- "continuous improvement" → describe what specifically improved

**Persona Transformation Rules** (I → Matt):
```
| Source (Matt's voice) | Output (Agy's voice) |
| I/Me/My               | Matt/Him/His         |
| In my journey         | Throughout Matt's career |
| I've learned          | Matt learned / Matt demonstrated |
| I led                 | Matt led             |
```
Banned starters: "In my journey", "I've encountered", "In my experience"

**Context Isolation via XML Tags** (prevents cross-story hallucination):

Stories are wrapped in XML tags before injection into the LLM prompt:
```xml
<primary_story>
  [Full story context - main focus of response]
</primary_story>

<supporting_story index="2">
  [Background context only - do NOT pull details into primary narrative]
</supporting_story>
```

**Rules enforced in system prompt:**
- `<primary_story>` is the MAIN story — response should primarily be about THIS story
- `<supporting_story>` tags are background context ONLY
- Do NOT use a client name from a supporting story to label the primary story
- A metric from a supporting story CANNOT appear in discussion of the primary story
- If Client="Multiple Clients" → say "across multiple engagements" even if named client in supporting story
- NEVER invent additional examples to "show breadth"

**Fact-Pairing Rule:** A metric is only valid if BOTH the number AND the specific outcome it measures appear together in the same story. Do not re-attach a number from one context to a different outcome.

**Texture Rule:** Preserve the story's distinctive details — quote unique phrases, name specific practices, include concrete anecdotes. Generic summaries are a failure mode.

**Personal Project Exception** (Client="Independent" or "Career Narrative"):
- **HARD RULE:** DO NOT mention job seekers, engineers, teams, or users "struggling"
- Only acceptable framing is Matt's OWN motivation
- ✅ "Matt recognized that traditional resumes failed to showcase..."
- ✅ "Matt wanted to demonstrate his RAG architecture skills..."
- ❌ NEVER: "Job seekers were struggling..." / "Engineers needed..."

**Post-processing:**
- Auto-bold all known client names (derived from story corpus)
- Auto-bold numbers/metrics: $50M, 30%, 4x, 150+ engineers, etc.
- Fix LLM's malformed bolding (e.g., **1**0%** → **10%**)
- Remove banned phrases that LLM ignores (BANNED_PHRASES_CLEANUP list)

**Meta-Commentary Safety Net** (temporary — see BACKLOG.md #1):
- `META_SENTENCE_PATTERNS` regex catches LLM meta-commentary that violates NEVER rules
- Patterns: "This story demonstrates...", "This reflects Matt's...", "reveals his pattern of..."
- Logs violations with `_log_bandaid()` for tracking which rules fire
- **Known issue:** Prompt conflict between "Emphasize X" and "NEVER meta-commentary" causes this to fire frequently

**BANDAID Logging:**
```python
def _log_bandaid(bandaid_name: str, details: str):
    """Log when a post-processing safety net catches a violation.
    Used to track which band-aids fire so unused ones can be deleted."""
```
- Logged to DEBUG output when `DEBUG=True`
- Helps identify which post-processing rules are actually needed vs. cruft

### Data Flow Diagram

```
User Query
    ↓
[Layer 1: Validation]
    ├── is_nonsense() → reject if regex match
    └── semantic_router() → reject if score < 0.72 (also provides intent_family)
    ↓
[Layer 2: Classification]
    ├── intent_family from semantic router (primary)
    ├── detect_entity() → (field, value) or None
    └── classify_query_intent() fallback if needed
    ↓
[Layer 3: Retrieval]
    ├── Standard Mode: entity pin → diversify_results() (named clients first)
    ├── Narrative Mode: sort by Pinecone score (skip diversity)
    └── Synthesis Mode: get_synthesis_stories() → named-clients-first
    ↓
[Layer 4: Context Assembly]
    └── XML isolation: <primary_story> + <supporting_story> tags
    ↓
[Layer 5: Generation]
    └── GPT-4o → Agy-voiced markdown (fact-pairing + texture rules)
    ↓
User Response
```

### Cross-Page Navigation into Ask MattGPT

Multiple pages can navigate into Ask MattGPT with pre-filled context. This uses session state injection.

**Entry Points:**

| Source | Trigger | Session State Set |
|--------|---------|-------------------|
| Story Detail | "Ask Agy About This" button | `seed_prompt`, `active_story`, `active_story_obj`, `__ctx_locked__`, `__ask_from_suggestion__` |
| Hero CTA | Main call-to-action button | `active_tab` only |
| Category Cards | Card click | `active_tab` only |
| Footer | "Ask MattGPT" link | `active_tab` only |
| Banking Landing | Capability card click | `active_tab` only (prefilters go to Explore) |
| Cross-Industry Landing | Capability card click | `active_tab` only (prefilters go to Explore) |

**Context Injection Keys (for story-specific queries):**

```python
# Set by story_detail.py:handle_ask_about_this()
st.session_state["seed_prompt"] = "Tell me more about: {Title}"  # Pre-filled query
st.session_state["active_story"] = story_id                      # Story ID for context
st.session_state["active_story_obj"] = story_dict                # Full story object
st.session_state["__ctx_locked__"] = True                        # Lock context to this story
st.session_state["__ask_from_suggestion__"] = True               # Bypass off-domain filters
st.session_state["active_tab"] = "Ask MattGPT"                   # Navigate to Ask MattGPT
st.rerun()
```

**Consumption in Ask MattGPT:**

```python
# In conversation_view.py
seed = st.session_state.pop("seed_prompt", None)  # Pop to consume once
if seed:
    # Auto-submit the seed prompt
    process_query(seed)

# In utils.py:get_context_story()
if st.session_state.get("__ctx_locked__"):
    return st.session_state.get("active_story_obj")  # Use locked story
```

**Prefilter Pattern (for Explore Stories, NOT Ask MattGPT):**

```python
# Used by banking_landing.py, cross_industry_landing.py → Explore Stories
st.session_state["prefilter_industry"] = "Financial Services"
st.session_state["prefilter_capability"] = "Platform Engineering"
st.session_state["active_tab"] = "Explore Stories"

# Consumed in explore_stories.py BEFORE widgets render
if "prefilter_industry" in st.session_state:
    F["industry"] = st.session_state.pop("prefilter_industry")
```

**Key Rule:** Set prefilters BEFORE the target page renders, then `pop()` to consume them. Never modify widget-bound session state after the widget renders.

### UI Hydration Pattern (January 2026)

Landing pages now receive the full `stories` list and compute counts dynamically at render time. This ensures metrics never drift from the JSONL source of truth.

**Updated Function Signatures:**
```python
# app.py passes STORIES to all landing pages
render_home_page(STORIES)
render_banking_landing(STORIES)
render_cross_industry_landing(STORIES)

# Each landing page derives counts from stories
def render_banking_landing(stories: list[dict]):
    banking_stories = [s for s in stories if s.get("Industry") == "Financial Services / Banking"]
    total_projects = len(banking_stories)

    # Client counts with exclusions
    client_counter = Counter(s.get("Client", "Unknown") for s in banking_stories
                             if s.get("Client") not in _EXCLUDED_CLIENTS)
    named_clients = [(client, count) for client, count in client_counter.most_common()]
    num_clients = len(named_clients)

    # Capability areas
    capabilities = set(s.get("Solution / Offering", "") for s in banking_stories
                       if s.get("Solution / Offering"))
    num_capabilities = len(capabilities)
```

**Hydrated Pages:**
| File | Hydrated Metrics |
|------|------------------|
| `banking_landing.py` | Project count, client pills with counts, capability areas |
| `cross_industry_landing.py` | Project count, industry pills, capability areas |
| `category_cards.py` | Banking/Cross-industry project counts, top 3 client pills |
| `home.py` | Passes STORIES to category_cards |

**Excluded Clients:** "Career Narrative", "Independent", "Multiple Clients" (excluded from counts and pills)

**Why:** Previously had hardcoded counts like "12 projects" that drifted as JSONL changed. Now counts are always accurate.

### Explore Stories Search Architecture

Explore Stories (`ui/pages/explore_stories.py`) has a **3-path search architecture** to minimize Pinecone API calls:

```
User Interaction
       ↓
┌──────────────────────────────────────────────────────────────┐
│ PATH 1: New Keyword Query (Expensive - Pinecone Call)        │
│ Trigger: User submits search query (different from cached)   │
│ Action: semantic_search() → Pinecone → cache results         │
│ Cost: ~$0.0001 (one embedding + Pinecone query)              │
└──────────────────────────────────────────────────────────────┘
       ↓ results cached
┌──────────────────────────────────────────────────────────────┐
│ PATH 2: Filter Change (Cheap - No Pinecone Call)             │
│ Trigger: User changes filter while query unchanged           │
│ Action: Reuse cached Pinecone results + local filter         │
│ Cost: Zero (no API calls)                                    │
└──────────────────────────────────────────────────────────────┘
       ↓ if no query
┌──────────────────────────────────────────────────────────────┐
│ PATH 3: No Query (Free - Local Filter Only)                  │
│ Trigger: Empty search box, filter-only browsing              │
│ Action: matches_filters() on full story corpus               │
│ Cost: Zero (no API calls)                                    │
└──────────────────────────────────────────────────────────────┘
```

**Code Location:** `explore_stories.py:1805-1900`

**Cache Keys:**
```python
LAST_RESULTS = "__explore_last_results__"     # Cached Pinecone results
LAST_CONFIDENCE = "__explore_last_confidence__" # "high" | "low" | "none"
LAST_QUERY = "__explore_last_query__"         # Query that produced cache
```

**Filter Application:**
- **PATH 1:** Pinecone handles semantic matching; UI filters applied post-search
- **PATH 2:** Apply filters EXCEPT `q` (keyword) — Pinecone already did semantic match
- **PATH 3:** Full local filtering via `matches_filters(s, F)`

**Key Optimization:** When user changes filters (Industry, Capability, etc.) without changing the search query, the system reuses cached Pinecone results instead of re-querying. This prevents expensive API calls on every filter toggle.

**matches_filters() Logic** (`utils/filters.py`):
- Industry → exact match on `s["Industry"]`
- Capability → exact match on `s["Solution / Offering"]`
- Era → exact match on `s["Era"]`
- Clients, Domains, Roles → IN list (OR logic)
- Tags → case-insensitive intersection
- has_metric → `story_has_metric(s)`
- q (keyword) → token-based ALL match on Title, Client, Purpose, Process, Performance, tags

### Known Limitations

1. **Synthesis + specific topic:** "Tell me about Matt's rapid prototyping work" classified as synthesis but should find the specific rapid prototyping story. Current workaround: synthesis now uses user query embedding.
2. ~~**Multi-client stories:** Stories with `Client="Multiple Clients"` won't match entity filters.~~ **FIXED (Jan 2026):** Multi-Field Entity Gate now searches across 5 fields (client, employer, division, project, place) using Pinecone `$or` operator.
3. **Ground truth fidelity:** LLM paraphrases instead of quoting verbatim despite `[[CORE BRAND DNA]]` markers.
4. **Deprecated documentation:** `mattgpt_system_prompt.md` documents the original "MattGPT" persona (pre-Agy). The current Agy voice is documented in this file under Component Contracts → Agy Voice Generator.
5. **LLM stochasticity:** Eval may show occasional failures due to LLM response variability. Re-running typically passes. Semantic similarity scoring would address this (see BACKLOG.md MATTGPT-004).

---

### Session State Keys Reference

Central reference for all session state keys used across the application.

**Ask MattGPT Keys:**
| Key | Type | Purpose | Set By | Used By |
|-----|------|---------|--------|---------|
| `ask_transcript` | `list[dict]` | Chat history `[{role, text}, ...]` | conversation_view.py | All ask_mattgpt modules |
| `ask_input_value` | `str` | Current input field value | landing_view.py, conversation_view.py | Input widget |
| `seed_prompt` | `str` | Pre-filled query from navigation | story_detail.py | conversation_view.py (pop) |
| `pending_query` | `str` | Query being processed | landing_view.py | Backend processing |
| `processing_suggestion` | `bool` | Processing indicator flag | landing_view.py | UI disable state |
| `last_answer` | `str` | Most recent Agy response | conversation_helpers.py | Display |
| `last_sources` | `list[dict]` | Retrieved stories for response | conversation_helpers.py | Related Projects |
| `last_results` | `list[dict]` | Raw Pinecone results | backend_service.py | Scoring |
| `answer_modes` | `dict` | Response modes (narrative, etc.) | conversation_helpers.py | Mode switching |
| `answer_mode` | `str` | Currently selected mode | conversation_helpers.py | Display |
| `show_ask_panel` | `bool` | Whether to show conversation view | shared_state.py | View routing |
| `show_how_modal` | `bool` | "How Agy Searches" modal open | landing_view.py | Modal |

**Context Keys (double-underscore prefix = internal):**
| Key | Type | Purpose |
|-----|------|---------|
| `__ctx_locked__` | `bool` | Lock context to specific story |
| `__ask_from_suggestion__` | `bool` | Query from suggestion (bypass filters) |
| `__ask_force_answer__` | `bool` | Force answer even on low confidence |
| `__ask_query_intent__` | `str` | Detected query intent |
| `__ask_confidence__` | `str` | Confidence level (high/low/none) |
| `__asked_once__` | `bool` | User has asked at least one question |
| `__inject_user_turn__` | `str` | Inject follow-up question |
| `__landing_processing__` | `bool` | Landing page processing state |
| `__processing_chip_injection__` | `bool` | Chip click processing |

**Story Selection Keys:**
| Key | Type | Purpose |
|-----|------|---------|
| `active_story` | `str` | Selected story ID |
| `active_story_obj` | `dict` | Full story object |
| `active_story_title` | `str` | Selected story title |
| `active_story_client` | `str` | Selected story client |

**Explore Stories Keys:**
| Key | Type | Purpose |
|-----|------|---------|
| `filters` | `dict` | Active filter state |
| `__explore_last_results__` | `list` | Cached Pinecone results |
| `__explore_last_confidence__` | `str` | Cached confidence level |
| `__explore_last_query__` | `str` | Query that produced cache |
| `page_offset` | `int` | Pagination offset |

**Prefilter Keys (cross-page navigation):**
| Key | Purpose | Consumed By |
|-----|---------|-------------|
| `prefilter_industry` | Pre-set Industry filter | explore_stories.py |
| `prefilter_capability` | Pre-set Capability filter | explore_stories.py |
| `prefilter_era` | Pre-set Era filter | explore_stories.py |
| `prefilter_view_mode` | Pre-set view mode (table/cards/timeline) | explore_stories.py |
| `prefilter_domains` | Pre-set domains filter | explore_stories.py |
| `prefilter_roles` | Pre-set roles filter | explore_stories.py |

**Navigation Keys:**
| Key | Type | Purpose |
|-----|------|---------|
| `active_tab` | `str` | Current page ("Home", "Explore Stories", "Ask MattGPT", "About Matt") |

---

### JSONL Story Schema

Stories are stored in `echo_star_stories_nlp.jsonl` (130+ entries). Each line is a JSON object.

**Core Fields:**
| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"platform-modernization\|jpmc"` | Unique ID (title\|client) |
| `Title` | `str` | `"Platform Modernization for Payments"` | Story title |
| `Client` | `str` | `"JPMorgan Chase"` | Client name |
| `Employer` | `str` | `"Accenture"` | Employer |
| `Division` | `str` | `"Technology"` | Division/business unit |
| `Role` | `str` | `"Platform Architect"` | Matt's role |
| `Project` | `str` | `"Payments Modernization"` | Project name |
| `Industry` | `str` | `"Financial Services"` | Industry vertical |
| `Theme` | `str` | `"Execution & Delivery"` | One of 7 themes |
| `Era` | `str` | `"Financial Services Platform Modernization"` | Career era |
| `Solution / Offering` | `str` | `"Platform Engineering"` | Capability/offering |
| `Sub-category` | `str` | `"Platform Engineering"` | Domain sub-category |

**STAR Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `Situation` | `list[str]` | Context and challenge |
| `Task` | `list[str]` | Objective or goal |
| `Action` | `list[str]` | Steps taken |
| `Result` | `list[str]` | Outcomes achieved |

**5P Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `Person` | `str` | Who Matt worked with |
| `Place` | `str` | Where work happened |
| `Purpose` | `str` | Why this work mattered |
| `Process` | `list[str]` | How it was done |
| `Performance` | `list[str]` | Results and metrics |
| `5PSummary` | `str` | Synthesized summary |

**Metadata Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `Start_Date` | `str` | Start date (YYYY-MM) |
| `End_Date` | `str` | End date (YYYY-MM) |
| `Competencies` | `list[str]` | Skills demonstrated |
| `Use Case(s)` | `list[str]` | Interview scenarios |
| `public_tags` | `str` | Comma-separated search tags |
| `content` | `str` | Empty (reserved for future) |

**Special Values:**
- `Client="Career Narrative"` → Professional narrative stories
- `Client="Independent"` → Personal projects (MattGPT)
- `Client="Multiple Clients"` → Cross-client patterns
- `Theme="Professional Narrative"` → Identity/philosophy stories
- `Era="Leadership & Professional Narrative"` → Excluded from Timeline view

---

### Utils Modules (`utils/`)

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **client_utils.py** | Client classification | `is_generic_client()` — pattern-based detection of placeholder clients |
| **validation.py** | Query validation, tokenization, nonsense detection | `is_nonsense()`, `_tokenize()`, `vocab_overlap_ratio()` |
| **filters.py** | Story filtering for Explore Stories | `matches_filters(story, filters)` |
| **formatting.py** | Story presentation, metric extraction | `story_has_metric()`, `strongest_metric_line()`, `build_5p_summary()`, `_format_narrative()` |
| **scoring.py** | Hybrid scoring (semantic + keyword) | `_keyword_score_for_story()`, `_hybrid_score()` |
| **ui_helpers.py** | Debug logging, UI utilities | `dbg()` |

**client_utils.py Key Function:**
```python
def is_generic_client(client: str) -> bool:
    """Pattern-based detection of generic/placeholder clients.
    Returns True for: empty strings, values ending with 'clients' or 'project'.
    Examples: 'Multiple Clients', 'Fortune 500 Clients', 'Independent Project'."""
```

**validation.py Key Functions:**
```python
def is_nonsense(query: str) -> tuple[bool, str | None]:
    """Check if query matches nonsense patterns from nonsense_filters.jsonl.
    Returns (is_nonsense, category) where category is e.g., 'profanity', 'meta', 'gibberish'."""

def _tokenize(text: str) -> list[str]:
    """Tokenize text into normalized words (3+ chars, lowercase)."""

def vocab_overlap_ratio(query: str, corpus_vocab: set[str]) -> float:
    """Calculate what % of query tokens appear in corpus vocabulary."""
```

**filters.py Key Function:**
```python
def matches_filters(s: dict, F: dict | None = None) -> bool:
    """Check if story matches all active filters. F reads from st.session_state['filters'] if None.
    Supports: industry, capability, era, clients, domains, roles, tags, has_metric, q (keyword)."""
```

**scoring.py Weights:**
```python
W_PC = 1.0  # Semantic (Pinecone) weight
W_KW = 0.0  # Keyword weight (disabled by default)
```

---

### story_intelligence.py

Theme inference and voice guidance for RAG.

**7 Themes (constants):**
```python
THEME_EXECUTION = "Execution & Delivery"      # PRIMARY - He ships
THEME_STRATEGIC = "Strategic & Advisory"       # He advises
THEME_ORG_TRANSFORM = "Org & Working-Model Transformation"  # He transforms
THEME_TALENT = "Talent & Enablement"          # He builds people
THEME_RISK = "Risk & Responsible Tech"        # He manages risk
THEME_EMERGING = "Emerging Tech"              # He explores pragmatically
THEME_PROFESSIONAL = "Professional Narrative" # He knows who he is
```

**THEME_TO_PATTERN** (prevents voice drift in synthesis):
```python
THEME_TO_PATTERN = {
    THEME_EXECUTION: "He ships.",
    THEME_STRATEGIC: "He advises.",
    THEME_ORG_TRANSFORM: "He transforms how teams work.",
    THEME_TALENT: "He builds people.",
    THEME_RISK: "He manages risk.",
    THEME_EMERGING: "He explores pragmatically.",
    THEME_PROFESSIONAL: "He knows who he is.",
}
```

**Key Functions:**
```python
def infer_story_theme(story: dict) -> str:
    """Get theme from story's Theme field (defaults to THEME_EXECUTION)."""

def get_theme_guidance(theme: str) -> str:
    """Get Agy voice guidance for theme (emphasize, voice pattern, position, proof points)."""

def build_story_context_for_rag(story: dict) -> str:
    """Build WHY→HOW→WHAT context string for RAG prompt injection."""

def get_theme_emoji(theme: str) -> str:
    """Get emoji for theme (🏗️ 🧠 🔄 👥 🛡️ 🚀 🧭)."""
```

---

### Config Modules (`config/`)

| Module | Purpose | Contents |
|--------|---------|----------|
| **debug.py** | Global debug flag | `DEBUG = False` |
| **settings.py** | Configuration management | `get_conf(key, default)` |

**settings.py Pattern:**
```python
def get_conf(key: str, default: str | None = None):
    """Get config from st.secrets (Streamlit Cloud) or .env fallback."""
    try:
        v = st.secrets.get(key)
        if v is not None:
            return v
    except Exception:
        pass
    return os.getenv(key, default)
```

**Required Environment Variables:**
| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API for embeddings + LLM |
| `PINECONE_API_KEY` | Pinecone vector database |
| `PINECONE_INDEX` | Pinecone index name |

---

### CSS Variables (Full List)

Defined in `ui/styles/global_styles.py`. Use these instead of hardcoding colors.

**Light Mode (`:root`):**
```css
/* Brand */
--accent-purple: #8B5CF6;
--accent-purple-hover: #7C3AED;
--accent-purple-bg: rgba(139, 92, 246, 0.08);
--accent-purple-light: rgba(139, 92, 246, 0.2);
--accent-purple-text: #8B5CF6;

/* Backgrounds */
--bg-card: #FFFFFF;
--bg-surface: #F9FAFB;
--bg-primary: #FFFFFF;
--bg-hover: #F3F4F6;
--bg-input: #FFFFFF;

/* Text */
--text-heading: #111827;
--text-primary: #1F2937;
--text-secondary: #6B7280;
--text-muted: #9CA3AF;
--text-color: #1F2937;

/* Borders & Shadows */
--border-color: #E5E7EB;
--border-light: #F3F4F6;
--card-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
--hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

/* Components */
--pill-bg: #F3F4F6;
--pill-text: #4B5563;
--success-color: #10B981;
--banner-info-bg: rgba(139, 92, 246, 0.05);

/* Tables */
--table-header-bg: #F9FAFB;
--table-row-bg: #FFFFFF;
--table-row-hover-bg: #F9FAFB;

/* Chat/Status */
--status-bar-bg: #F9FAFB;
--status-bar-border: #E5E7EB;
--chat-ai-bg: #F9FAFB;
--chat-ai-border: #8B5CF6;
--chat-user-bg: #FBFBFC;

/* Gradients */
--gradient-purple-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Legacy (navbar, hero) */
--purple-gradient-start: #667eea;
--dark-navy: #2c3e50;
--dark-navy-hover: #34495e;
```

**Dark Mode (`body.dark-theme`):**
```css
--bg-card: #1E1E2E;
--bg-surface: #262633;
--bg-primary: #0E1117;
--bg-hover: #2D2D3D;
--text-heading: #F9FAFB;
--text-primary: #E5E7EB;
--text-secondary: #9CA3AF;
--border-color: #374151;
--accent-purple-text: #A78BFA;  /* Lighter for dark backgrounds */
```

---

### Eval Framework (`tests/`)

| File | Purpose |
|------|---------|
| `eval_rag_quality.py` | RAG quality evaluation against ground truth |
| `test_agy_behavior.py` | Agy response behavior tests |

**Current Status (January 22, 2026):** 100% pass rate (31/31 queries)

**eval_rag_quality.py:**
- Runs 31 test queries across 5 categories: narrative, client, intent, edge, synthesis
- Checks: voice consistency, ground truth matches, client attribution, client bolding
- Outputs JSON results to `tests/eval_results/`

**Test Categories:**
| Category | Count | Checks |
|----------|-------|--------|
| `narrative` | 10 | Voice + ground_truth phrases |
| `client` | 8 | Voice + client attribution + bolding |
| `synthesis` | 5 | Voice + synthesis mode detection + theme coverage |
| `intent` | 4 | Voice + intent classification |
| `edge` | 4 | Voice + client attribution |

**Eval History:**
| Date | Pass Rate | Changes |
|------|-----------|---------|
| Jan 21, 2026 | 71% (22/31) | Baseline after sovereign narrative sync |
| Jan 22, 2026 | 100% (31/31) | Multi-field entity gate + dynamic DNA |

**Running Eval:**
```bash
python tests/eval_rag_quality.py
# Outputs: tests/eval_results/eval_YYYYMMDD_HHMMSS.json
```

---

### Error Handling Patterns

**Layer 1 (Validation):**
- `is_nonsense()` → Returns rejection message with category
- `semantic_router()` → Returns `(False, score)` if below threshold; fails-open on errors

**Layer 2 (Classification):**
- `classify_query_intent()` → Falls back to `"general"` on LLM error
- `detect_entity()` → Returns `None` if no entity found

**Layer 3 (Retrieval):**
- `semantic_search()` → Returns empty results on Pinecone error
- `get_synthesis_stories()` → Returns empty list on error

**Layer 4 (Generation):**
- `_generate_agy_response()` → Raises `RateLimitError` on 429, returns fallback on other errors
- `rag_answer()` → Catches `RateLimitError`, returns empty sources with:
  ```
  "🐾 I need a quick breather — try again in about 15 seconds!"
  ```

**UI Error Handling:**
- `send_to_backend()` wraps all errors in try/except
- Failed responses show generic error message
- Network errors trigger retry prompt

**Logging:**
- `dbg()` function logs when `DEBUG=True`
- Error details captured in `st.session_state["__ask_dbg_*"]` keys

---

### Analytics (Paused)

Google Analytics integration was attempted but removed due to session state conflicts.

**History:**
| Date | Action | Outcome |
|------|--------|---------|
| Jan 10, 2026 | Added `streamlit-analytics2` | Working initially (3 pageviews logged) |
| Jan 12, 2026 | Production failure | `AttributeError: st.session_state has no attribute "session_data"` |
| Jan 12, 2026 | Removed analytics | Quick fix to restore production stability |

**Root Cause:**
The `streamlit-analytics2` wrapper (`with streamlit_analytics.track():`) executed before Streamlit initialized session state. The wrapper runs at import time, but `app.py` session state setup (lines 46-54) hadn't completed yet.

**Planned Tracking Events:**
| Event | Trigger | Data |
|-------|---------|------|
| `page_view` | Tab navigation | `page_name` |
| `search` | Explore Stories query | `query`, `result_count` |
| `ask_query` | Ask MattGPT query | `query_intent`, `confidence` |
| `story_view` | Story detail opened | `story_id`, `source_page` |
| `related_project_click` | Related Projects card clicked | `story_id` |

**Implementation Status:**
- [ ] GA4 measurement ID configured
- [ ] gtag.js injected in app.py
- [ ] Event tracking functions created
- [ ] Events wired to UI actions

**Next Attempt - Critical Fix:**
Place the analytics wrapper **AFTER** all session state initialization:
```python
# app.py - CORRECT placement
import streamlit_analytics2 as streamlit_analytics

# ... all session state setup (lines 46-54) ...
# ... render_navbar(), setdefault("active_tab"), etc. ...

# THEN wrap page rendering:
with streamlit_analytics.track():
    if st.session_state["active_tab"] == "Home":
        render_home_page()
    # ... rest of page routing ...
```

**Fallback:** Manual `gtag.js` injection via `st.components.html()` if `streamlit-analytics2` continues to conflict.

**Environment Variable (when implemented):**
```
GA_MEASUREMENT_ID=G-XXXXXXXXXX
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
    4. Apply optional metadata filters (including multi-field entity gate)
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
# Standard filters
filters = {
    "industry": "Financial Services",
    "domain": "Platform Engineering"
}

# Entity filter (January 2026) - uses $or across 5 fields
filters = {
    "entity_field": "client",
    "entity_value": "Accenture"
}
# Translates to: {"$or": [{client: "Accenture"}, {employer: "accenture"}, ...]}
```

**Multi-Field Entity Gate:** When `entity_field` and `entity_value` are provided, the service builds a Pinecone `$or` clause that searches across `client`, `employer`, `division`, `project`, and `place` fields simultaneously. See Component Contracts → Multi-Field Entity Gate for details.

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
STORIES_JSONL=echo_star_stories_nlp.jsonl
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

## Data Governance & Master Source

### Principle

The **Excel master file** (`MPugmire - STAR Stories - [DATE].xlsx`) owned by the user is the canonical source for all portfolio data. The JSONL file is a derived artifact. No component should hardcode values that exist in the data.

### Hybrid Sovereignty Model

MattGPT uses a **Hybrid Sovereignty** approach that balances two complementary strategies:

| Strategy | Purpose | Examples |
|----------|---------|----------|
| **Dynamic RAG Grounding** | Accuracy — metrics, counts, and facts derived from data | Client names in MATT_DNA, project counts on landing pages, entity filters |
| **Curated UI** | Narrative control — intentional framing of user experience | Suggested questions on landing page, About Matt timeline, capability card copy |

**Why Hybrid?**
- **Pure dynamic** risks losing narrative voice (e.g., auto-generated questions might not showcase strengths)
- **Pure curated** risks data drift (e.g., hardcoded "12 projects" becomes wrong when JSONL grows)
- **Hybrid** gets accuracy where it matters (facts) + control where it matters (story)

**Decision Framework:**
| Content Type | Approach | Rationale |
|--------------|----------|-----------|
| Counts, metrics, client names | **Dynamic** | Must match reality |
| Suggested questions, CTAs | **Curated** | Showcase specific capabilities |
| Capability/industry pills | **Dynamic** | Derived from actual story distribution |
| About page timeline | **Curated** | Resume narrative, not raw data |
| RAG grounding prompt | **Dynamic** | Client names from JSONL prevent hallucination |

### January 2026 Sovereignty Patterns

Three patterns implement the Dynamic RAG Grounding half of Hybrid Sovereignty:

#### 1. Dynamic Identity (MATT_DNA)

The `MATT_DNA` grounding prompt—injected into every LLM call—is now rendered at runtime from JSONL data rather than hardcoded.

| Element | Source | Example |
|---------|--------|---------|
| Banking clients | Stories where `Industry = "Financial Services / Banking"` | JP Morgan Chase, Capital One, Fiserv |
| Telecom clients | Stories where `Industry = "Telecommunications"` | AT&T |
| Transport clients | Stories where `Industry = "Transportation & Logistics"` | Norfolk Southern |

**Implementation:** `backend_service.py:generate_dynamic_dna()` (lines 160-273)

**Why:** Previously hardcoded "JPMorgan" drifted from JSONL canonical name "JP Morgan Chase". Dynamic derivation ensures the LLM never hallucinates client names that don't exist in the data.

#### 2. Multi-Field Entity Gate

When a user asks about an entity (e.g., "Accenture work"), the system now searches across **five metadata fields** using Pinecone's `$or` operator—not just the `client` field.

| Field | Casing | Example Match |
|-------|--------|---------------|
| `client` | PascalCase | `"Accenture"` |
| `employer` | lowercase | `"accenture"` |
| `division` | lowercase | `"cloud innovation center"` |
| `project` | lowercase | `"accenture"` |
| `place` | lowercase | `"accenture"` |

**Implementation:** `pinecone_service.py:189-216`

**Why:** Closed the "entity blind spot" where stories with `Client="Confidential Healthcare Provider"` but `Employer="Accenture"` weren't found for Accenture queries. The CIC stories were particularly affected since many had `Division="Cloud Innovation Center"` but generic client names.

#### 3. UI Hydration

Landing pages now receive the full `stories` list and compute counts dynamically at render time—no hardcoded metrics.

| Page | Hydrated Values |
|------|-----------------|
| `banking_landing.py` | Project count, client pills with counts, capability count |
| `cross_industry_landing.py` | Project count, industry pills, capability count |
| `category_cards.py` | Banking/Cross-industry counts, top 3 client pills |

**Implementation:** All landing pages accept `stories: list[dict]` parameter; `app.py` passes `STORIES` to each.

**Why:** Previously had hardcoded "12 projects" that drifted as JSONL grew. Removed phantom industries ("Manufacturing", "Retail & Consumer Goods") that were wireframe leftovers with zero stories.

**See also:**
- [MATT_DNA Ground Truth](#matt_dna-ground-truth-dynamically-generated-from-jsonl--january-2026) — Full prompt template
- [Multi-Field Entity Gate](#multi-field-entity-gate-january-2026) — Component contract details
- [UI Hydration Pattern](#ui-hydration-pattern-january-2026) — Code examples

### Master Data Source

| Artifact | Role | Owner |
|----------|------|-------|
| Excel master file | **Source of truth** — all story content, metadata, tags | User (Matt) |
| `echo_star_stories_nlp.jsonl` | Derived artifact — ingested from Excel | Generated |
| Pinecone index | Derived artifact — embeddings from JSONL | Generated |
| UI counts, pills, prompts | Derived at runtime — from JSONL | Dynamic |

### Ingestion Workflow

Data flows one direction: **Excel → JSONL → Pinecone → App**

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USER updates Excel master file                              │
│     - Add/edit stories, metadata, tags                          │
│     - Schema changes (new columns, renamed fields)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. Copy Excel to environment                                   │
│     - Place in project root                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. Run ingestion pipeline                                      │
│     python generate_jsonl_from_excel.py                         │
│     python generate_public_tags.py      # Optional enrichment   │
│     python build_custom_embeddings.py   # Upsert to Pinecone    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. echo_star_stories_nlp.jsonl is regenerated                  │
│     - Previous JSONL is backed up (.bak)                        │
│     - All downstream consumers see updated data                 │
└─────────────────────────────────────────────────────────────────┘
```

### What Derives from JSONL (at Runtime)

| Component | Derived Values |
|-----------|----------------|
| `MATT_DNA` prompt | Client names grouped by industry |
| `banking_landing.py` | Project count, client pills with counts, capability areas |
| `cross_industry_landing.py` | Project count, industry pills, capability areas |
| `category_cards.py` | Banking/Cross-industry project counts, top 3 client pills |
| Pinecone metadata | All searchable fields (client, industry, theme, etc.) |
| Entity normalization | Alias map derived from unique Client/Employer values |

### Curated Content (Intentionally Static)

Some UI content is intentionally curated and NOT derived from data:

| File | Content | Reason |
|------|---------|--------|
| `landing_view.py` | Suggested questions | Curated UX showcase, tied to eval queries |
| `about_matt.py` | Timeline, company names | Curated CV/resume presentation |

### Anti-Patterns (Don't Do This)

- ❌ Hardcoding "12 projects" when JSONL count changes
- ❌ Listing "JPMorgan" when JSONL says "JP Morgan Chase"
- ❌ Adding phantom industries/capabilities not in the data
- ❌ Manual JSONL edits that will be overwritten on next ingestion

### ⚠️ WARNING: No Manual JSONL Surgery

**Do not perform manual metadata surgery on the JSONL file.**

Schema or tagging changes (like adding "AI/ML" tags to existing rows, renaming fields, or fixing typos) **must be implemented in the Excel master** to prevent data drift during the next ingestion cycle.

**Why this matters:**
1. The next `generate_jsonl_from_excel.py` run will overwrite manual changes
2. JSONL and Excel will diverge, causing confusion
3. Pinecone embeddings may not match JSONL metadata
4. Debugging becomes impossible ("why does prod differ from my Excel?")

**Correct workflow for metadata changes:**
```bash
# 1. Edit Excel master (add AI/ML tag to stories)
# 2. Re-run ingestion
python generate_jsonl_from_excel.py
python build_custom_embeddings.py

# 3. Verify changes
grep "AI/ML" echo_star_stories_nlp.jsonl | wc -l
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
4. ~~Begin mobile responsiveness Phase 1~~ ✅ Done
5. **NEW:** Landing Page Capability Surfacing Redesign (MATTGPT-012) - UX design task for visual capability browsing

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

## RAG Pipeline Audit (January 2026)

Comprehensive audit of the RAG (Retrieval-Augmented Generation) pipeline covering data flow, embedding analysis, ranking operations, test coverage, and architecture issues.

### Data Flow Map

**Query → Response Trace:**

```
User Query
    ↓
┌─────────────────────────────────────────────────┐
│ Gate 1: Rules-Based Rejection (Free)            │
│ - nonsense_filters.jsonl patterns               │
│ - is_nonsense() regex validation                │
└─────────────────────────────────────────────────┘
    ↓ (passed)
┌─────────────────────────────────────────────────┐
│ Gate 2: Semantic Router (Cheap)                 │
│ - Embed query with text-embedding-3-small       │
│ - Compare against 11 intent-family centroids    │
│ - HARD_ACCEPT=0.80, SOFT_ACCEPT=0.72            │
└─────────────────────────────────────────────────┘
    ↓ (accepted)
┌─────────────────────────────────────────────────┐
│ Gate 3: Entity Gate                             │
│ - detect_entity() substring matching            │
│ - Multi-field normalization (client aliases)    │
│ - Returns (field, value) or None                │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Intent Classification                           │
│ - Semantic router intent_family (primary)       │
│ - LLM classifier fallback (rare)                │
│ - Priority: entity > narrative > synthesis      │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Pinecone Vector Search                          │
│ - Query embedding → vector search               │
│ - Entity filter (Pinecone $or across 5 fields)  │
│ - UI filters (industry, domain, role)           │
│ - Returns top 100 candidates                    │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Post-Retrieval Processing (Mode-Dependent)      │
│ STANDARD: entity_pin → diversify_results() → 7 │
│ NARRATIVE: sort by score (skip diversity) → 7   │
│ SYNTHESIS: theme-filter → named-clients-first   │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Context Assembly                                │
│ - XML isolation: <primary_story> tags           │
│ - MATT_DNA ground truth injection               │
│ - Mode-specific prompt selection                │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ LLM Generation (OpenAI GPT-4o)                  │
│ - Temperature: 0.4 (standard) / 0.2 (synthesis) │
│ - Max tokens: 700                               │
│ - Fact-pairing + texture rules                  │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Response Formatting                             │
│ - Extract answer + sources                      │
│ - Meta-commentary cleanup                       │
│ - Banned phrase removal                         │
└─────────────────────────────────────────────────┘
    ↓
User Response
```

### Embedding Analysis

**Embedding Model:** OpenAI `text-embedding-3-small` (1536 dimensions)

**Vectors Stored in Pinecone:**

| Vector Type | Source | Dimensions | Purpose |
|-------------|--------|------------|---------|
| Story embeddings | `build_custom_embeddings.py` | 1536 | Retrieved from Pinecone for story matching |
| Query embeddings | `pinecone_service.py` | 1536 | Generated at runtime for semantic search |
| Intent centroids | `semantic_router.py` | 1536 | 11 pre-computed intent family embeddings |

**Embedding Fields Used (from JSONL):**

Stories are embedded using a concatenated text block:
```python
text = f"{title}. {why}. {' '.join(how or [])}. {' '.join(what or [])}"
```

**Fields NOT embedded** (metadata only):
- Client, Employer, Division (used for filtering)
- Theme, Sub-category (used for filtering)
- Role, Era, Industry (used for filtering)
- STAR structure (situation/task/action/result)

### Ranking Pipeline Order of Operations

**1. Pinecone Search (services/pinecone_service.py)**
```
query_vector → Pinecone.query(top_k=100, filter=entity_filters)
↓
Returns: [(story_id, score, metadata), ...] sorted by cosine similarity
```

**2. Entity Pinning (backend_service.py)**
```
If entity detected AND matching story found:
  Move matching story to position 0
  Rest maintain Pinecone order
```

**3. Diversity Reordering (backend_service.py:diversify_results)**
```
Standard/Behavioral modes only:
  - Group by client
  - Interleave to avoid consecutive same-client stories
  - Skip for narrative mode (trust Pinecone semantic ranking)
```

**4. Final Selection**
```
Standard: top 7 after diversity
Narrative: top 7 by Pinecone score (no reorder)
Synthesis: up to 9 (3 per theme × 3 themes)
```

**Scoring Formula:**
- Primary: Pinecone cosine similarity (0.0 - 1.0)
- No secondary scoring layer
- Confidence thresholds: HIGH=0.25, LOW=0.15 (UI display only)

### Test Coverage Analysis

**Eval Framework:** `tests/test_benchmark_rag.py`

| Test Category | Count | Coverage |
|---------------|-------|----------|
| Entity queries | 8 | Client, Employer, Division detection |
| Synthesis queries | 5 | Cross-cutting theme questions |
| Narrative queries | 6 | Identity/philosophy questions |
| Behavioral queries | 4 | STAR-style interview questions |
| Boundary cases | 8 | Edge cases, negation, ambiguity |
| **Total** | 31 | 100% pass rate (as of Jan 24, 2026) |

**Test File Structure:**
- `tests/test_benchmark_rag.py` - Main eval suite
- `data/borderline_queries.csv` - Edge case query log
- `tests/test_boost_narrative.py` - Narrative boost tests

**Gaps Identified:**
- No rate limit handling tests
- No concurrent request tests
- Limited negative test cases ("don't tell me about X")
- No tests for "Tell me more about: [Title]" pattern

### Architecture Issues

**1. Coupling Between Layers**

| Issue | Location | Impact |
|-------|----------|--------|
| `backend_service.py` imports from 6+ modules | backend_service.py:1-40 | Hard to test in isolation |
| Entity detection duplicated | backend_service.py, pinecone_service.py | Inconsistent normalization |
| Mode logic scattered | backend_service.py, rag_service.py | Unclear ownership |

**2. Fragile Patterns**

| Pattern | Risk | Recommendation |
|---------|------|----------------|
| Substring entity matching | False positives ("CIC" in "SPECIFIC") | Use word boundaries |
| Hardcoded client lists | Stale data, maintenance burden | Derive from JSONL |
| Regex-based meta-commentary cleanup | Brittle, catches false positives | Improve prompt instead |

**3. Unclear Boundaries**

| Question | Current State |
|----------|---------------|
| Who owns ranking? | Split: Pinecone → backend_service → rag_service |
| Who owns intent classification? | Split: semantic_router → backend_service |
| Who owns response formatting? | Split: backend_service → formatting.py → conversation_helpers.py |

**4. Hybrid Scoring Confusion**

The system has two scoring systems that don't align:
- **Pinecone scores**: 0.0-1.0 cosine similarity
- **Confidence thresholds**: 0.15-0.25 (arbitrary UI buckets)

No clear mapping between "Pinecone score 0.82" and "high confidence display."

**5. Error Handling**

| Error Type | Handling | Issues |
|------------|----------|--------|
| Rate limit (429) | `RateLimitError` exception | ✅ Fixed Jan 25, 2026 |
| Pinecone timeout | Silent fallback | No user notification |
| Embedding failure | Fail-open (accept query) | May pass garbage |
| LLM failure | Static fallback message | Loses context |

### Hardcoded Values Audit

**1. Client Names (7+ locations)**

```python
# backend_service.py
GENERIC_CLIENTS = ["Multiple Clients", "Independent", "Career Narrative"]

# formatting.py
if client.lower() in ["multiple clients", "independent"]: ...

# rag_service.py
NAMED_CLIENT_PREFERENCE = ["JP Morgan", "RBC", "JPMC", ...]
```

**Recommendation:** Centralize in `config/constants.py` or derive from JSONL.

**2. Threshold Constants**

| Constant | Value | Location |
|----------|-------|----------|
| HARD_ACCEPT | 0.80 | semantic_router.py |
| SOFT_ACCEPT | 0.72 | semantic_router.py |
| ENTITY_GATE_THRESHOLD | 0.50 | backend_service.py |
| CONFIDENCE_HIGH | 0.25 | backend_service.py |
| CONFIDENCE_LOW | 0.15 | backend_service.py |
| SEARCH_TOP_K | 100 | pinecone_service.py |
| SEARCH_TOP_K | 7 | backend_service.py (conflict!) |

**3. Model Names**

```python
# 4 different locations:
model="text-embedding-3-small"  # pinecone_service.py
model="text-embedding-3-small"  # semantic_router.py
model="text-embedding-3-small"  # build_custom_embeddings.py
model="gpt-4o"                  # backend_service.py
model="gpt-4o-mini"             # backend_service.py (classifier)
```

**4. Entity Normalization Map**

```python
ENTITY_NORMALIZATION = {
    "jpmorgan": "JP Morgan Chase",
    "jp morgan": "JP Morgan Chase",
    "jpm": "JP Morgan Chase",
    "cic": "Cloud Innovation Center",
    ...
}
```

**Location:** backend_service.py:315-323
**Issue:** Not synchronized with JSONL field values.

**5. Intent Family Keywords**

Hardcoded in semantic_router.py - 11 intent families with ~20 example phrases each.
These should be reviewed quarterly for relevance.

**6. Banned Phrases**

```python
BANNED_PHRASES = [
    "meaningful outcomes",
    "foster collaboration",
    "strategic mindset",
    ...
]
```

**Location:** backend_service.py
**Purpose:** Post-processing cleanup of corporate filler.

**7. Sacred Vocabulary (Verbatim Phrases)**

```python
VERBATIM_PHRASES = ["builder", "modernizer", "complexity to clarity", ...]
```

**Location:** backend_service.py
**Purpose:** Force LLM to use exact phrases for Professional Narrative.

**8. UI Display Strings**

```python
"🐾 I need a quick breather — try again in about 15 seconds!"
"Found {n} relevant stories"
"No strong matches found"
```

**Scattered across:** backend_service.py, conversation_helpers.py

**9. Temperature Settings**

```python
temperature=0.4  # standard mode
temperature=0.2  # synthesis mode
```

**Location:** backend_service.py
**Issue:** Not configurable, no A/B testing capability.

**10. Token Limits**

```python
max_tokens=700  # generation
max_tokens=150  # classifier
```

**11. Pinecone Index Name**

```python
index_name="portfolio-stories"  # pinecone_service.py
```

**Should be:** Environment variable.

### Summary Findings

**Strengths:**
- Multi-layer gating prevents garbage queries efficiently
- Entity detection adds precision to broad queries
- Mode-specific retrieval (standard/narrative/synthesis) improves relevance
- 100% eval pass rate demonstrates quality baseline
- XML context isolation prevents cross-story bleed
- Dynamic MATT_DNA derived from single source of truth

**Weaknesses:**
- Hardcoded values scattered across 6+ files
- Unclear ownership boundaries between layers
- No centralized configuration
- Limited error handling coverage
- Test suite focused on happy path
- Duplicate logic (client exclusions, entity normalization)
- Hybrid scoring systems don't align

**Recommended Actions:**
1. **Centralize constants** in `config/constants.py`
2. **Derive client lists** from JSONL metadata at startup
3. **Add error handling tests** for rate limits, timeouts
4. **Clarify layer boundaries** with explicit contracts
5. **Remove duplicate code** (client exclusions, entity maps)
6. **Add negative test cases** to eval suite

---

