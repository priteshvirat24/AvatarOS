from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

class MediaValidationResult(BaseModel):
    is_valid: bool
    file_path: str
    file_size_bytes: int = 0
    duration_s: float = 0.0
    has_video: bool = False
    has_audio: bool = False
    resolution: Optional[str] = None
    codec: Optional[str] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    fps: float = 30.0
    frame_count: int = 0
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    errors: List[str] = Field(default_factory=list)

class ExtractedFrame(BaseModel):
    timestamp_s: float
    frame_index: int
    image_path: str
    scene_no: Optional[int] = None
    sha256: str = ""

class AudioExtractionResult(BaseModel):
    audio_path: str
    duration_s: float = 0.0
    sample_rate: int = 16000
    channels: int = 1
    sha256: str = ""

class ASRTranscriptSegment(BaseModel):
    start_s: float = 0.0
    end_s: float = 0.0
    text: str
    confidence: float = 1.0

class ASRTranscript(BaseModel):
    transcript_text: str
    language: str = "en"
    confidence: float = 0.95
    word_count: int = 0
    duration_s: float = 0.0
    segments: List[ASRTranscriptSegment] = Field(default_factory=list)

class VisualAuditResult(BaseModel):
    identity_similarity: float = 0.94
    min_frame_similarity: float = 0.88
    detected_emotion: str = "confident"
    emotion_mismatch: float = 0.08
    detected_shot: str = "medium_close_up"
    shot_matched: bool = True
    visual_quality_passed: bool = True
    brand_passed: bool = True
    safety_passed: bool = True
    failure_reasons: List[str] = Field(default_factory=list)

class AudioAuditResult(BaseModel):
    voice_similarity: float = 0.915
    lip_sync_offset_ms: int = 42
    audio_integrity_passed: bool = True
    failure_reasons: List[str] = Field(default_factory=list)

class SceneAuditResult(BaseModel):
    scene_no: int
    identity_similarity: float
    identity_min_frame_similarity: float
    identity_passed: bool
    voice_similarity: float
    voice_passed: bool
    script_adherence_pct: float
    script_passed: bool
    expected_emotion: str
    detected_emotion: str
    emotion_mismatch_score: float
    emotion_passed: bool
    claims_verified_count: int
    claims_blocked_count: int
    claims_passed: bool
    brand_passed: bool
    safety_passed: bool
    lip_sync_offset_ms: int
    lip_sync_passed: bool
    scene_verdict: Literal["PASS", "FAIL"]
    failure_reasons: List[str] = Field(default_factory=list)
    # Media Inspection Extended Fields (Milestone 5, 8)
    media_path: Optional[str] = None
    observed_shot: Optional[str] = None
    expected_shot: Optional[str] = None
    shot_passed: bool = True
    sampled_frame_count: int = 0
    asr_transcript: Optional[str] = None
    claim_drift_detected: bool = False

class GuardianReport(BaseModel):
    audit_id: str
    asset_id: str
    overall_status: Literal["APPROVED", "REWORK", "BLOCKED"]
    mean_identity_similarity: float
    voice_similarity: float
    script_adherence_pct: float
    claims_audit_summary: str
    emotion_audit_summary: str
    failed_scenes: List[int] = Field(default_factory=list)
    scene_audits: List[SceneAuditResult] = Field(default_factory=list)
    timestamp: str
    # Media Artifact Verification Metadata (Milestone 5, 8)
    media_path: Optional[str] = None
    media_sha256: Optional[str] = None
    audio_sha256: Optional[str] = None
    media_duration_s: float = 0.0
    media_validated: bool = True
    media_facts: Optional[Dict[str, Any]] = None
    asr_provider: str = "deterministic"
    guardian_provider: str = "deterministic"
    total_sampled_frames: int = 0
    full_asr_transcript: Optional[str] = None
    claim_drift_detected: bool = False
