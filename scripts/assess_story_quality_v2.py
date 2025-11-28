#!/usr/bin/env python3
"""
Story Quality Assessment V2 - Intelligently uses BOTH STAR and 5P fields

This script evaluates your stories by looking at BOTH STAR and 5P fields
and using whichever has better content for each component.

Usage:
    python assess_story_quality_v2.py echo_star_stories_nlp.jsonl
"""

import json
import sys


def get_text(story: dict, *field_names: str) -> str:
    """Get text from first non-empty field (handles both string and list fields)"""
    for field in field_names:
        value = story.get(field, "")
        if isinstance(value, list):
            value = " ".join(value) if value else ""
        if value and value.strip():
            return value.strip()
    return ""


def count_metrics(text: str) -> int:
    """Count quantifiable metrics in text (numbers followed by units/descriptors)"""
    import re

    # Look for patterns like: "90%", "20+ screens", "5 months", "doubled", "2x", etc.
    patterns = [
        r'\d+\s*%',  # percentages
        r'\d+\+',  # numbers with +
        r'\d+x',  # multipliers
        r'\d+\s*months?',
        r'\d+\s*weeks?',
        r'\d+\s*days?',
        r'\d+\s*screens?',
        r'\d+\s*teams?',
        r'doubled?|tripled?|quadrupled?',  # outcome descriptors
        r'\d+\s*million',
        r'\d+\s*billion',
    ]
    matches = 0
    for pattern in patterns:
        matches += len(re.findall(pattern, text, re.IGNORECASE))
    return matches


def assess_why(story: dict) -> tuple[int, str, str]:
    """
    Assess WHY it mattered - uses Purpose OR Situation (whichever is better)
    Returns: (stars, source_field, text_used)
    """
    purpose = get_text(story, "Purpose")
    situation = get_text(story, "Situation")

    # Prefer whichever has more human-centered content
    # Look for: teams, people, challenges, pain points, business impact
    human_keywords = [
        "team",
        "people",
        "customer",
        "user",
        "struggle",
        "challenge",
        "pain",
        "bottleneck",
        "issue",
        "problem",
        "impact",
        "business",
    ]

    purpose_score = sum(1 for kw in human_keywords if kw in purpose.lower())
    situation_score = sum(1 for kw in human_keywords if kw in situation.lower())

    if situation_score >= purpose_score and situation:
        text = situation
        source = "Situation"
    elif purpose:
        text = purpose
        source = "Purpose"
    else:
        return (1, "None", "Missing WHY content")

    # Rate the content
    if len(text) > 200 and any(kw in text.lower() for kw in human_keywords):
        stars = 3  # Excellent - human stakes clear
    elif len(text) > 100:
        stars = 2  # Good - has context
    else:
        stars = 1  # Weak - too generic

    return (stars, source, text)


def assess_how(story: dict) -> tuple[int, str, str]:
    """
    Assess HOW Matt approached it - uses Process OR Action (whichever is better)
    Returns: (stars, source_field, text_used)
    """
    process = get_text(story, "Process")
    action = get_text(story, "Action")

    # Prefer whichever shows unique methodology better
    method_keywords = [
        "established",
        "developed",
        "implemented",
        "created",
        "built",
        "designed",
        "architected",
        "coached",
        "led",
        "enabled",
        "framework",
        "approach",
        "methodology",
        "practice",
        "pattern",
        "standard",
    ]

    process_score = sum(1 for kw in method_keywords if kw in process.lower())
    action_score = sum(1 for kw in method_keywords if kw in action.lower())

    if action_score >= process_score and action:
        text = action
        source = "Action"
    elif process:
        text = process
        source = "Process"
    else:
        return (1, "None", "Missing HOW content")

    # Rate the content
    if len(text) > 300 and any(kw in text.lower() for kw in method_keywords):
        stars = 3  # Excellent - shows unique approach
    elif len(text) > 150:
        stars = 2  # Good - has methodology
    else:
        stars = 1  # Weak - too generic

    return (stars, source, text)


def assess_what(story: dict) -> tuple[int, str, str]:
    """
    Assess WHAT happened - uses Performance OR Result (whichever is better)
    Returns: (stars, source_field, text_used)
    """
    performance = get_text(story, "Performance")
    result = get_text(story, "Result")

    # Prefer whichever has more concrete outcomes with numbers
    perf_metrics = count_metrics(performance)
    result_metrics = count_metrics(result)

    if result_metrics >= perf_metrics and result:
        text = result
        source = "Result"
    elif performance:
        text = performance
        source = "Performance"
    else:
        return (1, "None", "Missing WHAT content")

    metrics = max(perf_metrics, result_metrics)

    # Rate the content
    if metrics >= 3:
        stars = 3  # Excellent - 3+ metrics
    elif metrics >= 1:
        stars = 2  # Good - has metrics
    else:
        stars = 1  # Weak - no quantifiable outcomes

    return (stars, source, text)


def assess_summary(story: dict) -> tuple[int, str]:
    """Assess the 5PSummary"""
    summary = get_text(story, "5PSummary")

    if not summary:
        return (1, "Missing 5PSummary")

    # Good summary has: who, what, measured by, how
    has_who = any(
        word in summary.lower() for word in ["i ", "helped", "led", "enabled"]
    )
    has_what = len(summary) > 50
    has_metrics = count_metrics(summary) > 0
    has_how = any(word in summary.lower() for word in ["by ", "through ", "using "])

    score = sum([has_who, has_what, has_metrics, has_how])

    if score >= 3:
        return (3, summary)
    elif score >= 2:
        return (2, summary)
    else:
        return (1, summary)


def assess_story(story: dict) -> dict:
    """Assess a single story and return detailed ratings"""
    why_stars, why_source, why_text = assess_why(story)
    how_stars, how_source, how_text = assess_how(story)
    what_stars, what_source, what_text = assess_what(story)
    summary_stars, summary_text = assess_summary(story)

    total_stars = why_stars + how_stars + what_stars + summary_stars

    # Determine tier
    if total_stars >= 11:
        tier = "Tier 1 - Ready for Agy V2"
    elif total_stars >= 8:
        tier = "Tier 2 - Close, needs minor work"
    else:
        tier = "Tier 3 - Needs significant work"

    return {
        "title": story.get("Title", "Untitled"),
        "client": story.get("Client", "Unknown"),
        "why_stars": why_stars,
        "why_source": why_source,
        "how_stars": how_stars,
        "how_source": how_source,
        "what_stars": what_stars,
        "what_source": what_source,
        "summary_stars": summary_stars,
        "total_stars": total_stars,
        "tier": tier,
        "id": story.get("id", ""),
    }


def load_stories(filepath: str) -> list[dict]:
    """Load stories from JSONL file"""
    stories = []
    with open(filepath) as f:
        for line in f:
            if line.strip():
                stories.append(json.loads(line))
    return stories


def print_assessment(results: list[dict]):
    """Print assessment results"""
    print("\n" + "=" * 80)
    print("STORY QUALITY ASSESSMENT V2")
    print("Using intelligent STAR + 5P field selection")
    print("=" * 80 + "\n")

    # Group by tier
    tier1 = [r for r in results if "Tier 1" in r["tier"]]
    tier2 = [r for r in results if "Tier 2" in r["tier"]]
    tier3 = [r for r in results if "Tier 3" in r["tier"]]

    print(f"Total Stories: {len(results)}")
    print(f"  Tier 1 (Ready for Agy V2): {len(tier1)}")
    print(f"  Tier 2 (Close, minor work): {len(tier2)}")
    print(f"  Tier 3 (Needs significant work): {len(tier3)}")
    print("\n" + "-" * 80 + "\n")

    # Print Tier 1 stories
    if tier1:
        print("TIER 1 STORIES (READY FOR AGY V2)")
        print("-" * 80)
        for r in tier1[:20]:  # Show first 20
            print(f"\n✅ {r['title']}")
            print(f"   Client: {r['client']}")
            print(f"   {'⭐' * r['why_stars']} WHY - {r['why_source']}")
            print(f"   {'⭐' * r['how_stars']} HOW - {r['how_source']}")
            print(f"   {'⭐' * r['what_stars']} WHAT - {r['what_source']}")
            print(f"   {'⭐' * r['summary_stars']} 5PSummary")
            print(f"   Overall: {r['tier']}")
        if len(tier1) > 20:
            print(f"\n   ... and {len(tier1) - 20} more Tier 1 stories")

    # Data source analysis
    print("\n" + "=" * 80)
    print("DATA SOURCE ANALYSIS")
    print("=" * 80)

    why_sources = {}
    how_sources = {}
    what_sources = {}

    for r in results:
        why_sources[r['why_source']] = why_sources.get(r['why_source'], 0) + 1
        how_sources[r['how_source']] = how_sources.get(r['how_source'], 0) + 1
        what_sources[r['what_source']] = what_sources.get(r['what_source'], 0) + 1

    print("\nWHY (Purpose vs Situation):")
    for source, count in sorted(why_sources.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(results)) * 100
        print(f"  {source}: {count} stories ({pct:.0f}%)")

    print("\nHOW (Process vs Action):")
    for source, count in sorted(how_sources.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(results)) * 100
        print(f"  {source}: {count} stories ({pct:.0f}%)")

    print("\nWHAT (Performance vs Result):")
    for source, count in sorted(what_sources.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(results)) * 100
        print(f"  {source}: {count} stories ({pct:.0f}%)")

    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80 + "\n")

    if len(tier1) >= 10:
        print("✅ You have 10+ Tier 1 stories - YOU'RE READY TO LAUNCH AGY V2!")
        print("   Focus on using these stories first, then gradually improve others.")
    elif len(tier1) >= 5:
        print("⚠️  You have 5-10 Tier 1 stories - you're close!")
        print("   Focus on upgrading a few Tier 2 stories to Tier 1.")
    else:
        print("❌ You have <5 Tier 1 stories - focus on your top 10-20 stories")
        print("   Use the field source analysis above to see where to enrich.")

    print("\n💡 NEXT STEPS:")
    print("1. Update your _generate_agy_response() to use both STAR and 5P fields")
    print("2. Test with your Tier 1 stories to validate the approach")
    print("3. Only enrich specific weak fields (not entire stories)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python assess_story_quality_v2.py <stories.jsonl>")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"Loading stories from {filepath}...")
    stories = load_stories(filepath)

    print(f"Assessing {len(stories)} stories...")
    results = [assess_story(story) for story in stories]

    print_assessment(results)

    # Export Tier 1 IDs for easy reference
    tier1_ids = [r["id"] for r in results if "Tier 1" in r["tier"]]
    with open("tier1_story_ids.txt", "w") as f:
        for story_id in tier1_ids:
            f.write(f"{story_id}\n")
    print("\n✅ Tier 1 story IDs exported to tier1_story_ids.txt")


if __name__ == "__main__":
    main()
