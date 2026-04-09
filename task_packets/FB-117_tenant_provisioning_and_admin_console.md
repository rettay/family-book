# Task Packet - FB-117 Tenant Provisioning and Operator Console

Status: Done

## Objective

Add the minimum operator capability to create, inspect, suspend, reactivate, and delete hosted archives.

## Why / KPI

Paid hosting cannot rely on manual shell edits forever. Even if each archive is single-tenant, the operator needs consistent lifecycle controls.

## Scope

- In scope:
  - hosted archive registry model or external registry file/service
  - create/suspend/reactivate/delete lifecycle
  - owner email, base URL, plan state, storage path, backup state, and support metadata
  - safe support console that avoids private content by default
  - audit events for lifecycle actions
- Out of scope:
  - full pooled tenant runtime
  - CRM/helpdesk integration
  - automated cloud account creation unless chosen by `FB-109`

## Likely Files

- `app/models/hosted_archive.py`
- `app/routes/hosted_platform.py`
- `app/services/hosted_archive_service.py`
- `app/templates/operator.html`
- `tests/test_operator.py`
- `docs/ops/billing-runbook.md`

## Acceptance Criteria

- [x] Operator can create a new archive record with owner and plan.
- [x] Operator can suspend/reactivate archive access without deleting data.
- [x] Operator can mark deletion/export workflow states.
- [x] Support view shows health, plan, storage, backup, and auth status without private content.
- [x] All lifecycle transitions are audited.
- [x] Unsupported lifecycle states are rejected instead of being stored as live bypass values.

## Validation Commands

- `uv run pytest tests/test_operator.py tests/test_auth.py -q`
- `git diff --check`

## Evidence

- `app/models/hosted_archive.py`
- `app/routes/hosted_platform.py`
- `app/templates/operator.html`
- `tests/test_operator.py`
- `docs/ops/billing-runbook.md`

## Definition of Done

- [x] Hosted archive lifecycle is manageable without ad hoc database edits.
