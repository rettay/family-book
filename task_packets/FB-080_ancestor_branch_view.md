# Task Packet - FB-080 Ancestor Branch View

## Objective

Add a "View ancestors" action to the tree sidebar that filters the tree to show only the selected person's ancestors (and their partners), with a banner indicating the active filter and a way to return to the full tree.

## Why / KPI

- Users with large family trees want to focus on a single lineage without visual noise from unrelated branches.
- A family member specifically requested the ability to see "only this person's ancestors."
- CFLSR improves when the tree workspace supports focused exploration, not just the full view.

## Scope

- In scope:
  - **"View ancestors" button** in the tree sidebar, near the existing "Set as focus" action.
  - **Client-side ancestor collection**: BFS/DFS walk up parent_child edges from the selected person, collecting all ancestor person IDs. Also include partners of each ancestor (to preserve family unit context).
  - **Filter and re-render**: Filter treeData.persons, treeData.parent_child, and treeData.partnerships to only include collected IDs. Call render() with the filtered data.
  - **Filter banner**: When ancestor view is active, show a banner above the tree: "Showing ancestors of {name}" with a "Show full tree" button.
  - **URL state**: Update the URL to `?ancestors_of={person-id}` so the view is shareable/bookmarkable. On page load, if this param is present, apply the filter after tree data loads.
  - **"Show full tree" action**: Clears the filter, re-renders with full treeData, removes the URL param.
  - **Sidebar integration**: The "View ancestors" button should be visible when a person is selected. When ancestor view is active for the current person, the button should indicate the active state (e.g., "Viewing ancestors" with a different style).
  - i18n for button label, banner text, and "Show full tree" across 5 locales.
- Out of scope:
  - Descendants-only view (future enhancement)
  - Lineage-only view (direct line without siblings)
  - Depth limiting ("show 3 generations")
  - Server-side filtering
  - Saving ancestor view as a preference

## Task Type

- member-facing tree exploration feature

## Dependencies

- None. Independent of other packets.

## Likely Files

- `app/static/js/tree.js` (collectAncestorIds function, filter logic, banner, URL state, sidebar button wiring)
- `app/templates/partials/person_sidebar.html` (add "View ancestors" button)
- `app/templates/tree.html` (banner container element)
- `app/static/css/main.css` (banner styles, button state)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task: add ancestor branch filtering to the tree
- Verifier: manual browser verification — click "View ancestors" on a person with known lineage, confirm only ancestors + their partners are shown
- Reference/oracle: the full tree as baseline, filtered tree should be a strict subset
- Expected evidence: banner visible, URL updated, "Show full tree" restores the full view
- Known failure modes:
  - Ancestor walk misses a generation (broken parent_child edge traversal)
  - Partners of ancestors not included (orphaned nodes)
  - Filter persists after clicking "Show full tree" (stale state)
  - URL param not parsed on page load (bookmark doesn't work)
- Verifiability class: `bounded-judgment`
- Context policy: client-side only; don't modify tree API

## Acceptance Criteria

- [ ] "View ancestors" button appears in the sidebar when a person is selected.
- [ ] Clicking "View ancestors" filters the tree to show only that person + all ancestors + partners of ancestors.
- [ ] A banner appears: "Showing ancestors of {name}" with a "Show full tree" button.
- [ ] "Show full tree" restores the complete tree and removes the banner.
- [ ] URL updates to include `?ancestors_of={person-id}` when filter is active.
- [ ] Loading the page with `?ancestors_of={person-id}` applies the filter on initial render.
- [ ] The ancestor walk correctly traverses all generations (not just parents).
- [ ] Partners of ancestors are included so family units render correctly.
- [ ] The sidebar "View ancestors" button shows active state when the current person's ancestors are being viewed.
- [ ] i18n for all new labels across 5 locales.

## Risk and Verification Notes

- The ancestor walk must handle: multiple parents (adoptive + biological), single parents, and persons with no parents (root of the tree).
- Filtering must preserve the parent_child and partnership edges that connect the remaining persons — don't just filter persons and leave dangling edges.
- The banner must not overlap with the graph mode banner (they're mutually exclusive — ancestor view should exit graph mode if active).

## Execution Budget

- Builder may explore: whether to store the full treeData separately from the filtered view, or re-fetch on "Show full tree".
- Recommended: keep a reference to the unfiltered treeData (e.g., `fullTreeData`) and swap between full and filtered when toggling.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] Ancestor view works for persons at any depth in the tree
