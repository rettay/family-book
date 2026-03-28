# Task Packet - FB-046 Guided Holiday Layers, Mobile Agenda, and Empty States

## Objective

Make holiday and observance layers discoverable through guided setup, while improving mobile agenda behavior and empty-state recovery so the calendar feels useful even before a family has many events.

## Why / KPI

- The product supports inbound holiday calendars, but the current UI expects users to know raw iCal URLs and mixes that concern too closely with family feed subscription.
- New or light-data families need an obvious way to make the calendar feel alive. A blank or sparse month should lead to setup actions, not dead ends.

Primary KPI:
- improve successful activation of holiday layers and first-run calendar usefulness.

Secondary KPI:
- reduce mobile and empty-state confusion on `/calendar`.

## Scope

- In scope:
  - create a distinct `Add Holidays` or equivalent entrypoint separate from family feed subscription
  - add guided holiday and observance setup using curated country, region, religion, or preset source choices where possible
  - keep manual URL entry available as an advanced or admin path rather than the primary discovery model
  - strengthen mobile agenda/list behavior and management ergonomics on narrow screens
  - redesign empty and sparse states so they prompt useful next steps such as subscribing to family feeds or adding holiday layers
  - ensure external/holiday layer language is clearly separated from family subscriptions
- Out of scope:
  - reminders or push notifications for holidays
  - exhaustive global holiday-source coverage
  - fully personalized holiday recommendations based on inferred person attributes

## Task Type

- member-facing calendar activation and recovery packet

## Dependencies and Ordering Assumptions

- Depends on FB-043 for the page shell and FB-044 for the secondary management surface.
- Holiday setup should integrate with existing external-source plumbing rather than introducing a separate incompatible source model.

## Changed Surfaces

- `calendar_workspace`

## Target Personas

- Primary personas:
  - `contributing_member`
- Safety personas:
  - `family_admin`
  - `mobile_first_relative`

## Required Scenario IDs

- `open_manage_calendars_and_subscribe`
- `add_holiday_layer_or_recover_from_empty_state`
- `view_month_and_toggle_layers`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/templates/calendar.html`
  - `app/templates/partials/calendar_grid.html`
  - `app/routes/calendar.py`
  - `app/services/calendar_service.py`
  - `app/models/calendar.py`
  - `app/static/css/main.css`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/test_calendar_and_relationships.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_calendar_and_relationships.py tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  improve holiday-layer setup, mobile usability, and first-run recovery on the calendar surface
- Verifier:
  structural review, deterministic browser assertions, and visual/persona review
- Reference/oracle:
  the product promise that holiday/religious calendars can be layered into the family calendar
  current empty-state and manual-URL-heavy admin flow on `/calendar`
- Expected evidence:
  guided setup screenshots, empty-state recovery walkthroughs, and mobile screenshots showing a usable agenda/management experience
- Known failure modes / reward hacks:
  - `Add Holidays` exists only as relabeled manual URL entry
  - presets appear in UI but do not produce valid sources
  - mobile agenda remains secondary to a cramped management surface
  - empty states add copy but still provide no obvious next action
- Verifiability class:
  `bounded-judgment`
- Context policy:
  favor clear activation paths and truthful setup guidance over exhaustive source catalogs

## UI Review Requirements

- Structural oracle:
  - CodeMap over `calendar_workspace` and source-management wiring
  - confirm holiday setup uses the same underlying source model or an explicitly compatible extension
- Browser oracle:
  - seeded assertions proving:
    - holiday setup is presented as a separate action from family feed subscription
    - at least one preset holiday or observance path can be added without typing a raw URL
    - empty or sparse state presents actionable setup paths
    - mobile renders a usable agenda/list view and manageable controls without clipping
    - `webcal://` or equivalent subscribe actions remain available on mobile for outbound feeds
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough recovering from an empty or sparse calendar
  - `family_admin` walkthrough adding a holiday layer through guided setup
  - `mobile_first_relative` mobile walkthrough using agenda view and management affordances
- Required artifacts:
  - CodeMap JSON output
  - screenshots of holiday setup, empty state, and mobile agenda
  - replay notes covering at least one guided holiday-add flow
- Expected visual states:
  - family feeds and holiday layers are clearly separate concepts
  - empty state behaves like onboarding, not failure
  - mobile remains legible and action-oriented

## Acceptance Criteria

- [ ] The calendar offers a distinct `Add Holidays` or equivalent action separate from family feed subscription.
- [ ] A user can add at least one holiday or observance layer through a guided preset path without manually entering an iCal URL.
- [ ] Manual URL entry remains available as a secondary/advanced path rather than the primary holiday discovery experience.
- [ ] Empty or sparse calendar states present actionable next steps such as adding holiday layers or subscribing to family feeds.
- [ ] Mobile provides a usable agenda/list-first recovery path and management interaction with no critical clipping or hidden controls.

## Risk and Verification Notes

- Complexity hotspots:
  - sourcing and maintaining truthful preset holiday feeds
  - balancing admin-only source configuration with member-facing discovery language
  - keeping mobile interactions simple while the page supports both viewing and setup
- Likely shallow-pass failure modes:
  - the UI separates holidays conceptually but still requires users to paste raw URLs
  - mobile empty states become dense walls of copy
  - advanced/admin controls leak into member-first empty states
- Required verification depth:
  - deterministic browser evidence for guided setup and mobile agenda
  - wrong-variant evidence should fail if the flow regresses to raw-URL-first behavior
- Sufficient discriminative power means:
  review should fail if a first-time user still needs outside knowledge of iCal sources to make the calendar feel alive.

## Execution Budget

- Builder may explore:
  - curated preset lists, country/religion pickers, or template sources mapped onto the existing source model
  - bottom-sheet or drawer patterns for mobile management
  - empty-state onboarding modules tied to actual available actions
- Builder must escalate if:
  - preset feeds require operational commitments or third-party dependencies not already acceptable for the product
  - the current source model cannot represent guided presets without schema changes broader than this packet
- Material scope drift:
  - comprehensive world-holiday catalog maintenance
  - notification or recommendation systems
- Proof obligations before review:
  - at least one guided holiday path works end to end
  - empty-state and mobile evidence show clear recovery actions, not just new copy

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 activation regressions remain for empty, sparse, or mobile calendar states
- [ ] The calendar now has an understandable setup path for both family and holiday layers
