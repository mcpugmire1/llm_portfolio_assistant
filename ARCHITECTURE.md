# Architecture Documentation

> **Naming convention note (May 30-31, 2026 — MATTGPT-100 + MATTGPT-106 + MATTGPT-107):**
>
> Display labels were renamed via Strategy B (coordinated rename across UI labels + `session_state["active_tab"]` routing values):
>
> | Old display label | New display label | session_state value | Module/file name |
> |---|---|---|---|
> | Explore Stories | **My Work** | `"My Work"` | `ui/pages/explore_stories.py` (unchanged) |
> | Ask MattGPT | **Ask Agy** | `"Ask Agy"` | `ui/pages/ask_mattgpt/` (unchanged) |
> | About Matt | **My Profile** | `"My Profile"` | `ui/pages/about_matt.py` (unchanged) |
>
> Streamlit converts spaces in keys to dashes for CSS classes: `key="topnav_My Work"` produces class `st-key-topnav_My-Work`. References below to "Ask MattGPT", "Explore Stories", or "About Matt" as MODULE / FUNCTION / PACKAGE names (e.g., `ask_mattgpt_header.py`, `render_about_matt()`, `tests/bdd/features/about_matt.feature`) refer to the unchanged code structure — only the user-facing labels and routing values changed.
>
> Additionally: Home navbar is now brand-left + space-between layout (MATTGPT-106); category cards are 3-col grid with unified light-bg treatment and whole-card click targets (MATTGPT-107).

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
    - [Multi-Field Entity Search](#2-multi-field-entity-search)
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
- [Mobile Responsiveness](#mobile-responsiveness)
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
**Last Updated:** June 8, 2026

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

### Current State (May 2026)

**Role Match feature (April–May 2026):** JD-to-portfolio fit assessment. Phases 1-3 (recruiter view, AgGrid results panel, action buttons, share/export) shipped April 2026. Phase 4 slice 1 (private-view lock icon + password gate UI shell, fail-closed: deployment state must not leak) shipped May 2026. Engine: `services/jd_assessor.py` three-stage pipeline + deterministic `compute_recommendation()` scoring. See `BACKLOG.md` MATTGPT-012 for Phase 4 slices 2 (agentic bypass) and 3 (private assessment view).

**Triage Agent surface (May 2026):** Engine-as-adapter pattern. `services/jd_assessor.py` is now shared by two surfaces — the interactive Streamlit Role Match page and `scripts/assess_jd.py` (CLI for external agent orchestration, schema-versioned JSON envelope over stdin/stdout). Orchestration assets live in `agent/triage/` (synthesis prompt, filter config) — source of truth in this repo, copied to Cowork's designated folder. `agent/discovery/` reserved for v2 ATS push-model discovery. See `tests/unit/test_assess_jd.py` for the CLI contract.

**Prompt Architecture Refactor (Jan 26, 2026) — 93-97% structural pass rate:**
- Created `prompts.py` with clean BASE_PROMPT + SYNTHESIS_DELTA + STANDARD_DELTA architecture
- BASE_PROMPT establishes Agy as fact-relayer, not evaluator (prevents meta-commentary)
- Removed `get_theme_guidance()` which had conflicting "Emphasize:" instructions
- Removed `BANNED_PHRASES_CLEANUP` post-processing bandaid
- Fixed hardcoded client exclusions → pattern-based `is_generic_client()`
- Added structural assertion tests: `assert_no_meta_commentary()`, `assert_agy_voice()`, `assert_no_hardcoded_drift()`
- Meta-commentary failures reduced from 10/31 → 1-2/31
- `backend_service.py` reduced by 564 lines

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
5. **Future Enhancements:** See [BACKLOG.md](BACKLOG.md)

**For migration history and refactoring details,** see [HISTORY.md](HISTORY.md)

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
│   ├── jd_assessor.py              # Role Match engine (extraction → retrieval → assessment + compute_recommendation())
│   ├── pinecone_service.py         # Pinecone client & vector search
│   ├── query_logger.py             # 32-column event logger → Google Sheets
│   ├── rag_service.py              # Semantic search orchestration
│   ├── semantic_router.py          # Query routing & validation
│   └── story_service.py            # Story retrieval logic (placeholder)
│
├── ui/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── navbar.py                  # Top navigation
│   │   ├── footer.py                  # Footer
│   │   ├── story_detail.py            # Story Detail Component (shared renderer)
│   │   ├── ask_mattgpt_header.py      # Unified Ask MattGPT header
│   │   ├── why_agy_dialog.py          # "Why Agy?" @st.dialog (identity + origin story)
│   │   ├── how_agy_dialog.py          # "How Agy Searches" @st.dialog (3-step RAG flow)
│   │   ├── how_i_built_dialog.py      # "How I Built MattGPT" @st.dialog (MATTGPT-102)
│   │   ├── category_cards.py          # Landing page capability cards
│   │   ├── hero.py                    # Hero section component
│   │   ├── lock_icon.py               # Private-view gate (popover + password, fail-closed)
│   │   ├── thinking_indicator.py      # Loading/processing indicator
│   │   └── timeline_view.py           # Era-based timeline for Explore Stories
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                    # Home page
│   │   ├── explore_stories.py         # Stories browser
│   │   ├── ask_mattgpt/               # Modular page structure (router + 9 submodules)
│   │   │   ├── __init__.py            # Router
│   │   │   ├── landing_view.py        # Landing page UI
│   │   │   ├── conversation_view.py   # Chat conversation UI
│   │   │   ├── conversation_helpers.py # Message rendering
│   │   │   ├── backend_service.py     # RAG pipeline integration
│   │   │   ├── prompts.py             # BASE_PROMPT + DELTA architecture
│   │   │   ├── styles.py              # CSS definitions
│   │   │   ├── story_intelligence.py  # Theme/persona inference
│   │   │   ├── shared_state.py        # Session state management
│   │   │   └── utils.py               # Shared utilities
│   │   ├── about_matt.py              # About page
│   │   ├── banking_landing.py         # Banking landing
│   │   ├── cross_industry_landing.py  # Cross-industry landing
│   │   └── role_match.py              # Role Match page
│   │
│   ├── styles/
│   │   ├── __init__.py
│   │   └── global_styles.py        # Shared CSS overrides
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
├── scripts/                        # Operational scripts
│   └── assess_jd.py                # Engine CLI wrapper (JD stdin → JSON envelope; agent-callable surface)
│
├── agent/                          # Orchestration assets for Cowork (Claude Desktop)
│   ├── README.md                   # Layout + Cowork setup
│   ├── triage/                     # v1 JD triage (operational)
│   │   ├── synthesis_prompt.md     # Three-layer logic (capability + filter + thin fit)
│   │   └── filter_config.json      # Hard rules + engagement_mode definitions
│   └── discovery/                  # v2 placeholder (ATS push-model discovery)
│       └── README.md
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
| **ask_mattgpt_header.py** | Unified header + dialog trigger buttons | Ask MattGPT (Landing + Conversation) | `render_ask_header()`, `get_ask_header_css()` |
| **why_agy_dialog.py** | "Why Agy?" identity + origin story | Ask MattGPT, Home footer | `render_why_agy_dialog()` |
| **how_agy_dialog.py** | "How Agy Searches" 3-step RAG flow | Ask MattGPT, Home footer | `render_how_agy_dialog()` |
| **how_i_built_dialog.py** | "How I Built MattGPT" technical deep-dive — architecture, pipeline, CTA chips → Ask Agy | Ask MattGPT, Home footer | `render_how_i_built_dialog()` |
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
    st.session_state["active_tab"] = "Ask Agy"  # was "Ask MattGPT" pre-MATTGPT-100
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
st.session_state["active_tab"] = "My Work"  # was "Explore Stories" pre-MATTGPT-100
```

---

### Interactive Click Handling Patterns

Three distinct patterns exist in the codebase. Read this before building any new click handler. **Start with Pattern 1; only escalate when it provably fails.**

#### Pattern 1 — Plain `st.button` + scoped CSS (default)

**Use when:** The clickable element can visually be a Streamlit button (styled away via CSS).

**Canonical example:** `ui/pages/ask_mattgpt/conversation_helpers.py` — Related Projects source chips (~line 626). Button is styled as a chip via `[class*="st-key-{stable_key}"] button` CSS. Click is handled by the standard Streamlit WebSocket → Python rerun cycle. No JS, no HTML bridge.

```python
if st.button(label, key=f"chip_{idx}"):
    handle_chip_click(idx)
```

**Why this is the default:** Zero fragility. React reconciliation never affects it. Streamlit reruns don't kill anything.

#### Pattern 2 — Delegated `parentDoc` listener + hidden `st.button` bridge

**Use when:** The clickable element must be a raw HTML element (not a Streamlit button), and per-element `onclick` would die on React reconciliation.

**Canonical examples:**
- `ui/components/how_i_built_dialog.py` — `.hib-cta-prompt` chips (MATTGPT-117)
- `ui/pages/about_matt.py` — Copy snippet + Download PDF spans (MATTGPT-118)
- `ui/pages/explore_stories.py` — Cards view delegated listener

**Key rules:**
1. Listener lives on `parentDoc` (the Streamlit page's `document`), not on individual elements. This survives React DOM reconciliation because `parentDoc` itself is never replaced.
2. Use `e.target.closest(selector)` inside the handler to find the target dynamically.
3. For clipboard: use `window.parent.navigator.clipboard.writeText()` (async API). Both `.then()` and `.catch()` should show confirmation so feedback fires regardless of clipboard permission state in headless test environments.
4. For Streamlit-triggered actions (anything requiring a Python rerun): find `parentDoc.querySelector('[class*="st-key-{key}"] button')` and call `.click()` — hidden button fires the Streamlit rerun.

```python
# Hidden bridge button (Python side)
if st.button("", key="am_download_pdf"):
    # handler runs after Streamlit rerun

# JS side — delegated listener
components.html("""
<script>
(function() {
    var parentDoc = window.parent.document;
    parentDoc.addEventListener('click', function(e) {
        var btn = e.target.closest('#my-html-btn');
        if (!btn) return;
        // For clipboard:
        window.parent.navigator.clipboard.writeText(text).then(showConfirm).catch(showConfirm);
        // For Streamlit bridge:
        var stBtn = parentDoc.querySelector('[class*="st-key-am_download_pdf"] button');
        if (stBtn) stBtn.click();
    });
})();
</script>""", height=0)
```

**CSS for hidden bridge buttons** (in `global_styles.py`):
```css
[class*='st-key-am_download_pdf'] { display: none !important; }
```

**Why NOT per-element `onclick`:** React's `dangerouslySetInnerHTML` reconciliation replaces inner DOM nodes on every Streamlit rerun, killing per-element event bindings from the `components.html` iframe's JS context. Delegates on `parentDoc` survive because `parentDoc` is never replaced. See April 2026 incident in CLAUDE.md.

#### Pattern 3 — Per-element `addEventListener` (deprecated, do not use)

Legacy pattern — per-element bindings inside `components.html` iframes. Dies on Streamlit rerun (iframe is recreated, destroying the JS context). **Do not introduce new instances.** See CLAUDE.md "Interactive Click Handling — STOP, Read This First" for the full incident history.

---

### My Profile Page (`ui/pages/about_matt.py`)

**MATTGPT-118 (June 2026):** Added Copy snippet + Download PDF interaction to the "For a referrer" section.

- **Copy snippet:** HTML `<span id="am-copy-snippet-btn">` wired via Pattern 2 delegated listener. Calls `window.parent.navigator.clipboard.writeText()`. Both `.then` and `.catch` change the span label to `✓ Copied!` (green, 2s timeout) so feedback fires regardless of clipboard permission state.
- **Download PDF:** HTML `<span id="am-download-pdf-btn">` → JS finds `[class*="st-key-am_download_pdf"] button` → `.click()` → Streamlit rerun → Python handler opens `window.open` + `printWindow.print()` with a full printable HTML doc (signals, voice, competencies, How I Lead, career timeline). Pattern matches `action_buttons.py`.
- Both interactions share a single `components.html` delegated listener block registered once per page render.

---

## Refactoring History

See [HISTORY.md](HISTORY.md) for the full evolution story including the Oct-Nov 2025 component-based migration (app.py 5,765 → 284 lines), RAG pipeline cleanup timeline, and removed component decisions.

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

### Avatar Sizing Standards

See **ADR 017** in `docs/ADR.md` for the full decision record.

**Quick reference:** Header avatars = 64px, chat avatars = 60px. Inline styles required to override Streamlit emotion-cache. Do not change avatar sizing without consulting ADR 017.

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
INPUT_EXCEL_FILE="MPugmire - STAR Stories - [DATE].xlsx"  # e.g. 09MAR26
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
    - Title (story title - improves keyword matching)  # Added Jan 2026
    - Theme + Industry + Sub-category (behavioral context)
    - 5P Summary (concise overview)
    - STAR fields: Situation, Task, Action, Result (2-3 items each)
    - Process details (max 3 items)
    - Public tags (comma-separated)

    Result: ~200-400 token text optimized for behavioral queries
    """
```

**Why This Approach:**
- **Title inclusion:** Story titles contain key terminology (e.g., "Platform Modernization", "Cloud Migration") that users search for directly
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

See [RAG Pipeline Audit → Data Flow Map](#data-flow-map) for the canonical query→response diagram (9-layer trace with removal history).

---

### Synthesis Mode (Updated January 2026)

**Problem:** RAG retrieves individual stories well but struggles with big-picture questions like "What are common themes?" or "What patterns do you see?" — these need holistic context, not a single story.

**Solution:** Intent-aware retrieval that changes strategy based on query type, with entity-first classification.

**Intent Classification (Semantic Router Only - Jan 29, 2026):**

All intent classification uses the embedding-based semantic router (`services/semantic_router.py`) which maps queries to 15 intent families without LLM cost. Entity detection runs in parallel to identify company/project/title mentions.

```
Query → Semantic Router (embedding similarity against 106+ intent embeddings)
      → Entity Detection (substring matching against known entities + exact title match)
      → Intent Family Resolution:
        - background, behavioral, delivery, team_scaling, leadership
        - technical, domain_payments, domain_healthcare, stakeholders
        - innovation, agile_transformation, narrative, synthesis, out_of_scope, personal
```

The semantic router handles all intent classification — synthesis detection (`intent_family == "synthesis"`), out_of_scope detection, and all other families — via embedding similarity alone.

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

**Entity Detection:**
Checks fields in order: Client, Employer, Division (Project and Place excluded — semantic search handles those naturally)
- "CIC" matches Division: "Cloud Innovation Center"
- "JPMorgan" matches Client: "JP Morgan Chase"
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
- **Thresholds:** HARD_ACCEPT=0.80, SOFT_ACCEPT=0.40 (calibrated Jan 2026)
- **Intent Families:** 15 families (background, behavioral, delivery, team_scaling, leadership, technical, domain_payments, domain_healthcare, stakeholders, innovation, agile_transformation, narrative, synthesis, out_of_scope, personal)
- **Cost:** ~$0.0000002 per query (one embedding)
- **Rule:** Fail-open on errors (accept query if embedding fails)
- **Do not remove:** Saves LLM cost, prevents garbage-in

#### Observability Logging (Jan 2026)

Structured logs added to diagnose "I can't help with that" issues in production.

**Log tags:**
- `[QUERY_REJECTED]` — Query rejected by entity gate or low Pinecone confidence
- `[API_ERROR_DETECTED]` — Router returned `error_fallback` family (connection/timeout issue)

**Log format:**
```
[QUERY_REJECTED] reason=low_pinecone, router_family=background, router_score=0.42, pinecone_score=0.12, query=Tell me about...
[API_ERROR_DETECTED] router=error_fallback, pinecone_score=0.35, confidence=high, query=Tell me about...
```

**Lives in:** `ui/pages/ask_mattgpt/backend_service.py`

### Layer 2: Intent Classification (Hybrid)

#### Semantic Router Intent Family (Primary)
- **Job:** Map query to intent family via embedding similarity (no LLM cost)
- **Lives in:** `services/semantic_router.py`
- **Families:** narrative, behavioral, delivery, team_scaling, leadership, technical, etc.
- **Cost:** Free (reuses embedding from validation step)



#### Entity Detection
- **Job:** Detect company/division/title mentions in query for scoped retrieval
- **Lives in:** `ui/pages/ask_mattgpt/backend_service.py:detect_entity()`
- **Fields checked (in order):** Client, Employer, Division, Title
- **Hard filtering:** Client, Employer, Division → Apply Pinecone metadata filter
- **Soft filtering:** Title → Detected but NO Pinecone filter (semantic search ranks naturally)
- **Why soft filtering for Title:** Hard filtering returned only 1 result, breaking Related Projects UX
- **Exclusions:** "Multiple Clients", "Independent", "Career Narrative" (too generic to filter)
- **Returns:** `(field_name, entity_value)` tuple or `None`

#### Multi-Field Entity Search
- **Job:** Search across ALL entity fields when entity detected, not just the primary field
- **Lives in:** `services/pinecone_service.py:189-216`
- **Implementation:** Uses Pinecone `$or` operator to search across 6 fields simultaneously
- **Note:** Entity DETECTION checks 4 fields (Client, Employer, Division, Title), but Title uses soft filtering. Pinecone SEARCH spans 6 fields for hard-filtered entities.
- **Fields searched:** `client`, `employer`, `division`, `project`, `place`, `title`
- **Casing rules:**
  - **Lowercase fields:** `division`, `employer`, `project`, `place` → `.lower()` applied
  - **PascalCase fields:** `client` → preserve original casing
- **Example:** Query "Accenture work" → detected as Client, then searches:
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
- **⚠️ Note (Feb 2026):** `get_synthesis_stories()` uses PascalCase `"Theme"` in Pinecone filters (line ~444). This works currently (Pinecone metadata was uploaded with PascalCase `Theme` key) but is inconsistent with the lowercase field name convention used elsewhere. If entity-scoped synthesis returns unexpected zero results, check this field name casing first.

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

**Generic-client exclusion (pattern-based, replaces the former `EXCLUDED_CLIENTS` constants):**
**Lives in:** `utils/client_utils.py` — `is_generic_client(client: str) -> bool`

Per the CLAUDE.md "No Hardcoded Enums for Data-Derived Values" rule, the prior set of hardcoded `EXCLUDED_CLIENTS` constants (replicated across three files and prone to drift) was replaced by a single pattern-matching helper. Call sites import `is_generic_client` and use it as a filter rather than maintaining parallel exclusion lists.

| Value pattern | Reason |
|-------|--------|
| `Independent`, `Independent Project` | Personal projects, not a real client |
| `Career Narrative` | Meta-content, not a client |
| `Multiple Clients`, `Multiple Financial Services Clients` | Aggregate, not a real client |
| `Financial Services Client(s)` | Anonymized aggregate |
| `Personal`, `Sabbatical`, `Various`, `N/A`, `""`, `None` | Empty/placeholder values |

**Note:** Single source of truth — if a new exclusion is needed, update `is_generic_client()` once, not multiple files.

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
- **Standard mode:** WHY (tension/stakes — what wasn't working) → HOW (what Matt did differently) → WHAT (proof — measurable results)
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
- ~~Remove banned phrases that LLM ignores (BANNED_PHRASES_CLEANUP list)~~ ✅ **REMOVED (Jan 26):** BASE_PROMPT now instructs "delete and state the fact"

**Meta-Commentary Safety Net** ✅ **LARGELY RESOLVED (Jan 26):**
- `META_SENTENCE_PATTERNS` regex catches LLM meta-commentary that violates NEVER rules
- Patterns: "This story demonstrates...", "This reflects Matt's...", "reveals his pattern of..."
- ~~**Known issue:** Prompt conflict between "Emphasize X" and "NEVER meta-commentary"~~ ✅ **FIXED:** Removed `get_theme_guidance()`, new BASE_PROMPT + DELTA architecture
- Failures reduced from 10/31 → 1-2/31 (LLM variance)

**BANDAID Logging:**
```python
def _log_bandaid(bandaid_name: str, details: str):
    """Log when a post-processing safety net catches a violation.
    Used to track which band-aids fire so unused ones can be deleted."""
```
- Logged to DEBUG output when `DEBUG=True`
- Helps identify which post-processing rules are actually needed vs. cruft

### Data Flow Diagram

See [RAG Pipeline Audit → Data Flow Map](#data-flow-map) for the canonical query→response diagram (9-layer trace with removal history).

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
st.session_state["active_tab"] = "Ask Agy"  # was "Ask MattGPT" pre-MATTGPT-100. Navigate to Ask Agy
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
st.session_state["active_tab"] = "My Work"  # was "Explore Stories" pre-MATTGPT-100

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
| `banking_landing.py` | Project count, client pills with counts, data-derived capability cards (Core ≥3 stories / Specialized <3 stories) via `utils/landing_cards.py::build_landing_cards()` |
| `cross_industry_landing.py` | Project count, industry pills, data-derived capability cards (same Core/Specialized tier shape) |
| `category_cards.py` | Banking/Cross-industry project counts, top 3 client pills |
| `home.py` | Passes STORIES to category_cards |

**Note on the data-derived card pattern** (Phase 2 refactor, May 11-12, 2026): banking_landing.py and cross_industry_landing.py no longer hardcode capability card lists. Cards are derived at runtime from the story corpus by `build_landing_cards(stories, industry)` — eliminates by construction the regression shape where a hardcoded card promises a curated slice that doesn't exist in the data. See `utils/landing_cards.py` and CHANGELOG May 11-12 entries.

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

### Explore Stories Two-Row Filter Bar (MATTGPT-065)

**Shipped:** June 2026. Replaced the collapsible "▸ Advanced Filters" toggle with a permanent two-row filter bar.

**Row 1 (unchanged):** Search box + Industry selectbox + Capability selectbox — `st.columns([2, 1, 1])`.

**Row 2 (new):** Client + Role + Domain selectboxes + Reset button — always visible on desktop, hidden on mobile via CSS.

```python
# Row 2 container key — used for CSS mobile-hide
with st.container(key="r2_row"):
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.4])
    with c1:
        clients_version = st.session_state.get("_widget_version_clients", 0)
        sel_client = st.selectbox("Client", options=["All"] + clients,
                                  index=client_index, key=f"r2_client_v{clients_version}")
        F["clients"] = [] if sel_client == "All" else [sel_client]
```

**CSS mobile-hide pattern** (in `global_styles.py`):
```css
@media (max-width: 767px) {
    [class*="st-key-r2_row"] { display: none !important; }
}
```

**Widget key versioning:** Row 2 selectboxes use `key=f"r2_{field}_v{version}"` so the Reset button can force a widget rebuild by incrementing `st.session_state["_widget_version_clients"]` (and `_roles`, `_domains` equivalents). Without versioning, Streamlit re-uses the old widget value even after session state is cleared.

**`F["clients"]` is always a list:** `matches_filters()` expects `F["clients"]` to be `[]` (all) or `["Capital One"]` (filtered). Never set it to a bare string — this breaks the IN-list logic in `utils/filters.py`.

**MATTGPT-119 (backlog):** Mobile "Filters ▾" toggle to reveal/hide Row 2 on small viewports. Row 2 is CSS-hidden on mobile until that ships.

### Known Limitations

1. **Synthesis + specific topic:** "Tell me about Matt's rapid prototyping work" classified as synthesis but should find the specific rapid prototyping story. Current workaround: synthesis now uses user query embedding.
2. ~~**Multi-client stories:** Stories with `Client="Multiple Clients"` won't match entity filters.~~ **FIXED (Jan 2026):** Multi-Field Entity Gate now searches across 5 fields using Pinecone `$or` operator. Entity detection narrowed to 3 fields (Client, Employer, Division) to prevent false positives.
3. **Ground truth fidelity:** LLM paraphrases instead of quoting verbatim despite `[[CORE BRAND DNA]]` markers.
4. **Deprecated documentation:** `mattgpt_system_prompt.md` documents the original "MattGPT" persona (pre-Agy). The current Agy voice is documented in this file under Component Contracts → Agy Voice Generator.
5. **LLM stochasticity:** Eval may show occasional failures due to LLM response variability. Re-running typically passes. Semantic similarity scoring would address this (see BACKLOG.md → MATTGPT-035 (Eval Modernization — Semantic Scoring)).

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
| `_widget_version_clients` | `int` | Row 2 Client selectbox rebuild counter (Reset increments) |
| `_widget_version_roles` | `int` | Row 2 Role selectbox rebuild counter |
| `_widget_version_domains` | `int` | Row 2 Domain selectbox rebuild counter |

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
| **ui_helpers.py** | Debug logging, branch-aware rejection banner | `dbg()`, `safe_container()`, `render_no_match_banner()`, `BANNER_COPY` / `RULE_CHIPS` / `PERSONAL_CHIPS` / `OUT_OF_SCOPE_CHIPS` |

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
    """⚠️ DEPRECATED (Jan 26, 2026) - No longer imported by backend_service.py.
    Had conflicting 'Emphasize:' instructions that caused meta-commentary.
    Kept for backward compatibility but not used in production."""

def build_story_context_for_rag(story: dict) -> str:
    """Build WHY→HOW→WHAT context string for RAG prompt injection."""

def get_theme_emoji(theme: str) -> str:
    """Get emoji for theme (🏗️ 🧠 🔄 👥 🛡️ 🚀 🧭)."""
```

---

### prompts.py ✅ NEW (Jan 26, 2026)

Clean prompt architecture that prevents meta-commentary by keeping Agy in REPORTING mode, not evaluation mode.

**Architecture: BASE_PROMPT + DELTA Pattern**

```
┌─────────────────────────────────────────────────────────────┐
│  BASE_PROMPT (shared across all modes)                      │
│  - Agy's core identity: fact-relayer, not evaluator         │
│  - Banned phrases with "delete and state the fact" guidance │
│  - Pronoun transformation rules (I → Matt)                  │
│  - Fact-pairing and context isolation rules                 │
├─────────────────────────────────────────────────────────────┤
│  + SYNTHESIS_DELTA (for multi-story questions)              │
│    OR                                                       │
│  + STANDARD_DELTA (for single-story questions)              │
├─────────────────────────────────────────────────────────────┤
│  + OFF_TOPIC_GUARD                                          │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle:** Agy RELAYS facts from stories. She does NOT evaluate Matt.

**Meta-Commentary Prevention:**
```python
# BAD: "Matt's ability to align stakeholders enabled the transformation."
# GOOD: "Matt aligned 12 stakeholders across 3 regions. The transformation shipped on time."

# BAD: "This demonstrates his technical leadership."
# GOOD: "He led a team of 40 engineers. They shipped the platform in 6 months."
```

**Key Functions:**
```python
def build_system_prompt(is_synthesis: bool, matt_dna: str, client_list: str) -> str:
    """Build complete system prompt: BASE_PROMPT + mode-specific DELTA + OFF_TOPIC_GUARD."""

def build_user_message(question, story_context, opening, closing, is_synthesis, ...) -> str:
    """Build user message with stories and response instructions."""

def get_verbatim_requirement(summary: str) -> str:
    """Extract required verbatim phrases from Professional Narrative stories."""
```

**Why This Architecture:** BASE_PROMPT + DELTA separates universal voice rules from contextual variations. Each module has a single job: `build_system_prompt()` selects the mode-appropriate delta, `build_user_message()` injects story context and response instructions, and `get_verbatim_requirement()` enforces identity-phrase fidelity. The result is a prompt that can't contradict itself — Agy's role as messenger (not evaluator) is structurally enforced.

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
| `test_structural_assertions.py` | ✅ NEW: Meta-commentary, voice, and drift checks |

**Current Status (March 2026):**
- RAG quality: 98.1% pass rate (60/61 golden queries across 8 categories)
- Structural: 93-97% pass rate (meta-commentary varies with LLM stochasticity)

**eval_rag_quality.py:**
- Runs 61 golden queries across 8 categories: narrative, client, intent, edge, surgical, entity_detection, marketing, context_story
- Checks: voice consistency, ground truth matches, client attribution, client bolding, entity detection, context bypass
- Outputs JSON results to `tests/eval_results/`

**Test Categories:**
| Category | Count | Checks |
|----------|-------|--------|
| `narrative` | 10 | Voice + ground_truth phrases |
| `client` | 6 | Voice + client attribution + bolding |
| `intent` | 5 | Voice + intent classification |
| `edge` | 4 | Voice + client attribution |
| `surgical` | 6 | Entity-first + specific story retrieval |
| `entity_detection` | 9 | Regression tests for detect_entity() |
| `marketing` | 3 | Marketing/recruiter question handling |
| `context_story` | 3 | "Ask Agy About This" button flow |

**Current eval pass rate:** 98.1% (60/61 queries across 8 categories, March 2026). Full progression history in [HISTORY.md](HISTORY.md).

**Running Eval:**
```bash
# RAG quality eval
python tests/eval_rag_quality.py
# Outputs: tests/eval_results/eval_YYYYMMDD_HHMMSS.json

# Structural assertions (meta-commentary, voice, drift)
python tests/test_structural_assertions.py --report
# Outputs: tests/eval_results/structural_baseline_YYYYMMDD_HHMMSS.json
```

**test_structural_assertions.py:**

Three structural assertion functions that run against all 31 queries:

| Function | Checks | Pass Criteria |
|----------|--------|---------------|
| `assert_no_meta_commentary()` | "Matt's ability to...", "This demonstrates...", etc. | No matches |
| `assert_agy_voice()` | Multiple 🐾, "we" pronouns, Agy self-reference | Exactly 1 🐾, no "we", no "Agy thinks" |
| `assert_no_hardcoded_drift()` | ENTITY_NORMALIZATION, client exclusions vs JSONL | All values exist in source |

**Meta-Commentary Patterns Detected:**
```python
META_PATTERNS = [
    r"\bThis demonstrates\b",
    r"\bThis reflects\b",
    r"\bMatt's ability to\b",
    r"\bhis ability to\b",
    r"\bIn essence,?\b",
    # ... 20+ patterns
]
```

---

### Error Handling Patterns (Updated Jan 29, 2026)

**Layer 1 (Validation):**
- `is_nonsense()` → Returns rejection message with category
- `semantic_router()` → Returns `(False, score)` if below threshold; fails-open on errors

**Layer 2 (Fast Exit + Entity Detection):**
- `out_of_scope` check → Returns graceful redirect if `intent_family == "out_of_scope"`
- `detect_entity()` → Returns `None` if no entity found; Title entities use soft filtering

**Layer 3 (Retrieval):**
- `semantic_search()` → Returns empty results on Pinecone error
- `get_synthesis_stories()` → Returns empty list on error

**Layer 4 (Confidence Gate):**
- `confidence == "none"` → Returns "I couldn't find relevant stories" message

**Layer 5 (Generation):**
- `_generate_agy_response()` → Raises `RateLimitError` on 429, returns fallback on other errors
- `rag_answer()` → Catches `RateLimitError`, returns empty sources with:
  ```
  "🐾 I need a quick breather — try again in about 15 seconds!"
  ```

**Removed (Jan 29, 2026):** `classify_query_intent()` error handling — function deleted.

**UI Error Handling:**
- `send_to_backend()` wraps all errors in try/except
- Failed responses show generic error message
- Network errors trigger retry prompt

**Logging:**
- `dbg()` function logs when `DEBUG=True`
- Error details captured in `st.session_state["__ask_dbg_*"]` keys

---

### Query Logger (Google Sheets)

Query logging to Google Sheets, capturing enriched data for every search across Ask MattGPT and Explore Stories.

**History:**
| Date | Action | Outcome |
|------|--------|---------|
| Jan 10, 2026 | Added `streamlit-analytics2` | Working initially (3 pageviews logged) |
| Jan 12, 2026 | Production failure | `AttributeError: st.session_state has no attribute "session_data"` |
| Jan 12, 2026 | Removed analytics + dependencies | Quick fix to restore production stability |
| Mar 9, 2026 | Re-enabled with Google Sheets logger | Enriched schema, fire-and-forget threading |

**Architecture:**
- **Service:** `services/query_logger.py`
- **Backend:** Google Sheets via `gspread` + Google service account
- **Threading:** Fire-and-forget daemon thread — Google Sheets API latency never blocks user response
- **Error handling:** Silent failure (try/except pass) — logging should never break the app
- **Browser context:** Captured in main Streamlit thread before spawning daemon (st.context is thread-local)

**Schema (11 columns):**
| Column | Source | Notes |
|--------|--------|-------|
| Timestamp | `datetime.now()` | Server-side UTC |
| Query | function param | User's search text |
| Page | function param | "Ask Agy" or "Explore Stories" |
| Intent Family | semantic router | e.g., "leadership", "personal", "out_of_scope" |
| Confidence | Pinecone result | "high", "low", "none", or "" if redirected before search |
| Result Count | `len(results)` | 0 for redirects |
| Redirect Reason | early-return reason | "rule:{cat}", "semantic_router:personal", "low_confidence", "" for success |
| User-Agent | `st.context.headers` | Browser identification |
| Screen Width | `streamlit_js_eval` | Viewport width for CSS breakpoint analysis |
| Timezone | `st.context.timezone` | User's timezone |
| Referrer | `st.context.headers` | Captured on first mount via first-mount guard |

**Logging Points:**
| Location | Count | Points |
|----------|-------|--------|
| `backend_service.py` | 6 | Nonsense filter, out_of_scope, personal, low_confidence, empty_pool, success |
| `explore_stories.py` | 2 | Personal/OOS redirect, search results |

**Dependencies:** `gspread`, `google-auth` (in requirements.txt)

**Secrets:** Requires `[gcp_service_account]` section in Streamlit secrets (both local `.streamlit/secrets.toml` and Streamlit Cloud settings)

**Browser Context Capture (app.py):**
- Referrer: Captured in first-mount guard from `st.context.headers.get("Referer", "")`
- Screen width: Captured via `streamlit_js_eval` with `st.rerun()` to remove iframe from DOM

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
- `top_k`: 10 (retrieve top 10 matches, from `SEARCH_TOP_K` in config/constants.py)
- `min_similarity`: 0.15 (from `PINECONE_MIN_SIM` in config/constants.py)
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

**Purpose:** Semantic search orchestration and confidence gating. LLM generation is handled by `backend_service.py`.

**Key Functions:**
```python
def semantic_search(q: str, stories: list, top_k: int = SEARCH_TOP_K, filters: dict = None):
    """
    1. Embed query with text-embedding-3-small
    2. Pinecone vector search (top_k from constants, default 10)
    3. Confidence gating (HIGH=0.25, LOW=0.20)
    4. Return ranked stories with scores and confidence level
    """
```

**Note:** LLM generation (GPT-4o, 700 max tokens) and context assembly live in `backend_service.py:_generate_agy_response()`. See Component Contracts → Layer 4: Response Generation for details.

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

**External Monitoring:**
- **UptimeRobot** — HTTP/S monitor configured at https://askmattgpt.streamlit.app. Pings the app every ~5 minutes to prevent Streamlit Cloud sleep. Sends User-Agent containing "UptimeRobot". Filtered from BOTH `page_load` AND `query` event logging via `MONITORING_BOT_SIGNATURES` in `config/constants.py` (checked at `app.py:104` for page_load and `services/query_logger.py::log_query()` via `is_bot()` for queries — extended May 13, 2026). The same signature list also catches `HeadlessChrome` (Chrome agent regression runs) and the legacy `Chrome/103.0.0.0` probe pattern. Bot traffic produces zero rows in the Google Sheet log, keeping conversion/bounce analysis based on real visitors only.

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

#### 2. Multi-Field Entity Search

When a user asks about an entity (e.g., "Accenture work"), the system now searches across **six metadata fields** using Pinecone's `$or` operator—not just the `client` field.

| Field | Casing | Example Match |
|-------|--------|---------------|
| `client` | PascalCase | `"Accenture"` |
| `employer` | lowercase | `"accenture"` |
| `division` | lowercase | `"cloud innovation center"` |
| `project` | lowercase | `"accenture"` |
| `place` | lowercase | `"accenture"` |
| `title` | PascalCase | `"Driving Cloud-Native Innovation..."` |

**Implementation:** `pinecone_service.py:189-216`

**Note (Jan 29, 2026):** Title entities use **soft filtering** — they're detected but don't create a Pinecone metadata filter. This ensures Related Projects populate naturally via semantic search.

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
- [Multi-Field Entity Search](#2-multi-field-entity-search) — Component contract details
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
| `about_matt.py` | Timeline, company names, sample chip questions (`ABOUT_MATT_SEED_QUESTIONS`) | Curated CV/resume presentation |

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

### Pattern 4: Page CSS Placement — Rerun Persistence (MATTGPT-068)

**Page CSS belongs in `ui/styles/global_styles.py`**, injected by
`apply_global_styles()` from `app.py` on every rerun at a stable position in
the script. Do **not** put long-lived page styling in an inline `<style>`
block inside a page's `render_*()` function.

**Why:** Inline `<style>` blocks inside a page render function are stripped by
Streamlit **position-reconciliation** when a rerun routes to a *different*
page. The prior page's DOM positions are replaced element-by-element by the
new page's output, and the page never re-runs its own render — so its first
markdown element (the `<style>` block) is overwritten and every rule it
carried disappears at once. The visible symptom is **layout collapse**: grids
and cards fall back to default block flow during the AI-thinking dim (the 33%
stale-frame opacity) on chip-click transitions that navigate away
(e.g., About Matt → Ask MattGPT). `global_styles.py` survives because
`apply_global_styles()` runs at the top of `app.py` on every rerun, at a
stable position reconciliation never replaces.

**Namespacing:** When a relocated page's class names collide with classes used
on other pages, globalizing them would leak styling app-wide. Namespace the
page-scoped ones — e.g., About Matt's `stats-bar` / `stat-*` / `section-*`
became `.am-*` so they don't restyle Home / banking / story_detail /
role_match (which share those class names with different intended styles).

**Precedent:** chip CSS was relocated from `ui/components/category_cards.py`
first; About Matt's full inline block was relocated under MATTGPT-068;
My Work / Explore Stories' full inline block was relocated under MATTGPT-105.

**Applies within a single page too (MATTGPT-105):** The same stripping occurs
during mid-rerun pauses *within the same page* — not only on page transitions.
When `render_thinking_indicator()` fires on My Work (Cards view) after "Ask Agy
About This", Streamlit partially replaces the DOM during its rerun pause. Inline
`<style>` blocks injected inside the page's render functions are in the
replacement window; `global_styles.py` is not, because `apply_global_styles()`
runs at `app.py:43` before any render path executes.

**Namespace convention (`es-*`):** When page-scoped CSS is relocated to
`global_styles.py` it gains app-wide scope, so collision-prone class names must
be prefixed. Pattern: `es-` for My Work/Explore Stories (`.es-fixed-height-card`,
`.es-pagination`, `.es-results-count`, etc.). Apply the prefix to any class that
previously had implicit page scope via inline injection.

**Use when:** A page renders custom CSS AND a user action on it can navigate
to a different page mid-rerun (any chip/button that sets `active_tab` and
reruns), OR can trigger a rerun on the same page (thinking indicator, filter
changes, pagination).

---

### Pattern 5: AgGrid Styling — Iframe Boundary Constraint (MATTGPT-064)

**CSS rules in `global_styles.py` cannot reach the AgGrid iframe.** AgGrid
renders inside a separate `iframe` document. CSS injected into the parent
page's `<head>` — including everything in `global_styles.py` — stops at the
iframe boundary. Any `.ag-theme-streamlit .ag-row` rules in `global_styles.py`
are effectively dead code; they never apply to AgGrid's DOM.

**Two delivery mechanisms for AgGrid styles:**

**1. Python-side (static row properties):** Pass `opts["rowStyle"]` to
`GridOptionsBuilder` — AgGrid applies it inside its own render, no iframe
boundary involved. Example: `opts["rowStyle"] = {"cursor": "pointer"}`.

**2. JS injection (CSS variable overrides):** Inject a `components.html`
snippet *after* the `AgGrid(...)` call. Reach into `iframe.contentDocument`
and call `root.style.setProperty(...)` on the AgGrid root element.

**Guard selector:** Use `.ag-root-wrapper`, not `.ag-theme-streamlit`.
The theme class is `.ag-theme-streamlit` in light mode and
`.ag-theme-streamlit-dark` in dark mode. MattGPT always runs dark, so
`.ag-theme-streamlit` returns `null` and the injection silently bails on
every call. `.ag-root-wrapper` is theme-agnostic and always present once
AgGrid renders.

**Three-fire pattern (immediate + 500ms + 1500ms):** The AgGrid iframe may
not be fully loaded when `components.html` first fires. Three calls cover:
initial load, post-CSS-parse, and post-Streamlit-rerun iframe recreation.

**Precedent:** `ui/pages/explore_stories.py` Table view render path
(`3a5e1bc`, `6590450` — June 2026).

---

## Testing Strategy

### BDD/E2E Tests (Explore Stories)

**Location:** `tests/bdd/`
**Framework:** pytest-bdd + Playwright
**Runtime:** ~25 minutes (browser session reuse)

```bash
# Run all BDD tests
pytest tests/bdd -v

# Run specific scenario
pytest tests/bdd -k "search_returns_relevant" -v
```

**Coverage (43 scenarios):**
| Category | Scenarios | Status |
|----------|-----------|--------|
| Search flow | 3 | ✅ All passing |
| Filter combinations | 7 | ✅ All passing |
| View switching | 6 | ✅ All passing |
| Story detail/STAR | 4 | ✅ All passing |
| Ask Agy navigation | 4 | ✅ All passing |
| Deeplinks | 3 | ✅ All passing |
| Pagination | 5 | ✅ All passing |
| Navigation/Reset | 5 | ✅ All passing |
| Responsive layout | 3 | ✅ All passing |
| Edge cases | 3 | ✅ All passing |

**Key Test Patterns:**
```python
# Browser session reuse with context isolation
@pytest.fixture(scope="session")
def shared_browser():
    """Reuse browser across all tests for speed."""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()

@pytest.fixture
def browser_page(shared_browser):
    """Fresh context per test for isolation."""
    context = shared_browser.new_context(
        viewport={"width": 1280, "height": 900},
        permissions=["clipboard-read", "clipboard-write"]
    )
    page = context.new_page()
    yield page
    context.close()

# Streamlit-specific waits
def wait_for_streamlit_rerun(page):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(200)  # Allow state sync
```

### RAG Eval Tests

**Location:** `tests/eval/`
**Framework:** pytest + OpenAI embeddings
**Runtime:** ~2-3 minutes

```bash
# Run eval suite
pytest tests/eval/test_eval_rag_quality.py -v
```

**Coverage:** 61 golden queries testing:
- Entity detection (clients, projects, roles)
- Semantic search relevance
- Response quality (no hallucinations)
- Intent classification

**Current Score:** 98.1% (60/61 passing)

### Unit Tests

**Location:** `tests/unit/`
**Framework:** pytest

```bash
pytest tests/unit -v
```

**Coverage:**
- `test_structural_assertions.py` - Threshold boundary tests
- `test_filters.py` - Filter logic
- `test_formatting.py` - STAR story formatting

---

## Mobile Responsiveness

Mobile responsive design is shipped via `ui/styles/mobile_overrides.py` (1,520 lines). Breakpoints: <768px (mobile), 768-1023px (tablet), 1024px+ (desktop). All page components, navigation, chat interface, modals, and grids have mobile-specific overrides. See CHANGELOG.md for the Q1 2026 implementation timeline.

---

## Future Enhancements

See [BACKLOG.md](BACKLOG.md) for current open work.

---

## RAG Pipeline Audit (January 2026)

Comprehensive audit of the RAG (Retrieval-Augmented Generation) pipeline covering data flow, embedding analysis, ranking operations, test coverage, and architecture issues.

### Data Flow Map

**Query → Response Trace (Updated Jan 29, 2026):**

```
User Query
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 1: Rules-Based Rejection (Free)           │
│ - nonsense_filters.jsonl patterns               │
│ - is_nonsense() regex validation                │
└─────────────────────────────────────────────────┘
    ↓ (passed)
┌─────────────────────────────────────────────────┐
│ Layer 2: Semantic Router (Cheap)                │
│ - Embed query with text-embedding-3-small       │
│ - Compare against 106+ intent embeddings        │
│ - 15 families including narrative, synthesis, out_of_scope, personal │
│ - HARD_ACCEPT=0.80, SOFT_ACCEPT=0.40            │
└─────────────────────────────────────────────────┘
    ↓ (accepted, returns intent_family)
┌─────────────────────────────────────────────────┐
│ Layer 3: Fast Exit Checks                       │
│ - out_of_scope: intent_family check → redirect  │
│ - detect_entity(): Client, Employer, Div, Title │
│ - Title = SOFT filter (no Pinecone metadata)    │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 4: Pinecone Vector Search                 │
│ - Query embedding → vector search               │
│ - Entity filter ($or across 6 fields) if hard   │
│ - Title: NO filter (semantic search ranks it)   │
│ - UI filters (industry, domain, role)           │
│ - Returns top 7 candidates                      │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 5: Confidence Gate                        │
│ - HIGH (≥0.25): proceed normally                │
│ - LOW (≥0.20): proceed with warning             │
│ - NONE (<0.20): "I couldn't find..."            │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 6: Post-Retrieval Processing              │
│ STANDARD: entity_pin → diversify_results() → 7 │
│ NARRATIVE: sort by score (skip diversity) → 7   │
│ SYNTHESIS: theme-filter → named-clients-first   │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 7: Context Assembly                       │
│ - XML isolation: <primary_story> tags           │
│ - MATT_DNA ground truth injection               │
│ - Mode-specific prompt selection                │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 8: LLM Generation (OpenAI GPT-4o)         │
│ - Temperature: 0.4 (standard) / 0.2 (synthesis) │
│ - Max tokens: 700                               │
│ - Fact-pairing + texture rules                  │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ Layer 9: Response Formatting                    │
│ - Extract answer + sources                      │
│ - Related Projects display                      │
│ - Meta-commentary cleanup                       │
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

Stories are embedded using `build_embedding_text()` which concatenates:
```python
# Header: [Title] [Theme] in Industry (Sub-category)
header_bits = [f"[{title}]", f"[{theme}]", f"in {industry}", f"({sub_category})"]

# Body sections
parts = [
    f"Summary: {summary_5p}",
    f"Situation: {situation}",  # STAR fields ARE embedded
    f"Task: {task}",
    f"Action: {action}",
    f"Result: {result}",
    f"Process: {process_text}",
    f"Keywords: {tags}",
]
```

**Fields embedded:**
- Title
- Theme, Industry, Sub-category (behavioral context)
- 5PSummary (concise overview)
- STAR fields: Situation, Task, Action, Result (2-3 items each)
- Process (max 3 items)
- public_tags (keywords)

**Fields NOT embedded** (metadata only, used for filtering):
- Client, Employer, Division
- Role, Era

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
  - Pin #1 from Pinecone retrieval (highest semantic relevance)
  - For slots #2+: named clients first, then generic, then duplicates
  - Limiting stories per client (max_per_client param)
  - Skip for narrative mode (trust Pinecone semantic ranking)
  - NO cross-query session state — diversify is deterministic per query
    (removed May 18, 2026 per ADR 019 / MATTGPT-073)
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
- Confidence thresholds: HIGH=0.25, LOW=0.20 (from config/constants.py)

### Test Coverage Analysis

**Eval Framework:** `tests/eval_rag_quality.py` — 98.1% pass rate (60/61 queries across 8 categories, March 2026).

See [Component Contracts → Testing Strategy](#testing-strategy) for the current category breakdown.

**Test File Structure:**
- `tests/test_benchmark_rag.py` - Main eval suite
- `data/borderline_queries.csv` - Edge case query log
- `tests/test_boost_narrative.py` - Narrative boost tests

Test coverage gaps are tracked in [BACKLOG.md](BACKLOG.md) (MATTGPT-040).

### Architecture Issues

Known architectural concerns are tracked in [BACKLOG.md](BACKLOG.md). Current categories:

- **Coupling and complexity** — `backend_service.py` is 2,034 lines with imports from 6+ modules; candidates for extraction (MATTGPT-020)
- **Boundary clarity** — ranking, intent classification, and formatting ownership split across files (MATTGPT-026)
- **Hybrid scoring** — Pinecone scores (0.0–1.0) don't map cleanly to confidence buckets (0.15–0.25) (MATTGPT-024)
- **Error handling** — limited test coverage on error paths; Pinecone timeout and embedding failure lack user notification (MATTGPT-025, MATTGPT-031)

See [BACKLOG.md](BACKLOG.md) detail blocks for fix approaches and status.

### Hardcoded Values Audit

**STATUS UPDATE (Jan 27, 2026):** Centralized in `config/constants.py`

The following constants are now in a single source of truth:

| Category | Constants | Location |
|----------|-----------|----------|
| **Models** | `DEFAULT_CHAT_MODEL`, `DEFAULT_CLASSIFICATION_MODEL`, `DEFAULT_EMBEDDING_MODEL` | config/constants.py |
| **Thresholds** | `HARD_ACCEPT`, `SOFT_ACCEPT`, `CONFIDENCE_HIGH`, `CONFIDENCE_LOW`, `PINECONE_MIN_SIM`, `ENTITY_GATE_THRESHOLD` | config/constants.py |
| **Voice Quality** | `BANNED_PHRASES`, `META_COMMENTARY_PATTERNS`, `META_COMMENTARY_REGEX_PATTERNS` | config/constants.py |
| **Entity Detection** | `ENTITY_DETECTION_FIELDS`, `ENTITY_SEARCH_FIELDS`, `EXCLUDED_DIVISION_VALUES`, `PINECONE_LOWERCASE_FIELDS` | config/constants.py |

Files that import from constants.py:
- `ui/pages/ask_mattgpt/backend_service.py`
- `services/rag_service.py`
- `services/semantic_router.py`
- `services/pinecone_service.py`
- `tests/eval_rag_quality.py`

---

**Remaining items (lower priority):**

**1. Client Names** — ✅ Resolved. Pattern-based via `utils/client_utils.py` using `is_generic_client()`.

**2. Intent Family Keywords**

Hardcoded in semantic_router.py - 15 intent families with ~20 example phrases each.
These should be reviewed quarterly for relevance.

**DEPENDENCY WARNING:** If you modify `VALID_INTENTS`, delete `data/intent_embeddings.json` to regenerate cache.

**3. Sacred Vocabulary (Verbatim Phrases)**

**Location:** `prompts.py` → `get_verbatim_requirement()`
**Mechanism:** Dynamically extracts identity phrases from each story's 5PSummary field at prompt-build time. Not a hardcoded list — phrases come from the data.
**Purpose:** Force LLM to use exact phrases for Professional Narrative stories.

**4. UI Display Strings**

```python
"🐾 I need a quick breather — try again in about 15 seconds!"
"Found {n} relevant stories"
"No strong matches found"
```

**Scattered across:** backend_service.py, conversation_helpers.py

**5. Temperature Settings**

```python
temperature=0.4  # standard mode
temperature=0.2  # synthesis mode
```

**Location:** backend_service.py (line ~945)

**6. Token Limits**

```python
max_tokens=700  # generation (backend_service.py line ~958)
```

**7. Pinecone Index Name**

✅ **RESOLVED:** Index name is now read from `get_conf("PINECONE_INDEX_NAME")` in `pinecone_service.py`. Current value: `matt-portfolio-v2`.

### Summary Findings

**Strengths:**
- Multi-layer gating prevents garbage queries efficiently
- Entity detection adds precision to broad queries
- Mode-specific retrieval (standard/narrative/synthesis) improves relevance
- XML context isolation prevents cross-story bleed
- Dynamic MATT_DNA derived from single source of truth
- Clean prompt architecture in `prompts.py` (BASE_PROMPT + DELTA pattern)
- Structural assertion tests catch meta-commentary and voice drift
- Pattern-based client filtering via `is_generic_client()` (no hardcoded lists)

Known weaknesses and recommended actions are tracked in [BACKLOG.md](BACKLOG.md).

---

