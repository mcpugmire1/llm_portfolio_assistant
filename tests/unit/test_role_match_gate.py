"""MATTGPT-240: unit tests for the Role Match rejection contract helpers.

Three pure-function helpers in ui/pages/role_match.py carry the contract:
  _looks_like_jd(text)          -- gate: reject non-JD input before LLM
  _is_retryable_error(e)        -- classify failure for UI two-state copy
  _handle_assessment_error(e)   -- log with class name, return UI message

Log-assertion test uses caplog rather than mocking run_assessment to
raise; that's why the handler was extracted rather than inlined in the
except block.
"""

import logging


class TestLooksLikeJD:
    """Gate requires a JD-shape term on a word boundary. Length does not
    bypass the shape check -- a long paste of pure filler (recipe, article)
    rejects the same as a short one."""

    def test_long_paste_no_shape_terms_rejects(self):
        """Length no longer bypasses the shape check. 85 words of pure
        filler with no JD-shape terms must fail the gate. This is the
        zucchini-recipe class: > 80 words, no shape signal, previously
        passed on length alone and burned an LLM call."""
        from ui.pages.role_match import _looks_like_jd

        text = " ".join(["alpha"] * 85)
        assert _looks_like_jd(text) is False

    def test_short_paste_with_shape_term_passes(self):
        from ui.pages.role_match import _looks_like_jd

        assert _looks_like_jd("Senior Python position at a startup") is True

    def test_short_paste_no_shape_terms_rejects(self):
        from ui.pages.role_match import _looks_like_jd

        assert _looks_like_jd("Chocolate cake recipe with butter and eggs") is False

    def test_short_paste_with_substring_only_still_rejects(self):
        """ "role" appears as a substring inside "casserole"; "job" inside
        "jobber". A substring-only gate lets recipes through by luck when
        they happen to include such words. Pins the intent that the gate
        matches JD-shape terms on word boundaries, not substrings."""
        from ui.pages.role_match import _looks_like_jd

        assert (
            _looks_like_jd("Chocolate cake recipe with casserole dish, butter and eggs")
            is False
        )

    def test_length_alone_does_not_bypass_shape_check(self):
        """No length bypass: word count doesn't affect the shape check.
        Both sides of the old 80-word threshold reject on no-shape-term."""
        from ui.pages.role_match import _looks_like_jd

        assert _looks_like_jd(" ".join(["alpha"] * 80)) is False
        assert _looks_like_jd(" ".join(["alpha"] * 79)) is False


class TestIsRetryableError:
    """String-compare classification: RateLimitError, APIConnectionError,
    APITimeoutError classify retryable; everything else does not."""

    def test_rate_limit_error_is_retryable(self):
        from ui.pages.role_match import _is_retryable_error

        # Simulate the OpenAI class name via a locally-defined subclass;
        # role_match.py compares e.__class__.__name__ as a string, so no
        # openai import is needed here or in production.
        class RateLimitError(Exception):
            pass

        assert _is_retryable_error(RateLimitError("rate limited")) is True

    def test_bad_request_error_not_retryable(self):
        from ui.pages.role_match import _is_retryable_error

        class BadRequestError(Exception):
            pass

        assert _is_retryable_error(BadRequestError("bad payload")) is False

    def test_internal_server_error_is_retryable(self):
        """MATTGPT-240 close-out: openai/_exceptions.py defines
        InternalServerError as a distinct APIStatusError sibling of
        RateLimitError. 5xx failures are transient; the visitor should
        see the "quick breather" copy, not "Something broke on my end.\" """
        from ui.pages.role_match import _is_retryable_error

        class InternalServerError(Exception):
            pass

        assert _is_retryable_error(InternalServerError("upstream 500")) is True


class TestHandleAssessmentError:
    """Log carries the error class name (four-way granularity for
    debugging); return value is the UI-facing message (two-state
    granularity for the visitor). Same helper, two decisions."""

    def test_retryable_returns_breather_copy_and_logs_class_name(self, caplog):
        from ui.pages.role_match import _handle_assessment_error

        class RateLimitError(Exception):
            pass

        with caplog.at_level(logging.WARNING, logger="ui.pages.role_match"):
            msg = _handle_assessment_error(RateLimitError("rate limited"))

        assert "RateLimitError" in caplog.text
        assert "quick breather" in msg
        # Locks the -240 defect: str(e) previously went to session state
        # and rendered raw. The exception detail must NOT reach the UI.
        assert "rate limited" not in msg

    def test_not_retryable_returns_something_broke_copy_and_logs_class_name(
        self, caplog
    ):
        from ui.pages.role_match import _handle_assessment_error

        class JSONDecodeError(Exception):
            pass

        with caplog.at_level(logging.WARNING, logger="ui.pages.role_match"):
            msg = _handle_assessment_error(JSONDecodeError("bad json"))

        assert "JSONDecodeError" in caplog.text
        assert "Something broke on my end" in msg
        # Same defect guard as the retryable case.
        assert "bad json" not in msg
