# Explore Stories UX Redesign
**Date:** 2025-10-28
**Status:** Design Phase - Pending Implementation

## Context

### Problem Statement
Current Explore Stories filters are not aligned with the data model:
- Some filters are empty (Audience, Tags)
- "Domain" uses synthetic field combining Category + Sub-category
- "Solution / Offering" (capability) is not filterable, but it's what landing pages need to link to
- Filter layout is cluttered with non-functional dropdowns

### User Journey
```
Home → Landing Page (Banking/Cross-Industry) → Explore Stories → Ask MattGPT
         ↓                                           ↓               ↓
      Overview/Viz                              Faceted Browse    Conversational
      "47 projects"                             Filter & scan     Deep questions
```

Landing pages provide **data visualization** to show the big picture. Explore Stories provides **faceted browsing** to drill into specific project subsets.

---

## Proposed Filter Design

### Primary Filters (Always Visible)
```
┌────────────────────────────────────────────────────────────────────┐
│  [Search keywords...                ] [Industry ▼] [Capability ▼] │
│                                                                     │
│  ▸ Advanced Filters                                      [Reset]   │
└────────────────────────────────────────────────────────────────────┘
```

### Advanced Filters (Collapsed by Default)
```
┌────────────────────────────────────────────────────────────────────┐
│  [Search keywords...                ] [Industry ▼] [Capability ▼] │
│                                                                     │
│  ▾ Advanced Filters                                      [Reset]   │
│    [Client ▼] [Role ▼] [Domain ▼]                                 │
└────────────────────────────────────────────────────────────────────┘
```

---

## Filter Specifications

### Primary Filters

#### 1. Search Keywords (Text Input)
- **Field mapping:** Token-based search across multiple fields
- **Behavior:**
  - Semantic search via Pinecone when query entered
  - Combined with facet filters
  - Off-domain detection and relevance scoring
  - Fallback to keyword matching
- **Placeholder:** "Search by title, client, or keywords..."
- **Keep existing logic:** No changes to search implementation

#### 2. Industry (Dropdown)
- **Field mapping:** `Industry` field from JSONL
- **Data source:** `sorted({s.get("Industry") for s in stories if s.get("Industry")})`
- **Options:**
  - Financial Services / Banking
  - Cross Industry
  - Healthcare / Life Sciences
  - Technology & Software
  - Telecommunications
  - Transportation & Logistics
- **Default:** "All" (no filter)
- **NEW:** This filter doesn't currently exist

#### 3. Capability (Dropdown)
- **Field mapping:** `Solution / Offering` field from JSONL
- **Data source:** `sorted({s.get("Solution / Offering") for s in stories if s.get("Solution / Offering")})`
- **Options:** 29 capabilities including:
  - Agile Transformation & Delivery
  - Modern Engineering Practices & Solutions
  - Technology Strategy & Advisory
  - Global Payments & Treasury Solutions
  - etc.
- **Default:** "All" (no filter)
- **NEW:** This is the critical filter for landing page integration

### Advanced Filters (Collapsed)

#### 4. Client (Multiselect)
- **Field mapping:** `Client` field from JSONL
- **Data source:** `sorted({s.get("Client") for s in stories if s.get("Client")})`
- **Options:** 16 clients (JP Morgan Chase, RBC, Accenture, etc.)
- **KEEP:** Existing implementation, just move to advanced section

#### 5. Role (Multiselect)
- **Field mapping:** `Role` field from JSONL
- **Data source:** `sorted({s.get("Role") for s in stories if s.get("Role")})`
- **Options:** 13 roles (Director, Architect, etc.)
- **KEEP:** Existing implementation, just move to advanced section

#### 6. Domain (Multiselect)
- **Field mapping:** `Sub-category` field from JSONL (formerly synthetic "domain")
- **Data source:** `sorted({s.get("Sub-category") for s in stories if s.get("Sub-category")})`
- **Options:** Sub-categories like "Application Modernization", "Security & Compliance Solutions", etc.
- **UPDATE:** Change to use Sub-category directly instead of synthetic Category / Sub-category
- **Note:** Remove the "Domain Category" parent dropdown - no longer needed

---

## Filter Removal

**Remove these filters entirely:**
- ❌ **Audience** - personas field is empty (killed in previous iteration)
- ❌ **Domain Category** - Too generic, redundant with Capability filter
- ❌ **Tags** - Empty field in data

---

## Data Model Changes

### Current (Synthetic Field)
```python
# app.py load_star_stories()
cat = raw.get("Category")
subcat = raw.get("Sub-category")
domain = " / ".join([cat, subcat])  # Synthetic field
```

### Proposed (Dumb Loader)
```python
# app.py load_star_stories() - just preserve raw JSONL fields
story = {
    "id": raw.get("id"),
    "Title": raw.get("Title"),
    "Client": raw.get("Client"),
    "Role": raw.get("Role"),
    "Industry": raw.get("Industry"),
    "Solution / Offering": raw.get("Solution / Offering"),
    "Category": raw.get("Category"),
    "Sub-category": raw.get("Sub-category"),
    # ... all other fields as-is
}
```

**Principle:** Loader should be "dumb" - no business logic, no transformation, no synthetic fields. Just load what's in JSONL.

---

## Landing Page Integration

### Banking Landing Page Example

**Current behavior:**
- Click "View Projects →" under "Agile Transformation & Delivery (8 projects)"
- Navigates to Explore Stories with NO filters

**New behavior:**
```python
# ui/pages/banking_landing.py button handler
if st.button("View Projects →", key=f"banking_agile"):
    st.session_state["prefilter_industry"] = "Financial Services / Banking"
    st.session_state["prefilter_capability"] = "Agile Transformation & Delivery"
    st.session_state["active_tab"] = "Explore Stories"
    st.rerun()
```

**Explore Stories reads pre-filters:**
```python
# ui/pages/explore_stories.py - initialize filters
F = st.session_state.get("filters", {}) or {}

# Apply pre-filters from landing pages
if "prefilter_industry" in st.session_state:
    F["industry"] = st.session_state.pop("prefilter_industry")
if "prefilter_capability" in st.session_state:
    F["capability"] = st.session_state.pop("prefilter_capability")
```

**Result:** Shows exactly 8 Banking + Agile Transformation projects, with visible filter chips showing what's filtered.

---

## Filter Chips (Active Filters Display)

**Current implementation:** Works well, keep as-is

**Add support for new filters:**
```python
# Render filter chips for Industry and Capability
for label, key in [
    ("Industry", "industry"),
    ("Capability", "capability"),
    ("Client", "clients"),
    ("Role", "roles"),
    ("Domain", "domains"),
]:
    for v in filters.get(key, []):
        chips.append((label, v, (key, v)))
```

Users can click X to remove any filter, including pre-applied ones from landing pages.

---

## Implementation Checklist

### Phase 1: Data Layer
- [ ] Refactor `load_star_stories()` to be dumb loader (preserve all JSONL fields)
- [ ] Update all consumers to use raw field names (Title-case)
- [ ] Remove synthetic "domain" field creation
- [ ] Test that all 119 stories load correctly

### Phase 2: Filter Logic
- [ ] Update `utils/filters.py` `matches_filters()` to support:
  - `Industry` field filtering
  - `Solution / Offering` field filtering (as "capability")
  - `Sub-category` field filtering (as "domain")
- [ ] Remove references to synthetic "domain" field
- [ ] Test filtering logic with new field names

### Phase 3: Explore Stories UI
- [ ] Remove Audience, Domain Category, Tags filters
- [ ] Add Industry dropdown (primary)
- [ ] Add Capability dropdown (primary)
- [ ] Move Client, Role to Advanced section
- [ ] Update Domain to use Sub-category
- [ ] Add collapsible "Advanced Filters" section
- [ ] Update filter initialization to read pre-filters from session state
- [ ] Test filter UI and interactions

### Phase 4: Landing Page Integration
- [ ] Update Banking landing page button handlers to set pre-filters
- [ ] Update Cross-Industry landing page button handlers to set pre-filters
- [ ] Test full flow: Landing → Filtered Explore Stories
- [ ] Verify filter chips show correctly
- [ ] Verify counts match (8 Agile projects, 7 Payments projects, etc.)

### Phase 5: Other Pages
- [ ] Update `ask_mattgpt.py` references to "domain" field
- [ ] Update `utils/scoring.py` references to "domain" field
- [ ] Update `services/pinecone_service.py` if needed
- [ ] Test semantic search still works
- [ ] Test Ask MattGPT context building

---

## Testing Plan

### Test Cases

**TC1: Direct Navigation to Explore Stories**
- Navigate directly to Explore Stories (no pre-filters)
- All filters should be empty/default
- Should show all 119 projects
- Can manually select Industry, Capability, etc.

**TC2: Banking Landing → Agile Transformation**
- Click "Agile Transformation & Delivery (8)" on Banking landing
- Should show exactly 8 projects
- Filter chips should show: "✕ Financial Services / Banking" and "✕ Agile Transformation & Delivery"
- Can remove filters to broaden results

**TC3: Cross-Industry Landing → Modern Engineering**
- Click "Modern Engineering Practices & Solutions (26)" on Cross-Industry landing
- Should show exactly 26 projects
- Industry pre-filter should allow multiple (or use "Cross Industry" value)

**TC4: Search + Filters**
- Pre-filter from landing page
- Enter search query "mobile app"
- Should combine semantic search with facet filters
- Results should match both search terms AND filters

**TC5: Advanced Filters**
- Pre-filter from landing page
- Expand Advanced Filters
- Add Client filter (e.g., "JP Morgan Chase")
- Should further narrow results

**TC6: Filter Chips**
- Apply multiple filters
- Click X on each chip
- Filters should be removed one by one
- UI should update correctly

---

## UI/UX Rationale

### Why This Design?

**Primary Filters (Industry, Capability):**
- Match the landing page structure (Banking = Industry, Agile = Capability)
- Answer the recruiter question: "What type of work in what industry?"
- Support the browse → drill-down flow
- Always visible = no hunting for key filters

**Advanced Filters (Client, Role, Domain):**
- Power user features for deeper slicing
- Not needed for 90% of use cases
- Reduce visual clutter by hiding initially
- Still accessible via one click

**Collapsed by Default:**
- Landing page pre-filtering only needs Industry + Capability
- Keeps UI clean and focused
- Progressive disclosure pattern (show complexity when needed)

**Filter Chips Always Visible:**
- Regardless of collapse state, active filters are always shown as chips
- Users always know what's filtered
- Can remove filters without expanding sections

---

## Visual Hierarchy

```
High-level strategic filters
↓
[Search] [Industry] [Capability]
    ↓
    More tactical/specific filters
    ↓
    ▸ Advanced: [Client] [Role] [Domain]
```

This matches how recruiters think:
1. What industry? (Banking, Healthcare, etc.)
2. What capability? (Agile, DevOps, Strategy, etc.)
3. Any specific client or role? (Advanced)

---

## Next Steps

1. **Review this design doc** - Get alignment on approach
2. **Create wireframes/mockups** (if needed for visual reference)
3. **Begin implementation** following the checklist above
4. **Test thoroughly** at each phase
5. **Update ARCHITECTURE.md** when complete

---

## Open Questions

- [ ] Should Industry be single-select or multi-select?
- [ ] Should Capability be single-select or multi-select?
- [ ] Do we need a "Domain Category" concept anymore? (Proposed: No)
- [ ] Should Advanced Filters remember collapsed/expanded state in session?
- [ ] What happens if someone navigates to Explore Stories from Ask MattGPT with a story context? (Keep existing behavior)

---

## Related Documents

- [ARCHITECTURE.md](ARCHITECTURE.md) - Phase 3 completion, Phase 4 planning
- [SESSION_HANDOFF.md](SESSION_HANDOFF.md) - Current session context and decisions
