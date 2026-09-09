#!/usr/bin/env bash
#
# Deploys AVATAROS to Cloud Run as a single public service.
#
# Idempotent: creates the Artifact Registry repository and Secret Manager secrets
# only if they are missing, then builds and deploys. Safe to re-run.
#
#   PROJECT_ID=my-project \
#   CLICKHOUSE_URL=https://abc.us-central1.gcp.clickhouse.cloud:8443 \
#   CLICKHOUSE_PASSWORD=... \
#   GEMINI_API_KEY=... \
#   ./deploy/cloud_run_deploy.sh
#
# Secrets are written to Secret Manager and referenced by the service at runtime.
# They are never baked into the image and never passed as build substitutions.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-avataros}"
REPO="${REPO:-avataros-repo}"

CLICKHOUSE_URL="${CLICKHOUSE_URL:-}"
CLICKHOUSE_DATABASE="${CLICKHOUSE_DATABASE:-default}"
CLICKHOUSE_USERNAME="${CLICKHOUSE_USERNAME:-default}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-}"
GEMINI_API_KEY="${GEMINI_API_KEY:-}"

SECRET_CH_PASSWORD="avataros-clickhouse-password"
SECRET_GEMINI="avataros-gemini-api-key"

die()  { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mwarning:\033[0m %s\n' "$*" >&2; }

# ---------------------------------------------------------------- preflight ---

[[ -n "$PROJECT_ID" ]] || die "PROJECT_ID is not set and no gcloud default project is configured."
command -v gcloud >/dev/null || die "gcloud is not installed."

if [[ -z "$CLICKHOUSE_URL" ]]; then
  die "CLICKHOUSE_URL is required.
     AVATAROS reads analytics through the official mcp-clickhouse server, which
     needs a reachable ClickHouse Cloud or self-hosted cluster. Deploying without
     one would leave every analytics panel showing 'no data'.
     Example: https://<id>.<region>.gcp.clickhouse.cloud:8443"
fi

if [[ -z "$GEMINI_API_KEY" ]]; then
  warn "GEMINI_API_KEY is not set. The agent chain will run on the deterministic
     offline engine and the UI will label it as such. Set it to run on Gemini."
fi

info "Project:  $PROJECT_ID"
info "Region:   $REGION"
info "Service:  $SERVICE"
info "Cluster:  $CLICKHOUSE_URL (db: $CLICKHOUSE_DATABASE, user: $CLICKHOUSE_USERNAME)"

gcloud config set project "$PROJECT_ID" >/dev/null 2>&1

# ------------------------------------------------------------------- APIs -----

info "Ensuring required APIs are enabled"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  --project "$PROJECT_ID" >/dev/null

# ------------------------------------------------------- Artifact Registry -----

if ! gcloud artifacts repositories describe "$REPO" \
      --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1; then
  info "Creating Artifact Registry repository '$REPO'"
  gcloud artifacts repositories create "$REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="AVATAROS container images" \
    --project "$PROJECT_ID" >/dev/null
else
  info "Artifact Registry repository '$REPO' already exists"
fi

# ----------------------------------------------------------------- secrets -----

# Writes a new version of a secret, creating the secret first if needed.
put_secret() {
  local name="$1" value="$2"
  if [[ -z "$value" ]]; then
    # Ensure the secret exists with an empty version so --set-secrets can bind it.
    if ! gcloud secrets describe "$name" --project "$PROJECT_ID" >/dev/null 2>&1; then
      info "Creating empty secret '$name' (no value supplied)"
      gcloud secrets create "$name" --replication-policy=automatic --project "$PROJECT_ID" >/dev/null
      printf '' | gcloud secrets versions add "$name" --data-file=- --project "$PROJECT_ID" >/dev/null
    fi
    return
  fi

  if ! gcloud secrets describe "$name" --project "$PROJECT_ID" >/dev/null 2>&1; then
    info "Creating secret '$name'"
    gcloud secrets create "$name" --replication-policy=automatic --project "$PROJECT_ID" >/dev/null
  else
    info "Adding a new version to secret '$name'"
  fi
  printf '%s' "$value" | gcloud secrets versions add "$name" --data-file=- --project "$PROJECT_ID" >/dev/null
}

put_secret "$SECRET_CH_PASSWORD" "$CLICKHOUSE_PASSWORD"
put_secret "$SECRET_GEMINI"      "$GEMINI_API_KEY"

# Grant the runtime service account read access to both secrets.
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for secret in "$SECRET_CH_PASSWORD" "$SECRET_GEMINI"; do
  gcloud secrets add-iam-policy-binding "$secret" \
    --member="serviceAccount:${RUNTIME_SA}" \
    --role="roles/secretmanager.secretAccessor" \
    --project "$PROJECT_ID" >/dev/null 2>&1 || \
    warn "Could not bind secretAccessor on '$secret' to $RUNTIME_SA — grant it manually if the service fails to start."
done

# ------------------------------------------------------------------ build -----

info "Submitting build (this takes a few minutes on a cold cache)"
gcloud builds submit \
  --config cloudbuild.yaml \
  --project "$PROJECT_ID" \
  --substitutions="_LOCATION=${REGION},_SERVICE=${SERVICE},_REPO=${REPO},_CLICKHOUSE_URL=${CLICKHOUSE_URL},_CLICKHOUSE_DATABASE=${CLICKHOUSE_DATABASE},_CLICKHOUSE_USERNAME=${CLICKHOUSE_USERNAME}" \
  .

# ----------------------------------------------------------------- verify -----

URL="$(gcloud run services describe "$SERVICE" --region "$REGION" \
        --project "$PROJECT_ID" --format='value(status.url)')"

info "Deployed: $URL"
info "Verifying the live service reports a real partner connection"

# Reads /health and exits non-zero unless the MCP partner is genuinely ready.
# Kept in its own file so the shell never has to escape quotes into Python.
VERIFY_PY="$(mktemp)"
trap 'rm -f "$VERIFY_PY"' EXIT
cat > "$VERIFY_PY" <<'PY'
import json
import sys

data = json.load(sys.stdin)
services = data.get("services", {})
mcp = services.get("mcp", {})

print("  status:     {}".format(data.get("status")))
print("  clickhouse: {}".format(services.get("clickhouse")))
print("  mcp ready:  {}  server: {}  transport: {}".format(
    mcp.get("ready"), mcp.get("server_identity"), mcp.get("transport")))
if mcp.get("last_error"):
    print("  mcp error:  {}".format(mcp["last_error"]))

sys.exit(0 if mcp.get("ready") else 1)
PY

# Cold start plus the MCP handshake; retry rather than judging on one attempt.
for attempt in $(seq 1 10); do
  if body="$(curl -fsS --max-time 25 "${URL}/health" 2>/dev/null)"; then
    if printf '%s' "$body" | python3 "$VERIFY_PY"; then
      info "Live and connected to the partner server."
      info "Open: $URL"
      exit 0
    fi
    warn "Service is up but the MCP partner is not ready yet (attempt ${attempt}/10)"
  else
    warn "Health check not answering yet (attempt ${attempt}/10)"
  fi
  sleep 10
done

die "Deployed to $URL but the MCP partner never became ready. Check:
     gcloud run services logs read $SERVICE --region $REGION --project $PROJECT_ID"
