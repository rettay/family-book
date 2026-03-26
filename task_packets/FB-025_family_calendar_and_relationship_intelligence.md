# FB-025: Family Calendar and Relationship Intelligence

## Objective

Make Family Book a place families visit regularly by surfacing stored dates as a living calendar, computing human-readable relationship paths between any two people, and visually distinguishing relationship types on the tree.

## Why / KPI

Directly improves CFLSR by creating recurring engagement (calendar), social delight (relationship calculator), and visual trust (seeing adoption vs. biological on the tree). The calendar rewards every date entry with a richer family view. The relationship calculator is the single highest-delight feature in the backlog — it turns the tree into a tool you use at family gatherings.

## Scope

### In scope

**Slice 1: Family Calendar**

- New `/calendar` page accessible from main navigation
- Auto-populate events from existing data:
  - Person birth dates (recurring annual, label: "{name}'s birthday")
  - Person death dates (recurring annual, label: "Remembering {name}")
  - Partnership start_date (recurring annual, label: "{name} & {name} anniversary")
  - Moments with `occurred_at` (one-time, label from moment title)
- Monthly grid view with day cells showing event dots/chips
- Day detail panel: click a day to see all events for that date
- Month navigation (prev/next) and jump-to-month selector
- Filter by event type: birthdays, remembrances, anniversaries, moments
- Root person redaction: use `display_name`, never raw names
- Responsive: calendar grid stacks gracefully on mobile (list view fallback)
- No new data model — all events computed from existing Person, Partnership, and Moment records
- API endpoint: `GET /api/calendar?month=YYYY-MM` returns events for the month
- HTMX-driven: server-rendered calendar partial, no client-side JS calendar library

**Slice 2: Relationship Calculator**

- Two-person selection mode on the tree page:
  - "Calculate Relationship" button in tree toolbar
  - Click first person, click second person
  - Display result in a panel/modal
- API endpoint: `GET /api/relationships/path?from={person_id}&to={person_id}`
- BFS/DFS path-finding through ParentChild and Partnership edges
- Human-readable relationship labeling:
  - Direct: parent, child, sibling, grandparent, grandchild, uncle/aunt, niece/nephew
  - Extended: cousin (with degree and removal), e.g. "second cousin once removed"
  - In-law relationships through partnerships
  - Step/adoptive qualification when ParentChild.kind is not biological
- Path visualization: highlight the connecting nodes and edges on the tree
- Handle disconnected persons: "No relationship path found" message
- Handle root person: use display_name in result text
- Performance: cache graph adjacency for the session; path computation should be fast for trees up to 500 persons

**Slice 3: Visual Relationship Types on Tree**

- Distinguish ParentChild.kind values visually on tree edges:
  - `biological`: solid line (current default — no change)
  - `adoptive`: dashed line with distinct color
  - `step`: dotted line with distinct color
  - `foster`: dash-dot line with distinct color
  - `guardian`: thin dashed line with distinct color
  - `unknown`: solid line, muted/gray
- Distinguish Partnership.kind visually on tree:
  - `married`: solid connector (current default)
  - `domestic_partner`: dashed connector
  - `co_parent`: dotted connector
  - `engaged`: thin solid connector
  - `other`: muted connector
- Legend: add a collapsible legend to the tree page showing line styles
- Respect existing tree preferences and theme tokens for colors
- Edge labels optional: show kind text on hover/focus

### Out of scope

- Manually-created recurring calendar events (use Moments for family traditions)
- Calendar push notifications or email reminders
- iCal/Google Calendar export (future sprint)
- Fan chart or pedigree views (G-11, separate sprint)
- Relationship suggestions ("you might want to add...")
- Genetic relationship inference

## Acceptance Criteria

### Slice 1: Family Calendar

1. `GET /api/calendar?month=2026-03` returns JSON with events array, each event having `date`, `type`, `label`, `person_id` (where applicable)
2. Calendar page renders a monthly grid with event indicators on correct dates
3. Clicking a day shows all events for that date in a detail panel
4. Birth dates appear as recurring annual events on the correct month/day
5. Death dates appear as recurring annual remembrance events
6. Partnership start_dates appear as recurring anniversary events
7. Moments with `occurred_at` appear on their specific date
8. Month navigation (prev/next) works via HTMX without full page reload
9. Event type filters (birthdays, remembrances, anniversaries, moments) toggle visibility
10. Root person events use `display_name`, not raw first_name/last_name
11. Calendar is responsive: mobile renders a list view instead of grid
12. Calendar link appears in main navigation

### Slice 2: Relationship Calculator

13. `GET /api/relationships/path?from={id}&to={id}` returns the shortest relationship path as JSON
14. Path response includes: `relationship_label` (human-readable), `path` (array of person IDs), `path_details` (array of edges with types)
15. Direct relationships labeled correctly: parent, child, sibling, grandparent, etc.
16. Cousin relationships include degree and removal: "second cousin once removed"
17. Step/adoptive relationships qualified: "adoptive mother", "step-sibling"
18. In-law relationships through partnerships: "sister-in-law", "father-in-law"
19. Disconnected persons return a clear "no path found" response (not an error)
20. Tree page has a "Calculate Relationship" mode with two-node selection
21. Relationship path highlights connecting nodes/edges on the tree
22. Root person uses display_name in all relationship labels

### Slice 3: Visual Relationship Types

23. Biological parent-child edges render as solid lines
24. Adoptive parent-child edges render with visually distinct dashed style
25. Step parent-child edges render with visually distinct dotted style
26. Partnership connectors distinguish married vs. domestic_partner vs. co_parent
27. Tree includes a collapsible legend showing relationship type line styles
28. Visual distinctions respect theme tokens and remain readable in both light and dark themes

## Technical Notes

- **Calendar data source**: Query `Person.birth_date`, `Person.death_date`, `Partnership.start_date`, `Moment.occurred_at` with appropriate date parsing
- **Date handling**: Person dates are ISO 8601 strings with precision. For calendar placement, parse to month/day. Approximate dates (year-only) should NOT appear on specific calendar days — optionally show in a "this year" section
- **Path-finding**: Build an adjacency list from ParentChild + Partnership records. BFS finds shortest path. Relationship labeling uses generation counting (parent=+1, child=-1, sibling=0) with cousin degree/removal math
- **Cousin calculation**: Common ancestor method — find the common ancestor(s) of both persons, count generations from each to the common ancestor. The lesser count minus 1 = cousin degree. The difference in counts = times removed
- **Tree edge styling**: D3.js path elements already exist. Add CSS classes based on `ParentChild.kind` and `Partnership.kind` values. Use `stroke-dasharray` for dashed/dotted styles
- **Performance**: Calendar query should be a single DB round-trip per month. Relationship path-finding loads the full graph once and computes in-memory (fine for <1000 persons)

## Dependencies

- Person model with birth_date, death_date (exists)
- Partnership model with kind, status, start_date (exists)
- ParentChild model with kind (exists)
- Moment model with occurred_at (exists)
- Tree.js with D3 rendering (exists, partnerships loaded but not visually distinguished)
- Root person redaction infrastructure (exists)

## Risks

- **Date parsing edge cases**: Person dates stored as strings with varying precision (year, year-month, full date). Calendar must handle all gracefully.
- **Disconnected graph components**: Some persons may not be connected to the main tree. Path-finding must handle this without errors.
- **Large trees**: BFS on a 500+ person tree should still be fast. Pre-compute adjacency list, don't query DB per step.
- **Relationship labeling complexity**: English kinship terminology has many edge cases (half-siblings, double cousins). Start with common cases, document limitations.
