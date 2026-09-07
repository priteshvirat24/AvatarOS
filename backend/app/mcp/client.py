import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.logging import app_logger
from backend.app.models.mcp import (
    MCPToolDefinition,
    MCPToolInvocation,
    MCPToolResult
)
from backend.app.mcp.adapters import BaseMCPAdapter, ClickHouseMCPAdapter, DeterministicMCPAdapter
from backend.app.mcp.permission import MCPToolPermissionPolicy
from backend.app.mcp.registry import mcp_tool_registry, MCPToolRegistry

class MCPClient:
    """
    Model Context Protocol (MCP) Client & Governance Gateway.
    Authoritative boundary for agent partner tool execution:
    - Enforces fine-grained agent authorization policy (no unauthorized analytics access).
    - Prohibits destructive operations (no DROP/DELETE/INSERT/arbitrary SQL).
    - Dispatches typed invocations to ClickHouse MCP or Deterministic test adapter.
    - Measures execution latency and emits structured telemetry.
    """
    def __init__(self, adapter: Optional[BaseMCPAdapter] = None):
        self.adapter: BaseMCPAdapter = adapter or self._resolve_adapter()
        self.registry: MCPToolRegistry = mcp_tool_registry
        self._initialize()

    def _resolve_adapter(self) -> BaseMCPAdapter:
        if settings.MCP_PROVIDER == "clickhouse_mcp":
            return ClickHouseMCPAdapter()
        return DeterministicMCPAdapter()

    def _initialize(self) -> None:
        self.adapter.initialize()
        tools = self.adapter.list_tools()
        self.registry.register_tools(tools)

    def get_status(self) -> Dict[str, Any]:
        adapter_status = self.adapter.get_status()
        return {
            "enabled": settings.MCP_ENABLED,
            "provider": adapter_status.get("provider", "deterministic"),
            "server_url": adapter_status.get("server_url", "in_process"),
            "ready": adapter_status.get("ready", True),
            "transport": settings.MCP_TRANSPORT,
            "configured": True,
            "tools_count": len(self.registry.list_tools())
        }

    def list_tools(self, agent_identity: Optional[str] = None) -> List[MCPToolDefinition]:
        all_tools = self.registry.list_tools()
        if not agent_identity:
            return all_tools
        allowed = MCPToolPermissionPolicy.get_allowed_tools_for_agent(agent_identity)
        return [t for t in all_tools if t.name in allowed]

    def call_tool(
        self,
        agent_identity: str,
        tool_name: str,
        arguments: Dict[str, Any],
        trace_id: str = "system",
        session_id: Optional[str] = None
    ) -> MCPToolResult:
        """
        Executes an authorized MCP tool on behalf of an agent.
        """
        if not settings.MCP_ENABLED:
            raise RuntimeError("MCP is currently disabled in system configuration.")

        invocation = MCPToolInvocation(
            tool_name=tool_name,
            agent_identity=agent_identity,
            trace_id=trace_id,
            session_id=session_id,
            arguments=arguments,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        # 1. Enforce Authorization Boundary
        try:
            MCPToolPermissionPolicy.enforce_authorization(invocation)
        except PermissionError as pe:
            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="UNAUTHORIZED",
                error=str(pe),
                server_identity=self.adapter.get_status().get("provider", "unknown")
            )

        # 2. Check Tool Registration
        if not self.registry.has_tool(tool_name):
            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="ERROR",
                error=f"MCP Tool '{tool_name}' not found in registry.",
                server_identity=self.adapter.get_status().get("provider", "unknown")
            )

        # 3. Log Call Initiation
        app_logger.log_operation(
            trace_id=trace_id,
            operation="mcp_tool_invocation_start",
            status="INVOKED",
            agent_task=agent_identity,
            details={
                "tool_name": tool_name,
                "agent_identity": agent_identity,
                "server_provider": self.adapter.get_status().get("provider")
            }
        )

        # 4. Execute on Adapter with Latency Measurement
        start_time = time.time()
        try:
            data = self.adapter.execute(invocation)
            elapsed_ms = (time.time() - start_time) * 1000

            app_logger.log_operation(
                trace_id=trace_id,
                operation="mcp_tool_invocation_success",
                status="SUCCESS",
                agent_task=agent_identity,
                details={
                    "tool_name": tool_name,
                    "latency_ms": round(elapsed_ms, 2),
                    "server_provider": self.adapter.get_status().get("provider")
                }
            )

            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="SUCCESS",
                data=data,
                latency_ms=round(elapsed_ms, 2),
                server_identity=self.adapter.get_status().get("provider", "clickhouse_mcp")
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            app_logger.log_operation(
                trace_id=trace_id,
                operation="mcp_tool_invocation_failure",
                status="ERROR",
                agent_task=agent_identity,
                details={
                    "tool_name": tool_name,
                    "error": str(e),
                    "latency_ms": round(elapsed_ms, 2)
                }
            )
            return MCPToolResult(
                tool_name=tool_name,
                agent_identity=agent_identity,
                trace_id=trace_id,
                status="ERROR",
                error=f"MCP tool execution failed: {str(e)}",
                latency_ms=round(elapsed_ms, 2),
                server_identity=self.adapter.get_status().get("provider", "clickhouse_mcp")
            )

mcp_client = MCPClient()
