---
name: "mattgpt-backlog-maintenance"
description: "Backlog session only. Use when running the MattGPT Backlog Maintenance pass or creating, updating, or closing tickets in BACKLOG.md and CHANGELOG.md."
---

## Backlog Maintenance

**Runner check, before anything else:**
1. Run `printenv MATTGPT_DOCS_SESSION`. If it doesn't print `backlog`, stop and tell Matt to launch `scripts/backlog-session.sh`.
2. Run `git status --short -- BACKLOG.md CHANGELOG.md`. If it shows any changes, stop and show Matt the diff. Never stage this pass's edits on top of changes you didn't make.

Run git and repo commands yourself against the local repo. Never clone the repo or work from any other copy: a clone only sees pushed commits.

**Scope:** This process writes `BACKLOG.md` and `CHANGELOG.md` only. It reads `docs/ADR.md` but never writes it; Architecture Sync owns ADRs. CLAUDE.md, ARCHITECTURE.md, source files, and all other documents are out of scope. Any finding that would require a CLAUDE.md change gets flagged to Matt, not written.

**Handoff:** Commit messages from dev sessions feed this pass. Dev sessions never create, modify, or close tickets.

### Status Enum
Six values only. Do not invent others.

| Status | Meaning |
|--------|---------|
| Open | Not started, no blocker |
| In Progress | Actively being worked |
| Blocked | Waiting on a specific ticket; name it in `Dependencies:` |
| Done | Shipped. Remove from BACKLOG.md, write to CHANGELOG.md |
| Parked | Valid but on conscious hold. No specific blocker, just not now |
| Decided Against | Ruled out with documented reasoning. Stays in BACKLOG.md until Architecture Sync writes its Rejected ADR, then removed |

"Resolved" is not a valid status.

### Ticket Lifecycle

**Creating a ticket:**
1. Find the current highest ID across every file a ticket can live in: `grep -ohE 'MATTGPT-[0-9]+' BACKLOG.md CHANGELOG.md docs/ADR.md | sort -t- -k2 -n | tail -1`. New ID = that number + 1. BACKLOG.md alone is not enough: closed and rejected tickets leave it, and their IDs must not be reused. Never eyeball the matrix to guess.
2. Add the matrix row in ID order in the **Active Matrix** table.
3. Add the detail block in ID order under **Detail Blocks > Active Tickets**, inserted at the correct ID position. Never append to end of file.
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
- Set the status in both the matrix row and the detail block, and add the reason to the detail block: what was proposed, why it was ruled out, and what happens instead, if anything. Required; Architecture Sync builds the Rejected ADR from it.
- Leave the ticket where it is in BACKLOG.md. Do not move it to a separate table, and do not write to `docs/ADR.md`.

**When marking Blocked:**
- Name the blocking ticket in `Dependencies:` in the detail block.
- Do not mark a ticket Done while any listed dependency is not Done or Decided Against.

### What Goes Where
- **CHANGELOG.md:** Done items only. Ship record. Written by this pass.
- **docs/ADR.md:** Decided Against items, as Rejected ADRs. Written by Architecture Sync.
- **BACKLOG.md:** Open, In Progress, Blocked, Parked, plus Decided Against tickets waiting for their ADR.

### Matrix and Detail Block Invariant
Always in sync. Touch one, touch the other. A matrix row without a detail block is invalid. A detail block without a matrix row is invalid. Matrix row and detail block must land in the same edit with matching Priority and Type fields. Fields that disagree are invalid and must be corrected before the session proceeds.

### Ticket Body Discipline
Ticket bodies state dated observations, not current architecture. Write "Verified Aug 2026: `_tokenize` returns X" not "The scorer filters stopwords." Architecture descriptions go stale and send future sessions in the wrong direction.

### Maintenance Pass
**Trigger:** Before picking up the next item on the NOW list. Runs after Architecture Sync in a cycle.

**Sync anchor:** `BACKLOG.md` contains `<!-- last-backlog-sync: <sha> -->` at the top. That is the start of the range. If the SHA is missing or unresolvable, stop and tell Matt; do not default to diffing the entire history.

**Range end:** Read the end from the newest Architecture Sync commit after the anchor:

```
git log -1 <anchor>..HEAD --grep='^Sync-Range:' --format='%H %(trailers:key=Sync-Range,valueonly)'
```

The end is the SHA after `..` in that trailer. If no `Sync-Range` trailer is newer than the anchor, use HEAD as the end and say so in the commit message.

**Inputs:** `BACKLOG.md`, `CHANGELOG.md`, `docs/ADR.md`, `git log <anchor>..<end> --oneline`.

**Actions (propose before writing anything):**
1. Check for any tickets marked Done in the matrix that still have a detail block in BACKLOG.md or are missing a CHANGELOG.md entry. These were not fully closed at ship time. Complete the cleanup now: remove matrix row AND detail block, write the CHANGELOG.md entry.
2. For each Decided Against ticket, check whether its Rejected ADR exists:

   ```
   grep -cE "^\*\*Ticket:\*\* MATTGPT-${ID}[[:space:]]*\$" docs/ADR.md
   ```

   Only this exact marker line counts; a ticket ID mentioned anywhere else in ADR.md is not a match. A count of 1 means remove the ticket's matrix row, detail block, and roadmap entry, if it has one, in the same edit. A count of 0 means leave the ticket for Architecture Sync. List only tickets with a count of 1; tickets still waiting produce no output.
3. If the explanatory note under `## Decided Against` still says tickets stay there permanently, propose rewording it: tickets wait there until Architecture Sync writes their Rejected ADR, then leave. Once no Decided Against tickets remain, propose removing the empty table, the note, and the section headers.
4. Update `<!-- last-backlog-sync: <sha> -->` to `<end>`.
5. Run `python3 .claude/skills/mattgpt-docs-check/check_docs.py` and include the report. Findings in files this pass owns go into this pass's proposed diff; everything else gets flagged to Matt.
6. Nothing writes until Matt approves the proposed diff.
7. After Matt approves, write the files, stage `BACKLOG.md` and `CHANGELOG.md` by name, show Matt the commit message, and commit on his OK. Use repeated `-m` arguments for multi-paragraph messages. Never push.
