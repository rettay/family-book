# Sprint Slices - S12 External Integrations and Confidence Hardening

## Slice Sequence

### S12-1 Google Maps Integration

Status: `planned`

- Objective:
  strengthen the map experience with a real map provider while preserving graceful fallback
- Scope:
  Google Maps integration, credential handling, and configured/unconfigured runtime behavior
- Deliverable:
  a map surface that can offer a materially better geographic experience in configured environments
- Verification:
  focused browser checks, staging review, and fallback-path validation

### S12-2 Resend Invite Delivery

Status: `planned`

- Objective:
  make invite delivery and related notification plumbing real
- Scope:
  Resend integration, admin invite behavior, failure reporting, and operator configuration
- Deliverable:
  real invite delivery in configured environments with safe fallback in local/self-hosted installs
- Verification:
  focused auth/invite tests plus staging/manual review of delivery flows

### S12-3 Confidence Hardening for Integration Paths

Status: `planned`

- Objective:
  reduce the remaining central-module risk that Sprint 12 touches
- Scope:
  direct coverage for `app/access_control.py` and `app/schemas.py`, plus any minimal observability or contract cleanup needed for the new integrations
- Deliverable:
  integration work backed by stronger central-module confidence and a stable CodeMap result
- Verification:
  focused pytest and CodeMap

## Slice Rules

- Keep Sprint 12 focused on Google Maps, Resend, and the hardening required to support them.
- Prefer graceful fallback behavior over brittle provider-only assumptions.
- Do not let the hardening slice expand into a general architecture rewrite.
- Preserve the browser/staging promotion contract established in earlier sprints.

## Recommended Builder Order

1. `S12-1`
2. `S12-2`
3. `S12-3`

## PM Note

Sprint 12 should unlock real external value without losing the release confidence earned in S08-S11. The right result is a more useful map, real invite delivery, and fewer central blind spots in the modules those integrations rely on.
