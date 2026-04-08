# Task Packet - FB-113 Role and Graph-Distance Privacy Model

Status: Done

## Objective

Replace broad non-admin visibility/editing with a product-grade permission model that matches the privacy promise.

## Why / KPI

Current access control allows active non-admin users to view full profile/contact details for visible people and manage any visible active person. That conflicts with the README's graph-distance privacy promise and is a launch blocker for a paid privacy-first app.

## Scope

- In scope:
  - decide roles: owner/admin/steward/member/viewer or equivalent
  - implement graph-distance view rules if retained in product copy
  - restrict profile/contact/medical/genetic/minor data by policy
  - restrict edit/manage rights by role and relationship scope
  - update tree, wiki, media, research, relationship, and person routes
  - update UI copy to explain permissions
- Out of scope:
  - full legal consent workflow
  - external identity provider redesign
  - tenant provisioning

## Likely Files

- `app/access_control.py`
- `app/models/person.py`
- `app/routes/persons.py`
- `app/routes/relationships.py`
- `app/routes/wiki.py`
- `app/routes/media.py`
- `app/routes/tree.py`
- `app/templates/admin.html`
- `tests/test_access_control.py`
- `tests/test_api.py`
- `tests/test_media.py`
- `tests/test_pages.py`

## Acceptance Criteria

- [x] Non-admin active members cannot edit every visible active person.
- [x] Contact fields are visible only according to explicit policy.
- [x] Medical/genetic fields are hidden unless policy permits.
- [x] Graph-distance behavior is either implemented and tested or removed from product copy.
- [x] Admin/steward/member/viewer behavior is covered by tests.
- [x] Existing invite/admin flows continue to work.

## Validation Commands

- `uv run pytest tests/test_access_control.py tests/test_api.py tests/test_media.py tests/test_pages.py -q`
- `git diff --check`

## Evidence

- `app/models/person.py`
- `app/roles.py`
- `app/access_control.py`
- `app/routes/relationships.py`
- `app/services/relationship_calculator.py`
- `tests/test_access_control.py`
- `tests/test_api.py`
- `tests/test_calendar_and_relationships.py`
- `tests/test_media.py`
- `tests/test_pages.py`

## Definition of Done

- [x] Privacy promise and enforcement match.
