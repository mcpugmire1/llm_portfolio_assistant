# LLM Portfolio Assistant

See instructions in this file.
This is a personalized, local-first assistant that helps you explore real experiences from Matt Pugmire's career. It uses custom embeddings, FAISS indexing, and OpenAI to respond in natural language to questions about Matt's work history.

## Features
- Interactive Streamlit UI
- STAR-format story recall
- Custom embedding search with FAISS
- Local-first and private by design

## Setup
1. Clone the repo
2. Create and activate a virtual environment
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Add your `.env` file:
   ```env
   OPENAI_API_KEY=sk-...
   ```
5. Build the embeddings:
   ```bash
   python build_custom_embeddings.py
   ```
6. Run the app:
   ```bash
   streamlit run app.py
   ```


## Notes
- Requires Python 3.10+
- Built using `sentence-transformers`, `faiss`, `streamlit`, and OpenAI SDK

## License
This project is for personal use only.
```
