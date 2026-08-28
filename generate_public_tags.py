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

# Pure helpers moved to utils/formatting.py (MATTGPT-216) so unit tests can
# exercise them without importing this module and triggering the eager
# OpenAI() client construction below.
from utils.formatting import (
    _dedupe_title_case_wins,
    _drop_restated_fields,
    _normalize_tag_case,
    _prompt_view,
    _strip_paren_acronym,
)

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
        raw_tags = [
            str(t).strip() for t in (payload.get("tags") or []) if str(t).strip()
        ]
        # Only _drop_restated_fields runs here -- it's LLM-specific (the
        # generator shouldn't emit tags that just restate story metadata).
        # Case normalization and paren-acronym stripping run later in the
        # main flow so they apply to Excel input tags too.
        return _drop_restated_fields(raw_tags, story)
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

    # Partition: three ways a story lands in to_tag; record the reason during
    # the check so the audit report can print the actual cause rather than
    # inferring it after the fact (MATTGPT-072).
    #
    # Skip fires only when input has tags AND prior has tags AND _prompt_view
    # matches. Input has tags = Excel populated; skipping preserves Excel-
    # authoritative content forward with no API call.
    to_tag = []
    tag_reason_by_id: dict[str, str] = {}
    for story in input_stories:
        sid = story.get("id")
        prior = prior_by_id.get(sid)
        prior_has_tags = prior is not None and bool(
            str(prior.get("public_tags", "") or "").strip()
        )
        input_has_tags = bool(str(story.get("public_tags", "")).strip())

        if not prior_has_tags:
            to_tag.append(story)
            tag_reason_by_id[sid] = "no prior tags"
        elif not input_has_tags:
            to_tag.append(story)
            tag_reason_by_id[sid] = "Excel cleared"
        elif _prompt_view(story) != _prompt_view(prior):
            to_tag.append(story)
            tag_reason_by_id[sid] = "content changed"
        # else: skip (input has tags, prior has tags, _prompt_view matches)

    total_count = len(input_stories)
    tag_count = len(to_tag)
    skip_count = total_count - tag_count

    # Cost estimation (gpt-4o pricing: $2.50 per 1M input tokens, $10 per 1M output tokens)
    # Measured 2026-08-26 via tiktoken (probe_072_token_measurement.py):
    #   Input: corpus mean 872, median 770, p90 1273, max 2839 tokens/story.
    #   Output: 15-tag JSON payload averages 72 tokens (bounded by maxItems=15).
    # Using mean input and rounded output. Count only stories being re-tagged.
    estimated_cost = tag_count * ((872 * 2.50 / 1_000_000) + (75 * 10 / 1_000_000))

    print(
        f"\n📊 Found {total_count} stories; "
        f"{tag_count} need re-tagging, {skip_count} unchanged"
    )
    print(f"💰 Estimated cost: ${estimated_cost:.2f} (using {MODEL})")
    print(f"⚠️  This will make {tag_count} API calls to OpenAI\n")

    if tag_count == 0:
        # No LLM calls needed, but check for Excel tag edits on unchanged
        # stories -- those still need to persist to the output file since
        # input.public_tags is authoritative on skip (MATTGPT-072).
        tag_edits = [
            s
            for s in input_stories
            if str(s.get("public_tags", "")).strip()
            != str(prior_by_id.get(s.get("id"), {}).get("public_tags", "")).strip()
        ]
        if not tag_edits:
            print("✅ All stories match prior output. Nothing to do.")
            return
        print(
            f"ℹ️  No LLM calls needed. {len(tag_edits)} stories have Excel "
            f"public_tags edits to persist; writing without prompt."
        )
    else:
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Cancelled by user")
            return

    # Tag changed/new stories via LLM. Mutates story dicts in place.
    # Naive merge here (LLM tags + Excel input tags); post-processing pass
    # below normalizes and dedupes across every story regardless of source.
    for story in to_tag:
        print(f"🔍 Processing story ID {story.get('id')}...")
        new_tag_list = extract_semantic_tags(story)
        existing_tags = story.get("public_tags", "")
        existing_tag_list = [
            tag.strip() for tag in existing_tags.split(",") if tag.strip()
        ]
        story["public_tags"] = ", ".join(new_tag_list + existing_tag_list)

    # Assemble final list in original input order. Tagged stories were
    # mutated in place above. Skipped stories carry input.public_tags
    # forward -- Excel is authoritative, no overwrite from prior nlp file
    # (MATTGPT-072).
    to_tag_ids = {s.get("id") for s in to_tag}
    enriched_records = list(input_stories)

    # Post-processing: strip parenthetical acronyms, title-case each word,
    # and dedupe case-insensitively. Applied to every story's public_tags
    # regardless of source (Excel input or LLM output) so both follow the
    # same rules. The rule "title case on every tag" needs to hold even for
    # tags Matt pastes into Excel; running this inside extract_semantic_tags
    # would leave Excel tags uncorrected.
    for story in enriched_records:
        raw = str(story.get("public_tags", "") or "")
        if not raw.strip():
            continue
        parts = [t.strip() for t in raw.split(",") if t.strip()]
        parts = [_strip_paren_acronym(t) for t in parts]
        parts = [_normalize_tag_case(t) for t in parts]
        parts = _dedupe_title_case_wins(parts)
        story["public_tags"] = ", ".join(sorted(parts))

    # Per-story audit report. Matches the shape of generate_jsonl_from_excel.py's
    # diff report: one block per story, OLD/NEW for anything that changed.
    # Reason for tagging comes from tag_reason_by_id (recorded at partition
    # time, not inferred here).
    print("\n--- 🔍 Per-story Report ---")
    counts = {
        "no prior tags": 0,
        "Excel cleared": 0,
        "content changed": 0,
        "tags unchanged": 0,
        "using Excel tags": 0,
    }
    for story in input_stories:
        sid = story.get("id")
        prior = prior_by_id.get(sid) or {}
        prior_tags = str(prior.get("public_tags", "") or "").strip()
        final_tags = str(story.get("public_tags", "") or "").strip()

        if sid in to_tag_ids:
            reason = tag_reason_by_id[sid]
            counts[reason] += 1
            print(f"\n[id={sid}] Tagged: {reason}")
            print("  • public_tags:")
            print(f"    OLD: {prior_tags!r}")
            print(f"    NEW: {final_tags!r}")
        else:
            if final_tags == prior_tags:
                counts["tags unchanged"] += 1
                print(f"\n[id={sid}] Skipped: tags unchanged")
            else:
                counts["using Excel tags"] += 1
                print(f"\n[id={sid}] Skipped: using Excel tags")
                print("  • public_tags:")
                print(f"    OLD: {prior_tags!r}")
                print(f"    NEW: {final_tags!r}")

    print(
        f"\n📊 Total: {total_count}   "
        f"Tagged: {len(to_tag)} "
        f"({counts['no prior tags']} no prior tags, "
        f"{counts['Excel cleared']} Excel cleared, "
        f"{counts['content changed']} content changed)   "
        f"Skipped: {total_count - len(to_tag)} "
        f"({counts['tags unchanged']} unchanged, "
        f"{counts['using Excel tags']} Excel tag edits)"
    )

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
