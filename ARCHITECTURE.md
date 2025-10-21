# Architecture Documentation

## Component-Based Refactoring (October 2025)

### Problem Statement

The original implementation suffered from:
- **Monolithic structure**: 4000+ line `app.py`, 2100+ line `ui/components.py`
- **CSS bleeding**: Broad selectors affected unintended elements across pages
- **Poor maintainability**: Difficult to locate bugs, make isolated changes
- **Unprofessional appearance**: Not suitable for Director/VP-level code review

### Solution: Component-Based Architecture

Refactored to a modular structure with clear separation of concerns:

```
l### Current Architecture (October 21, 2025)
```
llm_portfolio_assistant/
├── app.py                          # Main router (3600 lines → target: <1000 after cleanup)
│
├── config/
│   └── theme.py                    # Design system constants (colors, spacing, typography)
│
├── ui/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── navbar.py               # Top navigation bar with routing (80 lines)
│   │   └── footer.py               # Reusable footer component (60 lines)
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                 # Home page with hero & cards (38 lines)
│   │   ├── explore_stories.py      # Case studies browser with filters (2160 lines)
│   │   ├── ask_mattgpt.py          # Conversational RAG interface (2940 lines)
│   │   ├── about_matt.py           # Professional background & contact (467 lines)
│   │   ├── banking_landing.py      # Banking industry landing (14 lines, wraps legacy)
│   │   └── cross_industry_landing.py  # Cross-industry landing (14 lines, wraps legacy)
│   │
│   ├── styles/
│   │   ├── __init__.py
│   │   └── global_styles.py        # Shared CSS (metrics, forms, tables, AgGrid)
│   │
│   └── legacy_components.py        # Legacy monolith (2100 lines) - TO BE DELETED
│
├── data/
│   ├── echo_star_stories_nlp.jsonl # Story corpus (115 stories)
│   ├── nonsense_filters.jsonl      # Off-domain query rules
│   └── offdomain_queries.csv       # Query telemetry log
│
├── assets/
│   └── (images, SVGs, etc.)
│
└── .streamlit/
    └── config.toml                 # Streamlit theme config
```

---

### Target Architecture (After Phase 3 & 4 Cleanup)
```
llm_portfolio_assistant/
├── app.py                          # Pure router (<1000 lines, ideally <500)
│
├── config/
│   ├── __init__.py
│   ├── theme.py                    # Design system constants
│   └── debug.py                    # DEBUG flag (centralized)
│
├── utils/                          # 🆕 Shared business logic
│   ├── __init__.py
│   ├── search.py                   # semantic_search, pinecone_semantic_search
│   ├── validation.py               # is_nonsense, token_overlap_ratio
│   ├── formatting.py               # build_5p_summary, _format_* helpers
│   ├── filters.py                  # matches_filters, filter logic
│   ├── pinecone_utils.py           # _init_pinecone, _summarize_index_stats
│   ├── config.py                   # get_conf helper
│   └── ui_helpers.py               # safe_container, render_no_match_banner
│
├── ui/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── navbar.py               # Top navigation (~80 lines)
│   │   └── footer.py               # Footer (~60 lines)
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                 # Home page (~200 lines after extraction)
│   │   ├── explore_stories.py      # Stories browser (~1800 lines after utils)
│   │   ├── ask_mattgpt.py          # RAG interface (~2200 lines after utils)
│   │   ├── about_matt.py           # About page (~400 lines)
│   │   ├── banking_landing.py      # Banking page (fully extracted)
│   │   └── cross_industry_landing.py  # Cross-industry page (fully extracted)
│   │
│   └── styles/
│       ├── __init__.py
│       ├── global_styles.py        # Shared Streamlit overrides
│       └── css_injection.py        # 🆕 css_once() helper
│
├── data/
│   ├── echo_star_stories_nlp.jsonl
│   ├── nonsense_filters.jsonl
│   └── offdomain_queries.csv
│
├── assets/
│   └── (images, SVGs, etc.)
│
├── tests/                          # 🆕 Future: Unit & integration tests
│   ├── __init__.py
│   ├── test_search.py
│   ├── test_formatting.py
│   └── test_components.py
│
└── .streamlit/
    └── config.toml
```

---

### File Size Summary

**Current State (After Page Extraction):**
| File/Module | Lines | Status |
|-------------|-------|--------|
| app.py | 3600 | 🔄 Has ~2200 lines of commented code to delete |
| explore_stories.py | 2160 | ✅ Extracted, has duplicate helpers |
| ask_mattgpt.py | 2940 | ✅ Extracted, has duplicate helpers |
| about_matt.py | 467 | ✅ Extracted |
| legacy_components.py | 2100 | ⚠️ To be deleted in Phase 4 |
| **Total** | **11,267** | |

**Target State (After Utils Extraction):**
| File/Module | Lines | Status |
|-------------|-------|--------|
| app.py | <1000 | 🎯 Pure routing only |
| explore_stories.py | ~1500 | 🎯 Imports from utils/ |
| ask_mattgpt.py | ~1800 | 🎯 Imports from utils/ |
| about_matt.py | ~400 | ✅ Minimal changes |
| utils/*.py | ~1200 | 🆕 Shared logic extracted |
| **Total** | **~4900** | **56% reduction** |                  # Business logic (future)
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

### ADR-002: Theme Constants

**Decision:** Centralize colors, typography, spacing in `config/theme.py`.

**Problem:** Hardcoded values scattered across 20+ files:
- `#667eea` appears 47 times
- `padding: 24px` repeated 32 times
- Inconsistent values (sometimes `24px`, sometimes `20px`)

**Solution:**
```python
# config/theme.py
COLORS = {
    "primary_purple": "#8B5CF6",
    "dark_navy": "#2c3e50",
}

SPACING = {
    "card_padding": "24px",
}

# Usage in components
from config.theme import COLORS, SPACING

st.markdown(f"""
    background: {COLORS['dark_navy']};
    padding: {SPACING['card_padding']};
""")
```

**Benefits:**
- Single source of truth for design system
- Easy to update colors/spacing globally
- Type-safe imports (IDE autocomplete)

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

### Phase 1: Infrastructure ✅ Complete
- [x] Create directory structure
- [x] Extract `theme.py` constants
- [x] Create `global_styles.py`
- [x] Extract `navbar.py` component
- [x] Extract `footer.py` component

### Phase 2: Page Extraction ✅ COMPLETE (October 21, 2025)
- [x] Extract Explore Stories page (2160 lines)
- [x] Extract Ask MattGPT page (2940 lines)
- [x] Extract About Matt page (467 lines)
- [x] Create landing page stubs (28 lines)

**Total extracted: 5633 lines**

### Phase 3: Cleanup 🔄 Next
- [ ] Delete commented old code from app.py (~2200 lines)
- [ ] Centralize DEBUG flag to config/debug.py
- [ ] Move css_once to ui/styles/css_injection.py  
- [ ] Move shared helpers to utils/ (semantic_search, etc.)
- [ ] Investigate potential state-related filtering issues in Explore Stories (intermittent, needs reproduction)



### Phase 4: Cleanup 📋 Planned
- [ ] Extract banking_landing_page from legacy_components
- [ ] Extract cross_industry_landing_page from legacy_components
- [ ] Remove `ui/components.py` legacy file
- [ ] Reduce `app.py` to pure routing (<200 lines)
- [ ] Add docstrings to all modules
- [ ] Add type hints

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

## File Size Targets

| File | Current | Target | Status |
|------|---------|--------|--------|
| `app.py` | 3600 lines | 200 lines | 🔄 In Progress |
| `ui/components.py` | 2100 lines | 0 lines (delete) | 📋 Planned |
| `navbar.py` | 80 lines | 80 lines | ✅ Complete |
| `footer.py` | 60 lines | 60 lines | ✅ Complete |
| `home.py` | 30 lines | 200 lines | 🔄 Stub |

**Rule:** No file exceeds 300 lines.

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

## Future Enhancements

### Short-term (Next 2 weeks)
1. Complete page extraction
2. Delete `ui/components.py` legacy file
3. Add docstrings and type hints

### Medium-term (Next month)
4. Add unit tests for components
5. Implement proper error boundaries
6. Add logging and observability

### Long-term (3-6 months)
7. Migrate to Next.js + React
8. Replace Streamlit with FastAPI backend
9. Add proper state management (Redux/Zustand)

---

## Lessons Learned

### What Worked Well
✅ Component isolation fixed CSS bleeding immediately
✅ Theme constants made color updates trivial
✅ Clear file structure makes code reviews easier
✅ Shows engineering maturity to hiring managers

### What Was Challenging
❌ Streamlit's CSS specificity is difficult to override
❌ Refactoring takes time (2-3 hours)
❌ Need to maintain backward compatibility during transition

### What We'd Do Differently
- Start with component architecture from day 1
- Use React instead of Streamlit for pixel-perfect UI
- Write tests alongside implementation

---

**Last Updated:** October 21, 2025
**Author:** Matt Pugmire
**Review Status:** Ready for technical review
