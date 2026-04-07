# Task Packet - FB-104 MXroute SMTP Email Delivery

Status: Done

## Objective

Replace Resend-specific invite delivery with a generic SMTP email delivery path configured for MXroute.

## Why / KPI

CFLSR depends on family members receiving invites and sign-in links. The current invite code is tied to Resend even though the deployment already has SMTP-style settings and the domain is now hosted through MXroute. Removing Resend from the critical path simplifies the stack and gives the app one email contract that can support invites and magic links.

## Scope

- In scope:
  - introduce an email-delivery abstraction that can send invite-style HTML/text mail through SMTP
  - use `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, and `SMTP_FROM`
  - support STARTTLS on `587` and SSL/TLS on `465` based on port/config
  - preserve `InviteDeliveryResult` shape or replace it with a backward-compatible delivery result
  - update admin status copy from Resend-specific to SMTP/MXroute-ready/manual fallback
  - deprecate or remove Resend env requirements from `.env.example` and config flags
  - keep manual invite-link fallback when SMTP is not configured or fails
- Out of scope:
  - inbound email webhook changes
  - bounce webhooks
  - DNS automation for MXroute
  - magic-link routes; those are `FB-105`

## Task Type

- integration + admin-facing reliability

## Dependencies and Ordering

- Depends on current invite delivery status model from prior auth visibility work.
- Must land before `FB-105` so magic-link emails reuse the same SMTP delivery contract.
- May preserve deprecated `RESEND_*` fields for one release only if removing them would be risky, but runtime must no longer require them.

## Likely Files

- `app/services/email_delivery.py`
- `app/config.py`
- `.env.example`
- `app/routes/pages.py`
- `app/templates/admin.html`
- `locales/en.json`
- `locales/es.json`
- `locales/it.json`
- `locales/ru.json`
- `locales/zh.json`
- `tests/test_config.py`
- `tests/test_email_delivery.py`
- `tests/test_pages.py`

## Evaluation Environment

- Task: verify SMTP-based invite email delivery behavior and admin status copy.
- Verifier: unit tests with mocked SMTP client plus admin page rendering tests.
- Reference/oracle: configured SMTP returns `sent` with provider `smtp`; missing config returns `not_configured`; failed SMTP returns `failed` with no raw secrets leaked.
- Expected evidence: pytest output and a concise note identifying the mocked SMTP cases.
- Known failure modes / reward hacks: tests only checking env parsing while invite sending still calls Resend; errors leaking SMTP password; admin UI still says Resend.
- Verifiability class: deterministic.
- Context policy: no live MXroute credentials required; live SMTP send is optional manual smoke only.

## Acceptance Criteria

- [x] Invite email sending uses SMTP when `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, and `SMTP_FROM` are configured.
- [x] SMTP provider result records provider as `smtp` or `mxroute_smtp`, not `resend`.
- [x] Missing SMTP config preserves a manual-link fallback and returns `not_configured`.
- [x] SMTP connection/auth/send failures return `failed` without exposing `SMTP_PASS`.
- [x] Admin dashboard invite-delivery status copy no longer references Resend as the active provider.
- [x] `.env.example` documents MXroute-oriented SMTP settings and removes or marks Resend settings as deprecated.
- [x] Existing invite creation/resend API response shape remains compatible for the admin frontend.
- [x] Tests cover configured, not-configured, and failure states.

## Validation Commands

- `uv run pytest tests/test_email_delivery.py tests/test_config.py tests/test_pages.py -q`
- `uv run pytest tests/test_auth.py -q`
- `bash -n tests/ui/playwright-flow-checks.sh`

## Definition of Done

- [x] Acceptance criteria satisfied.
- [x] No code path requires `RESEND_API_KEY` for invite delivery.
- [x] Manual fallback still returns a copyable invite URL when SMTP is unavailable.
- [x] Tests pass with SMTP mocked and no live provider secrets required.

## Risk and Verification Notes

- Complexity hotspots: async/sync SMTP choice, TLS mode by port, avoiding secret leakage in errors.
- Likely shallow-pass failure mode: replacing labels but leaving `httpx.post("https://api.resend.com/emails")`.
- Required verification depth: inspect call path and assert no Resend HTTP call remains in invite delivery.
- Negative-case evidence expected: auth failure or send failure returns `failed` and preserves admin workflow.

## Execution Budget

- Builder may choose stdlib `smtplib` wrapped in a thread or an async SMTP dependency if already acceptable in the project.
- Escalate before adding a heavy new dependency or changing deploy secrets outside `.env.example`.
- Material scope drift: inbound mail, bounce tracking, or full notification redesign.
