#!/bin/sh
set -eu

mkdir -p /data/media /data/backups
chown -R appuser:appuser /data

# Run migrations and optional seeding as root (before switching to appuser)
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

# Start the app as non-root user
exec su -s /bin/sh appuser -c "exec uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
