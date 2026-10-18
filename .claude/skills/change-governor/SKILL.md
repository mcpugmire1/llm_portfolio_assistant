---
name: change-governor
description: Advisory pre-go review of a consequential change. Lists every production behavior the change removes or alters, its value driver, what replaces it, and the recorded decision or "none found", plus conflicts with accepted ADRs. Use before "go" on any ticket that deletes, bypasses or alters a function, call, branch, prompt clause, gate, fallback, logged or returned field, or changes a model, retrieval or prompt. Advisory only; never blocks, edits, approves or rejects.
---

# Change Governor

The review runs in a separate, confined agent: Read, Grep and Glob only,
confined to a fresh folder holding only the parent snapshot, the diff and
spec.md. This session prepares the folder, launches the run, and relays
the output. It does not review the change itself.

## Inputs
- BASE: the commit the change applies to (for a proposed change, HEAD;
  for a past commit X, X^).
- The change: the working-tree diff against BASE, or BASE..X.
- The ticket ID, so the agent can find "### <ID>" in BACKLOG.md.

## Steps
1. Make a run folder in the scratchpad (never inside the repo):
   RUN=<scratchpad>/governor_<ticket>_<timestamp>; mkdir -p "$RUN/repo"
2. Export the parent without history or sensitive files:
   git archive --format=tar "$BASE" | tar -x -C "$RUN/repo" \
     --exclude='*.xlsx' --exclude='.env*' --exclude='*secret*' \
     --exclude='*credential*' --exclude='*token*' --exclude='archive'
3. Write the diff: git diff "$BASE" > "$RUN/change.diff"
   (or git diff "$BASE" X for a past commit).
4. Copy this skill's spec.md to "$RUN/spec.md". Confirm there is no .git
   anywhere under $RUN: find "$RUN" -name .git must print nothing.
5. Run, from $RUN:
   claude -p "<prompt>" --tools "Read,Grep,Glob" --restricted \
     --strict-mcp-config --permission-prompts none --model opus \
     --output-format stream-json --verbose < /dev/null > "$RUN/run.jsonl"
   Prompt: read spec.md and follow it exactly; the change is <ticket>;
   repo/ is the parent, change.diff the diff, the ticket is under
   "### <ticket>" in repo/BACKLOG.md; write "unknown" for anything not
   in the folder; end with "Files and searches used".
6. Audit the run: list every tool call in run.jsonl and flag any path
   outside $RUN or any tool other than Read, Grep, Glob. Paste the
   counts and any flags.
7. Paste the governor output verbatim. Do not summarize, re-rank or
   soften it.

## Rules for the session relaying it
- It is advisory. Matt decides; the output is not an approval.
- Before relaying any row as a finding, spot-check its quotes with
  grep -cF against $RUN/repo. Report what was checked.
- A conflict or "none found" row is a question for Matt, not a defect
  to fix. No fix proposals.
- If Decisions needed is over 10, relay the size line as written.

## Known limits (from the 1095d2c and -323 blind tests)
- One run per change; run-to-run variance is unmeasured.
- Driver can come back "unknown" on some rows, and visibility calls
  are judgment.
- Cost: about $0.66 and 2 minutes for a one-file change; about $5.60
  and 13 minutes for a 10,500-line diff.
