# Task Packet - FB-081 Tree Node Context Menu

## Objective

Add a right-click (desktop) / long-press (mobile) context menu on tree nodes that surfaces the most common actions directly on the canvas, reducing sidebar dependency for frequent operations.

## Why / KPI

- Currently, every node interaction funnels through the sidebar. Users must click → wait for sidebar → find the right tab → find the action. A context menu puts the top actions one click away.
- This is Phase 1 of the tree-native interactions initiative — the lowest-risk step toward a canvas-first experience.
- CFLSR improves when contributors can act on the tree without mental context-switching between canvas and sidebar.

## Scope

- In scope:
  - **Right-click** (contextmenu event) on a tree node shows a floating menu positioned near the node
  - **Long-press** (touchstart + 500ms hold) on mobile shows the same menu
  - Menu items:
    1. **View branch** — applies branch filter for this person (existing `applyAncestorView`)
    2. **Add parent** — opens sidebar relationships tab with parent creation flow
    3. **Add child** — opens sidebar relationships tab with child creation flow
    4. **Add partner** — opens sidebar relationships tab with partner creation flow
    5. **Upload photo** — triggers file picker → auto-set as headshot
    6. **Edit details** — opens sidebar Details tab (current single-click behavior)
    7. **View profile** — navigates to wiki person page
  - Menu dismisses on: click outside, Escape key, scroll
  - Menu is keyboard navigable (arrow keys + Enter)
  - Menu positioned to stay within viewport bounds (flip if near edge)
  - Prevent the browser's native context menu on tree nodes
  - **Single-click behavior unchanged** — still opens sidebar (Phase 2 changes this)
  - i18n for all menu item labels across 5 locales
- Out of scope:
  - Changing single-click behavior (Phase 2)
  - Inline editing on nodes (Phase 2)
  - Drag-to-connect relationships (Phase 3)
  - Removing the left panel (Phase 4)

## Task Type

- member-facing tree interaction enhancement

## Likely Files

- `app/static/js/tree.js` (context menu creation, positioning, event handlers, long-press detection)
- `app/static/css/main.css` (context menu styles — floating card, shadow, hover states)
- `app/templates/tree.html` (container div for the context menu)
- `locales/en.json` + 4 other locales (menu item labels)

## Acceptance Criteria

- [ ] Right-click on a tree node shows a floating context menu near the node.
- [ ] Long-press (500ms) on mobile shows the same menu.
- [ ] Menu has 7 items: View branch, Add parent, Add child, Add partner, Upload photo, Edit details, View profile.
- [ ] Each menu item triggers the correct action.
- [ ] Menu dismisses on click outside, Escape, or scroll.
- [ ] Menu is keyboard navigable (arrow keys to move, Enter to select).
- [ ] Menu stays within viewport bounds (repositions if near edge).
- [ ] Native browser context menu is suppressed on tree nodes.
- [ ] Single-click still opens the sidebar (unchanged).
- [ ] i18n for all menu labels across 5 locales.
- [ ] Mobile long-press works without triggering a normal click.

## Risk and Verification Notes

- Long-press detection must distinguish from normal tap (touch → immediate release = click; touch → hold 500ms = context menu). Use a timer that cancels on touchend/touchmove.
- Context menu positioning near viewport edges: if the node is in the bottom-right corner, the menu should flip to appear above/left of the cursor.
- The menu must not interfere with graph mode — when graph mode is active, right-click should NOT show the context menu (graph mode has its own click handler).
- Accessibility: the menu must be reachable via keyboard. After right-clicking, focus should move to the menu. Arrow keys navigate items. Escape dismisses.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] Context menu works on desktop (right-click) and mobile (long-press)
- [ ] No interference with existing graph mode or sidebar interactions
