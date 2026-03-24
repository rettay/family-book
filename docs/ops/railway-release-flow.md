# Railway Release Flow

## Goal

Family Book uses a two-environment Railway release model:

- `production`
  - branch: `main`
  - public URL: `https://cutroni.xyz`
- `staging`
  - branch: `codex/staging`
  - public URL: `https://family-book-staging.up.railway.app`

This gives the project a stable non-production environment for manual sprint review while keeping production deployments tied to merges on `main`.

## Current Railway State

- Project: `family-book`
- Project ID: `b20599a1-015f-48e4-aba4-452cb304e948`
- Service: `family-book`
- Service ID: `59be3540-f319-4cc6-b984-766e537e5111`
- Production environment ID: `f5b1cb8e-e85e-4ae1-a967-0254e836eda0`
- Staging environment ID: `f6323cdb-1ede-404a-ba7c-00fa771af0f7`

## Storage Isolation

- Production volume:
  - existing volume mounted at `/data`
- Staging volume:
  - dedicated Railway volume mounted at `/data`
  - volume name currently `family-book-volume-PgmW`

Do not let staging and production share the same mounted volume. This app stores SQLite data, media, and backups in `/data`, so shared volumes would corrupt the release model.

## GitHub Automation

Repository workflow:
- [ci-deploy.yml](/Users/cheech/code/family-book/.github/workflows/ci-deploy.yml)

Behavior:
- Pull requests targeting `main` or `codex/staging`
  - run compile, focused pytest, and Docker build
- Pushes to `codex/staging`
  - run CI, then deploy to Railway `staging`
- Pushes to `main`
  - run CI, then deploy to Railway `production`

GitHub repository configuration required:
- repository secret: `RAILWAY_API_TOKEN`
- repository variable: `RAILWAY_PROJECT_ID`
- repository variable: `RAILWAY_SERVICE_ID`
- repository variable: `RAILWAY_PRODUCTION_ENV_ID`
- repository variable: `RAILWAY_STAGING_ENV_ID`

## Branch Flow

- day-to-day work:
  - `codex/*`
- integration / manual QA:
  - merge into `codex/staging`
- production release:
  - merge accepted staging work into `main`

Recommended PM workflow:
1. Builder works on a `codex/*` branch.
2. Auditor and CodeMap run on that branch.
3. Merge to `codex/staging`.
4. Railway `staging` auto-deploys.
5. Manually verify the sprint on `family-book-staging.up.railway.app`.
6. Merge `codex/staging` to `main`.
7. Railway `production` auto-deploys.

## One-Time Dashboard Checks

The GitHub Actions workflow handles deployment directly, but these Railway settings should still be verified once in the dashboard:

1. Service build path
- Railway should use the repository [Dockerfile](/Users/cheech/code/family-book/Dockerfile) contract consistently.
- The current environment config still reports `RAILPACK`; verify the service is not bypassing the Dockerfile path unexpectedly.

2. Production domain
- Production should keep `cutroni.xyz` as the canonical public URL.
- `BASE_URL` and `TRUSTED_HOSTS` should match the live production domain.

3. Staging domain
- Staging should keep `family-book-staging.up.railway.app`.
- `BASE_URL` and `TRUSTED_HOSTS` must match the staging domain.

4. Volume mounts
- Both environments must mount `/data`.
- Production and staging must use different volume IDs.

## Manual Smoke Checklist

After any staging deploy:

1. Open `/health` and confirm it returns `200`.
2. Log in with an admin account.
3. Confirm tree, person page, home feed, and map render.
4. Add or edit one record and verify it persists after refresh.
5. Confirm backup status renders on the admin page.

After any production deploy:

1. Check `/health`.
2. Log in and verify the home feed loads.
3. Verify no unexpected bootstrap/demo data appeared.
4. Confirm backups still report truthful status.
