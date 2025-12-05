# Generate 5P Summaries Without Modifying Master Sheet

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
OUTPUT_FILE = "MPugmire - STAR Stories - 12JUL25_5p_summaries_only.xlsx"
OPENAI_MODEL = "gpt-4"

# === Load Excel ===
df = pd.read_excel(INPUT_FILE, sheet_name=INPUT_SHEET)


# === Helper ===
def generate_5p_summary(row):
    person = str(row.get("Person", "")).strip()
    place = str(row.get("Place", "")).strip()
    purpose = str(row.get("Purpose", "")).strip()
    performance = str(row.get("Performance", "")).strip()
    process = str(row.get("Process", "")).strip()

    def format_bullets(text):
        items = [f"- {item.strip()}" for item in text.split(';') if item.strip()]
        return '\n'.join(items)

    prompt = f"""
    You are formatting a STAR story summary into markdown format using the following format:

    **Person:** {person}
    **Place:** {place}
    **Purpose:** {purpose}
    **Performance:**
    {format_bullets(performance)}
    **Process:**
    {format_bullets(process)}

    Format this into a clean, readable 5P markdown summary.
    """

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that formats 5P summaries.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error generating summary:", e)
        return ""


# === Apply to Not Started Only ===
not_started = df[df["5P Retrofit Status"] == "Not Started"].copy()

# === Generate Summaries ===
summaries = []
for idx, row in not_started.iterrows():
    print(f"Processing row {idx}...")
    summary = generate_5p_summary(row)
    summaries.append((idx, summary))
    time.sleep(1.2)  # To respect API limits

# === Add to Copy and Save ===
for idx, summary in summaries:
    df.at[idx, "5PSummary"] = summary
    df.at[idx, "5P Retrofit Status"] = "Complete"

output_df = df[df.index.isin([idx for idx, _ in summaries])]
output_df.to_excel(OUTPUT_FILE, index=False)
print(f"Saved {len(summaries)} updated rows to: {OUTPUT_FILE}")
