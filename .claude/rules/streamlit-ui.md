---
paths:
  - "ui/**"
  - "app.py"
---

# Streamlit UI rules

## CSS Rules
1. **Scope mobile CSS:** use wrapper classes (`.explore-page`) or page-specific selectors.
2. **Never use generic selectors:** `div[data-testid="stColumn"]` leaks everywhere.
3. **Mobile changes go in `@media (max-width: 767px)` blocks:** don't touch desktop rules.
4. **Test at breakpoints:** 375px (iPhone SE), 767px (tablet boundary), 1024px+ (desktop). Mobile must not break desktop: check both after any CSS change.
5. **Never target Streamlit's dynamically-hashed class names:** `st-emotion-cache-*`, `.st-bz`, `.st-c0`, and any short `.st-XX` atomic classes change between builds and can migrate onto different DOM elements. Even "unmatched no-op" selectors are risky: they become active overrides the moment the hash drifts onto a new element. Target `data-testid`, `data-baseweb`, or `.st-key-*` instead. (Enforced on added lines in `ui/` and `app.py`.)
6. **Use existing CSS variables from `global_styles.py`:** `--accent-purple`, `--bg-card`, `--bg-surface`, `--text-primary`, `--text-secondary`, `--border-color`, `--hover-shadow`. Don't hardcode values that are CSS variables.
7. **Container keys for targeting:** `st.container(key="my_container")` then target `.st-key-my_container`.
8. **DevTools before any CSS proposal:** see Critical Rules in CLAUDE.md.
9. **Streamlit transforms spaces in `key=` to dashes in CSS class names:** `key="topnav_My Work"` produces `.st-key-topnav_My-Work`. Use the dash form in CSS/JS/BDD selectors.

## Session State & Widget Keys
- **Never modify a session state key after its widget renders:** causes `StreamlitAPIException`.
- **Use the prefilter pattern for cross-page navigation:**
  ```python
  # Source page (e.g., timeline_view.py):
  st.session_state["prefilter_role"] = role
  st.rerun()

  # Target page (e.g., explore_stories.py), BEFORE widgets render:
  if "prefilter_role" in st.session_state:
      F["role"] = st.session_state.pop("prefilter_role")
  ```
- **Check existing patterns first:** see `banking_landing.py` → `explore_stories.py`.

## HTML in Streamlit
- `st.markdown()` with complex nested HTML often renders as raw text: use single-line HTML strings.
- For interactive HTML, use `components.html()`: clicks require JS to trigger hidden `st.button()` elements.
- JS in iframes can't directly access the parent: use `window.parent.document` with a timeout for DOM readiness.

## Interactive Click Handling
Two proven patterns exist. Use them in this order.

**Pattern 1 (default): `st.button` + scoped CSS.** See `_render_ask_transcript()` in `ui/pages/ask_mattgpt/conversation_helpers.py`, the `"conversational"` message-type branch. Plain `st.button` with a `stable_key`, styled via CSS targeting `[class*="st-key-{stable_key}"] button`. No JS bridge. No hidden trigger. This is the right starting point for any clickable element.

**Pattern 2 (only when Pattern 1 can't meet the visual requirement): delegated `parentDoc` listener.** See `ui/pages/explore_stories.py`, Cards view rendering. Listener on `parentDoc`, not individual elements, so it survives React DOM reconciliation across reruns.

Do not build a third pattern without a documented reason why neither works.

## Markdown Call Count Affects Layout
Each `st.markdown()` call creates a DOM element. On pages using `.conversation-header`, the header's negative margin is tuned to a specific number of preceding markdown elements. Extra `st.markdown()` calls, even containing only `<style>` tags, break visual alignment. Consolidate CSS injections; place additional injections after hero content, before `render_footer()`. Browser CSS parsing is order-independent, so bottom-of-page injection is functionally equivalent.
