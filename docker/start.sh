#!/bin/sh
set -eu

mkdir -p /data/media /data/backups
chown -R appuser:appuser /data

exec su -s /bin/sh appuser -c "
uv run alembic upgrade head
if [ \"\${LOAD_DEMO_DATA:-false}\" = \"true\" ]; then
  uv run python -m app.seed
elif [ \"\${LOAD_DEMO_DATA:-false}\" = \"comprehensive\" ]; then
  uv run python -m app.seed_comprehensive
fi
exec uv run uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}
"
