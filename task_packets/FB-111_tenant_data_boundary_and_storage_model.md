# Task Packet - FB-111 Tenant Data Boundary and Storage Model

Status: Done

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

- [x] Tenant data boundary doc exists and is linked from hosting ADR.
- [x] Every durable data class has an owner, path/table, retention rule, and export/delete behavior.
- [x] Backup and export paths cannot mix data from two archives.
- [x] Media paths are normalized and tested against traversal.
- [x] Future pooled multi-tenant requirements are captured without forcing implementation now.

## Validation Commands

- `uv run pytest tests/test_backup.py tests/test_media.py tests/test_config.py -q`
- `git diff --check`

## Definition of Done

- [x] Tenant boundary is clear enough to drive provisioning and support work.

## Builder Evidence

- Deliverable: `docs/ops/tenant-data-boundary.md`.
- ADR cross-link: `docs/ops/hosting-and-tenant-architecture-adr.md`.
- Enforcement improvement: `app/backup/service.py` now rejects unsafe zip paths during restore.
- Regression coverage: `tests/test_phase3.py::test_restore_backup_archive_rejects_unsafe_zip_paths`.
- Media file and variant helpers now reject traversal outside `DATA_DIR/media`.
- Regression coverage: `tests/test_media.py::TestMediaServing::test_serve_file_rejects_db_backed_path_traversal`.
- Regression coverage: `tests/test_media.py::TestMediaPathSafety::*`.
- Runtime enforcement also blocks production SQLite paths outside `DATA_DIR`.
