import json
import os
import shutil
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

print("🔍 DEBUG")
print(f"API Key: '{api_key}' (len={len(api_key)})")
print(f"Project ID: '{project_id}'")
print(f"Org ID: '{org_id}'")

from openai import OpenAI
client = OpenAI(
    api_key=api_key,
    project=project_id,
    organization=org_id
)

# Initialize OpenAI client with API key from environment variable

INPUT_FILE = "echo_star_stories.jsonl"
OUTPUT_FILE = "echo_star_stories.jsonl"  # Will be overwritten after backup
MODEL = "gpt-3.5-turbo"  # Or use "gpt-4" if you prefer

def summarize_star(story):
    prompt = (
        "You are a helpful assistant summarizing STAR stories for interview preparation.\n\n"
        "Summarize the following STAR story in a natural, interview-ready way. Make it conversational, include nuance, and avoid just repeating section headers. Here's the data:\n\n"
        f"Situation: {story.get('Situation', [''])[0]}\n"
        f"Task: {story.get('Task', [''])[0]}\n"
        f"Action: {' '.join(story.get('Action', []))}\n"
        f"Result: {' '.join(story.get('Result', []))}\n\n"
        "Output the summary as a single paragraph."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error summarizing story ID {story.get('id')}: {e}")
        return ""

def enrich_stories_with_content():
    enriched_records = []

    with open(INPUT_FILE, "r", encoding="utf-8") as infile:
        for line in infile:
            story = json.loads(line)
            if not story.get("content"):
                print(f"🔄 Summarizing story ID {story.get('id')}...")
                story["content"] = summarize_star(story)
            enriched_records.append(story)

    # Backup before overwrite
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_filename = f"{OUTPUT_FILE.replace('.jsonl', '')}_backup_{timestamp}.jsonl"
    shutil.copy(INPUT_FILE, archive_filename)
    print(f"📦 Backup created: {archive_filename}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for record in enriched_records:
            outfile.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    print("\n✅ Done! File updated with content field.")
    print(f"📄 Final output: {OUTPUT_FILE}")
    print("📌 You can now run: python build_custom_embeddings.py")

if __name__ == "__main__":
    enrich_stories_with_content()