# Task Packet - FB-115 Archive Export and GEDCOM Export

Status: Proposed

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

- [ ] Admin can download GEDCOM export.
- [ ] Admin can download full archive export.
- [ ] Export includes media and stories in portable formats.
- [ ] Export manifest documents omissions and custom fields.
- [ ] Sensitive-field export behavior is explicit and tested.
- [ ] Export generation does not expose hidden/private data to unauthorized users.

## Validation Commands

- `uv run pytest tests/test_export.py tests/test_gedcom_parser.py tests/test_access_control.py -q`
- `git diff --check`

## Definition of Done

- [ ] "You can leave with your data" is true.
