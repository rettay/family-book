#!/bin/sh
set -eu

mkdir -p /data/media /data/backups
chown -R appuser:appuser /data

# Ensure uv cache is writable regardless of which user runs the container
export UV_CACHE_DIR=/tmp/uv-cache

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
