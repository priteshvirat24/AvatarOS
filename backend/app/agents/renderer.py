import os
import hashlib
from typing import Dict, List, Optional
from backend.app.models.director import DirectorPlan
from backend.app.models.performance import PerformancePlan, ProductionPerformancePlan
from backend.app.models.dna import DigitalDNA
from backend.app.config import settings
from backend.app.ai.avatar_renderer import get_avatar_renderer, BaseAvatarRenderer, RenderSceneResult, RenderMasterResult
from backend.app.ai.voice_provider import get_voice_provider, BaseVoiceProvider, AudioGenerationResult

class AvatarRenderer:
    """
    Pluggable Media & Digital Human Renderer Facade (Section 12, 13, Milestone 8)
    Delegates to the active BaseAvatarRenderer and BaseVoiceProvider instances.
    Provides backward-compatible rendering methods and status discovery.
    """
    def __init__(self, media_dir: Optional[str] = None):
        self.media_dir = media_dir or settings.VAULT_STORAGE_PATH
        os.makedirs(self.media_dir, exist_ok=True)
        self.avatar_renderer: BaseAvatarRenderer = get_avatar_renderer()
        self.voice_provider: BaseVoiceProvider = get_voice_provider()

    def generate_voice_track(
        self,
        text: str,
        character_dna: DigitalDNA,
        language: str = "en",
        target_emotion: str = "confident",
        pace_multiplier: float = 1.0,
        trace_id: str = "system"
    ) -> AudioGenerationResult:
        """
        Synthesizes verified voice track using the configured Voice Provider.
        """
        return self.voice_provider.generate_speech(
            text=text,
            character_dna=character_dna,
            language=language,
            target_emotion=target_emotion,
            pace_multiplier=pace_multiplier,
            output_dir=self.media_dir,
            trace_id=trace_id
        )

    def render_scene(
        self,
        scene_no: int,
        role: str,
        text: str,
        duration_s: float,
        character_name: str = "Maya",
        character_version: str = "v1.7.0",
        target_emotion: str = "excited",
        energy: float = 0.78,
        language: str = "en",
        aspect: str = "16:9",
        character_dna: Optional[DigitalDNA] = None,
        performance_plan: Optional[PerformancePlan] = None,
        audio_path: Optional[str] = None,
        trace_id: str = "system"
    ) -> str:
        """
        Renders a single scene MP4 clip.
        Returns the absolute filepath to the rendered MP4.
        """
        # Resolve character DNA if not explicitly provided
        if not character_dna:
            from backend.app.data.seed_characters import get_seed_characters
            char_key = character_name.lower()
            character_dna = get_seed_characters()["characters"].get(char_key, get_seed_characters()["characters"]["maya"])

        # If audio track not supplied, generate voice track first
        if not audio_path:
            audio_res = self.generate_voice_track(
                text=text,
                character_dna=character_dna,
                language=language,
                target_emotion=target_emotion,
                pace_multiplier=character_dna.speech.pace_multiplier,
                trace_id=trace_id
            )
            audio_path = audio_res.audio_path

        render_res: RenderSceneResult = self.avatar_renderer.render_scene(
            scene_no=scene_no,
            role=role,
            text=text,
            duration_s=duration_s,
            character_dna=character_dna,
            performance_plan=performance_plan,
            audio_path=audio_path,
            language=language,
            aspect=aspect,
            trace_id=trace_id
        )

        return render_res.video_path

    def stitch_master_video(
        self,
        scene_paths: List[str],
        output_name: str = "master_video_en.mp4",
        trace_id: str = "system"
    ) -> str:
        """
        Stitches rendered scene clips into a complete master video.
        """
        master_res: RenderMasterResult = self.avatar_renderer.stitch_master_video(
            scene_paths=scene_paths,
            output_name=output_name,
            trace_id=trace_id
        )
        return master_res.master_video_path

    def compute_sha256(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return ""
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"

    def get_status(self) -> Dict[str, Any]:
        return {
            "avatar_renderer": self.avatar_renderer.get_renderer_status(),
            "voice_provider": self.voice_provider.get_voice_status()
        }

renderer = AvatarRenderer()
