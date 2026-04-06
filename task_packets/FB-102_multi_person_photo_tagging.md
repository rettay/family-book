# Task Packet - FB-102 Multi-Person Photo Tagging

## Objective

Replace the single `person_id` FK on media with a proper many-to-many join table so that a single photo can be associated with multiple people — and expose tagging UI in the gallery metadata editor.

## Why / KPI

- Family photos almost always depict more than one person. The current single-person model means every photo in a group shot can only be attributed to one family member, discarding the connections to everyone else in the frame.
- Multi-person tagging dramatically increases the discoverability of photos: when a family member views their own bio page, they see all photos that include them — not just photos where they are the "primary" subject.
- This is a prerequisite for the future "photos of this person" cross-reference feature on bios.

## Scope

**In scope:**
- New `media_person_tags` join table: `media_id` (FK → media.id, cascade delete), `person_id` (FK → persons.id, cascade delete), composite PK (media_id, person_id)
- Alembic migration:
  1. Create `media_person_tags` table
  2. Back-fill: for every media row where `person_id IS NOT NULL`, insert a row into `media_person_tags(media_id, person_id)` — preserving all existing attributions
  3. The `person_id` column on `media` is **not** dropped (it remains as the "primary subject" — used for wiki bio media section and headshot logic)
- API:
  - `GET /api/media/{id}/tags` — list tagged person ids and display names
  - `POST /api/media/{id}/tags` — body: `{ "person_id": "..." }` — add a tag. Idempotent (no error if already tagged). Auth: owner or admin.
  - `DELETE /api/media/{id}/tags/{person_id}` — remove a tag. Auth: owner or admin.
- `serialize_media_item` extended to include `tagged_person_ids: list[str]` and `tagged_people: list[{id, display_name, slug}]`
  - Note: `tagged_person_ids` and `tagged_people` may already exist on the model — verify before adding duplicate fields
- Gallery metadata editor (FB-101) extended: tag picker in the edit form — multi-select or pill-style tag input showing existing tags with remove buttons and an "Add person" dropdown
- On the gallery card: show tagged people as linked names below the existing primary person link (e.g. "Also: [Name], [Name]")
- Wiki bio media section: show photos where the person appears in `media_person_tags` in addition to photos where `person_id = person.id`

**Out of scope:**
- Face detection or automatic tagging (future, requires AI)
- Removing the `person_id` column from media (remains as primary subject; do not change headshot logic)
- Tagging on video or document items (photos only for this sprint)

## Task Type

- Data model + backend API + UI extension (extends FB-101 edit form)

## Dependencies

- FB-101 should be complete first (the tag picker lives in the metadata edit form)
- The `tagged_person_ids` / `tagged_people` fields may already be partially scaffolded — verify `serialize_media_item` before adding duplicate columns

## Likely Files

- `app/models/media.py` — check for existing `tagged_person_ids` field; add `media_person_tags` relationship if not present
- `app/models/media_person_tag.py` (new) — `MediaPersonTag` association model
- `alembic/versions/XXXX_add_media_person_tags.py` — migration with backfill
- `app/routes/media.py` — add tag endpoints
- `app/services/media_queries.py` — extend `serialize_media_item` with tagged people
- `app/templates/partials/wiki_media_edit_form.html` — add tag picker to metadata edit form (FB-101 partial)
- `app/templates/partials/global_gallery_items.html` — show tagged people on cards
- `app/templates/wiki_person.html` — include tagged-in photos in bio media section
- `locales/en.json` + 4 others

## i18n Keys Required

```
media.tag_people          → "Tag people"
media.tagged_in           → "Also in this photo"
media.add_tag             → "Add person"
media.remove_tag          → "Remove"
```

## Local Validation Commands

```bash
uv run alembic upgrade head
sqlite3 /data/family.db ".schema media_person_tags"

# Verify backfill
sqlite3 /data/family.db "SELECT COUNT(*) FROM media_person_tags;"

uv run pytest tests/test_s45_gallery.py -v
```

## Acceptance Criteria

- [ ] `media_person_tags` table created with `media_id` and `person_id` as composite PK, both with cascade delete.
- [ ] Backfill migration inserts one row per existing media record where `person_id IS NOT NULL`.
- [ ] `GET /api/media/{id}/tags` returns list of `{id, display_name, slug}` for all tagged persons.
- [ ] `POST /api/media/{id}/tags` adds a tag. Calling twice with the same person_id does not error (idempotent).
- [ ] `DELETE /api/media/{id}/tags/{person_id}` removes the tag. 404 if tag does not exist.
- [ ] `serialize_media_item` includes `tagged_people: list[{id, display_name, slug}]`.
- [ ] Gallery metadata edit form (FB-101) includes a tag picker: shows existing tags as removable pills; dropdown to add new person.
- [ ] Gallery cards show tagged people ("Also: [Name], [Name]") below primary person name.
- [ ] Wiki bio media section shows photos where the person is tagged (via `media_person_tags`) in addition to `person_id` photos.
- [ ] Backfill is safe: no existing media attribution is lost; `person_id` on media is unchanged.
- [ ] All 4 i18n keys in all 5 locales; `test_i18n.py` passes.
- [ ] `uv run pytest tests/` passes with no regressions.

## Risk and Verification Notes

- **Existing `tagged_person_ids` field:** `serialize_media_item` already returns `tagged_person_ids` and `tagged_people`. Check whether `MediaPersonTag` table already exists in any form before creating a duplicate. If it does, this packet is a UI-only ticket — do not create a second table.
- **Backfill in migration:** The backfill must run inside the Alembic migration file using `op.execute()` or a connection execute — not in application code. Test with `alembic downgrade -1` + `alembic upgrade head` to verify the backfill is idempotent.
- **Cascade delete:** If a person is deleted, their tags should be removed (cascade). If a media item is deleted, all its tags are removed (cascade). Both FKs need `ondelete="CASCADE"`.
- **Primary person vs tagged persons distinction:** The `person_id` FK on media remains the "primary subject" (used for wiki section, headshot nomination). Tags are additional references. Do not conflate them — the bio media section query should be `WHERE person_id = X OR id IN (SELECT media_id FROM media_person_tags WHERE person_id = X)`.
- **Performance:** The bio media query extended with the tag subquery may be slower. Use a UNION or a single LEFT JOIN rather than two separate queries.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Table created + backfill | sqlite3 after migration | Schema + row count | Table exists; count matches existing person_id rows | Table absent or backfill skipped |
| Add tag | POST /api/media/{id}/tags | GET response | New person in tagged_people | Tag not persisted |
| Idempotent add | POST same person twice | No 409/500 | 200/201 both times | Error on second call |
| Remove tag | DELETE .../tags/{person_id} | GET response | Person removed | Tag remains |
| Tag picker in edit form | Open edit form for image | DOM | Pills for existing tags, add dropdown | No tag UI |
| Bio page cross-reference | Tag person B on person A's photo | Person B's wiki | Photo appears in B's media | Photo absent |
| Cascade on person delete | Delete a tagged person | media_person_tags | No orphan rows | Orphan rows remain |

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Migration up/down both succeed; backfill verified
- [ ] `uv run pytest tests/` passes
- [ ] i18n parity maintained
- [ ] Manually verified: tag two people on one photo → both see it on their bio pages
