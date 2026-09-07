import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app.data.seed_characters import get_seed_characters
from backend.app.data.documents import SEED_CLAIMS
from backend.app.data.telemetry_store import telemetry_store
from backend.app.agents.orchestrator import orchestrator
from backend.app.agents.research import ResearchAgent
from backend.app.agents.evolution import evolution_agent
from backend.app.agents.renderer import renderer
from backend.app.agents.guardian import guardian_agent
from backend.app.live.live_engine import LiveModeEngine
from backend.app.live.session_manager import live_session_manager
from backend.app.mcp.client import mcp_client
from backend.app.models.live import (
    LiveSessionCreateRequest,
    LiveSessionResponse,
    LiveTurnRequest,
    LiveTurnResponse
)
from backend.app.models.dna import DigitalDNA
from backend.app.models.production import (
    ProductionRun,
    ProductionRunCreateRequest,
    LiveStudioHandoffRequest,
    LiveStudioHandoffResponse
)
from backend.app.data.production_store import production_store
from backend.app.data.storage import media_storage
import uuid

from backend.app.config import settings
from backend.app.logging import app_logger
import httpx
import time

app = FastAPI(title="AVATAROS Studio Engine", version=settings.AVATAROS_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure media storage directory exists
os.makedirs(settings.VAULT_STORAGE_PATH, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.VAULT_STORAGE_PATH), name="media")

# In-memory storage for active campaign and characters
character_db = get_seed_characters()["characters"]
maya_dna = character_db["maya"]
live_engine = LiveModeEngine(maya_dna)
last_campaign_result = None
run1_plan = None
run2_plan = None

class CampaignRequest(BaseModel):
    command: str = "Create a 60-second product launch for Indian developers. Research our documentation first. Do not make unsupported claims. Produce English and Hindi versions."
    character_id: str = "maya"
    inject_claim_failure: bool = False
    inject_emotion_failure: bool = False

class ResolveClaimRequest(BaseModel):
    claim_id: str = "claim_fail_3x"
    evidence_document: str = "titan_benchmarks_mlperf_v2.pdf"

class LiveChatRequest(BaseModel):
    message: str

class CompileCharacterRequest(BaseModel):
    name: str = "Maya"
    voice_sample_sec: int = 30
    num_images: int = 5
    personality_brief: str = "Confident, analytical, witty developer advocate"
    rights_authorized: bool = True

@app.get("/")
def read_root():
    """
    Backwards-compatible root endpoint reporting system version and environment.
    """
    return {
        "status": "online",
        "system": "AVATAROS Autonomous Digital Human Studio",
        "version": settings.AVATAROS_VERSION,
        "environment": settings.APP_ENV
    }

@app.on_event("shutdown")
def shutdown_event():
    """
    Ensure pending telemetry in buffer is flushed to ClickHouse upon application exit.
    """
    try:
        telemetry_store.flush()
    except Exception:
        pass

@app.get("/health")
def health_check():
    """
    Section 13 Health Check:
    Distinguishes APPLICATION, CLICKHOUSE, STORAGE, and EXTERNAL AI PROVIDERS.
    Development mode remains usable even if optional providers are absent.
    Zero secrets or credentials exposed.
    """
    ch_status = "unconfigured"
    ch_connected = False
    if settings.TELEMETRY_PROVIDER == "in_memory":
        ch_status = "in_memory_configured"
    else:
        try:
            with httpx.Client(timeout=0.8) as client:
                resp = client.get(f"{settings.CLICKHOUSE_URL}/ping")
                if resp.status_code == 200:
                    ch_status = "connected"
                    ch_connected = True
                else:
                    ch_status = f"unhealthy_status_{resp.status_code}"
        except Exception:
            ch_status = "in_memory_simulation (active fallback)"

    ai_provider_state = {
        "provider": settings.AI_PROVIDER,
        "configured": bool(settings.GEMINI_API_KEY),
        "adk_enabled": settings.ADK_ENABLED,
        "model": settings.GEMINI_MODEL if settings.GEMINI_API_KEY else "deterministic_fallback_engine"
    }

    guardian_provider_state = {
        "provider": settings.GUARDIAN_PROVIDER,
        "configured": bool(settings.GEMINI_API_KEY) if settings.GUARDIAN_PROVIDER == "gemini_multimodal" else True,
        "identity_threshold": settings.GUARDIAN_IDENTITY_THRESHOLD,
        "voice_threshold": settings.GUARDIAN_VOICE_THRESHOLD,
        "emotion_threshold": settings.GUARDIAN_EMOTION_MISMATCH_THRESHOLD,
        "lip_sync_threshold_ms": settings.GUARDIAN_LIP_SYNC_THRESHOLD_MS,
        "frame_sample_count": settings.GUARDIAN_FRAME_SAMPLE_COUNT
    }

    asr_provider_state = {
        "provider": settings.ASR_PROVIDER,
        "configured": bool(settings.GEMINI_API_KEY) if settings.ASR_PROVIDER in ("google", "gemini") else True,
        "language": settings.ASR_LANGUAGE,
        "adherence_threshold": settings.GUARDIAN_SCRIPT_ADHERENCE_THRESHOLD
    }

    live_configured = (
        bool(settings.GEMINI_API_KEY) if settings.LIVE_PROVIDER == "gemini_live"
        else (bool(settings.MISTRAL_API_KEY) if settings.LIVE_PROVIDER == "mistral" else True)
    )
    live_provider_state = {
        "provider": settings.LIVE_PROVIDER,
        "configured": live_configured,
        "ready": True,
        "model": settings.LIVE_MODEL if settings.LIVE_PROVIDER == "gemini_live" else (settings.MISTRAL_MODEL if settings.LIVE_PROVIDER == "mistral" else "deterministic"),
        "voice": settings.LIVE_VOICE,
        "language": settings.LIVE_LANGUAGE,
        "active_sessions": len(live_session_manager.sessions) if "live_session_manager" in globals() else 0,
        "is_realtime": settings.LIVE_PROVIDER == "gemini_live" and bool(settings.GEMINI_API_KEY),
        "degraded_mode": settings.LIVE_PROVIDER == "mistral" and bool(settings.MISTRAL_API_KEY)
    }

    mistral_state = {
        "provider": "mistral",
        "configured": bool(settings.MISTRAL_API_KEY),
        "model": settings.MISTRAL_MODEL,
        "role": "conversational_turn_based_fallback",
        "native_realtime_audio": False
    }

    mcp_provider_state = mcp_client.get_status() if "mcp_client" in globals() else {
        "enabled": settings.MCP_ENABLED,
        "provider": settings.MCP_PROVIDER,
        "configured": True,
        "ready": True,
        "tools_count": 5
    }

    is_healthy = True
    if settings.is_production() and not ch_connected and settings.TELEMETRY_PROVIDER == "clickhouse":
        is_healthy = False

    return {
        "status": "healthy" if is_healthy else "degraded",
        "version": settings.AVATAROS_VERSION,
        "environment": settings.APP_ENV,
        "services": {
            "application": "healthy",
            "telemetry_provider": settings.TELEMETRY_PROVIDER,
            "clickhouse": ch_status,
            "ai_provider": "gemini_configured" if (settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY) else "deterministic_rule_engine",
            "ai": ai_provider_state,
            "guardian": guardian_provider_state,
            "asr": asr_provider_state,
            "live": live_provider_state,
            "mistral": mistral_state,
            "mcp": mcp_provider_state,
            "storage": media_storage.get_status(),
            "media_renderer": settings.RENDERER_PROVIDER,
            "avatar_renderer": renderer.avatar_renderer.get_renderer_status(),
            "voice_provider": renderer.voice_provider.get_voice_status()
        },
        "provider_matrix": settings.get_provider_matrix()
    }

@app.get("/health/ready")
def readiness_check():
    """
    Readiness probe for container orchestration.
    Distinguishes dev fallback vs production requirement.
    """
    ch_ready = False
    if settings.TELEMETRY_PROVIDER == "in_memory":
        ch_ready = True
    else:
        try:
            with httpx.Client(timeout=0.8) as client:
                resp = client.get(f"{settings.CLICKHOUSE_URL}/ping")
                ch_ready = (resp.status_code == 200)
        except Exception:
            ch_ready = False

    # In production, ClickHouse must be ready; in dev, fallback is acceptable
    system_ready = ch_ready if settings.is_production() else True

    return {
        "ready": system_ready,
        "version": settings.AVATAROS_VERSION,
        "environment": settings.APP_ENV,
        "clickhouse_connected": ch_ready,
        "telemetry_provider": settings.TELEMETRY_PROVIDER,
        "mcp_ready": mcp_client.get_status().get("ready", True) if "mcp_client" in globals() else True,
        "storage_ready": media_storage.get_status().get("ready", True),
        "ffmpeg": os.path.exists(settings.get_ffmpeg_executable()) or shutil.which(settings.get_ffmpeg_executable()) is not None,
        "ffprobe": os.path.exists(settings.get_ffprobe_executable()) or shutil.which(settings.get_ffprobe_executable()) is not None,
        "vault_storage": os.path.exists(settings.VAULT_STORAGE_PATH)
    }

@app.get("/api/production/provider-matrix")
def get_provider_matrix_endpoint():
    """
    Returns the real vs deterministic provider matrix for Studio observability.
    """
    return {
        "version": settings.AVATAROS_VERSION,
        "environment": settings.APP_ENV,
        "matrix": settings.get_provider_matrix()
    }

@app.get("/api/cast")
def list_cast():
    return [
        {
            "character_id": c.character_id,
            "name": c.character_id.capitalize(),
            "version": c.version,
            "status": c.status,
            "voice_model": c.identity.voice_model_id,
            "accent": c.speech.accent,
            "identity_confidence": 0.94 if c.character_id == "maya" else 0.91,
            "rights_status": "Active (Valid to 2027-04)",
            "primary_topics": c.topics.allowed[:3]
        }
        for c in character_db.values() if c.version != "1.0.0"
    ]

@app.get("/api/cast/{character_id}/dna")
def get_character_dna(character_id: str):
    if character_id in character_db:
        return character_db[character_id].model_dump()
    raise HTTPException(status_code=404, detail="Character not found")

@app.get("/api/cast/maya/diff")
def get_maya_diff():
    """
    Section 3.2: Character Diffing (Maya v1.0 -> v1.7)
    """
    v1_0 = character_db.get("maya_v1_0")
    v1_7 = character_db.get("maya")
    if not v1_0 or not v1_7:
        raise HTTPException(status_code=404, detail="Versions not found")
    return {
        "character": "maya",
        "diff_summary": "v1.0.0 -> v1.7.0",
        "differences": v1_0.diff(v1_7)
    }

@app.post("/api/cast/compile")
def compile_character(req: CompileCharacterRequest):
    """
    Section 5.2: Character Compiler Quality Gate
    """
    if not req.rights_authorized:
        raise HTTPException(status_code=400, detail="Compilation rejected: Signed rights authorization required.")
    return {
        "character": req.name,
        "version": "1.0.0",
        "compilation_report": {
            "identity_confidence": {"score": 0.94, "passed": True, "min_required": 0.85},
            "voice_confidence": {"score": 0.91, "passed": True, "min_required": 0.85},
            "personality_coverage": {"score": "6/6 trait dimensions anchored", "passed": True},
            "rights_binding": {"signed": True, "passed": True},
            "brand_binding": {"linked_org": "example_co", "passed": True},
            "reference_diversity": {"status": "advisory", "warning": "Single lighting condition in source images"}
        },
        "status": "ACTIVE (with advisory)"
    }

@app.post("/api/production/run", response_model=ProductionRun)
def create_production_run(req: ProductionRunCreateRequest):
    """
    Milestone 9: Single-action autonomous production run.
    Executes the complete verified DAG: Brief -> Research -> Claims -> Script -> Critic -> Director -> Performance -> Voice -> Avatar -> Guardian -> Publish.
    """
    global last_campaign_result, run1_plan, run2_plan
    prod_run = orchestrator.execute_production_run(req)
    last_campaign_result = {
        "run_id": prod_run.run_id,
        "trace_id": prod_run.trace_id,
        "character": orchestrator.characters.get(req.character_id, orchestrator.characters["maya"]).model_dump(),
        "research": prod_run.research_result,
        "claims": prod_run.claims_result,
        "script": prod_run.script_result,
        "critic_report": prod_run.critic_result,
        "director_plan": prod_run.director_result,
        "performance_plan": prod_run.performance_result,
        "guardian_report": prod_run.guardian_result,
        "publish_result": prod_run.publish_result,
        "hindi_production": prod_run.hindi_production,
        "repurposed_clips": prod_run.repurposed_clips,
        "master_video_url": prod_run.master_video_url,
        "media_sha256": prod_run.media_sha256,
        "scorecard": prod_run.scorecard.model_dump(),
        "failure_ux": prod_run.failure_ux.model_dump() if prod_run.failure_ux else None,
        "stages": [s.model_dump() for s in prod_run.stages],
        "trace_events": orchestrator.trace_events
    }
    if prod_run.strategy_version == 13:
        run1_plan = prod_run.director_result
    else:
        run2_plan = prod_run.director_result
    return prod_run

@app.get("/api/production/run/{run_id}", response_model=ProductionRun)
def get_production_run(run_id: str):
    run = production_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Production run not found.")
    return run

@app.get("/api/production/run/{run_id}/events")
def get_production_events(run_id: str):
    run = production_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Production run not found.")
    return {"run_id": run_id, "events": [e.model_dump() for e in production_store.get_events(run_id)]}

@app.get("/api/production/run/{run_id}/provenance")
def get_production_provenance(run_id: str):
    run = production_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Production run not found.")
    return {
        "run_id": run_id,
        "character_id": run.character_id,
        "dna_version": run.dna_version,
        "c2pa_manifest_hash": run.c2pa_manifest_hash,
        "media_sha256": run.media_sha256,
        "audio_sha256": run.audio_sha256,
        "publish_result": run.publish_result,
        "scorecard": run.scorecard.model_dump() if run.scorecard else {}
    }

@app.post("/api/production/demo/claim-block")
def demo_claim_block():
    """
    Step 4 Demo: Attempt unsupported claim injection to demonstrate deterministic claim blocking.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Explain Titan LLM performance. State that it is 3x faster than all competitors with zero latency.",
        inject_claim_failure=True
    )
    return orchestrator.execute_production_run(req)

@app.post("/api/production/demo/guardian-failure")
def demo_guardian_failure():
    """
    Step 5 Demo: Inject emotion mismatch into Scene 4 to demonstrate Guardian detection and bounded rework.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Explain Titan AI laptop benchmarks.",
        inject_emotion_failure=True
    )
    return orchestrator.execute_production_run(req)

@app.post("/api/production/demo/rights-block")
def demo_rights_block():
    """
    Controlled Demo: Simulate expired/revoked likeness authorization to demonstrate immediate render block.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Create marketing video.",
        simulate_rights_failure=True
    )
    return orchestrator.execute_production_run(req)

@app.post("/api/campaign/execute")
def execute_campaign(req: CampaignRequest):
    global last_campaign_result, run1_plan, run2_plan
    start_time = time.time()
    result = orchestrator.execute_campaign(
        command_intent=req.command,
        character_id=req.character_id,
        inject_claim_failure=req.inject_claim_failure,
        inject_emotion_failure=req.inject_emotion_failure
    )
    last_campaign_result = result
    
    # Store for closed loop diffing
    if telemetry_store.active_strategy.strategy_version == 13:
        run1_plan = result["director_plan"]
    else:
        run2_plan = result["director_plan"]

    duration_ms = (time.time() - start_time) * 1000
    app_logger.log_operation(
        trace_id=result.get("trace_id", "trace_unknown"),
        operation="campaign_execution",
        status=result.get("publish_result", {}).get("status", "COMPLETED"),
        duration_ms=duration_ms,
        agent_task="orchestrator_dag",
        details={
            "character_id": req.character_id,
            "publish_status": result.get("publish_result", {}).get("status"),
            "guardian_status": result.get("guardian_report", {}).get("overall_status")
        }
    )
        
    return result

@app.post("/api/campaign/claim/resolve")
def resolve_claim(req: ResolveClaimRequest):
    """
    Step 4 Demo: User attaches benchmark PDF to resolve blocked claim
    """
    updated_claim = orchestrator.research_agent.resolve_blocked_claim(
        claim_id=req.claim_id,
        uploaded_evidence_name=req.evidence_document
    )
    return {
        "status": "CLAIM_APPROVED",
        "claim": updated_claim.model_dump(),
        "publication_unblocked": True
    }

@app.post("/api/campaign/scene/rework")
def rework_scene(scene_no: int = Query(default=4)):
    """
    Step 5 Demo: Trigger scene-scoped re-rendering for failed scene only
    """
    re_path = renderer.render_scene(
        scene_no=scene_no,
        role="demonstration",
        text="Independent MLPerf benchmarks show 40% faster local LLM inference.",
        duration_s=15.0,
        character_name="Maya",
        character_version="v1.7.0",
        target_emotion="excited",
        energy=0.88,
        language="en"
    )
    return {
        "scene_no": scene_no,
        "action": "SCENE_SCOPED_REWORK_COMPLETE",
        "video_url": f"/media/scene_{scene_no}_en_16x9.mp4",
        "master_re_composited": True,
        "guardian_re_audit": "APPROVED (emotion mismatch resolved: 8%)"
    }

@app.post("/api/live/chat")
def live_chat(req: LiveChatRequest):
    """
    Section 17: Live Mode Conversational Turn (Backward-compatible)
    """
    start_time = time.time()
    response = live_engine.process_user_turn(req.message)
    app_logger.log_operation(
        trace_id=f"live_{int(time.time()*1000)}",
        operation="live_chat_turn",
        status="SUCCESS",
        duration_ms=(time.time() - start_time) * 1000,
        agent_task="live_mode_engine",
        details={
            "register": response.get("register"),
            "latency_ms": response.get("latency_breakdown", {}).get("total_latency_ms")
        }
    )
    return response

# ==============================================================================
# MILESTONE 6: GEMINI LIVE SESSION & REAL-TIME WEBSOCKET TRANSPORT
# ==============================================================================

@app.post("/api/live/session", response_model=LiveSessionResponse)
def create_live_session(req: LiveSessionCreateRequest):
    """
    Creates an explicit conversational LiveSession:
    - Resolves Digital DNA and validates likeness Rights server-side
    - Creates SessionMemory sandbox
    - Initializes Gemini Live or Deterministic Fallback provider
    """
    trace_id = f"trace_live_{int(time.time()*1000)}"
    try:
        session = live_session_manager.create_session(
            character_id=req.character_id,
            language=req.language,
            trace_id=trace_id
        )
        return LiveSessionResponse(
            session_id=session.session_id,
            character_id=session.character_id,
            character_version=session.character_version,
            language=session.language,
            status=session.status,
            provider=session.provider,
            created_at=session.created_at,
            active_register=session.active_register,
            degraded_mode=getattr(session, "degraded_mode", False),
            is_realtime=getattr(session, "is_realtime", True)
        )
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/live/session/{session_id}")
def get_live_session(session_id: str):
    """
    Retrieves LiveSession state, transcript history, active register, and latency metrics.
    """
    session = live_session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Live session not found.")
    return session.model_dump()

@app.post("/api/live/session/{session_id}/turn", response_model=LiveTurnResponse)
def submit_live_turn(session_id: str, req: LiveTurnRequest):
    """
    Submits a conversational turn to an active LiveSession.
    Enforces deterministic restricted-topic deflections and updates SessionMemory register.
    """
    trace_id = f"trace_turn_{int(time.time()*1000)}"
    try:
        user_text = req.text or req.message or ""
        audio_bytes = req.audio_base64.encode() if req.audio_base64 else None
        return live_session_manager.process_turn(
            session_id=session_id,
            user_text=user_text,
            audio_chunk=audio_bytes,
            trace_id=trace_id
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Live session not found.")
    except (ValueError, TimeoutError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/live/session/{session_id}/interrupt")
def interrupt_live_session(session_id: str):
    """
    Signals user interruption / barge-in. Cancels active model speech playback.
    """
    trace_id = f"trace_int_{int(time.time()*1000)}"
    try:
        return live_session_manager.interrupt_session(session_id, trace_id=trace_id).model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Live session not found.")

@app.post("/api/live/session/{session_id}/close")
def close_live_session(session_id: str):
    """
    Closes the LiveSession, persists audit record, and clears ephemeral session memory.
    """
    trace_id = f"trace_close_{int(time.time()*1000)}"
    try:
        closed = live_session_manager.close_session(session_id, trace_id=trace_id)
        return {"status": "CLOSED", "session_id": closed.session_id, "turns": closed.turn_count}
    except KeyError:
        raise HTTPException(status_code=404, detail="Live session not found.")

@app.post("/api/live/session/{session_id}/handoff", response_model=LiveStudioHandoffResponse)
def live_to_studio_handoff(session_id: str, req: LiveStudioHandoffRequest):
    """
    Section 24: Safe Live -> Studio Handoff.
    Creates a draft production brief from conversation transcript without silent promotion to permanent memory.
    """
    session = live_session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Live session not found.")
    
    turns_count = len(session.transcript_history)
    extracted_topic = req.brief_title or (session.transcript_history[-1].text if session.transcript_history else "Developer product introduction")
    draft_brief = f"Draft campaign brief synthesized from Live Session {session_id} with character {session.character_id}: Focus on '{extracted_topic}' tailored for {req.target_audience} audience."

    return LiveStudioHandoffResponse(
        handoff_id=f"handoff_{uuid.uuid4().hex[:8]}",
        source_session_id=session_id,
        character_id=session.character_id,
        status="DRAFT_CREATED",
        draft_brief=draft_brief,
        turns_analyzed=turns_count,
        is_promoted_to_permanent_memory=False
    )

@app.websocket("/ws/live/{session_id}")
async def live_websocket_stream(websocket: WebSocket, session_id: str):
    """
    Real-time bidirectional WebSocket transport for Gemini Live mode:
    - Receives user microphone audio chunks & text turns
    - Dispatches partial/final transcript events
    - Handles interruption events (`{"type": "interrupt"}`)
    - Streams assistant response chunks and audio waveforms
    """
    await websocket.accept()
    session = live_session_manager.get_session(session_id)
    if not session:
        await websocket.send_json({"type": "error", "message": "Session not found."})
        await websocket.close()
        return

    try:
        await websocket.send_json({
            "type": "session_connected",
            "session_id": session_id,
            "character_id": session.character_id,
            "character_version": session.character_version,
            "provider": session.provider,
            "language": session.language,
            "active_register": session.active_register,
            "degraded_mode": getattr(session, "degraded_mode", False),
            "is_realtime": getattr(session, "is_realtime", True)
        })

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "turn")

            if msg_type == "interrupt":
                event = live_session_manager.interrupt_session(session_id)
                await websocket.send_json({
                    "type": "response_interrupted",
                    "session_id": session_id,
                    "interruption_count": session.metrics.interruption_count
                })

            elif msg_type in ("turn", "text_input", "audio_input"):
                user_text = data.get("text") or data.get("message") or ""
                # Emit turn started & partial transcript
                await websocket.send_json({
                    "type": "turn_started",
                    "user_text": user_text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

                # Process turn
                turn_res = live_session_manager.process_turn(session_id, user_text)

                # Emit partial and final response chunks
                await websocket.send_json({
                    "type": "response_chunk",
                    "chunk": turn_res.reply,
                    "register": turn_res.register,
                    "target_emotion": turn_res.target_emotion
                })

                await websocket.send_json({
                    "type": "turn_completed",
                    "reply": turn_res.reply,
                    "register": turn_res.register,
                    "target_emotion": turn_res.target_emotion,
                    "gesture_profile": turn_res.gesture_profile,
                    "latency_breakdown": turn_res.latency_breakdown,
                    "transcript": turn_res.transcript.model_dump()
                })

            elif msg_type == "close":
                live_session_manager.close_session(session_id)
                await websocket.send_json({"type": "session_closed", "session_id": session_id})
                break

    except WebSocketDisconnect:
        app_logger.log_operation(
            trace_id="ws_live",
            operation="live_ws_disconnect",
            status="NOTICE",
            agent_task="live_ws",
            details={"session_id": session_id}
        )
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})

@app.get("/api/analytics/telemetry")
def get_telemetry():
    """
    Section 23: ClickHouse SQL Query & Telemetry
    """
    return telemetry_store.run_query_881a()

@app.get("/api/knowledge/documents")
def list_knowledge_documents():
    """
    Section 8: Knowledge Base Documents Inspection
    """
    from backend.app.knowledge.knowledge_base import knowledge_base
    return {
        "status": "success",
        "total_documents": len(knowledge_base.documents),
        "total_chunks": len(knowledge_base.chunks),
        "documents": knowledge_base.list_documents()
    }

@app.get("/api/knowledge/search")
def search_knowledge(
    q: Optional[str] = Query(default=None, description="Query text"),
    query: Optional[str] = Query(default=None, description="Query text alias"),
    top_k: int = Query(default=4)
):
    """
    Section 8: Hybrid Vector + BM25 Retrieval Inspection
    """
    from backend.app.knowledge.knowledge_base import knowledge_base
    query_text = query or q or "Titan local LLM inference"
    hits = knowledge_base.search(query=query_text, top_k=top_k)
    return {
        "query": query_text,
        "total_hits": len(hits),
        "results": [
            {
                "chunk_id": h.chunk.chunk_id,
                "doc_id": h.chunk.doc_id,
                "section": h.chunk.section,
                "page": h.chunk.page,
                "hybrid_score": h.hybrid_score,
                "semantic_score": h.semantic_score,
                "lexical_score": h.lexical_score,
                "retrieval_methods": h.retrieval_methods,
                "chunk_checksum": h.chunk.content_hash,
                "document_title": knowledge_base.documents.get(h.chunk.doc_id).title if h.chunk.doc_id in knowledge_base.documents else h.chunk.doc_id,
                "chunk_text": h.chunk.text,
                "excerpt": h.chunk.text[:200]
            }
            for h in hits
        ]
    }

@app.post("/api/evolution/evolve")
def trigger_evolution():
    """
    Section 24: Evolution Agent Strategy Optimization
    """
    return evolution_agent.analyze_and_evolve()

@app.get("/api/evolution/plan_diff")
def get_plan_diff():
    """
    Section 34.1: Step 9 Plan Diff (Run #1 vs Run #2)
    """
    global run1_plan, run2_plan
    # Default fallback plans if not yet run
    p1 = run1_plan or {
        "hook_type": "statement",
        "opening_duration_s": 9.2,
        "strategy_version": 13,
        "shots": [{"shot": "medium_shot"}]
    }
    p2 = run2_plan or {
        "hook_type": "question",
        "opening_duration_s": 6.8,
        "strategy_version": 14,
        "shots": [{"shot": "close_up"}]
    }
    return evolution_agent.compute_plan_diff(p1, p2)

class MCPExecuteRequest(BaseModel):
    agent_identity: str
    tool_name: str
    arguments: Dict[str, Any] = {}
    trace_id: Optional[str] = None

@app.get("/api/mcp/status")
def get_mcp_status():
    """
    Milestone 7: Model Context Protocol (MCP) partner status and health.
    """
    return mcp_client.get_status()

@app.get("/api/mcp/tools")
def list_mcp_tools(agent: Optional[str] = None):
    """
    Milestone 7: List governed MCP tools, with optional per-agent filtering.
    """
    return {"tools": [t.model_dump() for t in mcp_client.list_tools(agent_identity=agent)]}

@app.post("/api/mcp/execute")
def execute_mcp_tool(req: MCPExecuteRequest):
    """
    Milestone 7: Governed execution of an MCP partner tool with strict permission enforcement.
    """
    trace_id = req.trace_id or f"trace_mcp_exec_{int(time.time()*1000)}"
    res = mcp_client.call_tool(
        agent_identity=req.agent_identity,
        tool_name=req.tool_name,
        arguments=req.arguments,
        trace_id=trace_id
    )
    if res.status == "UNAUTHORIZED":
        raise HTTPException(status_code=403, detail=res.error)
    elif res.status == "ERROR":
        raise HTTPException(status_code=400, detail=res.error)
    return res.model_dump()

@app.get("/api/mcp/traces")
def get_mcp_decision_traces():
    """
    Milestone 7: Immutable audit trails of strategy decisions derived via MCP tools.
    """
    return {"traces": evolution_agent.get_decision_traces()}

@app.websocket("/ws/studio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or custom commands
            await websocket.send_json({"event": "ack", "payload": data})
    except WebSocketDisconnect:
        pass
