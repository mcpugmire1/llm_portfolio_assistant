import pandas as pd

INPUT_EXCEL_FILE = "MPugmire - STAR Stories - 6JUN25.xlsx"
SHEET_NAME = "STAR Stories - Interview Ready"


def run_sanity_check():
    print("🧠 Running sanity check...")

    df = pd.read_excel(INPUT_EXCEL_FILE, sheet_name=SHEET_NAME)

    total_rows = len(df)
    print(f"🔢 Total rows (including all statuses): {total_rows}")

    # Normalize and check 'Status' column
    if "Status" not in df.columns:
        print("⚠️ 'Status' column not found. Please unhide it in the Excel file.")
        return

    status_counts = df["Status"].value_counts()
    finalized_ready_rows = df[df["Status"].str.strip() == "Finalized (Interview-Ready)"]
    finalized_count = len(finalized_ready_rows)
    print(f"✅ Finalized (Interview-Ready) stories: {finalized_count}")

    print("\n📊 Status breakdown:")
    print(status_counts)

    # Check for critical missing fields
    required_fields = ["Title", "Situation", "Task", "Action", "Result"]
    missing_fields = finalized_ready_rows[required_fields].isnull().any(axis=1)
    missing_count = missing_fields.sum()

    if missing_count > 0:
        print(
            f"\n⚠️ Finalized (Interview-Ready) rows with missing critical fields: {missing_count}"
        )
        print(finalized_ready_rows[missing_fields][["Title"] + required_fields])
    else:
        print("\n✅ No missing critical fields in Interview-Ready stories.")


if __name__ == "__main__":
    run_sanity_check()
