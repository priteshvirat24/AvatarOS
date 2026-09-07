from typing import List, Dict, Optional, Literal, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class AgentExecutionEvent(BaseModel):
    """
    Standardized Observability Contract for Studio Activity Stream (Milestone 9, Section 5)
    """
    event_id: str
    run_id: str
    trace_id: str
    agent_name: str
    stage: str
    status: Literal["RUNNING", "COMPLETED", "FAILED", "BLOCKED", "REVISING", "REWORKING"]
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    input_summary: str = ""
    output_summary: str = ""
    evidence_refs: List[str] = Field(default_factory=list)
    structured_output: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    failure_detail: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProductionScorecard(BaseModel):
    """
    High-Level Compliance & Quality Scorecard across 8 Dimensions (Section 27)
    """
    identity: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    rights: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    evidence: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    performance: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    media: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    safety: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    provenance: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"
    learning: Literal["PASS", "BLOCKED", "PENDING"] = "PENDING"

class FailureUX(BaseModel):
    """
    Structured Failure Explanation (Section 29)
    """
    what_failed: str
    why: str
    what_was_protected: str
    what_happens_next: str

class ProductionRun(BaseModel):
    """
    Unified Autonomous Production Run Representation (Milestone 9, Section 2)
    """
    model_config = {"protected_namespaces": ()}
    run_id: str
    trace_id: str
    character_id: str = "maya"
    dna_version: str = "1.7.0"
    campaign_id: str = "titan_laptop_india_devs"
    input_brief: str
    language: str = "en"
    register: Optional[str] = None
    status: Literal["QUEUED", "RUNNING", "COMPLETED", "BLOCKED", "FAILED"] = "QUEUED"
    current_stage: str = "QUEUED"
    stages: List[AgentExecutionEvent] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    strategy_version: int = 13
    renderer_provider: str = "deterministic"
    voice_provider: str = "deterministic"
    research_result: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    claims_result: Optional[List[Dict[str, Any]]] = None
    script_result: Optional[Dict[str, Any]] = None
    critic_result: Optional[Dict[str, Any]] = None
    director_result: Optional[Dict[str, Any]] = None
    performance_result: Optional[Dict[str, Any]] = None
    master_video_url: Optional[str] = None
    media_sha256: Optional[str] = None
    audio_sha256: Optional[str] = None
    guardian_result: Optional[Dict[str, Any]] = None
    publish_result: Optional[Dict[str, Any]] = None
    provenance_id: Optional[str] = None
    c2pa_manifest_hash: Optional[str] = None
    hindi_production: Optional[Dict[str, Any]] = None
    repurposed_clips: List[Dict[str, Any]] = Field(default_factory=list)
    scorecard: ProductionScorecard = Field(default_factory=ProductionScorecard)
    failure_ux: Optional[FailureUX] = None

class ProductionRunCreateRequest(BaseModel):
    """
    Single-Action Production Request (Section 3)
    """
    model_config = {"protected_namespaces": ()}
    character_id: str = "maya"
    brief: str = "Create a 60-second product launch for Indian developers. Research our documentation first. Do not make unsupported claims. Produce English and Hindi versions."
    campaign_id: str = "titan_laptop_india_devs"
    language: str = "en"
    register: Optional[str] = None
    inject_claim_failure: bool = False
    inject_emotion_failure: bool = False
    simulate_rights_failure: bool = False

class LiveStudioHandoffRequest(BaseModel):
    """
    Safe Live -> Studio Handoff Request (Section 24)
    """
    session_id: str
    brief_title: Optional[str] = None
    target_audience: Optional[str] = "technical"

class LiveStudioHandoffResponse(BaseModel):
    """
    Safe Live -> Studio Draft Brief Response (Section 24)
    """
    handoff_id: str
    source_session_id: str
    character_id: str
    status: Literal["DRAFT_CREATED"] = "DRAFT_CREATED"
    draft_brief: str
    turns_analyzed: int
    is_promoted_to_permanent_memory: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
