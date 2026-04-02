# Developer Workflow

## Overview

Family Book uses a staging-first deployment model. All changes go through staging before reaching production.

```
feature branch → codex/staging → staging auto-deploy → acceptance test → main → approval gate → production
```

## Environments

| Environment | URL | Branch | Deploy | Data |
|---|---|---|---|---|
| **Local** | `http://localhost:8000` | any | manual | local SQLite |
| **Staging** | `https://family-book-staging.up.railway.app` | `codex/staging` | auto on push | isolated Railway volume |
| **Production** | `https://cutroni.xyz` | `main` | manual approval | production Railway volume |

## Local Development

```bash
cp .env.example .env          # Edit with your values
uv sync                       # Install dependencies
uv run alembic upgrade head   # Run migrations
uv run python -m app.seed     # Optional: load basic seed data
uv run python -m app.seed_comprehensive  # Optional: load ~100 person test corpus
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Run tests:
```bash
uv run pytest                 # Full test suite
uv run pytest tests/test_i18n.py  # i18n parity check
make test-ui-playwright       # Playwright browser tests
```

## Feature Development

1. **Branch from staging:**
   ```bash
   git checkout codex/staging && git pull
   git checkout -b feature/my-change
   ```

2. **Develop and test locally.** Run `uv run pytest` before pushing.

3. **Push and deploy to staging:**
   ```bash
   git checkout codex/staging
   git merge feature/my-change
   git push
   ```
   CI runs quality checks → auto-deploys to staging.

4. **Test on staging.** Run the acceptance checklist:
   - Quick smoke test (2 min) for low-risk changes
   - Full acceptance (15 min) for significant changes
   - See `docs/ops/staging-acceptance-checklist.md`

5. **Promote to production:**
   ```bash
   git checkout main
   git merge codex/staging
   git push
   ```
   CI runs quality checks → waits for manual approval → deploys to production.

6. **Approve the deploy** in GitHub Actions UI.

## Hotfixes

For urgent production fixes:

```bash
git checkout main
# Make minimal fix
git commit -m "hotfix: description"
git push
# Approve in GitHub Actions
# Then backport:
git checkout codex/staging && git merge main && git push
```

## Demo Data

Two seed modes available:

| Mode | Command | Persons | Use case |
|---|---|---|---|
| Basic | `uv run python -m app.seed` | ~20 | Playwright tests, quick local dev |
| Comprehensive | `uv run python -m app.seed_comprehensive` | ~100 | Staging stress test, i18n testing |

The comprehensive seed includes international names (CJK, Cyrillic, Arabic, diacritics), complex relationships (adoptions, guardians, blended families), and rich biographical data.

Set `LOAD_DEMO_DATA=comprehensive` in Railway staging env vars to auto-seed on deploy.

## CI Pipeline

```
push to any branch
  → compile check
  → pytest (focused suite)
  → Playwright browser tests
  → Docker build
  → if codex/staging: auto-deploy to staging
  → if main: manual approval gate → deploy to production
```

## Key References

- Environment variables: `docs/ops/staging-env-vars.md`
- Acceptance checklist: `docs/ops/staging-acceptance-checklist.md`
- Promotion guide: `docs/ops/release-promotion-guide.md`
- Architecture: `docs/CODEBASE_BRIEFING.md`
- Project rules: `CLAUDE.md`
