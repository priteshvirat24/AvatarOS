from typing import Dict, Any, Optional
from backend.app.models.dna import DigitalDNA

class MemoryArchitecture:
    """
    Implements Section 18:
    1. Character Memory (permanent identity)
    2. Organization Memory (company knowledge & brand)
    3. Session Memory (temporary context)
    Strict write-permission matrix enforced.
    """
    def __init__(self, character_dna: DigitalDNA, org_id: str = "example_co"):
        self.character_memory: DigitalDNA = character_dna
        self.org_memory: Dict[str, Any] = {
            "org_id": org_id,
            "approved_taglines": ["Direct to Silicon", "Compute Without Limits"],
            "restricted_competitors": ["Never mention competitor names directly"],
            "color_tokens": {"primary": "#6366F1", "secondary": "#10B981"}
        }
        self.session_memory: Dict[str, Any] = {
            "active_campaign": None,
            "conversation_turns": [],
            "current_audience": "Indian Developers",
            "active_tone_register": "technical"
        }

    def read_memory(self, layer: str, key: Optional[str] = None):
        if layer == "character":
            return self.character_memory.model_dump()
        elif layer == "organization":
            return self.org_memory.get(key) if key else self.org_memory
        elif layer == "session":
            return self.session_memory.get(key) if key else self.session_memory
        raise ValueError(f"Unknown memory layer '{layer}'")

    def write_memory(self, layer: str, caller_role: str, key: str, value: Any):
        # Section 18.1 Write-permission matrix
        if layer == "character":
            if caller_role != "human_admin":
                raise PermissionError(
                    f"Write to Character Memory denied for role '{caller_role}'. Only human_admin can commit character changes."
                )
            setattr(self.character_memory, key, value)
            self.character_memory.seal()

        elif layer == "organization":
            if caller_role != "human_admin":
                raise PermissionError(
                    f"Write to Organization Memory denied for role '{caller_role}'. Only human_admin can commit company knowledge."
                )
            self.org_memory[key] = value

        elif layer == "session":
            allowed_roles = ("orchestrator", "live_session", "human_admin")
            if caller_role not in allowed_roles:
                raise PermissionError(f"Role '{caller_role}' cannot write to Session Memory.")
            self.session_memory[key] = value

        else:
            raise ValueError(f"Invalid memory layer '{layer}'")
