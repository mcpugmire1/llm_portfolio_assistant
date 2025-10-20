# LLM Portfolio Assistant - Current Project Context

**Last Updated:** October 19, 2024 (Evening)
**Session Status:** 🟢 Banking & Cross-Industry landing pages complete - Ready for testing

---

## What This Project Is

**MattGPT Live Application** - The working Streamlit app that powers the AI-powered portfolio experience.

**Live App:** https://askmattgpt.streamlit.app
**Related Design Spec:** https://mcpugmire1.github.io/mattgpt-design-spec/

---

## Current State (What's Done)

### ✅ Streamlit App Styling Overhaul (COMPLETED - October 19, 2024)

**What was completed:**

1. **Navigation Redesign**
   - Removed sidebar navigation (negative mobile experience)
   - Switched to dark top button navigation matching wireframes
   - Files: `app.py:311, 433, 556-599`
   - Changes:
     - `USE_SIDEBAR_NAV = False`
     - `initial_sidebar_state="collapsed"`
     - Dark navbar (#2c3e50) with white text buttons
     - Hidden Streamlit default header and menu
     - Removed emoji icons from navigation labels

2. **Purple Gradient Brand Identity Applied**
   - Complete visual refresh to match wireframe specifications
   - Hero section: Full gradient background (`#667eea` → `#764ba2`)
   - Stats bar: Grid-with-borders layout (wireframe style)
   - Category cards: All 6 cards with gradient backgrounds
   - Buttons: White with purple text, gradient hover effects

3. **CSS Overhaul**
   - File: `ui/components.py`
   - Expanded from 725 → 1219 lines (+494 lines)
   - Replaced all blue (#4a90e2) with purple (#667eea)
   - Added comprehensive component styling:
     - Badges, pills, alerts
     - Form elements
     - Chat messages
     - Cards and buttons
     - Typography improvements

4. **Environment Fixed**
   - Virtual environment recreated after folder move
   - Location: `/Users/matthewpugmire/Projects/portfolio/llm_portfolio_assistant/venv`
   - All dependencies reinstalled from `requirements.txt`
   - Verified working: `venv/bin/streamlit run app.py`

**Status:** ✅ All styling complete, navigation cleaned up and aligned to wireframe - ready for testing

### ✅ Banking & Cross-Industry Landing Pages (COMPLETED - October 19, 2024 Evening)

**What was completed:**

1. **Created Banking Landing Page**
   - File: `ui/components.py:981-1213`
   - Function: `render_banking_landing_page()`
   - Header with "Financial Services / Banking" title
   - 6 client pills in horizontal layout (JPMorgan Chase, RBC, Fiserv, etc.)
   - 16 capability cards in 3-column responsive grid
   - White card backgrounds with purple accents (#667eea)
   - Purple hover effects on cards and pills
   - "Ask Agy 🐾" CTA button
   - Footer matching homepage

2. **Created Cross-Industry Landing Page**
   - File: `ui/components.py:1215-1448`
   - Function: `render_cross_industry_landing_page()`
   - Header with "Cross-Industry Transformation" title
   - 8 industry pills in horizontal layout
   - 15 capability cards in 3-column responsive grid
   - Same styling as Banking page (white cards, purple accents)
   - "Ask Agy 🐾" CTA button
   - Footer matching homepage

3. **Updated App Navigation**
   - File: `app.py:12-18` - Added imports for new landing page functions
   - File: `app.py:3612-3621` - Added routing for "Banking" and "Cross-Industry" tabs
   - Updated homepage card buttons to navigate to new landing pages:
     - "See Banking Projects →" → Banking tab (ui/components.py:820)
     - "Browse Transformations →" → Cross-Industry tab (ui/components.py:841)

4. **Fixed Streamlit CSS Issues**
   - Built complete HTML strings before rendering (prevents layout breaking)
   - Used CSS Grid for 3-column card layout: `grid-template-columns: repeat(3, 1fr)`
   - Responsive breakpoints: 2 columns at 1200px, 1 column at 768px
   - Pills render horizontally using `display: flex; flex-wrap: wrap`

**Status:** ✅ Both landing pages complete, matching wireframe specifications - ready for testing

**Known Issue:** Dark navbar still disappears intermittently (user deprioritized - will address later)

---

## Project Structure

```
llm_portfolio_assistant/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── venv/                          # Virtual environment
├── ui/
│   └── components.py              # CSS styling + UI components (1219 lines)
├── data/
│   └── [portfolio data files]
├── assets/
│   ├── full_logo_horizontal.png  # Brand assets (copied from design spec)
│   ├── logo_head_512.png
│   └── agy_avatar_128_dark.png
├── CONTEXT.md                     # This file - project status
└── STYLING-UPDATES.md            # Detailed changelog of styling work
```

---

## Key Files

### `/app.py`
**Purpose:** Main Streamlit application entry point

**Key Settings:**
- Line 311: `initial_sidebar_state="collapsed"` - Better mobile UX
- Line 433: `USE_SIDEBAR_NAV = False` - Top button navigation

### `/ui/components.py`
**Purpose:** All CSS styling and UI component rendering functions

**Size:** 1219 lines (was 725, added 494 lines of CSS)

**Key Sections:**
- Lines 24-157: Hero section CSS (gradient background, white text)
- Lines 336-387: Button styling (white buttons, purple text, gradient hover)
- Lines 980-1030: Stats bar CSS (grid layout, no cards)
- Lines 1112-1145: Category card CSS (gradient backgrounds)
- Lines 945-1262: Homepage rendering function

### `/requirements.txt`
**Purpose:** Python dependencies

**Key Packages:**
- streamlit
- langchain>=0.1.17
- openai
- faiss-cpu
- sentence-transformers==4.1.0
- pinecone
- streamlit-option-menu

### `/assets/`
**Purpose:** Brand assets copied from design spec project

**Files:**
- `full_logo_horizontal.png` (232KB)
- `logo_head_512.png` (105KB)
- `agy_avatar_128_dark.png` (12KB)

---

## Color Palette

**Primary Gradient:**
```css
linear-gradient(135deg, #667eea 0%, #764ba2 100%)
```

**Colors:**
- Primary Purple: `#667eea`
- Secondary Purple: `#764ba2`
- White: `#ffffff`
- Border Gray: `#e0e0e0`
- Text Gray: `#888888`

---

## How to Run

### Setup (First Time)
```bash
cd /Users/matthewpugmire/Projects/portfolio/llm_portfolio_assistant
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Run App
```bash
# Option 1: Activate venv first
source venv/bin/activate
streamlit run app.py

# Option 2: Run directly
venv/bin/streamlit run app.py
```

**Default URL:** http://localhost:8501

---

## Known Issues

### Issue 1: Virtual Environment Corruption (RESOLVED - October 19)
- **Problem:** After moving project from `/Downloads` to `/Projects/portfolio/`, venv was broken
- **Root Cause:** Hardcoded paths in venv activation scripts
- **Solution:** Recreated venv completely with `python3 -m venv venv`
- **Status:** Fixed, all dependencies reinstalled

### Issue 2: Nested Directory Confusion (RESOLVED - October 19)
- **Problem:** Empty nested `llm_portfolio_assistant/llm_portfolio_assistant/` folder
- **Root Cause:** Unknown (possibly accidental folder creation)
- **Solution:** User removed nested folder manually
- **Status:** Fixed, project structure clean

---

## Next Steps (Immediate)

1. **Test Landing Pages**
   - Refresh app at http://localhost:8501
   - Click "See Banking Projects →" from homepage
   - Verify Banking page: client pills horizontal, 3-column card grid, purple accents
   - Click "Browse Transformations →" from homepage
   - Verify Cross-Industry page: industry pills horizontal, 3-column card grid
   - Test "Ask Agy 🐾" buttons navigate to Ask MattGPT tab
   - Check footer renders correctly (no raw HTML)

2. **Next Story to Work On**
   - See `BACKLOG.md` for prioritized user stories
   - HIGH PRIORITY: MATTGPT-002 - Explore Stories Filter UI
   - Reference wireframe: `/Users/matthewpugmire/Projects/portfolio/mattgpt-design-spec/wireframes/explore_stories_cards_wireframe.html`

3. **Deploy to Streamlit Cloud** (when ready)
   - Push changes to GitHub
   - Trigger redeployment on Streamlit Cloud
   - Update live app at https://askmattgpt.streamlit.app

4. **Mobile testing** (lower priority)
   - Test responsive design on actual mobile device
   - Verify top button navigation works well
   - Check gradient backgrounds on mobile

---

## Next Steps (Later)

1. **Content updates** (if needed)
   - Review AI system prompt
   - Update "About Matt" content
   - Refresh project data

2. **Performance optimization**
   - Profile load times
   - Optimize vector search
   - Cache improvements

3. **Feature additions** (future)
   - Advanced filtering
   - Export functionality
   - Analytics tracking

---

## Related Projects

**Design Spec Project:**
- Location: `/Users/matthewpugmire/Projects/portfolio/mattgpt-design-spec`
- Purpose: Complete product blueprint, wireframes, architecture docs
- Site: https://mcpugmire1.github.io/mattgpt-design-spec/

**Relationship:**
- Design spec = "What to build" (wireframes, specifications)
- This project = "Working implementation" (live Streamlit app)

---

## How to Resume After Context Loss

**If Claude Code crashes or new session starts:**

1. **Read this file first** (`CONTEXT.md`) - Current project state
2. **Check git log** for recent changes:
   ```bash
   git log --oneline -10
   ```
3. **Review styling details** in `STYLING-UPDATES.md`
4. **Ask Matt:** "What are you working on right now?"
5. **Test current state:** `venv/bin/streamlit run app.py`

---

## Contact / Key Info

- **GitHub Repo:** [Add repo URL when available]
- **Live App:** https://askmattgpt.streamlit.app
- **Design Spec:** https://mcpugmire1.github.io/mattgpt-design-spec/
- **Email:** mpugmire@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/mattpugmire/

---

*This file is the single source of truth for "where are we right now?" in the Streamlit app project. Keep it updated!*
