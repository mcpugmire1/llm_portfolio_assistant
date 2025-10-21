"""
Ask MattGPT Page

Interactive chat interface for conversational exploration of Matt's experience.
Uses semantic search and Pinecone to retrieve relevant project stories.
"""

import streamlit as st
from typing import List, Dict, Optional
import json
from datetime import datetime
import os, re, time, textwrap, json
from config.debug import DEBUG
from config.settings import get_conf
from utils.ui_helpers import dbg, safe_container
from utils.validation import is_nonsense, token_overlap_ratio, _tokenize
from utils.formatting import story_has_metric, strongest_metric_line, build_5p_summary, _format_key_points, METRIC_RX
from services.pinecone_service import _init_pinecone, PINECONE_MIN_SIM, SEARCH_TOP_K, _safe_json, _summarize_index_stats, PINECONE_NAMESPACE, PINECONE_INDEX_NAME, W_PC, W_KW, _DEF_DIM, _PINECONE_INDEX, VECTOR_BACKEND


# --- Nonsense rules (JSONL) + known vocab -------------------
import csv
from datetime import datetime
import os, re, time, textwrap, json

# Known vocab built from stories (call once after STORIES is loaded)
_KNOWN_VOCAB = set()


# simple CSV logger
def log_offdomain(query: str, reason: str, path: str = "data/offdomain_queries.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    row = [datetime.utcnow().isoformat(timespec="seconds"), query, reason]
    header = ["ts_utc", "query", "reason"]
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(header)
        w.writerow(row)

def get_context_story(stories: list):
    # Highest priority: an explicitly stored story object
    obj = st.session_state.get("active_story_obj")
    if isinstance(obj, dict) and (obj.get("id") or obj.get("title")):
        return obj

    sid = st.session_state.get("active_story")
    if sid:
        for s in stories:
            if str(s.get("id")) == str(sid):
                return s

    # Fallback: match by title/client when id mapping isn’t stable
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    if at:
        for s in stories:
            stitle = (s.get("title") or "").strip().lower()
            sclient = (s.get("client") or "").strip().lower()
            if stitle == at and (not ac or sclient == ac):
                return s
        # Last resort: substring/startswith
        for s in stories:
            stitle = (s.get("title") or "").strip().lower()
            if at in stitle or stitle in at:
                return s
    # Fallback: attempt to resolve from last_results payloads
    lr = st.session_state.get("last_results") or []
    sid = st.session_state.get("active_story")
    at = (st.session_state.get("active_story_title") or "").strip().lower()
    ac = (st.session_state.get("active_story_client") or "").strip().lower()
    for x in lr:
        if not isinstance(x, dict):
            continue
        cand = x.get("story") if isinstance(x.get("story"), dict) else x
        if not isinstance(cand, dict):
            continue
        xid = str(cand.get("id") or cand.get("story_id") or "").strip()
        xt = (cand.get("title") or "").strip().lower()
        xc = (cand.get("client") or "").strip().lower()
        if (sid and xid and str(xid) == str(sid)) or (
            at and xt == at and (not ac or xc == ac)
        ):
            return cand
    return None

def _ensure_ask_bootstrap():
    """Guarantee the Ask transcript starts with the assistant opener once per session."""
    if "ask_transcript" not in st.session_state:
        st.session_state["ask_transcript"] = []
    if not st.session_state["ask_transcript"]:
        st.session_state["ask_transcript"].append(
            {"role": "assistant", "text": "Ask anything."}
        )

def _format_narrative(s: dict) -> str:
    """1-paragraph, recruiter-friendly narrative from a single story."""
    title = s.get("title", "")
    client = s.get("client", "")
    domain = s.get("domain", "")
    goal = (s.get("why") or "").strip().rstrip(".")
    how = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric = strongest_metric_line(s)
    bits = []
    if title or client:
        bits.append(
            f"I led **{title}** at **{client}**"
            if title
            else f"I led work at **{client}**"
        )
    if domain:
        bits[-1] += f" in **{domain}**."
    if goal:
        bits.append(f"The aim was {goal.lower()}.")
    if how:
        bits.append(f"We focused on {how.lower()}.")
    if metric:
        bits.append(f"Impact: **{metric}**.")
    return " ".join(bits) or build_5p_summary(s, 280)


# =========================
# Embedding + Pinecone query
# =========================

# Try to use the same model as build_custom_embeddings.py (all-MiniLM-L6-v2, 384-dim)
_EMBEDDER = None


def _get_embedder():
    global _EMBEDDER
    if _EMBEDDER is not None:
        return _EMBEDDER
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        _EMBEDDER = SentenceTransformer("all-MiniLM-L6-v2")
        if DEBUG:
            print(
                "DEBUG Embeddings: using SentenceTransformer(all-MiniLM-L6-v2) with normalize_embeddings=True"
            )
    except Exception as e:
        _EMBEDDER = None
        print(
            f"WARNING: sentence-transformers not available ({e}); falling back to stub embedder (low quality)"
        )
    return _EMBEDDER



def _keyword_score_for_story(s: dict, query: str) -> float:
    """
    Lightweight BM25-ish overlap using title/client/domain/tags + curated 5P one-liner.
    Returns 0..1 (normalized by unique query tokens).
    """
    q_toks = set(_tokenize(query))
    if not q_toks:
        return 0.0
    hay_parts = [
        s.get("title", ""),
        s.get("client", ""),
        s.get("role", ""),
        s.get("domain", ""),
        " ".join(s.get("tags", []) or []),
        build_5p_summary(s, 400),
        " ".join(s.get("how", []) or []),
        " ".join(s.get("what", []) or []),
    ]
    hay = " ".join(hay_parts)
    h_toks = set(_tokenize(hay))
    hits = q_toks & h_toks
    # soft weighting: title/domain twice
    title_dom = " ".join([s.get("title", ""), s.get("domain", "")])
    td_hits = q_toks & set(_tokenize(title_dom))
    score = len(hits) + len(td_hits)  # double-count td_hits
    return min(1.0, score / max(1, len(q_toks) * 2))


def _hybrid_score(
    pc_score: float, kw_score: float, w_pc: float = W_PC, w_kw: float = W_KW
):
    """
    Blend Pinecone similarity and keyword overlap into one score.
    Args:
        pc_score: float similarity from Pinecone (0..1+ depending on metric)
        kw_score: float keyword/token overlap helper (0..1)
    """
    try:
        pc = float(pc_score or 0.0)
    except Exception:
        pc = 0.0
    try:
        kw = float(kw_score or 0.0)
    except Exception:
        kw = 0.0

    blended = (pc * float(w_pc)) + (kw * float(w_kw))

    return blended



def _format_deep_dive(s: dict) -> str:
    """Detail without saying STAR/5P explicitly: What was happening / Goal / What we did / Results."""
    st_blocks = s.get("star", {}) or {}
    situation = st_blocks.get("situation") or []
    task = st_blocks.get("task") or []
    action = st_blocks.get("action") or []
    result = st_blocks.get("result") or []
    parts = []
    if situation:
        parts.append(
            "**What was happening**\n" + "\n".join([f"- {x}" for x in situation])
        )
    if task:
        parts.append("**Goal**\n" + "\n".join([f"- {x}" for x in task]))
    if action:
        parts.append("**What we did**\n" + "\n".join([f"- {x}" for x in action]))
    if result:
        parts.append("**Results**\n" + "\n".join([f"- {x}" for x in result]))
    return "\n\n".join(parts) or build_5p_summary(s, 320)


def _embed(text: str) -> List[float]:
    """
    Query-time embeddings that MATCH the build script:
    - Model: all-MiniLM-L6-v2 (384-dim)
    - Normalization: normalize_embeddings=True
    Falls back to the old stub only if sentence-transformers is unavailable.
    """
    model = _get_embedder()
    if model is not None:
        try:
            # sentence-transformers returns a numpy array; ensure list[float]
            v = model.encode(text or "", normalize_embeddings=True)
            return [float(x) for x in (v.tolist() if hasattr(v, "tolist") else list(v))]
        except Exception as e:
            print(f"WARNING: MiniLM encode failed ({e}); using stub embedding")

    # Fallback: deterministic stub (keeps app running, but scores will be poor)
    import math

    vec = [0.0] * _DEF_DIM
    if not text:
        return vec
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % _DEF_DIM] += (ch % 13) / 13.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _extract_match_fields(m) -> tuple[str, float, dict]:
    """
    Normalize a Pinecone match object or dict into (sid, score, metadata).
    Returns (None, 0.0, {}) if fields are missing.
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
def _format_key_points(s: dict) -> str:
    """3–4 bullets: scope, approach, outcomes."""
    metric = strongest_metric_line(s)
    lines = []
    lines.append(f"- **Scope:** {s.get('title','')} — {s.get('client','')}".strip(" —"))
    top_how = (s.get("how") or [])[:2]
    if top_how:
        lines.append("- **Approach:** " + " / ".join(top_how))
    outs = s.get("what") or []
    if metric:
        lines.append(f"- **Outcome:** {metric}")
    elif outs:
        lines.append(f"- **Outcome:** {outs[0]}")
    dom = s.get("domain")
    if dom:
        lines.append(f"- **Domain:** {dom}")
    return "\n".join(lines)

def send_to_backend(prompt: str, filters: dict, ctx: Optional[dict], stories: list):
    return rag_answer(prompt, filters, stories)

def rag_answer(question: str, filters: dict, stories: list):
    # If this prompt was injected by a suggestion chip, skip aggressive off-domain gating
    force_answer = bool(st.session_state.pop("__ask_force_answer__", False))
    from_suggestion = (
        bool(st.session_state.pop("__ask_from_suggestion__", False)) or force_answer
    )
    # Persist debug context for the Ask caption
    st.session_state["__ask_dbg_prompt"] = (question or "").strip()
    st.session_state["__ask_dbg_from_suggestion"] = bool(from_suggestion)
    st.session_state["__ask_dbg_force_answer"] = bool(force_answer)
    # Do not clear banner flags here. We clear them after a successful answer render
    # to ensure the current banner stays visible if anything goes wrong.
    if DEBUG:
        dbg(
            f"ask: from_suggestion={from_suggestion} q='{(question or '').strip()[:60]}'"
        )
    # Mode-only prompts should switch view over the last ranked set, not trigger new retrieval
    simple_mode = (question or "").strip().lower()
    _MODE_ALIASES = {
        "key points": "key_points",
        "keypoints": "key_points",
        "deep dive": "deep_dive",
        "deep-dive": "deep_dive",
        "narrative": "narrative",
    }
    if simple_mode in _MODE_ALIASES and st.session_state.get("__last_ranked_sources__"):
        ids = st.session_state["__last_ranked_sources__"]
        ranked = [
            next((s for s in stories if str(s.get("id")) == str(i)), None) for i in ids
        ]
        ranked = [s for s in ranked if s][:3] or (
            semantic_search(question or "", filters, top_k=SEARCH_TOP_K) or stories[:3]
        )
        primary = ranked[0]
        modes = {
            "narrative": _format_narrative(primary),
            "key_points": "\n\n".join([_format_key_points(s) for s in ranked]),
            "deep_dive": _format_deep_dive(primary)
            + (
                (
                    "\n\n_Also relevant:_ "
                    + ", ".join(
                        [
                            f"{s.get('title','')} — {s.get('client','')}"
                            for s in ranked[1:]
                        ]
                    )
                )
                if len(ranked) > 1
                else ""
            ),
        }
        sel = _MODE_ALIASES[simple_mode]
        answer_md = modes.get(sel, modes["narrative"])
        sources = [
            {"id": s["id"], "title": s["title"], "client": s.get("client", "")}
            for s in ranked
        ]
        return {
            "answer_md": answer_md,
            "sources": sources,
            "modes": modes,
            "default_mode": sel,
        }

    try:
        # 0) Rule-based nonsense check (fast)
        cat = is_nonsense(question or "")
        if cat and not from_suggestion:
            # Log and set a one-shot flag for the Ask view to render the banner in the right place.
            log_offdomain(question or "", f"rule:{cat}")
            st.session_state["ask_last_reason"] = f"rule:{cat}"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = None
            # Decision tag for debug
            st.session_state["__ask_dbg_decision"] = f"rule:{cat}"
            # Return an empty answer so the Ask view shows only the banner
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # 0.5) Compute overlap for telemetry only (do not gate yet)
        overlap = token_overlap_ratio(question or "", _KNOWN_VOCAB)
        if DEBUG:
            dbg(
                f"ask: overlap={overlap:.2f} __pc_suppressed__={st.session_state.get('__pc_suppressed__')}"
            )

        # 1) Pinecone-first retrieval
        pool = semantic_search(question or filters.get("q", ""), filters, stories, top_k=SEARCH_TOP_K)


        # If Pinecone returned nothing, *then* decide if we want to show a low-overlap banner
        if not pool and (overlap < 0.15) and not from_suggestion:
            log_offdomain(question or "", f"overlap:{overlap:.2f}")
            st.session_state["ask_last_reason"] = "low_overlap"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = f"low_overlap:{overlap:.2f}"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
        # If this was triggered by a suggestion, widen the candidate pool by
        # blending in top local keyword matches so the reranker can surface
        # off-namespace or semantically-adjacent stories (e.g., cloud-native).
        if (from_suggestion or force_answer) and pool:
            try:
                locals_top = sorted(
                    stories,
                    key=lambda s: _score_story_for_prompt(s, question),
                    reverse=True,
                )[:5]
                seen = {x.get('id') for x in pool if isinstance(x, dict)}
                for s in locals_top:
                    sid = s.get('id')
                    if sid not in seen:
                        pool.append(s)
                        seen.add(sid)
            except Exception:
                pass
        if DEBUG:
            dbg(f"ask: pool_size={len(pool) if pool else 0}")

        # Use full Pinecone pool - no intent-based filtering

        # 2) No semantic results? Show appropriate message
        if not pool:
            if st.session_state.get("__pc_suppressed__"):
                log_offdomain(question or "", "low_confidence")
                st.session_state["ask_last_reason"] = "low_confidence"
                st.session_state["ask_last_query"] = question or ""
                st.session_state["ask_last_overlap"] = overlap
                st.session_state["__ask_dbg_decision"] = "low_conf"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }

        # 3) Vocab overlap safety: only after Pinecone path ran
        if (
            (overlap < 0.05)
            and st.session_state.get("__pc_suppressed__")
            and not from_suggestion
        ):
            log_offdomain(question or "", "no_overlap+low_conf")
            st.session_state["ask_last_reason"] = "no_overlap+low_conf"
            st.session_state["ask_last_query"] = question or ""
            st.session_state["ask_last_overlap"] = overlap
            st.session_state["__ask_dbg_decision"] = "no_overlap+low_conf"
            return {
                "answer_md": "",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
    except Exception as e:
        # Catch-all guard so Ask never throws to the UI
        if DEBUG:
            print(f"DEBUG rag_answer fatal error before build: {e}")
        # Safe fallback ranking over local stories
        try:
            ranked = sorted(
                stories,
                key=lambda s: _score_story_for_prompt(s, question),
                reverse=True,
            )[:3]
        except Exception:
            ranked = stories[:1]
        if not ranked:
            return {
                "answer_md": "No stories available.",
                "sources": [],
                "modes": {},
                "default_mode": "narrative",
            }
        st.session_state["__ask_dbg_decision"] = "fatal_fallback"
        primary = ranked[0]
        summary = build_5p_summary(primary, 280)
        sources = [
            {"id": s.get("id"), "title": s.get("title"), "client": s.get("client", "")}
            for s in ranked
            if isinstance(s, dict)
        ]
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        return {
            "answer_md": summary,
            "sources": sources,
            "modes": modes,
            "default_mode": "narrative",
        }

    # … then continue with your existing ranking + modes construction …

    # 4) Rank top 3 using pure Pinecone order (no intent boosting or diversity filtering)
    try:
        # Always use Pinecone semantic ranking - no special cases
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )

        if DEBUG and ranked:
            try:
                dbg(f"ask: ranked by semantic similarity, first_ids={[s.get('id') for s in ranked]}")
            except Exception:
                pass
    except Exception as e:
        # Defensive: if ranking fails, take first 1–3 items in the pool order
        if DEBUG:
            print(f"DEBUG rag_answer rank error: {e}")
        ranked = [x for x in pool if isinstance(x, dict)][:3] or (
            pool[:1] if pool else []
        )
    if DEBUG and ranked:
        dbg(
            f"ask: primary='{ranked[0].get('title','')}' sources={[s.get('id') for s in ranked]}"
        )
    st.session_state["__ask_dbg_decision"] = (
        f"ok_ranked:{ranked[0].get('id')}" if ranked else "rank_empty"
    )
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in ranked]

    primary = ranked[0]
    try:
        narrative = _format_narrative(primary)

        # Key points: include top 2–3 stories as bullets for breadth
        kp_lines = [_format_key_points(s) for s in ranked]
        key_points = "\n\n".join(kp_lines)

        # Deep dive: use the primary story; optionally cite others for comparison
        deep_dive = _format_deep_dive(primary)
        if len(ranked) > 1:
            more = ", ".join(
                [f"{s.get('title','')} — {s.get('client','')}" for s in ranked[1:]]
            )
            deep_dive += f"\n\n_Also relevant:_ {more}"

        modes = {
            "narrative": narrative,
            "key_points": key_points,
            "deep_dive": deep_dive,
        }
        # Use the narrative itself as the assistant bubble; omit CTA text
        answer_md = narrative
    except Exception as e:
        # Defensive fallback so Ask never crashes: use 5P summary only
        if DEBUG:
            print(f"DEBUG rag_answer build error: {e}")
        summary = build_5p_summary(primary, 280)
        modes = {"narrative": summary, "key_points": summary, "deep_dive": summary}
        answer_md = summary

    sources = [
        {"id": s["id"], "title": s["title"], "client": s.get("client", "")}
        for s in ranked
    ]
    return {
        "answer_md": answer_md,
        "sources": sources,
        "modes": modes,
        "default_mode": "narrative",
    }

def build_known_vocab(stories: list[dict]):
    vocab = set()
    for s in stories:
        # Use lowercase field names from normalized stories
        for field in ["title", "client", "role", "domain", "division", "industry", "who", "where", "why"]:
            txt = (s.get(field) or "").lower()
            vocab.update(re.split(r"[^\w]+", txt))
        for t in s.get("tags") or []:
            vocab.update(re.split(r"[^\w]+", str(t).lower()))
    # prune tiny tokens
    return {w for w in vocab if len(w) >= 3}



def _choose_story_for_ask(top_story: dict | None, stories: list) -> dict | None:
    """Prefer Pinecone (top_story) unless a one-shot context lock is set."""
    if st.session_state.get("__ctx_locked__"):
        ctx = get_context_story(stories)
        return ctx or top_story
    return top_story


def pinecone_semantic_search(
    query: str, filters: dict, stories: list, top_k: int = SEARCH_TOP_K
) -> Optional[List[dict]]:
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
            print(
                f"DEBUG Embeddings: qvec_dim={len(qvec)}  model=MiniLM({'yes' if _get_embedder() else 'stub'})"
            )
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

                st.session_state["__pc_debug__"] = {
                    "index": _PINECONE_INDEX or PINECONE_INDEX_NAME,
                    "namespace": PINECONE_NAMESPACE or "",
                    "match_count": len(matches),
                    "preview": preview,
                    "weights": {"W_PC": W_PC, "W_KW": W_KW},
                    "min_sim": PINECONE_MIN_SIM,
                    "stats": stats_compact,
                }
            except Exception as e:
                print("DEBUG: Pinecone snapshot error:", e)
        # --- end DEBUG snapshot ---

        hits = []
        st.session_state["__pc_last_ids__"].clear()
        st.session_state["__pc_snippets__"].clear()

        for m in matches:
            sid, score, meta = _extract_match_fields(m)
            if not sid:
                continue

            story = next((s for s in stories if str(s.get("id")) == str(sid)), None)
            if not story:
                continue

            snip = meta.get("summary") or meta.get("snippet") or ""
            if snip:
                st.session_state["__pc_snippets__"][str(sid)] = snip

            kw = _keyword_score_for_story(story, query)
            blended = _hybrid_score(score, kw)
            st.session_state["__pc_last_ids__"][str(sid)] = blended

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

def semantic_search(
    query: str,
    filters: dict,
    *,
    enforce_overlap: bool = False,
    min_overlap: float = 0.0,
    stories: list,
    top_k: int = SEARCH_TOP_K,
):
    """
    Pinecone-first semantic retrieval with gentle gating; strict UI filters applied after.
    Falls back to local keyword filtering if Pinecone returns nothing.
    Persists session state needed for chips/badges and transparency UI.
    """
    q = (query or "").strip()

    # 1) Always try Pinecone first
    hits = pinecone_semantic_search(q, filters, stories, top_k=top_k) or []
    st.session_state["__pc_suppressed__"] = False

    # 2) If Pinecone gave us candidates, keep those crossing the raw PC gate
    if hits:
        # Raw Pinecone gate; 'score' is blended, 'pc_score' is raw vector sim
        raw_gate = float(globals().get("PINECONE_MIN_SIM", 0.15))
        confident = [h for h in hits if (h.get("pc_score", 0.0) or 0.0) >= raw_gate]

        # If nothing crossed, mark suppressed but still carry a small set forward
        if not confident:
            st.session_state["__pc_suppressed__"] = True
            confident = hits[:3]  # gentle fallback already handled inside pinecone fn

        # Persist per-story blended confidence scores for display
        try:
            st.session_state["__pc_last_ids__"] = {
                h["story"]["id"]: float(h.get("score", 0.0) or 0.0)  # Use blended score
                for h in confident
            }
            st.session_state["__pc_snippets__"] = {
                h["story"]["id"]: (h.get("snippet") or build_5p_summary(h["story"]))
                for h in confident
            }
            st.session_state["__last_ranked_sources__"] = [
                h["story"]["id"] for h in confident
            ]
            st.session_state["__dbg_pc_hits"] = len(hits)
            # Also keep a compact top-5 for the Sources row if caller hasn’t set it
            st.session_state.setdefault(
                "last_sources",
                [
                    {
                        "id": h["story"]["id"],
                        "title": h["story"]["title"],
                        "client": h["story"].get("client", ""),
                    }
                    for h in confident[:5]
                ],
            )
        except Exception:
            pass

        # 3) Apply strict UI filters after retrieval
        filtered = [
            h["story"] for h in confident if matches_filters(h["story"], filters)
        ]
        if filtered:
            return filtered

        # If UI filters eliminate everything, return the confident set’s stories
        return [h["story"] for h in confident]

    # 4) If Pinecone returned nothing, optionally enforce overlap, else local fallback
    if enforce_overlap:
        ov = token_overlap_ratio(q, _KNOWN_VOCAB)
        if ov < float(min_overlap or 0.0) and not st.session_state.get(
            "__ask_from_suggestion__"
        ):
            # No semantic hits and below overlap bar → empty (caller may show banner)
            st.session_state["__dbg_pc_hits"] = 0
            st.session_state["__pc_last_ids__"].clear()
            st.session_state["__pc_snippets__"].clear()
            return []

    # Local keyword fallback (keeps app responsive during indexing issues)
    local = [s for s in stories if matches_filters(s, filters)]
    st.session_state["__dbg_pc_hits"] = 0
    st.session_state["__pc_last_ids__"].clear()
    st.session_state["__pc_snippets__"].clear()
    st.session_state["__last_ranked_sources__"] = [s["id"] for s in local[:10]]
    return local

# =========================
# Story modes and related helpers
# =========================
def story_modes(s: dict) -> dict:
    """Return the three anchored views for a single story."""
    return {
        "narrative": _format_narrative(s),
        "key_points": _format_key_points(s),
        "deep_dive": _format_deep_dive(s),
    }


def _related_stories(s: dict, stories: list, max_items: int = 3) -> list[dict]:
    """
    Very light 'related' heuristic: prefer same client, then same domain/tags.
    Excludes the current story. Returns up to max_items stories.
    """
    cur_id = s.get("id")
    dom = s.get("domain", "")
    client = s.get("client", "")
    tags = set(s.get("tags", []) or [])
    # simple scoring
    scored = []
    for t in stories:
        if t.get("id") == cur_id:
            continue
        score = 0
        if client and t.get("client") == client:
            score += 3
        if dom and t.get("domain") == dom:
            score += 2
        if tags:
            score += len(tags & set(t.get("tags", []) or []))
        if score:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:max_items]]


def _safe_json(obj):
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


def _score_story_for_prompt(s: dict, prompt: str) -> float:
    """
    Weighted scoring with token intersection to avoid substring noise (e.g., 'ai' in 'chain').
    - Strong weight for title/client/domain tokens
    - Medium weight for tags
    - Light weight for body (how/what)
    - Small penalty when there is zero overlap
    """
    score = 0.0
    # Strong base credit if a clear metric exists
    if story_has_metric(s):
        score += 1.0

    q_toks = set(_tokenize(prompt or ""))
    if not q_toks:
        return score

    # Tokenize fields
    title_dom_toks = set(
        _tokenize(
            " ".join(
                [
                    s.get("title", ""),
                    s.get("client", ""),
                    s.get("domain", ""),
                    s.get("where", ""),
                ]
            )
        )
    )
    tag_toks = set(_tokenize(" ".join(s.get("tags", []) or [])))
    body_toks = set(
        _tokenize(
            " ".join(
                (s.get("how", []) or [])
                + (s.get("what", []) or [])
                + ([s.get("why", "")] if s.get("why") else [])
            )
        )
    )

    # Overlaps
    title_hits = len(q_toks & title_dom_toks)
    tag_hits = len(q_toks & tag_toks)
    body_hits = len(q_toks & body_toks)

    score += 0.6 * title_hits
    score += 0.5 * tag_hits
    score += 0.2 * body_hits

    if (title_hits + tag_hits + body_hits) == 0:
        score -= 0.4

    return score

def matches_filters(s, F=None):
    # Normalize incoming filters (Ask may pass `{}` intentionally)
    if F is None:
        F = st.session_state.get("filters", {}) or {}
    personas = F.get("personas", []) or []
    clients = F.get("clients", []) or []
    domains = F.get("domains", []) or []
    roles = F.get("roles", []) or []
    tags = F.get("tags", []) or []
    has_metric = bool(F.get("has_metric", False))
    if personas and not (set(personas) & set(s.get("personas", []))):
        return False
    if clients and s.get("client") not in clients:
        return False
    if domains and s.get("domain") not in domains:
        return False
    if roles and s.get("role") not in roles:
        return False
    if tags:
        want = {str(t).strip().lower() for t in tags}
        have = {str(t).strip().lower() for t in (s.get("tags", []) or [])}
        if not (want & have):
            return False
    if has_metric and not story_has_metric(s):
        return False
    # Keyword query: token-based match (all words must be present)
    q_raw = (F.get("q") or "").strip()
    if q_raw:
        # Try token containment first (robust to order and punctuation)
        q_toks = _tokenize(q_raw)
        hay_joined = " ".join(
            [
                s.get("title", ""),
                s.get("client", ""),
                s.get("role", ""),
                s.get("domain", ""),
                s.get("who", ""),
                s.get("where", ""),
                s.get("why", ""),
                " ".join(s.get("how", []) or []),
                " ".join(s.get("what", []) or []),
                " ".join(s.get("tags", []) or []),
            ]
        )
        if q_toks:
            hay_toks = set(_tokenize(hay_joined))
            if not all(t in hay_toks for t in q_toks):
                return False
        else:
            # Very short or non-word input: fall back to substring check
            if q_raw.lower() not in hay_joined.lower():
                return False
    return True

def render_compact_context_banner(stories: List):
    """Single-line context breadcrumb - no emojis, minimal styling."""
    ctx = get_context_story(stories)
    if not ctx:
        return
    
    client = (ctx.get("client") or "").strip()
    domain_full = (ctx.get("domain") or "").strip()
    domain_short = domain_full.split(" / ")[-1] if " / " in domain_full else domain_full
    
    st.markdown(f"""
    <div style='font-size: 13px; color: #888; margin-bottom: 16px; padding: 8px 12px; background: rgba(128,128,128,0.05); border-radius: 6px;'>
        Context: {client} | {domain_short}
    </div>
    """, unsafe_allow_html=True)

def _push_card_snapshot_from_state(stories: list):
    """Append a static answer card snapshot to the transcript based on current state."""
    modes = st.session_state.get("answer_modes", {}) or {}
    sources = st.session_state.get("last_sources", []) or []
    sel = st.session_state.get("answer_mode", "narrative")
    if not sources:
        return
    sid = str(sources[0].get("id", ""))
    primary = next((s for s in stories if str(s.get("id")) == sid), None)
    if not primary:
        return
    content_md = modes.get(sel) if modes else st.session_state.get("last_answer", "")

    # Capture ALL confidence scores at snapshot time (before they get cleared on next query)
    scores = st.session_state.get("__pc_last_ids__", {}) or {}
    confidence = scores.get(sid)
    if DEBUG:
        print(f"DEBUG _push_card_snapshot: sid={sid}, confidence={confidence}, scores={scores}")

    # Also store confidence scores for all sources
    source_confidences = {}
    for src in sources:
        src_id = str(src.get("id", ""))
        if src_id in scores:
            source_confidences[src_id] = scores[src_id]
    if DEBUG:
        print(f"DEBUG _push_card_snapshot: source_confidences={source_confidences}")

    entry = {
        "type": "card",
        "story_id": primary.get("id"),
        "title": primary.get("title"),
        "one_liner": build_5p_summary(primary, 9999),
        "content": content_md,
        "sources": sources,
        "confidence": confidence,  # Primary story confidence
        "source_confidences": source_confidences,  # All source confidences
    }
    st.session_state["ask_transcript"].append(entry)

# --- Minimal linear transcript helpers (Ask) ---
def _ensure_ask_bootstrap():
    """Guarantee the Ask transcript starts with the assistant opener once per session."""
    if "ask_transcript" not in st.session_state:
        st.session_state["ask_transcript"] = []
    if not st.session_state["ask_transcript"]:
        st.session_state["ask_transcript"].append(
            {"role": "assistant", "text": "Ask anything."}
        )

def _split_tags(s):
    if not s:
        return []
    if isinstance(s, list):
        return [str(x).strip() for x in s if str(x).strip()]
    return [t.strip() for t in str(s).split(",") if t.strip()]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-") or "x"

def _push_user_turn(text: str):
    st.session_state["ask_transcript"].append({"role": "user", "text": text})
    st.session_state["__asked_once__"] = True


def _push_assistant_turn(text: str):
    st.session_state["ask_transcript"].append({"role": "assistant", "text": text})


def _clear_ask_context():
    """Remove any sticky story context so the next Ask is general-purpose."""
    st.session_state.pop("active_story", None)
    st.session_state.pop("__ctx_locked__", None)
    st.session_state.pop("seed_prompt", None)
    st.rerun()

def render_followup_chips(primary_story: dict, query: str = "", key_suffix: str = ""):
    """Generate contextual follow-up suggestions based on the answer."""

    if not primary_story:
        return

    # Universal follow-up suggestions that work with card-based retrieval
    # Focus on themes that trigger good semantic searches
    tags = set(str(t).lower() for t in (primary_story.get("tags") or []))

    suggestions = []

    # Theme-based suggestions that trigger relevant searches
    if any(t in tags for t in ["stakeholder", "collaboration", "communication"]):
        suggestions = [
            "How do you handle difficult stakeholders?",
            "Tell me about cross-functional collaboration",
            "What about managing remote teams?"
        ]
    elif any(t in tags for t in ["cloud", "architecture", "platform", "technical"]):
        suggestions = [
            "Show me examples with cloud architecture",
            "How do you modernize legacy systems?",
            "Tell me about technical challenges you've solved"
        ]
    elif any(t in tags for t in ["agile", "process", "delivery"]):
        suggestions = [
            "How do you accelerate delivery?",
            "Tell me about scaling agile practices",
            "Show me examples of process improvements"
        ]
    else:
        # Generic suggestions that work for any story
        suggestions = [
            "Show me examples with measurable impact",
            "How do you drive innovation?",
            "Tell me about leading transformation"
        ]

    if not suggestions:
        return

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    cols = st.columns(len(suggestions[:3]))
    for i, suggest in enumerate(suggestions[:3]):
        with cols[i]:
            # Make key unique by including card index and suggestion index
            unique_key = f"followup_{key_suffix}_{i}" if key_suffix else f"followup_{hash(suggest)%10000}_{i}"
            if st.button(suggest, key=unique_key, use_container_width=True):
                st.session_state["__inject_user_turn__"] = suggest
                # Don't set __ask_from_suggestion__ - treat chips like fresh typed questions
                # This ensures context lock is cleared and we get fresh search results
                st.session_state["__ask_force_answer__"] = True
                st.rerun()

def _render_ask_transcript(stories: list):
    """Render in strict order so avatars / order never jump."""
    for i, m in enumerate(st.session_state.get("ask_transcript", [])):
        # Static snapshot card entry
        if m.get("type") == "card":
            with st.chat_message("assistant"):
                # Snapshot with the same visual shell as the live answer card
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                with safe_container(border=True):
                    title = m.get("title", "")
                    one_liner = m.get("one_liner", "")
                    sid = m.get("story_id")
                    story = next(
                        (s for s in stories if str(s.get("id")) == str(sid)), None
                    )
                    # If the user clicked a Source after this snapshot was created,
                    use_ctx = bool(st.session_state.get("__ctx_locked__"))
                    _ctx = get_context_story(stories) if use_ctx else None
                    if isinstance(_ctx, dict) and (_ctx.get("id") or _ctx.get("title")):
                        story = _ctx or story
                    # If we resolved to a different story via Source click, update the header text, too
                    if isinstance(story, dict):
                        title = story.get("title", title)
                        try:
                            one_liner = build_5p_summary(story, 9999)
                        except Exception:
                            one_liner = one_liner

                    # Title
                    if title:
                        st.markdown(f"### {title}")

                    # Metadata: Client, Role, Domain
                    if isinstance(story, dict):
                        client = story.get("client", "")
                        role = story.get("role", "")
                        domain = story.get("domain", "")

                        # Create metadata line with role and domain
                        meta_parts = []
                        if client:
                            meta_parts.append(f"<strong>{client}</strong>")
                        if role or domain:
                            role_domain = " • ".join([x for x in [role, domain] if x])
                            if role_domain:
                                meta_parts.append(role_domain)

                        if meta_parts:
                            st.markdown(
                                f"<div style='font-size: 13px; color: #888; margin-bottom: 12px;'>{' | '.join(meta_parts)}</div>",
                                unsafe_allow_html=True,
                            )

                    # Confidence indicator (check if story changed via source click)
                    confidence = m.get("confidence")  # Original confidence from snapshot
                    if DEBUG:
                     print(f"DEBUG render: card_id={m.get('story_id')}, current_story_id={story.get('id') if story else None}, confidence={confidence}")

                    # If user clicked a different source, get that story's confidence from stored data
                    if isinstance(story, dict) and str(story.get("id")) != str(m.get("story_id")):
                        # Story was changed via source click - use stored source confidences
                        source_confidences = m.get("source_confidences", {}) or {}
                        story_id = str(story.get("id"))
                        if story_id in source_confidences:
                            confidence = source_confidences[story_id]
                        if DEBUG:
                          print(f"DEBUG render: switched story, new confidence={confidence}")

                    if confidence:
                        conf_pct = int(float(confidence) * 100)
                        # Color gradient: red -> orange -> green
                        if conf_pct >= 70:
                            bar_color = "#238636"  # green
                        elif conf_pct >= 50:
                            bar_color = "#ff8c00"  # orange
                        else:
                            bar_color = "#f85149"  # red

                        st.markdown(f"""
                        <div style='display: flex; align-items: center; gap: 8px; font-size: 12px; color: #7d8590; margin-bottom: 12px;'>
                            <span>Match confidence</span>
                            <div style='width: 60px; height: 4px; background: #21262d; border-radius: 2px; overflow: hidden;'>
                                <div style='height: 100%; width: {conf_pct}%; background: {bar_color}; border-radius: 2px;'></div>
                            </div>
                            <span style='color: {bar_color}; font-weight: 600;'>{conf_pct}%</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # 5P Summary
                    if one_liner:
                        st.markdown(
                            f"<div class='fivep-quote fivep-unclamped'>{one_liner}</div>",
                            unsafe_allow_html=True,
                        )

                    # View pills (Narrative / Key Points / Deep Dive) — clean CX
                    mode_key = f"card_mode_{i}"
                    st.session_state.setdefault(mode_key, "narrative")
                    if story:
                        modes = story_modes(story)
                        labels = [
                            ("narrative", "Narrative"),
                            ("key_points", "Key Points"),
                            ("deep_dive", "Deep Dive"),
                        ]
                        current = st.session_state.get(mode_key, "narrative")

                        # Prefer segmented control when available
                        if hasattr(st, "segmented_control"):
                            label_map = {b: a for a, b in labels}
                            default_label = next(
                                (b for a, b in labels if a == current), "Narrative"
                            )
                            chosen = st.segmented_control(
                                "View mode",  # ← Non-empty label
                                [b for _, b in labels],
                                selection_mode="single",
                                default=default_label,
                                key=f"seg_{mode_key}",
                                label_visibility="collapsed",  # ← Hide it
                            )
                            new_mode = label_map.get(chosen, "narrative")
                            if new_mode != current:
                                st.session_state[mode_key] = new_mode
                                st.rerun()
                        else:
                            # Fallback: left‑aligned pill buttons styled by .pill-container CSS
                            st.markdown(
                                f'<div class="pill-container" data-mode="{current}">',
                                unsafe_allow_html=True,
                            )
                            for key, text in labels:
                                class_name = {
                                    "narrative": "pill-narrative",
                                    "key_points": "pill-keypoints",
                                    "deep_dive": "pill-deepdive",
                                }[key]
                                st.markdown(
                                    f'<div class="{class_name}">',
                                    unsafe_allow_html=True,
                                )
                                if st.button(
                                    text,
                                    key=f"snap_pill_{i}_{key}",
                                    disabled=(current == key),
                                ):
                                    st.session_state[mode_key] = key
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("<hr class='hr'/>", unsafe_allow_html=True)
                        sel = st.session_state.get(mode_key, "narrative")
                        body = modes.get(sel, modes.get("narrative", ""))
                        st.markdown(body)

                    # Sources inside the bubble for symmetry (interactive chips)
                    srcs = m.get("sources", []) or []
                    if srcs:
                        st.markdown(
                            '<div class="sources-tight">', unsafe_allow_html=True
                        )
                        render_sources_chips(
                            srcs,
                            title="Sources",
                            stay_here=True,
                            key_prefix=f"snap_{i}_",
                            stories=stories,
                        )
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Add follow-up suggestion chips
                        if story:
                            render_followup_chips(story, st.session_state.get("ask_input", ""), key_suffix=f"snap_{i}")
                st.markdown('</div>', unsafe_allow_html=True)
            continue

        # Default chat bubble (user/assistant text)
        role = "assistant" if m.get("role") == "assistant" else "user"
        with st.chat_message(role):  # Remove avatar parameter
            st.markdown(m.get("text", ""))

def _shorten_middle(text: str, max_len: int = 64) -> str:
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    keep = max_len - 1
    left = keep // 2
    right = keep - left
    return text[:left] + "… " + text[-right:]

def render_sources_chips(
    sources: list[dict],
    title: str = "Sources",
    *,
    stay_here: bool = False,
    key_prefix: str = "",
    stories: list,
):
    """Render Sources as compact, 2-line chips.
    - stay_here=True: switch the active story + modes inline on Ask (no tab jump)
    - stay_here=False: legacy behavior (navigate to Explore Stories)
    """
    if not sources:
        return

    # Normalize + prune empties, but accept story_id as fallback and try to infer from title/client if missing
    items = []
    for s in sources:
        # prefer 'id', fall back to 'story_id' (common from LLM/backend)
        sid = str(s.get("id") or s.get("story_id") or "").strip()
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        # If no id was provided, try to infer from STORIES by title/client
        if not sid and (title_txt or client):
            cand = None
            low_title = title_txt.lower()
            low_client = client.lower()
            for x in stories:
                xt = (x.get("title") or "").strip().lower()
                xc = (x.get("client") or "").strip().lower()
                if (
                    low_title
                    and xt == low_title
                    and (not low_client or xc == low_client)
                ):
                    cand = x
                    break
            if cand:
                sid = str(cand.get("id") or "").strip()
        # Skip if we still don't have an id and no visible label
        if not sid and not (title_txt or client):
            continue
        # Keep the item even if id is still blank, so click can resolve by title/client
        items.append(
            {
                "id": sid or "",
                "client": client,
                "title": title_txt,
            }
        )
    if not items:
        return

    # tighter, non-<p> header + zero top gap container
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div data-mpg-srcchips class='pill-container sources-tight sources-grid'>",
        unsafe_allow_html=True,
    )

    # Lay out chips in rows using Streamlit columns (3-up per row)
    per_row = 3
    container = st.container()
    batch: list[dict] = []

    def _chip_label(item: dict, idx: int) -> tuple[str, str]:
        sep = " \u2009— "
        base = (
            f"{item['client']}{sep}{item['title']}" if item["client"] else item["title"]
        )
        short = _shorten_middle(base, 72)
        safe_id = item.get("id") or _slug(base) or str(idx)
        _scores = st.session_state.get("__pc_last_ids__", {}) or {}
        sc = _scores.get(str(safe_id) or str(item.get("id") or ""))
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, (int, float)) else None
        label = f"{pct} Match • {short}" if pct else short
        return label, safe_id

    for i, s in enumerate(items, 1):
        batch.append(s)
        if len(batch) == per_row or i == len(items):
            cols = container.columns(len(batch))
            for col, item in zip(cols, batch):
                with col:
                    label, safe_id = _chip_label(item, i)
                    btn_key = f"{key_prefix}srcchip_{safe_id}"
                    if st.button(
                        label,
                        key=btn_key,
                        use_container_width=False,
                        help="Semantic relevance to your question (higher = stronger match)",
                    ):
                        st.session_state["active_story"] = item.get("id") or ""
                        st.session_state["active_story_title"] = item.get("title")
                        st.session_state["active_story_client"] = item.get("client")
                        st.session_state["show_ask_panel"] = True

                        # ➜ ADD THIS (one-shot lock)
                        st.session_state["__ctx_locked__"] = True

                        if stay_here:
                            # resolve and pin the selected story context
                            target = None
                            sid_norm = (item.get("id") or "").strip()
                            if sid_norm:
                                target = next(
                                    (
                                        x
                                        for x in stories
                                        if str(x.get("id")) == str(sid_norm)
                                    ),
                                    None,
                                )
                            if not target:
                                tgt_title = (item.get("title") or "").strip().lower()
                                tgt_client = (item.get("client") or "").strip().lower()
                                if tgt_title:
                                    for x in stories:
                                        xt = (x.get("title") or "").strip().lower()
                                        xc = (x.get("client") or "").strip().lower()
                                        if xt == tgt_title and (
                                            not tgt_client or xc == tgt_client
                                        ):
                                            target = x
                                            break
                            if not target:
                                lr = st.session_state.get("last_results") or []
                                for x in lr:
                                    cand = (
                                        x.get("story") if isinstance(x, dict) else None
                                    )
                                    if not isinstance(cand, dict):
                                        cand = x if isinstance(x, dict) else None
                                    if not isinstance(cand, dict):
                                        continue
                                    xid = str(
                                        cand.get("id") or cand.get("story_id") or ""
                                    ).strip()
                                    xt = (cand.get("title") or "").strip().lower()
                                    xc = (cand.get("client") or "").strip().lower()
                                    if (sid_norm and xid and xid == sid_norm) or (
                                        (
                                            item.get("title")
                                            and xt
                                            == (item.get("title") or "").strip().lower()
                                        )
                                        and (
                                            not item.get("client")
                                            or xc
                                            == (item.get("client") or "")
                                            .strip()
                                            .lower()
                                        )
                                    ):
                                        target = cand
                                        break
                            if target:
                                st.session_state["active_story_obj"] = target
                                st.session_state["answer_modes"] = story_modes(target)
                                cur = st.session_state.get("answer_mode", "narrative")
                                st.session_state["answer_mode"] = (
                                    cur
                                    if cur in ("narrative", "key_points", "deep_dive")
                                    else "narrative"
                                )
                                st.session_state["last_sources"] = [
                                    {
                                        "id": target.get("id")
                                        or target.get("story_id"),
                                        "title": target.get("title"),
                                        "client": target.get("client"),
                                    }
                                ]
                            else:
                                st.session_state["last_sources"] = [
                                    {
                                        "id": item.get("id") or item.get("story_id"),
                                        "title": item.get("title"),
                                        "client": item.get("client"),
                                    }
                                ]
                        else:
                            st.session_state["active_tab"] = "Explore Stories"
                        st.rerun()
            batch = []

    st.markdown("</div>", unsafe_allow_html=True)

_DOT_EMOJI = [
    "🟦",
    "🟩",
    "🟥",
    "🟧",
    "🟦",
    "🟪",
    "🟩",
    "🟧",
    "🟪",
    "🟦",
]  # stable palette-ish

def _dot_for(label: str) -> str:
    if not label:
        return "•"
    idx = sum(ord(c) for c in label) % len(_DOT_EMOJI)
    return _DOT_EMOJI[idx]


# --- Mock-style non-interactive source badges (stays on Ask) ---
def render_sources_badges(
    sources: list[dict], *, title: str = "Sources", key_prefix: str = "srcbad_", stories: list,
):
    """Backward-compatible alias: render interactive chips and stay on Ask."""
    return render_sources_chips(
        sources, title=title, stay_here=True, key_prefix=key_prefix, stories=stories
    )

def show_persona_tags(s: dict):
    """Simple alias for personas/tags badges for a single story (non-interactive)."""
    return render_badges_static(s)

def render_badges_static(s: dict):
    """Render a single flowing row of small badges for personas + tags.
    Matches the mock badge styling already defined in CSS (.badge-row, .badge).
    Safe no-op if nothing to show.
    """
    try:
        personas = s.get("personas") or []
        tags = s.get("tags") or []
    except Exception:
        personas, tags = [], []

    # Normalize to strings and prune empties
    personas = [str(p).strip() for p in personas if str(p).strip()]
    tags = [str(t).strip() for t in tags if str(t).strip()]

    if not personas and not tags:
        return

    chips = []

    # Personas first
    for p in personas:
        dot = _dot_for(p)
        chips.append(f"<span class='badge' title='Persona'>{dot} {p}</span>")

    # Then tags
    for t in tags:
        dot = _dot_for(t)
        chips.append(f"<span class='badge' title='Tag'>{dot} {t}</span>")

    html = "".join(chips)
    st.markdown(f"<div class='badge-row'>{html}</div>", unsafe_allow_html=True)

def render_sources_badges_static(
    sources: list[dict], title: str = "Sources", key_prefix: str = "srcbad_"
):
    """Render non-interactive mock-style badges under a small 'Sources' header.
    This avoids nested layout/columns and matches the mock_ask_hybrid DOM exactly.
    """
    if not sources:
        return

    # Normalize + prune empties
    items = []
    for s in sources:
        sid = str(s.get("id") or s.get("story_id") or "").strip()
        client = (s.get("client") or "").strip()
        title_txt = (s.get("title") or "").strip()
        if not (sid or client or title_txt):
            continue
        items.append({"id": sid, "client": client, "title": title_txt})
    if not items:
        return

    def _pick_icon(label: str) -> str:
        low = label.lower()
        if any(w in low for w in ["payment", "treasury", "bank"]):
            return "bi-bank"
        if any(w in low for w in ["health", "care", "patient", "kaiser"]):
            return "bi-hospital"
        if any(w in low for w in ["cloud", "kubernetes", "microservice"]):
            return "bi-cloud"
        if any(w in low for w in ["ai", "ml", "model", "genai", "rai"]):
            return "bi-cpu"
        return "bi-journal-text"

    # Tight section header (no extra paragraph margins)
    st.markdown(f"<div class='section-tight'>{title}</div>", unsafe_allow_html=True)

    chips_html = []
    _scores = st.session_state.get("__pc_last_ids__", {}) or {}
    for s in items:
        label_full = f"{s['client']} — {s['title']}" if s['client'] else s['title']
        _score_key = str(s.get("id") or "")
        sc = _scores.get(_score_key)
        pct = f"{float(sc)*100:.0f}%" if isinstance(sc, (int, float)) else None

        text = _shorten_middle(label_full, 96)
        if pct:
            text = f"{pct} Match • {text}"

        # Static badge (no icon) to match the mock capsule style
        chips_html.append(
            f"<span class='badge' title='Semantic relevance'>{text}</span>"
        )

    st.markdown(
        f"<div class='badge-row'>{''.join(chips_html)}</div>", unsafe_allow_html=True
    )

def show_sources(
    srcs: list[dict],
    *,
    interactive: bool = False,
    key_prefix: str = "src_",
    title: str = "Sources",
    stories: list,
):
    """Render Sources row using a single call site.
    - interactive=True  -> clickable chips (Ask)
    - interactive=False -> static badges (Explore/Details)
    """
    if not srcs:
        return
    if interactive:
        return render_sources_chips(
            srcs, title=title, stay_here=True, key_prefix=key_prefix, stories=stories
        )
    return render_sources_badges_static(srcs, title=title, key_prefix=key_prefix)

def set_answer(resp: dict):
    # State-only update; UI renders chips separately to avoid double-render / layout conflicts
    st.session_state["last_answer"] = resp.get("answer_md") or resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", []) or []
    st.session_state["answer_modes"] = resp.get("modes", {}) or {}
    st.session_state["answer_mode"] = resp.get("default_mode", "narrative")

def render_answer_card_compact(
    primary_story: dict, modes: dict, stories: List, answer_mode_key: str = "answer_mode",
):
    """Lightweight answer card - reduced padding, cleaner hierarchy, no emojis."""
    
    # Override with context-locked story if set
    if st.session_state.get("__ctx_locked__"):
        _ctx_story = get_context_story(stories)
        if _ctx_story and str(_ctx_story.get("id")) != str(primary_story.get("id")):
            primary_story = _ctx_story
            st.session_state["active_story_obj"] = _ctx_story
            try:
                modes = story_modes(primary_story)
            except Exception:
                pass
    
    title = field_value(primary_story, "title", "")
    client = field_value(primary_story, "client", "")
    domain = field_value(primary_story, "domain", "")
    
    # Compact header - single line with subtle separators
    meta_line = " • ".join([x for x in [client, domain] if x])
    
    st.markdown(f"""
    <div style='margin-bottom: 8px;'>
        <div style='font-size: 18px; font-weight: 600; margin-bottom: 4px;'>{title}</div>
        <div style='font-size: 13px; color: #888; margin-bottom: 12px;'>{meta_line}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # View mode pills - smaller, less prominent
    labels = [
        ("narrative", "Summary"),
        ("key_points", "Key Points"),
        ("deep_dive", "Details"),
    ]
    current = st.session_state.get(answer_mode_key, "narrative")
    
    # Compact pill row
    cols = st.columns([1, 1, 1, 9])
    for i, (key, text) in enumerate(labels):
        with cols[i]:
            disabled = (current == key)
            if st.button(
                text,
                key=f"mode_{answer_mode_key}_{key}",
                disabled=disabled,
                use_container_width=True
            ):
                st.session_state[answer_mode_key] = key
                st.rerun()
    
    st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
    
    # Body with less padding
    body_md = modes.get(st.session_state.get(answer_mode_key, "narrative"), "")
    if body_md:
        st.markdown(body_md)
    else:
        st.markdown("_No content available for this view._")
    
    # Sources - tighter spacing
    _srcs = st.session_state.get("last_sources") or []
    if not _srcs and primary_story:
        _srcs = [{
            "id": primary_story.get("id"),
            "title": primary_story.get("title"),
            "client": primary_story.get("client"),
        }]
        try:
            for r in _related_stories(primary_story, max_items=2):
                _srcs.append({
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "client": r.get("client"),
                })
        except Exception:
            pass
    
    if _srcs:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        show_sources(_srcs, interactive=True, key_prefix=f"compact_{answer_mode_key}_", title="Sources")
        st.write("DEBUG: About to call render_followup_chips")

        # Add follow-up suggestions
        render_followup_chips(primary_story, st.session_state.get("ask_input", ""))
        st.write("DEBUG: After render_followup_chips call")

# Safe alias that mirrors F() but is immune to shadowing elsewhere
def field_value(s: dict, key: str, default: str | list | None = None):
    # Inline copy of F() to avoid name collisions
    if key in s:
        return s[key]
    pc = key[:1].upper() + key[1:]
    if pc in s:
        return s[pc]

    if key == "domain":
        cat = s.get("Category") or s.get("Domain")
        sub = s.get("Sub-category") or s.get("SubCategory")
        if cat and sub:
            return f"{cat} / {sub}"
        return cat or sub or default

    if key == "tags":
        if "tags" in s and isinstance(s["tags"], list):
            return s["tags"]
        pub = s.get("public_tags")
        if isinstance(pub, list):
            return pub
        if isinstance(pub, str):
            return [t.strip() for t in pub.split(",") if t.strip()]
        return default or []

    alias = {
        "who": "Person",
        "where": "Place",
        "why": "Purpose",
        "how": "Process",
        "what": "Performance",
    }
    if key in alias and alias[key] in s:
        return s[alias[key]]

    return default


def STAR(s: dict) -> dict:
    return {
        "situation": s.get("Situation", []) or s.get("situation", []),
        "task": s.get("Task", []) or s.get("task", []),
        "action": s.get("Action", []) or s.get("action", []),
        "result": s.get("Result", []) or s.get("result", []),
    }


def FIVEP_SUMMARY(s: dict) -> str:
    return s.get("5PSummary") or s.get("5p_summary") or ""


def _format_narrative(s: dict) -> str:
    """1-paragraph, recruiter-friendly narrative from a single story."""
    title = s.get("title", "")
    client = s.get("client", "")
    domain = s.get("domain", "")
    goal = (s.get("why") or "").strip().rstrip(".")
    how = ", ".join((s.get("how") or [])[:2]).strip().rstrip(".")
    metric = strongest_metric_line(s)
    bits = []
    if title or client:
        bits.append(
            f"I led **{title}** at **{client}**"
            if title
            else f"I led work at **{client}**"
        )
    if domain:
        bits[-1] += f" in **{domain}**."
    if goal:
        bits.append(f"The aim was {goal.lower()}.")
    if how:
        bits.append(f"We focused on {how.lower()}.")
    if metric:
        bits.append(f"Impact: **{metric}**.")
    return " ".join(bits) or build_5p_summary(s, 280)


def _format_key_points(s: dict) -> str:
    """3–4 bullets: scope, approach, outcomes."""
    metric = strongest_metric_line(s)
    lines = []
    lines.append(f"- **Scope:** {s.get('title','')} — {s.get('client','')}".strip(" —"))
    top_how = (s.get("how") or [])[:2]
    if top_how:
        lines.append("- **Approach:** " + " / ".join(top_how))
    outs = s.get("what") or []
    if metric:
        lines.append(f"- **Outcome:** {metric}")
    elif outs:
        lines.append(f"- **Outcome:** {outs[0]}")
    dom = s.get("domain")
    if dom:
        lines.append(f"- **Domain:** {dom}")
    return "\n".join(lines)


def _format_deep_dive(s: dict) -> str:
    """Detail without saying STAR/5P explicitly: What was happening / Goal / What we did / Results."""
    st_blocks = s.get("star", {}) or {}
    situation = st_blocks.get("situation") or []
    task = st_blocks.get("task") or []
    action = st_blocks.get("action") or []
    result = st_blocks.get("result") or []
    parts = []
    if situation:
        parts.append(
            "**What was happening**\n" + "\n".join([f"- {x}" for x in situation])
        )
    if task:
        parts.append("**Goal**\n" + "\n".join([f"- {x}" for x in task]))
    if action:
        parts.append("**What we did**\n" + "\n".join([f"- {x}" for x in action]))
    if result:
        parts.append("**Results**\n" + "\n".join([f"- {x}" for x in result]))
    return "\n\n".join(parts) or build_5p_summary(s, 320)


# Also update your context banner to be minimal
def render_compact_context_banner(stories: list):
    """Single-line context breadcrumb."""
    ctx = get_context_story(stories)
    if not ctx:
        return
    
    client = (ctx.get("client") or "").strip()
    domain_full = (ctx.get("domain") or "").strip()
    domain_short = domain_full.split(" / ")[-1] if " / " in domain_full else domain_full
    
    st.markdown(f"""
    <div style='font-size: 13px; color: #888; margin-bottom: 16px; padding: 8px 12px; background: rgba(128,128,128,0.05); border-radius: 6px;'>
        Context: {client} | {domain_short}
    </div>
    """, unsafe_allow_html=True)

def render_no_match_banner(
    reason: str,
    query: str,
    overlap: float | None = None,
    suppressed: bool = False,
    filters: dict | None = None,
    *,
    key_prefix: str = "banner",
):
    """
    Unified yellow warning banner for 'no confident match' situations.
    Always shows a consistent message, suggestions, and optionally a Clear Filters button.
    """
    msg = "I couldn’t find anything confidently relevant to that query."
    debug_note = ""
    if DEBUG and reason:
        debug_note = f"  \n_Reason: {reason}"
        if overlap is not None:
            debug_note += f" (overlap={overlap:.2f})"
        debug_note += "_"
    msg += debug_note
    st.warning(msg)

    # Chips act as clean semantic prompts (no tag/domain filters)
    suggestions = [
        (
            "Payments modernization",
            "Tell me about your work modernizing payments platforms.",
        ),
        (
            "Generative AI in healthcare",
            "Tell me about applying Generative AI in healthcare.",
        ),
        (
            "Cloud-native architecture",
            "Tell me about your cloud-native architecture work.",
        ),
        (
            "Innovation in digital products",
            "Tell me about driving innovation in digital products.",
        ),
    ]
    cols = st.columns(len(suggestions))
    for i, (label, prompt_text) in enumerate(suggestions):
        with cols[i]:
            if st.button(
                label, key=f"{key_prefix}_suggest_no_match_{i}_{hash(label)%10000}"
            ):
                # Inject a new user turn with a concise prompt; rely on semantic search only
                st.session_state["__inject_user_turn__"] = prompt_text
                # Mark that this came from a suggestion chip to relax off-domain gating once
                st.session_state["__ask_from_suggestion__"] = True
                # Guarantee we build a compact answer panel even if retrieval is empty
                st.session_state["__ask_force_answer__"] = True
                st.session_state["ask_input"] = prompt_text
                st.session_state["active_tab"] = "Ask MattGPT"
                # Defer banner clearing to after a successful answer, avoiding duplicates
                st.session_state["__clear_banner_after_answer__"] = True
                st.rerun()

    # Show Clear Filters button if filters exist and are non-empty
    if filters:
        # Check if any filter is set (excluding 'q' and 'has_metric' for len check)
        any_active = any(
            (isinstance(v, list) and v)
            or (isinstance(v, str) and v.strip())
            or (isinstance(v, bool) and v)
            for k, v in filters.items()
            if k
            in ["personas", "clients", "domains", "roles", "tags", "has_metric", "q"]
        )
        if any_active:
            if st.button("Clear filters", key=f"{key_prefix}_clear_filters_no_match"):
                st.session_state["filters"] = {
                    "personas": [],
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                    "q": "",
                    "has_metric": False,
                }
                st.session_state["facet_domain_group"] = "All"
                st.session_state["page_offset"] = 0
                st.rerun()

def render_ask_mattgpt(stories: list):
    """
    Render the Ask MattGPT conversational interface.
    
    Args:
        stories: List of story dictionaries (STORIES from app.py)
    """
    
    # Page header
    st.title("Ask MattGPT")
    st.markdown("Ask me anything about my 20+ years in digital transformation...")
    
     # Anchor at top to force scroll position
    st.markdown('<div id="ask-top"></div>', unsafe_allow_html=True)

    # Force scroll to top using multiple methods
    st.markdown("""
    <script>
    // Immediate scroll
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;

    // Also try after a tiny delay in case content is still loading
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 10);
    </script>
    """, unsafe_allow_html=True)

    # Add a header row with the title and the How it Works link
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("Ask MattGPT")
    with col2:
        if st.button("🔧 How it works", key="how_works_top"):
            st.session_state["show_how_modal"] = not st.session_state.get(
                "show_how_modal", False
            )
            st.rerun()
    
    # Intelligence indicator strip
    st.markdown("""
    <div style='display: flex; gap: 12px; align-items: center; padding: 8px 12px; background: rgba(56, 139, 253, 0.1); border: 1px solid rgba(56, 139, 253, 0.2); border-radius: 6px; font-size: 12px; color: #58a6ff; margin-bottom: 16px;'>
        <span>🧠 Semantic search active</span>
        <span>•</span>
        <span>Pinecone index ready</span>
        <span>•</span>
        <span>115 stories indexed</span>
    </div>
    """, unsafe_allow_html=True)

    # Show the modal if toggled
    if st.session_state.get("show_how_modal", False):
        # Force scroll to top when modal opens
        st.markdown("""
        <script>
        window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
        """, unsafe_allow_html=True)

        # Create a proper modal container without using expander
        st.markdown("---")

        # Header with close button
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown("## 🔧 How MattGPT Works")
        with col2:
            if st.button("✕", key="close_how"):
                st.session_state["show_how_modal"] = False
                st.rerun()

        # Content in a bordered container
        with st.container():
            # Quick stats bar
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stories Indexed", "115")
            with col2:
                st.metric("Avg Response Time", "1.2s")
            with col3:
                st.metric("Retrieval Accuracy", "87%")
            with col4:
                st.metric("Vector Dimensions", "384")

            st.markdown("---")

            # Architecture overview
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    """
                ### Solution Architecture Overview
                
                **🎯 Semantic Search Pipeline**
                - Sentence-BERT embeddings (all-MiniLM-L6-v2)
                - 384-dimensional vector space
                - Pinecone vector database with metadata filtering
                
                **🔄 Hybrid Retrieval**
                - 80% semantic similarity weight
                - 20% keyword matching weight
                - Intent recognition for query understanding
                """
                )

            with col2:
                st.markdown(
                    """
                ### Data & Processing
                
                **📊 Story Corpus**
                - 115+ structured narratives from Fortune 500 projects
                - STAR/5P framework encoding
                - Rich metadata: client, domain, outcomes, metrics
                
                **💬 Response Generation**
                - Context-aware retrieval (top-k=30)
                - Multi-mode synthesis (Narrative/Key Points/Deep Dive)
                - Source attribution with confidence scoring
                """
                )

            # Query Flow
            st.markdown("### Query Flow")
            st.code(
                """
                Your Question 
                    ↓
                [Embedding + Intent Analysis]
                    ↓
                [Pinecone Vector Search + Keyword Matching]
                    ↓
                [Hybrid Scoring & Ranking]
                    ↓
                [Top 3 Stories Retrieved]
                    ↓
                [Response Synthesis with Sources]
                            """,
                language="text",
            )

            st.markdown("---")
            st.markdown("### System Architecture")

            try:
                with open("assets/rag_architecture_grid_svg.svg", "r") as f:
                    svg_content = f.read()
                
                # Remove XML declaration and DOCTYPE
                svg_content = svg_content.replace('<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '')
                svg_content = svg_content.replace('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">', '')
                
                # Use HTML component with transparent background and no scroll
                import streamlit.components.v1 as components
                
                components.html(f"""
                <div style='width: 100%; text-align: center;'>
                    {svg_content}
                </div>
                """, height=280, scrolling=False)
                
            except Exception as e:
                st.error(f"Error loading architecture diagram: {e}")

            st.markdown("---")
            

            # Detailed breakdown
            st.markdown("### Architecture Details")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                **Search & Retrieval**
                - **Semantic**: Pinecone cosine similarity (80% weight)
                - **Keyword**: BM25-style token overlap (20% weight)
                - Minimum similarity threshold: 0.15
                - Top-k pool: 30 candidates before ranking
                """)

            with col2:
                st.markdown("""
                **Response Synthesis**
                - Rank top 3 stories by blended score
                - Generate 3 views from same sources:
                - Narrative (1-paragraph summary)
                - Key Points (3-4 bullets)
                - Deep Dive (STAR breakdown)
                - Interactive source chips with confidence %
                """)

            st.markdown("---")

            st.markdown("""
            **Key Differentiators:**
            - Hybrid retrieval ensures both semantic understanding and exact term matching
            - Multi-mode synthesis provides flexible presentation for different use cases
            - Context locking allows follow-up questions on specific stories
            - Off-domain gating with suggestion chips prevents poor matches
            """)

    # Define ctx - MUST be outside and after the modal block
    ctx = get_context_story(stories)
    _show_ctx = bool(ctx) and (
        st.session_state.get("__ctx_locked__") or st.session_state.get("__asked_once__")
    )

    if _show_ctx:
        render_compact_context_banner(stories)

    # Rest of your Ask MattGPT content continues...
    # Rest of your Ask MattGPT content continues as normal
    # Context banner, transcript, etc...

    # with right:
    #    if st.button("×", key="btn_clear_ctx", help="Clear context"):
    #       _clear_ask_context()

    # Lightweight DEBUG status for Ask (visible only when DEBUG=True)
    if DEBUG:
        try:
            _dbg_flags = {
                "vector": VECTOR_BACKEND,
                "index": PINECONE_INDEX_NAME or "-",
                "ns": PINECONE_NAMESPACE or "-",
                "pc_suppressed": bool(st.session_state.get("__pc_suppressed__")),
                "has_last": bool(st.session_state.get("last_sources")),
                "pending_snap": bool(st.session_state.get("__pending_card_snapshot__")),
                # NEW: report external renderer overrides
                "ext_chips": (
                    "yes"
                    if callable(globals().get("_ext_render_sources_chips"))
                    else "no"
                ),
                "ext_badges": (
                    "yes"
                    if callable(globals().get("_ext_render_sources_badges_static"))
                    else "no"
                ),
            }
            st.caption("🧪 " + ", ".join(f"{k}={v}" for k, v in _dbg_flags.items()))
            # Second line: last prompt + ask decision
            lp = (st.session_state.get("__ask_dbg_prompt") or "").strip()
            lp = (lp[:60] + "…") if len(lp) > 60 else lp
            st.caption(
                "🧪 "
                + f"prompt='{lp}' from_suggestion={st.session_state.get('__ask_dbg_from_suggestion')}"
                + f" force={st.session_state.get('__ask_dbg_force_answer')} pc_hits={st.session_state.get('__dbg_pc_hits')}"
                + f" decision={st.session_state.get('__ask_dbg_decision')}"
                + f" reason={st.session_state.get('ask_last_reason')}"
            )
        except Exception:
            pass

    # 1) Bootstrap a stable transcript (one-time)
    _ensure_ask_bootstrap()

    # 2) Unify seeds and chip-clicks: inject as a real user turn if present
    seed = st.session_state.pop("seed_prompt", None)
    injected = st.session_state.pop("__inject_user_turn__", None)
    pending = seed or injected
    if pending:
        # If a live card was pending snapshot, capture it now before injecting the new turn
        if st.session_state.get("__pending_card_snapshot__"):
            _push_card_snapshot_from_state(stories)
            st.session_state["__pending_card_snapshot__"] = False
        _push_user_turn(pending)
        with st.status("Searching Matt's experience...", expanded=True) as status:
            try:
                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(pending, {}, ctx, stories)

                # Show confidence after retrieval
                sources = resp.get("sources", [])
                if sources:
                    first_id = str(sources[0].get("id", ""))
                    scores = st.session_state.get("__pc_last_ids__", {}) or {}
                    conf = scores.get(first_id)
                    if conf:
                        conf_pct = int(float(conf) * 100)
                        st.write(f"✓ Found relevant stories • {conf_pct}% match confidence")

                status.update(label="Answer ready!", state="complete", expanded=False)

            except Exception as e:
                    status.update(label="Error occurred", state="error")
                    print(f"DEBUG: send_to_backend failed: {e}")
                    import traceback
                    traceback.print_exc()
                    _push_assistant_turn(f"Error: {str(e)}")
                    st.rerun()

            else:
                set_answer(resp)
                # If no banner is active, append a static card snapshot now so it
                # appears in-order as a chat bubble; also suppress the bottom live card once.
                if not st.session_state.get(
                    "ask_last_reason"
                ) and not st.session_state.get("__sticky_banner__"):
                    _push_card_snapshot_from_state(stories)
                    st.session_state["__suppress_live_card_once__"] = True
                # If a chip click requested banner clear, perform it now after answer set
                if st.session_state.pop("__clear_banner_after_answer__", False):
                    st.session_state.pop("ask_last_reason", None)
                    st.session_state.pop("ask_last_query", None)
                    st.session_state.pop("ask_last_overlap", None)
                st.rerun()

    # 3) Render transcript so far (strict order, no reflow)
    _render_ask_transcript(stories)

    # Force scroll to top after transcript renders
    st.markdown("""
    <script>
    // Multiple scroll methods with longer delays
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 50);
    setTimeout(function() {
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
    }, 100);
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 200);
    </script>
    """, unsafe_allow_html=True)

    # 4) One‑shot nonsense/off‑domain banner appears AFTER transcript
    rendered_banner = False
    if st.session_state.get("ask_last_reason"):
        with st.chat_message("assistant"):
            render_no_match_banner(
                reason=st.session_state.get("ask_last_reason", ""),
                query=st.session_state.get("ask_last_query", ""),
                overlap=st.session_state.get("ask_last_overlap", None),
                suppressed=st.session_state.get("__pc_suppressed__", False),
                filters=st.session_state.get("filters", {}),
                key_prefix="askinline",
            )
        rendered_banner = True
        # Clear flags so the banner doesn't re-render on every rerun
        st.session_state.pop("ask_last_reason", None)
        st.session_state.pop("ask_last_query", None)
        st.session_state.pop("ask_last_overlap", None)
        # Persist as sticky so it remains visible between user turns unless dismissed
        st.session_state.setdefault(
            "__sticky_banner__",
            {
                "reason": (
                    dec
                    if (dec := (st.session_state.get("__ask_dbg_decision") or ""))
                    else "no_match"
                ),
                "query": st.session_state.get("__ask_dbg_prompt", ""),
                "overlap": None,
                "suppressed": bool(st.session_state.get("__pc_suppressed__", False)),
            },
        )
    elif True:
        # Forced fallback: if gating decided no‑match but the flag was not set,
        # render a banner anyway so the user sees actionable chips.
        dec = (st.session_state.get("__ask_dbg_decision") or "").strip().lower()
        no_match_decision = (
            dec.startswith("rule:")
            or dec.startswith("low_overlap")
            or dec == "low_conf"
            or dec == "no_overlap+low_conf"
        )
        if no_match_decision and not st.session_state.get("last_sources"):
            with st.chat_message("assistant"):
                render_no_match_banner(
                    reason=dec or "no_match",
                    query=st.session_state.get("__ask_dbg_prompt", ""),
                    overlap=st.session_state.get("ask_last_overlap", None),
                    suppressed=st.session_state.get("__pc_suppressed__", False),
                    filters=st.session_state.get("filters", {}),
                    key_prefix="askinline_forced",
                )
            rendered_banner = True

    # Sticky banner temporarily disabled to stabilize chip clicks
    st.session_state["__sticky_banner__"] = None

    # 5) Compact answer panel (title • unclamped 5P • view pills • sources)
    _m = st.session_state.get("answer_modes", {}) or {}
    _srcs = st.session_state.get("last_sources", []) or []
    _primary = None
    if _srcs:
        _sid = str(_srcs[0].get("id", ""))
        _primary = next((s for s in stories if str(s.get("id")) == _sid), None)
    # Suppress the bottom live card when:
    #  - a banner was rendered this run; or
    #  - we already have at least one static card snapshot in the transcript
    has_snapshot_card = any(
        (isinstance(x, dict) and x.get("type") == "card")
        for x in st.session_state.get("ask_transcript", [])
    )
    if (
        not rendered_banner
        and not has_snapshot_card
        and not st.session_state.get("__suppress_live_card_once__")
        and (_m or _primary or st.session_state.get("last_answer"))
    ):
        # Always render the bottom live card so pills are available.
        # Snapshot holds only header + one-liner + sources to avoid duplicate body text.
        render_answer_card_compact(
            _primary or {"title": "Answer"}, _m, stories, "answer_mode"
        )

    # Reset one-shot suppression flag after a render cycle
    if st.session_state.get("__suppress_live_card_once__"):
        st.session_state["__suppress_live_card_once__"] = False

    # 6) Handle a new chat input (command aliases or normal question)
    # Render the chat input only on the Ask MattGPT tab
    if st.session_state.get("active_tab") == "Ask MattGPT":
        user_input_local = st.chat_input("Ask anything…", key="ask_chat_input1")
    else:
        user_input_local = None
    if user_input_local:
        # If a live card is pending snapshot from the previous answer, snapshot it now
        if st.session_state.get("__pending_card_snapshot__"):
            _push_card_snapshot_from_state(stories)
            st.session_state["__pending_card_snapshot__"] = False

        # Append user's turn immediately to keep order deterministic
        _push_user_turn(user_input_local)

        # Clear context lock for fresh typed questions (not from suggestion chips)
        if not st.session_state.get("__ask_from_suggestion__"):
            st.session_state.pop("__ctx_locked__", None)
            st.session_state.pop("active_context", None)

        # Command aliases (view switches) should not trigger new retrieval
        cmd = re.sub(r"\s+", " ", user_input_local.strip().lower())
        cmd_map = {
            "narrative": "narrative",
            "key points": "key_points",
            "keypoints": "key_points",
            "deep dive": "deep_dive",
            "deep-dive": "deep_dive",
            "details": "deep_dive",
        }
        # If a quick command is used without any story context, show a friendly tip
        has_context = bool(
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        )
        if cmd in cmd_map and not has_context:
            _push_assistant_turn(
                "Quick mode commands like “key points” work after a story is in context — either select a story or ask a question first so I can cite sources. For now, try asking a full question."
            )
            st.rerun()
        if cmd in cmd_map and (
            ctx
            or st.session_state.get("active_story")
            or st.session_state.get("last_sources")
        ):
            # Resolve a target story: explicit context > last active story > last answer’s primary source
            target = ctx
            if not target:
                sid = st.session_state.get("active_story")
                if not sid:
                    srcs = st.session_state.get("last_sources") or []
                    if srcs:
                        sid = srcs[0].get("id")
                if sid:
                    target = next(
                        (x for x in stories if str(x.get("id")) == str(sid)), None
                    )

            if target:
                modes_local = story_modes(target)
                key = cmd_map[cmd]
                heading = {
                    "narrative": "Narrative",
                    "key_points": "Key points",
                    "deep_dive": "Deep dive",
                }[key]
                answer_md = (
                    f"**{heading} for _{target.get('title','')} — {target.get('client','')}_**\n\n"
                    + modes_local.get(key, "")
                )

                # Prime compact answer state (no assistant bubble)
                st.session_state["answer_modes"] = modes_local
                st.session_state["answer_mode"] = key
                st.session_state["last_answer"] = answer_md
                st.session_state["last_sources"] = [
                    {
                        "id": target.get("id"),
                        "title": target.get("title"),
                        "client": target.get("client"),
                    }
                ]
                # Show the answer card below the transcript
                _push_assistant_turn(answer_md)
                # Do NOT snapshot for command aliases; they don't represent a new question
                st.rerun()

        # Normal question → ask backend, persist state, append assistant turn
        # One-shot context lock: if a story was explicitly selected (chip/CTA),
        # use that story as context for THIS turn only, then clear the lock.
        # --- Determine context for THIS turn (one-shot lock) ---
        ctx_for_this_turn = ctx
        if st.session_state.pop("__ctx_locked__", False):  # consume the lock
            try:
                locked_ctx = get_context_story(stories)
            except Exception:
                locked_ctx = None
            if locked_ctx:
                ctx_for_this_turn = locked_ctx

        # --- Ask backend + render result ---
        with st.status("Searching Matt's experience...", expanded=True) as status:
            try:
                # Consume the suggestion flag (one-shot); we don't need its value here
                st.session_state.pop("__ask_from_suggestion__", None)

                # Ask is pure semantic; ignore Explore filters here
                resp = send_to_backend(user_input_local, {}, ctx_for_this_turn, stories)

                # Show confidence after retrieval
                sources = resp.get("sources", [])
                if sources:
                    first_id = str(sources[0].get("id", ""))
                    scores = st.session_state.get("__pc_last_ids__", {}) or {}
                    conf = scores.get(first_id)
                    if conf:
                        conf_pct = int(float(conf) * 100)
                        st.write(f"✓ Found relevant stories • {conf_pct}% match confidence")

                status.update(label="Answer ready!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Error occurred", state="error")
                _push_assistant_turn("Sorry, I couldn't generate an answer right now.")
                st.error(f"Backend error: {e}")
                st.rerun()

            else:
                set_answer(resp)

                # Add a static snapshot so the answer appears in-order as a bubble,
                # and suppress the bottom live card once to avoid duplication.
                if not st.session_state.get(
                    "ask_last_reason"
                ) and not st.session_state.get("__sticky_banner__"):
                    _push_card_snapshot_from_state(stories)
                    st.session_state["__suppress_live_card_once__"] = True

                st.rerun()