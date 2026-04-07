# Sprint Plan - S46 Passwordless Auth and MXroute Email

## Sprint

- Name: `S46 - Passwordless Auth and MXroute Email`
- Status: Closed
- Primary packet: `FB-105 Magic Link Authentication`
- Supporting packets:
  - `FB-104 MXroute SMTP Email Delivery`
  - `FB-106 Low-Friction Login and Admin Recovery UX`
  - `FB-107 Passkey Authentication Foundation`
  - `FB-108 Auth Observability and Audit Trail`

## Sprint Goal

Replace Resend-specific invite delivery with MXroute SMTP and make Family Book login passwordless, recoverable, and understandable for older family members through magic links, optional passkeys, admin-issued one-time links, and clearer authentication audit trails.

## Why This Sprint

CFLSR starts with "invited active family members can sign in." The current runtime supports Google sign-in and one-time invite claim, but normal magic-link login is only partially present at the service/model layer and not exposed in routes or UI. Resend also adds an extra provider dependency now that the domain is hosted with MXroute. This sprint removes that stack complexity and makes email ownership the primary recovery path while keeping higher-confidence authentication options available.

## Research Context

- Passwords are intentionally out of scope for this sprint. They add storage, reset, stuffing, and support burden without improving the target family-member experience.
- Email magic links are the universal fallback because they match the existing invite and contact-email model.
- Passkeys should be offered after login as a convenience and stronger phishing-resistant authenticator, not required before a member understands the app.
- QR-style login should rely on passkey cross-device flows handled by platform authenticators, not a custom QR bearer-token system.
- Admin "copy link" should generate a new one-time credential and audit it. The app should not store raw old invite tokens just to make them retrievable later.

## Must-Have Outcomes

- Invite delivery no longer depends on Resend and works through configured MXroute SMTP credentials.
- A known active family member can request an email magic link and sign in without Google.
- Admin can help a family member recover access by sending or copying a fresh one-time sign-in link with clear audit logging.
- Login and invite screens give older relatives a single obvious path with friendly recovery states.
- Passkey data model and basic registration/authentication flow exist behind the passwordless foundation.
- Admin can see recent login, magic-link, invite, and delivery events well enough to troubleshoot "I cannot get in" reports.

## Acceptance Criteria

1. SMTP delivery supports MXroute using `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, and `SMTP_FROM`, and Resend-specific runtime requirements are removed or deprecated.
2. Magic-link request and consume routes are implemented with hashed, single-use, expiring tokens and generic request responses that do not enumerate accounts.
3. Login UI presents email magic link as the primary path, with Google as optional when configured and passkeys as an available enhancement once implemented.
4. Admin can generate a fresh one-time invite or sign-in link for a person and copy/send it without needing raw persisted tokens.
5. Passkey credential storage and WebAuthn registration/authentication paths are implemented or explicitly gated as unavailable until configured dependencies are present.
6. Audit logs capture successful and failed auth-relevant events with enough metadata for admin support without storing raw tokens.
7. Auth and invite browser coverage proves a family admin can invite/help a member and that a member can sign in and reach the tree.
8. i18n parity is maintained for auth/admin login copy across supported locales.

## In Scope

- MXroute SMTP delivery for invite and magic-link email
- generic email-delivery abstraction replacing provider-specific Resend coupling
- magic-link request, email, consume, and session creation flow
- admin-issued one-time sign-in links for support/recovery
- admin audit visibility for auth and delivery events
- passkey credential model and WebAuthn registration/authentication foundation
- login/invite/admin UI changes required for the new flows
- pytest and Playwright coverage for auth and invite paths

## Out of Scope

- password storage or password reset flows
- SMS login
- custom QR bearer-token login outside WebAuthn/passkey cross-device behavior
- multi-tenant account provisioning
- broad account-role redesign beyond existing admin/member semantics
- inbound email ingestion changes beyond preserving existing Envelope webhook behavior
- external identity providers beyond keeping current Google sign-in working

## Implementation Order

1. Execute `FB-104` to replace Resend-specific email sending with SMTP/MXroute-compatible delivery.
2. Execute `FB-105` to expose magic-link request/consume routes using the existing token model.
3. Execute `FB-106` to make the login/admin support UX usable for low-confidence relatives.
4. Execute `FB-108` to harden tracking, logging, throttling, and admin diagnostics around the new flows.
5. Execute `FB-107` to add passkey registration/authentication on top of the stable email recovery path.

## Proof Obligations

- The app must never persist raw invite or magic-link bearer tokens.
- Requesting a magic link must not disclose whether an email matches a person record.
- Consuming a token must be single-use and must fail after expiry or reuse.
- Admin-generated copyable links must be fresh, auditable, and revocable where practical.
- Login UI must remain clear on mobile and in Spanish for the auth/invite surfaces.
- A member can still use Google sign-in if configured and already linked.
- Email delivery failures must preserve manual link fallback rather than blocking admin workflow.

## Risks To Watch

- SMTP provider configuration can fail silently without an explicit send result and admin-visible error.
- Magic links can become an account-enumeration surface if responses or timing differ too much.
- Copyable admin links are support-friendly but act as bearer credentials; audit and short expiry are non-negotiable.
- Passkeys can confuse older users if presented before email fallback; placement must be progressive.
- WebAuthn libraries and browser behavior add integration complexity; do not block magic-link shipment on passkeys.

## Exit Target

Sprint 46 is complete when Family Book can invite and sign in family members without Resend or Google dependency, while preserving a stronger optional passkey path and giving admins enough visibility to recover common login failures without database intervention.

## Closeout

- Closed: 2026-04-07
- Auditor result: PASS WITH FOLLOW-UPS
- Completed packets: `FB-104`, `FB-105`, `FB-106`, `FB-107`, `FB-108`
- Verification:
  - `uv run pytest tests/test_auth.py tests/test_pages.py -q` -> `47 passed`
  - `uv run pytest tests/test_email_delivery.py tests/test_config.py tests/test_pages.py tests/test_auth.py tests/test_i18n.py tests/test_phase1_edge_cases.py tests/test_security_guardrails.py -q` -> `90 passed`
  - `uv run ruff check app/routes/auth_routes.py app/middleware/security.py tests/test_auth.py tests/test_pages.py` -> passed
  - `uv run python -m compileall app -q && bash -n tests/ui/playwright-flow-checks.sh` -> passed
  - `git diff --check` -> passed
  - Focused rendered auth/admin smoke passed with screenshots under `output/playwright/s46-auth-audit/screenshots/`
- Follow-up:
  - Full `tests/ui/playwright-flow-checks.sh` still needs separate stabilization; the S46 builder run timed out later in an existing person-create section before reaching admin.
  - FB-106 should keep a future visual-artifact follow-up for login-submitted and invite-page screenshots beyond the focused auth/admin smoke.
