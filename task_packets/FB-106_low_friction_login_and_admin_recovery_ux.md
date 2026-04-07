# Task Packet - FB-106 Low-Friction Login and Admin Recovery UX

Status: Done

## Objective

Redesign the login and admin account-support flows so older relatives have one obvious email-based path and admins can safely issue fresh one-time links.

## Why / KPI

The product succeeds only if invited relatives can get into the shared family space without a support loop. Google-only login is too narrow, while raw invite-link recovery is currently confusing because old invite tokens are not reconstructable. This packet turns the passwordless backend into a clear user journey and gives the admin a safe support workflow.

## Scope

- In scope:
  - login page primary email magic-link form
  - clear "check your inbox" and expired/reused-link states
  - Google sign-in retained as optional secondary action when configured
  - admin actions for "Send sign-in link" and "Copy one-time sign-in link"
  - clear separation between onboarding invite links and recovery sign-in links
  - copy and layout for desktop/mobile and English/Spanish auth surfaces
  - Playwright coverage for admin invite/help and member login paths
- Out of scope:
  - passkey UI beyond placeholder/enrollment handoff if `FB-107` has not landed
  - passwords
  - storing/retrieving old raw invite tokens
  - SMS or phone support

## Task Type

- member/admin-facing UX + auth workflow

## Dependencies and Ordering

- Depends on `FB-104` and `FB-105`.
- Should land before `FB-107` UI is emphasized, so passkeys are progressive rather than required.

## Likely Files

- `app/templates/login.html`
- `app/templates/invite.html`
- `app/templates/admin.html`
- `app/routes/pages.py`
- `app/routes/auth_routes.py`
- `app/static/css/main.css`
- `locales/en.json`
- `locales/es.json`
- `locales/it.json`
- `locales/ru.json`
- `locales/zh.json`
- `tests/test_pages.py`
- `tests/test_auth.py`
- `tests/ui/playwright-flow-checks.sh`

## Evaluation Environment

- Task: prove that auth/invite UI supports a complete low-friction login/support flow.
- Verifier: pytest template/API tests plus Playwright release-confidence checks.
- Reference/oracle: family admin can issue/copy a fresh link; family member can request and consume a magic link; login UI does not imply Google is mandatory.
- Expected evidence: focused pytest output, Playwright pass, screenshots/artifacts for login/admin/invite surfaces.
- Known failure modes / reward hacks: DOM form exists but no visible primary CTA; "copy link" silently creates wrong credential type; old invite tokens are implied retrievable.
- Verifiability class: bounded-judgment due to UI clarity, with deterministic route assertions.
- Context policy: preserve screenshots in Playwright artifact directory, summarize only key visual states.

## Member-Facing UI Requirements

- Changed surfaces: `auth_and_invites`, `admin_and_settings`.
- Target personas: `family_admin`, `contributing_member`.
- Safety persona: `mobile_first_relative`.
- Required scenarios: `admin_invites_member`, `member_accepts_invite_and_signs_in`, `manage_accounts_or_policy`.
- Required viewports: desktop and mobile.
- Required locales: `en`, `es`.
- Structural oracle: CodeMap/static review confirms login/admin/invite routes, templates, i18n, and auth service wiring are complete.
- Browser oracle: Playwright proves admin sends/copies link and member reaches `/tree` through email-link flow.
- Visual/persona oracle: screenshots show one primary email path, optional Google, readable mobile layout, and clear admin action labels.
- Required artifacts: Playwright screenshots for login, login submitted state, invite page, admin accounts section.

## Acceptance Criteria

- [x] `/login` presents email magic-link login as the primary action.
- [x] Google sign-in remains available only as a secondary option when configured.
- [x] Login request success copy is generic and instructs the member to check email without revealing account existence.
- [x] Admin can send a fresh sign-in link for an active person.
- [x] Admin can copy a fresh one-time sign-in link for support and the action is audited.
- [x] Admin invite controls clearly distinguish "Invite" from "Sign-in link" or equivalent recovery wording.
- [x] Existing open invite rows no longer imply old raw invite links can be retrieved; fresh link generation is explicit.
- [x] Mobile login and admin account controls are visible and not clipped.
- [x] English and Spanish auth/admin copy pass i18n parity.

## Validation Commands

- `uv run pytest tests/test_pages.py tests/test_auth.py tests/test_email_delivery.py -q`
- `uv run pytest tests/test_i18n.py -q`
- `make test-ui-playwright`
- `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Definition of Done

- [x] Acceptance criteria satisfied.
- [x] Browser evidence covers family admin and member personas.
- [x] Admin support path does not expose stored raw tokens and does not require database intervention.

## Risk and Verification Notes

- Complexity hotspots: avoiding token leakage in copy-to-clipboard fallback, preserving safe redirects, keeping admin actions understandable.
- Likely shallow-pass failure mode: adding a form but leaving Google visually dominant.
- Required verification depth: rendered UI plus end-to-end sign-in.
- Negative-case evidence expected: reused/expired link copy leads to friendly recovery copy.

## Execution Budget

- Builder may adjust copy and layout to fit existing design system.
- Escalate before adding any custom QR login or storing raw invite tokens.
- Material scope drift: redesigning the entire admin dashboard beyond account auth controls.
