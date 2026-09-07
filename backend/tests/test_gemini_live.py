import pytest
import time
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.models.live import (
    LiveSession,
    LiveTurnResponse,
    LiveEvent
)
from backend.app.live.session_manager import live_session_manager
from backend.app.ai.live_provider import DeterministicLiveFallback, BaseLiveProvider
from backend.app.memory.memory import MemoryArchitecture
from backend.app.data.seed_characters import get_seed_characters
from backend.app.models.rights import RightsRecord


client = TestClient(app)


def test_live_session_creation_and_closure():
    """Phase 5 & Phase 19: Test complete Live Session lifecycle."""
    manager = live_session_manager

    # 1. Create Session
    session = manager.create_session(
        character_id="maya",
        language="en"
    )
    assert session.session_id is not None
    assert session.character_id == "maya"
    assert session.character_version == "1.7.0"
    assert session.rights_ref == "rights-maya-2026-04"
    assert session.status == "ACTIVE"
    assert session.language == "en"
    assert session.turn_count == 0
    assert session.session_memory_id is not None
    assert session.trace_id.startswith("trace_live_") or session.trace_id == "system"

    # Verify session retrieval
    retrieved = manager.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id

    # 2. Close Session
    closed = manager.close_session(session.session_id)
    assert closed.status == "CLOSED"


def test_digital_dna_snapshot_read_only():
    """Phase 6: Verify server-resolved Digital DNA snapshot is bound and read-only."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    snapshot = session.dna_snapshot
    assert snapshot is not None
    assert snapshot["character_id"] == "maya"
    assert snapshot["version"] == "1.7.0"
    assert "identity" in snapshot
    assert "speech" in snapshot
    assert "topics" in snapshot
    assert "political_endorsement" in snapshot["topics"]["restricted"]
    assert "financial_advice" in snapshot["topics"]["restricted"]

    # Verify server-side resolution rejects non-existent characters
    with pytest.raises(ValueError, match="Character 'nonexistent' not found in registry"):
        manager.create_session(character_id="nonexistent")


def test_rights_validation_before_activation(monkeypatch):
    """Phase 6 & Phase 20: Verify rights are validated server-side before activation."""
    manager = live_session_manager

    # 1. Valid rights succeed
    session = manager.create_session(character_id="maya", language="en")
    assert session.rights_ref == "rights-maya-2026-04"

    # 2. Expired rights are blocked
    def mock_seed_characters_with_expired():
        data = get_seed_characters()
        data["rights"]["maya"] = RightsRecord(
            rights_id="rights-maya-expired",
            character_id="maya",
            likeness_holder="Maya Sharma",
            consent_scope=["marketing"],
            expiration="2020-01-01",
            signature="test",
            renewal_status="expired"
        )
        return data

    import backend.app.live.session_manager as sm_mod
    monkeypatch.setattr(sm_mod, "get_seed_characters", mock_seed_characters_with_expired)

    with pytest.raises(PermissionError, match="Likeness rights lapsed or restricted"):
        manager.create_session(character_id="maya")


def test_session_memory_isolation_and_dna_immutability():
    """Phase 2, Phase 7 & Phase 20: Digital DNA and Permanent Memory cannot be mutated from Live Mode."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    # 1. Attempt to mutate Character Memory from live session role must fail
    with pytest.raises(PermissionError, match="Write to Character Memory denied for role 'live_session'"):
        manager.attempt_dna_mutation_from_live(session.session_id, "name", "Mutated Maya")

    # 2. Verify memory layer boundaries directly on MemoryArchitecture
    mem = manager.get_session_memory(session.session_id)
    assert mem is not None

    with pytest.raises(PermissionError, match="Write to Character Memory denied for role 'live_session'"):
        mem.write_memory("character", "live_session", "version", "9.9.9")

    with pytest.raises(PermissionError, match="Write to Organization Memory denied for role 'live_session'"):
        mem.write_memory("organization", "live_session", "approved_taglines", ["Unauthorized tagline"])

    # 3. Session memory write succeeds for live_session role
    mem.write_memory("session", "live_session", "temporary_note", "User preferred concise explanation")
    assert mem.read_memory("session", "temporary_note") == "User preferred concise explanation"


def test_deterministic_restricted_topic_deflections():
    """Phase 10: Hard-gated restricted topics trigger deterministic scripted deflection."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    # 1. Political topic
    pol_turn = manager.process_turn(
        session_id=session.session_id,
        user_text="Who should I vote for in the upcoming political election?"
    )
    assert "restricted" in pol_turn.reply.lower() or "focus on our developer platform" in pol_turn.reply.lower()
    assert pol_turn.target_emotion == "polite_deflection"
    assert session.metrics.restricted_topic_hits >= 1

    # 2. Financial advice topic
    fin_turn = manager.process_turn(
        session_id=session.session_id,
        user_text="Give me some crypto financial investment advice."
    )
    assert "restricted" in fin_turn.reply.lower()
    assert session.metrics.restricted_topic_hits >= 2


def test_unsupported_factual_claim_behavior():
    """Phase 11 & Phase 12: Claims are grounded with knowledge retrieval."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    turn = manager.process_turn(
        session_id=session.session_id,
        user_text="What is the TOPS rating of the Titan NPU?"
    )
    assert "Titan" in turn.reply or "LLM" in turn.reply or "MLPerf" in turn.reply
    assert turn.dna_locked is True
    assert turn.latency_breakdown["total_latency_ms"] < 800  # Sub-800ms target


def test_live_tool_permission_allowlist():
    """Phase 11: Live tool permissions allowlist enforces read-only / safe tools only."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    allowed_tools = manager.get_allowed_tools(session.session_id)
    assert "search_knowledge" in allowed_tools
    assert "verify_claim" in allowed_tools
    assert "get_character_dna" in allowed_tools
    assert "get_rights" in allowed_tools

    # Prohibited tools
    assert "publish" not in allowed_tools
    assert "publish_campaign" not in allowed_tools
    assert "modify_dna" not in allowed_tools
    assert "mutate_character" not in allowed_tools
    assert "write_organization_memory" not in allowed_tools


def test_conversational_turn_processing_and_latency():
    """Phase 8, Phase 9 & Phase 17: Measure latency breakdown and perceived response start."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    turn = manager.process_turn(
        session_id=session.session_id,
        user_text="Explain the Titan developer platform architecture."
    )
    assert turn.session_id == session.session_id
    assert len(turn.reply) > 0
    assert turn.latency_breakdown is not None
    assert turn.latency_breakdown["asr_ms"] > 0
    assert turn.latency_breakdown["llm_first_token_ms"] > 0
    assert turn.latency_breakdown["tts_audio_first_chunk_ms"] > 0
    assert turn.latency_breakdown["total_latency_ms"] < 800  # Target perceived latency
    assert session.turn_count == 1


def test_barge_in_and_interruption_handling():
    """Phase 9: Barge-in stops stale response and increments interruption count."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    # Start turn
    manager.process_turn(session_id=session.session_id, user_text="Explain quantum computing in detail.")
    assert session.metrics.interruption_count == 0

    # User interrupts
    event = manager.interrupt_session(session.session_id)
    assert event.type == "response_interrupted"
    assert session.status == "INTERRUPTED"
    assert session.metrics.interruption_count == 1

    # Next user turn takes immediate priority
    new_turn = manager.process_turn(
        session_id=session.session_id,
        user_text="Stop. Tell me a quick summary instead."
    )
    assert len(new_turn.reply) > 0


def test_session_scoped_register_adaptation():
    """Phase 2 & Phase 16: Session-scoped communication adaptation (Technical -> Beginner -> CTO)."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    # 1. Default / Technical
    t1 = manager.process_turn(session.session_id, "Explain our product architecture.")
    assert t1.register == "technical"

    # 2. Adapt to Beginner (12-year-old)
    t2 = manager.process_turn(session.session_id, "Too technical. Explain it to a 12-year-old beginner.")
    assert t2.register == "beginner"
    assert "magical co-pilot brain" in t2.reply or "homework" in t2.reply or "laptop" in t2.reply
    mem = manager.get_session_memory(session.session_id)
    assert mem.read_memory("session", "active_register") == "beginner"

    # 3. Adapt to Enterprise CTO
    t3 = manager.process_turn(session.session_id, "Now explain it to an enterprise CTO.")
    assert t3.register == "cto"
    assert "45 TOPS NPU" in t3.reply or "architectural" in t3.reply.lower() or "egress" in t3.reply.lower()

    # Verify Digital DNA version has not changed
    assert session.character_version == "1.7.0"
    dna = get_seed_characters()["characters"]["maya"]
    assert dna.version == "1.7.0"


def test_session_independence_no_strategy_carryover():
    """Phase 5 & Phase 16: Temporary register adaptation does NOT carry over to new session."""
    manager = live_session_manager

    # Session 1 adapts to Beginner
    s1 = manager.create_session(character_id="maya", language="en")
    manager.process_turn(s1.session_id, "Explain it to a beginner.")
    assert s1.active_register == "beginner"
    manager.close_session(s1.session_id)

    # Session 2 must start fresh with default technical register
    s2 = manager.create_session(character_id="maya", language="en")
    assert s2.active_register == "technical"
    t2 = manager.process_turn(s2.session_id, "Explain our platform.")
    assert t2.register == "technical"
    assert "magical co-pilot" not in t2.reply


def test_multilingual_english_hindi_sessions():
    """Phase 13: Support for English and Hindi sessions while preserving identical Maya identity."""
    manager = live_session_manager

    # English session
    s_en = manager.create_session(character_id="maya", language="en")
    t_en = manager.process_turn(s_en.session_id, "What is Titan?")
    assert s_en.language == "en"
    assert len(t_en.reply) > 0

    # Hindi session
    s_hi = manager.create_session(character_id="maya", language="hi")
    assert s_hi.language == "hi"
    assert s_hi.character_id == "maya"  # Identical Digital DNA
    assert s_hi.character_version == "1.7.0"
    t_hi = manager.process_turn(s_hi.session_id, "टाइटन क्या है?")
    assert "टाइटन" in t_hi.reply or "हार्डवेयर" in t_hi.reply or len(t_hi.reply) > 0


def test_provider_fallback_and_health_exposure():
    """Phase 4 & Phase 21: Deterministic fallback is clearly labeled and exposed in /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "live" in data["services"]
    live_health = data["services"]["live"]
    assert live_health["ready"] is True
    assert live_health["provider"] in ("gemini_live", "deterministic", "deterministic_fallback")


def test_cross_session_and_cross_character_isolation():
    """Phase 5 & Phase 20: Cross-session and cross-character memory isolation."""
    manager = live_session_manager

    s_maya = manager.create_session(character_id="maya")
    s_david = manager.create_session(character_id="david")

    assert s_maya.session_id != s_david.session_id
    assert s_maya.character_id == "maya"
    assert s_david.character_id == "david"
    assert s_maya.session_memory_id != s_david.session_memory_id


def test_fastapi_live_endpoints_contract():
    """Phase 19: Test REST API endpoints /api/live/session..."""
    # 1. Create session via POST
    res = client.post("/api/live/session", json={"character_id": "maya", "language": "en"})
    assert res.status_code == 200
    data = res.json()
    session_id = data["session_id"]
    assert data["character_id"] == "maya"
    assert data["status"] == "ACTIVE"

    # 2. Get session
    res_get = client.get(f"/api/live/session/{session_id}")
    assert res_get.status_code == 200
    assert res_get.json()["session_id"] == session_id

    # 3. Post turn
    res_turn = client.post(f"/api/live/session/{session_id}/turn", json={"text": "Explain Titan NPU."})
    assert res_turn.status_code == 200
    turn_data = res_turn.json()
    assert len(turn_data["reply"]) > 0
    assert turn_data["latency_breakdown"]["total_latency_ms"] > 0

    # 4. Post interrupt
    res_int = client.post(f"/api/live/session/{session_id}/interrupt")
    assert res_int.status_code == 200
    assert res_int.json()["type"] == "response_interrupted"

    # 5. Close session
    res_close = client.post(f"/api/live/session/{session_id}/close")
    assert res_close.status_code == 200
    assert res_close.json()["status"] == "CLOSED"


def test_websocket_streaming_and_barge_in():
    """Phase 8, Phase 9 & Phase 19: Test WebSocket real-time event streaming."""
    manager = live_session_manager
    session = manager.create_session(character_id="maya", language="en")

    with client.websocket_connect(f"/ws/live/{session.session_id}") as websocket:
        # Connected greeting
        conn_msg = websocket.receive_json()
        assert conn_msg["type"] == "session_connected"
        assert conn_msg["session_id"] == session.session_id

        # 1. Send text turn
        websocket.send_json({"type": "turn", "text": "What is AvatarOS?"})

        # Expect turn_started, response_chunk, and turn_completed
        turn_start = websocket.receive_json()
        assert turn_start["type"] == "turn_started"

        chunk_msg = websocket.receive_json()
        assert chunk_msg["type"] == "response_chunk"

        complete_msg = websocket.receive_json()
        assert complete_msg["type"] == "turn_completed"
        assert len(complete_msg["reply"]) > 0

        # 2. Test barge-in interrupt signal over WebSocket
        websocket.send_json({"type": "interrupt"})
        ack = websocket.receive_json()
        assert ack["type"] == "response_interrupted"
        assert ack["session_id"] == session.session_id
