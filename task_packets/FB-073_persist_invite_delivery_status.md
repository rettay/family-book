# Task Packet - FB-073 Persist Invite Delivery Status

## Objective

Save invite email delivery results (sent/failed/not_configured, error message, Resend message ID) to the database so the admin can check delivery status later, not just at the moment of sending.

## Why / KPI

- Currently, invite delivery status is returned in the API response but not persisted. If the admin refreshes or comes back later, the delivery result is lost.
- Admin can't tell if an invite email bounced, was never configured, or was actually delivered.
- CFLSR degrades when admins think invites were sent but users never received them.

## Scope

- In scope:
  - Add delivery tracking columns to the Invite model: `delivery_status` (sent/failed/not_configured/pending), `delivery_error`, `delivery_message_id`, `sent_at`
  - Alembic migration for the new columns
  - Persist delivery result when sending invite email
  - Admin dashboard: show delivery status badge on each invite (Sent/Failed/Not sent)
  - Admin dashboard: show sent_at timestamp
  - Admin dashboard: allow re-sending a failed invite
  - Log invite creation and delivery to AuditLog
- Out of scope:
  - Webhook-based bounce tracking from Resend
  - Automatic retry on failure

## Task Type

- admin-facing reliability enhancement + data model

## Likely Files

- `app/models/auth.py` (add delivery columns to Invite)
- `alembic/versions/` (new migration)
- `app/routes/auth.py` (persist delivery result after sending, resend endpoint)
- `app/services/email_delivery.py` (return delivery metadata)
- `app/templates/admin.html` (delivery status badges, resend button)
- `app/routes/admin.py` (resend invite endpoint)

## Acceptance Criteria

- [ ] Invite model has delivery_status, delivery_error, delivery_message_id, sent_at columns.
- [ ] Delivery result persisted when invite email is sent.
- [ ] Admin dashboard shows delivery status (Sent/Failed/Not configured) per invite.
- [ ] Admin dashboard shows sent_at timestamp per invite.
- [ ] Admin can resend a failed invite via a "Resend" button.
- [ ] Invite creation logged to AuditLog.
- [ ] Migration runs cleanly.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] Migration applied
