---
name: "mattgpt-docs-check"
description: "Report-only check that MattGPT's current-state docs hold current state only and that their links resolve to tracked files. Run at the end of Architecture Sync and Backlog Maintenance passes, during a rules contradiction audit, and before moving, archiving, or deleting any .md file. Needs a shell, so Claude Code runs it; other surfaces ask Matt to run the command and paste the output. Never edits files."
---

# MattGPT docs check

From the repo root, run:

    python3 .claude/skills/mattgpt-docs-check/check_docs.py [extra .md paths]

Paste the output in full. The script never edits anything and never blocks a commit; it always exits 0.

## What it checks
1. **History markers.** CLAUDE.md and ARCHITECTURE.md hold current state only. It reports ticket IDs, any "(Month ... YYYY)" parenthetical as an incident note, and other dates under "fact or history?". Some dates are facts (career dates, certification dates); say which each one is.
2. **Links.** Every relative link in CLAUDE.md, ARCHITECTURE.md, BACKLOG.md, and any path passed as an argument must resolve to a path tracked in git, with matching case. A file on disk that is untracked or gitignored counts as broken.
3. **Size.** ARCHITECTURE.md line count against 2,000, the point past which it can't be read in one pass. Report-only.

## Not checked
- BACKLOG.md history markers: dated evidence in ticket bodies is by design. Its links are still checked.
- `docs/ADR.md`, CHANGELOG.md and `archive/`: append-only history. Their links may point at removed files, and that is correct.
- Other .md files, unless passed as an argument.

## Before moving, archiving, or deleting a .md file
Pass the file's path as an argument. The report lists every tracked file that links to it. Fix or remove those links in the same change, and move any durable content into `docs/ADR.md` or CHANGELOG.md first.

## Reporting
Paste the output. For each finding, propose the fix and name the owner: Matt for CLAUDE.md; Architecture Sync for ARCHITECTURE.md; Backlog Maintenance for BACKLOG.md. Don't apply fixes to files outside your own pass's ownership.
