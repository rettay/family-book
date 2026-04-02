# Sprint Closeout - S11 Tree as Primary Workspace

## Sprint

- Name: `S11 - Tree as Primary Workspace`
- Status: Closed
- Result: `pass`

## Goal

Make the family tree the main Family Book workspace so members can browse, recognize, edit, and grow the family graph directly from the tree.

## Outcome

Sprint 11 moved the product center of gravity onto the tree. Authenticated users now land on `/tree`, nodes can render profile photos and compact richness counts, and the tree sidebar supports inline person edits plus relationship creation and linking without forcing every routine change through the older full edit form.

During audit follow-up, Builder corrected four regressions introduced by the tree-first shift: login once again respects safe `return_to` redirects, the moments filter stays on `/moments`, tree inline editing can clear existing values, and the `show_names` preference now actually suppresses fallback initials. The browser lane was extended to prove the new tree workspace behavior rather than only the older feed-centric paths.

## Delivered Slices

| Slice | Title | Status |
|---|---|---|
| S11-1 | Tree Identity and Richness | done |
| S11-2 | Inline Tree Editing | done |
| S11-3 | Relationship Workflows and Tree-First Landing | done |

## Verification

- `uv run python -m compileall app tests`
  - result: success
- `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - result: `62 passed`
- `uv run pytest tests/test_moments.py -q`
  - result: `35 passed`
- `uv run pytest tests/test_theme.py -q`
  - result: `5 passed`
- `make test-ui-playwright`
  - result: success
- `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `16 PASS`, `0 FAIL`, `9 WARN`

## Audit Result

- Builder implemented the tree-first workspace on `main`
- Auditor initially identified four blockers:
  - login dropped `return_to`
  - moments filtering still pointed at `/`
  - tree inline edit could not clear existing values
  - `show_names` still leaked fallback initials
- Builder corrected those issues and added regression coverage in page tests and the Playwright lane
- Final audit result: acceptable to close

## Product / Engineering Readout

- The tree is now a working surface, not just a visualization
- Users can identify people more quickly and understand which nodes are richer in family data
- Common edits and relationship-building can happen in tree context instead of always bouncing to CRUD-heavy forms
- The tree-first landing change is now aligned with the rest of the navigation and browser verification

## Residual Debt Carried Into Sprint 12

- CodeMap still reports non-blocking structural warnings around:
  - `app/access_control.py` test/attack-surface coverage
  - `app/schemas.py` critical-path coverage and observability
  - dependency cycle between `app/models/settings.py` and `app/services/theme_service.py`
  - bus-factor and hidden-coupling warnings in central modules
- These residual warnings are now explicitly folded into Sprint 12 alongside Google Maps and Resend work through `FB-014`.

## Recommended Next Sprint

- `S12 - External Integrations and Confidence Hardening`
- Primary packet: `FB-016 External Integrations: Google Maps and Email Delivery`
- Supporting packet: `FB-014 Architecture and Maintainability Hardening`
