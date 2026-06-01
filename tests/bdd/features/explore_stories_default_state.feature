Feature: Explore Stories default state — exclude Professional Narrative + sort Start_Date desc (MATTGPT-098)
  As a recruiter or hiring manager landing on My Work
  I want the default view to show project work (not career-narrative stories)
  ordered most-recent-first
  So that the first impression represents Matt's project portfolio rather than
  career-narrative meta-stories that don't categorize into a capability area

  # MATTGPT-098. Matches the existing Timeline view convention
  # (EXCLUDED_ERA = "Leadership & Professional Narrative" at
  # ui/components/timeline_view.py:42). Two changes to default state in
  # Table + Cards views:
  #   1. Filter out Category == "Professional Narrative" (10 stories;
  #      same 10 as Era == "Leadership & Professional Narrative" — 1:1
  #      overlap verified May 29, 2026).
  #   2. Sort by Start_Date desc (YYYY-MM string, directly sortable).
  #      Most-recent-first, not alphabetical.
  #
  # OUT OF SCOPE per the ticket:
  #   - Filter architecture (Advanced Filters progressive disclosure stays).
  #   - View switcher, pagination, detail pane — unchanged.
  #   - Sortable columns still work; this only changes the DEFAULT state.
  #
  # OPT-IN: Professional Narrative stories remain reachable via Advanced
  # Filters → Category filter. User can surface them deliberately.
  #
  # Scenarios assert DOM-observable state — story-row visibility,
  # Category/Era column values, Start_Date ordering across visible rows.
  # No st.session_state reads — see feedback_bdd_dom_observable. Per
  # the "No hardcoded story titles in tests" rule, title-matching is
  # avoided; assertions use Category / Era / Start_Date column values.

  Background:
    Given the user navigates to the My Work page

  Scenario: Default view excludes Professional Narrative stories
    Then no visible story row should be tagged Category "Professional Narrative"
    And no visible story row should be tagged Era "Leadership & Professional Narrative"

  Scenario: Default view sorts stories by Start_Date descending
    Then the first visible story row's Start_Date should be >= the second visible story row's Start_Date
    And the first visible story row's Era should be one of the recent eras

  Scenario: Professional Narrative stories remain reachable via Category filter
    When the user selects "Professional Narrative" from the Category filter in Advanced Filters
    Then at least one visible story row should be tagged Category "Professional Narrative"
