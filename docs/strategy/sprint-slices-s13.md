# Sprint Slices - S13 Tree Workspace 2.0

## Slice Sequence

### S13-1 Metric Actions and Sidebar Structure

Status: `planned`

- Objective:
  turn the tree sidebar into a comprehensible workspace instead of a form wall
- Scope:
  clickable metrics, metric-driven content panels, and progressive-disclosure sidebar structure
- Deliverable:
  a tree sidebar where users can understand available actions and drill into moments/media/details intentionally
- Verification:
  browser checks on metric actions, sidebar organization, and keyboard flow

### S13-2 Tree-Native Stories, Media, and Inline Editing

Status: `planned`

- Objective:
  let members enrich a person directly from the tree context
- Scope:
  quick-add story or note, media upload entry point, and inline editing of common person fields
- Deliverable:
  users can do meaningful person enrichment without leaving `/tree`
- Verification:
  browser checks plus focused pytest on tree-sidebar create/edit flows

### S13-3 Searchable Relationship Linking and Empty-State Prompts

Status: `planned`

- Objective:
  make missing family data easier to complete from the tree itself
- Scope:
  searchable person picker for relationship linking plus action-oriented empty states for missing stories/media/relationships
- Deliverable:
  tree relationship workflows that scale better and guide the user toward the next useful action
- Verification:
  browser checks on relationship linking and empty-state interaction paths

## Slice Rules

- Keep the sprint centered on the tree as the primary work surface.
- Prefer progressive disclosure and task flow over exposing all controls at once.
- Reuse the existing moments/media/person APIs where practical instead of inventing disconnected flows.
- Keep the deep profile and edit pages as secondary/detail surfaces, not primary workflow entry points.

## Recommended Builder Order

1. `S13-1`
2. `S13-2`
3. `S13-3`

## PM Note

This sprint should make Family Book feel like a place where users work directly in the family graph. The right result is not “more controls in the sidebar,” it is a calmer, more actionable tree workspace that lets users enrich family records in context.
