import logging
from typing import Dict
from moviepy.editor import VideoFileClip
from config.exceptions import SegmentServiceError
from services.video.base import SegmentServiceBase
from services.video.effects_service import VideoEffectsService
from services.video.text_overlay_service import TextOverlayService

class SegmentService(SegmentServiceBase):
    def __init__(
        self,
        video_effects: VideoEffectsService,
        text_overlay: TextOverlayService,
        config: Dict = None,
        logger: logging.Logger = None
    ):
        self.video_effects = video_effects
        self.text_overlay = text_overlay
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)

    def process_segment(self, segment: Dict, timing: Dict[str, float]) -> VideoFileClip:
        """Process a single video segment with effects and overlays."""
        try:
            # Get the base video clip
            video_path = segment.get("video_path")
            if not video_path:
                raise SegmentServiceError("No video path provided for segment")

            # Load the video clip
            clip = VideoFileClip(video_path)

            # Standardize the video duration
            clip = self.video_effects.standardize_video(clip, timing["duration"])

            # Apply any specified effects
            effect_type = segment.get("effect", "none")
            clip = self.video_effects.apply_effect(clip, effect_type)

            # Add text overlay if specified
            text = segment.get("text")
            if text:
                clip = self.text_overlay.create_text_overlay(clip, text)

            # Apply any segment-specific processing
            clip = self._apply_segment_specific_processing(clip, segment)

            return clip

        except Exception as e:
            self.logger.error(f"Failed to process segment: {str(e)}")
            raise SegmentServiceError(f"Failed to process segment: {str(e)}")

    def _apply_segment_specific_processing(self, clip: VideoFileClip, segment: Dict) -> VideoFileClip:
        """Apply any segment-type specific processing."""
        segment_type = segment.get("type", "default")

        if segment_type == "hook":
            # Apply hook-specific processing (e.g., more dynamic effects)
            clip = self._process_hook_segment(clip)
        elif segment_type == "question":
            # Apply question-specific processing
            clip = self._process_question_segment(clip)
        elif segment_type == "answer":
            # Apply answer-specific processing
            clip = self._process_answer_segment(clip)

        return clip

    def _process_hook_segment(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply hook-specific processing."""
        # Add hook-specific effects (e.g., faster cuts, more dynamic transitions)
        try:
            # Apply fade in effect
            clip = self.video_effects.apply_effect(clip, "fade_in")
            # Could add more hook-specific processing here
            return clip
        except Exception as e:
            self.logger.error(f"Failed to process hook segment: {str(e)}")
            raise SegmentServiceError(f"Failed to process hook segment: {str(e)}")

    def _process_question_segment(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply question-specific processing."""
        try:
            # Maybe add a slight blur effect to make text more readable
            clip = self.video_effects.apply_effect(clip, "blur")
            # Could add more question-specific processing here
            return clip
        except Exception as e:
            self.logger.error(f"Failed to process question segment: {str(e)}")
            raise SegmentServiceError(f"Failed to process question segment: {str(e)}")

    def _process_answer_segment(self, clip: VideoFileClip) -> VideoFileClip:
        """Apply answer-specific processing."""
        try:
            # Maybe brighten the video slightly for the answer
            clip = self.video_effects.apply_effect(clip, "brighten")
            # Could add more answer-specific processing here
            return clip
        except Exception as e:
            self.logger.error(f"Failed to process answer segment: {str(e)}")
            raise SegmentServiceError(f"Failed to process answer segment: {str(e)}") 