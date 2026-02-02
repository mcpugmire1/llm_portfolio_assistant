Feature: Explore Stories
  As a visitor to MattGPT
  I want to browse and filter Matt's transformation stories
  So that I can find relevant experience for my needs

  Background:
    Given the user navigates to the Explore Stories page
    And the page has finished loading

  # =============================================================================
  # SEARCH FLOW
  # =============================================================================

  Scenario: Search returns relevant results
    When the user types "payments transformation" in the search box
    And the user presses Enter
    Then the results count should update
    And the results should contain stories with "payments" or "transformation"
    And no error should be displayed

  Scenario: Search clears stale state
    Given the user has searched for "banking"
    And the user has opened a story detail
    When the user types "cloud" in the search box
    And the user presses Enter
    Then the story detail should be closed
    And the results should reflect the new search

  Scenario: Clearing search restores full list
    Given the user has searched for "payments"
    When the user clears the search box
    Then all stories should be displayed
    And no filters should be active

  # =============================================================================
  # FILTER COMBINATIONS
  # =============================================================================

  Scenario: Industry filter narrows results
    When the user selects "Financial Services / Banking" from the Industry filter
    Then all displayed stories should have Industry "Financial Services / Banking"
    And the active filters should show "Financial Services / Banking"

  Scenario: Capability filter narrows results
    When the user selects "Application Modernization" from the Capability filter
    Then all displayed stories should have Capability "Application Modernization"
    And the active filters should show "Application Modernization"

  Scenario: Combined Industry and Capability filters
    When the user selects "Financial Services / Banking" from the Industry filter
    And the user selects "Application Modernization" from the Capability filter
    Then all displayed stories should match both filters
    And the active filters should show "Financial Services / Banking" and "Platform Engineering"

  Scenario: Filter chip removal restores results
    Given the user has selected "Financial Services / Banking" from the Industry filter
    When the user clicks the "Financial Services / Banking" filter chip to remove it
    Then the Industry filter should be cleared
    And more stories should be displayed

  Scenario: Advanced filters expand on click
    When the user clicks "Advanced Filters"
    Then the advanced filter section should be visible
    And the Client multiselect should be visible
    And the Role multiselect should be visible
    And the Domain multiselect should be visible

  Scenario: Client multiselect filter works
    Given the advanced filters are expanded
    When the user selects "JP Morgan Chase" from the Client filter
    Then all displayed stories should have Client "JP Morgan Chase"

  Scenario: Multiple advanced filters combine
    Given the advanced filters are expanded
    When the user selects "JP Morgan Chase" from the Client filter
    And the user selects "Director" from the Role filter
    Then all displayed stories should match both Client and Role

  Scenario: Era filter from Timeline view
    When the user switches to Timeline view
    And the user clicks "View in Explore" for "Financial Services Platform Modernization"
    Then the Era filter should be set to "Financial Services Platform Modernization"
    And results should be filtered to that era

  # =============================================================================
  # RESET BEHAVIOR
  # =============================================================================

  Scenario: Reset clears all filters
    Given the user has selected "Financial Services / Banking" from the Industry filter
    And the user has searched for "payments"
    When the user clicks the Reset button
    Then all filters should be cleared
    And the search box should be empty
    And all stories should be displayed

  # =============================================================================
  # VIEW SWITCHING
  # =============================================================================

  Scenario: Table view displays stories in rows
    When the user switches to Table view
    Then stories should be displayed in a table format
    And the table should have columns for Title, Client, Role

  Scenario: Cards view displays stories in cards
    When the user switches to Cards view
    Then stories should be displayed as cards
    And each card should show Title and Client

  Scenario: Timeline view groups stories by era
    When the user switches to Timeline view
    Then stories should be grouped by career era
    And each era should be collapsible

  Scenario: View switching preserves search query
    Given the user has searched for "payments"
    And the user is in Table view
    When the user switches to Cards view
    Then the search query should still be "payments"
    And results should still be filtered

  Scenario: View switching preserves filters
    Given the user has selected "Financial Services / Banking" from the Industry filter
    And the user is in Table view
    When the user switches to Cards view
    Then the Industry filter should still be "Financial Services / Banking"

  Scenario: View switching preserves open story detail
    Given the user is in Cards view
    And the user has opened story "building-jp-morgans-global-payments-gateway-across-12-countries|jp-morgan-chase"
    When the user switches to Table view
    Then the story detail should still be open
    And the story should be "Building JP Morgan's Global Payments Gateway Across 12 Countries"

  # =============================================================================
  # STORY DETAIL
  # =============================================================================

  Scenario: Clicking story opens detail panel
    When the user clicks on a story card
    Then the story detail panel should open
    And the detail should show the story Title
    And the detail should show Situation, Task, Action, Result

  Scenario: Story detail shows STAR format
    When the user clicks on a story card
    Then the detail should have a Situation section
    And the detail should have a Task section
    And the detail should have an Action section
    And the detail should have a Result section

  Scenario: Closing detail returns to list
    Given the user has opened a story detail
    When the user clicks the close button
    Then the story detail should be closed
    And the story list should be visible

  # =============================================================================
  # ASK AGY ABOUT THIS
  # =============================================================================

  Scenario: Ask Agy button appears in story detail
    When the user clicks on a story card
    Then the "Ask Agy About This" button should be visible

  Scenario: Ask Agy navigates to Ask MattGPT with context
    Given the user has opened a story detail
    When the user clicks "Ask Agy About This"
    Then the page should navigate to Ask MattGPT
    And the question should reference the story

  Scenario: Ask Agy works from Table view
    Given the user is in Table view
    When the user clicks on a story row
    And the user clicks "Ask Agy About This"
    Then the page should navigate to Ask MattGPT

  Scenario: Ask Agy works from Cards view
    Given the user is in Cards view
    When the user clicks on a story card
    And the user clicks "Ask Agy About This"
    Then the page should navigate to Ask MattGPT

  # =============================================================================
  # DEEPLINKS
  # =============================================================================

  Scenario: Valid deeplink opens story detail
    When the user navigates to "?story=building-jp-morgans-global-payments-gateway-across-12-countries%7Cjp-morgan-chase"
    Then the story detail should be open
    And the story should be "Building JP Morgan's Global Payments Gateway Across 12 Countries"

  Scenario: Deeplink respects view mode
    Given the user preference is Cards view
    When the user navigates to "?story=building-jp-morgans-global-payments-gateway-across-12-countries%7Cjp-morgan-chase"
    Then the view should be Cards view
    And the story detail should be open

  Scenario: Share link generates correct URL
    Given the user has opened a story detail
    When the user clicks the Share button
    Then the clipboard should contain the story deeplink URL

  # =============================================================================
  # PAGINATION
  # =============================================================================

  Scenario: Pagination shows correct page count
    Given there are more than 25 stories
    Then the pagination should show page numbers
    And the current page should be 1

  Scenario: Next page loads more stories
    Given the user is on page 1
    When the user clicks "Next"
    Then page 2 should be displayed
    And different stories should be shown

  Scenario: Page size selector works
    When the user changes page size to 50
    Then up to 50 stories should be displayed per page

  Scenario: Pagination resets on new search
    Given the user is on page 3
    When the user types "cloud" in the search box
    And the user presses Enter
    Then the page should reset to 1

  Scenario: Pagination resets on filter change
    Given the user is on page 2
    When the user selects "Financial Services / Banking" from the Industry filter
    Then the page should reset to 1

  # =============================================================================
  # NAVIGATION - ALWAYS START FRESH
  # =============================================================================

  # UX Rule: Explore Stories is a browsing experience, not a working session.
  # Users expect a fresh start when they navigate back.
  # Retaining state creates confusion ("why is this old story showing?").
  # 0 extra steps to start fresh vs 2-3 steps to clear stale state.

  Scenario: Navigation to Explore Stories always starts fresh
    Given the user was previously on Explore Stories with filters and a story open
    When the user navigates away and returns
    Then all filters should be cleared
    And the search box should be empty
    And no story detail should be open

  Scenario: Return from Ask MattGPT starts fresh
    Given the user has searched for "payments"
    And the user has selected "Financial Services / Banking" from the Industry filter
    And the user has opened a story detail
    When the user clicks "Ask Agy About This"
    And the user navigates back to Explore Stories
    Then all filters should be cleared
    And the search box should be empty
    And no story detail should be open

  Scenario: Return from About page starts fresh
    Given the user has searched for "payments"
    When the user navigates to About Matt
    And the user navigates back to Explore Stories
    Then all filters should be cleared
    And the search box should be empty

  Scenario: Deeplinks still work (exception to fresh start)
    When the user navigates to "?story=building-jp-morgans-global-payments-gateway-across-12-countries%7Cjp-morgan-chase"
    Then the story detail should be open
    And the story should be "Building JP Morgan's Global Payments Gateway Across 12 Countries"

  # =============================================================================
  # RESPONSIVE DESIGN
  # =============================================================================

  Scenario: Mobile layout stacks filters
    When the browser window is 375px wide
    Then filters should be stacked vertically
    And content should not overflow horizontally

  Scenario: Tablet layout shows 2 columns
    When the browser window is 768px wide
    Then cards should display in 2 columns

  Scenario: Desktop layout shows full filters
    When the browser window is 1200px wide
    Then all filters should be visible inline
    And cards should display in 3 or more columns

  # =============================================================================
  # EDGE CASES
  # =============================================================================

  Scenario: Rapid filter changes don't cause errors
    When the user rapidly toggles Industry filter 5 times
    Then no error should be displayed
    And the final filter state should be consistent

  Scenario: Search with special characters
    When the user types "C++ & .NET" in the search box
    And the user presses Enter
    Then no error should be displayed

  Scenario: Very long search query
    When the user types a 500 character query in the search box
    And the user presses Enter
    Then no error should be displayed
    And the query should be processed
