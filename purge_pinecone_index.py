import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

# Setup Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")

# Confirm index exists
index_names = [index.name for index in pc.list_indexes()]
if index_name not in index_names:
    raise ValueError(f"Index '{index_name}' not found. Available: {index_names}")

index = pc.Index(index_name)

# Optional: check how many vectors exist before purging
stats = index.describe_index_stats()
vector_count = stats.get("total_vector_count", 0)
print(f"🧮 Existing vector count: {vector_count}")

# Purge everything
if vector_count > 0:
    index.delete(delete_all=True)
    print("🧼 All vectors deleted from Pinecone index.")
else:
    print("✅ Index already empty.")
