# Task Packet - FB-121 GEDCOM Migration Assistant

Status: Proposed

## Objective

Turn GEDCOM import from a raw upload into a guided migration workflow.

## Why / KPI

Existing genealogy users are a likely early buyer segment. They need confidence that their old tree imported correctly and a clear cleanup path.

## Scope

- In scope:
  - import batch detail page
  - duplicate review and skip/merge decisions
  - post-import checklist: unlinked people, missing dates, unknown names, duplicate candidates, unsupported GEDCOM fields
  - import rollback/quarantine strategy
  - user-facing summary of what was imported and what was omitted
- Out of scope:
  - perfect GEDCOM round-trip
  - automatic source-record matching
  - bulk media import from third-party services

## Likely Files

- `app/models/imports.py`
- `app/routes/imports.py`
- `app/services/import_service.py`
- `app/templates/imports.html`
- `app/static/js/tree.js`
- `tests/test_gedcom_parser.py`
- `tests/test_imports.py`

## Acceptance Criteria

- [ ] User can view import batch details after import.
- [ ] Import summary shows created people, relationships, duplicates, errors, and unsupported items.
- [ ] Cleanup checklist links to relevant profiles/tree filters.
- [ ] Rollback or quarantine plan exists and is implemented for failed imports.
- [ ] Tests cover duplicate and failed-import paths.

## Validation Commands

- `uv run pytest tests/test_gedcom_parser.py tests/test_imports.py -q`
- `git diff --check`

## Definition of Done

- [ ] GEDCOM import feels safe enough for existing genealogy users.
