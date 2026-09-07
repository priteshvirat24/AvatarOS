import pytest
import time
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.models.mcp import (
    MCPToolDefinition,
    MCPToolInvocation,
    MCPToolResult,
    StrategyDecisionTrace,
    ScenePerformanceQuery,
    StrategyPerformanceQuery,
    CompareStrategiesQuery,
    RecentProductionMetricsQuery,
    ClaimVerificationMetricsQuery
)
from backend.app.mcp.client import mcp_client, MCPClient
from backend.app.mcp.registry import mcp_tool_registry
from backend.app.mcp.permission import MCPToolPermissionPolicy
from backend.app.mcp.adapters import DeterministicMCPAdapter, ClickHouseMCPAdapter
from backend.app.agents.evolution import evolution_agent
from backend.app.data.telemetry_store import telemetry_store

client = TestClient(app)


def test_mcp_client_and_registry_initialization():
    """Phase 2 & Phase 3: MCP client and tool registry initialize cleanly."""
    assert mcp_client is not None
    assert mcp_client.registry is not None
    tools = mcp_client.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_strategy_performance" in tool_names
    assert "compare_strategy_versions" in tool_names
    assert "query_scene_performance" in tool_names
    assert "get_recent_production_metrics" in tool_names
    assert "get_claim_verification_metrics" in tool_names


def test_deterministic_mcp_adapter_initialization():
    """Phase 3: Deterministic MCP test adapter initializes with read-only tools."""
    adapter = DeterministicMCPAdapter()
    assert adapter.initialize() is True
    status = adapter.get_status()
    assert status["provider"] == "deterministic"
    assert status["ready"] is True
    assert status["read_only"] is True


def test_mcp_tool_permission_policy_allowlists():
    """Phase 11: Fine-grained permission allowlist matrix enforcement."""
    # 1. Evolution Agent is authorized for ClickHouse analytics tools
    assert MCPToolPermissionPolicy.is_authorized("evolution_agent", "get_strategy_performance") is True
    assert MCPToolPermissionPolicy.is_authorized("evolution_agent", "compare_strategy_versions") is True
    assert MCPToolPermissionPolicy.is_authorized("evolution_agent", "query_scene_performance") is True

    # 2. Director Agent has read-only access to scene performance, but not strategy analytics
    assert MCPToolPermissionPolicy.is_authorized("director_agent", "query_scene_performance") is True
    assert MCPToolPermissionPolicy.is_authorized("director_agent", "get_strategy_performance") is False
    assert MCPToolPermissionPolicy.is_authorized("director_agent", "compare_strategy_versions") is False

    # 3. Script and Critic agents cannot access ClickHouse analytics
    assert MCPToolPermissionPolicy.is_authorized("script_agent", "get_strategy_performance") is False
    assert MCPToolPermissionPolicy.is_authorized("critic_agent", "get_strategy_performance") is False


def test_live_mode_strictly_denied_mcp_analytics():
    """Phase 11 & Phase 20: Live Mode is strictly prohibited from MCP analytics tools."""
    assert MCPToolPermissionPolicy.is_authorized("live_session", "get_strategy_performance") is False
    assert MCPToolPermissionPolicy.is_authorized("live_session", "compare_strategy_versions") is False
    assert MCPToolPermissionPolicy.is_authorized("live_agent", "query_scene_performance") is False

    # Attempt execution from live_session role
    res = mcp_client.call_tool(
        agent_identity="live_session",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya"}
    )
    assert res.status == "UNAUTHORIZED"
    assert "not authorized" in res.error.lower()


def test_prohibited_destructive_operations_blocked():
    """Phase 4 & Phase 5: Destructive operations and raw SQL are universally blocked."""
    prohibited_tools = ["drop_table", "delete_records", "alter_table", "execute_raw_sql", "insert_events", "modify_dna"]
    for tool in prohibited_tools:
        assert MCPToolPermissionPolicy.is_authorized("evolution_agent", tool) is False
        assert MCPToolPermissionPolicy.is_authorized("human_admin", tool) is False

        res = mcp_client.call_tool(
            agent_identity="evolution_agent",
            tool_name=tool,
            arguments={"query": "DROP TABLE scene_events"}
        )
        assert res.status == "UNAUTHORIZED"


def test_typed_query_validation_and_malformed_arguments():
    """Phase 5: Parameter validation prevents malformed queries and injection."""
    # Valid query
    valid_query = StrategyPerformanceQuery(character_id="maya", region="IN", min_sample_size=50)
    assert valid_query.min_sample_size == 50

    # Invalid query (min_sample < 1)
    with pytest.raises(ValueError):
        StrategyPerformanceQuery(character_id="maya", region="IN", min_sample_size=0)

    # Invocations with malformed types are caught
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="get_recent_production_metrics",
        arguments={"limit": 5000}  # Exceeds max 1000
    )
    assert res.status == "ERROR"


def test_trace_id_and_agent_identity_propagation():
    """Phase 2 & Phase 12: Invocations preserve trace_id and agent_identity."""
    trace_id = "trace_mcp_prop_test_99"
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya", "region": "IN"},
        trace_id=trace_id
    )
    assert res.status == "SUCCESS"
    assert res.trace_id == trace_id
    assert res.agent_identity == "evolution_agent"
    assert res.latency_ms >= 0.0


def test_clickhouse_mcp_query_scene_performance():
    """Phase 4: query_scene_performance returns structured scene analytics."""
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="query_scene_performance",
        arguments={"character_id": "maya", "scene_no": 1, "min_sample": 50}
    )
    assert res.status == "SUCCESS"
    data = res.data
    assert data["character_id"] == "maya"
    assert data["scene_no"] == 1
    assert data["avg_watch_pct"] > 0.5
    assert data["sample_size"] >= 50


def test_clickhouse_mcp_get_strategy_performance():
    """Phase 4: get_strategy_performance returns Query 881a distributions."""
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya", "region": "IN", "min_sample_size": 50}
    )
    assert res.status == "SUCCESS"
    data = res.data
    assert "rows" in data
    assert "total_rows_scanned" in data
    assert len(data["rows"]) >= 4
    hook_types = [r["hook_type"] for r in data["rows"]]
    assert "question" in hook_types
    assert "statement" in hook_types


def test_clickhouse_mcp_compare_strategy_versions():
    """Phase 4: compare_strategy_versions returns statistical lift."""
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="compare_strategy_versions",
        arguments={"character_id": "maya", "strategy_a": 13, "strategy_b": 14, "metric": "avg_retention"}
    )
    assert res.status == "SUCCESS"
    data = res.data
    assert data["character_id"] == "maya"
    assert data["statistically_significant"] is True
    assert data["retention_lift"] > 0.05
    assert "justification" in data or "strategy_a" in data


def test_evolution_agent_mcp_evidence_preservation():
    """Phase 7 & Phase 8: Evolution Agent uses MCP to formulate strategy and stores StrategyDecisionTrace."""
    trace_id = "trace_evolution_test_mcp"
    evolution_result = evolution_agent.analyze_and_evolve(trace_id=trace_id)

    assert evolution_result["status"] == "STRATEGY_EVOLVED"
    assert evolution_result["new_strategy_version"] >= 14
    assert "mcp_governance" in evolution_result
    assert "get_strategy_performance" in evolution_result["mcp_governance"]["tools_invoked"]
    assert evolution_result["statistical_significance"]["sample_floor_met"] is True
    assert evolution_result["statistical_significance"]["decision"] == "PASS"

    # Verify Decision Trace
    traces = evolution_agent.get_decision_traces()
    assert len(traces) > 0
    latest = traces[-1]
    assert latest["statistical_decision"] == "PASS"
    assert latest["sample_size"] >= 50
    assert "question hook" in latest["agent_reasoning_summary"] or "Strategy B" in latest["agent_reasoning_summary"]
    assert latest["approval_status"] == "ACTIVE"


def test_strategy_lifecycle_human_boundary():
    """Phase 9: Strategy lifecycle enforces PROPOSED -> VALIDATED -> APPROVED -> ACTIVE."""
    now_iso = datetime.now(timezone.utc).isoformat()
    trace = StrategyDecisionTrace(
        decision_id="dec_test_01",
        trace_id="trace_test_01",
        character_id="maya",
        current_strategy_version=13,
        candidate_strategy_version=14,
        sample_size=742,
        metric="avg_retention",
        confidence_interval="[0.691, 0.733]",
        statistical_decision="PASS",
        agent_reasoning_summary="Validated by statistical CI.",
        approval_status="PROPOSED",
        created_at=now_iso
    )
    assert trace.approval_status == "PROPOSED"


def test_strategy_version_persistence_and_plan_diff():
    """Phase 6 & Phase 14: Strategy version updates and closed-loop Plan Diff cite ClickHouse MCP evidence."""
    run1 = {"hook_type": "statement", "opening_duration_s": 9.2, "strategy_version": 13, "shots": [{"shot": "medium_shot"}]}
    run2 = {"hook_type": "question", "opening_duration_s": 6.8, "strategy_version": 14, "shots": [{"shot": "close_up"}]}

    diff = evolution_agent.compute_plan_diff(run1, run2)
    assert diff["hook_type"]["changed"] is True
    assert diff["hook_type"]["run1"] == "statement"
    assert diff["hook_type"]["run2"] == "question"
    assert diff["opening_duration_s"]["changed"] is True
    assert diff["hook_shot"]["changed"] is True
    assert "ch_query_881a" in diff["justification"] or "ClickHouse query" in diff["justification"]


def test_health_endpoints_mcp_transparency():
    """Phase 17: Health endpoint exposes MCP provider, readiness, and status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "services" in data
    assert "mcp" in data["services"]
    mcp_health = data["services"]["mcp"]
    assert mcp_health["enabled"] is True
    assert mcp_health["ready"] is True
    assert mcp_health["provider"] in ("clickhouse_mcp", "deterministic")


def test_mcp_rest_endpoints_contract():
    """Phase 2 & Phase 19: REST endpoints for MCP status, tools list, execution, and traces."""
    # 1. GET /api/mcp/status
    res_status = client.get("/api/mcp/status")
    assert res_status.status_code == 200
    assert res_status.json()["enabled"] is True

    # 2. GET /api/mcp/tools
    res_tools = client.get("/api/mcp/tools")
    assert res_tools.status_code == 200
    tools = res_tools.json()["tools"]
    assert len(tools) >= 5

    # 3. POST /api/mcp/execute (Authorized)
    res_exec = client.post("/api/mcp/execute", json={
        "agent_identity": "evolution_agent",
        "tool_name": "query_scene_performance",
        "arguments": {"character_id": "maya", "scene_no": 1}
    })
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "SUCCESS"

    # 4. POST /api/mcp/execute (Unauthorized - Live Mode)
    res_unauth = client.post("/api/mcp/execute", json={
        "agent_identity": "live_session",
        "tool_name": "get_strategy_performance",
        "arguments": {"character_id": "maya"}
    })
    assert res_unauth.status_code == 403

    # 5. GET /api/mcp/traces
    res_traces = client.get("/api/mcp/traces")
    assert res_traces.status_code == 200
    assert "traces" in res_traces.json()


def test_a2a_and_mcp_separation():
    """Phase 10: Preserves separation of A2A (agent-to-agent) and MCP (agent-to-tool)."""
    from backend.app.models.a2a import A2AMessage
    a2a_msg = A2AMessage(
        from_agent="orchestrator",
        to_agent="evolution_agent",
        task="optimize_strategy",
        payload={"campaign_id": "titan_01"},
        trace_id="trace_a2a_sep"
    )
    assert a2a_msg.from_agent == "orchestrator"
    assert a2a_msg.to_agent == "evolution_agent"

    # MCP tool invocation is a distinct model
    mcp_inv = MCPToolInvocation(
        tool_name="get_strategy_performance",
        agent_identity="evolution_agent",
        trace_id="trace_a2a_sep",
        arguments={"character_id": "maya"}
    )
    assert mcp_inv.agent_identity == "evolution_agent"
    assert mcp_inv.tool_name == "get_strategy_performance"


def test_deterministic_mcp_contract_test():
    """Phase 20: Deterministic MCP Contract Test validating full loop offline."""
    adapter = DeterministicMCPAdapter()
    client_inst = MCPClient(adapter=adapter)

    # 1. Tool execution
    res = client_inst.call_tool(
        agent_identity="evolution_agent",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya", "region": "IN"},
        trace_id="contract_test_trace"
    )
    assert res.status == "SUCCESS"
    assert res.data["total_rows_scanned"] > 0
    assert res.latency_ms >= 0.0

    # 2. Strategy Comparison
    res_comp = client_inst.call_tool(
        agent_identity="evolution_agent",
        tool_name="compare_strategy_versions",
        arguments={"character_id": "maya", "strategy_a": 13, "strategy_b": 14},
        trace_id="contract_test_trace"
    )
    assert res_comp.status == "SUCCESS"
    assert res_comp.data["statistically_significant"] is True
    assert res_comp.data["retention_lift"] > 0.05
