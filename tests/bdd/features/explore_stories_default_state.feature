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
  # DOM-observable note: the AgGrid Table view displays only the columns
  # Title / Client / Role / Start_Date (explore_stories.py:2310-2317).
  # Category and Era are NOT displayed in the grid — so scenarios assert
  # the FILTER's effect via the visible results count (.results-count
  # element) rather than via per-row Category/Era checks. Start_Date IS
  # displayed and is used directly for the sort-order assertion.

  Background:
    Given the user navigates to the My Work page

  Scenario: Default view excludes Professional Narrative stories
    Then the visible Table results count should equal the corpus total minus the 10 Professional Narrative stories

  Scenario: Default view sorts stories by Start_Date descending
    Then the first visible Table row's Start_Date should be greater than or equal to the second visible Table row's Start_Date

  Scenario: Professional Narrative stories remain reachable via Category filter
    When the user selects "Professional Narrative" from the Category filter in Advanced Filters
    Then the visible Table results count should equal 10
