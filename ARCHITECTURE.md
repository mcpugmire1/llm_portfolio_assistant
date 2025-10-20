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
llm_portfolio_assistant/
├── app.py                          # Main router (~3600 lines → target: 200 lines)
├── config/
│   └── theme.py                    # Design system constants
├── ui/
│   ├── components/
│   │   ├── navbar.py               # Navigation bar (scoped CSS)
│   │   ├── footer.py               # Reusable footer
│   │   └── components.py           # Legacy (being phased out)
│   ├── pages/
│   │   ├── home.py                 # Home page render
│   │   ├── banking_landing.py     # Banking landing page
│   │   └── cross_industry_landing.py  # Cross-industry landing
│   └── styles/
│       └── global_styles.py        # Shared CSS (metrics, forms, tables)
└── services/                       # Business logic (future)
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

### Phase 2: Page Extraction 🔄 In Progress
- [x] Create page stubs (home, banking, cross-industry)
- [ ] Extract Explore Stories page
- [ ] Extract Ask MattGPT page
- [ ] Extract About Matt page

### Phase 3: Component Extraction 📋 Planned
- [ ] Extract hero component
- [ ] Extract category cards component
- [ ] Extract filters component
- [ ] Extract table component

### Phase 4: Cleanup 📋 Planned
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

**Last Updated:** October 20, 2025
**Author:** Matt Pugmire
**Review Status:** Ready for technical review
