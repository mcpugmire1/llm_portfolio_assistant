"""
Excel Delimiter Audit Script

Analyzes your Excel file to find all delimiter patterns in STAR fields.
This helps identify inconsistencies before deciding how to standardize.

Usage:
    python audit_delimiters.py
"""

import pandas as pd
import re
from collections import Counter, defaultdict

# ============================================================================
# CONFIG
# ============================================================================

INPUT_EXCEL_FILE = "MPugmire - STAR Stories - 024OCT25.xlsx"  # Update as needed
SHEET_NAME = "STAR Stories - Interview Ready"

# Fields to check for delimiters
# Set to None to auto-detect all text fields, or specify list manually
FIELDS_TO_CHECK = None  # Will check all text columns
# FIELDS_TO_CHECK = ["Task", "Action", "Result", "Performance", "Process"]  # Or specify manually

# Common delimiter patterns to look for
DELIMITER_PATTERNS = {
    " - ": r" - ",           # Space dash space
    "- ": r"^- |(?<=\n)- ",  # Dash space at start or after newline
    " -": r" -(?=\s|$)",     # Space dash (not followed by more text)
    "• ": r"• ",             # Bullet point
    "* ": r"\* ",            # Asterisk
    "\n": r"\n",             # Newline
    "·": r"·",               # Middle dot
    "—": r"—",               # Em dash
    "–": r"–",               # En dash
}


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================


def find_delimiters_in_text(text):
    """Find all delimiter patterns in a text string."""
    if not text or pd.isna(text):
        return {}
    
    text = str(text)
    found = {}
    
    for name, pattern in DELIMITER_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            found[name] = len(matches)
    
    return found


def extract_sample(text, delimiter, max_length=100):
    """Extract a sample showing the delimiter in context."""
    if not text or pd.isna(text):
        return ""
    
    text = str(text)
    
    # Find first occurrence of delimiter
    if delimiter == "\n":
        parts = text.split("\n")[:2]
        return " [NEWLINE] ".join(parts)[:max_length] + "..."
    else:
        idx = text.find(delimiter)
        if idx == -1:
            return ""
        
        # Get context around delimiter
        start = max(0, idx - 30)
        end = min(len(text), idx + len(delimiter) + 70)
        sample = text[start:end]
        
        if start > 0:
            sample = "..." + sample
        if end < len(text):
            sample = sample + "..."
            
        return sample


def audit_excel_delimiters():
    """Main audit function."""
    print(f"\n📊 Auditing delimiters in: {INPUT_EXCEL_FILE}")
    print(f"📄 Sheet: {SHEET_NAME}\n")
    
    # Load Excel
    df = pd.read_excel(INPUT_EXCEL_FILE, sheet_name=SHEET_NAME)
    df = df[df["Title"].notna()].copy()
    
    print(f"✅ Loaded {len(df)} stories\n")
    
    # Determine which fields to check
    if FIELDS_TO_CHECK is None:
        # Auto-detect: check all text columns with substantial content
        fields_to_check = []
        for col in df.columns:
            # Skip if mostly empty
            if df[col].notna().sum() < len(df) * 0.1:
                continue
            # Check if text field with reasonable length
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if sample and isinstance(sample, str) and len(sample) > 20:
                fields_to_check.append(col)
        print(f"📝 Auto-detected {len(fields_to_check)} text fields to analyze:")
        print(f"   {', '.join(fields_to_check)}\n")
    else:
        fields_to_check = FIELDS_TO_CHECK
        print(f"📝 Analyzing {len(fields_to_check)} specified fields\n")
    
    print("=" * 80)
    
    # Track stats
    field_stats = defaultdict(lambda: defaultdict(int))
    delimiter_examples = defaultdict(lambda: defaultdict(list))
    
    # Analyze each field
    for field in fields_to_check:
        print(f"\n🔍 Analyzing field: {field}")
        print("-" * 80)
        
        field_delimiter_counts = Counter()
        
        for idx, row in df.iterrows():
            text = row.get(field, "")
            if pd.isna(text) or not str(text).strip():
                continue
            
            delimiters = find_delimiters_in_text(text)
            
            for delim, count in delimiters.items():
                field_delimiter_counts[delim] += 1
                field_stats[field][delim] += count
                
                # Collect sample if we don't have many yet
                if len(delimiter_examples[field][delim]) < 3:
                    sample = extract_sample(text, delim)
                    if sample and sample not in delimiter_examples[field][delim]:
                        delimiter_examples[field][delim].append(sample)
        
        # Print results for this field
        if field_delimiter_counts:
            print(f"\nDelimiters found in {field}:")
            for delim, story_count in field_delimiter_counts.most_common():
                total_occurrences = field_stats[field][delim]
                print(f"  • '{delim}': Found in {story_count} stories ({total_occurrences} total occurrences)")
                
                # Show samples
                if delimiter_examples[field][delim]:
                    print(f"    Examples:")
                    for i, sample in enumerate(delimiter_examples[field][delim][:2], 1):
                        print(f"      {i}. {sample}")
        else:
            print(f"  ✓ No delimiters found (single paragraph format)")
    
    # Summary recommendations
    print("\n" + "=" * 80)
    print("\n📋 SUMMARY & RECOMMENDATIONS\n")
    
    # Find most common delimiter overall
    all_delimiters = Counter()
    for field in fields_to_check:
        for delim, count in field_stats[field].items():
            all_delimiters[delim] += count
    
    if all_delimiters:
        print("Most common delimiters across all fields:")
        for delim, count in all_delimiters.most_common(5):
            print(f"  • '{delim}': {count} total occurrences")
        
        print("\n💡 Recommendations:")
        
        # Check consistency
        if len(all_delimiters) > 2:
            print("  ⚠️  Multiple delimiter styles detected - consider standardizing in Excel")
            print("     Suggested approach: Use ' - ' (space-dash-space) consistently")
        else:
            print("  ✅ Relatively consistent delimiter usage")
        
        # Check if split_bullets will handle it
        common_delims = set(d for d, _ in all_delimiters.most_common(3))
        handled_delims = {" - ", "- ", "\n", "• "}
        
        if common_delims.issubset(handled_delims):
            print("  ✅ Current split_bullets() function should handle these delimiters")
        else:
            unhandled = common_delims - handled_delims
            print(f"  ⚠️  These delimiters may need special handling: {unhandled}")
            print("     Consider updating split_bullets() function")
    else:
        print("✅ No delimiters found - all fields use single paragraph format")
    
    # Field-specific notes
    print("\n📝 Field-specific notes:")
    for field in fields_to_check:
        if not field_stats[field]:
            print(f"  • {field}: Single paragraph format (no bullets)")
        elif len(field_stats[field]) == 1:
            delim = list(field_stats[field].keys())[0]
            print(f"  • {field}: Consistent use of '{delim}'")
        else:
            delims = ", ".join(f"'{d}'" for d in field_stats[field].keys())
            print(f"  • {field}: Mixed delimiters ({delims})")
    
    print("\n" + "=" * 80)
    print("\n✅ Audit complete!\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    audit_excel_delimiters()
