from typing import Dict, Any, List, Optional, Callable
from backend.app.knowledge.knowledge_base import knowledge_base
from backend.app.data.telemetry_store import telemetry_store
from backend.app.logging import app_logger

# ---------------------------------------------------------------------------
# DETERMINISTIC AGENT TOOLS
# ---------------------------------------------------------------------------

def tool_search_knowledge(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    Searches the grounded AVATAROS document knowledge base using hybrid vector + BM25 retrieval.
    Returns ranked documentary evidence chunks with page, section, and cryptographic hash provenance.
    """
    hits = knowledge_base.search(query=query, top_k=top_k, trace_id="adk_tool")
    results = []
    for h in hits:
        results.append({
            "doc_id": h.chunk.doc_id,
            "chunk_id": h.chunk.chunk_id,
            "section": h.chunk.section,
            "page": h.chunk.page or 1,
            "text": h.chunk.text,
            "doc_checksum": knowledge_base.documents.get(h.chunk.doc_id).content_hash if h.chunk.doc_id in knowledge_base.documents else "hash_unknown",
            "chunk_checksum": h.chunk.content_hash,
            "hybrid_score": round(h.hybrid_score, 4),
            "retrieval_methods": h.retrieval_methods
        })
    return results


def tool_verify_claim(claim_text: str, claim_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Deterministically evaluates factual entailment for a proposed claim assertion against grounded knowledge base.
    CRITICAL SAFETY RULE: High retrieval score != factual verification.
    Confidence < 0.60 -> strictly BLOCKED.
    """
    from backend.app.agents.research import ResearchAgent
    verifier = ResearchAgent()
    claim_res = verifier.verify_claim(claim_text=claim_text, claim_id=claim_id)
    return claim_res.model_dump()


def tool_get_character_dna(character_id: str = "maya") -> Dict[str, Any]:
    """
    Retrieves the sealed Digital DNA specification for a digital human character.
    Includes identity thresholds, voice timbre, speech pacing, emotional constraints, and behavioral boundaries.
    """
    from backend.app.agents.orchestrator import orchestrator
    dna = orchestrator.characters.get(character_id.lower())
    if not dna:
        dna = orchestrator.characters.get("maya")
    return dna.model_dump() if dna else {}


def tool_get_rights(character_id: str = "maya") -> Dict[str, Any]:
    """
    Retrieves the legal likeness license and commercial usage rights record for a character.
    """
    from backend.app.agents.orchestrator import orchestrator
    rec = orchestrator.rights.get(character_id.lower())
    if not rec:
        rec = orchestrator.rights.get("maya")
    return rec.model_dump() if rec else {}


def tool_get_active_strategy(character_id: str = "maya") -> Dict[str, Any]:
    """
    Retrieves the current production strategy learned by the Evolution Agent from ClickHouse telemetry.
    Includes hook_type, opening_duration, shot_preference, and energy_bias.
    """
    strat = telemetry_store.active_strategy
    return strat.model_dump() if strat else {}


def tool_get_strategy_performance(character_id: str = "maya", region: str = "IN") -> Dict[str, Any]:
    """
    Queries ClickHouse columnar telemetry using Query 881a for audience retention distributions.
    """
    return telemetry_store.run_query_881a(avatar_id=character_id, region=region)


def tool_compare_strategy_versions(character_id: str = "maya", strategy_a: int = 13, strategy_b: int = 14, metric: str = "avg_retention") -> Dict[str, Any]:
    """
    Compares audience retention lift and confidence intervals between two strategy versions.
    """
    from backend.app.mcp.client import mcp_client
    res = mcp_client.call_tool("evolution_agent", "compare_strategy_versions", {
        "character_id": character_id,
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "metric": metric
    })
    return res.data or {}


def tool_query_scene_performance(character_id: str = "maya", scene_no: Optional[int] = 1, min_sample: int = 50) -> Dict[str, Any]:
    """
    Queries scene-level completion and audience retention metrics from ClickHouse.
    """
    from backend.app.mcp.client import mcp_client
    res = mcp_client.call_tool("evolution_agent", "query_scene_performance", {
        "character_id": character_id,
        "scene_no": scene_no,
        "min_sample": min_sample
    })
    return res.data or {}


# ---------------------------------------------------------------------------
# TOOL REGISTRY & PER-AGENT PERMISSIONS (ALLOWLISTS)
# ---------------------------------------------------------------------------

TOOL_REGISTRY: Dict[str, Callable] = {
    "search_knowledge": tool_search_knowledge,
    "verify_claim": tool_verify_claim,
    "get_character_dna": tool_get_character_dna,
    "get_rights": tool_get_rights,
    "get_active_strategy": tool_get_active_strategy,
    "get_strategy_performance": tool_get_strategy_performance,
    "compare_strategy_versions": tool_compare_strategy_versions,
    "query_scene_performance": tool_query_scene_performance,
}

# Strict security boundary: Agents only have access to explicit allowlisted tools
AGENT_TOOL_ALLOWLISTS: Dict[str, List[str]] = {
    "research_agent": ["search_knowledge", "verify_claim", "get_character_dna"],
    "script_agent": ["get_character_dna", "get_rights", "get_active_strategy"],
    "critic_agent": ["get_character_dna", "get_rights", "get_active_strategy"],
    "director_agent": ["get_character_dna", "get_active_strategy", "query_scene_performance"],
    "evolution_agent": [
        "get_strategy_performance",
        "get_active_strategy",
        "compare_strategy_versions",
        "query_scene_performance"
    ],
}


def execute_tool(agent_name: str, tool_name: str, arguments: Dict[str, Any], trace_id: str = "system") -> Any:
    """
    Executes a deterministic tool on behalf of an agent after verifying explicit permission allowlist.
    """
    allowlist = AGENT_TOOL_ALLOWLISTS.get(agent_name, [])
    if tool_name not in allowlist:
        app_logger.log_operation(
            trace_id=trace_id,
            operation="tool_permission_denied",
            status="SECURITY_VIOLATION",
            agent_task=agent_name,
            details={"tool_name": tool_name, "allowed_tools": allowlist}
        )
        raise PermissionError(f"Security Violation: Agent '{agent_name}' is not authorized to invoke tool '{tool_name}'.")

    tool_func = TOOL_REGISTRY.get(tool_name)
    if not tool_func:
        raise KeyError(f"Tool '{tool_name}' not found in registry.")

    app_logger.log_operation(
        trace_id=trace_id,
        operation="tool_call_start",
        status="INVOKED",
        agent_task=agent_name,
        details={"tool_name": tool_name, "arguments": {k: str(v)[:60] for k, v in arguments.items()}}
    )

    result = tool_func(**arguments)

    app_logger.log_operation(
        trace_id=trace_id,
        operation="tool_call_complete",
        status="SUCCESS",
        agent_task=agent_name,
        details={"tool_name": tool_name}
    )

    return result
