from typing import Dict, List, Set
from backend.app.models.mcp import MCPToolInvocation
from backend.app.logging import app_logger

# ---------------------------------------------------------------------------
# MCP TOOL PERMISSION MATRIX (Section 11)
# ---------------------------------------------------------------------------

AGENT_MCP_ALLOWLIST: Dict[str, Set[str]] = {
    "evolution_agent": {
        "query_scene_performance",
        "get_strategy_performance",
        "compare_strategy_versions",
        "get_recent_production_metrics",
        "get_claim_verification_metrics"
    },
    "director_agent": {
        "query_scene_performance"
    },
    "research_agent": {
        "get_claim_verification_metrics"
    },
    "script_agent": set(),
    "critic_agent": set(),
    "guardian_agent": set(),
    "live_session": set(),  # Live Mode is strictly prohibited from analytics tools
    "live_agent": set()
}

# Explicitly prohibited operations (even if an MCP server were to advertise them)
PROHIBITED_OPERATIONS: Set[str] = {
    "drop_table",
    "delete_records",
    "alter_table",
    "execute_raw_sql",
    "insert_events",
    "system_command",
    "filesystem_access",
    "modify_dna",
    "publish_content"
}

class MCPToolPermissionPolicy:
    """
    Centralized security policy enforcing fine-grained agent authorization for MCP partner tools.
    Prevents unauthorized tool execution, SQL injection, and Live Mode permission creep.
    """
    @classmethod
    def is_authorized(cls, agent_identity: str, tool_name: str) -> bool:
        # 1. Prohibited operations are universally rejected
        if tool_name.lower() in PROHIBITED_OPERATIONS:
            return False

        # 2. Check agent-specific allowlist
        allowed_tools = AGENT_MCP_ALLOWLIST.get(agent_identity.lower(), set())
        return tool_name in allowed_tools

    @classmethod
    def get_allowed_tools_for_agent(cls, agent_identity: str) -> List[str]:
        return sorted(list(AGENT_MCP_ALLOWLIST.get(agent_identity.lower(), set())))

    @classmethod
    def enforce_authorization(cls, invocation: MCPToolInvocation) -> None:
        """
        Validates authorization for an MCP invocation, raising PermissionError on violation.
        """
        if not cls.is_authorized(invocation.agent_identity, invocation.tool_name):
            app_logger.log_operation(
                trace_id=invocation.trace_id,
                operation="mcp_permission_denied",
                status="UNAUTHORIZED",
                agent_task=invocation.agent_identity,
                details={
                    "tool_name": invocation.tool_name,
                    "agent_identity": invocation.agent_identity,
                    "allowed_tools": list(AGENT_MCP_ALLOWLIST.get(invocation.agent_identity, set()))
                }
            )
            raise PermissionError(
                f"MCP Security Violation: Agent '{invocation.agent_identity}' is not authorized to invoke MCP tool '{invocation.tool_name}'."
            )
