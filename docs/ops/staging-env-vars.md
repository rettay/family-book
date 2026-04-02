# Staging Environment Variables

## Required Variables

Set these in the Railway staging environment dashboard.

| Variable | Example Value | Notes |
|---|---|---|
| `SECRET_KEY` | (generate unique) | **Must differ from production.** Use `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FERNET_KEY` | (generate unique) | **Must differ from production.** Use `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `BASE_URL` | `https://family-book-staging.up.railway.app` | Staging domain — used for CORS, OAuth redirects, invite links |
| `DATABASE_URL` | `sqlite:///data/family.db` | Default is fine — staging has its own volume |
| `DATA_DIR` | (leave empty) | Railway auto-sets `RAILWAY_VOLUME_MOUNT_PATH` |
| `GOOGLE_CLIENT_ID` | (same as production or separate) | If using same Google project, add staging URL to authorized redirect URIs |
| `TRUSTED_HOSTS` | `family-book-staging.up.railway.app` | Staging domain |
| `LOAD_DEMO_DATA` | `comprehensive` | Seeds ~100 synthetic persons on first boot |
| `ENABLE_API_DOCS` | `true` | Show Swagger at /docs for API testing |
| `LOG_LEVEL` | `DEBUG` | More verbose logging for staging |

## Optional Variables

| Variable | Example Value | Notes |
|---|---|---|
| `RESEND_API_KEY` | (same as production) | For testing invite emails from staging |
| `RESEND_FROM_EMAIL` | `staging@cutroni.xyz` | Separate sender for staging emails |
| `GOOGLE_MAPS_BROWSER_API_KEY` | (same as production) | For map/places testing |
| `GOOGLE_MAPS_SERVER_API_KEY` | (same as production) | For geocoding |
| `GOOGLE_MAPS_MAP_ID` | (same as production) | For styled maps |
| `ADMIN_EMAILS` | (your email) | Bootstrap admin on staging |
| `DEV_BYPASS_AUTH` | `false` | Keep auth real on staging for proper testing |

## Variables NOT to Set

| Variable | Why |
|---|---|
| `RAILWAY_VOLUME_MOUNT_PATH` | Auto-set by Railway |
| `PORT` | Auto-set by Railway |

## Volume Isolation

Staging and production must use **separate Railway volumes**. Verify in the Railway dashboard:
- Production service → Volume tab → note the volume name
- Staging service → Volume tab → confirm it's a DIFFERENT volume

Both mount to `/data` but contain independent SQLite databases and media files.

## First Deploy Checklist

1. Set all required variables above in Railway staging environment
2. Push to `codex/staging` branch to trigger CI → staging deploy
3. Wait for deploy to complete
4. Visit `https://family-book-staging.up.railway.app/health` — should return `{"status":"ok","db":"connected"}`
5. Visit the login page — should render
6. If LOAD_DEMO_DATA=comprehensive, the seed should have created ~100 persons
