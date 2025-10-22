# Architecture Documentation

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

### Current Architecture (October 21, 2025)
```
llm_portfolio_assistant/
├── app.py                          # Main router (3,234 lines)
│
├── config/
│   ├── __init__.py
│   ├── theme.py                    # Design system constants
│   ├── debug.py                    # Centralized DEBUG flag
│   └── settings.py                 # Configuration helpers
│
├── utils/                          # Shared utilities
│   ├── __init__.py
│   ├── formatting.py               # build_5p_summary, _format_* helpers
│   ├── validation.py               # is_nonsense, token_overlap_ratio
│   ├── scoring.py                  # _keyword_score, _hybrid_score
│   ├── filters.py                  # matches_filters
│   └── ui_helpers.py               # safe_container, render_no_match_banner, dbg
│
├── services/                       # Business logic & external APIs
│   ├── __init__.py
│   ├── pinecone_service.py         # Pinecone client & vector search
│   ├── rag_service.py              # Semantic search orchestration
│   └── story_service.py            # Story retrieval logic
│
├── ui/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── navbar.py               # Top navigation (80 lines)
│   │   └── footer.py               # Footer (60 lines)
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                 # Home page (38 lines)
│   │   ├── explore_stories.py      # Stories browser (1,306 lines)
│   │   ├── ask_mattgpt.py          # RAG interface (1,885 lines)
│   │   ├── about_matt.py           # About page (467 lines)
│   │   ├── banking_landing.py      # Banking landing (14 lines, wraps legacy)
│   │   └── cross_industry_landing.py  # Cross-industry landing (14 lines, wraps legacy)
│   │
│   ├── styles/
│   │   ├── __init__.py
│   │   └── global_styles.py        # Shared CSS overrides
│   │
│   └── legacy_components.py        # Legacy monolith (2,100 lines) - TO BE DELETED
│
├── data/
│   ├── echo_star_stories_nlp.jsonl # Story corpus (115 stories)
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

### Phase 3: Shared Utilities ✅ COMPLETE (October 21, 2025)
- [x] Centralize DEBUG flag to config/debug.py
- [x] Move shared helpers to utils/ (formatting, validation, scoring, filters, ui_helpers)
- [x] Extract Pinecone logic to services/pinecone_service.py
- [x] Extract RAG logic to services/rag_service.py
- [x] Remove ALL duplicate functions across files
- [x] Fix circular import between services
- [x] Delete dead code (_pick_icon, duplicate functions)

**Total impact: 2,931 lines removed through deduplication**

### Phase 4: Final Cleanup 📋 Planned
- [ ] Investigate intermittent state-related filtering in Explore Stories
- [ ] Extract banking_landing_page content from legacy_components (~200 lines)
- [ ] Extract cross_industry_landing_page content from legacy_components (~200 lines)
- [ ] Delete ui/legacy_components.py entirely (2,100 lines)
- [ ] Move css_once() to ui/styles/css_injection.py
- [ ] Add docstrings to all public functions
- [ ] Add type hints consistently
- [ ] Set up pre-commit hooks (black, isort, mypy)

**Expected final app.py size: ~2,800 lines (pure routing + legacy wrappers)**

---

## Refactoring Impact (October 18-21, 2025)

### Quantitative Improvements
- **Code reduction:** 2,931 lines eliminated (-26% total codebase)
- **app.py reduction:** 2,531 lines removed (-44%)
  - Started: 5,765 lines
  - Current: 3,234 lines
- **Duplicate elimination:** 100% (from 20+ duplicates to 0)
- **New modular structure:** 10 new files created
  - 5 utils modules (548 lines)
  - 2 services modules (479 lines)
  - 3 config modules (120 lines)

### Qualitative Improvements
- ✅ No circular dependencies
- ✅ Clear separation of concerns
- ✅ Every function has single source of truth
- ✅ Pages can be modified independently
- ✅ Ready for React migration (1:1 module mapping)
- ✅ Professional architecture for GitHub portfolio

### File Size Summary

**After Phase 3 Completion (October 21, 2025):**
| File/Module | Lines | Change | Status |
|-------------|-------|--------|--------|
| app.py | 3,234 | -2,531 (-44%) | ✅ Duplicates removed |
| explore_stories.py | 1,306 | -854 (-40%) | ✅ Modularized |
| ask_mattgpt.py | 1,885 | -1,055 (-36%) | ✅ Modularized |
| about_matt.py | 467 | - | ✅ Extracted |
| utils/*.py | 548 | +548 (new) | ✅ Shared utilities |
| services/*.py | 479 | +479 (new) | ✅ Business logic |
| config/*.py | 120 | +120 (new) | ✅ Configuration |
| **Total** | **8,469** | **-2,931 (-26%)** | ✅ |

**Key Achievements:**
- Eliminated ALL duplicate functions (was 20+ duplicates)
- Zero circular dependencies
- Clear separation of concerns (pages/utils/services/config)

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

## Future Enhancements

### Short-term (Next 2 weeks)
1. Complete Phase 4 cleanup
2. Add docstrings and type hints
3. Set up pre-commit hooks

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
✅ Systematic refactoring over 3 days prevented regression
✅ Modular structure makes React migration straightforward

### What Was Challenging
❌ Streamlit's CSS specificity is difficult to override
❌ Refactoring took 3 days of focused work
❌ Managing circular dependencies during extraction
❌ Maintaining backward compatibility during transition

### What We'd Do Differently
- Start with component architecture from day 1
- Use React instead of Streamlit for pixel-perfect UI
- Write tests alongside implementation
- Set up linting/formatting from the beginning

---

**Last Updated:** October 21, 2025  
**Author:** Matt Pugmire  
**Review Status:** Ready for technical review