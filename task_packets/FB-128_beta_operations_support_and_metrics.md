# Task Packet - FB-128 Beta Operations, Support, and Metrics

Status: Proposed

## Objective

Create the operational playbook for the first paid beta customers.

## Why / KPI

Paid users will need help with login, imports, media, billing, export, and privacy. Support cannot depend on the founder remembering production details.

## Scope

- In scope:
  - support runbook for auth, invites, billing, export, backup restore, media upload, and privacy settings
  - beta cohort tracker
  - activation and retention dashboard spec
  - refund/cancellation process
  - customer interview script and feedback tagging
  - incident response basics
- Out of scope:
  - full helpdesk integration
  - SOC 2 process
  - enterprise SLA

## Likely Files

- `docs/ops/beta-operations-runbook.md`
- `docs/ops/support-playbook.md`
- `docs/ops/metrics-dictionary.md`
- `docs/ops/incident-response-lite.md`
- `app/services/audit_service.py`
- `tests/test_audit.py`

## Acceptance Criteria

- [ ] Support runbook covers the common paid-beta failure modes.
- [ ] Metrics dictionary defines activation, retention, invite, upload, prompt, export, and billing events.
- [ ] Refund/cancel/export workflow is documented.
- [ ] Incident response flow names owner, severity, customer comms, and rollback steps.
- [ ] Feedback loop captures why users pay, churn, or get stuck.

## Validation Commands

- `git diff --check`

## Definition of Done

- [ ] Paid beta can be operated without ad hoc heroics.
