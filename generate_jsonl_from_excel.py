# --------------------------------------------------------
# Ingestion: Excel master -> echo_star_stories.jsonl
#
# Input:    the current master xlsx in repo root, auto-detected by glob.
#           Run refresh_master.py DDMONYY first to place it.
# Sheet:    SHEET_NAME below (usually "STAR Stories - Interview Ready").
# Dry-run:  set DRY_RUN = True to preview without writing.
# Backups:  the previous JSONL is copied to archive/jsonl-backups/ before
#           overwrite. Repo root stays clean.
#
# The JSONL is rebuilt from the Excel master on every run: nothing from the
# prior JSONL carries over. id is the Title|Client slug.
# Only run when new or updated stories need to be synced.
# --------------------------------------------------------

import json
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

# ---------- config ----------
# MATTGPT-216 (Aug 28, 2026): master-xlsx auto-detection moved into
# excel_to_jsonl() below so importing this module does not raise
# SystemExit when the master isn't present (breaks CI + unit tests that
# import this module). Script UX unchanged -- running
# `python generate_jsonl_from_excel.py` still fails immediately with the
# same message when the master is missing.

OUTPUT_JSONL_FILE = "echo_star_stories.jsonl"
SHEET_NAME = "STAR Stories - Interview Ready"
DRY_RUN = False  # ✅ Change to False when ready to write output

# Backups land in archive/jsonl-backups/ (gitignored). Repo root stays clean.
ARCHIVE_BACKUPS_DIR = Path("archive/jsonl-backups")

# ---------- helpers ----------


def load_existing_jsonl(path: str) -> list[dict]:
    """Load the existing JSONL's records, in file order, for the change report."""
    records: list[dict] = []
    if not os.path.exists(path):
        return records
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            records.append(json.loads(line))
    return records


def backup_file(path: str):
    if os.path.exists(path):
        ts = datetime.now(UTC).strftime("%Y-%m-%dT%H_%M_%SZ")
        # Write directly into archive/jsonl-backups/ so backups never
        # accumulate in repo root. Directory is expected to exist.
        backup_path = str(ARCHIVE_BACKUPS_DIR / f"{Path(path).name}.bak-{ts}")
        shutil.copy2(path, backup_path)
        print(f"🛟 Backup written: {backup_path}")


# Utility functions (inlined from old utils.py)
def normalize(s) -> str:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return str(s).strip()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def strip_markdown_bold(text: str) -> str:
    """Strip ** markdown bold markers from text.

    Excel may contain **bold** markers for human readability,
    but these cause malformed markdown when LLM re-wraps them.
    Clean during export so LLM never sees them.
    """
    return text.replace("**", "") if text else text


def split_bullets(value: str):
    """Split multi-line bullet fields, removing Excel apostrophe prefix but preserving indentation."""
    if not value:
        return []

    value = str(value)

    # Strip Excel escape apostrophe before dashes globally, preserving whitespace
    # '  - becomes   - (keeps indentation)
    # '- becomes - (no indentation to keep)
    value = re.sub(r"'(\s*)-", r"\1-", value)

    # Strip markdown bold markers
    value = strip_markdown_bold(value)

    # Split on newlines
    lines = value.split("\n")
    parts = []

    for line in lines:
        line = (
            line.rstrip()
        )  # Only strip trailing whitespace, preserve leading (indentation)
        if line:
            parts.append(line)

    return parts


# ---------- main ----------


def excel_to_jsonl():
    # Auto-detect the current master. refresh_master.py enforces that
    # exactly one file matches this pattern in the repo root by archiving any
    # previous master before copying the new one in. If this assertion fails,
    # either two masters are present (run refresh_master again) or none are
    # (run refresh_master with the current date).
    master_matches = sorted(Path(".").glob("MPugmire - STAR Stories - *.xlsx"))
    if len(master_matches) != 1:
        raise SystemExit(
            f"Expected exactly one master xlsx in repo root, found {len(master_matches)}: "
            f"{[m.name for m in master_matches]}. "
            "Run refresh_master.py DDMONYY to normalize."
        )
    input_excel_file = str(master_matches[0])

    print(
        f"\n🚦 DRY_RUN = {DRY_RUN} — {'No file will be written' if DRY_RUN else 'Output will be saved to disk'}"
    )

    # Load existing JSONL for the change report
    existing_records = load_existing_jsonl(OUTPUT_JSONL_FILE)

    # Backup current JSONL before overwriting
    backup_file(OUTPUT_JSONL_FILE)

    # Load Excel
    df = pd.read_excel(input_excel_file, sheet_name=SHEET_NAME)

    # Drop rows with no Title (assumes finalized stories always have one)
    df = df[df["Title"].notna()].copy()

    out_records = []

    for _, row in df.iterrows():
        title = normalize(row.get("Title", ""))
        client = normalize(row.get("Client", ""))

        # Base fields from Excel
        rec_from_excel = {
            "Title": title,
            "Employer": normalize(row.get("Employer", "")),
            "Division": normalize(row.get("Division", "")),
            "Role": normalize(row.get("Role", "")),
            "Client": client,
            "Project": normalize(row.get("Project", "")),
            "Start_Date": normalize(row.get("Start_Date", "")),
            "End_Date": normalize(row.get("End_Date", "")),
            "Industry": normalize(row.get("Industry", "")),
            "Theme": normalize(row.get("Theme", "")),
            "Era": normalize(row.get("Era", "")),
            "Solution / Offering": normalize(row.get("Solution / Offering", "")),
            "Project Scope / Complexity": normalize(
                row.get("Project Scope / Complexity", "")
            ),
            "Category": normalize(row.get("Category", "")),
            "Sub-category": normalize(row.get("Sub-category", "")),
            "Competencies": [
                s.strip()
                for s in str(row.get("Competencies", "")).split(",")
                if s and s.strip()
            ],
            "Use Case(s)": [
                s.strip()
                for s in str(row.get("Use Case(s)", "")).split(";")
                if s and s.strip()
            ],
            "Interview Questions": [
                s.strip()
                for s in str(row.get("Interview Questions", "")).split(";")
                if s and s.strip()
            ],
            "Situation": split_bullets(normalize(row.get("Situation", ""))),
            "Task": split_bullets(normalize(row.get("Task", ""))),
            "Action": split_bullets(normalize(row.get("Action", ""))),
            "Result": split_bullets(normalize(row.get("Result", ""))),
            "public_tags": normalize(row.get("Public Tags", "")),
            "Person": normalize(row.get("Person", "")),
            "Place": normalize(row.get("Place", "")),
            "Purpose": normalize(row.get("Purpose", "")),
            "Performance": split_bullets(normalize(row.get("Performance", ""))),
            "Process": split_bullets(normalize(row.get("Process", ""))),
            "5PSummary": normalize(row.get("5PSummary", "")),
            # content is often generated later; Excel usually doesn't contain it
            "content": "",  # placeholder
        }

        record = {}

        # Always use sluggified id based on Title|Client, even if one exists already
        record["id"] = f"{slugify(title)}|{slugify(client)}"

        # Copy all base fields from Excel first
        record.update(rec_from_excel)

        out_records.append(record)

    # === PREVIEW OR WRITE OUTPUT JSONL ===
    out_ids = [rec["id"] for rec in out_records]
    existing_ids = [rec.get("id") for rec in existing_records if "id" in rec]
    new_ids = set(out_ids) - set(existing_ids)

    created, updated, unchanged = len(new_ids), 0, 0
    print(f"\n--- 🆕 Created ({len(new_ids)}) ---")
    for rec in out_records:
        if rec["id"] in new_ids:
            print(f"[id={rec['id']}] Title: {rec.get('Title', '')}")

    print("\n--- 🔍 Detailed Changes ---")
    for rec in out_records:
        rec_id = rec["id"]
        if rec_id in new_ids:
            continue  # Already listed

        # Find matching existing record
        old = next((r for r in existing_records if r.get("id") == rec_id), None)
        if not old:
            continue  # Shouldn't happen

        diffs = []
        for field in rec:
            if field in ["id", "content"]:
                continue
            new_val = rec[field]
            old_val = old.get(field)
            if new_val != old_val:
                diffs.append((field, old_val, new_val))

        print(f"\n[id={rec_id}] Changes:")
        if not diffs:
            print("  • No changes detected.")
            unchanged += 1
        else:
            updated += 1
            for field, old_val, new_val in diffs:
                print(f"  • {field} changed:")
                print(f"    OLD: {json.dumps(old_val, ensure_ascii=False)}")
                print(f"    NEW: {json.dumps(new_val, ensure_ascii=False)}")

    print(f"\n📊 Total records processed: {len(out_records)}")
    print(f"➕ Created: {created}  🔁 Updated: {updated}  ✅ Unchanged: {unchanged}")

    if DRY_RUN:
        print(
            "\n🛑 DRY RUN MODE: No file written. Set DRY_RUN = False to save changes."
        )
    else:
        with open(OUTPUT_JSONL_FILE, "w", encoding="utf-8") as f:
            for rec in out_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("✅ JSONL export complete.")
        print(f"📄 Output file: {OUTPUT_JSONL_FILE}")
        print(
            "📌 Safe to run content/tag enrichment next. The JSONL is rebuilt from the Excel master on every run."
        )


if __name__ == "__main__":
    excel_to_jsonl()
