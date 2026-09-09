-- ==============================================================================
-- AVATAROS ClickHouse Initialization Schema
--
-- Database-agnostic: statements are unqualified so they apply to whichever
-- database the connection is bound to (`CLICKHOUSE_DATABASE`). This lets the
-- identical file run against a local Docker ClickHouse and ClickHouse Cloud.
--
-- Read path : official `mcp-clickhouse` MCP server (read-only `run_select_query`)
-- Write path: clickhouse-connect batch insert from the AVATAROS backend
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Audience telemetry - drives the Evolution Agent feedback loop
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scene_events (
    event LowCardinality(String) DEFAULT 'scene_impression',
    avatar_id LowCardinality(String),
    character_version LowCardinality(String),
    campaign_id String,
    scene_id String,
    language LowCardinality(String),
    region LowCardinality(String),
    platform LowCardinality(String),
    hook_type LowCardinality(String),
    opening_duration_s Float32,
    emotion_target LowCardinality(String),
    shot_preference LowCardinality(String) DEFAULT 'medium_shot',
    watch_pct Float32,
    ctr Float32,
    conversion UInt8,
    strategy_version UInt32 DEFAULT 13,
    trace_id String DEFAULT '',
    ts DateTime64(3, 'UTC')
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(ts)
ORDER BY (avatar_id, region, platform, hook_type, ts)
SETTINGS index_granularity = 8192;

-- ------------------------------------------------------------------------------
-- 2. Strategy lineage - every applied performance strategy, with its evidence
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_versions (
    character_id LowCardinality(String),
    strategy_version UInt32,
    region LowCardinality(String),
    audience LowCardinality(String),
    platform LowCardinality(String),
    hook_type LowCardinality(String),
    opening_duration_min Float32,
    opening_duration_max Float32,
    shot_preference LowCardinality(String),
    energy_bias Float32,
    sample_size UInt32,
    retention_lift Float32,
    confidence String DEFAULT '',
    source_query_id String,
    trace_id String DEFAULT '',
    applied_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree()
ORDER BY (character_id, strategy_version);

-- ------------------------------------------------------------------------------
-- 3. MCP call ledger - append-only record of EVERY partner tool invocation.
--    This is what the in-app MCP Trace panel reads back, through the official
--    MCP server, making runtime partner usage self-evidencing.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mcp_tool_calls (
    call_id String,
    trace_id String,
    session_id String DEFAULT '',
    agent_identity LowCardinality(String),
    tool_name LowCardinality(String),
    arguments String DEFAULT '{}',
    compiled_sql String DEFAULT '',
    authorized UInt8,
    status LowCardinality(String),
    error String DEFAULT '',
    rows_returned UInt32 DEFAULT 0,
    server_identity LowCardinality(String),
    transport LowCardinality(String),
    latency_ms Float32,
    ts DateTime64(3, 'UTC')
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(ts)
ORDER BY (ts, agent_identity, tool_name)
SETTINGS index_granularity = 8192;

-- ------------------------------------------------------------------------------
-- 4. Governance ledger - immutable audit of every gate, rights and Guardian
--    decision. "Why was this promo blocked?" is answered by a SELECT, not a log.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS governance_events (
    event_id String,
    trace_id String,
    run_id String DEFAULT '',
    character_id LowCardinality(String),
    character_version LowCardinality(String) DEFAULT '',
    stage LowCardinality(String),
    decision LowCardinality(String),
    reason_code LowCardinality(String) DEFAULT '',
    detail String DEFAULT '',
    actor LowCardinality(String) DEFAULT 'system',
    severity LowCardinality(String) DEFAULT 'info',
    ts DateTime64(3, 'UTC')
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(ts)
ORDER BY (ts, character_id, stage, decision)
SETTINGS index_granularity = 8192;
