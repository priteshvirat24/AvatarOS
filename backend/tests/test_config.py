import os
from pydantic import SecretStr
from backend.app.config import Settings, settings
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_settings_development_defaults():
    s = Settings()
    assert s.APP_ENV == "development"
    assert s.DEBUG is True
    assert s.PORT == 8000
    assert "http://localhost:3000" in s.get_cors_origins()
    assert s.RENDERER_PROVIDER == "ffmpeg"
    assert s.LIVE_MODE_ENABLED is True

def test_boots_without_any_cloud_credentials():
    """
    The system must start with no API keys at all, and report that honestly.

    Asserted against an explicitly credential-free Settings rather than the
    ambient environment, so the result does not change depending on whether the
    developer running the suite happens to have a key in their .env.
    """
    s = Settings(_env_file=None, GEMINI_API_KEY=None, CLICKHOUSE_PASSWORD=None)

    assert s.GEMINI_API_KEY is None
    matrix = s.get_provider_matrix()
    # With no credential, nothing may claim to be a real provider.
    assert matrix["ai"]["is_real"] is False
    assert matrix["ai"]["active"] == "deterministic_rule_engine"
    assert matrix["live"]["is_real"] is False


def test_empty_string_credential_is_treated_as_absent():
    """
    `GEMINI_API_KEY=` in a .env produces SecretStr(''), which is a truthy object.
    Left unhandled, every `bool(settings.GEMINI_API_KEY)` check reports a live
    Gemini connection backed by no credential.
    """
    s = Settings(_env_file=None, GEMINI_API_KEY="   ", CLICKHOUSE_PASSWORD="")

    assert s.GEMINI_API_KEY is None
    assert s.CLICKHOUSE_PASSWORD is None
    assert s.get_provider_matrix()["ai"]["is_real"] is False

def test_environment_variable_overrides():
    s = Settings(
        APP_ENV="staging",
        PORT=9000,
        FRONTEND_URL="https://studio.avataros.dev",
        CORS_ORIGINS="https://studio.avataros.dev, http://localhost:5173"
    )
    assert s.APP_ENV == "staging"
    assert s.PORT == 9000
    origins = s.get_cors_origins()
    assert "https://studio.avataros.dev" in origins
    assert "http://localhost:5173" in origins

def test_cors_origins_parsing():
    # Comma-separated string parsing
    s = Settings(CORS_ORIGINS="http://site1.com, http://site2.com")
    origins = s.get_cors_origins()
    assert "http://site1.com" in origins
    assert "http://site2.com" in origins

def test_ffmpeg_executable_discovery():
    s = Settings()
    exe = s.get_ffmpeg_executable()
    assert exe is not None
    assert len(exe) > 0
    # Custom override
    s_custom = Settings(FFMPEG_PATH="/usr/bin/custom_ffmpeg")
    # If not on disk, falls back to discovered or fallback string
    assert s_custom.get_ffmpeg_executable() is not None

def test_clickhouse_configuration():
    s = Settings(
        CLICKHOUSE_URL="http://clickhouse-node:8123",
        CLICKHOUSE_DATABASE="analytics",
        CLICKHOUSE_USERNAME="writer"
    )
    assert s.CLICKHOUSE_URL == "http://clickhouse-node:8123"
    assert s.CLICKHOUSE_DATABASE == "analytics"
    assert s.CLICKHOUSE_USERNAME == "writer"

def test_secret_masking_no_plaintext_leak():
    s = Settings(
        GEMINI_API_KEY=SecretStr("super-secret-api-key-12345"),
        CLICKHOUSE_PASSWORD=SecretStr("secret-ch-password-999")
    )
    # repr and str of SecretStr must mask the value
    assert "super-secret-api-key-12345" not in str(s.GEMINI_API_KEY)
    assert "super-secret-api-key-12345" not in repr(s)
    
    # safe_dump() must mask all secret fields with asterisks
    dumped = s.safe_dump()
    assert dumped["GEMINI_API_KEY"] == "******"
    assert dumped["CLICKHOUSE_PASSWORD"] == "******"

def test_health_endpoints():
    # Backwards-compatible root endpoint
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "online"
    assert res_root.json()["version"] in ("1.0.0", "1.7.0", settings.AVATAROS_VERSION)

    # Multi-service health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data = res_health.json()
    assert "services" in data
    assert data["services"]["application"] == "healthy"
    assert "clickhouse" in data["services"]
    assert "ai_provider" in data["services"]

    # Readiness probe
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["ready"] is True
