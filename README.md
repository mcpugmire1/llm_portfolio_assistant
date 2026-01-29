# MattGPT - AI-Powered Career Portfolio Assistant

> An intelligent interface to 20+ years of digital transformation experience

🚀 **[Try the Live App](https://askmattgpt.streamlit.app/)** 

---
## 🎯 What This Is

An AI assistant that provides conversational access to my professional portfolio
across 130+ transformation projects, enabling recruiters and hiring managers to
ask specific questions and receive verifiable, outcome-focused answers.

**Example queries:**
- "How did Matt scale engineering teams from 4 to 150+ people?"
- "Show me examples of agile transformation in financial services"
- "What's Matt's experience with payments modernization?"

**The Innovation:** Moving beyond static resumes to an interactive, AI-powered 
portfolio that delivers cited, STAR-formatted stories on demand.

---
## 💡 Why This Approach

Traditional portfolios force readers to:
- 📄 Read pages of static text
- 🔍 Search manually for relevant experience
- ❓ Wonder about specific outcomes or methodologies

**MattGPT solves this by:**
- ✅ Answering specific questions in natural language
- ✅ Providing verifiable STAR-formatted stories
- ✅ Citing specific projects for verification
- ✅ Adapting responses to different audience needs (recruiters, technical leaders, executives)

---

## 🏗️ How It Works
```
User Query → Semantic Search → RAG Retrieval → GPT-4 → Cited Answer
                    ↓
              Pinecone/FAISS
           (130+ STAR stories)
```
**Technical Innovation:** Hybrid retrieval combining semantic embeddings with 
structured metadata filtering to deliver context-aware, outcome-focused responses.

---
---

## ✨ Key Features

- **Semantic Search** - Understands intent beyond keywords
- **STAR Framework** - Every answer includes Situation, Task, Action, Result
- **Source Citations** - Direct links to specific project details
- **Hybrid Retrieval** - Vector similarity + metadata filtering
- **Multi-Modal Responses** - Narrative summaries, key points, or detailed breakdowns
- **Role-Aware** - Tailors depth/focus for recruiters vs. technical vs. executive audiences

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (1536 dims)
- **Vector DB**: Pinecone (cloud)
- **Deployment**: Streamlit Cloud
- **Future**: React + AWS migration

---

## 🎓 Technical Learning Objectives

Built as a hands-on exploration of modern AI application development:
- ✅ RAG (Retrieval-Augmented Generation) architecture
- ✅ Vector databases and semantic search optimization
- ✅ Embedding model selection and performance tuning
- ✅ LLM prompt engineering and response synthesis
- ✅ Production deployment and cloud infrastructure

---
## 📊 What This Demonstrates

**Product Thinking**
- Identified user pain points (static portfolios, manual search)
- Designed solution prioritizing verifiability and user experience

**Technical Execution**
- Implemented RAG pipeline from scratch
- Integrated vector search, LLM APIs, and cloud deployment
- Optimized for both semantic understanding and structured retrieval

**Modern AI/ML Capabilities**
- Practical application of embeddings and vector search
- Production LLM integration with citation tracking
- Hybrid retrieval strategies for improved accuracy

---

## 🗺️ Roadmap

**Phase 1: MVP ✅ Complete**
- Streamlit app with semantic search
- RAG pipeline with STAR methodology
- Cloud deployment (Streamlit Cloud)

**Phase 2: Production Enhancement 🔄 In Progress**
- React frontend refactor
- AWS deployment
- Advanced filtering and timeline views
- Enhanced mobile experience

**Phase 3: Advanced Features 📋 Planned**
- Multi-modal search (semantic + filters)
- Analytics dashboard
- Export capabilities (PDF, portfolio packets)
- Performance optimizations

---


## 🚀 Quick Start

### Features
- **Interactive Streamlit UI** for exploring career stories and technical projects
- **Career story recall** in STAR format (with optional 5P summaries)
- **Semantic search** with OpenAI embeddings (text-embedding-3-small)
- **Pinecone (cloud)** vector search backend
- **Production deployment** at [askmattgpt.streamlit.app](https://askmattgpt.streamlit.app)

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

5. **Build the embeddings** (only needed if updating the dataset):

   **Data Pipeline (3 steps):**
   ```bash
   # Step 1: Extract base data from Excel
   python generate_jsonl_from_excel.py

   # Step 2: Enrich with AI-generated tags
   python generate_public_tags.py

   # Step 3: Generate embeddings and upload to vector DB
   python build_custom_embeddings.py
   ```

6. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## ⚙️ Configuration

### `config/constants.py` - Single Source of Truth

All application constants are centralized in `config/constants.py`:

| Category | Constants |
|----------|-----------|
| **Models** | `DEFAULT_CHAT_MODEL`, `DEFAULT_CLASSIFICATION_MODEL`, `DEFAULT_EMBEDDING_MODEL` |
| **Thresholds** | `HARD_ACCEPT`, `SOFT_ACCEPT`, `CONFIDENCE_HIGH`, `CONFIDENCE_LOW`, `PINECONE_MIN_SIM`, `ENTITY_GATE_THRESHOLD` |
| **Voice Quality** | `BANNED_PHRASES`, `META_COMMENTARY_PATTERNS` |
| **Entity Detection** | `ENTITY_DETECTION_FIELDS`, `ENTITY_SEARCH_FIELDS`, `EXCLUDED_DIVISION_VALUES` |

**To change a threshold or add a banned phrase, edit `config/constants.py` only.**

### Cache Dependencies

When modifying certain files, caches must be regenerated:

| If you change... | Run this... |
|-----------------|-------------|
| `echo_star_stories_nlp.jsonl` | `python build_custom_embeddings.py` |
| `VALID_INTENTS` in `semantic_router.py` | Delete `data/intent_embeddings.json` |
| `DEFAULT_EMBEDDING_MODEL` | `python build_custom_embeddings.py` |

---

## 📝 Notes
- Requires Python 3.11+
- Built with:
  - `openai` – Powers both embeddings (text-embedding-3-small) and conversational responses (GPT-4o-mini).
  - `pinecone` – Cloud vector database that stores embeddings and performs high-speed similarity searches to retrieve relevant stories.
  - `streamlit` – Interactive Python framework for building browser-based UIs, used here for filters, queries, and mobile-responsive design.
- Optimized for both desktop and mobile use; includes advanced filtering, timeline views, and semantic search.


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

### 📜 `generate_public_tags.py`

This script enriches the base JSONL data with AI-generated semantic tags using OpenAI's GPT-4.

**Pipeline Position:** Step 2 of 3

**Input:**  `echo_star_stories.jsonl` (from `generate_jsonl_from_excel.py`)
**Output:** `echo_star_stories_nlp.jsonl` (enriched with `public_tags` field)

---

#### 🔑 Key Features

- **AI-Powered Tagging**
  - Uses GPT-4 to analyze each story's Title, Use Cases, Situation, Task, Action, Result
  - Generates semantic tags aligned with SFIA, O*NET, LinkedIn, and industry frameworks
  - Captures technical skills, business capabilities, leadership themes

- **Smart Token Management**
  - Tracks token usage to avoid API limits
  - Estimates costs before running
  - Caches results to avoid re-processing unchanged stories

- **Backup Safety**
  - Creates timestamped backup of input file before processing
  - Preserves existing tags if present

---

#### 🚦 Usage

```bash
python generate_public_tags.py
```

**Requirements:**
- `OPENAI_API_KEY` in `.env` file
- `echo_star_stories.jsonl` must exist (run `generate_jsonl_from_excel.py` first)

**Expected Cost:** ~$0.50-2.00 for 120+ stories (using GPT-4o-mini)

---

### 📜 `build_custom_embeddings.py`

This script generates vector embeddings from the enriched JSONL data and uploads them to Pinecone or FAISS.

**Pipeline Position:** Step 3 of 3

**Input:**  `echo_star_stories_nlp.jsonl` (from `generate_public_tags.py`)
**Output:** Pinecone index or FAISS local index with embeddings

---

#### 🔑 Key Features

- **Dual Backend Support**
  - Pinecone (cloud vector database)
  - FAISS (local vector database)

- **Natural Language Embeddings**
  - Uses OpenAI `text-embedding-3-small` model (1536 dimensions)
  - Embeds 5P summary + Place + Industry context
  - Optimized for behavioral query matching

- **Clean Re-indexing**
  - Purges existing namespace before upserting
  - Handles NaN values and validation
  - Batch processing for efficiency

---

#### 🚦 Usage

```bash
python build_custom_embeddings.py
```

**Environment Variables:**
```env
VECTOR_BACKEND=pinecone    # or "faiss"
STORIES_JSONL=echo_star_stories_nlp.jsonl
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=...
PINECONE_NAMESPACE=default
```

---

## 📄 License
This project is for personal use only.

**Built by [Matt Pugmire](https://linkedin.com/in/matthewpugmire)** | [mcpugmire@gmail.com](mailto:mcpugmire@gmail.com)
