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
**Status:** Accepted  

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
**Status:** Accepted

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
**Status:** Accepted

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
**Status:** Accepted
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