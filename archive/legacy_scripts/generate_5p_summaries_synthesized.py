import os
import time

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT_ID"),
    organization=os.getenv("OPENAI_ORG_ID"),
)

# === Configuration ===
INPUT_FILE = "MPugmire - STAR Stories - 12JUL25.xlsx"
INPUT_SHEET = "STAR Stories - Interview Ready"
OUTPUT_FILE = "MPugmire - STAR Stories - 12JUL25_5p_summaries_synthesized.xlsx"
OPENAI_MODEL = "gpt-4"

# === Load Excel ===
df = pd.read_excel(INPUT_FILE, sheet_name=INPUT_SHEET)


# === Helper ===
def generate_5p_fields(row):
    situation = str(row.get("Situation", "")).strip()
    task = str(row.get("Task", "")).strip()
    action = str(row.get("Action", "")).strip()
    result = str(row.get("Result", "")).strip()
    existing_person = str(row.get("Person", "")).strip()

    prompt = f"""
    Based on the STAR story below, generate the 5P fields in markdown format.

    Use this format:
    **Person:** ...
    **Place:** ...
    **Purpose:** ...
    **Performance:**
    - ...
    **Process:**
    - ...
    **5P Summary:** I help [Person] at [Place] accomplish [Purpose], as measured by [Performance], by doing [Process]

    Use the existing Person field if it's informative: "{existing_person}"

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
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured 5P fields from STAR stories.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error generating 5P fields:", e)
        return ""


# === Filter for rows to update ===
target_rows = df[df["5P Retrofit Status"] == "Not Started"].copy()

# === Generate and Update ===
updated_rows = []
for idx, row in target_rows.iterrows():
    print(f"Processing row {idx}...")
    markdown = generate_5p_fields(row)
    if markdown:
        df.at[idx, "5PSummary"] = markdown
        df.at[idx, "5P Retrofit Status"] = "Complete"
    updated_rows.append(idx)
    time.sleep(1.2)

# === Output only updated rows ===
output_df = df[df.index.isin(updated_rows)]
output_df.to_excel(OUTPUT_FILE, index=False)
print(f"Saved {len(updated_rows)} updated rows to: {OUTPUT_FILE}")
