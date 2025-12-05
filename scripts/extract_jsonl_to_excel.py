import json

import pandas as pd

EXCEL_FILE = "MPugmire - STAR Stories - 01DEC25.xlsx"
JSONL_FILE = "echo_star_stories_nlp.jsonl"
OUTPUT_EXCEL_FILE = "MPugmire - STAR Stories - 01DEC25_PTags.xlsx"
SHEET_NAME = "STAR Stories - Interview Ready"

# Load Excel
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

# Filter out empty rows
df = df[df["Title"].notna()].copy()

# Load JSONL
with open(JSONL_FILE, encoding="utf-8") as f:
    jsonl_data = [json.loads(line) for line in f]

# Build a lookup from Title to public_tags
tag_lookup = {
    entry["Title"].strip(): entry.get("public_tags", "") for entry in jsonl_data
}

# Update the DataFrame with new tags
df["Public Tags"] = df["Title"].apply(lambda t: tag_lookup.get(t.strip(), ""))

# Save updated Excel
df.to_excel(OUTPUT_EXCEL_FILE, sheet_name=SHEET_NAME, index=False)

print(f"✅ NLP tags synced to Excel: {OUTPUT_EXCEL_FILE}")
