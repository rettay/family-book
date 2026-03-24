# Task Packet - FB-015 Tree as Primary Workspace

## Objective

Turn the family tree into the primary browsing and editing surface for Family Book so members can understand, update, and expand the family graph without bouncing through the current CRUD-heavy forms for every routine action.

## Why / KPI

- The tree is the strongest product surface for Family Book, but it still behaves more like a passive visualization than a working family workspace.
- Users want richer node identity, faster in-context editing, and relationship-building directly from the tree instead of navigating away to simplistic forms.

Primary KPI:
- increase tree-centered family maintenance activity without reducing successful edits.

Secondary KPI:
- reduce navigation away from the tree for common person and relationship updates.

## Scope

- In scope:
  - tree nodes show profile photos when available, with strong fallback behavior
  - tree nodes expose lightweight richness indicators for data density
  - tree sidebar/panel supports direct editing of common person fields
  - tree actions support adding parents, children, partners, and new people in context
  - tree becomes the default post-login landing page for authenticated members
- Out of scope:
  - full replacement of the advanced edit page
  - Google Maps integration
  - Resend email integration
  - full architecture refactor of tree/data code
  - broad redesign of all person editing surfaces

## Task Type

- product-surface enhancement / workflow improvement packet

## Dependencies and Ordering Assumptions

- Best sequenced after Sprint 10 so the tree workspace work lands on top of the improved accessibility, browser confidence, and readability baseline.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - node identity in the tree through photo-first rendering
  - inline editing of common person attributes from the tree sidebar
  - relationship creation and new-person creation from the tree context
  - the tree as the authenticated landing page
- Should improve:
  - richness cues on nodes or in the sidebar for moments/media/story density
  - tree interaction efficiency so users can stay in the tree longer for routine maintenance
- Must re-run:
  - focused browser verification for tree interaction, inline editing, and landing-page behavior
  - targeted pytest for route/template/API behavior touched by the new tree workspace flows
  - CodeMap to confirm no new governance failures are introduced

## Implementation Notes

- Likely files:
  - `app/routes/pages.py`
  - `app/routes/tree.py`
  - `app/routes/persons.py`
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/templates/person.html`
  - `app/static/js/tree.js`
  - `app/static/css/main.css`
  - `tests/test_pages.py`
  - `tests/test_api.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - `make test-ui-playwright`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make the family tree the primary browsing and editing workspace
- Verifier:
  browser review, focused pytest, code review, and staging/manual review
- Reference/oracle:
  current Family Book tree experience and the Sprint 11 product decisions
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  members can stay on the tree for common profile and relationship work instead of navigating away for every edit
- Known failure modes / reward hacks:
  - stuffing too much data into nodes until the tree becomes noisy
  - recreating the full CRUD form inside the sidebar without improving workflow
  - adding relationship actions that only open the old full-page forms
  - breaking tree accessibility or browser confidence while adding richer behavior
- Verifiability class:
  `tree-primary-workspace`
- Context policy:
  optimize for in-context family maintenance, not raw feature count

## Acceptance Criteria

- [ ] Tree nodes render profile photos when available, with clean fallback initials when not.
- [ ] The tree exposes lightweight richness indicators for a person’s family-history depth.
- [ ] Members can edit common person properties from the tree sidebar without navigating to the full edit page.
- [ ] Members can create or link core relationships from the tree context.
- [ ] Authenticated users land on the tree by default after login.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Browser verification covers the new tree-first flows
- [ ] The existing full person-edit page remains available as an advanced/fallback editor
