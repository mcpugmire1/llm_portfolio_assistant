import pickle
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Silence tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load FAISS index and metadata
index = faiss.read_index("faiss_index/index.faiss")
with open("faiss_index/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# Load stories
with open("star_stories_llm_enriched_with_search.json", "r") as f:
    stories = json.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def format_stories_grouped(story_indices, max_per_client=1, max_stories=5):
    client_seen = defaultdict(int)
    grouped = []

    for idx in story_indices:
        if idx >= len(stories):
            continue
        story = stories[idx]
        client = story.get("Client/Company", "Unknown")
        if client_seen[client] >= max_per_client:
            continue
        client_seen[client] += 1

        title = story.get("Title", "Untitled")
        category = story.get("Category", "")
        content = story["content"].strip()
        entry = f"**{title}** ({client}, {category})\n{content}"
        grouped.append(entry)

        if len(grouped) >= max_stories:
            break

    return "\n\n---\n\n".join(grouped)


def generate_chat_response(query, k=12):
    print("🔍 Embedding query and retrieving top matches...")
    query_embedding = model.encode([query])[0]
    D, I = index.search(np.array([query_embedding]), k)
    formatted_context = format_stories_grouped(I[0])

    system_prompt = (
        "You are Matt Pugmire. Always respond in first person, using 'I', 'my', and 'me'. "
        "These are your own STAR stories and career experiences — never refer to 'Matt' or 'the user'. "
        "When answering, highlight a few distinct examples with different clients or contexts. "
        "Use the story titles and clients to give the response structure and confidence. "
        "Be concise, confident, and personal — like you're speaking to a hiring manager."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"{query}\n\nHere are some relevant STAR stories:\n\n{formatted_context}",
        },
    ]

    print("📤 Sending query to OpenAI...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0.3
    )
    print("✅ Received response from OpenAI.")

    return response.choices[0].message.content


# CLI loop
if __name__ == "__main__":
    while True:
        query = input("\nAsk about Matt's experience (or type 'exit'): ")
        if query.lower() == "exit":
            break
        answer = generate_chat_response(query)
        print(f"\nAnswer:\n{answer}")
