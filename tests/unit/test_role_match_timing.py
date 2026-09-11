"""MATTGPT click-to-render timing: unit tests for _debug_print_click_to_render.

Same shape as tests/unit/test_run_assessment_loop.py's TestRunAssessmentTiming:
patch DEBUG on the module under test (no `create=True`, so a missing or
misnamed production import fails loudly at patch time rather than silently
creating an attribute the module never reads), call the helper, capture
stdout via capsys.

The helper is intentionally small and Streamlit-free so tests do not need
a Streamlit runtime. The wiring around _render_results_panel that computes
total_ms and calls this helper is a page-level concern, exercised
end-to-end by manual runs and BDD -- not by this file.
"""

import re
from unittest.mock import patch

from ui.pages import role_match


class TestDebugPrintClickToRender:
    def test_emits_role_match_line_when_debug_true(self, capsys):
        """DEBUG=True: stdout carries a `[role_match] total_ms=<float:.1f>
        n_reqs=<int>` line so click-to-render wall time is grep-legible
        alongside the [jd_assessor] per-stage lines."""
        with patch.object(role_match, "DEBUG", True):
            role_match._debug_print_click_to_render(1234.5, 22)
        captured = capsys.readouterr()
        lines = [ln for ln in captured.out.splitlines() if "total_ms=" in ln]
        assert lines, f"expected a total_ms line, got: {captured.out!r}"
        line = lines[0]
        assert (
            "[role_match]" in line
        ), f"expected '[role_match]' prefix on line, got: {line!r}"
        assert re.search(
            r"total_ms=\d+\.\d+", line
        ), f"expected 'total_ms=<float>' on line, got: {line!r}"
        assert re.search(
            r"n_reqs=\d+", line
        ), f"expected 'n_reqs=<int>' on line, got: {line!r}"

    def test_silent_when_debug_false(self, capsys):
        """DEBUG=False: no output. Guards against a Green that forgets the
        gate and prints on every production request."""
        with patch.object(role_match, "DEBUG", False):
            role_match._debug_print_click_to_render(1234.5, 22)
        captured = capsys.readouterr()
        assert (
            "total_ms" not in captured.out
        ), f"expected silence when DEBUG=False, got: {captured.out!r}"
