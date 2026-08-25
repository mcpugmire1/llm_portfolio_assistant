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
from pathlib import Path

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

# Backups land in archive/jsonl-backups/ (gitignored). Repo root stays clean.
ARCHIVE_BACKUPS_DIR = Path("archive/jsonl-backups")

# Stories with these Era values describe independent/solo product engineering
# work — no external client, no organizational stakeholders to coordinate.
# A context note is appended to the prompt for these stories so the LLM
# stops inferring stakeholder coordination, change management, or
# cross-functional dynamics from technical product content (OKRs, user
# journeys, scope decisions). See MATTGPT-061 for diagnosis.
TECHNICAL_ONLY_ERAS = {"Independent Product Development"}


# ---------------------------
# Helper: single source of truth for what the LLM sees per story
# ---------------------------
def _dedupe_title_case_wins(tags: list[str]) -> list[str]:
    """Case-insensitive dedup preferring the more uppercase-heavy variant.

    When two tags collide case-insensitively, keep the one with more uppercase
    characters. Handles both title-case-vs-lowercase ("Client Engagement" over
    "client engagement") and acronyms ("AWS" over "aws"). Ties keep first-seen.

    Known edge case: proper nouns whose official style is title case rather than
    all-caps -- e.g., Atlassian styles it "Jira", not "JIRA". This heuristic
    would pick "JIRA" over "Jira" (4 vs 1 uppercase). The master corpus is
    curated to the correct form; this note exists so a future generator run
    that emits both variants is understood as a known limitation, not a bug.
    """
    by_lower: dict[str, str] = {}
    for tag in tags:
        key = tag.lower()
        if key not in by_lower:
            by_lower[key] = tag
            continue
        current_upper = sum(1 for c in by_lower[key] if c.isupper())
        new_upper = sum(1 for c in tag if c.isupper())
        if new_upper > current_upper:
            by_lower[key] = tag
    return list(by_lower.values())


def _prompt_view(story: dict) -> dict:
    """The exact fields and projections the tag prompt reads.

    Returned by field name (e.g., "Project Scope / Complexity", "Use Case(s)")
    so change-detection can key lookups against the raw story dict. The tag
    prompt renders labels from this view.
    """
    return {
        "Era": story.get("Era", ""),
        "Title": story.get("Title", ""),
        "Role": story.get("Role", ""),
        "Industry": story.get("Industry", ""),
        "Theme": story.get("Theme", ""),
        "Category": story.get("Category", ""),
        "Sub-category": story.get("Sub-category", ""),
        "Project Scope / Complexity": story.get("Project Scope / Complexity", ""),
        "Competencies": story.get("Competencies", ""),
        "Use Case(s)": story.get("Use Case(s)", ""),
        "Situation": " ".join(story.get("Situation") or []),
        "Task": " ".join(story.get("Task") or []),
        "Action": " ".join(story.get("Action") or []),
        "Result": " ".join(story.get("Result") or []),
        "Process": " ".join(story.get("Process") or []),
        "Performance": " ".join(story.get("Performance") or []),
    }


# ---------------------------
# Helper: NLP-based tagger
# ---------------------------
def extract_semantic_tags(story) -> list[str]:
    """Generate discovery-vocabulary tags for a story.

    Returns a list of tag strings parsed from the LLM's JSON response.
    Empty list on API or parse error.
    """
    # For Independent Product Development stories, append a context note so
    # the LLM doesn't hallucinate stakeholder/change-management/coordination
    # tags from solo technical work. See TECHNICAL_ONLY_ERAS comment above.
    view = _prompt_view(story)
    context_note = ""
    if view["Era"] in TECHNICAL_ONLY_ERAS:
        context_note = (
            "\n\n**CONTEXT FOR THIS STORY:**\n"
            "This story documents independent product engineering work: solo or "
            "small-team development with no external client and no organizational "
            "stakeholders to coordinate across. Use product engineering and technical "
            "vocabulary. Avoid business strategy and organizational leadership phrasing. "
            "Do not infer stakeholder coordination, change management, or cross-functional "
            "dynamics where the work was independent."
        )

    system_msg = (
        "You are generating discovery vocabulary for a portfolio of STAR stories.\n\n"
        "public_tags are search terms: words a reader might type into a search box "
        "to find this story. They are NOT a claim about what the practitioner is "
        "skilled at; capability is captured separately in the Competencies field, "
        "which this prompt does not produce.\n\n"
        "Given the story data provided by the user, generate distinct tags naming "
        "what the story is ABOUT: topics, technologies, domains, methodologies, "
        "and concepts a reader might use to search for it. Do not produce multiple "
        "phrasings of the same concept."
    )

    user_msg = (
        f"Title: {view['Title']}\n"
        f"Role: {view['Role']}\n"
        f"Industry: {view['Industry']}\n"
        f"Theme: {view['Theme']}\n"
        f"Category: {view['Category']}\n"
        f"Sub-category: {view['Sub-category']}\n"
        f"Project Scope: {view['Project Scope / Complexity']}\n"
        f"Competencies: {view['Competencies']}\n"
        f"Use Cases: {view['Use Case(s)']}\n"
        f"Situation: {view['Situation']}\n"
        f"Task: {view['Task']}\n"
        f"Action: {view['Action']}\n"
        f"Result: {view['Result']}\n"
        f"Process: {view['Process']}\n"
        f"Performance: {view['Performance']}" + context_note
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "story_tags",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 8,
                                "maxItems": 15,
                            },
                        },
                        "required": ["tags"],
                        "additionalProperties": False,
                    },
                },
            },
        )
        payload = json.loads(response.choices[0].message.content)
        tags = payload.get("tags") or []
        return [str(t).strip() for t in tags if str(t).strip()]
    except Exception as e:
        print(f"❌ Error generating tags for story ID {story.get('id')}: {e}")
        return []


# ---------------------------
# Main enrichment process
# ---------------------------
def enrich_stories_with_nlp_tags():
    # File validation
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file '{INPUT_FILE}' not found.")
        print("   Please run generate_jsonl_from_excel.py first.")
        return

    # Load all input stories, preserving order.
    with open(INPUT_FILE, encoding="utf-8") as infile:
        input_stories = [json.loads(line) for line in infile if line.strip()]

    # Load prior OUTPUT_FILE keyed by id, empty dict on first run.
    prior_by_id: dict[str, dict] = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    prior_by_id[rec.get("id")] = rec

    # Partition: skip stories whose _prompt_view matches prior. public_tags
    # is excluded from the comparison implicitly (not a _prompt_view field),
    # matching generate_jsonl_from_excel.py's diff-loop convention.
    to_tag = []
    for story in input_stories:
        prior = prior_by_id.get(story.get("id"))
        if prior is None or _prompt_view(story) != _prompt_view(prior):
            to_tag.append(story)

    total_count = len(input_stories)
    tag_count = len(to_tag)
    skip_count = total_count - tag_count

    # Cost estimation (gpt-4o pricing: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens)
    # Rough estimate: ~1000 tokens input + ~100 tokens output per story.
    # Count only stories that need re-tagging, not the full corpus.
    estimated_cost = tag_count * ((1000 * 2.50 / 1_000_000) + (100 * 10 / 1_000_000))

    print(
        f"\n📊 Found {total_count} stories; "
        f"{tag_count} need re-tagging, {skip_count} unchanged"
    )
    print(f"💰 Estimated cost: ${estimated_cost:.2f} (using {MODEL})")
    print(f"⚠️  This will make {tag_count} API calls to OpenAI\n")

    if tag_count == 0:
        print("✅ All stories match prior output. Nothing to do.")
        return

    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled by user")
        return

    # Tag changed/new stories via LLM. Mutates story dicts in place.
    for story in to_tag:
        print(f"🔍 Processing story ID {story.get('id')}...")
        new_tag_list = extract_semantic_tags(story)
        existing_tags = story.get("public_tags", "")

        # Combine with existing (from Excel column) and case-insensitive dedupe.
        # Title case wins on collision; acronyms preserved via uppercase-count.
        existing_tag_list = [
            tag.strip() for tag in existing_tags.split(",") if tag.strip()
        ]
        deduped = _dedupe_title_case_wins(new_tag_list + existing_tag_list)
        story["public_tags"] = ", ".join(sorted(deduped))

    # Assemble final list in original input order. Stories in to_tag are
    # already mutated in place. Skipped stories carry prior public_tags
    # forward (guaranteed present since only prior-matching stories were
    # excluded from to_tag).
    to_tag_ids = {s.get("id") for s in to_tag}
    enriched_records = []
    for story in input_stories:
        if story.get("id") not in to_tag_ids:
            story["public_tags"] = prior_by_id[story.get("id")].get("public_tags", "")
        enriched_records.append(story)

    # Backup before overwriting. Source must be OUTPUT_FILE -- the file that
    # gets overwritten below -- not INPUT_FILE, which this script only reads.
    # Guard for first-ever runs where no prior OUTPUT_FILE exists to preserve.
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_name = f"{OUTPUT_FILE.replace('.jsonl', '')}_backup_{timestamp}.jsonl"
    backup_file = str(ARCHIVE_BACKUPS_DIR / backup_name)
    if os.path.exists(OUTPUT_FILE):
        shutil.copy(OUTPUT_FILE, backup_file)
        print(f"\n📦 Backup created: {backup_file}")
    else:
        print(f"\nℹ️  No prior {OUTPUT_FILE} to back up (first run)")
        backup_file = None

    # Write enriched records
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for record in enriched_records:
            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(
        f"\n🎉 Done! Successfully enriched {len(enriched_records)} stories with AI-generated tags."
    )
    print(f"📄 Output file: {OUTPUT_FILE}")
    if backup_file:
        print(f"📦 Backup file: {backup_file}")


# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    enrich_stories_with_nlp_tags()
