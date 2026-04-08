# Bug Triage Intake

Intake date: April 8, 2026

Source: founder QA from latest production site usage.

Context: these bugs should be addressed before starting the commercialization sprint sequence in `docs/strategy/commercialization-sprint-plan-2026.md`.

## Summary

| ID | Title | Area | Severity | Status |
|---|---|---|---:|---|
| BUG-001 | Popped-out tree sidebar collapse control behaves like close | Tree / overlay UI | P2 | Needs triage |
| BUG-002 | Timeline filters produce inconsistent errors and results | Timeline | P1 | Needs triage |
| BUG-003 | Research page returns mostly/only Antenati and sends users to useless/broken URLs | Research | P1 | Needs triage |

## BUG-001: Popped-out tree sidebar collapse control behaves like close

- Area: Tree / overlay UI / window and dialog behavior
- Severity: P2
- Environment: production, latest site
- URL/page: Tree view
- User report:
  - The right-hand sidebar can be popped out.
  - When it is popped out and the user clicks the caret labeled/understood as "Collapse Sidebar", the sidebar does not collapse to the side.
  - Instead, the entire sidebar disappears.
  - This makes the caret redundant with the `x` close control.
- Expected:
  - In docked mode, collapse should collapse the sidebar to the side.
  - In popped-out/floating mode, the control semantics should be coherent: minimize, collapse, dock, or close should each be distinct and predictable.
  - The `x` should remain the close action.
- Actual:
  - In popped-out mode, the caret behaves like close/disappear.
- Product impact:
  - Creates user confusion in the primary workspace.
  - Indicates a broader interaction-system issue: sidebars, floating panels, drawers, dialogs, popovers, and close/collapse/minimize behaviors are not governed by one consistent model.
- PM recommendation:
  - Do not fix only the caret handler unless it is a trivial hotfix.
  - Create a small "overlay and workspace panel contract" before adding more popouts/dialogs.
  - Define canonical states: docked, collapsed, floating, minimized, closed.
  - Define canonical controls: collapse, pop out, dock, minimize, close.
  - Define keyboard and mobile behavior for each.
- Candidate implementation direction:
  - For the current HTMX/Jinja/vanilla JS stack, prefer a small framework-agnostic foundation rather than a React-only component library.
  - Evaluate native `<dialog>` where appropriate for true modals, but not for every persistent workspace panel.
  - Evaluate Floating UI for positioning/popover mechanics where custom panels remain necessary.
  - Evaluate Shoelace or similar web components for framework-agnostic dialogs/drawers if adopting a component dependency is acceptable.
  - Treat Radix UI / Headless UI style React primitives as lower fit unless the frontend stack changes.
- Follow-up questions:
  - Should floating tree sidebars have a minimized tab state, or should floating mode only support dock and close?
  - On mobile, should pop-out be disabled in favor of a full-screen drawer?
  - Are there other current popups/dialogs with similar inconsistent close/collapse behavior?

## BUG-002: Timeline filters produce inconsistent errors and results

- Area: Timeline
- Severity: P1
- Environment: production
- URL/page: `https://cutroni.xyz/timeline`
- User report:
  - Content display and filtering are inconsistent.
  - Choosing values from the event-type dropdown often displays `could not load content`.
  - The selected dropdown value does not reliably apply.
  - Filtering by year also displays `could not load content`, although the year range appears to filter events.
  - After applying a year filter and selecting `All Events`, nothing is displayed.
  - Changing the dropdown to `births` after that does not show the error and appears to filter correctly.
- Reproduction detail:
  - Year range used: from `1880` to `2002`.
  - The dataset is expected to contain matching events in that range, including birthdays and deaths.
- Expected:
  - Event-type dropdown should consistently filter timeline content.
  - Year range should filter without an error if the response is valid.
  - `All Events` should show all events within the current year range.
  - Empty states should distinguish "no matching events" from "request failed".
  - Filter state should remain visible and consistent in URL/form/UI.
- Actual:
  - Error message appears even when some filter behavior seems to work.
  - `All Events` can show empty content after year filtering.
  - Dropdown behavior differs between `All Events` and `births`.
- Product impact:
  - Core timeline feature feels unreliable.
  - Users cannot trust filters or error states.
  - Likely blocks use during family browsing/research sessions.
- Likely investigation areas:
  - HTMX target/swap behavior for `/partials/timeline-events`.
  - Mismatch between UI dropdown values and API/service values. Example risk: UI uses `births` while backend expects `birth`.
  - Error handling that treats empty partials or non-HTML responses as failure.
  - `All Events` value serialization. Example risk: sending `event_type=all` when backend expects missing/empty `event_type`.
  - Year filter form submits and event-type filter submits may be overwriting each other.
- Suggested acceptance criteria for fix:
  - Selecting `All Events`, `Births`, `Deaths`, and `Marriages` returns either matching events or a no-results empty state, not a generic error.
  - Year-from/year-to filters work with each event type and with `All Events`.
  - URL/form state remains consistent after each filter.
  - Tests cover UI value mapping to backend values.
  - Add a regression test for "year range + All Events" specifically.
- Follow-up questions:
  - Which exact dropdown options are shown in production: `All Events`, `Births`, `Deaths`, `Marriages`, or different labels?
  - Was the error shown as an inline page message, toast, browser alert, or HTMX target replacement?

## BUG-003: Research page returns mostly/only Antenati and sends users to useless/broken URLs

- Area: Research / external records
- Severity: P1
- Environment: production
- URL/page: Research page
- User report:
  - Searches only ever return results from Antenati, regardless of query.
  - Other sources appear broken or unavailable.
  - Clicking the Antenati URL leads to a certificate error.
  - The browser redirects to `https://antenati.cultura.gov.it/`, which is not useful because it requires the user to search again.
  - User reaction: the research page wastes time and feels useless in its current state.
- Reproduction detail:
  - Searches tried: `cutroni`, `maglio`.
  - Each search returned only one hit and led to the Antenati flow described above.
  - The product result quality should be compared against ordinary web search queries such as `maglio family` via Google or Brave Search API to establish a basic relevance baseline.
- Expected:
  - Research page should either return useful source-specific results or clearly mark sources as unavailable/not configured/beta.
  - Clicking a result should preserve enough query context that the destination is useful.
  - Broken/certificate-error URLs should not be presented as working results.
  - If a source is only a guided lookup, the UI should label it as such, not present it like a successful search result.
- Actual:
  - Antenati dominates results.
  - Antenati result URL appears stale/broken or redirects to an unhelpful home/search page.
  - Other sources do not appear to provide useful results.
- Product impact:
  - Research page undermines trust because it promises external discovery but does not deliver.
  - The feature competes poorly with established genealogy tools.
  - This should not be part of the main paid-product promise until fixed.
- PM recommendation:
  - Leave the Research page visible for now because the founder is the only intensive current user, but treat it as beta/low-confidence in planning.
  - Separate "real searchable sources" from "guided lookup links."
  - Add per-source health/config status in the UI.
  - Remove or fix Antenati link generation before exposing it to production users.
  - For unconfigured API-key sources, show "not configured" instead of silently returning nothing.
- Likely investigation areas:
  - Validate current Antenati base URL and query URL.
  - Confirm whether Chronicling America and NARA calls fail in production due to network, TLS, response parsing, CORS is not relevant server-side, or query behavior.
  - Confirm whether Trove, DPLA, and FamilySearch are intentionally unavailable without API keys.
  - Check whether result ranking always displays Antenati because link-style sources return a synthetic result even when true search sources return no hits.
  - Add source-level logging and UI status to distinguish no results from source errors.
- Suggested acceptance criteria for fix:
  - Research page labels itself beta/labs until at least two sources return useful results in production.
  - Antenati result either deep-links with preserved place/query context or is removed.
  - Source cards show `configured`, `not configured`, `error`, or `no results`.
  - Searches for a known test query return expected results from at least Chronicling America and NARA, or show a clear no-results state.
  - The UI never presents a stale/certificate-error link as a successful result.
- Follow-up questions:
  - Did the page show source-specific error messages for the non-Antenati sources, or did they simply not appear?
  - When this becomes user-facing beyond founder usage, should it be shown with a beta warning or hidden behind an admin/beta flag?

## Proposed Stabilization Sprint

### `S47a - Product Stabilization Before Commercialization`

Sprint goal: fix production-facing trust and usability issues before starting `S47 - Hosting and Tenant Architecture`.

Candidate packets to create:

| Candidate | Title | Priority | Source bug |
|---|---|---:|---|
| FB-130 | Overlay and Workspace Panel Interaction Contract | P2 | BUG-001 |
| FB-131 | Tree Sidebar Popout Collapse/Dock Fix | P1 | BUG-001 |
| FB-132 | Timeline Filter Consistency and Error-State Fix | P0 | BUG-002 |
| FB-133 | Research Page Beta Gating and Source Health UI | P1 | BUG-003 |
| FB-134 | External Research Source Link and Result Quality Fixes | P2 | BUG-003 |

Recommended order:

1. `FB-132` because the timeline has a concrete broken production flow.
2. `FB-133` because a misleading research page should be hidden or clearly labeled quickly.
3. `FB-131` as a targeted sidebar fix if low-risk.
4. `FB-134` if the research page remains visible and source status work shows a contained Antenati/link-quality fix.
5. `FB-130` as the design-system follow-through before adding more popouts/drawers/dialogs.

## External UI References for Investigation

- Floating UI: https://floating-ui.com/
- Shoelace web components: https://shoelace.style/
- Radix UI primitives: https://www.radix-ui.com/primitives

These are references for evaluation, not approved dependencies.
