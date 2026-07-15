"""
build_custom_embeddings.py

Reads enriched STAR story data from a JSONL file, generates embeddings using
OpenAI's text-embedding-3-small (1536 dims), and upserts them into Pinecone.

Updated 12.05.25:
- Switched from MiniLM (384 dims) to OpenAI text-embedding-3-small (1536 dims)
- Better semantic matching for behavioral interview questions

DEPENDENCY WARNING:
Run this script after ANY changes to:
- echo_star_stories_nlp.jsonl (story data)
- Embedding text construction logic (what text gets embedded)
- Embedding model (DEFAULT_EMBEDDING_MODEL in config/constants.py)

Failure to re-run after changes will cause semantic search drift.

Env (via .env or shell):
  STORIES_JSONL=echo_star_stories_nlp.jsonl
  OPENAI_API_KEY=...
  PINECONE_API_KEY=...
  PINECONE_INDEX_NAME=matt-portfolio-v2
  PINECONE_NAMESPACE=default
"""

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s"
)
load_dotenv()

STORIES_JSONL = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims


# ---------------------------
# Helpers
# ---------------------------
def _as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    if ";" in s:
        return [x.strip() for x in s.split(";") if x.strip()]
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return [s]


def build_embedding_text(story: dict[str, Any]) -> str:
    """
    Build a rich, behavior-aware text representation for embeddings.
    """

    def _to_chars(val, char_limit: int) -> str:
        if not val:
            return ""
        if isinstance(val, list):
            text = " ".join(str(p).strip() for p in val if str(p).strip())
        else:
            text = str(val).strip()
        return text[:char_limit]

    title = (
        story.get("Title", "").strip() if isinstance(story.get("Title"), str) else ""
    )

    theme = (
        story.get("Theme", "").strip() if isinstance(story.get("Theme"), str) else ""
    )
    industry = (
        story.get("Industry", "").strip()
        if isinstance(story.get("Industry"), str)
        else ""
    )
    sub_category = (
        story.get("Sub-category", "").strip()
        if isinstance(story.get("Sub-category"), str)
        else ""
    )

    summary_5p = (
        story.get("5PSummary", "").strip()
        if isinstance(story.get("5PSummary"), str)
        else ""
    )
    situation = _to_chars(story.get("Situation"), 2000)
    task = _to_chars(story.get("Task"), 1500)
    action = _to_chars(story.get("Action"), 2500)
    result = _to_chars(story.get("Result"), 2000)
    process_text = _to_chars(story.get("Process"), 1500)

    tags = story.get("public_tags", "")
    if isinstance(tags, list):
        tags = ", ".join(tags)
    tags = tags.strip() if tags else ""

    use_cases = _to_chars(story.get("Use Case(s)"), 600)
    competencies = _to_chars(story.get("Competencies"), 600)
    interview_questions = _to_chars(story.get("Interview Questions"), 1200)

    parts: list[str] = []

    header_bits = []
    if title:
        header_bits.append(f"[{title}]")
    if theme:
        header_bits.append(f"[{theme}]")
    if industry:
        header_bits.append(f"in {industry}")
    if sub_category:
        header_bits.append(f"({sub_category})")

    if header_bits:
        parts.append(" ".join(header_bits))

    # Use Cases front-loaded — strongest retrieval signal, tuned per story
    if use_cases:
        parts.append(f"Use Cases: {use_cases}")

    if summary_5p:
        parts.append(f"Summary: {summary_5p}")

    if situation:
        parts.append(f"Situation: {situation}")
    if task:
        parts.append(f"Task: {task}")
    if action:
        parts.append(f"Action: {action}")
    if result:
        parts.append(f"Result: {result}")

    if process_text:
        parts.append(f"Process: {process_text}")

    if competencies:
        parts.append(f"Competencies: {competencies}")

    if tags:
        parts.append(f"Keywords: {tags}")

    if interview_questions:
        parts.append(f"Interview Questions: {interview_questions}")

    return " ".join(p for p in parts if p)


def build_metadata(story: dict[str, Any]) -> dict[str, Any]:
    """Compact but rich metadata for UI/snippets + Pinecone filters."""
    cat = story.get("Category", "")
    sub = story.get("Sub-category", "")
    theme = story.get("Theme", "")
    domain = " / ".join([x for x in [cat, sub] if x])

    tags_list = _as_list(story.get("public_tags"))

    industry = story.get("Industry", "").strip()
    division = story.get("Division", "").strip()
    employer = story.get("Employer", "").strip()
    project = story.get("Project", "").strip()
    complexity = story.get("Project Scope / Complexity", "").strip()

    meta = {
        # CANONICAL FIELDS
        "id": story.get("id"),
        "Title": story.get("Title", "Untitled"),
        "Employer": employer,
        "Division": division,
        "Role": story.get("Role", "Unknown"),
        "Client": story.get("Client", "Unknown"),
        "Project": project,
        "Start_Date": story.get("Start_Date", ""),
        "End_Date": story.get("End_Date", ""),
        "Industry": industry,
        "Project Scope / Complexity": complexity,
        "Category": cat,
        "Sub-category": sub,
        "Theme": theme,
        "Era": story.get("Era", "").strip(),
        "Use Case(s)": _as_list(story.get("Use Case(s)")),
        "Interview Questions": _as_list(story.get("Interview Questions")),
        "Competencies": _as_list(story.get("Competencies")),
        "Situation": _as_list(story.get("Situation")),
        "Task": _as_list(story.get("Task")),
        "Action": _as_list(story.get("Action")),
        "Result": _as_list(story.get("Result")),
        "Purpose": story.get("Purpose", ""),
        "Performance": _as_list(story.get("Performance")),
        "Process": _as_list(story.get("Process")),
        "5PSummary": story.get("5PSummary", ""),
        "public_tags": tags_list,
        # UI-FRIENDLY DUPLICATES
        "title": story.get("Title", "Untitled"),
        "employer": employer.lower() if employer else "",
        "division": division.lower() if division else "",
        "client": story.get("Client", "Unknown"),
        "role": story.get("Role", "Unknown"),
        "project": project.lower() if project else "",
        "industry": industry.lower() if industry else "",
        "complexity": complexity.lower() if complexity else "",
        "domain": domain,
        "tags": tags_list,
        "summary": story.get("5PSummary", ""),
    }
    return meta


def get_openai_embeddings(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Generate embeddings using OpenAI API in batches."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        logging.info(
            f"📤 Embedding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch)} texts)"
        )

        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)

        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


if __name__ == "__main__":
    # ---------------------------
    # Load data
    # ---------------------------
    stories: list[dict[str, Any]] = []
    with open(STORIES_JSONL) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    logging.info(f"🔎 Loaded {len(stories)} stories from {STORIES_JSONL}")

    # ---------------------------
    # Build embedding texts
    # ---------------------------
    texts = [build_embedding_text(s) for s in stories]

    if texts:
        logging.info("📝 Sample embedding text (first story):")
        logging.info(f"   {texts[0][:500]}...")

        # Check the failure story
        fail_idx = next(
            (i for i, s in enumerate(stories) if 'assumptions' in s.get('id', '')),
            None,
        )
        if fail_idx:
            logging.info("📝 Failure story embedding text:")
            logging.info(f"   {texts[fail_idx][:300]}...")

    # ---------------------------
    # Generate embeddings via OpenAI
    # ---------------------------
    logging.info(f"🤖 Generating embeddings with {EMBEDDING_MODEL}...")
    embeddings = get_openai_embeddings(texts)
    logging.info(
        f"✅ Generated {len(embeddings)} embeddings (dim={len(embeddings[0])})"
    )

    # ---------------------------
    # Upsert to Pinecone
    # ---------------------------
    if not (PINECONE_API_KEY and PINECONE_INDEX_NAME):
        raise RuntimeError("PINECONE_API_KEY or PINECONE_INDEX_NAME is missing.")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    logging.info(
        f"[INFO] Using Pinecone index='{PINECONE_INDEX_NAME}', namespace='{PINECONE_NAMESPACE}'"
    )

    existing = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        raise ValueError(
            f"Index '{PINECONE_INDEX_NAME}' does not exist. Available: {existing}"
        )

    index = pc.Index(PINECONE_INDEX_NAME)

    # Purge namespace
    logging.info("🧹 Purging namespace (delete_all=True)…")
    try:
        index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)
    except Exception as e:
        logging.warning(f"Purge warning: {e}")

    # Upsert in batches
    batch = 100
    upserted = 0
    for start in range(0, len(stories), batch):
        items = []
        for i in range(start, min(start + batch, len(stories))):
            vec = embeddings[i]
            meta = build_metadata(stories[i])
            vec_id = str(meta.get("id") or f"story-{i}")
            meta["id"] = vec_id
            items.append((vec_id, vec, meta))

        if items:
            index.upsert(vectors=items, namespace=PINECONE_NAMESPACE)
            upserted += len(items)
            logging.info(f"⬆️ Upserted {upserted}/{len(stories)}")

    logging.info("✅ Pinecone index updated successfully.")
