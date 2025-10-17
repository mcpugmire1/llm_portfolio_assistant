"""
Quick validation of Industry field in Excel before regenerating JSONL
"""

import pandas as pd
from collections import Counter

INPUT_EXCEL_FILE = "MPugmire - STAR Stories - 06AUG25.xlsx"
SHEET_NAME = "STAR Stories - Interview Ready"

print("📊 Validating Industry Field in Excel Data\n")
print("=" * 80)

# Load Excel
df = pd.read_excel(INPUT_EXCEL_FILE, sheet_name=SHEET_NAME)

# Drop rows with no Title (unfinalized stories)
df = df[df["Title"].notna()].copy()

print(f"\n✅ Total stories with Title: {len(df)}")

# Check Industry field
has_industry = df["Industry"].notna().sum()
missing_industry = df["Industry"].isna().sum()

print(f"\n📋 Industry Field Status:")
print(f"   Stories WITH Industry: {has_industry}")
print(f"   Stories WITHOUT Industry: {missing_industry}")

if missing_industry > 0:
    print(f"\n⚠️  WARNING: {missing_industry} stories are missing Industry field")
    print("\n   Stories missing Industry:")
    for idx, row in df[df["Industry"].isna()].iterrows():
        print(f"   - {row.get('Title', 'No Title')} (Client: {row.get('Client', 'Unknown')})")

# Show distinct Industry values
print(f"\n🏢 Distinct Industry Values:")
industry_counts = Counter(df["Industry"].dropna())

for industry, count in industry_counts.most_common():
    print(f"   {count:3d} stories: {industry}")

# Check for potential data quality issues
print(f"\n🔍 Data Quality Checks:")

# 1. Check for very similar industry names (potential duplicates)
industries = list(industry_counts.keys())
print(f"\n   Total unique industries: {len(industries)}")

# 2. Check if Industry aligns with Client
print(f"\n   Sample Industry → Client mapping:")
industry_client_map = df.groupby('Industry')['Client'].apply(lambda x: list(x.unique()[:3])).to_dict()
for ind, clients in list(industry_client_map.items())[:5]:
    print(f"   {ind}:")
    for client in clients:
        print(f"      - {client}")

# 3. Check cross-tabulation with Sub-category
print(f"\n   Industry vs Sub-category distribution:")
cross_tab = pd.crosstab(df['Industry'], df['Sub-category'], margins=True, dropna=False)
print(cross_tab.to_string())

print("\n" + "=" * 80)
print("\n✅ Validation complete. Review above before running generate_jsonl_from_excel.py")
print("\nNext steps:")
print("  1. If data looks good → Run: python3 generate_jsonl_from_excel.py")
print("  2. If issues found → Fix in Excel, then re-export and re-run this validation")
