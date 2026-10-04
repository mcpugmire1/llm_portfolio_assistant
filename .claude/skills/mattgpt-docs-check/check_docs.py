#!/usr/bin/env python3
"""Report-only MattGPT docs check. Never edits files; exit code is always 0.

History markers are checked in CLAUDE.md, ARCHITECTURE.md and .claude/rules/*.md.
BACKLOG.md gets the link check only: dated evidence in ticket bodies is by design.
docs/ADR.md, CHANGELOG.md and archive/ are append-only history and are not checked.
"""

import os
import re
import subprocess
import sys
from urllib.parse import unquote

CURRENT_STATE = ["CLAUDE.md", "ARCHITECTURE.md", "BACKLOG.md"]
RULES_DIR = ".claude/rules"
BUDGET = {"ARCHITECTURE.md": 2000}
MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|"
    r"Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?"
)
TICKET = re.compile(r"MATTGPT-\d+")
INCIDENT = re.compile(
    rf"\({MONTH}[^)]*20\d\d[^)]*\)"
)  # any "(Month ... YYYY ...)" parenthetical, incl. "(May 2026)"
DATE = re.compile(
    rf"\b{MONTH} (?:\d{{1,2}}(?:-\d{{1,2}})?,? )?20\d\d\b|\b20\d\d-\d\d-\d\d\b"
)
FENCE = re.compile(r"^(```|~~~)")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def git(*a):
    return subprocess.run(
        ["git", *a], capture_output=True, text=True, check=True
    ).stdout


def tracked():
    files = set(git("ls-files", "-z").split("\0")) - {""}
    dirs = {d for f in files for d in [os.path.dirname(f)] if d}
    for d in list(dirs):
        while d:
            dirs.add(d)
            d = os.path.dirname(d)
    return files, dirs


def current_state_files():
    out = [f for f in CURRENT_STATE if os.path.exists(f)]
    if os.path.isdir(RULES_DIR):
        out += sorted(
            f"{RULES_DIR}/{p}" for p in os.listdir(RULES_DIR) if p.endswith(".md")
        )
    return out


def links(md, files, dirs):
    bad, in_fence = [], False
    for n, line in enumerate(open(md, encoding="utf-8").read().splitlines(), 1):
        if FENCE.match(line.lstrip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for t in LINK.findall(line):
            if t.startswith("#") or SCHEME.match(t):
                continue
            p = unquote(t.split("#", 1)[0].split("?", 1)[0])
            if not p:
                continue
            r = os.path.normpath(
                p.lstrip("/")
                if p.startswith("/")
                else os.path.join(os.path.dirname(md), p)
            )
            if not r.startswith("..") and r not in files and r not in dirs:
                bad.append(f"{md}:{n}: '{t}' is not a tracked path")
    return bad


def inbound(target, files):
    hits = []
    for md in sorted(f for f in files if f.endswith(".md") and f != target):
        if not os.path.exists(md):
            continue
        for n, line in enumerate(
            open(md, encoding="utf-8", errors="replace").read().splitlines(), 1
        ):
            for t in LINK.findall(line):
                p = unquote(t.split("#", 1)[0])
                if p and os.path.normpath(
                    os.path.join(os.path.dirname(md), p)
                ) == os.path.normpath(target):
                    hits.append(f"{md}:{n}")
    return hits


def main(extra):
    files, dirs = tracked()
    cs = current_state_files()
    print("== History markers in current-state files ==")
    for f in cs:
        if f == "BACKLOG.md":
            continue  # ticket bodies carry dated evidence by design; links still checked below
        for n, line in enumerate(open(f, encoding="utf-8").read().splitlines(), 1):
            kinds = []
            if TICKET.search(line):
                kinds.append("ticket")
            if INCIDENT.search(line):
                kinds.append("incident")
            elif DATE.search(line):
                kinds.append("date (fact or history?)")
            if kinds:
                print(f"  {f}:{n} [{', '.join(kinds)}] {line.strip()[:110]}")
    print("\n== Broken links ==")
    for f in cs + [e for e in extra if e.endswith(".md") and os.path.exists(e)]:
        for b in links(f, files, dirs):
            print(f"  {b}")
    print("\n== Size ==")
    for f, cap in BUDGET.items():
        if os.path.exists(f):
            n = sum(1 for _ in open(f, encoding="utf-8"))
            print(f"  {f}: {n} lines (budget {cap}){'  OVER' if n > cap else ''}")
    for e in extra:
        print(f"\n== Inbound links to {e} (fix before moving or deleting it) ==")
        for h in inbound(e, files):
            print(f"  {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
