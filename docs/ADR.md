# Architectural Decision Records (ADR)

This document is a running log of key architectural and design decisions for the MattGPT / Portfolio Assistant project.  
We are using a single ADR.md file (instead of one file per decision) for simplicity at this stage.

---

## ADR 001 — Pinecone-First Semantic Search  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We need a scalable and accurate search strategy across curated STAR/5P stories. Literal keyword lookups are insufficient, and we want to handle natural questions (e.g., "How did you apply GenAI in healthcare?") gracefully.  
We validated that Pinecone-first retrieval with confidence gating is essential to avoid regressions and align with user expectations. Literal string maps proved brittle. Configuration should be centralized and consistent.

**Decision:**  
Adopt a **Pinecone-first semantic search** strategy using embeddings.  
- Pinecone provides similarity search and metadata filtering.  
- We apply a **low-confidence threshold** to suppress weak hits.  
- If Pinecone returns no confident results, fall back to local keyword/facet filtering.  
- `app_next.py` must implement **Pinecone-first semantic retrieval** with confidence gating and local FAISS fallback, mirroring `mockui.py`.  
- Environment and secrets are loaded via `load_dotenv()` with `st.secrets` fallback.  

**Consequences:**  
- Ensures semantic matches come first.  
- Preserves resilience when embeddings or Pinecone are unavailable.  
- Avoids brittle hardcoded string maps.
- Ensures alignment with validated UX.  
- Reduces risk of regressions.  
- Centralizes configuration and avoids divergence.  
- No literal string maps for retrieval.  
- Nonsense queries handled via low-confidence suppression plus helpful suggestions.  
---

## ADR 002 — Excel as System of Truth for Stories  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We curate STAR/5P stories in Excel. Content evolves often, and we want non-technical edits without touching code.  

**Decision:**  
Treat the **Excel master file as the source of truth**.  
- Scripts (`generate_jsonl_from_excel.py`, `fill_5p_fields.py`) convert Excel → JSONL → Pinecone vectors.  
- No story text, tense, or metadata should be hardcoded in the app.  

**Consequences:**  
- Simplifies content updates.  
- Reduces risk of divergence between code and curated content.  
- Empowers non-developers to update stories.

---

## ADR 003 — Single ADR File (vs. Multiple)  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
Industry practice sometimes favors one ADR per file (`ADR-001.md`, etc.). For our project, this adds overhead.  

**Decision:**  
Use a **single `ADR.md` file** as a chronological decision log. Split into multiple files only if it becomes unmanageable.  

**Consequences:**  
- Lightweight to maintain alongside `Backlog.md` and `Roadmap.md`.  
- Easy to review in one place.  
- Less discoverability for very large sets of ADRs, but acceptable for now.

---

## ADR 004 — Hybrid Search (Keyword + Semantic)  
**Date:** 2025-08-21  
**Status:** Planned  

**Context:**  
Semantic search (Pinecone) captures natural language queries well, but exact keywords (e.g., client names, acronyms) can still be important.  

**Decision:**  
Adopt a **hybrid search** strategy in the future:  
- Semantic similarity via Pinecone  
- Keyword/facet filters layered on top  
- Potentially integrate keyword signals into scoring  

**Consequences:**  
- Improves precision on proper nouns and acronyms  
- Slightly more complexity in query pipeline  

---

## ADR 005 — Streamlit-First UI  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We need a lightweight, interactive front-end for story exploration and Q&A.  

**Decision:**  
Use **Streamlit** as the primary UI framework.  
- Rapid iteration and live reload  
- Easy filters, tabs, and layout control  

**Consequences:**  
- Low barrier for MVPs and demos  
- Less flexible than a full frontend framework, but sufficient for current needs  

---

## ADR 006 — Markdown Backlog and Roadmap (vs. Jira)  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We don’t want to maintain an external tool (like Jira) for backlog/roadmap at this stage.  

**Decision:**  
Use **Backlog.md** and **Roadmap.md** in `/docs` to capture tasks and priorities.  

**Consequences:**  
- Lightweight and version-controlled  
- Less automation and workflow support than Jira  

---

## ADR 007 — JSONL as Intermediate Content Format  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We need a machine-readable format between Excel (system of truth) and Pinecone vectors.  

**Decision:**  
Generate **JSONL files** (one story per line) as the intermediate format.  
- Scripts output `echo_star_stories.jsonl` and enriched variants  
- JSONL is consumed by Pinecone upserts and mock UI  

**Consequences:**  
- Simplifies debugging and pipelines  
- Adds an intermediate artifact to version control  

---

## ADR 008 — Single Repo, Not Microservices  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We’re a small project; splitting into microservices adds overhead.  

**Decision:**  
Keep everything (backend scripts, UI, docs) in a **single repository**.  

**Consequences:**  
- Simple dev experience  
- Risk of monolith bloat later, but acceptable for now  

---

## ADR 009 — Devcontainer for Consistent Setup  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
Contributors may have different local environments.  

**Decision:**  
Use **`.devcontainer`** with pinned dependencies to ensure consistent setup.  

**Consequences:**  
- Reduces “works on my machine” issues  
- Requires VSCode or devcontainer-compatible tooling  

---

## ADR 010 — Pinecone Similarity Thresholds & Snippets  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
Not all Pinecone results are useful; low-similarity hits can confuse users.  

**Decision:**  
Apply a **similarity threshold (minSim = 0.22)** to suppress weak hits.  
- Show Pinecone-provided snippet or fallback to 5P Summary  
- Flag low-confidence cases in UI for transparency  

**Consequences:**  
- Improves trust in results  
- Some relevant but low-similarity matches may be hidden  


## ADR 011 — Content Curation Rules
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
During roadmap/backlog discussions, we agreed the portfolio should only surface *finalized, interview-ready* stories to maintain quality and consistency.  

**Decision:**  
Only curated, finalized STAR/5P stories are included in the content pipeline (Excel → JSONL → Pinecone). Drafts or incomplete items are excluded.  

**Consequences:**  
- Maintains high quality and consistency across surfaced content  
- Avoids recruiters seeing incomplete or draft material  
- Requires discipline in curation before pipeline ingestion  


## ADR 012 — UI Philosophy
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
The UX should feel conversational, like ChatGPT. Multiple conversations highlighted avoiding jargon or structural labels (e.g., "STAR" or "5P") in the UI, while still leveraging those frameworks behind the scenes.  

**Decision:**  
Maintain a natural, chat-like interaction style. Do not expose "STAR/5P" terms in UI labels. Instead, surface user-friendly options like "summary," "narrative," or "deep dive."  

**Consequences:**  
- Keeps UI accessible and intuitive for recruiters and hiring managers  
- Still leverages structured frameworks internally for consistency  
- Avoids confusing non-technical audiences with jargon  

ADR-PINECONE-FIRST (2025-08-20)
Decision: app_next.py must implement Pinecone-first semantic retrieval with confidence gating and local FAISS fallback, mirroring mockui.py. Env/secrets are loaded with load_dotenv() + st.secrets fallback.
Why: Aligns with validated UX, reduces regressions, and centralizes configuration.
Status: Accepted.
Implication: No literal string maps for retrieval; “nonsense” queries handled via low-confidence suppression + suggestions.


## ADR 13: Pinecone-First Semantic Search with Low-Confidence & Nonsense Handling

**Date:** 2025-08-21

**Decision:**  
We will continue with a Pinecone-first strategy for semantic search, using a confidence threshold (`PINECONE_MIN_SIM`) as the primary filter. If Pinecone results fall below threshold, fall back to local keyword/filter search. We explicitly avoid literal string lookup or hardcoding mappings in code.

**Nonsense Handling:**  
- Out-of-scope or nonsensical queries (e.g., "weather today", "McDonald's salaries") are filtered via a lightweight rules/config file, not hardcoded.  
- If detected, MattGPT responds with: "That’s outside scope, but here’s what I can help you with…" plus suggested queries.  
- All off-scope queries are logged for review and vocabulary improvement.

**Rationale:**  
- Preserves consistency with Pinecone-first architecture defined earlier.  
- Avoids regressions into brittle literal lookups.  
- Keeps nonsense handling configurable and data-driven.  
- Aligns with industry RAG best practices: abstain confidently, steer helpfully, and learn iteratively.

**Status:** Accepted

---

## ADR 014 — Canonical Field Naming for Client & Title
**Date:** 2025-09-03  
**Status:** Accepted  

**Context:**  
Repeated confusion arose around whether to use `Title` vs. `Story_Title` and `Client` vs. `client` fields in the JSONL export and downstream UI. This led to mismatches and blank displays in the mock UI.  

**Decision:**  
- The Excel-to-JSONL exporter must write records with `Title` and `Client` fields.  
- The loader/UI must normalize these to lowercase (`title`, `client`) for rendering.  
- No additional variants (`Story_Title`, `short_title`, etc.) are introduced.  

**Consequences:**  
- Ensures consistency across Excel, JSONL, Pinecone, and UI.  
- Eliminates recurring mismatch debates.  
- Simplifies pipeline code and reduces maintenance overhead.  
- Requires a one-time migration to map any legacy `Story_Title` keys to `Title`.