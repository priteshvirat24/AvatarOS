import os
import sys
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import clickhouse_connect

from backend.app.config import settings
from backend.app.logging import app_logger

SEED_HOOK_CONFIGS = {
    "question": {"mean_watch": 0.712, "std": 0.08, "mean_ctr": 0.048, "count": 742},
    "statistic": {"mean_watch": 0.638, "std": 0.09, "mean_ctr": 0.039, "count": 420},
    "challenge": {"mean_watch": 0.592, "std": 0.10, "mean_ctr": 0.035, "count": 360},
    "statement": {"mean_watch": 0.548, "std": 0.11, "mean_ctr": 0.027, "count": 320},
}

def get_client():
    host = settings.CLICKHOUSE_URL.replace("http://", "").replace("https://", "").split(":")[0]
    port = int(settings.CLICKHOUSE_URL.split(":")[-1]) if ":" in settings.CLICKHOUSE_URL else 8123
    password = settings.CLICKHOUSE_PASSWORD.get_secret_value() if settings.CLICKHOUSE_PASSWORD else ""
    return clickhouse_connect.get_client(
        host=host,
        port=port,
        database=settings.CLICKHOUSE_DATABASE,
        username=settings.CLICKHOUSE_USERNAME,
        password=password,
        connect_timeout=settings.CLICKHOUSE_CONNECT_TIMEOUT,
        send_receive_timeout=settings.CLICKHOUSE_SEND_RECEIVE_TIMEOUT
    )

def ensure_tables(client):
    ddl_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "init_clickhouse.sql")
    if os.path.exists(ddl_path):
        with open(ddl_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        for statement in sql_content.split(";"):
            clean_stmt = statement.strip()
            if clean_stmt and not clean_stmt.startswith("--"):
                client.command(clean_stmt)
    else:
        # Fallback DDL if file not found
        client.command("""
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
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(ts)
        ORDER BY (avatar_id, region, platform, hook_type, ts)
        SETTINGS index_granularity = 8192;
        """)
        client.command("""
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
        ) ENGINE = ReplacingMergeTree()
        ORDER BY (character_id, strategy_version);
        """)

def generate_seed_events() -> List[List[Any]]:
    random.seed(42)
    base_time = datetime.now(timezone.utc) - timedelta(days=60)
    rows = []
    
    for hook, cfg in SEED_HOOK_CONFIGS.items():
        for i in range(cfg["count"]):
            watch = max(0.1, min(0.99, random.gauss(cfg["mean_watch"], cfg["std"])))
            ctr = max(0.005, min(0.15, random.gauss(cfg["mean_ctr"], 0.01)))
            opening_dur = random.uniform(5.8, 7.5) if hook == "question" else random.uniform(8.5, 11.0)
            platform = random.choice(["instagram_reel", "youtube_shorts", "linkedin"])
            conv = 1 if (random.random() < (ctr * 0.4)) else 0
            ts = base_time + timedelta(hours=i * 1.8)
            char_ver = "1.7.0" if i % 2 == 0 else "1.6.0"
            
            rows.append([
                "scene_impression",
                "maya",
                char_ver,
                "titan_laptop_india_devs",
                f"sc_titan_{i%5 + 1}",
                random.choice(["en", "hi"]),
                "IN",
                platform,
                hook,
                float(round(opening_dur, 2)),
                "controlled_excitement" if hook == "question" else "neutral",
                "close_up" if hook == "question" else "medium_shot",
                float(round(watch, 4)),
                float(round(ctr, 4)),
                int(conv),
                13,
                f"trace_seed_{hook}_{i}",
                ts
            ])
    return rows

def seed_clickhouse(force: bool = False):
    print("Connecting to ClickHouse at", settings.CLICKHOUSE_URL, "...")
    client = get_client()
    ensure_tables(client)

    # 1. Seed strategy_versions baseline (v13)
    existing_strategies = client.query(
        "SELECT count() FROM strategy_versions WHERE character_id = 'maya' AND strategy_version = 13"
    ).result_rows[0][0]

    if existing_strategies == 0 or force:
        print("Inserting baseline strategy v13 into strategy_versions...")
        strategy_cols = [
            "character_id", "strategy_version", "region", "audience", "platform",
            "hook_type", "opening_duration_min", "opening_duration_max", "shot_preference",
            "energy_bias", "sample_size", "retention_lift", "confidence",
            "source_query_id", "trace_id", "applied_at"
        ]
        strategy_row = [
            "maya", 13, "IN", "developers", "instagram_reel",
            "statement", 8.5, 10.5, "medium_shot",
            0.60, 320, 0.0, "Baseline strategy (n=320)",
            "ch_query_base", "trace_seed_init",
            datetime.now(timezone.utc) - timedelta(days=60)
        ]
        client.insert("strategy_versions", [strategy_row], column_names=strategy_cols)
        print("✅ Baseline strategy v13 inserted.")
    else:
        print("Strategy v13 already exists in ClickHouse.")

    # 2. Seed scene_events
    existing_count = client.query("SELECT count() FROM scene_events").result_rows[0][0]
    print(f"Current scene_events row count: {existing_count}")

    if existing_count > 0 and not force:
        print(f"Table scene_events already has {existing_count} rows. Skipping seed generation (use --force to reseed).")
        return

    if force and existing_count > 0:
        print("Truncating scene_events table due to --force...")
        client.command("TRUNCATE TABLE scene_events")

    print("Generating 1,842 benchmark telemetry events...")
    rows = generate_seed_events()
    columns = [
        "event", "avatar_id", "character_version", "campaign_id", "scene_id",
        "language", "region", "platform", "hook_type", "opening_duration_s",
        "emotion_target", "shot_preference", "watch_pct", "ctr", "conversion",
        "strategy_version", "trace_id", "ts"
    ]

    # Batch insert in chunks of 500
    chunk_size = 500
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i + chunk_size]
        client.insert("scene_events", chunk, column_names=columns)
        print(f"Inserted chunk {i // chunk_size + 1} ({len(chunk)} rows)...")

    new_count = client.query("SELECT count() FROM scene_events").result_rows[0][0]
    print(f"✅ Seeding complete! Verified total rows in scene_events: {new_count}")

if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    seed_clickhouse(force=force_flag)
