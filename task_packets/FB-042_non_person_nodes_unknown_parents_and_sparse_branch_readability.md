# Task Packet - FB-042 Unknown Parents and Sparse-Branch Readability

## Objective

Handle the remaining high-confusion edge cases in the tree by making single-parent and unknown-parent structures truthful and by keeping sparse or detached branches readable without overlapping into an unreadable cluster.

Launch narrowing:
- Non-person nodes such as pets or institutions are explicitly deferred from this sprint.
- Reason: the current tree payload and entity model are person-only, and adding truthful non-person support requires a separate product/entity-model decision rather than an ad hoc renderer shortcut.

## Why / KPI

- Even with stronger household layout and relationship semantics, the tree will still feel incomplete or brittle if users cannot truthfully read single-parent structures, unknown-parent gaps, or lightly connected branches.
- Current detached-orphan handling reduces overlap but still needs product-level clarity around partial-family structures.

Primary KPI:
- increase truthful coverage of unusual but common family-record cases without degrading readability.

Secondary KPI:
- reduce pressure to encode special cases inaccurately just to make the tree render.

## Scope

- In scope:
  - clear single-parent and unknown-parent household rendering
  - improved layout and labeling for sparse or detached branches
  - readable packing of partially connected people so names do not collapse into one unreadable cluster
  - tree legend/help updates explaining placeholder semantics where shown
- Out of scope:
  - pets, institutions, or any other non-person node type
  - speculative support for every genogram symbol under the sun
  - legal or archival metadata around institutions
  - print/export or alternate chart modes

## Task Type

- member-facing tree edge-case modeling and readability packet

## Dependencies and Ordering Assumptions

- Depends on FB-039.
- Best sequenced after FB-041 so the main relationship semantics are already in place before special node types are added.
- Non-person nodes are deferred; any future support should start from a new task packet with an explicit entity-model contract.

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
- Should improve:
  - legend/help discoverability
  - packing of lightly connected people on smaller screens
- Must re-run:
  - seeded browser cases for detached branches and single-parent families
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
  model sparse and partial family branches truthfully without hurting readability
- Verifier:
  structural review, deterministic browser checks, locale parity, and visual/persona review
- Reference/oracle:
  tree truthfulness requirements from the Family Book product and UX contract
  user-reported detached-branch readability failures
- Expected evidence:
  single-parent or unknown-parent branches remain understandable, detached people do not overlap unreadably, and the UI does not imply support for non-person nodes that the model does not provide
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
    - unknown-parent or placeholder semantics are clearly distinct from known people when shown
    - detached branches remain separated and readable
    - unsupported non-person cases are not implied by the UI
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough of a sparse branch with unknown-parent or single-parent structure
  - `family_admin` desktop walkthrough of a detached sparse branch correction
  - `mobile_first_relative` mobile walkthrough confirming detached branches remain readable
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for sparse-branch states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - detached branches are separated but still legible
  - placeholder semantics are visually explicit where shown
  - unsupported cases are not disguised as supported tree features

## Acceptance Criteria

- [ ] Single-parent households render clearly without implying a second known parent.
- [ ] Unknown-parent or placeholder semantics, if shown, are visually distinct from known people and do not invent unsupported facts.
- [ ] Detached or sparse branches remain readable on desktop and mobile without overlapping names.
- [ ] The shipped tree scope does not imply support for pets, institutions, or other non-person nodes that are not present in the model.
- [ ] The packet improves truthful coverage of edge cases without making the main family tree harder to interpret.

## Risk and Verification Notes

- Complexity hotspots:
  - deciding what non-person support is truly in launch scope
  - keeping sparse-branch readability on small screens
  - placeholder semantics that are explicit without being visually noisy
- Likely shallow-pass failure modes:
  - detached-branch frames exist but labels still overlap
  - unknown-parent rendering subtly implies facts not present in data
  - launch docs still promise non-person support that the shipped model does not provide
- Required verification depth:
  - adversarial sparse-branch seed plus persona review
  - wrong-variant checks ensuring unsupported cases are not silently normalized into person nodes
- Sufficient discriminative power means:
  review should fail if special cases can only be represented by misleading the viewer.

## Execution Budget

- Builder may explore:
  - light placeholder semantics for unknown/absent parents
  - better detached-branch packing and label wrapping strategies
- Builder must escalate if:
  - requested support expands into pets, institutions, or other non-person entities
  - the implementation would require a large schema or permissions expansion
- Material scope drift:
  - full household management product beyond tree interpretation
  - broad new data-entry workflows outside the tree
- Proof obligations before review:
  - tree evidence shows at least one partial-family and one sparse-branch case
  - launch documentation explicitly bounds non-person-node support out of scope

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 edge-case truthfulness regressions remain in scope
