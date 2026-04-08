#!/bin/sh
set -eu

DATA_ROOT="${DATA_DIR:-/data}"
DB_PATH=""
case "${DATABASE_URL:-}" in
  sqlite:///*)
    DB_PATH="${DATABASE_URL#sqlite:///}"
    ;;
esac

mkdir -p "${DATA_ROOT}/media" "${DATA_ROOT}/backups"
if [ -n "${DB_PATH}" ]; then
  mkdir -p "$(dirname "${DB_PATH}")"
fi

if [ -d "${DATA_ROOT}" ]; then
  chown -R appuser:appuser "${DATA_ROOT}"
fi

# Ensure uv cache is writable regardless of which user runs the container
export UV_CACHE_DIR=/tmp/uv-cache

# Fail closed for paid/production archives before migrations or demo seeding.
uv run python -m app.runtime_contract

# Run migrations and optional seeding
uv run alembic upgrade head

DEMO_MODE="${LOAD_DEMO_DATA:-false}"
if [ "$DEMO_MODE" = "true" ]; then
  echo "Loading basic demo data..."
  uv run python -m app.seed
elif [ "$DEMO_MODE" = "comprehensive" ]; then
  echo "Loading comprehensive demo data..."
  uv run python -m app.seed_comprehensive
else
  echo "LOAD_DEMO_DATA=${DEMO_MODE} — skipping seed."
fi

# Start the app
exec uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
