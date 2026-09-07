from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class A2AMessage(BaseModel):
    from_agent: str
    to_agent: str
    task: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    reply_to: Optional[str] = None
    trace_id: str
    deadline_ms: int = 8000
    timestamp: Optional[str] = None
