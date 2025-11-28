import json

# Read the raw file with individual objects
with open("star_stories_llm_ready.json") as f:
    raw = f.read()

# Split objects if they're not in a list (naive but effective)
raw_objects = raw.strip().split("}\n{")
fixed_objects = []

for i, obj in enumerate(raw_objects):
    # Re-add missing braces after split
    if not obj.startswith("{"):
        obj = "{" + obj
    if not obj.endswith("}"):
        obj = obj + "}"
    try:
        fixed_objects.append(json.loads(obj))
    except json.JSONDecodeError as e:
        print(f"Error parsing object {i}: {e}")

# Save as a valid JSON array
with open("star_stories_llm_ready_fixed.json", "w") as f:
    json.dump(fixed_objects, f, indent=2)

print("✅ Fixed JSON saved to star_stories_llm_ready_fixed.json")
