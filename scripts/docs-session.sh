#!/bin/sh
# Launch a Claude Code docs session. The role check in .githooks/pre-commit
# lets this session commit only ARCHITECTURE.md, docs/ADR.md, BACKLOG.md and CHANGELOG.md.
MATTGPT_DOCS_SESSION=1 exec claude "$@"
