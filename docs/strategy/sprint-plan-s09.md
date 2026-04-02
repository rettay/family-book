# Sprint Plan - S09 Accessibility and Interaction Hardening

## Sprint

- Name: `S09 - Accessibility and Interaction Hardening`
- Status: Closed
- Primary packet: `FB-012 Accessibility and Interaction Hardening`
- Follow-on packet candidate: `FB-013 Readability and Responsive Polish`

## Sprint Goal

Fix the highest-severity UI/UX and accessibility failures in Family Book so the core flows are keyboard reachable, overlays behave correctly, dynamic updates communicate state, and core forms are materially easier to use.

## Why This Sprint

The latest UI/UX code review found concrete, code-grounded issues in the current implementation. The most severe gaps are not visual polish problems; they are interaction failures in overlays, SVG-based tree/map controls, form labeling, and dynamic-content feedback. These issues affect the product’s main value surfaces, so the next sprint should convert the review into implementation rather than letting the feedback sit as documentation.

## Must-Have Outcomes

- Core overlays behave like accessible dialogs instead of loose visual layers.
- Tree and map interactions become keyboard reachable and no longer rely on mouse-only behavior.
- Dynamic HTMX updates expose loading and update feedback in a way users can actually perceive.
- The most important forms have proper labels and more local error guidance.
- The sprint improves UI operability without turning into a broad redesign effort.

## Acceptance Criteria

1. Compose modal, lightbox, and tree sidebar support close semantics, focus management, and focus return.
2. Tree nodes and map markers are keyboard reachable and do not depend on double-click-only or mouse-only interaction.
3. Nav toggles, comment toggles, reaction toggles, and similar controls expose expanded/collapsed state accessibly.
4. People search, comments, lazy-loaded history/media, and similar dynamic regions expose useful loading or update feedback.
5. Person create/edit, search, and comment inputs have materially better label and validation behavior.
6. Browser and focused test coverage demonstrates the most important regressions are now caught.

## In Scope

- dialog and overlay accessibility
- keyboard semantics for tree/map/media/toggles
- HTMX loading/update semantics
- core form labeling and error UX
- selective reduction of context-breaking reloads where the payoff is high
- targeted browser and pytest coverage to verify the changes

## Out of Scope

- broad redesign or visual rebrand
- large information-architecture changes
- full WCAG audit certification work
- full visual regression tooling overhaul
- secondary readability polish better suited to FB-013

## Implementation Order

1. Execute Slice 1: dialog, focus, and nav semantics.
2. Execute Slice 2: keyboard access and semantic interaction hardening for tree/map/media.
3. Execute Slice 3: dynamic feedback, form usability, and selective responsive cleanup.
4. Validate with Playwright, focused pytest, and a staging/manual keyboard review.

## Execution Slices

### Slice 1 - Dialog and Focus Contract

- Goal:
  make overlays behave predictably for keyboard and assistive-technology users
- Scope:
  compose modal, lightbox, tree sidebar, close controls, Escape handling, and focus return
- Must prove:
  Family Book no longer loses user context when overlays open and close

### Slice 2 - Keyboard and Semantic Interaction Hardening

- Goal:
  remove mouse-only interaction from the highest-value interactive surfaces
- Scope:
  tree nodes, map markers, media triggers, nav toggles, reaction toggles, and comment toggles
- Must prove:
  the core app can be navigated and activated from the keyboard in the main flows

### Slice 3 - Dynamic Feedback and Form Usability

- Goal:
  make dynamic updates and core forms understandable without requiring guesswork
- Scope:
  HTMX loading/update semantics, people search, comments, history/media loads, person create/edit, and near-field error guidance
- Must prove:
  users receive meaningful feedback when content updates or form submission fails

## Proof Obligations

- The sprint must close the critical overlay and keyboard issues identified in the UI/UX review.
- The changes must fit the current server-rendered architecture rather than simulate SPA patterns.
- Browser evidence must demonstrate real keyboard and focus improvements, not just markup changes.
- The sprint should improve operability without broad stylistic churn.

## Risks To Watch

- patching semantics without fixing actual interaction behavior
- overloading the sprint with visual polish and diluting the critical fixes
- making tree/map accessibility too shallow to be meaningful
- increasing client-side complexity just to chase edge-case polish

## Exit Target

Sprint 09 is complete when Family Book’s core UI flows are materially more operable and accessible, especially for keyboard users, and the highest-severity UI/UX review findings are closed in code and browser verification.
