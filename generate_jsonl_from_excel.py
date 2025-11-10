# --------------------------------------------------------
# REMINDER:
# Before running, update:
#   INPUT_EXCEL_FILE – path to the latest Excel export
#   SHEET_NAME – usually "STAR Stories - Interview Ready"
#   DRY_RUN – set to False to write output / True to preview only
# Only run if new or updated stories need to be synced.
# This script PRESERVES existing public_tags, content, and IDs.
# --------------------------------------------------------

import pandas as pd
import json
import os
import shutil
from datetime import datetime, timezone
import re

# ---------- config ----------

INPUT_EXCEL_FILE = "MPugmire - STAR Stories - 11NOV25_CLEANED.xlsx"  # <-- update as needed
OUTPUT_JSONL_FILE = "echo_star_stories.jsonl"
SHEET_NAME = "STAR Stories - Interview Ready"
DRY_RUN = False  # ✅ Change to False when ready to write output

# ---------- helpers ----------


def load_existing_jsonl(path: str):
    """
    Load existing JSONL into:
      - records: list of dicts (original order)
      - by_key: dict keyed by (Title|Client) normalized
    """
    records, by_key = [], {}
    if not os.path.exists(path):
        return records, by_key
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append(rec)
            key = f"{slugify(rec.get('Title', ''))}|{slugify(rec.get('Client', ''))}"
            by_key[key] = rec
    return records, by_key


def backup_file(path: str):
    if os.path.exists(path):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H_%M_%SZ")
        backup_path = f"{path}.bak-{ts}"
        shutil.copy2(path, backup_path)
        print(f"🛟 Backup written: {backup_path}")

# Utility functions (inlined from old utils.py)
def normalize(s: str) -> str:
    return (s or "").strip()

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text

def norm_key(title: str, client: str) -> str:
    return f"{normalize(title).lower()}|{normalize(client).lower()}"


def split_bullets(value: str):
    """Split multi-line bullet fields, removing Excel apostrophe prefix."""
    if not value:
        return []
    
    lines = str(value).split("\n")
    parts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove leading apostrophe
        if line.startswith("'"):
            line = line[1:]
        
        parts.append(line)
    
    return parts

# ---------- main ----------


def excel_to_jsonl():
    print(
        f"\n🚦 DRY_RUN = {DRY_RUN} — {'No file will be written' if DRY_RUN else 'Output will be saved to disk'}"
    )

    # Load existing JSONL (to preserve public_tags/content/ids where appropriate)
    existing_records, existing_by_key = load_existing_jsonl(OUTPUT_JSONL_FILE)

    # Backup current JSONL before overwriting
    backup_file(OUTPUT_JSONL_FILE)

    # Load Excel
    df = pd.read_excel(INPUT_EXCEL_FILE, sheet_name=SHEET_NAME)

    # Drop rows with no Title (assumes finalized stories always have one)
    df = df[df["Title"].notna()].copy()

    out_records = []
    created, updated = 0, 0

    for _, row in df.iterrows():
        title = normalize(row.get("Title", ""))
        client = normalize(row.get("Client", ""))
        key = norm_key(title, client)

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
            "Solution / Offering": normalize(row.get("Solution / Offering", "")),
            "Project Scope / Complexity": normalize(row.get("Project Scope / Complexity", "")), 
            "Category": normalize(row.get("Category", "")),
            "Sub-category": normalize(row.get("Sub-category", "")),
            "Competencies": [
                s.strip()
                for s in str(row.get("Competencies", "")).split(",")
                if s and s.strip()
            ],
            "Solution / Offering": normalize(row.get("Solution / Offering", "")),
            "Project Scope / Complexity": normalize(row.get("Project Scope / Complexity", "")), 
            "Use Case(s)": [
                s.strip()
                for s in str(row.get("Use Case(s)", "")).split(";")
                if s and s.strip()
            ],
            "Situation": [normalize(row.get("Situation", ""))],
            "Task": [normalize(row.get("Task", ""))],
            "Action": [normalize(row.get("Action", ""))],
            "Result": [normalize(row.get("Result", ""))],
            "public_tags": normalize(row.get("Public Tags", "")),
            "Person": normalize(row.get("Person", "")),
            "Place": normalize(row.get("Place", "")),
            "Purpose": normalize(row.get("Purpose", "")),
            "Performance": split_bullets(normalize(row.get("Performance", ""))),
            "Process": split_bullets(normalize(row.get("Process", ""))),
            "5PSummary": normalize(row.get("5PSummary", "")),
            # content is often generated later; Excel usually doesn't contain it
            "content": "",  # placeholder; may be preserved from existing
        }

        # Merge with existing (preserve id, public_tags, content when Excel is blank)
        existing = existing_by_key.get(key, {})

        record = {}

        # Always use sluggified id based on Title|Client, even if one exists already
        record["id"] = f"{slugify(title)}|{slugify(client)}"

        # Copy all base fields from Excel first
        record.update(rec_from_excel)

        # Preserve public_tags if Excel is blank
        if not record["public_tags"] and "public_tags" in existing:
            record["public_tags"] = existing.get("public_tags", "")

        # Preserve content if Excel doesn't supply it (it usually doesn't)
        if not record.get("content") and "content" in existing:
            record["content"] = existing.get("content", "")

        # Also preserve any fields we’re not explicitly setting but exist in the old record
        # (e.g., future enrichments)
        for k, v in existing.items():
            if k not in record:
                record[k] = v

        out_records.append(record)
        if existing:
            updated += 1
        else:
            created += 1

    # === PREVIEW OR WRITE OUTPUT JSONL ===
    out_ids = [rec["id"] for rec in out_records]
    existing_ids = [rec.get("id") for rec in existing_records if "id" in rec]
    new_ids = set(out_ids) - set(existing_ids)

    unchanged = 0
    print(f"\n--- 🆕 Created ({len(new_ids)}) ---")
    for rec in out_records:
        if rec["id"] in new_ids:
            print(f"[id={rec['id']}] Title: {rec.get('Title', '')}")

    print(f"\n--- 🔍 Detailed Changes ---")
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
            if field in ["id", "content", "public_tags"]:
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
            "📌 Safe to run content/tag enrichment next; preserves existing data when Excel is blank."
        )


if __name__ == "__main__":
    excel_to_jsonl()
