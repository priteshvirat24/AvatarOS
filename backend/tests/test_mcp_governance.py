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

def _assert_result_envelope(data):
    """
    Every adapter payload must carry provenance: which query ran, how many rows
    came back, where the answer came from, and whether it is simulated.
    """
    assert "query_id" in data
    assert "sql" in data
    assert "row_count" in data
    assert data["row_count"] >= 0
    assert data["data_source"] in (
        "clickhouse_via_official_mcp_server",
        "deterministic_simulation",
    )
    assert isinstance(data["is_simulated"], bool)
    assert data["no_data"] == (data["row_count"] == 0)
    if not data["is_simulated"]:
        # A real answer must name the MCP server that produced it.
        assert data["executed_via"]["protocol"] == "mcp"
        assert data["executed_via"]["server"].startswith("mcp-clickhouse")
        assert data["executed_via"]["tool"]


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


def test_query_scene_performance_returns_measured_rows():
    """
    Scene analytics come back as real rows, each carrying its own sample size.

    Deliberately asserts shape and internal consistency rather than a specific
    retention figure: pinning an expected number here would re-introduce exactly
    the hardcoded-metric problem this tool was rewritten to remove.
    """
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="query_scene_performance",
        arguments={"character_id": "maya", "min_sample": 50}
    )
    assert res.status == "SUCCESS"
    data = res.data
    assert data["character_id"] == "maya"
    _assert_result_envelope(data)

    for scene in data["scenes"]:
        assert scene["sample_size"] > 0
        assert 0.0 <= scene["avg_watch_pct"] <= 1.0
        # drop-off is the complement of watch percentage, computed by the query
        assert abs((scene["avg_watch_pct"] + scene["dropoff_rate"]) - 1.0) < 0.01


def test_get_strategy_performance_returns_query_881a_distribution():
    """Hook-type distribution arrives with the variance needed for a real CI."""
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya", "region": "IN", "min_sample_size": 50}
    )
    assert res.status == "SUCCESS"
    data = res.data
    _assert_result_envelope(data)
    assert data["query_id"] == "ch_query_881a"

    hook_types = [r["hook_type"] for r in data["rows"]]
    assert "question" in hook_types
    assert "statement" in hook_types

    for row in data["rows"]:
        assert row["n"] >= 50, "HAVING clause must exclude under-sampled arms"
        assert row["meets_sample_floor"] is True
        low, high = row["ci_95"]
        assert low is not None and high is not None
        assert low <= row["avg_retention"] <= high, "mean must sit inside its own CI"

    # The query orders by retention descending; verify the server honoured it.
    retentions = [r["avg_retention"] for r in data["rows"]]
    assert retentions == sorted(retentions, reverse=True)


def test_compare_strategy_versions_reports_an_honest_verdict():
    """
    The comparison returns whatever the data supports - including "not enough
    data". The previous implementation hardcoded `statistically_significant: True`
    regardless of input; this test exists to make that regression impossible.
    """
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="compare_strategy_versions",
        arguments={"character_id": "maya", "strategy_a": 13, "strategy_b": 14, "metric": "retention"}
    )
    assert res.status == "SUCCESS"
    data = res.data
    assert data["character_id"] == "maya"

    sig = data["significance"]
    assert sig["test"] == "welch_t_test"
    assert sig["verdict"] in ("significant", "not_significant", "insufficient_data")
    assert isinstance(sig["statistically_significant"], bool)

    if sig["verdict"] == "insufficient_data":
        # An honest refusal must explain itself and must not claim significance.
        assert sig["statistically_significant"] is False
        assert sig["reason"]
    else:
        # A real verdict must be derivable from the reported groups.
        assert sig["statistically_significant"] == (sig["p_value"] < sig["alpha"])
        for group in (data["strategy_a"], data["strategy_b"]):
            assert group["sample_size"] >= 2
            assert group["no_data"] is False


def test_compare_strategy_versions_refuses_to_invent_a_missing_cohort():
    """Comparing against a version with no telemetry yields insufficient_data."""
    res = mcp_client.call_tool(
        agent_identity="evolution_agent",
        tool_name="compare_strategy_versions",
        arguments={"character_id": "maya", "strategy_a": 13, "strategy_b": 9999}
    )
    assert res.status == "SUCCESS"
    sig = res.data["significance"]
    assert sig["verdict"] == "insufficient_data"
    assert sig["statistically_significant"] is False
    assert res.data["strategy_b"]["no_data"] is True


def test_evolution_agent_mcp_evidence_preservation():
    """Phase 7 & Phase 8: Evolution Agent uses MCP to formulate strategy and stores StrategyDecisionTrace."""
    trace_id = "trace_evolution_test_mcp"
    evolution_result = evolution_agent.analyze_and_evolve(trace_id=trace_id)

    assert evolution_result["status"] == "STRATEGY_EVOLVED"
    assert evolution_result["new_strategy_version"] >= 14
    assert "mcp_governance" in evolution_result
    assert "get_strategy_performance" in evolution_result["mcp_governance"]["tools_invoked"]

    stats = evolution_result["statistical_significance"]
    assert stats["sample_floor_met"] is True
    assert stats["decision"] == "PASS"
    # A PASS is only legitimate if the underlying test actually found significance.
    assert stats["test"]["statistically_significant"] is True
    assert stats["test"]["p_value"] < stats["test"]["alpha"]
    assert stats["relative_lift"] >= 0.05
    # The winning arm must differ from the one that was active, otherwise there
    # was nothing to change.
    assert stats["candidate_hook"] != stats["baseline_hook"]

    # Verify Decision Trace
    traces = evolution_agent.get_decision_traces()
    assert len(traces) > 0
    latest = traces[-1]
    assert latest["statistical_decision"] == "PASS"
    assert latest["sample_size"] >= 50
    assert latest["approval_status"] == "ACTIVE"

    # The reasoning must name the arms and cite the evidence, not just assert a
    # conclusion. Asserted by content rather than by exact phrasing so a wording
    # change does not fail the test.
    summary = latest["agent_reasoning_summary"]
    assert stats["candidate_hook"] in summary
    assert stats["baseline_hook"] in summary
    assert "t-test" in summary

    # Evidence must reference the SQL that was actually executed.
    assert latest["evidence_results"]
    assert latest["evidence_results"][0]["sql"]


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
    assert res.latency_ms >= 0.0
    # Offline results must announce themselves as simulated so the UI can label
    # them, and must never be mistaken for measurements.
    assert res.data["is_simulated"] is True
    assert res.data["data_source"] == "deterministic_simulation"
    assert res.data["row_count"] > 0
    assert res.is_simulated is True

    # 2. Strategy comparison offline cannot produce a significance verdict,
    #    because the simulation does not carry sample variance. It must say so.
    res_comp = client_inst.call_tool(
        agent_identity="evolution_agent",
        tool_name="compare_strategy_versions",
        arguments={"character_id": "maya", "strategy_a": 13, "strategy_b": 14},
        trace_id="contract_test_trace"
    )
    assert res_comp.status == "SUCCESS"
    sig = res_comp.data["significance"]
    assert sig["verdict"] == "insufficient_data"
    assert sig["statistically_significant"] is False
    assert sig["reason"]

    # 3. Governance ledgers do not exist offline - the adapter must decline
    #    rather than fabricate an audit history.
    res_ledger = client_inst.call_tool(
        agent_identity="governance_console",
        tool_name="get_governance_ledger",
        arguments={"limit": 10},
        trace_id="contract_test_trace"
    )
    assert res_ledger.status == "SUCCESS"
    assert res_ledger.data["no_data"] is True
    assert res_ledger.data["events"] == []
    assert "unavailable_reason" in res_ledger.data



# ---------------------------------------------------------------------------
# Regression guards for the fabricated-analytics class of bug
# ---------------------------------------------------------------------------

def test_adapters_module_contains_no_hardcoded_metrics():
    """
    Guards the specific failure this integration was rewritten to eliminate:
    analytics adapters that return invented constants dressed up as measurements.

    The original implementation shipped `avg_watch_pct: 0.742`,
    `retention_lift: 0.164`, `statistically_significant: True`,
    `total_claims_audited: 142` and `mean_fidelity_score: 0.96`. Every number a
    user sees must now originate in a row returned by a query, so none of those
    literals may reappear in the adapter module.
    """
    import pathlib
    import re

    source = pathlib.Path("backend/app/mcp/adapters.py").read_text(encoding="utf-8")
    code_lines = []
    for line in source.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        code_lines.append(line)
    code = "\n".join(code_lines)

    banned_literals = ["0.742", "0.164", "0.712", "0.96", "0.88", "142", "0.082"]
    for literal in banned_literals:
        assert literal not in code, (
            f"hardcoded metric {literal!r} reappeared in adapters.py - "
            "analytics values must come from query results"
        )

    # `statistically_significant` may only ever be assigned from a computed
    # boolean or an explicit False, never hardcoded True.
    assert not re.search(r'"statistically_significant":\s*True', code), (
        "significance must be computed by welch_t_test(), never asserted"
    )


def test_welch_t_test_is_honest_about_weak_evidence():
    """The significance test must refuse, not guess, when evidence is thin."""
    from backend.app.mcp.adapters import welch_t_test

    # Too few observations.
    thin = welch_t_test(0.5, 0.01, 1, 0.7, 0.01, 1)
    assert thin["verdict"] == "insufficient_data"
    assert thin["statistically_significant"] is False

    # Identical distributions must not be called significant.
    same = welch_t_test(0.60, 0.01, 500, 0.60, 0.01, 500)
    assert same["statistically_significant"] is False

    # A large, well-sampled separation must be detected.
    clear = welch_t_test(0.55, 0.01, 500, 0.72, 0.01, 500)
    assert clear["statistically_significant"] is True
    assert clear["p_value"] < 0.05
    assert clear["absolute_difference"] > 0

    # Zero variance carries no information about dispersion.
    degenerate = welch_t_test(0.5, 0.0, 100, 0.9, 0.0, 100)
    assert degenerate["verdict"] == "insufficient_data"


def test_sql_templates_reject_injection_attempts():
    """
    Agents supply typed arguments, never SQL. Anything that could change the
    shape of a statement must be refused at the template boundary.
    """
    from backend.app.mcp import sql_templates as tpl

    hostile = [
        "maya'; DROP TABLE scene_events; --",
        "maya' OR '1'='1",
        "maya\\'",
        "maya UNION SELECT * FROM system.users",
    ]
    for value in hostile:
        with pytest.raises(tpl.TemplateArgumentError):
            tpl.build_strategy_performance(value, "IN", 50)

    # Numeric bounds are enforced rather than interpolated blindly.
    with pytest.raises(tpl.TemplateArgumentError):
        tpl.build_recent_production_metrics("maya", 10_000)
    with pytest.raises(tpl.TemplateArgumentError):
        tpl.build_recent_production_metrics("maya", "5; DROP TABLE scene_events")

    # Metric names are mapped through an allowlist, not concatenated.
    with pytest.raises(tpl.TemplateArgumentError):
        tpl.build_compare_strategies("maya", 13, 14, "watch_pct FROM system.tables --")

    # A legitimate call still renders.
    query_id, sql = tpl.build_strategy_performance("maya", "IN", 50)
    assert query_id == "ch_query_881a"
    assert "'maya'" in sql and "'IN'" in sql


def test_permission_matrix_covers_governance_console():
    """The observability identity may read ledgers and nothing else."""
    allowed = MCPToolPermissionPolicy.get_allowed_tools_for_agent("governance_console")
    assert "get_mcp_call_ledger" in allowed
    assert "get_governance_ledger" in allowed
    # It must not be able to influence production strategy.
    assert MCPToolPermissionPolicy.is_authorized("governance_console", "get_strategy_performance") is False
    assert MCPToolPermissionPolicy.is_authorized("governance_console", "compare_strategy_versions") is False
