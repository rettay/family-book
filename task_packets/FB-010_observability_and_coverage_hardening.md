# Task Packet - FB-010 Observability and Coverage Hardening

## Objective

Reduce the remaining high-signal CodeMap warnings by adding direct tests for risky plumbing, increasing coverage in central runtime modules, and making the most important request/runtime paths easier to inspect when something breaks.

## Why / KPI

- Family Book now has enough product surface that the next quality bottleneck is not missing features, it is confidence in the plumbing.
- CodeMap is passing overall, but the remaining warnings are concentrated in central modules and untrusted-input paths.
- The product needs a stronger reliability floor before opening another broad feature sprint.

Primary KPI:
- reduce CodeMap warning count from `9` to `5` or fewer without introducing new FAILs.

Secondary KPI:
- improve confidence in the runtime paths most likely to fail silently in production or staging.

## Scope

- In scope:
  - direct tests for `app/middleware/security.py`
  - direct tests for `app/services/io_limits.py`
  - targeted tests for `app/config.py`
  - targeted tests for `app/models/moments.py`
  - targeted tests for `app/schemas.py`
  - light observability improvements in central runtime paths where current warnings are justified
  - modest complexity reduction where it materially improves maintainability
- Out of scope:
  - feature work unrelated to quality hardening
  - full telemetry stack rollout
  - external monitoring vendor integration
  - broad architecture rewrites
  - nonessential UI changes

## Task Type

- Reliability / test-depth / observability hardening packet

## Dependencies and Ordering Assumptions

- Depends on S01-S06 being closed because the product surface is now stable enough to harden systematically.
- Should happen before another large user-facing feature sprint so the next feature cycle starts from a more reliable baseline.
- Should use the existing CodeMap config and Playwright/pytest layers as the measurement baseline.

## Constraints

- Prefer targeted tests over broad noisy test additions.
- Observability should stay pragmatic and self-host-friendly.
- Do not add instrumentation that materially complicates local development or self-host deployment.
- Complexity reduction should be surgical, not a disguised refactor sprint.

## Recommended Launch Scope Within This Packet

- Must directly cover:
  - request limits and rejection behavior
  - security middleware guardrails
  - config normalization and derived settings behavior
  - schema/model serialization paths for moments and shared APIs
- Should improve:
  - logging clarity around critical runtime boundaries
  - maintainability in a small number of central functions that CodeMap still flags
- Must re-run:
  - focused pytest
  - existing Playwright smoke flow where relevant
  - CodeMap check

## Implementation Notes

- Likely files:
  - `app/middleware/security.py`
  - `app/services/io_limits.py`
  - `app/config.py`
  - `app/models/moments.py`
  - `app/schemas.py`
  - `app/access_control.py`
  - `app/services/media_service.py`
  - tests added under `tests/`
- Validation commands:
  - focused pytest for the new hardening coverage
  - `uv run python -m compileall app tests`
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`

## Evaluation Environment

- Task:
  improve observability and direct test coverage in central and attack-surface modules
- Verifier:
  focused tests plus CodeMap warning regression check
- Reference/oracle:
  `STATUS.md`
  `docs/strategy/sprint-closeout-s06.md`
  `.codemap/brief.md`
- Expected evidence:
  CodeMap warning count drops, the targeted modules gain direct tests, and central runtime behavior is easier to inspect during failures
- Known failure modes / reward hacks:
  - adding superficial tests that do not exercise the warned paths
  - improving one warning category while introducing another
  - instrumenting routes noisily without improving actual diagnosis value
  - turning complexity cleanup into a high-risk refactor
- Verifiability class:
  `measurable-hardening`
- Context policy:
  optimize for high-signal quality improvements, not volume of changes

## Acceptance Criteria

- [ ] `app/middleware/security.py` has direct tests covering its main guardrail behavior.
- [ ] `app/services/io_limits.py` has direct tests covering success and rejection paths.
- [ ] `app/config.py`, `app/models/moments.py`, and `app/schemas.py` gain targeted direct coverage.
- [ ] CodeMap remains `0 FAIL` and warning count is reduced from the Sprint 06 baseline.
- [ ] No new user-facing regressions are introduced in the existing browser smoke flow.
- [ ] Any observability additions are documented by the code itself and remain self-host-friendly.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] CodeMap warning count improved
- [ ] No new security failures or injection findings
- [ ] No broad feature work smuggled into the sprint

## Risk and Verification Notes

- Complexity hotspots:
  - `app/access_control.py`
  - `app/services/media_service.py`
  - central config/schema behavior shared by many routes
- Likely shallow-pass failure modes:
  - tests cover importability but not behavior
  - logs are added but do not help diagnose failures
  - warning count stays flat because the wrong modules were targeted
  - builder drifts into unrelated cleanup
- Required verification depth:
  - direct behavioral tests
  - CodeMap comparison against the Sprint 06 baseline
  - compile check
- Sufficient discriminative power means:
  this packet should fail review if it merely adds noise without measurably improving warning posture or diagnosis value

## Execution Budget

- Builder may explore:
  - where a few structured log points add the most value
  - whether the two flagged complex functions can be split safely
  - the smallest useful assertions for the central config/schema modules
- Builder must escalate if:
  - lowering the warning count requires a much larger refactor than fits a hardening sprint
  - observability changes would materially affect deploy or operator complexity
- Material scope drift:
  - new user-facing features
  - analytics/monitoring vendor adoption
  - broad architectural decomposition
- Proof obligations before review:
  - targeted modules have direct test evidence
  - CodeMap warning posture improves
  - the hardening work is measurable and not cosmetic
