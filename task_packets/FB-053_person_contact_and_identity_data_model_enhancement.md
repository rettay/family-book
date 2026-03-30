# Task Packet - FB-053 Person Contact and Identity Data Model Enhancement

## Objective

Add multi-value contact fields (phones, emails, social accounts), name history tracking, and obituary URL to the Person data model with Pydantic sub-models, a safe migration, and API handling.

## Why / KPI

- The current single-field contact storage (one phone, one email, six hardcoded social columns) blocks family members from recording complete contact information for relatives.
- CFLSR improves when a contributor can record all known phone numbers, emails, and social accounts for a person and have another member see that data correctly.

Primary KPI:
- enable multi-value contact and social capture without data loss on existing records.

Secondary KPI:
- consolidate six individual social columns into a single extensible array, reducing schema fragility.

## Scope

- In scope:
  - new Pydantic sub-models: `PhoneEntry`, `EmailEntry`, `SocialAccountEntry`, `NameHistoryEntry`
  - new Person columns: `_contact_phones` (EncryptedText JSON array), `_contact_emails` (EncryptedText JSON array), `_social_accounts` (Text JSON array), `_name_history` (EncryptedText JSON array), `obituary_url` (String)
  - Python properties with JSON serialization matching existing `_contact_addresses` pattern
  - Alembic migration that adds new columns with safe defaults
  - Data migration: consolidate existing `contact_phone` → `_contact_phones`, `contact_email` → `_contact_emails`, `social_*` → `_social_accounts`
  - update `PersonCreate`, `PersonUpdate`, `PersonDetail` schemas to include new array fields
  - update `person_to_detail()` to expose new fields
  - update PUT `/api/persons/{id}` to handle new array fields with the existing `_strip_none_entries` pattern
  - primary-flag enforcement: at-most-one `is_primary=True` per phone/email array via Pydantic validator
  - DOD-after-DOB validation in the PUT handler
  - update revision snapshot protected fields lists for new encrypted arrays
  - tests for new sub-models, migration, API round-trip
- Out of scope:
  - frontend/template changes (FB-054, FB-055)
  - address schema enhancement (FB-055)
  - languages controlled vocabulary (FB-056)
  - removal of deprecated `contact_phone`, `contact_email`, `social_*` columns (future cleanup)

## Task Type

- backend data-model and API enhancement

## Dependencies and Ordering Assumptions

- No blocking dependencies. S31 work is on relationship models, not person contact fields.
- FB-054 and FB-055 depend on this packet.

## Likely Files

- `app/models/person.py`
- `app/schemas.py`
- `app/routes/persons.py`
- `app/services/revision_service.py` (protected fields lists)
- `alembic/versions/` (new migration)
- `tests/test_schema_models.py`
- `tests/test_api.py`

## Validation Commands

- `uv run python -m compileall app tests`
- `uv run pytest tests/test_schema_models.py tests/test_api.py -q`
- `uv run alembic upgrade head`

## Evaluation Environment

- Task:
  add multi-value contact and identity fields to the Person model with safe migration and API support
- Verifier:
  pytest assertions on sub-model validation, API round-trip, migration idempotency
- Reference/oracle:
  existing `_contact_addresses` pattern for JSON array fields on Person
- Expected evidence:
  test output showing sub-model validation, API create/update/read with new fields, migration success
- Known failure modes / reward hacks:
  - migration runs but does not consolidate existing single-field data
  - new fields accepted by API but not persisted or returned
  - primary-flag enforcement silently drops entries instead of adjusting flags
  - encrypted fields not added to revision snapshot protected lists
- Verifiability class:
  `deterministic`
- Context policy:
  stay within the data model and API layer; do not touch templates or frontend JS

## Acceptance Criteria

- [ ] `PhoneEntry`, `EmailEntry`, `SocialAccountEntry`, `NameHistoryEntry` Pydantic sub-models exist with field validation.
- [ ] Person model has new columns with JSON array properties following the existing `_contact_addresses` pattern.
- [ ] Alembic migration adds columns and consolidates existing `contact_phone`, `contact_email`, and `social_*` data into the new arrays.
- [ ] `PersonUpdate` and `PersonDetail` schemas include the new array fields.
- [ ] PUT `/api/persons/{id}` handles new arrays with `_strip_none_entries` and primary-flag enforcement.
- [ ] DOD-after-DOB validation returns 422 when violated.
- [ ] New encrypted arrays are included in revision snapshot protected field lists.
- [ ] Existing person records survive migration without data loss.
- [ ] Tests cover sub-model validation (valid + invalid), API round-trip, and primary-flag enforcement.

## Risk and Verification Notes

- Complexity hotspots:
  - data migration of encrypted fields (existing `contact_phone`/`contact_email` are EncryptedText)
  - primary-flag enforcement edge cases (empty array, all false, multiple true)
- Likely shallow-pass failure modes:
  - migration adds columns but skips data consolidation
  - sub-models validate but API handler ignores them
- Required verification depth:
  - deterministic pytest with positive and negative cases
- Sufficient discriminative power means:
  tests should fail if primary-flag enforcement is absent or if migration does not consolidate existing data.

## Execution Budget

- Builder may explore:
  - whether to consolidate data in the migration or in a separate data-migration script
  - how to handle encrypted field decryption/re-encryption during consolidation
- Builder must escalate if:
  - existing encrypted contact data cannot be safely re-encrypted into new array format
- Material scope drift:
  - any template or frontend JS changes
  - address schema changes
- Proof obligations before review:
  - all new sub-models tested
  - API round-trip proven
  - migration tested on a fresh DB and on a DB with existing person data

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] All tests pass
- [ ] Migration is reversible (downgrade does not lose data in original columns since they are preserved)
- [ ] No P0/P1 regressions in existing person API behavior
