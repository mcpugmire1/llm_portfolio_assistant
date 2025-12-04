# Explore Stories UI Checklist

Use this checklist to verify the UI is working correctly after making changes.

## Results Summary Row
- [ ] "115 projects found • Showing 1-10" displays on left
- [ ] "SHOW:" label is on same line
- [ ] Dropdown shows "10" (not "1", not blank)
- [ ] Dropdown width is narrow (fits "10", "20", "50")
- [ ] "Table | Cards" toggle is on same line at right
- [ ] All elements aligned horizontally

## Data Table (AgGrid)
- [ ] Table displays with 4 columns: Title, Client, Role, Domain
- [ ] Column proportions: Title (45%), Client (20%), Role (15%), Domain (20%)
- [ ] Rows have proper height (70px)
- [ ] Text is 14px
- [ ] Font size is readable
- [ ] Clicking a row selects it
- [ ] No empty space below table

## Pagination
- [ ] Pagination buttons display: First | Prev | 1 | 2 | 3 | ... | Next | Last
- [ ] Current page highlighted (red border/background)
- [ ] Button style matches Table/Cards segmented control
- [ ] Disabled buttons are grayed out
- [ ] "Page 1 of X" shows on right
- [ ] Starts at "Page 1" on load

## Detail Panel
- [ ] Shows selected story details below table
- [ ] Title displays
- [ ] Client • Role • Domain metadata line
- [ ] 5P Summary paragraph
- [ ] Key Achievements (max 4)
- [ ] "Ask MattGPT" button

## Light/Dark Mode
- [ ] All text visible in light mode
- [ ] All text visible in dark mode
- [ ] Borders visible in both modes

## Spacing
- [ ] No excessive gaps between sections
- [ ] Filter section compact
- [ ] Results summary compact
- [ ] Pagination spacing appropriate

## Functional Tests
- [ ] Clicking page numbers changes page
- [ ] Changing SHOW dropdown updates results
- [ ] Switching Table/Cards view works
- [ ] Filters work correctly
- [ ] Selecting a row updates detail panel
