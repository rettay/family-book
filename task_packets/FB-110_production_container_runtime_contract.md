# Task Packet - FB-110 Production Container Runtime Contract

Status: Proposed

## Objective

Make the container image a supported production artifact with documented runtime requirements, health checks, migrations, data mounts, and safe defaults.

## Why / KPI

Paid hosting requires repeatable deploys. A Dockerfile alone is not enough if secrets, volumes, migrations, demo data, and rollback behavior are implicit.

## Scope

- In scope:
  - production env var contract
  - data mount contract for SQLite, media, thumbnails, variants, backups, and exports
  - startup/migration behavior
  - health/readiness behavior
  - release version tagging and promotion notes
  - production-safe defaults: no `DEV_BYPASS_AUTH`, no demo seed, docs disabled unless explicitly enabled
  - operator smoke command
- Out of scope:
  - provider-specific IaC
  - multi-tenant provisioning
  - database migration to Postgres

## Likely Files

- `docs/ops/production-container-runtime.md`
- `Dockerfile`
- `docker/start.sh`
- `.env.example`
- `tests/test_config.py`
- `tests/test_health.py`

## Acceptance Criteria

- [ ] Production runtime docs list all required and optional env vars.
- [ ] Runtime docs state required volume paths and what must persist across deploys.
- [ ] Startup fails closed for missing invalid production secrets.
- [ ] Health endpoint is sufficient for container orchestrator checks.
- [ ] Demo data and dev bypass are impossible to enable accidentally in production docs.
- [ ] Release image tagging and rollback instructions are documented.

## Validation Commands

- `uv run pytest tests/test_config.py tests/test_health.py -q`
- `docker build -t family-book:local .`
- `git diff --check`

## Definition of Done

- [ ] A new operator can run the image in a production-like environment from docs only.
