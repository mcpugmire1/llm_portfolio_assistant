#!/bin/sh
# Launch the Claude Code Backlog Maintenance session. The role check in
# .githooks/pre-commit lets this session commit only BACKLOG.md and CHANGELOG.md.
MATTGPT_DOCS_SESSION=backlog exec claude --name "BACKLOG" "$@"
