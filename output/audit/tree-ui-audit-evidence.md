# Tree UI Audit Evidence

Surface under review: `tree_workspace`

Resolved from canonical sources:
- Persona registry: `/Users/cheech/code/family-book/docs/ops/persona_registry.yaml`
- UI surface matrix: `/Users/cheech/code/family-book/docs/ops/ui_surface_matrix.yaml`

Resolved personas:
- `contributing_member`
- `family_admin`
- `mobile_first_relative`

Resolved scenarios:
- `find_person_in_tree`
- `open_sidebar_and_edit_overview`
- `add_relative_from_tree_context`

Resolved viewports/locales:
- `desktop`, `mobile`
- `en`, `es`

## Structural Lane

Artifact:
- CodeMap JSON: `/Users/cheech/code/family-book/output/audit/tree-ui-codemap.json`

Result:
- `Changed UI surfaces`: `PASS`
- CodeMap resolves the changed implementation to `tree_workspace`
- Required personas/scenarios/viewports/locales in the artifact match the matrix for `tree_workspace`
- Changed tree files classified on-surface: `app/static/js/tree.js`, `app/templates/tree.html`, `app/templates/partials/person_sidebar.html`

Notes:
- CodeMap reports unmatched support files (`app/static/css/main.css`, locale files, Playwright scripts), but it does not report a partial changed-surface classification for the tree implementation itself.
- CodeMap also reports existing repo-level warnings outside this packet's acceptance scope; they do not contradict the tree surface classification.

## Rendered-Behavior Lane

Artifacts:
- Browser summary: `/Users/cheech/code/family-book/output/playwright/family-book-flow/summary.md`
- Browser traces/replay: `/Users/cheech/code/family-book/output/playwright/family-book-flow/traces`
- Screenshots: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots`

Commands:
- `uv run pytest tests/test_pages.py -q`
- `tests/ui/playwright-flow-checks.sh`

Result:
- `pytest`: `15 passed`
- Playwright flow: `passed`

High-signal tree checks now covered:
- partnered parents share a generation row and children render below the family unit
- two known parents without a partnership row still produce shared family-unit geometry and do not invent a partnership edge
- graph cancel remains hidden outside active edit mode
- relationship calculator and graph-edit mode cannot overlap; `Escape` exits cleanly
- controls collapse/expand without zero-width canvas regression
- focus recovery, keyboard open/close, inline edits, relationship linking/replacing/removal, and mobile overflow checks all pass

Verifier hardening included in this packet:
- `/Users/cheech/code/family-book/tests/ui/playwright_cli.sh` now fails when Playwright emits structured `### Error` output even if the CLI exits `0`
- the relationship-calculator assertion now checks DOM `hidden` state rather than Playwright `isVisible()` for a control that can remain layout-visible while semantically hidden

## Visual / Persona Lane

Artifact set:
- Desktop browse/read screenshot: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-member-view.png`
- Desktop focus/context screenshot: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-focus-sidebar.png`
- Mobile browse screenshot: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/home-mobile.png`
- Spanish tree screenshot: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-es.png`

Review notes:
- `contributing_member` / `find_person_in_tree` / desktop / `en`
  `tree-member-view.png` shows generation bands, lateral partner placement, and the adversarial no-partnership co-parent case (`Jane Martin` + `Alex Stone` -> `Jordan Stone`) as a shared descendant structure rather than a fake spouse or ancestry line.
- `family_admin` / `open_sidebar_and_edit_overview` + `add_relative_from_tree_context` / desktop / `en`
  `tree-focus-sidebar.png` shows the selected-person family context summary, explicit focus/root actions, and relationship-edit entry points in one sidebar without the old always-on cancel affordance leaking into browse mode.
- `mobile_first_relative` / `find_person_in_tree` / mobile / `en`
  `home-mobile.png` shows the tree controls stacked without horizontal overflow and the canvas/zoom controls still reachable on a narrow viewport.
- `contributing_member` / `find_person_in_tree` / desktop / `es`
  `tree-es.png` shows the tree workspace labels localized on the changed surface itself (`Arbol Familiar`, `Foco actual`, `Guardar Vista`, `Calcular relación`, `Aplicar Filtros`) while preserving the same family-unit semantics.

Rubric outcome:
- `hierarchy_and_readability`: pass
- `control_discoverability`: pass
- `mobile_fit`: pass

Persona-critical findings:
- none in the reviewed tree states above

## Defect Closure Map

1. Auditor defect: family-unit layout required a partnership row
   Fixed in `app/static/js/tree.js` by deriving `familyUnitsByPair` from any exactly-two-known-parent set and using those units in layout/rendering.
   Proved by the new browser assertion and the `tree-member-view.png` / `tree-es.png` screenshots.

2. Auditor defect: Playwright harness could print failures and still go green
   Fixed in `tests/ui/playwright_cli.sh` by treating structured Playwright error output as fatal.
   Proved by the rerun of `tests/ui/playwright-flow-checks.sh`, which now exits green only after all assertions pass.

3. Auditor defect: missing structural and visual/persona artifacts
   Closed by `tree-ui-codemap.json` plus this persona-backed evidence note and the referenced screenshot/replay artifacts.
