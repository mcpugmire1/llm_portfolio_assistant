import pandas as pd
import json

INPUT_EXCEL_FILE = "MPugmire - STAR Stories - 16JUL25924AM.xlsx"
OUTPUT_JSONL_FILE = "echo_star_stories.jsonl"
SHEET_NAME = "STAR Stories - Interview Ready"

def excel_to_jsonl():
    df = pd.read_excel(INPUT_EXCEL_FILE, sheet_name=SHEET_NAME)

    # Drop rows with no Title (assumes finalized stories always have one)
    df = df[df['Title'].notna()]

    records = []

    for idx, row in df.iterrows():
        record = {
            "id": str(idx),
            "Title": str(row.get("Title", "")).strip(),
            "Client": str(row.get("Client", "")).strip(),
            "Role": str(row.get("Role", "")).strip(),
            "Category": str(row.get("Category", "")).strip(),
            "Sub-category": str(row.get("Sub-category", "")).strip(),
            "Competencies": [s.strip() for s in str(row.get("Competencies", "")).split(",") if s.strip()],
            "Solution / Offering": str(row.get("Solution / Offering", "")).strip(),
            "Use Case(s)": [s.strip() for s in str(row.get("Use Case(s)", "")).split(";") if s.strip()],
            "Situation": [str(row.get("Situation", "")).strip()],
            "Task": [str(row.get("Task", "")).strip()],
            "Action": [str(row.get("Action", "")).strip()],
            "Result": [str(row.get("Result", "")).strip()],
            "public_tags": str(row.get("Public Tags", "")).strip(),
            "Person": str(row.get("Person", "")).strip(),
            "Place": str(row.get("Place", "")).strip(),
            "Purpose": str(row.get("Purpose", "")).strip(),
            "Performance": [s.strip() for s in str(row.get("Performance", "")).split("- ") if s.strip()],
            "Process": [s.strip() for s in str(row.get("Process", "")).split("- ") if s.strip()],
            "5PSummary": str(row.get("5PSummary", "")).strip(),
            "content": ""  # will be filled in by script 2 - need to determine if this is still needed
        }
        records.append(record)

    with open(OUTPUT_JSONL_FILE, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("✅ JSONL export complete.")
    print(f"📄 Output file: {OUTPUT_JSONL_FILE}")
    print("📌 Ready to run generate_content_field.py next.")

if __name__ == "__main__":
    excel_to_jsonl()