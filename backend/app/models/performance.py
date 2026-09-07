from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class PauseSpec(BaseModel):
    after_word_idx: int
    duration_ms: int

class GestureSpec(BaseModel):
    gesture_type: str
    trigger_word_idx: int
    intensity: float = 0.75

class FacialKeyframe(BaseModel):
    event: str
    trigger: str
    target_expression: str = "smile"
    intensity: float = 0.8

class FacialExpressionPlan(BaseModel):
    baseline_expression: str = "neutral"
    smile_intensity: float = Field(default=0.6, ge=0.0, le=1.0)
    eyebrow_elevation: float = Field(default=0.4, ge=0.0, le=1.0)
    eye_aperture: float = Field(default=0.85, ge=0.0, le=1.0)
    keyframes: List[FacialKeyframe] = Field(default_factory=list)

class GazePlan(BaseModel):
    target: Literal["camera", "screen", "presenter_left", "presenter_right", "audience"] = "camera"
    gaze_duration_ms: int = 4000
    saccades_enabled: bool = True
    direct_contact_ratio: float = Field(default=0.85, ge=0.0, le=1.0)

class HeadMotionPlan(BaseModel):
    nod_frequency: float = Field(default=0.2, ge=0.0, le=1.0)
    tilt_degrees: float = Field(default=4.0, ge=-30.0, le=30.0)
    idle_sway_amplitude: float = Field(default=0.1, ge=0.0, le=1.0)
    speaking_cadence: str = "rhythmic_natural"

class CameraControl(BaseModel):
    move: str = "slow_push_in"
    start_fov: float = 42.0
    end_fov: float = 36.0

class CameraShotPlan(BaseModel):
    shot_type: Literal[
        "close_up",
        "medium_close_up",
        "medium_shot",
        "medium_wide",
        "talking_head",
        "presentation_framing"
    ] = "medium_close_up"
    framing: str = "center_balanced"
    character_screen_position: Literal["center", "left_third", "right_third"] = "center"
    camera_control: CameraControl = Field(default_factory=CameraControl)

class LipSyncPlan(BaseModel):
    max_tolerance_ms: int = 80
    viseme_alignment_rate: float = Field(default=1.0, ge=0.5, le=2.0)
    phoneme_extraction_enabled: bool = True
    enforce_threshold: bool = True

class SceneTiming(BaseModel):
    scene_no: int
    start_s: float = 0.0
    duration_s: float = 12.0

class PerformanceTiming(BaseModel):
    total_duration_s: float = 60.0
    scene_timings: List[SceneTiming] = Field(default_factory=list)

class ScenePerformanceSpec(BaseModel):
    scene_no: int
    target_emotion: str = "confident"
    energy: float = Field(default=0.75, ge=0.0, le=1.0)
    eye_direction: str = "camera"
    speech_rate_multiplier: float = Field(default=1.02, ge=0.5, le=2.0)
    pauses_ms: List[PauseSpec] = Field(default_factory=list)
    gestures: List[GestureSpec] = Field(default_factory=list)
    facial_keyframes: List[FacialKeyframe] = Field(default_factory=list)
    facial_plan: FacialExpressionPlan = Field(default_factory=FacialExpressionPlan)
    gaze_plan: GazePlan = Field(default_factory=GazePlan)
    head_motion_plan: HeadMotionPlan = Field(default_factory=HeadMotionPlan)
    shot_plan: CameraShotPlan = Field(default_factory=CameraShotPlan)
    lip_sync_plan: LipSyncPlan = Field(default_factory=LipSyncPlan)
    camera: CameraControl = Field(default_factory=lambda: CameraControl(move="slow_push_in"))

class PerformancePlan(BaseModel):
    """
    Production Performance Plan (Milestone 8, Section 12)
    Grounded in Digital DNA and DirectorPlan to drive renderer execution.
    """
    plan_id: str
    character_id: str
    character_version: str
    dna_version: str = "1.7.0"
    voice_model: str = "maya-english-v4"
    language: str = "en"
    emotional_state: str = "confident"
    energy: float = Field(default=0.78, ge=0.0, le=1.0)
    speaking_style: str = "conversational_technical"
    facial_expression_plan: FacialExpressionPlan = Field(default_factory=FacialExpressionPlan)
    gaze_plan: GazePlan = Field(default_factory=GazePlan)
    head_motion_plan: HeadMotionPlan = Field(default_factory=HeadMotionPlan)
    gesture_plan: List[GestureSpec] = Field(default_factory=list)
    camera_plan: CameraControl = Field(default_factory=CameraControl)
    shot_plan: CameraShotPlan = Field(default_factory=CameraShotPlan)
    lip_sync_requirements: LipSyncPlan = Field(default_factory=LipSyncPlan)
    timing: PerformanceTiming = Field(default_factory=PerformanceTiming)
    renderer_requirements: Dict[str, Any] = Field(default_factory=lambda: {
        "resolution": "1280x720",
        "fps": 30,
        "format": "mp4",
        "aspect_ratio": "16:9"
    })
    scenes: List[ScenePerformanceSpec] = Field(default_factory=list)

# Backward-compatible alias for existing imports
ProductionPerformancePlan = PerformancePlan
