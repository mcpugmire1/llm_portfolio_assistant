"""
Excel Bullet Cleanup Script

Reads your Excel file, normalizes all bullet patterns, writes back to Excel.
This is a ONE-TIME cleanup of your existing 119 stories.

IMPORTANT: Only formats fields that ACTUALLY contain bullets.
Plain paragraph fields (like Situation, 5PSummary) are left unchanged.

After running this, follow the formatting guide for future edits.

Usage:
    python cleanup_excel_bullets.py
"""

import pandas as pd
import re

# ============================================================================
# CONFIG
# ============================================================================

INPUT_EXCEL = "MPugmire - STAR Stories - 11NOV25.xlsx"
OUTPUT_EXCEL = "MPugmire - STAR Stories - 11NOV25_CLEANED.xlsx"
SHEET_NAME = "STAR Stories - Interview Ready"
DRY_RUN = False  # Set to False to write output file

# Fields to clean
FIELDS_TO_CLEAN = [
    "Task", "Action", "Result",
    "Performance", "Process",
    "Situation",
    "Competencies", "Use Case(s)"
]

# ============================================================================
# CLEANING FUNCTIONS
# ============================================================================

def has_bullets(text):
    """
    Check if text contains bullet markers.
    Returns True only if text has bullet-like formatting.
    
    IMPORTANT: Distinguishes between bullet dashes and hyphenated words.
    - "- Something" → Bullet (dash + space)
    - "Human-centered" → NOT a bullet (hyphenated word)
    """
    if pd.isna(text) or not str(text).strip():
        return False
    
    text = str(text).strip()
    lines = text.split('\n')
    
    # Non-dash bullet markers (always bullets if at line start)
    unicode_bullets = ['•', '○', '▪', '◘']
    
    # Check if any line starts with a bullet marker
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check Unicode bullet markers
        for marker in unicode_bullets:
            if line.startswith(marker):
                return True
        
        # Check dash bullets (must have space after dash OR capital letter after dash)
        # This avoids catching "Human-centered" as a bullet
        if line.startswith("- ") or line.startswith(" - "):
            return True
        
        # Check em/en dashes
        if line.startswith("— ") or line.startswith("– "):
            return True
        
        # Edge case: Dash without space but followed by capital letter (likely a bullet)
        # "-Built the platform" → Bullet
        # "human-centered" → NOT a bullet (lowercase after dash)
        if len(line) > 1:
            if line[0] == '-' and line[1].isupper():
                return True
    
    return False


def normalize_bullets(text):
    """
    Normalize bullet formatting to consistent pattern.
    
    IMPORTANT: Only processes text that actually contains bullets.
    Plain paragraphs are returned unchanged.
    
    Rules:
    - Level 1: Line starts with "'- " (apostrophe, dash space)
    - Level 2: Line starts with "'  - " (apostrophe, 2 spaces, dash space)
    - Level 3: Line starts with "'    - " (apostrophe, 4 spaces, dash space)
    - Newlines separate bullets (Alt+Enter in Excel)
    """
    if pd.isna(text) or not str(text).strip():
        return text
    
    # CHECK: Does this text actually have bullets?
    if not has_bullets(text):
        # NO BULLETS → Return unchanged (plain paragraph)
        return text
    
    # YES, HAS BULLETS → Apply normalization
    text = str(text)
    
    # Normalize various dash types
    text = text.replace("—", "-")  # Em dash
    text = text.replace("–", "-")  # En dash
    
    # Split on newlines
    lines = text.split("\n")
    normalized_lines = []
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line:
            continue
        
        # Check if this line looks like a bullet
        # Must distinguish between "- Something" (bullet) and "Human-centered" (hyphenated word)
        is_bullet = False
        
        # Unicode bullets (always bullets)
        if line.startswith("▪") or line.startswith("○") or line.startswith("◘") or line.startswith("•"):
            is_bullet = True
        # Dash with space after (definitely a bullet)
        elif line.startswith("- ") or line.startswith(" - "):
            is_bullet = True
        # Em/en dash with space
        elif line.startswith("— ") or line.startswith("– "):
            is_bullet = True
        # Dash followed by capital letter (likely bullet without space)
        elif len(line) > 1 and line[0] == '-' and line[1].isupper():
            is_bullet = True
        
        if not is_bullet:
            # Not a bullet line - keep as-is (might be continuation text or paragraph)
            # Don't add apostrophe, don't format
            normalized_lines.append(line)  # Use stripped line, not original (for consistency)
            continue
        
        # Detect hierarchy level
        level = 1  # Default
        
        # Level 3 markers
        if line.startswith("▪"):
            level = 3
            line = line[1:].strip()
        # Level 2 markers
        elif line.startswith("○") or line.startswith("◘"):
            level = 2
            line = line[1:].strip()
        # Level 1 markers
        elif line.startswith("•"):
            level = 1
            line = line[1:].strip()
        # Dash-based (most common)
        elif line.startswith("-") or line.startswith(" -"):
            # Remove the dash and any leading spaces
            line = re.sub(r'^[\s-]+', '', line).strip()
            # Try to detect level from original indentation
            leading_spaces = len(original_line) - len(original_line.lstrip())
            if leading_spaces >= 4:
                level = 3
            elif leading_spaces >= 2:
                level = 2
            else:
                level = 1
        
        # Clean the text
        line = line.strip()
        line = re.sub(r'\s+', ' ', line)  # Normalize whitespace
        
        # Apply consistent formatting with apostrophe to prevent Excel formula issues
        indent = "  " * (level - 1)  # 2 spaces per level
        formatted_line = f"'{indent}- {line}"  # Apostrophe tells Excel "this is text"
        
        normalized_lines.append(formatted_line)
    
    # Join with newlines
    return "\n".join(normalized_lines)


# ============================================================================
# MAIN SCRIPT
# ============================================================================

def cleanup_excel():
    """Main cleanup function."""
    print(f"\n🧹 Excel Bullet Cleanup Script")
    print(f"📥 Input:  {INPUT_EXCEL}")
    print(f"📤 Output: {OUTPUT_EXCEL}")
    print(f"📄 Sheet: {SHEET_NAME}")
    print(f"🚦 DRY_RUN: {DRY_RUN}\n")
    
    if DRY_RUN:
        print("⚠️  DRY RUN MODE - No files will be written\n")
    else:
        print("✅ Will create new cleaned file (original unchanged)\n")
    
    # Load Excel
    df = pd.read_excel(INPUT_EXCEL, sheet_name=SHEET_NAME)
    df_original = df.copy()
    
    print(f"✅ Loaded {len(df)} stories\n")
    print("=" * 80)
    
    # Track changes
    changes_by_field = {field: 0 for field in FIELDS_TO_CLEAN}
    sample_changes = []
    
    # Process each field
    for field in FIELDS_TO_CLEAN:
        if field not in df.columns:
            print(f"⚠️  Field '{field}' not found in Excel, skipping")
            continue
        
        print(f"\n🔍 Processing: {field}")
        
        for idx, row in df.iterrows():
            original_value = row[field]
            
            if pd.isna(original_value) or not str(original_value).strip():
                continue
            
            # Normalize
            cleaned_value = normalize_bullets(original_value)
            
            # Update if changed
            if cleaned_value != original_value:
                df.at[idx, field] = cleaned_value
                changes_by_field[field] += 1
                
                # Collect sample (first 2 per field)
                if len([s for s in sample_changes if s['field'] == field]) < 2:
                    sample_changes.append({
                        'title': row.get('Title', 'Untitled'),
                        'field': field,
                        'before': str(original_value)[:200],
                        'after': str(cleaned_value)[:200]
                    })
        
        print(f"  Modified: {changes_by_field[field]} stories")
    
    # Summary
    print("\n" + "=" * 80)
    print("\n📊 SUMMARY\n")
    
    total_changes = sum(changes_by_field.values())
    print(f"Total modifications: {total_changes}")
    print(f"\nBy field:")
    for field, count in sorted(changes_by_field.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  • {field}: {count} stories")
    
    # Show samples
    if sample_changes:
        print("\n" + "=" * 80)
        print("\n🔍 SAMPLE CHANGES\n")
        
        for i, change in enumerate(sample_changes[:5], 1):
            print(f"\n{i}. [{change['title']}] - {change['field']}")
            print(f"\nBEFORE:")
            print(f"  {change['before']}...")
            print(f"\nAFTER:")
            print(f"  {change['after']}...")
            print("-" * 80)
    
    # Write changes
    if DRY_RUN:
        print("\n🛑 DRY RUN - No files written")
        print("\nTo create cleaned output:")
        print("  1. Review the sample changes above")
        print("  2. Set DRY_RUN = False in the script")
        print("  3. Run again")
    else:
        # Write to new output file
        with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=SHEET_NAME, index=False)
        
        print(f"\n✅ Cleaned file created: {OUTPUT_EXCEL}")
        print(f"📦 Original file unchanged: {INPUT_EXCEL}")
        print(f"\n📝 Next steps:")
        print(f"   1. Open {OUTPUT_EXCEL} and verify changes look correct")
        print(f"   2. If satisfied, replace original or update config to use cleaned version")
        print(f"   3. Update INPUT_EXCEL_FILE in generate_jsonl_from_excel.py")
        print(f"   4. Regenerate JSONL with: python generate_jsonl_from_excel.py")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    cleanup_excel()
