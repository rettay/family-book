# Map UI Audit Evidence - S30 Map Truthfulness and Place Intelligence

Surface under review: `map_view`

Sprint scope under audit:
- `FB-047` Google Maps platform contract and Railway runtime setup
- `FB-048` place autocomplete and country normalization across person surfaces
- `FB-049` coordinate persistence and truthful map marker placement
- `FB-050` kinship-aware map semantics and family distribution readability

Resolved from canonical sources:
- Persona registry: `/Users/cheech/code/family-book/docs/ops/persona_registry.yaml`
- UI surface matrix: `/Users/cheech/code/family-book/docs/ops/ui_surface_matrix.yaml`

Resolved personas:
- `contributing_member`
- `genealogy_researcher`
- `mobile_first_relative`

Resolved scenarios:
- `view_people_or_burials_on_map`
- `interpret_family_distribution_on_map`
- `understand_empty_state_and_filters`

Resolved viewports/locales:
- `desktop`, `mobile`
- `en`, `es`

## Structural Lane

Artifacts:
- CodeMap JSON: `/Users/cheech/code/family-book/output/audit/map-ui-codemap.json`

Changed files on `map_view`:
- `/Users/cheech/code/family-book/app/templates/map.html`
- `/Users/cheech/code/family-book/app/routes/pages.py`
- `/Users/cheech/code/family-book/app/routes/tree.py`
- `/Users/cheech/code/family-book/app/static/js/map.js`

Supporting data-entry and normalization files exercised by the sprint:
- `/Users/cheech/code/family-book/app/routes/persons.py`
- `/Users/cheech/code/family-book/app/services/location_service.py`
- `/Users/cheech/code/family-book/app/static/js/location_fields.js`

Result:
- `/map` now declares a truthful provider contract and fails closed when Google keys are placeholders or absent.
- Marker placement prefers persisted coordinates, then bounded place lookup, then country centroid fallback, with `location_source` exposed to the UI.
- The map surface distinguishes residence vs burial markers and relationship-distance scopes from the logged-in person.
- Person create/edit/tree-place entry surfaces now feed normalized country codes and coordinate fields into the backend contract used by the map.

## Rendered-Behavior Lane

Artifacts:
- Browser summary: `/Users/cheech/code/family-book/output/playwright/family-book-flow/summary.md`
- Browser traces: `/Users/cheech/code/family-book/output/playwright/family-book-flow/traces`
- Screenshots: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots`

Commands:
- `uv run pytest tests/test_location_service.py tests/test_pages.py tests/test_api.py -q`
- `node --check app/static/js/location_fields.js`
- `tests/ui/playwright-flow-checks.sh`
- `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json > output/audit/map-ui-codemap.json`

Result:
- `tests/test_location_service.py tests/test_pages.py tests/test_api.py`: `76 passed`
- Playwright flow: `passed`

High-signal map checks covered by the current flow:
- the map renders at least one accessible marker on the fallback SVG path
- keyboard navigation works on both SVG markers and the configured Google overlay path
- selected-marker details expose residence/burial and location-source semantics
- residence-country filtering changes the visible result set without breaking marker rendering
- Spanish locale coverage exists on the changed map surface
- mobile layout avoids horizontal overflow and keeps filters/details reachable
- changing country after place verification clears stale coordinates before save

## Visual / Persona Lane

Artifacts:
- Desktop first render: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/map.png`
- Desktop filtered state: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/map-filtered.png`
- Mobile map view: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/map-mobile.png`
- Spanish map surface: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/map-es.png`

Review notes:
- `contributing_member` / `view_people_or_burials_on_map` / desktop / `en`
  - `map.png` shows the family-distance filters, provider badge, selected-marker detail card, and marker semantics on the primary map view.
- `genealogy_researcher` / `interpret_family_distribution_on_map` / desktop / `en`
  - `map-filtered.png` shows the relationship and country filters narrowing the visible family distribution without collapsing the primary surface.
- `mobile_first_relative` / `understand_empty_state_and_filters` / mobile / `en`
  - `map-mobile.png` shows the single-column mobile layout with reachable filters and marker detail UI.
- `contributing_member` / `view_people_or_burials_on_map` / desktop / `es`
  - `map-es.png` shows the localized title and family-distance control labels on the changed map surface.

## Reviewer Notes

- This bundle is specific to `map_view`; existing `tree_workspace` and `calendar_workspace` artifacts remain separate in `/Users/cheech/code/family-book/output/audit`.
- The place-entry stale-coordinate probe is intentionally included in the release-confidence flow because the map’s truthfulness now depends on the person-edit normalization path, not just `/map` rendering in isolation.
