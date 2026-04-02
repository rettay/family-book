# Task Packet - FB-065 Media Delete Buttons

## Objective

Expose a delete action on media items across all gallery surfaces so family members can remove photos, videos, and documents they uploaded, with confirmation to prevent accidents.

## Why / KPI

- The soft-delete API exists (`DELETE /api/media/{id}`) but no UI button triggers it anywhere.
- Users who upload the wrong file or a duplicate have no way to remove it without admin intervention.
- CFLSR improves when contributors feel confident they can correct mistakes.

## Scope

- In scope:
  - Add a delete button (trash icon) to each media item in the tree sidebar media tab
  - Add a delete button to each media item in the wiki person gallery (media_gallery.html)
  - Add a delete button to each media item in the global /gallery page (global_gallery_items.html)
  - Confirmation prompt before delete ("Remove this photo?" with Cancel/Remove)
  - After delete: remove the item from the DOM without full page reload
  - If the deleted media is the person's current headshot, clear the tree node photo and show initials
  - Only show delete button to users who can manage the person (uploader or admin)
  - i18n for delete button label and confirmation text across en, es, ru, it, zh
- Out of scope:
  - Undo/restore UI (admin can restore via moderation queue)
  - Bulk delete
  - Permanent delete from UI (admin-only via API)

## Task Type

- member-facing UX enhancement

## Dependencies

- None. Independent of other S35 packets.

## Likely Files

- `app/static/js/tree.js` (createMediaNode — add delete button after headshot button)
- `app/static/js/main.js` (shared deleteMedia function with confirmation)
- `app/templates/partials/media_gallery.html` (add delete button per item)
- `app/templates/partials/global_gallery_items.html` (add delete button per item)
- `app/routes/media.py` (verify DELETE endpoint handles non-admin soft-delete correctly)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`
- `tests/test_media.py` (test delete via API if not already covered)

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_pages.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task: add delete buttons to all media surfaces
- Verifier: API test for delete round-trip; page-load assertions for delete button presence
- Reference/oracle: existing headshot star button pattern as interaction model
- Expected evidence: delete button visible on media items; clicking it removes the item after confirmation
- Known failure modes:
  - Delete button appears but doesn't actually call the API
  - Item disappears from DOM but reappears on refresh (API call failed silently)
  - Deleting a headshot photo leaves a stale photo_url on the person record
- Verifiability class: `bounded-judgment`
- Context policy: soft-delete only; confirm before action

## Acceptance Criteria

- [ ] Tree sidebar media items show a delete button (trash icon or similar).
- [ ] Wiki person gallery media items show a delete button.
- [ ] Global gallery media items show a delete button.
- [ ] Clicking delete shows a confirmation prompt before proceeding.
- [ ] After confirmed delete, the item is removed from the DOM immediately.
- [ ] Deleted media is soft-deleted (visibility=hidden) via the API.
- [ ] Delete button only appears for users who can manage the person.
- [ ] If the deleted media was the person's headshot, the tree node reverts to initials.
- [ ] i18n keys for delete label and confirmation across en, es, ru, it, zh.
- [ ] No regression on existing media surfaces.

## Risk and Verification Notes

- Complexity hotspot: headshot photo deletion must also clear person.photo_url to avoid stale references.
- The existing DELETE endpoint already protects against deleting another person's headshot — verify this still works.
- The tree sidebar needs to refresh after delete to reflect the change.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] No P0/P1 regressions
