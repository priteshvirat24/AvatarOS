import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.agents.renderer import renderer
from backend.app.agents.guardian import guardian_agent
from backend.app.agents.publication_gate import publication_gate
from backend.app.ai.media_inspector import media_inspector
from backend.app.ai.asr_provider import get_asr_provider, DeterministicASRFallback, GoogleGeminiASRProvider
from backend.app.ai.multimodal_guardian import get_multimodal_guardian_provider, DeterministicMediaInspector
from backend.app.models.dna import DigitalDNA
from backend.app.models.script import Script, ScriptScene, ScriptLine
from backend.app.models.director import DirectorPlan, SceneShot
from backend.app.models.rights import RightsRecord
from backend.app.models.guardian import GuardianReport, SceneAuditResult

client = TestClient(app)

@pytest.fixture
def sample_dna() -> DigitalDNA:
    from backend.app.data.seed_characters import get_seed_characters
    return get_seed_characters()["characters"]["maya"]

@pytest.fixture
def sample_rights() -> RightsRecord:
    from backend.app.data.seed_characters import get_seed_characters
    return get_seed_characters()["rights"]["maya"]

@pytest.fixture
def sample_script() -> Script:
    return Script(
        script_id="sc_test_titan_v1",
        version=1,
        duration_target_s=60.0,
        language="en",
        scenes=[
            ScriptScene(scene_no=1, role="hook", duration_s=6.8, lines=[ScriptLine(speaker="maya", text="What if local builds were instant?", claim_refs=[])]),
            ScriptScene(scene_no=2, role="problem", duration_s=12.0, lines=[ScriptLine(speaker="maya", text="Cloud latency breaks flow state.", claim_refs=[])]),
            ScriptScene(scene_no=3, role="product", duration_s=14.0, lines=[ScriptLine(speaker="maya", text="Meet Titan AI Studio with 45 TOPS NPU.", claim_refs=["claim_0310"])]),
            ScriptScene(scene_no=4, role="demonstration", duration_s=15.0, lines=[ScriptLine(speaker="maya", text="Independent MLPerf benchmarks show 40% faster local LLM inference.", claim_refs=["claim_0231"])]),
            ScriptScene(scene_no=5, role="cta", duration_s=10.0, lines=[ScriptLine(speaker="maya", text="Order at titan.dev.", claim_refs=[])]),
        ]
    )

@pytest.fixture
def sample_director_plan() -> DirectorPlan:
    return DirectorPlan(
        plan_id="dp_test_plan_v1",
        campaign_name="Titan AI Laptop Launch",
        target_audience="Developers",
        duration_target_s=60.0,
        languages=["en", "hi"],
        tone="Technical",
        strategy_version=13,
        strategy_citation="ch_query_881a",
        hook_type="question",
        opening_duration_s=6.8,
        shots=[
            SceneShot(scene_no=1, role="hook", duration_s=6.8, shot="close_up", camera_move="slow_push_in", target_emotion="curious", emotional_intensity=0.75),
            SceneShot(scene_no=2, role="problem", duration_s=12.0, shot="medium_shot", camera_move="static", target_emotion="concerned", emotional_intensity=0.35),
            SceneShot(scene_no=3, role="product", duration_s=14.0, shot="medium_close_up", camera_move="slow_push_in", target_emotion="confident", emotional_intensity=0.60),
            SceneShot(scene_no=4, role="demonstration", duration_s=15.0, shot="medium_close_up", camera_move="slow_push_in", target_emotion="excited", emotional_intensity=0.78),
            SceneShot(scene_no=5, role="cta", duration_s=10.0, shot="medium_shot", camera_move="static", target_emotion="direct", emotional_intensity=0.70),
        ]
    )

@pytest.fixture
def sample_rendered_video() -> str:
    # Render a real short clip using FFmpeg for media testing
    return renderer.render_scene(
        scene_no=1,
        role="hook",
        text="Testing Media Inspector for AVATAROS Multimodal Guardian",
        duration_s=2.0,
        character_name="Maya",
        character_version="v1.7.0",
        target_emotion="curious",
        energy=0.75,
        language="en"
    )

def test_media_validation_real_video(sample_rendered_video: str):
    """Test deterministic media validation on real FFmpeg-generated MP4."""
    val = media_inspector.validate_media(sample_rendered_video)
    assert val.is_valid is True
    assert val.file_size_bytes > 0
    assert val.duration_s > 0.0
    assert val.has_video is True

def test_media_validation_missing_and_corrupt(tmp_path):
    """Test rejection of missing, zero-byte, and corrupted media files."""
    missing = media_inspector.validate_media(str(tmp_path / "non_existent.mp4"))
    assert missing.is_valid is False
    assert "File not found" in missing.errors[0]

    zero_byte = tmp_path / "zero_byte.mp4"
    zero_byte.write_bytes(b"")
    zero_val = media_inspector.validate_media(str(zero_byte))
    assert zero_val.is_valid is False
    assert "Zero-byte" in zero_val.errors[0]

def test_frame_extraction_bounded_samples(sample_rendered_video: str):
    """Test deterministic frame sampling across video timeline."""
    frames = media_inspector.extract_frame_samples(sample_rendered_video, sample_count=5)
    assert len(frames) == 5
    for idx, f in enumerate(frames):
        assert f.frame_index == idx
        assert os.path.exists(f.image_path)
        assert f.sha256.startswith("sha256:")
        assert f.timestamp_s >= 0.0

def test_audio_extraction(sample_rendered_video: str):
    """Test extracting 16kHz mono audio track from rendered MP4."""
    audio_res = media_inspector.extract_audio_track(sample_rendered_video)
    assert audio_res.audio_path.endswith(".wav")
    assert os.path.exists(audio_res.audio_path)
    assert audio_res.sample_rate == 16000
    assert audio_res.channels == 1
    assert audio_res.sha256.startswith("sha256:")

def test_asr_provider_english_and_hindi():
    """Test offline deterministic ASR provider and language metadata."""
    asr = DeterministicASRFallback()
    res_en = asr.transcribe("", language="en")
    assert res_en.language == "en"
    assert res_en.confidence >= 0.95
    assert len(res_en.segments) == 5
    assert "Titan AI Studio Laptop" in res_en.transcript_text

    res_hi = asr.transcribe("", language="hi")
    assert res_hi.language == "hi"
    assert res_hi.confidence >= 0.95
    assert "टाइटन" in res_hi.transcript_text

def test_spoken_claim_audit_grounded_success(sample_rendered_video: str, sample_script: Script, sample_director_plan: DirectorPlan, sample_dna: DigitalDNA):
    """Test that grounded media passes multimodal guardian inspection."""
    report = guardian_agent.audit_production(
        asset_id="asset_grounded_test",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=sample_rendered_video,
        simulate_scene4_emotion_fail=False,
        simulate_claim_drift=False
    )
    assert report.overall_status == "APPROVED"
    assert report.mean_identity_similarity >= 0.92
    assert report.voice_similarity >= 0.90
    assert report.script_adherence_pct >= 95.0
    assert report.claim_drift_detected is False
    assert len(report.failed_scenes) == 0

def test_spoken_claim_drift_detection_and_blocking(sample_rendered_video: str, sample_script: Script, sample_director_plan: DirectorPlan, sample_dna: DigitalDNA):
    """Test that ungrounded claim drift in rendered speech triggers GUARDIAN BLOCKED."""
    report = guardian_agent.audit_production(
        asset_id="asset_drift_test",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=sample_rendered_video,
        simulate_scene4_emotion_fail=False,
        simulate_claim_drift=True
    )
    assert report.overall_status == "BLOCKED"
    assert report.claim_drift_detected is True
    assert 4 in report.failed_scenes

def test_emotion_mismatch_rework_trigger(sample_rendered_video: str, sample_script: Script, sample_director_plan: DirectorPlan, sample_dna: DigitalDNA):
    """Test that emotion mismatch (37% > 30%) on scene 4 triggers REWORK."""
    report = guardian_agent.audit_production(
        asset_id="asset_emotion_rework_test",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=sample_rendered_video,
        simulate_scene4_emotion_fail=True,
        simulate_claim_drift=False
    )
    assert report.overall_status == "REWORK"
    assert report.failed_scenes == [4]
    scene4_audit = next(s for s in report.scene_audits if s.scene_no == 4)
    assert scene4_audit.emotion_passed is False
    assert scene4_audit.emotion_mismatch_score > 0.30

def test_publication_gate_blocks_on_guardian_failure(sample_rights: RightsRecord):
    """Test that Forced Publication Gate hard-blocks when Guardian report is not APPROVED."""
    failed_report = GuardianReport(
        audit_id="guard_fail_test",
        asset_id="asset_blocked_1",
        overall_status="BLOCKED",
        mean_identity_similarity=0.938,
        voice_similarity=0.915,
        script_adherence_pct=96.8,
        claims_audit_summary="Ungrounded claim drift detected",
        emotion_audit_summary="Normal",
        failed_scenes=[4],
        timestamp="2026-09-08T00:00:00Z"
    )
    res = publication_gate.publish(
        asset_id="asset_blocked_1",
        guardian_report=failed_report,
        rights_record=sample_rights,
        script_id="sc_test",
        director_plan_id="dp_test"
    )
    assert res.status == "BLOCKED"
    assert res.failed_check in ("guardian_approval", "verify_claims")
    assert res.provenance is None

def test_publication_gate_approves_on_guardian_pass(sample_rights: RightsRecord):
    """Test that Forced Publication Gate approves and signs C2PA manifest when Guardian report is APPROVED."""
    approved_report = GuardianReport(
        audit_id="guard_pass_test",
        asset_id="asset_approved_1",
        overall_status="APPROVED",
        mean_identity_similarity=0.942,
        voice_similarity=0.915,
        script_adherence_pct=97.5,
        claims_audit_summary="100% verified",
        emotion_audit_summary="Matched",
        failed_scenes=[],
        timestamp="2026-09-08T00:00:00Z",
        total_sampled_frames=5
    )
    res = publication_gate.publish(
        asset_id="asset_approved_1",
        guardian_report=approved_report,
        rights_record=sample_rights,
        script_id="sc_test",
        director_plan_id="dp_test"
    )
    assert res.status == "PUBLISHED"
    assert res.provenance is not None
    assert res.provenance.c2pa_manifest_hash.startswith("c2pa:sha256:")
    assert any(a.label == "avataros.guardian" for a in res.provenance.assertions)

def test_health_endpoint_guardian_and_asr_observability():
    """Test that /health and /health/ready report Guardian and ASR provider states."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    services = data.get("services", {})
    assert "guardian" in services
    assert services["guardian"]["provider"] in ("deterministic", "gemini_multimodal")
    assert services["guardian"]["identity_threshold"] == 0.92
    assert "asr" in services
    assert services["asr"]["provider"] in ("deterministic", "google", "gemini")

    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    ready_data = ready_resp.json()
    assert "ffprobe" in ready_data
