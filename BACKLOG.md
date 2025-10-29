# MattGPT Streamlit App - Product Backlog

**Sprint Goal:** Phase 4 Complete - UI Polish & Wireframe Alignment ✅

**Last Updated:** October 28, 2025

---

## 🟢 DONE

### ✅ Homepage Redesign
**Status:** Complete
**Completed:** Oct 19, 2024

- [x] Purple gradient hero section with logo
- [x] Stats bar with grid layout (4 columns)
- [x] 6 category cards (2 industry gradient, 4 capability white, 1 quick question gradient)
- [x] Dark top navigation bar
- [x] Footer with contact links

**Reference:** `/wireframes/homepage_wireframe.html`
**Files:** `ui/legacy_components.py`, `ui/components/category_cards.py`

---

### ✅ Banking Landing Page
**Status:** Complete
**Completed:** Oct 28, 2025 (Rewritten with purple theme)

- [x] Header with title and project count
- [x] Purple gradient hero section matching home page
- [x] Stats section (47 projects, 16 capabilities, 6 clients)
- [x] Client pills horizontal layout (6 clients)
- [x] 15 capability cards in 3-column responsive grid
- [x] Purple button theme with varied text
- [x] Purple "Ask Agy" CTA button gradient
- [x] Purple footer email button

**Reference:** `/wireframes/banking_landing_page.html`
**Files:** `ui/pages/banking_landing.py` (complete rewrite, 413 lines)

---

### ✅ Cross-Industry Landing Page
**Status:** Complete
**Completed:** Oct 28, 2025 (Rewritten with purple theme)

- [x] Header with title and project count
- [x] Purple gradient hero section matching home page
- [x] Stats section (53 projects, 11 capabilities, 4 client groups)
- [x] Industry pills horizontal layout (8 industries)
- [x] 11 capability cards in 3-column responsive grid
- [x] Purple button theme with varied text
- [x] Purple "Ask Agy" CTA button gradient
- [x] Purple footer email button

**Reference:** `/wireframes/cross_industry_landing_page.html`
**Files:** `ui/pages/cross_industry_landing.py` (complete rewrite, 413 lines)

---

### ✅ Button Styling Unification (ADR 015)
**Status:** Complete
**Completed:** Oct 28, 2025

- [x] Implement purple theme (#8B5CF6) across all pages
- [x] Solve Streamlit emotion-cache CSS override issue
- [x] Create JavaScript workaround for button styling
- [x] Add varied button text (not all "View Projects →")
- [x] Unify button padding and hover states
- [x] Purple footer email button across all pages
- [x] "Ask Agy" purple gradient CTA buttons

**Technical Solution:** JavaScript injection via `streamlit.components.v1.html()` with inline styles
**Files:**
- `ui/legacy_components.py:1046-1094` (home page)
- `ui/pages/explore_stories.py:1378-1423` (card buttons)
- `ui/pages/banking_landing.py`, `ui/pages/cross_industry_landing.py`

**Reference:** ADR 015 in `docs/ADR.md`

---

### ✅ Explore Stories - Filter UI Redesign
**Status:** Complete
**Completed:** Oct 28, 2025

- [x] Progressive disclosure pattern (primary + advanced filters)
- [x] Industry and Capability filters (primary, always visible)
- [x] Advanced filters collapsed by default (Client, Role, Domain)
- [x] Pre-filtered navigation from landing pages
- [x] Filter chips with removal functionality
- [x] Purple accent colors throughout
- [x] Data layer refactored to use raw JSONL fields (Title-case)

**Reference:** `EXPLORE_STORIES_UX_REDESIGN.md`
**Files:** `ui/pages/explore_stories.py`, `utils/filters.py`, `app.py`

---

### ✅ Explore Stories - Detail Panel Redesign
**Status:** Complete
**Completed:** Oct 28, 2025

- [x] Match explore_stories_table_wireframe.html specification
- [x] Full STAR narrative display (Situation, Task, Action, Result)
- [x] Sidebar with tech tags, competencies, metrics
- [x] 100% JSONL-sourced data (zero fabrication verified)
- [x] Header with metadata icons (🏢 🎯 📅 🏷️)
- [x] "Ask Agy About This" CTA button
- [x] Two-column responsive layout

**Files:** `ui/pages/explore_stories.py:329-520`

---

## 🔴 HIGH PRIORITY (Job Search Critical)

### ✅ Fix Navigation Bar Disappearing Issue
**Story ID:** MATTGPT-001
**Status:** Complete
**Completed:** Oct 2025

**User Story:**
As a user navigating the app, I want a consistent dark navbar across all pages so that I can easily move between sections.

**Acceptance Criteria:**
- [x] Dark navbar visible on all pages (Home, Banking, Cross-Industry, Explore Stories, Ask MattGPT, About Matt)
- [x] Navigation buttons: Home, Explore Stories, Ask MattGPT, About Matt
- [x] White text with hover states
- [x] No emoji icons in nav labels
- [x] Fix doesn't break other pages

**Reference:** `ui/components/navbar.py`

---

### 2. Explore Stories - Filter UI Redesign
**Story ID:** MATTGPT-002
**Priority:** HIGH

**User Story:**
As a recruiter exploring Matt's portfolio, I want to filter projects by industry, capability, client, and role so that I can find relevant experience quickly.

**Acceptance Criteria:**
- [ ] 4 filter dropdowns in horizontal layout (Industry, Capability, Client, Role)
- [ ] Search bar on right side
- [ ] View switcher: Cards / Table / Timeline
- [ ] Filters match wireframe styling (dark background #2a2a2a, compact layout)
- [ ] Purple accent color for selected filters
- [ ] Responsive on mobile (stack vertically)

**Reference:** `/wireframes/explore_stories_cards_wireframe.html`
**Files to Update:** `app.py:3619-4783` (Explore Stories section)

**Design Notes:**
- Current implementation is too tall/spacious
- Need compact filter bar like wireframe
- Match purple accent color (#667eea)

---

### 3. Explore Stories - Card View
**Story ID:** MATTGPT-003
**Priority:** HIGH

**User Story:**
As a recruiter, I want to see projects as cards in a grid so that I can quickly scan titles, clients, and capabilities.

**Acceptance Criteria:**
- [ ] 3-column grid of project cards
- [ ] Each card shows: Client logo/icon, Project title, Capability tags, Client name, Short description
- [ ] White background cards with subtle border
- [ ] Purple hover effect (border + shadow)
- [ ] "View Details" button on each card
- [ ] Responsive: 2 columns on tablet, 1 on mobile

**Reference:** `/wireframes/explore_stories_cards_wireframe.html`
**Files to Update:** `app.py` (Explore Stories card rendering)

---

### 4. Explore Stories - Table View
**Story ID:** MATTGPT-004
**Priority:** MEDIUM

**User Story:**
As a recruiter, I want to see projects in a sortable table so that I can compare details side-by-side.

**Acceptance Criteria:**
- [ ] Table columns: Client, Project, Capability, Role, Year, Duration
- [ ] Sortable by clicking column headers
- [ ] Purple header row (#667eea)
- [ ] Zebra striping on rows (alternating light gray)
- [ ] Hover effect on rows
- [ ] Responsive: horizontal scroll on mobile

**Reference:** `/wireframes/explore_stories_table_wireframe.html`

---

### 5. Explore Stories - Timeline View
**Story ID:** MATTGPT-005
**Priority:** LOW (nice-to-have)

**User Story:**
As a recruiter, I want to see projects in chronological order so that I can understand Matt's career progression.

**Acceptance Criteria:**
- [ ] Vertical timeline with year markers
- [ ] Projects grouped by year
- [ ] Purple timeline line connecting projects
- [ ] Project cards on alternating sides (left/right)
- [ ] Responsive: single column on mobile

**Reference:** `/wireframes/explore_stories_timeline_wireframe.html`

---

## 🟡 MEDIUM PRIORITY

### 6. Ask MattGPT Page Styling
**Story ID:** MATTGPT-006
**Priority:** MEDIUM

**User Story:**
As a user, I want a clean chat interface to ask Agy questions about Matt's experience.

**Acceptance Criteria:**
- [ ] Header: "Ask Agy 🐾" with subtitle
- [ ] Starter question suggestions (purple gradient cards)
- [ ] Chat interface with Agy avatar
- [ ] Message bubbles: User (right, purple), Agy (left, gray)
- [ ] Input box at bottom with send button
- [ ] Footer matching homepage

**Reference:** `/wireframes/ask_mattgpt_landing_wireframe.html`
**Files to Update:** `app.py:4784-5337` (Ask MattGPT section)

---

### 7. About Matt Page Styling
**Story ID:** MATTGPT-007
**Priority:** MEDIUM

**User Story:**
As a recruiter, I want to learn about Matt's background, skills, and career journey in a visually appealing format.

**Acceptance Criteria:**
- [ ] Hero section with headshot and bio summary
- [ ] Skills section with purple gradient tags
- [ ] Career timeline (optional visual timeline)
- [ ] Education and certifications
- [ ] Contact CTA matching homepage footer
- [ ] Responsive layout

**Reference:** `/wireframes/about_matt_wireframe.html`
**Files to Update:** `app.py:5338-end` (About Matt section)

---

## ⚪ LOW PRIORITY (Future Enhancements)

### 8. Mobile Optimization Testing
**Story ID:** MATTGPT-008
**Priority:** LOW

**User Story:**
As a mobile user, I want all pages to render correctly on my phone so that I can explore Matt's portfolio on any device.

**Acceptance Criteria:**
- [ ] Test all pages on iPhone/Android
- [ ] Navigation works on mobile (no sidebar)
- [ ] Cards stack vertically on narrow screens
- [ ] Text remains readable (no tiny fonts)
- [ ] Buttons are tappable (min 44px height)

---

### 9. Footer Link Functionality
**Story ID:** MATTGPT-009
**Priority:** LOW

**User Story:**
As a user, I want footer links to navigate properly so that I can easily contact Matt or ask Agy questions.

**Current Issue:**
- "Ask Agy" link in footer uses `#ask` anchor (doesn't navigate)
- Should switch to "Ask MattGPT" tab

**Acceptance Criteria:**
- [ ] Email link opens mail client (already working)
- [ ] LinkedIn link opens in new tab (already working)
- [ ] "Ask Agy" button switches to Ask MattGPT tab and focuses input

**Files to Update:** `ui/components.py` (footer HTML in multiple functions)

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

---

## 📋 Backlog Notes

### Design System Reference
- **Primary Purple:** `#667eea`
- **Secondary Purple:** `#764ba2`
- **Gradient:** `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Dark Navbar:** `#2c3e50`
- **Border Gray:** `#e0e0e0`
- **Text Gray:** `#7f8c8d`

### Wireframe Files Location
`/Users/matthewpugmire/Projects/portfolio/mattgpt-design-spec/wireframes/`

### Migration to Jira
When ready to move this to Jira:
1. Import as Epic: "Streamlit Wireframe Alignment"
2. Create stories with Story IDs (MATTGPT-001, etc.)
3. Add acceptance criteria as subtasks
4. Link wireframe files in story descriptions
5. Track in sprint board

---

**Next Session Prompt Template:**
```
Work on Story: [Story ID] - [Title]

Reference: [Wireframe file path]

Requirements:
- [Copy acceptance criteria]

Match styling from: [Existing component reference]
```
