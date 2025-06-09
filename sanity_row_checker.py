# sanity_check_excel_rows.py
import pandas as pd

df = pd.read_excel("MPugmire - STAR Stories - 6JUN25.xlsx", sheet_name="STAR Stories - Interview Ready")

print(f"🔢 Total rows (excluding header): {len(df)}")

# Optional: Filter based on finalized status
filtered = df[df["Status"].str.strip() == "Finalized (Interview-Ready)"]
print(f"✅ Filtered finalized stories: {len(filtered)}")

# Find rows with missing critical fields
missing = filtered[filtered["Title"].isnull() | filtered["Situation"].isnull() | filtered["Task"].isnull() | filtered["Action"].isnull() | filtered["Result"].isnull()]
print(f"⚠️ Rows with missing critical fields: {len(missing)}")
if not missing.empty:
    print(missing[["Title", "Situation", "Task", "Action", "Result"]])