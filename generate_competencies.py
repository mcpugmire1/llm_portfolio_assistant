"""
generate_competencies.py

Generates AI-curated competencies for each STAR story based on actual story content.

Input:  echo_star_stories_nlp.jsonl
Output:
  - Updated JSONL with AI_Competencies field
  - Excel export for review (competencies_review.xlsx)

This script analyzes:
  - Existing Competencies field (picks most important)
  - Use Case(s) field (extracts capability statements)
  - Action/Result fields (what Matt actually did)

Usage:
    python generate_competencies.py
    python generate_competencies.py --dry-run   # Preview without writing
    python generate_competencies.py --limit 5   # Process only 5 stories
"""

import argparse
import json
import os
import shutil
from datetime import UTC, datetime

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

# Initialize OpenAI client
client = OpenAI(api_key=api_key, project=project_id, organization=org_id)

INPUT_FILE = "echo_star_stories_nlp.jsonl"
OUTPUT_FILE = "echo_star_stories_nlp.jsonl"  # Updates in place
EXCEL_OUTPUT = "competencies_review.xlsx"
MODEL = "gpt-4o"  # Use full model for richer competency extraction


# ---------------------------
# Helper: Extract competencies
# ---------------------------
def extract_competencies(story: dict) -> list[str]:
    """Generate 3-5 core competencies for a story using LLM analysis."""

    # Build context from story fields
    existing_competencies = story.get("Competencies", [])
    if isinstance(existing_competencies, str):
        existing_competencies = [
            c.strip() for c in existing_competencies.split(",") if c.strip()
        ]

    use_cases = story.get("Use Case(s)", [])
    if isinstance(use_cases, str):
        use_cases = [u.strip() for u in use_cases.split(",") if u.strip()]

    action_text = (
        " ".join(story.get("Action", []))
        if isinstance(story.get("Action"), list)
        else str(story.get("Action", ""))
    )
    result_text = (
        " ".join(story.get("Result", []))
        if isinstance(story.get("Result"), list)
        else str(story.get("Result", ""))
    )

    prompt = f"""You are analyzing a professional STAR story to identify core competencies.

**YOUR TASK:** Pick 3-5 competencies this story ACTUALLY demonstrates.

**RULES:**
1. Prefer concrete skills over generic terms
   - BAD: "Leadership", "Communication", "Problem Solving"
   - GOOD: "Cross-Functional Team Leadership", "Executive Stakeholder Communication", "Root Cause Analysis"

2. If existing Use Case describes a capability, include it
   - Use Case "Agile Transformation" → competency "Agile Transformation"

3. Look at what Matt ACTUALLY DID in Action/Result
   - "Led 12-person team" → "Team Leadership"
   - "Reduced cycle time 40%" → "Process Optimization"
   - "Built CI/CD pipeline" → "DevOps Implementation"

4. No keyword stuffing — quality over quantity
   - Pick the 3-5 MOST relevant, not every possible competency

5. Use professional terminology that hiring managers search for
   - Align with SFIA, O*NET, LinkedIn skills taxonomy

**STORY DATA:**

Title: {story.get("Title", "")}
Client: {story.get("Client", "")}
Role: {story.get("Role", "")}
Industry: {story.get("Industry", "")}
Theme: {story.get("Theme", "")}

Existing Competencies: {", ".join(existing_competencies) if existing_competencies else "None"}
Use Cases: {", ".join(use_cases) if use_cases else "None"}

Action: {action_text[:1000]}

Result: {result_text[:500]}

**OUTPUT FORMAT:**
Return ONLY a comma-separated list of 3-5 competencies.
Example: Program Management, Stakeholder Alignment, Agile Transformation

Do not include explanations, bullets, or numbering."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low temperature for consistency
            max_tokens=150,
        )

        raw_output = response.choices[0].message.content.strip()

        # Parse comma-separated output into list
        competencies = [c.strip() for c in raw_output.split(",") if c.strip()]

        # Validate: 3-5 competencies
        if len(competencies) < 3:
            print(
                f"  ⚠️  Only {len(competencies)} competencies returned for story {story.get('id')}"
            )
        if len(competencies) > 5:
            competencies = competencies[:5]  # Trim to 5 max

        return competencies

    except Exception as e:
        print(f"❌ Error generating competencies for story ID {story.get('id')}: {e}")
        return []


def load_stories(filepath: str) -> list[dict]:
    """Load stories from JSONL file."""
    stories = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    return stories


def save_stories(stories: list[dict], filepath: str) -> None:
    """Save stories to JSONL file."""
    with open(filepath, "w", encoding="utf-8") as f:
        for story in stories:
            f.write(json.dumps(story, ensure_ascii=False) + "\n")


def export_to_excel(stories: list[dict], filepath: str) -> None:
    """Export stories to Excel for review, with lists converted to strings."""

    # Select relevant columns for review
    review_columns = [
        "id",
        "Title",
        "Client",
        "Theme",
        "Competencies",  # Original
        "Use Case(s)",
        "AI_Competencies",  # New AI-generated
    ]

    # Build dataframe with only existing columns
    data = []
    for story in stories:
        row = {}
        for col in review_columns:
            val = story.get(col, "")
            # Convert lists to comma-separated strings
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            row[col] = val
        data.append(row)

    df = pd.DataFrame(data)

    # Write to Excel
    df.to_excel(filepath, index=False, engine="openpyxl")
    print(f"📊 Excel export saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI competencies for STAR stories"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing files"
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Process only N stories (0 = all)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip stories that already have AI_Competencies",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("COMPETENCY GENERATION")
    print("=" * 60)
    print(f"Input: {INPUT_FILE}")
    print(f"Model: {MODEL}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Load stories
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return 1

    stories = load_stories(INPUT_FILE)
    print(f"📚 Loaded {len(stories)} stories")

    # Filter if limit specified
    if args.limit > 0:
        stories_to_process = stories[: args.limit]
        print(f"🔢 Processing first {args.limit} stories only")
    else:
        stories_to_process = stories

    # Track statistics
    processed = 0
    skipped = 0
    errors = 0

    # Process each story
    for i, story in enumerate(stories_to_process, 1):
        story_id = story.get("id", "?")
        title = story.get("Title", "Untitled")[:40]

        # Skip if already has AI_Competencies and flag is set
        if args.skip_existing and story.get("AI_Competencies"):
            print(
                f"[{i}/{len(stories_to_process)}] Skipping {story_id}: {title}... (already has AI_Competencies)"
            )
            skipped += 1
            continue

        print(f"[{i}/{len(stories_to_process)}] Processing {story_id}: {title}...")

        if args.dry_run:
            print("  (dry run - skipping API call)")
            continue

        # Generate competencies
        competencies = extract_competencies(story)

        if competencies:
            story["AI_Competencies"] = competencies
            print(f"  ✅ {len(competencies)} competencies: {', '.join(competencies)}")
            processed += 1
        else:
            print("  ⚠️  No competencies generated")
            errors += 1

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed: {processed}")
    print(f"Skipped:   {skipped}")
    print(f"Errors:    {errors}")

    if args.dry_run:
        print("\n🔍 Dry run complete - no files written")
        return 0

    # Backup original file
    if processed > 0:
        backup_path = f"{INPUT_FILE}.bak.{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(INPUT_FILE, backup_path)
        print(f"\n💾 Backup saved: {backup_path}")

        # Save updated JSONL
        save_stories(stories, OUTPUT_FILE)
        print(f"💾 Updated JSONL: {OUTPUT_FILE}")

        # Export to Excel for review
        export_to_excel(stories, EXCEL_OUTPUT)
    else:
        print("\n⚠️  No stories processed - files not updated")

    return 0


if __name__ == "__main__":
    exit(main())
