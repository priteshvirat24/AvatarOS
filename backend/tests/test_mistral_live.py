import pytest
import time
from unittest.mock import MagicMock, patch
from pydantic import SecretStr
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.ai.live_provider import (
    MistralLiveProvider,
    GeminiLiveProvider,
    DeterministicLiveFallback,
    get_live_provider,
    BaseConversationalProvider,
    BaseLiveProvider
)
from backend.app.live.session_manager import LiveSessionManager
from backend.app.data.seed_characters import get_seed_characters
from backend.app.models.live import LiveSession

client = TestClient(app)


def test_mistral_provider_hierarchy():
    """Verify MistralLiveProvider implements BaseLiveProvider and BaseConversationalProvider."""
    assert issubclass(MistralLiveProvider, BaseLiveProvider)
    assert issubclass(MistralLiveProvider, BaseConversationalProvider)


def test_mistral_provider_initialization(monkeypatch):
    """Test MistralLiveProvider initialization with and without API key."""
    # 1. Unconfigured
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", None)
    provider = MistralLiveProvider()
    assert provider._client is None

    # 2. Configured
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))
    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_mistral_cls.return_value = mock_instance
        provider = MistralLiveProvider()
        assert provider._client is not None
        mock_mistral_cls.assert_called_once_with(api_key="test-mistral-key")


def test_mistral_session_creation(monkeypatch):
    """Verify Mistral creates sessions labeled honestly as degraded turn-based mode."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))
    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_mistral_cls.return_value = mock_instance
        provider = MistralLiveProvider()

        characters = get_seed_characters()["characters"]
        maya_dna = characters["maya"]

        session = provider.create_session(
            character_dna=maya_dna,
            rights_ref="rights-maya-2026-04",
            language="en",
            trace_id="test_mistral_trace"
        )

        assert session.session_id.startswith("live_")
        assert session.provider == "mistral"
        assert session.degraded_mode is True
        assert session.is_realtime is False
        assert session.character_id == "maya"
        assert session.character_version == "1.7.0"
        assert session.active_register == "technical"
        assert "political_endorsement" in session.dna_snapshot["topics"]["restricted"]


def test_mistral_restricted_topic_deflection(monkeypatch):
    """Verify deterministic restricted topic check deflects before calling Mistral API."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))
    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_mistral_cls.return_value = mock_instance
        provider = MistralLiveProvider()

        characters = get_seed_characters()["characters"]
        maya_dna = characters["maya"]
        session = provider.create_session(maya_dna, "rights-ref", "en")

        # Attempt to prompt for financial advice
        turn_res = provider.process_turn(session, "Can you provide some financial advice on crypto?")
        assert "restricted from providing financial advice" in turn_res.reply
        assert turn_res.target_emotion == "polite_deflection"
        assert turn_res.dna_locked is True
        assert turn_res.provider == "mistral"
        assert turn_res.degraded_mode is True
        # Verify the external API was NEVER called due to inline guardrail
        mock_instance.chat.complete.assert_not_called()


def test_mistral_turn_processing_mocked(monkeypatch):
    """Verify conversational turn generation invokes chat.complete with DNA constraints."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))
    monkeypatch.setattr(settings, "MISTRAL_MODEL", "mistral-small-latest")

    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "The Titan AI Laptop executes transformer operations locally on its 45 TOPS NPU."
        mock_response.choices = [mock_choice]
        mock_instance.chat.complete.return_value = mock_response
        mock_mistral_cls.return_value = mock_instance

        provider = MistralLiveProvider()
        characters = get_seed_characters()["characters"]
        maya_dna = characters["maya"]
        session = provider.create_session(maya_dna, "rights-ref", "en")

        turn_res = provider.process_turn(session, "Explain how Titan runs code locally.")
        assert turn_res.reply == "The Titan AI Laptop executes transformer operations locally on its 45 TOPS NPU."
        assert turn_res.provider == "mistral"
        assert turn_res.degraded_mode is True
        assert turn_res.character_version == "1.7.0"
        assert session.turn_count == 1
        assert len(session.transcript_history) == 2  # user + maya turns

        # Verify chat.complete was called with correct parameters
        mock_instance.chat.complete.assert_called_once()
        call_kwargs = mock_instance.chat.complete.call_args[1]
        assert call_kwargs["model"] == "mistral-small-latest"
        messages = call_kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert "Maya" in messages[0]["content"]
        assert "45 TOPS NPU" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Explain how Titan runs code locally."


def test_mistral_session_adaptation_beginner_and_cto(monkeypatch):
    """Verify session-scoped communication adaptation (beginner vs cto) within Mistral provider."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))

    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Adapted response from Mistral"
        mock_resp = MagicMock(choices=[mock_choice])
        mock_instance.chat.complete.return_value = mock_resp
        mock_mistral_cls.return_value = mock_instance

        provider = MistralLiveProvider()
        characters = get_seed_characters()["characters"]
        maya_dna = characters["maya"]
        session = provider.create_session(maya_dna, "rights-ref", "en")

        # 1. Adapt to beginner
        res_beginner = provider.process_turn(session, "Explain this to a beginner or 12-year-old.")
        assert session.active_register == "beginner"
        assert res_beginner.register == "beginner"
        assert res_beginner.target_emotion == "warm_enthusiastic"

        # 2. Adapt to CTO
        res_cto = provider.process_turn(session, "Now explain this from an enterprise CTO architecture perspective.")
        assert session.active_register == "cto"
        assert res_cto.register == "cto"
        assert res_cto.target_emotion == "authoritative_analytical"

        # 3. Verify underlying Digital DNA was NOT modified
        assert maya_dna.version == "1.7.0"
        assert session.character_version == "1.7.0"


def test_mistral_hindi_language_support(monkeypatch):
    """Verify Mistral provider supports Hindi session turns."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))

    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "टाइटन लैपटॉप स्थानीय एनपीयू पर 40% तेज़ी से काम करता है।"
        mock_resp = MagicMock(choices=[mock_choice])
        mock_instance.chat.complete.return_value = mock_resp
        mock_mistral_cls.return_value = mock_instance

        provider = MistralLiveProvider()
        characters = get_seed_characters()["characters"]
        maya_dna = characters["maya"]
        session = provider.create_session(maya_dna, "rights-ref", "hi")

        assert session.language == "hi"
        res = provider.process_turn(session, "टाइटन लैपटॉप के बारे में बताएं।")
        assert res.reply == "टाइटन लैपटॉप स्थानीय एनपीयू पर 40% तेज़ी से काम करता है।"
        assert res.transcript.language == "hi"

        call_kwargs = mock_instance.chat.complete.call_args[1]
        assert "Speak naturally and concisely in hi" in call_kwargs["messages"][0]["content"]


def test_mistral_fallback_on_api_error(monkeypatch):
    """Verify graceful fallback to deterministic cascade if Mistral API raises an exception."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))

    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_instance.chat.complete.side_effect = RuntimeError("Mistral API rate limit exceeded")
        mock_mistral_cls.return_value = mock_instance

        provider = MistralLiveProvider()
        characters = get_seed_characters()["characters"]
        maya_dna = characters["maya"]
        session = provider.create_session(maya_dna, "rights-ref", "en")

        # Turn should succeed by falling back to deterministic cascade without crashing
        res = provider.process_turn(session, "Tell me about Titan AI.")
        assert res is not None
        assert "Titan AI Laptop" in res.reply
        assert res.dna_locked is True


def test_provider_selection_gemini_to_mistral_fallback(monkeypatch):
    """Verify provider selection falls back from unconfigured Gemini Live to configured Mistral."""
    monkeypatch.setattr(settings, "LIVE_PROVIDER", "gemini_live")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))

    provider = get_live_provider()
    assert isinstance(provider, MistralLiveProvider)


def test_provider_selection_direct_mistral(monkeypatch):
    """Verify direct selection of Mistral provider via LIVE_PROVIDER='mistral'."""
    monkeypatch.setattr(settings, "LIVE_PROVIDER", "mistral")
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))

    provider = get_live_provider()
    assert isinstance(provider, MistralLiveProvider)


def test_provider_selection_offline_fallback(monkeypatch):
    """Verify fallback to DeterministicLiveFallback when neither Gemini nor Mistral are configured."""
    monkeypatch.setattr(settings, "LIVE_PROVIDER", "gemini_live")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", None)

    provider = get_live_provider()
    assert isinstance(provider, DeterministicLiveFallback)


def test_mistral_secret_hygiene_and_masking(monkeypatch):
    """Verify MISTRAL_API_KEY is masked in config, /health, and never leaked."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("super-secret-mistral-key-12345"))

    # 1. Check settings.safe_dump()
    dumped = settings.safe_dump()
    assert dumped["MISTRAL_API_KEY"] == "******"
    assert "super-secret-mistral-key-12345" not in str(dumped)

    # 2. Check /health endpoint
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "mistral" in data["services"]
    assert data["services"]["mistral"]["configured"] is True
    assert data["services"]["mistral"]["model"] == settings.MISTRAL_MODEL
    assert "api_key" not in data["services"]["mistral"]
    assert "super-secret-mistral-key-12345" not in res.text


def test_live_session_manager_integration(monkeypatch):
    """Test full session manager lifecycle with Mistral provider."""
    monkeypatch.setattr(settings, "MISTRAL_API_KEY", SecretStr("test-mistral-key"))

    with patch("backend.app.ai.live_provider.Mistral") as mock_mistral_cls:
        mock_instance = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Titan platform answers instantly."
        mock_resp = MagicMock(choices=[mock_choice])
        mock_instance.chat.complete.return_value = mock_resp
        mock_mistral_cls.return_value = mock_instance

        manager = LiveSessionManager(provider=MistralLiveProvider())
        session = manager.create_session(character_id="maya", language="en")

        assert session.provider == "mistral"
        assert session.degraded_mode is True
        assert session.is_realtime is False

        # Submit turn
        res = manager.process_turn(session.session_id, "How fast is Titan?")
        assert res.reply == "Titan platform answers instantly."

        # Interruption
        event = manager.interrupt_session(session.session_id)
        assert event.type == "response_interrupted"

        # Close session
        closed = manager.close_session(session.session_id)
        assert closed.status == "CLOSED"
