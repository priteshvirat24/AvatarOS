"""
Test configuration.

By default the suite runs fully hermetic: in-memory telemetry and the
deterministic MCP adapter, no ClickHouse, no MCP subprocess, no network. That is
what lets `pytest` pass on a clean clone, and it stops tests from mutating a real
cluster's strategy lineage (which previously made version assertions drift as the
suite ran).

To exercise the real path - official `mcp-clickhouse` server against a live
ClickHouse cluster - set AVATAROS_INTEGRATION_TESTS=1. The integration module
under backend/tests/integration/ is skipped unless that flag is set.

The environment is configured before any application import, because Settings is
resolved once at module import time.
"""

import os

INTEGRATION = os.getenv("AVATAROS_INTEGRATION_TESTS") == "1"

if not INTEGRATION:
    os.environ["TELEMETRY_PROVIDER"] = "in_memory"
    os.environ["MCP_PROVIDER"] = "deterministic"
    os.environ["AI_PROVIDER"] = "deterministic"
    os.environ["LIVE_PROVIDER"] = "deterministic"

import pytest
from datetime import datetime, timedelta, timezone
from backend.app.config import settings
from backend.app.data.telemetry_store import telemetry_store


@pytest.fixture(autouse=True)
def setup_test_telemetry():
    """Restores the baseline v13 strategy before each test."""
    if INTEGRATION:
        _reset_clickhouse_baseline()

    # Reset the in-memory provider's strategy lineage.
    try:
        target = telemetry_store
        if hasattr(target, "fallback"):
            target.fallback._init_strategies()
            target.fallback._active_strategy = target.fallback.strategies["maya_v13"]
            target._active_strategy = None
            if hasattr(target, "_load_active_strategy_from_db"):
                target._load_active_strategy_from_db()
        else:
            target._init_strategies()
            target._active_strategy = target.strategies["maya_v13"]
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


def _reset_clickhouse_baseline():
    """Integration mode only: truncate and re-seed the strategy lineage."""
    try:
        import clickhouse_connect

        url = settings.CLICKHOUSE_URL
        secure = url.startswith("https://")
        hostport = url.replace("https://", "").replace("http://", "").split("/")[0]
        host = hostport.split(":")[0]
        port = int(hostport.split(":")[1]) if ":" in hostport else (8443 if secure else 8123)
        password = settings.CLICKHOUSE_PASSWORD.get_secret_value() if settings.CLICKHOUSE_PASSWORD else ""
        client = clickhouse_connect.get_client(
            host=host, port=port, database=settings.CLICKHOUSE_DATABASE,
            username=settings.CLICKHOUSE_USERNAME, password=password, secure=secure,
            connect_timeout=5,
        )
        client.command("TRUNCATE TABLE strategy_versions")
        client.insert(
            "strategy_versions",
            [[
                "maya", 13, "IN", "developers", "instagram_reel",
                "statement", 8.5, 10.5, "medium_shot",
                0.60, 320, 0.0, "Baseline strategy",
                "ch_query_base", "trace_seed_init",
                datetime.now(timezone.utc) - timedelta(days=60),
            ]],
            column_names=[
                "character_id", "strategy_version", "region", "audience", "platform",
                "hook_type", "opening_duration_min", "opening_duration_max", "shot_preference",
                "energy_bias", "sample_size", "retention_lift", "confidence",
                "source_query_id", "trace_id", "applied_at",
            ],
        )
    except Exception:
        pass
