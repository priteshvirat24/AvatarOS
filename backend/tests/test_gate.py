from backend.app.models.guardian import GuardianReport, SceneAuditResult
from backend.app.models.rights import RightsRecord
from backend.app.agents.publication_gate import publication_gate

def test_forced_publication_gate_blocking_on_unsupported_claim():
    scene_audit = SceneAuditResult(
        scene_no=1,
        identity_similarity=0.95,
        identity_min_frame_similarity=0.91,
        identity_passed=True,
        voice_similarity=0.92,
        voice_passed=True,
        script_adherence_pct=98.0,
        script_passed=True,
        expected_emotion="curious",
        detected_emotion="curious",
        emotion_mismatch_score=0.05,
        emotion_passed=True,
        claims_verified_count=1,
        claims_blocked_count=1,  # BLOCKED CLAIM!
        claims_passed=False,
        brand_passed=True,
        safety_passed=True,
        lip_sync_offset_ms=30,
        lip_sync_passed=True,
        scene_verdict="FAIL",
        failure_reasons=["Unverified claim detected"]
    )

    report = GuardianReport(
        audit_id="guard_test_fail",
        asset_id="asset_01",
        overall_status="BLOCKED",
        mean_identity_similarity=0.95,
        voice_similarity=0.92,
        script_adherence_pct=98.0,
        claims_audit_summary="Blocked claim present",
        emotion_audit_summary="Pass",
        failed_scenes=[1],
        scene_audits=[scene_audit],
        timestamp="2026-09-08T00:00:00Z"
    )

    rights = RightsRecord(
        rights_id="rights-test",
        character_id="maya",
        likeness_holder="Maya Sharma",
        signature="signed",
        renewal_status="active"
    )

    result = publication_gate.publish(
        asset_id="asset_01",
        guardian_report=report,
        rights_record=rights,
        script_id="sc_01",
        director_plan_id="dp_01"
    )

    assert result.status == "BLOCKED"
    assert result.failed_check == "verify_claims"
    assert result.provenance is None

def test_forced_publication_gate_approved_c2pa_generation():
    scene_audit = SceneAuditResult(
        scene_no=1,
        identity_similarity=0.95,
        identity_min_frame_similarity=0.91,
        identity_passed=True,
        voice_similarity=0.92,
        voice_passed=True,
        script_adherence_pct=98.0,
        script_passed=True,
        expected_emotion="curious",
        detected_emotion="curious",
        emotion_mismatch_score=0.05,
        emotion_passed=True,
        claims_verified_count=2,
        claims_blocked_count=0,
        claims_passed=True,
        brand_passed=True,
        safety_passed=True,
        lip_sync_offset_ms=30,
        lip_sync_passed=True,
        scene_verdict="PASS"
    )

    report = GuardianReport(
        audit_id="guard_test_pass",
        asset_id="asset_pass",
        overall_status="APPROVED",
        mean_identity_similarity=0.95,
        voice_similarity=0.92,
        script_adherence_pct=98.0,
        claims_audit_summary="All claims verified",
        emotion_audit_summary="Pass",
        failed_scenes=[],
        scene_audits=[scene_audit],
        timestamp="2026-09-08T00:00:00Z"
    )

    rights = RightsRecord(
        rights_id="rights-test",
        character_id="maya",
        likeness_holder="Maya Sharma",
        signature="signed",
        renewal_status="active"
    )

    result = publication_gate.publish(
        asset_id="asset_pass",
        guardian_report=report,
        rights_record=rights,
        script_id="sc_01",
        director_plan_id="dp_01"
    )

    assert result.status == "PUBLISHED"
    assert result.provenance is not None
    assert result.provenance.c2pa_manifest_hash.startswith("c2pa:sha256:")
    assert result.provenance.ai_disclosure_marker is True
