# Task Packet - FB-055 Structured Addresses and Places Auto-Population

## Objective

Enhance the AddressEntry schema with structured subfields (line1, line2, city, state, postal_code, country, place_id, is_partial) and extend the Google Places integration to auto-populate structured address components from autocomplete selection.

## Why / KPI

- The current address storage is a single `place` string plus country code and coordinates. The separate Map feature and future address-based views need structured data.
- CFLSR improves when a contributor types an address and gets structured, map-ready data without manual field-by-field entry.

Primary KPI:
- upgrade address capture from freeform place strings to structured components with Places auto-population.

Secondary KPI:
- improve Map marker accuracy by storing place_id and complete structured addresses.

## Scope

- In scope:
  - enhance `AddressEntry` Pydantic model: add `line1`, `line2`, `city`, `state`, `postal_code`, `country`, `place_id`, `is_primary`, `is_partial` fields
  - update address card UI to show structured subfields
  - when Places autocomplete fires on `line1`, auto-populate: city, state, postal_code, country, country_code, place_id, latitude, longitude
  - extend `location_fields.js` with a structured address extraction callback (`onPlaceSelected`) that parses all address components
  - graceful fallback: if Places unavailable, all subfields are plain text inputs
  - `is_partial` flag: auto-set to `true` when coordinates are missing; display a subtle "incomplete address" indicator
  - migration of existing address entries: preserve `place` field, set `is_partial=true` for entries without structured fields
  - primary-flag enforcement on addresses (same pattern as phones/emails)
- Out of scope:
  - changes to birth_place / residence_place / burial_place single-field locations (those remain as-is)
  - Map page rendering changes
  - server-side geocoding

## Task Type

- member-facing location-entry UX and data-model enhancement

## Dependencies and Ordering Assumptions

- Depends on FB-053 (data model patterns established).
- Independent of FB-054 (can be built in parallel after FB-053).

## Changed Surfaces

- `person_edit` (address cards section)

## Target Personas

- Primary: `contributing_member`, `genealogy_researcher`
- Safety: `mobile_first_relative`

## Required Scenario IDs

- `add_structured_address_with_autocomplete`
- `add_address_manually_without_places`
- `edit_partial_address`
- `save_without_losing_context`

## Required Viewports and Locales

- Viewports: `desktop`, `mobile`
- Locales: `en`, `es`, `ru`

## Likely Files

- `app/schemas.py` (AddressEntry enhancement)
- `app/static/js/location_fields.js` (structured extraction callback)
- `app/templates/person_edit.html` (address card template)
- `app/routes/persons.py` (address handling)
- `locales/en.json`, `locales/es.json`, `locales/ru.json`
- `tests/test_schema_models.py`
- `tests/test_api.py`
- `tests/test_i18n.py`

## Validation Commands

- `uv run pytest tests/test_schema_models.py tests/test_api.py tests/test_i18n.py -q`
- `uv run python -m compileall app tests`

## Evaluation Environment

- Task:
  structured address capture with Places auto-population and graceful fallback
- Verifier:
  schema validation tests, API round-trip with structured addresses, structural review of Places extraction
- Reference/oracle:
  existing `location_fields.js` Places integration as the baseline; enhanced to extract all address components
- Expected evidence:
  test output for AddressEntry validation, API round-trip with structured fields, fallback behavior when Places is unavailable
- Known failure modes / reward hacks:
  - Places selection fills line1 but leaves city/state/zip empty
  - structured fields accepted but is_partial flag not computed
  - fallback mode hides subfields instead of making them editable
  - existing addresses lost during schema migration
- Verifiability class:
  `bounded-judgment`
- Context policy:
  extend existing location_fields.js rather than rewriting; preserve backward compatibility for existing address data

## UI Review Requirements

- Structural oracle:
  - confirm structured address fields are present in address card template
  - confirm Places callback extracts all components
- Browser oracle:
  - address autocomplete fills structured fields on selection
  - manual entry works for all subfields when Places is unavailable
  - is_partial indicator appears when coordinates are missing
- Visual/persona oracle:
  - `genealogy_researcher` can enter a historical address without exact data and see partial flag
  - `contributing_member` can enter a current address via autocomplete with full auto-population
- Required artifacts:
  - test output
  - code review of location_fields.js extraction logic

## Acceptance Criteria

- [ ] `AddressEntry` schema includes: line1, line2, city, state, postal_code, country, place_id, is_primary, is_partial alongside existing fields.
- [ ] Address card UI shows structured subfields (line1, line2, city, state, zip, country).
- [ ] Google Places autocomplete on line1 auto-populates city, state, postal_code, country, country_code, place_id, lat, lng.
- [ ] When Places is unavailable, all address subfields are plain text inputs with no broken UI.
- [ ] `is_partial` flag is auto-computed when coordinates are missing.
- [ ] Existing address entries are preserved with `is_partial=true` when they lack structured fields.
- [ ] Primary-flag enforcement works on addresses.
- [ ] i18n keys exist for all new address labels in en, es, ru.
- [ ] Tests cover structured AddressEntry validation and API round-trip.

## Risk and Verification Notes

- Complexity hotspots:
  - Places API response parsing varies by country/address type (some responses lack postal code, etc.)
  - backward compatibility with existing addresses that only have `place` field
- Likely shallow-pass failure modes:
  - autocomplete fires but extraction only gets country code (ignoring other components)
  - structured fields save but don't reload correctly from existing data
- Required verification depth:
  - schema tests + API round-trip + code review of extraction
- Sufficient discriminative power means:
  tests should fail if Places extraction misses structured components or if existing addresses are corrupted.

## Execution Budget

- Builder may explore:
  - which Google Places address_component types map to which structured fields
  - how to handle addresses in countries with different postal/state conventions
- Builder must escalate if:
  - Places API address component format has changed from what location_fields.js currently expects
- Material scope drift:
  - Map page rendering changes
  - server-side geocoding
- Proof obligations before review:
  - structured extraction demonstrated
  - fallback mode proven usable
  - existing address data preserved

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] Existing address data round-trips correctly
- [ ] No P0/P1 regressions in person edit or location fields
