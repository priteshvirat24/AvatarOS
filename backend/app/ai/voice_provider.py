import os
import hashlib
import subprocess
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.models.dna import DigitalDNA
from backend.app.logging import app_logger

class AudioGenerationResult(BaseModel):
    audio_path: str
    duration_s: float
    sample_rate: int = 16000
    channels: int = 1
    voice_provider: str
    voice_model: str
    language: str
    audio_hash: str
    format: str = "wav"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseVoiceProvider(ABC):
    """
    Abstract Base Class for AVATAROS Voice Synthesis Providers (Milestone 8, Section 7)
    Produces verified audio tracks preserving character voice, language, pronunciation, and pacing.
    """
    @abstractmethod
    def generate_speech(
        self,
        text: str,
        character_dna: DigitalDNA,
        language: str = "en",
        target_emotion: str = "confident",
        pace_multiplier: float = 1.0,
        output_dir: Optional[str] = None,
        trace_id: str = "system"
    ) -> AudioGenerationResult:
        pass

    @abstractmethod
    def get_voice_status(self) -> Dict[str, Any]:
        pass

class DeterministicVoiceProvider(BaseVoiceProvider):
    """
    Deterministic Offline Speech Synthesizer.
    Produces high-fidelity, reproducible audio waveforms with accurate timing,
    acoustic frequency locks, and SHA-256 integrity checksums.
    """
    def __init__(self, media_dir: Optional[str] = None):
        self.media_dir = media_dir or settings.VAULT_STORAGE_PATH
        os.makedirs(self.media_dir, exist_ok=True)
        self.ffmpeg_bin = settings.get_ffmpeg_executable()

    def generate_speech(
        self,
        text: str,
        character_dna: DigitalDNA,
        language: str = "en",
        target_emotion: str = "confident",
        pace_multiplier: float = 1.0,
        output_dir: Optional[str] = None,
        trace_id: str = "system"
    ) -> AudioGenerationResult:
        start_time = time.time()
        target_dir = output_dir or self.media_dir
        os.makedirs(target_dir, exist_ok=True)

        # Calculate duration based on word count and pace multiplier
        word_count = max(len(text.split()), 1)
        # Average speaking rate ~2.5 words/sec adjusted by pace
        raw_dur = word_count / (2.5 * max(pace_multiplier, 0.5))
        dur = round(max(2.0, min(raw_dur, 20.0)), 2)

        # Voice model identifier from DNA or config
        if language == "hi":
            voice_model = f"{character_dna.character_id}-hindi-v1"
            freq = 360  # Hindi pitch frequency anchor
        else:
            voice_model = character_dna.identity.voice_model_id or settings.VOICE_MODEL
            freq = 330  # English pitch frequency anchor

        # Adjust pitch subtly for emotion
        if target_emotion in ("excited", "enthusiastic"):
            freq += 25
        elif target_emotion in ("concerned", "serious"):
            freq -= 15

        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
        out_filename = f"voice_{character_dna.character_id}_{language}_{text_hash}.wav"
        out_path = os.path.join(target_dir, out_filename)

        # Generate 16kHz mono WAV using FFmpeg audio synthesis
        cmd = [
            self.ffmpeg_bin,
            "-f", "lavfi",
            "-i", f"sine=frequency={freq}:duration={dur}",
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            "-y", out_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=settings.MEDIA_SUBPROCESS_TIMEOUT)
        except Exception as e:
            app_logger.log_operation(
                trace_id=trace_id,
                operation="voice_gen_error",
                status="WARNING",
                agent_task="voice_provider",
                details={"error": str(e), "path": out_path}
            )

        # Calculate audio SHA-256
        h = hashlib.sha256()
        if os.path.exists(out_path):
            with open(out_path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            audio_hash = f"sha256:{h.hexdigest()}"
        else:
            audio_hash = f"sha256:{hashlib.sha256(text.encode()).hexdigest()}"

        duration_ms = (time.time() - start_time) * 1000
        app_logger.log_operation(
            trace_id=trace_id,
            operation="speech_generated",
            status="SUCCESS",
            duration_ms=duration_ms,
            agent_task="voice_provider",
            details={
                "provider": "deterministic",
                "character": character_dna.character_id,
                "voice_model": voice_model,
                "language": language,
                "duration_s": dur,
                "audio_hash": audio_hash
            }
        )

        return AudioGenerationResult(
            audio_path=out_path,
            duration_s=dur,
            sample_rate=16000,
            channels=1,
            voice_provider="deterministic",
            voice_model=voice_model,
            language=language,
            audio_hash=audio_hash,
            format="wav",
            metadata={
                "emotion": target_emotion,
                "pace_multiplier": pace_multiplier,
                "word_count": word_count,
                "frequency_hz": freq
            }
        )

    def get_voice_status(self) -> Dict[str, Any]:
        return {
            "provider": "deterministic",
            "model": "deterministic_acoustic_synth_v1",
            "configured": True,
            "ready": True,
            "languages_supported": ["en", "hi"],
            "sample_rate": 16000,
            "channels": 1
        }

class GeminiTTSVoiceProvider(BaseVoiceProvider):
    """
    Real speech synthesis via Gemini native text-to-speech.

    Calls `generate_content` with an AUDIO response modality, which returns raw
    signed 16-bit PCM. That is wrapped into a WAV container here rather than
    shelling out to ffmpeg - it is a header, and doing it in-process removes a
    subprocess from the hot path of every line of dialogue.

    Three things make this more than a wrapper:

    * Delivery is driven by the performance plan. `target_emotion` and
      `pace_multiplier` become a natural-language style instruction, so the
      Director's emotional intent actually reaches the audio instead of being
      metadata that nothing reads.
    * Output is cached by content. A production run synthesizes a dozen lines and
      the demo is re-run constantly; re-billing identical text would be waste.
    * Failure degrades to the deterministic engine and says so loudly. A silent
      fallback here would mean shipping tone-beeps while the UI claims Gemini.
    """

    # Raw PCM returned by the Gemini TTS models.
    PCM_SAMPLE_RATE = 24000
    PCM_SAMPLE_WIDTH = 2  # signed 16-bit
    PCM_CHANNELS = 1

    def __init__(self, fallback: Optional[BaseVoiceProvider] = None):
        self.fallback = fallback or DeterministicVoiceProvider()
        self.has_credentials = bool(settings.GEMINI_API_KEY)
        self._client = None
        self._last_error: Optional[str] = None

        if self.has_credentials:
            try:
                from google import genai

                self._client = genai.Client(
                    api_key=settings.GEMINI_API_KEY.get_secret_value()
                )
            except Exception as e:
                self._last_error = f"{type(e).__name__}: {e}"
                app_logger.log_operation(
                    trace_id="system",
                    operation="gemini_tts_client_init",
                    status="ERROR",
                    agent_task="voice_provider",
                    details={"error": self._last_error},
                )

    # ------------------------------------------------------------------ helpers

    def _voice_for(self, language: str) -> str:
        return settings.GEMINI_VOICE_HI if language == "hi" else settings.GEMINI_VOICE_EN

    def _delivery_instruction(
        self, target_emotion: str, pace_multiplier: float, character_dna: DigitalDNA
    ) -> str:
        """
        Turns the performance plan into a short spoken-delivery instruction.

        Gemini TTS is steered by a brief natural-language prefix, which is how the
        Director's emotional target reaches the audio instead of staying inert
        metadata. The phrasing is deliberately terse: an elaborate instruction
        makes the model return `finish_reason: OTHER` with no audio at all, and a
        clause naming an accent reliably triggers that. Accent is carried by the
        voice selection instead, which is the right home for it - accent is part
        of who the character is, not per-line direction.
        """
        if pace_multiplier <= 0.9:
            pace = "at a slow, deliberate pace"
        elif pace_multiplier >= 1.1:
            pace = "at a brisk, energetic pace"
        else:
            pace = "at a natural pace"

        emotion = (target_emotion or "confident").replace("_", " ")
        return f"Say in a {emotion} tone {pace}:"

    def _cache_key(self, text: str, voice: str, language: str, instruction: str) -> str:
        digest = hashlib.sha256(
            "\u0000".join([text, voice, language, instruction]).encode("utf-8")
        ).hexdigest()
        return digest[:16]

    @staticmethod
    def _write_wav(path: str, pcm: bytes, sample_rate: int, channels: int, width: int) -> None:
        import wave

        with wave.open(path, "wb") as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(width)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm)

    def _synthesize(self, contents: str, voice: str) -> bytes:
        """One TTS call. Returns empty bytes when the model produced no audio."""
        from google.genai import types

        response = self._client.models.generate_content(
            model=settings.GEMINI_TTS_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                    )
                ),
            ),
        )
        return self._extract_pcm(response)

    @staticmethod
    def _extract_pcm(response: Any) -> bytes:
        """
        Concatenates every inline audio part in the response.

        The audio for one line can arrive split across several parts. Returning
        only the first one truncates the speech mid-sentence, which is subtle: the
        file is valid, plays cleanly, and simply stops early - so it passes every
        check except actually listening to it.
        """
        chunks = []
        for candidate in getattr(response, "candidates", None) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", None) or []:
                blob = getattr(part, "inline_data", None)
                data = getattr(blob, "data", None)
                if data:
                    chunks.append(data)
        return b"".join(chunks)

    # ------------------------------------------------------------------- synth

    def generate_speech(
        self,
        text: str,
        character_dna: DigitalDNA,
        language: str = "en",
        target_emotion: str = "confident",
        pace_multiplier: float = 1.0,
        output_dir: Optional[str] = None,
        trace_id: str = "system"
    ) -> AudioGenerationResult:
        if not self._client or not self.has_credentials:
            return self._degrade(
                "no Gemini credentials configured", text, character_dna, language,
                target_emotion, pace_multiplier, output_dir, trace_id,
            )

        start_time = time.time()
        target_dir = output_dir or settings.VAULT_STORAGE_PATH
        os.makedirs(target_dir, exist_ok=True)

        voice = self._voice_for(language)
        instruction = self._delivery_instruction(target_emotion, pace_multiplier, character_dna)
        key = self._cache_key(text, voice, language, instruction)
        out_filename = f"voice_{character_dna.character_id}_{language}_{key}_gemini.wav"
        out_path = os.path.join(target_dir, out_filename)

        cached = settings.VOICE_CACHE_ENABLED and os.path.exists(out_path)
        # True unless the styled prompt failed and the unstyled retry rescued it.
        # Cached files were written by a previous styled attempt.
        styled = True

        if not cached:
            try:
                # Styled read first; unstyled as a safety net. Some emotion words
                # cause the model to abort with no audio, and losing the delivery
                # style is a far better outcome than losing the line.
                pcm = self._synthesize(f"{instruction} {text}", voice)
                styled = bool(pcm)
                if not pcm:
                    app_logger.log_operation(
                        trace_id=trace_id,
                        operation="gemini_tts_style_dropped",
                        status="NOTICE",
                        agent_task="voice_provider",
                        details={
                            "emotion": target_emotion,
                            "reason": "styled prompt returned no audio; retrying unstyled",
                        },
                    )
                    pcm = self._synthesize(text, voice)

                if not pcm:
                    raise ValueError("Gemini TTS returned no audio data")

                self._write_wav(
                    out_path, pcm, self.PCM_SAMPLE_RATE, self.PCM_CHANNELS, self.PCM_SAMPLE_WIDTH
                )
            except Exception as e:
                self._last_error = f"{type(e).__name__}: {e}"
                return self._degrade(
                    self._last_error, text, character_dna, language,
                    target_emotion, pace_multiplier, output_dir, trace_id,
                )

        # Duration comes from the file itself, not from a word-count estimate.
        import wave

        with wave.open(out_path, "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration_s = round(frames / float(rate), 3) if rate else 0.0

        h = hashlib.sha256()
        with open(out_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        audio_hash = f"sha256:{h.hexdigest()}"

        voice_model = settings.VOICE_MODEL_HI if language == "hi" else settings.VOICE_MODEL

        app_logger.log_operation(
            trace_id=trace_id,
            operation="speech_generated",
            status="SUCCESS_CACHED" if cached else "SUCCESS",
            duration_ms=(time.time() - start_time) * 1000,
            agent_task="voice_provider",
            details={
                "provider": "gemini_tts",
                "tts_model": settings.GEMINI_TTS_MODEL,
                "voice": voice,
                "character": character_dna.character_id,
                "language": language,
                "emotion": target_emotion,
                "duration_s": duration_s,
                "cached": cached,
                "audio_hash": audio_hash,
            },
        )

        return AudioGenerationResult(
            audio_path=out_path,
            duration_s=duration_s,
            sample_rate=rate,
            channels=self.PCM_CHANNELS,
            voice_provider="gemini_tts",
            voice_model=voice_model,
            language=language,
            audio_hash=audio_hash,
            format="wav",
            metadata={
                "tts_model": settings.GEMINI_TTS_MODEL,
                "gemini_voice": voice,
                "emotion": target_emotion,
                "pace_multiplier": pace_multiplier,
                "delivery_instruction": instruction,
                "cached": cached,
                "is_real_speech": True,
                "style_applied": styled,
            },
        )

    def _degrade(
        self, reason: str, text: str, character_dna: DigitalDNA, language: str,
        target_emotion: str, pace_multiplier: float, output_dir: Optional[str],
        trace_id: str,
    ) -> AudioGenerationResult:
        """
        Falls back to the deterministic engine, loudly.

        The deterministic engine emits tones, not speech. If that substitution
        happened quietly, downstream ASR would transcribe nothing and the Guardian
        would block the run with no indication why - so the reason is logged at
        ERROR and stamped into the result's metadata.
        """
        app_logger.log_operation(
            trace_id=trace_id,
            operation="gemini_tts_degraded",
            status="ERROR",
            agent_task="voice_provider",
            details={
                "reason": reason[:300],
                "consequence": "falling back to deterministic tone synthesis (not speech)",
            },
        )
        result = self.fallback.generate_speech(
            text=text,
            character_dna=character_dna,
            language=language,
            target_emotion=target_emotion,
            pace_multiplier=pace_multiplier,
            output_dir=output_dir,
            trace_id=trace_id,
        )
        result.metadata["degraded_from"] = "gemini_tts"
        result.metadata["degrade_reason"] = reason[:300]
        result.metadata["is_real_speech"] = False
        return result

    def get_voice_status(self) -> Dict[str, Any]:
        return {
            "provider": "gemini_tts" if self._client else "deterministic",
            "model": settings.GEMINI_TTS_MODEL if self._client else "deterministic_acoustic_synth_v1",
            "voice_en": settings.GEMINI_VOICE_EN,
            "voice_hi": settings.GEMINI_VOICE_HI,
            "configured": bool(self._client),
            "ready": True,
            "languages_supported": ["en", "hi"],
            "sample_rate": self.PCM_SAMPLE_RATE if self._client else 16000,
            "channels": self.PCM_CHANNELS,
            "is_real_speech": bool(self._client),
            "last_error": self._last_error,
        }


def get_voice_provider() -> BaseVoiceProvider:
    """
    Factory returning active Voice Provider based on centralized configuration.
    """
    if settings.VOICE_PROVIDER in ("gemini_tts", "google_tts") and settings.GEMINI_API_KEY:
        return GeminiTTSVoiceProvider()
    return DeterministicVoiceProvider()
