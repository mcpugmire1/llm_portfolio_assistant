"""The commit-msg repo-rules hook runs with verbose: true.

.githooks/commit-msg prints findings on a passing commit (e.g. which
BACKLOG entries name a changed constant). pre-commit hides a passing
hook's output unless the hook is verbose, so without it the list never
reaches the committer.
"""

from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml"


def _hook(hook_id: str) -> dict:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    hooks = [h for repo in config["repos"] for h in repo["hooks"] if h["id"] == hook_id]
    assert len(hooks) == 1, hooks
    return hooks[0]


def test_commit_msg_repo_rules_hook_is_verbose():
    assert _hook("repo-rules-commit-msg").get("verbose") is True
