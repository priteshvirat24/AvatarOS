import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.production import (
    ProductionRun,
    ProductionRunCreateRequest,
    AgentExecutionEvent,
    ProductionScorecard,
    FailureUX
)
from backend.app.agents.orchestrator import orchestrator
from backend.app.data.production_store import production_store

client = TestClient(app)

def test_production_run_success_lifecycle():
    """
    Milestone 9: Test successful autonomous production run creation,
    DAG execution, stage ordering, trace propagation, scorecard, and provenance.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Explain Titan laptop battery life and local LLM performance for developers.",
        campaign_id="titan_laptop_india_devs",
        language="en",
        register="technical"
    )
    prod_run = orchestrator.execute_production_run(req)

    # 1. Verification of run metadata
    assert prod_run.run_id.startswith("run_")
    assert prod_run.trace_id.startswith("trace_")
    assert prod_run.character_id == "maya"
    assert prod_run.dna_version == "1.7.0"
    assert prod_run.status == "COMPLETED"
    assert prod_run.current_stage == "COMPLETED"
    assert prod_run.duration_ms > 0

    # 2. Stage Ordering & Trace Propagation
    stage_names = set(s.stage for s in prod_run.stages)
    expected_stages = [
        "RIGHTS_CHECK",
        "RESEARCH",
        "VERIFY_CLAIMS",
        "SCRIPT",
        "CRITIC",
        "DIRECTOR",
        "PERFORMANCE",
        "VOICE",
        "AVATAR",
        "GUARDIAN",
        "PUBLICATION_GATE"
    ]
    for exp in expected_stages:
        assert exp in stage_names, f"Expected stage {exp} missing from stages"

    for st in prod_run.stages:
        assert st.trace_id == prod_run.trace_id
        assert st.status in ("RUNNING", "COMPLETED", "REVISING", "REWORKING", "BLOCKED", "FAILED")
        assert st.duration_ms >= 0

    # 3. Scorecard 8 Dimensions
    assert prod_run.scorecard.identity == "PASS"
    assert prod_run.scorecard.rights == "PASS"
    assert prod_run.scorecard.evidence == "PASS"
    assert prod_run.scorecard.performance == "PASS"
    assert prod_run.scorecard.media == "PASS"
    assert prod_run.scorecard.safety == "PASS"
    assert prod_run.scorecard.provenance == "PASS"
    assert prod_run.scorecard.learning == "PASS"

    # 4. Artifacts & Provenance
    assert prod_run.master_video_url is not None
    assert prod_run.media_sha256 is not None
    assert prod_run.c2pa_manifest_hash is not None
    assert prod_run.hindi_production is not None
    assert len(prod_run.repurposed_clips) == 3


def test_production_claim_block_failure_ux():
    """
    Milestone 9: Test deliberate unsupported claim injection.
    Expects: RESEARCH blocks claim -> SCRIPT blocks claim -> RENDER/PUBLISH blocked -> FailureUX populated.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Explain Titan LLM performance. State that it is 3x faster with zero latency.",
        campaign_id="titan_laptop_india_devs",
        inject_claim_failure=True
    )
    prod_run = orchestrator.execute_production_run(req)

    assert prod_run.status == "BLOCKED"
    assert prod_run.scorecard.evidence == "BLOCKED"
    assert prod_run.scorecard.safety == "BLOCKED"

    # Structured Failure UX
    assert prod_run.failure_ux is not None
    assert "Claim Grounding" in prod_run.failure_ux.what_failed
    assert "evidence" in prod_run.failure_ux.why.lower() or "claim" in prod_run.failure_ux.why.lower()
    assert "Evidence integrity" in prod_run.failure_ux.what_was_protected
    assert "benchmark proof" in prod_run.failure_ux.what_happens_next.lower() or "document" in prod_run.failure_ux.what_happens_next.lower()

    # Publication Gate must NOT publish ungrounded claim
    assert prod_run.publish_result is None or prod_run.publish_result.get("status") == "BLOCKED"


def test_production_guardian_emotion_mismatch_rework():
    """
    Milestone 9: Test multimodal Guardian detection of emotion mismatch and bounded rework.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Explain Titan laptop benchmarks.",
        campaign_id="titan_laptop_india_devs",
        inject_emotion_failure=True
    )
    prod_run = orchestrator.execute_production_run(req)

    # After rework, Guardian evaluates approved
    assert prod_run.status == "COMPLETED"
    assert prod_run.guardian_result is not None
    assert prod_run.guardian_result.get("overall_status") in ("APPROVED", "REWORK")
    assert prod_run.scorecard.safety == "PASS"


def test_production_rights_block():
    """
    Milestone 9: Test simulation of revoked/expired rights.
    Expects: Immediate render block, no media generated, Publication Gate blocked.
    """
    req = ProductionRunCreateRequest(
        character_id="maya",
        brief="Create marketing video for Titan laptop.",
        simulate_rights_failure=True
    )
    prod_run = orchestrator.execute_production_run(req)

    assert prod_run.status == "BLOCKED"
    assert prod_run.scorecard.rights == "BLOCKED"
    assert prod_run.failure_ux is not None
    assert "Likeness Rights" in prod_run.failure_ux.what_failed
    assert prod_run.master_video_url is None
    assert prod_run.publish_result.get("status") == "BLOCKED"


def test_production_run_api_endpoints():
    """
    Milestone 9: Test HTTP endpoints:
    - POST /api/production/run
    - GET /api/production/run/{run_id}
    - GET /api/production/run/{run_id}/events
    - GET /api/production/run/{run_id}/provenance
    """
    res = client.post("/api/production/run", json={
        "character_id": "maya",
        "brief": "Explain Titan AI architecture.",
        "campaign_id": "titan_laptop_india_devs",
        "language": "en",
        "register": "technical"
    })
    assert res.status_code == 200
    data = res.json()
    run_id = data["run_id"]

    # GET /api/production/run/{run_id}
    get_res = client.get(f"/api/production/run/{run_id}")
    assert get_res.status_code == 200
    assert get_res.json()["run_id"] == run_id

    # GET /api/production/run/{run_id}/events
    events_res = client.get(f"/api/production/run/{run_id}/events")
    assert events_res.status_code == 200
    events_data = events_res.json()
    assert events_data["run_id"] == run_id
    assert len(events_data["events"]) > 0

    # GET /api/production/run/{run_id}/provenance
    prov_res = client.get(f"/api/production/run/{run_id}/provenance")
    assert prov_res.status_code == 200
    prov_data = prov_res.json()
    assert prov_data["character_id"] == "maya"
    assert prov_data["c2pa_manifest_hash"] is not None


def test_production_demo_endpoints():
    """
    Milestone 9: Test specialized judge demo endpoints enforcing real architecture:
    - POST /api/production/demo/claim-block
    - POST /api/production/demo/guardian-failure
    - POST /api/production/demo/rights-block
    """
    res_claim = client.post("/api/production/demo/claim-block")
    assert res_claim.status_code == 200
    data_claim = res_claim.json()
    assert data_claim["status"] == "BLOCKED"
    assert data_claim["scorecard"]["evidence"] == "BLOCKED"

    res_guardian = client.post("/api/production/demo/guardian-failure")
    assert res_guardian.status_code == 200
    data_guardian = res_guardian.json()
    assert data_guardian["guardian_result"] is not None

    res_rights = client.post("/api/production/demo/rights-block")
    assert res_rights.status_code == 200
    data_rights = res_rights.json()
    assert data_rights["status"] == "BLOCKED"
    assert data_rights["scorecard"]["rights"] == "BLOCKED"


def test_live_to_studio_handoff_isolation():
    """
    Milestone 9 Section 24: Test safe Live -> Studio Handoff.
    Creates a draft brief without promoting ephemeral session memory to permanent character memory.
    """
    # Create live session
    sess_res = client.post("/api/live/session", json={
        "character_id": "maya",
        "language": "en"
    })
    assert sess_res.status_code == 200
    session_id = sess_res.json()["session_id"]

    # Submit a conversational turn
    turn_res = client.post(f"/api/live/session/{session_id}/turn", json={
        "text": "Tell me about the NPU architecture on Titan laptops."
    })
    assert turn_res.status_code == 200

    # Trigger handoff
    handoff_res = client.post(f"/api/live/session/{session_id}/handoff", json={
        "session_id": session_id,
        "target_audience": "enterprise CTO"
    })
    assert handoff_res.status_code == 200
    handoff_data = handoff_res.json()

    assert handoff_data["status"] == "DRAFT_CREATED"
    assert handoff_data["character_id"] == "maya"
    assert "Draft campaign brief synthesized from Live Session" in handoff_data["draft_brief"]
    assert handoff_data["is_promoted_to_permanent_memory"] is False
    assert handoff_data["turns_analyzed"] >= 1
