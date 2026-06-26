# Changelog

Shipped work for the MattGPT project, organized by month. For open work, see `BACKLOG.md`. For architectural decisions, see `docs/ADR.md`.

---

## June 2026

### CSS Architecture

**June 2026 — Page-load blep: re-add visibility:hidden on Ask Agy stale hero during nav (MATTGPT-018)** — `a6b427c`
Re-added CSS rule to `global_styles.py` hiding Ask Agy landing hero containers during the Streamlit stale-element retention window on navigation. Both selectors (`.main-intro-section`, `.ask-header-landing`) with `visibility: hidden !important`. Mechanism comment restored including deliberate `.ask-header-conversation` exclusion. Unit test added in `tests/unit/test_global_styles.py`: whitespace-tolerant assertion that selectors and `visibility: hidden !important` are present as a unit in `_CSS`, catching both rule deletion and mutation to a no-op value. 3/3 BDD scenarios passing.

### My Work

**June 2026 — My Work Table view: migrate from st_aggrid (iframe) to st.dataframe / Glide Data Grid (MATTGPT-144)** — `77dc1cb`
Replaced st_aggrid with st.dataframe (Glide Data Grid) in the My Work Table view. Eliminates the AgGrid custom-component iframe re-init on filter rerun (the -144 symptom) and removes the AgGrid bootstrap.min.css 195ms revalidation round-trip on page nav. BDD: 55/55 passing, 0 skipped. Key test changes: removed all AgGrid iframe / `.ag-row` / `frame_locator` assertions; added `st.dataframe` canvas-mount proxy (`data-grid-canvas`); replaced `networkidle` waits with `wait_for_streamlit_rerun` (Glide Data Grid's continuous XHR never settles networkidle); converted empty `pass` stubs to count-direction logic via `_read_count()`; added Cards-view-switch fallback in `click_story_card` (3 scenarios now run instead of skip); added Share "Copied!" confirmation scenario. Deleted 2 scenarios: Table-row Ask Agy (canvas row-click undriveable, redundant with Cards) and deeplink-respects-view-mode (non-feature: deeplinks intentionally start fresh session). Guard proof: breaking `no_story_results_shown` fails both rejection scenarios; non-vacuous.

### Ask Agy Performance

**June 2026 — Ask Agy landing chips: st.button → static HTML + JS bridge (MATTGPT-139)** — `4e8e461`, `722972b`
Converted 6 `st.button` chips + `st.columns` on the Ask Agy landing page to static HTML with a hidden receiver JS bridge (pattern from `category_cards.py`). Reduced navigation span window from ~667ms to ~400ms (40% reduction); FunctionCall cost from ~105ms to 82.5ms. Desktop and mobile paths both converted. Disabled state added via CSS pointer-events on the grid container during query submission. `.suggested-chips-grid` / `.suggested-chip` rules moved to `global_styles.py`. BDD: 14/14 scenarios passing. The 400ms floor is the practical limit of the chip-conversion approach — blep is narrower but not eliminated (see MATTGPT-018).

### My Profile

**June 2026 — My Profile visual-language reconciliation (MATTGPT-093)** — `4bbdb46`
About Matt strategic restructure resolved as a visual-language reconciliation. CTO and recruiter persona findings (May 27) drove a surface redesign that retained the single-page structure while improving the recruiter-facing conversion moment. 19/19 BDD scenarios passing.

**June 8 — My Profile — Copy snippet + Download PDF buttons (MATTGPT-118)** — `223aabf`
Added Copy snippet and Download PDF affordances. Copy uses delegated parentDoc listener + navigator.clipboard. PDF uses hidden st.button bridge + window.open/print. 20/20 BDD scenarios passing.

### How I Built

**June 8 — How I Built dialog — BDD coverage for "See It In Action" prompt buttons (MATTGPT-117)** — `97c7d51`, `3278128`
Added 2 BDD scenarios to `how_i_built.feature`: section visibility + 4-chip count, and chip-click → Ask Agy routing (first chip). 8/8 passing. Closes coverage gap left when MATTGPT-068 scenarios were removed from `about_matt.py` during MATTGPT-093.

### CSS Architecture

**June 17 — Gate mobile navbar IIFE behind viewport check (MATTGPT-135)** — `f818469`, `74ce328`
The mobile navbar IIFE in `navbar.py` ran on every Streamlit rerun regardless of viewport width, causing wasted DOM work and a double-avatar flash on desktop during page transitions. Fix: `if (window.parent.innerWidth > 767) return;` guard at the top of the IIFE. Must use `window.parent.innerWidth` not `window.innerWidth` — the IIFE runs inside a srcdoc iframe whose own viewport width differs from the parent page. Follow-up commit `74ce328` fixed a desktop dark mode regression introduced by the guard placement. BDD: 2 scenarios in `navbar_mobile_viewport_gate.feature` passing.

**June 14 — Page-transition Agy avatar flash — HTML constraints + mousedown pre-hide (MATTGPT-018)** — `bda7ba8`, `3659173`
Fixed 330px Agy avatar flash during Ask Agy → other page transitions. Root cause: `agy_avatar.png` renders at natural size during the window where Streamlit removes the old page's CSS from the CSSOM before clearing the DOM. Two-layer fix: (1) HTML `width`/`height` attributes on all Agy `<img>` elements in `ask_mattgpt_header.py` and `landing_view.py` prevent natural-size render without CSS constraints. (2) `mousedown`+`capture:true` JS listener in `navbar.py` sets `opacity:0` on avatar elements before React's synthetic `onClick` fires the Streamlit rerun — gives browser 50-200ms to commit the hide. Mobile hamburger `link.onclick` handlers got inline pre-hide logic before the `btn.click()` bridge. Global `agiAvatarReveal` fade-in animation in `global_styles.py` (0.15s ease-out, 0.15s delay) covers programmatic navigation paths where the mousedown listener doesn't fire.

**June 13 — Mobile header consistency — min-height floor + avatar alignment across 6 pages (MATTGPT-114)** — `9658e02`
Resolved via a min-height floor approach rather than the original shared-CSS-class plan. Added `min-height: 145.59px` to all purple header mobile blocks (`.conversation-header`, `.about-header`, `.ask-header-landing`, `.ask-header-conversation`) so all pages share a consistent header height regardless of content length. Fixed Banking and Cross-Industry page-level `min-height: auto !important` overrides that were blocking the global floor. Fixed CSS cascade in `ask_mattgpt_header.py` — moved `@media (max-width: 768px)` block after the global `.status-bar` reset so mobile `margin-top` wins. Aligned Ask Agy header to match `.conversation-header` structure (no negative margin bleed); inner flex gap `24px → 12px`. `about_matt.py`: `.about-header-avatar` class applied, badge absolutely positioned (`top: 50%; transform: translateY(-50%); right: 32px`), subtitle shortened, `deep-dive-card h3` `8px → 18px`. `global_styles.py`: avatar base rule, mobile badge hidden, orphaned duplicate avatar rules removed.

**June 13 — Home category cards — descriptive meta copy for all 6 cards (MATTGPT-108)** — `ff6c788`
Revised approach: replaced dynamic `{N} projects · {client list}` strings with static descriptive copy across all 6 cards. Original plan (add counts to the 4 non-industry cards) rejected as the wrong signal — counts were volume noise, not quality signal. Instead, Banking and Cross-Industry had their count/client strings replaced with capability-scoped descriptions matching the other four cards, achieving parity by subtracting rather than adding. One or two tight sentences per card, core message first. Removed now-unused computation variables (`banking_clients_inline`, `cross_industry_inline`, `cross_industry_stories` and upstream dependencies).

**June 12 — Story count copy — confirmed "130+" has no user-facing runtime references (MATTGPT-019)**
Audit confirmed zero user-facing `130+` references in active production code. All UI Python files already use `100+` or derive counts dynamically. Remaining `130+` occurrences are in dead code (`mobile_overrides.py` — never imported), design docs (`ARCHITECTURE.md`, `WIREFRAMES.md`), and `mattgpt_system_prompt.md` (not read at runtime). Ticket closed as resolved.

**June 9 — Bundle 1 CSS polish — back-link dark mode, How Agy scroll-to-top, stats label contrast (MATTGPT-111, -112, -069)** — `c8ce37d`
Three low-priority CSS/JS fixes shipped in one commit. Back-link breadcrumb pill (`explore_stories.py`): replaced hardcoded hex colors with CSS variables (`--bg-card`, `--accent-purple`, `--border-color`) — fixes white-pill-on-dark-background in dark mode (MATTGPT-111). How Agy Searches dialog (`how_agy_dialog.py`): scroll-to-top JS selector fixed from `[role="dialog"] > div` (overflow: visible, never scrolls) to `[role="dialog"]` (actual scrollable container, confirmed via DevTools); switched from fixed 100ms `setTimeout` to self-retrying IIFE (MATTGPT-112). Hero stats labels (`hero.py`): `var(--text-muted)` fails WCAG AA in both light (2.54:1) and dark (3.91:1) modes; swapped to `var(--text-secondary)` which passes in both (4.83:1 light, 7.44:1 dark), confirmed via DevTools CSSOM (MATTGPT-069).

**June 10 — Consolidate CSS to global_styles.py; fix rerun regression (MATTGPT-105)** — `191032b`
All `st.markdown()` CSS injections across `footer.py`, `thinking_indicator.py`, `timeline_view.py`, `story_detail.py`, and `explore_stories.py` relocated to `global_styles.py` with `es-*` HTML class namespace. Eliminates the rerun garbage-collection bug where inline `<style>` blocks injected inside render functions were stripped from the DOM during Streamlit's mid-rerun pause. Also fixed a live production JS bug: the delegated click listener in `explore_stories.py` was still targeting `.fixed-height-card` after the HTML rename, silently breaking card clicks in Cards view. BDD selectors updated across 7 step-def files to match renamed HTML classes.


### Ask Agy

**June 13 — Ask Agy landing — mobile chip grid redesign + dialog fixes (MATTGPT-113)** — `ff175e9`, `b7f88d5`
Mobile seed question chips redesigned as pill-shaped flex-wrap chips with short labels. Python mobile branch skips `st.columns()` on mobile (eliminates the stHorizontalBlock nuclear CSS rule conflict); desktop keeps 2-column grid with full questions. 3-tuples `(icon, short_label, full_question)` added to each chip. CSS: `.st-key-chip_grid` flex-wrap container with doubled-class specificity trick to beat global `stVerticalBlock gap: 4px` rule. Header height absolute-positioning fix shipped in `e7e079a`. Bonus fixes: Implementation Details grid (`details-grid`) single-column collapse on mobile corrected (two `1fr` rules → `repeat(2, 1fr)`); `deep-dive-card h3` font-size typo `8px` → `18px`.

**June 10 — How Agy dialog — mobile height compaction + stMain scroll reset (MATTGPT-110 follow-up)** — `8f9a1b5`, `be2872e`
Mobile viewport fix for the How Agy Searches dialog. CSS compaction across 5 selectors inside `@media (max-width: 640px)` in `_CSS` — `.search-card`, `.result-card`, `.result-wrapper`, `.cards-row`, `.pipeline-summary` padding/margin reductions totaling ~96px savings, bringing content from ~968px to ~872px against a ~595px usable area (Sections 1–2 fully visible on open; Section 3 reachable with one scroll). Scroll-to-top fix: `stMain.scrollTop = 0` added alongside existing `el.scrollTop = 0` in the scroll IIFE — `[data-testid="stMain"]` is Streamlit's real scroll container (confirmed via Chrome Claude DevTools; `window.scrollY` is always 0 under Streamlit's full-viewport flex layout). BDD regression guard: 2 scenarios covering scroll-to-top behavior added and passing.

**June 2 — How Agy Searches — migrate inline expander to `@st.dialog`, remove Technical Details block (MATTGPT-110)** — `37806a7`, `e24c1cb`
Replaced the inline collapsible expander on Ask Agy (Landing + Conversation views) with a `@st.dialog` overlay. Technical Details block removed — near-verbatim build content already covered in How I Built, sitting inside the runtime trust story where it didn't belong. Button label toggle and close-wiring JS removed from `ask_mattgpt_header.py`; `@st.dialog`'s built-in X / Escape / backdrop handles close. Bridge link added at bottom: "Want the technical details? See how I built it →". `show_how_modal` session state key and `render_modal_wrapper_start/end()` calls removed from both page files. BDD: 5/5 passing. CSS regression guards for navbar scope added in follow-up commit `e24c1cb`.

### Role Match

**June 2026 — Role Match sample JD cold-start affordance (MATTGPT-066)** — `6c39d8c`
Bundled with MATTGPT-067. See MATTGPT-067 entry below for full details — "Sample JD affordance" in the input controls section covers this ticket's scope.

**June 11–12 — Result panel + input polish bundle (MATTGPT-067)** — `6c39d8c`, `ac3d3dd`, `a2d002b`
Input controls: 30-word gate disables submit until sufficient JD text; Clear button (text link) empties textarea and pops all 5 session-state keys; Sample JD affordance ("Don't have a job description handy? / Try an example"). Summary block between legend and requirements: counts line (Required / Preferred tallies) + Discussion points (required gaps + partials + preferred gaps; preferred partials excluded). Legend relabeled "project evidence" / "verified skill"; card copy updated to "Verified skill" throughout. Post-result CTA copy changed to "Explore Matt's experience in depth." — honest framing that doesn't imply Agy has result context. UI fixes: right-column height anchor (`height_anchor = st.empty()`) prevents layout collapse during blocking LLM call; followup CTA gap rule scoped to `role_match_followup_block` container (was collapsing all inter-card gaps when results showed); `role_match_ev_*` expansion container gets 16px bottom margin to prevent overlay on next requirement card. BDD: 23/23 passing. Unit: 30/30 (`test_summary_block.py`).

### Explore Stories

**June 9 — My Work two-row permanent filter bar (MATTGPT-065)** — `765c14e`, `3015942`
Added a permanent two-row filter bar to My Work desktop. Row 1: Search / Industry / Capability. Row 2: Client / Role / Domain + Reset (always visible on desktop, CSS-hidden on mobile). `st.container(key="r2_row")` with border-top separator. `label_visibility="collapsed"` alone insufficient (label still takes vertical space) — Row 2 labels hidden via CSS as well. Mobile counterpart filed as MATTGPT-119.

**June 18 — AG Grid Client badge rendering — cellRenderer rewrite + Enterprise bundle drop (MATTGPT-132)** — `a809c57`
Fixed the AgGrid Client column badge in My Work Table view. Root cause: function-based `cellRenderer` fails in the st_aggrid React stack — the reconciler replaces the return value on rerender, losing the DOM node. Fix: class-based `ClientBadgeRenderer` using AG Grid 29's `init(params)` / `getGui()` contract, which returns the DOM element directly and bypasses React's reconciler. Also dropped `enable_enterprise_modules=False` to eliminate the license warning. Dark mode: Python-side detection via `st.get_option("theme.base")` passes hardcoded color values into `custom_css` at render time (CSS variables don't cross the AgGrid iframe boundary). Brief theme-toggle lag accepted as Streamlit architectural limitation.

**June 10 — AgGrid Table view — row cursor + purple hover color, dark-mode selector fix (MATTGPT-064)** — `3a5e1bc`, `6590450`
Two-part fix for AgGrid Table view styling. Root cause: CSS rules in `global_styles.py` cannot reach AgGrid's iframe — the iframe boundary blocks parent-doc stylesheets. Fix 1: Python `rowStyle = {"cursor": "pointer"}` on `GridOptionsBuilder` (bypasses iframe entirely). Fix 2: `components.html` JS injection reaching into `iframe.contentDocument` to set `--ag-row-hover-color: rgba(167,139,250,0.15)` and `--ag-selected-row-background-color: rgba(167,139,250,0.2)`. Dark-mode fix: guard selector changed from `.ag-theme-streamlit` (null in dark mode — actual class is `.ag-theme-streamlit-dark`) to `.ag-root-wrapper` (theme-agnostic). Three-fire timing pattern (immediate + 500ms + 1500ms) covers iframe load delay and post-rerun iframe recreation. Dead CSS removed from `global_styles.py`. Pattern documented in ARCHITECTURE.md as Pattern 5.

**June 10 — Retire how_i_built.py standalone route (MATTGPT-116)** — `9a55fbd`
Deleted `ui/pages/how_i_built.py` (standalone deep-link page fully superseded by `how_i_built_dialog.py`). Removed `?route=how-i-built` handler and `elif "How I Built"` render block from `app.py`; cleaned up `how_i_built_from` / `_deeplink_route` session state pops from `?nav=` handler. Removed 3 standalone-route BDD scenarios from `how_i_built.feature`; 5 dialog scenarios retained and passing. Items 2+3 (failing `test_desktop_shows_full_interface` + two-file revert) resolved as no-op — revert prescription was wrong; `window.innerWidth` + `screen_size_capture` approach is correct and test passes cleanly with current code.

**June 10 — My Work mobile — filter layout compaction (MATTGPT-123)** — `40aeb8e`
CSS-only changes to `global_styles.py`. Industry and Capability filters: label + dropdown inline on one row (`flex-direction: row` on the selectbox). Client/Role/Domain Row 2: 3-column grid, Streamlit labels hidden (`display: none`), field names injected via `::before` pseudo-element on the select control with `overflow: hidden` to suppress stray SVG title text. Reset filters button demoted to borderless underlined text link. Filters toggle made full-width via `stLayoutWrapper` + `stElementContainer` + `stButton` chain. Column stacker gained 5th `:not(:has([class*="st-key-r2_client_v2"]))` exclusion to preserve the 3-col grid. Search button alignment: `align-items: center` on stForm horizontal block, `gap: 0` on submit button column's vertical block, `margin-top: 3px` on `stForm`. stForm `align-items` split from `r2_row` rule (stForm → center; r2_row → flex-end). 4/4 BDD scenarios passing.

**June 10 — My Work mobile — "Filters ▾" toggle for Row 2 (Client, Role, Domain) (MATTGPT-119)** — `b65900e`
Added a "Filters ▾" toggle button to My Work, visible only on mobile (hidden on desktop via CSS). Tapping it toggles Row 2 visibility (Client, Role, Domain dropdowns) via `es_mobile_r2_open` session state; container key swap (`r2_row` ↔ `r2_row_open`) drives CSS show/hide without widget state loss. Required three CSS cascade fixes: (1) column-stacker rule gained 4th `:not(:has([data-testid="stFormSubmitButton"]))` exclusion — specificity (0,3,1) was overriding the stForm `flex-direction: row !important` rule; (2) facet rule gained same exclusion to prevent `flex-wrap: wrap` applying to the search form; (3) `[data-testid="stForm"] [data-testid="stColumn"]:last-child` rule added to block Streamlit's `min-width: calc(100% - 1.5rem)` from squeezing the submit button. BDD: 4/4 new scenarios passing, 2 regression guards confirmed.

---

## May 2026

### RAG Pipeline

**May 18 — Remove last_primary_client cross-query session state (MATTGPT-073)** — `3773c6b`
Option E applied. Removed `_last_primary_client` from `diversify_results` in `backend_service.py`. The mechanism stored the previous query's pinned client in session state and used it to demote stories on subsequent queries — making retrieval output for query N dependent on queries 1…N-1. Production log analysis (82 queries, 24 sessions) showed 45% of consecutive pairs were demotion-eligible. Post-removal eval: 70/70 (100%). Architectural decision recorded as ADR 019.

**May 18 — MattGPT portfolio story contamination in leadership queries resolved (MATTGPT-061)** — `02f6c79`
The dominant contamination mechanism — session-state demotion in MATTGPT-073 — removed. Validated against 12 production-traffic leadership queries: 11/12 clean responses (91.7%). 61-query eval suite 100% passing. Single residual failure (Q2 "transformations" polysemy) is a structural semantic search limit scoped to hybrid retrieval (see BACKLOG).

### Ask Agy

**May 25 — Nonsense rejection banner — branch-aware copy + contextual chip sets (MATTGPT-071)** — `c642575`
Differentiated copy and chip sets across all four reason branches in `render_no_match_banner`. Each rejection reason (rule:*, personal, out_of_scope) gets contextually appropriate copy and chips rather than a uniform fallback. Production-validated May 26: all branches render correct copy on both Ask Agy and My Work surfaces.

### UI Redesign Sprint

**May 27 — About Matt content polish bundle (MATTGPT-068)** — `efd6e00`
Sample questions converted from `<li>` text to `st.button` chips routing to Ask Agy via `seed_prompt` + `__ask_from_suggestion__` pattern. Code block wrapped in `<details><summary>` expander (collapsed by default). DevOps card merged into CI/CD Pipeline card. CTA card rendered as `st.container(key="about_matt_cta_card")` for true DOM nesting of chip buttons. BDD: Red/Red/Green cycle completed.

**May 29-30 — Home hero CTA inversion + seniority signal (MATTGPT-087 + MATTGPT-092)** — `ef133b2`
Role Match promoted to primary hero CTA; Ask Agy demoted to secondary. Explore Stories CTA removed from hero (reached via nav). Recruiter persona finding: Role Match was invisible when Ask Agy was primary. Seniority signal added to My Profile as a "LEVEL: Senior leader" signals panel — scope/outcome anchor, not a title chip, to avoid the title trap.

**May 29 — Explore Stories default state: exclude Professional Narrative + sort by date (MATTGPT-098)** — `856c908`
On default load, exclude Category == "Professional Narrative" (10 stories) and sort by Start_Date descending. Mirrors Timeline's EXCLUDED_ERA behavior. Behavioral stories remain reachable via Category filter. Applied to both Table and Cards views. Prerequisite for MATTGPT-104 math reconciliation.

**May 30 — Navigation labels rename (MATTGPT-100)** — `3c97d97`
Renamed tabs to: Home / My Work / Ask Agy / Role Match / My Profile. Updated across ~50 files: app.py tab definitions, navbar.py, session_state active_tab values, BDD fixtures, and landing page routing references. Mobile nav required separate handling (Streamlit transforms key spaces to dashes in CSS class names).

**May 30 — Why Agy? modal + "?" badge on Agy avatar (MATTGPT-101)** — `e1c2699`
New `why_agy_dialog.py` using `@st.dialog`. Badge wired across 7 surfaces: hero (Home), header + landing body (Ask Agy), banking header, cross-industry header, My Work header, Role Match header. Desktop-only in headers (30px mobile avatar too small); body/hero avatars show badge on all viewports. Sequential dialog pattern (`elif` not `if`) prevents StreamlitAPIException when Why Agy and How I Built open in sequence.

**May 30 — How I Built MattGPT dialog (MATTGPT-102)** — `b6ab8ae`
Replaced standalone `how_i_built.py` page with `@st.dialog` component. Removed `?route=how-i-built`, `?nav=`, `?from=` handlers from `app.py`; deleted standalone page; cleaned up `SECONDARY_SURFACES` and related session state keys. Content: subtitle, The Problem card, Tech Stack 6-item grid, System Architecture Flow (5-step lifecycle), Runtime Pipeline (numbered purple circles), Detail cards, CTA row.

**May 30 — Banking + Cross-Industry story count math reconciliation (MATTGPT-104)** — `19e03ba`
Landing hero/stats and Home card meta aligned to post-Era counts (32 Banking, 48 Cross-Industry), matching Timeline and My Work (post MATTGPT-098). Depended on MATTGPT-098 shipping first to establish post-Era as the cross-surface convention.

**May 31 — Navbar desktop layout: brand-left + space-between (MATTGPT-106)** — `3c97d97`
Added MattGPT brand element to desktop navbar left. Layout changed from `justify-content: space-evenly` (5 nav items full-width) to `space-between` (brand left, 5 items right). Brings desktop into structural alignment with mobile navbar and wireframe.

**May 31 — Home category cards redesign: 3-column grid + unified card treatment (MATTGPT-107)** — `19e03ba`
Redesigned from 2-column to 3-column grid. Unified light-bg treatment across all 6 cards (purple gradient removed from Banking/Cross-Industry top cards). Compact content (~3 lines vs ~5). Card itself is click target — inline buttons and italic example-question lines removed.

### Documentation Alignment

**May 11 — Align how_agy_modal + about_matt pipeline depictions to current code (MATTGPT-057)** — `ee730de`, `ec351a3`, `9a0c0e8`
Replaced stale architecture descriptions in user-facing pages with the current 5-stage pipeline shape (nonsense filters → semantic router → Pinecone → confidence gate → LLM). Dropped factually-false claims: "Semantic + keyword hybrid scoring" (W_KW = 0.0; pipeline is pure semantic), "GitHub Actions / CI/CD pipeline" (no CI exists — see MATTGPT-039), and unverified "6 Industries" stat. Touched `ui/pages/about_matt.py` "How I Built MattGPT" pseudocode, `ui/components/how_agy_modal.py` 3-stage framing expanded to 5-stage. Follow-up commits restyled the modal (pipeline as hero, demoted result pills) and stripped emojis from about_matt + footer for visual weight on deep-dive cards.

### Triage Agent (Cowork-orchestrated JD triage — new)

**May 10 — Initial scaffold for Cowork-orchestrated JD triage**
Enables Cowork (Claude Desktop) to drive JD triage against the existing engine by exposing it as a CLI surface and putting orchestration assets in version control as source of truth. `scripts/assess_jd.py` wraps `run_assessment()` + `compute_recommendation()` from `services/jd_assessor.py`, reads JD from stdin, and emits a schema-versioned JSON envelope; self-bootstraps `sys.path` so it works regardless of invocation context (subprocess, Cowork shell, pytest). `agent/triage/synthesis_prompt.md` carries the three-layer assessment logic (capability + filter + thin fit) with Pass-mode voice for high-volume discovery readiness; `agent/triage/filter_config.json` encodes Matt's hard rules (geographic, comp) + redline phrases. `agent/README.md` documents the layout and the Cowork setup checklist. `agent/discovery/` reserved as a placeholder for v2 ATS-based push-model discovery. `tests/unit/test_assess_jd.py` covers three contract surfaces: empty stdin (error JSON), missing JSONL (graceful error JSON), and valid-JD envelope shape (engine mocked in-process via `unittest.mock`). Architecture follow-up to update `mattgpt-design-spec/architecture.md` pending separately.

### Infrastructure

**May 6 — Reduce log noise on Streamlit Cloud (file watcher → poll)**
Streamlit's default watchdog (inotify) file watcher exhausted the kernel's per-host inotify instance limit on Streamlit Cloud's multi-tenant VMs, spamming the production log with non-fatal `OSError: [Errno 24] inotify instance limit reached` tracebacks (one per watched directory). Added `.streamlit/config.toml` with `fileWatcherType = "poll"` — no inotify overhead on Cloud (which never benefited from file watching anyway, since deploys come from git push), and the "Source file changed" toast still fires locally via polling. `"none"` rejected because it would silently disable the local toast.

### Role Match (Phase 4 in flight — see MATTGPT-012)

**May 4 — Committed 20 BDD scenarios for Role Match Phase 4** — `0d6285b`
Design contract for the private view: password gate edge cases, lock icon affordances, session persistence, agentic bypass (`X-Mattgpt-Bypass-Token` / `MATTGPT_PRIVATE_BYPASS_TOKEN`), recommendation matrix anchored to `compute_recommendation()` in `services/jd_assessor.py`, and locked↔unlocked transitions. Implementation deferred to a future session — step definitions co-author with implementation slices per CLAUDE.md testing protocol.

---

## April 2026

### Process & Infrastructure

**Apr 28 — Fix Playwright sync/async clash in BDD test suite** — `c889ab2`
Both `test_explore_stories.py` and `test_role_match.py` defined their own session-scoped Playwright fixtures with their own `_playwright_instance` globals. Running them in the same pytest session caused the second `sync_playwright().start()` call to clash with the asyncio event loop already owned by the first. Moved shared fixtures to `tests/bdd/steps/conftest.py`. BDD suite went from 10 failures to 3 (remaining 3 are pre-existing).

**Apr 28 — Add commit/push separate-gates rule to CLAUDE.md** — `1a2902c`
Replaced the previous "never push without confirmation" rule with a more specific version: commit and push are two separate gates requiring two separate approvals. Combining `git commit && git push` is not acceptable. Includes April 2026 incident reference.

### Role Match Feature (Phases 1-3 Complete)

**Apr — Role Match logging — assessment, chip click, and action button events** — `a3b3d84`
**Apr — BDD scenarios for Role Match logging (14 scenarios)** — `0dd2ee9`
**Apr — Fix AgGrid compatibility with Streamlit 1.50.0** — `fca174d`
Pre-import components submodule.

**Apr — Fix story detail STAR section spacing inside Role Match inline expansion** — `99053ee`
**Apr — Fix Role Match textarea persistence across page navigation** — `8386d8d`
Option A prefilter pattern.

**Apr — Improve JD extraction** — `455cac3`
Narrative prose mining, implicit requirements consumption, strong-without-evidence enforcement, explicit-bullet protection.

**Apr — Rebuild Role Match results panel — v3 design + Report button + UTM attribution** — `5e01460`
**Apr — Update Role Match BDD scenarios for mockup v2 design lock** — `211d04a`
**Apr — Fix Role Match chip toggle bug** — `c81dc35`
Refactor from JS bridge to `st.button` pattern. Roughly 100 lines of JS bridge code eliminated.

**Apr — Update Role Match mobile gate threshold from 768px to 1024px** — `f033c64`
Update BDD scenario wording.

**Apr — Add show_actions kwarg to render_story_detail** — `f6b1f71`
Default True, backwards compatible.

**Apr — BDD scenarios for Role Match story chip inline expansion (6 scenarios)** — `80024de`
**Apr — Fix navbar/hero gap regression caused by extra st.markdown call** — `af09041`
Documented layout spacing rule in CLAUDE.md.

**Apr — Phase 3 checkpoint: action buttons, share/export, BDD step definitions** — `9da8b59`
**Apr — BDD scenarios for Role Match action buttons (6 scenarios)** — `37786bb`
**Apr — Add Role Match page with recruiter view and pipeline wiring** — `9aec1a3`
**Apr — Promote JD pipeline functions into services/jd_assessor.py** — `119441d`
**Apr — BDD scenarios for Role Match page (27 scenarios)** — `043e6ba`
**Apr — Distinguish required vs preferred gaps in recommendation logic** — `8a6b203`
**Apr — Add matt_profile.json, dynamic grounding, evidence_type, entity aliases** — `8e24799`
**Apr — Add JD assessment prompt v1, BDD scenarios, and recommendation logic** — `7f3ddc0`

### Analytics — Logger Schema Extension (MATTGPT-013 Complete)

**Apr — 32-column query logger schema shipped to production** — `a3b3d84` and subsequent commits
Expanded `services/query_logger.py` from initial implementation to full 32-column schema. Captures event types (query, feedback, redirect, role_match_assessment, role_match_chip_click, role_match_action), query metadata (intent family, confidence, result count), user/session signals (user-agent, screen width, timezone, referrer), UTM attribution (source, medium, campaign, content, term), Role Match outcomes (role title, company, JD format, required/preferred/strong/partial/gap counts, session ID, story title, client), and feedback ratings. Write-only to Google Sheets. Downstream analytics work tracked separately (MATTGPT-045 dashboard, MATTGPT-046 latency, MATTGPT-047 cost tracking).

### Other April Work

**Apr — Add Chrome/103.0.0.0 stale bot UA to MONITORING_BOT_SIGNATURES** — `cfe1704`
**Apr — Add HeadlessChrome to MONITORING_BOT_SIGNATURES** — `2f42057`
**Apr — Add dark mode override for thinking indicator backdrop opacity (0.4 → 0.6)** — `a07ab06`
**Apr — Fix mobile gate false positive on Streamlit Cloud** — `dd4314d`
Use `screen.width` instead of `innerWidth`.

**Apr — Fix navbar column squishing caused by Explore Stories CSS leak** — `1a1e86e`
**Apr — Update wrong-person backlog: recommend Option 2 (canonical phrases)** — `63eb7f2`
**Apr — Fix 2 test bugs, update sacred vocabulary, backlog 6 code bugs** — `66818d7`

---

## March 2026

### Data Quality

**Mar — diversify_results Pinning Fix**
`diversify_results()` was reordering stories and displacing the primary story (e.g., D&F query: Row 40 ranked #1 but LLM talked about Row 28/AmEx). Fixed pinning logic so primary story stays #1 after diversification.

**Mar — IQ Differentiation (Leadership + CIC)**
Leadership and CIC stories lacked differentiation in Situation/Use Case fields — Pinecone couldn't distinguish them. Data quality pass on Excel master enriched Situation fields with resistance narratives and specific context.

**Mar — TDD/BDD Story Rewrite**
TDD methodology story had weak Situation field, BDD story surfacing instead for TDD queries. Rewrote Situation with resistance narrative, re-ingested data.

### RAG & Voice

**Mar — CIC Entity Alias**
"CIC" acronym not recognized by entity detector. Added `ENTITY_ALIASES` to `config/constants.py`, alias check in `detect_entity()`. "CIC" now resolves to Division: Cloud Innovation Center.

**Mar — SYNTHESIS_DELTA Reconciliation**
Rewrote with tension-first flow (WHY 30-40%, HOW 40-50%, WHAT 10-20%), coverage rule changed to "lead with 2-3 most relevant, don't force-fit."

**Mar — Voice Guide V2 Update**
Reconciled WHY=tension/stakes across `05-agy-voice-guide.md`, `prompts.py`, `ARCHITECTURE.md`.

### Eval & Code

**Mar — Eval Cases for "Tell me more about: [Title]"** (legacy #2)
Q53-Q57 added as regression guards covering title-based and entity-based queries. Title soft-filtering working correctly.

**Mar — Delete META_SENTENCE_PATTERNS Regex** (legacy #5)
Band-aid for prompt conflict; monitoring period complete. Prompt rewrite eliminated the root cause.

**Mar — Remove boost_narrative_matches()** (legacy #6)
Title now embedded in Pinecone. Semantic search handles narrative story ranking naturally.

**Mar — Centralize Hardcoded Values** (legacy #7)
Thresholds, model names, token limits scattered across 6+ files. `config/constants.py` created as single source of truth.

**Mar — Pinecone Index as Env Var** (legacy #18)
`index_name="portfolio-stories"` was hardcoded. Moved to environment variable via `get_conf()` pattern.

**Mar — Fix "Builder/Modernizer" Verbatim Quoting** (legacy #30)
Agy was quoting poetic language from 5PSummary verbatim in synthesis responses. Data fix — updated 5PSummary to concrete language in Excel master, re-indexed.

**Mar — New Development Stories** (legacy #31-35)
5 stories added in Feb 3 session. 130 stories total.

**Mar — Dead Code Cleanup (Partial)** (legacy #8)
Initial sweep complete. Remaining work tracked in BACKLOG.

---

## February 2026

**Feb — Excel→JSONL Script Bug Fixes** (legacy #38)
Fixed `normalize()` for pandas NaN, `split_bullets()` for Excel escape apostrophe.

**Feb 3 — New MattGPT Development Stories** (legacy #39)
Added 5 stories: Why Hire Matt, Entity Gate Removal, Eval-Driven Development, BDD, AI-Assisted Workflows. 130 total.

**Feb — Design Spec Testing Docs Consolidation** (legacy #40)
Consolidated into `docs/11-testing-and-quality.md` covering 3-layer strategy.

**Feb 1 — Stale Story on Return to Explore Stories** (legacy #23)
Widget version incrementing in `_clear_explore_state()`.

**Feb 1-2 — BDD/E2E Tests for Explore Stories State Machine** (legacy #25)
43 BDD scenarios using pytest-bdd + Playwright. All passing.

---

## January 2026

### RAG Pipeline Cleanup (Jan 29)
- Entity Gate removed (was causing false rejections)
- `classify_query_intent` LLM removed (redundant with semantic router)
- Eval improved from 96.4% to 98.1%

### Individual Items

**Jan 22 — Multi-Field Entity Blind Spot** (Sovereign Backlog #1)
Entity filter now searches 6 fields with Pinecone `$or` operator.

**Jan 22 — Dynamic Prompting** (Sovereign Backlog #3)
`generate_dynamic_dna()` derives clients by industry from story data.

**Jan 22 — UI Metrics Hydration**
All project/client counts derived dynamically from JSONL across 4 files.

**Jan 26 — Fix Prompt Conflict** (legacy #1)
Created `prompts.py` with BASE_PROMPT + DELTA architecture. Meta-commentary failures reduced from 10/31 → 1-2/31.

**Jan 26 — Semantic Router Fail-Open Handling** (legacy #9)
Verified fail-open behavior: returns `(True, 1.0, "", "error_fallback")` on exception.

**Jan 26 — Threshold Calibration** (legacy #10)
Lowered SOFT_ACCEPT from 0.72 to 0.40. Entity Gate removed entirely Jan 29.

**Jan 26 — Remove ENTITY_NORMALIZATION Hardcoded Map** (legacy #11)
Semantic search handles variations naturally. Removed map and fuzzy matching.

**Jan 26 — Add Observability Logging** (legacy #12)
Added `[QUERY_REJECTED]` and `[API_ERROR_DETECTED]` log tags.

**Jan 28 — Audit Excel Master for Corporate Filler** (legacy #4)
Deleted BANNED_PHRASES entirely — was testing for imaginary problems.

**Jan 30 — Fix SEARCH_TOP_K Conflict** (legacy #14)
Centralized to `config/constants.py` with value 10.

**Jan 30 — Deeplink Regression** (legacy #20)
Fixed page offset calculation for story deeplinks.

**Jan 30 — Search State Clearing** (legacy #21)
Surgical fix: only clear `active_story` when query actually changes.

**Jan 30 — "Ask Agy About This" Regression** (legacy #22)
Fixed by surgical state clearing in legacy #21.

**Jan 31 — 6 Sources on Surgical Queries** (legacy #24)
Added `query_intent` check: synthesis gets 6 sources, surgical gets 3.
