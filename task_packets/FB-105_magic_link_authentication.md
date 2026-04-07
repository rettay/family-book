# Task Packet - FB-105 Magic Link Authentication

Status: Done

## Objective

Expose a complete email magic-link login flow so active family members can sign in without Google or passwords.

## Why / KPI

Older relatives may not have or understand Google sign-in. Email ownership is already the account matching anchor through `contact_email`, and the repo already has `MagicLinkToken` storage helpers that are not wired to routes or UI. Completing this flow directly improves the first step of CFLSR: sign in without manual intervention.

## Scope

- In scope:
  - magic-link request route accepting an email address
  - magic-link consume route/page that validates a raw token, creates a session, and redirects safely
  - token hashing, single-use semantics, expiry, and account-state checks
  - generic public responses that do not disclose account existence
  - email content for magic-link delivery via `FB-104` SMTP delivery
  - audit events for request, send result, consume success, and consume failure
- Out of scope:
  - passkeys (`FB-107`)
  - admin support UI (`FB-106`)
  - SMS or passwords
  - custom QR login

## Task Type

- auth backend + member-facing login foundation

## Dependencies and Ordering

- Depends on `FB-104` SMTP delivery abstraction.
- Should precede `FB-106`, because login UX depends on these endpoints.
- Must preserve existing Google and invite-claim flows.

## Likely Files

- `app/routes/auth_routes.py`
- `app/services/auth_service.py`
- `app/services/email_delivery.py`
- `app/models/auth.py`
- `app/templates/login.html`
- `locales/en.json`
- `locales/es.json`
- `locales/it.json`
- `locales/ru.json`
- `locales/zh.json`
- `tests/test_auth.py`
- `tests/test_phase1_edge_cases.py`
- `tests/test_email_delivery.py`

## Evaluation Environment

- Task: verify passwordless magic-link creation and consumption.
- Verifier: pytest API tests using mocked email delivery plus DB assertions on `MagicLinkToken`.
- Reference/oracle: active known email creates a token and sends a link; unknown email produces the same public response but no token; used/expired tokens fail.
- Expected evidence: focused pytest output and notes on token DB assertions.
- Known failure modes / reward hacks: route signs in pending/suspended users; endpoint leaks unknown-account state; raw token stored; token reusable.
- Verifiability class: deterministic.
- Context policy: no live email delivery required.

## Acceptance Criteria

- [x] `POST /auth/magic-link/request` or equivalent accepts an email and always returns a generic success-style response.
- [x] Known active contact email creates exactly one fresh hashed token and sends a magic-link email.
- [x] Unknown email, suspended person, deleted person, or disallowed pending state does not disclose account existence.
- [x] Token consume endpoint creates a session using `AuthMethod.magic_link`, updates `last_login_at`, and redirects to a safe `return_to` or `/tree`.
- [x] Magic links are single-use and fail after `used_at` is set.
- [x] Expired magic links fail with a helpful user-facing message.
- [x] Raw magic-link tokens are never persisted or logged.
- [x] Existing Google and invite-claim tests still pass.

## Validation Commands

- `uv run pytest tests/test_auth.py tests/test_phase1_edge_cases.py tests/test_email_delivery.py -q`
- `uv run pytest tests/test_security_guardrails.py -q`
- `bash -n tests/ui/playwright-flow-checks.sh`

## Definition of Done

- [x] Acceptance criteria satisfied.
- [x] Magic-link flow is usable through API routes and ready for login UI in `FB-106`.
- [x] Tests prove no account enumeration, no token reuse, and no account-state bypass.

## Risk and Verification Notes

- Complexity hotspots: account matching by encrypted contact email hash, pending-account behavior under `REQUIRE_APPROVAL`, safe redirect handling.
- Likely shallow-pass failure mode: service helper exists but no route/UI path can actually send and consume a link.
- Required verification depth: negative tests for unknown, expired, reused, suspended, and pending states.
- Wrong-variant evidence expected: token replay must fail.

## Execution Budget

- Builder may adjust `MagicLinkToken` fields if indexes or metadata are needed.
- Escalate before changing account lifecycle policy.
- Material scope drift: adding passkeys, passwords, or unrelated account registration.
