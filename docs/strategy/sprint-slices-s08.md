# Sprint Slices - S08 Browser Regression Expansion and Release Confidence

## Slice Sequence

### S08-1 Playwright Coverage Expansion

Status: `done`

- Objective:
  expand the browser automation layer to cover the highest-value product workflows
- Scope:
  authenticated member flows, shared content flows, and core admin review surfaces
- Deliverable:
  a broader Playwright suite with useful screenshots and failure artifacts
- Verification:
  repeatable browser runs that prove the key flows still work end to end

### S08-2 Staging Acceptance Contract

Status: `done`

- Objective:
  define a reusable manual acceptance checklist for staging
- Scope:
  reviewer steps, expected artifacts, staging URLs, and pass/fail criteria
- Deliverable:
  a documented staging review contract that can be reused in later sprints
- Verification:
  the checklist maps cleanly to real staging flows and CI/browser evidence

### S08-3 Release Evidence and Promotion Gate

Status: `done`

- Objective:
  make main-branch promotion criteria explicit and inspectable
- Scope:
  release runbook updates, evidence expectations, and merge/promotion rules
- Deliverable:
  a clearer release-confidence standard for going from staging acceptance to production merge
- Verification:
  the repo docs and CI/release lane point to the same promotion contract

## Slice Rules

- Prefer a small number of high-value browser flows over a bloated suite.
- Keep release confidence pragmatic for a self-hosted product.
- Do not introduce brittle visual-diff tooling unless it is clearly justified.
- Keep manual acceptance lightweight but explicit.

## Recommended Builder Order

1. `S08-1`
2. `S08-2`
3. `S08-3`

## PM Note

This sprint is about trustworthy releases. The right outcome is not “more screenshots”; it is a release lane where automated browser evidence, staging review, and promotion to `main` all tell the same story.
