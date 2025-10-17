"""
generate_public_tags.py

Enriches STAR stories with semantic `public_tags` using OpenAI GPT-based NLP.

Input:  echo_star_stories.jsonl (base data from Excel)
Output: echo_star_stories_nlp.jsonl (enriched with AI-generated tags)

This is step 2 in the data pipeline:
  1. Excel → generate_jsonl_from_excel.py → echo_star_stories.jsonl
  2. echo_star_stories.jsonl → generate_public_tags.py → echo_star_stories_nlp.jsonl
  3. echo_star_stories_nlp.jsonl → build_custom_embeddings.py → Pinecone/FAISS
"""

import json
import os
import shutil
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

import tiktoken

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

# Initialize OpenAI client
client = OpenAI(api_key=api_key, project=project_id, organization=org_id)

INPUT_FILE = "echo_star_stories.jsonl"
OUTPUT_FILE = "echo_star_stories_nlp.jsonl"  # Overwrites original after backup
MODEL = "gpt-4"  # Use GPT-4 for richer tags


# ---------------------------
# Helper: NLP-based tagger
# ---------------------------
def extract_semantic_tags(story):
    prompt = (
        "You are an intelligent assistant that analyzes STAR stories for professional tagging.\n\n"
        "Given the following data, generate a concise, comma-separated list of **semantic tags** that capture:\n"
        "- Technical skills and methodologies\n"
        "- Business capabilities and outcomes\n"
        "- Leadership, transformation, or collaboration themes\n"
        "- Keywords useful for semantic search (aligned with SFIA, O*NET, LinkedIn, Accenture Tech Vision, etc)\n\n"
        "**Avoid repeating section headers or general terms. Be specific, insightful, and consistent.**\n\n"
        f"Title: {story.get('Title', '')}\n"
        f"Use Cases: {story.get('Use Case(s)', '')}\n"
        f"Situation: {story.get('Situation', [''])[0]}\n"
        f"Task: {story.get('Task', [''])[0]}\n"
        f"Action: {' '.join(story.get('Action', []))}\n"
        f"Result: {' '.join(story.get('Result', []))}\n\n"
        "Output only the semantic tags as a comma-separated string."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error generating tags for story ID {story.get('id')}: {e}")
        return ""


# ---------------------------
# Main enrichment process
# ---------------------------
def enrich_stories_with_nlp_tags():
    enriched_records = []

    with open(INPUT_FILE, "r", encoding="utf-8") as infile:
        for line in infile:
            story = json.loads(line)

            print(f"🔍 Processing story ID {story.get('id')}...")

            tags = extract_semantic_tags(story)
            existing_tags = story.get("public_tags", "")
            all_tags = set()

            enriched_records.append(story)

    # Backup before overwriting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{OUTPUT_FILE.replace('.jsonl', '')}_backup_{timestamp}.jsonl"
    shutil.copy(INPUT_FILE, backup_file)
    print(f"\n📦 Backup created: {backup_file}")

    # Write enriched records
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for record in enriched_records:
            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("\n🎉 Done! NLP-enhanced tags now stored in `public_tags`.")
    print(f"📄 Output file: {OUTPUT_FILE}")


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    enrich_stories_with_nlp_tags()
