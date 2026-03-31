# Task Packet - FB-074 Admin Session Visibility

## Objective

Surface active session data on the admin dashboard so the admin can see who is currently logged in, from which devices, and when each session was last active.

## Why / KPI

- UserSession already captures IP, user_agent, last_used, and created_at — but none of this is visible to the admin.
- Admin needs to verify "are they actually logged in?" when debugging access issues.
- Seeing device/browser info helps diagnose "it doesn't work on my phone" reports.

## Scope

- In scope:
  - API endpoint: GET /api/admin/sessions (list active sessions grouped by person)
  - Admin dashboard: expandable session detail per person showing device, IP, last used, created
  - Parse user_agent into a human-readable device string (e.g., "Chrome on macOS", "Safari on iPhone")
  - Show session age (e.g., "Active 2 hours ago", "Active 3 days ago")
  - Admin action: revoke a specific session (DELETE /api/admin/sessions/{id})
  - Admin action: revoke all sessions for a person ("Log out everywhere")
- Out of scope:
  - User-facing session management (users managing their own sessions)
  - GeoIP location lookup from IP addresses

## Task Type

- admin-facing visibility + management

## Likely Files

- `app/routes/admin.py` (session list endpoint, revoke endpoints)
- `app/templates/admin.html` (session visibility UI)
- `app/services/auth_service.py` (session revocation, user-agent parsing)

## Acceptance Criteria

- [ ] Admin dashboard shows active session count per person.
- [ ] Admin can expand to see individual sessions with device, IP, last used.
- [ ] User-agent is parsed into a readable device description.
- [ ] Session age shown as relative time ("2 hours ago").
- [ ] Admin can revoke a specific session.
- [ ] Admin can revoke all sessions for a person.
- [ ] Revoking a session immediately invalidates it (next request gets 401).

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] No regression on existing auth flow
