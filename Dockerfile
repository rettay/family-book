FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv==0.9.26

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

COPY . .
COPY docker/start.sh /start.sh

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /data/media /data/backups \
    && chown -R appuser:appuser /app /data \
    && chmod +x /start.sh

EXPOSE 8000

CMD ["/start.sh"]
