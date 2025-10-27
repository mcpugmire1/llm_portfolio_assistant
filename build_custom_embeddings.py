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
import os
import logging
from typing import List, Dict, Any

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Optional backends
import faiss
from pinecone import Pinecone

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
def _as_list(v) -> List[str]:
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


def _join(parts: List[str]) -> str:
    return " ".join(p for p in parts if p)


def build_embedding_text_bak(story: Dict[str, Any]) -> str:
    """Rich, semantic text for the vector (order is intentional)."""
    title = story.get("Title", "")
    client = story.get("Client", "")
    role = story.get("Role", "")
    cat = story.get("Category", "")
    sub = story.get("Sub-category", "")
    domain = " / ".join([x for x in [cat, sub] if x])

    purpose = story.get("Purpose", "")
    performance = "; ".join(_as_list(story.get("Performance")))
    process = "; ".join(_as_list(story.get("Process")))
    situation = "; ".join(_as_list(story.get("Situation")))
    task = "; ".join(_as_list(story.get("Task")))
    action = "; ".join(_as_list(story.get("Action")))
    result = "; ".join(_as_list(story.get("Result")))
    use_cases = "; ".join(_as_list(story.get("Use Case(s)")))
    competencies = "; ".join(_as_list(story.get("Competencies")))
    public_tags = "; ".join(_as_list(story.get("public_tags")))
    fivep = story.get("5PSummary", "")

    return "\n".join(
        [
            f"Title: {title}",
            f"Client: {client}",
            f"Role: {role}",
            f"Domain: {domain}",
            f"Purpose: {purpose}",
            f"Performance: {performance}",
            f"Process: {process}",
            f"Situation: {situation}",
            f"Task: {task}",
            f"Action: {action}",
            f"Result: {result}",
            f"Use Cases: {use_cases}",
            f"Competencies: {competencies}",
            f"Tags: {public_tags}",
            f"5P: {fivep}",
        ]
    ).strip()

def build_embedding_text(story: Dict[str, Any]) -> str:
    """Natural language embedding optimized for semantic search"""

    summary = story.get("5PSummary", "").strip()
    industry = story.get("Industry", "").strip()
    place = story.get("Place", "").strip()

    if summary and len(summary) > 50:
        # Put industry context up front for stronger semantic signal
        if industry:
            return f"In {industry}: {summary}"
        elif place:
            return f"{summary} This work was done at {place}."
        return summary

    # Fallback: simple natural text
    title = story.get("Title", "")
    client = story.get("Client", "")
    situation = story.get("Situation", [""])[0] if story.get("Situation") else ""
    result = story.get("Result", [""])[0] if story.get("Result") else ""

    base_text = f"Project: {title} at {client}. {situation} {result}".strip()

    if industry:
        return f"In {industry}: {base_text}"
    return base_text

def build_metadata(story: Dict[str, Any]) -> Dict[str, Any]:
    """Compact but rich metadata for UI/snippets + Pinecone filters."""
    cat = story.get("Category", "")
    sub = story.get("Sub-category", "")
    domain = " / ".join([x for x in [cat, sub] if x])

    tags_list = _as_list(story.get("public_tags"))

    # Extract Industry and Division for hybrid search filtering
    industry = story.get("Industry", "").strip()
    division = story.get("Division", "").strip()

    # ADDED: Extract new fields
    employer = story.get("Employer", "").strip()           # ← NEW 10.27.25
    project = story.get("Project", "").strip()             # ← NEW 10.27.25
    complexity = story.get("Project Scope / Complexity", "").strip()  # ← NEW 10.27.25
    status = story.get("Status", "").strip()               # ← NEW 10.27.25


    meta = {
        # canonical (matches JSONL / Excel)
        "id": story.get("id"),
        "Title": story.get("Title", "Untitled"),
        "Employer": employer,                               # ← NEW 10.27.25
        "Division": division,
        "Role": story.get("Role", "Unknown"),
        "Client": story.get("Client", "Unknown"),
        "Project": project,                                 # ← NEW 10.27.25
        "Start_Date": story.get("Start_Date", ""),         # ← NEW 10.27.25
        "End_Date": story.get("End_Date", ""),             # ← NEW 10.27.25
        "Industry": industry,
        "Project Scope / Complexity": complexity,           # ← NEW 10.27.25
        "Category": cat,
        "Sub-category": sub,
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
        # UI-friendly duplicates (lowercase) to minimize UI mapping pain
        "title": story.get("Title", "Untitled"),
        "employer": employer.lower() if employer else "",   # ← NEW 10.27.25
        "division": division.lower() if division else "",
        "client": story.get("Client", "Unknown"),
        "role": story.get("Role", "Unknown"),
        "project": project.lower() if project else "",      # ← NEW 10.27.25
        "industry": industry.lower() if industry else "",
        "complexity": complexity.lower() if complexity else "",  # ← NEW 10.27.25
        "domain": domain,
        "tags": tags_list,
        # Snippet used in list view when results come from Pinecone
        "summary": story.get("5PSummary", ""),
    }
    return meta


# ---------------------------
# Load data
# ---------------------------
stories: List[Dict[str, Any]] = []
with open(STORIES_JSONL, "r") as f:
    for line in f:
        if line.strip():
            stories.append(json.loads(line))
logging.info(f"🔎 Loaded {len(stories)} stories from {STORIES_JSONL}")

# ---------------------------
# Embed
# ---------------------------
model = SentenceTransformer(MODEL_NAME)
texts = [build_embedding_text(s) for s in stories]
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
