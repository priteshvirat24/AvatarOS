import pytest
from datetime import datetime, timezone
from backend.app.config import Settings
from backend.app.models.events import SceneImpressionEvent, ProductionStrategy, StrategyEvidence
from backend.app.data.telemetry_store import (
    BaseTelemetryProvider,
    InMemoryTelemetryProvider,
    ClickHouseTelemetryProvider,
    get_telemetry_provider,
    telemetry_store
)
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_telemetry_provider_selection():
    """Verify provider selection is configuration-driven."""
    in_mem_provider = InMemoryTelemetryProvider()
    assert isinstance(in_mem_provider, BaseTelemetryProvider)
    assert in_mem_provider.active_strategy.strategy_version == 13

    # Default settings has TELEMETRY_PROVIDER = "clickhouse"
    active_provider = get_telemetry_provider()
    assert isinstance(active_provider, BaseTelemetryProvider)

def test_scene_impression_event_serialization():
    """Verify SceneImpressionEvent model and fields."""
    event = SceneImpressionEvent(
        avatar_id="maya",
        character_version="1.7.0",
        campaign_id="test_camp",
        scene_id="sc_1",
        language="en",
        region="IN",
        platform="instagram_reel",
        hook_type="question",
        opening_duration_s=6.8,
        emotion_target="controlled_excitement",
        shot_preference="close_up",
        watch_pct=0.78,
        ctr=0.045,
        conversion=True,
        strategy_version=14,
        trace_id="trace_test_ser",
        ts=datetime.now(timezone.utc).isoformat()
    )
    d = event.model_dump()
    assert d["avatar_id"] == "maya"
    assert d["shot_preference"] == "close_up"
    assert d["strategy_version"] == 14
    assert d["trace_id"] == "trace_test_ser"

def test_query_881a_analytical_aggregation():
    """Verify parameterized Query 881a against real or fallback telemetry."""
    res = telemetry_store.run_query_881a(avatar_id="maya", region="IN", min_sample=50)
    assert res["query_id"] == "ch_query_881a"
    assert len(res["rows"]) >= 4
    
    top_hook = res["rows"][0]
    assert top_hook["hook_type"] == "question"
    assert top_hook["n"] >= 50
    assert top_hook["meets_sample_floor"] is True
    assert top_hook["avg_retention"] > 0.65
    assert len(top_hook["ci_95"]) == 2
    assert top_hook["ci_95"][0] < top_hook["ci_95"][1]

def test_batch_ingestion_and_flushing():
    """Verify batch ingestion buffer accepts events and flushes cleanly."""
    initial_recent = telemetry_store.get_recent_events(limit=10)
    
    test_event = SceneImpressionEvent(
        avatar_id="maya",
        character_version="1.7.0",
        campaign_id="batch_test",
        scene_id="sc_batch_1",
        language="en",
        region="IN",
        platform="linkedin",
        hook_type="statistic",
        opening_duration_s=7.2,
        emotion_target="neutral",
        shot_preference="medium_shot",
        watch_pct=0.62,
        ctr=0.035,
        conversion=False,
        strategy_version=13,
        trace_id="trace_batch_unit_test",
        ts=datetime.now(timezone.utc).isoformat()
    )
    
    telemetry_store.record_event(test_event)
    telemetry_store.flush()
    
    recent_after = telemetry_store.get_recent_events(limit=10)
    traces = [e.get("trace_id") for e in recent_after]
    assert "trace_batch_unit_test" in traces

def test_evolution_statistical_guard_sample_floor():
    """Verify rejection when sample size is below n >= 50."""
    provider = InMemoryTelemetryProvider()
    # Filter out events to make sample count small (< 50)
    provider.events = [e for e in provider.events if e.hook_type == "statement"][:20]
    
    with pytest.raises(ValueError, match="floor"):
        provider.propose_and_apply_evolution()

def test_evolution_statistical_guard_ci_overlap():
    """Verify rejection when confidence intervals overlap with baseline."""
    provider = InMemoryTelemetryProvider()
    # Overwrite events so all hook types have identical retention to statement
    for e in provider.events:
        e.watch_pct = 0.548

    with pytest.raises(ValueError, match="overlap"):
        provider.propose_and_apply_evolution()

def test_strategy_version_persistence_and_lineage():
    """Verify strategy creation increments version and adds to history."""
    provider = InMemoryTelemetryProvider()
    v13 = provider.active_strategy
    assert v13.strategy_version == 13
    
    v14 = provider.propose_and_apply_evolution()
    assert v14.strategy_version == 14
    assert v14.hook_type == "question"
    assert provider.active_strategy.strategy_version == 14
    
    history = provider.get_strategy_history("maya")
    versions = [s.strategy_version for s in history]
    assert 13 in versions
    assert 14 in versions

def test_clickhouse_unreachable_fallback_resilience():
    """Verify ClickHouseTelemetryProvider falls back safely if ClickHouse host is unreachable."""
    fallback_mock = InMemoryTelemetryProvider()
    # Mock settings pointing to unreachable port
    bad_provider = ClickHouseTelemetryProvider(fallback_provider=fallback_mock)
    # Simulate client failure
    bad_provider.client = None
    
    # Must not raise; must delegate safely
    q_res = bad_provider.run_query_881a()
    assert q_res["query_id"] == "ch_query_881a"
    assert bad_provider.active_strategy.strategy_version in (13, 14)

def test_health_endpoints_with_clickhouse():
    """Verify /health and /health/ready report ClickHouse status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "clickhouse" in data["services"]

    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    ready_data = ready_res.json()
    assert "clickhouse_connected" in ready_data
