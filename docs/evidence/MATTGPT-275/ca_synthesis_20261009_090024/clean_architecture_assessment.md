# Synthesis: Clean Architecture assessment

Read-only assessment of the synthesis answer path. No code was changed.

**Source state:** HEAD `d65fdc5` (no `ui/`, `services/` or `config/` changes since `3d34e91`), plus the uncommitted working tree in `config/constants.py`, `ui/pages/ask_mattgpt/backend_service.py` and `ui/pages/ask_mattgpt/prompts.py`. Those changes route `send_to_backend()` to `agy_answer()` (tool loop). At HEAD, `send_to_backend()` calls `rag_answer()`. Both designs are assessed.

**Method:** source reads of `get_synthesis_stories()`, `sync_portfolio_metadata()`, `_generate_agy_response()`, `_choose_opening_and_focus()`, the synthesis branches in `rag_answer()`, `agy_answer()`, `build_system_prompt()`, `build_tool_system_prompt()`, `SYNTHESIS_DELTA`, `TOOL_SYNTHESIS_SHAPE`, and `_sources_layout()` in `conversation_helpers.py`. Plus the clean-architecture plugin's `ca_cycles` on the repo root: 0 cycles.

## Layer mapping

| Clean Architecture layer | What synthesis has |
|---|---|
| Entities | Nothing. Stories, themes and clients are plain dicts; "theme" is the string key `"Theme"`. |
| Use case | Spread across `rag_answer()`, `get_synthesis_stories()`, `_generate_agy_response()` and `agy_answer()`, all in `ui/pages/ask_mattgpt/backend_service.py`, under the UI folder. |
| Adapters | `prompts.py` (pure string building). `conversation_helpers._sources_layout()`. |
| Frameworks | Pinecone, OpenAI and Streamlit, called directly from the use case. |

## Findings, most important first

### 1. The synthesis decision is made in four places, and the UI can disagree with the backend

- `rag_answer()` sets `is_synthesis` from the router family, entity cluster promotion can set it to True, and the empty-ranked guard can set it back to False.
- `rag_answer()` writes the router family, not the final `is_synthesis`, to `st.session_state["__ask_query_intent__"]`. The UI reads that value back and recomputes `is_synthesis = msg_query_intent == "synthesis"` before calling `_sources_layout()`.
- **Result on HEAD:** an entity-cluster-promoted query (example shape: "what did Matt do at RBC") gets the synthesis prompt with up to 7 stories, but the UI applies `SOURCES_MAX_SURGICAL = 3` instead of `SOURCES_MAX_SYNTHESIS = 6`. The empty-ranked guard mismatches in the other direction. Not observed in a browser; derived from the code path.
- **Result in the working tree:** `agy_answer()` sets `__ask_query_intent__ = None`, so the UI's synthesis branch can never run.
- **Fix:** return one resolved `answer_mode` in the result dict and have the UI read only that.

### 2. Synthesis is a boolean checked in many functions, not one mode object

- `is_synthesis` is branched on in `_choose_opening_and_focus`, `_generate_agy_response`, `build_system_prompt`, `build_user_message`, `build_tool_system_prompt`, `build_answer_instructions`, `_build_sources` and `_sources_layout`. A third mode means editing every one.
- Settings typed more than once:
  - Story limit `7 if is_synthesis else 5` is hardcoded in `_generate_agy_response()`, while `LLM_STORY_LIMIT_SYNTHESIS` and `LLM_STORY_LIMIT_STANDARD` exist in the same file.
  - Temperature `0.2 if is_synthesis else 0.4` appears in both `_generate_agy_response()` and `agy_answer()`.
  - The rank cap `[:9]` and `top_per_theme=3` are written at the `rag_answer()` call site; the function default is 2.
  - Source caps 6 and 3 are separate constants in `conversation_helpers.py`.
- **Fix:** one `AnswerMode` value holding temperature, story limit, rank cap, per-theme count, opener pool, prompt section and source cap.

### 3. The synthesis logic calls Pinecone, OpenAI and Streamlit directly

- `get_synthesis_stories()` calls `_init_pinecone()`, `idx.query()` and `_embed()` itself, and parses both Pinecone match shapes (dict or object) inline.
- Embed failures are reported by setting `st.session_state["__embed_failure__"]`, which `rag_answer()` pops. Session state is acting as the error channel.
- Hypothesis, not measured: the per-theme search runs in a `ThreadPoolExecutor` and writes session state inside a bare `try/except: pass`. Worker threads without a Streamlit run context may fail that write silently. That path only runs when `query` is None, and `rag_answer()` always passes the question.
- `services/rag_service.py` and `services/pinecone_service.py` both `import streamlit as st`, so the framework also reaches the layer synthesis depends on.
- **Fix:** a small `StorySearch` interface (`search(vector, filters, top_k) -> list[ScoredStory]`) passed into the synthesis logic; failures returned as an exception or result object.

### 4. Setup order is enforced only by module globals

- `SYNTHESIS_THEMES` and `MATT_DNA` are module globals filled by `sync_portfolio_metadata()`.
- If it hasn't run, `get_synthesis_stories()` loops over `[]`, returns an empty pool, and the empty-ranked guard falls back to a non-synthesis answer. No error, and no log outside DEBUG.
- **Fix:** derive themes into a value that is passed in (or a cached loader), so a missing sync fails loudly.

### 5. Working tree: two near-copies of the synthesis prompt

- `SYNTHESIS_DELTA` and `TOOL_SYNTHESIS_SHAPE` repeat the WHY/HOW/WHAT percentages and the "Lead with the tension..." rules almost verbatim.
- On the tool path, synthesis is only a prompt shape plus a temperature. Theme-filtered retrieval, named-clients-first ranking and cluster promotion are not used. HEAD's retrieval code stays loaded and tested through `rag_answer()`.

### 6. Smaller issues

- **Filter casing:** `get_synthesis_stories()` builds one Pinecone filter mixing `"Theme"` (PascalCase) with a lowercase entity field. CLAUDE.md says metadata field names are lowercase. ARCHITECTURE.md already notes the `Theme` casing. Live index not checked.
- **Linear lookup:** each Pinecone match does a `next()` scan over the full corpus. An id-to-story dict built once would remove it.
- **Unfinished stub:** `_build_sources()` has returned `[]` since the MATTGPT-128 Red commit (`220d14d`) and has no production callers. Its tests in `tests/unit/test_backend_service.py` are xfail. The `LLM_STORY_LIMIT_*` constants exist only for it.

## What already works

- `prompts.py` is a real adapter: pure functions, no I/O, mode chosen by an argument.
- Themes and client lists are derived from the corpus, not hardcoded.
- `get_synthesis_stories()` has a clear output contract: annotated story copies (`_search_score`, `_matched_theme`), de-duplicated.
- No import cycles (`ca_cycles`).

## Suggested order

1. Resolve the mode once and return it in the result; the UI stops recomputing it. Fixes the source-card mismatch with the least code.
2. Collect mode settings in one `AnswerMode` constant.
3. Put Pinecone behind a search interface; report embed failures by return value or exception.

Open decision before any of these: whether HEAD's retrieval-based synthesis survives MATTGPT-275. If the tool path ships, findings 3 and 4 reduce to cleaning up or removing `get_synthesis_stories()`.
