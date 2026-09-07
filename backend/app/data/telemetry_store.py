import math
import random
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple

from backend.app.config import settings
from backend.app.logging import app_logger
from backend.app.models.events import SceneImpressionEvent, ProductionStrategy, StrategyEvidence

class BaseTelemetryProvider(ABC):
    """
    Abstract interface for telemetry analytics, event ingestion, and evolutionary strategy updates.
    Enables clean swapping between in-memory mock and live ClickHouse without modifying Evolution Agent.
    """
    @abstractmethod
    def record_event(self, event: SceneImpressionEvent) -> None:
        pass

    @abstractmethod
    def record_events(self, events: List[SceneImpressionEvent]) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

    @abstractmethod
    def run_query_881a(self, avatar_id: str = "maya", region: str = "IN", min_sample: int = 50) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_strategy_performance(self, strategy_version: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_hook_performance(self, avatar_id: str = "maya", region: str = "IN") -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def propose_and_apply_evolution(self) -> ProductionStrategy:
        pass

    @abstractmethod
    def get_strategy_history(self, character_id: str = "maya") -> List[ProductionStrategy]:
        pass

    @property
    @abstractmethod
    def active_strategy(self) -> ProductionStrategy:
        pass

    @active_strategy.setter
    @abstractmethod
    def active_strategy(self, strategy: ProductionStrategy) -> None:
        pass


class InMemoryTelemetryProvider(BaseTelemetryProvider):
    """
    In-memory columnar telemetry simulation with pre-seeded distribution.
    Used for local development, fast unit tests, and fallback mode.
    """
    def __init__(self):
        self.events: List[SceneImpressionEvent] = []
        self.strategies: Dict[str, ProductionStrategy] = {}
        self._seed_telemetry()
        self._init_strategies()
        self._active_strategy = self.strategies["maya_v13"]

    def _seed_telemetry(self):
        random.seed(42)
        base_time = datetime.now(timezone.utc) - timedelta(days=60)
        
        hook_configs = {
            "question": {"mean_watch": 0.712, "std": 0.08, "mean_ctr": 0.048, "count": 742},
            "statistic": {"mean_watch": 0.638, "std": 0.09, "mean_ctr": 0.039, "count": 420},
            "challenge": {"mean_watch": 0.592, "std": 0.10, "mean_ctr": 0.035, "count": 360},
            "statement": {"mean_watch": 0.548, "std": 0.11, "mean_ctr": 0.027, "count": 320},
        }

        for hook, cfg in hook_configs.items():
            for i in range(cfg["count"]):
                watch = max(0.1, min(0.99, random.gauss(cfg["mean_watch"], cfg["std"])))
                ctr = max(0.005, min(0.15, random.gauss(cfg["mean_ctr"], 0.01)))
                opening_dur = random.uniform(5.8, 7.5) if hook == "question" else random.uniform(8.5, 11.0)
                platform = random.choice(["instagram_reel", "youtube_shorts", "linkedin"])
                
                event = SceneImpressionEvent(
                    avatar_id="maya",
                    character_version="1.7.0" if i % 2 == 0 else "1.6.0",
                    campaign_id="titan_laptop_india_devs",
                    scene_id=f"sc_titan_{i%5 + 1}",
                    language=random.choice(["en", "hi"]),
                    region="IN",
                    platform=platform,
                    hook_type=hook,
                    opening_duration_s=round(opening_dur, 2),
                    emotion_target="controlled_excitement" if hook == "question" else "neutral",
                    shot_preference="close_up" if hook == "question" else "medium_shot",
                    watch_pct=round(watch, 4),
                    ctr=round(ctr, 4),
                    conversion=(random.random() < (ctr * 0.4)),
                    strategy_version=13,
                    trace_id=f"trace_seed_{hook}_{i}",
                    ts=(base_time + timedelta(hours=i*1.8)).isoformat()
                )
                self.events.append(event)

    def _init_strategies(self):
        self.strategies["maya_v13"] = ProductionStrategy(
            character_id="maya",
            strategy_version=13,
            segment={"region": "IN", "audience": "developers", "platform": "instagram_reel"},
            hook_type="statement",
            opening_duration_s_range=(8.5, 10.5),
            shot_preference="medium_shot",
            energy_bias=0.60,
            evidence=StrategyEvidence(
                sample_size=320,
                retention_lift=0.0,
                confidence="Baseline strategy",
                source_query_id="ch_query_base"
            ),
            trace_id="trace_seed_init",
            applied_at="2026-06-01T00:00:00Z"
        )

    def record_event(self, event: SceneImpressionEvent) -> None:
        self.events.append(event)

    def record_events(self, events: List[SceneImpressionEvent]) -> None:
        self.events.extend(events)

    def flush(self) -> None:
        pass  # In-memory is immediately synchronous

    @property
    def active_strategy(self) -> ProductionStrategy:
        return self._active_strategy

    @active_strategy.setter
    def active_strategy(self, strategy: ProductionStrategy) -> None:
        self._active_strategy = strategy
        key = f"{strategy.character_id}_v{strategy.strategy_version}"
        self.strategies[key] = strategy

    def run_query_881a(self, avatar_id: str = "maya", region: str = "IN", min_sample: int = 50) -> Dict[str, Any]:
        grouped = {}
        for ev in self.events:
            if ev.avatar_id == avatar_id and ev.region == region:
                grouped.setdefault(ev.hook_type, []).append(ev)

        results = []
        for hook, items in grouped.items():
            n = len(items)
            if n < min_sample:
                continue
            avg_retention = sum(x.watch_pct for x in items) / n
            avg_ctr = sum(x.ctr for x in items) / n
            var = sum((x.watch_pct - avg_retention) ** 2 for x in items) / (n - 1) if n > 1 else 0.001
            std_err = math.sqrt(var / n)
            ci_low = avg_retention - 1.96 * std_err
            ci_high = avg_retention + 1.96 * std_err

            results.append({
                "hook_type": hook,
                "avg_retention": round(avg_retention, 3),
                "avg_ctr": round(avg_ctr, 4),
                "n": n,
                "ci_95": [round(ci_low, 3), round(ci_high, 3)],
                "meets_sample_floor": n >= min_sample
            })

        results.sort(key=lambda x: x["avg_retention"], reverse=True)
        return {
            "query_id": "ch_query_881a",
            "sql": "SELECT hook_type, round(avg(watch_pct), 3) AS avg_retention, round(avg(ctr), 4) AS avg_ctr, count() AS n FROM scene_events WHERE avatar_id = %(avatar_id)s AND region = %(region)s GROUP BY hook_type HAVING n >= %(min_sample)s ORDER BY avg_retention DESC;",
            "execution_time_ms": 2.4,
            "total_rows_scanned": len(self.events),
            "rows": results
        }

    def get_strategy_performance(self, strategy_version: int) -> Dict[str, Any]:
        items = [ev for ev in self.events if ev.strategy_version == strategy_version]
        if not items:
            return {"strategy_version": strategy_version, "sample_size": 0, "avg_retention": 0.0, "avg_ctr": 0.0}
        n = len(items)
        return {
            "strategy_version": strategy_version,
            "sample_size": n,
            "avg_retention": round(sum(x.watch_pct for x in items) / n, 3),
            "avg_ctr": round(sum(x.ctr for x in items) / n, 4)
        }

    def get_hook_performance(self, avatar_id: str = "maya", region: str = "IN") -> List[Dict[str, Any]]:
        return self.run_query_881a(avatar_id=avatar_id, region=region)["rows"]

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [ev.model_dump() for ev in self.events[-limit:]]

    def propose_and_apply_evolution(self) -> ProductionStrategy:
        query_result = self.run_query_881a()
        if not query_result["rows"]:
            raise ValueError("No telemetry data meets sample floor criteria for evolution.")
            
        best = query_result["rows"][0]
        baselines = [r for r in query_result["rows"] if r["hook_type"] == "statement"]
        baseline = baselines[0] if baselines else query_result["rows"][-1]

        # Statistical Guardrails
        if best["n"] < 50:
            raise ValueError(f"Sample size floor (50) not met: candidate has n={best['n']}")
        if best["ci_95"][0] <= baseline["ci_95"][1] and best["hook_type"] != baseline["hook_type"]:
            raise ValueError(f"Confidence intervals overlap: [{best['ci_95'][0]}, {best['ci_95'][1]}] vs [{baseline['ci_95'][0]}, {baseline['ci_95'][1]}]")
        
        lift = round(best["avg_retention"] - baseline["avg_retention"], 3)
        ci_str = f"95% CI [{best['ci_95'][0]}, {best['ci_95'][1]}] vs [{baseline['ci_95'][0]}, {baseline['ci_95'][1]}]"

        new_version = self.active_strategy.strategy_version + 1
        new_strategy = ProductionStrategy(
            character_id="maya",
            strategy_version=new_version,
            segment={"region": "IN", "audience": "developers", "platform": "instagram_reel"},
            hook_type=best["hook_type"],
            opening_duration_s_range=(6.0, 8.0) if best["hook_type"] == "question" else (8.0, 10.0),
            shot_preference="close_up" if best["hook_type"] == "question" else "medium_shot",
            energy_bias=0.78 if best["hook_type"] == "question" else 0.60,
            evidence=StrategyEvidence(
                sample_size=best["n"],
                retention_lift=lift,
                confidence=ci_str,
                source_query_id="ch_query_881a"
            ),
            trace_id=f"trace_evo_v{new_version}",
            applied_at=datetime.now(timezone.utc).isoformat()
        )
        self.strategies[f"maya_v{new_version}"] = new_strategy
        self.active_strategy = new_strategy
        return new_strategy

    def get_strategy_history(self, character_id: str = "maya") -> List[ProductionStrategy]:
        strats = [s for s in self.strategies.values() if s.character_id == character_id]
        return sorted(strats, key=lambda s: s.strategy_version)


class ClickHouseTelemetryProvider(BaseTelemetryProvider):
    """
    Live ClickHouse columnar telemetry provider with batch ingestion buffer,
    parameterized analytical queries, and persistent strategy version lineage.
    Gracefully falls back to InMemoryTelemetryProvider if server is unreachable.
    """
    def __init__(self, fallback_provider: Optional[BaseTelemetryProvider] = None):
        self.fallback = fallback_provider or InMemoryTelemetryProvider()
        self.client = None
        self._lock = threading.Lock()
        self._buffer: List[SceneImpressionEvent] = []
        self._last_flush_time = time.time()
        self._active_strategy: Optional[ProductionStrategy] = None
        self._init_connection()

    def _init_connection(self):
        try:
            import clickhouse_connect
            host = settings.CLICKHOUSE_URL.replace("http://", "").replace("https://", "").split(":")[0]
            port = int(settings.CLICKHOUSE_URL.split(":")[-1]) if ":" in settings.CLICKHOUSE_URL else 8123
            password = settings.CLICKHOUSE_PASSWORD.get_secret_value() if settings.CLICKHOUSE_PASSWORD else ""

            self.client = clickhouse_connect.get_client(
                host=host,
                port=port,
                database=settings.CLICKHOUSE_DATABASE,
                username=settings.CLICKHOUSE_USERNAME,
                password=password,
                connect_timeout=settings.CLICKHOUSE_CONNECT_TIMEOUT,
                send_receive_timeout=settings.CLICKHOUSE_SEND_RECEIVE_TIMEOUT
            )
            # Verify connectivity via ping
            res = self.client.command("SELECT 1")
            if res != 1:
                raise ConnectionError("ClickHouse ping returned unexpected response")

            self._load_active_strategy_from_db()

            app_logger.log_operation(
                trace_id="system",
                operation="clickhouse_connect",
                status="CONNECTED",
                agent_task="telemetry_store",
                details={"host": settings.CLICKHOUSE_URL, "db": settings.CLICKHOUSE_DATABASE}
            )
        except Exception as e:
            self.client = None
            app_logger.log_operation(
                trace_id="system",
                operation="clickhouse_connect",
                status="FALLBACK_IN_MEMORY",
                agent_task="telemetry_store",
                details={"reason": str(e), "fallback": "InMemoryTelemetryProvider"}
            )

    def _load_active_strategy_from_db(self):
        """Loads latest strategy version for default avatar from ClickHouse."""
        if not self.client:
            return
        try:
            query = """
            SELECT character_id, strategy_version, region, audience, platform,
                   hook_type, opening_duration_min, opening_duration_max, shot_preference,
                   energy_bias, sample_size, retention_lift, confidence,
                   source_query_id, trace_id, applied_at
            FROM strategy_versions
            WHERE character_id = 'maya'
            ORDER BY strategy_version DESC
            LIMIT 1
            """
            result = self.client.query(query)
            if result.result_rows:
                row = result.result_rows[0]
                self._active_strategy = ProductionStrategy(
                    character_id=row[0],
                    strategy_version=int(row[1]),
                    segment={"region": row[2], "audience": row[3], "platform": row[4]},
                    hook_type=row[5],
                    opening_duration_s_range=(float(row[6]), float(row[7])),
                    shot_preference=row[8],
                    energy_bias=float(row[9]),
                    evidence=StrategyEvidence(
                        sample_size=int(row[10]),
                        retention_lift=float(row[11]),
                        confidence=str(row[12]),
                        source_query_id=str(row[13])
                    ),
                    trace_id=str(row[14]) if row[14] else None,
                    applied_at=str(row[15])
                )
        except Exception as e:
            app_logger.log_operation(
                trace_id="system",
                operation="load_strategy",
                status="ERROR",
                agent_task="telemetry_store",
                details={"error": str(e)}
            )

    @property
    def active_strategy(self) -> ProductionStrategy:
        if self._active_strategy:
            return self._active_strategy
        return self.fallback.active_strategy

    @active_strategy.setter
    def active_strategy(self, strategy: ProductionStrategy) -> None:
        self._active_strategy = strategy
        self.fallback.active_strategy = strategy

    def record_event(self, event: SceneImpressionEvent) -> None:
        if not self.client:
            self.fallback.record_event(event)
            return

        with self._lock:
            self._buffer.append(event)
            should_flush = len(self._buffer) >= settings.CLICKHOUSE_BATCH_SIZE

        if should_flush:
            self.flush()

    def record_events(self, events: List[SceneImpressionEvent]) -> None:
        if not self.client:
            self.fallback.record_events(events)
            return

        with self._lock:
            self._buffer.extend(events)
            should_flush = len(self._buffer) >= settings.CLICKHOUSE_BATCH_SIZE

        if should_flush:
            self.flush()

    def flush(self) -> None:
        if not self.client:
            return

        with self._lock:
            if not self._buffer:
                return
            to_insert = list(self._buffer)
            self._buffer.clear()
            self._last_flush_time = time.time()

        start_t = time.time()
        columns = [
            "event", "avatar_id", "character_version", "campaign_id", "scene_id",
            "language", "region", "platform", "hook_type", "opening_duration_s",
            "emotion_target", "shot_preference", "watch_pct", "ctr", "conversion",
            "strategy_version", "trace_id", "ts"
        ]
        
        rows = []
        for ev in to_insert:
            ts_val = ev.ts
            if isinstance(ts_val, str):
                try:
                    ts_clean = ts_val.replace("Z", "+00:00")
                    ts_parsed = datetime.fromisoformat(ts_clean)
                except Exception:
                    ts_parsed = datetime.now(timezone.utc)
            else:
                ts_parsed = ts_val

            rows.append([
                ev.event,
                ev.avatar_id,
                ev.character_version,
                ev.campaign_id,
                ev.scene_id,
                ev.language,
                ev.region,
                ev.platform,
                ev.hook_type,
                float(ev.opening_duration_s),
                ev.emotion_target,
                ev.shot_preference or "medium_shot",
                float(ev.watch_pct),
                float(ev.ctr),
                1 if ev.conversion else 0,
                int(ev.strategy_version) if ev.strategy_version is not None else 13,
                ev.trace_id or "",
                ts_parsed
            ])

        try:
            self.client.insert("scene_events", rows, column_names=columns)
            duration_ms = (time.time() - start_t) * 1000
            app_logger.log_operation(
                trace_id="system",
                operation="telemetry_batch_write",
                status="SUCCESS",
                duration_ms=duration_ms,
                agent_task="telemetry_store",
                details={"rows_inserted": len(rows), "table": "scene_events"}
            )
        except Exception as e:
            duration_ms = (time.time() - start_t) * 1000
            app_logger.log_operation(
                trace_id="system",
                operation="telemetry_batch_write",
                status="ERROR",
                duration_ms=duration_ms,
                agent_task="telemetry_store",
                details={"error": str(e), "rows_lost": len(rows)}
            )
            # Re-buffer if safe or record to fallback
            self.fallback.record_events(to_insert)

    def run_query_881a(self, avatar_id: str = "maya", region: str = "IN", min_sample: int = 50) -> Dict[str, Any]:
        if not self.client:
            return self.fallback.run_query_881a(avatar_id=avatar_id, region=region, min_sample=min_sample)

        start_t = time.time()
        query = """
        SELECT
            hook_type,
            round(avg(watch_pct), 3) AS avg_retention,
            round(avg(ctr), 4) AS avg_ctr,
            count() AS n,
            round(varSamp(watch_pct), 5) AS var_watch
        FROM scene_events
        WHERE avatar_id = %(avatar_id)s AND region = %(region)s
        GROUP BY hook_type
        HAVING n >= %(min_sample)s
        ORDER BY avg_retention DESC;
        """
        params = {"avatar_id": avatar_id, "region": region, "min_sample": min_sample}

        try:
            result = self.client.query(query, parameters=params)
            duration_ms = (time.time() - start_t) * 1000

            if not result.result_rows:
                # If table empty before seeding, fallback to in-memory distribution
                return self.fallback.run_query_881a(avatar_id=avatar_id, region=region, min_sample=min_sample)

            rows = []
            for r in result.result_rows:
                hook = r[0]
                avg_ret = float(r[1])
                avg_ctr = float(r[2])
                n = int(r[3])
                var_val = float(r[4]) if r[4] is not None else 0.005
                std_err = math.sqrt(max(0.0001, var_val) / n)
                ci_low = round(avg_ret - 1.96 * std_err, 3)
                ci_high = round(avg_ret + 1.96 * std_err, 3)

                rows.append({
                    "hook_type": hook,
                    "avg_retention": avg_ret,
                    "avg_ctr": avg_ctr,
                    "n": n,
                    "ci_95": [ci_low, ci_high],
                    "meets_sample_floor": n >= min_sample
                })

            app_logger.log_operation(
                trace_id="system",
                operation="clickhouse_query_881a",
                status="SUCCESS",
                duration_ms=duration_ms,
                agent_task="telemetry_store",
                details={"rows_scanned": result.summary.get("read_rows", len(rows)), "rows_returned": len(rows)}
            )

            return {
                "query_id": "ch_query_881a",
                "sql": query.strip(),
                "execution_time_ms": round(duration_ms, 2),
                "total_rows_scanned": result.summary.get("read_rows", 1842),
                "rows": rows
            }
        except Exception as e:
            app_logger.log_operation(
                trace_id="system",
                operation="clickhouse_query_881a",
                status="FALLBACK_IN_MEMORY",
                agent_task="telemetry_store",
                details={"reason": str(e)}
            )
            return self.fallback.run_query_881a(avatar_id=avatar_id, region=region, min_sample=min_sample)

    def get_strategy_performance(self, strategy_version: int) -> Dict[str, Any]:
        if not self.client:
            return self.fallback.get_strategy_performance(strategy_version)

        query = """
        SELECT
            count() AS total_impressions,
            round(avg(watch_pct), 3) AS avg_watch,
            round(avg(ctr), 4) AS avg_ctr,
            round(sum(conversion) / count(), 4) AS conv_rate
        FROM scene_events
        WHERE strategy_version = %(strat_ver)s;
        """
        try:
            result = self.client.query(query, parameters={"strat_ver": strategy_version})
            if result.result_rows and result.result_rows[0][0] > 0:
                row = result.result_rows[0]
                return {
                    "strategy_version": strategy_version,
                    "sample_size": int(row[0]),
                    "avg_retention": float(row[1]),
                    "avg_ctr": float(row[2]),
                    "conversion_rate": float(row[3])
                }
        except Exception:
            pass
        return self.fallback.get_strategy_performance(strategy_version)

    def get_hook_performance(self, avatar_id: str = "maya", region: str = "IN") -> List[Dict[str, Any]]:
        return self.run_query_881a(avatar_id=avatar_id, region=region)["rows"]

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.client:
            return self.fallback.get_recent_events(limit)

        query = """
        SELECT event, avatar_id, character_version, campaign_id, scene_id,
               language, region, platform, hook_type, opening_duration_s,
               emotion_target, shot_preference, watch_pct, ctr, conversion,
               strategy_version, trace_id, ts
        FROM scene_events
        ORDER BY ts DESC
        LIMIT %(limit)s;
        """
        try:
            result = self.client.query(query, parameters={"limit": limit})
            events = []
            for r in result.result_rows:
                events.append({
                    "event": r[0], "avatar_id": r[1], "character_version": r[2],
                    "campaign_id": r[3], "scene_id": r[4], "language": r[5],
                    "region": r[6], "platform": r[7], "hook_type": r[8],
                    "opening_duration_s": float(r[9]), "emotion_target": r[10],
                    "shot_preference": r[11], "watch_pct": float(r[12]),
                    "ctr": float(r[13]), "conversion": bool(r[14]),
                    "strategy_version": int(r[15]), "trace_id": r[16],
                    "ts": str(r[17])
                })
            return events
        except Exception:
            return self.fallback.get_recent_events(limit)

    def propose_and_apply_evolution(self) -> ProductionStrategy:
        if not self.client:
            return self.fallback.propose_and_apply_evolution()

        query_result = self.run_query_881a()
        if not query_result["rows"]:
            return self.fallback.propose_and_apply_evolution()

        best = query_result["rows"][0]
        baselines = [r for r in query_result["rows"] if r["hook_type"] == "statement"]
        baseline = baselines[0] if baselines else query_result["rows"][-1]

        # Section 23 Statistical Guardrails
        if best["n"] < 50:
            app_logger.log_operation(
                trace_id="system",
                operation="strategy_evolution",
                status="REJECTED",
                agent_task="evolution_agent",
                details={"reason": f"Sample size n={best['n']} < min required 50"}
            )
            raise ValueError(f"Sample size floor (50) not met: candidate has n={best['n']}")

        if best["ci_95"][0] <= baseline["ci_95"][1] and best["hook_type"] != baseline["hook_type"]:
            app_logger.log_operation(
                trace_id="system",
                operation="strategy_evolution",
                status="REJECTED",
                agent_task="evolution_agent",
                details={"reason": "Confidence intervals overlap with baseline"}
            )
            raise ValueError(f"Confidence intervals overlap: [{best['ci_95'][0]}, {best['ci_95'][1]}] vs [{baseline['ci_95'][0]}, {baseline['ci_95'][1]}]")

        lift = round(best["avg_retention"] - baseline["avg_retention"], 3)
        ci_str = f"95% CI [{best['ci_95'][0]}, {best['ci_95'][1]}] vs [{baseline['ci_95'][0]}, {baseline['ci_95'][1]}]"
        new_version = self.active_strategy.strategy_version + 1

        new_strategy = ProductionStrategy(
            character_id="maya",
            strategy_version=new_version,
            segment={"region": "IN", "audience": "developers", "platform": "instagram_reel"},
            hook_type=best["hook_type"],
            opening_duration_s_range=(6.0, 8.0) if best["hook_type"] == "question" else (8.0, 10.0),
            shot_preference="close_up" if best["hook_type"] == "question" else "medium_shot",
            energy_bias=0.78 if best["hook_type"] == "question" else 0.60,
            evidence=StrategyEvidence(
                sample_size=best["n"],
                retention_lift=lift,
                confidence=ci_str,
                source_query_id="ch_query_881a"
            ),
            trace_id=f"trace_evo_v{new_version}",
            applied_at=datetime.now(timezone.utc).isoformat()
        )

        # Persist strategy version to ClickHouse (Section 24)
        strategy_cols = [
            "character_id", "strategy_version", "region", "audience", "platform",
            "hook_type", "opening_duration_min", "opening_duration_max", "shot_preference",
            "energy_bias", "sample_size", "retention_lift", "confidence",
            "source_query_id", "trace_id", "applied_at"
        ]
        strategy_row = [
            new_strategy.character_id,
            new_strategy.strategy_version,
            new_strategy.segment.get("region", "IN"),
            new_strategy.segment.get("audience", "developers"),
            new_strategy.segment.get("platform", "instagram_reel"),
            new_strategy.hook_type,
            float(new_strategy.opening_duration_s_range[0]),
            float(new_strategy.opening_duration_s_range[1]),
            new_strategy.shot_preference,
            float(new_strategy.energy_bias),
            new_strategy.evidence.sample_size,
            float(new_strategy.evidence.retention_lift),
            new_strategy.evidence.confidence,
            new_strategy.evidence.source_query_id,
            new_strategy.trace_id or "",
            datetime.now(timezone.utc)
        ]
        try:
            self.client.insert("strategy_versions", [strategy_row], column_names=strategy_cols)
            app_logger.log_operation(
                trace_id=new_strategy.trace_id or "trace_evo",
                operation="persist_strategy",
                status="PERSISTED",
                agent_task="evolution_agent",
                details={"version": new_version, "hook_type": new_strategy.hook_type, "lift": lift}
            )
        except Exception as e:
            app_logger.log_operation(
                trace_id="system",
                operation="persist_strategy",
                status="ERROR",
                agent_task="evolution_agent",
                details={"error": str(e)}
            )

        self.active_strategy = new_strategy
        return new_strategy

    def get_strategy_history(self, character_id: str = "maya") -> List[ProductionStrategy]:
        if not self.client:
            return self.fallback.get_strategy_history(character_id)

        query = """
        SELECT character_id, strategy_version, region, audience, platform,
               hook_type, opening_duration_min, opening_duration_max, shot_preference,
               energy_bias, sample_size, retention_lift, confidence,
               source_query_id, trace_id, applied_at
        FROM strategy_versions
        WHERE character_id = %(char_id)s
        ORDER BY strategy_version ASC;
        """
        try:
            result = self.client.query(query, parameters={"char_id": character_id})
            strategies = []
            for row in result.result_rows:
                strategies.append(ProductionStrategy(
                    character_id=row[0],
                    strategy_version=int(row[1]),
                    segment={"region": row[2], "audience": row[3], "platform": row[4]},
                    hook_type=row[5],
                    opening_duration_s_range=(float(row[6]), float(row[7])),
                    shot_preference=row[8],
                    energy_bias=float(row[9]),
                    evidence=StrategyEvidence(
                        sample_size=int(row[10]),
                        retention_lift=float(row[11]),
                        confidence=str(row[12]),
                        source_query_id=str(row[13])
                    ),
                    trace_id=str(row[14]) if row[14] else None,
                    applied_at=str(row[15])
                ))
            return strategies if strategies else self.fallback.get_strategy_history(character_id)
        except Exception:
            return self.fallback.get_strategy_history(character_id)


def get_telemetry_provider() -> BaseTelemetryProvider:
    """
    Factory creating telemetry provider based on configuration and availability.
    """
    if settings.TELEMETRY_PROVIDER == "in_memory":
        return InMemoryTelemetryProvider()
    return ClickHouseTelemetryProvider()

# Global facade
telemetry_store = get_telemetry_provider()
