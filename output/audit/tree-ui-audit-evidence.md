# Tree UI Audit Evidence - S28 Genealogy Sprint

Surface under review: `tree_workspace`

Sprint scope under audit:
- `FB-039` family-unit / genealogy layout foundation
- `FB-040` multi-household and remarriage correctness
- `FB-041` non-biological and partnership-state semantics
- `FB-042` launch-narrowed to unknown-parent and sparse-branch readability

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

## Scope Boundary

Launch-narrowing for `FB-042` is explicit:
- Packet: `/Users/cheech/code/family-book/task_packets/FB-042_non_person_nodes_unknown_parents_and_sparse_branch_readability.md`
- Backlog: `/Users/cheech/code/family-book/backlog.md`
- Sprint board: `/Users/cheech/code/family-book/docs/strategy/sprint-board-2026q1.md`

The shipped tree remains person-only at the payload/model boundary:
- `/Users/cheech/code/family-book/app/schemas.py`
- `/Users/cheech/code/family-book/app/routes/tree.py`

Audit interpretation:
- unknown-parent / single-parent / sparse-branch readability is in scope and implemented
- pets, institutions, and other non-person nodes are deferred and must not be implied by the shipped UI

## Structural Lane

Artifacts:
- CodeMap JSON: `/Users/cheech/code/family-book/output/audit/tree-ui-codemap.json`
- Scope docs:
  - `/Users/cheech/code/family-book/task_packets/FB-042_non_person_nodes_unknown_parents_and_sparse_branch_readability.md`
  - `/Users/cheech/code/family-book/backlog.md`
  - `/Users/cheech/code/family-book/docs/strategy/sprint-board-2026q1.md`

Result:
- `Changed UI surfaces`: `PASS`
- Changed implementation resolves to `tree_workspace`
- Tree surface changes are structurally present in:
  - `/Users/cheech/code/family-book/app/static/js/tree.js`
  - `/Users/cheech/code/family-book/app/templates/tree.html`
  - `/Users/cheech/code/family-book/app/templates/partials/person_sidebar.html`
  - `/Users/cheech/code/family-book/app/static/css/main.css`
- The relationship editor and renderer now have explicit support for:
  - family-unit clustering
  - multi-household partner placement
  - adoptive / guardian parent-child kinds
  - current vs former partnership styling
- `FB-042` is now documented truthfully as a narrowed launch scope rather than silently promising non-person-node support that the payload cannot represent.

Notes:
- The tree payload in `/api/tree` still exposes only `persons`, `parent_child`, and `partnerships`, which is why non-person nodes are deferred rather than treated as partially implemented.
- CodeMap still reports broader repo warnings outside this sprint’s acceptance scope; they do not contradict the `tree_workspace` classification.

## Rendered-Behavior Lane

Artifacts:
- Browser summary: `/Users/cheech/code/family-book/output/playwright/family-book-flow/summary.md`
- Browser traces/replay: `/Users/cheech/code/family-book/output/playwright/family-book-flow/traces`
- Screenshots: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots`

Commands:
- `uv run pytest tests/test_phase3.py -q`
- `uv run pytest tests/test_pages.py tests/test_api.py -q`
- `tests/ui/playwright-flow-checks.sh`

Result:
- `tests/test_phase3.py`: `25 passed`
- `tests/test_pages.py tests/test_api.py`: `68 passed`
- Playwright flow: `passed`

High-signal tree checks covered by the current flow:
- partnered parents share a generation row and children render below the shared family unit
- two known parents without a partnership row still produce shared family-unit geometry and do not invent a partnership edge
- one person can participate in multiple households without duplication
- adoptive and guardian ties render differently from biological ties
- current and former partnership states render differently
- detached branches receive explicit frames and labels instead of collapsing into unreadable clumps
- graph-edit mode, relationship calculator, inline edits, create/replace/remove relationship flows, and relationship-metadata persistence all pass
- the tree remains usable on mobile without horizontal overflow
- Spanish localization of the changed tree surfaces passes

Verifier quality notes:
- The Playwright checks now wait on persisted state and visible relationship workspaces rather than fixed sleeps and brittle DOM mutation shortcuts.
- The wrapper at `/Users/cheech/code/family-book/tests/ui/playwright_cli.sh` remains fatal on structured Playwright `### Error` output, so the suite cannot print assertion failures and still return green.

## Visual / Persona Lane

Artifacts:
- Desktop browse/read: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-member-view.png`
- Desktop focus/context: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-focus-sidebar.png`
- Desktop quick edit: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-details-admin.png`
- Mobile tree surface: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-mobile.png`
- Spanish tree surface: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-es.png`
- Spanish quick edit: `/Users/cheech/code/family-book/output/playwright/family-book-flow/screenshots/tree-details-es.png`

Review notes:
- `contributing_member` / `find_person_in_tree` / desktop / `en`
  - `tree-member-view.png` shows family units, generation rows, and detached-branch framing on the changed tree surface itself.
  - The updated layout reads as clustered households rather than long misleading spouse/in-law chains.
- `family_admin` / `open_sidebar_and_edit_overview` + `add_relative_from_tree_context` / desktop / `en`
  - `tree-focus-sidebar.png` shows the selected-person context summary and focus controls on the current tree sidebar.
  - `tree-details-admin.png` shows the quick-edit form condensed into grouped sections rather than the former high-noise editor.
- `mobile_first_relative` / `find_person_in_tree` / mobile / `en`
  - `tree-mobile.png` confirms the actual tree surface fits on a narrow viewport without horizontal overflow and keeps the canvas/tools reachable.
- `contributing_member` / `find_person_in_tree` / desktop / `es`
  - `tree-es.png` and `tree-details-es.png` show the changed tree workspace and quick-edit panel localized on-surface, not just via unit tests.

Scope note for visual review:
- No non-person-node screenshot is required for this audit pass because that capability is explicitly deferred out of the shipped sprint scope.

Rubric outcome:
- `hierarchy_and_readability`: pass
- `control_discoverability`: pass
- `mobile_fit`: pass
- `scope_truthfulness`: pass after the explicit `FB-042` de-scope

Persona-critical findings:
- none in the reviewed sprint scope

## Audit Closure

1. Auditor concern: `FB-042` still implied non-person-node delivery
   - Closed by explicitly narrowing the launch scope in:
     - `/Users/cheech/code/family-book/task_packets/FB-042_non_person_nodes_unknown_parents_and_sparse_branch_readability.md`
     - `/Users/cheech/code/family-book/backlog.md`
     - `/Users/cheech/code/family-book/docs/strategy/sprint-board-2026q1.md`
   - The code/model boundary in `/api/tree` remains person-only, so the sprint now documents that truth instead of over-claiming support.

2. Auditor concern: structural/rendered/visual artifacts were stale for the current sprint
   - Closed by regenerating:
     - `/Users/cheech/code/family-book/output/audit/tree-ui-codemap.json`
     - `/Users/cheech/code/family-book/output/playwright/family-book-flow`
     - this updated evidence note
   - The visual lane now references a current mobile tree screenshot (`tree-mobile.png`) on the changed surface instead of a generic home-page artifact.
