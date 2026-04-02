# Task Packet - FB-087 Developer Workflow Documentation

## Objective

Document the new development workflow end-to-end so any contributor knows how to go from code change to staging to production.

## Why / KPI

- With staging in place, the workflow changes from "push to main → auto-deploy" to "branch → staging → approve → production." This needs to be written down.
- Future contributors (or the user themselves in 6 months) need a reference.

## Scope

- In scope:
  - `docs/ops/developer-workflow.md` covering:
    1. Local development setup (existing — link to CLAUDE.md)
    2. Feature branch workflow: create branch → develop → test locally → push
    3. Staging deployment: merge/push to `codex/staging` → CI auto-deploys → staging URL
    4. Staging acceptance: run checklist (link to FB-085 checklist)
    5. Production promotion: merge to `main` → CI quality gate → manual approval → deploy
    6. Hotfix process: for urgent production fixes, push directly to `main` with expedited approval
    7. Environment overview: staging vs production URLs, env vars, data isolation
  - Update CLAUDE.md to reference the new workflow doc
- Out of scope:
  - Contributing guidelines for external contributors (future — multi-tenant)

## Likely Files

- `docs/ops/developer-workflow.md` (new)
- `CLAUDE.md` (update deploy section)

## Acceptance Criteria

- [ ] Workflow document covers all 7 sections.
- [ ] CLAUDE.md deploy section updated to reference new workflow.
- [ ] Document includes environment URLs and branch mapping.

## Definition of Done

- [ ] Documentation committed
