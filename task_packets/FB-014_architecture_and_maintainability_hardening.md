# Task Packet - FB-014 Architecture and Maintainability Hardening

## Objective

Reduce the remaining high-signal structural debt in Family Book so external integrations and future feature work land on a more stable, test-backed core.

## Why / KPI

- CodeMap is passing overall, but central modules still carry attention, observability, and testing debt.
- Sprint 11 increased pressure on the tree/access/schema layer, which makes a targeted hardening pass the right companion to the next integration sprint.

Primary KPI:
- reduce CodeMap warning pressure in central modules without creating regressions.

Secondary KPI:
- improve confidence in access-control and schema behavior that multiple product surfaces depend on.

## Scope

- In scope:
  - direct tests for `app/access_control.py`
  - direct tests for `app/schemas.py`
  - targeted observability improvements in central runtime modules where practical
  - narrow cleanup of structural warnings that directly affect Sprint 12 integration work
- Out of scope:
  - broad architectural rewrite
  - large dependency-graph redesign
  - feature-surface redesign unrelated to integration or quality hardening

## Task Type

- engineering hardening / maintainability packet

## Dependencies and Ordering Assumptions

- Best sequenced alongside Sprint 12 integration work so Google Maps and Resend do not land on an increasingly fragile base.

## Recommended Launch Scope Within This Packet

- Must directly improve:
  - coverage for access control and schema behavior
  - central-module confidence where CodeMap still flags risk
- Should improve:
  - observability in modules supporting integration flows
  - attention/maintainability posture in the tree-access integration path
- Must re-run:
  - focused pytest
  - CodeMap

## Implementation Notes

- Likely files:
  - `app/access_control.py`
  - `app/schemas.py`
  - `app/config.py`
  - `app/services/field_protection.py`
  - `tests/test_access_control.py`
  - `tests/test_schema_models.py`
  - `tests/test_config.py`
- Validation commands:
  - `uv run pytest tests/test_access_control.py tests/test_schema_models.py tests/test_config.py -q`
  - `uv run --directory ~/code/codemap codemap check /Users/cheech/code/family-book --json`

## Acceptance Criteria

- [ ] CodeMap no longer flags `app/access_control.py` as untested attack surface.
- [ ] CodeMap no longer flags `app/schemas.py` as untested critical-path coverage.
- [ ] Focused tests cover the central access/schema behaviors touched by Sprint 12.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Focused tests pass
- [ ] CodeMap remains passing overall
