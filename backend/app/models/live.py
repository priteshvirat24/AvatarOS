from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

class TranscriptTurn(BaseModel):
    turn_id: str
    session_id: str
    speaker: Literal["user", "maya", "system"]
    text: str
    language: str = "en"
    is_partial: bool = False
    final: bool = True
    timestamp: str
    latency_ms: Optional[float] = None
    register: Optional[str] = None

class LiveSessionMetrics(BaseModel):
    time_to_first_response_ms: float = 0.0
    time_to_first_audio_ms: float = 0.0
    turn_total_ms: float = 0.0
    interruption_count: int = 0
    restricted_topic_hits: int = 0
    tool_calls: int = 0
    input_audio_duration_s: float = 0.0
    response_audio_duration_s: float = 0.0

class LiveSession(BaseModel):
    session_id: str
    character_id: str
    character_version: str
    rights_ref: str
    language: str = "en"
    created_at: str
    last_activity_at: str
    status: Literal["INIT", "ACTIVE", "INTERRUPTED", "PROCESSING", "CLOSED", "ERROR"] = "INIT"
    provider: str = "deterministic"
    session_memory_id: str
    trace_id: str
    turn_count: int = 0
    active_register: str = "technical"
    explanation_depth: str = "intermediate"
    audience_model: str = "general_developer"
    metrics: LiveSessionMetrics = Field(default_factory=LiveSessionMetrics)
    transcript_history: List[TranscriptTurn] = Field(default_factory=list)
    dna_snapshot: Dict[str, Any] = Field(default_factory=dict)
    degraded_mode: bool = False
    is_realtime: bool = True

class LiveEvent(BaseModel):
    type: Literal[
        "turn_started",
        "partial_transcript",
        "turn_completed",
        "response_started",
        "response_chunk",
        "response_audio",
        "response_completed",
        "response_interrupted",
        "session_closed",
        "error",
        "deflection"
    ]
    session_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str

class LiveSessionCreateRequest(BaseModel):
    character_id: str = "maya"
    language: str = "en"
    enable_audio: Optional[bool] = False

class LiveSessionResponse(BaseModel):
    session_id: str
    character_id: str
    character_version: str
    language: str
    status: str
    provider: str
    created_at: str
    active_register: str
    degraded_mode: bool = False
    is_realtime: bool = True

class LiveTurnRequest(BaseModel):
    message: Optional[str] = None
    text: Optional[str] = None
    audio_base64: Optional[str] = None
    language: Optional[str] = None

class LiveTurnResponse(BaseModel):
    session_id: str
    reply: str
    register: str
    target_emotion: str
    gesture_profile: str
    dna_locked: bool = True
    character_version: str
    provider: Optional[str] = None
    degraded_mode: Optional[bool] = False
    latency_breakdown: Dict[str, Any] = Field(default_factory=dict)
    transcript: TranscriptTurn

