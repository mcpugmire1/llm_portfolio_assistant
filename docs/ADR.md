# Architectural Decision Records (ADR)

This document is a running log of key architectural and design decisions for the MattGPT / Portfolio Assistant project.  
We are using a single ADR.md file (instead of one file per decision) for simplicity at this stage.

---

## ADR 001 — Pinecone-First Semantic Search  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We need a scalable and accurate search strategy across curated STAR/5P stories. Literal keyword lookups are insufficient, and we want to handle natural questions (e.g., "How did you apply GenAI in healthcare?") gracefully.  
We validated that Pinecone-first retrieval with confidence gating is essential to avoid regressions and align with user expectations. Literal string maps proved brittle. Configuration should be centralized and consistent.

**Decision:**  
Adopt a **Pinecone-first semantic search** strategy using embeddings.  
- Pinecone provides similarity search and metadata filtering.  
- We apply a **low-confidence threshold** to suppress weak hits.  
- If Pinecone returns no confident results, fall back to local keyword/facet filtering.  
- `app_next.py` must implement **Pinecone-first semantic retrieval** with confidence gating and local FAISS fallback, mirroring `mockui.py`.  
- Environment and secrets are loaded via `load_dotenv()` with `st.secrets` fallback.  

**Consequences:**  
- Ensures semantic matches come first.  
- Preserves resilience when embeddings or Pinecone are unavailable.  
- Avoids brittle hardcoded string maps.
- Ensures alignment with validated UX.  
- Reduces risk of regressions.  
- Centralizes configuration and avoids divergence.  
- No literal string maps for retrieval.  
- Nonsense queries handled via low-confidence suppression plus helpful suggestions.  
---

## ADR 002 — Excel as System of Truth for Stories  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We curate STAR/5P stories in Excel. Content evolves often, and we want non-technical edits without touching code.  

**Decision:**  
Treat the **Excel master file as the source of truth**.  
- Scripts (`generate_jsonl_from_excel.py`, `fill_5p_fields.py`) convert Excel → JSONL → Pinecone vectors.  
- No story text, tense, or metadata should be hardcoded in the app.  

**Consequences:**  
- Simplifies content updates.  
- Reduces risk of divergence between code and curated content.  
- Empowers non-developers to update stories.

---

## ADR 003 — Single ADR File (vs. Multiple)  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
Industry practice sometimes favors one ADR per file (`ADR-001.md`, etc.). For our project, this adds overhead.  

**Decision:**  
Use a **single `ADR.md` file** as a chronological decision log. Split into multiple files only if it becomes unmanageable.  

**Consequences:**  
- Lightweight to maintain alongside `Backlog.md` and `Roadmap.md`.  
- Easy to review in one place.  
- Less discoverability for very large sets of ADRs, but acceptable for now.

---

## ADR 004 — Hybrid Search (Keyword + Semantic)  
**Date:** 2025-08-21  
**Status:** Planned  

**Context:**  
Semantic search (Pinecone) captures natural language queries well, but exact keywords (e.g., client names, acronyms) can still be important.  

**Decision:**  
Adopt a **hybrid search** strategy in the future:  
- Semantic similarity via Pinecone  
- Keyword/facet filters layered on top  
- Potentially integrate keyword signals into scoring  

**Consequences:**  
- Improves precision on proper nouns and acronyms  
- Slightly more complexity in query pipeline  

---

## ADR 005 — Streamlit-First UI  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We need a lightweight, interactive front-end for story exploration and Q&A.  

**Decision:**  
Use **Streamlit** as the primary UI framework.  
- Rapid iteration and live reload  
- Easy filters, tabs, and layout control  

**Consequences:**  
- Low barrier for MVPs and demos  
- Less flexible than a full frontend framework, but sufficient for current needs  

---

## ADR 006 — Markdown Backlog and Roadmap (vs. Jira)  
**Date:** 2025-08-21  
**Status:** Superseded by ADR 029  

**Context:**  
We don’t want to maintain an external tool (like Jira) for backlog/roadmap at this stage.  

**Decision:**  
Use **Backlog.md** and **Roadmap.md** in `/docs` to capture tasks and priorities.  

**Consequences:**  
- Lightweight and version-controlled  
- Less automation and workflow support than Jira  

---

## ADR 007 — JSONL as Intermediate Content Format  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We need a machine-readable format between Excel (system of truth) and Pinecone vectors.  

**Decision:**  
Generate **JSONL files** (one story per line) as the intermediate format.  
- Scripts output `echo_star_stories.jsonl` and enriched variants  
- JSONL is consumed by Pinecone upserts and mock UI  

**Consequences:**  
- Simplifies debugging and pipelines  
- Adds an intermediate artifact to version control  

---

## ADR 008 — Single Repo, Not Microservices  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
We’re a small project; splitting into microservices adds overhead.  

**Decision:**  
Keep everything (backend scripts, UI, docs) in a **single repository**.  

**Consequences:**  
- Simple dev experience  
- Risk of monolith bloat later, but acceptable for now  

---

## ADR 009 — Devcontainer for Consistent Setup  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
Contributors may have different local environments.  

**Decision:**  
Use **`.devcontainer`** with pinned dependencies to ensure consistent setup.  

**Consequences:**  
- Reduces “works on my machine” issues  
- Requires VSCode or devcontainer-compatible tooling  

---

## ADR 010 — Pinecone Similarity Thresholds & Snippets  
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
Not all Pinecone results are useful; low-similarity hits can confuse users.  

**Decision:**  
Apply a **similarity threshold (minSim = 0.22)** to suppress weak hits.  
- Show Pinecone-provided snippet or fallback to 5P Summary  
- Flag low-confidence cases in UI for transparency  

**Consequences:**  
- Improves trust in results  
- Some relevant but low-similarity matches may be hidden  


## ADR 011 — Content Curation Rules
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
During roadmap/backlog discussions, we agreed the portfolio should only surface *finalized, interview-ready* stories to maintain quality and consistency.  

**Decision:**  
Only curated, finalized STAR/5P stories are included in the content pipeline (Excel → JSONL → Pinecone). Drafts or incomplete items are excluded.  

**Consequences:**  
- Maintains high quality and consistency across surfaced content  
- Avoids recruiters seeing incomplete or draft material  
- Requires discipline in curation before pipeline ingestion  


## ADR 012 — UI Philosophy
**Date:** 2025-08-21  
**Status:** Accepted  

**Context:**  
The UX should feel conversational, like ChatGPT. Multiple conversations highlighted avoiding jargon or structural labels (e.g., "STAR" or "5P") in the UI, while still leveraging those frameworks behind the scenes.  

**Decision:**  
Maintain a natural, chat-like interaction style. Do not expose "STAR/5P" terms in UI labels. Instead, surface user-friendly options like "summary," "narrative," or "deep dive."  

**Consequences:**  
- Keeps UI accessible and intuitive for recruiters and hiring managers  
- Still leverages structured frameworks internally for consistency  
- Avoids confusing non-technical audiences with jargon  

ADR-PINECONE-FIRST (2025-08-20)
Decision: app_next.py must implement Pinecone-first semantic retrieval with confidence gating and local FAISS fallback, mirroring mockui.py. Env/secrets are loaded with load_dotenv() + st.secrets fallback.
Why: Aligns with validated UX, reduces regressions, and centralizes configuration.
Status: Accepted.
Implication: No literal string maps for retrieval; “nonsense” queries handled via low-confidence suppression + suggestions.


## ADR 13: Pinecone-First Semantic Search with Low-Confidence & Nonsense Handling

**Date:** 2025-08-21

**Decision:**  
We will continue with a Pinecone-first strategy for semantic search, using a confidence threshold (`PINECONE_MIN_SIM`) as the primary filter. If Pinecone results fall below threshold, fall back to local keyword/filter search. We explicitly avoid literal string lookup or hardcoding mappings in code.

**Nonsense Handling:**  
- Out-of-scope or nonsensical queries (e.g., "weather today", "McDonald's salaries") are filtered via a lightweight rules/config file, not hardcoded.  
- If detected, MattGPT responds with: "That’s outside scope, but here’s what I can help you with…" plus suggested queries.  
- All off-scope queries are logged for review and vocabulary improvement.

**Rationale:**  
- Preserves consistency with Pinecone-first architecture defined earlier.  
- Avoids regressions into brittle literal lookups.  
- Keeps nonsense handling configurable and data-driven.  
- Aligns with industry RAG best practices: abstain confidently, steer helpfully, and learn iteratively.

**Status:** Accepted

---

## ADR 014 — Canonical Field Naming for Client & Title
**Date:** 2025-09-03  
**Status:** Accepted  

**Context:**  
Repeated confusion arose around whether to use `Title` vs. `Story_Title` and `Client` vs. `client` fields in the JSONL export and downstream UI. This led to mismatches and blank displays in the mock UI.  

**Decision:**  
- The Excel-to-JSONL exporter must write records with `Title` and `Client` fields.  
- The loader/UI must normalize these to lowercase (`title`, `client`) for rendering.  
- No additional variants (`Story_Title`, `short_title`, etc.) are introduced.  

**Consequences:**
- Ensures consistency across Excel, JSONL, Pinecone, and UI.
- Eliminates recurring mismatch debates.
- Simplifies pipeline code and reduces maintenance overhead.
- Requires a one-time migration to map any legacy `Story_Title` keys to `Title`.

---

## ADR 015 — JavaScript Override for Streamlit Emotion-Cache Button Styling
**Date:** 2025-10-28
**Status:** Accepted

**Context:**
Streamlit uses emotion-based CSS-in-JS with dynamically generated classes (e.g., `.st-emotion-cache-7lqsib`) that have higher specificity than custom CSS. This prevents normal CSS overrides, even with `!important`, making it impossible to apply consistent button styling (purple theme #8B5CF6) across the portfolio website. The application is a job search portfolio aimed at recruiters and hiring managers, requiring professional, consistent visual presentation.

**Problem Evidence:**
```html
<!-- Streamlit-rendered button -->
<button class="st-emotion-cache-7lqsib e8vg11g2" data-testid="stBaseButton-secondary">
    View Projects →
</button>
```

Custom CSS attempts failed:
```css
button.st-emotion-cache-7lqsib {
    background: #8B5CF6 !important;  /* IGNORED - emotion classes win */
}
```

**Decision:**
Use `streamlit.components.v1.html()` to inject JavaScript that applies inline styles via `window.parent.document`, bypassing the emotion-cache specificity issue.

**Implementation Pattern:**
```python
import streamlit.components.v1 as components

components.html("""
<script>
(function() {
    function applyPurpleButtons() {
        const parentDoc = window.parent.document;
        const buttons = parentDoc.querySelectorAll('[class*="st-key-btn_"] button');

        buttons.forEach(function(button) {
            if (!button.dataset.purpled) {
                button.dataset.purpled = 'true';
                button.style.cssText = 'background: white !important; color: #8B5CF6 !important; border: 2px solid #e5e5e5 !important;';

                button.addEventListener('mouseenter', function() {
                    this.style.cssText = 'background: #8B5CF6 !important; color: white !important; border: 2px solid #8B5CF6 !important;';
                });
                button.addEventListener('mouseleave', function() {
                    this.style.cssText = 'background: white !important; color: #8B5CF6 !important; border: 2px solid #e5e5e5 !important;';
                });
            }
        });
    }

    // Handle async rendering
    setTimeout(applyPurpleButtons, 100);
    setTimeout(applyPurpleButtons, 500);
    setTimeout(applyPurpleButtons, 1000);
    setInterval(applyPurpleButtons, 2000);  // Catch dynamically added buttons
})();
</script>
""", height=0)
```

**Why This Works:**
- `window.parent.document` accesses Streamlit's DOM from iframe context
- `style.cssText` applies inline styles (CSS specificity: 1,0,0,0 - highest possible)
- `dataset.purpled` flag prevents duplicate event listener attachment
- Multiple `setTimeout` calls handle Streamlit's async rendering pipeline
- `setInterval` catches buttons added later (e.g., pagination, filters)
- Event listeners maintain hover/interaction states

**Alternatives Considered:**
1. ❌ **Pure CSS with `!important`** - Doesn't work; emotion classes have higher specificity
2. ❌ **CSS with nuclear selectors** - Still insufficient against emotion-cache
3. ❌ **Custom Streamlit component** - Too heavyweight for simple button styling
4. ❌ **Fork Streamlit** - Maintenance nightmare, not sustainable
5. ❌ **Modify Streamlit source** - Same issues as forking
6. ✅ **JavaScript inline styles** - Pragmatic, version-independent solution

**Trade-offs:**
- **Pros:**
  - Complete control over button styling
  - Works across all Streamlit versions
  - No modifications to Streamlit source code
  - Maintains hover states and interactions
  - Can target specific buttons via key patterns
- **Cons:**
  - Adds ~0.5-1KB per page (negligible impact)
  - Timing-dependent (100ms, 500ms delays)
  - Must handle button lifecycle (mount/unmount scenarios)
  - Requires iframe context awareness

**Usage Pattern:**
```python
# Target specific buttons by key
components.html(f"""
<script>
const container = window.parent.document.querySelector('.st-key-btn_{button_index}');
const button = container.querySelector('button');
// ... styling logic
</script>
""", height=0)
```

**Consequences:**
- **Positive:** Achieved consistent purple button theme across all pages (home, landing, explore stories)
- **Positive:** Professional appearance for recruiter/hiring manager audience
- **Positive:** Pattern established for future Streamlit styling challenges
- **Negative:** Technical debt if migrating away from Streamlit
- **Negative:** Must maintain timing logic if Streamlit rendering changes
- **Learning:** Inline styles are the highest CSS specificity weapon

**Lessons Learned:**
- Streamlit's emotion-cache is intentional (CSS-in-JS architecture)
- Inline styles via `style.cssText` have maximum CSS specificity
- Async rendering requires multiple timing strategies
- Always use dataset flags to prevent duplicate event listeners
- User quality standards drive technical solutions ("Do you think a half ass solution would help me land a new job? yes or no?")

**Applied To:**
- Home page category buttons ([legacy_components.py#L1046-L1094](../ui/legacy_components.py))
- Explore Stories card buttons ([explore_stories.py#L1378-L1423](../ui/pages/explore_stories.py))
- Landing page buttons (banking_landing.py, cross_industry_landing.py)

---

## ADR 016 — Two-Step Pipeline for JD Requirement Extraction

**Date:** 2026-03-25
**Status:** Accepted; ADR 063 corrects its extraction model: Role Match's calls run on DEFAULT_CHAT_MODEL, not Claude

**Context:**
The JD Match feature requires mapping job description requirements to STAR stories in Pinecone. Job descriptions vary widely in format — bulleted lists, narrative paragraphs, mixed structures, implicit requirements embedded in responsibilities. A single Pinecone query against raw JD text would produce imprecise retrieval and no structured output.

**Decision:**
Use a two-step pipeline:

1. **LLM extraction pass** — send raw JD text to Claude and extract structured requirements as JSON: required qualifications, preferred qualifications, responsibilities, implicit signals. This normalizes format variance before any vector search.

2. **Pinecone query pass** — use extracted requirement clusters as discrete semantic queries against the story corpus. One query per requirement cluster produces per-requirement match evidence rather than a single blended result.

**Clarification on retrieval layer (updated 2026-03-26):**
The Pinecone query pass reuses `pinecone_service.py` query functions and the existing index/embedding model directly. It does not route through the Ask MattGPT RAG pipeline (`backend_service.py`, `story_intelligence.py`). The assessment reasoning layer in `jd_assessor.py` is purpose-built for structured per-requirement evaluation, distinct from the conversational synthesis mode in Ask MattGPT.

**Three-step pipeline (refined from original two-step):**
1. **LLM extraction pass** — JD text → structured requirements JSON (Stage 1, validated)
2. **Pinecone retrieval pass** — per-requirement semantic query via `pinecone_service.py` → top candidate stories per requirement
3. **LLM assessment pass** — requirements + candidate stories → structured match report (✓ strong / ~ partial / ✗ gap) with story evidence and gap explanations

**Alternatives considered:**
- Single Pinecone query against full JD text — rejected. Produces blended retrieval with no per-requirement traceability. Cannot generate the structured match output the feature requires.
- Keyword extraction only — rejected. Misses semantic equivalents (e.g. "delivery excellence" matching "zero-defect delivery" stories).
- Pure long context (all 130 stories in one LLM call, no Pinecone) — rejected. Works at current corpus size but introduces noise from irrelevant stories. Pinecone pre-filtering produces a focused, higher-quality context for the assessment LLM.
- Routing through existing Ask MattGPT RAG pipeline — rejected. The conversational synthesis pipeline is optimized for narrative answers, not structured per-requirement evaluation. Shoe-horning a different output format through an existing pipeline adds coupling without benefit.

**Consequences:**
- Two LLM calls + per-requirement Pinecone queries per assessment — acceptable latency with parallel retrieval
- Extraction prompt is load-bearing — prompt design session required before implementation
- Per-requirement story evidence enables the LinkedIn-style match format
- Pipeline is testable in isolation: extraction, retrieval, and assessment steps can be evaled independently
- Shared infrastructure (Pinecone index, embeddings, `pinecone_service.py`) keeps the solution harmonious with the existing architecture

---

## ADR 017 — Avatar Sizing Standards (Inline Style Enforcement)

**Date:** 2025-10 (original decision); 2026-04 (promoted to ADR)
**Status:** Accepted

**Context:**
Avatar sizes drifted across views (50px, 60px, 64px variations) as different code changes adjusted sizing independently. Users notice inconsistency between header avatars and chat avatars. Streamlit's emotion-cache classes override normal CSS, so avatar sizing must be enforced through inline styles or high-specificity selectors. Without a documented standard, code changes (including AI-assisted changes) repeatedly introduce sizing regressions.

**Decision:**
Standardize avatar sizes with two tiers, enforced via inline styles to override emotion-cache:

- **Header avatars (all pages): 64px** — Landing page headers, conversation headers, About Matt
- **Chat avatars (in-conversation): 60px** — Both Agy and user avatars in the chat stream

**Implementation:**

Header avatars use inline `width`/`height` attributes plus inline `style`:
```html
<img src="...agy_avatar.png"
     width="64" height="64"
     style="width: 64px; height: 64px; border-radius: 50%;"
     alt="Agy">
```

Chat avatars use high-specificity CSS with `!important`:
```css
.stChatMessage > img[alt="assistant avatar"] {
    width: 60px !important;
    height: 60px !important;
    border-radius: 50% !important;
}
```

**Rationale:**
- Headers need visual prominence → 64px
- Chat needs balanced sizing → 60px (not too large, not too small)
- Inline styles required to override Streamlit emotion-cache (same constraint as ADR 015)
- Two-tier system is simple enough to remember and enforce

**Consequences:**
- Any code changing avatar sizing must check this ADR first
- AI coding assistants should reference this ADR before modifying avatar-related CSS

---

## ADR 018 — Confidence Threshold Calibration for Pinecone Semantic Search

**Date:** 2025-12 (original calibration); 2026-05-14 (promoted to ADR)
**Status:** Superseded by ADR 026

**Context:**
The semantic-search pipeline gates query confidence into three buckets — High / Low / None — using two thresholds applied to Pinecone's raw similarity scores. The original thresholds (~0.50) were badly miscalibrated against the corpus and embedding model: legitimate queries like "What problems does Matt solve?" scored 0.381 and got suppressed as low-confidence, while off-topic queries scored 0.075–0.129 and bypassed the gate's intent. Calibration was painful (December 2025 session) — multiple rounds of empirical tuning against real queries before settling on the current values.

**Decision:**
Set Pinecone confidence thresholds at:
- `CONFIDENCE_HIGH = 0.25` — top similarity ≥ 0.25 means "found X stories" (no warning banner)
- `CONFIDENCE_LOW = 0.15` — top similarity ≥ 0.15 but < 0.25 means "relevance may be low" warning banner shown
- Below `0.15` — "no strong matches" suppression

Both constants live in `config/constants.py` as the single source of truth.

**Rationale:**
- Empirically calibrated against legitimate vs off-topic queries on the current corpus + embedding model (OpenAI `text-embedding-3-small`, 1536 dims). Lower thresholds than the original ~0.50 because OpenAI's small embedding model produces tighter similarity distributions than the calibration originally assumed.
- The 0.15 / 0.25 split creates a narrow but useful "soft confidence" band where users see results with a relevance warning — gives them a chance to refine vs. getting either confident results or an outright rejection.
- Stable since January 2026; no production failures attributable to threshold misfires since calibration landed.

**Edge cases to watch (no active monitoring, surface if observed):**
- The narrow 0.15–0.25 band is context-dependent — same query shape can land in different buckets depending on retrieval ranking. A query that's "almost" relevant might oscillate across runs.
- Adding new canonical phrases or significantly changing the corpus could shift the similarity distribution and require recalibration. Last meaningful corpus shift: March 2026 data quality cleanup (85+ stories enriched).
- If the OpenAI embedding model is ever updated/retired, thresholds will need recalibration against the new distribution.

**Consequences:**
- Threshold changes require empirical testing against the full eval suite, not theoretical adjustment.
- The thresholds are NOT a configuration knob to "make rejection stricter" — they're calibrated against the embedding distribution; changing them without recalibrating produces the original problem (legitimate queries blocked).
- The "low-confidence banner" UX exists because the soft band is intentional; don't collapse it into a binary accept/reject.

**Historical context (migrated from MATTGPT-029, May 14, 2026):**
The "low-confidence banner edge cases" backlog ticket (logged April 2026 test audit) flagged that the banner "sometimes triggers incorrectly" but had no specific reproduction. The ticket was closed Decided Against on May 14, 2026 with the rationale that without a concrete failing case, there's nothing to investigate. This ADR captures the underlying threshold-calibration history so future investigators have the context if a real misfire ever surfaces.
- If a new avatar context is added (e.g., Role Match), it maps to one of the two tiers

---

## ADR 019 — No Cross-Query Session State in `diversify_results`

**Date:** 2026-05-18
**Status:** Superseded by ADR 047
**Related tickets:** MATTGPT-073 (resolved), MATTGPT-061, MATTGPT-021, MATTGPT-074

**Context:**
The `diversify_results` function in `ui/pages/ask_mattgpt/backend_service.py` was originally written on November 28, 2025 (commit `d657ed0`) with two co-located mechanisms:
1. **Within-query client diversity** — for a single Pinecone retrieval pool, prefer named clients over generics, limit stories per client, and cap result size. This has clear stated rationale in the commit message ("prevent single-client domination in results") and is genuinely load-bearing.
2. **Cross-query session-state tracking** — store the slot-#1 client in `st.session_state["_last_primary_client"]` and demote the new pinned story on subsequent queries when it matched. This had no documented rationale beyond a one-line docstring ("avoiding last-used client for primary"). No ADR, no tests pinning the behavior, no design doc, no commit-message-level justification.

The cross-query mechanism evolved over January 2026 to add a 0.05 score-gap threshold (only demote when the alternative was within 0.05 of pinned), narrowing the firing condition but preserving the session-state dependency.

May 2026 investigation under MATTGPT-073 revealed the mechanism was producing order-dependent retrieval contamination in real production sessions:
- Production log analysis (Apr 13 to May 18, 2026; 82 queries; 24 inferred sessions): 85.4% of queries occur in multi-turn sessions where the mechanism could fire; 45% of consecutive query pairs were demotion-eligible.
- A reproducible case (May 18, 2026): user runs Q1 "What kind of leader is Matt?" then Q3 "How does Matt show up when things go wrong?" within the same session. `last_primary_client = Accenture` from Q1 triggered the line 1293 demotion on Q3's 0.001 score gap (Why Hire Matt at 0.350 vs. MattGPT Product Vision at 0.349), promoting MattGPT Product Vision to slot #1. Fresh-session Q3 produced a clean response; same-session Q3 produced MattGPT contamination. Saturday May 16's "Q3 regression" attributed to LLM stochasticity was actually this bug firing.
- A six-query production session captured April 13, 2026 showed a real user drilling into a single topic (resistance/transformation/scaling). The session-state mechanism would actively work against user intent in that pattern, "diversifying" their results away from the topic they were investigating.

**Decision:**
Remove the cross-query session-state mechanism from `diversify_results` entirely. Specifically:
- Delete the read of `st.session_state["_last_primary_client"]` and the demotion check (former lines 1276-1305).
- Delete the write of `st.session_state["_last_primary_client"]` (former line 1328).
- Preserve all within-query diversity logic (named-clients-first, per-client limits, result-size cap).

Within-query diversity remains the only client-diversity mechanism in the function. There is no cross-query state. The retrieval output for query N is deterministic with respect to query N alone (modulo Pinecone non-determinism and LLM stochasticity at temperature 0.4).

**Rationale:**
- **No documented justification for the mechanism.** No ADR, no tests, no design doc. The docstring intent ("avoiding last-used client for primary") was speculative — added alongside within-query diversity in the same commit without separate justification or an observed problem it was solving.
- **Empirical evidence the mechanism was harmful.** Real production user behavior (drilling into a topic) is exactly the pattern where session-state "diversification" works against user intent. The mechanism conflated "same story repeating across queries" (legitimate concern, not implemented) with "same client appearing across queries" (debatable, what was implemented).
- **Eval validation post-removal.** Two consecutive runs of the 61+ query eval suite: 69/70 (98.6%) and 70/70 (100%), versus the 96.8% baseline from ADR 018. The mechanism wasn't load-bearing for correctness; if anything, removal improved eval pass rate.
- **The "no compensation logic on top of Pinecone" principle from January 2026 cleanup applies.** Adding speculative compensation gates to the retrieval pipeline accumulates side effects. The within-query diversity is justified delivery competency (no single client should dominate one response); the cross-query state was a layered compensation without a documented use case.
- **Reversibility.** If a real cross-query use case surfaces, Option D (track story_id rather than client, narrowing the trigger to true same-story repetition) is a safer reintroduction than the original mechanism.

**Consequences:**
- The retrieval pipeline is now session-independent for `diversify_results`. Same query produces the same Pinecone+diversify output regardless of session history.
- Multi-turn user behavior (the common case per production logs) no longer triggers order-dependent contamination from this mechanism.
- LLM stochasticity at temperature 0.4 remains a separate source of variance; this ADR does not address it.
- Future Claude sessions investigating diversify behavior should not re-add cross-query session state without first documenting (a) the specific production case it's solving, (b) eval evidence the case isn't already handled, and (c) explicit owner sign-off. The pattern of speculative compensation layers accumulating in this function is documented across MATTGPT-021, MATTGPT-061, MATTGPT-073, MATTGPT-074 and should be resisted.

**Edge cases / what this ADR does NOT cover:**
- **Q2 polysemy** ("How does Matt handle resistance in large-scale transformations?"): Strangler Fig technical-refactoring story still wins Pinecone retrieval over Norfolk Southern organizational-resistance stories because the word "transformation" is polysemic. This is a Pinecone-layer semantic problem, addressed in MATTGPT-061 (bidirectional enrichment) and on the NEXT roadmap (hybrid keyword retrieval). Not in scope for this ADR.
- **Entity cluster promotion** (`backend_service.py:1617-1629`): a separate mechanism that auto-promotes broad entity queries to synthesis mode. Has its own design tension documented in MATTGPT-074. Not in scope for this ADR.
- **diversify_results unused parameters** (MATTGPT-021): `max_per_client` is accepted but not actually applied in the function body. Pre-existing bug, separate ticket.

**Methodological note:**
This ADR was written immediately on resolution per a discipline established May 18, 2026: record the empirical evidence base alongside the decision, not just the decision. The W_KW=0.0 archaeology pattern (digging through git for missing decision context that was never recorded) was repeating before this discipline was articulated. Future decisions on `backend_service.py` orchestration should follow this pattern: write the ADR at the same time as the code change, with the empirical evidence inline.

---

## ADR 020: Remove the classify_query_intent() LLM Intent Fallback

**Date:** 2026-01-30 (removed); 2026-10-05 (recorded)
**Status:** Accepted
**Related tickets:** None

**Context:**
`classify_query_intent()` in `ui/pages/ask_mattgpt/backend_service.py` was an LLM call (GPT-4o-mini, about $0.0001 per query) that classified query intent as a fallback alongside the embedding-based semantic router. It did not recognize project names such as TICARA, and the semantic router already produced every intent it returned.

**Decision:**
Delete `classify_query_intent()`. The semantic router (`services/semantic_router.py`) is the only intent classifier: synthesis, out_of_scope, and every other intent family come from embedding similarity alone.

**Rationale:**
- Redundant: every intent it produced, the semantic router already produced without an LLM call.
- Brittle: it misclassified queries that named projects the model had no context for.
- Cost: one LLM call per query for no quality gain.
- Alternative considered: keep it as a fallback only when the router's score is low. Rejected because the confidence gate on Pinecone scores already handles weak queries, and the fallback still had the project-name blind spot.

**Consequences:**
- Intent classification has no per-query LLM cost.
- `tests/eval_rag_quality.py` and `tests/debug_trace_query.py` still import `classify_query_intent` from `backend_service.py`; those import paths fail if reached.
- Reintroducing an LLM classifier needs a named query class the semantic router misroutes, with eval evidence.

---

## ADR 021: Remove the Entity Gate Query Rejection

**Date:** 2026-01-30 (removed); 2026-10-05 (recorded)
**Status:** Accepted
**Related tickets:** MATTGPT-141

**Context:**
The Entity Gate was a runtime rejection step in `rag_answer()`: when `detect_entity()` found no entity and the semantic router score was below `ENTITY_GATE_THRESHOLD`, the query was rejected before retrieval. It rejected valid queries such as TICARA questions, which name no Client, Employer, or Division. This is distinct from the live multi-field entity filter (the Pinecone `$or` across `ENTITY_SEARCH_FIELDS`), which narrows retrieval when an entity is detected and rejects nothing.

**Decision:**
Remove the Entity Gate rejection. Query rejection comes only from the Pinecone confidence gate (`CONFIDENCE_HIGH` and `CONFIDENCE_LOW` in `config/constants.py`, logged as `[QUERY_REJECTED] reason=low_pinecone`). The dead `ENTITY_GATE_THRESHOLD` constant was later deleted under MATTGPT-141.

**Rationale:**
- Failing to detect an entity is not evidence that a query is off-topic; many legitimate questions name no client.
- Alternative tried first: recalibrate the threshold. It was lowered from 0.50 to 0.30 on 2026-01-26 after legitimate queries scored 0.31 to 0.49. Rejected as the fix because the gate's premise, not its number, caused the false rejections.
- The confidence gate measures retrieval quality directly, which is what the Entity Gate approximated.

**Consequences:**
- One rejection path instead of two, and fewer thresholds to calibrate.
- Reintroducing entity-based rejection needs an off-topic query class the confidence gate passes, with eval evidence.

---

## ADR 022: Title Entities Use Soft Filtering, Not a Pinecone Hard Filter

**Date:** 2026-01-30 (removed); 2026-10-05 (recorded)
**Status:** Superseded by ADR 047
**Related tickets:** None

**Context:**
`detect_entity()` matches story titles as well as Client, Employer, and Division. A Title match used to add a Pinecone metadata filter on that title, so retrieval returned only the one matching story. Related Projects then showed 1 result instead of 7.

**Decision:**
Remove hard filtering for Title. `detect_entity()` still returns `("Title", value)`, but `rag_answer()` skips the Pinecone entity filter when `entity_field` is `"Title"`; semantic search ranks the named story first and related stories fill the remaining slots in the same call. Client, Employer, and Division matches still apply the hard filter.

**Rationale:**
- A title names one story, so a hard filter can only ever return one result.
- The title is in the embedding text, so semantic search already ranks the named story first without a filter.
- Alternative considered: drop Title from detection entirely. Rejected because detection still identifies the named story for the answer.

**Consequences:**
- Title queries return the named story plus related stories in one retrieval.
- Any new detected field that identifies a single story should follow the soft path.

---

## ADR 023: Remove the ENTITY_NORMALIZATION Alias Map and Fuzzy Matching

**Date:** 2026-01-26 (removed); 2026-10-05 (recorded)
**Status:** Superseded by ADR 047
**Related tickets:** None

**Context:**
`ENTITY_NORMALIZATION` was a hardcoded dict mapping query variants to canonical client names, backed by fuzzy-matching helpers (`_normalize_for_matching`, `_get_acronym`, and related functions). It drifted from the JSONL corpus as client names changed, and the fuzzy matching added complexity without reliable matches.

**Decision:**
Delete `ENTITY_NORMALIZATION` and the fuzzy-matching helpers. Query variants are handled by `ENTITY_ALIASES` in `config/constants.py`: a small exact-alias dict, matched on word boundaries and consulted first in `detect_entity()`, limited to acronyms and shortened forms visitors actually type that do not appear in canonical values (for example "cic", "jpmc", "amex", "jp morgan").

**Rationale:**
- A broad alias map duplicated corpus values and drifted from them.
- Fuzzy matching produced matches that could not be predicted or tested.
- At removal, testing showed semantic search returned JP Morgan Chase stories for "JPMC", "JPM", and "Chase" without the map. Acronyms that embeddings cannot resolve to a filter, starting with "CIC", were added back as narrow exact aliases.
- Alternative considered: keep the map and add a drift test. Rejected because a narrow exact-alias list is smaller to keep current than a broad map with a test.

**Consequences:**
- `ENTITY_ALIASES` is the one alias source; entries need a demonstrated query that detection misses without them.
- `ENTITY_ALIASES` is not `ENTITY_NORMALIZATION` reintroduced: no fuzzy matching, only exact aliases absent from canonical values.

---

## ADR 024: Remove Project and Place from Entity Detection

**Date:** 2026-01-26 (removed); 2026-10-05 (recorded)
**Status:** Superseded by ADR 047
**Related tickets:** None

**Context:**
`detect_entity()` checked Project and Place along with Client, Employer, and Division. Project has many generic values ("Innovation", "Methodology", "Personal Growth") that match ordinary query words: "scaled innovation beyond prototypes" matched Project="Innovation" and filtered synthesis to 1 story instead of 5 or 6.

**Decision:**
`ENTITY_DETECTION_FIELDS` is `["Client", "Employer", "Division"]`. Project and Place are not detected. They stay in `ENTITY_SEARCH_FIELDS`, so a detected entity still searches across them in the Pinecone `$or`.

**Rationale:**
- Generic field values turn common words into false entity filters.
- Semantic search handles Project and Place questions without a filter.
- Alternative kept for a narrower case: Division stays in detection, with `EXCLUDED_DIVISION_VALUES` excluding generic values, because "Cloud Innovation Center" queries need the filter.

**Consequences:**
- Detection is deliberately narrower than search; the comments on both constants in `config/constants.py` say not to align them.
- Adding a field to detection needs a check that its values are not common query words.

---

## ADR 025: Delete scripts/test_pinecone_direct.py

**Date:** 2026-01-29 (removed); 2026-10-05 (recorded)
**Status:** Accepted
**Related tickets:** None

**Context:**
`scripts/test_pinecone_direct.py` was a standalone script that queried Pinecone directly. It defined its own `CONFIDENCE_HIGH` and `CONFIDENCE_LOW` instead of importing them, so its thresholds could disagree with the pipeline's after `config/constants.py` became the single source of truth.

**Decision:**
Delete the script. Threshold-dependent checks import from `config/constants.py`.

**Rationale:**
- A second copy of calibrated thresholds diverges silently.
- Alternative considered: update the script to import the shared constants. Not recorded as tried; the eval suite and probe scripts cover direct retrieval checks.

**Consequences:**
- Calibrated thresholds have one definition.

---

## ADR 026: CONFIDENCE_LOW Is 0.20

**Date:** 2026-01-19 (raised); 2026-10-05 (recorded)
**Status:** Superseded by ADR 033
**Related tickets:** MATTGPT-029, MATTGPT-024

**Context:**
ADR 018 records `CONFIDENCE_LOW = 0.15`. The live value is 0.20. It was raised in `services/rag_service.py` on 2026-01-19 with the comment "Raised from 0.15 to filter phantom similarity noise (e.g., "peanut butter")", and moved to `config/constants.py` on 2026-01-29 with the comment "Raised from 0.15 to filter phantom similarity noise". ADR 018 was written in May 2026 and recorded the value from before the raise.

**Decision:**
- `CONFIDENCE_HIGH = 0.25`: top similarity at or above 0.25 means "found X stories", no warning.
- `CONFIDENCE_LOW = 0.20`: top similarity at or above 0.20 and below 0.25 shows the "relevance may be low" warning.
- Below 0.20: `confidence="none"`, logged as `[QUERY_REJECTED] reason=low_pinecone`.

Both constants live in `config/constants.py`. This supersedes ADR 018. Its calibration method, edge cases, and consequences carry forward with the soft band at 0.20 to 0.25.

**Rationale:**
- Off-topic queries such as "peanut butter" produced phantom similarity scores in the old 0.15 to 0.20 range and got answers with a warning. Raising the floor to 0.20 rejects them.
- Alternatives considered: not recorded. The commit that made the change does not mention it; the code comment is the only record.

**Consequences:**
- The soft band is 0.05 wide.
- `PINECONE_MIN_SIM = 0.15` is a separate constant, the Pinecone retrieval floor, and is unchanged by this decision.
- Threshold changes still require measurement against the eval suite, as ADR 018 states.

---

## ADR 027: Doc Writes Are Separated From Code Work by Session Role

**Date:** 2026-10-05
**Status:** Accepted
**Related tickets:** None

**Context:**
Code sessions and docs passes share one working tree and one staging area. `ARCHITECTURE.md`, `docs/ADR.md`, `BACKLOG.md`, and `CHANGELOG.md` are owned by the Architecture Sync and Backlog Maintenance passes, and that ownership was enforced only by instruction.

**Decision:**
The repo-rules check in `.githooks/pre-commit` enforces ownership at commit time for commits made in a Claude Code session (`CLAUDECODE` set):
- `MATTGPT_DOCS_SESSION=arch` (launched by `scripts/arch-sync-session.sh`) may commit only `ARCHITECTURE.md` and `docs/ADR.md`.
- `MATTGPT_DOCS_SESSION=backlog` (launched by `scripts/backlog-session.sh`) may commit only `BACKLOG.md` and `CHANGELOG.md`.
- A session with no value is a dev session and may commit none of the four.
- Any other value is refused as an unknown role.

Commits from a terminal outside Claude Code are not checked. The first version of the check (same day) had a single docs role, `MATTGPT_DOCS_SESSION=1` from `scripts/docs-session.sh`, allowed all four files; it was split into the arch and backlog roles, and the value 1 is no longer accepted.

**Rationale:**
- Each docs pass writes only its own two files, so a commit from the wrong session is a mistake the hook can catch mechanically.
- The hook sees the temporary index for `commit -a` and pathspec commits, so it catches doc files staged by another session.
- Alternative kept alongside: instruction only (Document Ownership in CLAUDE.md). It stays, but it had no mechanical check.
- Alternative rejected: three enforcement layers (a file-tool PreToolUse hook, a Bash allow list, and a commit-time check). Over-built; command-string parsing produced false positives.
- Alternative rejected: a settings file with deny rules, loaded with `--settings`. Deny takes precedence over allow, so "allow four files, deny the rest" can't be expressed.
- Alternative rejected: a separate git worktree for docs. It needs its own branch and a merge every cycle.
- Alternative rejected: keep the passes in Cowork, fed by a git digest file or an automatically pushed sync branch. Local Cowork tasks end on 2026-10-06, and an automatic push bypasses the push gate and runs the pre-push test suite on every commit.
- Alternative replaced: one docs role for all four files (the first version, same day). Split into arch and backlog roles so each pass can commit only its own two files.

**Consequences:**
- A docs pass must be launched through its script; the Architecture Sync and Backlog Maintenance skills check the role before starting.
- Matt's own terminal commits bypass the check by design.

---

## ADR 028: Remove the CLAUDE.md Line Budget

**Date:** 2026-10-04
**Status:** Accepted
**Related tickets:** None

**Context:**
The repo-rules pre-commit check counted `CLAUDE.md` lines on every commit and failed above 268.

**Decision:**
Remove the line budget from `.githooks/pre-commit`; the hook's name in `.pre-commit-config.yaml` drops "CLAUDE.md budget". `CLAUDE.md` stays small by holding current rules only, with history in `docs/ADR.md` or `CHANGELOG.md`. The em dash and hashed-class checks are unchanged. `ARCHITECTURE.md` size is reported, not enforced, by the `mattgpt-docs-check` skill.

**Rationale:**
- A line count limits length, not content; the content rule (current rules only) addresses what makes the file grow.
- Alternative rejected: keep the 268-line check. It limits length, not content.
- Alternative rejected: a hook blocking dates and ticket IDs in current-state files. The report-only `mattgpt-docs-check` skill reports them instead, along with `ARCHITECTURE.md` size.

**Consequences:**
- No mechanical limit on `CLAUDE.md` length; the docs check reports history markers in it.

---

## ADR 029: The Roadmap Lives in BACKLOG.md

**Date:** 2026-10-04
**Status:** Accepted
**Related tickets:** None

**Context:**
ADR 006 chose Markdown files over Jira and named two files, `Backlog.md` and `Roadmap.md`, in `/docs`. `docs/Roadmap.md` was a 77-line phase roadmap committed once on 2025-09-12 and never updated. The backlog is `BACKLOG.md` at the repo root, and its Value Prioritized Roadmap section replaced the separate roadmap.

**Decision:**
Delete `docs/Roadmap.md`. `BACKLOG.md` at the repo root holds the backlog, and its Value Prioritized Roadmap section is the single roadmap. The choice of Markdown over Jira from ADR 006 stands. This supersedes ADR 006.

**Rationale:**
- Two roadmaps drift; the separate file had not been updated since it was committed.
- Alternatives considered: not recorded in the commit.

**Consequences:**
- Roadmap changes go through the Backlog Maintenance pass with the rest of `BACKLOG.md`.
- ADR 003 still names `Roadmap.md` in its context text; that reference is historical.

---

## ADR 030: Rule 0a's Direct No Is Scoped to Certifications

**Date:** 2026-10-04
**Status:** Accepted
**Related tickets:** MATTGPT-268, MATTGPT-250, MATTGPT-252, MATTGPT-273

**Context:**
Citation rule 0a (`_CITATION_RULE_0A` in `ui/pages/ask_mattgpt/prompts.py`) told the LLM that for any category the profile holds, an item not in the list gets a direct no, followed by what the list does contain. `_PROFILE_CATEGORY_LIST` existed only to fill that sentence's category list. Asked whether Matt has a Computer Science degree, Ask Agy led with a no in 9 of 10 runs; with the category-wide sentence removed, 0 of 10.

**Decision:**
The sentence becomes "For certifications, an item not in the list gets a direct no, followed by what the list does contain." `_PROFILE_CATEGORY_LIST` is removed. `matt_profile.json` is unchanged.

**Rationale:**
- The category-wide clause made education answers lead with a no that Role Match does not give.
- Alternative tried: delete the sentence outright. CS answers then led with a no in 0 of 40 runs, but PMP failed 10 of 20 direct phrasings: it answered "no" and narrated program-management stories with no certifications and no fact card.
- Alternative tried: label the certifications line "(complete list)" in `load_matt_profile()`. PMP still failed 10 of 20.
- Alternative tried: reword the AIU education note. The current wording gave 0 of 20 leading no; the April "satisfies requirements" wording gave 3 of 20 and broke PMP; a positive rewrite gave 3 of 20.
- With the scoped sentence, CS led with a no in 8 of 50 runs, and PMP direct phrasings passed 20 of 20.

**Consequences:**
- Any direct-no wording in rule 0a leaks into education answers: in one batch, the scoped sentence gave 4 of 20 CS leading no, and 0 of 20 with it removed in memory. The CS leading no is reduced, not eliminated.
- A follow-up such as "What about PMP" still pivots to stories, because `rag_answer()` takes no conversation history and profile-fact answers carry retrieved stories. That is MATTGPT-273.
- The MATTGPT-268 Green commit names the probe output directories behind these counts. If MATTGPT-252 changes `generate_dynamic_dna()`, rerun this acceptance.

---

## ADR 031: Query Analytics Use a Google Sheets Logger, Not streamlit-analytics2

**Date:** 2026-01-12 (streamlit-analytics2 removed); 2026-03-09 (Sheets logger enabled); 2026-10-05 (recorded)
**Status:** Accepted
**Related tickets:** None

**Context:**
`streamlit-analytics2` was added on 2026-01-10 and logged pageviews. On 2026-01-12 production failed with `AttributeError: st.session_state has no attribute "session_data"`, and the package and its dependencies were removed to restore stability.

**Decision:**
Query and page-load analytics go to Google Sheets through `services/query_logger.py`, using `gspread` and a service account, written on a fire-and-forget daemon thread. Enabled 2026-03-09 with an enriched schema.

**Rationale:**
- The third-party package broke production through its use of session state.
- A logger owned by the repo controls its schema and failure behavior: `_append_row` never raises.
- Alternatives considered: not recorded.

**Consequences:**
- The query logger is the only write path in the app.
- Schema changes are append-only, enforced by the HEADERS invariants in `tests/unit/test_query_logger.py`.

---

## ADR 032: My Work Table Uses st.dataframe, Not AgGrid

**Date:** 2026-06 (migrated); 2026-10-05 (recorded)
**Status:** Accepted
**Related tickets:** MATTGPT-144, MATTGPT-064

**Context:**
The My Work Table view rendered with AgGrid, which runs inside a separate iframe document. CSS injected into the parent page's `<head>` (everything in `global_styles.py`) stopped at the iframe boundary, so styling needed Python-side `rowStyle`, JS injection, and an `.ag-root-wrapper` guard (MATTGPT-064). The iframe intermittently failed to paint rows, leaving a blank grid. The AgGrid BDD suite stayed green while the grid was broken: its assertions were `pass` no-ops, and the one real assertion targeted `.ag-row` inside the iframe.

**Decision:**
Replace AgGrid with `st.dataframe` in the Table render path. AgGrid is not used by any live component. The ARCHITECTURE.md CSS pattern for AgGrid iframe styling is removed; its implementation is in git history if AgGrid is ever reintroduced.

**Rationale:**
- `st.dataframe` renders to a canvas in the main document, with no iframe, which removes the blank-grid failure mode and the iframe styling workarounds.
- Alternatives considered: not recorded.

**Consequences:**
- Rows, cells, and selection controls are painted to a canvas, so BDD cannot assert row content, row rendering, or canvas-driven selection. Row rendering is covered by a manual visual check (a 20-click filter test). See st.dataframe Canvas Constraint in ARCHITECTURE.md.
- `wait_for_load_state("networkidle")` never settles on a page with the grid; table steps use `wait_for_streamlit_rerun()`.
- Whole-row click or keyboard row selection requires self-rendered HTML rows (the Cards pattern).

---

## ADR 033: Ask Agy Refuses Below CONFIDENCE_HIGH; the Warning Tier Is My Work Only

**Date:** 2026-10-06 (recorded; the Ask Agy refusal of low confidence dates to 2025-12-05)
**Status:** Superseded by ADR 047
**Related tickets:** MATTGPT-273, MATTGPT-253

**Context:**
ADR 026, like ADR 018 before it, says a top similarity from 0.20 to 0.25 is answered with a "relevance may be low" warning. That is not what Ask Agy does. `semantic_search()` in `services/rag_service.py` buckets the top score as high (at or above `CONFIDENCE_HIGH = 0.25`), low (at or above `CONFIDENCE_LOW = 0.20`), or none, but `rag_answer()` in `backend_service.py` refuses both `low` and `none`. The evaluator probe for MATTGPT-273 (`docs/evidence/MATTGPT-273/tool_vs_pipeline_20261006_140406/`) found the pipeline refusing 25 turns at this gate. The MATTGPT-253 probe (`docs/evidence/MATTGPT-253/current_certs_20261006_163102/`) showed "Are any of those current" refused 3 of 3 at a top score of 0.221 and answered 3 of 3 at 0.252 with a trailing question mark.

**Decision:**
This records current behavior; no threshold changes.
- `semantic_search()`: high at or above 0.25; low at or above 0.20; none below 0.20, with empty results. Hits below 0.20 are dropped from low and high results.
- Ask Agy (`rag_answer()`): refuses `low` and `none`, logged as `[QUERY_REJECTED] reason=low_pinecone`, so any top score below 0.25 is refused. It has no warning tier. Two exceptions pass the gate: suggestion and context-locked queries (`from_suggestion`), and trusted behavioral queries (semantic router score at or above 0.80 with family `behavioral`).
- My Work (`_render_confidence_banner()` in `ui/pages/explore_stories.py`): `low` shows "Showing closest matches ... Relevance may be low."; `none` shows "No strong matches".

This supersedes ADR 026. The 0.20 value of `CONFIDENCE_LOW` and its reason (filtering phantom similarity noise) carry forward: it sets the none bucket for both surfaces and My Work's warning floor.

**Rationale:**
- ADRs 018 and 026 described one gate for both surfaces. The surfaces behave differently, and the evaluator scores and the punctuation result depend on Ask Agy's actual 0.25 floor.
- Alternative considered: correct ADR 026 in place. Not permitted; ADR.md is append-only.

**Consequences:**
- For Ask Agy, `CONFIDENCE_HIGH` is the refusal threshold, and small wording changes near 0.25 decide whether a question is answered.
- Any change to Ask Agy's gate is measured against the evaluator conversations in `tests/fixtures/evaluator_conversations.md` as well as the golden eval.

---

## ADR 034: Ask Agy Follow-Ups Carry the Last Two Exchanges

**Date:** 2026-10-06
**Status:** Accepted; its line that retrieval sees only the current question is superseded by ADR 061 (row 9)
**Related tickets:** MATTGPT-273, MATTGPT-275

**Context:**
`rag_answer()` took only the current question, so a follow-up such as "What about PMP" or "how big was the team" reached the response LLM with no prior turn.

**Decision:**
`send_to_backend()` reads `st.session_state["ask_transcript"]`; `_build_history_messages()` keeps the last `ASK_HISTORY_MAX_MESSAGES = 4` messages (two exchanges), reading both `role` and `Role` keys, skipping banners, and dropping the current question. `rag_answer(history=...)` passes them to `_generate_agy_response()`, which sends them between the system and user messages. Retrieval, the gates, and the semantic router still see only the current question.

**Rationale:**
- Acceptance (`docs/evidence/MATTGPT-273/acceptance_20261006_131919/`, 3 runs each): team size 3/3 with the JP Morgan referent, PMP 3/3 with no story pivot, AWS 3/3 leading with the two certifications, "what changed" 3/3 with the right referent, topic switch 3/3 with no drag.
- Rejected: prepending the previous question to the retrieval query. Topic drag in 3 of 3 switches (`docs/evidence/MATTGPT-273/history_20261006_125833/`).
- Rejected: putting the full corpus in context. About 8x the cost per query, and more narration on fact answers (`docs/evidence/MATTGPT-273/long_context_20261006_124253/`).
- Rejected: an answer-from-the-conversation prompt instruction. 0 of 3 on the browser pair, and the PMP pivot rose to 2 of 3 (local probe output only).
- Measured, not adopted: carrying the previous answer's top stories into the context fixed the browser pair 3/3, but as a rule layered over single-shot retrieval.

**Consequences:**
- Retrieval on a weak follow-up still runs on the bare question and can retrieve unrelated stories, which the model then narrates. Follow-up retrieval is MATTGPT-275 (tool-calling retrieval).

---

## ADR 035: Agy's Closing Offers Are Removed Until Follow-Ups Can Be Honored

**Date:** 2026-10-06
**Status:** Accepted; its opener line is reconciled in ADR 061 (row 29)
**Related tickets:** MATTGPT-276, MATTGPT-275

**Context:**
`_generate_agy_response()` ended every answer with a closer picked by `random.choice` from 8 standard or 4 synthesis offers ("Want me to dig deeper?"), and `build_user_message()` instructed the model to end with that exact text. The closers are a deliberate call to action, but an accepted offer is a follow-up, and retrieval runs on the bare follow-up.

**Decision:**
Remove the closers. `build_user_message()` takes no closing argument; the system prompts drop "End with the closing provided"; rule 0a places profile markers on their own line at the end of the response. The random opener and focus angle stay. The removal is temporary: restoring the closers is part of MATTGPT-275's acceptance.

**Rationale:**
- Rejected: keeping the closers while retrieval runs on the bare follow-up. Accepted offers retrieved unrelated stories in 3 of 3 browser follow-ups.
- Acceptance (`docs/evidence/MATTGPT-276/closers_20261006_152350/`): the final paragraph was an offer in 105 of 105 answers before and 0 of 106 after.

**Consequences:**
- Answers end on content, with no invitation to continue.
- When MATTGPT-275 lands, a new ADR restores the closers and supersedes this one.

---

## ADR 036: MATT_DNA States Only Facts a Story or the Profile Backs

**Date:** 2026-10-06
**Status:** Accepted
**Related tickets:** MATTGPT-269, MATTGPT-273, MATTGPT-275

**Context:**
`generate_dynamic_dna()` builds the MATT_DNA grounding prompt from the corpus plus curated text. The curated text carried figures and claims no story or profile entry backs, and restated story facts through derived placeholders. The MATTGPT-273 tool-calling probe (`docs/evidence/MATTGPT-273/tool_vs_pipeline_20261006_140406/`) flagged MATT_DNA figures in 6 answers: $300M+ (5), 30-60% (4), $189M (3), teams of 10 delivering like 20 (2). An audit by substance found the last backed by the Building Cloud Innovation Centers story; the other three, plus "MVP in 3 weeks", had no backing.

**Decision:**
MATT_DNA states only facts backed by a story or `data/matt_profile.json`, and does not restate story facts; the story is the source. Applied in MATTGPT-269:
- Removed four unbacked figures: $300M+ annual sales by FY23, the $189M cloud modernization win, 30-60% cycle time reduction, and MVP in 3 weeks vs months. The backed claims on the same lines stay (CIC 0 to 150+, 4X faster velocity, zero defects, $100M+ repeat business, teams of 10 delivering the output of 20, from the Building Cloud Innovation Centers story).
- Removed the "payments platform across 12 countries" line and the `major_banking_client` derivation that existed only for it; the fact stays in its story.
- Removed the eight-line "Career Eras (for timeline context)" block. The Timeline reads each story's Era field and is unaffected.
- Theme Strengths are tiered by story count: Execution & Delivery primary (59 stories), Org Transformation a strong secondary theme (19), Strategic Advisory, Talent & Enablement, Emerging Tech, and Risk narrower. "Matt builds people, not just systems" and "Regulatory (one engagement)" are removed.
- "Early-stage startups" is removed from the industries that are not Matt's; the Sparkfly story contradicts it.

**Rationale:**
- The model treats MATT_DNA as ground truth and cites it. In a design where the model answers directly from its context, every MATT_DNA line is authoritative.
- Rejected: keeping figures as unsourced persona context, because the model cites them.
- Rejected: deriving the 12-countries client from the story, because it keeps a duplicate of a fact the story already holds.

**Consequences:**
- A new MATT_DNA line needs a backing story or profile entry; `tests/unit/test_matt_dna_grounding.py` and the `matt_dna_grounding_drift` BDD feature pin the removed content.
- MATT_DNA items that remain hardcoded, including the How Matt Wins Business heading, carry into MATTGPT-275.

---

## ADR 037: Remove the NOT-Clients List From MATT_DNA

**Date:** 2026-10-06 (removed); the list was added 2026-01-19
**Status:** Accepted
**Related tickets:** MATTGPT-269, MATTGPT-207

**Context:**
`generate_dynamic_dna()` emitted "NOT Matt's Clients (NEVER mention): Kaiser, Google, Amazon, Microsoft, Meta, MetLife, Citizens Bank", added on 2026-01-19 to suppress a confabulated Kaiser engagement and pinned by a MATTGPT-207 scenario. This is distinct from the "NOT Matt's industries" line, which stays.

**Decision:**
Remove the list. Clients by Employer ("ONLY cite these") and grounding rules 1 and 3 cover companies that appear in no story.

**Rationale:**
- Rejected: keeping the list. Asked "Which clients can't you mention?", Ask Agy recited it in 5 of 5 runs, naming as confidential clients the companies it was meant to suppress.
- After removal (`docs/evidence/MATTGPT-269/not_clients_20261006_164532/`, 5 runs per question): no recital (0/5); Kaiser denied 10/10, as before, with healthcare described as "a Major U.S. Health System"; MetLife denied 5/5; no client claim for Google or Microsoft; controls and synthesis named no listed company (0/40 in both arms).

**Consequences:**
- Suppression of a company in no story rests on the positive client list and the grounding rules, not on a negative list.
- Observed in both arms and not addressed: answers sometimes call Accenture, Matt's employer, a client.

---

## ADR 038: Matt's Self-Description Lives in the Profile, Labeled, for Ask Agy Only

**Date:** 2026-10-06
**Status:** Accepted
**Related tickets:** MATTGPT-269

**Context:**
MATT_DNA carried Matt's self-description inline as fact: an Identity heading and line, a Core Values block, and lines such as "Builder's mindset, coach's heart" and "Teaches teams to fish".

**Decision:**
`data/matt_profile.json` holds `self_description`: a label and four statements. `generate_dynamic_dna()` reads it through `services.matt_profile.load_profile_dict()` and renders the statements under the label, which marks them as Matt's own words, not independently verified. If the profile can't be read, the block is omitted and the failure is logged with `logger.exception`. `jd_assessor.load_matt_profile()` renders only named keys, so Role Match does not see it. "Leads with empathy, clarity, and purpose" stays in Leadership Philosophy, backed by the Leadership Philosophy and Career Intent stories.

**Rationale:**
- Rejected: rendering it in `load_matt_profile()`. The assessor would read "coach's heart" as evidence and inflate leadership verdicts.
- The label lets Ask Agy quote the statements as self-description without presenting them as facts.

**Consequences:**
- Self-description edits are data edits in `matt_profile.json`, not code edits.
- Role Match grounding stays limited to backed facts.

---

## ADR 039: Probes Stay Untracked in probes/; Cited Output Is Frozen in docs/evidence/

**Date:** 2026-10-05
**Status:** Accepted
**Related tickets:** MATTGPT-265

**Context:**
Probe scripts and their output accumulated at the repo root, some tracked and some not, and tickets cited probe output by local path. Probes are exploratory instruments and stay untracked, so citations to their output broke when the files moved.

**Decision:**
- `/probes/` is gitignored, anchored to the root. Probe scripts live there, with output under `probes/output/<ticket>/<timestamp>/`. Fourteen previously tracked root probes were untracked and moved there; each stays in git history.
- Output that a ticket, commit, or ADR cites is copied byte-identical into `docs/evidence/MATTGPT-<n>/` and tracked. Probe scripts are not copied. The pre-commit em-dash check skips `docs/evidence/`.
- Tracked at the root: `probe_assessor.py` with its `probe_extraction_*.json` caches (the documented probe harness), the corpus pipeline's `generate_*.py` tools, and `generate_208_fixtures.py` (named as provenance by test fixtures). `probe_assessor.py` writes its results under `probes/output/`.

**Rationale:**
- Probes stay untracked, and frozen copies keep cited evidence available on a fresh clone.
- Alternatives considered: not recorded in the commits.

**Consequences:**
- A citation points at `docs/evidence/`, never at `probes/`, which a fresh clone does not have.
- Current-state docs describe a measurement by what it does, not by a probe script's path.

---

## ADR 040: Ask Agy Is a Conversational System; Retrieval Is Its Evidence Step

**Date:** 2026-10-08
**Status:** Superseded by ADR 047
**Related tickets:** MATTGPT-275, MATTGPT-273, MATTGPT-253, MATTGPT-276

**Context:**
Ask Agy was designed as a conversational guide to Matt's work: a visitor asks, Agy answers from Matt's stories in its own voice, offers to go deeper, and the next question builds on the last. The closers were its call to action. As built, each turn is single-shot search: a gate and a router on the visitor's literal words, a Pinecone search on those same words, a diversification reshuffle, and a prompt to narrate what came back. Each step assumes the question stands alone, and the step that makes conversation work, rewriting a follow-up into a standalone query, was never built. When visitors behaved conversationally, failures were fixed one at a time with prompt clauses, post-processing, and gates. Probes from Oct 6 to 8 found:
- Literal queries miss follow-ups and topic questions; a short resolved query retrieved more on-topic stories than the visitor's literal words (local probe output, `probes/output/275/no_client_20261008_113819/`, to be frozen into `docs/evidence/MATTGPT-275/`).
- The confidence gate refuses evaluator questions: 25 refused turns in the evaluator run (`docs/evidence/MATTGPT-273/tool_vs_pipeline_20261006_140406/`).
- A model left to decide whether to search skips the search on follow-ups (local probe output, `probes/output/275/simplest_20261007_123042/` and `search_sentence_20261007_143054/`, to be frozen).
- The reshuffle discards on-topic stories (local probe output, `probes/output/275/arm_a_20261008_145724/`, to be frozen).

**Decision:**
Ask Agy is a conversational system, and retrieval is an evidence step inside it, not the system. Each turn:
1. Understand the turn: rewrite the latest question into a standalone query using the conversation.
2. Retrieve deterministically: always search on that query, and pass the raw top results with no reshuffle.
3. Answer from evidence: the profile, the conversation history (ADR 034), and the retrieved stories, in Agy's voice under the honesty rules, saying plainly when something isn't recorded.
4. Offer to continue only when the next step can be delivered; that is when the closers return (ADR 035).

Role Match remains a separate, retrieval-heavy workflow.

**Rationale:**
- The failures share one cause: a single-shot search pipeline asked to hold a conversation. The gate, the reliance on the router, the reshuffle, and query substitution exist to compensate for literal single-shot search.
- Arm A (remove the reshuffle; the gate stays) tests step 2. Arm C (rewrite the question into a standalone query) tests step 1. If they recover the conversational behavior, this design is simpler than today's pipeline and than a tool-calling loop.
- Alternative measured: let the model decide whether to search (the tool-calling design first scoped in MATTGPT-275). It skips the search on follow-ups.
- Alternative: keep patching the pipeline per failure. Rejected; that is the remediation history this design ends.

**Consequences:**
- Accepted once the Arm A and Arm C evaluator scores support it, read against this design. It will then supersede the parts of ADRs 033 and 035 it replaces, and the gate, router dependence, reshuffle, and substitution become candidates for removal, each with its own removal ADR.
- Follow-ups such as "What went wrong?" depend on step 1; Arm A alone cannot fix them.
- MATTGPT-275's scope (tool-calling retrieval) needs reconciling with this ADR in the backlog pass.

---

## ADR 041: Pinecone Queries Return Ids and Scores Only

**Date:** 2026-10-10
**Status:** Accepted
**Related tickets:** MATTGPT-275

**Context:**
Every story is uploaded to Pinecone with its full text as metadata, about 8 KB a match. One `top_k=25` query returned 205,342 bytes. The app reads only the match id, because stories are looked up in the local corpus, and the hit snippet, which is the story's own `5PSummary`. On 2026-10-10, probe traffic at that size reached the Starter plan's 1 GB monthly egress cap, and capped queries fell back silently to local results (MATTGPT-275 run `poc_clean_20261010_093712`, labelled invalid).

**Decision:**
`pinecone_semantic_search()` in `services/pinecone_service.py` and both query branches of `get_synthesis_stories()` in `backend_service.py` pass `include_metadata=False`. The hit snippet comes from the local story's `5PSummary`, and the DEBUG preview reads title and client from the local story. Metadata is still stored at ingestion and still used for Pinecone-side filters.

**Rationale:**
- Measured with the query "Fiserv white-label card portal", same client and script: 205,342 bytes before, 3,127 after; the same 25 story ids in the same order, scores within 0.001.
- Rejected: lowering `top_k`, because it changes ranking.
- Rejected: trimming the uploaded metadata, because it changes ingestion. Ids-only changes neither.

**Consequences:**
- `tests/unit/test_pinecone_egress.py` pins `include_metadata=False` on all three query sites and the local snippet source.
- When Pinecone returns no hits, `semantic_search()` falls back silently to the corpus in file order; that is MATTGPT-292.

---

## ADR 042: MATT_DNA's Industry Experience Is Derived From the Corpus

**Date:** 2026-10-07
**Status:** Accepted
**Related tickets:** MATTGPT-279, MATTGPT-269, MATTGPT-275

**Context:**
MATT_DNA's Industry Experience block in `generate_dynamic_dna()` was hand-typed: Primary / Secondary / Limited tier labels, "Limited: Healthcare (one engagement)", "NOT Matt's industries: Consumer products, retail", and fallback client names ("AT&T", "Norfolk Southern", "Various financial services clients"). Signature Achievements carried a derived line, "{transport clients} legacy-to-cloud transformation", which read "Cendian Chemical Logistics, Norfolk Southern legacy-to-cloud transformation" once the corpus unified the transportation label in 3c4b068; that is false for Cendian. ADR 037 recorded that the "NOT Matt's industries" line stays; this decision removes it.

**Decision:**
The block lists every Industry value except "Cross Industry" as "- {Industry}: {n} stories ({clients})", most stories first, with the non-generic clients of that industry's stories. Removed: the tier labels, the Limited line, the NOT-industries line, the fallback client names, and the derived-client achievements line. A new story's industry reaches the model without a code change.

**Rationale:**
- Acceptance (`docs/evidence/MATTGPT-279/industry_20261007_121045/`, 3 runs per question, before / after): "Which industries has Matt worked in?" named Aerospace & Defense 0/3 / 3/3, Education 0/3 / 3/3, Healthcare 2/3 / 3/3, Telecom 2/3 / 3/3. Cendian appeared only as logistics integration, never as legacy-to-cloud, in either arm. No figure outside a story or the profile in either arm.
- Rejected: keeping the achievements line with Norfolk Southern named, because it is a hardcoded client and the Norfolk Southern stories carry the work.

**Consequences:**
- Consumer goods stays out because TICARA's Industry is Cross Industry; whether an industry appears depends on the corpus Industry field alone.
- "Has Matt worked in retail?" is answered from the absence of a retail industry, not from a negative list.
- `tests/unit/test_matt_dna_industry.py` pins the derived block.

---

## ADR 043: Questions Naming Matt Pass Five Nonsense Rules; Roleplay Impersonation Gets Its Own Rule

**Date:** 2026-10-10
**Status:** Accepted
**Related tickets:** MATTGPT-285, MATTGPT-251, MATTGPT-290, MATTGPT-291

**Context:**
Five rules in `nonsense_filters.jsonl` (`creative_writing` twice, `general_knowledge` twice, `gaming`) matched words that also appear in legitimate questions about Matt, so questions such as "When was he at JP Morgan?" were refused before retrieval. No commit, ADR or test recorded the rules' original targets.

**Decision:**
- The five rules gain a lookahead in front of their unchanged pattern, `^(?!.*\b(matt|matt's|pugmire|he|his|him)\b)`, so a question that names Matt or uses he, his or him passes them.
- A new `roleplay_impersonation` rule rejects requests to roleplay, pretend or act as a person named by a pronoun or by "my" plus a family word. Role phrasings ("a hiring manager", "my interviewer") pass.
- `stocks_crypto` and `homework` are unchanged.

**Rationale:**
- Sweep of 850 distinct queries, before and after: 5 changed, three of them intended passes. The grandmother attempt moved from `creative_writing` to `roleplay_impersonation`; "Tell me about Matt's gaming experience" now reaches the router, which rejects it as out of scope.
- Live acceptance (`docs/evidence/MATTGPT-285/acceptance_narrowed_20261010_161142/`, 91e825a, 2 runs): 11 / 11 must-answer questions answered; every claim in the 22 newly unblocked answers on record in the corpus or profile.
- Rejected: unblocking `stocks_crypto` and `homework` now. Unblocked, "Has Matt worked on trading platforms?" and "How did Matt calculate ROI?" misattributed in 2 of 2 runs each. Their tests are `xfail(strict=True)` until MATTGPT-251 lands.
- Rejected: a fixed roleplay word list, because "act as" and "pretend to be" also start legitimate interview-practice requests.

**Consequences:**
- Both changes key on wording, not intent. Pronoun questions about other people ("When did Elvis release his first album?") now pass this layer, and the roleplay rule misses phrasings such as "my friend Sarah" or "my mentor".
- Questions with no name or pronoun ("When did the CIC launch?") are still refused by these rules.
- The data-extraction request stays rejected only by an incidental match in the second `creative_writing` rule (MATTGPT-290).
- "Act as a hiring manager" answers describe Matt rather than ask questions (MATTGPT-291).

---

## ADR 044: My Profile Type Scale Follows Home's Rendered Scale

**Date:** 2026-10-09
**Status:** Accepted
**Related tickets:** None

**Context:**
My Profile's body and card text used wireframe v4 sizes (body 13px, secondary 11-12px, item titles 12-13px, labels 10-11px). Home's category cards were also specified at 12/11px, but their single-class rules lost to Streamlit's markdown `p { font-size: inherit }`, so Home rendered at 16px. The Profile mobile block was never applied: a comment above its `@media (max-width: 768px)` closed early, and the browser dropped the block.

**Decision:**
My Profile follows Home's rendered scale: body 15px, secondary body 14px / 1.55, item titles 16px, labels 12-13px; h1, status badge and section eyebrows unchanged. Home's card title and meta are set at 16px with two-class selectors, so the size no longer depends on inheritance. The Profile mobile block applies, with sizes matching desktop. Wireframe v4's Profile sizes are superseded.

**Rationale:**
- Rejected: shrinking Home's cards to the wireframe's 12/11px. 16px is what users see on Home, and an 11px body is below readable size.

**Consequences:**
- `.prof-timeline-period` stays 12px on mobile (13px desktop), because a later `.timeline-year` mobile rule wins.
- Gates: computed styles before and after at 375, 767 and 1280px; BDD 24 / 24 (About, Home category cards); browser check at 375/440, 767 and 1024+.

---

## ADR 045: Router Rejection of Off-Topic Questions About Other People

**Date:** 2026-10-06
**Status:** Rejected
**Ticket:** MATTGPT-188
**Related tickets:** MATTGPT-063, MATTGPT-174, MATTGPT-016

**Context:**
Three router test cases failed: "Tell me a joke" (0.429, behavioral), "Tell me about Elon Musk" (0.401, technical) and "What's Jeff Bezos's leadership style?" (0.664, leadership) all cleared `SOFT_ACCEPT = 0.40`. The router matches on question shape, not subject, and logged production behavioral queries score 0.499 to 0.605, so no threshold separates them.

**Decision:**
Do not change the semantic router to reject off-topic questions about other people.

**Rationale:**
- The router is the wrong layer. e307d6d removed the three router test cases. The joke, Musk and Bezos queries are caught earlier in `rag_answer()` by `nonsense_filters.jsonl` (`jokes_riddles`, `celebrity`).
- Raising the threshold above 0.664 would reject legitimate traffic.

**Consequences:**
- Names outside the nonsense regex are the residual, tracked as MATTGPT-063.

---

## ADR 046: Stabilize the test_error_state_extraction_failure Marathon Flake

**Date:** 2026-10-06
**Status:** Rejected
**Ticket:** MATTGPT-205
**Related tickets:** MATTGPT-240, MATTGPT-197, MATTGPT-198, MATTGPT-203

**Context:**
`test_error_state_extraction_failure` in `tests/bdd/steps/test_role_match.py` passed in isolation and at file scope but failed intermittently in the full BDD marathon, the same suite-order class as MATTGPT-197, -198 and -203.

**Decision:**
Do not stabilize it.

**Rationale:**
- The test no longer exists. badde42 (MATTGPT-240 Red) replaced it with `test_non_jd_rejected_by_gate`, a gate-before-LLM rejection with new copy.

**Consequences:**
- A flake in the replacement test gets its own ticket.

---

## ADR 047: Ask Agy Answers Through a Search Tool Loop on gpt-6.1-sol; rag_answer() and Its Gates Are Retired

**Date:** 2026-10-15
**Status:** Accepted; ADR 061 corrects its `_degraded_fallback()` line and does not accept its opener lines as examples
**Related tickets:** MATTGPT-275, MATTGPT-282, MATTGPT-273, MATTGPT-169, MATTGPT-128, MATTGPT-292, MATTGPT-306

**Context:**
ADR 040 set the design: Ask Agy is a conversational system, and retrieval is its evidence step. Ask Agy still answered through `rag_answer()` in `backend_service.py`: the nonsense rules and the router, then `detect_entity()` with a hard Pinecone entity filter, `semantic_search()` on the visitor's literal words, a refusal below `CONFIDENCE_HIGH` (ADR 033), entity pinning and `diversify_results()` (or `get_synthesis_stories()` for synthesis), then `_generate_agy_response()` on gpt-4o with the stories in `<primary_story>` and `<supporting_story>` tags. Follow-ups retrieved on the bare question (ADR 034). MATTGPT-282 run 2 measured a tool-calling prompt ("lever 2") on gpt-6.1-sol: its lever2_sol arm scored 123/130, 122/130 under the quotation rule (`docs/evidence/MATTGPT-282/sol_arms_20261011_211830/`). A rewritten contract prompt scored 57/70 against lever 2's 61/70 on gpt-4o (4cb617f), so the build used lever 2's measured shape.

**Decision:**
- `send_to_backend()` calls `agy_answer()` only. The nonsense rules and the router's out_of_scope and personal redirects run first; suggestion chips skip both.
- Then a tool loop on `ASK_ANSWER_MODEL = "gpt-6.1-sol"`, on the Responses API, streamed, reasoning effort medium, 4000 output tokens. The input is `build_tool_system_prompt()` (the mode's system prompt, `TOOL_STORY_NOTE`, then `build_answer_instructions()` with Agy's opener lines as examples), the last two exchanges, and the question as asked. Call 1 must call `search_stories`; later calls may, up to `ASK_TOOL_MAX_ROUNDS` (3); one more call with `tool_choice` "none" must answer. The model writes each search query from the question and the conversation.
- `search_stories` runs `semantic_search()` with no filters and returns the first 5 stories. Search confidence does not gate the answer. The sources are the stories the searches returned.
- The answer streams into the conversation and is then replaced by the post-processed text.
- A model error other than a rate limit returns `ANSWER_ERROR_MESSAGE` ("Sorry, I couldn't generate an answer right now."), no sources, `degraded: True`. It replaces `_degraded_fallback()`, a keyword sort that scored almost every question 0, so the first three corpus stories in file order were cited and one story's 5P summary was shown raw in Matt's first person (seen Oct 13, 2026 after an APITimeoutError).
- Two nonsense rules are added: `gibberish` (two or more words each typed from one keyboard row) and `local_recommendations` ("best", "good" or "cheap" plus a food or venue word). With the confidence gate gone, "asdf jkl qwerty" and "Best pizza in Atlanta" reached the answering model.
- Removed: `rag_answer()`, `_generate_agy_response()`, `_degraded_fallback()`, `diversify_results()` and `_diversify_for_background()`, `get_synthesis_stories()`, `detect_entity()`, `ENTITY_ALIASES`, `ENTITY_DETECTION_FIELDS`, `EXCLUDED_DIVISION_VALUES`, entity pinning, the Ask Agy refusal below `CONFIDENCE_HIGH` (`[QUERY_REJECTED] reason=low_pinecone`), `build_user_message()` and its `<primary_story>` and `<supporting_story>` context, and the gpt-4o answer call's temperature and token settings. `semantic_search()` and its confidence buckets stay; My Work uses them.

**Rationale:**
- Gate rerun (`docs/evidence/MATTGPT-275/gate_20261015_093237/`; 3 arms interleaved, 10 runs, 1,250 rows, 0 errors, loggers patched; 32 blind scorers): new 386/450, opener arm 384/450, baseline 354/450. Invented figures, clients or dates: 0. Four turns below their bar (c03 t2, x1, x2, x4), each accepted as a known issue.
- Rejected: a score floor for garbage queries. It can't separate them: gibberish scored 0.17, "RBC?" 0.20.
- Rejected: the old overlap gate. It would block 12 must-answer follow-ups ("PMP?", "Sure.", "Would he relocate?"). Across 133 test queries and 7,573 log rows, the two rules matched only the two garbage test queries and one off-domain log row.
- Rejected: letting the model decide whether to search on call 1. It skipped the search on follow-ups (ADR 040).
- Not re-added: the Professional Narrative exclusion (MATTGPT-169). The gate run's grounding scores decide.

**Consequences:**
- Supersedes ADR 022 (no entity filter on Ask Agy), ADR 033 (Ask Agy no longer refuses on search confidence; My Work's buckets are unchanged) and ADR 040 (built, with the standalone query written by the model inside the tool call). ADR 034 stays Accepted: its history carriage holds, and its consequence that follow-up retrieval runs on the bare question is resolved, since the model writes each search query from the history. ADR 019's constraint has no subject left: `diversify_results()` is gone.
- No production caller sets the Pinecone entity filter. `ENTITY_SEARCH_FIELDS` and the `$or` builder in `pinecone_semantic_search()` remain.
- Professional Narrative stories show as sources for any question: in run 2's lever2_sol, 15 of 22 question-turns cited one. Source cards show what was retrieved, not what the answer cited (MATTGPT-128).
- When Pinecone returns nothing, `semantic_search()` falls back to the corpus in file order, and those stories reach the model as evidence (MATTGPT-292).
- Responses API calls are stored at OpenAI by default, visitors' questions included (MATTGPT-306).
- Required closings (c14 to c17) scored 0/10 in every arm, the baseline included; ADR 035 still holds.
- The golden eval and the structural tests call `agy_answer()` through a fixture in `rag_answer()`'s old call shape; the `entity_detection` eval category is skipped.
- The commit carries no `Decision:` or `Rejected:` trailer for this decision; it is recorded from the commit message.

---

## ADR 048: Ask Agy's Prompt Carries NO_DASH_RULE; normalize_dashes() Stays as the Backstop

**Date:** 2026-10-15
**Status:** Accepted; its Rejected line on Role Match's prompts is superseded for the assessment prompt by ADR 063
**Related tickets:** MATTGPT-275, MATTGPT-301

**Context:**
On gpt-6.1-sol, Ask Agy's answers carried em and en dashes: 42 of 55 answers in the current-prompt arm had one.

**Decision:**
- `NO_DASH_RULE` (`config/constants.py`): "Don't use em dashes or en dashes; use a comma, a colon, parentheses or a separate sentence, whichever fits." `build_answer_instructions()` carries it after the prose line, so both of Ask Agy's system prompts have it.
- `normalize_dashes()` (`backend_service.py`) stays on Ask Agy's stream and final text as the backstop: an em dash or spaced en dash becomes ", ", an en dash between digits becomes " to ", an en dash joining two words becomes "-".
- The prompts' own em dashes are rewritten by hand, as are the fixed texts visitors read: the rate-limit messages, source chip labels ("Client: Title"), the personal chip's question, the "Also relevant:" and "Scope:" lines, and the Why Agy? paragraphs.

**Rationale:**
- Four-arm run (`docs/evidence/MATTGPT-275/dash_arms_20261014_071542/`; c01, c03, c09, x1, x3; 5 runs each, 55 answers per arm): answers with a dash went from 42 of 55 to 4 of 55 with the line, each of the 4 a bolded number range copied from a story, which `normalize_dashes()` turns into "70 to 80%". Single em dashes per answer 0.73 to 0. No stand-ins (spaced hyphens 0, "--" 0); parentheses, colons and length unchanged.
- Backstop replay on run 2's 130 saved answers: 162 of 163 dashes replaced, 0 cleanup defects, 260 stream replays matching.
- Rejected: the rule in Role Match's prompts. On gpt-4o its model-written text had no dash with or without it (`docs/evidence/MATTGPT-275/role_match_dashes_20261014_113329/`): assessment notes and gap explanations 0 of 165 rows before, 0 of 167 after.
- Rejected: rewriting the prompt's own em dashes as the fix. Without the line it changed nothing (48 of 55).

**Consequences:**
- The dashes visitors see on Role Match are the JD's own wording and one corpus story title cited as evidence. Neither gets a backstop.
- Gate rerun (ADR 047): visible dashes in Sol answers 0 of 900.
- `tests/unit/test_no_dash_rule.py` pins the rule and the dash-free prompts; the run 2 parity fixture holds the prompt to arm D's measured text.

---

## ADR 049: Ask Agy's Prompt Carries COMPARISON_RULE

**Date:** 2026-10-15
**Status:** Accepted
**Related tickets:** MATTGPT-275, MATTGPT-251

**Context:**
On c12 t2 ("Which was bigger?" after Fiserv and JP Morgan ACCESS), answers ranked Fiserv's 45-person team above ACCESS's 40+, and ranked by measures only one side has.

**Decision:**
`COMPARISON_RULE` (`config/constants.py`), on the line after `NO_DASH_RULE` in `build_answer_instructions()`, so both of Ask Agy's system prompts carry it: "When asked which of two things was bigger or better, compare only on a measure the stories give for both, in the same units. If their figures can't settle it (an open-ended figure against an exact one, or two different measures), say the stories don't establish which is larger."

**Rationale:**
- Control isolation run (`docs/evidence/MATTGPT-275/control_iso_20261015_065005/`; 200 turns, 10 runs, blind): c12 t2 3/10 without the rule, 10/10 with it; the controls c01 t1 to t3 and c12 t1 10/10 with and without. Gate rerun: c12 t2 10/10 in both Sol arms.
- Rejected: removing "Draw on all the stories provided." first. It fixed no target, and x1 fell to 1/3 (five-arm run, `docs/evidence/MATTGPT-275/rule_arms_20261014_214612/`, 270 turns; c12 t2 2/3).
- Rejected: `INDUSTRY_CLAIM_RULE` in this change. It moves to MATTGPT-251, whose candidate rule it is; its arm dropped c01 t3 to 8/10.
- Rejected: `TERM_SENSE_RULE` in this change. It is held until MATTGPT-251 lifts the `stocks_crypto` hold, since production refuses x3 before the model runs (ADR 043).

**Consequences:**
- x1 ("Has Matt worked in real estate?") stays below its bar (new 1/10) and is a known issue under MATTGPT-251.
- `tests/unit/test_comparison_rule.py` pins the rule and its position; the parity fixture's two system prompts carry it.

---

## ADR 050: Ask Agy's Stream Has a 30 s Read Timeout and One Retry Before Any Answer Text

**Date:** 2026-10-15
**Status:** Accepted
**Related tickets:** MATTGPT-303, MATTGPT-275, MATTGPT-302

**Context:**
`_openai_client()` used the SDK's 600 s read timeout. The SDK's own 2 retries wrap only the request send, not a stream that breaks after it starts. The overnight five-arm run had three failures (2 connection resets, 1 read timeout after 604 s), all before any answer text.

**Decision:**
- `_openai_client()` sets a read timeout of `ASK_ANSWER_READ_TIMEOUT_S = 30` s; connect stays 5 s.
- `_stream_response()` sends a stream that raises `httpx.TransportError` before any answer text again, once. After text, the visitor has seen part of the answer, so the break raises and the turn ends on `ANSWER_ERROR_MESSAGE`.

**Rationale:**
- Gap probe (`docs/evidence/MATTGPT-275/stream_gaps_20261015_091852/`, 279 calls on the gate's turn set): the longest silence per call was 3.52 s at p99 and 3.67 s at most, all before the first answer text; 0.62 s at most after it.

**Consequences:**
- A healthy stall of 30 s would now be cut and sent again. The 122.7 s overnight turn that recovered (x3, 430 output tokens over 3 calls) would be cut if any one silence in it reached 30 s; its silences weren't recorded. If healthy stalls that long appear, revisit the timeout.
- `backend_service.py` imports `httpx` directly; openai 2.5.0 requires it, so it is not a new dependency.
- The retry catches `httpx.TransportError`. openai 3.x moved to httpx2, where the retry is inert; the 30 s timeout still applies. The Streamlit Cloud builds had installed 3.28.0 and 3.31.0 because `requirements.txt` listed openai with no version, so 130febd pins `openai==2.5.0`, the version every test, probe and gate ran on. `requirements-ci.txt` stays unpinned: CI's unit tests replace `openai.OpenAI` with a fake. Moving to openai 3.x, with tests, belongs with MATTGPT-302. 130febd carries no trailer; it is recorded here from its message.
- `TestBrokenStreams` and `TestClientTimeout` in `tests/unit/test_ask_agy_tool_answer.py` pin the retry and the timeout.

---

## ADR 051: The Search Tool's Story Text Carries Start_Date and End_Date

**Date:** 2026-10-15
**Status:** Accepted
**Related tickets:** MATTGPT-275, MATTGPT-311

**Context:**
`build_story_context_for_rag()` passed no dates, so the model answered "how long" and "when" questions with "not on record".

**Decision:**
`build_story_context_for_rag()` (`story_intelligence.py`) adds "[DATES]: <Start_Date> to <End_Date>" after the Domain line when a story has both, so the `search_stories` tool's story text carries them.

**Rationale:**
- Acceptance run (`docs/evidence/MATTGPT-275/dates_accept_20261014_210208/`; 54 turns, loggers patched, blind): 49 of 54 after 2 recorded corrections.
- Gate rerun: c18 t3 10/10 and c10 t3 6/10, against a baseline of 0/10 on both. Every Sol answer to x7 gives dates; every baseline answer says it has none.

**Consequences:**
- A story without an End_Date gets no dates line, including an ongoing period (MATTGPT-311).
- c03 t2: 2 of 10 answers place a 2014-2019 incident under a 2019-2023 culture the dates rule out. Accepted; the story's broad dates are part of its anonymization.
- x7 ("When was he at JP Morgan?"): answers list three of the four periods, because top-5 retrieval misses one story.
- `TestStoryDates` in `tests/unit/test_story_intelligence.py` pins the line.

---

## ADR 052: Role Match Required and Preferred Rows Carry the Verbatim JD Bullet

**Date:** 2026-09-20
**Status:** Accepted
**Related tickets:** MATTGPT-244

**Context:**
The assessor received the extraction model's compressed `requirement`, which dropped qualifiers such as "AWS, Azure, or GCP".

**Decision:**
`_flatten_extraction()` in `services/jd_assessor.py` uses `source_text` as the row text for required and preferred rows, falling back to `requirement`; implicit rows keep `requirement`. The required and preferred extraction prompts tell the model to copy `source_text` as the entire JD bullet or sentence, verbatim and complete (b28a080).

**Rationale:**
- A matched-sample probe on the same JD compared the old and new instruction: truncations went from 23/85 to 0/85. The figure was recorded only in ARCHITECTURE.md (45d6321), with no evidence path.

**Consequences:**
- `source_text` fidelity is checked by exact match against JD lines, not containment; a truncated span still passes a containment check.
- The `requirement` field stays compressed, and implicit rows are inferred text by design (Role Match Known Defects in ARCHITECTURE.md).

---

## ADR 053: Ask Agy Accepts Seven Behaviors the 1095d2c Audit Found Dropped

**Date:** 2026-10-17
**Status:** Superseded by ADR 061
**Related tickets:** MATTGPT-236, MATTGPT-275, MATTGPT-077, MATTGPT-128

**Context:**
A Code audit compared 1095d2c^ with 1095d2c and listed each behavior dropped or changed when `rag_answer()` became `agy_answer()` (ADR 047). A golden comparison from recorded calls only went with it: `docs/evidence/MATTGPT-275/golden_rag_20261014_140843/` vs `docs/evidence/MATTGPT-320/golden_20261016_102942/`. The figures below are the audit session's, as recorded on MATTGPT-236.

**Decision:**
Seven audit rows are accepted as part of the target answer path, in which the router is out of Ask Agy and the model judges (5e3e99f):
- Row 12: a router failure (error_fallback) with a low or empty search no longer shows "I need a quick breather".
- Row 15: suggestion-chip and forced answers no longer add the top 5 keyword-matched stories to the pool.
- Row 16: entity cluster promotion no longer sends "What did Matt do at RBC?"-shaped questions to the synthesis prompt.
- Row 18: the synthesis pool no longer puts named-client stories ahead of generic ones.
- Row 19: the narrative family's ordering step (Professional Narrative kept at #1, the rest diversified) is gone.
- Row 28: SYNTHESIS_DELTA no longer fills `{client_list}` with the retrieved named clients.
- Row 41: the query log no longer records search confidence (high, low or none).

**Rationale:**
- The recorded reason: the model judges, with no router (ADR 054).
- Row 28: 0 confirmed figure misattributions in synthesis answers in either golden run; no effect established either way.
- Row 12: not measured (0 error_fallback rows in either golden run).

**Consequences:**
- Row 13 (every search empty: the model answers instead of refusing) is covered by rule 0b's decline (ADR 056): in the -236 gate and MATTGPT-322 run 6, 20 turns had every search empty, all "Is Matt married?", and all 20 declined without invented content. Empty searches on work-history questions aren't covered.
- Row 27 is open on MATTGPT-236: the Professional Narrative verbatim-phrase block is added for every narrative story any search returns, not only when the top story is one.
- Row 8 stays on MATTGPT-077, unmeasured. Row 38 folds into MATTGPT-128.

---

## ADR 054: Ask Agy Makes No Semantic Router Call

**Date:** 2026-10-17
**Status:** Planned, conditional: MATTGPT-236 was re-scoped on 2026-10-18 to first decide how big-picture questions get breadth (keep or replace the synthesis pick); it becomes Accepted only after that decision and -236's Green
**Related tickets:** MATTGPT-236, MATTGPT-322, MATTGPT-329, MATTGPT-223, MATTGPT-239

**Context:**
`agy_answer()` calls the semantic router after the nonsense rules: an out_of_scope or personal family at `HARD_ACCEPT` gets a redirect banner, and the synthesis family picks the synthesis prompt. A gate run on a frozen checkout of 725d564 (1743846, `docs/evidence/MATTGPT-236/gate_20261016_140623/`; 10 runs, 1,830 turns, blind-scored) compared arm A as shipped, arm B with the router returning an empty family, and arm C passing only a personal family.

**Decision:**
Ask Agy makes no router call, including no score-only call: no redirects and no synthesis pick (5e3e99f). Arm B was decided on Oct 16, 2026, sequenced after MATTGPT-322's decline; the target was set on Oct 17. MATTGPT-223 and MATTGPT-239 are re-scoped to My Work. Status becomes Accepted when MATTGPT-236's Green lands.

**Rationale:**
- All turns: A 524/610, B 532/610, C 531/610. The 49 questions the router does not change: A 427/490, B 430/490, C 430/490, the noise floor.
- The 12 questions it changes: A 97/120, B 102/120, C 101/120. The synthesis pick changed nothing measurable (A 67, B 66, C 65 of 80).
- Rule 0b's sentence on the personal and hobby questions (r01 to r06): A 28/60, B 57/60, C 24/60.
- Rejected: arm C, a personal-only gate (24/60 on r01 to r06).

**Consequences:**
- The nonsense rules are the only check before the model; crude questions about Matt are caught there (ADR 055).
- Married, age and kids questions move from the personal banner to rule 0b's decline (ADR 056).
- My Work keeps its router call.
- ARCHITECTURE.md keeps describing Ask Agy's router redirects until the Green lands.

---

## ADR 055: Crude Questions About Matt Are Rejected by the adult_content Rule

**Date:** 2026-10-17
**Status:** Accepted
**Related tickets:** MATTGPT-329, MATTGPT-236

**Context:**
Crude questions about Matt ("Does Matt have a penis?") were rejected by `rag_answer()`'s low-confidence gate until 1095d2c removed it (ADR 047), and then reached the answering model. "Is Matt sexy?" reached the model before 1095d2c too.

**Decision:**
`adult_content` in `nonsense_filters.jsonl` widens from `\b(nsfw|porn|xxx|nude|naked|sex)\b` to `\b(nsfw|porn|xxx|nude|naked|sex|sexy|penis|vagina|genitals?)\b`, so these questions are rejected before the router, search or any model call (88ac7ed).

**Rationale:**
- Across the local logs (6,369 borderline, 1,075 off-domain and 255 router low-confidence rows) and the query log (327 rows), the new pattern matches only the five logged crude questions (old pattern: 0); the must-preserve set (59) matches 0. "Essex", "Sussex", "sextant" and "sexton" do not match.
- Live check (`docs/evidence/MATTGPT-329/live_20261017_130336/`): the five targets hit `rule:adult_content` with 0 model calls, 10/10; six story and fact controls answered, 12/12.
- Rejected: restoring a search-confidence gate (1095d2c removed it because it blocked 12 must-answer follow-ups).
- Rejected: relying on the router's personal family (it scores these 0.58 to 0.68, below `HARD_ACCEPT`, and leaves Ask Agy's answer path under ADR 054).

**Consequences:**
- With the router out of Ask Agy (ADR 054), the nonsense rules are the only check before the model.

---

## ADR 056: Rule 0b Declines in Agy's Voice, Opening With a Line Picked in Code

**Date:** 2026-10-17
**Status:** Accepted
**Related tickets:** MATTGPT-322, MATTGPT-236

**Context:**
Rule 0b (a question about a category the profile has no key for, such as patents or publications) told the model to reply "Nothing I know about Matt covers that" and nothing else. After an opener that promised content it read as bare and dismissive: with the router off, it met the voice checklist and decline standard 0/80 and was too dismissive 57/80.

**Decision:**
Rule 0b states only the requirements: decline in first person, in one or two sentences, the first beginning with 🐾, the topic named in the model's own words, no guessing, no padding with story evidence, no excess apology. `_choose_decline_line()` in `backend_service.py` picks one of `DECLINE_LINES` per answer, and `build_answer_instructions()` gives it to the model in both modes as "**IF YOU DECLINE:** Begin with this line, filling in the topic in your own words". Nothing is inserted into the answer (58fe71f).

**Rationale:**
- Live run (`docs/evidence/MATTGPT-322/run6_20261017_115952/`, router off, 17 questions x 10): declines 79/80, the assigned line followed whole 78/80 (run 4: 45/80), facts 40/40, story controls 49/50, no decline-line wording in any fact or control answer.
- Rejected: the fixed reply-only sentence (0/80 on the voice checklist and decline standard).
- Rejected: examples to vary in the prompt (run 3: the model used none of four lines; it cannot vary across calls it does not see; 7a866bc's "Vary your opening naturally" failed the same way).
- Rejected: "Use this shape" (run 4: line followed whole 45/80, patents 1 of 10).
- Rejected: four decline lines ("That trail goes cold here" misread on age, followed 5 of 19; "I've been through Matt's stories" followed 3 of 10).
- Rejected: inserting the line into the answer after the response (text chosen without knowing the answer).

**Consequences:**
- In a conversation that repeats the question, the model follows the line less often on later turns (repeat run: 10/10, 10/10, 8/10, `docs/evidence/MATTGPT-322/run7_20261017_123603/`).

---

## ADR 057: The Career Arc's Facts Live in matt_profile.json

**Date:** 2026-10-15
**Status:** Accepted
**Related tickets:** MATTGPT-294, MATTGPT-275, MATTGPT-209

**Context:**
MATT_DNA's Career Arc lines (progression, employers and years, current status) were hard-coded in `generate_dynamic_dna()`.

**Decision:**
The arc's facts live in `data/matt_profile.json` as `career_arc` (`progression`, `employers` with `name`, `years` and an optional `note`, and `current`), and `generate_dynamic_dna()` renders them from the profile, as it does `self_description` (ADR 038). The CIC line stays derived from the CIC story's practitioner count. Each line is left out when its field is empty (24d00ca).

**Rationale:**
- MATT_DNA rendered by the new code matched the old code's output, 3,219 vs 3,219 characters, 0 diff lines; Ask Agy's standard and synthesis system prompts were identical before and after.
- Rejected: moving the CIC line into the profile (it would hard-code a corpus value).

**Consequences:**
- Editing "current" is a one-line profile change.
- Role Match grounding (`jd_assessor.load_matt_profile()`) does not render the arc.
- The drift guard checks each corpus Employer against the Career Arc block only, and its failure points to `career_arc` (1b0e68c).

---

## ADR 058: A Commit Deleting a Production Function Names It in a Decision Trailer

**Date:** 2026-10-17
**Status:** Accepted
**Related tickets:** MATTGPT-287, MATTGPT-217

**Context:**
In the MATTGPT-287 and MATTGPT-217 pre-flight, "no production caller" for MATTGPT-077's query substitution turned out to mean its only caller was retired in 1095d2c, which a deletion would have buried.

**Decision:**
`.githooks/commit-msg` fails a commit that removes a def (including async defs and methods, and every def in a deleted file) from a `.py` file under `ui/`, `services/`, `utils/` or `config/` without re-adding it anywhere in the commit, unless a `Decision:` line names it as `<file>:<function>`. The session that deletes it writes the trailer (62d975b; message wording in f3cb599).

**Rationale:**
- Signature edits and moves between files pass, since the name is re-added; removals under `tests/` are not checked.
- Rejected: a `Removal-Approved: Matt` trailer only Matt can write, enforced by `guard-bash.sh` (sessions record the decision themselves; naming each function is the check).

**Consequences:**
- Deleted calls are not checked, only deleted defs.

---

## ADR 059: The Excel Export Rebuilds the JSONL; the Prior-JSONL Merge Is Removed

**Date:** 2026-10-16
**Status:** Accepted
**Related tickets:** MATTGPT-323, MATTGPT-072, MATTGPT-270

**Context:**
`generate_jsonl_from_excel.py` merged each Excel record with the prior JSONL record matched by `norm_key()`: `_merge_with_existing()` kept `content` and any prior-only field when Excel did not supply them. The lookup used `norm_key()` while ids use slugs, so the merge matched only when the two keys agreed: 0 of 124 keys in today's corpus, but any one-word Title and Client.

**Decision:**
The JSONL is rebuilt from the Excel master on every run; nothing from the prior JSONL carries over. `_merge_with_existing()`, `norm_key()` and the `existing_by_key` lookup are deleted. `load_existing_jsonl()` returns the prior records only, for the change report and the summary counters (a66ce99).

**Rationale:**
- The rule is that the JSONL is rebuilt from the Excel master; MATTGPT-072 had already made Excel authoritative for `public_tags`. The merge was dead for today's corpus but not for one-word titles and clients.
- On the real master, the export's output JSONL was byte-identical before and after.

**Consequences:**
- A field that exists only in the JSONL does not survive an export.

---

## ADR 060: Q15 Keeps Its Client-Name Check

**Date:** 2026-10-16
**Status:** Rejected
**Ticket:** MATTGPT-082
**Related tickets:** MATTGPT-275, MATTGPT-320

**Context:**
Q15 ("Matt's work at Fiserv") once failed because the answer described the Fiserv engagement without naming Fiserv. The ticket proposed checking response correctness instead: project-anchor phrases, a looser `client_variants` list, or removing Q15.

**Decision:**
Q15 stays as it is.

**Rationale:**
- Q15 is a `category: "client"` query in `TestClientAttribution`: `check_client_attribution()` looks for a variant of the expected client, and a single-client query also fails when the client is not bolded. Checking that the client is named and bolded is the test's purpose; content correctness is covered by the ground-truth checks.
- Q15 passed in both golden runs: `docs/evidence/MATTGPT-275/golden_agy_20261014_150939/` and `docs/evidence/MATTGPT-320/golden_20261016_102942/`.

**Consequences:**
- None.

---

## ADR 061: Decisions on the Behaviors 1095d2c Dropped From Ask Agy

**Date:** 2026-10-19
**Status:** Accepted; row 13 accepted in full for work-history questions too (MATTGPT-339, 94f256c; the agriculture miss is a retrieval miss on -325).
**Related tickets:** MATTGPT-236, MATTGPT-275, MATTGPT-128, MATTGPT-338, MATTGPT-292, MATTGPT-077, MATTGPT-322

**Context:**
A Code audit compared 1095d2c^ with 1095d2c, where `agy_answer()` replaced `rag_answer()`, and listed each behavior dropped or changed by row. Independent confined checkers re-checked it claim by claim, and Matt walked it row by row on Oct 18 and 19, 2026 against recorded runs: the old path's golden run (`docs/evidence/MATTGPT-275/golden_rag_20261014_140843/`), the new path's (`docs/evidence/MATTGPT-320/golden_20261016_102942/`), the MATTGPT-236 gate, MATTGPT-322 run 6 and the MATTGPT-320 extras. ADR 047, ADR 053 and the BACKLOG audit lines were provisional records until this walkthrough, not decisions. The audit's row table is not in the repo; rows without a description here are cited by number only.

**Decision:**
- **Kept:**
  - Row 1: suggestion-chip and force-answer flags skip the checks. Chips are static questions, designed at design time.
  - Rows 10, 31 and 34: the embedding-failure breather, what the model is told, and the rate-limit breather.
  - Row 3: the router's out_of_scope and personal redirects, unchanged. Whether the router stays in Ask Agy is MATTGPT-236's decision (ADR 054).
- **Accepted:**
  - Row 2: the `gibberish` and `local_recommendations` nonsense rules added in 1095d2c.
  - Row 4: removal of the mode-word shortcut; it was not a valid scenario.
  - Rows 6, 7 and 21: removal of entity detection, the hard client filter and the slot-1 pin.
  - Row 36: source cards are every story retrieved, until MATTGPT-128's cited cards replace them.
  - Rows 16, 17, 18, 22, 23, 28 and 30: removal of synthesis promotion, per-theme retrieval, named-client ordering, client diversity, era diversity, `{client_list}` and synthesis selection, as mechanisms. The capability they served comes back as a priority, through MATTGPT-236's breadth decision.
  - Rows 11, 12 and 33: removal of the confidence gate, the router-failure breather and the error fallbacks.
  - Row 9: the model writes each search from the question and the conversation.
  - Row 15: chip pool widening.
  - Row 19: narrative ordering.
  - Row 24: the ranking-error safety net.
  - Row 25: the story count read by the model.
  - Row 32: the answer model and its settings.
  - Row 35: post-processing.
  - Row 13, for the personal case only: an empty search on a personal question is declined by rule 0b (ADR 056).
- **Dropped:** row 5 (debug-only), and rows 37, 39, 40, 41 and 42.
- **Not accepted:**
  - Row 29: the opener. The opener `_choose_opening_and_focus()` picks is to be passed to the model as "Begin with this line", not shown among the opener lines as examples.
  - Rows 20 and 27: Professional Narrative stories on technical questions, and their verbatim-phrase block. Decided together with the "builder" revisit.
- **To change:** row 26: remove "Go deep on the primary story" from `STANDARD_DELTA`.
- **Open:**
  - Row 14 (the file-order fallback when Pinecone returns nothing), on MATTGPT-292.
  - Row 8 (Matt substitution in the search query), on MATTGPT-077, decided with rows 20 and 27.
  - Row 13 for work-history questions: a NEXT chore after MATTGPT-338 checks empty searches there.

**Rationale:**
- Row 2: `local_recommendations`' broad case, a food or venue word anywhere in a portfolio question, is untested in the logs.
- Row 42: the check it lost is covered by MATTGPT-338's breadth measures.
- Rows 6, 7 and 21: card accuracy on questions that name a client goes to MATTGPT-128.
- Row 13: the personal case is measured. In the MATTGPT-236 gate and MATTGPT-322 run 6, 20 turns had every search empty, all "Is Matt married?", and all 20 declined without invented content.

**Corrections:**
- ADR 053's text was wrong in four places:
  - Row 15 is not "keyword-matched". `_score_story_for_prompt()` scored a story only when the whole question was a substring of its Title, Client, Industry or tags, so almost every question scored 0 on every story, and the sort kept the first 5 corpus stories in file order.
  - Row 16's example, "What did Matt do at RBC?", is in neither golden run. In the old run's directory it appears only in the as-run copy of `backend_service.py`.
  - Row 28's "0 confirmed figure misattributions" has no recorded method.
  - Row 12 left out that the embedding-failure breather still fires: `agy_answer()` returns it when `__embed_failure__` is set.
- ADR 047 (row 33) and the 1095d2c commit say `ANSWER_ERROR_MESSAGE` replaces `_degraded_fallback()`. Model errors never reached `_degraded_fallback()`, which ran only on an exception before ranking. `_generate_agy_response()` caught a model error other than a rate limit and returned "🐾 Let me show you what I found..." followed by `_format_narrative()` of the top story, and `rag_answer()` still returned the ranked stories as source cards.

**Consequences:**
- ADR 053 is superseded by this ADR.
- ADR 019, ADR 023 and ADR 024 are superseded by ADR 047: `diversify_results()`, `ENTITY_ALIASES`, `detect_entity()` and its fields were deleted in 1095d2c.
- ADR 034's "Retrieval, the gates, and the semantic router still see only the current question" no longer holds for retrieval (row 9). The nonsense rules and the router still see only the current question.
- ADR 035's "The random opener and focus angle stay" holds for the focus angle. Since 1095d2c the picked opener has been discarded and the model shown the opener lines as examples; row 29 restores the picked opener.
- MATTGPT-236 owns breadth for big-picture answers (rows 16 to 30) and the card cap on them (row 38); MATTGPT-128 references it.
- Rows 26 and 29 are prompt changes, each under the answer-pipeline gates.

---

## ADR 062: Role Match Is Desktop Only; Below 1024px a Gate Replaces the Input

**Date:** 2026-10-14
**Status:** Accepted
**Related tickets:** MATTGPT-102

**Context:**
Role Match's two-column workspace is legible only at iPad Pro width or wider. The gate below 1024px has been in place since April 2026, but no ADR or ticket recorded desktop only as a decision; only the BDD "DESKTOP ONLY" scenarios and a CHANGELOG entry carried it. The Role Match intent review (Oct 20, 2026) listed it as an intent line with no decision record.

**Decision:**
Role Match is desktop only (Matt, Oct 14, 2026). Below 1024px the page shows "Best experienced on desktop" in place of the JD input. Mobile Role Match is not a supported surface: skipped mobile Role Match scenarios are not coverage gaps, and mobile fixes beyond the gate itself are out of scope.

**Rationale:**
- The comment above the gate in `ui/pages/role_match.py` records why the threshold is 1024px: visual testing showed the two-column workspace is legible only at iPad Pro width or wider, and tablets in the 768 to 1023px range rendered it cramped.

**Consequences:**
- `app.py` captures `window.innerWidth` once per session into `st.session_state["_browser_screen_size"]`. The gate in `ui/pages/role_match.py` shows when that value is below 1024 or missing.
- Measured by `tests/bdd/steps/test_role_match.py`: "Role Match shows mobile gate at 375px" and "Desktop shows full Role Match interface", both bound and not skipped.

**History:**
- f033c64 (Apr 8, 2026) raised the gate threshold from 768px to 1024px.
- dd4314d (Apr 11, 2026) switched the capture to `screen.width`, after the `streamlit_js_eval` iframe could report `window.innerWidth` as 0 on Streamlit Cloud and fire the gate on desktop.
- d4354fc (Jun 6, 2026, MATTGPT-102) switched back to `window.innerWidth`: `screen.width` reports the physical display resolution, so the gate never fired on desktop browsers emulating mobile viewports. The capture iframe is excluded from the `stIFrame` collapse rule by its `st-key-screen_size_capture` class.

---

## ADR 063: Role Match Runs on gpt-5.6-terra at Low Effort, With a 30 s Read Timeout and 2 Retries

**Date:** 2026-10-25
**Status:** Accepted
**Related tickets:** MATTGPT-302, MATTGPT-012

**Context:**
The gpt-4o family retires January 14, 2027. Role Match's four calls (`_call_required`, `_call_preferred`, `_call_implicit`, `assess_requirement()`) ran on gpt-4o at temperature 0.0, and its client had the SDK's default timeout and retries.

**Decision:**
- All four calls use `ASSESSMENT_MODEL`, which is `DEFAULT_CHAT_MODEL` (`config/constants.py`, "gpt-5.6-terra"), with `reasoning_effort=DEFAULT_REASONING_EFFORT` ("low"). They send no temperature, since the model rejects it; `ASSESSMENT_TEMPERATURE` is removed.
- `_get_openai_client()` sets `ROLE_MATCH_MAX_RETRIES = 2` and a read timeout of `ROLE_MATCH_READ_TIMEOUT_S = 30` s, connect 5 s. The calls are not streamed, so the read timeout covers the whole call.
- `JD_ASSESSMENT_PROMPT_TEMPLATE` carries `NO_DASH_RULE`, on the line before the JSON-only line.
- `_REQUIRED_EXTRACTION_PROMPT`'s Populate rule drops "(what the role does, not what the candidate must have)". `key_responsibilities` stays in the schema.
- `DEFAULT_CLASSIFICATION_MODEL` is removed; nothing read it.
- The acceptance bar no longer requires recommendations unchanged from gpt-4o: `compute_recommendation()` has no `ui/` caller, so visitors never see one.

**Rationale:**
- Acceptance, live through `run_assessment()` on all 10 test JDs, 3 runs (`docs/evidence/MATTGPT-302/`: `green_20261025_073015`, `paren_20261025_091309`, `green_confirm_20261025_094412`): end to end at most 30 s on every JD (slowest 28.1 s; AT&T 21.1 to 24.7 s; demo 14.3 to 17.3 s, against gpt-4o's 13.6 to 16.5 s). Required plus implicit never 0; within 25% of gpt-4o's count wherever gpt-4o extracts 5 or more. 0 strong rows without evidence, 0 cited stories outside those given, 0 dashes, 0 output shape failures.
- Rejected: gpt-6.1-sol at medium. AT&T took 49.5 to 65.2 s end to end.
- Rejected: a 60 s read timeout, sized for gpt-6.1-sol's 24.6 s call. On Terra at low, the slowest call measured was 10.35 s over 722 calls.
- Rejected: no dash rule. Terra wrote 10 dashes in 6 runs without it.
- Rejected: removing `key_responsibilities`. Extraction was also steady without it, but removing it would supersede ADR 016's responsibilities output and MATTGPT-012's option on it.

**Consequences:**
- ADR 048's rejection of the rule in Role Match's prompts no longer holds for the assessment prompt, where gpt-4o wrote no dashes and Terra does. The extraction prompts still don't carry it.
- ADR 016 names Claude as the extraction model; extraction runs on `ASSESSMENT_MODEL`.
- `compute_recommendation()` serves `scripts/assess_jd.py`. On Terra, AT&T gave Apply/High in 4 of 12 production-shaped runs, where gpt-4o always gave Consider/Medium.
- Two runs over 30 s, both on the `key_responsibilities` removal arm (hybrid_jd 41.8 s, narrative_jd 38.2 s), had embedding calls of 6 to 17.8 s (median 0.4 s) and slower chat calls in the same runs.
- The four root generator scripts stay on gpt-4o until MATTGPT-302's later cycles (three deleted, the tag script moved), and openai 3.x is still pending (ADR 050).

**History:** 4818c59 (Red on gpt-6.1-sol), 2a7a56d (RM-D1 reopened), d6c1fb4 (Red on gpt-5.6-terra), de3b698 (Populate rule Red), 466b55a (Green).
