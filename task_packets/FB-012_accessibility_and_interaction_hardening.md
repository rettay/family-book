# Task Packet - FB-012 Accessibility and Interaction Hardening

## Objective

Fix the highest-severity UI/UX and accessibility gaps in Family Book so the core member and admin flows are operable by keyboard, understandable during dynamic updates, and materially more resilient for real family use.

## Why / KPI

- The recent UI/UX code review found concrete accessibility and interaction failures in the current implementation, especially around overlays, keyboard reachability, data-visualization controls, dynamic HTMX updates, and form usability.
- These are not cosmetic issues. They block or materially degrade the main product flows: moments, people, tree, map, and admin operations.
- The next sprint should convert the review into shipped fixes rather than letting the findings sit as passive feedback.

Primary KPI:
- reduce the number of critical and warning-level accessibility/interaction failures across the main Family Book flows.

Secondary KPI:
- improve successful manual staging review of keyboard-only and assistive-tech-adjacent paths for core surfaces.

## Scope

- In scope:
  - accessible dialog behavior for the compose modal, lightbox, and tree sidebar
  - keyboard and semantic access for tree nodes, map markers, nav toggles, reaction toggles, and comment toggles
  - replace or harden non-semantic clickable media and upload controls
  - improve HTMX/live-update feedback with loading, busy, and announcement semantics
  - fix missing form labels, field associations, and high-friction error feedback in core forms
  - reduce full-page reloads where they currently break user context in high-value flows
- Out of scope:
  - broad visual redesign
  - major information-architecture changes
  - cross-browser accessibility certification work
  - a full design-system rewrite
  - unrelated feature additions

## Task Type

- Accessibility / interaction hardening packet

## Dependencies and Ordering Assumptions

- Depends on S01-S08 being closed because the collaboration spine, release lane, and staging workflow already exist.
- Should happen before another feature-heavy sprint so future work lands on a more accessible interaction baseline.
- Assumes the current server-rendered FastAPI + Jinja + HTMX architecture remains the product delivery model.

## Constraints

- Fixes should preserve the existing product surface and avoid broad rewrites.
- Accessibility improvements must be real implementation changes, not documentation-only work.
- Keyboard reachability and dialog behavior should be testable in browser automation where practical.
- Dynamic-content feedback should fit the current HTMX/server-rendered model instead of introducing SPA-only patterns.

## Recommended Launch Scope Within This Packet

- Must directly fix:
  - compose modal focus and keyboard behavior
  - lightbox focus and keyboard behavior
  - tree sidebar open/close behavior and focus handling
  - keyboard access for tree and map interactive nodes
  - form labeling problems on person create/edit and comment/search inputs
  - dynamic feedback gaps in comments, people search, person history/media, and audit-log style regions
- Should improve:
  - state exposure for nav, comments, and reactions
  - high-friction reload-heavy actions where localized updates are feasible
  - semantic affordances for clickable media and upload triggers
- Must re-run:
  - focused pytest for affected templates/routes/helpers
  - Playwright flow checks with new keyboard/assertion coverage
  - CodeMap to ensure the sprint does not introduce new governance failures

## Implementation Notes

- Likely files:
  - `app/templates/base.html`
  - `app/templates/home.html`
  - `app/templates/people.html`
  - `app/templates/person.html`
  - `app/templates/person_edit.html`
  - `app/templates/person_new.html`
  - `app/templates/tree.html`
  - `app/templates/map.html`
  - `app/templates/admin.html`
  - `app/templates/partials/moment_card.html`
  - `app/templates/partials/comments.html`
  - `app/templates/partials/media_gallery.html`
  - `app/templates/partials/person_sidebar.html`
  - `app/static/css/main.css`
  - `app/static/js/main.js`
  - `app/static/js/tree.js`
  - `app/static/js/map.js`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_pages.py tests/test_theme.py -q`
  - targeted pytest for any added template/client behavior coverage
  - `make test-ui-playwright`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  fix concrete accessibility and interaction failures from the UI/UX review
- Verifier:
  keyboard-oriented browser checks, targeted pytest, code review, and staging/manual review
- Reference/oracle:
  the latest UI/UX code review findings
  `docs/ops/staging-acceptance-checklist.md`
  `tests/ui/playwright-flow-checks.sh`
- Expected evidence:
  core overlays behave like dialogs, key interactive surfaces are keyboard reachable, and dynamic content updates communicate state clearly
- Known failure modes / reward hacks:
  - adding ARIA attributes without fixing actual keyboard behavior
  - keeping mouse-only click targets and merely documenting them
  - adding more reloads or toasts instead of improving local feedback
  - claiming accessibility improvements without browser-level evidence
- Verifiability class:
  `accessibility-and-interaction-hardening`
- Context policy:
  optimize for real user operability, not superficial compliance cosmetics

## Acceptance Criteria

- [ ] Compose modal, lightbox, and tree sidebar behave as accessible overlays with close, focus, and return semantics.
- [ ] Tree and map interactive nodes are keyboard reachable and no longer depend on mouse-only or double-click-only interaction.
- [ ] Core toggles and action controls expose state correctly and use semantic buttons/links where appropriate.
- [ ] People search, comments, lazy-loaded history/media, and similar HTMX regions expose loading and update feedback accessibly.
- [ ] Core forms have proper labels and materially better inline or near-field error feedback.
- [ ] The sprint reduces context-breaking reload behavior in at least the highest-value interaction paths.
- [ ] Playwright and focused tests cover the most important accessibility/interaction regressions introduced by this work.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] No critical UI/UX review findings remain open in the sprint scope
- [ ] No unrelated redesign work folded into the sprint

## Risk and Verification Notes

- Likely shallow-pass failure modes:
  - dialog ARIA added without focus management
  - keyboard reachability added for some controls but not the core tree/map surfaces
  - HTMX regions still update silently with no user feedback
  - forms remain toast-driven rather than field-guided
- Required verification depth:
  - code review of semantics and keyboard paths
  - browser verification of focus behavior and keyboard interaction
  - staging review of the core member/admin flows
- Sufficient discriminative power means:
  this packet should fail review if the UI is still primarily mouse-first or if overlay behavior is still context-breaking

## Execution Budget

- Builder may explore:
  - the lightest-weight focus-management approach that fits the current JS architecture
  - how best to attach busy/live semantics to HTMX swaps
  - the smallest browser assertions that materially prove keyboard improvements
- Builder must escalate if:
  - a fix would require re-architecting the tree or map rendering model
  - overlay behavior conflicts with current product expectations in a non-trivial way
- Material scope drift:
  - visual redesign
  - new navigation or information architecture
  - generalized design-system work
- Proof obligations before review:
  - the most severe overlay/keyboard issues are concretely fixed
  - dynamic updates and forms are materially easier to use
  - browser evidence demonstrates real accessibility/interaction improvement
