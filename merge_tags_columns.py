import pandas as pd

INPUT_FILE = "MPugmire - STAR Stories - 16JUL25.xlsx"
OUTPUT_FILE = "MPugmire - STAR Stories - 16JUL25MergedTags.xlsx"

# Columns to merge
PUBLIC_TAGS_COL = "Public Tags"
REFINED_TAGS_COL = "Refined Tags"
MERGED_TAGS_COL = "Merged Tags"

def merge_and_clean_tags(row):
    tags = set()

    for col in [PUBLIC_TAGS_COL, REFINED_TAGS_COL]:
        raw = row.get(col)
        if pd.notna(raw):
            tags.update([t.strip() for t in str(raw).split(",") if t.strip()])

    return ", ".join(sorted(tags))

def main():
    print(f"📂 Loading file: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)

    print("🔀 Merging tag columns...")
    df[MERGED_TAGS_COL] = df.apply(merge_and_clean_tags, axis=1)

    print(f"💾 Saving updated file to: {OUTPUT_FILE}")
    df.to_excel(OUTPUT_FILE, index=False)

    print("\n✅ Done! Merged tags are now available in the column 'Merged Tags'.")

if __name__ == "__main__":
    main()