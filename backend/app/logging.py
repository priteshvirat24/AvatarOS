import logging
import json
import time
from typing import Optional, Dict, Any

REDACTED_KEYS = {
    "api_key", "password", "gemini_api_key", "renderer_api_key",
    "token", "secret", "authorization", "face_embedding", "speaker_embedding"
}

def sanitize_data(data: Any) -> Any:
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sensitive in k.lower() for sensitive in REDACTED_KEYS):
                sanitized[k] = "******"
            elif isinstance(v, (dict, list)):
                sanitized[k] = sanitize_data(v)
            else:
                sanitized[k] = v
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data

class StructuredLogger:
    def __init__(self, name: str = "avataros"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z"
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_operation(
        self,
        trace_id: str,
        operation: str,
        status: str,
        duration_ms: Optional[float] = None,
        agent_task: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        log_payload = {
            "trace_id": trace_id,
            "operation": operation,
            "status": status,
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
            "agent_task": agent_task,
            "details": sanitize_data(details) if details else None,
            "error": error
        }
        # Clean null values
        log_payload = {k: v for k, v in log_payload.items() if v is not None}
        message = json.dumps(log_payload, default=str)
        if error or status == "FAILED":
            self.logger.error(message)
        else:
            self.logger.info(message)

app_logger = StructuredLogger()
