# Sprint Slices - S07 Observability and Coverage Hardening

## Slice Sequence

### S07-1 Attack-Surface Test Hardening

Status: `done`

- Objective:
  add direct tests for the remaining risky untrusted-input helpers
- Scope:
  request guardrails in `app/middleware/security.py` and size/stream handling in `app/services/io_limits.py`
- Deliverable:
  meaningful direct coverage on the paths CodeMap still flags as attack surface
- Verification:
  focused pytest proving both accepted and rejected request paths

### S07-2 Critical-Module Coverage Expansion

Status: `done`

- Objective:
  add direct coverage to the central modules still flagged as under-tested
- Scope:
  `app/config.py`, `app/models/moments.py`, and `app/schemas.py`
- Deliverable:
  central runtime modules have explicit behavioral tests instead of only indirect coverage
- Verification:
  focused pytest plus improved CodeMap coverage posture

### S07-3 Observability and Complexity Hardening

Status: `done`

- Objective:
  improve diagnosis value in central paths and reduce the most justified remaining complexity warnings
- Scope:
  pragmatic runtime instrumentation plus limited cleanup in `app/access_control.py` and `app/services/media_service.py`
- Deliverable:
  better diagnostic value and a lower CodeMap warning count without a broad refactor
- Verification:
  CodeMap comparison against the Sprint 06 baseline and focused regression checks

## Slice Rules

- Do not add new user-facing features.
- Do not pull in third-party observability platforms.
- Prefer direct behavioral tests over broad low-signal coverage inflation.
- Keep complexity cleanup narrow and reviewable.

## Recommended Builder Order

1. `S07-1`
2. `S07-2`
3. `S07-3`

## PM Note

This sprint is about trust in the runtime. The right outcome is not “more files touched”; it is a smaller warning surface, better diagnosis when something fails, and tighter proof around the most important plumbing modules.
