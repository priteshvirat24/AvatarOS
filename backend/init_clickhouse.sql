-- ==============================================================================
-- AVATAROS ClickHouse Initialization Schema (Section 22 & 23)
-- Target: Real columnar telemetry storage for the Evolution Agent feedback loop
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS default;

CREATE TABLE IF NOT EXISTS default.scene_events (
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

-- Strategy versions table for persistent strategy lineage (Section 24)
CREATE TABLE IF NOT EXISTS default.strategy_versions (
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
