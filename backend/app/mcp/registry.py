from typing import Dict, List, Optional
from backend.app.models.mcp import MCPToolDefinition

class MCPToolRegistry:
    """
    Central registry of governed Model Context Protocol (MCP) partner tools.
    """
    def __init__(self):
        self._tools: Dict[str, MCPToolDefinition] = {}

    def register_tool(self, tool_def: MCPToolDefinition) -> None:
        self._tools[tool_def.name] = tool_def

    def register_tools(self, tool_defs: List[MCPToolDefinition]) -> None:
        for t in tool_defs:
            self.register_tool(t)

    def get_tool(self, name: str) -> Optional[MCPToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[MCPToolDefinition]:
        return list(self._tools.values())

    def has_tool(self, name: str) -> bool:
        return name in self._tools

mcp_tool_registry = MCPToolRegistry()
