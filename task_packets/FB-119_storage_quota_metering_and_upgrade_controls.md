# Task Packet - FB-119 Storage Quota Metering and Upgrade Controls

Status: Done

## Objective

Measure and enforce per-archive storage limits for hosted plans.

## Why / KPI

Media-heavy family archives can create unbounded hosting cost. Users need understandable limits and upgrade paths.

## Scope

- In scope:
  - per-archive storage usage computation for media, variants, backups, exports, and database
  - upload preflight checks
  - plan quota settings
  - admin/operator usage display
  - user-facing warning and upgrade copy
- Out of scope:
  - object storage migration
  - image/video transcoding overhaul
  - automatic cold storage

## Likely Files

- `app/services/storage_usage_service.py`
- `app/routes/media.py`
- `app/routes/pages.py`
- `app/routes/hosted_platform.py`
- `app/templates/admin.html`
- `app/templates/operator.html`
- `app/templates/settings.html`
- `tests/test_media.py`
- `tests/test_storage_usage.py`

## Acceptance Criteria

- [x] Storage usage can be computed for an archive.
- [x] Uploads are blocked gracefully when a hosted archive exceeds plan quota.
- [x] Admin/operator UI shows usage and quota.
- [x] Self-hosted deployments can opt out or use unlimited quota.
- [x] Tests cover media variants and backups in usage calculations.

## Validation Commands

- `uv run pytest tests/test_media.py tests/test_storage_usage.py -q`
- `git diff --check`

## Evidence

- `app/services/storage_usage_service.py`
- `app/routes/media.py`
- `app/templates/admin.html`
- `app/templates/settings.html`
- `app/templates/operator.html`
- `tests/test_media.py`
- `tests/test_storage_usage.py`

## Definition of Done

- [x] Hosted storage cost is bounded by plan controls.
