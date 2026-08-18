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

    def _is_preload_call(node):
        if not isinstance(node, ast.Call):
            return False
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id == "preload_nonsense_rules":
            return True
        if isinstance(fn, ast.Attribute) and fn.attr == "preload_nonsense_rules":
            return True
        return False

    def _handler_names(handler):
        """Return the set of call names invoked inside an except handler."""
        names = set()
        for node in ast.walk(handler):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Attribute):
                    names.add(fn.attr)
                elif isinstance(fn, ast.Name):
                    names.add(fn.id)
        return names

    # Enforced pattern: a Try whose parent is the module body (NOT nested inside
    # a function, class, if, while, for, or with), containing a bare
    # preload_nonsense_rules() call in its try body, and an except handler that
    # calls both st.markdown and st.stop for user-safe error presentation.
    #
    # st.markdown (not st.error) is required because global CSS at
    # ui/styles/global_styles.py:190-196 hides .stAlert and [data-testid="stAlert"]
    # unless they contain a thinking-ball element. st.error renders invisibly.
    # The codebase's user-visible pattern is st.markdown(..., unsafe_allow_html=True).
    #
    # Only iterate tree.body so a try nested inside a function does not
    # satisfy the assertion by accident.
    wrapped_call_sites = []
    for stmt in tree.body:
        if not isinstance(stmt, ast.Try):
            continue
        preload_in_body = [
            s
            for s in stmt.body
            if isinstance(s, ast.Expr) and _is_preload_call(s.value)
        ]
        if not preload_in_body:
            continue
        handler_ok = any(
            {"markdown", "stop"}.issubset(_handler_names(h)) for h in stmt.handlers
        )
        if handler_ok:
            wrapped_call_sites.append(preload_in_body[0].lineno)

    # Diagnostic: preload calls anywhere else (bare at top level with no wrap,
    # or nested inside function/class/conditional). Used only for error messages.
    other_call_sites = []
    for node in ast.walk(tree):
        if _is_preload_call(node):
            lineno = getattr(node, "lineno", -1)
            if lineno not in wrapped_call_sites:
                other_call_sites.append(lineno)

    ctx["wrapped_call_sites"] = wrapped_call_sites
    ctx["other_call_sites"] = other_call_sites


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
    "at least one call appears as a bare statement in the body of a try"
    " that is itself a top-level statement in app.py"
    " and whose except handler calls both st.markdown and st.stop"
)
def then_call_wrapped_at_top_level(ctx):
    assert ctx["wrapped_call_sites"], (
        "Expected preload_nonsense_rules() to be called inside a module-level"
        " try/except at app.py, with the except handler calling both st.markdown"
        " and st.stop for user-safe error presentation (st.error is hidden by"
        " global CSS at ui/styles/global_styles.py:190-196). Found no such call."
        f" Other preload calls (not wrapped or not at module scope) at lines:"
        f" {ctx['other_call_sites']}"
    )
