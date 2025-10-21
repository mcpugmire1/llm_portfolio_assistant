"""Pinecone vector database service."""

import streamlit as st
from typing import Optional, List
from config.settings import get_conf
from config.debug import DEBUG
import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Config / constants
# =========================
VECTOR_BACKEND = (get_conf("VECTOR_BACKEND", "faiss") or "faiss").lower()
OPENAI_API_KEY = get_conf("OPENAI_API_KEY")
PINECONE_API_KEY = get_conf("PINECONE_API_KEY")
PINECONE_INDEX_NAME = get_conf("PINECONE_INDEX_NAME")  # no default
PINECONE_NAMESPACE = get_conf("PINECONE_NAMESPACE")  # no default

PINECONE_ALLOW_CREATE = str(
    get_conf("PINECONE_ALLOW_CREATE", "false")
).strip().lower() in {"1", "true", "yes", "on"}

PINECONE_TRY_DEFAULT_NS = str(
    get_conf("PINECONE_TRY_DEFAULT_NS", "false")
).strip().lower() in {"1", "true", "yes", "on"}

# Guard: Require Pinecone config ONLY if VECTOR_BACKEND == "pinecone"
if VECTOR_BACKEND == "pinecone":
    missing = []
    if not PINECONE_API_KEY:
        missing.append("PINECONE_API_KEY")
    if not PINECONE_INDEX_NAME:
        missing.append("PINECONE_INDEX_NAME")
    if not PINECONE_NAMESPACE:
        missing.append("PINECONE_NAMESPACE")
    if missing:
        raise RuntimeError(
            f"Missing required Pinecone config: {', '.join(missing)}. Set them in st.secrets or .env"
        )

# Lazy Pinecone init only if selected
pinecone_index = None
if VECTOR_BACKEND == "pinecone":
    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        # Do NOT downgrade to FAISS silently; keep backend as pinecone and retry lazily later.
        st.warning(f"Pinecone init failed at startup; will retry lazily. ({e})")
        pinecone_index = None

PINECONE_MIN_SIM = 0.15  # gentler gate: surface more semantically-close hits
_DEF_DIM = 384  # stub embedding size to keep demo self-contained
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional

# 🔧 Hybrid score weights (tune these!)
W_PC = 0.8  # semantic (Pinecone vector match)
W_KW = 0.2  # keyword/token overlap

# Centralized retrieval pool size for semantic search / Pinecone
SEARCH_TOP_K = 100  # Increased to capture more industry-specific results
# Centralized retrieval pool size for semantic search / Pinecone
SEARCH_TOP_K = 100  # Increased to capture more industry-specific results

# =========================
# Config / constants
# =========================
PINECONE_MIN_SIM = 0.15  # gentler gate: surface more semantically-close hits
_DEF_DIM = 384  # stub embedding size to keep demo self-contained
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")  # optional

# 🔧 Hybrid score weights (tune these!)
W_PC = 0.8  # semantic (Pinecone vector match)
W_KW = 0.2  # keyword/token overlap

# Centralized retrieval pool size for semantic search / Pinecone
SEARCH_TOP_K = 100  # Increased to capture more industry-specific results


# =========================
# Safe Pinecone wiring (optional)
# =========================
try:
    from pinecone import Pinecone  # type: ignore
except Exception:
    Pinecone = None  # keeps the app running without Pinecone installed

_PINECONE_API_KEY = get_conf("PINECONE_API_KEY")
_PINECONE_INDEX = PINECONE_INDEX_NAME or get_conf("PINECONE_INDEX_NAME")
_PC = None
_PC_INDEX = None


def _init_pinecone():
    """Lazy init of Pinecone client + index (no-op if unavailable)."""
    global _PC, _PC_INDEX
    if _PC_INDEX is not None:
        return _PC_INDEX
    if not (_PINECONE_API_KEY and Pinecone):
        return None
    try:
        _PC = Pinecone(api_key=_PINECONE_API_KEY)
        # Inspect existing indexes (and their dimensions) once
        idx_list = _PC.list_indexes().indexes
        existing = {i.name: i for i in idx_list}
        if _PINECONE_INDEX not in existing:
            if DEBUG:
                print(
                    f"DEBUG Pinecone: index '{_PINECONE_INDEX}' missing. allow_create={PINECONE_ALLOW_CREATE or DEBUG}"
                )
            if PINECONE_ALLOW_CREATE or DEBUG:
                _PC.create_index(
                    name=_PINECONE_INDEX, dimension=_DEF_DIM, metric="cosine"
                )
            else:
                # Do not create in prod unless explicitly allowed
                return None
        else:
            # Validate dimension if available
            try:
                dim = getattr(existing[_PINECONE_INDEX], "dimension", None)
                if dim and int(dim) != int(_DEF_DIM):
                    if DEBUG:
                        print(
                            f"DEBUG Pinecone: index dim mismatch (have={dim}, want={_DEF_DIM}); refusing to use."
                        )
                    return None
            except Exception:
                pass

        _PC_INDEX = _PC.Index(_PINECONE_INDEX)
        return _PC_INDEX
    except Exception as e:
        if DEBUG:
            print(f"DEBUG Pinecone init error: {e}")
        return None

def _safe_json(obj):
    """Convert Pinecone objects to JSON-serializable dicts."""
    try:
        # pinecone client may expose one of these:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):  # pydantic v1
            return obj.dict()
    except Exception:
        pass
    import json

    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return {"_raw": str(obj)}
    
def _summarize_index_stats(stats: dict) -> dict:
    """Return a compact view of Pinecone index stats."""
    if not isinstance(stats, dict):
        return {}
    namespaces = stats.get("namespaces") or {}
    dims = stats.get("dimension")
    total_vecs = 0
    by_ns = {}
    for ns, info in namespaces.items():
        count = (info or {}).get("vector_count") or 0
        by_ns[ns or ""] = int(count)
        total_vecs += int(count)
    return {
        "dimension": int(dims) if dims else None,
        "total_vectors": int(total_vecs),
        "namespaces": by_ns,  # {"default": 115, "": 0, ...}
    }