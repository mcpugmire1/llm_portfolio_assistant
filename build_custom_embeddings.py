"""
build_custom_embeddings.py

This script reads enriched STAR story data from a JSONL file, generates OpenAI embeddings
using the specified model, and upserts the results into a Pinecone index for semantic search.
It also ensures existing vectors in the namespace are purged before reindexing, providing a clean slate.

Assumes environment variables are set for Pinecone and OpenAI API keys and configuration.
"""
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)

load_dotenv()

"""
Main execution logic:
- Loads enriched STAR story records from JSONL.
- Generates embeddings using OpenAI.
- Batches and upserts them into Pinecone under a defined namespace.
- Handles errors and skips empty content.
"""

VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss")  # default to faiss if not set

# Load enriched STAR stories
file_path = "echo_star_stories_nlp.jsonl"
stories = []
with open(file_path, "r") as f:
    for line in f:
        stories.append(json.loads(line.strip()))
logging.info(f"\U0001F50D Total stories found: {len(stories)}")

# Initialize the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Prepare documents and metadata
texts = []
metadata = []

# Minimal semantic embedding input using only core 5P fields
for story in stories:
    # Enrich content for embedding
    enriched_content = f"""
Purpose: {story.get('Purpose', '')}
Performance: {'; '.join(story.get('Performance', []))}
Process: {'; '.join(story.get('Process', []))}
""".strip()

    texts.append(enriched_content)

    metadata.append({
        "id": story.get("id"),
        "Title": story.get("Title", "Untitled"),
        "Client": story.get("Client", "Unknown"),
        "Role": story.get("Role", "Unknown"),
        "Category": story.get("Category", "Uncategorized"),
        "Sub-category": story.get("Sub-category", ""),
        "Competencies": story.get("Competencies", []),
        "Solution / Offering": story.get("Solution / Offering", ""),
        "Use Case(s)": story.get("Use Case(s)", []),
        "Situation": story.get("Situation", []),
        "Task": story.get("Task", []),
        "Action": story.get("Action", []),
        "Result": story.get("Result", []),
        "public_tags": story.get("public_tags", ""),
        "Person": story.get("Person", ""),
        "Place": story.get("Place", ""),
        "Purpose": story.get("Purpose", ""),
        "Performance": story.get("Performance", []),
        "Process": story.get("Process", []),
        "5PSummary": story.get("5PSummary", "")
    })

# Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

if VECTOR_BACKEND == "pinecone":
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    namespace = os.getenv("PINECONE_NAMESPACE", "default")

    logging.info(f"[INFO] Using Pinecone index: {index_name} and namespace: {namespace}")
    

    # Ensure index exists
    index_names = [index.name for index in pc.list_indexes()]
    if index_name not in index_names:
        raise ValueError(f"Index '{index_name}' does not exist. Available indexes: {index_names}")

    index = pc.Index(index_name)

    logging.info("\U0001f9f9 Purging existing Pinecone index data...")
    existing_ids = [f"story-{i}" for i in range(len(stories))]
    
    # Get current namespaces
    stats = index.describe_index_stats()
    existing_namespaces = stats.get("namespaces", {}).keys()

    if namespace in existing_namespaces:
        index.delete(ids=existing_ids, namespace=namespace)
        logging.info(f"✅ Deleted {len(existing_ids)} vectors from namespace '{namespace}'")
    else:
        logging.info(f"⚠️ Namespace '{namespace}' not found — skipping delete")
        logging.info("✅ Purge complete.")

    upsert_items = []
    for i, embedding in enumerate(embeddings):
        if np.any(np.isnan(embedding)):
            logging.warning(f"❌ Skipping story-{i}: embedding contains NaNs")
            continue
        upsert_items.append((f"story-{i}", embedding.tolist(), metadata[i]))

    logging.info(f"📦 Ready to upsert {len(upsert_items)} stories to Pinecone")
    index.upsert(upsert_items, namespace=namespace)
    logging.info("✅ Pinecone index updated successfully.")

else:
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    logging.info("📁 Saving FAISS index and metadata locally...")

    os.makedirs("faiss_index", exist_ok=True)
    faiss.write_index(index, "faiss_index/index.faiss")
    with open("faiss_index/story_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logging.info("✅ Custom embeddings built and saved to faiss_index/")
