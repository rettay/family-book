# Sprint Plan - S12 External Integrations and Confidence Hardening

## Sprint

- Name: `S12 - External Integrations and Confidence Hardening`
- Status: Closed
- Primary packet: `FB-016 External Integrations: Google Maps and Email Delivery`
- Supporting packet: `FB-014 Architecture and Maintainability Hardening`

## Sprint Goal

Introduce the next high-value product integrations while preserving release confidence by pairing Google Maps and Resend delivery work with targeted hardening of the central modules CodeMap still flags.

## Why This Sprint

Sprint 11 made the tree the primary workspace. The next product-visible gains are external: a materially better map experience and real email delivery for invites and notifications. At the same time, CodeMap still points to structural debt in access control, schemas, and observability. Sprint 12 should combine these tracks so the integrations land on a safer base.

## Must-Have Outcomes

- Google Maps is integrated into the map experience with safe fallback behavior.
- Invite delivery works through Resend in configured environments.
- The runtime/operator contract for integration credentials is explicit and testable.
- Central CodeMap risk in `app/access_control.py` and `app/schemas.py` is reduced through direct coverage.

## Acceptance Criteria

1. Configured environments can send Family Book invites through Resend.
2. Unconfigured environments fail gracefully without breaking invite-management UX.
3. The map surface can render through Google Maps in configured environments with a truthful fallback path when credentials are absent.
4. Focused tests cover the central access/schema behaviors supporting Sprint 12.
5. CodeMap remains passing overall with no new failures.
6. Browser and staging review evidence remain part of the promotion gate.

## In Scope

- Google Maps integration
- Resend invite delivery and related notification groundwork
- configuration, fallback, and operator-contract updates for external integrations
- focused hardening for `app/access_control.py`, `app/schemas.py`, and related critical modules
- focused pytest, Playwright, CodeMap, and staging/manual review

## Out of Scope

- broad map redesign beyond the provider integration step
- generalized notification center or messaging system
- large architecture rewrite unrelated to Sprint 12 integrations
- unrelated backlog cleanup not tied to integration confidence

## Implementation Order

1. Execute Slice 1: Google Maps foundation and fallback contract.
2. Execute Slice 2: Resend invite delivery and notification contract.
3. Execute Slice 3: targeted hardening for CodeMap residual risk and promotion confidence.
4. Validate through focused tests, browser checks, CodeMap, and staging/manual review.

## Risks To Watch

- leaking provider-specific assumptions into local or self-hosted fallback behavior
- shipping email delivery without clear failure reporting in admin flows
- adding integration complexity without shoring up the central access/schema modules that gate correctness
- letting Sprint 12 sprawl into a broad platform rewrite

## Exit Target

Sprint 12 is complete when Family Book can deliver real invites, offer a meaningfully stronger map surface through Google Maps, and carry those integrations on a tested, CodeMap-clean-enough base.

## Closeout Result

- Exit result: `pass`
- Builder implemented the external integration layer and the audit follow-up on `main`
- Auditor initially flagged Google Maps keyboard regression, unescaped invite email HTML, and non-retryable Google loader failures
- Builder corrected those issues and added focused regression coverage for escaped outbound email content and the configured Google Maps keyboard path
- Focused closeout baseline:
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run pytest tests/test_email_delivery.py tests/test_auth.py tests/test_pages.py tests/test_config.py tests/test_access_control.py tests/test_schema_models.py -q`
  - result: `52 passed`
  - `make test-ui-playwright`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`
