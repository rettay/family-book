# Task Packet - FB-082 Replace Node Hover Buttons with Context Menu

## Objective

Remove the hover-revealed "add photo" camera icon and "add relative" plus button from tree nodes, since their functionality is now accessible via the context menu (FB-081). This declutters the node rendering and eliminates the hover-only discoverability problem (mobile users never see hover states).

## Why / KPI

- The hover buttons were the only way to trigger photo upload and relationship creation from the canvas. With the context menu, they're redundant.
- Hover-only UI elements are invisible on mobile (no hover state on touch devices). The context menu (long-press) replaces them with a mobile-friendly interaction.
- Removing hover overlays simplifies the node rendering code and reduces visual noise on dense trees.

## Scope

- In scope:
  - Remove the camera icon overlay (`.tree-node__add-photo`) from renderNode()
  - Remove the plus button (`.tree-node__add-relative`) from renderNode()
  - Remove the associated click handlers (`triggerTreePhotoUpload`, relationship tab opener)
  - Remove the CSS for these overlays
  - Keep the `triggerTreePhotoUpload` function itself (the context menu's "Upload photo" calls it)
- Out of scope:
  - Changing node click behavior
  - Changing node visual appearance (circles, photos, initials)

## Task Type

- code cleanup / UX simplification

## Likely Files

- `app/static/js/tree.js` (renderNode — remove overlay creation code)
- `app/static/css/main.css` (remove hover overlay styles)

## Acceptance Criteria

- [ ] No camera icon overlay appears on tree nodes.
- [ ] No plus button appears on tree nodes.
- [ ] Context menu "Upload photo" still works (triggerTreePhotoUpload preserved).
- [ ] Context menu "Add parent/child/partner" still works.
- [ ] Nodes render cleanly without hover artifacts.
- [ ] No JS errors from removed elements.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] Tree renders cleanly at all zoom levels
