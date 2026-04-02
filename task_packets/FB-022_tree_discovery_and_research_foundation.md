# FB-022: Tree Discovery and Research Foundation

## Objective

Make the family tree navigable at scale and establish the foundational research-workflow support that genealogy-focused family members need to use Family Book as their primary working tool.

## Why / KPI

Directly improves CFLSR by removing the biggest tree-navigation bottleneck (no search), fixing the content hierarchy that buries engaging content below admin metadata, and adding research notes so the genealogy-researcher persona can track in-progress work inside the app rather than externally.

## Scope

### In scope

**Slice 1: Tree Search and Navigate-to-Node**

- Add a search input to the tree page (left panel or floating)
- Search filters `treeData.persons` client-side by display name, first name, last name, nickname (case-insensitive substring match)
- Results appear in a dropdown below the search input (max 8 results)
- Selecting a result pans and zooms the tree to center that node, and optionally opens the sidebar
- Keyboard accessible: type to search, arrow keys to navigate results, Enter to select, Escape to close
- Empty state: "No matching family members"
- Clear button to reset search

**Slice 2: Person Page Content Hierarchy**

- Reorder `person.html` sections to match the UX North Star content-over-chrome principle:
  1. Profile header (identity, key dates, edit button)
  2. Bio
  3. Moments (stories, notes, timeline entries for this person) — move UP from bottom
  4. Photos & Media
  5. Relationships
  6. Contact information
  7. Burial details (if deceased)
  8. Languages, Medical History
  9. Version History — move DOWN to last
- Move the "add moment" button/composer to be more prominent (above the moments list, not hidden behind a toggle)
- No backend changes required

**Slice 3: Research Notes Per Person**

- Add `research_notes` field to Person model:
  - Type: Text, max 5000 chars
  - Not encrypted (research notes are shared family knowledge, not sensitive PII)
  - Visible to all active family members
  - Editable by anyone with `can_manage` access
- Alembic migration for the new column
- Add `research_notes` to `PersonCreate`, `PersonUpdate`, and `PersonDetail` schemas
- Add `research_notes` to the person edit page (`person_edit.html`) as a dedicated section below Bio, above Medical History
- Add `research_notes` to the tree sidebar Details tab
- Include in revision snapshots for audit trail
- Add to person API responses (respecting existing redaction rules)

### Out of scope

- Family-level completeness dashboard (deferred to Sprint 18, G-04)
- Per-field source citations (deferred to G-07)
- Timeline view (deferred to G-08)
- GEDCOM import (deferred to G-10)
- Relationship calculator (deferred to G-06)
- Changes to the moments feed page or admin page

## Dependencies

- Sprint 16 tree workspace must be stable (confirmed: S16 closed, pass)
- No external service dependencies
- No data model conflicts with existing fields

## Task Type

Feature development (frontend + backend + migration)

## Likely Files

### Slice 1 (Tree Search)
- `app/static/js/tree.js` — search logic, results dropdown, zoom-to-node
- `app/static/css/main.css` — search input and results styling
- `app/templates/tree.html` — search input markup in left panel

### Slice 2 (Content Hierarchy)
- `app/templates/person.html` — section reordering
- `app/static/css/main.css` — any layout adjustments for new order

### Slice 3 (Research Notes)
- `app/models/person.py` — add `research_notes` field
- `alembic/versions/` — new migration
- `app/routes/persons.py` — include in create/update/detail schemas
- `app/services/revision_service.py` — include in snapshot serialization
- `app/templates/person_edit.html` — research notes section
- `app/static/js/tree.js` — research notes in sidebar Details tab
- `app/templates/person.html` — optional: show research notes section on profile

## Local Validation Commands

```bash
# Syntax check
uv run python -m compileall app tests

# Migration
uv run alembic upgrade head

# API tests
uv run pytest tests/test_api.py tests/test_pages.py -q

# Moments/media regression
uv run pytest tests/test_moments.py tests/test_media.py -q

# Browser flow
make test-ui-playwright

# CodeMap governance
uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json
```

## Acceptance Criteria

### Slice 1: Tree Search
1. A search input is visible on the tree page without requiring scroll or panel expansion
2. Typing 2+ characters filters matching persons by display name, first name, last name, or nickname (case-insensitive)
3. Selecting a search result pans and zooms the tree to center the matched node within the visible viewport
4. The search is keyboard accessible: focus via Tab, type to search, arrow keys to navigate results, Enter to select, Escape to close results
5. Searching for a name that doesn't exist shows an empty-state message
6. Selecting a search result opens the person sidebar for that node

### Slice 2: Content Hierarchy
7. On the person profile page, Moments appear above Version History in the DOM order
8. On the person profile page, Photos & Media appear above Version History
9. The "add moment" composer or its trigger button is visible without scrolling past administrative sections
10. No backend changes are introduced by this slice

### Slice 3: Research Notes
11. The Person model has a `research_notes` text field with a corresponding Alembic migration
12. Research notes can be set via `POST /api/persons` and updated via `PUT /api/persons/{id}`
13. Research notes appear in `GET /api/persons/{id}` responses for accessible persons
14. Research notes are included in revision snapshots (creating a research note triggers an audit trail entry)
15. Research notes are editable from the tree sidebar Details tab
16. Research notes are editable from the person edit page
17. Research notes are visible on the person profile page (in an appropriate position per the content hierarchy)

### Regression
18. Existing tree interactions (node click, sidebar tabs, graph mode, moments/media) remain functional
19. `make test-ui-playwright` passes
20. `uv run pytest tests/test_api.py tests/test_pages.py -q` passes
21. CodeMap governance shows no new FAIL results

## Definition of Done

All acceptance criteria pass. Validation commands are reproducible and passing. Browser evidence demonstrates tree search working with real rendered behavior. No P0/P1 issues remain in scope. CFLSR is preserved or improved.

## Evaluation Environment

- **Task:** Feature development across frontend, backend, and migration
- **Verifier:** Automated tests (pytest + playwright) plus manual browser evidence for tree search behavior
- **Reference/oracle:** UX North Star principles (content-over-chrome, in-context editing, tree-as-workspace)
- **Expected evidence:** Test results, browser screenshots showing tree search in action, API test showing research_notes round-trip
- **Known failure modes / reward hacks:**
  - Search that only works with exact match (must be substring/case-insensitive)
  - Zoom-to-node that centers the node but at wrong zoom level (too zoomed in/out to be useful)
  - Research notes that appear in API but not in the sidebar (frontend-only omission)
  - Content hierarchy change that breaks moment composer or HTMX lazy-loading
- **Verifiability class:** `bounded-judgment` (search UX requires visual inspection, API changes are deterministic)
- **Context policy:** Builder should read `foundation/UX_NORTH_STAR.md`, the tree.js file, and the person model before starting. Exploration of D3 zoom APIs is expected but should not expand scope.

## Risk and Verification Notes

### Complexity hotspots
- D3 zoom-to-node: the `zoomTo(x, y, scale)` interaction must feel smooth and land at a useful zoom level. Builder should test with both small (5 person) and larger (20+ person) trees.
- HTMX lazy-load sections on person.html may depend on DOM order for trigger timing. Reordering sections in Slice 2 should be tested to confirm lazy-load still fires correctly.

### Likely shallow-pass failure modes
- Search that passes tests but doesn't actually zoom the viewport (only sets internal state)
- Research notes field added to model but not wired into revision snapshots
- Person page reorder that looks correct but breaks the moment composer's JS initialization

### Required verification depth
- Tree search must be demonstrated with browser evidence, not just unit tests
- Research notes must be verified through a create → read → update → history round-trip
- Person page reorder must be verified with a real page render showing the new section order

### What counts as sufficient discriminative power
- At least one negative-case check (search for non-existent name, verify empty state)
- At least one regression check (existing tree sidebar still works after search is added)
- Research notes appear in revision history (not just current state)

## Execution Budget

### Builder may explore autonomously
- D3 zoom/pan API for smooth scroll-to-node behavior
- CSS/layout approaches for search input placement
- Collapsible section patterns for research notes in sidebar

### Requires escalation
- Any change to the Person model beyond adding `research_notes`
- Any change to access control logic
- Any change to the revision snapshot schema beyond adding the new field
- Any scope expansion into completeness prompts, source citations, or timeline features

### Material scope drift
- Adding new API endpoints beyond the existing person CRUD
- Modifying the moments or media APIs
- Changing tree layout algorithm or node rendering beyond search highlight

### Proof obligations before review
- Working tree search with browser evidence
- Research notes API round-trip (create, read, update, history)
- Person page screenshot showing new section order
- Passing test suite
