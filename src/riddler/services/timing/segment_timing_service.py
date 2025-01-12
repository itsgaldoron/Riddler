import logging
from typing import Dict, List
from riddler.config.exceptions import TimingServiceError
from riddler.services.timing.base import SegmentTimingServiceBase
from riddler.utils.logger import log

class SegmentTimingService(SegmentTimingServiceBase):
    def __init__(self, config: Dict = None, logger=None):
        self.config = config or {}
        self.logger = logger or log
        
        # Get timing configurations from config
        riddle_config = self.config.get("riddle", {})
        timing_config = riddle_config.get("timing", {})
        
        # Default timing configurations
        self.default_timings = {
            "hook": {
                "end_padding": timing_config.get("hook", {}).get("end_padding", 0.5)
            },
            "question": {
                "end_padding": timing_config.get("question", {}).get("end_padding", 1.0)
            },
            "thinking": {
                "end_padding": timing_config.get("thinking", {}).get("end_padding", 0.25)
            },
            "answer": {
                "end_padding": timing_config.get("answer", {}).get("end_padding", 1.5)
            },
            "transition": {
                "end_padding": 0.25
            }
        }
        
        # Update with config values if provided
        if config and "timing" in config:
            self._update_timing_config(config["timing"])

    def calculate_segment_timings(
        self,
        segments: List[Dict],
        config: Dict
    ) -> List[Dict[str, float]]:
        try:
            timings = []
            
            for segment in segments:
                segment_type = segment.get("type", "default")
                segment_id = segment.get("id")
                
                if not segment_id:
                    raise TimingServiceError("Segment missing ID")
                
                # Get base duration
                base_duration = 0
                if segment_type == "thinking":
                    # For thinking segments, base duration is 0 since there's no voiceover
                    base_duration = 0
                else:
                    # For other segments, get duration from voice clip if present
                    voice_path = segment.get("voice_path")
                    if voice_path:
                        from moviepy.editor import AudioFileClip
                        with AudioFileClip(voice_path) as audio:
                            base_duration = audio.duration
                
                # Get timing config for segment type
                timing_config = self.default_timings.get(
                    segment_type,
                    self.default_timings["question"]  # Default to question timing
                )
                
                # Get end padding
                end_padding = timing_config.get("end_padding", 0)
                
                # Calculate final duration (base duration plus end padding)
                final_duration = base_duration + end_padding
                
                timings.append({
                    "id": segment_id,
                    "type": segment_type,
                    "duration": final_duration,
                    "base_duration": base_duration,
                    "end_padding": end_padding
                })
            
            # Validate the timings
            if not self.validate_timings(timings, config):
                raise TimingServiceError("Invalid segment timings")
            
            return timings
            
        except Exception as e:
            self.logger.error(f"Failed to calculate segment timings: {str(e)}")
            raise TimingServiceError(f"Failed to calculate segment timings: {str(e)}")

    def validate_timings(
        self,
        timings: List[Dict[str, float]],
        config: Dict
    ) -> bool:
        try:
            if not timings:
                return False
            
            # Get total duration limits from config
            video_config = config.get("video", {})
            duration_config = video_config.get("duration", {})
            min_total_duration = duration_config.get("min_total", 60.0)
            max_total_duration = duration_config.get("max_total", 90.0)
            
            # Calculate total duration
            total_duration = sum(timing["duration"] for timing in timings)
            
            # Check total duration
            if total_duration < min_total_duration:
                self.logger.warning(
                    f"Total duration {total_duration:.2f}s is less than minimum {min_total_duration}s"
                )
                return False
                
            if total_duration > max_total_duration:
                self.logger.warning(
                    f"Total duration {total_duration:.2f}s exceeds maximum {max_total_duration}s"
                )
                return False
            
            # Check individual segment durations
            for timing in timings:
                if timing["duration"] <= 0:
                    self.logger.warning(f"Invalid duration for segment {timing['id']}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate timings: {str(e)}")
            return False

    def _update_timing_config(self, timing_config: Dict):
        """Update default timing configurations with provided values."""
        for segment_type, config in timing_config.items():
            if segment_type in self.default_timings:
                self.default_timings[segment_type].update(config) 