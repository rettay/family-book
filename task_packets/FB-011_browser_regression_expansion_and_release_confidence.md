# Task Packet - FB-011 Browser Regression Expansion and Release Confidence

## Objective

Increase confidence in Family Book staging and production releases by broadening automated browser coverage, formalizing staging acceptance, and tightening the evidence expected before promotion to `main`.

## Why / KPI

- Family Book now has a stable product and runtime spine, but the browser confidence layer is still relatively thin.
- Staging exists and is useful, but sprint acceptance still relies too much on ad hoc review.
- The next quality gain should make release decisions easier and less subjective.

Primary KPI:
- increase the number of meaningful browser-verified core flows and make their evidence inspectable in CI.

Secondary KPI:
- reduce ambiguity around what must be checked in staging before promoting to production.

## Scope

- In scope:
  - expand Playwright flow coverage for core member/admin journeys
  - improve screenshot/trace artifact expectations for browser runs
  - create a reusable staging acceptance checklist
  - tighten release-flow documentation and merge-to-main evidence requirements
  - validate that Railway staging and production continue to fit the documented promotion model
- Out of scope:
  - unrelated product features
  - large-scale cross-browser or device-matrix testing
  - full visual regression infrastructure
  - third-party cloud browser grids
  - deployment-platform rewrites

## Task Type

- Release confidence / browser testing / staging acceptance hardening packet

## Dependencies and Ordering Assumptions

- Depends on S01-S07 being closed because the product surface and release lane are now stable enough to harden.
- Should happen before another broad feature sprint so later feature work ships with a stronger browser/release safety net.
- Assumes the current GitHub Actions plus Railway staging/production flow remains the canonical deployment path.

## Constraints

- Browser coverage should focus on high-value flows, not coverage inflation.
- Manual acceptance should stay lightweight and realistic for ongoing sprint use.
- Promotion rules should fit a self-hosted app and not become heavy enterprise ceremony.
- Release evidence must be easy to inspect quickly.

## Recommended Launch Scope Within This Packet

- Must directly cover:
  - login and authenticated landing flow
  - shared moment/timeline flow
  - person workflow and person timeline flow
  - tree and map navigation flow
  - at least one admin verification flow tied to release readiness
- Should improve:
  - screenshot naming and artifact consistency
  - failure traces/video capture where useful
  - staging review documentation
  - merge/promotion runbook clarity
- Must re-run:
  - Playwright/browser checks
  - focused pytest where browser changes touch helper code
  - CI/release documentation review

## Implementation Notes

- Likely files:
  - `tests/ui/playwright-flow-checks.sh`
  - `tests/ui/playwright_seed.py`
  - `Makefile`
  - `.github/workflows/ci-deploy.yml`
  - `docs/ops/railway-release-flow.md`
  - new or updated release/staging acceptance docs under `docs/strategy/` or `docs/ops/`
- Validation commands:
  - `make test-ui-playwright`
  - focused pytest if browser fixtures/helpers change
  - deploy/runbook sanity check against staging/prod health endpoints

## Evaluation Environment

- Task:
  expand browser regression coverage and make release confidence explicit
- Verifier:
  browser run artifacts, staging acceptance docs, and release/runbook consistency
- Reference/oracle:
  `STATUS.md`
  `docs/ops/railway-release-flow.md`
  existing Playwright artifacts and current staging lane
- Expected evidence:
  broader browser artifacts, clearer manual acceptance instructions, and an explicit merge/promotion contract
- Known failure modes / reward hacks:
  - adding browser steps that only assert pages load
  - producing many screenshots without meaningful assertions
  - documenting a staging checklist that does not match the actual release flow
  - adding process weight without improving decision quality
- Verifiability class:
  `release-confidence-hardening`
- Context policy:
  optimize for reusable release confidence, not cosmetic QA ceremony

## Acceptance Criteria

- [ ] Playwright covers additional high-value member/admin flows beyond the current smoke baseline.
- [ ] Browser test artifacts include useful screenshots and failure traces that are easy to inspect.
- [ ] A documented staging acceptance checklist exists and maps to real core flows.
- [ ] The release runbook explains what must be green before merging to `main`.
- [ ] The documented promotion model matches the actual GitHub Actions and Railway lane.
- [ ] The sprint improves release confidence without adding brittle or noisy process.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Validation evidence attached
- [ ] Staging acceptance contract documented
- [ ] Release evidence requirements documented
- [ ] No unrelated feature work folded into the sprint

## Risk and Verification Notes

- Likely shallow-pass failure modes:
  - browser flows remain too shallow to catch real regressions
  - staging acceptance is documented but not actionable
  - release guidance drifts from the actual deployment setup
  - artifact volume grows without improving decision quality
- Required verification depth:
  - meaningful browser assertions
  - inspectable screenshots/traces
  - documentation consistency with the real release lane
- Sufficient discriminative power means:
  this packet should fail review if it only produces more artifacts without making releases easier to trust

## Execution Budget

- Builder may explore:
  - the smallest set of browser flows that materially improves coverage
  - how best to surface failure artifacts in CI
  - where a concise staging acceptance checklist belongs for routine use
- Builder must escalate if:
  - the browser harness becomes too flaky to be useful
  - release-gating changes would materially disrupt current deployment cadence
- Material scope drift:
  - new product features
  - broad UI redesign
  - deployment-platform migration
- Proof obligations before review:
  - browser coverage is broader and meaningful
  - staging acceptance is explicit and reusable
  - the release lane is better documented and easier to trust
