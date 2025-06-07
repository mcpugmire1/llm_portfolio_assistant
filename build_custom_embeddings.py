import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load enriched STAR stories
with open("star_stories_llm_enriched_with_search.json", "r") as f:
    stories = json.load(f)
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
        "Result": story.get("Result", [])
    })

# Generate embeddings
embeddings = model.encode(texts, show_progress_bar=True)

if VECTOR_BACKEND == "pinecone":
    pinecone_index.upsert([
        (f"story-{i}", embedding.tolist(), metadata[i])
        for i, embedding in enumerate(embeddings)
    ])
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
