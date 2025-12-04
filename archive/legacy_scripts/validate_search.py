import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "stories-index")

# Import embed function from vector_search with fallback names
try:
    from vector_search import embed as embed
except ImportError:
    try:
        from vector_search import embed_query as embed
    except ImportError:
        try:
            from vector_search import get_embedding as embed
        except ImportError:
            raise ImportError(
                "No embedding function (embed, embed_query, get_embedding) found in vector_search.py"
            )

# Load stories dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "echo_star_stories.jsonl")
stories = []
with open(DATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        stories.append(json.loads(line))

# Prepare corpus for FAISS fallback
corpus_embeddings = None
corpus_texts = None


def search_pinecone(query_embedding, top_k=5, threshold=0.25):
    from pinecone import Pinecone

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    print("Index stats:", stats.to_dict() if hasattr(stats, "to_dict") else stats)

    if hasattr(query_embedding, "tolist"):
        query_embedding = query_embedding.tolist()

    results_obj = index.query(
        vector=query_embedding, top_k=top_k, include_metadata=True, namespace="default"
    )

    if hasattr(results_obj, "to_dict"):
        results_dict = results_obj.to_dict()
    else:
        results_dict = results_obj if isinstance(results_obj, dict) else {}

    matches = results_dict.get("matches", [])
    filtered = filter_results(matches, threshold)

    print(
        f"DEBUG number of matches (pre-filter): {len(matches)} | (post-filter): {len(filtered)}"
    )

    if not filtered:
        print("⚠️ Query deemed irrelevant or too weak to match professional stories.")
    return filtered


def search_faiss(query_embedding, top_k=3):
    import numpy as np
    import faiss

    global corpus_embeddings, corpus_texts
    # Prepare corpus if not already loaded
    if corpus_embeddings is None:
        corpus_texts = [
            story.get("title", "") + " " + story.get("content", "") for story in stories
        ]
        corpus_embeddings = [embed(text) for text in corpus_texts]
        corpus_embeddings = np.stack(corpus_embeddings).astype("float32")
        # Build the index
        dim = corpus_embeddings.shape[1]
        faiss_index = faiss.IndexFlatL2(dim)
        faiss_index.add(corpus_embeddings)
        search_faiss.faiss_index = faiss_index
    else:
        faiss_index = search_faiss.faiss_index
    query_vec = np.array(query_embedding, dtype="float32").reshape(1, -1)
    D, I = faiss_index.search(query_vec, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        results.append({"score": float(-score), "idx": int(idx)})
    return results


def filter_results(matches, threshold=0.25):
    """Filter Pinecone results by similarity threshold."""
    if not matches:
        return []
    return [m for m in matches if m.get("score", 0) >= threshold]


def print_results(query, results, backend):
    print(f"\nQuery: {query}")
    print(f"Backend: {backend}")
    if not results:
        print(
            "⚠️ That question isn’t relevant to my professional portfolio. "
            "Please ask about my experience, skills, or professional stories."
        )
        return
    for i, r in enumerate(results):
        if backend == "pinecone":
            score = r["score"]
            meta = r.get("metadata", {})
            title = meta.get("title", "(no title)")
        else:
            score = r["score"]
            idx = r["idx"]
            title = stories[idx].get("title", "(no title)")
        print(f"{i+1}. Score: {score:.4f} | Title: {title}")


def main():
    test_query = "A story about a robot learning to love"
    nonsense_query = "baseball caps at Walmart"
    top_k = 3

    # Embed queries
    test_query_emb = embed(test_query)
    nonsense_query_emb = embed(nonsense_query)
    print("DEBUG embedding length test_query:", len(test_query_emb))
    print("DEBUG embedding length nonsense_query:", len(nonsense_query_emb))

    if VECTOR_BACKEND.lower() == "pinecone":
        # --- Run search on first query ---
        results = search_pinecone(test_query_emb, top_k)
        print("DEBUG raw test_query results:", results)
        print_results(test_query, results, "pinecone")

        # --- Run search on nonsense query ---
        results = search_pinecone(nonsense_query_emb, top_k)
        print("DEBUG raw nonsense_query results:", results)
        print_results(nonsense_query, results, "pinecone")

        # Always run debug
        debug_pinecone_index()
    else:
        results = search_faiss(test_query_emb, top_k)
        print_results(test_query, results, "faiss")
        results = search_faiss(nonsense_query_emb, top_k)
        print_results(nonsense_query, results, "faiss")


def debug_pinecone_index():
    from pinecone import Pinecone
    import numpy as np

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    # Confirm available indexes
    try:
        print("DEBUG available indexes:", pc.list_indexes())
    except Exception as e:
        print("DEBUG list_indexes failed:", e)

    try:
        stats = index.describe_index_stats()
        print(
            "DEBUG Index stats:",
            stats.to_dict() if hasattr(stats, "to_dict") else stats,
        )
        namespaces = []
        namespace_counts = {}
        if hasattr(stats, "get"):
            ns_dict = stats.get("namespaces", {})
            if ns_dict:
                namespaces = list(ns_dict.keys())
                for ns in namespaces:
                    count = ns_dict[ns].get("vector_count", 0)
                    namespace_counts[ns] = count
        print(f"DEBUG namespaces and counts: {namespace_counts}")

        # Use a zero vector to query real matches and IDs
        dim = len(embed("test"))
        zero_vector = [0.0] * dim
        try:
            zero_res = index.query(vector=zero_vector, top_k=10, include_metadata=True)
            if hasattr(zero_res, "to_dict"):
                zero_res_printable = zero_res.to_dict()
            else:
                zero_res_printable = zero_res
            matches = (
                zero_res_printable.get("matches", [])
                if isinstance(zero_res_printable, dict)
                else []
            )
            if matches:
                print("DEBUG first 5 real IDs and metadata from zero vector query:")
                for m in matches[:5]:
                    print(f"   ID: {m.get('id')}, Metadata: {m.get('metadata')}")
            else:
                print("DEBUG zero vector query returned no matches")
        except Exception as e:
            print("DEBUG zero vector query failed:", e)

        # Direct fetch of known IDs
        try:
            fetch_res = index.fetch(ids=["0", "1", "2"], namespace="default")
            if hasattr(fetch_res, "to_dict"):
                fetch_res_printable = fetch_res.to_dict()
            else:
                fetch_res_printable = fetch_res
            print(
                "DEBUG sample fetch result for IDs ['0','1','2']:", fetch_res_printable
            )
        except Exception as e:
            print("DEBUG direct fetch failed:", e)
    except Exception as e:
        print("DEBUG failed to get index stats or query:", e)


if __name__ == "__main__":
    main()
