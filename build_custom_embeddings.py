"""
build_custom_embeddings.py

Reads enriched STAR story data from a JSONL file, generates embeddings (MiniLM),
and upserts them into a Pinecone index (or FAISS locally). It purges the target
Pinecone namespace before reindexing for a clean slate.

Env (via .env or shell):
  VECTOR_BACKEND=faiss | pinecone
  STORIES_JSONL=echo_star_stories_nlp.jsonl   # default if unset
  PINECONE_API_KEY=...
  PINECONE_INDEX_NAME=...
  PINECONE_NAMESPACE=default
"""

import json
import logging
import os
from typing import Any

# Optional backends
import faiss
import numpy as np
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s"
)
load_dotenv()

VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss").strip().lower()
STORIES_JSONL = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim


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
    # split on common separators if someone stored as string
    if ";" in s:
        return [x.strip() for x in s.split(";") if x.strip()]
    if "," in s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return [s]


def _join(parts: list[str]) -> str:
    return " ".join(p for p in parts if p)


def build_embedding_text(story: dict[str, Any]) -> str:
    """
    Build a rich, behavior-aware text representation for embeddings.

    We intentionally include:
    - Theme / Industry / Sub-category  → high-level positioning
    - 5PSummary                       → condensed narrative
    - Situation / Action / Result     → behavioral signals + context
    - Process (from 5P)              → how Matt works with people / systems
    - public_tags                    → search hooks

    This makes behavioral queries like "handled conflict" or
    "disagreements with leadership" much easier to match.
    """

    def _to_text(val, max_items: int = 3) -> str:
        """Convert string or list to space-joined text."""
        if not val:
            return ""
        if isinstance(val, list):
            return " ".join(str(p).strip() for p in val[:max_items] if str(p).strip())
        return str(val).strip()

    # High-level metadata
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

    # Core narrative fields
    summary_5p = (
        story.get("5PSummary", "").strip()
        if isinstance(story.get("5PSummary"), str)
        else ""
    )
    situation = _to_text(story.get("Situation"), max_items=2)
    task = _to_text(story.get("Task"), max_items=2)
    action = _to_text(
        story.get("Action"), max_items=3
    )  # More action = more behavioral signal
    result = _to_text(story.get("Result"), max_items=2)
    process_text = _to_text(story.get("Process"), max_items=3)

    # Tags
    tags = story.get("public_tags", "")
    if isinstance(tags, list):
        tags = ", ".join(tags)
    tags = tags.strip() if tags else ""

    parts: list[str] = []

    # Header framing
    header_bits = []
    if theme:
        header_bits.append(f"[{theme}]")
    if industry:
        header_bits.append(f"in {industry}")
    if sub_category:
        header_bits.append(f"({sub_category})")

    if header_bits:
        parts.append(" ".join(header_bits))

    # 5P summary (if present) as the lead
    if summary_5p:
        parts.append(f"Summary: {summary_5p}")

    # Classic STAR fields – these help behavioral questions a lot
    if situation:
        parts.append(f"Situation: {situation}")
    if task:
        parts.append(f"Task: {task}")
    if action:
        parts.append(f"Action: {action}")
    if result:
        parts.append(f"Result: {result}")

    # Process (methods, collaboration style, practices)
    if process_text:
        parts.append(f"Process: {process_text}")

    # Tags at the tail – good semantic + keyword hooks
    if tags:
        parts.append(f"Keywords: {tags}")

    return " ".join(p for p in parts if p)


def build_metadata(story: dict[str, Any]) -> dict[str, Any]:
    """Compact but rich metadata for UI/snippets + Pinecone filters."""
    cat = story.get("Category", "")
    sub = story.get("Sub-category", "")
    theme = story.get("Theme", "")  # ← NEW 11.10.25
    domain = " / ".join([x for x in [cat, sub] if x])

    tags_list = _as_list(story.get("public_tags"))

    # Extract Industry and Division for hybrid search filtering
    industry = story.get("Industry", "").strip()
    division = story.get("Division", "").strip()

    # ADDED: Extract new fields
    employer = story.get("Employer", "").strip()
    project = story.get("Project", "").strip()
    complexity = story.get("Project Scope / Complexity", "").strip()
    status = story.get("Status", "").strip()

    meta = {
        # ═══════════════════════════════════════════════════════════
        # CANONICAL FIELDS (matches JSONL / Excel)
        # ═══════════════════════════════════════════════════════════
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
        "Theme": theme,  # ← MOVED HERE (canonical section)
        "Use Case(s)": _as_list(story.get("Use Case(s)")),
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
        # ═══════════════════════════════════════════════════════════
        # UI-FRIENDLY DUPLICATES (lowercase for easier UI mapping)
        # ═══════════════════════════════════════════════════════════
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
# Embed
# ---------------------------
model = SentenceTransformer(MODEL_NAME)
texts = [build_embedding_text(s) for s in stories]
# Log a sample embedding for verification
if texts:
    logging.info("📝 Sample embedding text (first story):")
    logging.info(f"   {texts[0][:500]}...")

    # ← ADD THIS: Check the CI/CD story specifically
    cicd_idx = next(
        (
            i
            for i, s in enumerate(stories)
            if 'cloud-native-architecture-cicd' in s.get('id', '')
        ),
        None,
    )
    if cicd_idx:
        logging.info("📝 CI/CD story FULL embedding text:")
        logging.info(f"{texts[cicd_idx]}")  # ← No truncation, show EVERYTHING
        logging.info(f"Length: {len(texts[cicd_idx])} characters")
    ns_idx = next(
        (i for i, s in enumerate(stories) if 'norfolk-southern' in s.get('id', '')),
        None,
    )
    if ns_idx:
        logging.info("📝 Norfolk Southern FULL embedding text:")
        logging.info(f"{texts[ns_idx]}")
        logging.info(f"Length: {len(texts[ns_idx])} characters")
embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

# ---------------------------
# Pinecone or FAISS
# ---------------------------
if VECTOR_BACKEND == "pinecone":
    if not (PINECONE_API_KEY and PINECONE_INDEX_NAME):
        raise RuntimeError(
            "Pinecone selected but PINECONE_API_KEY or PINECONE_INDEX_NAME is missing."
        )

    pc = Pinecone(api_key=PINECONE_API_KEY)
    logging.info(
        f"[INFO] Using Pinecone index='{PINECONE_INDEX_NAME}', namespace='{PINECONE_NAMESPACE}'"
    )

    # Ensure index exists
    existing = [i.name for i in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing:
        raise ValueError(
            f"Index '{PINECONE_INDEX_NAME}' does not exist. Available: {existing}"
        )

    index = pc.Index(PINECONE_INDEX_NAME)

    # Purge namespace (best effort across SDK variants)
    try:
        logging.info("🧹 Purging namespace (delete_all=True)…")
        index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)  # v3 SDK
    except Exception:
        # Fallback: delete by id range (not perfect, but avoids stale dupes)
        ids_guess = [f"story-{i}" for i in range(max(1, len(stories) * 2))]
        logging.info("🧹 Fallback purge by guessed ids…")
        index.delete(vectors=ids_guess, namespace=PINECONE_NAMESPACE)

    # Upsert in batches
    batch = 200
    upserted = 0
    for start in range(0, len(stories), batch):
        items = []
        for i in range(start, min(start + batch, len(stories))):
            vec = embeddings[i]
            if np.any(np.isnan(vec)):
                logging.warning(f"❌ Skipping story-{i}: embedding contains NaNs")
                continue
            meta = build_metadata(stories[i])
            vec_id = str(meta.get("id") or f"story-{i}")
            meta["id"] = vec_id  # ensure metadata ID matches vector ID
            items.append((vec_id, vec.tolist(), meta))
            logging.debug(f"Prepared upsert ID={vec_id} with dim={len(vec)}")
        if items:
            index.upsert(vectors=items, namespace=PINECONE_NAMESPACE)
            upserted += len(items)
            logging.info(f"⬆️ Upserted {upserted}/{len(stories)}")

    logging.info("✅ Pinecone index updated successfully.")

else:
    # FAISS local index
    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(np.array(embeddings, dtype="float32"))
    os.makedirs("faiss_index", exist_ok=True)
    faiss.write_index(faiss_index, "faiss_index/index.faiss")
    with open("faiss_index/story_metadata.json", "w") as f:
        json.dump([build_metadata(s) for s in stories], f, indent=2)
    logging.info("✅ FAISS index + metadata saved to ./faiss_index/")
