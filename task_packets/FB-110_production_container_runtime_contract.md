# Task Packet - FB-110 Production Container Runtime Contract

Status: Partial

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

- [x] Production runtime docs list all required and optional env vars.
- [x] Runtime docs state required volume paths and what must persist across deploys.
- [x] Startup fails closed for missing invalid production secrets.
- [x] Health endpoint is sufficient for container orchestrator checks.
- [x] Demo data and dev bypass are impossible to enable accidentally in production docs.
- [x] Release image tagging and rollback instructions are documented.

## Validation Commands

- `uv run pytest tests/test_config.py tests/test_health.py -q`
- `docker build -t family-book:local .`
- `git diff --check`

## Definition of Done

- [ ] A new operator can run the image in a production-like environment from docs only.

## Builder Evidence

- Deliverable: `docs/ops/production-container-runtime.md`.
- New runtime enforcement: `app/runtime_contract.py`.
- Container startup now validates the production contract before migrations or demo seeding.
- Container startup now honors `DATA_DIR`, not only hard-coded `/data`, when creating archive directories.
- Production runtime validation now rejects unsupported non-SQLite `DATABASE_URL` values.
- Example env files: `.env.production.example`, `.env.hosted-archive.example`.
- Structural checks: `uv run pytest tests/test_config.py tests/test_runtime_contract.py tests/test_phase3.py -q`, `bash -n docker/start.sh`.
- Verification blocker: `docker build -t family-book:local .` could not be run here because no local container runtime (`docker`, `podman`, `nerdctl`, `buildah`) is installed.
- Remaining proof obligation: run a real image build on a machine with a container runtime before closing `FB-110`.
