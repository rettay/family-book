# Task Packet - FB-075 Resend Setup and Invite Email Polish

## Objective

Ensure Resend email delivery is properly configured and working, create a polished invite email template, and improve the invite claim flow with clear error messages.

## Why / KPI

- Resend integration exists in code but may not be configured in production (Railway env vars).
- The invite email content is minimal — a branded, welcoming email would increase claim rates.
- When invite claim fails (expired, wrong Google account, already claimed), error messages are unclear.
- CFLSR depends on family members successfully receiving and claiming their invites.

## Scope

- In scope:
  - Verify Resend env vars are set in Railway production (RESEND_API_KEY, RESEND_FROM_EMAIL)
  - Create a polished HTML invite email template with:
    - Family name / branding
    - Clear "Join your family tree" call-to-action button
    - Invite link
    - Expiry notice ("This link expires in 30 days")
    - Who invited them
  - Improve invite claim page error messages:
    - "This invite has expired" (with contact admin hint)
    - "This invite was already claimed"
    - "This invite has been revoked"
    - "Sign in with the Google account matching your invite" (email mismatch hint)
  - Admin dashboard: show Resend delivery mode (configured/not configured) clearly
  - Add a "Copy invite link" button for manual sharing when email isn't configured
- Out of scope:
  - Additional email types (welcome, notifications)
  - Email templates for non-invite purposes
  - Alternative email providers

## Task Type

- admin/member-facing email delivery + UX

## Likely Files

- `app/services/email_delivery.py` (email template, HTML body)
- `app/routes/auth.py` (invite claim error messages)
- `app/templates/invite.html` (claim page error display)
- `app/templates/admin.html` (Resend status, copy link button)
- Railway environment variables (RESEND_API_KEY, RESEND_FROM_EMAIL)
- `locales/*.json` (error message i18n)

## Acceptance Criteria

- [ ] Resend env vars verified in production (or documented for user to set).
- [ ] Invite email uses a polished HTML template with branding and CTA.
- [ ] Invite email includes who sent the invite and expiry notice.
- [ ] Invite claim page shows clear error messages for expired/claimed/revoked/email-mismatch.
- [ ] Admin dashboard clearly shows Resend delivery status.
- [ ] Admin can copy invite link for manual sharing.
- [ ] i18n for error messages across 5 locales.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] i18n parity maintained
- [ ] Invite email tested with Resend (or documented setup steps if keys not available)
