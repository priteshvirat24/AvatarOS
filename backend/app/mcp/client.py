"""
MCP client and governance gateway.

This is the only door between an AVATAROS agent and the ClickHouse partner server.
It does four things, in order, for every call:

1. Enforces the per-agent tool allowlist (Live Mode, for instance, can never reach
   analytics - the gateway will not compile a template on its behalf).
2. Confirms the tool is registered.
3. Executes it on the adapter, measuring wall-clock latency.
4. Appends the outcome - authorized or refused, successful or failed - to the
   `mcp_tool_calls` ledger in ClickHouse.

Step 4 is what makes the integration auditable: the trace panel reads that ledger
back through the same MCP server, so the evidence of partner usage is produced by
partner usage.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.config import settings
from backend.app.logging import app_logger
from backend.app.mcp.adapters import (
    BaseMCPAdapter,
    ClickHouseMCPAdapter,
    DeterministicMCPAdapter,
)
from backend.app.mcp.ledger import ledger
from backend.app.mcp.permission import MCPToolPermissionPolicy
from backend.app.mcp.registry import MCPToolRegistry, mcp_tool_registry
from backend.app.models.mcp import MCPToolDefinition, MCPToolInvocation, MCPToolResult


class MCPClient:
    """Authoritative boundary for agent partner-tool execution."""

    def __init__(self, adapter: Optional[BaseMCPAdapter] = None):
        self._adapter: Optional[BaseMCPAdapter] = adapter
        self._explicit_adapter = adapter is not None
        self.registry: MCPToolRegistry = mcp_tool_registry
        self._init_lock = threading.Lock()
        self._initialized = False

        # Tools are registered eagerly (cheap, no I/O) so `/api/mcp/tools` answers
        # before the server subprocess has been spawned. The transport itself is
        # connected lazily on first use, which keeps import and test collection fast.
        self.registry.register_tools(self._resolve_adapter().list_tools())

    # ---------------------------------------------------------------- adapter

    def _resolve_adapter(self) -> BaseMCPAdapter:
        if self._adapter is None:
            if settings.MCP_PROVIDER == "clickhouse_mcp":
                self._adapter = ClickHouseMCPAdapter()
            else:
                self._adapter = DeterministicMCPAdapter()
        return self._adapter

    @property
    def adapter(self) -> BaseMCPAdapter:
        return self._resolve_adapter()

    def ensure_initialized(self) -> bool:
        """Connects the transport on first use. Safe to call repeatedly."""
        if self._initialized:
            return True
        with self._init_lock:
            if self._initialized:
                return True
            ok = self.adapter.initialize()
            self.registry.register_tools(self.adapter.list_tools())
            self._initialized = ok
            return ok

    def reset_adapter(self) -> None:
        """Rebuilds the adapter from current settings (used by tests)."""
        if self._explicit_adapter:
            return
        with self._init_lock:
            self._adapter = None
            self._initialized = False
        self.registry.register_tools(self._resolve_adapter().list_tools())

    # ----------------------------------------------------------------- status

    def get_status(self) -> Dict[str, Any]:
        adapter_status = self.adapter.get_status()
        return {
            "enabled": settings.MCP_ENABLED,
            "provider": adapter_status.get("provider", "deterministic"),
            "server_url": adapter_status.get("server_url", "in_process"),
            "server_identity": adapter_status.get("server_identity", "unknown"),
            "ready": adapter_status.get("ready", True),
            "handshake_ok": adapter_status.get("handshake_ok", adapter_status.get("ready", True)),
            "transport": adapter_status.get("transport", settings.MCP_TRANSPORT),
            "is_simulated": adapter_status.get("is_simulated", True),
            "read_only": adapter_status.get("read_only", True),
            "server_tools": adapter_status.get("server_tools", []),
            "query_tool": adapter_status.get("query_tool"),
            "database": adapter_status.get("database"),
            "last_error": adapter_status.get("last_error"),
            "configured": True,
            "tools_count": len(self.registry.list_tools()),
            "ledger": ledger.status(),
        }

    def list_tools(self, agent_identity: Optional[str] = None) -> List[MCPToolDefinition]:
        all_tools = self.registry.list_tools()
        if not agent_identity:
            return all_tools
        allowed = MCPToolPermissionPolicy.get_allowed_tools_for_agent(agent_identity)
        return [t for t in all_tools if t.name in allowed]

    # ------------------------------------------------------------------ calls

    def call_tool(
        self,
        agent_identity: str,
        tool_name: str,
        arguments: Dict[str, Any],
        trace_id: str = "system",
        session_id: Optional[str] = None,
    ) -> MCPToolResult:
        """Executes an authorized MCP tool on behalf of an agent."""
        if not settings.MCP_ENABLED:
            raise RuntimeError("MCP is currently disabled in system configuration.")

        invocation = MCPToolInvocation(
            tool_name=tool_name,
            agent_identity=agent_identity,
            trace_id=trace_id,
            session_id=session_id,
            arguments=arguments,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        status_snapshot = self.adapter.get_status()
        server_identity = status_snapshot.get("server_identity", "unknown")
        transport = status_snapshot.get("transport", settings.MCP_TRANSPORT)
        is_simulated = bool(status_snapshot.get("is_simulated", True))
        args_json = _safe_json(arguments)

        # 1. Authorization boundary --------------------------------------------
        try:
            MCPToolPermissionPolicy.enforce_authorization(invocation)
        except PermissionError as pe:
            call_id = ledger.record_mcp_call(
                trace_id=trace_id,
                agent_identity=agent_identity,
                tool_name=tool_name,
                status="UNAUTHORIZED",
                authorized=False,
                latency_ms=0.0,
                server_identity=server_identity,
                transport=transport,
                arguments=args_json,
                error=str(pe),
                session_id=session_id or "",
            )
            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="UNAUTHORIZED",
                error=str(pe),
                server_identity=server_identity,
                transport=transport,
                is_simulated=is_simulated,
                call_id=call_id,
            )

        # 2. Registration -------------------------------------------------------
        if not self.registry.has_tool(tool_name):
            call_id = ledger.record_mcp_call(
                trace_id=trace_id,
                agent_identity=agent_identity,
                tool_name=tool_name,
                status="ERROR",
                authorized=True,
                latency_ms=0.0,
                server_identity=server_identity,
                transport=transport,
                arguments=args_json,
                error="tool not registered",
                session_id=session_id or "",
            )
            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="ERROR",
                error=f"MCP Tool '{tool_name}' not found in registry.",
                server_identity=server_identity,
                transport=transport,
                is_simulated=is_simulated,
                call_id=call_id,
            )

        self.ensure_initialized()

        app_logger.log_operation(
            trace_id=trace_id,
            operation="mcp_tool_invocation_start",
            status="INVOKED",
            agent_task=agent_identity,
            details={
                "tool_name": tool_name,
                "agent_identity": agent_identity,
                "server_provider": status_snapshot.get("provider"),
            },
        )

        # 3. Execute ------------------------------------------------------------
        start_time = time.perf_counter()
        try:
            data = self.adapter.execute(invocation)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            evidence = self.adapter.last_call_evidence()
            compiled_sql = str(data.get("sql") or evidence.get("compiled_sql") or "")
            rows_returned = int(data.get("row_count", evidence.get("rows_returned", 0)) or 0)

            app_logger.log_operation(
                trace_id=trace_id,
                operation="mcp_tool_invocation_success",
                status="SUCCESS",
                agent_task=agent_identity,
                details={
                    "tool_name": tool_name,
                    "latency_ms": elapsed_ms,
                    "rows_returned": rows_returned,
                    "server_provider": status_snapshot.get("provider"),
                },
            )

            call_id = ledger.record_mcp_call(
                trace_id=trace_id,
                agent_identity=agent_identity,
                tool_name=tool_name,
                status="SUCCESS",
                authorized=True,
                latency_ms=elapsed_ms,
                server_identity=server_identity,
                transport=transport,
                arguments=args_json,
                compiled_sql=compiled_sql,
                rows_returned=rows_returned,
                session_id=session_id or "",
            )

            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="SUCCESS",
                data=data,
                latency_ms=elapsed_ms,
                server_identity=server_identity,
                transport=transport,
                is_simulated=is_simulated,
                compiled_sql=compiled_sql,
                rows_returned=rows_returned,
                call_id=call_id,
            )

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            evidence = self.adapter.last_call_evidence()
            app_logger.log_operation(
                trace_id=trace_id,
                operation="mcp_tool_invocation_failure",
                status="ERROR",
                agent_task=agent_identity,
                details={"tool_name": tool_name, "error": str(e), "latency_ms": elapsed_ms},
            )
            call_id = ledger.record_mcp_call(
                trace_id=trace_id,
                agent_identity=agent_identity,
                tool_name=tool_name,
                status="ERROR",
                authorized=True,
                latency_ms=elapsed_ms,
                server_identity=server_identity,
                transport=transport,
                arguments=args_json,
                compiled_sql=str(evidence.get("compiled_sql") or ""),
                error=str(e),
                session_id=session_id or "",
            )
            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="ERROR",
                error=f"MCP tool execution failed: {e}",
                latency_ms=elapsed_ms,
                server_identity=server_identity,
                transport=transport,
                is_simulated=is_simulated,
                compiled_sql=str(evidence.get("compiled_sql") or ""),
                call_id=call_id,
            )


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, default=str)
    except Exception:
        return "{}"


mcp_client = MCPClient()
