#!/bin/sh
set -eu

mkdir -p /data/media /data/backups
chown -R appuser:appuser /data

exec su -s /bin/sh appuser -c "
uv run alembic upgrade head
if [ \"\${LOAD_DEMO_DATA:-false}\" = \"true\" ]; then
  uv run python -m app.seed
fi
exec uv run uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}
"
