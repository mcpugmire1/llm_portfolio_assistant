"""Unit tests for the Ask Agy Anything chip-click handler in
ui/components/category_cards.py.

Why this exists: the May 13, 2026 chip CX adds three suggested-question
chips to the Quick Question card on Home. Each chip must set the same three
session-state keys that ui/components/story_detail.py::on_ask_this_story
sets — seed_prompt (literal question), __ask_from_suggestion__ (True), and
active_tab ("Ask MattGPT") — and call st.rerun(). The consumer side
(conversation_view.py::165) already handles the rest by popping seed_prompt
and firing the query.

These tests pin the contract that the chip handler mirrors story_detail's
pattern exactly. If implementation drifts (e.g., introduces a new key like
pending_query, or omits __ask_from_suggestion__), the chip queries will
either fail to fire or be wrongly classified by the nonsense filter.

The handler is expected to be exposed as `on_chip_click(question: str)` in
ui/components/category_cards.py. Pre-implementation: these tests RED on
ImportError. Post-implementation: GREEN.
"""

from unittest.mock import patch

# The three literal chip strings from home.feature. If they ever drift from
# the feature file, both the BDD and unit tests will fail in lockstep — that's
# the desired property (single source of truth pressure).
CHIP_QUESTIONS = [
    "How did Matt scale a Cloud Innovation Center from 0 to 150+ engineers?",
    "How does Matt build teams that ship like startups in enterprise?",
    "How does Matt manage resistance when leading enterprise transformation programs?",
]


class TestOnChipClick:
    """on_chip_click(question) must set seed_prompt, __ask_from_suggestion__,
    active_tab, and call st.rerun() — mirroring story_detail.on_ask_this_story.
    """

    def _setup_session_state(self) -> dict:
        """Build a dict-backed session_state mock that supports both
        attribute and item access (mirrors Streamlit's SessionState API).
        """
        state: dict = {}
        return state

    def test_sets_seed_prompt_to_literal_question(self):
        """The seed_prompt key must equal the question string verbatim —
        no normalization, no truncation, no rephrasing. conversation_view
        renders this as the user's first turn, so any drift shows up as a
        question different from what the recruiter clicked.
        """
        from ui.components import category_cards

        state = self._setup_session_state()
        with (
            patch.object(category_cards.st, "session_state", state),
            patch.object(category_cards.st, "rerun"),
        ):
            category_cards.on_chip_click(CHIP_QUESTIONS[0])

        assert state.get("seed_prompt") == CHIP_QUESTIONS[0], (
            f"seed_prompt should be the literal question string. "
            f"Got: {state.get('seed_prompt')!r}"
        )

    def test_sets_ask_from_suggestion_flag(self):
        """__ask_from_suggestion__ must be True to bypass nonsense-filter
        misfires (see backend_service.py:1413 and shared_state.py:157 for
        consumers). Without it, "How does Matt..." queries may get redirected.
        """
        from ui.components import category_cards

        state = self._setup_session_state()
        with (
            patch.object(category_cards.st, "session_state", state),
            patch.object(category_cards.st, "rerun"),
        ):
            category_cards.on_chip_click(CHIP_QUESTIONS[0])

        assert state.get("__ask_from_suggestion__") is True, (
            f"__ask_from_suggestion__ must be True after chip click. "
            f"Got: {state.get('__ask_from_suggestion__')!r}"
        )

    def test_sets_active_tab_to_ask_mattgpt(self):
        """The handler navigates to Ask MattGPT by setting active_tab.
        No skip_home_menu / other flags are needed — conversation_view's
        seed_prompt check handles the routing on the consumer side.
        """
        from ui.components import category_cards

        state = self._setup_session_state()
        with (
            patch.object(category_cards.st, "session_state", state),
            patch.object(category_cards.st, "rerun"),
        ):
            category_cards.on_chip_click(CHIP_QUESTIONS[0])

        assert state.get("active_tab") == "Ask MattGPT", (
            f"active_tab must route to 'Ask MattGPT' after chip click. "
            f"Got: {state.get('active_tab')!r}"
        )

    def test_calls_streamlit_rerun(self):
        """st.rerun() must be called so the page transitions immediately.
        Without it, the chip click only updates session_state — the user
        stays on Home until something else triggers a rerun.
        """
        from ui.components import category_cards

        state = self._setup_session_state()
        with (
            patch.object(category_cards.st, "session_state", state),
            patch.object(category_cards.st, "rerun") as mock_rerun,
        ):
            category_cards.on_chip_click(CHIP_QUESTIONS[0])

        mock_rerun.assert_called_once()

    def test_handles_all_three_chip_questions(self):
        """The handler is question-agnostic — each of the three chip
        strings must round-trip into seed_prompt verbatim. Negative control
        against a handler that hardcodes one specific question.
        """
        from ui.components import category_cards

        for question in CHIP_QUESTIONS:
            state = self._setup_session_state()
            with (
                patch.object(category_cards.st, "session_state", state),
                patch.object(category_cards.st, "rerun"),
            ):
                category_cards.on_chip_click(question)
            assert state["seed_prompt"] == question, (
                f"seed_prompt drift for chip {question!r}. "
                f"Got: {state['seed_prompt']!r}"
            )

    def test_does_not_set_story_specific_keys(self):
        """Negative control: the chip handler is the STORY-AGNOSTIC variant
        of on_ask_this_story. It must NOT set active_story or
        active_story_obj — those are story-detail-only and would confuse
        conversation_view by anchoring the response to a specific story.
        """
        from ui.components import category_cards

        state = self._setup_session_state()
        with (
            patch.object(category_cards.st, "session_state", state),
            patch.object(category_cards.st, "rerun"),
        ):
            category_cards.on_chip_click(CHIP_QUESTIONS[0])

        assert "active_story" not in state, (
            "Chip handler set active_story — that's a story-detail-only key. "
            "Chip questions are general and should not lock a specific story "
            "into the conversation context."
        )
        assert (
            "active_story_obj" not in state
        ), "Chip handler set active_story_obj — same issue as above."
