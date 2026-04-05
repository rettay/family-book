# Task Packet - FB-093 Relationship Edit from Tree

## Objective

Let users change the kind of a parent-child relationship (biological / adoptive / step / foster / guardian) and remove parent-child or partnership relationships directly from the tree context menu, without opening the full sidebar form.

## Why / KPI

- Correcting a mis-tagged relationship (e.g. biological → adoptive) currently requires opening the sidebar, switching to the relationships tab, finding the right card, and editing a form. For a simple kind correction on the canvas this is too many clicks.
- Relationship kind is the most-edited relationship field — it drives the visual edge style on the tree and the relationship calculator output. Making it one click from the canvas increases data quality without friction.
- Leverages the context menu infrastructure from S40 — no new UI patterns required.

## Scope

**In scope:**
- Context menu for a tree node gets a new "Edit relationships" item
- Clicking it opens a small inline popover listing the person's relationships (parent-child rows, partnership rows) with per-row controls:
  - **Parent-child row:** kind selector (dropdown with all `ParentChildKind` values) + "Remove" button
  - **Partnership row:** "Remove" button only (partnership kind/status editing stays in the sidebar details form — out of scope here)
- Kind change: `PUT /api/relationships/parent-child/{rel_id}` with the new kind; tree edge re-styles on success without full reload
- Remove (parent-child): `DELETE /api/relationships/parent-child/{rel_id}` with inline confirm step (two-button confirm, no `window.confirm()`)
- Remove (partnership): `DELETE /api/relationships/partnership/{rel_id}` with inline confirm step
- After any change, the affected edges are redrawn without a full `render()` call
- Relationship IDs are looked up from `treeData.parent_child` and `treeData.partnerships` using person IDs
- i18n: add keys `tree.edit_relationships` ("Edit relationships"), `tree.relationship_kind_label` ("Relationship kind"), `tree.remove_relationship` ("Remove"), `tree.remove_confirm` ("Remove this relationship?"), `tree.remove_confirm_yes` ("Yes, remove"), `tree.remove_confirm_no` ("Cancel")

**Out of scope:**
- Adding new relationships from this popover (add parent / add child / add partner remains in the context menu + sidebar flow from S40)
- Editing partnership kind, status, or dates from this popover
- Editing confidence, source, or notes from this popover
- Bulk relationship operations

## Task Type

- Member-facing UI — tree canvas enhancement

## Dependencies

- `PUT /api/relationships/parent-child/{rel_id}` — already exists (`app/routes/relationships.py` line ~202)
- `DELETE /api/relationships/parent-child/{rel_id}` — already exists (line ~180)
- `DELETE /api/relationships/partnership/{rel_id}` — already exists (line ~415)
- `treeData.parent_child[].id` and `treeData.partnerships[].id` are available in client-side JS
- FB-092 not required; packets are independent

## Target Personas

- `family_admin` — corrects relationship kinds imported from GEDCOM or added with wrong type
- `genealogy_researcher` — fixes adoptive/biological/guardian distinctions that affect the visual and the relationship calculator

## Changed Surfaces

- `GET /tree` — context menu gains "Edit relationships" action; inline relationship popover added

## Likely Files

- `app/static/js/tree.js` — add "Edit relationships" to `showTreeContextMenu` items array; add `showRelationshipEditPopover(personId, anchorEl)` function; add kind-change and remove handlers; add edge redraw logic
- `app/templates/tree.html` — add `#tree-rel-edit-popover` container (hidden by default)
- `app/static/css/main.css` — popover styles, kind dropdown, confirm row
- `locales/en.json` + 4 others — 6 new `tree.*` keys (listed in scope)

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual: right-click a node with a parent-child relationship
# → "Edit relationships" → popover lists relationships
# Change kind → edge on canvas updates to new style
# Click Remove → confirm row appears → confirm → edge disappears
# Cancel remove → edge unchanged

uv run pytest tests/ -v
```

## Acceptance Criteria

- [ ] "Edit relationships" appears in the tree context menu for every node.
- [ ] Clicking it opens the relationship popover listing all parent-child and partnership relationships for that person.
- [ ] Changing a parent-child kind sends `PUT /api/relationships/parent-child/{id}` and the edge class on the canvas updates (e.g. `parent-child-line--adoptive`) without a full reload.
- [ ] Clicking Remove on a parent-child row shows a two-button inline confirm (no `window.confirm()`).
- [ ] Confirming remove sends `DELETE /api/relationships/parent-child/{id}` and the edge disappears from the canvas.
- [ ] Cancelling remove dismisses the confirm without changes.
- [ ] Same remove flow applies to partnership rows.
- [ ] Popover closes on Escape and when clicking outside it.
- [ ] 6 i18n keys added across all 5 locales; `test_i18n.py` passes.
- [ ] `uv run pytest tests/` passes (no regressions).

## Structural Oracle

- `#tree-rel-edit-popover` present in DOM (hidden when not editing)
- After opening: popover contains `[data-rel-id]` rows
- After kind change: `.parent-child-line[data-from][data-to]` has updated `--kind` class
- After remove: edge element absent from DOM

## Risk and Verification Notes

- **Relationship ID lookup:** `treeData.parent_child` contains full relationship objects including `id`. Look up by `parent_id + child_id` match. Store `data-rel-id` on edge paths during render (add `.attr('data-rel-id', parentChild.id)`) to make lookups cheap and reliable.
- **Partial edge redraw:** After kind change, select the specific path `[data-rel-id="{id}"]`, update its class attribute to `parent-child-line parent-child-line--{newKind}`. Also update `treeData.parent_child` in memory. Do NOT call full `render()` — it resets pan/zoom.
- **Popover positioning:** Same anchor logic as the context menu (clamp to viewport edges). The popover is wider than the context menu — account for this when clamping.
- **Remove + treeData sync:** After a successful DELETE, remove the relationship from `treeData.parent_child` (or `treeData.partnerships`) in memory and remove the SVG edge element directly. This avoids a full re-fetch.
- **Access control:** Both PUT and DELETE endpoints call `_require_manageable_person`. If the user lacks permission they'll get a 403. Show an inline error in the popover ("You don't have permission to edit this relationship.").

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Menu item present | Right-click any node | Context menu | "Edit relationships" item visible | Item absent |
| Popover lists rels | Click "Edit relationships" | Popover DOM | Row per relationship shown | Empty popover |
| Kind change | Change dropdown, save | Edge class on SVG | Edge re-styled immediately | Reload required or edge unchanged |
| Remove with confirm | Click Remove → confirm | Edge gone | Edge removed from canvas | Edge persists |
| Remove cancel | Click Remove → cancel | Edge unchanged | No change | Edge removed |
| Escape closes popover | Press Escape | Popover hidden | Popover dismissed | Popover stays open |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes
- [ ] i18n parity maintained
- [ ] Manually verified: kind change, remove with confirm, remove cancel, Escape dismissal
