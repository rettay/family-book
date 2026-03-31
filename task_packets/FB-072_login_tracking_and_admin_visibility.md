# Task Packet - FB-072 Login Tracking and Admin Visibility

## Objective

Add last_login_at timestamp to person records, log login/logout events to the audit trail, and surface login activity on the admin dashboard so the admin can see who has actually accessed the app.

## Why / KPI

- Admin has no way to know if a family member has ever logged in. People claim "trouble" but admin can't verify.
- Session data (IP, user-agent, last_used) exists but is invisible to the admin.
- CFLSR depends on the admin being able to diagnose access issues for family members.

## Scope

- In scope:
  - Add `last_login_at` datetime column to Person model (Alembic migration)
  - Update `last_login_at` on every successful login (Google OAuth callback, invite claim)
  - Log login events to AuditLog (action="login", entity_type="session", with IP and auth_method)
  - Log logout events to AuditLog (action="logout")
  - Admin dashboard: show "Last login" column in the accounts/people table
  - Admin dashboard: show active session count per person
  - Sort people by last_login_at so admin can see who's active vs. never logged in
- Out of scope:
  - Failed login tracking / rate limiting
  - Per-session management UI (revoke individual sessions)
  - New auth methods

## Task Type

- admin-facing visibility enhancement + data model

## Likely Files

- `app/models/person.py` (add last_login_at column)
- `alembic/versions/` (new migration)
- `app/routes/auth.py` (update last_login_at on login, log audit events)
- `app/services/auth_service.py` (capture login metadata)
- `app/models/audit.py` (verify action types cover login/logout)
- `app/templates/admin.html` (login activity column, session counts)
- `app/routes/admin.py` (query session counts, last login data)

## Acceptance Criteria

- [ ] Person model has `last_login_at` datetime column.
- [ ] `last_login_at` updates on every successful Google OAuth login and invite claim.
- [ ] AuditLog entry created for each login (action="login", includes IP and auth_method).
- [ ] AuditLog entry created for each logout (action="logout").
- [ ] Admin dashboard shows "Last login" for each person in the accounts table.
- [ ] Admin dashboard shows active session count per person.
- [ ] People with no login show "Never" or similar indicator.
- [ ] Migration runs cleanly.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] Migration applied
