# Task Packet - FB-083 Staging Environment Configuration

## Objective

Configure the Railway staging environment with the correct env vars, verify volume isolation, seed demo data, and confirm the staging app boots and serves pages correctly.

## Why / KPI

- Real family members are on production. Every push goes live immediately with no testing buffer.
- The staging environment exists in Railway but hasn't been configured or verified.
- CFLSR depends on changes being tested before reaching real users.

## Scope

- In scope:
  - Document all required Railway staging env vars (BASE_URL, SECRET_KEY, FERNET_KEY, DATABASE_URL, DATA_DIR, GOOGLE_CLIENT_ID, TRUSTED_HOSTS, LOAD_DEMO_DATA, etc.)
  - Create a staging env var checklist in docs/ops/
  - Verify Railway staging volume mount is isolated from production
  - Set LOAD_DEMO_DATA=true for staging so the seed runs on first deploy
  - Set ENABLE_API_DOCS=true for staging (useful for testing)
  - Confirm the staging app boots, health check passes, and pages render
  - Document the staging URL for team reference
- Out of scope:
  - Changing production env vars
  - CI workflow changes (separate packet)
  - Google OAuth config for staging domain (note as follow-up if needed)

## Likely Files

- `docs/ops/staging-env-vars.md` (new — checklist of required vars)
- `.env.staging.example` (new — example env file for staging)

## Acceptance Criteria

- [ ] Staging env var checklist documented with all required variables.
- [ ] .env.staging.example file created with placeholder values.
- [ ] Railway staging environment has correct BASE_URL pointing to staging domain.
- [ ] LOAD_DEMO_DATA=true set for staging.
- [ ] Staging app boots and /health returns ok (verified after first deploy).
- [ ] Staging volume confirmed isolated from production.

## Definition of Done

- [ ] Acceptance criteria satisfied
- [ ] Documentation committed
- [ ] Staging URL accessible after deploy
