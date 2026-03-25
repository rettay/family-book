# Task Packet - FB-021 Tree Graph Editing and Relationship Modeling

## Objective

Turn the family tree into the place where members maintain family structure directly: create new relatives, connect existing people, correct mistaken links, and understand graph changes without leaving the tree workspace for common structural tasks.

## Why / KPI

- Sprint 13 through Sprint 15 made the tree the strongest surface for family enrichment, but the family graph itself still feels harder to edit than the content surrounding it.
- Members can now work around a person from the tree, yet relationship maintenance still feels more mechanical than direct. That is the next usability bottleneck.

Primary KPI:
- increase successful tree-native relationship editing sessions that complete without fallback navigation to older create/edit pages.

Secondary KPI:
- increase successful create-and-connect flows for new relatives from the tree while reducing confusion between creating a new person and linking an existing one.

## Scope

- In scope:
  - direct tree-native editing for parent, child, and partner relationships
  - graph-aware creation-and-connect flows for new people from tree context
  - clearer review, correction, and unlink behavior for existing relationships
  - focused browser, pytest, and CodeMap verification for graph-editing flows
- Out of scope:
  - unrestricted freeform graph canvas editing
  - merge/split identity tooling
  - unrelated longform authoring or storytelling work already improved in Sprint 15
  - broad backend model redesign unrelated to direct graph editing
  - structural cleanup not required for Sprint 16 workflow confidence

## Task Type

- product workflow deepening / structural family-graph editing packet

## Dependencies and Ordering Assumptions

- Best sequenced after Sprint 15 because the tree sidebar and content flows are now strong enough that family-graph editing is the next major workflow gap.
- Should build on the existing relationship model coherently instead of inventing a disconnected tree-only graph-edit layer.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - tree-native add/link flows for parent, child, and partner relationships
  - create-and-connect workflow for a new relative from tree context
  - review/correct/remove relationship behavior from the tree
- Should improve:
  - visual clarity around what graph edit is about to happen
  - post-action confirmation and graph-state confidence
- Must re-run:
  - focused pytest
  - Playwright tree graph-editing flows
  - CodeMap
  - staging/manual review of graph-editing behavior

## Implementation Notes

- Likely files:
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/js/tree.js`
  - `app/static/css/main.css`
  - `app/routes/relationships.py`
  - `app/routes/tree.py`
  - `app/routes/pages.py`
  - `app/schemas.py`
  - `tests/test_pages.py`
  - `tests/test_api.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
  - `make test-ui-playwright`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make the tree the primary workspace for editing and correcting family structure
- Verifier:
  browser review, focused pytest, code review, and staging/manual review
- Reference/oracle:
  current Family Book tree workspace after Sprint 15, the latest product assessment, and the browser evidence lane
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  a member can add, connect, and correct relatives from `/tree` without awkward fallback navigation and with clearer graph-state feedback
- Known failure modes / reward hacks:
  - adding more sidebar controls without making graph edits feel more direct
  - making destructive relationship changes too easy or unclear
  - blurring the distinction between creating a new person and linking an existing one
  - forking the relationship model into a tree-only implementation that behaves differently elsewhere
- Verifiability class:
  `tree-graph-editing-and-relationship-modeling`
- Context policy:
  optimize for direct, understandable family-graph maintenance from the tree without turning the interface into an unsafe freeform editor

## Acceptance Criteria

- [ ] A member can add a parent, child, or partner from the tree without leaving `/tree`.
- [ ] A member can link an existing person into the graph from the tree through a searchable, graph-aware workflow.
- [ ] A member can create a new relative and connect them into the graph as one coherent tree-native task.
- [ ] A member can review, correct, or remove a mistaken relationship from tree context with clear feedback and guardrails.
- [ ] The browser regression lane proves common graph-editing flows from the tree.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Browser verification covers relationship add/link/create/correct flows from the tree
- [ ] The tree remains keyboard reachable and does not regress into a confusing graph-editing surface
