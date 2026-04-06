# Task Packet - FB-101 In-Gallery Metadata Editor

## Objective

Let any family member edit a media item's title, description, date taken, location, and person tag directly from the gallery page and the wiki media gallery — without leaving the page or navigating to a separate edit form.

## Why / KPI

- Currently metadata (title, description, date, person) can only be set at upload time. Photos uploaded without metadata — or imported from other sources — have no way to be enriched after the fact.
- The gallery is the discovery surface; unlabelled photos provide no genealogical value. Every labelled photo increases the richness of the family record.
- CFLSR improves when members can complete a contribution loop entirely within the gallery: see a photo → recognise it → add the person's name, date, and place → be seen.

## Scope

**In scope:**
- "Edit details" button on every gallery item (owner or admin) — opens an inline slide-up or side panel with a form
- Form fields:
  - **Title** (text input, `name="title"`)
  - **Description** (textarea, `name="description"`)
  - **Date taken** (text input, free text — `name="taken_date"`, e.g. "Summer 1962", "June 1985", "circa 1940")
  - **Location** (text input, free text — `name="taken_location"`, e.g. "Palermo, Sicily", "Brooklyn, NY") — new field, requires model + migration
  - **Person** (searchable select — `name="person_id"` — list of all accessible persons, same list used in upload modal)
- Form submitted via PATCH to `/api/media/{id}` — updates only the fields sent
- After save: the card updates in place (HTMX swap or JS update) — no full page reload
- New `taken_location` field on the `Media` model (Text, nullable) and Alembic migration
- PATCH `/api/media/{id}` endpoint extended to accept `taken_location` alongside existing fields
- All authenticated members can edit (not admin-gated — same as current upload)
- The "edit details" button replaces or co-exists with the existing pencil icon (crop/rotate); these are two different capabilities — crop changes the pixel data, edit-details changes the metadata

**Out of scope:**
- Multi-person tagging (FB-102)
- Crop/rotate editing (already shipped in S43)
- Batch metadata editing (future)
- Geocoding or map-based location input (free text only)
- Edit from tree sidebar (FB-103)

## Task Type

- Member-facing UI + lightweight backend extension

## Dependencies

- Requires existing `PATCH /api/media/{id}` endpoint — extend it, do not replace it
- FB-102 and FB-103 are independent and can run in parallel once FB-101 is complete

## Likely Files

- `app/models/media.py` — add `taken_location` field (Text, nullable)
- `alembic/versions/XXXX_add_media_taken_location.py` — new migration
- `app/routes/media.py` — extend PATCH handler to accept `taken_location`
- `app/services/media_queries.py` — include `taken_location` in `serialize_media_item` return dict
- `app/templates/partials/global_gallery_items.html` — add "Edit details" button; inline panel or HTMX form swap
- `app/templates/partials/media_gallery.html` — same for wiki page media gallery
- `app/templates/partials/wiki_media_edit_form.html` (new) — the edit metadata form partial
- `app/static/css/main.css` — styles for edit panel
- `locales/en.json` + 4 others — new keys (see i18n section)

## i18n Keys Required

```
media.edit_details          → "Edit details"
media.taken_date_label      → "Date taken"
media.taken_location_label  → "Location"
media.person_label          → "Person"
media.save_details          → "Save"
media.details_saved         → "Saved"
```

## Local Validation Commands

```bash
uv run alembic upgrade head
sqlite3 /data/family.db ".schema media" | grep taken_location

uv run pytest tests/test_s45_gallery.py -v
uv run pytest tests/test_i18n.py -v
```

## Acceptance Criteria

- [ ] `taken_location` column exists on the `media` table after migration.
- [ ] `PATCH /api/media/{id}` accepts `taken_location` and persists it. Returns updated fields. Auth required; 403 if not owner or admin.
- [ ] `serialize_media_item` includes `taken_location` in its return dict.
- [ ] Every image/gif card in the global gallery shows an "Edit details" button for owner or admin.
- [ ] Clicking "Edit details" opens a form (inline panel or HTMX swap) pre-filled with current title, description, taken_date, taken_location, and person_id.
- [ ] Submitting the form PATCHes the media item and updates the card in place — no full page reload.
- [ ] Person dropdown lists all accessible persons; current person_id is pre-selected.
- [ ] Free-text date and location fields accept any string (no validation beyond non-empty title if title is required).
- [ ] Same "Edit details" capability available on the wiki person page media gallery.
- [ ] All 6 i18n keys present in all 5 locales; `test_i18n.py` passes.
- [ ] `uv run pytest tests/` passes with no regressions.

## Structural Oracle

- `[data-edit-details-btn]` or equivalent present on each image card for admin user
- Edit form contains `input[name="title"]`, `textarea[name="description"]`, `input[name="taken_date"]`, `input[name="taken_location"]`, `select[name="person_id"]`
- After save, card `strong` element reflects updated title

## Risk and Verification Notes

- **PATCH vs PUT:** The existing media PATCH endpoint may only accept certain fields. Audit it before extending — do not silently drop `taken_location` by omitting it from the Pydantic schema.
- **Person dropdown population:** The edit form needs the full persons list. If it's a standalone partial, the person list must be passed into the template context when the edit form is fetched via HTMX GET.
- **Edit button alongside crop button:** The gallery card currently has a crop/rotate button (&#9999;). The "Edit details" button is additive — do not remove the crop button. Both should be visible in the meta-row for owner/admin.
- **Inline panel vs HTMX swap:** Prefer an HTMX GET that swaps the card with an edit-form partial, and a POST/PATCH that swaps back to the card. This is the simplest pattern and consistent with stories.
- **`taken_location` migration:** Simple nullable Text column, no FK, no index needed. Down migration drops the column.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Column created | sqlite3 schema | Migration | `taken_location` in schema | Column absent |
| PATCH accepts location | PATCH with taken_location | DB value | Persisted correctly | Field ignored |
| Edit button present | Admin views gallery | DOM button | Button visible on each image card | Button absent |
| Prefill on open | Open edit form | Input values | Match current media record | Blank inputs |
| Save updates card | Submit form | Card title | Updated title in DOM, no reload | Full reload or title unchanged |
| Person dropdown | Open edit form | Select options | All persons listed, current selected | Empty dropdown |
| Non-owner, non-admin | View gallery as member | Button state | No "Edit details" on others' photos | Button shown to all |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Migration up/down both succeed
- [ ] `uv run pytest tests/` passes
- [ ] i18n parity maintained
- [ ] Manually verified: open edit form → change title + location → save → card updates in place
