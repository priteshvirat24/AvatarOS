import os
import pytest
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.models.dna import DigitalDNA, IdentitySpec, PersonalityVector
from backend.app.models.rights import RightsRecord
from backend.app.models.director import DirectorPlan, DirectorShot
from backend.app.models.script import Script, ScriptScene, ScriptLine
from backend.app.models.performance import (
    PerformancePlan,
    ScenePerformanceSpec,
    FacialExpressionPlan,
    GazePlan,
    HeadMotionPlan,
    CameraShotPlan,
    LipSyncPlan
)
from backend.app.models.provenance import ProvenanceRecord, PublishResult
from backend.app.data.seed_characters import get_seed_characters
from backend.app.ai.voice_provider import (
    BaseVoiceProvider,
    DeterministicVoiceProvider,
    GeminiTTSVoiceProvider,
    get_voice_provider,
    AudioGenerationResult
)
from backend.app.ai.avatar_renderer import (
    BaseAvatarRenderer,
    DeterministicAvatarRenderer,
    ProductionAvatarRenderer,
    get_avatar_renderer,
    RenderSceneResult,
    RenderMasterResult
)
from backend.app.ai.media_inspector import media_inspector
from backend.app.agents.performance import performance_agent
from backend.app.agents.renderer import renderer
from backend.app.agents.guardian import guardian_agent
from backend.app.agents.publication_gate import publication_gate
from backend.app.agents.orchestrator import orchestrator

@pytest.fixture
def sample_dna():
    seeds = get_seed_characters()
    return seeds["characters"]["maya"]

@pytest.fixture
def sample_rights():
    seeds = get_seed_characters()
    return seeds["rights"]["maya"]

@pytest.fixture
def sample_director_plan():
    return DirectorPlan(
        plan_id="plan_test_001",
        campaign_name="Titan AI Laptop",
        target_audience="Indian developers",
        duration_target_s=60.0,
        tone="technical_conversational",
        strategy_version=14,
        hook_type="question",
        opening_duration_s=6.8,
        shots=[
            DirectorShot(
                scene_no=1,
                shot="close_up",
                target_emotion="curious",
                emotional_intensity=0.72,
                role="hook",
                pacing="rapid_hook",
                visual_prompt="Close up of Maya in tech studio",
                duration_s=6.8
            ),
            DirectorShot(
                scene_no=2,
                shot="medium_shot",
                target_emotion="concerned",
                emotional_intensity=0.68,
                role="problem",
                pacing="steady",
                visual_prompt="Medium shot with terminal overlay",
                duration_s=12.0
            ),
            DirectorShot(
                scene_no=3,
                shot="medium_close_up",
                target_emotion="confident",
                emotional_intensity=0.82,
                role="product",
                pacing="confident",
                visual_prompt="Chassis reveal with NPU badge",
                duration_s=14.0
            ),
            DirectorShot(
                scene_no=4,
                shot="medium_close_up",
                target_emotion="excited",
                emotional_intensity=0.88,
                role="demonstration",
                pacing="energetic",
                visual_prompt="MLPerf benchmark graph",
                duration_s=15.0
            ),
            DirectorShot(
                scene_no=5,
                shot="medium_shot",
                target_emotion="direct",
                emotional_intensity=0.75,
                role="cta",
                pacing="direct",
                visual_prompt="Order portal lower third",
                duration_s=10.0
            )
        ]
    )

@pytest.fixture
def sample_script():
    return Script(
        script_id="script_test_001",
        scenes=[
            ScriptScene(scene_no=1, role="hook", duration_s=6.8, lines=[ScriptLine(speaker="Maya", text="Still waiting for cloud AI models to respond?")]),
            ScriptScene(scene_no=2, role="problem", duration_s=12.0, lines=[ScriptLine(speaker="Maya", text="Cloud latency kills developer flow.")]),
            ScriptScene(scene_no=3, role="product", duration_s=14.0, lines=[ScriptLine(speaker="Maya", text="Meet Titan AI Laptop with 45 TOPS NPU.")]),
            ScriptScene(scene_no=4, role="demonstration", duration_s=15.0, lines=[ScriptLine(speaker="Maya", text="Independent MLPerf benchmarks show 40% faster local LLM inference.", claim_refs=["claim_0231"])]),
            ScriptScene(scene_no=5, role="cta", duration_s=10.0, lines=[ScriptLine(speaker="Maya", text="Order your Titan developer kit today at titan.dev.")])
        ],
        language="en"
    )

# ==============================================================================
# 1. RENDERER ABSTRACTION & DETERMINISTIC EXECUTION TESTS
# ==============================================================================

def test_renderer_abstraction_initializes():
    rend = get_avatar_renderer()
    assert isinstance(rend, BaseAvatarRenderer)
    status = rend.get_renderer_status()
    assert status["configured"] is True
    assert status["ready"] is True
    assert "capabilities" in status
    assert status["capabilities"]["lip_sync"] is True

def test_deterministic_renderer_execution(sample_dna, sample_director_plan):
    det_rend = DeterministicAvatarRenderer()
    perf_plan = performance_agent.create_performance_plan(sample_director_plan, sample_dna)
    
    res = det_rend.render_scene(
        scene_no=1,
        role="hook",
        text="Testing digital human render pipeline",
        duration_s=4.0,
        character_dna=sample_dna,
        performance_plan=perf_plan,
        language="en"
    )
    assert isinstance(res, RenderSceneResult)
    assert os.path.exists(res.video_path)
    assert res.file_size_bytes > 0
    assert res.sha256.startswith("sha256:")
    assert res.is_neural is False
    assert res.renderer_provider == "deterministic"

def test_deterministic_renderer_timeline_stitching(sample_dna):
    det_rend = DeterministicAvatarRenderer()
    p1 = det_rend.render_scene(1, "hook", "Scene 1 text", 3.0, sample_dna)
    p2 = det_rend.render_scene(2, "problem", "Scene 2 text", 3.0, sample_dna)
    
    master = det_rend.stitch_master_video([p1.video_path, p2.video_path], output_name="test_master.mp4")
    assert isinstance(master, RenderMasterResult)
    assert os.path.exists(master.master_video_path)
    assert master.scene_count == 2
    assert master.sha256.startswith("sha256:")

def test_production_renderer_configuration_detection():
    prod_rend = ProductionAvatarRenderer()
    status = prod_rend.get_renderer_status()
    # In offline test environment without RENDERER_API_KEY, honestly reports deterministic
    assert status["ready"] is True
    if not settings.RENDERER_API_KEY:
        assert status["is_neural"] is False
        assert status["provider"] == "deterministic"

# ==============================================================================
# 2. VOICE PROVIDER TESTS
# ==============================================================================

def test_voice_provider_abstraction_initializes():
    voice_prov = get_voice_provider()
    assert isinstance(voice_prov, BaseVoiceProvider)
    status = voice_prov.get_voice_status()
    assert status["configured"] is True
    assert status["ready"] is True
    assert "en" in status["languages_supported"]
    assert "hi" in status["languages_supported"]

def test_deterministic_voice_generation_en_and_hi(sample_dna):
    voice_prov = DeterministicVoiceProvider()
    
    # English voice generation
    res_en = voice_prov.generate_speech(
        text="Cloud latency kills developer flow.",
        character_dna=sample_dna,
        language="en",
        target_emotion="confident"
    )
    assert isinstance(res_en, AudioGenerationResult)
    assert os.path.exists(res_en.audio_path)
    assert res_en.duration_s > 0
    assert res_en.audio_hash.startswith("sha256:")
    assert res_en.language == "en"
    assert res_en.voice_model == "maya-english-v4"

    # Hindi voice generation
    res_hi = voice_prov.generate_speech(
        text="क्लाउड लेटेंसी डेवलपर फ्लो को धीमा कर देती है।",
        character_dna=sample_dna,
        language="hi",
        target_emotion="confident"
    )
    assert isinstance(res_hi, AudioGenerationResult)
    assert os.path.exists(res_hi.audio_path)
    assert res_hi.audio_hash.startswith("sha256:")
    assert res_hi.language == "hi"
    assert res_hi.voice_model == "maya-hindi-v1"

# ==============================================================================
# 3. PERFORMANCE PLAN SCHEMA & BINDING TESTS
# ==============================================================================

def test_performance_plan_schema_validation(sample_dna, sample_director_plan):
    perf_plan = performance_agent.create_performance_plan(sample_director_plan, sample_dna, language="en")
    assert isinstance(perf_plan, PerformancePlan)
    assert perf_plan.character_id == "maya"
    assert perf_plan.dna_version == "1.7.0"
    assert perf_plan.voice_model == "maya-english-v4"
    assert perf_plan.language == "en"
    assert len(perf_plan.scenes) == 5
    
    # Verify typed sub-plans
    s1 = perf_plan.scenes[0]
    assert isinstance(s1.facial_plan, FacialExpressionPlan)
    assert isinstance(s1.gaze_plan, GazePlan)
    assert isinstance(s1.head_motion_plan, HeadMotionPlan)
    assert isinstance(s1.shot_plan, CameraShotPlan)
    assert isinstance(s1.lip_sync_plan, LipSyncPlan)
    assert s1.lip_sync_plan.max_tolerance_ms == 80

def test_emotional_state_mapping(sample_dna, sample_director_plan):
    perf_plan = performance_agent.create_performance_plan(sample_director_plan, sample_dna)
    # Scene 4 has excited emotion
    s4 = perf_plan.scenes[3]
    assert s4.target_emotion == "excited"
    assert s4.facial_plan.smile_intensity >= 0.7
    assert s4.head_motion_plan.nod_frequency >= 0.3

def test_identity_locking_immutable(sample_dna):
    # Ensure character DNA identity thresholds cannot be weakened
    assert sample_dna.identity.similarity_threshold == 0.92
    assert sample_dna.identity.voice_similarity_threshold == 0.90
    assert sample_dna.character_id == "maya"

# ==============================================================================
# 4. SERVER-SIDE RIGHTS ENFORCEMENT TESTS
# ==============================================================================

def test_valid_rights_permit_rendering(sample_dna, sample_rights):
    assert sample_rights.is_valid_for_context("marketing product_education") is True

def test_expired_rights_blocks_rendering(sample_dna):
    expired_rights = RightsRecord(
        rights_id="rights-expired",
        character_id="maya",
        likeness_holder="Maya Sharma",
        consent_scope=["marketing"],
        territories=["IN"],
        expiration="2020-01-01",
        signature="test_sig_expired",
        renewal_status="expired"
    )
    assert expired_rights.is_valid_for_context("marketing") is False

def test_revoked_rights_blocks_rendering(sample_dna):
    revoked_rights = RightsRecord(
        rights_id="rights-revoked",
        character_id="maya",
        likeness_holder="Maya Sharma",
        consent_scope=["marketing"],
        territories=["IN"],
        expiration="2028-01-01",
        signature="test_sig_revoked",
        renewal_status="revoked"
    )
    assert revoked_rights.is_valid_for_context("marketing") is False

def test_unauthorized_scope_blocks_rendering(sample_rights):
    # Political context is excluded by consent_excludes
    assert sample_rights.is_valid_for_context("political_endorsement") is False

# ==============================================================================
# 5. MULTIMODAL GUARDIAN & MEDIA FACT INSPECTION
# ==============================================================================

def test_media_inspector_extracts_measurable_facts(sample_dna, sample_director_plan):
    det_rend = DeterministicAvatarRenderer()
    res = det_rend.render_scene(1, "hook", "Facts test", 3.0, sample_dna)
    
    val = media_inspector.validate_media(res.video_path)
    assert val.is_valid is True
    assert val.file_size_bytes > 0
    assert val.duration_s > 0
    assert val.has_video is True
    assert val.has_audio is True
    assert val.fps > 0
    assert val.frame_count > 0
    assert val.video_codec is not None

def test_guardian_audit_and_threshold_enforcement(sample_dna, sample_director_plan, sample_script):
    det_rend = DeterministicAvatarRenderer()
    res = det_rend.render_scene(1, "hook", "Audit test", 4.0, sample_dna)
    master = det_rend.stitch_master_video([res.video_path], output_name="guardian_test_master.mp4")
    
    report = guardian_agent.audit_production(
        asset_id="asset_guard_001",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=master.master_video_path
    )
    
    assert report.mean_identity_similarity >= 0.92
    assert report.voice_similarity >= 0.90
    assert report.script_adherence_pct >= 95.0
    assert report.media_validated is True
    assert report.media_facts is not None
    assert report.media_sha256.startswith("sha256:")

def test_guardian_claim_drift_blocks_approval(sample_dna, sample_director_plan, sample_script):
    det_rend = DeterministicAvatarRenderer()
    res = det_rend.render_scene(4, "demonstration", "Claim drift test", 4.0, sample_dna)
    master = det_rend.stitch_master_video([res.video_path], output_name="claim_drift_master.mp4")
    
    # Simulate claim drift
    drift_report = guardian_agent.audit_production(
        asset_id="asset_drift_001",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=master.master_video_path,
        simulate_claim_drift=True
    )
    assert drift_report.claim_drift_detected is True
    assert drift_report.overall_status in ("BLOCKED", "REWORK")

# ==============================================================================
# 6. BOUNDED REWORK & PUBLICATION GATE TESTS
# ==============================================================================

def test_bounded_rework_on_emotion_failure(sample_dna, sample_director_plan, sample_script):
    det_rend = DeterministicAvatarRenderer()
    res = det_rend.render_scene(4, "demonstration", "Emotion fail test", 4.0, sample_dna)
    master = det_rend.stitch_master_video([res.video_path], output_name="rework_master.mp4")
    
    fail_report = guardian_agent.audit_production(
        asset_id="asset_rework_001",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=master.master_video_path,
        simulate_scene4_emotion_fail=True
    )
    assert fail_report.overall_status == "REWORK"
    assert 4 in fail_report.failed_scenes

    # Rework Scene 4 only and re-audit
    re_res = det_rend.render_scene(4, "demonstration", "Emotion resolved test", 4.0, sample_dna)
    re_master = det_rend.stitch_master_video([re_res.video_path], output_name="rework_master.mp4")
    
    pass_report = guardian_agent.audit_production(
        asset_id="asset_rework_001",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=re_master.master_video_path,
        simulate_scene4_emotion_fail=False
    )
    assert pass_report.overall_status == "APPROVED"

def test_publication_gate_emits_c2pa_provenance(sample_dna, sample_rights, sample_director_plan, sample_script):
    det_rend = DeterministicAvatarRenderer()
    res = det_rend.render_scene(1, "hook", "Publication gate test", 4.0, sample_dna)
    master = det_rend.stitch_master_video([res.video_path], output_name="pub_master.mp4")
    
    report = guardian_agent.audit_production(
        asset_id="asset_pub_001",
        script=sample_script,
        director_plan=sample_director_plan,
        character_dna=sample_dna,
        media_path=master.master_video_path
    )
    
    pub_res = publication_gate.publish(
        asset_id="asset_pub_001",
        guardian_report=report,
        rights_record=sample_rights,
        script_id=sample_script.script_id,
        director_plan_id=sample_director_plan.plan_id,
        performance_plan_id="perf_plan_test_001",
        character_version=f"{sample_dna.character_id}@{sample_dna.version}",
        dna_version=sample_dna.version,
        voice_provider="deterministic",
        voice_model="maya-english-v4",
        renderer_provider="deterministic",
        renderer_model="ffmpeg_identity_lock_v1",
        media_sha256=master.sha256
    )
    
    assert pub_res.status == "PUBLISHED"
    assert pub_res.provenance is not None
    assert pub_res.provenance.dna_version == "1.7.0"
    assert pub_res.provenance.renderer_provider == "deterministic"
    assert pub_res.provenance.voice_provider == "deterministic"
    assert pub_res.provenance.c2pa_manifest_hash.startswith("c2pa:sha256:")

# ==============================================================================
# 7. SECURITY & SUBPROCESS VALIDATION
# ==============================================================================

def test_path_traversal_blocked():
    val = media_inspector.validate_media("../../../etc/passwd")
    assert val.is_valid is False

def test_oversized_media_blocked(tmp_path):
    huge_file = tmp_path / "huge.mp4"
    # Create empty file and mock size exceeding limit
    huge_file.write_bytes(b"0" * 100)
    orig_limit = settings.GUARDIAN_MAX_FILE_SIZE_BYTES
    try:
        settings.GUARDIAN_MAX_FILE_SIZE_BYTES = 50  # Lower limit for test
        val = media_inspector.validate_media(str(huge_file))
        assert val.is_valid is False
        assert any("exceeds" in e for e in val.errors)
    finally:
        settings.GUARDIAN_MAX_FILE_SIZE_BYTES = orig_limit

# ==============================================================================
# 8. MULTILINGUAL & CROSS-CHARACTER CONSISTENCY
# ==============================================================================

def test_multilingual_maya_identity_consistency(sample_dna, sample_director_plan):
    perf_en = performance_agent.create_performance_plan(sample_director_plan, sample_dna, language="en")
    perf_hi = performance_agent.create_performance_plan(sample_director_plan, sample_dna, language="hi")
    
    # Identity attributes must match exactly
    assert perf_en.character_id == perf_hi.character_id == "maya"
    assert perf_en.dna_version == perf_hi.dna_version == "1.7.0"
    
    # Language and voice model adapt appropriately
    assert perf_en.language == "en"
    assert perf_hi.language == "hi"
    assert perf_en.voice_model == "maya-english-v4"
    assert perf_hi.voice_model == "maya-hindi-v1"

def test_cross_character_isolation():
    seeds = get_seed_characters()
    maya = seeds["characters"]["maya"]
    aria = seeds["characters"]["aria"]
    david = seeds["characters"]["david"]
    
    assert maya.identity.face_embedding_ref != aria.identity.face_embedding_ref
    assert maya.identity.voice_model_id != david.identity.voice_model_id
    assert aria.speech.accent != david.speech.accent
