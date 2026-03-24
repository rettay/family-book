# Sprint Plan - S08 Browser Regression Expansion and Release Confidence

## Sprint

- Name: `S08 - Browser Regression Expansion and Release Confidence`
- Status: Closed
- Primary packet: `FB-011 Browser Regression Expansion and Release Confidence`

## Sprint Goal

Increase confidence in Family Book staging and production releases by expanding browser-based regression coverage, making staging acceptance criteria explicit, and tightening the evidence required before promotion to `main`.

## Why This Sprint

Family Book now has seven closed sprints with a stable collaboration/runtime foundation. The next highest-value gap is no longer backend correctness; it is confidence that the shipped user flows still work end to end in the browser, in staging, and during release promotion.

## Must-Have Outcomes

- Playwright covers more than the current narrow smoke path.
- The core member/admin/manual-QA flows are explicit and repeatable in staging.
- Promotion to `main` has a lightweight but real evidence contract.
- Release confidence improves without turning the repo into a heavyweight platform process.

## Acceptance Criteria

1. Playwright covers the highest-value logged-in member and admin flows beyond the current smoke baseline.
2. Browser test artifacts include screenshots and failure traces that are easy to inspect from CI.
3. A staging acceptance checklist exists and maps directly to the flows most likely to regress.
4. The release/runbook documentation explains what must be green before merging to `main`.
5. Existing Railway staging and production flow remains functional after the changes.
6. The sprint produces a clearer release-confidence baseline than the current “smoke test plus judgment” model.

## In Scope

- Playwright flow expansion
- screenshot/trace artifact expectations
- staging acceptance checklist and manual review contract
- release evidence/runbook tightening
- targeted CI/release documentation updates where needed

## Out of Scope

- major product feature work
- cross-browser matrix explosion
- visual-diff tooling that is likely to create brittle noise
- third-party test grid integration
- broad deployment-platform changes unrelated to release confidence

## Implementation Order

1. Execute Slice 1: expand Playwright flow coverage.
2. Execute Slice 2: formalize staging acceptance and manual QA.
3. Execute Slice 3: tighten release evidence and promotion guidance.
4. Validate with browser runs, artifact inspection, and a staging/production deploy sanity check.

## Execution Slices

### Slice 1 - Playwright Coverage Expansion

- Goal:
  expand automated browser coverage to the flows that matter most for member/admin confidence
- Scope:
  login, shared timeline, person workflows, tree/map, and core admin acceptance surfaces
- Must prove:
  the suite catches practical breakage in real user flows, not just route availability

### Slice 2 - Staging Acceptance Contract

- Goal:
  define what “ready for manual staging review” means for a sprint
- Scope:
  documented checklist, staging URLs/surfaces, expected evidence, and reviewer steps
- Must prove:
  a human can evaluate the build consistently without inventing the checklist each sprint

### Slice 3 - Release Evidence and Promotion Gate

- Goal:
  make the path from staging acceptance to `main` promotion explicit and inspectable
- Scope:
  runbook/CI expectations, artifact locations, promotion rules, and merge criteria
- Must prove:
  production promotion is backed by named evidence rather than informal memory

## Proof Obligations

- Browser coverage must expand in meaningful user-facing flows.
- The staging review contract must be concrete enough to reuse in later sprints.
- Promotion guidance must align with the actual Railway/GitHub flow already in place.
- The sprint must improve confidence without creating brittle release ceremony.

## Risks To Watch

- adding too many browser flows too quickly and making the suite noisy
- writing a manual checklist that nobody will actually follow
- over-engineering promotion gates beyond what this self-hosted app needs
- mistaking screenshot volume for meaningful release confidence

## Exit Target

Sprint 08 is complete when Family Book has a broader, credible browser regression layer, a repeatable staging acceptance contract, and a clearer release-evidence standard for merges to `main`.
