"""
MCP partner adapters.

`ClickHouseMCPAdapter` is the production path. It owns no data of its own: each
domain tool compiles to a governed SQL template, that SQL is executed by the
official `mcp-clickhouse` server over a real MCP transport, and the rows that come
back are what the caller receives. When a query matches nothing, the adapter says
so - `no_data: True` - rather than substituting a plausible number.

`DeterministicMCPAdapter` is the offline path used by unit tests and by a clone
that has no cluster configured. It computes its answers from the in-memory
telemetry simulation, and everything it returns is stamped `is_simulated: True`
and `data_source: "deterministic_simulation"` so the UI can label it honestly.
Neither adapter contains a hardcoded metric.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from backend.app.config import settings
from backend.app.logging import app_logger
from backend.app.mcp import sql_templates as tpl
from backend.app.mcp.mcp_session import MCPCallOutcome, mcp_server_session
from backend.app.models.mcp import (
    ClaimVerificationMetricsQuery,
    CompareStrategiesQuery,
    GovernanceLedgerQuery,
    GovernanceSummaryQuery,
    MCPCallLedgerQuery,
    MCPToolDefinition,
    MCPToolInvocation,
    RecentProductionMetricsQuery,
    ScenePerformanceQuery,
    StrategyPerformanceQuery,
)
from backend.app.data.telemetry_store import telemetry_store


class MCPAdapterError(RuntimeError):
    """Raised when the partner server could not satisfy a call."""


# ---------------------------------------------------------------------------
# Shared tool catalogue
# ---------------------------------------------------------------------------

def _tool_catalogue() -> List[MCPToolDefinition]:
    return [
        MCPToolDefinition(
            name="query_scene_performance",
            description="Per-scene retention, drop-off and opening-duration percentiles from ClickHouse.",
            input_schema=ScenePerformanceQuery.model_json_schema(),
        ),
        MCPToolDefinition(
            name="get_strategy_performance",
            description="Hook-type retention distribution with sample variance (query 881a), for strategy selection.",
            input_schema=StrategyPerformanceQuery.model_json_schema(),
        ),
        MCPToolDefinition(
            name="compare_strategy_versions",
            description="Two-sample comparison of strategy versions with a Welch's t-test computed from real aggregates.",
            input_schema=CompareStrategiesQuery.model_json_schema(),
        ),
        MCPToolDefinition(
            name="get_recent_production_metrics",
            description="Most recent audience impression rows for the live telemetry feed.",
            input_schema=RecentProductionMetricsQuery.model_json_schema(),
        ),
        MCPToolDefinition(
            name="get_claim_verification_metrics",
            description="Claim-verification outcomes aggregated from the immutable governance ledger.",
            input_schema=ClaimVerificationMetricsQuery.model_json_schema(),
        ),
        MCPToolDefinition(
            name="get_mcp_call_ledger",
            description="Reads the MCP call ledger back through the partner server - the trace panel's data source.",
            input_schema=MCPCallLedgerQuery.model_json_schema(),
            category="governance",
        ),
        MCPToolDefinition(
            name="get_governance_ledger",
            description="Immutable gate, rights and Guardian decisions with reason codes.",
            input_schema=GovernanceLedgerQuery.model_json_schema(),
            category="governance",
        ),
        MCPToolDefinition(
            name="get_governance_summary",
            description="Decision counts per pipeline stage over a time window.",
            input_schema=GovernanceSummaryQuery.model_json_schema(),
            category="governance",
        ),
    ]


def welch_t_test(
    mean_a: float, var_a: float, n_a: int, mean_b: float, var_b: float, n_b: int
) -> Dict[str, Any]:
    """
    Welch's unequal-variance t-test computed from group aggregates.

    Returns an honest verdict. When either group is too small, or the variance is
    degenerate, the result is `insufficient_data` - not a significance claim. The
    two-sided p-value uses a normal approximation to the t distribution, which is
    accurate at these sample sizes and avoids a SciPy dependency; the approximation
    is named in the payload so nobody has to guess how it was produced.
    """
    if n_a < 2 or n_b < 2:
        return {
            "test": "welch_t_test",
            "verdict": "insufficient_data",
            "statistically_significant": False,
            "reason": f"needs at least 2 observations per group, got n_a={n_a}, n_b={n_b}",
        }

    se_sq = (var_a / n_a) + (var_b / n_b)
    if se_sq <= 0:
        return {
            "test": "welch_t_test",
            "verdict": "insufficient_data",
            "statistically_significant": False,
            "reason": "zero pooled variance - the samples carry no dispersion",
        }

    se = math.sqrt(se_sq)
    diff = mean_b - mean_a
    t_stat = diff / se

    # Welch-Satterthwaite degrees of freedom.
    num = se_sq ** 2
    den = ((var_a / n_a) ** 2 / (n_a - 1)) + ((var_b / n_b) ** 2 / (n_b - 1))
    dof = num / den if den > 0 else float(n_a + n_b - 2)

    # Two-sided p-value, normal approximation to t (valid at these dof).
    p_value = math.erfc(abs(t_stat) / math.sqrt(2))

    ci_half_width = 1.96 * se
    significant = p_value < 0.05

    return {
        "test": "welch_t_test",
        "verdict": "significant" if significant else "not_significant",
        "statistically_significant": significant,
        "t_statistic": round(t_stat, 4),
        "degrees_of_freedom": round(dof, 2),
        "p_value": round(p_value, 6),
        "alpha": 0.05,
        "absolute_difference": round(diff, 5),
        "relative_lift": round(diff / mean_a, 5) if mean_a else None,
        "difference_ci_95": [round(diff - ci_half_width, 5), round(diff + ci_half_width, 5)],
        "p_value_method": "normal_approximation_to_t",
    }


def _ci95(mean: float, var: float, n: int) -> List[Optional[float]]:
    if n < 2 or var < 0:
        return [None, None]
    se = math.sqrt(var / n)
    return [round(mean - 1.96 * se, 4), round(mean + 1.96 * se, 4)]


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BaseMCPAdapter(ABC):
    """Abstract MCP partner tool adapter."""

    @abstractmethod
    def initialize(self) -> bool:
        ...

    @abstractmethod
    def list_tools(self) -> List[MCPToolDefinition]:
        ...

    @abstractmethod
    def execute(self, invocation: MCPToolInvocation) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        ...

    def last_call_evidence(self) -> Dict[str, Any]:
        """Evidence about the most recent execute() on this thread."""
        return {}


# ---------------------------------------------------------------------------
# Production adapter - official mcp-clickhouse over a real MCP transport
# ---------------------------------------------------------------------------

class ClickHouseMCPAdapter(BaseMCPAdapter):
    """
    Executes governed templates against ClickHouse via the official MCP server.

    Every value this adapter returns originates in a row the server sent back.
    """

    def __init__(self) -> None:
        self.session = mcp_server_session
        self._evidence: Dict[str, Any] = {}
        # Populated when the handshake succeeded but the cluster probe did not.
        self._probe_error: Optional[str] = None

    # -------------------------------------------------------------- lifecycle

    def initialize(self) -> bool:
        """
        Connects, then proves the connection is usable.

        A successful MCP handshake only means the partner server process started -
        it says nothing about whether that server can reach ClickHouse. Readiness
        must mean "a query would work", otherwise health reports green while every
        analytical call fails.
        """
        if not self.session.start(timeout=30.0):
            app_logger.log_operation(
                trace_id="system",
                operation="mcp_adapter_initialize",
                status="ERROR",
                agent_task="clickhouse_mcp_adapter",
                details={"stage": "handshake", "error": self.session.last_error},
            )
            self._probe_error = self.session.last_error
            return False

        probe = self.session.run_query("SELECT 1 AS ok")
        if not probe.ok:
            self._probe_error = probe.error
            app_logger.log_operation(
                trace_id="system",
                operation="mcp_adapter_initialize",
                status="ERROR",
                agent_task="clickhouse_mcp_adapter",
                details={"stage": "cluster_probe", "error": probe.error},
            )
            return False

        self._probe_error = None
        app_logger.log_operation(
            trace_id="system",
            operation="mcp_adapter_initialize",
            status="READY",
            agent_task="clickhouse_mcp_adapter",
            details={
                "server": self.session.server_identity,
                "transport": settings.MCP_TRANSPORT,
                "probe_latency_ms": probe.latency_ms,
            },
        )
        return True

    def list_tools(self) -> List[MCPToolDefinition]:
        return _tool_catalogue()

    def get_status(self) -> Dict[str, Any]:
        s = self.session.status()
        return {
            "provider": "clickhouse_mcp",
            "server_url": s["endpoint"],
            # Ready means the server answered AND the cluster behind it responded.
            "ready": bool(s["ready"] and self._probe_error is None),
            "handshake_ok": s["ready"],
            "transport": s["transport"],
            "read_only": True,
            "is_simulated": False,
            "server_identity": self.session.server_identity,
            "server_tools": s["server_tools"],
            "query_tool": settings.MCP_QUERY_TOOL,
            "database": settings.CLICKHOUSE_DATABASE,
            "last_error": self._probe_error or s["last_error"],
        }

    def last_call_evidence(self) -> Dict[str, Any]:
        return dict(self._evidence)

    # ---------------------------------------------------------------- helpers

    def _run(self, query_id: str, sql: str) -> Tuple[MCPCallOutcome, Dict[str, Any]]:
        """Executes one governed statement and records the evidence."""
        outcome = self.session.run_query(sql)
        self._evidence = {
            "query_id": query_id,
            "compiled_sql": sql,
            "rows_returned": outcome.row_count,
            "latency_ms": outcome.latency_ms,
            "server_identity": self.session.server_identity,
            "transport": settings.MCP_TRANSPORT,
            "mcp_tool": settings.MCP_QUERY_TOOL,
        }
        if not outcome.ok:
            raise MCPAdapterError(
                f"ClickHouse MCP query '{query_id}' failed: {outcome.error}"
            )
        envelope = {
            "query_id": query_id,
            "sql": sql,
            "executed_via": {
                "protocol": "mcp",
                "server": self.session.server_identity,
                "tool": settings.MCP_QUERY_TOOL,
                "transport": settings.MCP_TRANSPORT,
            },
            "execution_time_ms": outcome.latency_ms,
            "row_count": outcome.row_count,
            "data_source": "clickhouse_via_official_mcp_server",
            "is_simulated": False,
            "no_data": outcome.row_count == 0,
        }
        return outcome, envelope

    # --------------------------------------------------------------- dispatch

    def execute(self, invocation: MCPToolInvocation) -> Dict[str, Any]:
        tool = invocation.tool_name
        args = invocation.arguments
        handler = getattr(self, f"_tool_{tool}", None)
        if handler is None:
            raise KeyError(f"Unknown tool '{tool}' on ClickHouse MCP adapter.")
        return handler(args)

    # ------------------------------------------------------------------ tools

    def _tool_query_scene_performance(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = ScenePerformanceQuery(**args)
        query_id, sql = tpl.build_scene_performance(q.character_id, q.scene_no)
        outcome, env = self._run(query_id, sql)
        rows = outcome.dicts()
        env.update({
            "character_id": q.character_id,
            "scenes": rows,
            "scene_count": len(rows),
        })
        if rows:
            total_n = sum(int(r.get("sample_size") or 0) for r in rows)
            weighted = sum(
                float(r.get("avg_watch_pct") or 0) * int(r.get("sample_size") or 0)
                for r in rows
            )
            env["overall_avg_watch_pct"] = round(weighted / total_n, 4) if total_n else None
            env["total_sample_size"] = total_n
        return env

    def _tool_get_strategy_performance(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = StrategyPerformanceQuery(**args)
        query_id, sql = tpl.build_strategy_performance(
            q.character_id, q.region, q.min_sample_size
        )
        outcome, env = self._run(query_id, sql)
        rows = []
        for r in outcome.dicts():
            n = int(r.get("n") or 0)
            mean = float(r.get("avg_retention") or 0.0)
            var = float(r.get("var_watch") or 0.0)
            rows.append({
                "hook_type": r.get("hook_type"),
                "n": n,
                "avg_retention": mean,
                "avg_ctr": float(r.get("avg_ctr") or 0.0),
                "var_watch": var,
                "avg_opening_duration_s": float(r.get("avg_opening_duration_s") or 0.0),
                "ci_95": _ci95(mean, var, n),
                "meets_sample_floor": n >= q.min_sample_size,
            })
        env.update({
            "character_id": q.character_id,
            "region": q.region,
            "min_sample_size": q.min_sample_size,
            "rows": rows,
        })
        return env

    def _tool_compare_strategy_versions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = CompareStrategiesQuery(**args)
        metric = "retention" if q.metric in ("avg_retention", "retention") else q.metric
        query_id, sql = tpl.build_compare_strategies(
            q.character_id, q.strategy_a, q.strategy_b, metric
        )
        outcome, env = self._run(query_id, sql)

        by_version: Dict[int, Dict[str, Any]] = {}
        for r in outcome.dicts():
            by_version[int(r["strategy_version"])] = r

        group_a = by_version.get(q.strategy_a)
        group_b = by_version.get(q.strategy_b)

        env.update({
            "character_id": q.character_id,
            "comparison_metric": metric,
            "strategy_a": _strategy_group(q.strategy_a, group_a),
            "strategy_b": _strategy_group(q.strategy_b, group_b),
        })

        if not group_a or not group_b:
            missing = [
                str(v) for v, g in ((q.strategy_a, group_a), (q.strategy_b, group_b)) if not g
            ]
            env["significance"] = {
                "test": "welch_t_test",
                "verdict": "insufficient_data",
                "statistically_significant": False,
                "reason": f"no telemetry rows for strategy version(s): {', '.join(missing)}",
            }
            env["no_data"] = True
            return env

        env["significance"] = welch_t_test(
            mean_a=float(group_a["mean_metric"]),
            var_a=float(group_a["var_metric"] or 0.0),
            n_a=int(group_a["n"]),
            mean_b=float(group_b["mean_metric"]),
            var_b=float(group_b["var_metric"] or 0.0),
            n_b=int(group_b["n"]),
        )
        return env

    def _tool_get_recent_production_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = RecentProductionMetricsQuery(**args)
        query_id, sql = tpl.build_recent_production_metrics(q.character_id, q.limit)
        outcome, env = self._run(query_id, sql)
        events = outcome.dicts()
        env.update({
            "character_id": q.character_id,
            "total_events": len(events),
            "events": events,
        })
        return env

    def _tool_get_claim_verification_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = ClaimVerificationMetricsQuery(**args)
        query_id, sql = tpl.build_claim_verification_metrics(q.time_window_days)
        outcome, env = self._run(query_id, sql)
        rows = outcome.dicts()
        summary = rows[0] if rows else {}
        total = int(summary.get("total_decisions") or 0)
        env.update({
            "time_window_days": q.time_window_days,
            "total_decisions": total,
            "passed": int(summary.get("passed") or 0),
            "blocked": int(summary.get("blocked") or 0),
            "warned": int(summary.get("warned") or 0),
            "distinct_runs": int(summary.get("distinct_runs") or 0),
            "distinct_reason_codes": int(summary.get("distinct_reason_codes") or 0),
        })
        # A zero-row governance ledger is a real, meaningful answer: nothing has been
        # adjudicated yet. Say that instead of manufacturing an audit history.
        env["no_data"] = total == 0
        if total:
            env["block_rate"] = round(int(summary.get("blocked") or 0) / total, 4)
        return env

    def _tool_get_mcp_call_ledger(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = MCPCallLedgerQuery(**args)
        query_id, sql = tpl.build_mcp_call_ledger(q.limit, q.agent_identity)
        outcome, env = self._run(query_id, sql)
        env.update({"calls": outcome.dicts(), "total": outcome.row_count})
        return env

    def _tool_get_governance_ledger(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = GovernanceLedgerQuery(**args)
        query_id, sql = tpl.build_governance_ledger(q.limit, q.decision)
        outcome, env = self._run(query_id, sql)
        env.update({"events": outcome.dicts(), "total": outcome.row_count})
        return env

    def _tool_get_governance_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        q = GovernanceSummaryQuery(**args)
        query_id, sql = tpl.build_governance_summary(q.time_window_days)
        outcome, env = self._run(query_id, sql)
        env.update({
            "time_window_days": q.time_window_days,
            "breakdown": outcome.dicts(),
        })
        return env


def _strategy_group(version: int, row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not row:
        return {"strategy_version": version, "sample_size": 0, "no_data": True}
    n = int(row["n"])
    mean = float(row["mean_metric"])
    var = float(row["var_metric"] or 0.0)
    return {
        "strategy_version": version,
        "sample_size": n,
        "mean_metric": mean,
        "variance": var,
        "avg_retention": float(row.get("avg_retention") or 0.0),
        "avg_ctr": float(row.get("avg_ctr") or 0.0),
        "ci_95": _ci95(mean, var, n),
        "no_data": False,
    }


# ---------------------------------------------------------------------------
# Offline adapter - deterministic simulation, explicitly labelled as such
# ---------------------------------------------------------------------------

class DeterministicMCPAdapter(BaseMCPAdapter):
    """
    Offline adapter for tests and for a clone with no ClickHouse configured.

    It answers from the in-memory telemetry simulation, computing every statistic
    from that dataset. Nothing is hardcoded, and every payload declares
    `is_simulated: True` so the UI never presents these numbers as measurements.
    """

    def initialize(self) -> bool:
        return True

    def list_tools(self) -> List[MCPToolDefinition]:
        return _tool_catalogue()

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "deterministic",
            "server_url": "in_process://deterministic_mcp_adapter",
            "ready": True,
            "transport": "in_process",
            "read_only": True,
            "is_simulated": True,
            "server_identity": "deterministic_simulation",
            "note": "No MCP server is contacted in this mode. Figures are simulated, not measured.",
        }

    def _envelope(self, query_id: str, sql: str, row_count: int) -> Dict[str, Any]:
        return {
            "query_id": query_id,
            "sql": sql,
            "executed_via": {"protocol": "none", "server": "in_process_simulation"},
            "execution_time_ms": 0.0,
            "row_count": row_count,
            "data_source": "deterministic_simulation",
            "is_simulated": True,
            "no_data": row_count == 0,
        }

    def execute(self, invocation: MCPToolInvocation) -> Dict[str, Any]:
        tool = invocation.tool_name
        args = invocation.arguments

        if tool == "get_strategy_performance":
            q = StrategyPerformanceQuery(**args)
            result = telemetry_store.run_query_881a(
                avatar_id=q.character_id, region=q.region, min_sample=q.min_sample_size
            )
            env = self._envelope(result["query_id"], result["sql"], len(result["rows"]))
            env.update({
                "character_id": q.character_id,
                "region": q.region,
                "min_sample_size": q.min_sample_size,
                "rows": result["rows"],
            })
            return env

        if tool == "compare_strategy_versions":
            q = CompareStrategiesQuery(**args)
            perf_a = telemetry_store.get_strategy_performance(q.strategy_a)
            perf_b = telemetry_store.get_strategy_performance(q.strategy_b)
            env = self._envelope(
                "sim_strategy_compare",
                "-- deterministic simulation: no SQL executed",
                (1 if perf_a.get("sample_size") else 0) + (1 if perf_b.get("sample_size") else 0),
            )
            n_a = int(perf_a.get("sample_size") or 0)
            n_b = int(perf_b.get("sample_size") or 0)
            env.update({
                "character_id": q.character_id,
                "comparison_metric": q.metric,
                "strategy_a": {"strategy_version": q.strategy_a, **perf_a, "no_data": n_a == 0},
                "strategy_b": {"strategy_version": q.strategy_b, **perf_b, "no_data": n_b == 0},
            })
            if n_a < 2 or n_b < 2:
                env["significance"] = {
                    "test": "welch_t_test",
                    "verdict": "insufficient_data",
                    "statistically_significant": False,
                    "reason": f"simulation holds n_a={n_a}, n_b={n_b}",
                }
            else:
                # Variance is not tracked by the simulation's aggregate helper, so a
                # significance verdict cannot be computed honestly here.
                env["significance"] = {
                    "test": "welch_t_test",
                    "verdict": "insufficient_data",
                    "statistically_significant": False,
                    "reason": "sample variance is unavailable in deterministic simulation mode",
                }
            return env

        if tool == "query_scene_performance":
            q = ScenePerformanceQuery(**args)
            events = [
                e for e in telemetry_store.get_recent_events(limit=2000)
                if e.get("avatar_id") == q.character_id
            ]
            by_scene: Dict[str, List[Dict[str, Any]]] = {}
            for e in events:
                by_scene.setdefault(e["scene_id"], []).append(e)
            scenes = []
            for scene_id in sorted(by_scene):
                items = by_scene[scene_id]
                n = len(items)
                avg_watch = sum(float(i["watch_pct"]) for i in items) / n
                scenes.append({
                    "scene_id": scene_id,
                    "sample_size": n,
                    "avg_watch_pct": round(avg_watch, 4),
                    "dropoff_rate": round(1 - avg_watch, 4),
                    "avg_ctr": round(sum(float(i["ctr"]) for i in items) / n, 5),
                })
            env = self._envelope(
                "sim_scene_perf", "-- deterministic simulation: no SQL executed", len(scenes)
            )
            env.update({
                "character_id": q.character_id,
                "scenes": scenes,
                "scene_count": len(scenes),
            })
            return env

        if tool == "get_recent_production_metrics":
            q = RecentProductionMetricsQuery(**args)
            events = telemetry_store.get_recent_events(limit=q.limit)
            env = self._envelope(
                "sim_recent_metrics", "-- deterministic simulation: no SQL executed", len(events)
            )
            env.update({
                "character_id": q.character_id,
                "total_events": len(events),
                "events": events,
            })
            return env

        if tool in (
            "get_claim_verification_metrics",
            "get_mcp_call_ledger",
            "get_governance_ledger",
            "get_governance_summary",
        ):
            # These read the ClickHouse governance ledgers. Offline there is no
            # ledger to read, and inventing one would be exactly the kind of
            # fabricated audit history this system exists to prevent.
            env = self._envelope(
                f"sim_{tool}", "-- deterministic simulation: no ledger available", 0
            )
            env.update({
                "unavailable_reason": (
                    "Governance and MCP ledgers live in ClickHouse. "
                    "Configure MCP_PROVIDER=clickhouse_mcp with a reachable cluster to read them."
                ),
                "calls": [],
                "events": [],
                "breakdown": [],
                "total": 0,
                "total_decisions": 0,
            })
            return env

        raise KeyError(f"Unknown tool '{tool}' on Deterministic MCP adapter.")
