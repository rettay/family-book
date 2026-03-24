# Task Packet - FB-002 Account, Invite, and Admin Foundation

## Objective

Build a reliable account and invite foundation so admins can onboard family members and manage the family boundary without manual database intervention.

## Why / KPI

- CFLSR cannot improve if invited family members cannot reliably enter the system.
- The family boundary is the core privacy boundary in the launch model.
- Account/admin controls are the prerequisite for safe flat shared access.

## Scope

- In scope:
  - explicit invite lifecycle
  - admin account-management flows
  - account-to-person linking rules
  - onboarding path for invited users
  - tests for invite, claim, login, and admin management flows
- Out of scope:
  - external social login beyond what is already necessary
  - map, tree filters, or rich content model expansion

## Constraints

- Do not require manual DB edits for normal invite and onboarding flows.
- Keep the family boundary explicit and inspectable.
- Preserve session security and authenticated media behavior.

## Implementation Notes

- Likely files:
  - `app/models/auth.py`
  - `app/models/person.py`
  - `app/routes/auth_routes.py`
  - `app/routes/pages.py`
  - `app/services/auth_service.py`
  - `app/templates/admin.html`
  - `app/templates/invite.html`
  - `tests/test_auth.py`
  - `tests/test_api.py`
- Validation commands:
  - `uv run pytest tests/test_auth.py tests/test_api.py -q`
  - targeted multi-user invite/login checks

## Evaluation Environment

- Task: account and invite workflow repair
- Verifier: API and page tests plus at least one end-to-end invite flow
- Reference/oracle: canonical product contract and collaboration/privacy docs
- Expected evidence: passing tests covering admin invite, member claim, login, and account management
- Known failure modes / reward hacks:
  - admin-only happy path passes while member onboarding still breaks
  - account record exists but is not linkable to a usable person profile
  - user can log in but still cannot reach shared content
- Verifiability class: `deterministic`

## Acceptance Criteria

- [ ] Admin can create and manage invites without manual database intervention.
- [ ] Invited user can claim access and sign in through a supported flow.
- [ ] Active invited user reaches shared family content after login.
- [ ] Admin can disable or remove an account through supported app flows.
- [ ] Automated tests cover invite creation, claim, login, and disabled-account behavior.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation commands are reproducible and passing
- [ ] No manual database workaround is required for the tested onboarding path

## Risk and Verification Notes

- Complexity hotspots:
  - account/person linking
  - token lifecycle
  - session state and disabled-account handling
- Shallow-pass risk:
  - tests only cover token creation but not the full onboarding transition
- Required verification depth:
  - positive path plus at least one rejected/disabled path
