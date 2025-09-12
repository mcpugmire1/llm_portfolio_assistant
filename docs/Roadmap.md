# 🧠 MattGPT (Echo) — Personalized Career Assistant
🔄 Status: v1.1 Running with RAG + Pinecone + Streamlit

📌 *See [ADR.md](./ADR.md) for key architectural decisions.*

---

## ✅ Completed (Phase 1 & 2 Foundations)
1. Core Functionality
   - ✅ Built semantic search with Pinecone + sentence-transformers
   - ✅ Created echo_star_stories.jsonl + echo_star_stories_nlp.jsonl
   - ✅ Added 5P tagging and rich metadata (Person, Place, Purpose, etc.)
   - ✅ Integrated Streamlit frontend with query and filter support
   - ✅ Finalized story curation — only Finalized (Interview-Ready) stories
   - ✅ Built script to truncate and upsert Pinecone vectors with namespace support

2. Content Management
   - ✅ Developed generate_jsonl_from_excel.py to convert master Excel to JSONL
   - ✅ Created generate_content_field.py to enrich with LLM summary
   - ✅ Created fill_5p_fields.py to auto-generate 5P metadata
   - ✅ 5P Summary used as contextual lead-in for AI answers
   - ✅ Validated Pinecone vector count and metadata integrity

---

## 🚧 In Progress (Phase 3: UX & Enrichment)
3. Public Tags Enrichment
   - 🛠️ Script: generate_public_tags.py (Planned)
   - Enrich public_tags using SFIA / O*NET / LinkedIn Skills Taxonomy
   - Align with target role keywords for SEO and filtering
   - Controlled vocabulary mapping (e.g., “DevOps” → “Agile & DevOps Leadership”)

4. UX & Presentation
   - 🚧 Polish Streamlit UI (colors, spacing, layout consistency)
   - 🛠️ Add “About Matt” hero panel
   - 🛠️ Preload example queries for discoverability
   - 🚧 Improve STAR story formatting (bold labels, consistent spacing)
   - 🛠️ Add filters for Role, Client, Sub-category, Competencies, 5Ps
   - ✅ Added dropdown/pill filters (Role, Client, Tags, 5Ps)
   - 🛠️ Surface 5P Summary as preview in results
   - 🧭 Explore showing full 5P breakdown alongside STAR content

---

## 🧭 Next Up (Phase 4+)
5. Interactive Search Enhancements
   - 🔍 Hybrid keyword + semantic search
   - 🧠 Query rewriting (“led” → “orchestrated”)
   - 📊 Show similarity scores in results

6. Portfolio Integration
   - 🌐 Link into Notion portfolio & LinkedIn
   - 📎 Copy-to-Clipboard for answers
   - 💼 Recruiter/hiring manager exploration by use case

7. Version Control & Stability
   - 🧪 Script version tagging (v1.1, v1.2…)
   - 📦 Backup JSONL & Excel each milestone
   - 🛡️ Avoid overwrites of semantically enriched files (manual confirm)

---

## 🧭 Planned
8. Job Fit & Matching
   - 📝 Paste job description
   - 🧠 Semantic + keyword match with STARs
   - ✍️ Generate tailored response (mini cover letter / pitch)

---

## 🪄 Stretch Goals
- 🤖 Agent-like assistant persona (“Ask Matt anything about his experience”)
- 🧩 LangChain or Haystack upgrade for advanced RAG
- 🎙️ Audio/chatbot interface for interview practice
- 🧪 Local embedding storage (Chroma) for offline
- 🎯 User feedback signals (thumbs, stars) to log match quality

🗂️ *For granular backlog items and acceptance criteria, see [Backlog.md](./Backlog.md).*