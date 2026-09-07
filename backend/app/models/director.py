from typing import List, Optional, Literal, Tuple
from pydantic import BaseModel, Field

class CutawaySpec(BaseModel):
    cutaway_type: str
    timing_s: Tuple[float, float]
    description: Optional[str] = None

class SceneShot(BaseModel):
    scene_no: int
    role: str
    duration_s: float
    shot: Literal["close_up", "medium_close_up", "medium_shot", "wide"] = "medium_close_up"
    camera_move: Literal["static", "slow_push_in", "pan_right", "orbit_subtle"] = "static"
    cutaway: Optional[CutawaySpec] = None
    b_roll_ref: Optional[str] = None
    target_emotion: str
    emotional_intensity: float = Field(ge=0.0, le=1.0)
    hook_type: Optional[Literal["question", "statement", "statistic", "challenge"]] = None
    visual_prompt: str = ""

class DirectorPlan(BaseModel):
    plan_id: str
    campaign_name: str
    target_audience: str
    duration_target_s: float
    languages: List[str] = Field(default_factory=lambda: ["en", "hi"])
    tone: str
    strategy_version: int = 13
    strategy_citation: Optional[str] = None
    hook_type: Literal["question", "statement", "statistic", "challenge"] = "statement"
    opening_duration_s: float = 9.2
    shots: List[SceneShot] = Field(default_factory=list)

DirectorShot = SceneShot
