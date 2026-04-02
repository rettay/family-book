# Sprint Slices - S14 Family Content and Relationship Authoring

## Slice Order

1. `S14-1 Rich Metric Workspaces and Content Browsing`
2. `S14-2 Tree-Native Content Authoring Completion`
3. `S14-3 Relationship Authoring UX and Cleanup`

## `S14-1 Rich Metric Workspaces and Content Browsing`

### Goal

Make the tree sidebar metrics feel like real workspaces by improving what members see after they click into moments, stories, and media.

### Scope

- richer story and moment browsing in the sidebar
- clearer recent content lists and section states
- better media workspace presentation after open and after upload
- stronger empty and populated states for metric-driven panels

### Acceptance Checks

- clicking a metric opens a sidebar panel with enough content depth to keep the user in-tree
- content panels are still keyboard reachable and do not regress the sidebar interaction model
- populated and empty states both make it obvious what to do next

## `S14-2 Tree-Native Content Authoring Completion`

### Goal

Make the in-tree content creation flows feel complete rather than provisional.

### Scope

- improve story/note creation feedback and immediate review behavior
- improve media upload feedback and post-upload presentation
- reduce unnecessary redirects or page escapes for common tree-content actions

### Acceptance Checks

- a member can add a story or note from the tree and immediately review it there
- a member can add media from the tree and immediately see the updated workspace state
- browser regression coverage proves these flows without leaving `/tree`

## `S14-3 Relationship Authoring UX and Cleanup`

### Goal

Make relationship creation and maintenance from the tree clearer, more scalable, and less mechanical.

### Scope

- improve relationship presentation in the sidebar
- refine searchable add/link flows
- add action-oriented prompts where relationship data is missing
- reduce the feeling of a relationship form dump while preserving capability

### Acceptance Checks

- a member can understand current parents/children/partners quickly from the sidebar
- a member can add or link a relative with less confusion than the Sprint 13 baseline
- missing relationships are surfaced as invitations to act, not just empty gaps

## Validation Baseline

- `uv run pytest tests/test_pages.py tests/test_api.py tests/test_moments.py tests/test_media.py -q`
- `make test-ui-playwright`
- `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Recommended Builder Order

1. `S14-1`
2. `S14-2`
3. `S14-3`

This order matters because the metric panels define the workspace shell for the rest of the sprint. Content authoring should improve after the workspace destinations are credible, and relationship cleanup should land once the broader sidebar structure is stable.
