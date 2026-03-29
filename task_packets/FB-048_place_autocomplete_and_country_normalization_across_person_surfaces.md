# Task Packet - FB-048 Place Autocomplete and Country Normalization Across Person Surfaces

## Objective

Add place lookup/autocomplete and normalized country capture to the person create, full edit, and tree quick-edit flows so members can enter location data naturally without knowing ISO country codes.

## Why / KPI

- The current place-entry UX is manual free text plus raw 2-letter country fields, which is fragile and unfriendly.
- CFLSR improves when family members can add accurate location information during normal editing without leaving the flow or guessing country-code syntax.

Primary KPI:
- improve successful capture of usable place and country data on shared person records.

Secondary KPI:
- reduce malformed or missing country codes that currently weaken filtering and map usefulness.

## Scope

- In scope:
  - add Google-backed place lookup/autocomplete where configured on:
    - `/people/new`
    - `/people/:id/edit`
    - tree sidebar place-edit fields
  - preserve a usable manual-entry fallback when Google config is absent
  - normalize country output into ISO alpha-2 codes or another explicit canonical format if the implementation proves a better contract
  - ensure place selection can populate the relevant place and country fields without forcing users to know internal storage rules
  - validate and sanitize any normalized location values before persistence
- Out of scope:
  - coordinate persistence and map marker changes
  - relation-aware map icons or kinship overlays
  - comprehensive structured-address storage redesign

## Task Type

- member-facing location-entry UX and data-normalization packet

## Dependencies and Ordering Assumptions

- Depends on FB-047 clarifying the Google provider/runtime contract.
- FB-049 will build on the normalized place data produced here.

## Changed Surfaces

- `person_edit`
- `tree_workspace`

## Target Personas

- Primary personas:
  - `family_admin`
  - `contributing_member`
- Safety personas:
  - `mobile_first_relative`
  - `genealogy_researcher`

## Required Scenario IDs

- `update_core_identity_fields`
- `capture_normalized_place_with_autocomplete`
- `save_without_losing_context`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/templates/person_new.html`
  - `app/templates/person_edit.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/routes/persons.py`
  - `app/static/js/main.js`
  - `app/static/js/tree.js`
  - `app/config.py`
  - `app/schemas.py`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/test_pages.py`
  - `tests/test_api.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make location entry natural while preserving a truthful normalized storage contract
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  person create/edit/tree flows should accept natural place entry and persist normalized country data without hidden magic
- Expected evidence:
  create/edit/sidebar screenshots, seeded form interactions, and API assertions on normalized stored values
- Known failure modes / reward hacks:
  - autocomplete suggestions appear but do not actually write normalized data
  - desktop works but the tree sidebar or mobile path becomes unusable
  - manual fallback silently breaks when Google config is absent
  - country validation is cosmetic and bad values still persist
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prioritize truthful normalization and user comprehension over maximum provider-specific metadata capture

## UI Review Requirements

- Structural oracle:
  - CodeMap over `person_edit` and `tree_workspace`
  - confirm shared location-entry logic is not duplicated in a fragile way across the three surfaces
- Browser oracle:
  - seeded assertions proving:
    - a user can select a place and get normalized country output
    - the same flow works in create, full edit, and tree quick-edit contexts
    - manual fallback remains usable when the provider is unavailable
    - mobile remains tappable and unclipped
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough entering a residence naturally
  - `family_admin` desktop walkthrough correcting a birth or burial place in the tree sidebar
  - `mobile_first_relative` mobile walkthrough confirming the control is understandable and reachable
- Required artifacts:
  - CodeMap JSON output
  - screenshots of create/edit/sidebar location flows
  - replay notes showing normalized output after selection
- Expected visual states:
  - no raw ISO-code dependency as the primary user burden
  - location-entry UI explains itself whether Google lookup is present or absent

## Acceptance Criteria

- [ ] Person create, full edit, and tree quick-edit surfaces support place lookup/autocomplete when Google is configured.
- [ ] Manual place entry remains usable and truthful when Google lookup is not configured.
- [ ] Country data is normalized into the app’s canonical storage format instead of relying on user-guessed 2-letter codes.
- [ ] The normalized location flow is usable on desktop and mobile without clipping or hidden controls.
- [ ] New member-facing copy remains localized across `en`, `es`, and `ru`.

## Risk and Verification Notes

- Complexity hotspots:
  - keeping three editing surfaces behaviorally aligned
  - preserving tree quick-edit momentum while adding lookup UI
  - fallback behavior when provider state changes
- Likely shallow-pass failure modes:
  - only one surface gets the real normalization logic
  - autocomplete is present but persistence remains manual or inconsistent
  - mobile interaction degrades because the widget is desktop-first
- Required verification depth:
  - deterministic create/edit/tree assertions plus API proof of normalized persistence
- Sufficient discriminative power means:
  review should fail if a member still has to know ISO country codes or if normalized values differ across surfaces.

## Execution Budget

- Builder may explore:
  - shared client-side place helpers
  - lightweight hidden-field or normalization strategies that preserve current schemas when possible
- Builder must escalate if:
  - the normalized location contract requires a schema change broader than the person/location work already planned
- Material scope drift:
  - coordinate persistence
  - kinship-aware map rendering
- Proof obligations before review:
  - all three editing surfaces demonstrate the same normalized location behavior with graceful fallback

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 location-entry or normalization regressions remain on create/edit/tree surfaces
- [ ] Members can enter useful place data without having to think like database administrators
