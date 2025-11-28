import json

import pandas as pd

EXCEL_FILE = "MPugmire - STAR Stories - 16JUL25924AM.xlsx"
JSONL_FILE = "echo_star_stories_nlp.jsonl"
OUTPUT_EXCEL_FILE = "MPugmire - STAR Stories - 16JUL25-NLP-Updated.xlsx"
SHEET_NAME = "STAR Stories - Interview Ready"

# Load Excel
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

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
