# Utility Scripts

This directory contains one-off utility scripts for data processing, quality checks, and maintenance tasks. These scripts are not part of the main application flow but are useful for data engineering and validation.

## Data Processing Scripts

### Excel/JSONL Conversion
- `generate_jsonl_from_excel.py` - **MOVED TO ROOT** (critical data engineering flow)
- `extract_jsonl_to_excel.py` - Export JSONL data to Excel format
- `extract_jsonl_with_personas_to_excel.py` - Export JSONL with persona data to Excel

### Data Cleanup
- `cleanup_excel_bullets.py` - Clean bullet points in Excel data
- `cleanup_excel_bullets_v2.py` - Updated version of bullet cleanup
- `merge_tags_columns.py` - Merge tag columns in data
- `extract_5p_from_synthesized.py` - Extract 5P framework from synthesized data
- `fix_json.py` - Fix malformed JSON data

## Quality & Validation Scripts

### Story Quality
- `assess_story_quality_v2.py` - Assess quality of story entries
- `audit_delimiters.py` - Audit delimiter usage in data

### Sanity Checks
- `sanity_check.py` - General data sanity checks
- `sanity_check_for_matt.py` - Specific sanity checks
- `sanity_check_raw.py` - Raw data sanity checks
- `sanity_row_checker.py` - Row-by-row validation

### Data Validation
- `validate_industry_data.py` - Validate industry field data
- `validate_pinecone_data.py` - Validate Pinecone index data

## Pinecone & Vector Operations

- `build_custom_embeddings.py` - **MOVED TO ROOT** (critical data engineering flow)
- `download_model.py` - Download embedding models
- `purge_pinecone_index.py` - Clear Pinecone index
- `rerank_with_metadata.py` - Rerank results with metadata
- `vector_search.py` - Vector search utilities

## Analysis & Statistics

- `client_distribution.py` - Analyze client distribution in stories
- `gen_personas_stats.py` - Generate persona statistics

## Miscellaneous

- `chat_snippet_based.py` - Snippet-based chat experiments
- `streamlit_drawer_approximation.py` - UI drawer component experiments
- `utils.py` - Legacy utility functions (avoid name collision with `utils/` package)

## Note

The main data engineering flow uses these **root-level** scripts:
- `app.py` - Main Streamlit application
- `build_custom_embeddings.py` - Build custom embeddings
- `generate_jsonl_from_excel.py` - Generate JSONL from Excel
- `generate_public_tags.py` - Generate public-facing tags

These must remain at the root for the workflow to function correctly.
