import os

from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment
load_dotenv()

# Setup
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")
pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Check total vectors
stats = index.describe_index_stats()
print(f"✅ Index contains {stats['total_vector_count']} vectors.\n")

# Use dummy vector with correct dimension (384)
dummy_vector = [0.0] * 384
results = index.query(vector=dummy_vector, top_k=5, include_metadata=True)

# Print story info
print("🔍 Sample stories in Pinecone:\n")
for match in results["matches"]:
    meta = match["metadata"]
    print(f"🆔 ID: {match['id']}")
    print(f"📌 Title: {meta.get('Title', 'N/A')}")
    print(f"🏷️ Tags: {meta.get('public_tags', '—')}")
    print(f"📝 Content Preview: {meta.get('content', '')[:100]}...\n")
