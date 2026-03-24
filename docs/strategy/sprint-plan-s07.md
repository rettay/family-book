# Sprint Plan - S07 Observability and Coverage Hardening

## Sprint

- Name: `S07 - Observability and Coverage Hardening`
- Status: Closed
- Primary packet: `FB-010 Observability and Coverage Hardening`

## Sprint Goal

Raise the reliability floor of Family Book by adding direct tests for risky runtime plumbing, improving coverage in central modules, and reducing the remaining high-signal CodeMap warnings without opening a new feature surface.

## Why This Sprint

Family Book now has six closed implementation sprints and a stable release lane. The next highest-value work is hardening: the current CodeMap warnings are concentrated in attack-surface helpers, central config/schema paths, and a few runtime hotspots that deserve better tests and modest observability.

## Must-Have Outcomes

- Untrusted-input runtime helpers have direct behavioral tests.
- Central config/schema/model modules gain explicit coverage.
- CodeMap warning posture improves from the Sprint 06 baseline.
- Existing user-visible flows continue to pass the current smoke layer.

## Acceptance Criteria

1. `app/middleware/security.py` has direct tests for its main request guardrails.
2. `app/services/io_limits.py` has direct tests for allowed and rejected upload/stream cases.
3. `app/config.py`, `app/models/moments.py`, and `app/schemas.py` gain focused direct test coverage.
4. `codemap check` remains `0 FAIL` and drops below the Sprint 06 warning baseline of `9 WARN`.
5. Existing focused browser smoke verification still passes after the hardening work.
6. Any observability additions remain pragmatic for a self-hosted deployment.

## In Scope

- attack-surface tests
- critical-module coverage
- modest observability additions in central runtime paths
- small complexity reductions where clearly justified
- focused CodeMap warning reduction

## Out of Scope

- new user-facing features
- external monitoring vendor rollout
- large internal architecture changes
- broad UI polish
- speculative cleanup unrelated to the measured warnings

## Implementation Order

1. Execute Slice 1: attack-surface test hardening.
2. Execute Slice 2: critical-module coverage expansion.
3. Execute Slice 3: observability and complexity hardening.
4. Validate with focused pytest, compile checks, browser smoke where relevant, and CodeMap comparison.

## Execution Slices

### Slice 1 - Attack-Surface Test Hardening

- Goal:
  directly test request guardrails and untrusted-input handling
- Scope:
  `app/middleware/security.py` and `app/services/io_limits.py`
- Must prove:
  rejection and allowed paths are both covered with meaningful assertions

### Slice 2 - Critical-Module Coverage Expansion

- Goal:
  cover the central modules CodeMap still flags as under-tested
- Scope:
  `app/config.py`, `app/models/moments.py`, and `app/schemas.py`
- Must prove:
  the tests exercise behavior that matters to runtime correctness, not just imports

### Slice 3 - Observability and Complexity Hardening

- Goal:
  make key runtime paths easier to inspect and, where safe, reduce complexity in the most flagged hotspots
- Scope:
  targeted log/diagnostic improvements plus limited cleanup in `app/access_control.py` and `app/services/media_service.py`
- Must prove:
  the CodeMap warning posture improves and the changes do not reopen product behavior risk

## Proof Obligations

- The new tests must be direct and behaviorally meaningful.
- CodeMap warning count must improve from the Sprint 06 baseline.
- Hardening changes must not regress the current product flows.
- Scope must stay disciplined: this sprint is for reliability, not feature expansion.

## Risks To Watch

- turning “coverage expansion” into low-value assertion noise
- making observability heavier than appropriate for a self-hosted app
- refactoring complex functions too aggressively
- reducing one warning category while increasing coupling or regression risk elsewhere

## Exit Target

Sprint 07 is complete when Family Book has stronger direct tests on the risky plumbing, a lower CodeMap warning count than Sprint 06, and no regressions in the current smoke-verified product flows.

## Closeout Result

- Result: `pass`
- Focused verification:
  - `uv run pytest tests/test_config.py tests/test_security_guardrails.py tests/test_schema_models.py tests/test_phase3.py tests/test_auth.py tests/test_models.py -q`
  - result: `78 passed`
  - `uv run python -m compileall app tests`
  - result: success
  - `uv run --directory /Users/cheech/code/codemap codemap check /Users/cheech/code/family-book --json`
  - result: `17 PASS`, `0 FAIL`, `8 WARN`
- Outcome summary:
  - direct tests were added for middleware, IO limits, config normalization, schemas, and model behavior
  - complexity warnings in `app/access_control.py` and `app/services/media_service.py` were eliminated
  - CodeMap warning count improved from the Sprint 06 baseline of `9 WARN` to `8 WARN`
