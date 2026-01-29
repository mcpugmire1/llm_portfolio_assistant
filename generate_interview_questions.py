"""
generate_interview_questions.py

Generates story-specific interview questions to improve semantic retrieval.

Key difference from generic questions:
- Questions contain ANCHOR TERMS (client, method, outcome, context)
- Questions should match THIS story, not similar stories
- Outputs to new field: `Interview Questions` (preserves Use Cases)

Usage:
    python generate_interview_questions.py
    python generate_interview_questions.py --limit 5    # Test with 5 stories
    python generate_interview_questions.py --no-confirm
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
    raise RuntimeError("OPENAI_API_KEY is missing.")

client = OpenAI(api_key=api_key, project=project_id, organization=org_id)

INPUT_FILE = "echo_star_stories_nlp.jsonl"
OUTPUT_FILE = "echo_star_stories_interview_questions.jsonl"
EXCEL_OUTPUT = "interview_questions_review.xlsx"
MODEL = "gpt-4o"
TEMPERATURE = 0.2  # Lower for anchor-term precision


# ---------------------------
# Helpers
# ---------------------------
def normalize_question(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^[\-\*\d\.\)\s]+", "", s)
    s = re.sub(r"\s+", " ", s)
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    # Remove trailing punctuation before adding ?
    s = s.rstrip(".?!")
    if s:
        s = s + "?"
    return s


def parse_list_from_model(text: str) -> list[str]:
    text = text.strip()

    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline > 0:
            text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(x) for x in data]
    except Exception:
        pass

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line in ("[", "]", "```", "```json"):
            continue
        line = line.rstrip(",")
        if (line.startswith('"') and line.endswith('"')) or (
            line.startswith("'") and line.endswith("'")
        ):
            line = line[1:-1]
        if line:
            lines.append(line)
    return lines


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


# ---------------------------
# Extract anchor terms from story
# ---------------------------
def extract_anchor_terms(story: dict) -> dict:
    """Pull out story-specific details for the prompt."""

    title = story.get("Title", "")
    five_p = story.get("5PSummary", "") or story.get("5P Summary", "") or ""
    situation = story.get("Situation", [])
    if isinstance(situation, list) and situation:
        situation = situation[0]
    elif isinstance(situation, list):
        situation = ""

    result = story.get("Result", [])
    if isinstance(result, list):
        result = " ".join(result)

    # Extract potential anchors
    anchors = {
        "client": story.get("Client", "") or story.get("Organization", "") or "",
        "industry": story.get("Industry", "") or "",
        "role": story.get("Role", "") or "",
        "theme": story.get("Theme", "") or "",
        "category": story.get("Category", "") or "",
        "subcategory": story.get("Sub-category", "") or "",
        "competencies": story.get("Competencies", []),
        "title": title,
        "five_p": five_p,
        "situation": situation,
        "result_snippet": result[:500] if result else "",
    }

    # Convert competencies list to string
    if isinstance(anchors["competencies"], list):
        anchors["competencies"] = ", ".join(anchors["competencies"])

    return anchors


def has_anchor_terms(question: str, anchors: dict) -> bool:
    """Check if question contains at least one anchor term."""
    q_lower = question.lower()

    # Check for client name (if not generic)
    client = anchors.get("client", "")
    if client and client.lower() not in [
        "multiple clients",
        "independent",
        "fortune 500 clients",
    ]:
        if client.lower() in q_lower:
            return True
        # Check for partial match (e.g., "JP Morgan" in "JP Morgan Chase")
        client_parts = [p for p in client.lower().split() if len(p) > 2]
        if any(p in q_lower for p in client_parts):
            return True

    # Check for key terms from title (words > 4 chars, skip common words)
    skip_words = {
        "about",
        "through",
        "across",
        "building",
        "leading",
        "managing",
        "creating",
        "delivering",
        "driving",
        "scaling",
        "transforming",
        "enabling",
        "ensuring",
        "implementing",
        "modernizing",
        "aligning",
        "establishing",
        "accelerating",
    }
    title_words = [
        w.lower()
        for w in re.findall(r"\b\w+\b", anchors.get("title", ""))
        if len(w) > 4 and w.lower() not in skip_words
    ]
    if any(w in q_lower for w in title_words[:5]):
        return True

    # Check for industry terms
    industry = anchors.get("industry", "").lower()
    if industry and len(industry) > 4 and industry in q_lower:
        return True

    # For Professional Narrative, be more lenient
    if anchors.get("category", "").lower() == "professional narrative":
        return True

    return False


# ---------------------------
# Generate questions
# ---------------------------
def generate_interview_questions(story: dict) -> list[str]:
    anchors = extract_anchor_terms(story)
    is_narrative = anchors.get("category", "").lower() == "professional narrative"

    # Build category-specific guidance
    if is_narrative:
        category_guidance = """
CATEGORY-SPECIFIC (Professional Narrative):
This is a Professional Narrative story (leadership philosophy, career intent, background).
- Focus on values, approach, leadership style, and philosophy
- Prefer "How do you..." or "What is your approach to..." over "Describe a time..."
- Still include distinguishing context (e.g., "at Accenture's Cloud Innovation Center")

GOOD examples for Professional Narrative:
- "Walk me through your leadership journey at Accenture and how it shaped you."
- "How do you build trust and psychological safety on engineering teams?"
- "What is your approach to solving ambiguous problems?"
- "What kind of roles and environments do you thrive in?"

BAD examples (too generic):
- "Tell me about your leadership style."
- "How do you lead teams?"
"""
    else:
        category_guidance = """
CATEGORY-SPECIFIC (Execution/Technical):
This is a delivery, transformation, or technical story.
- Include specific methods, practices, technologies, or outcomes
- Reference client name and project context
- Include measurable results where available

GOOD examples:
- "Tell me about implementing zero-downtime deployment for JP Morgan's payments gateway."
- "How did you break mainframe-era patterns at Norfolk Southern using Agile?"
- "Describe leading the I&AM platform migration across 12 countries."

BAD examples (too generic):
- "Tell me about a time you led a transformation."
- "How do you implement CI/CD?"
- "Describe a challenging project."
"""

    prompt = f"""You are generating interview questions that would retrieve THIS SPECIFIC STORY from a vector database.

CRITICAL RULES:
1) Each question must contain ANCHOR TERMS unique to this story:
   - Client name: {anchors['client'] or 'not specified'}
   - Industry: {anchors['industry'] or 'not specified'}
   - Specific methods, practices, or technologies mentioned in the story
   - Specific outcomes or metrics achieved
   - Unique situational context from the title or situation

2) Questions must be SPECIFIC enough that they would NOT match similar stories.
   - A question like "Tell me about leading a transformation" could match 50 stories. DON'T DO THAT.
   - A question like "Tell me about breaking mainframe patterns at Norfolk Southern" matches ONE story. DO THAT.

3) Generate 3-5 questions in a JSON array.

4) Mix question styles:
   - "Tell me about..." (behavioral)
   - "How did you..." (method-focused)
   - "Describe..." (situation-focused)
   - "Walk me through..." (process-focused)

{category_guidance}

STORY CONTEXT:
Title: {anchors['title']}
Client: {anchors['client']}
Industry: {anchors['industry']}
Theme: {anchors['theme']}
Category: {anchors['category']}
Sub-category: {anchors['subcategory']}
Competencies: {anchors['competencies']}

5P Summary: {anchors['five_p']}

Situation: {anchors['situation']}

Results (snippet): {anchors['result_snippet']}

OUTPUT: JSON array of 3-5 interview questions. No other text."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
        )
        raw = response.choices[0].message.content.strip()
        candidates = parse_list_from_model(raw)
        candidates = [normalize_question(q) for q in candidates if q]
        candidates = dedupe_preserve_order(candidates)

        # Filter to only questions with anchor terms
        validated = [q for q in candidates if has_anchor_terms(q, anchors)]

        # If validation filtered too many, fall back to all candidates
        if len(validated) < 2 and len(candidates) >= 2:
            print(
                f"   ⚠️ Anchor validation too strict, using {len(candidates)} unvalidated"
            )
            return candidates[:5]

        return validated[:5]

    except Exception as e:
        print(f"❌ Error for story {story.get('id')}: {e}")
        return []


# ---------------------------
# Main
# ---------------------------
def main(limit: int = 0, no_confirm: bool = False):
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file '{INPUT_FILE}' not found.")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        all_stories = [json.loads(line) for line in f]

    process_count = limit if limit > 0 else len(all_stories)
    estimated_cost = process_count * (
        (1200 * 2.50 / 1_000_000) + (150 * 10 / 1_000_000)
    )

    print(f"\n📊 Found {len(all_stories)} stories")
    if limit > 0:
        print(f"🔢 Processing first {limit} stories only (--limit)")
    print(f"💰 Estimated cost: ${estimated_cost:.2f} (using {MODEL})")

    if not no_confirm:
        if input("\nContinue? (y/n): ").strip().lower() != "y":
            print("❌ Cancelled")
            return

    stories_to_process = all_stories[:limit] if limit > 0 else all_stories
    processed_ids = set()

    for i, story in enumerate(stories_to_process, 1):
        story_id = story.get("id", story.get("Title", "unknown"))
        title = story.get("Title", "")[:50]
        print(f"\n🔍 [{i}/{len(stories_to_process)}] {title}...")

        questions = generate_interview_questions(story)
        story["Interview Questions"] = questions
        processed_ids.add(story_id)

        if questions:
            print(f"   ✅ Generated {len(questions)} questions:")
            for q in questions:
                print(f"      • {q[:80]}{'...' if len(q) > 80 else ''}")
        else:
            print("   ⚠️ No questions generated")

    # Backup original
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_file = f"{INPUT_FILE.replace('.jsonl', '')}_backup_{timestamp}.jsonl"
    shutil.copy(INPUT_FILE, backup_file)
    print(f"\n💾 Backup: {backup_file}")

    # Write ALL stories (processed ones have new field, others unchanged)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for story in all_stories:
            f.write(json.dumps(story, ensure_ascii=False) + "\n")

    # Excel for review (only processed stories for easier review)
    df = pd.DataFrame(stories_to_process)
    # Select relevant columns for review
    review_cols = [
        "id",
        "Title",
        "Client",
        "Category",
        "Interview Questions",
        "Use Case(s)",
        "Competencies",
    ]
    review_cols = [c for c in review_cols if c in df.columns]
    df = df[review_cols]
    # Convert lists to comma-separated strings
    for col in df.columns:
        df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    df.to_excel(EXCEL_OUTPUT, index=False)

    print(
        f"\n🎉 Done! Generated Interview Questions for {len(stories_to_process)} stories."
    )
    print(f"📄 Output: {OUTPUT_FILE}")
    print(f"📊 Review: {EXCEL_OUTPUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate story-specific interview questions"
    )
    parser.add_argument(
        "--limit", type=int, default=0, help="Process only N stories (0 = all)"
    )
    parser.add_argument(
        "--no-confirm", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()
    main(limit=args.limit, no_confirm=args.no_confirm)
