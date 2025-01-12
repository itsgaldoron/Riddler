import logging
from typing import Dict
from moviepy.editor import VideoFileClip, vfx
from riddler.config.exceptions import VideoEffectsError
from riddler.services.video.base import VideoEffectsServiceBase
from riddler.utils.logger import log

class VideoEffectsService(VideoEffectsServiceBase):
    def __init__(self, config: Dict = None, logger=None):
        self.config = config or {}
        self.logger = logger or log
        self.effects_map = {
            "none": self._no_effect,
            "fade_in": self._fade_in,
            "fade_out": self._fade_out,
            "blur": self._blur,
            "brighten": self._brighten,
            "darken": self._darken
        }

    def apply_effect(self, clip: VideoFileClip, effect_type: str) -> VideoFileClip:
        try:
            effect_func = self.effects_map.get(effect_type.lower(), self._no_effect)
            return effect_func(clip)
        except Exception as e:
            self.logger.error(f"Failed to apply effect {effect_type}: {str(e)}")
            raise VideoEffectsError(f"Failed to apply effect {effect_type}: {str(e)}")

    def standardize_video(self, clip: VideoFileClip, target_duration: float) -> VideoFileClip:
        try:
            # Resize video to target resolution
            target_width = self.config.get("video", {}).get("resolution", {}).get("width", 1080)
            target_height = self.config.get("video", {}).get("resolution", {}).get("height", 1920)
            
            resized_clip = clip.resize(height=target_height, width=target_width)
            
            # Adjust duration
            if resized_clip.duration < target_duration:
                # Loop the video if it's too short
                n_loops = int(target_duration / resized_clip.duration) + 1
                resized_clip = resized_clip.loop(n=n_loops)
            
            # Cut to exact duration
            final_clip = resized_clip.subclip(0, target_duration)
            
            return final_clip
            
        except Exception as e:
            self.logger.error(f"Failed to standardize video: {str(e)}")
            raise VideoEffectsError(f"Failed to standardize video: {str(e)}")

    def _no_effect(self, clip: VideoFileClip) -> VideoFileClip:
        return clip

    def _fade_in(self, clip: VideoFileClip) -> VideoFileClip:
        fade_duration = min(1.0, clip.duration / 4)
        return clip.fadein(fade_duration)

    def _fade_out(self, clip: VideoFileClip) -> VideoFileClip:
        fade_duration = min(1.0, clip.duration / 4)
        return clip.fadeout(fade_duration)

    def _blur(self, clip: VideoFileClip) -> VideoFileClip:
        return clip.fx(vfx.blur, 2)

    def _brighten(self, clip: VideoFileClip) -> VideoFileClip:
        return clip.fx(vfx.colorx, 1.2)

    def _darken(self, clip: VideoFileClip) -> VideoFileClip:
        return clip.fx(vfx.colorx, 0.8) 