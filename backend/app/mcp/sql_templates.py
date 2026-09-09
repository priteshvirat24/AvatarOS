"""
Governed SQL templates for the ClickHouse MCP partner integration.

The official `mcp-clickhouse` server exposes a general `run_query` tool. Handing
that tool to an autonomous agent verbatim would mean handing it arbitrary SQL, so
AVATAROS never does. Instead each domain tool an agent may call maps to exactly one
template here. The agent supplies typed arguments; this module renders them into
literals under strict validation and returns the finished statement.

Consequences that matter for the governance thesis:

* An agent cannot express a query that is not already written down in this file.
* Every literal is validated and escaped before it reaches SQL.
* The rendered statement is recorded verbatim in the MCP call ledger, so the exact
  SQL that produced any number on screen can be read back later.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

# Identifiers we are willing to interpolate as bare strings, deliberately narrow.
_SAFE_STRING = re.compile(r"^[A-Za-z0-9_\-. ]{1,64}$")

# Metric names an agent may sort or compare on, mapped to their column expression.
COMPARABLE_METRICS: Dict[str, str] = {
    "retention": "watch_pct",
    "watch_pct": "watch_pct",
    "ctr": "ctr",
    "conversion": "conversion",
}


class TemplateArgumentError(ValueError):
    """Raised when an agent supplies an argument that fails validation."""


def lit_str(value: Any, field: str) -> str:
    """Validates and single-quotes a string literal."""
    if value is None:
        raise TemplateArgumentError(f"'{field}' is required")
    text = str(value)
    if not _SAFE_STRING.match(text):
        raise TemplateArgumentError(
            f"'{field}' contains characters that are not permitted in a governed query: {text!r}"
        )
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


def lit_int(value: Any, field: str, minimum: int = 0, maximum: int = 1_000_000) -> str:
    """Validates and renders an integer literal within bounds."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise TemplateArgumentError(f"'{field}' must be an integer, got {value!r}")
    if not (minimum <= number <= maximum):
        raise TemplateArgumentError(
            f"'{field}' must be between {minimum} and {maximum}, got {number}"
        )
    return str(number)


def metric_column(value: Any, field: str = "metric") -> str:
    """Maps an agent-supplied metric name onto an allowlisted column."""
    key = str(value or "retention").lower()
    if key not in COMPARABLE_METRICS:
        raise TemplateArgumentError(
            f"'{field}' must be one of {sorted(COMPARABLE_METRICS)}, got {value!r}"
        )
    return COMPARABLE_METRICS[key]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
# Each builder returns (query_id, sql). The query_id is a stable label used in the
# UI and in the call ledger so a chart can be traced back to the statement behind it.


def build_scene_performance(character_id: str, scene_no: Optional[int] = None) -> Tuple[str, str]:
    """Per-scene retention and drop-off for one character."""
    where = f"avatar_id = {lit_str(character_id, 'character_id')}"
    if scene_no is not None:
        where += f" AND scene_id = {lit_str(f'sc_titan_{int(scene_no)}', 'scene_no')}"

    sql = f"""
SELECT
    scene_id,
    count()                                   AS sample_size,
    round(avg(watch_pct), 4)                  AS avg_watch_pct,
    round(1 - avg(watch_pct), 4)              AS dropoff_rate,
    round(avg(ctr), 5)                        AS avg_ctr,
    round(quantile(0.9)(opening_duration_s), 2) AS p90_opening_duration_s
FROM scene_events
WHERE {where}
GROUP BY scene_id
ORDER BY scene_id
""".strip()
    return "ch_query_scene_perf", sql


def build_strategy_performance(
    character_id: str, region: str, min_sample: int = 50
) -> Tuple[str, str]:
    """
    Hook-type retention distribution with the variance needed for a confidence
    interval. This is the query the Evolution Agent reasons over.
    """
    sql = f"""
SELECT
    hook_type,
    count()                        AS n,
    round(avg(watch_pct), 4)       AS avg_retention,
    round(avg(ctr), 5)             AS avg_ctr,
    round(varSamp(watch_pct), 6)   AS var_watch,
    round(avg(opening_duration_s), 2) AS avg_opening_duration_s
FROM scene_events
WHERE avatar_id = {lit_str(character_id, 'character_id')}
  AND region = {lit_str(region, 'region')}
GROUP BY hook_type
HAVING n >= {lit_int(min_sample, 'min_sample_size', 1, 100000)}
ORDER BY avg_retention DESC
""".strip()
    return "ch_query_881a", sql


def build_compare_strategies(
    character_id: str, strategy_a: int, strategy_b: int, metric: str = "retention"
) -> Tuple[str, str]:
    """
    Side-by-side aggregates for two strategy versions, including sample variance so
    a real Welch's t-test can be computed from the returned rows.
    """
    column = metric_column(metric)
    sql = f"""
SELECT
    strategy_version,
    count()                     AS n,
    round(avg({column}), 5)     AS mean_metric,
    round(varSamp({column}), 6) AS var_metric,
    round(avg(watch_pct), 4)    AS avg_retention,
    round(avg(ctr), 5)          AS avg_ctr
FROM scene_events
WHERE avatar_id = {lit_str(character_id, 'character_id')}
  AND strategy_version IN ({lit_int(strategy_a, 'strategy_a', 0, 100000)}, {lit_int(strategy_b, 'strategy_b', 0, 100000)})
GROUP BY strategy_version
ORDER BY strategy_version
""".strip()
    return "ch_query_strategy_compare", sql


def build_recent_production_metrics(character_id: str, limit: int = 20) -> Tuple[str, str]:
    """Most recent impression rows, for the live telemetry feed."""
    sql = f"""
SELECT
    scene_id,
    hook_type,
    platform,
    region,
    language,
    round(watch_pct, 4) AS watch_pct,
    round(ctr, 5)       AS ctr,
    conversion,
    strategy_version,
    toString(ts)        AS ts
FROM scene_events
WHERE avatar_id = {lit_str(character_id, 'character_id')}
ORDER BY ts DESC
LIMIT {lit_int(limit, 'limit', 1, 500)}
""".strip()
    return "ch_query_recent_metrics", sql


def build_claim_verification_metrics(time_window_days: int = 30) -> Tuple[str, str]:
    """
    Claim-verification outcomes drawn from the immutable governance ledger.

    Every claim the Publication Gate evaluated is a row in `governance_events`, so
    this returns what the system actually decided rather than a stored statistic.
    """
    sql = f"""
SELECT
    count()                                  AS total_decisions,
    countIf(decision = 'PASS')               AS passed,
    countIf(decision = 'BLOCK')              AS blocked,
    countIf(decision = 'WARN')               AS warned,
    uniqExact(run_id)                        AS distinct_runs,
    uniqExact(reason_code)                   AS distinct_reason_codes
FROM governance_events
WHERE stage IN ('verify_claims', 'publication_gate')
  AND ts >= now() - INTERVAL {lit_int(time_window_days, 'time_window_days', 1, 3650)} DAY
""".strip()
    return "ch_query_claim_audit", sql


def build_mcp_call_ledger(limit: int = 25, agent_identity: Optional[str] = None) -> Tuple[str, str]:
    """
    Reads the MCP call ledger back out of ClickHouse.

    This is the self-evidencing part of the integration: the trace panel's contents
    are themselves fetched by an MCP call, which is in turn appended to this table.
    """
    where = "1"
    if agent_identity:
        where = f"agent_identity = {lit_str(agent_identity, 'agent_identity')}"
    sql = f"""
SELECT
    call_id,
    toString(ts)     AS ts,
    agent_identity,
    tool_name,
    status,
    authorized,
    rows_returned,
    round(latency_ms, 2) AS latency_ms,
    server_identity,
    transport,
    compiled_sql,
    error
FROM mcp_tool_calls
WHERE {where}
ORDER BY ts DESC
LIMIT {lit_int(limit, 'limit', 1, 500)}
""".strip()
    return "ch_query_mcp_ledger", sql


def build_governance_ledger(limit: int = 25, decision: Optional[str] = None) -> Tuple[str, str]:
    """Reads governance decisions - the "why was this blocked?" query."""
    where = "1"
    if decision:
        where = f"decision = {lit_str(decision, 'decision')}"
    sql = f"""
SELECT
    event_id,
    toString(ts) AS ts,
    trace_id,
    run_id,
    character_id,
    character_version,
    stage,
    decision,
    reason_code,
    severity,
    detail
FROM governance_events
WHERE {where}
ORDER BY ts DESC
LIMIT {lit_int(limit, 'limit', 1, 500)}
""".strip()
    return "ch_query_governance_ledger", sql


def build_governance_summary(time_window_days: int = 90) -> Tuple[str, str]:
    """Decision counts per stage - powers the governance overview tiles."""
    sql = f"""
SELECT
    stage,
    decision,
    count() AS n
FROM governance_events
WHERE ts >= now() - INTERVAL {lit_int(time_window_days, 'time_window_days', 1, 3650)} DAY
GROUP BY stage, decision
ORDER BY stage, decision
""".strip()
    return "ch_query_governance_summary", sql
