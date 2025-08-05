import os
# Force CPU on Streamlit Cloud (prevents CUDA meta-tensor issues)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from sentence_transformers import SentenceTransformer
import numpy as np
import json

# --- Backend Configuration: Model, Vector Store, and Environment Variables ---
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")

# Canonical HF ID; explicitly load on CPU
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_ID, device="cpu")

def embed_query(query: str):
    return model.encode([query])[0]

def search(query_embedding, top_k=5):
    if VECTOR_BACKEND == "pinecone":
        import pinecone
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        response = index.query(
            vector=query_embedding.tolist(),
            top_k=top_k,
            include_metadata=True,
            namespace=PINECONE_NAMESPACE
        )
        return [match["metadata"] for match in response["matches"]]
    else:
        import faiss
        index = faiss.read_index("faiss_index/index.faiss")
        with open("faiss_index/story_metadata.json", "r") as f:
            metadata = json.load(f)
        D, I = index.search(np.array([query_embedding]), top_k)
        return [metadata[int(i)] for i in I[0]]

def rerank_by_metadata(stories, domain_filter=None, competency_filter=None):
    filtered = stories
    if domain_filter and domain_filter.strip().lower() != "(all)":
        filtered = [
            s for s in filtered
            if s.get("Sub-category", "").strip().lower() == domain_filter.strip().lower()
        ]
    if competency_filter:
        filtered = [
            s for s in filtered
            if any(
                tag.strip().lower() in (s.get("public_tags") or "").lower().split(",")
                for tag in competency_filter
            )
        ]
    return filtered