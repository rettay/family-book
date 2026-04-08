# Task Packet - FB-129 Production Readiness Security and Performance Gate

Status: Proposed

## Objective

Create and run the release gate for launching paid hosted archives.

## Why / KPI

The product handles sensitive family data. Launch should be blocked unless privacy, security, performance, backup/restore, and support readiness meet a defined bar.

## Scope

- In scope:
  - paid-launch checklist
  - access-control adversarial tests
  - upload/file handling probes
  - export/delete/backup/restore verification
  - auth/session/rate-limit checks
  - realistic media/tree performance smoke
  - logging review for secrets/private content
  - rollback drill
- Out of scope:
  - formal third-party pentest
  - SOC 2
  - full chaos engineering

## Likely Files

- `docs/ops/paid-launch-readiness-gate.md`
- `tests/test_security_guardrails.py`
- `tests/test_access_control.py`
- `tests/test_media.py`
- `tests/test_export.py`
- `tests/ui/playwright-flow-checks.sh`

## Acceptance Criteria

- [ ] Paid launch checklist exists and is actionable.
- [ ] Access-control adversarial tests cover current paid-beta roles.
- [ ] Backup restore verification must pass before launch.
- [ ] Export/delete flows are verified before launch.
- [ ] Logs and audit records are sampled for sensitive leakage.
- [ ] Performance smoke covers realistic tree and media volumes.
- [ ] Rollback path is documented and tested.

## Validation Commands

- `uv run pytest tests/ -q`
- `make test-ui-playwright`
- `git diff --check`

## Definition of Done

- [ ] Paid hosted launch has a clear go/no-go gate.
