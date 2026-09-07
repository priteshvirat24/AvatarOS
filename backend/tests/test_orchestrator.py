from backend.app.agents.orchestrator import orchestrator

def test_orchestrator_execution_success():
    res = orchestrator.execute_campaign(
        command_intent="Test campaign for Indian developers",
        character_id="maya",
        inject_claim_failure=False,
        inject_emotion_failure=False
    )
    assert res["trace_id"] is not None
    assert res["publish_result"]["status"] == "PUBLISHED"
    assert res["guardian_report"]["overall_status"] == "APPROVED"
    assert len(res["repurposed_clips"]) == 3
    assert res["hindi_production"]["meaning_equivalence_score"] >= 0.85

def test_orchestrator_claim_failure_injection_and_resolution():
    # Step 4 Demo test: Deliberate unsupported claim triggers block
    res = orchestrator.execute_campaign(
        command_intent="Trigger 3x faster unsupported claim",
        character_id="maya",
        inject_claim_failure=True,
        inject_emotion_failure=False
    )
    # The unsupported claim causes publication to be BLOCKED!
    assert res["publish_result"]["status"] == "BLOCKED"
    assert res["publish_result"]["failed_check"] == "verify_claims"

    # Now resolve the claim by attaching benchmark document
    resolve_res = orchestrator.research_agent.resolve_blocked_claim(
        claim_id="claim_fail_3x",
        uploaded_evidence_name="titan_benchmarks_mlperf_v2.pdf"
    )
    assert resolve_res.is_blocked is False
    assert resolve_res.status == "verified"
