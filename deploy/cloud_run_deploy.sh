#!/usr/bin/env bash
# ==============================================================================
# AVATAROS - Google Cloud Run Production Deployment Script
# Provisions Artifact Registry, builds container images, sets Secret Manager,
# and deploys backend & frontend services to Cloud Run.
# ==============================================================================

set -euo pipefail

# Configuration defaults
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo "")}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
REPO_NAME="avataros-repo"
BACKEND_SERVICE="avataros-backend"
FRONTEND_SERVICE="avataros-frontend"

if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: Google Cloud Project ID is not set. Set GOOGLE_CLOUD_PROJECT or run 'gcloud config set project <ID>'."
    exit 1
fi

echo "=============================================================================="
echo " Deploying AVATAROS to Google Cloud"
echo " Project:  $PROJECT_ID"
echo " Region:   $REGION"
echo "=============================================================================="

# 1. Enable required Google Cloud APIs
echo "[1/6] Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    --project="$PROJECT_ID"

# 2. Create Artifact Registry repository if it does not exist
echo "[2/6] Ensuring Artifact Registry repository '$REPO_NAME' exists..."
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="AVATAROS container images" \
        --project="$PROJECT_ID"
fi

# 3. Configure Secret Manager for Gemini API key if present in env
if [[ -n "${GEMINI_API_KEY:-}" ]]; then
    echo "[3/6] Configuring GEMINI_API_KEY in Secret Manager..."
    if ! gcloud secrets describe GEMINI_API_KEY --project="$PROJECT_ID" &>/dev/null; then
        echo -n "$GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=- --project="$PROJECT_ID"
    else
        echo -n "$GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=- --project="$PROJECT_ID"
    fi
else
    echo "[3/6] Notice: GEMINI_API_KEY not provided in environment; backend will boot with honest Deterministic Fallback engine."
fi

# 4. Build and Push Backend Image
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/avataros-backend:latest"
echo "[4/6] Building Backend Container Image ($BACKEND_IMAGE)..."
docker build -t "$BACKEND_IMAGE" -f backend/Dockerfile .
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
docker push "$BACKEND_IMAGE"

# 5. Deploy Backend Service to Cloud Run
echo "[5/6] Deploying Backend to Cloud Run ($BACKEND_SERVICE)..."
SECRET_FLAG=""
if gcloud secrets describe GEMINI_API_KEY --project="$PROJECT_ID" &>/dev/null; then
    SECRET_FLAG="--set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest"
fi

gcloud run deploy "$BACKEND_SERVICE" \
    --image="$BACKEND_IMAGE" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --port=8000 \
    --memory=2Gi \
    --cpu=2 \
    --set-env-vars="APP_ENV=production,HOST=0.0.0.0,PORT=8000,AVATAROS_VERSION=1.0.0" \
    $SECRET_FLAG \
    --project="$PROJECT_ID"

BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID")
echo "Backend URL: $BACKEND_URL"

# 6. Build and Deploy Frontend Service
FRONTEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/avataros-frontend:latest"
echo "[6/6] Building and Deploying Frontend Container ($FRONTEND_IMAGE)..."
docker build -t "$FRONTEND_IMAGE" -f frontend/Dockerfile .
docker push "$FRONTEND_IMAGE"

gcloud run deploy "$FRONTEND_SERVICE" \
    --image="$FRONTEND_IMAGE" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --port=3000 \
    --memory=512Mi \
    --cpu=1 \
    --set-env-vars="VITE_BACKEND_URL=$BACKEND_URL" \
    --project="$PROJECT_ID"

FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region="$REGION" --format='value(status.url)' --project="$PROJECT_ID")

echo "=============================================================================="
echo " AVATAROS Deployment Completed Successfully!"
echo " Frontend: $FRONTEND_URL"
echo " Backend:  $BACKEND_URL"
echo " Health:   $BACKEND_URL/health"
echo "=============================================================================="
