import time
from typing import Dict, Any, List
from backend.app.models.dna import DigitalDNA

class LiveModeEngine:
    """
    Live Mode Conversational Digital Human Engine (Section 17)
    Latency budget target: < 800ms.
    Demonstrates dynamic communication strategy adaptation:
    - Default / Technical
    - Beginner / 12-year-old
    - CTO / Enterprise Architect
    While underlying Digital DNA remains immutable.
    """
    def __init__(self, character_dna: DigitalDNA):
        self.character_dna = character_dna
        self.history: List[Dict[str, str]] = []
        self.active_register = "technical"

    def process_user_turn(self, user_text: str) -> Dict[str, Any]:
        start_time = time.time()
        txt_lower = user_text.lower()

        # 1. Guardrail topic check against Digital DNA (inline low-latency guardrail)
        for restricted in self.character_dna.topics.restricted:
            if restricted.replace("_", " ") in txt_lower:
                return {
                    "reply": f"As Maya representing {self.character_dna.brand.org_id}, I'm restricted from providing {restricted.replace('_', ' ')}. Let's focus on our developer platform and engineering benchmarks!",
                    "register": self.active_register,
                    "dna_locked": True,
                    "latency_ms": int((time.time() - start_time) * 1000) + 120,
                    "target_emotion": "polite_deflection"
                }

        # 2. Communication Strategy Adaptation (Session-scoped)
        if "12-year-old" in txt_lower or "beginner" in txt_lower or "simple" in txt_lower or "too technical" in txt_lower:
            self.active_register = "beginner"
            reply = (
                "Imagine your computer has a magical co-pilot brain built right inside it! "
                "Instead of sending your homework across the internet to ask a question, "
                "this laptop answers instantly right on your desk, without any lag or waiting."
            )
            target_emotion = "warm_enthusiastic"
            gesture = "open_friendly_gestures"

        elif "cto" in txt_lower or "architect" in txt_lower or "enterprise" in txt_lower:
            self.active_register = "cto"
            reply = (
                "From an architectural standpoint, the Titan system offloads transformer matrix multiplications "
                "to an isolated 45 TOPS NPU bus. This eliminates egress cloud latency, guarantees data compliance "
                "within air-gapped developer environments, and reduces p99 code-completion inference latencies to sub-15ms."
            )
            target_emotion = "authoritative_analytical"
            gesture = "measured_precision_emphasis"

        else:
            self.active_register = "technical"
            reply = (
                "The Titan AI Laptop runs local LLMs and code assistance directly on hardware. "
                "With 40% faster MLPerf-verified inference and 18-hour sustained battery endurance, "
                "developers get zero-cloud compile and debugging velocity right at their fingertips."
            )
            target_emotion = "confident_direct"
            gesture = "confident_technical_v2"

        # Simulating latency breakdown: ASR ~120ms, LLM ~280ms, TTS ~140ms, Face driving ~110ms = ~650ms
        elapsed = int((time.time() - start_time) * 1000) + 210

        self.history.append({"user": user_text, "maya": reply, "register": self.active_register})

        return {
            "reply": reply,
            "register": self.active_register,
            "target_emotion": target_emotion,
            "gesture_profile": gesture,
            "dna_locked": True,
            "character_version": self.character_dna.version,
            "latency_breakdown": {
                "asr_ms": 115,
                "llm_first_token_ms": 260,
                "tts_audio_first_chunk_ms": 145,
                "avatar_driving_ms": 120,
                "total_latency_ms": 640
            }
        }
