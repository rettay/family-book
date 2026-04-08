# Sprint Plan - S47a Product Stabilization Before Commercialization

## Sprint

- Name: `S47a - Product Stabilization Before Commercialization`
- Status: Closed
- Primary packet: `FB-132 Timeline Filter Consistency and Error-State Fix`
- Core supporting packets:
  - `FB-133 Research Page Beta Gating and Source Health UI`
  - `FB-131 Tree Sidebar Popout Collapse/Dock Fix`
- Stretch / queued packets:
  - `FB-134 External Research Source Link and Result Quality Fixes`
  - `FB-130 Overlay and Workspace Panel Interaction Contract`

## Sprint Goal

Fix the most visible production-facing UX and feature-trust issues before starting the commercialization hosting and tenant-architecture work.

## Why This Sprint

Recent production usage surfaced broken timeline filters, a misleading research page, and inconsistent tree sidebar popout controls. These issues make the product feel unreliable even before any hosting or billing work starts. Stabilization should come before `S47 - Hosting and Tenant Architecture` so the commercialization roadmap starts from a credible product baseline.

## Must-Have Outcomes

- Timeline filters work consistently for the reported `1880` to `2002` range and do not show bogus `could not load content` errors.
- Research page is clearly labeled as beta/low-confidence and shows per-source health/config/result states.
- Popped-out tree sidebar controls have distinct, predictable behavior for collapse/dock/close.
- Research results do not overstate guided lookup links as robust external search hits.

## Stretch Outcomes

- Antenati links are corrected, demoted, or removed if they cannot preserve useful query context.
- A small overlay/workspace panel contract exists so future popouts, drawers, and dialogs do not drift further.

## Acceptance Criteria

1. Timeline event-type and year filters produce correct results or explicit no-results states for `All Events`, `Births`, `Deaths`, and `Marriages`.
2. Timeline filtering for `from=1880` and `to=2002` works with `All Events` and specific event types.
3. Timeline errors distinguish network/server failure from "no matching events."
4. Research page visibly indicates beta/low-confidence status and per-source state: configured, not configured, no results, or error.
5. Guided lookup links are labeled differently from real search results.
6. Floating tree sidebar caret no longer duplicates the `x` close behavior.
7. Antenati is either corrected to a useful current deep link or downgraded/removed as a guided lookup result if `FB-134` is pulled into the sprint.
8. Research query behavior is verified with `cutroni`, `maglio`, and a baseline web-search comparison query such as `maglio family` if `FB-134` is pulled into the sprint.
9. Overlay/panel behavior is documented with canonical states and controls if `FB-130` is pulled into the sprint.

## In Scope

- Timeline filter UI and API/partial consistency
- Timeline empty/error states and tests
- Research source status UI and beta copy
- Research source result quality for current configured/free sources if `FB-134` is pulled in
- Antenati link correction or demotion if `FB-134` is pulled in
- Tree sidebar popped-out collapse/dock/close behavior
- Overlay/workspace panel interaction contract documentation if `FB-130` is pulled in

## Out of Scope

- Full research product redesign
- Adding paid/commercial record-provider integrations
- Brave Search API integration unless already available and trivial
- New frontend framework migration
- Multi-tenant hosting
- Stripe/billing work
- Broad design system rewrite beyond overlay/panel contract

## Implementation Order

1. Execute `FB-132` first because the timeline bug is concrete and user-visible.
2. Execute `FB-133` to stop the research page from overpromising and make source health visible.
3. Execute `FB-131` as a targeted sidebar behavior fix.
4. Pull in `FB-134` only after source health is visible, focusing on Antenati and basic free-source behavior.
5. Pull in `FB-130` only if the sidebar fix exposes reusable panel-state decisions or if time remains for a doc-only contract.

## Proof Obligations

- Reproduce or cover the reported timeline range: `1880` to `2002`.
- Prove `All Events` does not serialize a backend-invalid event type.
- Prove UI event-type values match backend-supported event types.
- Prove research source errors are visible and not collapsed into fake successful results.
- Prove tree sidebar `collapse`, `dock`, and `close` are not ambiguous in popped-out mode.
- Do not adopt a UI dependency in `FB-130` without an explicit decision note.

## Risks To Watch

- Timeline may have a value mismatch (`births` vs `birth`) hidden by partial update behavior.
- Research may be returning synthetic guided links that look like real hits.
- Fixing Antenati alone may still leave research feeling bad; status labeling is the safety net.
- Sidebar panel state may be spread across CSS, DOM classes, and localStorage; avoid a large rewrite unless necessary.
- UI libraries can add bundle and integration complexity; use them as references unless there is a clear reason to adopt.

## Exit Target

Sprint S47a is complete when the reported production bugs are fixed or deliberately downgraded with honest beta/status UI, and the product is ready to resume commercialization architecture work.

## Closeout Evidence

- Evidence summary: `docs/strategy/sprint-closeout-s47a.md`
- Rendered browser artifacts: `output/playwright/family-book-flow/`
