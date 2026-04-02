# Task Packet - FB-038 Tree Navigation Recovery and Controls Information Architecture

## Objective

Make the tree easier to navigate at scale by improving recovery when users get lost, regrouping controls by task, and giving the left-hand tree controls a clearer information architecture.

## Why / KPI

- The tree is now the primary workspace, but its controls still read as an engineer's utility stack more than a member-facing task system.
- As trees grow, users need orientation and recovery mechanisms, not just zoom buttons and filters. When a member loses track of where they are, contribution stops.

Primary KPI:
- reduce "lost in the tree" moments and navigation abandonment on `/tree`.

Secondary KPI:
- improve discoverability of search, filters, view controls, and recovery actions without increasing clutter.

## Scope

- In scope:
  - regroup the left panel into clearer task-based sections such as navigate, filter, and view
  - stronger search-and-focus behavior that helps users recover orientation after jumping to a person
  - explicit recovery controls such as return to focus, fit family, or similar bounded navigation affordances
  - optional mini-map or overview navigator if it can be delivered without overcomplication
  - clearer empty/help text around navigation and filters
  - preservation of tree usability when the controls panel is collapsed or reopened
- Out of scope:
  - full replacement of the tree with a different visualization paradigm
  - map-view redesign
  - broad admin/settings IA changes
  - feature creep into research or timeline surfaces

## Task Type

- member-facing navigation / information architecture packet

## Dependencies and Ordering Assumptions

- Best sequenced after FB-035 and FB-037 so the tree semantics and selected-person context are already clearer before navigation and control regrouping land.
- The mini-map portion is optional within launch scope; the packet should still ship value if task-based control regrouping and recovery actions land first.

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
  - search-to-person navigation clarity
  - recovery after zoom/pan/jump
  - left-panel information architecture
- Should improve:
  - fit/reset/focus discoverability
  - collapsed-panel resilience
  - large-tree confidence
- Must re-run:
  - browser flows for search, zoom, reset, collapse/expand, and recovery
  - visual/persona review of desktop and mobile navigation understandability

## Implementation Notes

- Likely files:
  - `app/templates/tree.html`
  - `app/static/js/tree.js`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/css/main.css`
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/test_pages.py`
- Validation commands:
  - `uv run pytest tests/test_pages.py -q`
  - `tests/ui/playwright-flow-checks.sh`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  improve tree navigation recovery and control discoverability
- Verifier:
  structural review, deterministic browser checks, and visual/persona review
- Reference/oracle:
  `/Users/cheech/code/family-book/foundation/UX_NORTH_STAR.md`
  current `/tree` navigation, search, zoom, and collapsed-controls behavior
- Expected evidence:
  users can search, jump, recover orientation, and understand where navigation controls live without trial-and-error
- Known failure modes / reward hacks:
  - adding a mini-map that is visually clever but not actually useful
  - regrouping controls cosmetically while leaving key actions hard to find
  - desktop improvements that hide or crowd critical actions on mobile
  - introducing another recovery control that duplicates reset without clarifying intent
- Verifiability class:
  `bounded-judgment`
- Context policy:
  optimize for navigation confidence and recovery, not more chrome

## UI Review Requirements

- Structural oracle:
  - CodeMap review over control regrouping, collapse behavior, and navigation state wiring
- Browser oracle:
  - deterministic checks for:
    - search and jump-to-person
    - return-to-focus or equivalent recovery action
    - reset/fit behavior after manual zoom/pan
    - collapse/expand controls preserving usable recovery actions
    - mobile access to the primary navigation controls
- Visual/persona oracle:
  - `contributing_member` desktop review for search and reorientation
  - `family_admin` desktop review for filter and navigate control discovery
  - `mobile_first_relative` mobile review for touch reachability and uncluttered priority actions
- Required artifacts:
  - CodeMap JSON output
  - Playwright screenshots/traces for search, zoom, recovery, and collapsed-panel states
  - persona-backed replay and screenshots for desktop and mobile
- Expected visual states:
  - left-panel controls are grouped by task rather than mixed utilities
  - recovery actions are visible and understandable
  - collapsed state does not strand the user without a way to recover orientation

## Acceptance Criteria

- [ ] The left tree controls are reorganized into clearer task-based groups rather than one undifferentiated stack.
- [ ] After searching or jumping to a person, the user has an explicit way to recover orientation or return to the previous focus/root context.
- [ ] Zoom, reset, fit, and collapse/expand controls have distinct purposes and are visually understandable.
- [ ] Mobile preserves access to the primary navigation and recovery actions without clipped or hidden controls.
- [ ] The packet improves navigation confidence on larger trees without making the tree surface feel busier or more intimidating.

## Risk and Verification Notes

- Complexity hotspots:
  - control density on smaller screens
  - overlap between reset, fit, and focus actions
  - optional mini-map value versus clutter
- Likely shallow-pass failure modes:
  - controls are visually regrouped but still hard to interpret
  - search jump works but users still cannot tell how to get back
  - collapse state hides important recovery affordances
- Required verification depth:
  - positive navigation flow plus recovery flow
  - visual review for clutter and mobile compression
- Sufficient discriminative power means:
  the packet should fail if a user can still easily get lost with no obvious way back.

## Execution Budget

- Builder may explore:
  - mini-map versus lighter-weight recovery affordances
  - sectioned or accordion control groups
  - subtle helper text that clarifies navigation actions
- Builder must escalate if:
  - proposed navigation changes imply a larger visualization architecture rewrite
- Material scope drift:
  - new non-tree features
  - broad redesign of admin/settings surfaces
- Proof obligations before review:
  - browser and visual evidence show a real recovery path after jump/zoom
  - controls read as task-based and less intimidating than before

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Structural/browser/visual evidence attached and consistent
- [ ] No new navigation dead ends or collapsed-state regressions remain in scope
