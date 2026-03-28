# Calendar UI Audit Evidence - S29 Calendar Polish Sprint

Surface under review: `calendar_workspace`

Sprint scope under audit:
- `FB-043` calendar primary surface and layout hierarchy
- `FB-044` manage calendars drawer and subscription UX
- `FB-045` event density, discovery, and detail intelligence
- `FB-046` guided holiday layers, mobile agenda, and empty/sparse recovery

Resolved from canonical sources:
- Persona registry: `/Users/cheech/code/family-book/docs/ops/persona_registry.yaml`
- UI surface matrix: `/Users/cheech/code/family-book/docs/ops/ui_surface_matrix.yaml`

Resolved personas:
- `contributing_member`
- `family_admin`
- `mobile_first_relative`

Resolved scenarios:
- `view_month_and_toggle_layers`
- `open_manage_calendars_and_subscribe`
- `inspect_day_details_and_upcoming_events`
- `add_holiday_layer_or_recover_from_empty_state`

Resolved viewports/locales:
- `desktop`, `mobile`
- `en`, `es`

## Structural Lane

Artifacts:
- CodeMap JSON: `/Users/cheech/code/family-book/output/audit/calendar-ui-codemap.json`

Changed files on `calendar_workspace`:
- `/Users/cheech/code/family-book/app/templates/calendar.html`
- `/Users/cheech/code/family-book/app/templates/partials/calendar_grid.html`
- `/Users/cheech/code/family-book/app/routes/calendar.py`
- `/Users/cheech/code/family-book/app/services/calendar_service.py`
- `/Users/cheech/code/family-book/app/static/css/main.css`

Result:
- `/calendar` now renders the month surface before secondary management UI.
- Feed management is implemented as a secondary drawer with grouped family feeds, holiday setup, imported-source controls, and feed-token security actions.
- Event decoration is wired from service output into localized calendar display labels, including birthday age context and locale-safe anniversary context.
- Mobile agenda behavior and selected-day / upcoming discovery surfaces are implemented inside the calendar grid partial rather than as detached markup.

## Rendered-Behavior Lane

Artifacts:
- Browser summary: `/Users/cheech/code/family-book/output/playwright/family-book-flow/summary.md`
- Browser traces: `/Users/cheech/code/family-book/output/playwright/family-book-flow/traces`
- Screenshots: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots`

Commands:
- `uv run pytest tests/test_calendar_and_relationships.py tests/test_pages.py tests/test_i18n.py -q`
- `tests/ui/playwright-flow-checks.sh`

Result:
- `tests/test_calendar_and_relationships.py tests/test_pages.py tests/test_i18n.py`: `52 passed`
- Playwright flow: `passed`

High-signal calendar checks covered by the current flow:
- the calendar grid lands above feed management on desktop first render
- richer event labels surface age-turning birthdays and anniversary-year context
- the manager drawer groups feed actions and supports search plus copy
- holiday presets are presented separately from family feed subscriptions
- mobile uses the agenda fallback without horizontal overflow
- Spanish locale coverage exists for the changed calendar surface and manager close action

## Visual / Persona Lane

Artifacts:
- Desktop first render: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/calendar-hero.png`
- Desktop management drawer: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/calendar-manager.png`
- Mobile agenda view: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/calendar-mobile.png`
- Spanish calendar surface: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/calendar-es.png`

Review notes:
- `contributing_member` / `view_month_and_toggle_layers` / desktop / `en`
  - `calendar-hero.png` shows the month surface, layer chips, upcoming rail, and selected-day panel as the primary content above the fold.
- `contributing_member` / `open_manage_calendars_and_subscribe` / desktop / `en`
  - `calendar-manager.png` shows grouped family-feed actions separated from holiday/import management.
- `mobile_first_relative` / `view_month_and_toggle_layers` / mobile / `en`
  - `calendar-mobile.png` shows the agenda-first fallback instead of a cramped month grid.
- `family_admin` / `add_holiday_layer_or_recover_from_empty_state` / desktop / `en`
  - `calendar-manager.png` captures guided holiday presets and advanced custom-feed entry in the same secondary surface.
- `contributing_member` / `inspect_day_details_and_upcoming_events` / desktop / `es`
  - `calendar-es.png` shows the localized calendar surface and supports the Spanish manager interaction path covered by Playwright.

## Reviewer Notes

- The current month sample is intentionally sparse enough to exercise the empty/sparse recovery callout while still proving birthdays and anniversaries render with richer labels.
- The audit bundle is specific to `calendar_workspace`; tree artifacts remain separate in `/Users/cheech/code/family-book/output/audit/tree-ui-audit-evidence.md`.
