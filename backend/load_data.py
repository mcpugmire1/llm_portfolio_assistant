# backend/load_data.py
import json
import os

def load_stories(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Could not find {json_path}")
    with open(json_path, "r") as f:
        data = json.load(f)
    return data