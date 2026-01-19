"""Pinecone vector database service."""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from config.debug import DEBUG
from config.settings import get_conf
from utils.scoring import _hybrid_score, _keyword_score_for_story

load_dotenv()


def _safe_session_get(key: str, default=None):
    """Safely get session state, works outside Streamlit context."""
    try:
        return st.session_state.get(key, default)
    except Exception:
        return default


def _safe_session_set(key: str, value):
    """Safely set session state, no-op outside Streamlit context."""
    try:
        st.session_state[key] = value
    except Exception:
        pass


# =========================
# Config / constants
# =========================
VECTOR_BACKEND = (get_conf("VECTOR_BACKEND", "faiss") or "faiss").lower()
OPENAI_API_KEY = get_conf("OPENAI_API_KEY")
PINECONE_API_KEY = get_conf("PINECONE_API_KEY")
PINECONE_INDEX_NAME = get_conf("PINECONE_INDEX_NAME")
PINECONE_NAMESPACE = get_conf("PINECONE_NAMESPACE")

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
        st.warning(f"Pinecone init failed at startup; will retry lazily. ({e})")
        pinecone_index = None

# =========================
# Embedding config
# =========================
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI model
_DEF_DIM = 1536  # OpenAI text-embedding-3-small dimension

# =========================
# Search config
# =========================
PINECONE_MIN_SIM = 0.15
DATA_FILE = os.getenv("STORIES_JSONL", "echo_star_stories_nlp.jsonl")

# Hybrid score weights
W_PC = 1.0
W_KW = 0.0

# Retrieval pool size
SEARCH_TOP_K = 100


# =========================
# Safe Pinecone wiring
# =========================
try:
    from pinecone import Pinecone
except Exception:
    Pinecone = None

_PINECONE_API_KEY = get_conf("PINECONE_API_KEY")
_PINECONE_INDEX = PINECONE_INDEX_NAME or get_conf("PINECONE_INDEX_NAME")
_PC = None
_PC_INDEX = None


def _init_pinecone():
    """Lazy init of Pinecone client + index."""
    global _PC, _PC_INDEX
    if _PC_INDEX is not None:
        return _PC_INDEX
    if not (_PINECONE_API_KEY and Pinecone):
        return None
    try:
        _PC = Pinecone(api_key=_PINECONE_API_KEY)
        idx_list = _PC.list_indexes().indexes
        existing = {i.name: i for i in idx_list}
        if _PINECONE_INDEX not in existing:
            if DEBUG:
                print(f"DEBUG Pinecone: index '{_PINECONE_INDEX}' missing.")
            return None

        _PC_INDEX = _PC.Index(_PINECONE_INDEX)
        return _PC_INDEX
    except Exception as e:
        if DEBUG:
            print(f"DEBUG Pinecone init error: {e}")
        return None


def _safe_json(obj):
    """Convert Pinecone objects to JSON-serializable dicts."""
    try:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
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
        "namespaces": by_ns,
    }


def pinecone_semantic_search(
    query: str, filters: dict, stories: list, top_k: int = SEARCH_TOP_K
) -> list[dict] | None:
    idx = _init_pinecone()
    if not idx or not query:
        if DEBUG:
            print(
                f"DEBUG Pinecone: skipped (idx={'present' if idx else 'none'}, query_len={len(query or '')})"
            )
        return None

    # Build filter for Pinecone
    pc_filter = {}
    if filters.get("domains"):
        pc_filter["domain"] = {"$in": filters["domains"]}
    if filters.get("clients"):
        pc_filter["client"] = {"$in": filters["clients"]}

    try:
        qvec = _embed(query)
        if DEBUG:
            print(f"DEBUG Embeddings: qvec_dim={len(qvec)} model={EMBEDDING_MODEL}")
            print(
                f"DEBUG Pinecone query → index={_PINECONE_INDEX or PINECONE_INDEX_NAME}, namespace={PINECONE_NAMESPACE}"
            )

        res = idx.query(
            vector=qvec,
            top_k=top_k,
            include_metadata=True,
            namespace=PINECONE_NAMESPACE,
            filter=pc_filter or None,
        )

        matches = getattr(res, "matches", []) or []

        # --- DEBUG: snapshot Pinecone info to session (compact) ---
        if DEBUG:
            try:
                preview = []
                for m in matches[:8]:
                    sid, score, meta = _extract_match_fields(m)
                    found = any(str(s.get("id")) == str(sid) for s in stories)
                    title = (meta or {}).get("title") or ""
                    client = (meta or {}).get("client") or ""
                    if title and client:
                        title = f"{client} — {title}"
                    if len(title) > 72:
                        title = title[:69] + "…"
                    preview.append(
                        {
                            "id": str(sid or ""),
                            "score": float(score or 0.0),
                            "title": title,
                            "in_STORIES": bool(found),
                        }
                    )

                try:
                    raw_stats = idx.describe_index_stats()
                except Exception:
                    raw_stats = {}
                stats_compact = _summarize_index_stats(_safe_json(raw_stats))

                _safe_session_set(
                    "__pc_debug__",
                    {
                        "index": _PINECONE_INDEX or PINECONE_INDEX_NAME,
                        "namespace": PINECONE_NAMESPACE or "",
                        "match_count": len(matches),
                        "preview": preview,
                        "weights": {"W_PC": W_PC, "W_KW": W_KW},
                        "min_sim": PINECONE_MIN_SIM,
                        "stats": stats_compact,
                    },
                )
            except Exception as e:
                print("DEBUG: Pinecone snapshot error:", e)
        # --- end DEBUG snapshot ---

        hits = []
        # Safely clear session state dicts (works outside Streamlit context)
        pc_last_ids = _safe_session_get("__pc_last_ids__", {})
        if pc_last_ids:
            pc_last_ids.clear()
        pc_snippets = _safe_session_get("__pc_snippets__", {})
        if pc_snippets:
            pc_snippets.clear()

        for m in matches:
            sid, score, meta = _extract_match_fields(m)
            if not sid:
                continue

            story = next((s for s in stories if str(s.get("id")) == str(sid)), None)
            if not story:
                continue

            snip = meta.get("summary") or meta.get("snippet") or ""
            if snip and pc_snippets is not None:
                try:
                    pc_snippets[str(sid)] = snip
                except Exception:
                    pass

            kw = _keyword_score_for_story(story, query)
            blended = _hybrid_score(score, kw)
            if pc_last_ids is not None:
                try:
                    pc_last_ids[str(sid)] = blended
                except Exception:
                    pass

            if DEBUG:
                try:
                    title_dbg = (story.get("title") or "")[:60]
                    client_dbg = story.get("client") or ""
                    print(
                        f"DEBUG Hit: id={sid} pc={score:.3f} kw={kw:.3f} blend={blended:.3f}  [{client_dbg}] {title_dbg}"
                    )
                except Exception:
                    pass

            hits.append(
                {
                    "story": story,
                    "pc_score": score,
                    "kw_score": kw,
                    "score": blended,
                    "snippet": snip,
                }
            )

        st.session_state["last_results"] = hits
        st.session_state["last_sources"] = [
            {
                "id": h["story"].get("id"),
                "title": h["story"].get("title"),
                "client": h["story"].get("client"),
            }
            for h in hits[:5]
        ]

        hits.sort(key=lambda h: h.get("score", 0.0), reverse=True)

        strong = [
            h for h in hits if (h.get("pc_score", 0.0) or 0.0) >= PINECONE_MIN_SIM
        ]
        if strong:
            st.session_state["__pc_suppressed__"] = False
            return strong
        st.session_state["__pc_suppressed__"] = True
        return hits[:3]

    except Exception as e:
        if DEBUG:
            print(f"DEBUG Pinecone query error: {e}")
        return None


# =========================
# OpenAI Embeddings
# =========================
_OPENAI_CLIENT = None


def _get_openai_client():
    """Lazy init OpenAI client."""
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        _OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
    return _OPENAI_CLIENT


def _embed(text: str) -> list[float]:
    """
    Generate query embedding using OpenAI text-embedding-3-small.
    Must match the model used in build_custom_embeddings.py.
    """
    if not text:
        return [0.0] * _DEF_DIM

    try:
        client = _get_openai_client()
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        return response.data[0].embedding
    except Exception as e:
        if DEBUG:
            print(f"DEBUG OpenAI embedding error: {e}")
        # Return zero vector on error (will result in poor matches but won't crash)
        return [0.0] * _DEF_DIM


def _extract_match_fields(m) -> tuple[str, float, dict]:
    """
    Normalize a Pinecone match object or dict into (sid, score, metadata).
    """
    try:
        if isinstance(m, dict):
            meta = m.get("metadata") or {}
            sid = meta.get("id") or m.get("id")
            score = float(m.get("score") or 0.0)
        else:
            meta = getattr(m, "metadata", None) or {}
            sid = meta.get("id") or getattr(m, "id", None)
            score = float(getattr(m, "score", 0.0) or 0.0)
    except Exception:
        return None, 0.0, {}
    return sid, score, meta
