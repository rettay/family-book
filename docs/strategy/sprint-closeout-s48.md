# Sprint Closeout - S48 Privacy and Exit Trust

Status: Closed

Audit result: PASS

## Scope Completed

- `FB-113`: role and graph-distance privacy model.
- `FB-114`: sensitive-field defaults, living-minor restrictions, and privacy audit events.
- `FB-115`: GEDCOM export and full archive export.
- `FB-116`: public trust page plus trust/export documentation alignment.

## Outcome

- Family Book now enforces `owner/admin/steward/member/viewer` behavior in the application permission model instead of broad visible-person access for every active member.
- Members can no longer edit every visible profile, and hidden profiles now remain restricted to owner/admin even if a member originally created them.
- Contact visibility and sensitive-field visibility are explicit per-profile policies, with staff-only defaults for medical/genetic data and staff-only contact access for living minors.
- Privacy-setting changes now create dedicated audit log entries.
- Admins can download GEDCOM and full archive exports, and the archive export includes manifest, JSON, stories, media metadata, original files where present, and an embedded GEDCOM file.
- Export downloads are now ephemeral: the server-side artifact is deleted before the response returns instead of being retained under `DATA_DIR`.
- Existing archives now have a real migration path for the new `persons.role`, `persons.contact_visibility`, and `persons.sensitive_visibility` columns.
- Relationship-path lookups now respect the same person-visibility rules as the rest of the app and reject hidden/inaccessible endpoints.
- Public trust copy now distinguishes authenticated transport/media/backups from zero-knowledge or end-to-end encryption claims.

## Structural Evidence

- `uv run pytest tests/test_access_control.py tests/test_api.py tests/test_exports.py tests/test_pages.py tests/test_schema_models.py -q`
- `uv run pytest tests/test_auth.py tests/test_media.py tests/test_calendar_and_relationships.py tests/test_physical_genetic.py tests/test_medical_conditions.py -q`
- `uv run pytest tests/test_migrations.py tests/test_api.py tests/test_calendar_and_relationships.py tests/test_exports.py tests/test_media.py -q`
- `uv run python -m py_compile app/access_control.py app/models/person.py app/roles.py app/routes/exports.py app/services/export_service.py app/routes/persons.py app/routes/pages.py app/routes/wiki.py app/services/media_queries.py app/routes/auth_routes.py app/schemas.py`
- `git diff --check`

## Documentation Deliverables

- `docs/ops/trust-center.md`
- `docs/ops/export-and-delete.md`
- `README.md`
- `app/templates/trust.html`

## Notes

- This sprint intentionally kept the first hosted privacy model in the current single-archive shape instead of attempting pooled multi-tenant privacy controls.
- Alembic revision `c4f8e2a1b6d9` backfills S48 privacy columns for pre-existing archives.
- The two untracked `docs/bizanalysis/*` analyst input files remain untouched and are not part of S48 deliverables.
