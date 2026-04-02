# Task Packet - FB-039 Genealogy Graph Architecture and Family-Unit Layout Foundation

## Objective

Replace the current person-only tree placement approach with a genealogy-grade layout foundation that uses explicit family-unit or union semantics so direct relatives cluster correctly and in-law or spouse relationships cannot read like ancestry.

## Why / KPI

- Recent live debugging confirms the database is often correct while the rendered tree is still misleading because the layout engine treats partnerships as secondary decoration instead of structural constraints.
- CFLSR falls when a member opens `/tree`, sees a false-looking relationship, and no longer trusts the workspace enough to contribute.

Primary KPI:
- improve first-pass correctness of tree interpretation for multigenerational families on `/tree`.

Secondary KPI:
- reduce support/debug loops where relationship data is correct but the rendered graph looks wrong.

## Scope

- In scope:
  - select and implement the launch-direction layout model for multigenerational genealogy graphs
  - move the renderer toward explicit family-unit or union-node semantics rather than raw person-to-person edge packing
  - generation-layer assignment that respects parents, children, spouses, and co-parents
  - coordinate assignment that clusters direct relatives into readable households
  - removal of misleading direct geometry between blood relatives and in-laws
- Out of scope:
  - adoption, foster, guardian, and step semantics beyond what is required for the new foundation to support them later
  - pets or institutions as node types
  - broad redesign of the sidebar or non-tree surfaces
  - print/export or alternative view modes

## Task Type

- member-facing tree architecture and layout packet

## Dependencies and Ordering Assumptions

- This is the first packet in the sprint. Later packets assume the tree has an explicit family-unit layout model.
- Builder should treat Sugiyama-style layered genealogy layout with union/family nodes as the default direction unless implementation evidence shows a narrower equivalent is sufficient.
- If the renderer cannot achieve trustworthy clustering without introducing explicit union nodes in the client data model, builder should implement that change rather than layering more heuristics onto the current approach.

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
  - spouse and co-parent clustering
  - parent-child household grouping
  - in-law non-ancestry rendering correctness
  - detached branch placement so separate components remain readable
- Should improve:
  - large-family spacing stability
  - root/focus behavior so root choice does not distort household meaning
- Must re-run:
  - deterministic browser assertions over multigenerational seeded families
  - structural review of the tree layout architecture
  - visual/persona review for one straightforward family and one complex in-law branch

## Implementation Notes

- Likely files:
  - `app/static/js/tree.js`
  - `app/templates/tree.html`
  - `app/static/css/main.css`
  - `app/routes/tree.py`
  - `app/schemas.py`
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
  implement a genealogy-grade family-unit layout foundation for the tree
- Verifier:
  structural review, deterministic browser geometry checks, and visual/persona review
- Reference/oracle:
  `/Users/cheech/code/family-book/foundation/UX_NORTH_STAR.md`
  prod relationship cases where spouses or in-laws currently read like ancestors or children
  expected family semantics from `/api/tree`
- Expected evidence:
  geometry assertions, screenshots, and replay showing households rendered as local clusters instead of long misleading lateral chains
- Known failure modes / reward hacks:
  - partner edges still exist visually but do not participate in placement
  - family units are added in DOM but children still descend from the wrong visual center
  - root-node choice still drags unrelated in-laws into a bloodline-looking chain
  - desktop looks acceptable while mobile compresses households back into ambiguity
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prioritize trustworthy family interpretation over preserving the current renderer shape

## UI Review Requirements

- Structural oracle:
  - CodeMap review over tree layout, relationship rendering, and any new family-unit abstractions
  - confirm that the chosen layout model is structural rather than purely stylistic
- Browser oracle:
  - seeded assertions proving:
    - spouses and co-parents share the intended generation layer
    - children render below the correct family unit
    - in-law cases do not produce false direct parent-child geometry
    - detached components stay readable instead of collapsing into one row
    - mobile still preserves household grouping
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough reading a married couple with children
  - `family_admin` desktop walkthrough reading a branch with siblings, spouses, and in-laws
  - `mobile_first_relative` mobile walkthrough confirming family units remain understandable
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for family-unit cases
  - persona-backed replay plus screenshot notes for desktop and mobile
- Expected visual states:
  - households read as grouped local units
  - no direct-looking ancestor line from a parent to their child’s spouse
  - disconnected branches are separated without unreadable clumping

## Acceptance Criteria

- [ ] The tree uses an explicit family-unit or equivalent structural layout model rather than relying on decorative partner-line packing.
- [ ] A spouse or in-law does not visually appear as the biological child or parent of the wrong person in the seeded multigenerational cases.
- [ ] Children of a known parent pair descend from a shared local household structure rather than from one spouse’s standalone node position.
- [ ] Separate components and unconnected people remain individually readable without name overlap or household ambiguity.
- [ ] Desktop and mobile both preserve the new household clustering semantics.

## Risk and Verification Notes

- Complexity hotspots:
  - generation assignment for a DAG rather than a pure tree
  - clustering families with and without explicit partnerships
  - spacing for branches with mixed sibling and spouse ordering
- Likely shallow-pass failure modes:
  - layout looks better for the current prod screenshot but not for variant family shapes
  - new abstractions exist in code but browser geometry still misleads
  - households cluster correctly only when both parents have children together
- Required verification depth:
  - geometry assertions plus visual review on at least one prod-like adversarial branch
  - wrong-variant evidence proving the old false direct-in-law geometry would now fail
- Sufficient discriminative power means:
  review should fail if a reasonable first-time viewer can still misread a spouse or in-law as a bloodline ancestor/descendant.

## Execution Budget

- Builder may explore:
  - union nodes, family anchors, or equivalent hidden structural nodes
  - layered DAG strategies and crossing-reduction heuristics
  - selective layout refactors that preserve tree interactivity and sidebar behavior
- Builder must escalate if:
  - the new layout foundation requires server schema changes to ship basic correctness
  - performance regresses materially on the live-size tree
- Material scope drift:
  - adding new relationship types or full authoring UX for edge-case relationships
  - building a second visualization mode in the same packet
- Proof obligations before review:
  - production-style misread cases are represented in deterministic evidence
  - the new architecture is visible in code structure, not only in CSS tuning

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 interpretation regressions remain in the affected tree layout paths
- [ ] The tree is more trustworthy as the primary workspace for complex family reading
