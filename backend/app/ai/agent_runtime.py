from typing import Type, TypeVar, List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from backend.app.ai.provider import BaseAIProvider, get_ai_provider
from backend.app.ai.tools import execute_tool, AGENT_TOOL_ALLOWLISTS
from backend.app.models.a2a import A2AMessage
from backend.app.logging import app_logger

T = TypeVar("T", bound=BaseModel)

class ADKAgent:
    """
    Google ADK-compatible In-Process Agent Runtime for AVATAROS.
    Binds Agent Role, System Instruction, Allowed Tool Capabilities, and Structured Output Schema.
    """
    def __init__(
        self,
        agent_name: str,
        system_instruction: str,
        allowed_tools: Optional[List[str]] = None,
        provider: Optional[BaseAIProvider] = None
    ):
        self.agent_name = agent_name
        self.system_instruction = system_instruction
        self.allowed_tools = allowed_tools or AGENT_TOOL_ALLOWLISTS.get(agent_name, [])
        self.provider = provider or get_ai_provider()

    def run_structured(
        self,
        prompt: str,
        response_model: Type[T],
        trace_id: str = "system"
    ) -> T:
        """
        Executes agent reasoning with structured output validation.
        """
        app_logger.log_operation(
            trace_id=trace_id,
            operation="adk_agent_start",
            status="RUNNING",
            agent_task=self.agent_name,
            details={"prompt_len": len(prompt), "target_schema": response_model.__name__}
        )

        result = self.provider.generate_structured(
            prompt=prompt,
            response_model=response_model,
            system_instruction=self.system_instruction,
            trace_id=trace_id
        )

        app_logger.log_operation(
            trace_id=trace_id,
            operation="adk_agent_complete",
            status="SUCCESS",
            agent_task=self.agent_name,
            details={"target_schema": response_model.__name__}
        )

        return result

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        trace_id: str = "system"
    ) -> Any:
        """
        Invokes an authorized deterministic tool within the agent's explicit allowlist.
        """
        return execute_tool(
            agent_name=self.agent_name,
            tool_name=tool_name,
            arguments=arguments,
            trace_id=trace_id
        )

    def create_a2a_envelope(
        self,
        to_agent: str,
        task: str,
        payload: Dict[str, Any],
        trace_id: str
    ) -> A2AMessage:
        """
        Creates an A2A envelope for typed inter-agent handoffs.
        """
        return A2AMessage(
            from_agent=self.agent_name,
            to_agent=to_agent,
            task=task,
            payload=payload,
            trace_id=trace_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
