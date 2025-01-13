import logging
from typing import Dict, Optional
from moviepy.editor import VideoFileClip
from riddler.config.exceptions import SegmentServiceError
from riddler.services.video.base import SegmentServiceBase
from riddler.services.video.effects_service import VideoEffectsService
from riddler.services.video.text_overlay_service import TextOverlayService

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

            # Add text overlay if specified
            text = segment.get("text")
            if text:

                clip = self.text_overlay.create_text_overlay(
                    clip, 
                    text,
                    emoji=segment.get("emoji")
                )

            return clip

        except Exception as e:
            self.logger.error(f"Failed to process segment: {str(e)}")
            raise SegmentServiceError(f"Failed to process segment: {str(e)}")
