# Task Packet - FB-098 Occupation Data Model and API

## Objective

Create the `PersonOccupation` model, Alembic migration, and CRUD API for occupation history — capturing each role a person has held as a discrete, queryable record with date ranges (SCD Type 2). Expose `current_occupation` on the tree person payload for use by FB-100.

## Why / KPI

- Occupation is currently unstructured: the `career[]` JSON array on Person stores prose entries that cannot be queried, filtered, or rendered selectively on the tree.
- A discrete, date-ranged model allows the tree to show what someone does/did, the bio to render a clean career timeline, and future features to filter/search by profession.
- SCD Type 2 design preserves history without overwriting: when someone changes jobs, the old role is closed (end_date set), the new one is opened (end_date null). This is the same principle as census and genealogy records.

## Scope

**In scope:**
- `app/models/occupation.py` — new `PersonOccupation` SQLAlchemy model:
  - `id` (UUID PK, `generate_uuid` default)
  - `person_id` (FK → `persons.id`, non-null, cascade delete)
  - `title` (Text, non-null — e.g. "Teacher", "Postal Worker", "Farmer")
  - `employer` (Text, nullable — org or institution name)
  - `start_date` (Text, nullable — ISO date or year string, e.g. "1985" or "1985-06")
  - `end_date` (Text, nullable — **null means currently in this role**)
  - `source` (Text, nullable — `"user:{person_id}"` on create)
  - `created_at`, `updated_at` (TimestampMixin)
  - Index on `person_id`
- Register `PersonOccupation` in `app/models/__init__.py`
- Alembic migration: `person_occupations` table
- API endpoints in a new `app/routes/occupations.py`, mounted at `/api/persons/{person_id}/occupations`:
  - `GET  /api/persons/{person_id}/occupations` — list all roles for person. Current role (end_date IS NULL) first; remaining ordered by start_date DESC. Each entry: `id`, `title`, `employer`, `start_date`, `end_date`. Auth: any authenticated member.
  - `POST /api/persons/{person_id}/occupations` — create a new role. If `end_date` is null (marking as current), automatically set `end_date = today` on any existing role where `end_date IS NULL` before inserting the new row. Auth: any authenticated member.
  - `PUT  /api/persons/{person_id}/occupations/{occ_id}` — update any field. Same auto-close logic applies if `end_date` is set to null on an update. Auth: any authenticated member.
  - `DELETE /api/persons/{person_id}/occupations/{occ_id}` — hard delete. Auth: admin only.
- Expose `current_occupation` on existing person payloads used by the tree:
  - In the `/api/tree` (or equivalent) person serialization, add `current_occupation: str | None` — the `title` of the row where `end_date IS NULL` for that person. Empty string or null if none.
  - This is a read-only computed field; it is NOT added to the person edit form.
- i18n keys in all 5 locales (see i18n section below)
- Source field set to `"user:{current_user.id}"` on create

**Out of scope:**
- UI (FB-099)
- Tree display preference and rendering (FB-100)
- Editing `career[]` JSON array on Person (separate field, coexists — do not touch)
- Occupation search, filtering, or reporting
- Pagination (all roles returned at once; a person will rarely have more than ~10)

## Task Type

- Data model + backend API

## Dependencies

- Requires `Person` model (exists)
- FB-099 and FB-100 both depend on this packet completing first

## Likely Files

- `app/models/occupation.py` (new)
- `app/models/__init__.py` (register PersonOccupation)
- `alembic/versions/XXXX_add_person_occupations_table.py` (new migration)
- `app/routes/occupations.py` (new)
- `app/main.py` (include occupations router)
- `app/routes/tree.py` or equivalent tree serialization file (add `current_occupation` field)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`, `locales/it.json`, `locales/zh.json`

## i18n Keys Required

All keys go in an `"occupation"` namespace block:

```
occupation.section_title      → "Occupation History"
occupation.current_role       → "Current Role"
occupation.add_occupation     → "Add Role"
occupation.edit_occupation    → "Edit Role"
occupation.delete_occupation  → "Remove"
occupation.title_label        → "Job Title"
occupation.employer_label     → "Employer / Organization"
occupation.start_date_label   → "Start"
occupation.end_date_label     → "End"
occupation.currently_in_role  → "Currently in this role"
occupation.save               → "Save"
occupation.cancel             → "Cancel"
occupation.delete_confirm     → "Remove this role?"
occupation.empty              → "No occupation history recorded."
occupation.present            → "Present"
```

## Local Validation Commands

```bash
# Run migration
uv run alembic upgrade head

# Verify table
sqlite3 /data/family.db ".schema person_occupations"

# Run tests
uv run pytest tests/test_occupation.py -v
uv run pytest tests/test_i18n.py -v
```

## Acceptance Criteria

- [ ] `person_occupations` table created by migration with correct columns, FK to persons (cascade delete), and index on `person_id`.
- [ ] `GET /api/persons/{person_id}/occupations` returns a JSON array ordered: current role (end_date IS NULL) first, then by start_date descending. Returns `[]` if none. Requires auth; returns 401 if unauthenticated.
- [ ] `POST /api/persons/{person_id}/occupations` creates a row. If `end_date` is null, closes any existing current role by setting its `end_date` to today's date before inserting. Returns 201 with the created row.
- [ ] `PUT /api/persons/{person_id}/occupations/{occ_id}` updates the row. Same auto-close logic for null end_date. Returns 200 with updated row; 404 if id not found.
- [ ] `DELETE /api/persons/{person_id}/occupations/{occ_id}` removes the row. Admin only; non-admin gets 403. Returns 204.
- [ ] Tree person payload includes `current_occupation: str | None` (title of current role, or null).
- [ ] All 15 i18n keys present in all 5 locales.
- [ ] `uv run pytest tests/test_i18n.py` passes with no new missing-key failures.
- [ ] Migration is idempotent: `alembic downgrade -1` drops the table cleanly; `alembic upgrade head` re-creates it.

## Risk and Verification Notes

- **Auto-close on create:** The SCD Type 2 invariant (at most one current role per person) must be enforced server-side, not relied upon in the UI. When `end_date` is null on POST or PUT, check for existing null-end_date rows and close them before committing. Use today's date (`datetime.date.today().isoformat()`) as the close date.
- **Multiple current roles:** If data somehow has multiple rows with `end_date IS NULL` (e.g. seeded data), the GET endpoint should still return them all — do not silently drop rows. Only the auto-close write path enforces the invariant going forward.
- **`current_occupation` on tree payload:** This requires a JOIN or subquery in the tree person serialization. Prefer a single LEFT JOIN rather than N separate queries. If the tree serializer issues per-person queries today, do not introduce a new one per person for occupation — batch it.
- **`career[]` coexistence:** The existing `career[]` JSON array on `Person` is prose-based career notes. Do not modify it. Both fields can be populated independently. FB-099 will display both on the bio page.
- **Cascade delete:** Use `ondelete="CASCADE"` on the FK so that deleting a `Person` row also removes their occupation records. Verify this in the migration.
- **Source field:** Set `source = f"user:{current_user.id}"` on create. Do not update on edit.

## Evaluation Environment

| Task | Verifier | Oracle | Expected Evidence | Failure Mode |
|---|---|---|---|---|
| Table created | sqlite3 schema | Alembic migration | `person_occupations` with correct columns | Migration skipped, column missing |
| Create role | POST (end_date null) | DB rows | 201 + previous current role closed | Previous role not closed |
| Create role (past) | POST (end_date set) | DB rows | 201 + no other roles touched | Auto-close fires incorrectly on past roles |
| List ordering | GET after 2+ roles | Response JSON | Current role first | Wrong order |
| Delete non-admin | DELETE as member | 403 response | No row deleted | Missing auth check |
| Tree payload | GET /api/tree | JSON person objects | `current_occupation` field present | Field absent or null for persons with roles |
| i18n parity | test_i18n.py | All locale files | Zero missing-key failures | Key absent in one locale |
| Cascade delete | Delete person | person_occupations table | Occupation rows gone | Orphan rows remain |

## Definition of Done

- [ ] Acceptance criteria all satisfied
- [ ] `uv run alembic upgrade head` runs cleanly from a fresh state
- [ ] `uv run alembic downgrade -1` and re-upgrade both succeed
- [ ] `uv run pytest tests/` passes (no regressions)
- [ ] i18n keys in all 5 locales; `test_i18n.py` passes
- [ ] `current_occupation` confirmed in tree API response via test or manual check
