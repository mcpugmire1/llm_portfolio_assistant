# About Matt Page Refactoring Plan

**Status:** Partially Complete - Career Timeline ✅ (Session 4, Nov 10, 2025) - Remaining sections deferred
**Wireframe:** https://mcpugmire1.github.io/mattgpt-design-spec/wireframes/about_matt_wireframe.html
**Current File:** [ui/pages/about_matt.py](ui/pages/about_matt.py)

---

## Summary of Changes Needed

This document captures the gap between the current About Matt implementation and the wireframe specification.

**Completed:**
- ✅ Career Timeline Visualization (Session 4 - November 10, 2025)

**Remaining sections deferred** to focus on Ask MattGPT improvements.

---

## 1. Hero Section Changes

**Current:**
- Simple title "Matt's Journey" with subtitle
- No avatar image
- No gradient background (uses `var(--background-color)`)
- Generic subtitle about Fortune 500 modernization

**Wireframe Target:**
- Title: "Matt Pugmire"
- Subtitle: "Digital Transformation Leader | Director of Technology Delivery"
- **Add 140px circular avatar** (two-column layout with avatar on left)
- **Purple gradient background**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Bio text: "20+ years driving innovation, agile transformation, and application modernization across Fortune 500 companies. Proven track record of accelerating delivery 3-20x..."

---

## 2. Stats Bar Changes

**Current (4 columns):**
```
20+ Years Experience
300+ Professionals Upskilled
200+ Engineers Certified
2 Innovation Centers Built & Scaled to 150+
```

**Wireframe Target (5 columns):**
```
20+ Years Experience (keep)
115 Projects Delivered (NEW)
300+ Professionals Trained (word change from "Upskilled")
15+ Enterprise Clients (NEW - replace Engineers Certified)
3-20x Delivery Acceleration (NEW - replace Innovation Centers)
```

**Color:** Use purple accent `#8B5CF6` instead of blue `#4a90e2`

---

## 3. Career Timeline Visualization ✅ COMPLETE

**Status:** ✅ Implemented November 10, 2025 (Session 4)

**Implementation Details:**
- **Vertical purple gradient line** (4px width, increased from wireframe 3px) connecting all positions
- **Circular dots** (20px diameter with 4px border, increased from wireframe 14px/3px for better visibility)
- **7 positions** matching wireframe exactly (not 6 as originally planned)
- Purple gradient accent (`linear-gradient(to bottom, #8B5CF6, #7C3AED)`)
- Single-line descriptions (changed from bullet points to match wireframe)
- Transparent card backgrounds (no borders/shadows for minimal design)
- 900px max-width container
- CSS `::before` pseudo-elements for line and dots
- HTML consolidation into single `st.markdown()` call to prevent Streamlit wrapper issues

**Timeline Positions Implemented:**
1. 2023–Present: Sabbatical | Innovation & Upskilling
2. 2019–2023: Director, Cloud Innovation Center @ Accenture
3. 2016–2023: Capability Development Lead @ Accenture
4. 2018–2019: Cloud Native Architecture Lead @ Accenture
5. 2009–2017: Sr. Technology Architecture Manager @ Accenture
6. 2005–2009: Technology Manager @ Blue Cross Blue Shield
7. 2000–2005: Early Career | Startups & Consulting

**Technical Approach:**
- CSS classes: `.timeline`, `.timeline-item`, `.timeline-card`
- Typography: 14px purple years (bold), 18px dark titles, 14px gray companies, 14px descriptions
- Spacing: 30px margin-bottom between items, 40px left padding for timeline container
- Dot positioning: `-50px` left offset from timeline container

**Key Learnings:**
- Streamlit wraps each `st.markdown()` call in container divs, breaking width constraints
- Solution: Build complete HTML string before single markdown render
- List collection with `join()` prevents raw HTML display issues

---

## 4. Core Competencies Restructure

**Current (3 cards with skill bars):**
- Digital Product & Innovation (4 skills with % bars)
- Technical Architecture (4 skills with % bars)
- Industry Expertise (4 skills with % bars)

**Wireframe Target (6 category cards in 3x2 grid):**

1. **Product & Innovation** (5 items)
   - Product Thinking
   - Rapid Prototyping
   - Innovation Strategy
   - Portfolio Management
   - OKRs/Metrics

2. **Modern Engineering** (5 items)
   - Cloud-Native Architecture
   - Microservices
   - DevOps/CI/CD
   - Test Automation
   - Platform Engineering

3. **Agile at Scale** (5 items)
   - SAFe
   - Scrum
   - Kanban
   - PI Planning
   - Agile Coaching

4. **Transformation Leadership** (5 items)
   - Change Management
   - Stakeholder Alignment
   - Org Design
   - Culture Building
   - Executive Presence

5. **Team Building** (5 items)
   - Hiring/Onboarding
   - Coaching/Mentoring
   - Performance Management
   - Psychological Safety
   - Distributed Teams

6. **AI & Emerging Tech** (5 items)
   - LLMs/RAG
   - Prompt Engineering
   - Vector Databases
   - ML Ops
   - GenAI Strategy

**Layout:** 3-column grid, 2 rows, remove skill percentage bars

---

## 5. Leadership Philosophy Expansion

**Current (4 brief items):**
- 🎯 Outcome-Driven: "Measure success by business impact, not activity"
- 🚀 Iterate Fast: "Small experiments beat big plans"
- 👥 People First: "Technology serves humans, not the other way around"
- 🔄 Learn Continuously: "Every failure is data for the next attempt"

**Wireframe Target (4 detailed principles with full paragraphs):**

1. **"Outcomes Over Output"**
   > "I don't measure success by velocity or features shipped. I measure it by business outcomes, customer impact, and whether the team is solving the right problems. Focus on what moves the needle, not what fills the backlog."

2. **"Experimentation Culture"**
   > "Innovation requires safe-to-fail environments where teams can test hypotheses, learn fast, and pivot without fear. Build cultures where failure is data, not career risk."

3. **"Servant Leadership"**
   > "My job is to remove blockers, amplify team voices, and create conditions for autonomy. I lead by asking questions, not giving answers. The team owns the solution; I own their success."

4. **"Continuous Learning"**
   > "Technology evolves fast. Organizations that don't invest in upskilling fall behind. I prioritize learning budgets, communities of practice, and knowledge-sharing rituals. Growth isn't optional—it's strategic."

**Layout:** 2-column card grid (2x2)

---

## 6. NEW SECTION: MattGPT Technical Deep-Dive

**Current:** This entire section is MISSING

**Wireframe Target:** Major new section (~200-300 lines) with:

### 6.1 Problem Statement
- Why traditional portfolios are static/limited
- Need for conversational, contextual portfolio exploration

### 6.2 "Agy" Origin Story
- Named after Matt's Plott Hound companion
- Symbolizes loyalty, tracking, and finding the right path
- Friendly AI assistant persona

### 6.3 Tech Stack Visualization
Display with icons + tool names:
- **Frontend:** Streamlit
- **LLM:** OpenAI GPT-4
- **Vector DB:** Pinecone
- **Language:** Python
- **Embeddings:** text-embedding-3-small
- **Search:** Hybrid (vector + keyword)

### 6.4 System Architecture (4-step flow)
```
1. User Query → 2. Embedding Generation → 3. Vector Retrieval → 4. LLM Response with Context
```

### 6.5 Code Samples (Python)

**Embedding Generation:**
```python
def generate_embedding(text: str) -> List[float]:
    """Generate OpenAI embedding for semantic search"""
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response['data'][0]['embedding']
```

**Vector Retrieval:**
```python
def retrieve_stories(query: str, top_k: int = 5) -> List[dict]:
    """Hybrid retrieval: vector similarity + keyword matching"""
    query_embedding = generate_embedding(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"type": "story"}
    )

    return [match['metadata'] for match in results['matches']]
```

**RAG Implementation:**
```python
def ask_mattgpt(question: str) -> str:
    """RAG pipeline: retrieve context + generate answer"""
    relevant_stories = retrieve_stories(question, top_k=3)

    context = "\n\n".join([
        f"Story: {s['title']}\n{s['situation']}\n{s['result']}"
        for s in relevant_stories
    ])

    prompt = f"""Based on Matt's experience:

{context}

Question: {question}

Answer naturally, referencing specific projects:"""

    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )['choices'][0]['message']['content']
```

### 6.6 Implementation Notes
- **Data Pipeline:** 115 STAR stories embedded using OpenAI API
- **Embeddings Strategy:** Title + Situation + Result fields concatenated
- **Hybrid Retrieval:** Combines vector similarity (0.7 weight) + keyword match (0.3 weight)
- **Frontend:** Streamlit components with custom CSS for chat interface

---

## 7. Contact/CTA Section Redesign

**Current:**
- "Let's Connect" header
- 3-column contact cards (Email, LinkedIn, Coffee Chat)
- Interactive buttons that reveal info on click
- Generic availability statement

**Wireframe Target:**

### Design:
- **Full-width purple gradient background**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Centered content (max-width: 900px)
- White text on gradient

### Content:
**Heading:** "Let's Connect"

**Subheading:**
> "Exploring Director/VP opportunities in Product Leadership, Platform Engineering, and Organizational Transformation"

**Availability:**
> "Available for immediate start • Remote or Atlanta-based • Open to consulting engagements"

### CTA Buttons (3 buttons, horizontal layout):
1. **Primary:** `📧 mcpugmire@gmail.com` (purple solid background)
2. **Secondary:** `💼 LinkedIn` (transparent with white border)
3. **Secondary:** `🐾 Ask Agy` (transparent with white border)

**Button Styling:**
- Padding: `14px 28px`
- Border radius: `8px`
- Font size: `16px`, weight: `600`
- Actual links (not interactive reveals)

---

## Implementation Priority

**Priority Order:**
1. ⏸️ Hero section (deferred - pending Ask MattGPT completion)
2. ⏸️ Stats bar (deferred - pending Ask MattGPT completion)
3. ✅ **Timeline visualization** (COMPLETE - November 10, 2025)
4. ⏸️ Core competencies restructure (deferred - pending Ask MattGPT completion)
5. ⏸️ Leadership philosophy expansion (deferred - pending Ask MattGPT completion)
6. ⭐ **MattGPT Technical Deep-Dive** (HIGHEST PRIORITY when we return - showcases technical credibility)
7. ⏸️ Contact/CTA redesign (deferred - pending Ask MattGPT completion)

---

## Estimated Effort

- **Quick wins:** Stats bar, color scheme updates (~30 min)
- **Medium effort:** Hero, ~~Timeline~~ ✅, CTA section (~1-2 hours)
- **Heavy lift:** Core Competencies restructure, Leadership expansion (~2-3 hours)
- **Major addition:** MattGPT Technical Deep-Dive (~3-4 hours)

**Timeline Actual Effort:** ~60 minutes (completed Session 4)
**Remaining Estimated Effort:** ~7-9 hours for complete wireframe alignment

---

## Design System Notes

**Color Palette (from wireframe):**
- Primary gradient: `#667eea → #764ba2` (purple range)
- Accent: `#8B5CF6` (vibrant purple)
- Dark text: `#2c3e50`
- Secondary gray: `#7f8c8d`
- Backgrounds: `#f5f5f5`, `#fafafa`, `white`
- Borders: `#e0e0e0`

**Typography:**
- Font family: System UI stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial`)
- H1: `36px`, bold
- H2: `32px`, centered
- Section titles: `20px`
- Body text: `14-15px`
- Small labels: `12px` uppercase, `600` weight

**Spacing:**
- Page padding: `20px`
- Section padding: `50px 40px`
- Grid gaps: `16-30px` (varies by section)
- Card padding: `24-32px`

---

## Next Steps When Resuming

1. ⭐ **MattGPT Technical Deep-Dive section** (highest impact - showcases technical credibility)
2. Update hero section with avatar + gradient
3. Update stats bar metrics (5 columns, purple accent)
4. Restructure core competencies (6 categories in 3x2 grid, no skill bars)
5. Expand leadership philosophy (full paragraphs in 2x2 grid)
6. Redesign contact/CTA (gradient background, centered, actual links)
7. ~~Timeline visualization~~ ✅ COMPLETE

---

**Last Updated:** November 10, 2025
**Status:** Career Timeline Complete (Session 4) - Remaining sections deferred pending Ask MattGPT completion
**Next Action:** Continue focusing on Ask MattGPT priorities, return to remaining About Matt sections when ready
