# Task Packet - FB-004 Rich Person Record and Tagged Family Content Foundation

## Objective

Expand the person and content model so Family Book can represent the richer family-history data the product requires: stories, tagged media, contact data, medical data, burial details, and multi-person content references.

## Why / KPI

- CFLSR is not enough if the shared system cannot hold the content the family actually wants to store.
- The launch contract is richer than the current person/card model.
- Tagged, multi-person content is central to a usable family archive.

## Scope

- In scope:
  - person schema changes needed for launch content
  - tagged media or content references to one or more people
  - story/note content foundation
  - burial-detail fields and tombstone media support
  - medical/contact field handling consistent with launch contract
  - tests for new model behaviors
- Out of scope:
  - external social/news ingestion
  - full moderation or version-history system
  - map rendering and tree preference UI

## Constraints

- Keep schema changes auditable and migration-friendly.
- Do not introduce launch-only product claims without persisted state.
- Preserve authenticated media access.

## Implementation Notes

- Likely files:
  - `app/models/person.py`
  - `app/models/media.py`
  - `app/models/moments.py`
  - `app/schemas.py`
  - `app/routes/persons.py`
  - `app/routes/media.py`
  - `app/routes/moments.py`
  - Alembic migration files
  - `tests/test_models.py`
  - `tests/test_media.py`
  - `tests/test_moments.py`
- Validation commands:
  - `uv run pytest tests/test_models.py tests/test_media.py tests/test_moments.py -q`
  - migration smoke plus targeted CRUD checks

## Evaluation Environment

- Task: data-model expansion for person/content richness
- Verifier: migration plus CRUD and serialization tests
- Reference/oracle: `foundation/V1_PRODUCT_REQUIREMENTS.md`
- Expected evidence: persisted fields and content relationships exist and round-trip correctly through APIs
- Known failure modes / reward hacks:
  - docs promise fields that are not persisted
  - single-person media works but tagged multi-person references are absent
  - burial or medical fields exist in templates but not in schema/contracts
- Verifiability class: `deterministic`

## Acceptance Criteria

- [ ] Person records can persist the launch-critical fields missing today, including medical/contact/burial/location data needed by the contract.
- [ ] The system supports content or media associated with one or more people.
- [ ] Stories or notes have a persisted model and API path rather than template-only placeholders.
- [ ] Automated tests cover schema round-trips and API behavior for the new launch-critical fields.
- [ ] Migration and model changes remain compatible with existing authenticated media behavior.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Migration and validation commands reproducible and passing
- [ ] Product-critical content types are represented in persisted state

## Risk and Verification Notes

- Complexity hotspots:
  - schema migration shape
  - content tagging design
  - compatibility with current templates/routes
- Shallow-pass risk:
  - adding fields without full API or serialization support
- Required verification depth:
  - model, API, and migration evidence
