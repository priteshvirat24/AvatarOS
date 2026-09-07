import json
from typing import List, Optional, Dict, Any
from backend.app.models.dna import DigitalDNA
from backend.app.models.script import Script, CriticReport, CriticIssue
from backend.app.data.documents import SEED_CLAIMS
from backend.app.ai.adk_runtime import ADKAgent
from backend.app.ai.prompts.critic import CRITIC_SYSTEM_PROMPT, CRITIC_USER_PROMPT
from backend.app.logging import app_logger

class CriticAgent:
    """
    Adversarial Script Critic Agent (Section 10, Milestone 4)
    Performs Gemini-assisted adversarial critique with deterministic safety verification overlay.
    Enforces bounded revision loop (max 3 rounds).
    """
    def __init__(self, adk_agent: Optional[ADKAgent] = None):
        self.adk_agent = adk_agent or ADKAgent(
            agent_name="critic_agent",
            system_instruction=CRITIC_SYSTEM_PROMPT,
            allowed_tools=["get_character_dna", "get_rights", "get_active_strategy"]
        )

    def review_script(
        self,
        script: Script,
        character_dna: DigitalDNA,
        round_number: int = 1,
        claims_registry: Optional[List[Dict[str, Any]]] = None,
        trace_id: str = "system"
    ) -> CriticReport:
        from backend.app.agents.orchestrator import orchestrator
        live_claims = orchestrator.research_agent.claims if (hasattr(orchestrator, 'research_agent') and hasattr(orchestrator.research_agent, 'claims')) else SEED_CLAIMS

        claims_json = json.dumps([c.model_dump() for c in live_claims.values()], indent=2)
        script_json = script.model_dump_json(indent=2)

        prompt = CRITIC_USER_PROMPT.format(
            character_id=character_dna.character_id,
            round_number=round_number,
            script_json=script_json,
            sentence_length=character_dna.speech.sentence_length,
            tone="Technical, confident, and direct",
            claims_status_json=claims_json
        )

        # 1. Gemini adversarial reasoning via ADK
        report: CriticReport = self.adk_agent.run_structured(
            prompt=prompt,
            response_model=CriticReport,
            trace_id=trace_id
        )

        # 2. Deterministic Safety Verification Overlay
        self._enforce_deterministic_safety(report, script, character_dna, live_claims, round_number, trace_id)

        return report

    def _enforce_deterministic_safety(
        self,
        report: CriticReport,
        script: Script,
        character_dna: DigitalDNA,
        live_claims: Dict[str, Any],
        round_number: int,
        trace_id: str
    ) -> None:
        """
        Ensures that Gemini cannot hallucinate approval for blocked claims or severe rule breaks.
        """
        # A. Check for blocked claim references
        for scene in script.scenes:
            for line in scene.lines:
                for cid in line.claim_refs:
                    claim = live_claims.get(cid)
                    if claim and getattr(claim, "is_blocked", False):
                        # Ensure blocking issue exists
                        if not any(i.claim_ref == cid and i.severity == "BLOCKING" for i in report.issues):
                            report.issues.append(CriticIssue(
                                issue_id=f"iss_claim_{cid}",
                                severity="BLOCKING",
                                scene_no=scene.scene_no,
                                issue_type="unsupported_claim",
                                description=f"Claim '{claim.claim_text}' has confidence {claim.confidence} (<0.60) with no verified documentary grounding.",
                                claim_ref=cid
                            ))

        # B. Check sentence length against DNA
        for scene in script.scenes:
            for line in scene.lines:
                word_count = len(line.text.split())
                if character_dna.speech.sentence_length == "short" and word_count > 25:
                    if not any(i.scene_no == scene.scene_no and i.issue_type == "sentence_length" for i in report.issues):
                        report.issues.append(CriticIssue(
                            issue_id=f"iss_length_{scene.scene_no}",
                            severity="MINOR",
                            scene_no=scene.scene_no,
                            issue_type="sentence_length",
                            description=f"Scene {scene.scene_no} sentence length ({word_count} words) exceeds short guidance."
                        ))

        # C. Recompute blocking count and verdict
        report.blocking_count = sum(1 for i in report.issues if i.severity == "BLOCKING")
        if report.blocking_count > 0 or (round_number == 1 and len(report.issues) > 0):
            report.verdict = "reject"
        else:
            report.verdict = "approve"

        report.feedback_summary = (
            f"Adversarial audit completed: {len(report.issues)} issue(s) identified ({report.blocking_count} blocking). "
            f"Verdict: {report.verdict.upper()}."
        )

        app_logger.log_operation(
            trace_id=trace_id,
            operation="critic_review",
            status="SUCCESS",
            agent_task="critic_agent",
            details={
                "verdict": report.verdict,
                "issues_count": len(report.issues),
                "blocking_count": report.blocking_count,
                "round": round_number
            }
        )
