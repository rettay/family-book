# Task Packet - FB-045 Calendar Event Density, Discovery, and Detail Intelligence

## Objective

Make the calendar itself more informative and easier to scan by improving event styling, dense-month handling, upcoming-event discovery, and day-level detail semantics.

## Why / KPI

- Once the calendar is visible, it still under-delivers on meaning: dots are too lossy, event labels are generic, and dense family months require too much clicking to interpret.
- CFLSR improves when family members can quickly understand what is happening this month and why an event matters, especially birthdays and anniversaries.

Primary KPI:
- improve comprehension of family events per visit to `/calendar`.

Secondary KPI:
- reduce clicks required to understand a busy day or month.

## Scope

- In scope:
  - improve calendar event styling so family events and imported/holiday events are visually distinguishable at a glance
  - enrich birthday and anniversary labels with age-turning and years-married context where the data supports it
  - improve density handling for busy days and months with more informative indicators than anonymous dots alone
  - add an adjacent discovery surface such as `Upcoming`, `This Month`, or selected-day context on desktop
  - improve day-detail presentation so event type, person context, and source context are clearer
  - preserve responsive fallback behavior on mobile
- Out of scope:
  - full week view or multi-column agenda application
  - reminders, RSVP, or custom event authoring
  - branch-aware color systems if they dilute readability more than they help

## Task Type

- member-facing calendar readability and detail packet

## Dependencies and Ordering Assumptions

- Depends on FB-043 for the primary page shell.
- May overlap with FB-044’s management shell but should not depend on completion of all feed grouping work.

## Changed Surfaces

- `calendar_workspace`

## Target Personas

- Primary personas:
  - `contributing_member`
- Safety personas:
  - `mobile_first_relative`
  - `family_admin`

## Required Scenario IDs

- `view_month_and_toggle_layers`
- `inspect_day_details_and_upcoming_events`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/templates/partials/calendar_grid.html`
  - `app/templates/calendar.html`
  - `app/routes/calendar.py`
  - `app/services/calendar_service.py`
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
  improve the information value and scanability of the month calendar
- Verifier:
  structural review, deterministic browser assertions, and visual/persona review
- Reference/oracle:
  family-calendar expectations for birthdays, anniversaries, holidays, and dense-month navigation
  existing family and imported event data in `calendar_service.py`
- Expected evidence:
  screenshots and deterministic checks showing informative busy-day handling, enriched labels, and a usable upcoming/discovery surface
- Known failure modes / reward hacks:
  - colors change but event meaning remains too shallow
  - age/anniversary calculations exist in service output but never surface in the actual UI
  - a new sidebar or list appears but duplicates the same generic labels
  - dense-day handling still collapses to anonymous `+N` counts with no recovery path
- Verifiability class:
  `bounded-judgment`
- Context policy:
  optimize for fast interpretation by normal family members rather than maximum event metadata density on the month grid itself

## UI Review Requirements

- Structural oracle:
  - CodeMap over `calendar_workspace`, especially service-to-template wiring for enriched labels and new discovery surfaces
  - confirm type-specific styling remains localized and theme-safe
- Browser oracle:
  - seeded assertions proving:
    - birthdays display age-turning context when the birth year is known
    - anniversaries display years-married context when the start year is known
    - imported/holiday events are visually distinct from family milestones
    - a dense seeded month remains interpretable through counts, details, or upcoming views
    - selected day or upcoming panel updates correctly when interacting with the month surface
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough understanding a busy family month
  - `mobile_first_relative` mobile walkthrough reading agenda/detail content without dense-grid confusion
  - `family_admin` desktop walkthrough confirming imported holidays remain visually separate from family events
- Required artifacts:
  - CodeMap JSON output
  - screenshots of a dense month, selected-day details, and upcoming panel
  - replay notes covering birthday and anniversary interpretation
- Expected visual states:
  - family milestones feel emotionally specific, not generic
  - imported holidays do not visually blend into birthdays/anniversaries
  - busy months still yield understandable detail without excessive clicking

## Acceptance Criteria

- [ ] Birthdays show age-turning context when the required year data is available.
- [ ] Anniversaries show years-married context when the partnership start year is available.
- [ ] Family milestones and imported/holiday events are visually distinguishable beyond a barely different dot color.
- [ ] Busy days or months provide a readable recovery path through richer density handling and/or an upcoming or selected-day panel.
- [ ] Desktop and mobile both preserve readable event discovery without regressing navigation or clipping.

## Risk and Verification Notes

- Complexity hotspots:
  - date math for partial-precision records
  - dense-month information design without overwhelming the grid
  - keeping detail surfaces synchronized with HTMX month reloads
- Likely shallow-pass failure modes:
  - service labels are enriched but truncation or styling hides the benefit
  - dense-month UI still requires trial-and-error clicking
  - imported events remain visually too similar to family events
- Required verification depth:
  - deterministic assertions on rendered labels and event distinctions
  - at least one dense seeded month in visual review
- Sufficient discriminative power means:
  review should fail if a user cannot quickly tell who is having a birthday, what anniversary count is being celebrated, or how to inspect a crowded day.

## Execution Budget

- Builder may explore:
  - chips, stacked labels, count badges, right-rail discovery panels, or richer selected-day layouts
  - age and anniversary computations in the service layer
  - modest interaction changes to keep detail discovery obvious
- Builder must escalate if:
  - precise age/anniversary logic becomes ambiguous for partial-precision dates in a way that affects product truthfulness
  - the chosen density approach materially harms mobile fit
- Material scope drift:
  - full scheduler product features
  - custom event editing and reminders
- Proof obligations before review:
  - enriched event intelligence is visible in the rendered UI
  - dense-month readability is proven with seeded adversarial cases

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 readability regressions remain on dense or mixed-type calendar months
- [ ] The calendar conveys family meaning, not just date occupancy
