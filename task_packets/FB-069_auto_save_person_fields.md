# Task Packet - FB-069 Auto-Save Person Fields

## Objective

Replace the manual save button in the tree sidebar person editor with debounced auto-save, so changes persist as the user types without needing to scroll to and click a save button.

## Why / KPI

- The current flow: edit a field at the top of the form → scroll to the bottom → click "Save". This is especially painful in the narrow sidebar with 40+ fields.
- The backend already supports partial updates via `PUT /api/persons/{id}` with `exclude_unset=True`.
- CFLSR improves when edits feel instant and don't require a manual commit step.

## Scope

- In scope:
  - Debounced auto-save on the tree sidebar person edit form (Details tab)
  - Each field change triggers a debounced PATCH/PUT after ~1s of inactivity
  - Only the changed field(s) are sent in the request
  - Visual feedback: subtle "Saved" indicator near the field or at the top of the form
  - Error feedback: if save fails, show inline error and don't lose the user's input
  - Remove or de-emphasize the manual "Save" button (keep as fallback but not primary)
  - Handle concurrent edits gracefully (last-write-wins is acceptable for launch)
- Out of scope:
  - Auto-save on the full person edit page (/people/{id}/edit) — keep manual save there for now
  - Conflict resolution / optimistic locking
  - Undo/revert after auto-save

## Task Type

- member-facing UX enhancement

## Likely Files

- `app/static/js/tree.js` (saveTreePerson refactor, debounce logic, field change listeners)
- `app/templates/partials/person_sidebar.html` (save button de-emphasis, saved indicator)
- `app/static/css/main.css` (saved indicator styles)
- `locales/*.json` (saved/saving labels)

## Acceptance Criteria

- [ ] Editing a field in the sidebar Details tab auto-saves after ~1s debounce.
- [ ] Only changed fields are sent to the API (partial update).
- [ ] A "Saved" indicator appears briefly after successful save.
- [ ] If save fails, an error message appears and the user's input is preserved.
- [ ] The manual save button is still present but de-emphasized (secondary style).
- [ ] Rapid edits across multiple fields are batched into a single save.
- [ ] No data loss: navigating away mid-debounce flushes the pending save.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] No regression on person data integrity
