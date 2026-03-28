# Task Packet - FB-042 Non-Person Nodes, Unknown Parents, and Sparse-Branch Readability

## Objective

Handle the remaining high-confusion edge cases in the tree by supporting non-person household nodes where justified, clear unknown-parent or single-parent structures, and readable separation of sparse or detached branches such as pets, institutions, and orphaned people.

## Why / KPI

- Even with stronger household layout and relationship semantics, the tree will still feel incomplete or brittle if users cannot truthfully represent pets, unknown parents, guardianship-like households, or lightly connected branches.
- Current detached-orphan handling reduces overlap but still lacks a product-level model for special nodes and partial-family structures.

Primary KPI:
- increase truthful coverage of unusual but common family-record cases without degrading readability.

Secondary KPI:
- reduce pressure to encode special cases inaccurately just to make the tree render.

## Scope

- In scope:
  - support for non-person nodes that are explicitly in launch scope for tree interpretation, such as pets or institutions/households, if represented in the model
  - clear single-parent and unknown-parent household rendering
  - improved layout and labeling for sparse or detached branches
  - readable packing of partially connected people so names do not collapse into one unreadable cluster
  - tree legend/help updates explaining any new node types or placeholder semantics
- Out of scope:
  - speculative support for every genogram symbol under the sun
  - legal or archival metadata around institutions
  - print/export or alternate chart modes

## Task Type

- member-facing tree edge-case modeling and readability packet

## Dependencies and Ordering Assumptions

- Depends on FB-039.
- Best sequenced after FB-041 so the main relationship semantics are already in place before special node types are added.
- If pets or institutions would require a materially new entity model, builder should narrow launch scope to read-only placeholder semantics or escalate rather than forcing an ad hoc implementation.

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
  - readability of detached and sparse branches
  - single-parent and unknown-parent family structures
  - truthful display of supported non-person node types
- Should improve:
  - legend/help discoverability
  - packing of lightly connected people on smaller screens
- Must re-run:
  - seeded browser cases for detached branches, single-parent families, and any supported non-person node types
  - visual review confirming dense sparse-branch cases remain readable

## Implementation Notes

- Likely files:
  - `app/static/js/tree.js`
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/css/main.css`
  - `app/routes/tree.py`
  - `app/schemas.py`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/ui/playwright_seed.py`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_api.py`
  - `tests/test_pages.py`
- Validation commands:
  - `uv run pytest tests/test_api.py tests/test_pages.py tests/test_phase3.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  model sparse, partial, and non-person family branches truthfully without hurting readability
- Verifier:
  structural review, deterministic browser checks, locale parity, and visual/persona review
- Reference/oracle:
  tree truthfulness requirements from the Family Book product and UX contract
  user-reported detached-branch readability failures
- Expected evidence:
  single-parent or unknown-parent branches remain understandable, detached people do not overlap unreadably, and any supported non-person nodes are clearly distinct from people
- Known failure modes / reward hacks:
  - unsupported node types are faked as regular people
  - sparse-branch labels exist but nodes still overlap in practice
  - unknown-parent handling silently invents relationships
  - mobile detached-branch packing regresses into clipped or illegible text
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prefer truthful limited support over broad but ambiguous pseudo-support

## UI Review Requirements

- Structural oracle:
  - CodeMap review over special-node rendering, placeholder semantics, and sparse-branch layout logic
- Browser oracle:
  - seeded assertions proving:
    - single-parent families render without false second-parent implication
    - unknown-parent or placeholder semantics are clearly distinct from known people
    - detached branches remain separated and readable
    - any supported pet or institution node type renders distinctly from a person node
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough of a sparse branch with unknown-parent or single-parent structure
  - `family_admin` desktop walkthrough of a supported non-person node type if in scope
  - `mobile_first_relative` mobile walkthrough confirming detached branches remain readable
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for sparse-branch and special-node states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - detached branches are separated but still legible
  - placeholder or non-person semantics are visually explicit
  - unsupported cases are not disguised as normal family relationships

## Acceptance Criteria

- [ ] Single-parent households render clearly without implying a second known parent.
- [ ] Unknown-parent or placeholder semantics, if shown, are visually distinct from known people and do not invent unsupported facts.
- [ ] Detached or sparse branches remain readable on desktop and mobile without overlapping names.
- [ ] Any supported non-person node type such as a pet or institution is visually distinct from a person and explained by the tree legend or help cues.
- [ ] The packet improves truthful coverage of edge cases without making the main family tree harder to interpret.

## Risk and Verification Notes

- Complexity hotspots:
  - deciding what non-person support is truly in launch scope
  - keeping sparse-branch readability on small screens
  - placeholder semantics that are explicit without being visually noisy
- Likely shallow-pass failure modes:
  - pets or institutions are added with no clear legend
  - detached-branch frames exist but labels still overlap
  - unknown-parent rendering subtly implies facts not present in data
- Required verification depth:
  - adversarial sparse-branch seed plus persona review
  - wrong-variant checks ensuring unsupported cases are not silently normalized into person nodes
- Sufficient discriminative power means:
  review should fail if special cases can only be represented by misleading the viewer.

## Execution Budget

- Builder may explore:
  - light placeholder nodes
  - distinct shapes or badges for supported non-person nodes
  - better detached-branch packing and label wrapping strategies
- Builder must escalate if:
  - supporting pets or institutions requires a new product decision about entity scope
  - the implementation would require a large schema or permissions expansion
- Material scope drift:
  - full household management product beyond tree interpretation
  - broad new data-entry workflows outside the tree
- Proof obligations before review:
  - tree evidence shows at least one partial-family and one sparse-branch case
  - non-person support, if included, is truthful and explicitly bounded

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 edge-case truthfulness regressions remain in scope
