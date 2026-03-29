# Task Packet - FB-049 Coordinate Persistence and Truthful Map Marker Placement

## Objective

Persist normalized coordinates for supported person location fields and use them on `/map` so the product can place markers truthfully instead of falling back to country centroids whenever better data exists.

## Why / KPI

- The current map plots `residence` and `burial` using country centroids, which is only a coarse fallback and undermines trust once members start entering real places.
- CFLSR improves when contributed location data visibly pays off in a more accurate family map.

Primary KPI:
- improve truthful geographic rendering of family locations on `/map`.

Secondary KPI:
- increase the product value of location entry by making saved places materially improve the map.

## Scope

- In scope:
  - define how normalized coordinates are stored for residence and burial markers, and any other place types explicitly chosen for launch scope
  - persist coordinates derived from confirmed place selection or geocoding
  - update map marker generation to prefer persisted coordinates and fall back explicitly when unavailable
  - preserve truthful labels/source distinctions so the UI does not imply exact precision when only fallback data exists
  - update tests and browser checks so wrong-location regressions are caught
- Out of scope:
  - full historical migration for every legacy place string unless explicitly scoped
  - kinship-aware iconography
  - fully structured address book redesign

## Task Type

- member-facing map correctness and data-model packet

## Dependencies and Ordering Assumptions

- Depends on FB-047 for provider/runtime truth.
- Depends on FB-048 for normalized place-entry inputs.
- FB-050 will build on the truthful marker data produced here.

## Changed Surfaces

- `map_view`
- `person_edit`

## Target Personas

- Primary personas:
  - `contributing_member`
- Safety personas:
  - `genealogy_researcher`
  - `mobile_first_relative`
  - `family_admin`

## Required Scenario IDs

- `capture_normalized_place_with_autocomplete`
- `view_people_or_burials_on_map`
- `understand_empty_state_and_filters`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/models/person.py`
  - `alembic/versions/*`
  - `app/schemas.py`
  - `app/routes/persons.py`
  - `app/routes/tree.py`
  - `app/services/geo.py`
  - `app/templates/map.html`
  - `app/static/js/map.js`
  - `tests/test_api.py`
  - `tests/test_models.py`
  - `tests/test_pages.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_models.py tests/test_api.py tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run alembic upgrade head`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  upgrade the map from coarse fallback geography to truthful coordinate-backed marker placement
- Verifier:
  structural review, deterministic browser checks, model/API assertions, and visual/persona review
- Reference/oracle:
  if coordinates exist for a saved location, `/map` should use them instead of country centroids
- Expected evidence:
  schema/migration proof, API assertions, and screenshots showing real marker movement when coordinates are present
- Known failure modes / reward hacks:
  - coordinates are stored but `/api/map` still serves country-centroid markers
  - exact-looking markers are shown without a trustworthy coordinate source
  - migration introduces null/legacy breakage on existing person records
  - map labels stay ambiguous about residence vs burial precision
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prefer truthful precision and explicit fallback over fake exactness

## UI Review Requirements

- Structural oracle:
  - CodeMap over `map_view` plus the person/location model changes
  - confirm migration, schema, route, and client wiring are complete
- Browser oracle:
  - seeded assertions proving:
    - map markers use persisted coordinates when available
    - fallback remains functional when coordinates are absent
    - residence and burial markers remain distinguishable
    - mobile still fits and remains navigable
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough seeing a real saved place reflected on the map
  - `genealogy_researcher` walkthrough confirming the map no longer implies false precision
- Required artifacts:
  - CodeMap JSON output
  - migration evidence
  - desktop/mobile map screenshots with real-coordinate markers
  - replay notes covering one fallback marker and one coordinate-backed marker
- Expected visual states:
  - markers reflect actual saved coordinates when present
  - fallback behavior is understandable rather than disguised as exact mapping

## Acceptance Criteria

- [ ] Supported person locations can persist coordinates in the app’s canonical model.
- [ ] `/api/map` and `/map` prefer persisted coordinates over country-centroid fallback when available.
- [ ] Fallback behavior remains explicit and truthful when exact coordinates are unavailable.
- [ ] Residence and burial markers remain distinguishable and understandable on desktop and mobile.
- [ ] The migration and persistence path are verified against existing SQLite deploy expectations.

## Risk and Verification Notes

- Complexity hotspots:
  - schema evolution and migration safety
  - choosing a launch-scope coordinate model that does not overfit one provider
  - avoiding false precision in UI language and marker behavior
- Likely shallow-pass failure modes:
  - coordinate fields exist but are not consumed by the map
  - existing records silently regress because only new records carry coordinates
  - mobile marker rendering becomes unreadable while desktop passes
- Required verification depth:
  - migration/model/API/browser evidence plus at least one adversarial fallback case
- Sufficient discriminative power means:
  review should fail if `/map` still renders centroid-level geography for records that have stored coordinates.

## Execution Budget

- Builder may explore:
  - provider-neutral coordinate fields
  - clear fallback marker labeling
  - lightweight backfill for seed/demo data if needed for deterministic tests
- Builder must escalate if:
  - the chosen location model requires a broader address schema redesign
- Material scope drift:
  - kinship-aware marker layering
  - full historical geocoding sweep for legacy data
- Proof obligations before review:
  - at least one coordinate-backed marker and one fallback marker are both demonstrated with durable evidence

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 map-truth regressions remain in coordinate-backed rendering
- [ ] `/map` becomes a truthful reflection of saved location data instead of a country-only approximation
