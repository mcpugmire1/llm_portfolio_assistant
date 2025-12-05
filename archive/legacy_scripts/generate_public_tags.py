import os

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

# Initialize OpenAI client
client = OpenAI(api_key=api_key, project=project_id, organization=org_id)

INPUT_EXCEL = "MPugmire - STAR Stories - 14JUL25.xlsx"
OUTPUT_EXCEL = "MPugmire - STAR Stories - Tagged.xlsx"

MODEL = "gpt-3.5-turbo"

# Read Excel file
df = pd.read_excel(INPUT_EXCEL)


# Define function to generate tags using GPT
def generate_refined_tags(row):
    story = {
        "title": row.get("Title", ""),
        "situation": row.get("Situation", ""),
        "task": row.get("Task", ""),
        "action": row.get("Action", ""),
        "result": row.get("Result", ""),
        "use_cases": row.get("Use Case(s)", ""),
        "category": row.get("Category", ""),
        "sub_category": row.get("Sub-category", ""),
        "competencies": row.get("Competencies", ""),
        "solutions": row.get("Solution / Offering", ""),
        "public_tags": row.get("Public Tags", ""),
        "five_p_summary": row.get("5P Summary", ""),
    }

    prompt = f"""
You are an expert assistant generating semantic search tags to help users find relevant STAR stories.

Given the metadata and summary of a STAR story below, return a comma-separated list of 5–8 concise, discoverable tags.
Tags should align with terminology from SFIA, O*NET, LinkedIn Skills, Accenture Tech Vision, and modern enterprise language.
Focus on clarity, discoverability, and avoiding redundancy.

TITLE: {story['title']}
CATEGORY: {story['category']} / {story['sub_category']}
COMPETENCIES: {story['competencies']}
USE CASE(S): {story['use_cases']}
SOLUTION: {story['solutions']}
EXISTING TAGS: {story['public_tags']}

SITUATION: {story['situation']}
TASK: {story['task']}
ACTION: {story['action']}
RESULT: {story['result']}
5P SUMMARY: {story['five_p_summary']}

Output only the comma-separated list of refined tags.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating tags: {e}")
        return ""


# Apply GPT-based tag generation
tqdm.pandas()
df["Refined Tags"] = df.progress_apply(generate_refined_tags, axis=1)

# Save output
print("\n✅ Saving to:", OUTPUT_EXCEL)
df.to_excel(OUTPUT_EXCEL, index=False)
print("🎯 Done generating refined tags!")
