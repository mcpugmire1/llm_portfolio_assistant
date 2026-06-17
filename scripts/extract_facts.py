"""
extract_facts.py — Derive volatile facts from source code and emit facts.json.

Run from the repo root:
    python scripts/extract_facts.py

Output: facts.json (repo root, gitignored — consumed by CI sync workflow)

Facts are derived, never declared. Every value here traces to a source file.
If a value drifts in code, it drifts here automatically on the next run.
"""

import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Repo root — all paths relative to here
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

facts: dict[str, Any] = {}

# ---------------------------------------------------------------------------
# 1. Model names and thresholds — config/constants.py
# ---------------------------------------------------------------------------
from config.constants import (  # noqa: E402
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    DEFAULT_CHAT_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    HARD_ACCEPT,
    PINECONE_MIN_SIM,
    SEARCH_TOP_K,
    SOFT_ACCEPT,
)

facts["chat_model"] = DEFAULT_CHAT_MODEL
facts["embedding_model"] = DEFAULT_EMBEDDING_MODEL
facts["confidence_high"] = CONFIDENCE_HIGH
facts["confidence_low"] = CONFIDENCE_LOW
facts["router_hard_accept"] = HARD_ACCEPT
facts["router_soft_accept"] = SOFT_ACCEPT
facts["pinecone_min_sim"] = PINECONE_MIN_SIM
facts["search_top_k"] = SEARCH_TOP_K

# ---------------------------------------------------------------------------
# 2. Intent families and total intents — services/semantic_router.py
#    VALID_INTENTS is a dict: {family_name: [intent_strings]}
#    len(VALID_INTENTS) = family count
#    sum of all values = total canonical intents
# ---------------------------------------------------------------------------
from services.semantic_router import VALID_INTENTS  # noqa: E402

facts["intent_family_count"] = len(VALID_INTENTS)
facts["intent_family_names"] = sorted(VALID_INTENTS.keys())
facts["intent_total_count"] = sum(len(v) for v in VALID_INTENTS.values())

# ---------------------------------------------------------------------------
# 3. Story count — production JSONL line count
#    Each line is one story. Blank trailing lines skipped.
# ---------------------------------------------------------------------------
jsonl_path = REPO_ROOT / "echo_star_stories_nlp.jsonl"
if jsonl_path.exists():
    lines = [ln for ln in jsonl_path.read_text().splitlines() if ln.strip()]
    facts["story_count"] = len(lines)
    facts["story_count_label"] = f"{(len(lines) // 10) * 10}+"
else:
    facts["story_count"] = None
    facts["story_count_label"] = "100+"

# ---------------------------------------------------------------------------
# 4. BDD scenario counts — tests/bdd/features/**/*.feature
#    Count "Scenario:" and "Scenario Outline:" lines.
#    Also count feature files.
# ---------------------------------------------------------------------------
feature_dir = REPO_ROOT / "tests" / "bdd" / "features"
scenario_count = 0
feature_files = []

if feature_dir.exists():
    for feature_file in sorted(feature_dir.rglob("*.feature")):
        feature_files.append(feature_file.name)
        for line in feature_file.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("Scenario:") or stripped.startswith(
                "Scenario Outline:"
            ):
                scenario_count += 1

facts["bdd_scenario_count"] = scenario_count
facts["bdd_feature_file_count"] = len(feature_files)
facts["bdd_feature_files"] = feature_files
facts["bdd_summary"] = (
    f"{scenario_count} scenarios across {len(feature_files)} feature files"
)

# ---------------------------------------------------------------------------
# 5. Unit test files — tests/unit/test_*.py
# ---------------------------------------------------------------------------
unit_dir = REPO_ROOT / "tests" / "unit"
if unit_dir.exists():
    unit_files = sorted(p.name for p in unit_dir.glob("test_*.py"))
    facts["unit_test_file_count"] = len(unit_files)
    facts["unit_test_files"] = unit_files
else:
    facts["unit_test_file_count"] = 0
    facts["unit_test_files"] = []

# ---------------------------------------------------------------------------
# 6. UI component inventory — ui/components/*.py (excludes __init__.py)
# ---------------------------------------------------------------------------
components_dir = REPO_ROOT / "ui" / "components"
if components_dir.exists():
    components = sorted(
        p.name for p in components_dir.glob("*.py") if p.name != "__init__.py"
    )
    facts["component_count"] = len(components)
    facts["components"] = components
else:
    facts["component_count"] = 0
    facts["components"] = []

# ---------------------------------------------------------------------------
# 7. UI pages — ui/pages/*.py + ui/pages/ask_mattgpt/ submodule
# ---------------------------------------------------------------------------
pages_dir = REPO_ROOT / "ui" / "pages"
if pages_dir.exists():
    pages = sorted(p.name for p in pages_dir.glob("*.py") if p.name != "__init__.py")
    ask_mattgpt_dir = pages_dir / "ask_mattgpt"
    ask_mattgpt_files = []
    if ask_mattgpt_dir.exists():
        ask_mattgpt_files = sorted(p.name for p in ask_mattgpt_dir.glob("*.py"))

    facts["page_count"] = len(pages)
    facts["pages"] = pages
    facts["ask_mattgpt_module_file_count"] = len(ask_mattgpt_files)
    facts["ask_mattgpt_module_files"] = ask_mattgpt_files

# ---------------------------------------------------------------------------
# 8. Env var names — .env.example
# ---------------------------------------------------------------------------
env_example = REPO_ROOT / ".env.example"
if env_example.exists():
    env_vars = []
    for line in env_example.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            env_vars.append(line.split("=")[0].strip())
    facts["env_vars"] = env_vars
else:
    facts["env_vars"] = []

# ---------------------------------------------------------------------------
# 9. Pinecone index name — from environment / .streamlit/secrets.toml key name only
#    We extract the KEY NAME from .env.example, not the value (never print secrets)
# ---------------------------------------------------------------------------
facts["pinecone_index_env_var"] = "PINECONE_INDEX_NAME"

# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------
output_path = REPO_ROOT / "facts.json"
with open(output_path, "w") as f:
    json.dump(facts, f, indent=2)

print(f"facts.json written to {output_path}")
print(f"  chat_model:           {facts['chat_model']}")
print(f"  embedding_model:      {facts['embedding_model']}")
print(f"  intent_families:      {facts['intent_family_count']}")
print(f"  stories:              {facts['story_count']} ({facts['story_count_label']})")
print(f"  bdd:                  {facts['bdd_summary']}")
print(f"  unit_test_files:      {facts['unit_test_file_count']}")
print(f"  components:           {facts['component_count']}")
print(f"  confidence_high:      {facts['confidence_high']}")
print(f"  confidence_low:       {facts['confidence_low']}")
print(f"  router_soft_accept:   {facts['router_soft_accept']}")
