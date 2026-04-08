# Task Packet - FB-131 Tree Sidebar Popout Collapse/Dock Fix

Status: Done

## Objective

Fix the popped-out tree sidebar so the caret/collapse control does not behave like the `x` close control.

## Why / KPI

The tree is the primary workspace. When the sidebar is popped out, clicking the caret currently makes the entire sidebar disappear, making it redundant with close and confusing the user.

## Scope

- In scope:
  - inspect tree sidebar state model in docked and popped-out modes
  - define the immediate behavior for the caret in floating mode
  - preserve `x` as close
  - preserve dock/popout/resize behavior
  - update accessible labels and tooltips
  - add focused regression coverage
- Out of scope:
  - full overlay-system rewrite
  - adopting a third-party UI library
  - changing the entire tree layout

## Likely Files

- `app/templates/tree.html`
- `app/static/js/tree.js`
- `app/static/css/main.css`
- `locales/en.json`
- `locales/es.json`
- `locales/ru.json`
- `tests/test_pages.py`
- `tests/ui/playwright-flow-checks.sh`

## Acceptance Criteria

- [x] In popped-out mode, caret/collapse does not close or disappear the sidebar.
- [x] `x` remains the close control.
- [x] Dock and popout controls remain functional.
- [x] If floating collapse/minimize is not supported, the control is hidden or relabeled instead of behaving like close.
- [x] Accessible labels reflect actual behavior.
- [x] Focused regression coverage proves the popped-out behavior.

## Validation Commands

- `uv run pytest tests/test_pages.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Definition of Done

- [x] Popped-out sidebar controls are distinct and predictable.

## Builder Evidence

- Changed surfaces: `tree_workspace`, `app/templates/tree.html`, `app/static/js/tree.js`.
- Resolved personas/scenarios: `contributing_member`, `family_admin`, `mobile_first_relative`; `find_person_in_tree`, `open_sidebar_and_edit_overview`, `add_relative_from_tree_context`.
- Structural check: `tests/test_pages.py::test_tree_sidebar_floating_collapse_docks_instead_of_closing` verifies the floating collapse guard docks instead of closing and that popout/dock toggle the collapse control.
- Rendered check: `make test-ui-playwright` includes `S47a popped-out sidebar collapse docks instead of closing`.
- Visual artifact: `output/playwright/family-book-flow/screenshots/s47a-sidebar-docked-after-collapse.png`.
- Sprint evidence: `docs/strategy/sprint-closeout-s47a.md`.
