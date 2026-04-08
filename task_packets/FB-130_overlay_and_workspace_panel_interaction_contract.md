# Task Packet - FB-130 Overlay and Workspace Panel Interaction Contract

Status: Proposed

## Objective

Define a coherent interaction contract for sidebars, popped-out panels, drawers, popovers, and dialogs so future UI work does not keep inventing inconsistent close/collapse/dock behavior.

## Why / KPI

The popped-out tree sidebar has a caret control that behaves like close, duplicating the `x` close control. This is a symptom of a broader UI system issue. Family Book needs a small, documented panel model before commercialization adds more onboarding, billing, support, and export dialogs.

## Scope

- In scope:
  - define canonical panel states: docked, collapsed, floating, minimized, closed
  - define canonical controls: collapse, expand, pop out, dock, minimize, close
  - define keyboard behavior: Escape, focus trapping where appropriate, focus return, tab order
  - define mobile behavior: drawer/full-screen fallback vs floating disabled
  - evaluate native `<dialog>`, Floating UI, Shoelace, and custom JS as options
  - document which component types should use which pattern
- Out of scope:
  - adopting a UI dependency without a separate decision
  - rewriting all modals/dialogs
  - React migration
  - broad visual redesign

## Likely Files

- `docs/ops/overlay-and-panel-interaction-contract.md`
- `docs/strategy/bug-triage-intake.md`
- `app/templates/tree.html`
- `app/static/js/tree.js`
- `app/static/css/main.css`

## Acceptance Criteria

- [ ] Contract document defines panel states and controls.
- [ ] Contract distinguishes persistent workspace panels from true modal dialogs.
- [ ] Contract defines mobile fallback behavior.
- [ ] Contract evaluates Floating UI, Shoelace, native `<dialog>`, and custom JS without automatically approving a dependency.
- [ ] `FB-131` tree sidebar behavior is checked against the contract.
- [ ] Future packet authors can reference the contract for new dialogs/drawers/panels.

## Validation Commands

- `git diff --check`

## Definition of Done

- [ ] Product and engineering have a shared vocabulary for panels and overlays.
