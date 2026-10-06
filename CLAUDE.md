# MattGPT: Claude Working Agreement

## Critical Rules
Rules marked "Enforced" are also blocked by hooks. If a hook blocks a command, stop and report it to Matt. Never route around a hook: no `--no-verify`, no `core.hooksPath` changes, no alternate command that does the same thing.

- **No em dashes anywhere in this repo.** Not in docs, not in commits, not in this file. Use a colon, comma, or rewrite the sentence. (Enforced on added lines and commit messages.)
- **Only Matt pushes.** No Claude session runs `git push`, even when asked. `git push origin main` triggers a production deploy on Streamlit Cloud. Stop after committing. (Enforced.)
- **Tests before any implementation code.** Shape, exceptions, and Red-Green discipline: see Testing Protocol.
- **Subtract before you add, in the answer pipeline.** Before adding a prompt clause, post-processing step (regex strip, bolding), or gate: read the removal ADRs in `docs/ADR.md`, confirm the output is actually wrong rather than just changed, name the observed failure, check whether the fix belongs in the data instead (`data/matt_profile.json` or the story corpus), and show a live acceptance run that fixes it, including the story controls it wasn't written for (see Testing Protocol). A clause written for one query type can change answers to others, so the run includes unrelated queries. When one causes a new failure, try removing it before adding an exception. Keeping one under review takes the same checks as adding it; a test that requires it is not the justification.
- **Paste literal test output at every gate, never self-summarize.** "Looks good, ready to commit?" is not a gate. Paste the literal `pytest` output before requesting commit approval at every Red and Green commit.
- **One "go" ships the full Red → Red → Green cycle.** After Matt says "go" on a ticket, run all three gates without re-asking between them. Re-ask only when a substantive new design decision surfaces mid-cycle.
- **Pre-flight before touching any existing file.** Name the files the ticket touches, the patterns those files use, any cross-surface couplings, and existing test coverage, before proposing anything. Check `conversation_helpers.py` before any click handler and `banking_landing.py` before any cross-page navigation. Build on existing patterns; replace one only when you can name in a comment why it fails.
- **Stage specific files by name, never `git add -A` or `git add .`.** Parallel sessions share one staging area. (Enforced.)
- **No Co-Authored-By lines in commit messages.** Never add them, in any session. (Enforced.)
- **Never use `grep -v` to redact secrets.** Use positive include filters (keys only). Applies to `.streamlit/secrets.toml`, `.env`, any service-account JSON. (Enforced.)
- **Artifacts for user review go in chat, not /tmp.** Edit tool calls show diffs inline. Writing to /tmp creates a local-only artifact Matt cannot see.
- **DevTools before any CSS proposal.** For any layout, alignment, positioning, sizing, color, or typography issue: get computed styles before proposing a fix, from Playwright `getComputedStyle` or by asking Matt to paste them from DevTools. Source-code reasoning misses Streamlit's wrapper-layer surprises.
- **Unexpected test or eval failures are your problem until proven otherwise.** Every failure gets an isolation run and a traceback before anything else. Nothing is labeled pre-existing, stochastic, or a known issue without a git bisect, a prior passing-run artifact, or a validation against production. "I didn't touch that code" is not evidence, and file proximity to the diff is not evidence either way until checked. Presenting options and waiting is not investigating. A known issue that isn't in BACKLOG is an unvalidated note.
- **Bug findings lead with the defect and the fix, never with origin.** All bugs in this repo are ours. Code age or provenance is stated only when it gates a live decision (push safety, revert scope) and only after the fix is on the table. Leading with "pre-existing confirmed" or "not introduced by this branch" is deflection regardless of whether it's true.
- **Any assertion about file contents needs a visible source in the response:** a Read or Grep tool call, or the command that produced it and that command's literal output. This covers what a file contains, what it does not contain, and what a function does. It applies with particular force to claims of absence: a search that returns nothing is not a finding until the search and its empty result are visible, because a malformed search also returns nothing. If there is no source, the assertion does not get made. Before citing a constraint as the reason for an approach, show it in the file; if it isn't there, use the simplest approach the file supports.
- **Working notes do not replace tracking.** Any bug, regression, or unvalidated behavior written to a working note also goes in the next commit message or gets flagged to Matt before the session proceeds. A finding that only exists in `docs/working/` or a notes file has no owner and will not be acted on. "I noted it" is not the same as "it is tracked."
- **Cite functions and constants by name, not line number.** Line numbers go stale between sessions and across commits. `load_matt_profile()` is stable; a line number is not. Applies to CLAUDE.md, ARCHITECTURE.md, tickets, and chat.
- **A structural refactor invalidates values and selectors anchored to the old structure.** Navbar height, container classes, DOM nesting: when these change, re-audit what's calibrated to them. Renaming `.main` to `.stMain` silently kills every rule targeting `.main`, and a changed navbar height orphans every offset calibrated to it. These surface in production, not at change time.

---

## Where Things Live
- `scripts/arch-sync-session.sh` and `scripts/backlog-session.sh`: launch the two docs sessions, one per pass.
- `mattgpt-architecture-sync` skill (`.claude/skills/`): ARCHITECTURE.md and `docs/ADR.md` from recent commits. Arch sync session only.
- `mattgpt-backlog-maintenance` skill (`.claude/skills/`): BACKLOG.md and CHANGELOG.md. Backlog session only.
- `.claude/rules/streamlit-ui.md`: CSS rules and Streamlit patterns. Loads when UI files are read.
- `.claude/rules/rag-pipeline.md`: RAG pipeline, entity filters, Pinecone casing, nonsense filters. Loads when pipeline files are read.
- `ARCHITECTURE.md`: full system context, including the file structure.
- [Design Specification](https://mcpugmire1.github.io/mattgpt-design-spec/): canonical tech stack and system architecture. Do not duplicate tech stack facts here.

## Document Ownership
- **Read this entire file before proposing any edit to it.** Synthesize across all sections first. Do not add a section after reading two lines.
- **Current state only.** CLAUDE.md, `.claude/rules/`, and ARCHITECTURE.md hold current rules and current state: no dates, ticket IDs, incident history, or change narrative. History goes to `docs/ADR.md` (decisions, removals, rejections) or CHANGELOG.md (shipped work).
- **CLAUDE.md and `.claude/rules/`:** Matt writes these himself. No Claude session edits them.
- **`.claude/settings.json`, `.claude/hooks/`, `.githooks/`, `.pre-commit-config.yaml`:** Matt owns these. No automated process writes to them on its own initiative; Code applies a change only when Matt directs that specific change.
- **ARCHITECTURE.md and `docs/ADR.md`:** written only by the arch sync session. **BACKLOG.md and CHANGELOG.md:** written only by the backlog session. Dev sessions never write any of the four; their commit messages are the handoff. (Enforced: the pre-commit role check limits each session to its own files.)

## Code Conventions
- Filter state lives in `st.session_state["filters"]`
- CSS variables defined in `global_styles.py` (use them, don't hardcode colors)
- Widget versioning pattern: `key=f"widget_name_v{version}"` for forced refreshes
- Use `safe_container()` wrapper for bordered sections
- Container keys for CSS targeting: `.st-key-{key_name}` selectors

## Behavioral Rules

### Before starting any ticket
1. **Pre-flight:** name the files, patterns, couplings, and test coverage (see Critical Rules).
2. **Pre-implementation reasoning gate:** before proposing any implementation, state in one sentence what the current code does, one sentence what the change does, and one sentence why it's better than the simplest alternative. If that third sentence can't be written confidently, stop and ask. Do not default to the more complex approach.
3. **Default is build-on-top-of, not replace-with:** extend the existing pattern; only propose replacing when you can name in a comment why it fails.
4. **Tests first,** in the shape the Testing Protocol calls for.

### During implementation
- Give direct solutions immediately after pre-flight
- **Scope:** a trivial fix in a file you're already editing (typo, dead import, stale comment, no behavior change) gets fixed and named in the commit message. A behavior change outside the ticket gets proposed, not made.
- Keep reference docs/comments when rewriting files
- Do not add dependencies without flagging it
- Do not hardcode values that are already CSS variables
- Do not invent new patterns when existing ones work

### On specs and wireframes
- **Cross-check the artifact, not just the verbal scope.** When a wireframe/spec AND verbal scope are given, the artifact is truth on copy/structure/sizing. Match it exactly or flag the conflict explicitly.
- **Visual spacing: give baseline + lever, let Matt call the value.** For margins/gaps/padding, name the controlling rule by selector and file, suggest a starting point, let Matt eyeball and call the final value.

### On estimates
- **Headline number = raw implementation time only.** BDD overhead and discovery risk are listed as explicit add-ons, not folded into the headline. A 30-min change is quoted as 30 min, not "2-3 hours."

### On evidence and verification
- **Re-measure any recorded number before it scopes work.** A figure from an earlier pass may be wrong, stale, or from a broken command.
- **Grep for importers before proposing a deletion, and read the file a ticket names before writing about it.** Key presence in a file isn't the same as the file being safe to remove.
- **Verify against the shape production passes in, not the shape at rest.** A field that exists in the JSONL may not survive the pipeline transformation the LLM actually receives.
- **Distinguish what a command proved from what you concluded from it.** Key presence isn't field-access correctness. A grep without `-r` isn't a repo search. State what the evidence actually shows, not what you inferred from it.

### On debugging and diagnosis
- **A repeated, specific, concrete observation is a constraint the diagnosis must satisfy, not an anecdote to explain away.** When instrument data and a consistent human observation conflict, the observation usually means the instrument is measuring the wrong thing, not that the observation is noise.
- **"The framework" is not a stopping point.** Framework-internal is often partly true and always unactionable. Keep going until the explanation accounts for the specific named symptom, which always lands somewhere project-side.
- **When Matt names a specific thing, verify you are looking at exactly that thing before reasoning about it.** Anchor to the named element, component, or behavior and confirm it before theorizing. Reasoning about the wrong frame is not diagnosis.
- **This is not a rule about deference.** Wrong theories get killed with evidence regardless of whose they are. The rule is about how to treat a specific class of input: a repeated, named, concrete symptom is a falsification test, not color commentary.

### Parallel sessions
When multiple Claude Code sessions run concurrently, they share one git working tree and one staging area.
- Stage specific files by name (see Critical Rules)
- Check `git status` before staging to see what the other session has modified
- Coordinate commit timing through Matt: Session A commits and reports its SHA; Matt tells Session B to proceed.
- For true parallelism: `git worktree add ../project-branchname`

## Testing Protocol

**The non-negotiable:** Tests are written and committed before any implementation code. Two exceptions: look-only CSS changes (spacing, color, layout, with nothing appearing, disappearing, or behaving differently) get no Red test, and probes and PoCs are exempt as described under Probes and PoCs. Look-only CSS gates are computed styles before the change (see the DevTools rule) and a browser check at 375px, 767px, and 1024px+ on a restarted Streamlit after it. If anything visible appears, disappears, or responds differently, it's a behavior change and tests come first. If a spec is provided, tests come first.

### Choosing the test shape
- **BDD:** UI behavior, user-facing flows, anything Playwright can observe in the DOM. Write `.feature` scenarios.
- **Unit tests:** Pure functions, batch scripts, pipeline stages with no DOM surface. Write pytest functions directly. Do not write `.feature` files for batch scripts or functions with no UI interaction.
- **Live acceptance runs:** For changes to prompts, retrieval, or anything else whose output depends on the LLM. A live acceptance run is a probe script in `probes/`, writing its output to `probes/output/<ticket>/<timestamp>/`. It runs the acceptance queries through the real pipeline (`rag_answer()` or `assess_requirement()`, with all loggers patched out: `log_query`, `log_offdomain`, and the router's two CSV writers, `_log_borderline` and `_log_router_low_confidence`; stderr in its own file), at least 2 runs per query, and it pastes the full answer text for each run. It includes the story controls when the change touches a shared prompt. It supplements unit tests and doesn't replace them: unit tests prove the text reaches the prompt, and the live run shows what the model does with it.

### Red-Green cycle

- **Red (scenarios commit):** Write scenarios in `tests/bdd/features/X.feature` AND bind via `scenarios("../features/X.feature")` in `tests/bdd/steps/test_X.py`. Run `pytest tests/bdd/steps/test_X.py -v`, confirm all scenarios discovered and all in undefined-step state. Commit message proof: `Red (scenarios): N scenarios discovered, all N undefined-step.`
- **Red (step defs commit):** Write step definitions. Confirm scenarios run end-to-end and fail with assertion errors (not undefined-step or import errors). Commit message proof: `Red (step defs): N scenarios bound, N assertion failures, 0 undefined-step / import errors.`
- **Green (production code commit):** Write minimum production code to pass. Confirm all pass. Commit message proof: `Green: N / N scenarios passing.`
- **Refactor (optional):** Clean up while keeping tests passing.

### Unit test Red-Green cycle
The two-Red split applies to BDD where `.feature` and `test_X.py` are separate artifacts with a meaningful intermediate state. For unit tests, one Red commit: tests written fully, failing on assertion errors (not import errors). Green is still a separate commit. The non-negotiable is the same: tests exist before implementation and fail for the right reason.

When testing a new function that doesn't exist yet, the Red commit includes the test file plus stub signatures raising `NotImplementedError`, and nothing else. Tests then fail on assertion errors, not import errors. A stub is a function signature and `raise NotImplementedError` only: no logic, no returns, no constants.

### Probes and PoCs
Probes and PoCs are exploratory measuring instruments, exempt from the Red gate. They stay untracked and never import into production. The exemption ends the moment probe code moves into `services/` or `ui/`: at that point it's production and the full protocol applies.

**A probe result is one measurement.** Before it scopes work or changes a conclusion, verify it against an independent source: a different field, a different file, a different derivation. Two derivations that agree is a finding. One derivation is a reading.

**A causal claim needs the comparison that isolates the cause.** "X caused Y" requires a measurement with X absent. Without it, say "Y is present under X" and name what measurement would settle it. Either the before-state was measured or it wasn't.

### Validation rules
- **When reporting test results, state explicitly what was tested and what was not.** A pass count covers the scenarios run; it does not validate untested changes in the same commit. Never present partial coverage as full validation.
- **Green commits only after every validation relevant to the change has run.** Name the applicable gates before committing: whichever test shape the change called for (BDD for UI behavior, unit tests for pure functions and scripts, live acceptance runs for prompt or retrieval changes), plus a browser check on a restarted Streamlit when rendered output changed. A Green commit message never says "not run": list the gates that ran and mark the rest "not applicable". (Enforced.) If a relevant gate can't run, stop and ask rather than committing around it.
- **Scope per-gate runs to the relevant test file:** `pytest tests/bdd/steps/test_X.py -v`, not the full suite, except where a rule below requires the full suite.
- **A `.feature` file without its `test_*.py` binding is documentation, not a test.**
- **BDD scenarios must assert DOM-observable behavior.** Playwright cannot read `st.session_state`; assert navigation visible + user-message echo + assistant-response streaming.
- **After any change to UI files, ask Matt to restart Streamlit before running BDD tests.**
- **After any change to `explore_stories.py`, run the full BDD suite (`pytest tests/bdd/steps -v`) before presenting for review.**
- **Every test or eval failure follows the failure rule in Critical Rules.**
- **On a second Playwright selector timeout, screenshot before iterating:**
  ```python
  try:
      option.click(timeout=5000)
  except Exception:
      browser_page.screenshot(path='docs/working/pw_debug_selector.png')
      raise
  ```

### Canvas-Rendered Grids (st.dataframe): BDD Constraints

`st.dataframe` renders rows, cells, column headers, and selection controls to an HTML canvas, not the DOM. Full explanation and verified selectors: see `ARCHITECTURE.md` (st.dataframe canvas constraint).

**CAN assert:** grid mounted (`[data-testid="stDataFrame"]` + `[data-testid="data-grid-canvas"]`, waiting explicitly for canvas paint); filter pipeline worked (count direction from `.es-results-count`); detail pipeline worked (deeplink `?story=id` then assert `.es-detail-header`).

**CANNOT assert, ever:** row content, visual row rendering, canvas-driven row selection. A green BDD suite does not prove the grid painted its rows. Visual row-rendering correctness is manual visual check, not optional.

Any new `st.dataframe` surface inherits all of the above. If whole-row-click or keyboard row selection is a hard requirement, use self-rendered HTML rows (the Cards pattern).

## Secrets & Sensitive Output Handling
1. **Positive include filters only** (see Critical Rules):
   - `grep -oE "^[A-Z_][A-Z_0-9]*" .env`: key names only
   - `grep -oE "^[a-z_]+ ?=" secrets.toml`: top-level scalar keys only
2. **When inspecting any secrets file, extract keys-only by default.** Ask Matt to confirm values rather than printing them.
3. **Hard-cap output for any command touching a secrets file:** pipe to `| head -20`.

Applies to: `.streamlit/secrets.toml`, `.env`, `.env.local`, any service-account JSON, any file matching `*secret*` / `*credential*` / `*token*`.

## Pre-Commit Doc Checklist
Before committing, answer for each:
- **ARCHITECTURE.md and `docs/ADR.md`:** Does this change a pattern, surface, or fact in ARCHITECTURE.md? Describe the change fully in the commit message. Does it make a design decision, or remove a layer, component, prompt clause, or gate? Add trailers: `--trailer "Decision: <what was decided or removed>" --trailer "Rejected: <alternative> (<why>)"`. The Architecture Sync pass turns both into ARCHITECTURE.md edits and ADRs.
- **mattgpt-design-spec** (Jekyll repo): Does this change anything in the user-facing spec?
- **`ui/components/how_agy_dialog.py`:** Does this change anything described in the Ask MattGPT architecture exposition?
- **about_matt.py:** Does this change anything described in the "How I Built MattGPT" section?

If yes to any of the last three: the doc-update commit pairs with this code commit. Same session, same push. Not a follow-up.

Always triggers this check:
- New file in `services/`, `ui/pages/`, `ui/components/`, `utils/`, or `config/`
- Model, embedding, or vector store change
- Pipeline stage added/removed/renamed
- Schema change in story corpus, query logger, or any `config_*.json`

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

## Configuration Rules
Priority order:
1. **Derive from data:** if computable from source data, do that
2. **Environment variable:** if it changes between environments or is a secret
3. **`config/constants.py`:** if it's application logic that must be consistent
4. **Local constant with comment:** only if truly file-specific

If hardcoded values are duplicated across files, that's a bug. Centralize immediately.

## Quality Standards
- Every claim, metric, or statement must be factually accurate
- Story corpus content is real experience only. Never generate or embellish story facts.

## Deployment
```bash
streamlit run app.py        # local
```
`git push origin main` deploys to Streamlit Cloud (see the push rule in Critical Rules).

## Related Documentation
- [API Reference](https://mcpugmire1.github.io/mattgpt-design-spec/docs/09-api-reference)
- [Data Model](https://mcpugmire1.github.io/mattgpt-design-spec/docs/10-data-model)
