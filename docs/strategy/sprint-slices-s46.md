# Sprint Slices - S46 Passwordless Auth and MXroute Email

## Slice Order

1. `S46-1 MXroute SMTP Delivery`
2. `S46-2 Magic Link Login Core`
3. `S46-3 Older-Relative Login and Admin Recovery UX`
4. `S46-4 Auth Observability and Guardrails`
5. `S46-5 Passkey Foundation`

## `S46-1 MXroute SMTP Delivery`

### Goal

Remove the Resend runtime dependency and make outbound invite/auth email work through MXroute SMTP.

### Scope

- email delivery abstraction for invite and magic-link messages
- SMTP/TLS send path using existing `SMTP_*` settings
- MXroute-oriented env documentation and admin status copy
- tests for configured, failed, and not-configured delivery states

### Acceptance Checks

- invites can be sent through SMTP when `SMTP_*` is configured
- missing SMTP config returns a non-blocking `not_configured` result
- Resend-specific env vars are no longer required for invite delivery
- admin status reflects SMTP/MXroute readiness rather than Resend readiness

## `S46-2 Magic Link Login Core`

### Goal

Enable known family members to request and consume one-time email sign-in links without Google or passwords.

### Scope

- `/auth/magic-link/request` route
- `/auth/magic-link/consume` route or equivalent GET/POST claim flow
- hashed, expiring, single-use tokens using the existing `MagicLinkToken` model
- generic responses that prevent account enumeration
- session creation with `AuthMethod.magic_link`

### Acceptance Checks

- active member can request a link and sign in through it
- unknown email receives the same public response but no credential is sent
- reused or expired magic links fail safely
- pending/suspended/deleted accounts cannot bypass account state through magic links

## `S46-3 Older-Relative Login and Admin Recovery UX`

### Goal

Make login and recovery obvious for non-technical relatives and give admins a safe support workflow.

### Scope

- login page primary email field with friendly copy
- Google sign-in retained as optional secondary action
- invite page copy aligned with the magic-link mental model
- admin "send sign-in link" and "copy one-time link" actions
- clear distinction between onboarding invite and recovery sign-in link
- desktop/mobile and English/Spanish auth surface coverage

### Acceptance Checks

- a relative sees one primary path: enter email, check inbox, click link
- admin can issue a fresh one-time sign-in link for an active person
- admin can issue a fresh invite link for a pending/unclaimed person
- old raw invite tokens are not reconstructed from storage
- UI copy does not imply passwords or Google are required

## `S46-4 Auth Observability and Guardrails`

### Goal

Make auth support diagnosable without exposing credentials or sensitive raw tokens.

### Scope

- audit events for magic-link request, send result, consume success/failure, invite copy/send, passkey registration/auth attempts
- rate limiting or equivalent throttling for magic-link request and consume endpoints
- admin-visible recent auth activity per person
- structured logs that include request metadata but not raw tokens

### Acceptance Checks

- admin can see whether an invite/sign-in email was sent, failed, or not configured
- repeated magic-link requests are throttled without revealing whether an account exists
- failed token consumption is logged without token value
- successful login updates `last_login_at` and session metadata

## `S46-5 Passkey Foundation`

### Goal

Add passwordless passkeys as a stronger, easier repeat-login option after email recovery works.

### Scope

- passkey credential data model and migration
- WebAuthn registration start/finish endpoints for logged-in users
- WebAuthn authentication start/finish endpoints from login page
- settings/admin visibility for registered passkeys
- progressive enrollment prompt after magic-link or invite login

### Acceptance Checks

- logged-in active member can register a passkey
- a member with a passkey can sign in without email or Google
- passkey auth creates the same session type and audit trail as other auth methods
- passkey failure does not strand the user because email magic link remains available

## Validation Baseline

- `uv run pytest tests/test_auth.py tests/test_config.py tests/test_email_delivery.py tests/test_pages.py -q`
- `uv run pytest tests/test_security_guardrails.py tests/test_phase1_edge_cases.py -q`
- `make test-ui-playwright`
- `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Recommended Builder Order

1. `FB-104`
2. `FB-105`
3. `FB-106`
4. `FB-108`
5. `FB-107`

This order makes SMTP and magic links the reliable fallback before passkeys. Passkeys improve repeat login, but email remains the recovery anchor for older relatives and account support.
