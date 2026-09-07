from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

class SceneImpressionEvent(BaseModel):
    event: str = "scene_impression"
    avatar_id: str
    character_version: str
    campaign_id: str
    scene_id: str
    language: str
    region: str
    platform: str
    hook_type: str
    opening_duration_s: float
    emotion_target: str
    shot_preference: str = "medium_shot"
    watch_pct: float
    ctr: float
    conversion: bool
    strategy_version: int = 13
    trace_id: Optional[str] = None
    ts: str

class StrategyEvidence(BaseModel):
    sample_size: int
    retention_lift: float
    confidence: str
    source_query_id: str

class ProductionStrategy(BaseModel):
    character_id: str
    strategy_version: int
    segment: dict
    hook_type: str
    opening_duration_s_range: Tuple[float, float]
    shot_preference: str
    energy_bias: float
    evidence: StrategyEvidence
    trace_id: Optional[str] = None
    applied_at: str
