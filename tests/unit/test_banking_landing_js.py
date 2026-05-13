"""
Unit tests for the JS click-bridge in ui/pages/banking_landing.py.

Why this exists: the May 12, 2026 refactor commit shipped a bug where the
Streamlit button keys (Python side) used new naming (card_btn_banking_{tier}_{idx})
but the JS click-bridge still hardcoded the old naming (card_btn_banking_{i}_{j}).
Cards rendered visibly but clicks did nothing — the bridge couldn't find the
matching hidden buttons.

The BDD test in tests/bdd/steps/test_banking_landing.py catches this end-to-end
but requires Streamlit + Playwright (slow, environment-dependent). These unit
tests catch the same drift shape in milliseconds, no Streamlit needed —
suitable for pre-commit gating.

Contract: the JS template produced by _build_card_wiring_js() must reference
the same key patterns that render_banking_landing() uses for st.button() keys.
"""


class TestBuildCardWiringJs:
    """Pin the JS template ↔ button-key naming contract."""

    def test_js_contains_correct_tier_names(self):
        """JS template must use the tier names that st.button() keys use.

        Banking landing buttons are keyed card_btn_banking_core_{idx} and
        card_btn_banking_spec_{idx}. If the JS uses other tier names (e.g.,
        'specialized' instead of 'spec'), the bridge will silently miss
        every card.
        """
        from utils.landing_cards import build_card_wiring_js

        js = build_card_wiring_js("banking", core_count=3, spec_count=5)

        assert "['core', 3]" in js, (
            "JS should iterate tier 'core' with the supplied core_count. "
            "If this fails, the tier name or count interpolation drifted from "
            "what render_banking_landing() uses for st.button() keys."
        )
        assert "['spec', 5]" in js, (
            "JS should iterate tier 'spec' with the supplied spec_count. "
            "Same drift risk as the 'core' check."
        )

    def test_js_uses_post_refactor_button_key_pattern(self):
        """JS must look up buttons via the new card_btn_banking_{tier}_{idx} pattern.

        This is the specific bug the original refactor shipped: JS still
        referenced the old card_btn_banking_${i}_${j} pattern after the
        Python side moved to card_btn_banking_{tier}_{idx}.
        """
        from utils.landing_cards import build_card_wiring_js

        js = build_card_wiring_js("banking", core_count=3, spec_count=5)

        # The querySelector must look up by the (tier, idx) pattern.
        assert "card_btn_banking_${tier}_${idx}" in js, (
            "JS button-key selector must reference the (tier, idx) pattern. "
            "Found the old (i, j) pattern OR a different naming. This is the "
            "exact shape of the May 12 click-bridge regression."
        )

    def test_js_does_not_reference_old_2d_index_pattern(self):
        """Negative check: the obsolete card_btn_banking_${i}_${j} pattern must be gone.

        Catches the case where someone reverts the JS to the pre-refactor
        loop shape but leaves the Python side using tier-prefixed keys.
        """
        from utils.landing_cards import build_card_wiring_js

        js = build_card_wiring_js("banking", core_count=3, spec_count=5)

        assert "card_btn_banking_${i}_${j}" not in js, (
            "JS still references the pre-refactor (i, j) button-key pattern. "
            "Cards rendered with new tier-prefixed keys won't match this "
            "selector — clicks will silently no-op."
        )
        assert "card-banking-${i}-${j}" not in js, (
            "JS still references the pre-refactor (i, j) card-ID pattern. "
            "The Python side renders card-banking-{tier}-{idx}; this selector "
            "would find nothing."
        )

    def test_js_card_id_pattern_matches_render_function(self):
        """JS must look up cards via the new card-banking-{tier}-{idx} ID pattern.

        Pairs with the button-key check above — both sides of the bridge
        (visible card id ↔ hidden button key) need to use the same naming.
        """
        from utils.landing_cards import build_card_wiring_js

        js = build_card_wiring_js("banking", core_count=3, spec_count=5)

        assert "card-banking-${tier}-${idx}" in js, (
            "JS card-ID lookup must reference the (tier, idx) pattern that "
            "render_banking_landing() uses when rendering card markup."
        )

    def test_js_handles_zero_count_tiers(self):
        """If a tier has zero cards (e.g., empty data), the JS must not blow up.

        Defensive: build_landing_cards() could in principle return an empty
        Core or Specialized list. The JS should iterate zero times for that
        tier, not crash.
        """
        from utils.landing_cards import build_card_wiring_js

        js = build_card_wiring_js("banking", core_count=0, spec_count=0)

        assert "['core', 0]" in js
        assert "['spec', 0]" in js
        # No syntax-level crash: the function returned without error.
