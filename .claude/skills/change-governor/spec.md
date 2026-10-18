# Change Governor (advisory), v3

**Job.** Before a consequential change is approved, list every behavior it removes or alters, the value driver each serves, what replaces it, and the evidence or decision behind it. Advisory only: it informs the person approving; it never blocks, edits, approves or rejects.

**Consequential change.** Any change that deletes, bypasses or alters a function, call, branch, constant, prompt clause, gate, fallback, logged field or returned field in production code (`services/`, `ui/`, `utils/`, `config/`, `app.py`, root-level pipeline scripts), or that changes a model, retrieval or prompt.

**Out of scope (do not list).**
- Tests, fixtures, probes, evals, and verification gates or check scripts that do not run when a visitor uses the app or when the pipeline produces data.
- Wording-only changes to operator-facing output (console prints, log message text, developer error strings) when what is computed, written or returned is unchanged. Visitor-facing text stays in scope.

**Inputs (nothing else).**
1. The proposed change: its diff, plus its ticket text if one exists.
2. The repository as it stands before the change (the parent).
3. Value drivers: `docs/value_scorecard.md` at the parent, including each driver's **Status** (met, failing, not measured).
4. Decision records at the parent: `docs/ADR.md`, `BACKLOG.md`, and commit SHAs those documents cite.

**Principles.**
- Every claim cites a file plus a function or constant name (never a line number), or a commit SHA, or a document heading. No citation means the claim is written as "unknown".
- A claim of absence ("no decision found", "no caller") shows the search that returned nothing.
- Describe what the parent's code does, read from the code, not from comments, docstrings or ticket prose. When code and prose disagree, report the code and note the disagreement.
- **A decision counts only if it names the specific behavior.** Quote the words from the record that name it. A ticket's general goal, an acceptance criterion about a neighbouring behavior, or an inference from what the ticket implies is not a decision: write "none found" and, if useful, "related: <heading>" with the quote.
- **A recorded decision that the change contradicts is a conflict.** Quote the decision and say what the change does instead. A conflict stands even when the ticket itself also decides the behavior; then quote both.
- Classify each behavior as: kept, altered, relocated, replaced, dropped, or added. Do not judge whether the change is good.
- No fix proposals, no severity scores, no approve or reject recommendation.

**Procedure.**
1. **Enumerate.** From the diff, list every deleted or changed in-scope: function, call site, branch, constant, prompt string, session-state write, logged field, returned field. For each deleted or bypassed function, follow what it called in the parent until reaching code the change leaves intact; behaviors in that call tree count too, including helpers in other modules left with no production caller.
2. **Kept items.** Behaviors in that call tree that survive the change unaltered get a row marked "kept", with where they now run. One line each.
3. **Added items.** Behavior the parent did not have at all (a new clause, rule, step, constant or setting with no predecessor) is classified "added". If it replaces something the parent did, it is "replaced" or "altered", not "added".
4. **Stale references.** For every prompt string, instruction, template or code path in production code that the change keeps or adds, check whether it refers to an input, tag, field, variable or step the change removes (for example "the primary story" when no story is marked primary any more). Each one is a row classified "altered (stale reference)", quoting the text and naming the removed input. Documentation (README, ARCHITECTURE, ADR, BACKLOG, other docs) that describes removed behavior is not a row: it goes in Doc follow-ups.
5. **Describe.** One sentence per behavior: what it did to a question, its retrieval, its answer, its output or its data.
6. **Locate.** Where the behavior lives after the change, citing it, or "dropped".
7. **Driver.** The one scorecard driver whose intended outcome the behavior serves (by the scorecard's own number and name), with that driver's Status; "n/a" for kept; "unknown" if none fits.
8. **Decision and conflicts.** Search the decision records for a decision on that specific behavior, under the quote rule above. Cite heading plus quote, or "none found" with the search shown. Separately, search the accepted decisions (ADRs not marked Superseded or Rejected, and Locked or Decided lines in tickets) for any statement the change contradicts, whether or not it is about a removed behavior.
9. **Self-check.** Re-open every cited location and confirm it says what the row claims, and that every decision and conflict quote appears verbatim. Delete or mark "unverified" any row that fails.

**Output, in this order.**
1. **Conflicts with accepted decisions.** One line each: the decision's heading and quote, what the change does instead, the row number it relates to. If none: "No conflicts found", with the searches shown.
2. **Table A, answer pipeline:** behaviors that affect retrieval, the prompt, the model call, gates, fallbacks, the answer text, or the logged or returned fields that describe an answer.
3. **Table B, presentation, copy and ops:** everything else in scope (layout, styling, visitor copy, navigation, scripts, data generation).
   - Columns in both: #, behavior, old location, after the change (or dropped), classification, driver (status), decision (quote) or evidence, confidence (verified in code / inferred / unknown).
   - Row order in each table: undecided rows first, ordered by driver status (failing, then not measured, then met); then decided rows; then added rows; kept rows last.
4. **Added.** One line per added row: "#n: <behavior>: decided (<quote>) / no decision found". Added rows never appear in Decisions needed.
5. **Doc follow-ups.** One line per document passage that still describes removed or altered behavior, quoting it. Never in Decisions needed.
6. **Decisions needed.** Every undecided row classified dropped, altered, relocated or replaced, plus every conflict, as two ranked lists, A then B, each in table order, one line per row: "#n: <behavior>: <visible to a visitor / no visible effect>". If the list is empty, say "No decisions needed".
7. **Size line.** If Decisions needed has more than 10 entries, end with: "Decisions needed: N (over 10). Consider splitting this change into smaller changes, each with its own review." Otherwise end with "Decisions needed: N."
