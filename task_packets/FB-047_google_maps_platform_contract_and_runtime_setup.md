# Task Packet - FB-047 Google Maps Platform Contract and Railway Runtime Setup

## Objective

Establish a truthful Google Maps Platform runtime contract for Family Book so `/map` and future place lookup features use one clear provider configuration on Railway and in the product code.

## Why / KPI

- The codebase already supports `GOOGLE_MAPS_API_KEY`, but the runtime contract is not visible enough and the product is at risk of drifting into confusing multi-key or half-configured behavior.
- CFLSR suffers when a map feature appears present in code but fails in production because deployment configuration is missing or ambiguous.

Primary KPI:
- improve deploy-time reliability and truthfulness of Google-backed map capabilities.

Secondary KPI:
- reduce operator confusion about which Google env vars are required for map display vs. place lookup.

## Scope

- In scope:
  - confirm and document `GOOGLE_MAPS_API_KEY` as the canonical Google provider env var for map display and Places-style client lookup
  - support optional `GOOGLE_MAPS_MAP_ID` throughout the runtime contract for styled maps
  - make `/map` provider state and fallback behavior truthful when Google config is absent, partial, or invalid
  - add any missing tests or admin/operator-facing diagnostics needed to verify the configured provider contract
  - ensure deployment docs and product copy do not imply a separate `GOOGLE_PLACES_API_KEY` unless it is truly required
- Out of scope:
  - Places autocomplete UX itself
  - geocoding persistence or coordinate storage
  - kinship-aware marker semantics
  - broad admin settings UI for every third-party integration

## Task Type

- runtime contract and member-facing map truthfulness packet

## Dependencies and Ordering Assumptions

- This is the first packet in the map/location sprint.
- Later packets assume the Google runtime contract is stable and deployable on Railway without ambiguous env naming.

## Changed Surfaces

- `map_view`

## Target Personas

- Primary personas:
  - `contributing_member`
- Safety personas:
  - `genealogy_researcher`
  - `mobile_first_relative`

## Required Scenario IDs

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
  - `app/config.py`
  - `app/routes/pages.py`
  - `app/templates/map.html`
  - `app/static/js/map.js`
  - `tests/test_pages.py`
  - `tests/test_config.py`
  - `tests/ui/playwright-flow-checks.sh`
  - deployment/runtime docs if present
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_config.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  establish a truthful deploy/runtime contract for Google-backed map features
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  the existing `GOOGLE_MAPS_API_KEY` / `GOOGLE_MAPS_MAP_ID` config contract
  the product decision that one Google provider contract should cover map display and place lookup
- Expected evidence:
  CodeMap output, provider-state screenshots, and deterministic checks proving fallback and configured paths behave truthfully
- Known failure modes / reward hacks:
  - code mentions `GOOGLE_MAPS_MAP_ID` but the runtime never emits it to the page
  - UI implies Google-backed map behavior when only the centroid fallback is active
  - deployment docs drift toward a fake `GOOGLE_PLACES_API_KEY` requirement
  - provider state is technically present in DOM but not understandable to the user or operator
- Verifiability class:
  `bounded-judgment`
- Context policy:
  preserve one canonical Google provider contract and do not imply capabilities the runtime cannot actually perform

## UI Review Requirements

- Structural oracle:
  - CodeMap over `map_view`
  - config/template/script review proving the runtime contract is consistent end-to-end
- Browser oracle:
  - assertions proving:
    - `/map` renders a truthful fallback when Google config is absent
    - `/map` emits Google provider data attributes when config is present
    - desktop and mobile keep the map/filter surface usable in both states
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough seeing either a Google map or a clearly labeled fallback
  - `mobile_first_relative` mobile walkthrough confirming the provider state does not hide the primary map workflow
- Required artifacts:
  - CodeMap JSON output
  - fallback and configured-provider screenshots
  - replay notes describing the runtime contract and fallback behavior
- Expected visual states:
  - no misleading “Google map” presentation when the feature is not configured
  - optional styled-map support is visible only when configured

## Acceptance Criteria

- [ ] `GOOGLE_MAPS_API_KEY` is the documented and implemented canonical env var for Google-backed map capabilities.
- [ ] `GOOGLE_MAPS_MAP_ID` is supported as an optional enhancement without becoming a required launch dependency.
- [ ] `/map` truthfully distinguishes configured Google behavior from fallback behavior.
- [ ] No product surface or runtime doc implies a separate `GOOGLE_PLACES_API_KEY` unless the implementation truly requires one.
- [ ] Desktop and mobile continue to present a usable map/filter experience regardless of provider state.

## Risk and Verification Notes

- Complexity hotspots:
  - keeping product truth and deploy/runtime docs aligned
  - avoiding a split-brain provider contract between current map rendering and future place lookup
- Likely shallow-pass failure modes:
  - config exists in tests but production-facing docs remain ambiguous
  - fallback/provider labels are technically rendered but not understandable
  - map behavior regresses on mobile while desktop looks fine
- Required verification depth:
  - deterministic configured-vs-fallback checks plus visual evidence on both breakpoints
- Sufficient discriminative power means:
  review should fail if an operator still cannot tell which env vars to set or if a member cannot tell whether the live map is running in fallback mode.

## Execution Budget

- Builder may explore:
  - lightweight provider-status UX
  - runtime diagnostics that stay truthful and non-technical for members
- Builder must escalate if:
  - Google provider setup requires additional secrets or server-side credentials not reflected in the current product contract
- Material scope drift:
  - Places autocomplete or geocoding implementation
  - map-marker semantics beyond provider-state truthfulness
- Proof obligations before review:
  - fallback and configured provider paths are both demonstrated with durable evidence

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 provider-contract or deploy-truth regressions remain
- [ ] Google-backed map behavior is deployable and truthful before location-intelligence work builds on top of it
