# Task Packet - FB-019 Family Content and Relationship Authoring

## Objective

Deepen the tree workspace so Family Book members can do more meaningful family-history work from the tree itself: browse richer content, add or review stories and media in context, and manage relationships with less friction.

## Why / KPI

- Sprint 13 made the tree actionable, but the product assessment still correctly identifies a gap between opening tree workflows and wanting to stay in them.
- The tree now has the right entry points, but some of the resulting experiences are still too shallow to feel like the real operating surface.

Primary KPI:
- increase successful story/media/relationship actions completed from `/tree` without fallback navigation to older CRUD surfaces.

Secondary KPI:
- increase continued in-tree engagement after opening a metric or relationship action instead of bouncing to profile, feed, or edit routes.

## Scope

- In scope:
  - richer moments, stories, and media workspaces from tree metric actions
  - better in-tree review of family content after creation
  - stronger empty-state prompts and next-action guidance
  - improved relationship authoring and maintenance UX in the tree sidebar
  - modest tree-centered reductions in remaining CRUD detours where they directly improve workflow quality
- Out of scope:
  - full graph-editing mode on the canvas
  - full profile-page redesign
  - bulk drag-and-drop media system
  - broad data-model rewrites unrelated to tree workflow quality
  - unrelated structural cleanup not required for Sprint 14 usability goals

## Task Type

- product workflow deepening / usability and authoring packet

## Dependencies and Ordering Assumptions

- Best sequenced after Sprint 13 because the new tree workspace shell and metric actions now exist.
- Should deepen the existing tree interaction model rather than introducing a competing authoring surface.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - metric-driven content browsing in the tree sidebar
  - tree-native story/note/media workflow completeness
  - relationship presentation and authoring quality from the tree
- Should improve:
  - empty-state action quality
  - user understanding of what content exists and what is missing for a selected person
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
  - `app/routes/relationships.py`
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
  make the tree workspace deeper and more self-sufficient for family content and relationship authoring
- Verifier:
  browser review, focused pytest, code review, and staging/manual review
- Reference/oracle:
  current Family Book tree workspace after Sprint 13, the latest product usability assessment, and the browser evidence lane
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  a member can stay in `/tree` to inspect, add, and improve more meaningful family content and relationships than before
- Known failure modes / reward hacks:
  - making metric panels visually richer without improving what users can actually do there
  - adding more controls that recreate the form-wall problem
  - deepening tree flows by forking existing moments/media behavior instead of reusing it coherently
  - making relationship authoring denser rather than clearer
- Verifiability class:
  `tree-content-and-relationship-authoring`
- Context policy:
  optimize for staying in-tree for real family-history work, not just adding more UI

## Acceptance Criteria

- [x] Tree metric panels for moments, stories, and media feel like richer workspaces instead of shallow counters.
- [x] A member can add and then immediately review a story or note from the tree workspace without leaving `/tree`.
- [x] A member can add media from the tree workspace and see a clearer updated media state there.
- [x] Relationship authoring from the tree is easier to understand and maintain than the Sprint 13 baseline.
- [x] Missing content or relationships are represented as action-oriented prompts instead of passive emptiness.

## Definition of Done

- [x] Acceptance criteria satisfied
- [x] Browser verification covers richer metric usage, content creation/review, and relationship authoring from the tree
- [x] The tree remains keyboard reachable and does not regress into another dense form dump
