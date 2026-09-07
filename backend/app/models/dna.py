import hashlib
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, model_validator

class IdentitySpec(BaseModel):
    face_embedding_ref: str
    face_embedding_model: str = "arcface-r100-ir"
    similarity_threshold: float = Field(default=0.92, ge=0.0, le=1.0)
    voice_model_id: str
    voice_similarity_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    reference_media: List[str] = Field(default_factory=list)

class PersonalityVector(BaseModel):
    confident: float = Field(ge=0.0, le=1.0, default=0.8)
    witty: float = Field(ge=0.0, le=1.0, default=0.6)
    analytical: float = Field(ge=0.0, le=1.0, default=0.7)
    warmth: float = Field(ge=0.0, le=1.0, default=0.6)
    formality: float = Field(ge=0.0, le=1.0, default=0.4)
    assertiveness: float = Field(ge=0.0, le=1.0, default=0.7)

class SpeechSpec(BaseModel):
    sentence_length: Literal["short", "medium", "long"] = "short"
    pace_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)
    accent: str = "indian_english"
    filler_words: Literal["none", "minimal", "natural"] = "minimal"

class TopicsSpec(BaseModel):
    allowed: List[str] = Field(default_factory=list)
    restricted: List[str] = Field(default_factory=list)
    on_restricted_hit: Literal["deflect_and_log", "terminate_session", "escalate"] = "deflect_and_log"

class GestureProfile(BaseModel):
    expressiveness: float = Field(default=0.7, ge=0.0, le=1.0)
    gesture_library: str = "confident_technical_v2"

class BrandBinding(BaseModel):
    org_id: str = "example_co"
    brand_kit_ref: str = "vault://brand/example_co/v9"
    primary_color: str = "#6366F1"
    font_family: str = "Outfit, sans-serif"

class DigitalDNA(BaseModel):
    character_id: str
    version: str = "1.0.0"
    status: Literal["active", "compiling", "needs_rights_renewal", "archived"] = "active"
    identity: IdentitySpec
    personality_vector: PersonalityVector
    speech: SpeechSpec
    topics: TopicsSpec
    gesture_profile: GestureProfile
    brand: BrandBinding
    rights_ref: str
    parent_version: Optional[str] = None
    changed_fields: List[str] = Field(default_factory=list)
    created_by: str = "character_compiler"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: Optional[str] = None

    def calculate_checksum(self) -> str:
        data = self.model_dump(exclude={"checksum"})
        serialized = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(serialized.encode()).hexdigest()}"

    def seal(self) -> "DigitalDNA":
        self.checksum = self.calculate_checksum()
        return self

    def diff(self, other: "DigitalDNA") -> Dict[str, Dict[str, any]]:
        d1 = self.model_dump()
        d2 = other.model_dump()
        differences = {}
        for key in d1:
            if key in ("checksum", "created_at"):
                continue
            if d1[key] != d2.get(key):
                differences[key] = {"old": d1[key], "new": d2.get(key)}
        return differences

def validate_dna_write_guard(target_dna: DigitalDNA, caller_role: str, changes: Dict[str, any]) -> bool:
    """
    Enforces write permissions as per Section 4.1 & 18.1.
    Any agent output touching identity.*, rights_ref, or topics.restricted
    is rejected unless caller_role == 'human_admin'.
    """
    forbidden_prefixes = ("identity", "rights_ref", "topics.restricted")
    if caller_role == "human_admin":
        return True

    for field in changes.keys():
        for prefix in forbidden_prefixes:
            if field == prefix or field.startswith(f"{prefix}."):
                raise PermissionError(
                    f"Agent role '{caller_role}' is not authorized to modify protected field '{field}'. "
                    "Core character identity and rights require human admin approval."
                )
    return True
