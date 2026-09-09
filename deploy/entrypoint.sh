#!/usr/bin/env bash
#
# Container entrypoint.
#
# SEED_ON_START waits for the configured ClickHouse to accept connections, then
# applies the schema and loads demo telemetry before serving. This is what makes
# a cold deployment land on a populated cluster instead of showing "no data"
# across every analytics panel.
#
# It does not care how ClickHouse is provided: a Cloud Run sidecar sharing
# localhost, a compose service, or a managed cluster are all the same to it.

set -euo pipefail

log() { printf '[entrypoint] %s\n' "$*"; }

if [ "${SEED_ON_START:-false}" = "true" ]; then
  probe="${CLICKHOUSE_URL:-http://127.0.0.1:8123}/ping"
  log "waiting for ClickHouse at ${probe}"

  ready=false
  for _ in $(seq 1 90); do
    if curl -fsS --max-time 2 "$probe" >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 1
  done

  if [ "$ready" != "true" ]; then
    # Serving without the cluster would misrepresent the partner integration,
    # so fail visibly rather than starting in a degraded state that looks fine.
    log "FATAL: ClickHouse did not become reachable at ${probe}"
    exit 1
  fi

  log "ClickHouse is up; applying schema and seeding demo telemetry"
  if ! python -m backend.app.data.seed_clickhouse; then
    log "FATAL: seeding failed"
    exit 1
  fi
fi

log "starting AVATAROS on port ${PORT:-8080}"
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
