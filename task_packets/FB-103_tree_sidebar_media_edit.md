# Task Packet - FB-103 Tree Sidebar Media Edit Controls

## Objective

Surface the same edit-details and delete capabilities from the gallery directly in the tree sidebar's media tab, so users don't have to leave the tree to manage a person's photos.

## Why / KPI

- The tree is the primary workspace. When a user clicks a person and sees their photo in the sidebar, there is currently no way to edit, delete, or correct it — they must navigate away to the gallery or bio page, losing their tree context.
- Keeping editing within the tree sidebar is the UX North Star in practice: every round-trip to another page and back costs momentum and orientation.

## Scope

**In scope:**
- In the tree sidebar's media tab, each photo item gets two additional controls (owner or admin only):
  - **Edit details** — opens the same metadata edit form from FB-101 inline within the sidebar (HTMX-loaded partial)
  - **Delete** — same delete flow as gallery (inline confirm step, removes item on confirm)
- The metadata edit form in the sidebar uses the same `wiki_media_edit_form.html` partial from FB-101 — no duplication
- After a successful edit, the sidebar media item updates in place (title, person name, etc.)
- After a delete, the media item is removed from the sidebar list
- Headshot button (already present) is unaffected

**Out of scope:**
- Crop/rotate (Cropper.js) from the sidebar — the sidebar is narrow; defer to the gallery for pixel editing
- Tagging from the sidebar (FB-102 tag picker is in the gallery edit form; not worth duplicating in the narrow sidebar)
- Any change to tree canvas rendering

## Task Type

- Member-facing UI — tree sidebar enhancement

## Dependencies

- FB-101 must be complete (the edit-details partial must exist before it can be embedded in the sidebar)
- FB-102 is independent

## Likely Files

- `app/templates/partials/tree_sidebar_media_item.html` (or equivalent sidebar media partial) — add edit and delete buttons
- `app/static/css/main.css` — sidebar action button styles (likely already exist from headshot button)
- `locales/en.json` + 4 others — no new keys needed (reuse `media.edit_details` and `media.delete` from prior packets)

## Local Validation Commands

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Manual flow:
# Click a person on the tree → open sidebar media tab
# Verify: edit-details button present on each photo (as admin)
# Click edit → metadata form loads in sidebar
# Save → sidebar item title updates
# Delete → item disappears from sidebar list

uv run pytest tests/test_s45_gallery.py -v
```

## Acceptance Criteria

- [ ] Tree sidebar media tab shows "Edit details" and "Delete" buttons on each photo item for owner or admin.
- [ ] Non-admin, non-owner members do NOT see these buttons.
- [ ] Clicking "Edit details" loads the FB-101 metadata edit form inline within the sidebar (no page navigation).
- [ ] Saving the edit form updates the sidebar item in place.
- [ ] Clicking "Delete" shows an inline confirm step. Confirming removes the item from the sidebar list.
- [ ] Headshot button behaviour is unaffected.
- [ ] No new i18n keys required; existing `media.edit_details` and `media.delete` keys are reused.
- [ ] `uv run pytest tests/` passes with no regressions.

## Structural Oracle

- Sidebar media item has `[data-edit-details-btn]` and `[data-delete-media-btn]` for admin users
- After edit save, sidebar item `[data-media-title]` reflects updated title
- After delete confirm, item removed from DOM

## Risk and Verification Notes

- **Sidebar width constraint:** The sidebar is ~340px wide when docked. The metadata edit form must be usable at that width. Verify all form inputs are accessible and not overflowing. Textarea description may need a reduced height.
- **HTMX target scoping:** The edit form loads inside the sidebar. The HTMX target must be scoped to the specific media item element, not the full sidebar content. Each sidebar media item must have a unique `id` for correct targeting.
- **Shared partial reuse:** The `wiki_media_edit_form.html` partial from FB-101 must work correctly when rendered inside a narrow sidebar container. Check that no styles assume a wide viewport.
- **No Cropper.js in sidebar:** The crop/rotate button (`openGalleryPhotoCrop`) should NOT be added here. The sidebar is not a suitable host for the Cropper.js canvas. The gallery is the right place for pixel editing.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Buttons present (admin) | Click person, open media tab | DOM buttons | Edit + Delete visible | Buttons absent |
| Buttons absent (member) | Log in as non-admin non-owner | DOM | No edit/delete buttons | Buttons shown |
| Edit opens inline | Click Edit | Form in sidebar | Form loads without navigation | Navigates away |
| Edit saves in place | Submit form | Sidebar item title | Title updated, no reload | Full page reload |
| Delete confirm | Click Delete | Confirm step appears | Two-step confirm | Immediate delete or no confirm |
| Delete removes item | Confirm delete | Sidebar list | Item gone from list | Item remains |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] `uv run pytest tests/` passes
- [ ] Manually verified at docked sidebar width (~340px): form usable, no overflow
- [ ] Headshot button unaffected
