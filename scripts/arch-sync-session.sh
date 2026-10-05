#!/bin/sh
# Launch the Claude Code Architecture Sync session. The role check in
# .githooks/pre-commit lets this session commit only ARCHITECTURE.md and docs/ADR.md.
MATTGPT_DOCS_SESSION=arch exec claude "$@"
