#!/usr/bin/env bash
# PreToolUse guard for Bash calls. Exit 2 blocks the call and sends stderr to Claude.
block() {
  echo "BLOCKED by .claude/hooks/guard-bash.sh: $1 Do not retry by another route. Report this to Matt." >&2
  exit 2
}
command -v jq >/dev/null 2>&1 || block "jq is not installed, so commands cannot be checked. Matt needs to run: brew install jq."

cmd=$(jq -r '.tool_input.command // ""')
has() { printf '%s' "$cmd" | grep -Eq -e "$1"; }

if has 'git[[:space:]]+commit' && has 'git[[:space:]]+push'; then
  block "git commit and git push in one call. Commit, stop, and wait for an explicit push instruction."
fi
if has 'git[[:space:]]+add([[:space:]]+[^;&|]*)?[[:space:]](-A|--all|\.)([[:space:];&|]|$)'; then
  block "git add -A, --all, or . stages everything. Stage specific files by name."
fi
if has '--no-verify'; then
  block "--no-verify skips the repo's git hooks."
fi
if has 'core\.hooksPath'; then
  block "changing core.hooksPath disables the repo's git hooks."
fi
if has 'grep[[:space:]]+([^|;&]*[[:space:]])?(-[a-zA-Z]*v|--invert-match)' \
   && printf '%s' "$cmd" | grep -Eiq -e 'secret|credential|token|\.env|service[-_]?account'; then
  block "grep -v on a secrets file. Use positive include filters that print key names only."
fi
exit 0
