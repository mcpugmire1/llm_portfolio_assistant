"""MATTGPT-160: Red tests for the extract_requirements split.

Splits `services.jd_assessor.extract_requirements` from a single serial
LLM call into three section-scoped calls. Wave 1: required + preferred
concurrent. Wave 2: implicit, seeded with wave 1 output because the
extraction prompt's rule -- "extract implicit requirements from
responsibilities when no explicit qualification covers them" -- gives
implicit a cross-section dependency that requires the explicit lists
to evaluate against.

Hypothesis under test: per-call output size drives the count
instability the probe measured at 1113 words (AT&T fixture, spread
4-7 vs 1-2 below 706 words). Input pressure is unchanged (each call
still sees the full JD). The after-measurement is
probe_160_extraction_variance.py run against the AT&T fixture; these
unit tests pin the mechanical contracts around the split, not the
count-stability outcome.

Section classification here is by a section-name marker each split
prompt must carry in a header line (`=== SECTION: required ===`,
`=== SECTION: preferred ===`, `=== SECTION: implicit ===`). Schema-key
substring classification was tried first and rejected: the implicit
prompt legitimately needs to describe the wave-1 context it receives,
and using the exact schema key names as classifier markers made a
reasonable implicit prompt unable to route. Header markers are stable
against prompt-copy tuning as long as the header line survives edits.
"""

import json
from unittest.mock import MagicMock

import pytest

from services import jd_assessor

# Section-name markers Green must include in each split prompt's system
# message so the routing dispatcher can classify calls without
# colliding with prose that legitimately mentions the sections by name.
_REQUIRED_MARKER = "=== SECTION: required ==="
_PREFERRED_MARKER = "=== SECTION: preferred ==="
_IMPLICIT_MARKER = "=== SECTION: implicit ==="


# ---------------------------------------------------------------------------
# Fake responses. Each section's canned response carries a distinct
# requirement string so tests can assert on which section the merged
# output pulled from.
# ---------------------------------------------------------------------------


def _fake_response(content_dict: dict):
    """Build a mock object shaped like an openai chat.completions.create
    return: `.choices[0].message.content` is a JSON string."""
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = json.dumps(content_dict)
    return resp


def _required_json() -> dict:
    """Canned required-call response. Carries the JD-level metadata
    (role_title, company, jd_format) per the design decision that
    metadata folds into the required call rather than a fourth
    metadata-only call."""
    return {
        "role_title": "Principal Engineer",
        "company": "AT&T",
        "jd_format": "hybrid",
        "required_qualifications": [
            {
                "requirement": "10+ years engineering leadership",
                "source_text": "10+ years",
                "type": "experience",
            },
        ],
    }


def _preferred_json() -> dict:
    return {
        "preferred_qualifications": [
            {
                "requirement": "Kubernetes fluency",
                "source_text": "K8s a plus",
                "type": "skill",
            },
        ],
    }


def _implicit_json() -> dict:
    return {
        "implicit_requirements": [
            {
                "requirement": "Executive stakeholder alignment",
                "inferred_from": "senior partners who care about ROI",
                "confidence": "medium",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Routing dispatcher: classify each call by which section-name marker
# appears in the system prompt. Order-independent, so wave-1 parallel
# calls arriving in either order still get the right response.
#
# A system prompt that names zero or more than one marker (the current
# single-call implementation names none of these markers) fires an
# AssertionError inside the mock. Under Red that's the failure signal
# for every test in this file that goes through the dispatcher --
# pre-split code CAN'T route because it doesn't carry the markers.
# ---------------------------------------------------------------------------


def _routing_side_effect(required=None, preferred=None, implicit=None):
    req_resp = required if required is not None else _required_json()
    pref_resp = preferred if preferred is not None else _preferred_json()
    impl_resp = implicit if implicit is not None else _implicit_json()

    def _side_effect(**kwargs):
        system = kwargs["messages"][0]["content"]
        has_req = _REQUIRED_MARKER in system
        has_pref = _PREFERRED_MARKER in system
        has_impl = _IMPLICIT_MARKER in system
        markers = int(has_req) + int(has_pref) + int(has_impl)
        if markers != 1:
            raise AssertionError(
                f"Routing dispatcher expected exactly one section marker "
                f"in the system prompt; got {markers} of "
                f"[{_REQUIRED_MARKER!r}, {_PREFERRED_MARKER!r}, "
                f"{_IMPLICIT_MARKER!r}]. Green must include exactly one "
                f"marker per split prompt so tests can identify which "
                f"section each call belongs to; pre-split code carries "
                f"none of these markers and fails this classifier -- "
                f"that's the Red signal for MATTGPT-160. System prompt "
                f"head: {system[:400]!r}"
            )
        if has_req:
            return _fake_response(req_resp)
        if has_pref:
            return _fake_response(pref_resp)
        return _fake_response(impl_resp)

    return _side_effect


def _make_client(side_effect):
    """Build a MagicMock shaped like an OpenAI client with a stubbed
    chat.completions.create."""
    client = MagicMock()
    client.chat.completions.create.side_effect = side_effect
    return client


# ---------------------------------------------------------------------------
# MATTGPT-160 Red
# ---------------------------------------------------------------------------


class TestExtractRequirementsSplit:
    """MATTGPT-160: extract_requirements splits into three section-scoped
    OpenAI calls. Wave 1 (required + preferred) is concurrent; wave 2
    (implicit) follows with wave 1 output injected into its user
    message so the LLM's dedup rule has something to evaluate against.
    Sequencing is not asserted directly -- test 2 pins it by
    construction, because implicit's user message can't carry wave 1's
    requirement text unless wave 1 completed first.
    """

    def test_makes_three_openai_calls_with_distinct_system_prompts(self):
        """Three calls total, one per section, each with a distinct
        system prompt containing exactly one section marker.

        Order-agnostic: the set of three prompts must contain one for
        each section, but wave ordering is not asserted here. Pre-split
        code makes one call, not three, and its single prompt carries
        none of the section markers, so this test fails at the routing
        dispatcher before reaching the len-check assertion below."""
        client = _make_client(_routing_side_effect())
        jd_assessor.extract_requirements(client, "fake JD text")

        calls = client.chat.completions.create.call_args_list
        assert len(calls) == 3, (
            f"expected 3 chat.completions.create calls (one per section); "
            f"got {len(calls)}"
        )

        system_prompts = [c.kwargs["messages"][0]["content"] for c in calls]
        assert len(set(system_prompts)) == 3, (
            f"expected 3 distinct system prompts (one per section); got "
            f"{len(set(system_prompts))} distinct. Prompt heads: "
            f"{[p[:120] for p in system_prompts]!r}"
        )

        for key in (
            "required_qualifications",
            "preferred_qualifications",
            "implicit_requirements",
        ):
            hits = sum(1 for p in system_prompts if key in p)
            assert hits == 1, (
                f"expected {key!r} to appear in exactly one of the three "
                f"prompts (Green splits each prompt to one section's "
                f"schema); appeared in {hits}."
            )

    def test_implicit_call_receives_required_and_preferred_output_in_context(self):
        """The current JD_EXTRACTION_PROMPT rule -- 'extract implicit
        requirements from responsibilities when no explicit qualification
        covers them' -- gives implicit a cross-section dependency.
        Green feeds wave 1's output into the implicit call so the LLM's
        dedup rule has something to evaluate against.

        This test pins that dependency by asserting the implicit call's
        user message contains the requirement text from both wave 1
        responses. Proves the sequencing by construction: implicit's
        user message can't carry that text unless required and preferred
        completed first."""
        client = _make_client(_routing_side_effect())
        jd_assessor.extract_requirements(client, "fake JD text")

        calls = client.chat.completions.create.call_args_list
        implicit_calls = [
            c for c in calls if _IMPLICIT_MARKER in c.kwargs["messages"][0]["content"]
        ]
        assert (
            len(implicit_calls) == 1
        ), f"expected exactly one implicit call; got {len(implicit_calls)}"
        implicit_user = implicit_calls[0].kwargs["messages"][1]["content"]

        assert "10+ years engineering leadership" in implicit_user, (
            f"implicit call's user message must contain the required "
            f"call's requirement text so the LLM's dedup rule ('when no "
            f"explicit qualification covers them') has something to "
            f"evaluate against. User message head: {implicit_user[:400]!r}"
        )
        assert "Kubernetes fluency" in implicit_user, (
            f"implicit call's user message must contain the preferred "
            f"call's requirement text for the same reason. User message "
            f"head: {implicit_user[:400]!r}"
        )

    def test_merges_three_sections_into_expected_shape(self):
        """Returned dict has all three section lists populated from
        their respective call responses. Contract preservation: every
        caller of extract_requirements (`run_assessment`,
        `tests/jd_pipeline_validation.py`, `probe_160`) reads these
        three keys and tolerates missing sections via `or []`, but the
        happy path must populate all three."""
        client = _make_client(_routing_side_effect())
        result = jd_assessor.extract_requirements(client, "fake JD text")

        assert "required_qualifications" in result
        assert "preferred_qualifications" in result
        assert "implicit_requirements" in result

        req_reqs = [r["requirement"] for r in result["required_qualifications"]]
        pref_reqs = [r["requirement"] for r in result["preferred_qualifications"]]
        impl_reqs = [r["requirement"] for r in result["implicit_requirements"]]

        assert "10+ years engineering leadership" in req_reqs, (
            f"required_qualifications should carry the required call's "
            f"requirements; got {req_reqs!r}"
        )
        assert "Kubernetes fluency" in pref_reqs, (
            f"preferred_qualifications should carry the preferred call's "
            f"requirements; got {pref_reqs!r}"
        )
        assert "Executive stakeholder alignment" in impl_reqs, (
            f"implicit_requirements should carry the implicit call's "
            f"requirements; got {impl_reqs!r}"
        )

    def test_required_call_carries_metadata_fields(self):
        """role_title, company, jd_format land in the returned dict.
        Design decision: fold JD-level metadata into the required call
        rather than issuing a fourth call. `jd_format` is consumed by
        role_match.py forwarding to the Sheet; the other two are read
        elsewhere in the assessment surface."""
        client = _make_client(_routing_side_effect())
        result = jd_assessor.extract_requirements(client, "fake JD text")

        assert result.get("role_title") == "Principal Engineer", (
            f"expected role_title='Principal Engineer' from the required "
            f"call's response; got {result.get('role_title')!r}"
        )
        assert result.get("company") == "AT&T", (
            f"expected company='AT&T' from the required call's response; "
            f"got {result.get('company')!r}"
        )
        assert result.get("jd_format") == "hybrid", (
            f"expected jd_format='hybrid' from the required call's "
            f"response; got {result.get('jd_format')!r}"
        )

    def test_wave_1_failure_prevents_wave_2_and_propagates(self):
        """A failed wave-1 call must (a) prevent wave 2 from firing and
        (b) raise out of extract_requirements. Pinning the wave-2-never-
        called observable is what makes this test meaningful -- a Green
        that catches wave 1's exception and lets wave 2 fire against
        partial data would produce a merged output missing the failed
        section, and the Apply/Consider/Pass recommendation math would
        silently use a smaller denominator (inflating strong_ratio).
        The observable regression this test catches:

        - return_exceptions=True with no re-raise: wave 2 fires against
          partial data, function returns a dict missing the failed
          section -> pytest.raises fails.
        - return_exceptions=True with re-raise AFTER wave 2 launches:
          wave 2 was issued unnecessarily against partial data ->
          implicit_calls > 0, second assertion fails.

        Cancellation of in-flight wave-1 siblings under threading is
        not externally observable (Python threads aren't cancellable
        from the async layer), so this test doesn't attempt to pin
        that. The observables are: exception propagates, and wave 2
        was never issued.

        Under pre-split code the single combined prompt carries none
        of the section markers, so the `_fail_on_preferred` branch on
        `_PREFERRED_MARKER` never fires -- the function falls through
        to the `_required_json` return, no RuntimeError is raised, and
        pytest.raises fails the test. Correct Red signal."""

        def _fail_on_preferred(**kwargs):
            system = kwargs["messages"][0]["content"]
            if _PREFERRED_MARKER in system:
                raise RuntimeError("simulated preferred-call failure")
            if _IMPLICIT_MARKER in system:
                return _fake_response(_implicit_json())
            return _fake_response(_required_json())

        client = _make_client(_fail_on_preferred)
        with pytest.raises(RuntimeError, match="simulated preferred-call failure"):
            jd_assessor.extract_requirements(client, "fake JD text")

        # Wave 2 (implicit) must NOT have been called. Firing wave 2
        # after wave 1 raised is the regression this assertion pins.
        calls = client.chat.completions.create.call_args_list
        implicit_calls = [
            c for c in calls if _IMPLICIT_MARKER in c.kwargs["messages"][0]["content"]
        ]
        assert len(implicit_calls) == 0, (
            f"expected wave 2 (implicit) to NEVER be called when wave 1 "
            f"raised; got {len(implicit_calls)} implicit call(s). Firing "
            f"wave 2 against partial wave-1 results would produce a "
            f"merged output missing the failed section and silently "
            f"corrupt the Apply/Consider/Pass recommendation math."
        )

    def test_schema_omits_unused_key_responsibilities_and_seniority_signals(self):
        """`key_responsibilities` and `seniority_signals` appear in the
        current JD_EXTRACTION_PROMPT schema block (lines 63-64) but are
        read nowhere in `services/` or `ui/` (grep-confirmed September
        2026). Generating output nothing reads is directly against the
        count-stability mechanism this ticket targets. None of the
        three split prompts may mention either field in its JSON
        schema."""
        client = _make_client(_routing_side_effect())
        jd_assessor.extract_requirements(client, "fake JD text")

        calls = client.chat.completions.create.call_args_list
        system_prompts = [c.kwargs["messages"][0]["content"] for c in calls]
        combined = "\n".join(system_prompts)

        assert "key_responsibilities" not in combined, (
            "key_responsibilities is unused downstream; it must not "
            "appear in any of the three split prompts' schemas. "
            "Someone re-added it during a prompt edit."
        )
        assert "seniority_signals" not in combined, (
            "seniority_signals is unused downstream; it must not appear "
            "in any of the three split prompts' schemas. Someone "
            "re-added it during a prompt edit."
        )
