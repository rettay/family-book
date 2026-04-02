# Task Packet - FB-084 Promotion Workflow and CI Gate

## Objective

Establish a clear deploy-to-staging → test → promote-to-production workflow with an optional manual approval gate in CI, so production deploys only happen after staging has been verified.

## Why / KPI

- Currently, pushing to `main` auto-deploys to production with no human gate. This is fine for a solo developer but risky with real users.
- The staging branch (`codex/staging`) already triggers staging deploys, but there's no documented promotion process.
- CFLSR depends on production stability — broken deploys erode family trust.

## Scope

- In scope:
  - **CI workflow update**: Add a GitHub Actions `environment: production` with required reviewers on the deploy job for `main`. This creates a manual approval gate — CI runs quality checks, then waits for approval before deploying.
  - **Promotion process**: Document the workflow:
    1. Feature branch → PR to `codex/staging`
    2. CI deploys to staging automatically
    3. Developer tests on staging URL
    4. PR from `codex/staging` to `main` (or direct merge)
    5. CI runs quality checks on `main`
    6. Manual approval gate → deploy to production
  - **GitHub environment setup**: Configure the `production` environment in GitHub repo settings with required reviewers (the repo owner).
  - **Staging auto-deploy**: Staging deploys remain automatic (no gate) — fast iteration.
  - Update `.github/workflows/ci-deploy.yml` to add the approval gate.
- Out of scope:
  - Rollback automation
  - Blue-green deployment
  - Multiple staging environments

## Likely Files

- `.github/workflows/ci-deploy.yml` (add environment approval)
- `docs/ops/release-promotion-guide.md` (new — step-by-step promotion process)

## Acceptance Criteria

- [ ] Pushing to `codex/staging` auto-deploys to staging (no gate).
- [ ] Pushing to `main` runs quality checks, then waits for manual approval before deploying to production.
- [ ] GitHub `production` environment configured with required reviewer.
- [ ] Promotion process documented step-by-step.
- [ ] Developer can approve production deploy from the GitHub Actions UI.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] CI workflow updated
- [ ] Documentation committed
- [ ] Tested: push to main shows approval gate in GitHub Actions
