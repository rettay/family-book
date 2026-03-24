# Sprint Plan - S11 Tree as Primary Workspace

## Sprint

- Name: `S11 - Tree as Primary Workspace`
- Status: Planned
- Primary packet: `FB-015 Tree as Primary Workspace`
- Follow-on packet candidates:
  - `FB-014 Architecture and Maintainability Hardening`
  - external integrations sprint for Google Maps and Resend

## Sprint Goal

Make the family tree the main workspace for Family Book so members can browse people, inspect data richness, make common person edits, and establish relationships directly from the tree.

## Why This Sprint

The tree is the strongest surface in the product and should become the default starting point for family collaboration. Right now it is still too passive: node identity is thin, editing happens elsewhere, and relationship creation pushes users into generic CRUD flows. This sprint focuses the next user-visible improvement on making the tree a working surface rather than just a visualization.

## Must-Have Outcomes

- Tree nodes use profile photos where available and feel more personal.
- The tree shows lightweight signals of how much information exists for a person.
- Common person edits can be made directly from the tree sidebar.
- Parent/child/partner creation or linking can be initiated from the tree context.
- Authenticated users land on the tree instead of the moments feed.

## Acceptance Criteria

1. Tree nodes show a profile photo when one exists and fall back cleanly when one does not.
2. Each person exposed through the tree has a compact richness cue such as moment/media counts or a comparable summary indicator.
3. A member can select a person from the tree and edit common profile fields from the sidebar or panel without leaving the tree.
4. A member can add or link at least parent, child, and partner relationships from the tree context.
5. After authentication, the default landing page for members is `/tree`.
6. The browser regression lane remains green and the tree remains keyboard reachable.

## In Scope

- photo-first node rendering
- fallback node identity design
- compact richness indicators on tree nodes or in the immediate tree context
- tree sidebar or panel editing for common person fields
- relationship actions from the tree context
- default landing-page change from moments to tree
- focused browser and CodeMap verification

## Out of Scope

- Google Maps integration
- Resend email delivery and invite/notification plumbing
- full replacement of the advanced person edit page
- broad redesign of all person or tree surfaces
- architecture-debt cleanup unrelated to the tree workflow

## Implementation Order

1. Execute Slice 1: tree identity and richness cues.
2. Execute Slice 2: inline tree editing.
3. Execute Slice 3: relationship workflows and tree-first landing behavior.
4. Validate with browser checks, focused pytest, and staging/manual review.

## Execution Slices

### Slice 1 - Tree Identity and Richness

- Goal:
  make nodes feel personal and informative without turning the tree into a noisy dashboard
- Scope:
  profile-photo rendering, initials fallback, and compact richness indicators
- Must prove:
  the tree is easier to scan and gives users a better sense of where the richest family data lives

### Slice 2 - Inline Tree Editing

- Goal:
  let members make routine person edits from the tree context
- Scope:
  tree sidebar or panel editing for common person fields, photo handling if practical, and save/update feedback
- Must prove:
  members can perform common edits without being forced into the full advanced form

### Slice 3 - Relationship Workflows and Tree-First Landing

- Goal:
  make the tree the primary operational workspace rather than a secondary visualization
- Scope:
  add/link parent, child, and partner actions from the tree plus default landing-page behavior
- Must prove:
  users can grow and maintain the family graph from the tree itself and arrive there first after login

## Proof Obligations

- The sprint must preserve the accessibility and keyboard improvements from Sprint 09.
- The sprint must preserve the responsive/readability baseline from Sprint 10.
- The tree should become more useful without becoming visually overloaded.
- The work should remain focused on tree-centered browsing and editing, not on external integrations.

## Risks To Watch

- packing too much data into nodes and making the tree harder to read
- recreating the full CRUD editor in the sidebar instead of building a better workflow
- implementing relationship actions that still rely on awkward page-to-page navigation
- weakening keyboard or browser-test coverage while adding richer tree interactions

## Exit Target

Sprint 11 is complete when Family Book users can arrive on the tree first, understand who has richer data, make common profile changes in context, and establish core relationships directly from the tree.
