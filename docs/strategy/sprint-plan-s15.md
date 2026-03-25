# Sprint Plan - S15 Rich Family Storytelling and Multi-Item Authoring

## Sprint

- Name: `S15 - Rich Family Storytelling and Multi-Item Authoring`
- Status: Planned
- Primary packet: `FB-020 Rich Family Storytelling and Multi-Item Authoring`
- Follow-on packet candidates:
  - `FB-017 Post-Integration Structural Cleanup`

## Sprint Goal

Make the tree workspace strong enough for richer family-history capture by supporting better in-tree story composition, grouped media/story workflows, and clearer shared family event authoring.

## Why This Sprint

Sprint 13 and Sprint 14 fixed the biggest context-switching and shallow-workspace problems. The next bottleneck is richer family-history composition. Many real memories are not a single text post or a single upload; they are a story with a few photos, a set of people, and a shared event context. Sprint 15 should make the tree better at capturing those richer units without drifting into a full editor rewrite or a brand-new content model.

## Must-Have Outcomes

- Members can compose richer stories from the tree with more than one attached media item.
- Small photo-and-story sets feel like one memory workflow rather than disconnected uploads.
- Shared family events are easier to author and understand from the tree context.
- The tree sidebar keeps immediate review and follow-up actions in the same workspace after creation.

## Acceptance Criteria

1. A member can create a story from the tree sidebar with multiple media attachments and complete that workflow without leaving `/tree`.
2. The resulting story/media presentation in the tree sidebar makes grouped memory items feel coherent instead of flat and disconnected.
3. A member can author a shared family event from the tree and tag multiple people with feedback that clearly reflects the event’s participants.
4. The sidebar distinguishes clearly between person-specific storytelling and shared-event authoring.
5. Browser, accessibility, and CodeMap baselines remain intact after the richer authoring flows land.

## In Scope

- richer tree-native story composition UX
- support for grouped story/media authoring and review
- improved multi-person tagging and shared-event framing in tree context
- better post-create review states inside the tree sidebar
- focused browser, pytest, and CodeMap verification

## Out of Scope

- full longform document editor
- drag-and-drop bulk archive ingest
- full graph-edit relationship mode on the canvas
- broad backend remodel unrelated to the Sprint 15 workflow goal
- unrelated structural cleanup beyond what is required to keep the new authoring flows confident

## Implementation Order

1. Execute Slice 1: establish richer story composition in the tree context.
2. Execute Slice 2: make multi-item media and story grouping feel coherent after create and during review.
3. Execute Slice 3: improve cross-person event authoring so shared family moments are first-class.
4. Validate through focused pytest, Playwright, CodeMap, and staging/manual review.

## Execution Slices

### Slice 1 - Rich Story Composition in Tree Context

- Goal:
  let members compose richer in-tree stories without bouncing to older fallback pages
- Scope:
  richer story form state, multi-item attachment flow, clearer story review after save
- Must prove:
  users can create a meaningful story cluster from the tree in one continuous workflow

### Slice 2 - Multi-Item Media and Story Grouping

- Goal:
  make a small photo set plus narrative feel like one memory instead of isolated uploads
- Scope:
  grouped display, better post-create browsing, stronger empty/populated states for attached media
- Must prove:
  users can understand and review a grouped story/media memory from the same sidebar context

### Slice 3 - Cross-Person Family Event Authoring

- Goal:
  make shared family events clearer and more first-class than today’s tagged-person afterthought
- Scope:
  clearer about-vs-shared event intent, improved multi-person tagging UX, better feedback on event participants
- Must prove:
  users can create a shared family event in the tree and understand who it belongs to immediately after save

## Proof Obligations

- The sprint must preserve the tree accessibility and keyboard baseline from Sprint 09, Sprint 13, and Sprint 14.
- The sprint must preserve the browser confidence lane for tree-native authoring.
- The richer story workflow must deepen the tree workspace without reintroducing a new dense form wall.
- Multi-item and shared-event workflows must feel like coherent user tasks, not just more fields on the same form.

## Risks To Watch

- adding more attachment controls without improving the authoring experience
- making grouped media visually denser instead of clearer
- introducing shared-event terminology that confuses members about whether a story is personal or collective
- forking tree storytelling from the underlying moments/media model in a way that becomes hard to maintain

## Exit Target

Sprint 15 is complete when Family Book members can use the tree to capture richer family history as one cohesive workflow: write a fuller story, attach a small set of related media, tag the right people, and immediately review the resulting memory without falling back to older disconnected pages.
