# MattGPT - Claude Working Agreement

## Critical Rules
Read these before every session. Each one has caused a real incident.

- **Read this entire file before proposing any edit to it.** Synthesize across all sections first. Do not add a section after reading two lines.
- **When a simple fix is visible while working in a file, fix it.** Do not defer trivial corrections under the pretense of scope management.
- **No em dashes anywhere in this repo.** Not in docs, not in commits, not in this file. Use a colon, comma, or rewrite the sentence.
- **Before citing a constraint as the reason for an approach, verify the constraint exists in the actual file.** Show the evidence. If the constraint doesn't exist, use the simplest direct substitution: f-string with the constant inline. (June 2026: .replace() pattern built for a CSS brace problem that affected 3 lines, not 4000.)
- **Push is a separate gate from commit, always.** `git push origin main` triggers a production deploy on Streamlit Cloud. A commit approval is not a push approval. Stop after committing and wait for an explicit "push" instruction. Never chain `git commit && git push`. (April 2026)
- **BDD scenarios before any implementation code, no exceptions.** First action on any ticket: write scenarios in `tests/bdd/features/` and bind them with `scenarios()` in `test_*.py`. Not logistics. Not split decisions. Scenarios first. (May 2026)
- **Paste literal test output at every gate, never self-summarize.** "Looks good, ready to commit?" is not a gate. Paste the literal `pytest` output before requesting commit approval at every Red and Green commit.
- **One "go" ships the full Red → Red → Green cycle.** After Matt says "go" on a ticket, run all three gates without re-asking between them. Re-ask only when a substantive new design decision surfaces mid-cycle.
- **Pre-flight before touching any existing file.** Name the files the ticket touches, the patterns those files use, any cross-surface couplings, and existing test coverage, before proposing anything. (June 2026)
- **Read existing patterns before building anything new.** Check `conversation_helpers.py` before any click handler. Check `banking_landing.py` before any cross-page navigation. Build on top; replace only when you can name in a comment why the existing pattern fails. (April 2026)
- **Stage specific files by name, never `git add -A` or `git add .`.** Parallel sessions share one staging area. (May 2026)
- **Never use `grep -v` to redact secrets.** Use positive include filters (keys only). Applies to `.streamlit/secrets.toml`, `.env`, any service-account JSON. (May 2026)
- **Artifacts for user review go in chat, not /tmp.** Edit tool calls show diffs inline. Writing to /tmp creates a local-only artifact Matt cannot see. (June 2026)
- **DevTools before any CSS proposal.** For any layout, alignment, positioning, sizing, color, or typography issue: ask Matt to paste computed styles from DevTools before proposing a fix. Source-code reasoning misses Streamlit's wrapper-layer surprises. (May 2026)
- **Unexpected test failures are your problem until proven otherwise.** When tests fail on code you touched, investigate before labeling anything pre-existing. Run the failures in isolation, read the output, and either fix them or produce evidence they existed before your change. "I didn't touch that code" is not evidence. Presenting options and waiting is not investigating.
- **Working notes do not replace BACKLOG tickets.** Any bug, regression, or unvalidated behavior written to a working note must also produce a BACKLOG entry before the session proceeds. A finding that only exists in `docs/working/` or a notes file has no owner and will not be acted on. "I noted it" is not the same as "it is tracked."

---

## Tech Stack
See [Design Specification](https://mcpugmire1.github.io/mattgpt-design-spec/) for the canonical tech stack and system architecture. Do not duplicate tech stack facts here.

Read `ARCHITECTURE.md` for full system context.

## File Structure
```
ui/pages/               # Page components
  explore_stories.py    # Story browsing with Table/Card/Timeline views
  ask_mattgpt/          # Modular chat interface (8 files)
    __init__.py         # Router
    landing_view.py     # Landing page with capability cards
    conversation_view.py # Chat conversation UI
    conversation_helpers.py # Message rendering, Related Projects UX
    backend_service.py  # RAG pipeline integration
    styles.py           # Chat-specific CSS
    story_intelligence.py # Theme/persona inference
    shared_state.py     # Session state management
    utils.py            # Shared utilities
  about_matt.py         # About page
  banking_landing.py    # Banking industry landing
  cross_industry_landing.py # Cross-industry landing

ui/components/          # Shared components
  timeline_view.py      # Era-based Timeline (5 career phases)
  story_detail.py       # Story detail modal
  how_agy_modal.py      # "How Agy Searches" modal
  how_i_built_dialog.py # "How I Built MattGPT" dialog
  ask_mattgpt_header.py # Unified header component
  category_cards.py     # Landing page capability cards
  thinking_indicator.py # Loading/processing indicator
  navbar.py             # Top navigation
  footer.py             # Footer

ui/styles/              # CSS
  global_styles.py      # Shared CSS + mobile breakpoints + CSS variables
  mobile_overrides.py   # Additional mobile CSS

services/               # Business logic
  rag_service.py        # Semantic search orchestration
  pinecone_service.py   # Vector database integration

utils/                  # Helpers
  filters.py, scoring.py, formatting.py, validation.py

config/                 # Settings
  debug.py, settings.py, constants.py

data/
  echo_star_stories_nlp.jsonl   # STAR story corpus (source of truth)
```

## Code Conventions
- Filter state lives in `st.session_state["filters"]`
- CSS variables defined in `global_styles.py` (use them, don't hardcode colors)
- Widget versioning pattern: `key=f"widget_name_v{version}"` for forced refreshes
- Use `safe_container()` wrapper for bordered sections
- Container keys for CSS targeting: `.st-key-{key_name}` selectors

## CSS Rules
1. **Scope mobile CSS** - use wrapper classes (`.explore-page`) or page-specific selectors
2. **Never use generic selectors** - `div[data-testid="stColumn"]` leaks everywhere
3. **Mobile changes go in `@media (max-width: 767px)` blocks** - don't touch desktop rules
4. **Test at breakpoints:** 375px (iPhone SE), 767px (tablet boundary), 1024px+ (desktop)
5. **Streamlit class names like `st-emotion-cache-*` change between versions** - target `data-testid` or `.st-key-*` instead
6. **Use existing CSS variables** - check `global_styles.py` for `--bg-card`, `--border-color`, `--text-primary`, `--accent-purple`, etc.
7. **Container keys for targeting** - `st.container(key="my_container")` then target `.st-key-my_container`
8. **DevTools before any CSS proposal** - see Critical Rules. Applies to layout, alignment, positioning, sizing, color, and typography.
9. **Streamlit transforms spaces in `key=` to dashes in CSS class names** - `key="topnav_My Work"` produces `.st-key-topnav_My-Work`. Use the dash form in CSS/JS/BDD selectors.

## Streamlit Patterns

### Session State & Widget Keys
- **Never modify a session state key after its widget renders** - causes `StreamlitAPIException`
- **Use prefilter pattern for cross-page navigation:**
  ```python
  # Source page (e.g., timeline_view.py):
  st.session_state["prefilter_role"] = role
  st.rerun()

  # Target page (e.g., explore_stories.py), BEFORE widgets render:
  if "prefilter_role" in st.session_state:
      F["role"] = st.session_state.pop("prefilter_role")
  ```
- **Check existing patterns first** - see `banking_landing.py` → `explore_stories.py`

### HTML in Streamlit
- **`st.markdown()` with complex nested HTML often renders as raw text** - use single-line HTML strings
- **For interactive HTML, use `components.html()`** - clicks require JS to trigger hidden `st.button()` elements
- **JS in iframes can't directly access parent** - use `window.parent.document` with timeout for DOM readiness

### Interactive Click Handling - Read This First
Two proven patterns exist. Use them in this order:

**Pattern 1 (default): `st.button` + scoped CSS**
See `ui/pages/ask_mattgpt/conversation_helpers.py` around line 626. Plain `st.button` styled via CSS targeting `[class*="st-key-{stable_key}"] button`. No JS bridge. No hidden trigger. This is the right starting point for any clickable element.

**Pattern 2 (when Pattern 1 genuinely can't meet the visual requirement): delegated `parentDoc` listener**
See `ui/pages/explore_stories.py`, Cards view rendering (~lines 2393-2487). Listener on `parentDoc`, not individual elements, so it survives React DOM reconciliation across reruns.

Do not build a third pattern without a documented reason why neither of these works. April 2026: ~100 lines of JS bridge code were written and then abandoned when switching to Pattern 1 fixed the problem.

### Streamlit Markdown Call Count Affects Layout
Each `st.markdown()` call creates a DOM element. On pages using `.conversation-header`, the negative margin (`-3rem`) is tuned to a specific number of preceding markdown elements. Extra `st.markdown()` calls, even containing only `<style>` tags, break visual alignment. Consolidate CSS injections; place additional injections after hero content, before `render_footer()`. Browser CSS parsing is order-independent so bottom-of-page injection is functionally equivalent.

## Behavioral Rules

### Before starting any ticket
1. **Pre-flight** (see Critical Rules) - name the files, patterns, couplings, and test coverage
2. **Pre-implementation reasoning gate** - before proposing any implementation, state in one sentence what the current code does, one sentence what the change does, and one sentence why it's better than the simplest alternative. If that third sentence can't be written confidently, stop and ask. Do not default to the more complex approach.
3. **Default is build-on-top-of, not replace-with** - extend the existing pattern; only propose replacing when you can name in a comment why it fails
4. **BDD scenarios first** (see Testing Protocol)

### During implementation
- Give direct solutions immediately after pre-flight
- Backup before modifying: `cp file.py file.py.bak`
- Keep reference docs/comments when rewriting files
- Do not make changes outside the requested scope
- Do not add dependencies without flagging it
- Do not hardcode values that are already CSS variables
- Do not invent new patterns when existing ones work

### On specs and wireframes
- **Cross-check the artifact, not just the verbal scope.** When a wireframe/spec AND verbal scope are given, the artifact is truth on copy/structure/sizing. Match it exactly or flag the conflict explicitly. (May 2026)
- **Visual spacing: give baseline + lever, let Matt call the value.** For margins/gaps/padding, name the controlling rule + `file:line`, suggest a starting point, let Matt eyeball and call the final value. (May 2026)

### On estimates
- **Headline number = raw implementation time only.** BDD overhead and discovery risk are listed as explicit add-ons, not folded into the headline. A 30-min change is quoted as 30 min, not "2-3 hours."

### On debugging and diagnosis
- **A repeated, specific, concrete observation is a constraint the diagnosis must satisfy, not an anecdote to explain away.** When instrument data and a consistent human observation conflict, the observation usually means the instrument is measuring the wrong thing, not that the observation is noise.
- **"The framework" is not a stopping point.** Framework-internal is often partly true and always unactionable. Keep going until the explanation accounts for the specific named symptom, which always lands somewhere project-side.
- **When Matt names a specific thing, verify you are looking at exactly that thing before reasoning about it.** Anchor to the named element, component, or behavior and confirm it before theorizing. Reasoning about the wrong frame is not diagnosis.
- **This is not a rule about deference.** Wrong theories get killed with evidence regardless of whose they are. The rule is about how to treat a specific class of input: a repeated, named, concrete symptom is a falsification test, not color commentary.

### Parallel sessions
When multiple Claude Code sessions run concurrently, they share one git working tree and one staging area.
- Stage specific files by name (see Critical Rules)
- Check `git status` before staging to see what the other session has modified
- Coordinate commit timing: Session A stages → commits → reports SHA → Session B stages → commits
- For true parallelism: `git worktree add ../project-branchname`

## Testing Protocol

**The non-negotiable:** BDD scenarios are written and committed before any implementation code. No exceptions. If a spec is provided, scenarios come first.

### Red-Green cycle
One "go" from Matt ships the full cycle without re-asking between gates. Re-ask only on substantive new design decisions.

- **Red (scenarios commit):** Write scenarios in `tests/bdd/features/X.feature` AND bind via `scenarios("../features/X.feature")` in `tests/bdd/steps/test_X.py`. Run `pytest tests/bdd/steps/test_X.py -v`, confirm all scenarios discovered and all in undefined-step state. Commit message proof: `Red (scenarios): N scenarios discovered, all N undefined-step.`
- **Red (step defs commit):** Write step definitions. Confirm scenarios run end-to-end and fail with assertion errors (not undefined-step or import errors). Commit message proof: `Red (step defs): N scenarios bound, N assertion failures, 0 undefined-step / import errors.`
- **Green (production code commit):** Write minimum production code to pass. Confirm all pass. Commit message proof: `Green: N / N scenarios passing.`
- **Refactor (optional):** Clean up while keeping tests passing.

### Validation rules
- **Paste literal pytest output at every gate** - never self-summarize (see Critical Rules)
- **Scope per-gate runs to the relevant test file** - `pytest tests/bdd/steps/test_X.py -v`, not the full suite
- **A `.feature` file without its `test_*.py` binding is documentation, not a test**
- **BDD scenarios must assert DOM-observable behavior** - Playwright cannot read `st.session_state`; assert navigation visible + user-message echo + assistant-response streaming
- **After any change to UI files, restart Streamlit before running BDD tests**
- **After any change to `explore_stories.py`, run the BDD suite before presenting for review**
- **On a second Playwright selector timeout, screenshot before iterating:**
  ```python
  try:
      option.click(timeout=5000)
  except Exception:
      browser_page.screenshot(path='/tmp/pw_debug_selector.png')
      raise
  ```
- **Eval failure discipline:** Any eval failure must be validated against production before being labeled "pre-existing" or "stochastic." If a "known issue" isn't in BACKLOG, it's an unvalidated note.

### Canvas-Rendered Grids (st.dataframe) - BDD Constraints

`st.dataframe` renders rows, cells, column headers, and selection controls to an HTML canvas, not the DOM. Full explanation, verified selectors, and origin: see `ARCHITECTURE.md` (st.dataframe canvas constraint). (MATTGPT-144)

**CAN assert:** grid mounted (`[data-testid="stDataFrame"]` + `[data-testid="data-grid-canvas"]`, waiting explicitly for canvas paint); filter pipeline worked (count direction from `.es-results-count`); detail pipeline worked (deeplink `?story=id` then assert `.es-detail-header`).

**CANNOT assert, ever:** row content, visual row rendering, canvas-driven row selection. A green BDD suite does not prove the grid painted its rows. Visual row-rendering correctness is manual visual check, not optional.

Any new `st.dataframe` surface inherits all of the above. If whole-row-click or keyboard row selection is a hard requirement, use self-rendered HTML rows (the Cards pattern).

## Secrets & Sensitive Output Handling
Three rules from a real GCP private key exposure (May 2026):

1. **Never use `grep -v` to redact secrets** (see Critical Rules). Use positive include filters:
   - `grep -oE "^[A-Z_][A-Z_0-9]*" .env` - key names only
   - `grep -oE "^[a-z_]+ ?=" secrets.toml` - top-level scalar keys only
2. **When inspecting any secrets file, extract keys-only by default.** Ask Matt to confirm values rather than printing them.
3. **Hard-cap output for any command touching a secrets file** - pipe to `| head -20`.

Applies to: `.streamlit/secrets.toml`, `.env`, `.env.local`, any service-account JSON, any file matching `*secret*` / `*credential*` / `*token*`.

## Pre-Commit Doc Checklist
Before committing, answer for each:
- **ARCHITECTURE.md** - Does this change a pattern, surface, or fact stated here?
- **mattgpt-design-spec** (Jekyll repo) - Does this change anything in the user-facing spec?
- **how_agy_modal.py** - Does this change anything described in the Ask MattGPT architecture exposition?
- **about_matt.py** - Does this change anything described in the "How I Built MattGPT" section?

If yes to any: the doc-update commit pairs with this code commit. Same session, same push. Not a follow-up.

Always triggers this check:
- New file in `services/`, `ui/pages/`, `utils/`, or `config/`
- Model, embedding, or vector store change
- Pipeline stage added/removed/renamed
- Schema change in story corpus, query logger, or any `config_*.json`

## Backlog Maintenance

### Status Enum
Six values only. Do not invent others.

| Status | Meaning |
|--------|---------|
| Open | Not started, no blocker |
| In Progress | Actively being worked |
| Blocked | Waiting on a specific ticket - name it in `Dependencies:` |
| Done | Shipped. Remove from BACKLOG.md, write to CHANGELOG.md |
| Parked | Valid but on conscious hold. No specific blocker, just not now |
| Decided Against | Ruled out with documented reasoning. Permanent |

"Resolved" is not a valid status.

### Ticket Lifecycle

**Creating a ticket:**
1. Find the current highest ID: `grep -o 'MATTGPT-[0-9]*' BACKLOG.md | sort -t- -k2 -n | tail -1`. New ID = that number + 1. Never eyeball the matrix to guess.
2. Add matrix row in ID order.
3. Add detail block at end of Detail Blocks section.
4. Required fields: Status, Priority, Type, Issue, Logged.
5. If it belongs in NOW or NEXT, add it to the roadmap immediately.

**Status transitions:**
- Open → In Progress → Done
- Open / In Progress → Blocked (add blocking ticket ID to `Dependencies:`)
- Blocked → Open (when the blocking ticket closes)
- Any active status → Parked or Decided Against

**When marking Done:**
- Add `Resolved: <date> + <commit hash>` to the detail block.
- Remove the matrix row AND the detail block from BACKLOG.md.
- Write a CHANGELOG.md entry (paragraph + commit hash + ticket ref).
- All three in the same edit. Never partial.

**When marking Decided Against:**
- Add a one-line reason to the detail block. Required - future context depends on it.
- Leave the matrix row and detail block in place permanently.

**When marking Blocked:**
- Name the blocking ticket in `Dependencies:` in the detail block.
- Do not mark a ticket Done while any listed dependency is not Done or Decided Against.

### What Goes Where
- **CHANGELOG.md:** Done items only. Ship record.
- **BACKLOG.md:** Everything else - Open, In Progress, Blocked, Parked, Decided Against. None of these move to CHANGELOG.md.

### Matrix and Detail Block Invariant
Always in sync. Touch one, touch the other. A matrix row without a detail block is invalid. A detail block without a matrix row is invalid.

### Maintenance Pass
**Trigger:** Before picking up the next item on the NOW list.

**Sync anchor:** `BACKLOG.md` contains `<!-- last-backlog-sync: <sha> -->` at the top. Read this, run `git log <sha>..HEAD --oneline` for the commit range, then update the comment. If the SHA is missing or unresolvable, prompt Matt before proceeding; do not default to diffing the entire history.

**Inputs:** `BACKLOG.md`, `CHANGELOG.md`, `git log <sha>..HEAD --oneline` since last sync.

**Actions (propose before writing anything):**
1. Check for any tickets marked Done in the matrix that still have a detail block in BACKLOG.md or are missing a CHANGELOG.md entry - these were not fully closed at ship time. Complete the cleanup now: remove matrix row AND detail block, write CHANGELOG.md entry.
2. Architecture Sync: run the Architecture Sync pass (see section below) using the same commit range. The two passes share one anchor and one approval gate.
3. Update `<!-- last-backlog-sync: <sha> -->` to HEAD.
4. Nothing writes until Matt approves the proposed diff.

## Architecture Sync

**Trigger:** Run alongside the Backlog Maintenance pass, or on demand. Uses the same `<!-- last-backlog-sync: <sha> -->` anchor and commit range.

**Who runs it:** The dedicated Architecture Sync Cowork process, not Code. Code's job is to write a commit message that fully describes any structural change. That commit message is the handoff. The sync process reads the commit range and proposes ARCHITECTURE.md updates for Matt's approval before writing anything. Code never edits ARCHITECTURE.md directly.

**Inputs:** `ARCHITECTURE.md`, `git log <sha>..HEAD --oneline` (same range as the backlog pass).

**Step 1: Classify commits**
For each commit in the range, classify:
- New file in `services/`, `ui/pages/`, `ui/components/`, `utils/`, `config/` - likely needs ARCHITECTURE.md update
- Change to an existing pattern (click handling, session state, CSS architecture, RAG pipeline) - likely needs ARCHITECTURE.md update
- New constraint discovered (canvas BDD, widget key rules, etc.) - needs ARCHITECTURE.md entry
- Bug fix or style tweak with no structural implication - skip

**Step 2: Propose specific text**
For each structural change: name the section and paste the exact proposed text. Nothing vague. If the right section does not exist, propose the section header too.

**Step 3: Approval gate**
Nothing writes until Matt approves the full proposed diff. One approval covers all ARCHITECTURE.md changes from this pass.

## Documentation Restraint
Default to **not** creating new markdown files. Most findings belong in commit messages, BACKLOG entries, ADRs, or inline updates to existing docs.

Before creating a new `.md` file, justify why it can't go into an existing doc, a commit message, a BACKLOG entry, or a code comment. Transitory files go in `docs/working/` with a lifecycle declaration. Permanent new top-level docs require explicit approval.

## No Hardcoded Enums for Data-Derived Values
Never hardcode lists of values that come from story data (clients, industries, themes, eras).

```python
# BAD
if client in {"JP Morgan", "Capital One", "RBC"}:

# GOOD
from utils.client_utils import is_generic_client
if is_generic_client(client):
```

If a value comes from the JSONL, derive it or use pattern matching. One source of truth in `utils/` or `config/`, imported everywhere.

## No Hardcoded Story Titles in Tests
Never hardcode specific story titles in eval tests. Use index-based selection; filter by Client, Domain, or Era instead.

## Nonsense Filter Rules
`nonsense_filters.jsonl` contains regex patterns to block off-topic queries. Rules for adding patterns:
1. Test against real queries first - will this block "Tell me about Matt's X"?
2. Avoid common verbs - "solve", "build", "create", "manage" appear in legitimate queries
3. Prefer multi-word phrases - `"homework help"` safer than `"homework"`
4. Use word boundaries - `\b(word)\b` prevents partial matches
5. Don't duplicate the semantic scoring gate (< 0.55 already catches gibberish)

## Pinecone Metadata Casing
Lowercase field names; values have inconsistent casing:

| Field | Casing | Example |
|-------|--------|---------|
| `division`, `employer`, `project`, `industry`, `complexity` | lowercase | `"cloud innovation center"` |
| `client`, `role`, `title`, `domain` | PascalCase | `"Accenture"` |

```python
if pc_field == "division":
    pc_value = entity_value.lower()
else:
    pc_value = entity_value
```

## Configuration Rules
Priority order:
1. **Derive from data** - if computable from source data, do that
2. **Environment variable** - if it changes between environments or is a secret
3. **`config/constants.py`** - if it's application logic that must be consistent
4. **Local constant with comment** - only if truly file-specific

If hardcoded values are duplicated across files, that's a bug. Centralize immediately.

## RAG Pipeline
```
Query → Nonsense Filters → Semantic Router → out_of_scope check → Pinecone → Confidence Gate → LLM
```

**Intent families (15):** background, behavioral, delivery, team_scaling, leadership, technical, domain_payments, domain_healthcare, stakeholders, innovation, agile_transformation, narrative, synthesis, out_of_scope, personal

**Entity detection:** Client, Employer, Division, Title. Hard filters: Client, Employer, Division, Project, Place. Soft filters: Title.

**Context exclusion prefixes:** "after", "leaving", "before", "transition from", "left" - prevent entity filtering.

**Verbatim phrases (sacred vocabulary):** "builder" - use exactly in Professional Narrative responses.

**Confidence thresholds:** See `config/constants.py`. Do not duplicate values here.

## Quality Standards
- Every claim, metric, or statement must be factually accurate
- No AI fabrications - real stories from real experience only
- Mobile must not break desktop - test both after any CSS change

## CSS Variable Reference
See `global_styles.py` for the full variable set. Do not duplicate values here. Key variables: `--accent-purple`, `--bg-card`, `--bg-surface`, `--text-primary`, `--text-secondary`, `--border-color`, `--hover-shadow`.

## Deployment
```bash
streamlit run app.py        # local
git push origin main        # triggers Streamlit Cloud deploy
```

## Related Documentation
- [Design Specification](https://mcpugmire1.github.io/mattgpt-design-spec/)
- [API Reference](https://mcpugmire1.github.io/mattgpt-design-spec/docs/09-api-reference)
- [Data Model](https://mcpugmire1.github.io/mattgpt-design-spec/docs/10-data-model)
