from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class MCPToolDefinition(BaseModel):
    """
    Metadata definition for a governed partner tool exposed via MCP.
    """
    name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    partner: str = "clickhouse"
    category: str = "analytics"
    read_only: bool = True

class MCPToolInvocation(BaseModel):
    """
    Structured record of an agent's request to execute an MCP tool.
    """
    tool_name: str
    agent_identity: str
    trace_id: str
    session_id: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MCPToolResult(BaseModel):
    """
    Governed result returned from the MCP layer to the agent.
    """
    tool_name: str
    agent_identity: str
    trace_id: str
    status: Literal["SUCCESS", "ERROR", "UNAUTHORIZED", "TIMEOUT"]
    data: Optional[Any] = None
    latency_ms: float = 0.0
    error: Optional[str] = None
    server_identity: str = "clickhouse_mcp"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ---------------------------------------------------------------------------
# TYPED MCP QUERY SCHEMAS (NO ARBITRARY SQL)
# ---------------------------------------------------------------------------

class ScenePerformanceQuery(BaseModel):
    character_id: str = "maya"
    scene_no: Optional[int] = None
    min_sample: int = Field(default=50, ge=1)

class StrategyPerformanceQuery(BaseModel):
    character_id: str = "maya"
    region: str = "IN"
    min_sample_size: int = Field(default=50, ge=1)
    strategy_version: Optional[int] = None

class CompareStrategiesQuery(BaseModel):
    character_id: str = "maya"
    strategy_a: int = 13
    strategy_b: int = 14
    metric: str = "avg_retention"
    time_window: str = "60d"

class RecentProductionMetricsQuery(BaseModel):
    limit: int = Field(default=50, ge=1, le=1000)
    character_id: str = "maya"

class ClaimVerificationMetricsQuery(BaseModel):
    time_window_days: int = Field(default=30, ge=1, le=365)

# ---------------------------------------------------------------------------
# STRATEGY DECISION TRACE (EVIDENCE PRESERVATION)
# ---------------------------------------------------------------------------

class StrategyDecisionTrace(BaseModel):
    """
    Immutable audit trail recording how the Evolution Agent analyzed ClickHouse telemetry
    via MCP tools and formulated a statistically-grounded strategy proposal.
    """
    decision_id: str
    trace_id: str
    character_id: str
    current_strategy_version: int
    candidate_strategy_version: int
    evidence_queries: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_results: List[Dict[str, Any]] = Field(default_factory=list)
    sample_size: int
    metric: str
    confidence_interval: str
    statistical_decision: Literal["PASS", "FAIL_SAMPLE_SIZE", "FAIL_CONFIDENCE", "FAIL_LIFT"]
    agent_reasoning_summary: str
    approval_status: Literal["PROPOSED", "VALIDATED", "APPROVED", "REJECTED", "ACTIVE"] = "PROPOSED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
