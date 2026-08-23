"""Refresh the local master STAR Stories xlsx from OneDrive.

Usage:
    python refresh_master.py DDMONYY

Example:
    python refresh_master.py 21AUG26

Behavior:
    1. Asserts exactly one "MPugmire - STAR Stories - {DATE}.xlsx" exists in
       the OneDrive source directory.
    2. Refuses to overwrite: fails if the same filename already exists in the
       repo root.
    3. Archives any existing "MPugmire - STAR Stories - *.xlsx" files in the
       repo root to archive/star-stories-versions/.
    4. Copies the OneDrive file into the repo root.

Nothing writes to git. The archive directory holds gitignored history; the
current master in repo root is what generate_jsonl_from_excel.py picks up via
its glob-and-assert-exactly-one check.
"""

import shutil
import sys
from pathlib import Path

ONEDRIVE_DIR = Path(
    "/Users/matthewpugmire/OneDrive/Documents/Career Hub/Content Vault/Storytelling & Anecdotes"
)
REPO_ROOT = Path("/Users/matthewpugmire/Projects/portfolio/llm_portfolio_assistant")
ARCHIVE_DIR = REPO_ROOT / "archive" / "star-stories-versions"
FILENAME_PATTERN = "MPugmire - STAR Stories - {date}.xlsx"


def main(date: str) -> int:
    source_name = FILENAME_PATTERN.format(date=date)
    source = ONEDRIVE_DIR / source_name
    dest = REPO_ROOT / source_name

    # Assert the OneDrive master exists.
    if not source.exists():
        print(f"[refresh_master] source not found: {source}", file=sys.stderr)
        return 1

    # Refuse to overwrite an already-present target.
    if dest.exists():
        print(
            f"[refresh_master] refusing to overwrite existing local file: {dest}",
            file=sys.stderr,
        )
        return 1

    # Archive existing local masters. Do not overwrite in the archive either.
    existing = sorted(REPO_ROOT.glob("MPugmire - STAR Stories - *.xlsx"))
    for old in existing:
        target = ARCHIVE_DIR / old.name
        if target.exists():
            print(
                f"[refresh_master] refusing to overwrite existing archive file: {target}",
                file=sys.stderr,
            )
            return 1
        shutil.move(str(old), str(target))
        print(f"[refresh_master] archived: {old.name} -> {target}")

    # Copy new master in.
    shutil.copy2(str(source), str(dest))
    print(f"[refresh_master] copied:  {source} -> {dest}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python refresh_master.py DDMONYY", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
