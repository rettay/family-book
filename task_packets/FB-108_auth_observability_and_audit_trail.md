# Task Packet - FB-108 Auth Observability and Audit Trail

Status: Done

## Objective

Improve tracking, logging, and admin visibility for invite, magic-link, passkey, and session events without storing raw credentials.

## Why / KPI

When a relative says "I cannot get in," the admin needs actionable evidence: was an invite sent, did email fail, did a magic link get requested, was the link reused or expired, is the account pending, and are there active sessions? Better diagnostics reduce manual intervention and improve CFLSR while preserving credential hygiene.

## Scope

- In scope:
  - structured audit events for invite send/copy/resend/revoke, magic-link request/send/consume, passkey registration/auth/removal, login/logout/session revocation
  - rate limiting or throttling for auth request and token consume endpoints
  - admin-visible recent auth activity per person
  - delivery status metadata for SMTP email attempts
  - log messages that include person/invite/session IDs and coarse request metadata but never raw tokens or secrets
- Out of scope:
  - external observability vendor integration
  - email bounce webhooks
  - SIEM dashboards
  - fine-grained per-field privacy changes

## Task Type

- observability + admin support + security guardrails

## Dependencies and Ordering

- Depends on `FB-104` and `FB-105`.
- Can land before or after `FB-106`, but admin UI visibility should align with `FB-106`.
- Passkey event coverage may include placeholders until `FB-107` lands, but final S46 exit requires passkey coverage too.

## Likely Files

- `app/routes/auth_routes.py`
- `app/services/auth_service.py`
- `app/services/email_delivery.py`
- `app/services/audit_service.py`
- `app/templates/admin.html`
- `app/routes/pages.py`
- `app/middleware/rate_limit.py`
- `tests/test_auth.py`
- `tests/test_phase1_edge_cases.py`
- `tests/test_security_guardrails.py`
- `tests/test_pages.py`

## Evaluation Environment

- Task: prove auth-relevant events are observable and rate-limited without credential leakage.
- Verifier: pytest API tests, DB audit assertions, and admin page rendering tests.
- Reference/oracle: each auth transition creates an audit record with event type and safe metadata; repeated requests are throttled; no raw token appears in audit/log fields.
- Expected evidence: focused pytest output and a short matrix of event types covered.
- Known failure modes / reward hacks: logging raw bearer tokens; audit only on success; rate limit reveals account existence; admin UI only shows last login and hides recent failures.
- Verifiability class: deterministic.
- Context policy: store event matrix in packet evidence or sprint closeout, not in code comments.

## Acceptance Criteria

- [x] Successful Google, invite, magic-link, and passkey logins update `last_login_at` and create audit entries.
- [x] Failed magic-link consume attempts create safe audit/log records without raw token values.
- [x] Magic-link request endpoint is throttled by request key without account enumeration.
- [x] Invite send/copy/resend/revoke events are auditable with actor, target person, delivery status, and credential type.
- [x] Admin page exposes recent auth/support activity enough to diagnose common login failures.
- [x] Session revocation and logout events remain auditable.
- [x] Tests assert raw tokens and SMTP secrets are not stored in audit values.
- [x] Event naming is documented or centralized enough for future auth methods.

## Validation Commands

- `uv run pytest tests/test_auth.py tests/test_phase1_edge_cases.py tests/test_security_guardrails.py tests/test_pages.py -q`
- `uv run pytest tests/test_email_delivery.py -q`
- `make test-ui-playwright`

## Definition of Done

- [x] Acceptance criteria satisfied.
- [x] Event matrix covers invite, magic-link, passkey, and session lifecycle.
- [x] Admin can diagnose delivery/auth state without database access.
- [x] Logs and audit records do not contain raw bearer tokens or provider secrets.

## Risk and Verification Notes

- Complexity hotspots: rate-limit key design, account enumeration, audit-table noise, admin UI density.
- Likely shallow-pass failure mode: audit only successful events and misses failure/recovery paths.
- Required verification depth: negative tests for throttling and token redaction.
- Wrong-variant evidence expected: intentionally invalid token should produce safe failure event only.

## Execution Budget

- Builder may reuse existing middleware patterns for throttling if present.
- Escalate before adding a new observability service or changing retention policy.
- Material scope drift: broad analytics dashboards or global notification system.
