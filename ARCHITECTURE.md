# Architecture Documentation

## Table of Contents

### 📋 Overview
- [Executive Summary](#executive-summary)
- [System Overview](#system-overview)
  - [Current Architecture](#current-architecture)

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

---

## Executive Summary

**Project:** MattGPT Portfolio Assistant - AI-powered career story search and chat interface
**Tech Stack:** Streamlit, OpenAI GPT-4o-mini, Pinecone vector DB, Python 3.11+
**Data Corpus:** 130+ STAR-formatted transformation project stories
**Last Updated:** January 20, 2026

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

### Current State (December 2025)

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

1. **System Overview:** Current file structure, components, services (as of Dec 2025)
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
│   │   └── thinking_indicator.py      # ✨ Loading/processing indicator (3 KB)
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
[Intent Classification - backend_service.py]
- classify_query_intent() → synthesis | behavioral | technical | client | background | general
- Uses gpt-4o-mini for cheap, self-maintaining classification
      ↓
[Retrieval Strategy - based on intent]
- STANDARD MODE: diversify_results() → top 3 stories with client variety
- SYNTHESIS MODE: Career Narrative stories + diverse project stories (up to 7)
      ↓
[Context Assembly - ui/pages/ask_mattgpt/backend_service.py]
- Select stories based on intent mode
- Build prompt with STAR narratives
- Include metadata (Client, Industry, Theme)
      ↓
[LLM Generation - OpenAI GPT-4o-mini]
- STANDARD: Single-story focus, human stakes → methodology → outcomes
- SYNTHESIS: Theme/pattern → evidence across projects → insight
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

**Intent Classification (Entity-First Priority):**
```python
def classify_query_intent(query: str) -> str:
    """
    Uses gpt-4o-mini (~$0.0001 per query) with PRIORITY HIERARCHY:
    1. ENTITY ANCHOR: Company/Project mentioned → client (overrides verbs)
    2. BIOGRAPHICAL ANCHOR: Narrative fragments → narrative
    3. SYNTHESIS: No entity + cross-cutting question → synthesis
    4. BEHAVIORAL: STAR-style questions → behavioral
    5. TECHNICAL: Technology without company → technical
    6. BACKGROUND: Career history → background
    7. OUT_OF_SCOPE: Industries Matt hasn't worked in → out_of_scope
    8. GENERAL: Everything else → general
    """
```

**Key Rule:** Entity detection OVERRIDES verb patterns.
- "How did Matt scale at Accenture?" → `client` (not synthesis)
- "What are Matt's core themes?" → `synthesis` (no entity)

**Retrieval Strategies:**

| Intent | Stories Retrieved | Retrieval Method |
|--------|-------------------|------------------|
| synthesis | 7-9 (up to 2 per theme) | Theme-filtered search with USER query embedding |
| narrative | 5 | Standard + narrative boost |
| client | 5 | Standard diversify_results() with entity filter |
| behavioral | 5 | Standard diversify_results() |
| technical | 5 | Standard diversify_results() |
| background | 5 | Standard diversify_results() |
| general | 5 | Standard diversify_results() |

**Synthesis Retrieval (get_synthesis_stories):**
1. Embed USER's actual query (not fixed theme keywords)
2. For each of 7 themes: Pinecone query with `filter={"Theme": theme}` + user embedding
3. If entity detected: Add entity filter (e.g., `{"Division": "Cloud Innovation Center"}`)
4. Up to 2 stories per theme, skip themes with no entity-scoped results
5. Sort by score, return top 7-9 stories

**Entity Detection (Multi-Field):**
Checks fields in order: Client, Employer, Division, Project, Place
- "CIC" normalizes to Division: "Cloud Innovation Center"
- "JPMorgan" normalizes to Client: "JP Morgan Chase"
- Excludes generic values: "Multiple Clients", "Independent"

**Synthesis Prompt Mode:**
- Different system prompt focused on patterns/themes
- Asks for breadth across stories, not depth on one
- Structure: Theme → Evidence from 2-4 clients → Insight
- Longer responses (250-350 words vs 200-300)

**Cost:**
- Intent classification: ~$0.0001 per query (gpt-4o-mini, 10 tokens output)
- Total query cost increase: negligible

**Self-Maintenance:**
- LLM-based classification handles novel phrasings without keyword list updates
- New story themes automatically included via Career Narrative content

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

### Layer 2: Intent Classification (Cheap LLM)

#### Intent Classifier
- **Job:** Route queries to synthesis/client/narrative/behavioral/technical/background/out_of_scope/general
- **Lives in:** `ui/pages/ask_mattgpt/backend_service.py:classify_query_intent()`
- **Model:** gpt-4o-mini (~$0.0001 per query)
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
  2. Pinecone vector search (top 100)
  3. Confidence gating
  4. `boost_narrative_matches()` for biographical queries
  5. `diversify_results()` → top 5 stories with client variety
- **Lives in:** `services/rag_service.py` + `backend_service.py:rag_answer()`
- **Story limit:** 5 stories to LLM context

#### Synthesis Mode
- **Job:** Answer "what are Matt's themes/patterns/philosophy" questions
- **Triggers:** Intent = `synthesis` (no entity + cross-cutting question)
- **Retrieval:**
  1. User query → OpenAI embedding (NOT fixed theme keywords)
  2. For each of 7 themes: Pinecone query with `filter={"Theme": theme}` + user embedding
  3. If entity detected: Add entity filter (e.g., `{"Theme": theme, "Client": "Accenture"}`)
  4. Up to 2 stories per theme
  5. Skip themes with no results for detected entity (don't fall back to other entities)
- **Lives in:** `backend_service.py:get_synthesis_stories()`
- **Story limit:** 7-9 stories to LLM context
- **MUST use:** User's actual query embedding for semantic relevance
- **MUST NOT:** Ignore user's query for fixed theme keywords (previous bug)

#### Narrative Boost
- **Job:** Force Professional Narrative stories to top for biographical queries
- **Lives in:** `services/rag_service.py:boost_narrative_matches()`
- **Triggers on fragments:** "leadership journey", "career intent", "philosophy", "early failure", "risk ownership", "work philosophy", "sustainable leadership", "career transition", "complex problems", "who is matt", "about matt"
- **Rule:** Matches story Title containing fragment + Theme="Professional Narrative"

### Layer 4: Response Generation

#### Agy Voice Generator
- **Job:** Transform retrieved stories into WHY→HOW→WHAT narrative with Agy personality
- **Lives in:** `backend_service.py:_generate_agy_response()`
- **Model:** gpt-4o-mini
- **Structure:**
  - **Standard mode:** Human stakes → How Matt tackled it → What changed → Pattern insight
  - **Synthesis mode:** Name patterns → Prove with client examples → Connect the thread
- **Guardrails:**
  - MATT_DNA ground truth injected
  - Banned corporate filler phrases
  - `[[CORE BRAND DNA]]` verbatim anchors for Professional Narrative
  - Personal project warning (no fictional stakeholders)
- **Post-processing:** Auto-bold client names and metrics

### Data Flow Diagram

```
User Query
    ↓
[Layer 1: Validation]
    ├── is_nonsense() → reject if regex match
    └── semantic_router() → reject if score < 0.72
    ↓
[Layer 2: Classification]
    ├── classify_query_intent() → synthesis | client | narrative | ...
    └── detect_entity() → (field, value) or None
    ↓
[Layer 3: Retrieval]
    ├── Standard Mode: semantic_search() → diversify_results()
    └── Synthesis Mode: get_synthesis_stories() with user embedding + theme filter
    ↓
[Layer 4: Generation]
    └── _generate_agy_response() → Agy-voiced markdown
    ↓
User Response
```

### Known Limitations

1. **Synthesis + specific topic:** "Tell me about Matt's rapid prototyping work" classified as synthesis but should find the specific rapid prototyping story. Current workaround: synthesis now uses user query embedding.
2. **Multi-client stories:** Stories with `Client="Multiple Clients"` won't match entity filters. Workaround: check Employer/Division fields.
3. **Ground truth fidelity:** LLM paraphrases instead of quoting verbatim despite `[[CORE BRAND DNA]]` markers.

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

