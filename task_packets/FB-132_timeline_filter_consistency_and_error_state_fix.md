# Task Packet - FB-132 Timeline Filter Consistency and Error-State Fix

Status: Done

## Objective

Fix timeline filtering so event-type and year filters work consistently and valid responses do not display `could not load content`.

## Why / KPI

Production use shows the timeline page is unreliable. With year range `1880` to `2002`, expected birthdays and deaths exist, but filtering can show errors, empty content for `All Events`, or inconsistent behavior between `All Events` and `births`.

## Scope

- In scope:
  - event-type dropdown value mapping
  - `All Events` serialization behavior
  - year-from/year-to filter interactions
  - partial update error handling
  - empty/no-results state
  - regression tests for `1880` to `2002`
- Out of scope:
  - redesigning the timeline visualization
  - adding new event types
  - calendar feature changes

## Likely Files

- `app/routes/timeline.py`
- `app/services/timeline_service.py`
- `app/templates/timeline.html`
- `app/templates/partials/timeline_events.html`
- `app/static/js/main.js`
- `locales/en.json`
- `locales/es.json`
- `locales/ru.json`
- `tests/test_calendar_and_relationships.py`
- `tests/test_pages.py`
- `tests/test_timeline.py`

## Acceptance Criteria

- [x] `All Events` maps to no `event_type` filter or an explicitly supported backend value.
- [x] `Births`, `Deaths`, and `Marriages` map to backend-supported values.
- [x] `from=1880` and `to=2002` works with `All Events`.
- [x] `from=1880` and `to=2002` works with specific event types.
- [x] Valid filter responses never show `could not load content`.
- [x] Empty results show an intentional no-results state.
- [x] Server/client errors show an error state with enough detail for debugging.
- [x] Regression tests cover the reported range and `All Events` case.

## Validation Commands

- `uv run pytest tests/test_timeline.py tests/test_pages.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Definition of Done

- [x] Timeline filters are reliable enough for production use.

## Builder Evidence

- Changed surfaces: `moments_and_timeline`, `app/routes/timeline.py`, `app/templates/partials/timeline_events.html`.
- Resolved personas/scenarios: `contributing_member`, `mobile_first_relative`; `add_story_or_note`, `view_recent_family_activity`.
- Structural check: `uv run pytest tests/test_timeline.py tests/test_pages.py -q` covers event-type aliases, empty HTMX year inputs, the `1880` to `2002` range, and the `All Events` case.
- Rendered check: `make test-ui-playwright` includes `S47a timeline filters keep all-events range stable` and `S47a timeline filters cover Spanish mobile surface`.
- Visual artifact: `output/playwright/family-book-flow/screenshots/s47a-timeline-filters.png`.
- Visual artifact: `output/playwright/family-book-flow/screenshots/s47a-timeline-filters-mobile-es.png`.
- Sprint evidence: `docs/strategy/sprint-closeout-s47a.md`.
