# Task Packet - FB-076 Login and Invite Claim Error UX

## Objective

Improve error handling and messaging across the login and invite claim flows so users (and admins helping them) can understand exactly what went wrong and what to do next.

## Why / KPI

- When Google OAuth fails silently or the invite claim doesn't work, users see generic errors or blank redirects.
- The most common failure: Google email doesn't match the person record's email — user sees nothing helpful.
- Admin can't troubleshoot remotely without knowing what error the user hit.
- CFLSR depends on every invited family member being able to get in on the first try.

## Scope

- In scope:
  - Login page: show clear error messages for common failures:
    - "No account found for this Google email" (with hint to contact admin)
    - "Your account is suspended" (with hint to contact admin)
    - "Your account is pending approval"
  - Invite claim page: show specific errors:
    - Invite expired → "This invite expired on {date}. Ask {admin} for a new one."
    - Already claimed → "This invite was already used on {date}."
    - Revoked → "This invite was cancelled."
    - Google email mismatch → "Sign in with {expected_email} to claim this invite."
  - Pass error codes via URL query params (e.g., `/login?error=no_account`) so messages render server-side
  - Log failed login/claim attempts to AuditLog for admin visibility
  - i18n for all error messages across 5 locales
- Out of scope:
  - Rate limiting on failed attempts
  - Account lockout
  - Password reset (no passwords in the system)

## Task Type

- member-facing error UX + audit logging

## Likely Files

- `app/routes/auth.py` (error handling in OAuth callback and invite claim)
- `app/templates/login.html` (error message display)
- `app/templates/invite.html` (error message display)
- `locales/*.json` (error message keys)

## Acceptance Criteria

- [ ] Login page shows specific error messages for no-account, suspended, pending states.
- [ ] Invite claim page shows specific errors for expired, claimed, revoked, email-mismatch.
- [ ] Error messages include actionable hints (who to contact, what email to use).
- [ ] Failed login/claim attempts logged to AuditLog.
- [ ] i18n for all error messages across 5 locales.
- [ ] No regression on successful login/claim flows.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
