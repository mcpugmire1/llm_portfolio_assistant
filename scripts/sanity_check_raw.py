# sanity_check_raw.py
print("📂 Reading .env directly...")
with open(".env") as f:
    for line in f:
        print("🧾", repr(line.strip()))
