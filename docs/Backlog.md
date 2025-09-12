# Backlog — Sprint-Level Stories

## 🟢 Current Sprint (ties to Roadmap Phase 3)
### Story 1: UX Polish — Streamlit
- Roadmap: 4. UX & Presentation
- As a recruiter, I want clean and clear STAR story rendering so I can quickly understand impact without confusion.
- Acceptance:
  - STAR fields bolded + spaced properly
  - “See how it unfolded” expands cleanly
  - Filters for Role/Client/Domain/Tags usable without page reloads
  - 5P Summary formatting polished (tense + clarity)
  - Related ADRs: UI Philosophy (ChatGPT-like style, avoid STAR/5P labels)

### Story 2: Pinecone-first Search
- Roadmap: 5. Interactive Search Enhancements
- As a recruiter, I want semantically relevant results even if phrasing is different from story text.
- Acceptance:
  - Pinecone query always runs first
  - Low-confidence (<0.22) → fallback banner
  - Literal keyword only as last resort
  - Related ADRs: Pinecone-first Semantic Search

### Story 3: Nonsense Question Handling
- Roadmap: 5. Interactive Search Enhancements
- As a recruiter, I want off-topic questions (e.g., “weather today”, “McDonalds salary”) to return a friendly redirect so I stay focused on portfolio content.
- Acceptance:
  - Detect when query is irrelevant to stories/portfolio
  - Return graceful message suggesting example portfolio-related queries
  - Ensure no backend errors or empty answers surface
  - Related ADRs: Content Curation Rules

---

## 🚧 In Progress
- [ ] Add “About Matt” hero panel (Phase 3)
- 🚧 Implement Pinecone-first + Low-Confidence + Nonsense Handling (semantic abstain + scope filter + friendly UX)
---

## 🔜 Planned
- [ ] Copy-to-Clipboard in Ask MattGPT answers (Phase 6)
- [ ] Add nonsense-question handler (weather, McDonalds, etc.)

---

## ✅ Done
- Multi-tab layout (Home, Stories, Ask, About)
- Session state nav fixes (Explore Stories, Home button)
- Integrated 5P summary into compact cards
- Low-confidence suppression warning for Pinecone search
- Debounced search input logic