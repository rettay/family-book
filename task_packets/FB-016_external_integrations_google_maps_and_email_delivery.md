# Task Packet - FB-016 External Integrations: Google Maps and Email Delivery

## Objective

Add the first real external integrations to Family Book so the map experience becomes meaningfully better and invites or notifications can be delivered through actual email infrastructure.

## Why / KPI

- The current map is functional but thin compared to a real geographic browsing experience.
- Invites and notifications are product promises that should no longer depend on manual or placeholder delivery behavior.

Primary KPI:
- increase successful invite delivery and acceptance confidence.

Secondary KPI:
- improve usefulness of the map as a real exploration surface rather than a basic SVG visualization only.

## Scope

- In scope:
  - Google Maps integration for the map view
  - Resend integration for invite delivery
  - notification plumbing where required for the invite flow
  - operator configuration and fallback behavior for missing credentials
  - focused hardening tied to the new integration paths
- Out of scope:
  - broad rewrite of all map UX
  - generalized notification center
  - arbitrary third-party integrations beyond Google Maps and Resend

## Task Type

- external integration / delivery infrastructure packet

## Dependencies and Ordering Assumptions

- Best sequenced after Sprint 11 because the tree workspace is now the primary surface and external integrations are the next major product-value unlock.
- Should be paired with targeted hardening work so new provider dependencies do not lower release confidence.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - real invite delivery through Resend
  - map experience through Google Maps integration
  - runtime/operator contract for API keys and graceful fallback
- Should improve:
  - notification readiness for future member-facing updates
  - staging/manual review quality for integration behavior
- Must re-run:
  - focused pytest
  - Playwright
  - staging verification
  - CodeMap

## Implementation Notes

- Likely files:
  - `app/routes/auth_routes.py`
  - `app/services/auth_service.py`
  - `app/templates/map.html`
  - `app/static/js/map.js`
  - `app/config.py`
  - `docs/ops/railway-release-flow.md`
  - `tests/test_auth.py`
  - `tests/test_pages.py`
  - `tests/ui/playwright-flow-checks.sh`
- Validation commands:
  - `uv run pytest tests/test_auth.py tests/test_pages.py -q`
  - `make test-ui-playwright`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Acceptance Criteria

- [ ] Admin invite actions can deliver real emails through Resend in configured environments.
- [ ] Invite flows fail clearly and safely when Resend is not configured.
- [ ] The map view can use Google Maps in configured environments with graceful fallback when credentials are absent.
- [ ] Sprint 12 does not introduce new CodeMap failures.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Staging verification covers both integrations
- [ ] Focused tests and browser checks pass
