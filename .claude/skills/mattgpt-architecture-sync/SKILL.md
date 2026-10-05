---
name: "mattgpt-architecture-sync"
description: "Arch sync session only. Use when running the MattGPT Architecture Sync pass to propose ARCHITECTURE.md and docs/ADR.md updates from recent commits and Decided Against tickets, or when migrating legacy Decided Against tickets into Rejected ADRs."
---

## Architecture Sync

**Runner check, before anything else:**
1. Run `printenv MATTGPT_DOCS_SESSION`. If it doesn't print `arch`, stop and tell Matt to launch `scripts/arch-sync-session.sh`.
2. Run `git status --short -- ARCHITECTURE.md docs/ADR.md`. If it shows any changes, stop and show Matt the diff. Never stage this pass's edits on top of changes you didn't make.

Run git and repo commands yourself against the local repo. Never clone the repo or work from any other copy: a clone only sees pushed commits.

**Scope:** This pass is the only writer of `ARCHITECTURE.md` and `docs/ADR.md`. It reads BACKLOG.md but never writes it. Any finding that would require a change to CLAUDE.md, `.claude/rules/`, hooks, or skills gets flagged to Matt, not written.

**Trigger:** On demand. Run this pass before the backlog pass in a cycle. Matt may also hand this pass a one-off migration batch (see Step 1b); apply the same ADR and content rules to it.

**Range:** The range is `<anchor>..<end>`.
- `<anchor>`: read from `<!-- last-backlog-sync: <sha> -->` in BACKLOG.md, or the SHA Matt gives when starting ("sync from `<sha>`"). Never update the anchor; only the backlog pass moves it.
- `<end>`: HEAD at the start of this pass. Fix it once and use it for every step. Commits that land during the pass, including this pass's own commit, belong to the next range.

**Handoff:** Commit messages from dev sessions feed this pass: a commit that changes structure describes it fully, and a commit that makes a design decision or removes a layer carries `Decision:` and `Rejected:` trailers.

**Inputs:** `ARCHITECTURE.md`, `docs/ADR.md`, `BACKLOG.md` (Decided Against tickets only), `git log <anchor>..<end> --oneline`, and the decision trailers:

```
git log <anchor>..<end> --format='%h%n%(trailers:key=Decision)%(trailers:key=Rejected)'
```

**Step 0: Churn report (report only)**
For the commit range, list the 5 most-changed code files (exclude *.md, tests/, probes/, probe_*, data/) and any code-file pairs that changed together in 3+ commits. Flag files over 1,000 lines. Propose nothing; Matt decides whether a flagged file gets a ticket.

**Step 0b: Design spec drift (report only, after Step 1)**
The design spec repo is checked out at `../mattgpt-design-spec`. First run `git -C ../mattgpt-design-spec fetch` and report whether the local checkout is behind `origin/main` (`git -C ../mattgpt-design-spec rev-list --count HEAD..origin/main`). If it is, say so at the top of the report and search `origin/main` rather than the stale working tree. Report `origin/main`'s last commit date.
For each structural change Step 1 identifies (a `Decision:` trailer, a removal, a changed pattern), search the spec for the component's name: `git -C ../mattgpt-design-spec grep -n -i "<name>" origin/main -- '*.md'`. List each hit with its file and line, and whether the spec describes the component as current or as removed. Propose nothing; Matt decides whether the spec needs an update. Never write to the design spec repo.

**Step 1: Classify commits**
For each commit in the range, classify:
- New file in `services/`, `ui/pages/`, `ui/components/`, `utils/`, `config/`: likely needs an ARCHITECTURE.md update.
- Change to an existing pattern (click handling, session state, CSS architecture, RAG pipeline): likely needs an ARCHITECTURE.md update.
- New constraint discovered (canvas BDD, widget key rules, etc.): needs an ARCHITECTURE.md entry.
- `Decision:` trailer: propose a new ADR.
- Removal of a layer, component, prompt clause, gate, or pattern: delete its description from ARCHITECTURE.md and propose a new ADR recording what was removed, why, and what replaced it. If an existing ADR introduced it, mark that ADR Superseded.
- A message that describes a design decision or removal without trailers: propose the ADR anyway and flag the missing trailer to Matt.
- Bug fix or style tweak with no structural implication: skip.

**Step 1b: Decided Against tickets**
Regular passes check every ticket in the Active Matrix with Status Decided Against. The marker check makes repeats harmless, so a ticket that's still waiting on reasoning gets picked up again on the next pass. Tickets in the legacy Decided Against table are handled only when Matt hands over a migration batch, at most 10 tickets per batch.

For each ticket in scope, check whether its Rejected ADR exists:

```
grep -cE "^\*\*Ticket:\*\* MATTGPT-${ID}[[:space:]]*\$" docs/ADR.md
```

A count of 1 means it exists; skip the ticket. A count of 0 means propose a Rejected ADR using the fields below. Only that exact marker line counts; a ticket ID mentioned anywhere else in ADR.md is not a match. If the ticket's recorded reasoning is too thin to fill the ADR, ask Matt for it; do not infer a reason. Do not touch BACKLOG.md; the backlog pass removes the ticket once its ADR exists.

**Step 2: Propose specific text**
For each change: name the section or ADR and paste the exact proposed text. Nothing vague. If the right ARCHITECTURE.md section does not exist, propose the section header too. When a section you touch contains history (change dates, ticket IDs, "was removed", "previously", "no longer", "didn't change"), propose stripping it, and move any decision content into an ADR.

**Step 3: Docs check**
Run `python3 .claude/skills/mattgpt-docs-check/check_docs.py` and include the report. Findings in ARCHITECTURE.md go into this pass's proposed diff. Findings in files this pass doesn't own get flagged to Matt.

**Step 4: Approval gate**
Nothing writes until Matt approves the full proposed diff. One approval covers all ARCHITECTURE.md and `docs/ADR.md` changes from this pass.

**Step 5: Commit**
After Matt approves, write the files, stage `ARCHITECTURE.md` and `docs/ADR.md` by name, show Matt the commit message, and commit on his OK. Use repeated `-m` arguments for multi-paragraph messages. Commit by pathspec, so nothing else that is staged gets included. Always carry the range as a trailer:

```
git commit -m "Architecture Sync: <summary>" -m "<body>" --trailer "Sync-Range: <anchor>..<end>" -- ARCHITECTURE.md docs/ADR.md
```

If the pass found no changes, make an empty commit that records the range:

```
git commit --allow-empty --only -m "Architecture Sync: no changes" --trailer "Sync-Range: <anchor>..<end>"
```

Never push. The backlog pass reads this trailer to know where to move the anchor.

Exception: a migration batch commits without the Sync-Range trailer. It doesn't review the commit range, so the trailer would move the backlog anchor past commits nobody reviewed.

**ARCHITECTURE.md content rules:**
- Current state only: no change narrative, ticket numbers, or commit hashes, and no dates that record when the system changed. Dates that are data, such as career dates and employment ranges, stay.
- Decisions, removals, and rejections go to `docs/ADR.md`. Shipped work goes to CHANGELOG.md through the backlog pass.
- A section may point to the ADR behind it: "See ADR 0NN in `docs/ADR.md`."

**docs/ADR.md rules:**
- Append only. New entries go at the end of the file.
- Next number: `grep -oE '^## ADR [0-9]+' docs/ADR.md | grep -oE '[0-9]+' | sort -n | tail -1`, plus one, zero-padded to three digits.
- Heading for new entries: `## ADR 0NN: Title`. Colon, no dashes. Existing headings use other styles; leave them as they are.
- Fields, in this order, each as a bold label (`**Date:**`, `**Status:**`, and so on):
  - Date
  - Status: Accepted, Planned, Rejected, or Superseded by ADR 0NN
  - Ticket: Rejected ADRs only, one line, `**Ticket:** MATTGPT-NNN`, nothing else on the line
  - Related tickets
  - Context
  - Decision
  - Rationale: includes the alternatives considered and why they lost
  - Consequences
  - Further sections only when the entry needs them, such as a methodological note
- The only permitted edit to an existing ADR is its Status line, when a newer ADR supersedes it.
- A removal ADR names the removed component precisely enough to distinguish it from anything live with a similar name, and says what replaced it.
- Dates and ticket IDs are allowed in ADRs. Line numbers are not; cite functions and constants by name.
