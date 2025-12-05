# mockui.py — 5P Stories + Ask MattGPT (polished demo, Pinecone-first w/ fallback)
import os
import re
import textwrap
import time

import streamlit as st

st.set_page_config(
    page_title="MattGPT — Story Cards", page_icon="🎯", layout="centered"
)

# =========================
# Config / constants
# =========================
PINECONE_MIN_SIM = 0.22  # suppress low-confidence semantic hits
_DEF_DIM = 384  # stub embedding vector size (keeps demo self-contained)

# =========================
# Safe Pinecone wiring (optional)
# =========================
try:
    from pinecone import Pinecone  # type: ignore
except Exception:
    Pinecone = None  # keeps the demo working without Pinecone installed

_PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
_PINECONE_INDEX = os.getenv("PINECONE_INDEX", "mattgpt-stories")
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
        # Create index lazily if not present — small dim for stub embedder
        existing = {i.name for i in _PC.list_indexes().indexes}
        if _PINECONE_INDEX not in existing:
            _PC.create_index(name=_PINECONE_INDEX, dimension=_DEF_DIM, metric="cosine")
        _PC_INDEX = _PC.Index(_PINECONE_INDEX)
        return _PC_INDEX
    except Exception:
        return None


# =========================
# Demo data
# =========================
STORIES = [
    {
        "id": "rbc-payments",
        "title": "Global Payments Modernization",
        "client": "RBC",
        "role": "Product & Delivery Lead",
        "domain": "Payments / Treasury",
        "personas": ["Product Leaders", "Banking Stakeholders"],
        "who": "Corporate banking customers & operations teams",
        "where": "RBC – Commercial Banking",
        "why": "Increase straight-through processing and reduce settlement delays",
        "how": [
            "Introduced OKR-driven roadmapping",
            "Implemented event-driven architecture",
            "Scaled CI/CD across teams",
        ],
        "what": [
            "Reduced wire transfer delays by 30%",
            "Improved SLA adherence to 99.5%",
        ],
        "star": {
            "situation": [
                "Legacy payments flows caused reconciliation delays and operations pain across regions."
            ],
            "task": [
                "Define a modernization roadmap and deliver near-term wins while aligning stakeholders."
            ],
            "action": [
                "Introduced OKR-driven roadmap and prioritized high-impact flows",
                "Implemented event-driven services and hardened CI/CD",
            ],
            "result": [
                "30% fewer wire transfer delays",
                "SLA adherence improved to 99.5%",
                "Stakeholder satisfaction up measurably",
            ],
        },
        "tags": ["Payments", "OKRs", "Event-Driven"],
    },
    {
        "id": "kp-rai",
        "title": "Responsible AI Governance",
        "client": "Kaiser Permanente",
        "role": "AI Program Lead",
        "domain": "AI/ML / Governance",
        "personas": ["Product Leaders", "Data Science Leaders", "Compliance"],
        "who": "Clinical operations & compliance stakeholders",
        "where": "Healthcare (Fortune 100)",
        "why": "Protect patient privacy while enabling predictive care",
        "how": [
            "Risk taxonomy & model registry",
            "Human-in-the-loop review",
            "Policy gating in CI/CD",
        ],
        "what": [
            "Zero high-severity compliance incidents post-launch",
            "Audit time reduced by 40%",
        ],
        "star": {
            "situation": [
                "Multiple ML pilots lacked centralized governance and clear risk controls."
            ],
            "task": [
                "Stand up a Responsible AI program that satisfied privacy and audit requirements."
            ],
            "action": [
                "Built risk taxonomy and model registry",
                "Added human-in-the-loop reviews and policy gates in CI/CD",
            ],
            "result": [
                "Zero high-severity compliance incidents post-launch",
                "Audit prep time reduced by 40%",
            ],
        },
        "tags": ["Responsible AI", "Governance", "Privacy"],
    },
]

# =========================
# Session state
# =========================
st.session_state.setdefault(
    "filters",
    {
        "personas": [],
        "clients": [],
        "domains": [],
        "roles": [],
        "tags": [],
        "q": "",
        "has_metric": False,
    },
)
st.session_state.setdefault("persona_filter", [])
st.session_state.setdefault("active_tab", "Stories")
st.session_state.setdefault("active_story", None)
st.session_state.setdefault("chat", [])
st.session_state.setdefault("seed_prompt", "")
st.session_state.setdefault("last_answer", "")
st.session_state.setdefault("last_sources", [])
st.session_state.setdefault("last_results", STORIES)

# For Pinecone snippets + low-confidence banner
st.session_state.setdefault("__pc_last_ids__", {})  # {story_id: score}
st.session_state.setdefault("__pc_snippets__", {})  # {story_id: snippet}
st.session_state.setdefault("__pc_suppressed__", False)

# =========================
# Tiny CSS polish
# =========================
st.markdown(
    """
<style>
.compact-row { display:flex; gap:16px; align-items:flex-start; }
.compact-left { flex: 1 1 auto; min-width:0; }
.compact-right { width: 160px; display:flex; align-items:center; justify-content:flex-end; }
.compact-summary {
  line-height: 1.35;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 2px;
}
.badge-row { display:flex; flex-wrap:wrap; gap:6px; margin-top:2px; margin-bottom:2px; }
.story-block { margin: 8px 0 14px 0; }
.badge {
  display:inline-flex; align-items:center; gap:6px;
  font-size:14px; line-height:1.2; padding:5px 10px; border-radius:999px;
  border:1px solid rgba(0,0,0,0.08); background: rgba(0,0,0,0.04);
}
.badge .dot { width:8px; height:8px; border-radius:50%; display:inline-block; }
.story-block .stMarkdown p { margin: 0.25rem 0; }
.field-label{ display:block; font-weight:700; text-transform:uppercase; letter-spacing:.02em;
  font-size:0.85rem; opacity:.85; margin:6px 0 2px; }
.card-summary{ font-size:1rem; line-height:1.4; opacity:.9; margin:6px 0 10px; }
/* Starter chips (Ask) */
#starter-chips { margin-top: 6px; }
#starter-chips .stButton>button {
  border-radius: 12px; background: transparent; border: 1px solid rgba(0,0,0,0.16);
  padding: 10px 16px; box-shadow: none; font-weight: 600;
}
#starter-chips .stButton>button:hover {
  background: rgba(0,0,0,0.04); border-color: rgba(0,0,0,0.28);
}
#starter-chips .stButton { margin-bottom: 8px; }
/* Sticky filters + chips */
.sticky-filters { position: sticky; top: 8px; z-index: 9; }
.active-chip-row { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin: 6px 0 2px 0; }
.results-count { font-weight:600; margin-right:8px; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Helpers
# =========================
METRIC_RX = re.compile(
    r"(\b\d{1,3}\s?%|\$\s?\d[\d,\.]*\b|\b\d+x\b|\b\d+(?:\.\d+)?\s?(pts|pp|bps)\b)", re.I
)
_BADGE_PALETTE = [
    "#4F46E5",
    "#059669",
    "#DC2626",
    "#D97706",
    "#0EA5E9",
    "#7C3AED",
    "#16A34A",
    "#EA580C",
    "#A855F7",
    "#0891B2",
]


def should_run_after_pause(key: str, value: str, wait: float = 0.6) -> bool:
    ts_key = f"__deb_ts__{key}"
    val_key = f"__deb_val__{key}"
    now = time.time()
    prev_val = st.session_state.get(val_key)
    if value != prev_val:
        st.session_state[val_key] = value
        st.session_state[ts_key] = now
        return False
    return (now - st.session_state.get(ts_key, 0.0)) >= wait


def _badge_color(label: str) -> str:
    if not label:
        return "#6B7280"
    idx = sum(ord(c) for c in label) % len(_BADGE_PALETTE)
    return _BADGE_PALETTE[idx]


def render_badges(domain: str | None, tags: list[str] | None):
    parts = []
    if domain:
        c = _badge_color(domain)
        parts.append(
            f'<span class="badge"><span class="dot" style="background:{c}"></span>'
            f"<strong>Domain</strong>&nbsp;{domain}</span>"
        )
    for t in tags or []:
        c = _badge_color(t)
        parts.append(
            f'<span class="badge"><span class="dot" style="background:{c}"></span>{t}</span>'
        )
    if parts:
        st.markdown(
            f'<div class="badge-row">{"".join(parts)}</div>', unsafe_allow_html=True
        )


def render_list(items: list[str] | None):
    for x in items or []:
        st.write(f"- {x}")


def render_outcomes(items: list[str] | None):
    for line in items or []:
        out = line
        for m in METRIC_RX.finditer(line or ""):
            token = m.group(0)
            out = out.replace(token, f"**{token}**")
        st.write(f"- {out}")


def _extract_metric_value(text: str):
    if not text:
        return None
    best = None
    for m in METRIC_RX.finditer(text):
        tok = m.group(0)
        if "%" in tok:
            try:
                num = float(tok.replace("%", "").strip())
            except Exception:
                num = 0.0
            score = 1000 + num
        else:
            digits = "".join([c for c in tok if c.isdigit() or c == "."])
            try:
                num = float(digits)
            except Exception:
                num = 0.0
            score = num
        item = (score, text)
        if best is None or item[0] > best[0]:
            best = item
    return best


def strongest_metric_line(s: dict) -> str | None:
    candidates = []
    for line in s.get("what") or []:
        v = _extract_metric_value(line or "")
        if v:
            candidates.append(v)
    for line in s.get("star", {}).get("result") or []:
        v = _extract_metric_value(line or "")
        if v:
            candidates.append(v)
    if not candidates:
        return None
    return max(candidates, key=lambda t: t[0])[1]


def build_5p_summary(s: dict) -> str:
    why = (s.get("why") or "").strip()
    how = ", ".join((s.get("how") or [])[:2]).strip()
    metric_line = strongest_metric_line(s)
    parts = []
    if why:
        parts.append(
            why if why[:2].lower() in ("to", "in") else (why[:1].lower() + why[1:])
        )
    if how:
        parts.append(f"by {how}")
    if metric_line:
        parts.append(f"resulting in {metric_line}")
    sent = ", ".join([p for p in parts if p]).strip()
    if sent and not sent.endswith("."):
        sent += "."
    return textwrap.shorten(sent, width=160, placeholder="…")


def story_card(s, idx=0):
    st.markdown('<div class="story-block">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"### {s.get('title','')}")
        st.markdown(
            f'<div class="card-summary">{build_5p_summary(s)}</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"Client: {s.get('client','')} • Role: {s.get('role','')} • {s.get('domain','')}"
        )
        render_badges(s.get("domain"), s.get("tags", []))

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<span class="field-label">Who</span>', unsafe_allow_html=True)
            st.write(s.get("who", "—"))
            st.markdown('<span class="field-label">Why</span>', unsafe_allow_html=True)
            st.write(s.get("why", "—"))
        with c2:
            st.markdown(
                '<span class="field-label">Where</span>', unsafe_allow_html=True
            )
            st.write(s.get("where", "—"))
            st.markdown(
                '<span class="field-label">How (Approach)</span>',
                unsafe_allow_html=True,
            )
            render_list(s.get("how", []))

        st.markdown(
            '<span class="field-label">What (Outcomes)</span>', unsafe_allow_html=True
        )
        render_outcomes(s.get("what", []))

        row_left, row_right = st.columns([3, 1])
        details_key = f"details_open__{s.get('id','x')}"
        is_open = st.session_state.get(details_key, False)

        with row_left:
            label = ("▾ " if is_open else "▸ ") + "See how it unfolded"
            if st.button(label, key=f"toggle_details_{s.get('id','x')}_{idx}"):
                st.session_state[details_key] = not is_open
                st.rerun()
            if st.session_state.get(details_key):
                with st.container(border=True):
                    st.markdown(
                        '<span class="field-label">What Was Happening</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("situation", []))
                    st.markdown(
                        '<span class="field-label">What We Wanted to Achieve</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("task", []))
                    st.markdown(
                        '<span class="field-label">What We Did About It</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("action", []))
                    st.markdown(
                        '<span class="field-label">The Difference It Made</span>',
                        unsafe_allow_html=True,
                    )
                    render_list(s.get("star", {}).get("result", []))

        with row_right:
            if st.button("Ask MattGPT about this", key=f"ask_{s.get('id','x')}_{idx}"):
                st.session_state["active_story"] = s.get("id")
                st.session_state["active_tab"] = "Ask MattGPT"
                st.session_state["seed_prompt"] = (
                    f"How were these outcomes achieved for {s.get('client','')} — {s.get('title','')}? "
                    "Focus on tradeoffs, risks, and replicable patterns."
                )
    st.markdown("</div>", unsafe_allow_html=True)


def compact_row(s, idx=0):
    st.markdown('<div class="story-block">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="compact-row">', unsafe_allow_html=True)
        # left side
        st.markdown('<div class="compact-left">', unsafe_allow_html=True)
        st.markdown(f"**{s['title']}**")
        st.caption(f"{s['client']}  •  {s['role']}")
        render_badges(s.get("domain"), s.get("tags", []))
        st.markdown(
            f'<div class="compact-summary">{build_5p_summary(s)}</div>',
            unsafe_allow_html=True,
        )

        # Optional Pinecone snippet if present
        snippet = st.session_state["__pc_snippets__"].get(s["id"])
        if snippet:
            st.caption(snippet)

        st.markdown("</div>", unsafe_allow_html=True)
        # right side CTA
        st.markdown('<div class="compact-right">', unsafe_allow_html=True)
        if st.button("Ask MattGPT", key=f"mock_ask_{s['id']}_{idx}"):
            st.session_state["active_story"] = s["id"]
            st.session_state["active_tab"] = "Ask MattGPT"
            st.session_state["seed_prompt"] = (
                f"How were these outcomes achieved for {s['client']} — {s['title']}? "
                "Focus on tradeoffs, risks, and replicable patterns."
            )
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def get_context_story():
    sid = st.session_state.get("active_story")
    if not sid:
        return None
    for s in STORIES:
        if s["id"] == sid:
            return s
    return None


def build_facets(stories):
    clients = sorted({s["client"] for s in stories})
    domains = sorted({s["domain"] for s in stories})
    roles = sorted({s["role"] for s in stories})
    tags = sorted({t for s in stories for t in s.get("tags", [])})
    personas = sorted({p for s in stories for p in s.get("personas", [])})
    return clients, domains, roles, tags, personas


def story_has_metric(s):
    for line in s.get("what") or []:
        if METRIC_RX.search(line or ""):
            return True
    for line in s.get("star", {}).get("result") or []:
        if METRIC_RX.search(line or ""):
            return True
    return False


def matches_filters(s, F=None):
    if F is None:
        F = st.session_state.get(
            "filters",
            {
                "personas": [],
                "clients": [],
                "domains": [],
                "roles": [],
                "tags": [],
                "has_metric": False,
                "q": "",
            },
        )
    if F["personas"] and not (set(F["personas"]) & set(s.get("personas", []))):
        return False
    if F["clients"] and s["client"] not in F["clients"]:
        return False
    if F["domains"] and s["domain"] not in F["domains"]:
        return False
    if F["roles"] and s["role"] not in F["roles"]:
        return False
    if F["tags"] and not (set(F["tags"]) & set(s.get("tags", []))):
        return False
    if F["has_metric"] and not story_has_metric(s):
        return False
    q = (F["q"] or "").strip().lower()
    if q:
        hay = " ".join(
            [
                s.get("title", ""),
                s.get("client", ""),
                s.get("role", ""),
                s.get("domain", ""),
                s.get("who", ""),
                s.get("where", ""),
                s.get("why", ""),
                " ".join(s.get("how", [])),
                " ".join(s.get("what", [])),
                " ".join(s.get("tags", [])),
            ]
        ).lower()
        if q not in hay:
            return False
    return True


# =========================
# Embedding + Pinecone query
# =========================
def _embed(text: str) -> list[float]:
    """Deterministic stub embedder so the demo runs without external models."""
    import math

    vec = [0.0] * _DEF_DIM
    if not text:
        return vec
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % _DEF_DIM] += (ch % 13) / 13.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def pinecone_semantic_search(
    query: str, filters: dict, top_k: int = 5
) -> list[dict] | None:
    idx = _init_pinecone()
    if not idx or not query:
        return None
    pc_filter = {}
    if filters.get("domains"):
        pc_filter["domain"] = {"$in": filters["domains"]}
    if filters.get("clients"):
        pc_filter["client"] = {"$in": filters["clients"]}
    try:
        qvec = _embed(query)
        res = idx.query(
            vector=qvec, top_k=top_k, include_metadata=True, filter=pc_filter or None
        )
        hits = []
        st.session_state["__pc_last_ids__"].clear()
        st.session_state["__pc_snippets__"].clear()
        for m in res.matches:
            meta = (m.metadata or {}) if hasattr(m, "metadata") else {}
            sid = meta.get("id")
            score = getattr(m, "score", 0.0) or 0.0
            if not sid:
                continue
            hit = next((s for s in STORIES if s.get("id") == sid), None)
            if hit:
                hits.append(
                    {
                        "story": hit,
                        "score": float(score),
                        "snippet": meta.get("summary"),
                    }
                )
        return hits
    except Exception:
        return None


def semantic_search(query: str, filters: dict):
    """Pinecone-first with confidence threshold; fallback to local filters; persists snippet/score for UI."""
    hits = pinecone_semantic_search(query, filters)
    st.session_state["__pc_suppressed__"] = False
    if hits is not None:
        # Keep Pinecone ordering; filter by threshold
        confident = [h for h in hits if h["score"] >= PINECONE_MIN_SIM]
        if confident:
            # Store snippet/score for UI rows
            st.session_state["__pc_last_ids__"] = {
                h["story"]["id"]: h["score"] for h in confident
            }
            st.session_state["__pc_snippets__"] = {
                h["story"]["id"]: (h["snippet"] or build_5p_summary(h["story"]))
                for h in confident
            }
            # Apply local facet gates on top
            return [
                h["story"] for h in confident if matches_filters(h["story"], filters)
            ]
        else:
            # Low-confidence — drop to local and flag UI
            st.session_state["__pc_suppressed__"] = bool(query.strip())
    # Local-only path
    return [s for s in STORIES if matches_filters(s, filters)]


# =========================
# Ask backend (stub)
# =========================
def rag_answer(question: str, filters: dict):
    hits = [s for s in STORIES if matches_filters(s, filters)][:2]
    if not hits:
        return {
            "answer": "I couldn’t find a strong match yet. Try adjusting filters or keywords.",
            "sources": [],
        }
    bullets = "\n".join(f"- {h['title']} ({h['client']})" for h in hits)
    return {
        "answer": f"Here’s how I’ve approached that:\n{bullets}",
        "sources": [h["title"] for h in hits],
    }


def send_to_backend(prompt: str, filters: dict, ctx: dict | None):
    return rag_answer(prompt, filters)


def set_answer(resp: dict):
    st.session_state["last_answer"] = resp.get("answer", "")
    st.session_state["last_sources"] = resp.get("sources", [])


# =========================
# UI — Home / Stories / Ask / About
# =========================
clients, domains, roles, tags, personas_all = build_facets(STORIES)
tabs = st.tabs(["Home", "Stories", "Ask MattGPT", "About Matt"])

# --- HOME ---
with tabs[0]:
    st.subheader("Welcome")
    st.caption("Pick a path to get started.")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(
            "📖 Explore Stories", use_container_width=True, key="home_stories"
        ):
            st.session_state["active_tab"] = "Stories"
            st.rerun()
    with c2:
        if st.button("💬 Ask MattGPT", use_container_width=True, key="home_ask"):
            st.session_state["active_tab"] = "Ask MattGPT"
            st.rerun()
    with c3:
        if st.button("👤 About Matt", use_container_width=True, key="home_about"):
            st.session_state["active_tab"] = "About Matt"
            st.rerun()
    st.markdown("##### Quick search")
    q_global = st.text_input(
        "Search across stories",
        value=st.session_state["filters"].get("q", ""),
        placeholder="Try: payments modernization, governance, OKRs…",
        label_visibility="collapsed",
        key="home_q",
    )
    if q_global != st.session_state["filters"].get("q"):
        st.session_state["filters"]["q"] = q_global
        st.session_state["active_tab"] = "Stories"
        st.rerun()

# --- STORIES ---
with tabs[1]:
    # Sticky filter bar + full facet panel
    st.markdown('<div class="sticky-filters">', unsafe_allow_html=True)
    F = st.session_state["filters"]
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            F["personas"] = st.multiselect(
                "Audience",
                personas_all,
                default=F["personas"],
                key="facet_personas",
                help="Who would find this story most relevant?",
            )
            F["clients"] = st.multiselect(
                "Client", clients, default=F["clients"], key="facet_clients"
            )
        with c2:
            F["domains"] = st.multiselect(
                "Domain", domains, default=F["domains"], key="facet_domains"
            )
            F["roles"] = st.multiselect(
                "Role", roles, default=F["roles"], key="facet_roles"
            )
        with c3:
            F["tags"] = st.multiselect(
                "Tags", tags, default=F["tags"], key="facet_tags"
            )
            F["has_metric"] = st.toggle(
                "Has metric in outcomes", value=F["has_metric"], key="facet_has_metric"
            )

        F["q"] = st.text_input(
            "Search keywords",
            value=F["q"],
            placeholder="title, client, outcomes…",
            key="facet_q",
        )

        cols = st.columns([1, 4])
        with cols[0]:
            if st.button("Reset filters", key="btn_reset_filters"):
                st.session_state["filters"] = {
                    "personas": [],
                    "clients": [],
                    "domains": [],
                    "roles": [],
                    "tags": [],
                    "q": "",
                    "has_metric": False,
                }
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Debounced semantic search (Pinecone-first with fallback)
    if should_run_after_pause("story_search", F["q"], wait=0.6) or not F["q"]:
        view = semantic_search(F["q"], F)
        st.session_state["last_results"] = view
    else:
        view = st.session_state["last_results"]
        st.caption("⏳ searching… (waiting for you to pause)")

    # Active chips + result count (inline rendering, simple)
    st.session_state["__results_count__"] = len(view)
    chips = []
    if F.get("q"):
        chips.append(("Search", f"“{F['q']}”", ("q", None)))
    if F.get("has_metric"):
        chips.append(("Flag", "Has metric", ("has_metric", None)))
    for label, key in [
        ("Audience", "personas"),
        ("Client", "clients"),
        ("Domain", "domains"),
        ("Role", "roles"),
        ("Tag", "tags"),
    ]:
        for v in F.get(key, []):
            chips.append((label, v, (key, v)))
    st.markdown('<div class="active-chip-row">', unsafe_allow_html=True)
    st.markdown(
        f'<span class="results-count">{len(view)} results</span>',
        unsafe_allow_html=True,
    )
    cleared = False
    for i, (_, text, (k, v)) in enumerate(chips):
        if st.button(f"✕ {text}", key=f"chip_{k}_{i}"):
            if k == "q":
                F["q"] = ""
            elif k == "has_metric":
                F["has_metric"] = False
            else:
                F[k] = [x for x in F.get(k, []) if x != v]
            cleared = True
    st.markdown("</div>", unsafe_allow_html=True)
    if cleared:
        st.rerun()

    # Optional sort + view toggle
    if st.checkbox("Sort: Metric-rich first", value=True, key="sort_metric"):
        view.sort(key=lambda s: story_has_metric(s), reverse=True)

    view_mode = st.radio(
        "View", ["Cards", "List"], index=1, horizontal=True, key="view_mode"
    )

    # Low-confidence UX + render
    if not view:
        if F["q"] and st.session_state["__pc_suppressed__"]:
            st.warning(
                "Tried semantic search but didn’t find anything confidently relevant. Try rephrasing or pick a filter."
            )
            sug = ["Payments modernization", "Generative AI", "Governance", "OKRs"]
            cols = st.columns(len(sug))
            for i, tip in enumerate(sug):
                with cols[i]:
                    if st.button(tip, key=f"suggest_{i}"):
                        F["q"] = tip
                        st.rerun()
        else:
            st.info("No stories match your filters yet.")
        if st.button("Clear filters", key="clear_filters_empty"):
            st.session_state["filters"] = {
                "personas": [],
                "clients": [],
                "domains": [],
                "roles": [],
                "tags": [],
                "q": "",
                "has_metric": False,
            }
            st.rerun()
    else:
        renderer = story_card if view_mode == "Cards" else compact_row
        for i, s in enumerate(view):
            renderer(s, i)

# --- ASK (debounced + manual send) ---
with tabs[2]:
    ctx = get_context_story()
    if ctx:
        with st.container(border=True):
            st.markdown(f"**Context:** {ctx['title']}")
            st.caption(
                f"Client: {ctx['client']} • Role: {ctx['role']} • {ctx['domain']}"
            )
            st.caption("Change context via the Stories tab.")
    else:
        st.info("Pick a story and click ‘Ask MattGPT about this’ to preload context.")

    # Starter chips (match Home style)
    starters = [
        "Summarize this in 3 key bullets.",
        "What challenges were overcome?",
        "What trade-offs did we make and why?",
        "How could we replicate this elsewhere?",
    ]
    st.markdown('<div id="starter-chips">', unsafe_allow_html=True)
    per_row = min(3, max(1, len(starters)))
    idx_base = 0
    for row_start in range(0, len(starters), per_row):
        cols = st.columns(per_row)
        for j, tip in enumerate(starters[row_start : row_start + per_row]):
            with cols[j]:
                if st.button(tip, key=f"starter_{idx_base}", use_container_width=True):
                    st.session_state["ask_input"] = tip
                    st.rerun()
            idx_base += 1
    st.markdown("</div>", unsafe_allow_html=True)

    prompt = st.text_area(
        "Ask MattGPT",
        value=st.session_state.get(
            "ask_input", st.session_state.get("seed_prompt", "")
        ),
        key="ask_input",
        height=120,
        placeholder="Type your question…",
    )

    ran_key = "__ask_ran_for__"
    can_autorun = False
    if prompt.strip():
        if should_run_after_pause("ask_input", prompt, wait=0.6):
            can_autorun = True
        else:
            st.caption("⏳ answering… (waiting for you to pause)")

    if can_autorun and st.session_state.get(ran_key) != prompt:
        with st.spinner("Answering…"):
            resp = send_to_backend(prompt, st.session_state.get("filters", {}), ctx)
        set_answer(resp)
        st.session_state[ran_key] = prompt

    c_send, c_clear = st.columns([1, 1])
    with c_send:
        if st.button("Send", key="ask_send"):
            with st.spinner("Answering…"):
                resp = send_to_backend(prompt, st.session_state.get("filters", {}), ctx)
            set_answer(resp)
            st.session_state[ran_key] = prompt
    with c_clear:
        if st.button("Clear", key="ask_clear"):
            st.session_state["seed_prompt"] = ""
            st.session_state["ask_input"] = ""
            st.session_state["last_answer"] = ""
            st.session_state["last_sources"] = []
            st.session_state.pop(ran_key, None)
            st.rerun()

    if st.session_state.get("last_answer"):
        st.markdown("#### Answer")
        st.markdown(st.session_state["last_answer"])
        if st.session_state.get("last_sources"):
            st.markdown("**Sources**")
            for s in st.session_state["last_sources"]:
                st.write(f"• {s}")
        st.download_button(
            "Download answer",
            data=st.session_state["last_answer"].encode("utf-8"),
            file_name="answer.txt",
            mime="text/plain",
            key="download_answer",
        )

# --- ABOUT ---
with tabs[3]:
    st.subheader("About Matt")
    st.caption("A human-centered portfolio + AI assistant.")
    st.markdown(
        """
**What this is** — A simple place to browse outcomes (Stories) and ask follow‑ups (Ask MattGPT).

**How to use it**
- **Stories:** Filter by audience, client, domain, role, tags, or search keywords.
- **Ask MattGPT:** Click **Ask MattGPT about this** on any story to preload context, then type a question.
  Debounce will auto-run when you pause typing; you can also press **Send**.

**What’s next**
- Real embeddings + Pinecone metadata snippets
- Cleaner card/list theming
- Optional keep‑alive
"""
    )
