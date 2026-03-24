# Staging Acceptance Checklist

## Goal

Use this checklist to decide whether a sprint build on Railway staging is acceptable for promotion toward `main`.

Staging URL:
- [family-book-staging.up.railway.app](https://family-book-staging.up.railway.app)

Primary evidence sources:
- GitHub Actions run for the branch
- Playwright artifacts uploaded from `make test-ui-playwright`
- manual staging verification against the current sprint scope

## Entry Conditions

Before manual staging review starts, confirm all are true:

1. The branch has a green `CI and Railway Deploy` run.
2. Railway staging is serving the new branch build.
3. `/health` returns `200` on staging.
4. The Playwright artifact bundle exists for the branch run.

## Core Acceptance Flows

These flows should be checked every sprint unless the sprint explicitly excludes a surface:

1. Login and session continuity
- open `/login`
- confirm successful sign-in
- refresh one authenticated page and confirm the session remains valid

2. Shared family feed
- confirm the home feed renders
- create or inspect one recent moment
- confirm another member can see shared content where appropriate

3. Person workflow
- open a person page
- confirm timeline/media sections render
- if the sprint touched people flows, create or edit one person and verify persistence

4. Tree and map
- confirm `/tree` renders and can accept filters or preferences
- confirm `/map` renders and shows markers or truthful empty state

5. Admin surface
- open `/admin`
- confirm backup/protection status renders
- if the sprint touched admin controls, verify the changed admin path directly

## Sprint-Specific Acceptance

Add a short sprint-specific section to the PR or sprint notes with:

- the exact changed flows that need manual review
- what “pass” looks like
- any temporary known limitations that are acceptable for this sprint

Do not rely on memory. If the sprint changed UI behavior, write down what the reviewer should actually click.

## Evidence to Collect

Minimum evidence before production promotion:

1. green CI run
2. uploaded Playwright artifacts
3. one short written staging acceptance note in the PR, merge thread, or sprint closeout

The acceptance note should answer:

- what was checked
- what environment was checked
- whether any deviations were accepted intentionally

## Promotion Decision

Staging is acceptable for promotion only when:

- automated checks are green
- Playwright artifacts show the current branch behavior
- the manual checklist is complete
- no open blocker findings remain from auditor review

If one of those is missing, do not merge to `main`.
