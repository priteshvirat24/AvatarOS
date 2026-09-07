from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ScriptLine(BaseModel):
    speaker: str
    text: str
    claim_refs: List[str] = Field(default_factory=list)

class ScriptScene(BaseModel):
    scene_no: int
    role: Literal["hook", "problem", "product", "demonstration", "cta"]
    duration_s: float
    lines: List[ScriptLine] = Field(default_factory=list)

class Script(BaseModel):
    script_id: str
    version: int = 1
    duration_target_s: float = 60.0
    language: str = "en"
    scenes: List[ScriptScene] = Field(default_factory=list)

    @property
    def total_duration(self) -> float:
        return sum(s.duration_s for s in self.scenes)

class CriticIssue(BaseModel):
    issue_id: str
    severity: Literal["BLOCKING", "MAJOR", "MINOR"]
    scene_no: Optional[int] = None
    issue_type: Literal["unsupported_claim", "personality_mismatch", "brand_violation", "pacing", "sentence_length"]
    description: str
    claim_ref: Optional[str] = None

class CriticReport(BaseModel):
    verdict: Literal["approve", "reject"]
    round_number: int
    max_rounds: int = 3
    issues: List[CriticIssue] = Field(default_factory=list)
    blocking_count: int = 0
    feedback_summary: str = ""
