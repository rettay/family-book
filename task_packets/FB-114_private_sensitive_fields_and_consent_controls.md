# Task Packet - FB-114 Private Sensitive Fields and Consent Controls

Status: Done

## Objective

Make sensitive data defaults and disclosure controls explicit for contacts, medical/genetic fields, minors, private media, and living people.

## Why / KPI

The app stores unusually sensitive living-family data. Users need safe defaults and clear expectations before inviting relatives.

## Scope

- In scope:
  - default visibility for contact, address, medical, genetic, minor, and private media fields
  - profile UI badges/explanations for restricted fields
  - invite copy explaining what an invitee can see and do
  - admin/steward controls for sensitive-field visibility
  - audit events for sensitive visibility changes
- Out of scope:
  - legal consent signatures
  - client-side encryption
  - HIPAA/medical compliance positioning

## Likely Files

- `app/models/person.py`
- `app/models/media.py`
- `app/access_control.py`
- `app/routes/persons.py`
- `app/routes/media.py`
- `app/templates/person_edit.html`
- `app/templates/partials/person_sidebar.html`
- `app/templates/invite.html`
- `tests/test_access_control.py`
- `tests/test_media.py`
- `tests/test_pages.py`

## Acceptance Criteria

- [x] Sensitive fields have documented defaults and UI copy.
- [x] Users cannot accidentally expose medical/genetic/contact data to all members.
- [x] Minor-related media/profile defaults are conservative.
- [x] Visibility changes create audit records.
- [x] Tests prove redaction in API and HTML paths.

## Validation Commands

- `uv run pytest tests/test_access_control.py tests/test_media.py tests/test_pages.py -q`
- `git diff --check`

## Evidence

- `app/models/person.py`
- `app/access_control.py`
- `app/routes/persons.py`
- `alembic/versions/c4f8e2a1b6d9_add_person_privacy_role_columns.py`
- `app/templates/invite.html`
- `app/templates/trust.html`
- `tests/test_access_control.py`
- `tests/test_migrations.py`
- `tests/test_media.py`
- `tests/test_pages.py`

## Definition of Done

- [x] Sensitive data handling is safe enough for paid beta.
