---
name: change-governor
description: Advisory review of a consequential change, at pre-flight and again at Green. Lists every production behavior the change removes or alters, its value driver, what replaces it, and the recorded decision or "none found", plus conflicts with accepted ADRs; at Green, also where the code differs from the approved plan. A separate checker verifies each row. Use before "go" on any ticket that deletes, bypasses or alters a function, call, branch, prompt clause, gate, fallback, logged or returned field, or changes a model, retrieval or prompt. Advisory only; never blocks, edits, approves or rejects.
---

# Change Governor

Each review runs in two separate, confined agents, a governor and a
checker: Read, Grep and Glob only, each confined to a fresh folder
holding only what its run type lists below. This session prepares the
folders, launches both runs, and builds Matt's decision packet. It does
not review the change itself.

## Review flow
- At pre-flight (before any code): the governor receives the ticket
  text, the ADRs and decisions it touches, the current code it names
  (at HEAD), and the session's planned change list (functions and
  prompt lines to add, change or remove). It does not receive the
  brief's risk or measurement sections.
  Folder: repo/ (HEAD snapshot, which carries BACKLOG.md, docs/ADR.md
  and the code), plan.md (the planned change list only), spec.md.
- At Green: the governor runs again on the actual diff, and reports
  where the code differs from the approved plan.
  Folder: repo/ (snapshot of BASE), change.diff, plan.md as Matt
  approved it at pre-flight, spec.md.
- After each governor run, the checker runs (step 6), then this session
  builds the decision packet.
- Status: first used on MATTGPT-128; revise after that trial.

## Inputs
- The run type: pre-flight or Green.
- BASE: at pre-flight, HEAD. At Green, the parent of the ticket's first
  commit (for a past commit X, X^).
- At pre-flight, the planned change list. At Green, the diff BASE..HEAD
  (or BASE..X) and the plan as Matt approved it.
- The ticket ID, so the agents can find "### <ID>" in BACKLOG.md.

## Steps
1. Make a run folder in the scratchpad (never inside the repo):
   RUN=<scratchpad>/governor_<ticket>_<runtype>_<timestamp>; mkdir -p "$RUN/repo"
2. Export BASE without history or sensitive files:
   git archive --format=tar "$BASE" | tar -x -C "$RUN/repo" \
     --exclude='*.xlsx' --exclude='.env*' --exclude='*secret*' \
     --exclude='*credential*' --exclude='*token*' --exclude='archive'
3. Pre-flight: write the planned change list to "$RUN/plan.md".
   Green: write the diff, git diff "$BASE" HEAD > "$RUN/change.diff"
   (or git diff "$BASE" X for a past commit), and write the approved
   plan to "$RUN/plan.md" exactly as Matt approved it.
4. Copy this skill's spec.md to "$RUN/spec.md". Confirm there is no .git
   anywhere under $RUN: find "$RUN" -name .git must print nothing.
5. Governor run, from $RUN:
   claude -p "<prompt>" --tools "Read,Grep,Glob" --restricted \
     --strict-mcp-config --permission-prompts none --model opus \
     --output-format stream-json --verbose < /dev/null > "$RUN/run.jsonl"
   Prompt: read spec.md and follow it exactly; the run type is
   <pre-flight|Green>; the change is <ticket>; repo/ is BASE, plan.md
   the plan (and at Green, change.diff the diff); the ticket is under
   "### <ticket>" in repo/BACKLOG.md; write "unknown" for anything not
   in the folder; end with "Files and searches used". Save the final
   output as "$RUN/governor.md".
6. Checker run: make "$RUN/check" holding copies of repo/, plan.md,
   change.diff (at Green) and governor.md, and no spec.md. Confirm
   find "$RUN/check" -name .git prints nothing. Run the same command
   from "$RUN/check", writing "$RUN/check/run.jsonl", with this prompt:
   "governor.md reviews the change described in plan.md (and
   change.diff, if present). For every row and every conflict in
   governor.md, read the code in repo/ and the records in
   repo/docs/ADR.md and repo/BACKLOG.md yourself; do not rely on the
   row's citations. Record your own reading of what the code does and
   what the records say, then mark the row CONFIRMED, DISAGREES (say
   what you found instead, citing file and function or heading and
   quote) or CANNOT CONFIRM (say what is missing). Keep every row;
   never drop one. Quotes must match exactly. Read nothing outside this
   folder." Save the final output as "$RUN/check/checker.md".
   Re-checks: after the first full check, a later round checks only the
   changed lines and what they depend on, not the whole output. Only a
   flag that changes a fact, a citation or a decision triggers another
   round. A wording-only flag is fixed once, without a re-check.
7. Audit both runs: list every tool call in each run.jsonl and flag any
   path outside its folder or any tool other than Read, Grep, Glob.
8. Build the decision packet. Keep governor.md and checker.md unedited;
   paste either in full, or one row's evidence, when Matt asks.

## Decision packet
Plain language, one screen, no command output.
1. The session's brief: what changes, what could get worse, how it's
   measured, cost.
2. The governor report: conflicts with decisions, behavior removed or
   altered with no decision, unknowns; at Green, where the code differs
   from the approved plan. Show only rows that need a decision or that
   the checker marked DISAGREES or CANNOT CONFIRM. Every other row goes
   in one line: "N rows agreed with the checker; no decision needed."
2a. At Green: for each function and module-level constant the diff
   deletes, `git grep -n -w <name> -- BACKLOG.md` at HEAD, and list the
   ticket IDs that name it, one line per name. "No hits" is listed too.
   These go to the backlog session as a relay; the packet does not judge
   them.
3. The checker's result on the governor rows: counts of CONFIRMED,
   DISAGREES and CANNOT CONFIRM.
4. One recommendation: go, go with changes, or not yet.
Each shown row: what a visitor sees before and now, the decision
needed, and confidence (the checker's mark). Evidence is shown only for
a row Matt asks about.

## Rules for the session relaying it
- The governor and checker are advisory. Matt decides; their output is
  not an approval.
- The packet's recommendation is this session's, labeled as such. The
  governor never recommends, and this session never changes a governor
  classification or a checker mark.
- A conflict or "none found" row is a question for Matt, not a defect
  to fix. "Go with changes" names changes to the plan, not code fixes.
- If Decisions needed is over 10, relay the size line as written.
- If the step 7 audit flags anything, say so at the top of the packet.

## Known limits (from the 1095d2c and -323 blind tests)
- One governor run and one checker run per run type; run-to-run
  variance is unmeasured. The checker's cost and accuracy are
  unmeasured.
- Driver can come back "unknown" on some rows, and visibility calls
  are judgment.
- Cost: about $0.66 and 2 minutes for a one-file change; about $5.60
  and 13 minutes for a 10,500-line diff.
