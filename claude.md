  # MattGPT - Claude Working Agreement

  ## Project Overview
  AI-powered portfolio assistant showcasing Matt's 20+ years of digital transformation experience. Named after his late Plott Hound "Agy" (short for Agador Spartacus from "The Birdcage"). Deployed at askmattgpt.streamlit.app.

  Read `ARCHITECTURE.md` for full system context.

  ## Tech Stack
  - **Frontend:** Streamlit (Python 3.11)
  - **Vector DB:** Pinecone (semantic search)
  - **Embeddings:** OpenAI text-embedding-3-small (1536 dims)
  - **Generation:** OpenAI GPT-4o-mini
  - **Data:** 130+ STAR stories in JSONL, 5P framework

  ## File Structure
  ```
  ui/pages/               # Page components
    explore_stories.py    # Story browsing with Table/Card/Timeline views
    ask_mattgpt/          # Modular chat interface (8 files)
      __init__.py         # Router
      landing_view.py     # Landing page with capability cards
      conversation_view.py # Chat conversation UI
      conversation_helpers.py # Message rendering, Related Projects UX
      backend_service.py  # RAG pipeline integration
      styles.py           # Chat-specific CSS
      story_intelligence.py # Theme/persona inference
      shared_state.py     # Session state management
      utils.py            # Shared utilities
    about_matt.py         # About page
    banking_landing.py    # Banking industry landing
    cross_industry_landing.py # Cross-industry landing

  ui/components/          # Shared components
    timeline_view.py      # Era-based Timeline (5 career phases)
    story_detail.py       # Story detail modal
    how_agy_modal.py      # "How Agy Searches" modal
    ask_mattgpt_header.py # Unified header component
    category_cards.py     # Landing page capability cards
    thinking_indicator.py # Loading/processing indicator
    navbar.py             # Top navigation
    footer.py             # Footer

  ui/styles/              # CSS
    global_styles.py      # Shared CSS + mobile breakpoints + CSS variables
    mobile_overrides.py   # Additional mobile CSS

  services/               # Business logic
    rag_service.py        # Semantic search orchestration
    pinecone_service.py   # Vector database integration

  utils/                  # Helpers
    filters.py            # Story filtering logic
    scoring.py            # Confidence scoring
    formatting.py         # STAR story presentation
    validation.py         # Input validation

  config/                 # Settings
    debug.py              # DEBUG flag
    settings.py           # Configuration helpers
  ```

  ## Code Conventions
  - Filter state lives in `st.session_state["filters"]`
  - CSS variables defined in `global_styles.py` (use them, don't hardcode colors)
  - Widget versioning pattern: `key=f"widget_name_v{version}"` for forced refreshes
  - Use `safe_container()` wrapper for bordered sections
  - Container keys for CSS targeting: `.st-key-{key_name}` selectors

  ## CSS Rules (Learned the Hard Way)
  1. **Scope mobile CSS** — Use wrapper classes (`.explore-page`) or page-specific selectors
  2. **Never use generic selectors** — `div[data-testid="stColumn"]` leaks everywhere
  3. **Mobile changes go in `@media (max-width: 768px)` blocks** — Don't touch desktop rules
  4. **Test at breakpoints:** 375px (iPhone SE), 768px (tablet), 1024px+ (desktop)
  5. **Streamlit class names like `st-emotion-cache-*` change between versions** — Target `data-testid` or `.st-key-*` classes instead
  6. **Use existing CSS variables** — Check `global_styles.py` for `--bg-card`, `--border-color`, `--text-primary`, `--accent-purple`, etc. Don't invent new ones.
  7. **Container keys for targeting** — Use `st.container(key="my_container")` then target with `.st-key-my_container` in CSS

  ## Streamlit Patterns (Learned the Hard Way)

  ### Session State & Widget Keys
  - **Never modify a session state key after its widget renders** — You'll get `StreamlitAPIException`
  - **Use prefilter pattern for cross-page navigation:**
    ```python
    # In source page (e.g., timeline_view.py):
    st.session_state["prefilter_role"] = role
    st.rerun()
    
    # In target page (e.g., explore_stories.py), BEFORE widgets render:
    if "prefilter_role" in st.session_state:
        F["role"] = st.session_state.pop("prefilter_role")
    ```
  - **Check existing patterns first** — See `banking_landing.py` → `explore_stories.py` for navigation with filters

  ### HTML in Streamlit
  - **`st.markdown()` with complex nested HTML often renders as raw text** — Use single-line HTML strings (no pretty formatting)
  - **For interactive HTML, use `components.html()`** — But clicks require JS to trigger hidden `st.button()` elements
  - **JS in iframes can't directly access parent** — Use `window.parent.document` with timeout for DOM readiness

  ### Click Handling Pattern (for custom HTML components)
  ```python
  # 1. Render HTML with data attributes
  st.markdown('<div class="card" data-index="0">...</div>', unsafe_allow_html=True)

  # 2. Hidden buttons for each clickable item
  for idx in range(len(items)):
      if st.button("", key=f"card_{idx}"):
          handle_click(items[idx])

  # 3. JS to wire clicks (in components.html with height=0)
  js = """
  <script>
  setTimeout(function() {
      document.querySelectorAll('.card').forEach(function(card) {
          card.addEventListener('click', function() {
              var idx = this.getAttribute('data-index');
              var btn = document.querySelector('[class*="st-key-card_' + idx + '"] button');
              if (btn) btn.click();
          });
      });
  }, 100);
  </script>
  """
  components.html(js, height=0)

  # 4. CSS to hide the buttons
  [class*="st-key-card_"] { position: absolute !important; left: -9999px !important; }
  ```

  ### Era-Based Timeline Pattern
  ```python
  # Timeline groups stories by career phase, not chronological
  ERA_ORDER = [
      "Integration & Platform Foundations (2005-2008)",
      "Banking & Capital Markets (2008-2013)",
      "Platform Leadership (2014-2018)",
      "Innovation Center (2019-2023)",
      "Current Work (2024-2025)"
  ]

  # Each era is collapsible with story count badge
  # Clicking a story opens detail modal
  # "View in Explore" link navigates with Era filter applied
  ```

  ### Related Projects UX Pattern
  ```python
  # Selected state with visual feedback
  # - Purple highlight on selected card
  # - "✕ Close" toggle appears when selected
  # - Clicking same card again deselects
  # - Only one related project selected at a time
  ```

  ## Behavioral Rules

  ### Do
  - **Check existing codebase patterns FIRST** — Before proposing any solution, search for how similar problems are already solved
  - Give direct solutions immediately
  - Execute the work, don't discuss it
  - Provide full file replacements (not patches) unless asked otherwise
  - Backup before modifying: `cp file.py file.py.bak`
  - Keep reference docs/comments when rewriting files

  ### Don't
  - Ask about priorities or trade-offs before starting
  - Add dependencies without flagging it
  - Over-engineer (80/20 rule applies)
  - Make changes outside the requested scope
  - Be condescending, rude, or defeatist
  - **Invent new patterns when existing ones work** — If banking_landing.py does X, timeline_view.py should do X the same way
  - **Hardcode values that are already CSS variables** — Always check global_styles.py first
  - **Generate fantasy roadmaps** — No "100K users", "99.9% SLA", "enterprise customers" nonsense

  ## Working with Claude
  - Start with "what's the minimal fix?" before architectural changes
  - Verify root cause before accepting complex solutions
  - Check simple things first: regex, config, cache, typos
  - If Claude proposes 50+ lines, ask "is there a simpler way?"

  ## No Hardcoded Enums for Data-Derived Values

  **NEVER hardcode lists of values that come from story data (clients, industries, themes, eras, etc.)**

  ❌ BAD:
  ```python
  EXCLUDED_CLIENTS = {"Multiple Clients", "Career Narrative", "Independent"}
  if client in {"JP Morgan", "Capital One", "RBC"}:
  ```

  ✅ GOOD:
  ```python
  # Pattern-based (no maintenance)
  from utils.client_utils import is_generic_client
  if is_generic_client(client):

  # Or derived from data at runtime
  named_clients = {s.get("Client") for s in stories if not is_generic_client(s.get("Client"))}
  ```

  **Why:** Hardcoded lists drift, duplicate across files, and break when data changes. If a value comes from the JSONL, the code should derive it or use pattern matching — never enumerate it.

  **If you need a list:** Create ONE source of truth in `utils/` or `constants/`, import everywhere.

  ## Nonsense Filter Rules (Learned the Hard Way)

  The `nonsense_filters.jsonl` file contains regex patterns to block off-topic queries. **Be extremely careful with word choices.**

  ### The "solve" Incident (Dec 2025)
  - **Problem:** Added "solve" to homework pattern → blocked "What problems does Matt solve?"
  - **Root cause:** Overly broad word in regex matched legitimate portfolio queries
  - **Fix:** Removed "solve" from pattern (commit `2dab2dc`)

  ### Rules for Adding Patterns
  1. **Test against real queries first** — Will this block "Tell me about Matt's X"?
  2. **Avoid common verbs** — Words like "solve", "build", "create", "manage" appear in legitimate queries
  3. **Prefer multi-word phrases** — `"homework help"` is safer than `"homework"` alone
  4. **Use word boundaries** — `\b(word)\b` prevents partial matches
  5. **Don't duplicate the entity gate's job** — Semantic scoring (< 0.55) already catches gibberish like "asdfghjkl"

  ### Pattern Testing
  ```python
  # Always test new patterns against these legitimate queries:
  test_queries = [
      "What problems does Matt solve?",
      "How did Matt transform delivery?",
      "Tell me about stakeholder alignment",
      "What's Matt's leadership philosophy?",
  ]
  ```

  ## Pinecone Metadata Casing Protocol (Learned the Hard Way)

  Pinecone metadata fields use **lowercase field names** but values have inconsistent casing. When building entity filters in `pinecone_service.py`, follow these rules:

  ### Lowercase Values (must call `.lower()`)
  | Field | Example Value |
  |-------|---------------|
  | `division` | `"cloud innovation center"` |
  | `employer` | `"accenture"` |
  | `project` | `"cloud innovation center"` |
  | `industry` | `"cross industry"` |
  | `complexity` | `"internal"` |

  ### PascalCase Values (preserve original case)
  | Field | Example Value |
  |-------|---------------|
  | `client` | `"Accenture"` |
  | `role` | `"Director"` |
  | `title` | `"Scaling CIC Impact..."` |
  | `domain` | `"Leadership & Talent Development"` |

  ### The Q29 Incident (Jan 2026)
  - **Problem:** Entity filter `division = "Cloud Innovation Center"` returned 0 hits
  - **Root cause:** Pinecone stores `division` values lowercase (`"cloud innovation center"`)
  - **Fix:** Field-specific lowercasing in `pinecone_service.py:198`

  ### Implementation
  ```python
  # In pinecone_service.py
  if pc_field == "division":
      pc_value = entity_value.lower()
  else:
      pc_value = entity_value  # Keep PascalCase for client, role, etc.
  ```

  ## Quality Standards
  - **"Can you defend it?"** — Every claim, metric, or statement must be factually accurate
  - **No AI fabrications** — Real stories from real experience only
  - **Mobile must not break desktop** — Test both after any CSS change

  ## Current Status (December 2025)
  - ✅ Era-based Timeline view (complete)
  - ✅ Mobile responsive implementation (complete)
  - ✅ Filter redesign - Primary + Advanced (complete)
  - ✅ Related Projects UX (complete)
  - ✅ Design spec documentation sync (complete)
  - 🎯 React + FastAPI migration (Q1 2026)

  ## Quick Reference

  ### Breakpoints
  | Device | Width | Layout |
  |--------|-------|--------|
  | Mobile | <768px | Single column, stacked |
  | Tablet | 768-1023px | 2 columns |
  | Desktop | ≥1024px | Full layout |

  ### CSS Variables (from global_styles.py)
  ```css
  --accent-purple: #8B5CF6
  --accent-purple-hover: #7C3AED
  --accent-purple-bg: rgba(139, 92, 246, 0.08)
  --accent-purple-light: rgba(139, 92, 246, 0.2)
  --bg-card: #FFFFFF
  --bg-surface: #F9FAFB
  --bg-hover: #F3F4F6
  --text-primary: #1F2937
  --text-secondary: #6B7280
  --border-color: #E5E7EB
  --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15)
  ```

  ### Confidence Thresholds
  ```python
  # RAG Service (Pinecone result confidence)
  CONFIDENCE_HIGH = 0.25  # "Found X stories"
  CONFIDENCE_LOW = 0.15   # "Relevance may be low"
  # Below 0.15 = "No strong matches"
  ```

  ## Sovereign Narrative Update (Jan 2026)

  Major RAG pipeline changes to improve handling of Professional Narrative (identity/philosophy) queries. Eval improved from 51.6% to 71.0%.

  ### Key Changes

  | Change | File | Purpose |
  |--------|------|---------|
  | Entity Gate Threshold | backend_service.py | Lowered from 0.55 to 0.50 to allow narrative queries |
  | Narrative Intent Family | semantic_router.py | Added 22 intents for Professional Narrative recognition |
  | Context Exclusions | backend_service.py | "after Accenture" doesn't filter TO Accenture stories |
  | Verbatim Phrase Injection | backend_service.py | Forces LLM to use "builder", "modernizer" verbatim |
  | Banned Phrase Cleanup | backend_service.py | Post-processing removes corporate filler phrases |
  | Narrative Mode Ranking | backend_service.py | Keeps boosted narrative story at #1 in results |
  | Dynamic Boost Fragments | rag_service.py | Derives title fragments from story data |

  ### Verbatim Phrases (Sacred Vocabulary)
  When responding to Professional Narrative queries, the LLM must use these exact phrases:
  - "builder", "modernizer"
  - "complexity to clarity"
  - "build something from nothing"
  - "not looking for a maintenance role"

  ### Context Exclusion Prefixes
  These words before an entity name prevent entity filtering:
  - "after", "leaving", "before", "transition from", "left"
  - Example: "career transition after Accenture" → broad search, not Accenture filter

  ### Banned Phrases (Auto-Removed)
  - "meaningful outcomes"
  - "foster collaboration"
  - "strategic mindset"
  - "stakeholder alignment"
  - "bridge the gap"

  ### Common Fixes
  - **Widget won't reset:** Increment version key, delete old widget keys
  - **CSS not applying:** Check specificity, add `!important` if scoped correctly
  - **Columns stacking wrong:** Streamlit auto-stacks below ~640px, use CSS grid instead
  - **Session state error on widget key:** Use prefilter pattern (set before widget renders, pop when reading)
  - **HTML rendering as text:** Remove newlines/indentation from f-string HTML
  - **Import conflicts:** Check you're not importing same function from two different files (last import wins)

  ## Deployment
  ```bash
  # Local
  streamlit run app.py

  # Deploy (Streamlit Cloud)
  git push origin main
  ```

  ## Related Documentation
  - [Design Specification](https://mcpugmire1.github.io/mattgpt-design-spec/) - Full product blueprint
  - [API Reference](https://mcpugmire1.github.io/mattgpt-design-spec/docs/09-api-reference) - Function signatures
  - [Data Model](https://mcpugmire1.github.io/mattgpt-design-spec/docs/10-data-model) - JSONL schema
