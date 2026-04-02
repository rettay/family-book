#!/bin/sh
set -eu

mkdir -p /data/media /data/backups
chown -R appuser:appuser /data

# Export env vars so they survive the su switch
export LOAD_DEMO_DATA="${LOAD_DEMO_DATA:-false}"
export PORT="${PORT:-8000}"

exec su -s /bin/sh -p appuser -c '
uv run alembic upgrade head
if [ "${LOAD_DEMO_DATA}" = "true" ]; then
  echo "Loading basic demo data..."
  uv run python -m app.seed
elif [ "${LOAD_DEMO_DATA}" = "comprehensive" ]; then
  echo "Loading comprehensive demo data..."
  uv run python -m app.seed_comprehensive
fi
exec uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
'
