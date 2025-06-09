import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone
load_dotenv()

VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss")  # default to faiss if not set

# Load enriched STAR stories
file_path = "echo_star_stories.jsonl"
stories = []
with open(file_path, "r") as f:
    for line in f:
        stories.append(json.loads(line.strip()))
print(f"🔍 Total stories found: {len(stories)}")


# Initialize the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Prepare documents and metadata
texts = []
metadata = []

for story in stories:
    content = f"{story.get('search_context', '')}\n\n{story['content']}"
    texts.append(content)
    metadata.append({
        "Title": story.get("Title", "Untitled"),
        "Client": story.get("Client", "Unknown"),
        "Role": story.get("Role", "Unknown"),
        "Category": story.get("Category", "Uncategorized"),
        "Use Case(s)": story.get("Use Case(s)", []),
        "Situation": story.get("Situation", []),
        "Task": story.get("Task", []),
        "Action": story.get("Action", []),
        "Result": story.get("Result", []),
        "content": story.get("content", ""),  # <-- ✅ Add this
        "public_tags": story.get("public_tags", "")  # <-- ✅ Add this too
    })

# Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

if VECTOR_BACKEND == "pinecone":
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    print(f"📌 Using Pinecone index: {index_name}")

    # Ensure index exists (optional but good practice)
    index_names = [index.name for index in pc.list_indexes()]
    if index_name not in index_names:
        raise ValueError(f"Index '{index_name}' does not exist. Available indexes: {index_names}")

    index = pc.Index(index_name)

    # 🔥 Purge existing index entries
    print("🧹 Purging existing Pinecone index data...")
    existing_ids = [f"story-{i}" for i in range(len(stories))]
    index.delete(ids=existing_ids)
    print("✅ Purge complete.")

   # index.upsert([
    #    (f"story-{i}", embedding.tolist(), metadata[i])
    #   for i, embedding in enumerate(embeddings)
   # ])
    # Prepare and validate upsert data
    upsert_items = []
    for i, embedding in enumerate(embeddings):
        if np.any(np.isnan(embedding)):
            print(f"❌ Skipping story-{i}: embedding contains NaNs")
            continue
        upsert_items.append((f"story-{i}", embedding.tolist(), metadata[i]))

    print(f"📦 Ready to upsert {len(upsert_items)} stories to Pinecone")

    # Then upsert
    index.upsert(upsert_items)


    print("✅ Pinecone index updated successfully.")
else:
    # Build FAISS index
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    # Save index and metadata
    os.makedirs("faiss_index", exist_ok=True)
    faiss.write_index(index, "faiss_index/index.faiss")
    with open("faiss_index/story_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("✅ Custom embeddings built and saved to faiss_index/")
