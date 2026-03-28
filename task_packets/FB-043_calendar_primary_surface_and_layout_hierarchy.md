# Task Packet - FB-043 Calendar Primary Surface and Layout Hierarchy

## Objective

Rebuild `/calendar` so the month calendar is the hero surface at first render and feed management is demoted to a secondary control layer instead of consuming the page above the fold.

## Why / KPI

- The current calendar page opens with a wall of subscription links before the actual month view, which demotes the core utility and makes the page feel like configuration plumbing instead of a family calendar.
- CFLSR suffers when members land on `/calendar`, do not immediately see family events, and have to scroll past admin-style controls before understanding the page.

Primary KPI:
- increase first-screen comprehension and usage of the family calendar surface on `/calendar`.

Secondary KPI:
- reduce bounce and confusion caused by configuration-heavy UI appearing before the calendar itself.

## Scope

- In scope:
  - reorder the page so the month calendar appears before feed and source-management UI in DOM and rendered order
  - define a new page architecture for `/calendar` with a clear hero region, secondary management entrypoint, and stable desktop/mobile layout shell
  - add a page-level toolbar or subheader for month navigation, `Today`, and visible layer controls if needed to keep the month surface self-sufficient
  - ensure the first viewport at common desktop width shows title plus usable calendar content without scrolling
  - keep admin-only controls secondary in presentation even when present
- Out of scope:
  - full grouped feed management UX beyond the collapsed/secondary shell needed to unblock it
  - branch/person feed generation logic
  - richer event detail semantics, age math, or holiday source presets
  - push reminders, week view, or notifications

## Task Type

- member-facing calendar IA and layout packet

## Dependencies and Ordering Assumptions

- This is the first packet in the calendar sprint. Later packets assume `/calendar` already treats the month view as primary and exposes a stable secondary entrypoint for feed management.
- Builder may introduce a drawer, sheet, or collapsed management panel here, but detailed feed grouping/search belongs to FB-044.

## Changed Surfaces

- `calendar_workspace`

## Target Personas

- Primary personas:
  - `contributing_member`
- Safety personas:
  - `family_admin`
  - `mobile_first_relative`

## Required Scenario IDs

- `view_month_and_toggle_layers`
- `open_manage_calendars_and_subscribe`
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
  - `app/templates/calendar.html`
  - `app/templates/partials/calendar_grid.html`
  - `app/static/css/main.css`
  - `app/routes/calendar.py`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_pages.py`
- Validation commands:
  - `uv run pytest tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  restructure the calendar page so event viewing is primary and management is secondary
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  `/Users/cheech/code/family-book/foundation/UX_NORTH_STAR.md`
  the current live screenshots showing the subscription wall above the calendar
  expected first-screen behavior for a consumer family calendar
- Expected evidence:
  browser proof that the month grid is visible above the fold on desktop, that mobile opens into a readable primary view, and that management UI is no longer the first dominant block
- Known failure modes / reward hacks:
  - the calendar is moved higher in DOM but still visually pushed below a large secondary panel
  - the management section is technically collapsible but opens by default or remains visually louder than the calendar
  - desktop improves while mobile still opens into a long preamble
  - the toolbar becomes sticky but obscures the grid or creates clipping
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prioritize clear hierarchy and first-screen comprehension over preserving the current single-column arrangement

## UI Review Requirements

- Structural oracle:
  - CodeMap over `calendar_workspace` to confirm layout, copy, and CSS are wired consistently
  - confirm management UI is secondary in template structure rather than only visually minimized
- Browser oracle:
  - seeded assertions proving:
    - the calendar grid container is visible in the initial desktop viewport without scrolling
    - management UI is collapsed, drawer-based, or otherwise secondary on first load
    - admin source controls do not displace the month grid above the fold
    - mobile shows a clear primary calendar or agenda view before management content
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough landing on the month view and using navigation/layer toggles
  - `family_admin` desktop walkthrough confirming admin controls are available but not dominant
  - `mobile_first_relative` mobile walkthrough confirming the first screen has an obvious primary action and readable context
- Required artifacts:
  - CodeMap JSON output
  - desktop and mobile screenshots of `/calendar` on first load
  - replay notes showing the management UI entrypoint and the calendar visible at first render
- Expected visual states:
  - month grid or agenda content appears as the hero
  - management is discoverable but not visually equal to the calendar
  - no raw feed wall occupies the fold

## Acceptance Criteria

- [ ] The first rendered region of `/calendar` shows the month calendar surface before feed or source-management lists.
- [ ] At a 1280px desktop viewport, the initial screen contains visible usable calendar content without scrolling.
- [ ] Feed management and external-source controls are available through a clearly secondary interaction model rather than a full open wall above the calendar.
- [ ] Mobile opens into a readable primary calendar or agenda surface without an oversized management preamble.
- [ ] New copy and control labels remain localized across `en`, `es`, and `ru`.

## Risk and Verification Notes

- Complexity hotspots:
  - balancing hero-calendar layout with admin-only controls
  - making the same structure work cleanly on desktop and mobile
  - avoiding regressions in HTMX month navigation while changing the shell
- Likely shallow-pass failure modes:
  - the page is reordered but still feels configuration-first
  - CSS-only fixes hide content visually while leaving keyboard or mobile flow awkward
  - the management shell becomes another clutter source
- Required verification depth:
  - first-viewport browser assertions plus visual evidence on desktop and mobile
  - wrong-variant evidence should fail if the old feed-wall-first layout returns
- Sufficient discriminative power means:
  review should fail if a first-time member cannot identify the calendar as the primary purpose of the page within one screen.

## Execution Budget

- Builder may explore:
  - drawer, sheet, collapsed panel, or two-column layouts
  - sticky or semi-sticky page toolbar patterns
  - modest template and CSS restructuring to create a durable shell for later packets
- Builder must escalate if:
  - the current HTMX structure makes hierarchy correction require a broader routing rewrite
  - the design depends on introducing a new JS framework or calendar library
- Material scope drift:
  - full feed grouping/search implementation
  - richer event intelligence or holiday preset libraries
- Proof obligations before review:
  - initial viewport evidence proves the calendar is primary
  - structural evidence shows the hierarchy change is real, not purely cosmetic

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 hierarchy regressions remain on `/calendar`
- [ ] `/calendar` now reads as a family calendar first and a feed configuration page second
