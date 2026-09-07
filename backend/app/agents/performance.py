from typing import List, Optional
from backend.app.models.dna import DigitalDNA
from backend.app.models.director import DirectorPlan
from backend.app.models.performance import (
    PerformancePlan,
    ProductionPerformancePlan,
    ScenePerformanceSpec,
    PauseSpec,
    GestureSpec,
    FacialKeyframe,
    FacialExpressionPlan,
    GazePlan,
    HeadMotionPlan,
    CameraControl,
    CameraShotPlan,
    LipSyncPlan,
    SceneTiming,
    PerformanceTiming
)

class PerformanceAgent:
    """
    Performance Director Agent (Milestone 8, Section 4 & 12)
    Consumes DirectorPlan and Digital DNA to emit a fully structured,
    schema-validated PerformancePlan driving avatar rendering and audio synthesis.
    """
    def create_performance_plan(
        self,
        director_plan: DirectorPlan,
        character_dna: DigitalDNA,
        language: str = "en"
    ) -> PerformancePlan:
        scenes: List[ScenePerformanceSpec] = []
        scene_timings: List[SceneTiming] = []
        current_time_s = 0.0

        for shot in director_plan.shots:
            s_no = shot.scene_no
            speech_rate = character_dna.speech.pace_multiplier
            dur = float(shot.duration_s)

            # Map emotion to controlled facial behavior anchored within DNA personality vector
            emotion = shot.target_emotion.lower()
            if emotion in ("excited", "enthusiastic"):
                facial_plan = FacialExpressionPlan(
                    baseline_expression="energized_smile",
                    smile_intensity=min(0.85, character_dna.personality_vector.warmth + 0.3),
                    eyebrow_elevation=0.6,
                    eye_aperture=0.9,
                    keyframes=[
                        FacialKeyframe(event="smile_onset", trigger="start", target_expression="energized_smile", intensity=0.85)
                    ]
                )
                head_motion = HeadMotionPlan(nod_frequency=0.35, tilt_degrees=6.0, idle_sway_amplitude=0.15, speaking_cadence="energetic")
                gaze = GazePlan(target="camera", direct_contact_ratio=0.90)
            elif emotion in ("concerned", "analytical", "serious"):
                facial_plan = FacialExpressionPlan(
                    baseline_expression="focused",
                    smile_intensity=0.2,
                    eyebrow_elevation=0.3,
                    eye_aperture=0.8,
                    keyframes=[
                        FacialKeyframe(event="direct_focus", trigger="problem_statement", target_expression="focused", intensity=0.7)
                    ]
                )
                head_motion = HeadMotionPlan(nod_frequency=0.15, tilt_degrees=2.0, idle_sway_amplitude=0.05, speaking_cadence="measured")
                gaze = GazePlan(target="camera", direct_contact_ratio=0.95)
            elif emotion in ("confident", "authoritative"):
                facial_plan = FacialExpressionPlan(
                    baseline_expression="confident_smile",
                    smile_intensity=min(0.75, character_dna.personality_vector.confident),
                    eyebrow_elevation=0.45,
                    eye_aperture=0.85,
                    keyframes=[
                        FacialKeyframe(event="smile_onset", trigger="product_reveal", target_expression="confident_smile", intensity=0.75)
                    ]
                )
                head_motion = HeadMotionPlan(nod_frequency=0.25, tilt_degrees=4.0, idle_sway_amplitude=0.1, speaking_cadence="rhythmic_natural")
                gaze = GazePlan(target="camera", direct_contact_ratio=0.88)
            else:
                facial_plan = FacialExpressionPlan(
                    baseline_expression="neutral",
                    smile_intensity=0.5,
                    eyebrow_elevation=0.35,
                    eye_aperture=0.85,
                    keyframes=[
                        FacialKeyframe(event="natural_gaze", trigger="start", target_expression="neutral", intensity=0.5)
                    ]
                )
                head_motion = HeadMotionPlan(nod_frequency=0.2, tilt_degrees=3.0, idle_sway_amplitude=0.08, speaking_cadence="natural")
                gaze = GazePlan(target="camera", direct_contact_ratio=0.85)

            # Map camera and shot type from DirectorPlan
            shot_type_val = "medium_close_up"
            raw_shot = shot.shot.lower().replace("-", "_").replace(" ", "_")
            if "close" in raw_shot and "medium" not in raw_shot:
                shot_type_val = "close_up"
            elif "medium_close" in raw_shot or "mcu" in raw_shot:
                shot_type_val = "medium_close_up"
            elif "wide" in raw_shot:
                shot_type_val = "medium_wide"
            elif "present" in raw_shot:
                shot_type_val = "presentation_framing"
            elif "talk" in raw_shot:
                shot_type_val = "talking_head"
            else:
                shot_type_val = "medium_shot"

            shot_plan = CameraShotPlan(
                shot_type=shot_type_val,
                framing="center_balanced",
                character_screen_position="center",
                camera_control=CameraControl(
                    move="slow_push_in" if s_no in (1, 3, 4) else "static",
                    start_fov=42.0 if s_no == 1 else (38.0 if s_no == 4 else 40.0),
                    end_fov=38.0 if s_no == 1 else (34.0 if s_no == 4 else 40.0)
                )
            )

            # Scene-specific pauses and gestures
            if s_no == 1:
                pauses = [PauseSpec(after_word_idx=6, duration_ms=350)]
                gestures = [GestureSpec(gesture_type="curious_head_tilt", trigger_word_idx=4, intensity=0.7)]
            elif s_no == 3:
                pauses = [PauseSpec(after_word_idx=5, duration_ms=400)]
                gestures = [GestureSpec(gesture_type="open_palm_present", trigger_word_idx=7, intensity=0.8)]
            elif s_no == 4:
                pauses = [PauseSpec(after_word_idx=4, duration_ms=300)]
                gestures = [GestureSpec(gesture_type="right_hand_emphasis", trigger_word_idx=6, intensity=0.85)]
            else:
                pauses = [PauseSpec(after_word_idx=5, duration_ms=250)]
                gestures = [GestureSpec(gesture_type="natural_affirmative", trigger_word_idx=4, intensity=0.6)]

            scene_spec = ScenePerformanceSpec(
                scene_no=s_no,
                target_emotion=shot.target_emotion,
                energy=shot.emotional_intensity,
                eye_direction="camera",
                speech_rate_multiplier=speech_rate,
                pauses_ms=pauses,
                gestures=gestures,
                facial_keyframes=facial_plan.keyframes,
                facial_plan=facial_plan,
                gaze_plan=gaze,
                head_motion_plan=head_motion,
                shot_plan=shot_plan,
                lip_sync_plan=LipSyncPlan(max_tolerance_ms=80, viseme_alignment_rate=1.0),
                camera=shot_plan.camera_control
            )
            scenes.append(scene_spec)
            scene_timings.append(SceneTiming(scene_no=s_no, start_s=current_time_s, duration_s=dur))
            current_time_s += dur

        voice_model_id = (
            f"{character_dna.character_id}-hindi-v1"
            if language == "hi"
            else (character_dna.identity.voice_model_id or "maya-english-v4")
        )

        return PerformancePlan(
            plan_id=f"perf_{director_plan.plan_id}",
            character_id=character_dna.character_id,
            character_version=character_dna.version,
            dna_version=character_dna.version,
            voice_model=voice_model_id,
            language=language,
            emotional_state="confident",
            energy=0.78,
            speaking_style=character_dna.speech.accent,
            facial_expression_plan=FacialExpressionPlan(),
            gaze_plan=GazePlan(),
            head_motion_plan=HeadMotionPlan(),
            gesture_plan=[g for sc in scenes for g in sc.gestures],
            camera_plan=CameraControl(move="slow_push_in"),
            shot_plan=CameraShotPlan(),
            lip_sync_requirements=LipSyncPlan(max_tolerance_ms=80),
            timing=PerformanceTiming(total_duration_s=current_time_s, scene_timings=scene_timings),
            renderer_requirements={
                "resolution": "1280x720",
                "fps": 30,
                "format": "mp4",
                "aspect_ratio": "16:9"
            },
            scenes=scenes
        )

performance_agent = PerformanceAgent()
