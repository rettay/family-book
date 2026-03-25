# Sprint Plan - S13 Tree Workspace 2.0

## Sprint

- Name: `S13 - Tree Workspace 2.0`
- Status: Closed
- Primary packet: `FB-018 Tree Workspace Interaction Overhaul`
- Follow-on packet candidates:
  - `FB-017 Post-Integration Structural Cleanup`

## Sprint Goal

Make the tree the place where members actually enrich family records by turning metrics into actions, restructuring the sidebar into a usable workspace, and supporting tree-native stories, media, inline edits, and relationship linking.

## Why This Sprint

Family Book now has a credible tree-first starting point, but the product assessment is right: the tree still behaves like an attractive visualization with a bolted-on form stack. Users can see where data is missing, but they cannot fix it naturally from that context. Sprint 13 should close the gap between “tree as inspiration” and “tree as working surface.”

## Must-Have Outcomes

- Tree sidebar metrics become actionable entry points instead of static counts.
- The tree sidebar becomes sectioned or tabbed with progressive disclosure instead of showing every edit/link/create block at once.
- Members can add a story or note from the tree sidebar without leaving `/tree`.
- Members can initiate media upload from the tree sidebar without leaving `/tree`.
- Members can edit common person fields inline from the tree workspace.
- Relationship linking from the tree uses searchable selection instead of raw full-family dropdowns.

## Acceptance Criteria

1. Clicking tree sidebar metrics for moments, stories, or media opens actionable content or creation states rather than dead display cards.
2. A member can add a story or note for a person directly from the tree sidebar and see the result without leaving `/tree`.
3. A member can start media upload from the tree sidebar without leaving `/tree`.
4. The tree sidebar uses progressive disclosure so edit fields, relationship actions, and create/link flows are not all visible at once.
5. Common person fields such as name, nickname, dates, branch, and bio can be edited inline from the tree workspace.
6. Relationship linking from the tree uses a searchable picker instead of a raw full-family `<select>` list.
7. The browser regression lane remains green and the tree workspace stays keyboard reachable.

## In Scope

- clickable metric cards or metric actions in the tree sidebar
- sidebar tabs, sections, or collapsible workspace structure
- tree-native quick-add for moments/stories/media
- inline editing for common person fields in the tree sidebar
- searchable person picker for relationship linking
- empty-state prompts for under-documented people where they directly support action
- focused browser and CodeMap verification

## Out of Scope

- connect-two-nodes visual graph editing mode
- full drag-and-drop or bulk media overhaul
- full deep-profile redesign
- replacing the profile page as the detailed reading surface
- broader architecture cleanup unrelated to the tree workspace

## Implementation Order

1. Execute Slice 1: metric actions and sidebar information architecture reset.
2. Execute Slice 2: tree-native content creation and inline editing.
3. Execute Slice 3: searchable relationship workflows and empty-state action prompts.
4. Validate through focused pytest, browser checks, CodeMap, and staging/manual review.

## Execution Slices

### Slice 1 - Metric Actions and Sidebar Structure

- Goal:
  make the sidebar feel like a workspace instead of a form dump
- Scope:
  clickable metrics plus tabs/sections/collapsible organization
- Must prove:
  users can understand what to do next from the tree without scanning a wall of inputs

### Slice 2 - Tree-Native Stories, Media, and Inline Editing

- Goal:
  let members enrich a person directly from the tree context
- Scope:
  quick-add story/note, media entry point, and inline editing for common fields
- Must prove:
  a user can do meaningful person enrichment without leaving `/tree`

### Slice 3 - Searchable Relationship Linking and Empty-State Prompts

- Goal:
  make missing family data easier to fix from the tree itself
- Scope:
  searchable person picker for relationship linking plus action-oriented empty states
- Must prove:
  relationship workflows scale beyond tiny families and missing-data surfaces invite action

## Proof Obligations

- The sprint must preserve the accessibility and keyboard baseline closed in Sprint 09.
- The sprint must preserve the readability and responsive improvements from Sprint 10.
- The tree must become more actionable without turning into a noisy admin panel.
- The work should keep users in `/tree` for common actions instead of adding new navigation detours.

## Risks To Watch

- replacing one form wall with a tabbed form wall that still feels heavy
- metric click paths that still bounce users into unrelated pages
- adding content creation controls that fragment the existing moments/media flows
- building a searchable relationship picker that is visually better but keyboard worse

## Exit Target

Sprint 13 is complete when Family Book users can open a person in the tree, understand what data exists or is missing, add stories or media, edit common fields, and link relatives from that same workspace with much less context switching.
