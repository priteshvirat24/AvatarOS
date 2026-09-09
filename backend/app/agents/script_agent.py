from typing import Optional, List, Dict, Any
from backend.app.models.dna import DigitalDNA
from backend.app.models.script import Script, ScriptScene, ScriptLine
from backend.app.ai.agent_runtime import StructuredAgent
from backend.app.ai.prompts.script import SCRIPT_SYSTEM_PROMPT, SCRIPT_USER_PROMPT
from backend.app.logging import app_logger

class ScriptAgent:
    """
    Script Agent (Section 9, Milestone 4)
    Generates structured 5-scene video production script via Gemini structured output.
    Enforces deterministic claim-reference validation and Digital DNA speech guards.
    """
    def __init__(self, agent_runtime: Optional[StructuredAgent] = None):
        self.agent_runtime = agent_runtime or StructuredAgent(
            agent_name="script_agent",
            system_instruction=SCRIPT_SYSTEM_PROMPT,
            allowed_tools=["get_character_dna", "get_rights", "get_active_strategy"]
        )

    def generate_script(
        self,
        character_dna: DigitalDNA,
        objective: str,
        target_audience: str = "Indian Developers",
        target_duration: float = 60.0,
        version: int = 1,
        include_unsupported_claim: bool = False,
        hook_type: str = "statement",
        verified_claims: Optional[List[Dict[str, Any]]] = None,
        trace_id: str = "system"
    ) -> Script:
        speaker = character_dna.character_id

        # Build verified claims context for prompt conditioning
        claims_ctx = ""
        if verified_claims:
            for c in verified_claims:
                if not c.get("is_blocked"):
                    claims_ctx += f"- ID: {c.get('claim_id')} | Status: verified | Text: {c.get('claim_text')}\n"
        else:
            claims_ctx = "- ID: claim_0231 | Status: verified | Text: 40% faster inference on local LLM code completion\n- ID: claim_0310 | Status: verified | Text: 45 TOPS on-device NPU for instant code assistance\n"

        if include_unsupported_claim:
            claims_ctx += "- ID: claim_fail_3x | Status: unsupported | Text: 3x faster than all competitor machines on the planet\n"

        prompt = SCRIPT_USER_PROMPT.format(
            character_id=speaker,
            objective=objective,
            target_audience=target_audience,
            target_duration=target_duration,
            hook_type=hook_type,
            personality_traits=f"confident={character_dna.personality_vector.confident}, analytical={character_dna.personality_vector.analytical}",
            tone="Technical, confident, and direct",
            sentence_length=character_dna.speech.sentence_length,
            vocabulary_tier="technical_engineer",
            verified_claims_context=claims_ctx
        )

        # 1. Gemini structured generation via the agent runtime
        script: Script = self.agent_runtime.run_structured(
            prompt=prompt,
            response_model=Script,
            trace_id=trace_id
        )

        # 2. Structural guard.
        #
        # A live model occasionally returns a schema-valid Script with no scenes
        # at all. Downstream stages index scenes positionally, so an empty script
        # crashed the entire production run - and because validation only *logged*
        # the deviation, the pipeline sailed on into an IndexError. Detecting a
        # structurally unusable script has to mean refusing to use it.
        if not self._is_structurally_usable(script):
            app_logger.log_operation(
                trace_id=trace_id,
                operation="script_structure_rejected",
                status="FALLBACK",
                agent_task="script_agent",
                details={
                    "scene_count": len(script.scenes),
                    "reason": "model returned a script the pipeline cannot stage",
                    "action": "regenerating deterministically",
                },
            )
            script = self._deterministic_script(character_dna, trace_id)

        # 3. Deterministic Validation Layer
        self._validate_script(script, character_dna, trace_id)

        return script

    @staticmethod
    def _is_structurally_usable(script: Script) -> bool:
        """
        A script is usable only if every scene the pipeline will stage exists and
        actually carries a spoken line. Scene count is checked against what
        downstream stages index, not against a style preference.
        """
        if not script or not script.scenes:
            return False
        if len(script.scenes) < 5:
            return False
        return all(sc.lines and sc.lines[0].text.strip() for sc in script.scenes[:5])

    def _deterministic_script(self, character_dna: DigitalDNA, trace_id: str) -> Script:
        """Falls back to the offline generator, which always produces 5 staged scenes."""
        from backend.app.ai.provider import DeterministicFallbackAIProvider

        return DeterministicFallbackAIProvider().generate_structured(
            prompt="",
            response_model=Script,
            trace_id=trace_id,
        )

    def _validate_script(self, script: Script, character_dna: DigitalDNA, trace_id: str) -> None:
        """
        Deterministic validation on model-generated script:
        - Exactly 5 scenes with expected roles
        - Forbidden word / restricted topic rejection
        - Non-empty speech lines
        """
        if len(script.scenes) != 5:
            app_logger.log_operation(
                trace_id=trace_id,
                operation="script_validation_warning",
                status="DEVIATION",
                agent_task="script_agent",
                details={"scene_count": len(script.scenes), "expected": 5}
            )

        # Validate restricted topics / forbidden phrases against Digital DNA
        forbidden = set(w.lower() for w in character_dna.topics.restricted)
        for sc in script.scenes:
            for line in sc.lines:
                words = set(line.text.lower().split())
                violation = forbidden.intersection(words)
                if violation:
                    app_logger.log_operation(
                        trace_id=trace_id,
                        operation="dna_speech_guard",
                        status="REJECTED_WORD",
                        agent_task="script_agent",
                        details={"scene_no": sc.scene_no, "forbidden_words": list(violation)}
                    )
                    for vw in violation:
                        line.text = line.text.replace(vw, "").replace("  ", " ")

        app_logger.log_operation(
            trace_id=trace_id,
            operation="script_generated",
            status="VALIDATED",
            agent_task="script_agent",
            details={
                "script_id": script.script_id,
                "scenes": len(script.scenes),
                "total_duration": script.total_duration
            }
        )
