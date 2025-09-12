import os
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()  # ✅ This loads variables from .env into os.environ

# Initialize OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# File paths
input_file = "MPugmire - STAR Stories - 18JUN25.xlsx"
output_file = "MPugmire - STAR Stories - 5P - OUTPUT.xlsx"

# Load Excel
df = pd.read_excel(input_file, sheet_name="STAR Stories - Interview Ready")


# Utility: Is field filled
def is_filled(val):
    return isinstance(val, str) and val.strip() != ""


def infer_place(client, category):
    if client == "Multiple Clients":
        category = category.lower()
        if "healthcare" in category:
            return "U.S. healthcare providers"
        elif "financial" in category:
            return "leading global banks"
        elif (
            "innovation" in category
            or "liquid studio" in category
            or "cloud innovation center" in category
        ):
            return "Fortune 500 innovation teams"
        elif "public sector" in category:
            return "government agencies and regulators"
        elif "technology" in category:
            return "enterprise IT organizations"
        else:
            return "enterprise organizations"
    return client


# Prompt generator
def generate_prompt(star_text, place=None):
    note = f'Note: The organization type (Place) is likely "{place}".' if place else ""
    return f"""You're helping write a short, clear 5P summary from this STAR story. 
Break it into:
1. Person (the role or title of the person being helped),
2. Place (type of organization),
3. Purpose (the business goal),
4. Performance (measurable results),
5. Process (how it was done).

Then write a 5PSummary in this format:
"I help [Person] at [Place] accomplish [Purpose], as measured by [Performance], by doing [Process]."

STAR story:
\"\"\"{star_text}\"\"\"

{note}
"""


# Field extractor
def extract(label, text):
    match = re.search(rf"{label}:\s*(.*)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


# Process rows
for idx, row in df.iterrows():
    if all(
        is_filled(row[col])
        for col in ["Person", "Place", "Purpose", "Performance", "Process", "5PSummary"]
    ):
        continue

    story = " ".join(
        [str(row.get(fld, "")) for fld in ["Situation", "Task", "Action", "Result"]]
    ).strip()
    place_override = infer_place(row["Client"], row["Category"])
    prompt = generate_prompt(story, place_override)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()

        # Extract and fill values
        person = extract("Person", content)
        place = extract("Place", content)
        df.at[idx, "Person"] = person if person else "digital and technology executives"
        df.at[idx, "Place"] = place if place else "enterprise organizations"
        df.at[idx, "Purpose"] = extract("Purpose", content)
        df.at[idx, "Performance"] = extract("Performance", content)
        df.at[idx, "Process"] = extract("Process", content)
        df.at[idx, "5PSummary"] = extract("5PSummary", content)

        print(f"✅ Processed row {idx}")
        time.sleep(1)

    except Exception as e:
        print(f"⚠️ Error on row {idx}: {e}")
        continue

# Save output
df.to_excel(output_file, index=False)
print(f"📝 Finished writing to: {output_file}")
