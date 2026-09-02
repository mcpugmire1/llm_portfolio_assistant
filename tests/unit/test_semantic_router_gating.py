"""MATTGPT-234: unit tests for router_rejection_reason.

Pure-function tests -- no mocks. Consolidates -219's out_of_scope
HARD_ACCEPT gate and -234's personal HARD_ACCEPT gate into one helper
that both call sites (backend_service.py, explore_stories.py) consult.

Score choices come from real production evidence:
  - 0.186 = probe_234_personal_gate.py measurement of "how much are
    bananas?" (ticket cites 0.223 from an earlier probe; both well
    below HARD_ACCEPT and the difference is embedding drift, not
    signal).
  - 0.87 = probe_234_personal_gate.py measurement of "What religion is
    Matt?" -- the lowest real personal query in the sample. Locks the
    scenario at the tight end of the confident-personal band.
  - 0.696 = -219 ticket evidence for "Tell me about Matt's amex work",
    the case that motivated the out_of_scope gate.
"""

from services.semantic_router import (
    ROUTER_REJECTING_FAMILIES,
    router_rejection_reason,
)


class TestRouterRejectionReason:
    """The helper returns the family name when the router is confident
    enough to hard-reject; None otherwise. HARD_ACCEPT (0.80) is the
    only threshold. Only families in ROUTER_REJECTING_FAMILIES qualify.
    """

    def test_personal_below_hard_accept_returns_none(self):
        """Bananas case: family=personal, score 0.186. Below HARD_ACCEPT
        the router has no confident opinion; hard-stop should not fire.
        Falls through to Pinecone where overlap:0.00 rejects with the
        correct off-topic copy.
        """
        assert router_rejection_reason("personal", 0.186) is None

    def test_personal_at_hard_accept_returns_personal(self):
        """Boundary: exactly HARD_ACCEPT (0.80) is inclusive -- gate
        fires. Guards against a future >= vs > refactor.
        """
        assert router_rejection_reason("personal", 0.80) == "personal"

    def test_personal_above_hard_accept_returns_personal(self):
        """Real personal query at 0.87 ('What religion is Matt?') --
        the lowest genuine personal score in the probe sample. Locks the
        gate firing at the tight end of the confident-personal band.
        """
        assert router_rejection_reason("personal", 0.87) == "personal"

    def test_out_of_scope_below_hard_accept_returns_none(self):
        """-219 case: Amex at 0.696, out_of_scope family. Should fall
        through, not hard-stop. Regression guard for -219.
        """
        assert router_rejection_reason("out_of_scope", 0.696) is None

    def test_out_of_scope_above_hard_accept_returns_out_of_scope(self):
        """High-confidence out_of_scope still rejects. The -219 gate
        does not change behavior above HARD_ACCEPT.
        """
        assert router_rejection_reason("out_of_scope", 0.85) == "out_of_scope"

    def test_background_family_returns_none_regardless_of_score(self):
        """Non-rejecting family: even at 0.99 the helper returns None.
        Only families in ROUTER_REJECTING_FAMILIES hard-reject.
        """
        assert router_rejection_reason("background", 0.99) is None

    def test_synthesis_family_returns_none_regardless_of_score(self):
        """Second non-rejecting family case. Two guards together assert
        ROUTER_REJECTING_FAMILIES stays scoped to {personal, out_of_scope}
        -- if a third family is added, both these tests must be
        deliberately touched.
        """
        assert router_rejection_reason("synthesis", 0.99) is None

    def test_rejecting_families_set_membership(self):
        """Lock the set contents so an accidental widening (e.g., adding
        'behavioral') fails loudly rather than silently changing routing
        behavior for real portfolio queries.
        """
        assert ROUTER_REJECTING_FAMILIES == {"out_of_scope", "personal"}
