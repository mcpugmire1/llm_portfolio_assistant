"""
Script to generate structured 5P summaries (Person, Place, Purpose, Performance, Process) for STAR stories using OpenAI's GPT model.
Preserves the 'Person' field as-is and outputs results in markdown format.
Only processes rows where '5P Retrofit Status' is marked 'Not Started'.
"""

import pandas as pd
from openai import OpenAI
import time
from dotenv import load_dotenv
import os

# === Load environment variables and authenticate OpenAI ===
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT_ID"),
    organization=os.getenv("OPENAI_ORG_ID")
)

# === Configuration ===
INPUT_FILE = "MPugmire - STAR Stories - 12JUL25.xlsx"  # Master STAR stories file
INPUT_SHEET = "STAR Stories - Interview Ready"
OUTPUT_FILE = "MPugmire - STAR Stories - 12JUL25_5p_summaries_preserve_person.xlsx"
OPENAI_MODEL = "gpt-4"

# === Load Excel ===
df = pd.read_excel(INPUT_FILE, sheet_name=INPUT_SHEET)

# === Helper ===
def generate_5p_fields(row):
    """
    Generates 5P fields in markdown format using OpenAI GPT, preserving the existing 'Person' value.
    
    Args:
        row (pd.Series): A single row from the STAR story DataFrame containing STAR fields.

    Returns:
        str: The markdown-formatted 5P content, or an empty string if generation fails.
    """
    person = str(row.get("Person", "")).strip()
    situation = str(row.get("Situation", "")).strip()
    task = str(row.get("Task", "")).strip()
    action = str(row.get("Action", "")).strip()
    result = str(row.get("Result", "")).strip()

    prompt = f"""
Based on the STAR story below, generate the following 5P fields in markdown format.
Use the existing Person value exactly as provided: **Person:** {person}

Output format:
**Person:** {person}
**Place:** ...
**Purpose:** ...
**Performance:**
- ...
**Process:**
- ...
**5P Summary:** I help {person} at [Place] accomplish [Purpose], as measured by [Performance], by doing [Process]

STAR Story:
Situation: {situation}
Task: {task}
Action: {action}
Result: {result}
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured 5P fields from STAR stories."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error generating 5P fields:", e)
        return ""

# === Filter for rows to update ===
target_rows = df[df["5P Retrofit Status"] == "Not Started"].copy()

# === Generate and Update ===
updated_rows = []
for idx, row in target_rows.iterrows():
    print(f"🛠️ Processing row {idx}...")
    markdown = generate_5p_fields(row)
    if markdown:
        df.at[idx, "5PSummary"] = markdown
        df.at[idx, "5P Retrofit Status"] = "Complete"
    updated_rows.append(idx)
    time.sleep(1.2)  # Respect OpenAI rate limits

# === Output only updated rows ===
output_df = df[df.index.isin(updated_rows)]
output_df.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Saved {len(updated_rows)} updated rows to: {OUTPUT_FILE}")