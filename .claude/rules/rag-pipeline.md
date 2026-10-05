---
paths:
  - "services/**"
  - "ui/pages/ask_mattgpt/**"
  - "config/**"
  - "**/nonsense_filters.jsonl"
---

# RAG pipeline rules

## Pipeline
```
Query → Nonsense Filters → Semantic Router → out_of_scope check → Pinecone → Confidence Gate → LLM
```

**Intent families:** defined in `services/semantic_router.py`.

**Entity detection:** `detect_entity()` checks Client, Employer and Division (`ENTITY_DETECTION_FIELDS`), then story titles. A Client, Employer or Division match becomes a hard Pinecone filter: one `$or` across `ENTITY_SEARCH_FIELDS` (client, employer, division, project, place, title) using the detected value. A Title match adds no Pinecone filter (soft filtering). The synthesis path filters on the detected field only. Detection is deliberately narrower than search; see the comments on both constants in `config/constants.py`.

**Context exclusion prefixes:** `EXCLUSION_PREFIXES` in `ui/pages/ask_mattgpt/backend_service.py` prevent entity filtering.

**Sacred vocabulary:** "builder" is used verbatim in Professional Narrative responses. Preserve it exactly when editing the prompts or code that produce them.

**Confidence thresholds:** see `config/constants.py`. Do not duplicate values anywhere else.

## Pinecone Metadata Casing
Lowercase field names. Stored values (`build_custom_embeddings.py`):

| Field | Stored value | Example |
|-------|--------------|---------|
| `division`, `employer`, `project`, `industry`, `complexity` | lowercase | `"cloud innovation center"` |
| `client`, `role`, `title`, `domain` | as written in the corpus | `"Accenture"` |

```python
from config.constants import PINECONE_LOWERCASE_FIELDS
pc_value = entity_value.lower() if pc_field in PINECONE_LOWERCASE_FIELDS else entity_value
```

## Nonsense Filter Rules
`nonsense_filters.jsonl` contains regex patterns that block off-topic queries. When adding patterns:
1. Test against real queries first: will this block "Tell me about Matt's X"?
2. Avoid common verbs: "solve", "build", "create", "manage" appear in legitimate queries.
3. Prefer multi-word phrases: `"homework help"` is safer than `"homework"`.
4. Use word boundaries: `\b(word)\b` prevents partial matches.
5. Don't duplicate the semantic scoring gate, which already catches gibberish (threshold in `config/constants.py`).
