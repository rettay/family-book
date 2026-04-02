# Task Packet - FB-052 Tree Relationship Correction and Editing Flow

## Objective

Expose relationship correction directly in the tree workspace so members can edit, reverse, and remove mistaken family links from the existing relationship cards without leaving the tree.

## Why / KPI

- The tree is already the primary workspace, but relationship cards currently expose only remove and replace actions, which are not enough when the person is right but the relationship direction or metadata is wrong.
- CFLSR improves when members can confidently repair genealogy mistakes in context instead of abandoning the edit.

Primary KPI:
- increase successful relationship correction completion in the tree workspace.

Secondary KPI:
- reduce confusion around mistaken parent/child direction.

## Scope

- In scope:
  - add an `Edit relationship` flow to existing tree relationship cards
  - expose `Reverse direction` for parent-child relationships in that flow
  - keep `Remove relationship` available and clearer as a correction action
  - allow editing of existing partnership metadata already represented in the tree
  - preserve the current tree layout and overall sidebar structure
- Out of scope:
  - a tree redesign
  - a separate global relationship-management page
  - bulk editing or multi-select correction flows

## Task Type

- member-facing tree correction UX packet

## Dependencies and Ordering Assumptions

- Depends on FB-051 for canonical update/reverse primitives.

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
- `add_relative_from_tree_context`

## Required Viewports and Locales

- Viewports:
  - `desktop`
  - `mobile`
- Locales:
  - `en`
  - `es`

## Implementation Notes

- Likely files:
  - `app/templates/partials/person_sidebar.html`
  - `app/static/js/tree.js`
  - `app/templates/tree.html`
  - `locales/en.json`
  - `locales/es.json`
  - `locales/ru.json`
  - `tests/test_pages.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make mistaken relationship correction obvious and usable inside the tree sidebar
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  users should be able to inspect an existing relationship card and understand how to edit, reverse, or remove it without resorting to trial-and-error
- Expected evidence:
  sidebar screenshots, browser flows for edit/reverse/remove, and localized copy proof
- Known failure modes / reward hacks:
  - edit controls exist but are hidden behind confusing UI
  - reverse direction is offered on partnerships or otherwise nonsensical contexts
  - desktop works but mobile makes the correction controls unreachable
  - correction form exists but does not prefill current relationship metadata
- Verifiability class:
  `bounded-judgment`
- Context policy:
  prefer the smallest tree-native interaction that makes correction obvious and safe

## UI Review Requirements

- Structural oracle:
  - CodeMap over `tree_workspace`
  - confirm relationship correction controls are wired into the existing sidebar cards rather than bolted on incompletely
- Browser oracle:
  - seeded assertions proving:
    - a parent-child relationship can be edited from a tree card
    - a parent-child relationship can be reversed from a tree card
    - a partnership can be edited from a tree card
    - remove still works after edit/reverse additions
    - mobile does not clip or hide the primary correction controls
- Visual/persona oracle:
  - `contributing_member` desktop walkthrough correcting a mistaken parent-child direction
  - `family_admin` desktop walkthrough editing partnership status/details
  - `mobile_first_relative` mobile walkthrough confirming correction actions remain discoverable
- Required artifacts:
  - CodeMap JSON output
  - desktop/mobile screenshots of the relationship correction cards/forms
  - replay notes for edit/reverse/remove scenarios
- Expected visual states:
  - correction actions are visible and understandable from the relationship cards
  - the UI distinguishes `edit`, `reverse`, and `remove` instead of overloading `replace`

## Acceptance Criteria

- [ ] Tree relationship cards expose a clear edit flow for existing parent, child, and partner relationships.
- [ ] Parent-child cards expose a clear reverse-direction action that updates the rendered relationship grouping after save.
- [ ] Remove relationship remains available and understandable as a separate destructive action.
- [ ] Existing relationship metadata is prefilled into the correction form instead of forcing users to start from scratch.
- [ ] Desktop and mobile both keep the correction actions reachable and localized.

## Risk and Verification Notes

- Complexity hotspots:
  - prefilling and resubmitting existing relationship metadata
  - keeping the sidebar state coherent after a reverse moves a card between parent and child sections
  - avoiding confusing overlap with the existing replace-on-tree action
- Likely shallow-pass failure modes:
  - edit flow only works for one relationship type
  - reverse succeeds in the backend but the tree sidebar stays stale
  - too many actions on the card create new confusion
- Required verification depth:
  - deterministic browser proof for all three correction paths plus screenshots on both breakpoints
- Sufficient discriminative power means:
  review should fail if a user still cannot tell how to fix “this is the wrong parent/child direction.”

## Execution Budget

- Builder may explore:
  - compact disclosure forms, inline edit cards, or a light card-expansion pattern
- Builder must escalate if:
  - the existing sidebar structure cannot support correction without a broader tree workspace redesign
- Material scope drift:
  - redesigning the whole relationships panel
  - creating a separate relationship-management application surface
- Proof obligations before review:
  - the correction actions must be understandable and proven on the real tree UI

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 relationship-correction UX regressions remain in scope
- [ ] Members can correct mistaken relationship direction from the tree without leaving the workspace
