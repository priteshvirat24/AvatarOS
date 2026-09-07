# AVATAROS - Google Cloud Production Deployment Architecture

This directory contains the production deployment assets for hosting **AVATAROS** on Google Cloud.

## 1. Cloud Architecture Overview

```
                          ┌───────────────────────────┐
                          │   Client Browser / Judge  │
                          └─────────────┬─────────────┘
                                        │ HTTPS / WSS
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
    ┌──────────────────────────┐                  ┌──────────────────────────┐
    │  Cloud Run: Frontend     │                  │   Cloud Run: Backend API  │
    │  (React + Vite on Nginx) │                  │ (FastAPI + Python 3.12)  │
    └──────────────────────────┘                  └─────────────┬────────────┘
                                                                │
                 ┌──────────────────────────────────────────────┼──────────────────────────────┐
                 ▼                                              ▼                              ▼
    ┌──────────────────────────┐                  ┌──────────────────────────┐   ┌──────────────────────────┐
    │   Google GenAI / Gemini  │                  │  Google Secret Manager   │   │  Google Cloud Storage    │
    │  (Gemini 2.5 Pro/Flash)  │                  │   (GEMINI_API_KEY, etc.) │   │  (Generated Media MP4s)  │
    └──────────────────────────┘                  └──────────────────────────┘   └──────────────────────────┘
                 ▲                                              ▲                              ▲
                 │                                              │                              │
    ┌────────────┴─────────────┐                  ┌─────────────┴────────────┐   ┌─────────────┴────────────┐
    │   Gemini Live API        │                  │ ClickHouse Cloud / VM    │   │  Artifact Registry       │
    │  (Bidirectional Stream)  │                  │ (Telemetry + Strategy)   │   │  (Container Images)      │
    └──────────────────────────┘                  └──────────────────────────┘   └──────────────────────────┘
```

---

## 2. Google Cloud Service Mapping

| Component | Google Cloud Service | Purpose | Fallback / Dev Mode |
|---|---|---|---|
| **API Server** | **Google Cloud Run** | Serverless container hosting for FastAPI backend with autoscaling | Local uvicorn / Docker Compose |
| **Frontend UI** | **Google Cloud Run** | High-performance Nginx hosting for React/Vite SPA bundle | Local Vite dev server |
| **AI Reasoning** | **Google Gemini 2.5 Pro / Flash** | Structured reasoning for Research, Script, Critic, and Director | Deterministic Rule Engine |
| **Live Conversation**| **Google Gemini Live API** | Bidirectional audio streaming with sub-800ms target response | Deterministic Live Cascade |
| **Secrets** | **Google Secret Manager** | Secure storage and mounting of API keys without code exposure | Local `.env` / Environment variables |
| **Media Storage** | **Google Cloud Storage (GCS)** | Object storage for rendered MP4 clips and C2PA metadata | Local static directory `/backend/static/media` |
| **Container Images** | **Artifact Registry** | Secure, managed Docker container image repository | Local Docker daemon |
| **Observability** | **Google Cloud Logging** | Structured JSON logs with trace ID propagation | Console structured logging |

---

## 3. Quick Deployment Guide

### Prerequisites
1. `gcloud` CLI installed and authenticated (`gcloud auth login`).
2. Google Cloud project configured (`gcloud config set project YOUR_PROJECT_ID`).
3. Docker installed locally (or submit builds directly via Cloud Build).

### Deploy via Automated Script
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GEMINI_API_KEY="your-gemini-api-key"

chmod +x deploy/cloud_run_deploy.sh
./deploy/cloud_run_deploy.sh
```

### Deploy via Google Cloud Build
```bash
gcloud builds submit --config=cloudbuild.yaml --project=YOUR_PROJECT_ID
```
