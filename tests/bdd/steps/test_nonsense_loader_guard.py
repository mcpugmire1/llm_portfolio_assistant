"""
BDD step definitions for nonsense_loader_guard.feature (MATTGPT-165 loader hardening).

Tests that _load_nonsense_rules raises ValueError at load time on:
- duplicate (category, pattern) pairs
- non-dict rules (bare strings, lists)
- dicts missing required category or pattern fields
- dicts with uncompilable regex patterns

And that app.py invokes preload_nonsense_rules unconditionally at module top
level so guard failures fire at startup instead of first-query time.
"""

import ast
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_bdd import given, scenarios, then, when

if "streamlit" not in sys.modules:
    _st_mock = MagicMock()
    _st_mock.session_state = {}
    _st_mock.secrets = {}
    sys.modules["streamlit"] = _st_mock
    sys.modules["streamlit.components"] = MagicMock()
    sys.modules["streamlit.components.v1"] = MagicMock()

scenarios("../features/nonsense_loader_guard.feature")


@pytest.fixture
def ctx():
    return {}


# =============================================================================
# Given steps: build a temp JSONL file with the offending content
# =============================================================================


def _write_temp_jsonl(lines: list[str]) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        for line in lines:
            f.write(line + "\n")
        return f.name


@given(
    "a nonsense filters file containing two rules with the same category and pattern"
)
def given_duplicate_pair(ctx):
    ctx["temp_path"] = _write_temp_jsonl(
        [
            '{"category": "test", "pattern": "hello.*world"}',
            '{"category": "test", "pattern": "hello.*world"}',
        ]
    )


@given("a nonsense filters file containing a bare JSON string as a rule line")
def given_bare_string(ctx):
    ctx["temp_path"] = _write_temp_jsonl(
        [
            '{"category": "test", "pattern": "hello.*world"}',
            '"just a bare string"',
        ]
    )


@given("a nonsense filters file containing a dict with only a category field")
def given_missing_pattern(ctx):
    ctx["temp_path"] = _write_temp_jsonl(
        [
            '{"category": "test", "pattern": "hello.*world"}',
            '{"category": "orphan"}',
        ]
    )


@given("a nonsense filters file containing a rule with an invalid regex pattern")
def given_invalid_regex(ctx):
    ctx["temp_path"] = _write_temp_jsonl(
        [
            '{"category": "test", "pattern": "hello.*world"}',
            '{"category": "broken", "pattern": "[invalid(regex"}',
        ]
    )


@given("the app.py source file at project root")
def given_app_py_source(ctx):
    ctx["app_path"] = Path("app.py")
    assert ctx["app_path"].exists(), "app.py must exist at project root"
    ctx["app_source"] = ctx["app_path"].read_text(encoding="utf-8")


# =============================================================================
# When steps
# =============================================================================


@when("_load_nonsense_rules is called")
def when_load(ctx):
    from utils.validation import _load_nonsense_rules

    try:
        ctx["result"] = _load_nonsense_rules(ctx["temp_path"])
        ctx["raised"] = None
    except ValueError as e:
        ctx["result"] = None
        ctx["raised"] = e
    except Exception as e:
        ctx["result"] = None
        ctx["raised"] = e
    finally:
        Path(ctx["temp_path"]).unlink(missing_ok=True)


@when("its AST is inspected for preload_nonsense_rules call sites")
def when_inspect_ast(ctx):
    tree = ast.parse(ctx["app_source"])
    top_level_calls = []
    nested_calls = []

    def _is_preload_call(node):
        if not isinstance(node, ast.Call):
            return False
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id == "preload_nonsense_rules":
            return True
        if isinstance(fn, ast.Attribute) and fn.attr == "preload_nonsense_rules":
            return True
        return False

    # Top-level: walk module body, look for bare expression statements at depth 0.
    for stmt in tree.body:
        if isinstance(stmt, ast.Expr) and _is_preload_call(stmt.value):
            top_level_calls.append(stmt.lineno)

    # Nested: any preload call inside a FunctionDef, AsyncFunctionDef, ClassDef,
    # If, Try, While, For, or With counts as nested (conditional / wrapped).
    NESTING_TYPES = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.If,
        ast.Try,
        ast.While,
        ast.For,
        ast.With,
    )
    for node in ast.walk(tree):
        if isinstance(node, NESTING_TYPES):
            for child in ast.walk(node):
                if _is_preload_call(child):
                    nested_calls.append(getattr(child, "lineno", -1))

    ctx["top_level_calls"] = top_level_calls
    ctx["nested_calls"] = nested_calls


# =============================================================================
# Then steps
# =============================================================================


@then("it raises ValueError naming the offending line number")
def then_raises_duplicate(ctx):
    assert isinstance(
        ctx["raised"], ValueError
    ), f"Expected ValueError, got {type(ctx['raised']).__name__}: {ctx['raised']}"
    msg = str(ctx["raised"])
    assert "line" in msg.lower() and (
        "2" in msg or "duplicate" in msg.lower()
    ), f"Expected message to identify offending line 2 or duplicate; got: {msg}"


@then("it raises ValueError identifying the line as not a rule dict")
def then_raises_nondict(ctx):
    assert isinstance(
        ctx["raised"], ValueError
    ), f"Expected ValueError, got {type(ctx['raised']).__name__}: {ctx['raised']}"
    msg = str(ctx["raised"]).lower()
    assert (
        "dict" in msg or "not a rule" in msg or "rule" in msg
    ), f"Expected message to identify non-dict rule; got: {ctx['raised']}"


@then("it raises ValueError identifying the missing pattern field")
def then_raises_missing_pattern(ctx):
    assert isinstance(
        ctx["raised"], ValueError
    ), f"Expected ValueError, got {type(ctx['raised']).__name__}: {ctx['raised']}"
    msg = str(ctx["raised"]).lower()
    assert (
        "pattern" in msg
    ), f"Expected message to identify missing 'pattern' field; got: {ctx['raised']}"


@then("it raises ValueError identifying the pattern as invalid")
def then_raises_invalid_regex(ctx):
    assert isinstance(
        ctx["raised"], ValueError
    ), f"Expected ValueError, got {type(ctx['raised']).__name__}: {ctx['raised']}"
    msg = str(ctx["raised"]).lower()
    assert (
        "regex" in msg or "pattern" in msg or "compile" in msg
    ), f"Expected message to identify invalid regex/pattern; got: {ctx['raised']}"


@then(
    "at least one call appears as a module top-level statement"
    " not nested in any function, class, if, or try block"
)
def then_call_at_top_level(ctx):
    assert ctx["top_level_calls"], (
        "Expected preload_nonsense_rules() to be called at app.py module top level,"
        f" but found no such call. Nested calls found at lines: {ctx['nested_calls']}"
    )
