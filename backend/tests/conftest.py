import pytest
from datetime import datetime, timedelta, timezone
import clickhouse_connect
from backend.app.config import settings
from backend.app.data.telemetry_store import telemetry_store

@pytest.fixture(autouse=True)
def setup_test_telemetry():
    """Ensure baseline strategy v13 is active before each test."""
    try:
        host = settings.CLICKHOUSE_URL.replace("http://", "").replace("https://", "").split(":")[0]
        port = int(settings.CLICKHOUSE_URL.split(":")[-1]) if ":" in settings.CLICKHOUSE_URL else 8123
        password = settings.CLICKHOUSE_PASSWORD.get_secret_value() if settings.CLICKHOUSE_PASSWORD else ""
        client = clickhouse_connect.get_client(
            host=host,
            port=port,
            database=settings.CLICKHOUSE_DATABASE,
            username=settings.CLICKHOUSE_USERNAME,
            password=password,
            connect_timeout=0.05
        )
        client.command("TRUNCATE TABLE strategy_versions")
        strategy_cols = [
            "character_id", "strategy_version", "region", "audience", "platform",
            "hook_type", "opening_duration_min", "opening_duration_max", "shot_preference",
            "energy_bias", "sample_size", "retention_lift", "confidence",
            "source_query_id", "trace_id", "applied_at"
        ]
        strategy_row = [
            "maya", 13, "IN", "developers", "instagram_reel",
            "statement", 8.5, 10.5, "medium_shot",
            0.60, 320, 0.0, "Baseline strategy",
            "ch_query_base", "trace_seed_init",
            datetime.now(timezone.utc) - timedelta(days=60)
        ]
        client.insert("strategy_versions", [strategy_row], column_names=strategy_cols)
    except Exception:
        pass

    # Reset active strategy on global facade
    try:
        if hasattr(telemetry_store, "_load_active_strategy_from_db"):
            telemetry_store._load_active_strategy_from_db()
        if hasattr(telemetry_store, "fallback"):
            telemetry_store.fallback._init_strategies()
            telemetry_store.fallback._active_strategy = telemetry_store.fallback.strategies["maya_v13"]
    except Exception:
        pass

    # Reset claims state in orchestrator
    try:
        from backend.app.agents.orchestrator import orchestrator
        from backend.app.data.documents import get_seed_claims
        orchestrator.research_agent.claims = get_seed_claims()
    except Exception:
        pass

    yield
