# Tree UI Audit Evidence - S31 Relationship Correction Sprint

Surface under review: `tree_workspace`

Sprint scope under audit:
- `FB-051` relationship correction primitives and API truth
- `FB-052` tree relationship correction and editing flow

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

Artifacts:
- CodeMap JSON: `/Users/cheech/code/family-book/output/audit/tree-ui-codemap.json`
- Scope docs:
  - `/Users/cheech/code/family-book/task_packets/FB-051_relationship_correction_primitives_and_api_truth.md`
  - `/Users/cheech/code/family-book/task_packets/FB-052_tree_relationship_correction_and_editing_flow.md`
  - `/Users/cheech/code/family-book/backlog.md`
  - `/Users/cheech/code/family-book/docs/strategy/sprint-board-2026q1.md`

Changed implementation:
- `/Users/cheech/code/family-book/app/routes/relationships.py`
- `/Users/cheech/code/family-book/app/schemas.py`
- `/Users/cheech/code/family-book/app/templates/tree.html`
- `/Users/cheech/code/family-book/app/templates/partials/person_sidebar.html`
- `/Users/cheech/code/family-book/app/static/js/tree.js`
- `/Users/cheech/code/family-book/locales/en.json`
- `/Users/cheech/code/family-book/locales/es.json`
- `/Users/cheech/code/family-book/locales/ru.json`

Result:
- `changed_surface_classification`: `PASS`
- `canonical correction primitives`: `PASS`
- `i18n wiring for correction UI`: `PASS`

Notes:
- The canonical API now supports parent-child update and atomic reverse, plus truthful partnership updates.
- The tree workspace now exposes explicit `Edit relationship`, `Reverse direction`, and `Remove link` actions instead of relying on `Replace on tree` for correction.
- The relationship editor is part of the existing sidebar card flow rather than a separate redesign.

## Rendered-Behavior Lane

Artifacts:
- Browser summary: `/Users/cheech/code/family-book/output/playwright/family-book-flow/summary.md`
- Browser traces/replay: `/Users/cheech/code/family-book/output/playwright/family-book-flow/traces`
- Screenshots: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots`

Commands:
- `uv run pytest tests/test_api.py tests/test_pages.py -q`
- `tests/ui/playwright-flow-checks.sh`
- `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json > output/audit/tree-ui-codemap.json`

Result:
- `tests/test_api.py tests/test_pages.py`: `75 passed`
- Playwright flow: `passed`

High-signal checks covered by the current flow:
- existing relationship cards expose `Edit relationship` on the tree sidebar
- the desktop editor prefills current kind/confidence and the related-person summary
- a child relationship can be created, edited, reversed, and then removed from the tree workspace
- a partnership can be created, edited, and then removed from the tree workspace
- the canonical `/api/tree` payload reflects correction edits and reversed parent-child direction
- Spanish opens the actual relationship editor and verifies translated labels on the changed surface
- mobile opens the relationship editor and proves the correction actions are visible and not horizontally clipped

Verifier quality notes:
- the correction-flow browser check uses unique temporary relatives per run, so it cannot accidentally bind to leftover seeded names
- the reverse-direction path is verified against canonical `/api/tree` state rather than only sidebar text
- the localized tree verifier now opens the changed relationship editor, not just the quick-edit details panel

## Visual / Persona Lane

Artifacts:
- Desktop correction editor: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-relationship-editor-admin.png`
- Desktop browse/read: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-member-view.png`
- Mobile correction editor: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-relationship-editor-mobile.png`
- Mobile tree surface: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-mobile.png`
- Spanish correction editor: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-relationship-editor-es.png`
- Spanish tree surface: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-es.png`

Review notes:
- `contributing_member` / `add_relative_from_tree_context` / desktop / `en`
  - `tree-relationship-editor-admin.png` shows correction controls inline with the existing relationship cards.
  - The card/editor split now makes `edit`, `reverse`, and `remove` distinct actions instead of overloading `replace`.
- `family_admin` / `open_sidebar_and_edit_overview` / desktop / `en`
  - the desktop editor keeps the current related person, metadata fields, and destructive action in one visible block without requiring navigation away from the tree.
- `mobile_first_relative` / `find_person_in_tree` / mobile / `en`
  - `tree-relationship-editor-mobile.png` shows the actual correction form on a narrow viewport, with the action row still reachable.
  - `tree-mobile.png` still confirms the underlying tree surface fits without horizontal overflow.
- `contributing_member` / `add_relative_from_tree_context` / desktop / `es`
  - `tree-relationship-editor-es.png` proves the changed correction surface is localized, including the editor title, related-person summary, and correction actions.

Rubric outcome:
- `hierarchy_and_readability`: pass
- `control_discoverability`: pass
- `mobile_fit`: pass
- `translation_completeness`: pass

Persona-critical findings:
- none in reviewed sprint scope

## Audit Closure

1. Auditor concern: the relationship editor leaked hardcoded English placeholder copy
   - Closed by localizing the editor source placeholder in:
     - `/Users/cheech/code/family-book/app/templates/partials/person_sidebar.html`
     - `/Users/cheech/code/family-book/locales/en.json`
     - `/Users/cheech/code/family-book/locales/es.json`
     - `/Users/cheech/code/family-book/locales/ru.json`
   - The Spanish browser lane now opens the editor and verifies the changed surface directly.

2. Auditor concern: mobile discoverability for correction controls was unproven
   - Closed by adding deterministic mobile editor assertions and the screenshot:
     - `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-relationship-editor-mobile.png`
   - The browser lane now proves the correction action row remains reachable on a phone-sized viewport.

3. Auditor concern: the tree audit note was stale and still described the earlier genealogy sprint
   - Closed by regenerating this note and refreshing the structural/browser/visual references to `FB-051` and `FB-052`.
