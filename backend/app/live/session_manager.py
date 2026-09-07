import time
from typing import Dict, Optional, Any, List
from backend.app.config import settings
from backend.app.models.live import (
    LiveSession,
    LiveTurnResponse,
    LiveEvent
)
from backend.app.data.seed_characters import get_seed_characters
from backend.app.memory.memory import MemoryArchitecture
from backend.app.ai.live_provider import get_live_provider, BaseLiveProvider
from backend.app.logging import app_logger

class LiveSessionManager:
    """
    Live Session Manager (Section 17, Milestone 6)
    Authoritative server-side manager for conversational digital human sessions:
    - Resolves and binds read-only Digital DNA server-side
    - Validates likeness Rights authorization before session start
    - Enforces complete memory layer isolation (SessionMemory sandbox)
    - Rejects any DNA mutation attempts through live mode
    - Manages real-time turns, audio streams, and interruption cancellations
    """
    def __init__(self, provider: Optional[BaseLiveProvider] = None):
        self.provider = provider or get_live_provider()
        self.sessions: Dict[str, LiveSession] = {}
        self.session_memories: Dict[str, MemoryArchitecture] = {}

    def create_session(
        self,
        character_id: str = "maya",
        language: str = "en",
        trace_id: str = "system"
    ) -> LiveSession:
        seed_data = get_seed_characters()
        characters = seed_data["characters"]
        rights_db = seed_data.get("rights", {})

        # 1. Server-side Digital DNA resolution
        character_dna = characters.get(character_id)
        if not character_dna:
            raise ValueError(f"Character '{character_id}' not found in registry.")

        # 2. Server-side Rights authorization verification
        rights_rec = rights_db.get(character_id)
        if rights_rec:
            if not (rights_rec.is_valid_for_context("interactive_live") or rights_rec.is_valid_for_context("product_education")):
                raise PermissionError(
                    f"Likeness rights lapsed or restricted for character '{character_id}' in interactive_live context."
                )
            rights_ref = rights_rec.rights_id
        else:
            rights_ref = character_dna.rights_ref

        # 3. Create Session Memory Sandbox
        mem = MemoryArchitecture(character_dna=character_dna, org_id=character_dna.brand.org_id)
        mem.write_memory("session", "live_session", "active_language", language)
        mem.write_memory("session", "live_session", "active_register", "technical")

        # 4. Bind Read-Only DNA snapshot to Session
        session = self.provider.create_session(
            character_dna=character_dna,
            rights_ref=rights_ref,
            language=language,
            trace_id=trace_id
        )

        self.sessions[session.session_id] = session
        self.session_memories[session.session_id] = mem

        return session

    def get_session(self, session_id: str) -> Optional[LiveSession]:
        return self.sessions.get(session_id)

    def process_turn(
        self,
        session_id: str,
        user_text: str,
        audio_chunk: Optional[bytes] = None,
        trace_id: str = "system"
    ) -> LiveTurnResponse:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Live session '{session_id}' not found.")

        if session.status == "CLOSED":
            raise ValueError(f"Cannot process turn on closed session '{session_id}'.")

        # Check session duration limit
        start_time = float(datetime_to_epoch(session.created_at))
        if (time.time() - start_time) > settings.LIVE_MAX_SESSION_DURATION:
            session.status = "CLOSED"
            raise TimeoutError(f"Live session '{session_id}' exceeded maximum duration ({settings.LIVE_MAX_SESSION_DURATION}s).")

        mem = self.session_memories.get(session_id)

        # Process turn through Live Provider
        response = self.provider.process_turn(session, user_text, audio_chunk, trace_id=trace_id)

        # Record turn in SessionMemory sandbox (never mutates Character or Org memory)
        if mem:
            mem.write_memory("session", "live_session", "active_register", response.register)
            turns = mem.read_memory("session", "conversation_turns") or []
            turns.append({"user": user_text, "reply": response.reply, "register": response.register})
            mem.write_memory("session", "live_session", "conversation_turns", turns)

        return response

    def interrupt_session(self, session_id: str, trace_id: str = "system") -> LiveEvent:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Live session '{session_id}' not found.")

        return self.provider.interrupt(session, trace_id=trace_id)

    def close_session(self, session_id: str, trace_id: str = "system") -> LiveSession:
        session = self.sessions.get(session_id)
        if not session:
            raise KeyError(f"Live session '{session_id}' not found.")

        closed = self.provider.close_session(session, trace_id=trace_id)
        # Clean up ephemeral session memory
        if session_id in self.session_memories:
            del self.session_memories[session_id]

        return closed

    def get_allowed_tools(self, session_id: str) -> List[str]:
        """
        Phase 11: Tool permission allowlist for conversational Live Mode.
        Only read-only / factual verification tools are exposed.
        Mutating tools (publish, modify_dna, filesystem, shell) are strictly forbidden.
        """
        return ["search_knowledge", "verify_claim", "get_character_dna", "get_rights"]

    def get_session_memory(self, session_id: str) -> Optional[MemoryArchitecture]:
        return self.session_memories.get(session_id)

    def attempt_dna_mutation_from_live(self, session_id: str, key: str, value: Any) -> None:
        """
        Security verification helper demonstrating that Live Mode role cannot mutate Digital DNA.
        """
        mem = self.session_memories.get(session_id)
        if not mem:
            raise KeyError(f"Live session '{session_id}' not found.")
        # Attempting to write to character layer with live_session role must raise PermissionError
        mem.write_memory("character", "live_session", key, value)


def datetime_to_epoch(iso_str: str) -> float:
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.timestamp()
    except Exception:
        return time.time()

live_session_manager = LiveSessionManager()
