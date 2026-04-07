# Task Packet - FB-107 Passkey Authentication Foundation

Status: Done

## Objective

Add passkey/WebAuthn registration and authentication as an optional passwordless repeat-login method.

## Why / KPI

Magic links solve recovery, but passkeys can make repeat login easier and stronger for members on supported devices. They avoid local passwords while using platform authenticators such as device PIN, Face ID, Touch ID, or password-manager passkeys. For older relatives, passkeys should be a convenience after successful email login, not a hard gate.

## Scope

- In scope:
  - passkey credential model and Alembic migration
  - WebAuthn registration start/finish endpoints for logged-in active members
  - WebAuthn authentication start/finish endpoints from login page
  - credential challenge storage with expiry and replay protection
  - settings or login UI affordance for passkey enrollment/authentication
  - audit logging for registration and authentication outcomes
- Out of scope:
  - custom QR login outside platform passkey cross-device behavior
  - replacing magic links
  - enterprise device management
  - password fallback

## Task Type

- auth/security foundation + member-facing progressive enhancement

## Dependencies and Ordering

- Depends on `FB-105` for email fallback.
- Should land after `FB-106` so passkey enrollment is progressive and not confusing.
- May require adding a WebAuthn library; dependency choice must be explicit and justified.

## Likely Files

- `app/models/auth.py`
- `alembic/versions/`
- `app/services/auth_service.py`
- `app/routes/auth_routes.py`
- `app/templates/login.html`
- `app/templates/settings.html`
- `app/static/js/main.js`
- `locales/en.json`
- `locales/es.json`
- `locales/it.json`
- `locales/ru.json`
- `locales/zh.json`
- `tests/test_auth.py`
- `tests/test_security_guardrails.py`
- `tests/test_pages.py`

## Evaluation Environment

- Task: verify passkey credential lifecycle and auth path with deterministic server-side tests plus browser capability smoke.
- Verifier: pytest for challenge/credential logic, mocked WebAuthn verification where needed, and browser UI smoke that passkey controls are progressive and fallback remains visible.
- Reference/oracle: registration stores a public credential only; authentication validates challenge and creates session; email fallback remains available.
- Expected evidence: migration check, pytest output, and UI smoke notes.
- Known failure modes / reward hacks: storing private key material; passkey button blocks login on unsupported browser; challenge reusable; no origin/RP ID validation.
- Verifiability class: deterministic for server logic, bounded-judgment for browser UX.
- Context policy: keep dependency and WebAuthn verification details in implementation notes; avoid overloading main thread with spec excerpts.

## Acceptance Criteria

- [x] Passkey credential table stores public-key credential data, user/person reference, sign count or equivalent, created/last-used metadata, and display label.
- [x] Registration requires an active logged-in user and validates challenge, origin, and RP ID.
- [x] Authentication validates challenge, origin, RP ID, and credential ownership before creating a session.
- [x] Challenge values expire and cannot be reused.
- [x] Login page exposes passkey sign-in without hiding email magic-link fallback.
- [x] A logged-in user can remove or manage their registered passkeys.
- [x] Audit events record passkey registration, removal, successful auth, and failed auth without credential secrets.
- [x] Tests cover success, replay, wrong credential/person, and disabled/suspended account cases.

## Validation Commands

- `uv run pytest tests/test_auth.py tests/test_security_guardrails.py tests/test_pages.py -q`
- `uv run pytest tests/test_i18n.py -q`
- `make test-ui-playwright`
- `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Definition of Done

- [x] Acceptance criteria satisfied.
- [x] No passwords or private key material are introduced.
- [x] Magic-link fallback remains visibly available.
- [x] WebAuthn dependency and runtime config are documented.

## Risk and Verification Notes

- Complexity hotspots: RP ID/origin config, browser support, challenge state, dependency API correctness.
- Likely shallow-pass failure mode: UI button exists but server verification is mocked in production path.
- Required verification depth: wrong-variant tests for replay and wrong credential/person.
- Negative-case evidence expected: unsupported browser or passkey failure leaves email sign-in path usable.

## Execution Budget

- Builder may propose a focused WebAuthn dependency and document tradeoffs.
- Escalate if dependency size, maintenance, or platform support is unclear.
- Material scope drift: custom QR login, account recovery by passkey alone, or password introduction.
