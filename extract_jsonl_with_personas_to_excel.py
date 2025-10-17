import pandas as pd
import json

EXCEL_FILE = "MPugmire - STAR Stories - 06AUG25.xlsx"
JSONL_FILE = "echo_star_stories_nlp_with_personas.jsonl"
OUTPUT_EXCEL_FILE = "MPugmire - STAR Stories - 04OCT25-Personas -Updated.xlsx"
SHEET_NAME = "STAR Stories - Interview Ready"

# Load Excel
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

# Load JSONL
with open(JSONL_FILE, "r", encoding="utf-8") as f:
    jsonl_data = [json.loads(line) for line in f]

# Build a lookup from Title to personas (convert list to comma-separated string)
tag_lookup = {
    entry["Title"].strip(): ", ".join(entry.get("personas", [])) 
    for entry in jsonl_data
}

# Update the DataFrame with new personas
df["personas"] = df["Title"].apply(lambda t: tag_lookup.get(t.strip(), ""))

# Save updated Excel
df.to_excel(OUTPUT_EXCEL_FILE, sheet_name=SHEET_NAME, index=False)

print(f"✅ Personas synced to Excel: {OUTPUT_EXCEL_FILE}")
