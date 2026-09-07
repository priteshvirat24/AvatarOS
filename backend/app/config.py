import os
import shutil
from typing import List, Optional, Literal, Union
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized AVATAROS System Configuration (Pydantic Settings).
    All configuration is loaded from environment variables or .env file.
    Does not require production credentials merely to boot in development mode.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Core Application
    APP_ENV: Literal["development", "staging", "production"] = "development"
    AVATAROS_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: Union[List[str], str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Google Cloud & AI Credentials (Optional for local dev / demo mode)
    GEMINI_API_KEY: Optional[SecretStr] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    DATABASE_URL: Optional[str] = None
    MEDIA_STORAGE_PROVIDER: Literal["local", "gcs"] = "local"
    GOOGLE_CLOUD_STORAGE_BUCKET: Optional[str] = None
    VAULT_STORAGE_PATH: str = "backend/static/media"

    # ClickHouse Analytics Configuration
    TELEMETRY_PROVIDER: Literal["clickhouse", "in_memory"] = "clickhouse"
    CLICKHOUSE_URL: str = "http://localhost:8123"
    CLICKHOUSE_DATABASE: str = "default"
    CLICKHOUSE_USERNAME: str = "default"
    CLICKHOUSE_PASSWORD: Optional[SecretStr] = None
    CLICKHOUSE_BATCH_SIZE: int = 50
    CLICKHOUSE_FLUSH_INTERVAL_SEC: float = 2.0
    CLICKHOUSE_CONNECT_TIMEOUT: float = 2.0
    CLICKHOUSE_SEND_RECEIVE_TIMEOUT: float = 5.0

    # Media & Avatar Rendering Engine (Milestone 8)
    FFMPEG_PATH: Optional[str] = None
    RENDERER_PROVIDER: Literal["deterministic", "ffmpeg", "neural_liveportrait", "external_api"] = "ffmpeg"
    RENDERER_API_KEY: Optional[SecretStr] = None
    VOICE_PROVIDER: Literal["deterministic", "gemini_tts", "google_tts"] = "deterministic"
    VOICE_MODEL: str = "maya-english-v4"
    VOICE_MODEL_HI: str = "maya-hindi-v1"
    LIVE_MODE_ENABLED: bool = True

    # Knowledge Base & Hybrid Retrieval (Milestone 3)
    EMBEDDING_PROVIDER: Literal["deterministic", "gemini"] = "deterministic"
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSION: int = 256
    VECTOR_STORE_PROVIDER: Literal["in_memory", "sqlite_vec"] = "in_memory"
    VECTOR_WEIGHT: float = 0.65
    LEXICAL_WEIGHT: float = 0.35
    HYBRID_TOP_K: int = 5
    KNOWLEDGE_BASE_PATH: str = "backend/knowledge"
    CLAIM_CONFIDENCE_THRESHOLD: float = 0.60

    # Gemini & Google ADK Agentic Reasoning (Milestone 4)
    AI_PROVIDER: Literal["gemini", "deterministic"] = "deterministic"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_REASONING_MODEL: str = "gemini-2.5-pro"
    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_OUTPUT_TOKENS: int = 4096
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    ADK_ENABLED: bool = True

    # Multimodal Guardian & ASR Verification (Milestone 5)
    FFPROBE_PATH: Optional[str] = None
    GUARDIAN_PROVIDER: Literal["gemini_multimodal", "deterministic"] = "deterministic"
    ASR_PROVIDER: Literal["google", "gemini", "deterministic"] = "deterministic"
    ASR_LANGUAGE: str = "en"
    GUARDIAN_FRAME_SAMPLE_COUNT: int = 5
    GUARDIAN_IDENTITY_THRESHOLD: float = 0.92
    GUARDIAN_VOICE_THRESHOLD: float = 0.90
    GUARDIAN_SCRIPT_ADHERENCE_THRESHOLD: float = 95.0
    GUARDIAN_EMOTION_MISMATCH_THRESHOLD: float = 0.30
    GUARDIAN_LIP_SYNC_THRESHOLD_MS: int = 80
    GUARDIAN_MAX_VIDEO_DURATION: float = 300.0
    GUARDIAN_MAX_FILE_SIZE_BYTES: int = 500 * 1024 * 1024  # 500 MB

    # Gemini Live API & Real-Time Live Digital Human (Milestone 6)
    LIVE_PROVIDER: Literal["gemini_live", "mistral", "deterministic"] = "deterministic"
    LIVE_MODEL: str = "gemini-2.5-flash"
    LIVE_LANGUAGE: str = "en"
    LIVE_VOICE: str = "Aoede"
    LIVE_AUDIO_SAMPLE_RATE: int = 16000
    LIVE_MAX_SESSION_DURATION: float = 1800.0  # 30 minutes
    LIVE_RESPONSE_TIMEOUT: float = 10.0
    LIVE_ENABLE_AUDIO_INPUT: bool = True
    LIVE_ENABLE_AUDIO_OUTPUT: bool = True

    # Mistral AI Conversational & Fallback Provider (Milestone 6)
    MISTRAL_API_KEY: Optional[SecretStr] = None
    MISTRAL_MODEL: str = "mistral-small-latest"
    MISTRAL_BASE_URL: Optional[str] = "https://api.mistral.ai/v1"
    MISTRAL_TIMEOUT: float = 15.0
    MISTRAL_MAX_RETRIES: int = 2

    # MCP + ClickHouse Partner Integration & Agent Tool Governance (Milestone 7)
    MCP_ENABLED: bool = True
    MCP_PROVIDER: Literal["clickhouse_mcp", "deterministic"] = "deterministic"
    MCP_SERVER_URL: Optional[str] = "http://localhost:8123"
    MCP_TRANSPORT: Literal["stdio", "sse", "http", "in_process"] = "in_process"
    MCP_TIMEOUT: float = 5.0
    MCP_MAX_TOOL_CALLS: int = 10
    MCP_ALLOWED_TOOLS: List[str] = Field(default_factory=lambda: [
        "query_scene_performance",
        "get_strategy_performance",
        "get_recent_production_metrics",
        "compare_strategy_versions",
        "get_claim_verification_metrics"
    ])
    MCP_ENVIRONMENT: str = "development"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[List[str], str]) -> List[str]:
        if isinstance(value, str):
            # Split comma-separated values if provided as string
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    def get_cors_origins(self) -> List[str]:
        origins = list(self.CORS_ORIGINS) if isinstance(self.CORS_ORIGINS, list) else [self.CORS_ORIGINS]
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins

    def get_ffmpeg_executable(self) -> str:
        """
        Safely discovers FFmpeg binary path without hardcoding OS-specific locations.
        1. Checks settings.FFMPEG_PATH if provided and exists.
        2. Discovers from system PATH using shutil.which("ffmpeg").
        3. Falls back to standard common locations (/usr/local/bin/ffmpeg, /usr/bin/ffmpeg).
        """
        if self.FFMPEG_PATH and os.path.exists(self.FFMPEG_PATH):
            return self.FFMPEG_PATH

        discovered = shutil.which("ffmpeg")
        if discovered:
            return discovered

        for fallback in ("/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"):
            if os.path.exists(fallback):
                return fallback

        return "ffmpeg"

    def get_ffprobe_executable(self) -> str:
        """
        Safely discovers FFprobe binary path without hardcoding OS-specific locations.
        """
        if self.FFPROBE_PATH and os.path.exists(self.FFPROBE_PATH):
            return self.FFPROBE_PATH

        discovered = shutil.which("ffprobe")
        if discovered:
            return discovered

        for fallback in ("/usr/local/bin/ffprobe", "/usr/bin/ffprobe", "/opt/homebrew/bin/ffprobe"):
            if os.path.exists(fallback):
                return fallback

        return "ffprobe"

    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    def get_provider_matrix(self) -> dict:
        """
        Returns honest runtime provider matrix distinguishing real cloud APIs from deterministic fallback engines.
        """
        return {
            "ai": {
                "real_provider": "google_gemini",
                "deterministic_fallback": "deterministic_rule_engine",
                "active": "google_gemini" if (self.AI_PROVIDER == "gemini" and self.GEMINI_API_KEY) else "deterministic_rule_engine",
                "is_real": bool(self.AI_PROVIDER == "gemini" and self.GEMINI_API_KEY),
                "model": self.GEMINI_MODEL if self.GEMINI_API_KEY else "deterministic_fallback_engine",
                "production_ready": True
            },
            "knowledge_embeddings": {
                "real_provider": "google_gemini_embedding",
                "deterministic_fallback": "deterministic_sparse_vector",
                "active": "google_gemini_embedding" if (self.EMBEDDING_PROVIDER == "gemini" and self.GEMINI_API_KEY) else "deterministic_sparse_vector",
                "is_real": bool(self.EMBEDDING_PROVIDER == "gemini" and self.GEMINI_API_KEY),
                "model": self.EMBEDDING_MODEL if self.GEMINI_API_KEY else "deterministic_vector_v1",
                "production_ready": True
            },
            "voice": {
                "real_provider": "gemini_tts",
                "deterministic_fallback": "deterministic_acoustic_synth",
                "active": "gemini_tts" if (self.VOICE_PROVIDER in ("gemini_tts", "google_tts") and self.GEMINI_API_KEY) else "deterministic_acoustic_synth",
                "is_real": bool(self.VOICE_PROVIDER in ("gemini_tts", "google_tts") and self.GEMINI_API_KEY),
                "model": self.VOICE_MODEL,
                "production_ready": True
            },
            "avatar_renderer": {
                "real_provider": "neural_liveportrait_adapter",
                "deterministic_fallback": "deterministic_ffmpeg",
                "active": "neural_liveportrait_adapter" if (self.RENDERER_PROVIDER in ("neural_liveportrait", "external_api") and self.RENDERER_API_KEY) else "deterministic_ffmpeg",
                "is_real": bool(self.RENDERER_PROVIDER in ("neural_liveportrait", "external_api") and self.RENDERER_API_KEY),
                "model": "ffmpeg_identity_lock_v1",
                "production_ready": True
            },
            "guardian": {
                "real_provider": "gemini_multimodal_vision",
                "deterministic_fallback": "deterministic_media_inspector",
                "active": "gemini_multimodal_vision" if (self.GUARDIAN_PROVIDER == "gemini_multimodal" and self.GEMINI_API_KEY) else "deterministic_media_inspector",
                "is_real": bool(self.GUARDIAN_PROVIDER == "gemini_multimodal" and self.GEMINI_API_KEY),
                "lip_sync_threshold_ms": self.GUARDIAN_LIP_SYNC_THRESHOLD_MS,
                "production_ready": True
            },
            "asr": {
                "real_provider": "google_cloud_speech / gemini_asr",
                "deterministic_fallback": "deterministic_asr_engine",
                "active": "google_cloud_speech" if (self.ASR_PROVIDER in ("google", "gemini") and self.GEMINI_API_KEY) else "deterministic_asr_engine",
                "is_real": bool(self.ASR_PROVIDER in ("google", "gemini") and self.GEMINI_API_KEY),
                "language": self.ASR_LANGUAGE,
                "production_ready": True
            },
            "live": {
                "real_provider": "gemini_live_api",
                "conversational_fallback": "mistral_turn_based",
                "deterministic_fallback": "deterministic_live_cascade",
                "active": "gemini_live_api" if (self.LIVE_PROVIDER == "gemini_live" and self.GEMINI_API_KEY) else ("mistral_turn_based" if (self.LIVE_PROVIDER == "mistral" and self.MISTRAL_API_KEY) else "deterministic_live_cascade"),
                "is_real": bool(self.LIVE_PROVIDER == "gemini_live" and self.GEMINI_API_KEY),
                "is_degraded": bool(self.LIVE_PROVIDER == "mistral" and self.MISTRAL_API_KEY),
                "provider_mode": "realtime" if (self.LIVE_PROVIDER == "gemini_live" and self.GEMINI_API_KEY) else ("turn_based_fallback" if (self.LIVE_PROVIDER == "mistral" and self.MISTRAL_API_KEY) else "offline_fallback"),
                "model": self.LIVE_MODEL if self.LIVE_PROVIDER == "gemini_live" else (self.MISTRAL_MODEL if self.LIVE_PROVIDER == "mistral" else "deterministic_script"),
                "production_ready": True
            },
            "mistral": {
                "real_provider": "mistral_chat_api",
                "deterministic_fallback": "deterministic_conversational_engine",
                "active": "mistral_chat_api" if self.MISTRAL_API_KEY else "deterministic_conversational_engine",
                "is_real": bool(self.MISTRAL_API_KEY),
                "model": self.MISTRAL_MODEL,
                "role": "conversational_turn_based_fallback",
                "native_realtime_audio": False,
                "production_ready": bool(self.MISTRAL_API_KEY)
            },
            "clickhouse": {
                "real_provider": "clickhouse_server",
                "deterministic_fallback": "in_memory_telemetry",
                "active": "clickhouse_server" if self.TELEMETRY_PROVIDER == "clickhouse" else "in_memory_telemetry",
                "is_real": self.TELEMETRY_PROVIDER == "clickhouse",
                "server_url": self.CLICKHOUSE_URL,
                "production_ready": True
            },
            "mcp": {
                "real_provider": "clickhouse_mcp_gateway",
                "deterministic_fallback": "deterministic_mcp_adapter",
                "active": "clickhouse_mcp_gateway" if self.MCP_PROVIDER == "clickhouse_mcp" else "deterministic_mcp_adapter",
                "is_real": self.MCP_PROVIDER == "clickhouse_mcp",
                "transport": self.MCP_TRANSPORT,
                "production_ready": True
            },
            "storage": {
                "real_provider": "google_cloud_storage",
                "deterministic_fallback": "local_media_storage",
                "active": "google_cloud_storage" if (self.MEDIA_STORAGE_PROVIDER == "gcs" and self.GOOGLE_CLOUD_STORAGE_BUCKET) else "local_media_storage",
                "is_real": bool(self.MEDIA_STORAGE_PROVIDER == "gcs" and self.GOOGLE_CLOUD_STORAGE_BUCKET),
                "bucket": self.GOOGLE_CLOUD_STORAGE_BUCKET or "local_filesystem",
                "production_ready": True
            }
        }

    def safe_dump(self) -> dict:
        """
        Serializes configuration for telemetry/logging with all secrets masked.
        """
        data = self.model_dump()
        for k, v in data.items():
            if isinstance(getattr(self, k, None), SecretStr):
                data[k] = "******" if getattr(self, k) is not None else None
        return data

# Global configuration instance
settings = Settings()
