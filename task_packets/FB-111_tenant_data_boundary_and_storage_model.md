# Task Packet - FB-111 Tenant Data Boundary and Storage Model

Status: Proposed

## Objective

Define and test the data boundary for a hosted family archive.

## Why / KPI

Family Book stores sensitive living-person data. Paid hosting must make cross-archive data leakage structurally hard, especially for media, backups, exports, and support tooling.

## Scope

- In scope:
  - data inventory for database, media, variants, backups, exports, sessions, tokens, logs, Matrix bridge data, inbound email attachments, and secrets
  - archive identifier and directory layout if single-tenant managed hosting is chosen
  - tenant_id requirements if pooled multi-tenancy is chosen later
  - backup/restore/delete/export boundary tests
  - path traversal and archive mix-up threat checklist
- Out of scope:
  - full threat model report
  - provider-specific IaC
  - client-side encryption redesign

## Likely Files

- `docs/ops/tenant-data-boundary.md`
- `app/config.py`
- `app/backup/service.py`
- `app/services/media_service.py`
- `tests/test_backup.py`
- `tests/test_media.py`
- `tests/test_config.py`

## Acceptance Criteria

- [ ] Tenant data boundary doc exists and is linked from hosting ADR.
- [ ] Every durable data class has an owner, path/table, retention rule, and export/delete behavior.
- [ ] Backup and export paths cannot mix data from two archives.
- [ ] Media paths are normalized and tested against traversal.
- [ ] Future pooled multi-tenant requirements are captured without forcing implementation now.

## Validation Commands

- `uv run pytest tests/test_backup.py tests/test_media.py tests/test_config.py -q`
- `git diff --check`

## Definition of Done

- [ ] Tenant boundary is clear enough to drive provisioning and support work.
