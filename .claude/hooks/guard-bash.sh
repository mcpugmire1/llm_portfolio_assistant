#!/usr/bin/env bash
# PreToolUse guard for Bash calls. Exit 2 blocks the call and sends stderr to Claude.
block() {
  echo "BLOCKED by .claude/hooks/guard-bash.sh: $1 Do not retry by another route. Report this to Matt." >&2
  exit 2
}
command -v jq >/dev/null 2>&1 || block "jq is not installed, so commands cannot be checked. Matt needs to run: brew install jq."

cmd=$(jq -r '.tool_input.command // ""')
has() { printf '%s' "$cmd" | grep -Eq -e "$1"; }

if has 'git([[:space:]]+-[^[:space:]]+([[:space:]]+[^-[:space:]][^[:space:]]*)?)*[[:space:]]+push([[:space:];&|]|$)'; then
  block "git push. Only Matt pushes. Stop after committing."
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
# Known limit: heredoc bodies are scanned as commands. A commit message that
# quotes grep -v and .env together will block; commit it with -F <file>.
# grep -v on a secrets file: block only when grep -v reads a secrets file, in the
# same pipeline segment or downstream of a segment that names one (cat .env | grep -v X).
# Pipelines split on unquoted ; & && || newline, segments on unquoted |, so
# "grep -v ... ; something .env" and patterns like "a|b" are judged correctly.
GREPV_RE='(^|[[:space:]])[a-z]*grep[[:space:]]+([^[:space:]]+[[:space:]]+)*(-[[:alnum:]]*v[[:alnum:]]*|--invert-match)([[:space:]]|$)'
SECRET_FILE_RE='(^|[[:space:]=<"'"'"'])[^[:space:]"'"'"']*(\.env(\.[[:alnum:]_-]+)?|\.pem|\.key|(secret|credential|token|service[-_]?account)[^[:space:]"'"'"'/]*\.(toml|json|ya?ml|env|txt|ini|cfg))["'"'"']?([[:space:]]|$)'
split_cmd() {
  awk -v sq="'" '{
    out=""; q=""; n=length($0)
    for (i=1; i<=n; i++) {
      c=substr($0,i,1); nx=substr($0,i+1,1); pv=substr($0,i-1,1)
      if (q=="") {
        if (c=="\"" || c==sq) { q=c }
        else if (c=="|" && nx=="|") { c="\n"; i++ }
        else if (c=="|") { c="\037" }
        else if (c==";") { c="\n" }
        else if (c=="&" && (pv==">" || nx==">")) { }
        else if (c=="&") { c="\n"; if (nx=="&") i++ }
      } else if (c==q) { q="" }
      out=out c
    }
    print out
  }'
}
while IFS= read -r pipeline; do
  secret_seen=0
  while IFS= read -r seg; do
    printf '%s' "$seg" | grep -Eiq -e "$SECRET_FILE_RE" && secret_seen=1
    if [ "$secret_seen" = 1 ] && printf '%s' "$seg" | grep -Eq -e "$GREPV_RE"; then
      block "grep -v on a secrets file. Use positive include filters that print key names only."
    fi
  done < <(printf '%s\n' "$pipeline" | tr '\037' '\n')
done < <(printf '%s\n' "$cmd" | split_cmd)
exit 0
