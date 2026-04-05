# Task Packet - FB-097 Fix Tree Panel Toggle Label

## Objective

The left-panel toggle tab always shows "Expand Family Tree Settings" regardless of whether the panel is open or closed. Fix it so the tab is always visible, shows "Expand Family Tree Settings" with a right-pointing caret when the panel is closed, and "Hide Family Tree Settings" with a left-pointing caret when the panel is open.

## Root Cause

Two bugs compound:

1. **CSS overrides `[hidden]`:** `.tree-panel-expand-tab { display: flex }` in the inline `<style>` block of `tree.html` has higher specificity than the browser UA stylesheet's `[hidden] { display: none }`, so the expand tab is permanently visible regardless of the `hidden` attribute being set by JS.

2. **Two-button design is confusing:** There is a separate collapse button (`#tree-panel-collapse-btn`) inside the panel that says "Hide Family Tree Settings", and the expand tab on the canvas edge that says "Expand Family Tree Settings". The collapse button is visually buried inside the panel. The expand tab — being permanently visible due to bug 1 — is the only affordance the user ever sees, and it always says "Expand."

## Fix

Consolidate to a single always-visible toggle tab that updates its own label and caret:

- Tab always visible at the left edge of the canvas (no `hidden` toggle, no JS hide/show)
- When panel is **open**: caret points left (`❮`), label "Hide Family Tree Settings"
- When panel is **closed**: caret points right (`❯`), label "Expand Family Tree Settings"
- Remove the redundant `#tree-panel-collapse-btn` inside the panel
- `_updatePanelToggleUI(collapsed)` updates the tab's caret and label text instead of toggling `hidden`
- `aria-label` and `title` also update to match the current state

## Scope

**In scope:**
- Fix `tree.html` template: remove `#tree-panel-collapse-btn`, make `#tree-panel-expand-tab` always rendered (no `hidden` attribute), update its initial state to match panel-open
- Fix `_updatePanelToggleUI(collapsed)` in `tree.js`: update caret character and label text instead of toggling `hidden`
- Update `restoreTreePanelState()` to call `_updatePanelToggleUI` on page load with the correct initial state (default = open = `collapsed: false`)
- i18n: `tree.expand_settings` and `tree.hide_settings` keys already exist — no new keys required

**Out of scope:**
- Any other tree panel behaviour (preferences, branch view, search)
- Mobile layout (the tab is already `display: none` on mobile via the `@media` block — keep that unchanged)

## Task Type

- Bug fix

## Dependencies

- None

## Likely Files

- `app/templates/tree.html` — remove `#tree-panel-collapse-btn`, update `#tree-panel-expand-tab` markup (remove `hidden` default, update initial caret/label to show "Hide" state since panel is open by default)
- `app/static/js/tree.js` — update `_updatePanelToggleUI(collapsed)` to set caret and label text; update `restoreTreePanelState()` to always call `_updatePanelToggleUI` on load

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual:
# Load /tree — panel is open, tab shows "❮ Hide Family Tree Settings"
# Click tab — panel collapses, tab shows "❯ Expand Family Tree Settings"
# Click tab again — panel expands, tab shows "❮ Hide Family Tree Settings"
# Reload with panel collapsed (localStorage set) — tab shows "❯ Expand..."

uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] When the tree panel is **open**, the toggle tab shows a left-pointing caret and "Hide Family Tree Settings".
- [ ] When the tree panel is **closed**, the toggle tab shows a right-pointing caret and "Expand Family Tree Settings".
- [ ] The tab is always visible on desktop (not hidden or toggled out of existence).
- [ ] The caret and label update correctly on every toggle, including on page reload restoring a collapsed state.
- [ ] The redundant `#tree-panel-collapse-btn` button inside the panel is removed.
- [ ] `aria-label` on the tab reflects the current action (Hide or Expand).
- [ ] Mobile: tab remains hidden (existing `@media` rule unchanged).
- [ ] `uv run pytest tests/` passes.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes
- [ ] Manually verified: toggle updates label/caret both directions; page reload restores correct label
