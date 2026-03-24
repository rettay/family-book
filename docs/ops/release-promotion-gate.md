# Release Promotion Gate

## Goal

Define the minimum evidence required to promote Family Book from a working branch through staging and into `main`.

This is intentionally lightweight. The purpose is to prevent “it probably works” releases, not to add enterprise ceremony.

## Promotion Path

1. work happens on `codex/*`
2. branch CI runs
3. merge to `codex/staging`
4. Railway staging auto-deploys
5. staging acceptance is completed
6. accepted staging work is merged to `main`
7. Railway production auto-deploys

## Required Evidence Before Merging to `main`

All of the following must exist:

1. Green GitHub Actions run for the candidate branch or staging branch
- compile/test steps are green
- browser flow step is green

2. Playwright artifacts
- screenshots exist for the run
- trace/video artifacts exist for the run or failure path
- artifacts are inspectable from the GitHub Actions run

3. Staging acceptance note
- reviewer states what was checked on staging
- reviewer notes pass/fail outcome
- reviewer records any accepted limitations explicitly

4. No unresolved blocker findings
- auditor review is clear, or blocker findings have been fixed and re-reviewed

## Minimum Merge Checklist

Before merging to `main`, answer:

- Is staging healthy?
- Are the changed flows covered by either browser automation or explicit manual review?
- Do the artifacts and the manual check agree?
- Is there any known issue that should block production?

If any answer is “no” or “unclear,” stop and resolve that first.

## Artifact Locations

- CI workflow:
  - [ci-deploy.yml](/Users/cheech/code/family-book/.github/workflows/ci-deploy.yml)
- Playwright local artifact root:
  - `/Users/cheech/code/family-book/output/playwright/family-book-flow`
- Staging acceptance checklist:
  - [staging-acceptance-checklist.md](/Users/cheech/code/family-book/docs/ops/staging-acceptance-checklist.md)
- Railway release model:
  - [railway-release-flow.md](/Users/cheech/code/family-book/docs/ops/railway-release-flow.md)

## Non-Goals

This gate does not require:

- a large cross-browser matrix
- pixel-perfect visual diffing
- external QA tooling
- formal release signoff meetings

It only requires enough evidence that merging to `main` is a reasoned decision.
