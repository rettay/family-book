# Task Packet - FB-122 Invite Visibility and Contribution Flow

Status: Done

## Objective

Make invitees understand their role, visibility, and first contribution opportunity.

## Why / KPI

Family Book becomes valuable when relatives contribute. Invites must be safe, understandable, and action-oriented.

## Scope

- In scope:
  - invite page role/visibility explanation
  - first contribution prompt after invite claim
  - role-aware landing state for viewer/member/steward
  - optional review queue for high-risk edits if enabled
  - invite analytics event
- Out of scope:
  - legal consent signatures
  - social feed
  - external contact import

## Likely Files

- `app/routes/auth_routes.py`
- `app/routes/pages.py`
- `app/templates/invite.html`
- `app/templates/tree.html`
- `app/access_control.py`
- `tests/test_auth.py`
- `tests/test_pages.py`
- `tests/test_access_control.py`

## Acceptance Criteria

- [x] Invite page states what the invitee can see and edit.
- [x] After claim, invitee lands on a relevant profile or contribution prompt.
- [x] Viewer/member/steward roles see different permitted actions.
- [x] High-risk edits are blocked or routed to review according to policy.
- [x] Invite conversion event is auditable.

## Validation Commands

- `uv run pytest tests/test_auth.py tests/test_pages.py tests/test_access_control.py -q`
- `make test-ui-playwright`
- `git diff --check`

## Evidence

- `app/routes/auth_routes.py`
- `app/routes/pages.py`
- `app/templates/invite.html`
- `app/templates/invite_first_steps.html`
- `tests/test_auth.py`
- `tests/test_pages.py`

## Definition of Done

- [x] Invited relatives know what to do and cannot over-contribute.
