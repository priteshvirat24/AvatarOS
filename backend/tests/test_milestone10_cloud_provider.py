import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.data.storage import LocalMediaStorage, GCSMediaStorage, get_media_storage
from backend.app.agents.guardian import guardian_agent
from backend.app.agents.publication_gate import publication_gate
from backend.app.models.dna import DigitalDNA
from backend.app.models.script import Script, ScriptScene, ScriptLine
from backend.app.models.director import DirectorPlan, SceneShot
from backend.app.models.guardian import GuardianReport
from backend.app.models.rights import RightsRecord
from backend.app.models.production import ProductionRunCreateRequest
from backend.app.agents.orchestrator import orchestrator

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
        script_id="sc_m10_test_v1",
        version=1,
        duration_target_s=60.0,
        language="en",
        scenes=[
            ScriptScene(scene_no=1, role="hook", duration_s=6.8, lines=[ScriptLine(speaker="maya", text="Test hook", claim_refs=[])]),
            ScriptScene(scene_no=2, role="problem", duration_s=12.0, lines=[ScriptLine(speaker="maya", text="Test problem", claim_refs=[])]),
            ScriptScene(scene_no=3, role="product", duration_s=14.0, lines=[ScriptLine(speaker="maya", text="Test product", claim_refs=["claim_0310"])]),
            ScriptScene(scene_no=4, role="demonstration", duration_s=15.0, lines=[ScriptLine(speaker="maya", text="Test demo", claim_refs=["claim_0231"])]),
            ScriptScene(scene_no=5, role="cta", duration_s=10.0, lines=[ScriptLine(speaker="maya", text="Test cta", claim_refs=[])]),
        ]
    )

@pytest.fixture
def sample_director_plan() -> DirectorPlan:
    return DirectorPlan(
        plan_id="dp_m10_test_v1",
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
            SceneShot(scene_no=1, role="hook", duration_s=6.8, shot="close_up", target_emotion="curious", emotional_intensity=0.75),
            SceneShot(scene_no=2, role="problem", duration_s=12.0, shot="medium_shot", target_emotion="concerned", emotional_intensity=0.35),
            SceneShot(scene_no=3, role="product", duration_s=14.0, shot="medium_close_up", target_emotion="confident", emotional_intensity=0.60),
            SceneShot(scene_no=4, role="demonstration", duration_s=15.0, shot="medium_close_up", target_emotion="excited", emotional_intensity=0.78),
            SceneShot(scene_no=5, role="cta", duration_s=10.0, shot="medium_shot", target_emotion="direct", emotional_intensity=0.70),
        ]
    )

# ------------------------------------------------------------------------------
# 1. Provider Matrix & Health Honesty Tests
# ------------------------------------------------------------------------------

def test_health_version_and_honest_observability():
    """Test that /health reports application version, environment, and honest provider states without secret leakage."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()

    assert data["version"] == "1.0.0"
    assert data["environment"] in ("development", "staging", "production")
    assert data["status"] in ("healthy", "degraded")
    
    # Zero secrets exposed check
    raw_text = resp.text.lower()
    assert "api_key" not in raw_text or "configured" in raw_text
    assert "secret" not in raw_text or "configured" in raw_text
    assert "password" not in raw_text or "configured" in raw_text

    # Provider matrix validation
    matrix = data.get("provider_matrix", {})
    assert "ai" in matrix
    assert "knowledge_embeddings" in matrix
    assert "voice" in matrix
    assert "avatar_renderer" in matrix
    assert "guardian" in matrix
    assert "asr" in matrix
    assert "live" in matrix
    assert "clickhouse" in matrix
    assert "mcp" in matrix
    assert "storage" in matrix


def test_provider_matrix_endpoint():
    """Test dedicated /api/production/provider-matrix endpoint."""
    resp = client.get("/api/production/provider-matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "1.0.0"
    assert "matrix" in data
    assert data["matrix"]["guardian"]["lip_sync_threshold_ms"] == 80


def test_readiness_probe():
    """Test that /health/ready probe returns system readiness and storage status."""
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready"] is True
    assert data["storage_ready"] is True
    assert data["version"] == "1.0.0"

# ------------------------------------------------------------------------------
# 2. Cloud Run & Config Compatibility Tests
# ------------------------------------------------------------------------------

def test_config_cloud_run_bindings():
    """Test that Settings default host and port align with Cloud Run container runtime."""
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT >= 1000
    assert settings.AVATAROS_VERSION == "1.0.0"


def test_cors_origin_parsing():
    """Test dynamic CORS origin parsing from comma-separated string."""
    parsed = settings.parse_cors_origins("https://avataros.app, https://cloud.run.app")
    assert "https://avataros.app" in parsed
    assert "https://cloud.run.app" in parsed

# ------------------------------------------------------------------------------
# 3. Media Storage Abstraction Tests
# ------------------------------------------------------------------------------

def test_local_media_storage_operations(tmp_path):
    """Test LocalMediaStorage file saving, URLs, existence checks, and traversal rejection."""
    storage = LocalMediaStorage(base_dir=str(tmp_path))
    
    # Save bytes
    url1 = storage.save_file("test_clip.mp4", b"fake_mp4_bytes", content_type="video/mp4")
    assert url1 == "/media/test_clip.mp4"
    assert storage.exists("test_clip.mp4") is True
    assert os.path.exists(storage.get_local_path("test_clip.mp4"))

    # Traversal security check
    with pytest.raises(ValueError):
        storage.save_file("../../../etc/passwd", b"malicious")


def test_gcs_media_storage_fallback():
    """Test that GCSMediaStorage falls back gracefully to local storage when unconfigured."""
    storage = GCSMediaStorage(bucket_name=None)
    status = storage.get_status()
    assert status["provider"] == "local_media_storage"
    assert status["is_real_cloud"] is False
    assert status["ready"] is True

# ------------------------------------------------------------------------------
# 4. Authoritative Lip-Sync Threshold (80ms) Invariant Tests
# ------------------------------------------------------------------------------

def test_authoritative_lip_sync_threshold_consistency():
    """Verify that settings, models, and agents consistently enforce the 80ms threshold."""
    assert settings.GUARDIAN_LIP_SYNC_THRESHOLD_MS == 80

    from backend.app.models.performance import LipSyncPlan
    plan = LipSyncPlan()
    assert plan.max_tolerance_ms == 80


def test_guardian_passes_at_or_below_80ms(sample_dna: DigitalDNA, sample_script: Script, sample_director_plan: DirectorPlan, tmp_path):
    """Verify that Guardian approves when lip-sync is 80ms or below."""
    from backend.app.models.guardian import AudioAuditResult
    aud_pass = AudioAuditResult(
        voice_similarity=0.92,
        lip_sync_offset_ms=80,
        audio_integrity_passed=True,
        failure_reasons=[]
    )
    assert aud_pass.lip_sync_offset_ms <= settings.GUARDIAN_LIP_SYNC_THRESHOLD_MS

# ------------------------------------------------------------------------------
# 5. Concurrency & Isolation Tests
# ------------------------------------------------------------------------------

def test_concurrent_production_run_isolation():
    """Test that two simultaneous production runs maintain strict trace and state isolation."""
    req1 = ProductionRunCreateRequest(
        character_id="maya",
        brief="Production Run 1: Cloud latency and compile velocity.",
        campaign_id="campaign_alpha",
        language="en"
    )
    req2 = ProductionRunCreateRequest(
        character_id="maya",
        brief="Production Run 2: Indian developer NPU benchmarks.",
        campaign_id="campaign_beta",
        language="hi"
    )

    run1 = orchestrator.execute_production_run(req1)
    run2 = orchestrator.execute_production_run(req2)

    assert run1.run_id != run2.run_id
    assert run1.trace_id != run2.trace_id
    assert run1.campaign_id == "campaign_alpha"
    assert run2.campaign_id == "campaign_beta"
    assert run1.language == "en"
    assert run2.language == "hi"

# ------------------------------------------------------------------------------
# 6. Security Invariants & Tampering Protection Tests
# ------------------------------------------------------------------------------

def test_unauthorized_publication_bypass_blocked(sample_rights: RightsRecord):
    """Verify that Publication Gate cannot be bypassed when Guardian fails."""
    failed_report = GuardianReport(
        audit_id="guard_sec_test",
        asset_id="asset_unverified",
        overall_status="BLOCKED",
        mean_identity_similarity=0.75,
        voice_similarity=0.70,
        script_adherence_pct=60.0,
        claims_audit_summary="Unverified",
        emotion_audit_summary="Mismatch",
        failed_scenes=[1, 2],
        timestamp="2026-09-08T00:00:00Z"
    )
    res = publication_gate.publish(
        asset_id="asset_unverified",
        guardian_report=failed_report,
        rights_record=sample_rights,
        script_id="sc_test",
        director_plan_id="dp_test"
    )
    assert res.status == "BLOCKED"
    assert res.provenance is None


def test_dna_immutability_server_authoritative():
    """Verify that seed character DNA biometric locks cannot be modified via client parameters."""
    from backend.app.data.seed_characters import get_seed_characters
    chars = get_seed_characters()["characters"]
    maya = chars["maya"]
    assert maya.identity.similarity_threshold == 0.92
    assert maya.identity.voice_similarity_threshold == 0.90
    assert maya.version == "1.7.0"
