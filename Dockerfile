# ==============================================================================
# AVATAROS - single-image build
#
# One container serves the React SPA and the FastAPI API from the same origin, so
# a deployed instance is a single URL with no CORS configuration and no second
# service to keep alive. Cloud Run scales it to zero between visits.
#
# Three stages:
#   1. web      - builds the Vite bundle
#   2. mcpdeps  - builds an isolated virtualenv for the OFFICIAL mcp-clickhouse
#                 server, whose fastmcp/starlette pins conflict with the app's
#                 FastAPI pin. Keeping them in separate environments is what lets
#                 AVATAROS talk to the real partner server over a real transport
#                 instead of reimplementing it in-process.
#   3. runtime  - the application image
# ==============================================================================

# ------------------------------------------------------------------ 1. frontend
FROM node:22-slim AS web

WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# ------------------------------------------- 2. official MCP server environment
FROM python:3.12-slim AS mcpdeps

RUN pip install --no-cache-dir --upgrade pip virtualenv
COPY backend/requirements-mcp-server.txt /tmp/requirements-mcp-server.txt
RUN python -m venv /opt/mcp-server-venv && \
    /opt/mcp-server-venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/mcp-server-venv/bin/pip install --no-cache-dir -r /tmp/requirements-mcp-server.txt


# ------------------------------------------------------------------- 3. runtime
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8080 \
    SERVE_FRONTEND=true \
    FRONTEND_DIST_PATH=/app/frontend_dist \
    MCP_SERVER_COMMAND=/opt/mcp-server-venv/bin/mcp-clickhouse

WORKDIR /app

# ffmpeg/ffprobe back the deterministic renderer and the media inspector.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg \
      curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# The official partner server, isolated from the application's dependency tree.
COPY --from=mcpdeps /opt/mcp-server-venv /opt/mcp-server-venv

COPY backend /app/backend
COPY --from=web /web/dist /app/frontend_dist

RUN mkdir -p /app/backend/static/media

# Cloud Run supplies PORT; the default keeps `docker run` working locally.
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

CMD ["sh", "-c", "exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
