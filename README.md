# AVATAROS

> **Autonomous Governed Digital Human Production & Real-Time Interaction Operating System**
>
> *"Create a digital actor once. Direct them forever.*  
> *The system may change how the actor performs; it may not silently change who the actor is."*

[![Backend Tests](https://img.shields.io/badge/pytest-148%20passed-emerald)](https://github.com/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run%20%7C%20Secret%20Manager%20%7C%20GCS-4285F4)](https://cloud.google.com/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash%20%26%20Live%20API-8E75B2)](https://ai.google.dev/)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-Telemetry%20%26%20MCP-FEE440?logo=clickhouse&logoColor=black)](https://clickhouse.com/)
[![Mistral](https://img.shields.io/badge/Mistral%20AI-Conversational%20Fallback-FF7000)](https://mistral.ai/)

---

## Architecture Overview

AVATAROS is a production-grade autonomous digital human platform that marries **immutable persona governance (Digital DNA)**, **multi-agent reasoning (Google Gemini + ADK)**, **multimodal safety verification (Guardian Gate)**, **real-time conversational streaming (Gemini Live + Mistral)**, and **closed-loop evolutionary learning (ClickHouse + Model Context Protocol)**.

```
                              AVATAROS PIPELINE
                                      │
                                ORCHESTRATOR
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
    AI REASONING                     MCP                     DIGITAL DNA
 [REAL: Gemini 2.5]          [REAL: ClickHouse]           [IMMUTABLE LOCAL]
 [FALLBACK: Scripted]        [FALLBACK: In-Mem]                   │
          │                           │                        RIGHTS
          │                     CLICKHOUSE DB               [AUTH POLICY]
          │                    [REAL / IN-MEM]                    │
          └───────────────────────────┼───────────────────────────┘
                                      │
                               PRODUCTION RUN
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                VOICE GENERATION              AVATAR RENDERING
              [REAL: Cloud TTS]             [REAL: Neural API]
              [FALLBACK: Synth Tone]        [FALLBACK: FFmpeg Stitch]
                       │                             │
                       └──────────────┬──────────────┘
                                      │
                              GUARDIAN VERIFY
                           [REAL: Multimodal ASR]
                           [FALLBACK: Frame Scan]
                                      │
                              PUBLICATION GATE
                           [C2PA Provenance Seal]
                                      │
                             TELEMETRY / EVOLUTION
                           [ClickHouse Closed Loop]
```

---

## Key Capabilities

### 1. Dual Operational Modes
* **Studio Mode**: Autonomous end-to-end production DAG. Generates grounded multi-scene videos, synthesizes speech, drives facial animation via FFmpeg/neural models, validates safety through the Multimodal Guardian, and binds C2PA cryptographic provenance manifests.
* **Live Mode**: Conversational low-latency digital human runtime. Connects over WebSockets with Google Gemini Live API for real-time bidirectional multimodal interaction, falling back gracefully to Mistral AI for turn-based conversational reasoning or high-fidelity deterministic offline cascades.

### 2. Immutable Identity & Likeness Rights Governance
* **Digital DNA**: Encapsulates core facial descriptors, speech cadence, personality bounds, and strict safety guardrails. DNA is authoritative and read-only to production agents and live sessions.
* **Likeness Consent & Rights**: Rigorous authorization checking across production contexts (`interactive_live`, `product_education`, `broadcast_commercial`).

### 3. Google Gemini & Agentic Reasoning Network
* **Research Agent**: Scans documents, extracts grounded claims from hybrid BM25 + Vector knowledge bases with strict confidence thresholds ($\ge 0.60$).
* **Script Agent**: Synthesizes persona-aligned scene scripts conditioned on verified claims.
* **Critic Agent**: Validates brand tone, emotional congruence, and adherence to Digital DNA.
* **Director Agent**: Compiles high-resolution `PerformancePlan` instructions with explicit camera angles, emotion intensities, speech cadence multipliers, and gestural cues.

### 4. Multimodal Guardian & Authoritative Safety Gate
* **Visual Biometrics**: Validates facial likeness drift ($\ge 0.92$ threshold).
* **Vocal Fingerprinting**: Enforces voice timbre consistency ($\ge 0.90$ threshold).
* **Lip-Sync Alignment**: Authoritative safety invariant globally enforced at $\le 80\text{ ms}$ deviation.
* **Publication Gate**: Fail-closed release engine that aborts publishing if safety thresholds fail or claim drift is detected.

### 5. ClickHouse Analytics & Governed MCP Evolution Loop
* **Real Telemetry**: Streaming telemetry pipeline recording millisecond-level viewer engagement, emotion resonance, and scene drop-offs.
* **Model Context Protocol (MCP)**: Standards-compliant read-only analytics gateway exposing ClickHouse metrics directly to the Evolution Agent.
* **Statistical Lift Gate**: Proposes and verifies strategy adaptations (pacing, vocabulary, emotional registers) using Bayesian significance testing ($p < 0.05$).

---

## Provider Matrix & Transparency

AVATAROS operates with 100% honesty regarding provider capabilities. Every subsystem reports whether a real external cloud provider is active or operating via deterministic offline fallback:

| Subsystem | Real Cloud Provider | Offline / Dev Fallback | Capability Designation |
| :--- | :--- | :--- | :--- |
| **AI Reasoning** | Google Gemini (`gemini-2.5-flash`) | Scripted Deterministic Agent | Structured Agentic DAG |
| **Live Interaction** | Google Gemini Live API | Mistral / Deterministic | Realtime Audio Streaming |
| **Conversational Fallback** | Mistral AI (`mistral-small-latest`) | Deterministic Cascade | Turn-Based Text Reasoning |
| **Knowledge Embeddings**| Google Gemini (`text-embedding-004`) | Bag-of-Words / BM25 Index | Hybrid Vector + Lexical Search |
| **Voice Synthesis** | Google Cloud TTS / ElevenLabs | Synthetic Dual-Tone Generator | SHA-256 Audio Provenance |
| **Avatar Rendering** | Neural Video Generator API | Deterministic FFmpeg Stitcher | Frame-accurate Audio Muxing |
| **Multimodal Guardian**| Google Video Intelligence + Whisper | Frame & Spectrum Inspector | Multimodal Safety Verification |
| **Analytics Telemetry** | ClickHouse Cloud / Native HTTP | InMemoryTelemetryProvider | High-throughput OLAP Aggregations |
| **Tool Protocol** | ClickHouse MCP Gateway | In-Process Governed Dispatcher | Model Context Protocol (MCP) |
| **Media Storage** | Google Cloud Storage (GCS) | Local File Vault (`/static/media`)| Path-traversal Protected Storage |

---

## Quickstart

### Prerequisites
* Python 3.12+ (tested through Python 3.14)
* Node.js 18+ and npm
* FFmpeg installed locally (for video/audio rendering)
* Docker & Docker Compose (optional, for full containerized stack)

### 1. Local Development Setup

```bash
# Clone repository
git clone https://github.com/priteshvirat24/AvatarOS.git
cd AvatarOS

# Setup Backend Virtual Environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Setup Frontend
cd frontend
npm install
cd ..

# Copy Environment Template
cp .env.example .env
```

### 2. Run the Application

```bash
# Terminal 1: Launch Backend API (binds to 0.0.0.0:8000)
source backend/.venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Frontend (Vite SPA on http://localhost:3000)
cd frontend
npm run dev
```

### 3. Run with Docker Compose

```bash
docker compose up -d
```
Services will be available at:
* Frontend: `http://localhost:3000`
* Backend API & Docs: `http://localhost:8000/docs`
* ClickHouse HTTP: `http://localhost:8123`

---

## Automated Verification & Testing

AVATAROS maintains a comprehensive test suite of **148 automated tests** covering all 10 milestones:

```bash
# Run full test suite offline without external credentials
PYTHONPATH=. ./backend/.venv/bin/pytest backend/tests/

# Verify Frontend Production Build
cd frontend && npm run build
```

---

## Google Cloud Production Deployment

AVATAROS is built natively for serverless deployment on Google Cloud:

```bash
# Configure Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Submit Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or execute automated Cloud Run deployment script
chmod +x deploy/cloud_run_deploy.sh
./deploy/cloud_run_deploy.sh
```

---

## Repository Structure

```
AvatarOS/
├── backend/
│   ├── app/
│   │   ├── agents/          # Multi-Agent Network (Research, Script, Critic, Director, Guardian, Gate, Evolution)
│   │   ├── ai/              # Provider Abstractions (Gemini, Mistral, Live, Voice, Avatar Renderer)
│   │   ├── data/            # Seed DNA, Rights, Storage Abstraction, Telemetry
│   │   ├── live/            # Conversational Engine & LiveSessionManager
│   │   ├── mcp/             # ClickHouse Model Context Protocol Server & Tool Bridge
│   │   ├── memory/          # 3-Tier Isolated Memory (Character, Org, Session)
│   │   ├── models/          # Pydantic Core Domain Schemas (DNA, Rights, Live, Production)
│   │   ├── config.py        # Centralized Settings & Secret Management
│   │   └── main.py          # FastAPI Application & WebSocket Routes
│   ├── tests/               # 148 Pytest Unit & Integration Tests
│   └── requirements.txt     # Pinned Production Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI (Studio, LiveStage, LiveModeChat, Evolution, DNA, ProviderMatrix)
│   │   └── App.tsx          # Main Application Orchestrator
│   └── package.json
├── deploy/                  # Cloud Run Deployment Script & Documentation
├── cloudbuild.yaml          # Google Cloud Multi-Container Build Configuration
├── docker-compose.yml       # Complete Local Containerized Environment
├── .env.example             # Configuration Template (No Secrets Committed)
└── .gitignore               # Secret Hygiene & Build Caches Protection
```

---

## License

This project is licensed under the MIT License.
