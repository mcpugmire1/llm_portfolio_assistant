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
from datetime import UTC, datetime

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

# Initialize OpenAI client
client = OpenAI(api_key=api_key, project=project_id, organization=org_id)

INPUT_FILE = "echo_star_stories.jsonl"
OUTPUT_FILE = "echo_star_stories_nlp.jsonl"  # Overwrites original after backup
MODEL = "gpt-4o"  # Use GPT-4o for richer tags


# ---------------------------
# Helper: NLP-based tagger
# ---------------------------
def extract_semantic_tags(story):
    prompt = (
        "You are an intelligent assistant that analyzes STAR stories for professional tagging.\n\n"
        "Given the following data, generate a concise, comma-separated list of **semantic tags** that capture:\n\n"
        "**Behavioral & Leadership (CRITICAL - include these when present in Action/Result):**\n"
        "- Stakeholder management, trust-building, influencing without authority\n"
        "- Coaching, mentoring, capability building, knowledge transfer\n"
        "- Navigating resistance, organizational politics, conflict resolution\n"
        "- Team dynamics, psychological safety, culture change\n"
        "- Cross-functional collaboration, alignment, consensus-building\n"
        "- Change management, overcoming skepticism, building credibility\n\n"
        "**Technical & Methodological:**\n"
        "- Technical skills, architectures, platforms, tools\n"
        "- Methodologies (Agile, TDD, DevOps, CI/CD, etc.)\n"
        "- Engineering practices and patterns\n\n"
        "**Business & Outcomes:**\n"
        "- Business capabilities and measurable outcomes\n"
        "- Industry-specific terminology\n"
        "- Transformation types (digital, agile, cloud, etc.)\n\n"
        "**Keyword Alignment:**\n"
        "- Use terminology aligned with SFIA, O*NET, LinkedIn Skills, and Accenture Tech Vision\n"
        "- Include synonyms that recruiters and hiring managers search for\n"
        "- Ensure tags are discoverable via semantic search\n\n"
        "**IMPORTANT RULES:**\n"
        "1. Read the Action and Result fields carefully for behavioral signals\n"
        "2. If the story describes navigating politics, coaching stakeholders, building trust, "
        "or overcoming resistance - those behaviors MUST appear in tags\n"
        "3. Phrases like 'coached', 'mentored', 'navigated', 'aligned', 'influenced', 'facilitated' "
        "indicate behavioral competencies - tag them\n"
        "4. Balance technical and behavioral tags - most stories have both dimensions\n"
        "5. Be specific and avoid generic terms like 'leadership' - use 'stakeholder alignment' or 'team coaching' instead\n\n"
        f"Title: {story.get('Title', '')}\n"
        f"Role: {story.get('Role', '')}\n"
        f"Industry: {story.get('Industry', '')}\n"
        f"Theme: {story.get('Theme', '')}\n"
        f"Category: {story.get('Category', '')}\n"
        f"Sub-category: {story.get('Sub-category', '')}\n"
        f"Project Scope: {story.get('Project Scope / Complexity', '')}\n"
        f"Use Cases: {story.get('Use Case(s)', '')}\n"
        f"Situation: {story.get('Situation', [''])[0]}\n"
        f"Task: {story.get('Task', [''])[0]}\n"
        f"Action: {' '.join(story.get('Action', []))}\n"
        f"Result: {' '.join(story.get('Result', []))}\n"
        f"Process: {' '.join(story.get('Process', []))}\n"
        f"Performance: {' '.join(story.get('Performance', []))}\n\n"
        "Output only the semantic tags as a comma-separated string. "
        "Aim for 8-15 tags that balance behavioral and technical dimensions."
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
    # File validation
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file '{INPUT_FILE}' not found.")
        print("   Please run generate_jsonl_from_excel.py first.")
        return

    # Count stories and estimate cost
    story_count = 0
    with open(INPUT_FILE, encoding="utf-8") as infile:
        for line in infile:
            story_count += 1

    # Cost estimation (gpt-4o pricing: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens)
    # Rough estimate: ~1000 tokens input + ~100 tokens output per story
    estimated_cost = story_count * ((1000 * 2.50 / 1_000_000) + (100 * 10 / 1_000_000))

    print(f"\n📊 Found {story_count} stories to process")
    print(f"💰 Estimated cost: ${estimated_cost:.2f} (using {MODEL})")
    print(f"⚠️  This will make {story_count} API calls to OpenAI\n")

    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled by user")
        return

    enriched_records = []

    with open(INPUT_FILE, encoding="utf-8") as infile:
        for line in infile:
            story = json.loads(line)

            print(f"🔍 Processing story ID {story.get('id')}...")

            tags = extract_semantic_tags(story)
            existing_tags = story.get("public_tags", "")

            # Combine and deduplicate
            new_tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            existing_tag_list = [
                tag.strip() for tag in existing_tags.split(",") if tag.strip()
            ]
            all_tags = set(new_tag_list + existing_tag_list)

            story["public_tags"] = ", ".join(sorted(all_tags))
            enriched_records.append(story)

    # Backup before overwriting
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_file = f"{OUTPUT_FILE.replace('.jsonl', '')}_backup_{timestamp}.jsonl"
    shutil.copy(INPUT_FILE, backup_file)
    print(f"\n📦 Backup created: {backup_file}")

    # Write enriched records
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for record in enriched_records:
            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(
        f"\n🎉 Done! Successfully enriched {len(enriched_records)} stories with AI-generated tags."
    )
    print(f"📄 Output file: {OUTPUT_FILE}")
    print(f"📦 Backup file: {backup_file}")


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    enrich_stories_with_nlp_tags()
