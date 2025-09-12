import pandas as pd
import re

# === Config ===
INPUT_FILE = "MPugmire - STAR Stories - 12JUL25_5p_summaries_synthesized.xlsx"
SHEET_NAME = "Sheet1"
OUTPUT_FILE = "MPugmire - STAR Stories - 12JUL25_5p_columns_extracted.xlsx"

# === Load Excel ===
df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

# === Regex Patterns ===
patterns = {
    "Person": r"\*\*Person:\*\*\s*(.+)",
    "Place": r"\*\*Place:\*\*\s*(.+)",
    "Purpose": r"\*\*Purpose:\*\*\s*(.+)",
    "Performance": r"\*\*Performance:\*\*\s*((?:- .+\n?)*)",
    "Process": r"\*\*Process:\*\*\s*((?:- .+\n?)*)",
    "5PSummary": r"\*\*5P Summary:\*\*\s*(.+)",
}


# === Extract and populate columns ===
def extract_5p_components(summary):
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, summary, re.MULTILINE)
        extracted[key] = match.group(1).strip() if match else ""
    return extracted


# Apply to rows with markdown summaries
for idx, row in df.iterrows():
    summary = str(row.get("5PSummary", ""))
    if summary.startswith("**Person:**"):
        extracted = extract_5p_components(summary)
        for key in extracted:
            df.at[idx, key] = extracted[key]

# Save result
df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Extracted 5P columns written to: {OUTPUT_FILE}")
