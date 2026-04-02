# Task Packet - FB-036 Tree Relationship Edit Mode Clarity and Guardrails

## Objective

Make relationship-editing state on the tree unmistakable by giving graph mode a clear start, active, and exit state so members always know when they are browsing versus modifying relationships.

## Why / KPI

- The tree currently mixes browse, select, relationship-calculator, and relationship-editing behaviors in a way that can feel fragile or surprising.
- When a member is unsure whether they are "just looking" or "about to change the graph," hesitation and accidental actions increase, especially on the primary tree surface.

Primary KPI:
- reduce aborted or confusing relationship-edit attempts on `/tree`.

Secondary KPI:
- increase confidence that relationship edits are intentional and reversible.

## Scope

- In scope:
  - stronger graph-mode entry state for link and replace flows
  - persistent but mode-scoped cancel/exit affordances
  - clearer copy for source person, intended relationship, and target selection
  - visual de-emphasis or disabling of irrelevant controls while graph mode is active
  - clean interaction boundaries between graph mode, relationship calculator, and standard browsing
  - keyboard and touch-safe exit behavior for active relationship-edit modes
- Out of scope:
  - new relationship types
  - bulk graph editing
  - drag-to-connect interactions
  - redesign of the full person profile page

## Task Type

- member-facing workflow clarity / state-guardrail packet

## Dependencies and Ordering Assumptions

- Best sequenced after FB-035 so the graph itself is already semantically trustworthy before mode clarity is layered on top.
- May reuse the existing graph-mode banner/prompt structure but should simplify if dual prompts remain confusing.

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
  - graph-mode discoverability and clarity
  - cancel/exit behavior
  - conflict handling between multiple tree modes
- Should improve:
  - inline reassurance that a change has not happened yet until a target is confirmed
  - touch guidance for mobile-first users
- Must re-run:
  - deterministic Playwright flows for start/cancel/replace/link
  - visual/persona review of relationship editing on desktop and mobile

## Implementation Notes

- Likely files:
  - `app/templates/tree.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/js/tree.js`
  - `app/static/css/main.css`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_pages.py`
- Validation commands:
  - `uv run pytest tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  make relationship editing feel explicit, safe, and cancelable
- Verifier:
  structural review, deterministic browser interaction checks, and persona-backed visual review
- Reference/oracle:
  `/Users/cheech/code/family-book/foundation/UX_NORTH_STAR.md`
  existing tree graph-mode flows and recent prompt/cancel regressions
- Expected evidence:
  mode starts clearly, irrelevant browse controls no longer compete, cancel exits cleanly, and no edit-mode controls leak into normal browsing
- Known failure modes / reward hacks:
  - adding more banners without reducing ambiguity
  - hiding controls globally rather than only during active edit mode
  - desktop mode looks clear while mobile becomes cramped or obscured
  - cancel exits one prompt but leaves latent graph state active
- Verifiability class:
  `bounded-judgment`
- Context policy:
  optimize for user certainty about current mode and consequences of the next click

## UI Review Requirements

- Structural oracle:
  - CodeMap review over state transitions for graph mode, relationship calculator, and standard tree browsing
  - verify only one relationship-editing state machine is active at a time
- Browser oracle:
  - deterministic assertions that:
    - no graph-mode cancel/prompt controls are visible outside active edit mode
    - starting graph mode highlights the source and exposes the intended action
    - `Cancel` and `Escape` fully restore browse mode
    - replace and link flows both present the right copy and exit behavior
- Visual/persona oracle:
  - `contributing_member` desktop review for start/cancel/link
  - `family_admin` desktop review for replace flow
  - `mobile_first_relative` mobile review for touch discoverability and exit clarity
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for enter/edit/cancel states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - browse mode feels quiet and uncluttered
  - active graph mode has one obvious message and one obvious escape path
  - nodes read as selectable targets only while edit mode is active

## Acceptance Criteria

- [ ] No relationship-edit cancel or prompt control is visible during ordinary tree browsing.
- [ ] Starting a link or replace flow makes the current mode explicit, including source person and intended relationship.
- [ ] Canceling graph mode, pressing `Escape`, or completing the action returns the tree to a clean browse state with no stale edit affordances.
- [ ] Relationship calculator mode and graph-edit mode cannot silently overlap or compete for the next node click.
- [ ] The relationship-edit flow remains understandable and operable on both desktop and mobile.

## Risk and Verification Notes

- Complexity hotspots:
  - multiple overlapping tree interaction modes
  - prompt/banner duplication
  - focus restoration and keyboard escape behavior
- Likely shallow-pass failure modes:
  - mode copy changes but actual state leakage remains
  - cancel hides visuals but leaves click handlers in edit mode
  - mobile prompt overlays the canvas too aggressively
- Required verification depth:
  - positive and negative interaction paths
  - explicit stale-state checks after cancel and after completion
- Sufficient discriminative power means:
  the packet should fail if a user can still plausibly ask, "am I editing right now or not?"

## Execution Budget

- Builder may explore:
  - single-banner versus sidebar-plus-canvas mode treatments
  - dimming/disable patterns that preserve accessibility
  - improved keyboard shortcuts and touch affordances
- Builder must escalate if:
  - mode clarity requires a larger tree interaction redesign than this packet can safely hold
- Material scope drift:
  - general sidebar IA redesign
  - full relationship calculator redesign
- Proof obligations before review:
  - active mode and exit behavior are unambiguous in browser evidence
  - normal browsing is visibly clean when not editing

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No P0/P1 state-leak or stale-mode issues remain in tree relationship editing
