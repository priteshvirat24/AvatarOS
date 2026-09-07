from typing import Optional
from backend.app.models.script import Script
from backend.app.models.director import DirectorPlan, SceneShot, CutawaySpec
from backend.app.models.events import ProductionStrategy
from backend.app.ai.adk_runtime import ADKAgent
from backend.app.ai.prompts.director import DIRECTOR_SYSTEM_PROMPT, DIRECTOR_USER_PROMPT
from backend.app.logging import app_logger

class DirectorAgent:
    """
    Director Agent (Section 11, Milestone 4)
    Converts approved script into production plan via Gemini structured planning.
    Directly incorporates Evolution Agent's learned strategy from ClickHouse telemetry.
    """
    def __init__(self, adk_agent: Optional[ADKAgent] = None):
        self.adk_agent = adk_agent or ADKAgent(
            agent_name="director_agent",
            system_instruction=DIRECTOR_SYSTEM_PROMPT,
            allowed_tools=["get_character_dna", "get_active_strategy"]
        )

    def plan_production(
        self,
        script: Script,
        campaign_name: str,
        target_audience: str = "Indian Developers",
        strategy: Optional[ProductionStrategy] = None,
        trace_id: str = "system"
    ) -> DirectorPlan:
        # Ingest strategy parameters
        strat_ver = strategy.strategy_version if strategy else 13
        strat_cite = strategy.evidence.source_query_id if strategy else "ch_query_base"
        hook_type = strategy.hook_type if strategy else "statement"
        opening_dur = 6.8 if hook_type == "question" else 9.2
        hook_shot = strategy.shot_preference if strategy else "medium_shot"
        hook_energy = strategy.energy_bias if strategy else 0.55

        system_instruction = DIRECTOR_SYSTEM_PROMPT.format(
            hook_type=hook_type,
            opening_duration_s=opening_dur,
            shot_preference=hook_shot,
            energy_bias=hook_energy
        )

        prompt = DIRECTOR_USER_PROMPT.format(
            campaign_name=campaign_name,
            character_id="maya",
            script_json=script.model_dump_json(indent=2),
            strategy_version=strat_ver,
            hook_type=hook_type,
            opening_duration_s=opening_dur,
            shot_preference=hook_shot,
            energy_bias=hook_energy,
            strategy_citation=strat_cite,
            target_audience=target_audience
        )

        # 1. Gemini structured generation via ADK
        agent = ADKAgent(
            agent_name="director_agent",
            system_instruction=system_instruction,
            allowed_tools=["get_character_dna", "get_active_strategy"]
        )
        plan: DirectorPlan = agent.run_structured(
            prompt=prompt,
            response_model=DirectorPlan,
            trace_id=trace_id
        )

        # 2. Deterministic Strategy Enforcement Overlay
        plan.strategy_version = strat_ver
        plan.strategy_citation = strat_cite
        plan.hook_type = hook_type  # type: ignore
        plan.opening_duration_s = opening_dur

        if plan.shots:
            plan.shots[0].duration_s = opening_dur
            plan.shots[0].shot = hook_shot  # type: ignore
            plan.shots[0].hook_type = hook_type  # type: ignore
            plan.shots[0].emotional_intensity = hook_energy

        app_logger.log_operation(
            trace_id=trace_id,
            operation="director_plan_created",
            status="SUCCESS",
            agent_task="director_agent",
            details={
                "plan_id": plan.plan_id,
                "strategy_version": strat_ver,
                "hook_type": hook_type,
                "shots_count": len(plan.shots)
            }
        )

        return plan
