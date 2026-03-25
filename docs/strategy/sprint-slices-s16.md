# Sprint Slices - S16 Tree Graph Editing and Relationship Modeling

## Slice Order

1. `S16-1 Direct Relationship Editing from the Tree`
2. `S16-2 Graph-Aware Person Creation and Connection`
3. `S16-3 Relationship Review, Correction, and Confidence`

## `S16-1 Direct Relationship Editing from the Tree`

### Goal

Make parent, child, and partner edits feel direct from the tree workspace rather than like buried form operations.

### Scope

- improved relationship action affordances in tree context
- better initiate/link flows for core relationship types
- clearer feedback after graph edits complete

### Acceptance Checks

- a member can start and complete common relationship edits from the tree
- relationship-edit affordances are understandable and keyboard reachable
- the workflow avoids forcing users into older edit/create pages for common operations

## `S16-2 Graph-Aware Person Creation and Connection`

### Goal

Let members create a new person and connect them into the family graph as one coherent task from the tree.

### Scope

- context-aware create-and-connect flow from a selected node
- clearer distinction between new-person creation and linking an existing person
- immediate graph update and sidebar review after the new relative is placed

### Acceptance Checks

- a member can create a new parent, child, or partner from the tree
- the new person is connected into the expected graph position
- the post-create tree state is easy to understand without extra navigation

## `S16-3 Relationship Review, Correction, and Confidence`

### Goal

Make existing relationships easier to inspect, correct, and safely remove when they are wrong.

### Scope

- clearer review states for current relationships
- better unlink/correct flows with guardrails
- stronger feedback after relationship correction or removal

### Acceptance Checks

- a member can review current relationships from the tree workspace
- a mistaken relationship can be corrected or removed with clear feedback
- the workflow preserves confidence and does not feel destructive or ambiguous

## Validation Baseline

- `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
- `make test-ui-playwright`
- `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Recommended Builder Order

1. `S16-1`
2. `S16-2`
3. `S16-3`

This order matters because direct relationship editing establishes the interaction model for structural graph changes. Create-and-connect should build on that same model, and relationship correction/removal should only land after the primary add/link flows are clear.
