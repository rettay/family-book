# Sprint Slices - S11 Tree as Primary Workspace

## Slice Sequence

### S11-1 Tree Identity and Richness

Status: `planned`

- Objective:
  make the tree more personal and informative at a glance
- Scope:
  node photos, fallback identity rendering, and compact richness indicators
- Deliverable:
  a tree where people are easier to recognize and high-value records are easier to spot
- Verification:
  browser checks and focused UI review on tree rendering and node density

### S11-2 Inline Tree Editing

Status: `planned`

- Objective:
  move routine person editing into the tree workflow
- Scope:
  tree sidebar or panel editing for common fields, inline save behavior, and clear update feedback
- Deliverable:
  members can update common person details without leaving the tree
- Verification:
  browser checks plus focused pytest on the edited fields and tree update path

### S11-3 Relationship Workflows and Tree-First Landing

Status: `planned`

- Objective:
  make the tree the operational center of the product
- Scope:
  add/link relationship flows from the tree and change the authenticated default landing page to `/tree`
- Deliverable:
  users can expand the graph from the tree itself and reach that surface first after login
- Verification:
  browser checks on login landing behavior and relationship creation flows

## Slice Rules

- Keep the sprint centered on the tree as a workspace, not a passive diagram.
- Prefer compact, high-signal node enhancements over visually noisy density.
- Keep the full edit page available as a fallback rather than trying to eliminate it in one sprint.
- Do not fold Google Maps or email delivery into this sprint.

## Recommended Builder Order

1. `S11-1`
2. `S11-2`
3. `S11-3`

## PM Note

This sprint should make Family Book feel more like a real family workspace by putting the tree at the center of day-to-day use. The right result is a more capable tree, not a giant mixed integration sprint.
