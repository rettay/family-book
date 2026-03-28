# Task Packet - FB-044 Manage Calendars Drawer and Subscription UX

## Objective

Turn the current raw feed-link dump into a grouped, searchable, action-oriented `Manage Calendars` experience for family feeds and outbound subscription links.

## Why / KPI

- The page currently exposes naked `https` and `webcal` URLs as if they were primary content, which is a poor consumer subscription model and scales badly as more feeds are added.
- CFLSR improves when members can discover and subscribe to the right family feed without understanding raw URLs, query strings, or admin concepts.

Primary KPI:
- reduce friction to finding and using the correct family calendar feed.

Secondary KPI:
- improve truthful discoverability of outbound feeds for all-events, type-based, person-based, and branch-based subscriptions where supported.

## Scope

- In scope:
  - replace the flat feed wall with grouped feed management inside a drawer, sheet, modal, or equivalent secondary surface
  - group outbound feeds by meaningful categories such as family-wide, event type, branches, and people where routes support them
  - add search or filter for feeds when the group size is non-trivial
  - add explicit actions such as `Subscribe`, `Copy Link`, and `Download .ics` or equivalent truthful affordances
  - visually separate family feed subscriptions from holiday/source management concerns
  - provide immediate UI feedback for copy or subscribe actions without pretending the app can verify external client subscription state
- Out of scope:
  - push reminders or in-app reminders
  - inferred subscribed/unsubscribed state unless the app truly tracks it
  - holiday source presets or country/religion pickers beyond the separation needed to keep the drawer coherent
  - major changes to the month grid itself

## Task Type

- member-facing calendar feed-management packet

## Dependencies and Ordering Assumptions

- Depends on FB-043 establishing the secondary entrypoint and page shell.
- If person/branch feed routes are incomplete or missing, builder must either implement truthful support in the same packet or explicitly narrow the visible grouped UI so it does not imply unsupported granularity.

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
  - `app/routes/calendar.py`
  - `app/services/calendar_service.py`
  - `app/static/css/main.css`
  - `app/static/js/main.js`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_api.py`
  - `tests/test_pages.py`
- Validation commands:
  - `uv run pytest tests/test_api.py tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  redesign feed discovery and subscription handling for the calendar surface
- Verifier:
  structural review, deterministic browser flow, and visual/persona review
- Reference/oracle:
  consumer calendar subscription patterns such as a secondary `Manage Calendars` surface
  existing outbound ICS/webcal route truth in `app/routes/calendar.py`
- Expected evidence:
  grouped management screenshots, deterministic copy/subscribe action checks, and visual proof that raw URLs are no longer dumped as the main interface
- Known failure modes / reward hacks:
  - the UI is relabeled but still exposes long raw URLs as the main interaction
  - grouping exists only visually while person/branch feeds are missing or broken
  - copy buttons exist but there is no user-visible confirmation
  - mobile management UI becomes cramped or clipped
- Verifiability class:
  `bounded-judgment`
- Context policy:
  preserve product truthfulness about what outbound feeds exist; do not imply tracked subscriptions the app cannot actually confirm

## UI Review Requirements

- Structural oracle:
  - CodeMap over `calendar_workspace` and feed URL generation
  - confirm grouped feed data and labels are derived from supported feed scopes rather than hardcoded placeholders
- Browser oracle:
  - seeded assertions proving:
    - `Manage Calendars` opens and closes correctly on desktop and mobile
    - feeds are grouped by category rather than rendered as one flat list
    - search/filter narrows feed results where implemented
    - `Copy Link` or equivalent feedback visibly succeeds
    - `webcal://` subscribe links are present and correctly formed where offered
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough finding and subscribing to birthdays
  - `family_admin` walkthrough distinguishing family feeds from holiday/source controls
  - `mobile_first_relative` mobile walkthrough opening the manager and finding one desired feed quickly
- Required artifacts:
  - CodeMap JSON output
  - screenshots of grouped management UI on desktop and mobile
  - replay notes covering one copy action and one subscribe action
- Expected visual states:
  - feed groups are clearly labeled and separated
  - raw URLs are subordinate to explicit actions
  - family subscriptions and holiday/source tools are not conflated

## Acceptance Criteria

- [ ] Feed management is presented through a grouped secondary surface rather than a flat sequential wall.
- [ ] Outbound family feeds are organized into truthful categories such as family-wide, event-type, branch, or person scopes according to actual route support.
- [ ] The UI provides explicit subscribe/copy actions with visible confirmation rather than only showing raw URLs.
- [ ] Family feed subscriptions are visually separated from holiday/import source management.
- [ ] Desktop and mobile both provide a usable feed-management interaction without clipping or search/discovery failure.

## Risk and Verification Notes

- Complexity hotspots:
  - truthful branch/person feed scope support
  - keeping mobile management UI compact and tappable
  - avoiding fake subscription state that the server cannot validate
- Likely shallow-pass failure modes:
  - categories are present but not meaningfully discoverable
  - the action buttons just reveal the same raw URL dump
  - mobile drawer height or focus behavior breaks usability
- Required verification depth:
  - deterministic browser evidence for copy/subscribe flows
  - negative-case evidence that bad or missing feed categories do not silently fall back to misleading labels
- Sufficient discriminative power means:
  review should fail if a normal member still has to read raw URLs to understand how to subscribe.

## Execution Budget

- Builder may explore:
  - drawer, modal, accordion, or side-panel feed-management patterns
  - lightweight client-side search/filter for feed groups
  - route additions needed to support truthful branch/person feeds
- Builder must escalate if:
  - per-branch or per-person feeds require a broader authorization redesign
  - a robust UX depends on persistent subscription tracking not currently modeled
- Material scope drift:
  - holiday source library curation
  - notification/reminder systems
- Proof obligations before review:
  - grouped feed scopes match actual runtime behavior
  - copy/subscribe actions are deterministic and visible to the user

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 truthfulness regressions remain in feed scope or subscribe affordances
- [ ] Feed management now behaves like a discoverable configuration layer instead of raw transport plumbing
