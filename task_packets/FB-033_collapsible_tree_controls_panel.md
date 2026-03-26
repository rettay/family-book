# FB-033: Collapsible Tree Controls Panel

## Objective

Make the left-hand tree controls panel (search, display preferences, relationship calculator, legend, filters) collapsible so users can maximize the tree canvas area when they don't need the controls.

## Why / KPI

**CFLSR impact:** Medium. The tree is the primary workspace. On smaller screens or when users are focused on browsing the tree rather than filtering or searching, the 280-340px left panel takes valuable horizontal space. A collapse toggle — matching the pattern already established on the right-hand person sidebar — gives users full-width tree viewing when they want it.

**User feedback:** User requested this feature directly, noting that the right sidebar already has a caret collapse button but the left panel does not.

## In Scope

- **Collapse button** on the left panel (matching right sidebar pattern: a caret button)
- **Expand tab** on the left edge when collapsed (matching the right sidebar's `sidebar-expand-tab` pattern)
- **Smooth animation** using CSS transform or grid transition
- **State persistence** — remember collapsed/expanded state in localStorage or tree preferences
- **Responsive behavior** — on mobile (<900px) the panel already stacks vertically; collapse behavior applies to desktop grid layout only

## Out of Scope

- Redesigning the left panel content
- Moving controls into the tree canvas (floating toolbar)
- Changing the right sidebar behavior

## Existing Pattern to Match

The right-hand person sidebar (`person-sidebar`) uses:
- `.person-sidebar__collapse` button (caret `&#x276F;`) at top of sidebar → removes `person-sidebar--open` class
- `#sidebar-expand-tab` button (caret `&#x276E;`) on the right edge → shown when collapsed, hidden when open
- CSS `transform: translateX(100%)` for hide, `translateX(0)` for show
- `collapseSidebar()` and `expandSidebar()` functions in tree.js

The left panel should follow the same UX pattern but mirrored (collapse slides left, expand tab appears on left edge).

## Acceptance Criteria

- [ ] Left tree controls panel has a collapse button (caret or chevron)
- [ ] Clicking collapse hides the panel and expands the tree canvas to full width
- [ ] A visible expand tab appears on the left edge when the panel is collapsed
- [ ] Clicking the expand tab restores the panel
- [ ] Collapse/expand animates smoothly (CSS transition)
- [ ] Collapsed state persists across page reloads (localStorage)
- [ ] Mobile layout (<900px) is unaffected
- [ ] Keyboard accessible (focusable, operable via Enter/Space)

## Likely Files

| File | Change |
|------|--------|
| `app/templates/tree.html` | Add collapse button to `.tree-panel`, add expand tab element, update grid CSS |
| `app/static/js/tree.js` | Add `collapseTreePanel()` / `expandTreePanel()` functions, localStorage persistence |
| `app/static/css/main.css` | Optional: move tree panel CSS from tree.html inline styles to main.css |

## Complexity

Low-medium. Follows an established pattern (right sidebar collapse). Main work is CSS grid transition when the left column collapses, plus the toggle logic.

## Definition of Done

- Left panel can be collapsed and expanded with smooth animation
- Expand tab visible on left edge when collapsed
- State persists across reloads
- No regression on right sidebar or mobile layout
