from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class C2PAAssertion(BaseModel):
    label: str
    data: dict

class ProvenanceRecord(BaseModel):
    asset_id: str
    character_version: str
    dna_version: str = "1.7.0"
    voice_provider: str = "deterministic"
    voice_model: str
    renderer: str
    renderer_provider: str = "deterministic"
    renderer_model: str = "ffmpeg_identity_lock_v1"
    script_id: str
    evidence_refs: List[str] = Field(default_factory=list)
    director_plan_id: str
    performance_plan_id: Optional[str] = None
    guardian_result: str
    rights_ref: str
    generated_at: str
    media_sha256: str
    audio_sha256: Optional[str] = None
    c2pa_manifest_hash: str
    ai_disclosure_marker: bool = True
    assertions: List[C2PAAssertion] = Field(default_factory=list)

class PublishResult(BaseModel):
    status: Literal["PUBLISHED", "BLOCKED"]
    asset_id: str
    failed_check: Optional[str] = None
    detail: Optional[str] = None
    provenance: Optional[ProvenanceRecord] = None
    distribution_urls: dict = Field(default_factory=dict)
