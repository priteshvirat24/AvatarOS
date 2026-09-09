"""
Append-only ledgers in ClickHouse: MCP calls and governance decisions.

Two tables, two purposes:

`mcp_tool_calls`
    Every partner tool invocation an agent makes - authorized or refused - with
    the exact SQL that was compiled for it, the row count that came back, and the
    measured latency. The in-app MCP Trace panel reads this table back *through*
    the official MCP server, which is what makes the integration self-evidencing.

`governance_events`
    Every Publication Gate, rights and Guardian decision. This is the difference
    between "we log governance" and "governance is queryable": answering "why was
    this promo blocked, and has it happened before?" becomes a SELECT.

Writes go directly over clickhouse-connect rather than through MCP, because the
official server is deliberately held in read-only mode. Reads go through MCP. A
ledger write must never be able to fail a production run, so every path here
swallows its errors after logging them.
"""

from __future__ import annotations

import threading
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any, Callable, Deque, Dict, List, Optional

from backend.app.config import settings
from backend.app.logging import app_logger

MCP_CALL_COLUMNS = [
    "call_id", "trace_id", "session_id", "agent_identity", "tool_name",
    "arguments", "compiled_sql", "authorized", "status", "error",
    "rows_returned", "server_identity", "transport", "latency_ms", "ts",
]

GOVERNANCE_COLUMNS = [
    "event_id", "trace_id", "run_id", "character_id", "character_version",
    "stage", "decision", "reason_code", "detail", "actor", "severity", "ts",
]


class MCPCallBroadcaster:
    """
    In-process live feed of MCP calls, for the trace panel's streaming view.

    ClickHouse remains the durable record; this is only a low-latency mirror so the
    UI can show a call the instant it happens instead of waiting for the next poll.
    Bounded, so a long-running session cannot grow it without limit.
    """

    def __init__(self, capacity: int = 200) -> None:
        self._recent: Deque[Dict[str, Any]] = deque(maxlen=capacity)
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = threading.Lock()

    def publish(self, call: Dict[str, Any]) -> None:
        with self._lock:
            self._recent.append(call)
            subscribers = list(self._subscribers)
        for callback in subscribers:
            try:
                callback(call)
            except Exception:
                # A broken subscriber must never affect the caller's request.
                pass

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._recent)
        return list(reversed(items))[:limit]

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> Callable[[], None]:
        with self._lock:
            self._subscribers.append(callback)

        def unsubscribe() -> None:
            with self._lock:
                if callback in self._subscribers:
                    self._subscribers.remove(callback)

        return unsubscribe


mcp_call_feed = MCPCallBroadcaster()


class ClickHouseLedger:
    """Direct-write ledger client. Degrades to a no-op when ClickHouse is absent."""

    def __init__(self) -> None:
        self._client: Any = None
        self._lock = threading.Lock()
        self._connect_attempted = False
        self._last_error: Optional[str] = None

    # ---------------------------------------------------------------- plumbing

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        with self._lock:
            if self._client is not None:
                return self._client
            self._connect_attempted = True
            try:
                import clickhouse_connect

                url = settings.CLICKHOUSE_URL
                secure = url.startswith("https://")
                hostport = url.replace("https://", "").replace("http://", "").split("/")[0]
                host = hostport.split(":")[0]
                port = int(hostport.split(":")[1]) if ":" in hostport else (8443 if secure else 8123)
                password = (
                    settings.CLICKHOUSE_PASSWORD.get_secret_value()
                    if settings.CLICKHOUSE_PASSWORD
                    else ""
                )
                self._client = clickhouse_connect.get_client(
                    host=host,
                    port=port,
                    database=settings.CLICKHOUSE_DATABASE,
                    username=settings.CLICKHOUSE_USERNAME,
                    password=password,
                    secure=secure,
                    connect_timeout=settings.CLICKHOUSE_CONNECT_TIMEOUT,
                    send_receive_timeout=settings.CLICKHOUSE_SEND_RECEIVE_TIMEOUT,
                )
                self._client.command("SELECT 1")
                self._last_error = None
            except Exception as exc:
                self._client = None
                self._last_error = f"{type(exc).__name__}: {exc}"
            return self._client

    @property
    def available(self) -> bool:
        return self._ensure_client() is not None

    def status(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "database": settings.CLICKHOUSE_DATABASE,
            "last_error": self._last_error,
        }

    def _insert(self, table: str, columns: List[str], rows: List[List[Any]]) -> bool:
        client = self._ensure_client()
        if client is None or not rows:
            return False
        try:
            client.insert(table, rows, column_names=columns)
            return True
        except Exception as exc:
            self._last_error = f"{type(exc).__name__}: {exc}"
            app_logger.log_operation(
                trace_id="system",
                operation="ledger_write",
                status="ERROR",
                agent_task="clickhouse_ledger",
                details={"table": table, "error": self._last_error},
            )
            # A failed audit write must not fail the caller's request.
            self._client = None
            return False

    # ------------------------------------------------------------- MCP ledger

    def record_mcp_call(
        self,
        *,
        trace_id: str,
        agent_identity: str,
        tool_name: str,
        status: str,
        authorized: bool,
        latency_ms: float,
        server_identity: str,
        transport: str,
        arguments: str = "{}",
        compiled_sql: str = "",
        rows_returned: int = 0,
        error: str = "",
        session_id: str = "",
    ) -> str:
        call_id = f"mcpcall_{uuid.uuid4().hex[:16]}"
        row = [
            call_id,
            trace_id or "system",
            session_id or "",
            agent_identity,
            tool_name,
            arguments[:8000],
            compiled_sql[:8000],
            1 if authorized else 0,
            status,
            (error or "")[:2000],
            int(rows_returned),
            server_identity,
            transport,
            float(latency_ms),
            datetime.now(timezone.utc),
        ]
        persisted = self._insert("mcp_tool_calls", MCP_CALL_COLUMNS, [row])

        mcp_call_feed.publish({
            "call_id": call_id,
            "ts": row[-1].isoformat(),
            "trace_id": trace_id or "system",
            "agent_identity": agent_identity,
            "tool_name": tool_name,
            "status": status,
            "authorized": bool(authorized),
            "rows_returned": int(rows_returned),
            "latency_ms": round(float(latency_ms), 2),
            "server_identity": server_identity,
            "transport": transport,
            "compiled_sql": compiled_sql,
            "arguments": arguments,
            "error": error or "",
            "persisted_to_clickhouse": persisted,
        })
        return call_id

    # ------------------------------------------------------ governance ledger

    def record_governance_event(
        self,
        *,
        trace_id: str,
        character_id: str,
        stage: str,
        decision: str,
        reason_code: str = "",
        detail: str = "",
        run_id: str = "",
        character_version: str = "",
        actor: str = "system",
        severity: str = "info",
    ) -> str:
        event_id = f"gov_{uuid.uuid4().hex[:16]}"
        row = [
            event_id,
            trace_id or "system",
            run_id or "",
            character_id,
            character_version or "",
            stage,
            decision,
            reason_code or "",
            (detail or "")[:4000],
            actor,
            severity,
            datetime.now(timezone.utc),
        ]
        self._insert("governance_events", GOVERNANCE_COLUMNS, [row])
        return event_id

    def record_governance_events(self, events: List[Dict[str, Any]]) -> int:
        """Batch variant for a full production run's decisions."""
        rows = []
        now = datetime.now(timezone.utc)
        for e in events:
            rows.append([
                f"gov_{uuid.uuid4().hex[:16]}",
                e.get("trace_id", "system"),
                e.get("run_id", ""),
                e.get("character_id", "maya"),
                e.get("character_version", ""),
                e.get("stage", "unknown"),
                e.get("decision", "PASS"),
                e.get("reason_code", ""),
                str(e.get("detail", ""))[:4000],
                e.get("actor", "system"),
                e.get("severity", "info"),
                now,
            ])
        return len(rows) if self._insert("governance_events", GOVERNANCE_COLUMNS, rows) else 0


ledger = ClickHouseLedger()
