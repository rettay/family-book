# Task Packet - FB-035 Couple-First Tree Layout and Generation Clarity

## Objective

Make the tree immediately legible by rendering couples as same-generation family units, clarifying generation structure visually, and preventing partnership or in-law relationships from reading like ancestry.

## Why / KPI

- Recent production debugging showed the current tree can be technically correct in data while still feeling wrong in presentation because spouses and in-laws are easy to misread as parents or children.
- Family Book's primary experience promise is that a member opens the tree and understands their family right there; when generation and couple semantics are ambiguous, CFLSR drops because users stop trusting what they see.

Primary KPI:
- increase correct first-pass interpretation of immediate family structure on `/tree`.

Secondary KPI:
- reduce support/debug loops caused by "the data is right but the tree looks wrong."

## Scope

- In scope:
  - couple-first layout rules so spouses/partners share the same generation row
  - shared child-anchor treatment when two known parents are present
  - generation-band or row-level visual scaffolding that makes parent/child levels obvious
  - clearer visual distinction between parent-child edges and partnership edges
  - explicit handling so in-law and partner relationships cannot visually impersonate ancestry
- Out of scope:
  - broad visual redesign of the entire tree sidebar
  - drag-and-drop graph editing
  - GEDCOM or relationship-model schema changes
  - timeline, wiki, or map redesign

## Task Type

- member-facing UI semantics / layout correctness packet

## Dependencies and Ordering Assumptions

- Should be treated as the first packet in this tree-interpretability sequence because later UX refinements depend on the tree being structurally trustworthy.
- May build on the recent partner-generation renderer fix, but should not assume that fix alone is sufficient for couple-first readability.

## Changed Surfaces

- `tree_workspace`

## Target Personas

- Primary personas:
  - `contributing_member`
  - `family_admin`
- Safety personas:
  - `mobile_first_relative`

## Required Scenario IDs

- `find_person_in_tree`
- `open_sidebar_and_edit_overview`
- `add_relative_from_tree_context`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - spouse/partner row alignment
  - shared-parent child placement
  - generation readability
  - relationship-line semantics
- Should improve:
  - root/focus orientation if needed to avoid generation ambiguity
  - small-screen readability of family units
- Must re-run:
  - deterministic tree browser assertions against seeded multi-generation families
  - structural review of the tree layout code path
  - visual/persona review against at least one couple-with-children case and one in-law case

## Implementation Notes

- Likely files:
  - `app/static/js/tree.js`
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/css/main.css`
  - `app/routes/tree.py`
  - `tests/ui/playwright_seed.py`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_pages.py`
  - `tests/test_api.py`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_api.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make tree relationship semantics visually trustworthy
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  `/Users/cheech/code/family-book/foundation/UX_NORTH_STAR.md`
  current production misread cases involving spouse/child and in-law confusion
  expected family-graph semantics from `/api/tree`
- Expected evidence:
  screenshots, replay, and DOM/geometry assertions showing couples aligned on one generation row and children descending from the correct family unit
- Known failure modes / reward hacks:
  - partners are technically on the same `y` value but still visually read as detached from the child anchor
  - line styling changes mask deeper layout ambiguity
  - happy-path seeds pass while asymmetric real families still misread
  - desktop-only fixes leave mobile family-unit readability broken
- Verifiability class:
  `bounded-judgment`
- Context policy:
  keep attention on interpretability of real family structures, not pure graph-theory elegance

## UI Review Requirements

- Structural oracle:
  - CodeMap review over tree layout, relationship rendering, and template/CSS wiring
  - verify partnership semantics influence rendered hierarchy rather than appearing as decorative afterthoughts
- Browser oracle:
  - seeded assertions proving:
    - spouses/partners share a generation row
    - children render below their known parents
    - in-law relationships do not introduce parent-child geometry
    - mobile still shows legible family-unit grouping
- Visual/persona oracle:
  - Folio or equivalent browser walkthrough for:
    - `contributing_member` on desktop reading a couple with children
    - `family_admin` on desktop checking a more complex in-law case
    - `mobile_first_relative` on mobile confirming the same family unit is still understandable
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for tree family-unit states
  - persona-backed replay plus screenshot notes for desktop and mobile
- Expected visual states:
  - spouses appear lateral to each other, not stacked as ancestor/descendant
  - child lines visually descend from the couple unit or clearly from a single known parent
  - parent-child lines and partner lines are distinguishable at a glance
  - generation bands or equivalent scaffolding make row meaning obvious

## Acceptance Criteria

- [ ] A two-parent couple with children renders with both partners on the same generation row.
- [ ] Children of a known couple descend from a shared family-unit anchor or equally clear two-parent structure, not from a misleading single-spouse position.
- [ ] An in-law case does not visually imply a biological parent-child relationship where none exists.
- [ ] Parent-child edges and partnership edges are visually distinct enough that a first-time viewer can tell them apart quickly.
- [ ] Desktop and mobile tree views preserve the improved generation semantics without overlapping or clipped family-unit presentation.

## Risk and Verification Notes

- Complexity hotspots:
  - mixed parent/partner graph traversal
  - asymmetric families with one known parent
  - detached subtrees and multiple marriages
- Likely shallow-pass failure modes:
  - only the seeded happy path looks correct
  - couples align but shared child anchors still mislead
  - line crossings or compact mobile layout reintroduce confusion
- Required verification depth:
  - geometry assertions plus visual review
  - at least one wrong-variant check for in-law misrendering
- Sufficient discriminative power means:
  the packet should fail review if a human can still plausibly misread spouse or in-law placement as ancestry.

## Execution Budget

- Builder may explore:
  - couple-node or shared-anchor layout strategies
  - subtle generation-band treatments
  - CSS/JS approaches that preserve current tree interactivity
- Builder must escalate if:
  - the required layout semantics imply a material API or schema redesign
  - performance degrades meaningfully on larger trees
- Material scope drift:
  - redesigning unrelated person-sidebar flows
  - adding new relationship types or schema changes
- Proof obligations before review:
  - production-style misread cases are represented in test evidence
  - browser and visual evidence agree that family semantics are clearer

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 tree-interpretation regressions remain in the affected layout paths
- [ ] The tree remains the primary workspace while becoming easier to read correctly
