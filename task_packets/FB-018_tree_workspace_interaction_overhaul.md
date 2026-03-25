# Task Packet - FB-018 Tree Workspace Interaction Overhaul

## Objective

Turn the family tree from a strong visualization into the primary enrichment workspace for Family Book by making the tree sidebar actionable, reducing the current form wall, and letting members add stories, media, and relationships without leaving the tree context.

## Why / KPI

- The tree is now the default landing page, but it still behaves more like a canvas than a working environment.
- Metrics, relationships, and rich family content are visible from the tree, but most meaningful actions still require detours into CRUD-heavy flows.

Primary KPI:
- increase tree-native content creation and editing activity without increasing abandonment from the tree surface.

Secondary KPI:
- reduce navigation away from `/tree` for common person maintenance, relationship linking, and family-history enrichment.

## Scope

- In scope:
  - clickable sidebar metrics for moments, stories, and media
  - progressive-disclosure sidebar structure instead of a stacked form dump
  - tree-native quick add for moments/stories/media
  - inline editing for common person fields in the tree workspace
  - searchable person picker for relationship linking
  - empty-state prompts that turn missing data into invitations to act
- Out of scope:
  - full replacement of the deep profile page
  - connect-two-nodes visual relationship mode on the canvas
  - full drag-and-drop/bulk media system
  - broad profile-page redesign outside the tree workflow
  - unrelated architecture cleanup not required for Sprint 13 usability goals

## Task Type

- product workflow overhaul / usability and interaction packet

## Dependencies and Ordering Assumptions

- Best sequenced after Sprint 12 because the product now has real integrations and a tree-first starting point.
- Should treat the tree sidebar as the main interaction surface rather than recreating the full person edit form in miniature.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - metric interactivity in the tree sidebar
  - sidebar information architecture and progressive disclosure
  - tree-native moment and media creation
  - inline editing of common person fields
  - relationship linking through searchable selection
- Should improve:
  - empty-state prompting for under-documented people
  - staying on `/tree` for common family enrichment work
- Must re-run:
  - focused pytest
  - Playwright tree/sidebar flows
  - CodeMap
  - staging/manual review of the tree workspace

## Implementation Notes

- Likely files:
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/js/tree.js`
  - `app/static/css/main.css`
  - `app/routes/tree.py`
  - `app/routes/moments.py`
  - `app/routes/media.py`
  - `app/routes/persons.py`
  - `tests/test_pages.py`
  - `tests/test_api.py`
  - `tests/test_moments.py`
  - `tests/test_media.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - `make test-ui-playwright`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make the tree a real workspace for family enrichment
- Verifier:
  browser review, focused pytest, code review, and staging/manual review
- Reference/oracle:
  current Family Book tree experience, Sprint 11 tree-first baseline, and the latest product assessment of tree/sidebar usability
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  a member can open a person in the tree and add or edit meaningful family data without bouncing into the old CRUD-heavy flows
- Known failure modes / reward hacks:
  - making metric cards clickable but still routing users away to unrelated pages
  - hiding the form wall behind tabs without improving task flow
  - bolting more forms into the sidebar without reducing cognitive load
  - adding rich actions that weaken keyboard or browser-test confidence
- Verifiability class:
  `tree-workspace-overhaul`
- Context policy:
  optimize for in-tree completion of meaningful work, not just more controls

## Acceptance Criteria

- [x] Tree sidebar metrics for moments, stories, and media are interactive rather than decorative.
- [x] A member can add a story or note for a person directly from the tree sidebar without leaving `/tree`.
- [x] A member can start media upload from the tree sidebar without leaving `/tree`.
- [x] The tree sidebar no longer shows all edit/link/create forms at once; it uses progressive disclosure or sectioning.
- [x] Core person fields can be edited inline from the tree workspace.
- [x] Relationship linking from the tree uses searchable selection instead of a raw full-family dropdown.

## Definition of Done

- [x] Acceptance criteria satisfied
- [x] Browser verification covers metric interaction, inline editing, and in-tree story/media creation
- [x] The deep profile/edit pages remain available as secondary/detail surfaces
