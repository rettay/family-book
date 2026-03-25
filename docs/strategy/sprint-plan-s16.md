# Sprint Plan - S16 Tree Graph Editing and Relationship Modeling

## Sprint

- Name: `S16 - Tree Graph Editing and Relationship Modeling`
- Status: Closed
- Primary packet: `FB-021 Tree Graph Editing and Relationship Modeling`
- Follow-on packet candidates:
  - `FB-017 Post-Integration Structural Cleanup`

## Sprint Goal

Make the family tree editable at the graph level so members can create, connect, correct, and understand core family relationships directly from the tree workspace.

## Why This Sprint

Sprint 13 through Sprint 15 turned the tree into a credible workspace for family enrichment, content authoring, and richer storytelling. The remaining product truth is that family structure itself still feels harder to edit than family content around it. Relationship work is possible, but it still leans on sidebar mechanics more than direct graph editing. Sprint 16 should close that gap by making the tree better at structural family maintenance without drifting into an unsafe freeform graph editor.

## Must-Have Outcomes

- Members can initiate relationship changes directly from the tree in a way that feels more visual and direct than the current sidebar-only workflow.
- Members can create a new person and connect them into the family graph in one flow from the tree context.
- Members can review, correct, and remove relationship links more safely and clearly than today.
- The tree remains understandable, keyboard reachable, and confidence-tested after graph-editing controls are introduced.

## Acceptance Criteria

1. A member can add a parent, child, or partner from the tree without falling back to older create/edit pages.
2. A member can link an existing person into the graph from the tree through a searchable, graph-aware workflow.
3. A member can remove or correct a relationship from tree context with clear guardrails and feedback.
4. The graph-editing flows distinguish clearly between creating a new person and linking an existing one.
5. Browser, accessibility, and CodeMap baselines remain intact after the tree graph-editing flows land.

## In Scope

- direct relationship editing from the tree workspace
- graph-aware creation-and-connect flows for new people
- clearer review, correction, and unlink behavior for existing relationships
- improved visual and interaction affordances for graph editing within the current tree model
- focused browser, pytest, and CodeMap verification for graph-editing flows

## Out of Scope

- unrestricted freeform graph canvas editing
- deep GEDCOM-style merge/split tooling
- broad data-model redesign beyond what direct graph editing requires
- unrelated architecture cleanup not required for Sprint 16 confidence
- longform profile or storytelling work already improved in Sprint 15

## Implementation Order

1. Execute Slice 1: direct relationship editing from the tree.
2. Execute Slice 2: create-and-connect flows for new people from tree context.
3. Execute Slice 3: relationship review, correction, and unlink safety flows.
4. Validate through focused pytest, Playwright, CodeMap, and staging/manual review.

## Execution Slices

### Slice 1 - Direct Relationship Editing from the Tree

- Goal:
  make core relationship changes feel direct from the tree rather than sidebar-mechanical
- Scope:
  improved add/link actions for parent, child, and partner relationships with better tree-context affordances
- Must prove:
  users can initiate and complete common relationship edits from the tree without detouring to older fallback surfaces

### Slice 2 - Graph-Aware Person Creation and Connection

- Goal:
  let members create a new person and attach them to the graph as one coherent tree workflow
- Scope:
  context-aware new-person flows from a selected node, with clearer connection intent and post-create graph updates
- Must prove:
  users can create and place a new relative from the tree in one continuous flow

### Slice 3 - Relationship Review, Correction, and Confidence

- Goal:
  make existing relationship structures easier to inspect, correct, and safely remove when needed
- Scope:
  better relationship review states, clearer unlink/correct actions, and stronger feedback/guardrails
- Must prove:
  users can understand and fix a mistaken relationship from tree context without ambiguity

## Proof Obligations

- The sprint must preserve the tree accessibility and keyboard baseline established in Sprint 09 through Sprint 15.
- The sprint must preserve the browser confidence lane for the tree workspace while adding graph-editing coverage.
- The graph-editing flows must feel more direct without becoming visually chaotic or dangerously destructive.
- The distinction between linking an existing person and creating a new person must remain explicit and understandable.

## Risks To Watch

- overcomplicating the tree with too many simultaneous edit affordances
- making destructive relationship changes too easy to trigger
- creating graph-editing rules that are not clearly visible to users
- introducing a second relationship workflow that conflicts with the current sidebar model instead of simplifying it

## Exit Target

Sprint 16 is complete when Family Book members can use the tree to maintain family structure directly: add or connect relatives, correct mistaken links, and understand the resulting graph changes without leaving the tree workspace for common structural tasks.
