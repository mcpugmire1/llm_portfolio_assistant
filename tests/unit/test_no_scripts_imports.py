"""No production module imports from scripts/.

scripts/ has no __init__.py: a production import from it makes mypy see the
module under two names whenever a scripts/*.py file is in the same run, which
fails the pre-push mypy hook. Lives in tests/unit/ so the pre-push hook and CI
both run it; the other architecture fitness checks stay in
tests/test_structural_assertions.py (MATTGPT-233).
"""

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PRODUCTION = ("app.py", "ui", "services", "utils", "config")


def _imports_from_scripts(root: Path) -> list[str]:
    """Production files (relative paths) that import scripts or scripts.*."""
    files = []
    for name in PRODUCTION:
        target = root / name
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files += [p for p in target.rglob("*.py") if "__pycache__" not in p.parts]
    found = []
    for path in sorted(files):
        modules = []
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                modules += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                modules.append(node.module)
        if any(m == "scripts" or m.startswith("scripts.") for m in modules):
            found.append(path.relative_to(root).as_posix())
    return found


def test_no_production_imports_from_scripts():
    found = _imports_from_scripts(REPO)
    assert not found, (
        "app.py, ui/, services/, utils/ and config/ must not import from"
        " scripts/:\n" + "\n".join(found)
    )


def test_the_check_finds_a_planted_import(tmp_path):
    # Guards the walk itself: a check that finds nothing must be able to find
    # something.
    (tmp_path / "ui").mkdir()
    (tmp_path / "ui" / "page.py").write_text("from scripts.utils import slugify\n")
    (tmp_path / "app.py").write_text("import scripts\n")
    (tmp_path / "utils").mkdir()
    (tmp_path / "utils" / "ok.py").write_text("from utils import formatting\n")
    assert _imports_from_scripts(tmp_path) == ["app.py", "ui/page.py"]
