# Sprint Closeout - S50 Activation and Migration

Status: Closed

Audit result: PASS

## Scope Completed

- `FB-120`: hosted onboarding activation wizard and resumable milestone tracking.
- `FB-121`: GEDCOM migration review, unsupported-item summary, batch detail, and rollback.
- `FB-122`: invite role/visibility handoff and first-contribution landing.
- `FB-123`: PWA share inbox, attach, and reject flow.

## Outcome

- Hosted archive admins are now redirected into a resumable onboarding flow until they finish or explicitly skip first-run setup.
- Onboarding milestones are derived from real archive activity instead of a separate checklist fiction: add a relative, import GEDCOM, upload first media, and send the first invite.
- GEDCOM import now exposes unsupported items before import, stores a richer post-import summary, offers a dedicated batch detail view, and supports rollback of created records.
- GEDCOM migration endpoints are now restricted to staff roles so invitees cannot bulk-import or roll back family data.
- Invite claim now explains role and visibility more clearly, records an activation audit event, and lands invitees on a role-aware first-steps screen.
- Mobile/PWA share uploads now create reviewable inbox items instead of loose files, and those items can be attached only to manageable profiles or rejected cleanly.
- Duplicate share-inbox attaches now create the correct media record for the chosen target person instead of silently reusing an unrelated existing media row.
- Alembic revision `a6d9f3b1c2e4` adds onboarding progress and media inbox persistence for existing archives.
- Rolled-back GEDCOM batches no longer count toward onboarding completion.

## Structural Evidence

- `uv run pytest tests/test_onboarding.py tests/test_imports.py tests/test_auth.py tests/test_pages.py tests/test_media.py tests/test_migrations.py -q`
- `uv run pytest tests/test_onboarding.py tests/test_imports.py tests/test_auth.py tests/test_pages.py tests/test_access_control.py tests/test_media.py tests/test_migrations.py tests/test_gedcom_parser.py -q`
- `uv run pytest tests/test_imports.py tests/test_onboarding.py tests/test_pages.py tests/test_media.py -q`
- `uv run pytest tests/test_gedcom_parser.py -q`
- `uv run python -m py_compile app/models/onboarding.py app/models/imports.py app/models/media.py app/services/onboarding_service.py app/services/import_service.py app/routes/onboarding.py app/routes/imports.py app/routes/pages.py app/routes/auth_routes.py app/pwa/routes.py app/main.py`
- `make test-ui-playwright`
- `git diff --check`

## Key Deliverables

- `alembic/versions/a6d9f3b1c2e4_add_onboarding_and_media_inbox_tables.py`
- `app/models/onboarding.py`
- `app/services/onboarding_service.py`
- `app/routes/onboarding.py`
- `app/templates/onboarding.html`
- `app/templates/import_batch.html`
- `app/templates/invite_first_steps.html`
- `app/templates/media_inbox.html`

## Notes

- `FB-123` was planned as stretch and landed within the sprint.
- Auditor result is PASS after follow-up fixes for import permissions, onboarding rollback state, media inbox target visibility, and duplicate inbox attach integrity.
- The two untracked `docs/bizanalysis/*` analyst input files remain untouched and are not part of S50 deliverables.
