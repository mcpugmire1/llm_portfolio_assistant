"""
generate_use_cases.py

Enriches STAR stories with AI-generated `Use Case(s)` interview question patterns.

Input:  echo_star_stories_nlp.jsonl          (base data from Excel export)
Output: echo_star_stories_nlp_use_cases.jsonl (enriched; does NOT overwrite input)

Pipeline example:
  1) Excel → generate_jsonl_from_excel.py → echo_star_stories.jsonl
  2) echo_star_stories.jsonl → generate_public_tags.py → echo_star_stories_nlp.jsonl
  3) echo_star_stories_nlp.jsonl → generate_use_cases.py → echo_star_stories_nlp_use_cases.jsonl
  4) echo_star_stories_nlp_use_cases.jsonl → generate_excel_from_use_case_jsonl.py

Goal:
- Use Case(s) should be recruiter/interview query patterns (NOT task descriptions)
- Helps semantic retrieval match the *question asked* to the right story

Usage:
    python generate_use_cases.py
    python generate_use_cases.py --limit 3    # Process only 3 stories (for testing)
    python generate_use_cases.py --no-confirm # Skip confirmation prompt
"""

import argparse
import json
import os
import re
import shutil
from datetime import UTC, datetime

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------
# Config
# ---------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Set it in your environment or .env file."
    )

client = OpenAI(api_key=api_key, project=project_id, organization=org_id)

INPUT_FILE = "echo_star_stories_nlp.jsonl"
OUTPUT_FILE = "echo_star_stories_nlp_use_cases.jsonl"
MODEL = "gpt-4o"
TEMPERATURE = 0.2

# Behavior: choose one
OVERWRITE_EXISTING_USE_CASES = True  # If False: merge + dedupe
MAX_USE_CASES = 6  # Cap when merging
MIN_USE_CASES_REQUIRED = 2  # Flag if fewer than this pass validation


# ---------------------------
# Helpers: validation
# ---------------------------
QUESTION_STARTERS = (
    "tell me",
    "walk me",
    "how do",
    "describe",
    "give me an example",
    "share an example",
    "what do you do",
    "how would you",
    "what's your experience with",
    "have you ever",
    "can you give me an example",
)

# Phrases that often indicate "task/resume bullet" vs "question pattern"
BANNED_PHRASES = (
    "responsible for",
    "i was responsible",
    "led ",
    "managed ",
    "created ",
    "delivered ",
    "implemented ",
    "designed ",
    "built ",
    "owned ",
    "oversaw ",
)


def normalize_use_case(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^[\-\*\d\.\)\s]+", "", s)  # remove leading bullets/numbers
    s = re.sub(r"\s+", " ", s)
    # Keep original casing? Normalize lightly: capitalize first char.
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    return s


def looks_like_question_pattern(s: str) -> bool:
    if not s or len(s) < 10:
        return False

    low = s.lower().strip()

    # Allow either explicit question mark or common interview starters
    starts_ok = low.startswith(QUESTION_STARTERS)
    ends_q = low.endswith("?")

    if not (starts_ok or ends_q):
        return False

    # Reject obvious resume/task phrasing if it doesn't read like a question
    # (We still allow "How did you lead..." even though it contains "lead".)
    if not starts_ok and ends_q:
        # If it ends with ?, it might still be fine even with banned words.
        pass
    else:
        # For starter-based patterns, ban common bullet verbs unless phrased as a question
        for phrase in BANNED_PHRASES:
            if phrase in low and not low.startswith(
                (
                    "how did",
                    "tell me",
                    "walk me",
                    "describe",
                    "give me an example",
                    "share an example",
                    "what do you do",
                    "how would you",
                    "what's your experience with",
                    "have you ever",
                    "can you give me an example",
                )
            ):
                return False

    return True


def parse_list_from_model(text: str) -> list[str]:
    """
    Model is instructed to return JSON array of strings.
    We try JSON parse first; if that fails, fall back to line parsing.
    """
    text = text.strip()

    # Strip markdown code fences if present (```json ... ```)
    if text.startswith("```"):
        # Find the end of the opening fence line
        first_newline = text.find("\n")
        if first_newline > 0:
            text = text[first_newline + 1 :]
        # Remove closing fence
        if text.endswith("```"):
            text = text[:-3].strip()

    # Try to locate a JSON array in the response
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass

    # Fallback: split lines and clean up
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line in ("[", "]", "```", "```json"):
            continue
        # Remove trailing comma
        line = line.rstrip(",")
        # Remove surrounding quotes
        if (line.startswith('"') and line.endswith('"')) or (
            line.startswith("'") and line.endswith("'")
        ):
            line = line[1:-1]
        if line:
            lines.append(normalize_use_case(line))
    return lines


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for it in items:
        key = it.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(it)
    return out


# ---------------------------
# OpenAI call
# ---------------------------
def generate_use_cases(story: dict) -> list[str]:
    """
    Returns a list[str] of interview question patterns.
    """
    # Prefer 5PSummary if present (your best summary field for retrieval intent)
    five_p = story.get("5PSummary", "") or story.get("5P Summary", "") or ""

    situation = story.get("Situation", [])
    task = story.get("Task", [])
    action = story.get("Action", [])
    result = story.get("Result", [])
    public_tags = story.get("public_tags", [])

    # Handle fields that might be strings in some records
    if isinstance(situation, str):
        situation = [situation]
    if isinstance(task, str):
        task = [task]
    if isinstance(action, str):
        action = [action]
    if isinstance(result, str):
        result = [result]
    if isinstance(public_tags, str):
        public_tags = [public_tags]

    prompt = (
        "You are generating 'Use Case(s)' for a STAR story database used in interview prep and semantic retrieval.\n\n"
        "Definition:\n"
        "- 'Use Case(s)' are short recruiter/interview QUESTION PATTERNS this story answers well.\n"
        "- They are NOT responsibilities, tasks, or project summaries.\n\n"
        "Output rules (STRICT):\n"
        "1) Output ONLY a JSON array of strings (no extra text).\n"
        "2) Generate 2 to 4 items.\n"
        "3) Each item must read like a recruiter/interviewer question pattern.\n"
        "   Use forms like:\n"
        '   - "Tell me about a time you ..."\n'
        '   - "How do you ...?"\n'
        '   - "Walk me through ..."\n'
        '   - "Describe a time when ..."\n'
        "4) Keep each item concise (8–16 words) and high-recall.\n"
        "5) Avoid task phrasing like 'Led X' unless framed as a question.\n"
        "6) Prefer wording that a recruiter would actually type.\n"
        "7) CATEGORY-SENSITIVE OUTPUT (STRICT):\n"
        "   - If Category is 'Professional Narrative' (e.g., Background & Career Story, Leadership Philosophy, Career Intent):\n"
        "     - Generate questions about leadership journey, values, decision-making style, how you lead, what you optimize for, and what you're looking for next.\n"
        "     - DO NOT generate project-execution questions about specific deliveries, implementations, or metrics.\n"
        "     - Prefer 'How do you...' or 'What is your approach to...' over 'Describe a time...' for Professional Narrative stories.\n"
        "     - HARD CONSTRAINT: At least 3 of the 4 questions must be NON-technical and journey/leadership focused.\n\n"
        "     GOOD examples:\n"
        '     - "Walk me through your leadership journey and how it shaped you."\n'
        '     - "How do you build trust and psychological safety on engineering teams?"\n'
        '     - "How do you approach ambiguous problems and create clarity for stakeholders?"\n'
        '     - "What kind of roles and environments do you thrive in, and why?"\n\n'
        "     BAD examples (do not output):\n"
        '     - "Tell me about a time you improved time-to-market."\n'
        '     - "How did you achieve 4x faster delivery?"\n'
        '     - "Walk me through implementing CI/CD."\n\n'
        "   - For Delivery / Transformation stories: generate questions about methods, practices, and outcomes.\n"
        "   - For Architecture / Integration stories: generate questions about technical decisions, tradeoffs, and system design.\n"
        "   - For Leadership / Talent stories: generate questions about team building, coaching, culture, and scaling people.\n\n"
        "8) Avoid generic questions that could apply to almost any transformation story.\n"
        "9) Each Use Case must reflect what is DISTINCTIVE about this story.\n"
        "10) Prefer referencing specific methods, practices, constraints, or transformation types.\n"
        "11) At least 2 Use Cases must include a specific method or practice from the story (unless Category is Professional Narrative).\n\n"
        "Use Competencies only to refine framing and terminology — not to generate abstract skill-based questions.\n\n"
        "Story context:\n"
        f"Title: {story.get('Title', '')}\n"
        f"Role: {story.get('Role', '')}\n"
        f"Industry: {story.get('Industry', '')}\n"
        f"Theme: {story.get('Theme', '')}\n"
        f"Category: {story.get('Category', '')}\n"
        f"Sub-category: {story.get('Sub-category', '')}\n"
        f"Project Scope: {story.get('Project Scope / Complexity', '')}\n"
        f"Competencies: {', '.join(story.get('Competencies', [])) if isinstance(story.get('Competencies'), list) else story.get('Competencies', '')}\n"
        f"public_tags: {', '.join(public_tags) if public_tags else ''}\n"
        f"5PSummary: {five_p}\n"
        f"Situation: {situation[0] if situation else ''}\n"
        f"Task: {task[0] if task else ''}\n"
        f"Action: {' '.join(action)[:2200]}\n"
        f"Result: {' '.join(result)[:1200]}\n"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
        )
        raw = response.choices[0].message.content.strip()
        candidates = parse_list_from_model(raw)
        candidates = [normalize_use_case(x) for x in candidates]
        candidates = dedupe_preserve_order([c for c in candidates if c])

        # Validate + filter
        validated = [c for c in candidates if looks_like_question_pattern(c)]

        # If the model output is off-format, keep best-effort but do not invent
        return validated

    except Exception as e:
        print(f"❌ Error generating use cases for story ID {story.get('id')}: {e}")
        return []


# ---------------------------
# Main enrichment process
# ---------------------------
def enrich_stories_with_use_cases(limit: int = 0, no_confirm: bool = False):
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file '{INPUT_FILE}' not found.")
        print("   Please run generate_jsonl_from_excel.py first.")
        return

    # Load all stories
    all_stories = []
    with open(INPUT_FILE, encoding="utf-8") as infile:
        for line in infile:
            all_stories.append(json.loads(line))

    story_count = len(all_stories)
    process_count = limit if limit > 0 else story_count

    # Very rough cost estimate assumptions (adjust as you learn actuals)
    # e.g., ~900 input tokens + ~80 output tokens per story
    estimated_cost = process_count * ((900 * 2.50 / 1_000_000) + (80 * 10 / 1_000_000))

    print(f"\n📊 Found {story_count} stories total")
    if limit > 0:
        print(f"🔢 Processing first {limit} stories only (--limit)")
    print(f"💰 Estimated cost: ${estimated_cost:.2f} (using {MODEL})")
    print(f"⚠️  This will make {process_count} API calls to OpenAI\n")

    if not no_confirm:
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Cancelled by user")
            return

    enriched_records = []
    stories_to_process = all_stories[:limit] if limit > 0 else all_stories

    for i, story in enumerate(stories_to_process, 1):
        story_id = story.get("id", "")

        print(f"🔍 [{i}/{len(stories_to_process)}] Processing {story_id}...")

        existing = story.get("Use Case(s)", []) or []
        if isinstance(existing, str):
            existing = [existing]

        new_use_cases = generate_use_cases(story)

        # Merge/overwrite behavior
        if OVERWRITE_EXISTING_USE_CASES:
            final_use_cases = new_use_cases
        else:
            combined = [normalize_use_case(x) for x in existing] + new_use_cases
            combined = dedupe_preserve_order([c for c in combined if c])
            final_use_cases = combined[:MAX_USE_CASES]

        story["Use Case(s)"] = final_use_cases

        # Optional: flag for review if too few valid
        story["_use_cases_needs_review"] = len(final_use_cases) < MIN_USE_CASES_REQUIRED

        enriched_records.append(story)

        # Show generated use cases
        if new_use_cases:
            print(f"   ✅ {len(new_use_cases)} use cases: {new_use_cases}")

    # Backup input (non-destructive, still helpful)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_file = f"{INPUT_FILE.replace('.jsonl', '')}_backup_{timestamp}.jsonl"
    shutil.copy(INPUT_FILE, backup_file)
    print(f"\n📦 Backup created: {backup_file}")

    # Write enriched output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        for record in enriched_records:
            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

    with open(OUTPUT_FILE) as f:
        data = [json.loads(line) for line in f]
    df = pd.DataFrame(data)

    # Convert list columns to comma-separated strings for Excel readability
    for col in df.columns:
        df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    df.to_excel("use_cases_review.xlsx", index=False)

    print(f"\n🎉 Done! Enriched {len(enriched_records)} stories with Use Case(s).")
    print(f"📄 Output file: {OUTPUT_FILE}")
    print(f"📦 Backup file: {backup_file}")
    print("\nNext step:")
    print("- Review stories where _use_cases_needs_review = true")
    print(
        "- Then re-run your Excel pipeline (Excel remains master) or round-trip updates back into Excel."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Use Cases for STAR stories")
    parser.add_argument(
        "--limit", type=int, default=0, help="Process only N stories (0 = all)"
    )
    parser.add_argument(
        "--no-confirm", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    enrich_stories_with_use_cases(limit=args.limit, no_confirm=args.no_confirm)
