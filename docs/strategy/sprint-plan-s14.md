# Sprint Plan - S14 Family Content and Relationship Authoring

## Sprint

- Name: `S14 - Family Content and Relationship Authoring`
- Status: Closed
- Primary packet: `FB-019 Family Content and Relationship Authoring`
- Follow-on packet candidates:
  - `FB-017 Post-Integration Structural Cleanup`

## Sprint Goal

Make the tree workspace feel complete enough for everyday family-history work by turning metric panels into richer content surfaces, keeping more story/media interaction in-tree, and improving relationship authoring beyond the current basic link/create model.

## Why This Sprint

Sprint 13 made the tree actionable, but the product assessment is right that some of the new surfaces still feel like thin wrappers around existing data rather than places users want to stay. Counts open, but the resulting experiences are still narrow. Relationship linking works, but it is not yet expressive or graceful enough to feel like a durable family-graph workflow. Sprint 14 should deepen those workflows without trying to jump straight to full visual graph editing.

## Must-Have Outcomes

- Metric actions open richer tree-native content browsing, not just shallow summaries.
- Members can add or review stories, notes, and media from the tree workspace with less need to bounce to profile or feed pages.
- Relationship authoring in the tree supports clearer creation, linking, and maintenance flows.
- Empty states in the tree workspace become prompts to add meaningful family history, not just blank containers.

## Acceptance Criteria

1. Clicking a person’s moments, stories, or media metrics in the tree opens a richer in-tree workspace that lets members browse recent relevant content, not just see a thin stub state.
2. A member can add at least one meaningful story or note and immediately review it from the tree workspace without leaving `/tree`.
3. A member can add media from the tree workspace and see it represented there with a clearer post-upload state.
4. Relationship authoring from the tree supports both finding the right person quickly and understanding existing relationships well enough to maintain them confidently.
5. Under-documented people show useful prompts that directly guide the next meaningful action.
6. The browser regression lane remains green and the tree workspace stays keyboard reachable.

## In Scope

- richer sidebar panels for moments, stories, and media
- improved in-tree review of recently created or existing content
- stronger empty-state prompts and next-action guidance
- relationship authoring UX improvements for create/link/maintain flows
- modest reductions in remaining CRUD detours where they materially help tree workflow quality
- focused browser, pytest, and CodeMap verification

## Out of Scope

- full connect-two-nodes graph editing mode on the canvas
- full profile-page redesign
- broad rewrite of the moments or media backend models
- drag-and-drop bulk media system
- unrelated architecture cleanup not required for the tree-authoring workflow

## Implementation Order

1. Execute Slice 1: deepen metric workspaces and sidebar content browsing.
2. Execute Slice 2: complete tree-native content authoring loops for stories, notes, and media.
3. Execute Slice 3: improve relationship authoring, maintenance, and missing-data prompts.
4. Validate through focused pytest, Playwright, CodeMap, and staging/manual review.

## Execution Slices

### Slice 1 - Rich Metric Workspaces and Content Browsing

- Goal:
  make tree metrics feel like doors into useful content workspaces rather than summarized counters
- Scope:
  richer moments/stories/media panels, better recent-content browsing, clearer section states
- Must prove:
  users can open a metric and meaningfully inspect or continue work from there

### Slice 2 - Tree-Native Content Authoring Completion

- Goal:
  make the story/note/media flows in the tree feel complete enough for routine use
- Scope:
  better in-tree creation, post-create review state, and less bouncing into fallback pages
- Must prove:
  users can add and then immediately work with family content from the same tree context

### Slice 3 - Relationship Authoring UX and Cleanup

- Goal:
  make relationship creation and maintenance clearer and more scalable
- Scope:
  clearer existing-relationship presentation, better search/add flows, action-oriented empty states
- Must prove:
  users can understand and improve a person’s relationship graph without a confusing form dump

## Proof Obligations

- The sprint must preserve the tree accessibility and keyboard baseline from Sprint 09 and Sprint 13.
- The sprint must preserve the browser confidence lane added in S08 and expanded in later sprints.
- The sprint must deepen the tree workspace without reintroducing the old “form wall” problem.
- New prompts and content panels must clarify what to do next instead of just surfacing more controls.

## Risks To Watch

- adding more panels without making the content meaningfully richer
- turning the tree sidebar into a denser interface instead of a clearer one
- adding authoring affordances that fork existing moments/media behavior
- relationship improvements that look better visually but remain hard to understand at family scale

## Exit Target

Sprint 14 is complete when Family Book users can stay in the tree for a broader set of real family-history tasks: opening content-rich metric views, adding and reviewing stories or media, and improving a person’s relationships with much less need to fall back to the older CRUD-heavy routes.
