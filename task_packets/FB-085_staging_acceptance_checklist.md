# Task Packet - FB-085 Staging Acceptance Checklist

## Objective

Create a concrete, runnable acceptance checklist that must pass on staging before promoting a release to production.

## Why / KPI

- Without a checklist, "test on staging" is vague. Developers skip steps or test inconsistently.
- A written checklist ensures every promotion covers the critical paths: auth, tree, media, admin, i18n.
- CFLSR depends on the core collaborative loop being verified before every production deploy.

## Scope

- In scope:
  - Create `docs/ops/staging-acceptance-checklist.md` with sections:
    - **Health**: `/health` returns ok, no server errors in logs
    - **Auth**: Login with Google OAuth, logout, session persists across page reload
    - **Tree**: Tree renders all nodes, click opens sidebar, context menu works, branch view works
    - **Media**: Upload a photo, set as headshot, delete media, gallery page renders
    - **Person editing**: Edit a field in sidebar (auto-save), edit on person edit page, place history works
    - **Admin**: Admin dashboard loads, invite creation works, session visibility shows data
    - **Wiki/Bios**: Person wiki page renders sections, media gallery section visible
    - **i18n**: Switch to Spanish, verify key surfaces render in Spanish
    - **Mobile**: Tree, sidebar, and person edit don't overflow on 390px viewport
  - Each item should be a checkbox with a brief instruction (what to do + what to expect)
  - Add a "Quick smoke test" version (5 items, 2 minutes) for low-risk changes
  - Add a "Full acceptance" version (all items, 10-15 minutes) for significant changes
- Out of scope:
  - Automating the checklist (future — could become Playwright tests)
  - Performance benchmarks

## Likely Files

- `docs/ops/staging-acceptance-checklist.md` (new)

## Acceptance Criteria

- [ ] Checklist document exists with quick and full versions.
- [ ] Quick smoke test covers: health, auth, tree render, media upload, sidebar edit.
- [ ] Full acceptance covers all 9 categories listed above.
- [ ] Each item has clear do/expect instructions.
- [ ] Checklist is referenced from the promotion guide (FB-084).

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Documentation committed
