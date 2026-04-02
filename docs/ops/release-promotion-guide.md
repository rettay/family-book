# Release Promotion Guide

## Overview

All code changes go through staging before reaching production. The workflow is:

```
Feature branch → codex/staging → staging auto-deploy → acceptance test → main → approval gate → production deploy
```

## Step-by-Step Process

### 1. Develop on a feature branch

```bash
git checkout codex/staging
git pull
git checkout -b feature/my-change
# ... make changes, commit ...
git push -u origin feature/my-change
```

### 2. Deploy to staging

Merge your feature branch into `codex/staging`:

```bash
git checkout codex/staging
git merge feature/my-change
git push
```

CI automatically:
- Runs quality checks (compile, pytest, Playwright)
- If all pass, deploys to staging

### 3. Test on staging

Visit the staging URL and run the acceptance checklist:
- **Quick smoke test** (2 min): for low-risk changes — see `docs/ops/staging-acceptance-checklist.md`
- **Full acceptance** (15 min): for significant changes

### 4. Promote to production

Once staging is verified, merge to `main`:

```bash
git checkout main
git merge codex/staging
git push
```

CI automatically:
- Runs quality checks
- **Waits for manual approval** (GitHub Actions environment protection)
- After approval, deploys to production

### 5. Approve the production deploy

1. Go to GitHub Actions → the running workflow
2. The `deploy` job shows "Waiting for review"
3. Click "Review deployments" → select `production` → "Approve and deploy"

## GitHub Environment Setup (One-Time)

To enable the approval gate, configure the `production` environment in GitHub:

1. Go to repo → Settings → Environments
2. Click `production` (create if it doesn't exist)
3. Check "Required reviewers"
4. Add yourself as a required reviewer
5. Save

The `staging` environment should have NO required reviewers (auto-deploy).

## Hotfix Process

For urgent production fixes that can't wait for staging:

```bash
git checkout main
# ... make minimal fix ...
git commit -m "hotfix: description"
git push
```

CI runs quality checks, then waits for your approval. After approving:
- Backport the fix to `codex/staging`: `git checkout codex/staging && git merge main && git push`

## Environment URLs

| Environment | URL | Branch | Deploy |
|---|---|---|---|
| **Production** | `https://cutroni.xyz` | `main` | Manual approval |
| **Staging** | `https://family-book-staging.up.railway.app` | `codex/staging` | Auto |
| **Local** | `http://localhost:8000` | any | `uv run uvicorn ...` |

## Branch Mapping

```
main                → production (Railway production env)
codex/staging       → staging (Railway staging env)
feature/*           → local only (no auto-deploy)
```
