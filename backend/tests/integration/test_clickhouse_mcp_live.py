"""
Live integration tests: official `mcp-clickhouse` server against a real cluster.

Skipped unless AVATAROS_INTEGRATION_TESTS=1, because they require a reachable
ClickHouse and will spawn the partner server subprocess.

    docker compose up -d clickhouse
    backend/.venv/bin/python -m backend.app.data.seed_clickhouse
    AVATAROS_INTEGRATION_TESTS=1 backend/.venv/bin/python -m pytest backend/tests/integration -v

These are the tests that substantiate the ClickHouse track requirement: they assert
that analytics leave this process over a real MCP transport and are executed by the
official partner server.
"""

import os

import pytest

INTEGRATION = os.getenv("AVATAROS_INTEGRATION_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not INTEGRATION,
    reason="set AVATAROS_INTEGRATION_TESTS=1 with a reachable ClickHouse to run",
)


@pytest.fixture(scope="module")
def gateway():
    from backend.app.mcp.client import mcp_client

    assert mcp_client.ensure_initialized(), (
        f"MCP session failed to start: {mcp_client.get_status().get('last_error')}"
    )
    return mcp_client


def test_session_is_the_official_server_over_a_real_transport(gateway):
    """The connection must be the published ClickHouse server, not an in-process stub."""
    status = gateway.get_status()
    assert status["provider"] == "clickhouse_mcp"
    assert status["ready"] is True
    assert status["is_simulated"] is False
    assert status["server_identity"].startswith("mcp-clickhouse@")
    assert status["transport"] in ("stdio", "http", "sse")
    # Tools advertised by the partner server itself, discovered via MCP tools/list.
    assert "run_query" in status["server_tools"]
    assert status["read_only"] is True


def test_metrics_originate_in_returned_rows(gateway):
    """Every reported figure must be reconstructable from the rows the server sent."""
    res = gateway.call_tool(
        agent_identity="evolution_agent",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya", "region": "IN", "min_sample_size": 50},
        trace_id="trace_integration_881a",
    )
    assert res.status == "SUCCESS"
    assert res.is_simulated is False
    assert res.rows_returned > 0
    assert res.compiled_sql.startswith("SELECT")
    assert res.data["executed_via"]["server"].startswith("mcp-clickhouse")
    assert res.data["row_count"] == len(res.data["rows"])

    for row in res.data["rows"]:
        low, high = row["ci_95"]
        assert low <= row["avg_retention"] <= high


def test_significance_is_computed_not_asserted(gateway):
    """A real two-sample comparison, with a verdict the data actually supports."""
    res = gateway.call_tool(
        agent_identity="evolution_agent",
        tool_name="compare_strategy_versions",
        arguments={"character_id": "maya", "strategy_a": 13, "strategy_b": 14},
        trace_id="trace_integration_compare",
    )
    assert res.status == "SUCCESS"
    sig = res.data["significance"]

    if sig["verdict"] == "insufficient_data":
        pytest.skip("seed data does not contain both strategy cohorts")

    assert sig["statistically_significant"] == (sig["p_value"] < sig["alpha"])
    # The reported difference must match the two group means.
    diff = res.data["strategy_b"]["mean_metric"] - res.data["strategy_a"]["mean_metric"]
    assert abs(diff - sig["absolute_difference"]) < 1e-4


def test_unauthorized_call_is_refused_and_still_recorded(gateway):
    """A refusal is itself an audit event - it must reach the ledger."""
    res = gateway.call_tool(
        agent_identity="live_session",
        tool_name="get_strategy_performance",
        arguments={"character_id": "maya"},
        trace_id="trace_integration_refusal",
    )
    assert res.status == "UNAUTHORIZED"
    assert res.call_id, "refused calls must still be written to the ledger"

    ledger_res = gateway.call_tool(
        agent_identity="governance_console",
        tool_name="get_mcp_call_ledger",
        arguments={"limit": 50},
        trace_id="trace_integration_refusal_check",
    )
    assert ledger_res.status == "SUCCESS"
    refusals = [
        c for c in ledger_res.data["calls"]
        if c["agent_identity"] == "live_session" and c["status"] == "UNAUTHORIZED"
    ]
    assert refusals, "the refusal should be queryable from ClickHouse"
    assert refusals[0]["authorized"] == 0


def test_the_trace_ledger_is_read_back_through_mcp(gateway):
    """
    Self-evidencing: the panel that proves partner usage is itself fed by partner
    usage. A call made now must be visible in the ledger read afterwards, with the
    SQL that produced it.
    """
    marker = "trace_integration_selfref"
    first = gateway.call_tool(
        agent_identity="evolution_agent",
        tool_name="query_scene_performance",
        arguments={"character_id": "maya"},
        trace_id=marker,
    )
    assert first.status == "SUCCESS"

    ledger_res = gateway.call_tool(
        agent_identity="governance_console",
        tool_name="get_mcp_call_ledger",
        arguments={"limit": 100},
        trace_id="trace_integration_selfref_read",
    )
    assert ledger_res.status == "SUCCESS"
    assert ledger_res.data["executed_via"]["protocol"] == "mcp"

    matching = [c for c in ledger_res.data["calls"] if c["call_id"] == first.call_id]
    assert matching, "the just-made call must be present in the ledger"
    entry = matching[0]
    assert entry["tool_name"] == "query_scene_performance"
    assert entry["status"] == "SUCCESS"
    assert entry["compiled_sql"].startswith("SELECT")
    assert entry["latency_ms"] > 0
    assert entry["server_identity"].startswith("mcp-clickhouse@")


def test_partner_server_refuses_writes(gateway):
    """
    The server is configured read-only. A mutation must fail at the server, which
    is the backstop behind the template layer's refusal to express one.
    """
    from backend.app.mcp.mcp_session import mcp_server_session

    outcome = mcp_server_session.run_query(
        "INSERT INTO scene_events (avatar_id, ts) VALUES ('injected', now())"
    )
    assert outcome.ok is False, "read-only server must reject an INSERT"
