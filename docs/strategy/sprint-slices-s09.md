# Sprint Slices - S09 Accessibility and Interaction Hardening

## Slice Sequence

### S09-1 Dialog and Focus Contract

Status: `done`

- Objective:
  turn the current modal/sidebar/lightbox behavior into a consistent accessibility contract
- Scope:
  compose modal, lightbox, tree sidebar, close buttons, Escape behavior, focus trap where appropriate, and focus return
- Deliverable:
  overlays that behave like dialogs instead of loose visual layers
- Verification:
  keyboard/browser checks and focused code review of focus behavior

### S09-2 Keyboard and Semantic Interaction Hardening

Status: `done`

- Objective:
  eliminate mouse-only interaction from high-value controls and visualizations
- Scope:
  tree nodes, map markers, media triggers, mobile nav, comment toggles, reaction toggles, and similar controls
- Deliverable:
  semantic, keyboard-reachable interaction patterns for the core Family Book surfaces
- Verification:
  browser checks proving the main flows can be completed without mouse-only behavior

### S09-3 Dynamic Feedback and Form Usability

Status: `done`

- Objective:
  make dynamic content updates and core forms self-explanatory during use
- Scope:
  HTMX/live regions, people search, comments, lazy-loaded sections, person create/edit, and localized submission/error feedback
- Deliverable:
  better perceived responsiveness and clearer form guidance without full-page reload dependence
- Verification:
  focused tests plus staging/manual review of the affected flows

## Slice Rules

- Keep the sprint centered on concrete accessibility and operability issues.
- Prefer semantic HTML and light JS improvements over heavier rewrites.
- Treat tree and map accessibility as first-class sprint scope, not optional polish.
- Defer secondary typography and responsive polish to FB-013 unless it directly blocks a critical interaction fix.

## Recommended Builder Order

1. `S09-1`
2. `S09-2`
3. `S09-3`

## PM Note

This sprint exists to turn a code-review accessibility report into shipped improvements. The right result is not “more ARIA”; it is a Family Book UI that is materially easier to operate in the browser.
