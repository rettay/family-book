# Production Container Runtime

## Purpose

Define the supported production contract for the Family Book container image.

This document is for paid hosted archives and serious self-hosted production deployments. It is stricter than local development.

## Supported Runtime Shape

- one application runtime per family archive
- one persistent filesystem mounted at `DATA_DIR`
- one SQLite database inside that filesystem
- one archive-specific secret bundle

## Production Marker

Production contract enforcement turns on when any of these environment variables equals `production`:

- `FAMILY_BOOK_ENV`
- `APP_ENV`
- `ENVIRONMENT`
- `RAILWAY_ENVIRONMENT_NAME`

When production contract enforcement is active, the container startup will fail closed if required conditions are not met.

## Required Environment Variables

| Variable | Required | Notes |
|---|---|---|
| `FAMILY_BOOK_ENV` | recommended | Set to `production` for paid hosted archives. |
| `SECRET_KEY` | yes | Must be a generated 64-character hex string. |
| `FERNET_KEY` | yes | Must be a valid Fernet key. |
| `BASE_URL` | yes | Must be the canonical `https://` URL for the archive. |
| `DATABASE_URL` | yes for production docs | Current supported production shape is SQLite inside `DATA_DIR`. |
| `DATA_DIR` | yes for managed hosting | Must resolve to the persistent archive volume mount. |
| `TRUSTED_HOSTS` | yes | Include the archive host/domain and any proxy hostnames. |

## Common Optional Variables

| Variable | Optional | Notes |
|---|---|---|
| `SMTP_HOST` | optional | Required only if invite and magic-link email is enabled. |
| `SMTP_PORT` | optional | Defaults to `587`. |
| `SMTP_USER` | optional | Use archive-specific sender when possible. |
| `SMTP_PASS` | optional | Secret. |
| `SMTP_FROM` | optional | Sender header for invites and magic links. |
| `PASSKEY_RP_ID` | optional | Defaults from `BASE_URL` host. |
| `PASSKEY_RP_NAME` | optional | Defaults to `Family Book`. |
| `ADMIN_EMAILS` | optional | Bootstrap admin list. |
| `BOOTSTRAP_ADMIN_EMAIL` | optional | One-time bootstrap path. |
| `ENVELOPE_WEBHOOK_SECRET` | optional | Required only if inbound email is enabled. |
| `ENVELOPE_API_URL` | optional | Used for attachment allowlist inference. |
| `ENVELOPE_ALLOWED_HOSTS` | optional | Strongly recommended when inbound email attachments are enabled. |
| `MATRIX_HOMESERVER` | optional | Required only if Matrix bot integration is enabled. |
| `MATRIX_BOT_USER` | optional | Matrix credential. |
| `MATRIX_BOT_PASSWORD` | optional | Matrix credential. |
| `MATRIX_FAMILY_ROOM` | optional | Matrix room binding. |

## Variables That Must Be Off In Production

| Variable | Required state | Why |
|---|---|---|
| `DEV_BYPASS_AUTH` | `false` or unset | Development-only auth bypass. |
| `LOAD_DEMO_DATA` | `false` or unset | Paid production must never seed demo data. |
| `ENABLE_API_DOCS` | `false` | Keep docs off unless there is a separate reviewed decision. |

## Persistent Paths

Current supported persistent paths:

- database: `DATABASE_URL`, expected to resolve inside `DATA_DIR`
- media originals: `DATA_DIR/media`
- media thumbnails: `DATA_DIR/media/thumbnails`
- media variants: `DATA_DIR/media/variants`
- backups: `DATA_DIR/backups`
- export archive: `DATA_DIR/backups/family-book-backup.zip`

These paths must persist across container restarts and image updates.

## Startup Contract

Current container startup order:

1. create `DATA_DIR/media` and `DATA_DIR/backups`
2. create the SQLite parent directory if needed
3. run production runtime validation when production mode is enabled
4. run Alembic migrations
5. seed demo data only if `LOAD_DEMO_DATA` explicitly requests it
6. start `uvicorn`

Operational consequences:

- migrations run on every boot
- invalid production config fails before migrations and before demo seed logic
- the image is not a blue/green migration coordinator; rollouts should assume one archive runtime at a time

## Health And Readiness

Current health endpoint:

- `GET /health`

Behavior:

- returns `200`
- reports `status=ok` and `db=connected` if the DB probe succeeds
- reports `status=degraded` if the DB probe fails

What it does not prove:

- SMTP connectivity
- backup freshness
- Matrix sync health
- restore verification recency

Those are operator checks, not orchestrator liveness.

## Release And Rollback

Recommended image tagging:

- immutable image per commit SHA
- optional human tag per release

Rollback rule:

- revert to the prior known-good image tag
- do not roll back by reusing a shared mutable tag
- do not delete archive data during rollback

Because SQLite and media live on the persistent archive volume, rollbacks are application-image rollbacks, not data resets.

## Smoke Commands

Runtime checks:

```bash
uv run pytest tests/test_config.py tests/test_runtime_contract.py -q
```

If Docker runtime behavior changed:

```bash
docker build -t family-book:local .
```

## Unsupported Production Shapes

- one app runtime serving multiple paid archives from one shared `DATA_DIR`
- enabling `LOAD_DEMO_DATA` in paid production
- trusting a container image alone without persistent storage and backup procedures
