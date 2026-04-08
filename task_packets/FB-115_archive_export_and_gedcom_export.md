# Task Packet - FB-115 Archive Export and GEDCOM Export

Status: Done

## Objective

Make data ownership operational by adding GEDCOM export and full archive export.

## Why / KPI

The paid privacy/ownership story requires exitability. GEDCOM import exists, but repository search did not find GEDCOM export support.

## Scope

- In scope:
  - GEDCOM export for people, parent-child relationships, partnerships, birth/death/burial dates and places, notes, source detail, and confidence where mappable
  - full archive export with media zip, stories, wiki sections, manifest JSON, and README
  - admin UI export action
  - CLI/operator export path
  - privacy policy for encrypted/sensitive fields in export
- Out of scope:
  - perfect GEDCOM round-trip for every custom field
  - print book export
  - third-party cloud backup integrations

## Likely Files

- `app/services/export_service.py`
- `app/routes/exports.py`
- `app/templates/admin.html`
- `app/importers/gedcom_parser.py`
- `tests/test_export.py`
- `tests/test_gedcom_parser.py`
- `docs/ops/export-and-delete.md`

## Acceptance Criteria

- [x] Admin can download GEDCOM export.
- [x] Admin can download full archive export.
- [x] Export includes media and stories in portable formats.
- [x] Export manifest documents omissions and custom fields.
- [x] Sensitive-field export behavior is explicit and tested.
- [x] Export generation does not expose hidden/private data to unauthorized users.

## Validation Commands

- `uv run pytest tests/test_exports.py tests/test_access_control.py -q`
- `git diff --check`

## Evidence

- `app/services/export_service.py`
- `app/routes/exports.py`
- `app/templates/admin.html`
- `docs/ops/export-and-delete.md`
- `tests/test_exports.py`
- `tests/test_api.py`

## Definition of Done

- [x] "You can leave with your data" is true.
