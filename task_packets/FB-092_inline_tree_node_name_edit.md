# Task Packet - FB-092 Inline Tree Node Name Edit

## Objective

Replace the tree node double-click "go to edit page" behaviour with an inline name-edit overlay on the canvas, so users can fix a person's first/last name without leaving the tree.

## Why / KPI

- Navigating to `/people/{id}/edit` for a simple name typo breaks the browsing flow. Users return to the tree, re-pan, re-zoom, and re-select the node. The full round-trip kills momentum.
- The tree is the workspace (UX North Star). Inline editing keeps the user in context and lowers the cost of data quality fixes.
- This is the first step of the tree-native editing vision and delivers standalone value with bounded scope.

## Scope

**In scope:**
- Double-click on a tree node opens an inline floating overlay anchored to that node
- Overlay contains two plain `<input>` fields: first name, last name (pre-filled from current values)
- Save: Enter key or a "Save" button — PATCH `/api/persons/{id}` with updated names, then refresh the node label on the canvas without a full tree reload
- Cancel: Escape key or a "Cancel" button — overlay dismissed, no change
- After save, the SVG node text updates in place (no full `render()` call required)
- The overlay is keyboard-accessible: Tab moves between inputs, Enter saves, Escape cancels
- If the save fails (422, network error), show an inline error message in the overlay and leave it open
- The existing dblclick→`/people/{id}/edit` navigation is replaced by this flow
- i18n: use existing person field labels where applicable; add two keys: `tree.edit_name_title` ("Edit Name"), `tree.edit_name_save` ("Save")

**Out of scope:**
- Editing any field other than first_name and last_name from this overlay (nickname, birth date, etc. remain in the sidebar details form)
- Root person inline edit — the root person's name is not displayed on the tree, so there is nothing to click; if somehow triggered, the PATCH will succeed but display name remains redacted
- Drag-to-reposition or relationship editing (separate packets)

## Task Type

- Member-facing UI — tree canvas enhancement

## Dependencies

- None. `PATCH /api/persons/{id}` already exists and handles partial updates.

## Target Personas

- `contributing_member` — fixes name typos discovered while browsing
- `family_admin` — corrects maiden names, formal vs. preferred names
- `genealogy_researcher` — most likely to find data quality issues while traversing the tree

## Changed Surfaces

- `GET /tree` — canvas interaction (dblclick behaviour changes)
- `PATCH /api/persons/{id}` — called from new JS path (no endpoint change)

## Likely Files

- `app/static/js/tree.js` — replace dblclick handler (line ~2601), add `showNameEditOverlay(personId, anchorEl)` function, add save/cancel logic, add node label update after save
- `app/templates/tree.html` — add `#tree-name-edit-overlay` container (hidden by default), with two inputs and Save/Cancel buttons
- `app/static/css/main.css` — overlay positioning, input styles, error state
- `locales/en.json` + 4 others — `tree.edit_name_title`, `tree.edit_name_save`

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual: double-click a tree node — overlay should appear anchored to node
# Edit first name, press Enter — node label updates, overlay closes
# Press Escape while overlay is open — overlay closes, name unchanged
# Tab between inputs, keyboard-only save

uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] Double-clicking a tree node opens the name-edit overlay anchored near the node.
- [ ] Overlay is pre-filled with the person's current first_name and last_name.
- [ ] Pressing Enter or clicking Save sends PATCH `/api/persons/{id}` and updates the node label in place.
- [ ] Pressing Escape or clicking Cancel closes the overlay without changes.
- [ ] Save failure (422 or network error) shows an inline error and keeps the overlay open.
- [ ] Node label reflects the new name without a full tree reload.
- [ ] Overlay is keyboard-accessible (Tab, Enter, Escape work as expected).
- [ ] Root person: dblclick opens overlay; PATCH succeeds; display name on canvas remains redacted (unchanged from before).
- [ ] Two i18n keys added and present in all 5 locales; `test_i18n.py` passes.
- [ ] `uv run pytest tests/` passes (no regressions).

## Structural Oracle

- `#tree-name-edit-overlay` present in DOM (hidden when not editing)
- `#tree-name-edit-overlay input[name="first_name"]` and `input[name="last_name"]` exist
- After dblclick, overlay `hidden` attribute is removed
- After save, `[data-id="{id}"] text` content reflects updated name

## Risk and Verification Notes

- **Overlay positioning:** The overlay must be positioned in screen coordinates relative to the clicked node's SVG transform + the SVG container's bounding rect. Use `getBoundingClientRect()` on the node element after `getTranslate()`. Clamp to viewport edges (same pattern as context menu).
- **Partial re-render after save:** Do not call the full `render()` function — it resets pan/zoom. Instead update only the text element of the affected node: `d3.select('[data-id="' + id + '"] text').text(newLabel)`. Also update the in-memory `treeData.persons` entry so subsequent interactions see the new name.
- **Root person:** The canvas renders root person with `display_name` (e.g. "Our Family Root"). After a PATCH of the underlying names, the tree data will be re-fetched on next load; on the current session the displayed name does not change. This is acceptable — the redaction is presentation-only.
- **i18n keys placement:** Add the two `tree.*` keys inside the existing `"tree"` namespace block if one exists, or at top level with a `tree.` prefix — whichever pattern the existing locale files use.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Overlay opens on dblclick | Double-click node | `#tree-name-edit-overlay` visible | Overlay appears near node | Full page navigates to /edit |
| Pre-fill | Observe inputs | Input values match person data | Correct names in inputs | Blank inputs |
| Save updates label | Save after editing | Node text in SVG | New name visible on canvas without reload | Page reloads, or label unchanged |
| Escape cancels | Press Escape | Overlay hidden, label unchanged | No change | Name changes or overlay stays open |
| Error handling | Save with empty first name (422) | Error message in overlay | Overlay stays open with error | Silent failure |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes
- [ ] i18n parity maintained
- [ ] Manually verified: dblclick → edit → save → label updates; Escape cancels; error on blank name
