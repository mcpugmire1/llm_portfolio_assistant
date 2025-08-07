# LLM Portfolio Assistant

This is a personalized, local-first assistant that helps you explore real experiences from Matt Pugmire's career.  
It uses custom embeddings, FAISS or Pinecone indexing, and OpenAI's API to respond in natural language to questions about Matt's work history.

---

## 🚀 Quick Start

### Features
- **Interactive Streamlit UI** for exploring career stories and technical projects
- **Career story recall** in STAR format (with optional 5P summaries)
- **Semantic search** with custom embeddings via `sentence-transformers`
- **FAISS (local)** or **Pinecone (cloud)** vector search backends
- **Local-first and private by design**, with optional cloud deployment

---

## ⚙️ Setup

⚠️ **Note:** This repo does not include the `echo_star_stories.jsonl` dataset 
for privacy reasons. If you'd like to run the app locally with the complete 
career story dataset, please contact [Matt Pugmire](mailto:mcpugmire@gmail.com) 
for access or instructions to generate it from the source Excel file.

1. **Clone the repo**  
   ```bash
   git clone https://github.com/mcpugmire1/llm_portfolio_assistant.git
   cd llm_portfolio_assistant
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install requirements**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your `.env` file** with required API keys and config:  
   ```env
   OPENAI_API_KEY=sk-...
   VECTOR_BACKEND=faiss   # or "pinecone"
   PINECONE_API_KEY=...
   PINECONE_INDEX_NAME=...
   PINECONE_NAMESPACE=default
   ```

5. **Build the embeddings** (only needed if updating `echo_star_stories.jsonl`):  
   ```bash
   python build_custom_embeddings.py
   ```

6. **Run the app**  
   ```bash
   streamlit run app.py
   ```

---

## 📝 Notes
- Requires Python 3.10+
- Built with:
  - `sentence-transformers` – Creates dense vector embeddings from text, enabling semantic search by meaning rather than keywords.
  - `faiss` or `pinecone` – Vector databases that store embeddings and perform high-speed similarity searches to retrieve relevant stories.
  - `streamlit` – Interactive Python framework for building browser-based UIs, used here for filters, queries, and mobile-friendly design.
  - `openai` – Powers the conversational responses by synthesizing retrieved stories into clear, first-person narratives.
- Optimized for both desktop and mobile use; includes sidebar filtering and semantic search.


---
## 🛠️ Scripts

### 📜 `generate_jsonl_from_excel.py`

This script converts the **"STAR Stories – Interview Ready"** sheet in the Excel file  
(e.g. `MPugmire - STAR Stories - 06AUG25.xlsx`) into a structured `echo_star_stories.jsonl` file,  
while **preserving existing data** (`public_tags`, `content`, and `id`) from a prior JSONL when possible.

---

#### 🔑 Key Features

- **Safe Overwrite**
  - Loads existing JSONL to avoid overwriting important fields with blanks.
  - Backs up the current JSONL before making any changes.

- **Stable Matching**
  - Matches stories using a normalized `Title|Client` key.
  - Ensures accurate updates even if row order changes.

- **Field Processing**
  - Splits multi-value fields (e.g. `Competencies`, `Use Case(s)`).
  - Parses bullet-style fields (`Performance`, `Process`) into arrays.
  - Normalizes whitespace, removes extraneous bullets, and ensures clean formatting.

- **Preservation Logic**
  - Keeps `public_tags` and `content` from old JSONL if Excel cell is blank.
  - Maintains stable `id` fields for consistent downstream use.

- **Dry Run Mode**
  - Set `DRY_RUN = True` in the script to preview changes without writing the file.
  - Useful for verifying record count, merge accuracy, and previewing diffs.

---

#### 🚦 Usage

```bash
python generate_jsonl_from_excel.py
```

Edit the script directly to:
- Update the Excel file path (`INPUT_EXCEL_FILE`)
- Set `DRY_RUN = True` to preview or `False` to write changes

---

## 📄 License
This project is for personal use only.
