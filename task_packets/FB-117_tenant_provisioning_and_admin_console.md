# Task Packet - FB-117 Tenant Provisioning and Operator Console

Status: Proposed

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
- `app/routes/operator.py`
- `app/services/provisioning_service.py`
- `app/templates/operator.html`
- `tests/test_operator.py`
- `docs/ops/managed-hosting-baseline.md`

## Acceptance Criteria

- [ ] Operator can create a new archive record with owner and plan.
- [ ] Operator can suspend/reactivate archive access without deleting data.
- [ ] Operator can mark deletion/export workflow states.
- [ ] Support view shows health, plan, storage, backup, and auth status without private content.
- [ ] All lifecycle transitions are audited.

## Validation Commands

- `uv run pytest tests/test_operator.py tests/test_auth.py -q`
- `git diff --check`

## Definition of Done

- [ ] Hosted archive lifecycle is manageable without ad hoc database edits.
