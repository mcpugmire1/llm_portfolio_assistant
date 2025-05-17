import pickle
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from collections import defaultdict

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")

# Silence tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load FAISS index and metadata
index = faiss.read_index("faiss_index/index.faiss")
with open("faiss_index/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Load enriched STAR stories
with open("star_stories_llm_enriched_with_search.json", "r") as f:
    stories = json.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def format_response_from_stories(story_indices, max_per_client=1, max_stories=5):
    client_seen = defaultdict(int)
    output = []

    for idx in story_indices:
        if idx >= len(stories):
            continue
        story = stories[idx]
        client = story.get("Client") or story.get("Client/Company") or "Internal (Accenture)"
        if client_seen[client] >= max_per_client:
            continue
        client_seen[client] += 1

        title = story.get("Title", "Untitled")
        role = story.get("Role", "")
        category = story.get("Category", "")
        use_case_raw = story.get("Use Case(s)", [])
        use_case = ", ".join(use_case_raw if isinstance(use_case_raw, list) else [use_case_raw])
        impact_line = story["content"].strip().split("R:")[-1].strip() if "R:" in story["content"] else story["content"].strip()

        summary = (
            f"> {title} ({client}, {role})\n"
            f"  Category: {category}\n"
            f"  Use Case(s): {use_case}\n"
            f"  Impact: {impact_line}"
        )
        output.append(summary)

        if len(output) >= max_stories:
            break

    return "\n\n".join(output)

def generate_chat_response(query, k=12):
    print("🔍 Embedding query and retrieving top matches...")
    query_embedding = model.encode([query])[0]
    D, I = index.search(np.array([query_embedding]), k)
    print("✅ Retrieved relevant STAR stories.")
    return format_response_from_stories(I[0])

# CLI loop
if __name__ == "__main__":
    while True:
        query = input("\nAsk about Matt's experience (or type 'exit'): ")
        if query.lower() == "exit":
            break
        answer = generate_chat_response(query)
        print(f"\nAnswer:\n{answer}")

