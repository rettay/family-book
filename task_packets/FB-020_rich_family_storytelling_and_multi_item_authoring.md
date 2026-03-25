# Task Packet - FB-020 Rich Family Storytelling and Multi-Item Authoring

## Objective

Deepen the tree workspace so Family Book members can capture richer family history in one place: compose better stories with multiple attachments, represent small photo/story sets as one memory cluster, and author shared family events that belong to more than one person.

## Why / KPI

- Sprint 13 and Sprint 14 made the tree a credible workspace, but the current authoring model still treats many memories as single-item actions instead of one richer family-history unit.
- Users can now stay in the tree for more work, but story/media creation still feels fragmented when the memory involves multiple photos, multiple people, or a richer narrative arc.

Primary KPI:
- increase successful in-tree story and event creation sessions that include multiple attachments or multiple tagged people without fallback navigation to older routes.

Secondary KPI:
- increase the number of meaningful tree-authored content items that are immediately reviewable from the same sidebar context after creation.

## Scope

- In scope:
  - richer tree-native story composition with multiple media attachments
  - better grouped presentation of story-linked media or small memory clusters
  - improved tagged-people and shared-event authoring in the tree workspace
  - clearer distinction between person-specific stories and shared family events
  - focused browser, pytest, and CodeMap verification for the richer authoring flows
- Out of scope:
  - full document-style longform editor
  - drag-and-drop bulk archival ingest beyond small grouped attachments
  - broad rewrite of the moments or media backend beyond what this workflow requires
  - visual graph-edit mode for relationships
  - unrelated structural cleanup not required for Sprint 15 workflow confidence

## Task Type

- product workflow deepening / family-history authoring packet

## Dependencies and Ordering Assumptions

- Best sequenced after Sprint 14 because the tree sidebar now behaves like a richer workspace and relationship/context flows are clearer.
- Should extend the existing moments/media model coherently instead of creating a second storytelling surface.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - in-tree story composition with more than one media item
  - representation of small media/story groups as one memory workflow
  - authoring of shared family events with multiple tagged people
- Should improve:
  - immediate post-create review in the tree sidebar
  - clarity around whether a story is about one person or a shared event
- Must re-run:
  - focused pytest
  - Playwright tree/sidebar authoring flows
  - CodeMap
  - staging/manual review of rich tree storytelling

## Implementation Notes

- Likely files:
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/js/tree.js`
  - `app/static/css/main.css`
  - `app/routes/moments.py`
  - `app/routes/media.py`
  - `app/routes/tree.py`
  - `app/routes/pages.py`
  - `app/schemas.py`
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
  make the tree workspace capable of richer, grouped, multi-person family-history authoring
- Verifier:
  browser review, focused pytest, code review, and staging/manual review
- Reference/oracle:
  current Family Book tree workspace after Sprint 14, the latest product assessment, and the browser evidence lane
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  a member can create and immediately review richer stories or shared events from `/tree` without awkward fallback navigation
- Known failure modes / reward hacks:
  - adding more fields to the sidebar without making authoring feel more coherent
  - supporting multiple uploads but still forcing the user through one-item-at-a-time review
  - treating shared events as just tagged-person afterthoughts rather than first-class authoring intent
  - forking existing story/media behavior into a disconnected tree-only implementation
- Verifiability class:
  `rich-tree-storytelling-and-multi-item-authoring`
- Context policy:
  optimize for capturing real family memories as cohesive units, not just more form inputs

## Acceptance Criteria

- [x] A member can create a tree-native story that includes multiple media items without leaving `/tree`.
- [x] Story-linked media is presented as a coherent grouped memory in the tree workspace rather than a flat disconnected upload list.
- [x] A member can author a shared family event from the tree and attach multiple tagged people with clear feedback about who the event involves.
- [x] The tree sidebar makes it obvious whether the current authoring flow is person-specific or a broader family event.
- [x] The browser regression lane proves richer story creation, multi-item attachment, and cross-person event visibility from the tree.

## Definition of Done

- [x] Acceptance criteria satisfied
- [x] Browser verification covers rich story composition, grouped media attachment, and shared-event authoring from the tree
- [x] The tree remains keyboard reachable and does not regress into a dense multi-step form wall
