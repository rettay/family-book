# Sprint Plan - S03 Timeline and Family Moments Expansion

## Sprint

- Name: `S03 - Timeline and Family Moments Expansion`
- Status: Closed
- Primary packet: `FB-006 Timeline and Family Moments Expansion`

## Sprint Goal

Make Family Book feel like a living family archive by improving stories, notes, and multi-person moments across the home feed and person timelines.

## Why This Sprint

Sprint 01 established collaboration. Sprint 02 established discovery. The next gap is narrative usefulness: the app still needs a more trustworthy, expressive timeline layer so members can actually preserve family history over time instead of only managing records and relationships.

## Must-Have Outcomes

- Members can create richer timeline entries for stories, notes, and milestones.
- Tagged multi-person events show up in the right person timelines.
- Home feed and person-level timeline surfaces stay aligned on visibility and ordering.
- Timeline behavior remains consistent with the flat-family collaboration model.

## Acceptance Criteria

1. A logged-in member can create a richer story/note moment and see it persisted. `done`
2. A second logged-in member can see the shared moment in the expected timeline surface. `done`
3. A tagged person appears in person-specific timeline results even when they are not the posting owner. `done`
4. Home feed ordering and person timeline ordering are consistent for the same visible events. `done`
5. Focused tests prove tagged-person timeline correctness and shared visibility behavior. `done`

## In Scope

- Timeline query and ordering hardening
- Richer moment authoring for stories/notes
- Tagged multi-person event support and display
- Home feed and person timeline integration
- Focused tests for timeline and tagged-person correctness

## Out of Scope

- Version history and revert workflow
- Moderation queue or editorial approvals
- External news/social-media ingestion
- AI-generated timeline content
- Encryption hardening work
- Theme customization

## Implementation Order

1. Execute Slice 1: timeline query and ordering hardening.
2. Execute Slice 2: rich moments authoring and tagged events.
3. Execute Slice 3: home/person timeline integration.
4. Validate the combined sprint outcomes with focused tests and UI evidence.

## Execution Slices

### Slice 1 - Timeline Query and Ordering Hardening

- Goal:
  make timeline retrieval correct and deterministic across feed contexts
- Scope:
  tagged-person queries, ordering, pagination expectations, shared visibility alignment
- Must prove:
  tagged people can discover relevant moments in person-specific timelines
- Suggested acceptance checks:
  older tagged moments are still queryable
  home and person feeds agree on visible results for the same member

### Slice 2 - Rich Moments Authoring and Tagged Events

- Goal:
  expand the usefulness of moments beyond minimal text posts
- Scope:
  richer story/note authoring, tagged people support, multi-person event persistence
- Must prove:
  authoring changes are real persisted behavior, not UI-only structure
- Suggested acceptance checks:
  new content fields survive create/read cycles
  tagged multi-person moments can be rendered in the API and UI

### Slice 3 - Home and Person Timeline Integration

- Goal:
  make the richer timeline visible in the product's core reading surfaces
- Scope:
  home feed rendering, person-page timeline rendering, moment-card consistency
- Must prove:
  users can discover the same shared memory in the right places without inconsistent behavior
- Suggested acceptance checks:
  person page shows relevant tagged moments
  home feed and person feed render the same moment coherently

## Proof Obligations

- Tagged-person timeline behavior is implemented in the data/query layer, not faked in templates.
- Home and person timeline surfaces use the same visibility rules.
- Rich moments remain collaborative family content, not owner-only records.
- Sprint scope stays away from moderation/version-history work.

## Risks To Watch

- Tagged moments saved correctly but retrieved incorrectly
- Timeline work expanding into a full editorial/versioning system
- Home and person timeline surfaces drifting into different logic paths
- Adding fields without improving discoverability in the actual product surfaces

## Exit Target

Sprint 03 is complete when Family Book supports meaningful shared family-history entries that can be created, discovered, and revisited through timeline surfaces instead of existing only as isolated data records.

## Closeout Result

- Exit result: `pass`
- Builder implementation landed on `codex/shared-collaboration-reset`
- Auditor defects were fixed and follow-up validation completed
- Focused verification at closeout:
  - `uv run pytest tests/test_moments.py tests/test_media.py tests/test_api.py -q`
  - result: `92 passed`
  - `uv run pytest tests/test_phase1_edge_cases.py -q`
  - result: `15 passed, 1 xfailed`
  - `uv run python -m compileall app`
  - result: success
- Browser evidence at closeout:
  - `make test-ui-playwright`
  - result: success
  - screenshots written to `/Users/cheech/code/family-book/output/playwright/family-book-flow`
