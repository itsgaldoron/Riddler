"""Configuration management"""

import os
import json
from typing import Dict, Any, Optional
from config.exceptions import ConfigurationError, ConfigValidationError
from utils.logger import log

class Configuration:
    """Configuration management for the application."""

    DEFAULT_CONFIG = {
        "tts": {
            "provider": "elevenlabs",
            "voice_id": "pqHfZKP75CvOlQylNhV4",
            "model": "eleven_monolingual_v1",
            "stability": 0.5,
            "similarity_boost": 0.75,
            "cache_dir": "cache/voice",
            "language": "en-US"
        },
        "video": {
            "min_duration": 30,
            "max_duration": 60,
            "min_width": 1080,
            "min_height": 1920,
            "orientation": "portrait",
            "resolution": {
                "width": 1080,
                "height": 1920
            },
            "fps": 30,
            "pexels": {
                "categories": ["landscape", "mountains", "ocean"],
                "resolution": {
                    "width": 1080,
                    "height": 1920
                },
                "fps": 30,
                "preferred_orientation": "portrait",
                "min_duration": 1,
                "max_duration": 3
            },
            "text": {
                "font_scale": 1.0,
                "font_thickness": 2,
                "font_color": [255, 255, 255],
                "background_color": [0, 0, 0],
                "font_size": 36,
                "font_family": "Arial",
                "background_opacity": 0.5,
                "position": "smart"
            },
            "effects": {
                "zoom": {
                    "enabled": True,
                    "max_scale": 1.2
                }
            },
            "duration": {
                "min_total": 60,
                "max_total": 90,
                "target_total": 75,
                "min_segment": 3,
                "max_segment": 3
            },
            "tiktok_optimization": {
                "target_duration": 27,
                "hook_duration": 3,
                "end_screen_duration": 2,
                "sound_effects": {
                    "enabled": True,
                    "background_music_volume": 0.1,
                    "voice_volume": 1.0
                }
            },
            "cache_dir": "cache/video",
            "max_cache_size_gb": 5
        },
        "presentation": {
            "text_overlay": {
                "font_size": 48,
                "font_family": "Arial",
                "color": "#FFFFFF",
                "background_opacity": 0.6,
                "padding": 20,
                "position": "smart"
            }
        },
        "cache": {
            "voice_dir": "cache/voice",
            "video_dir": "cache/video",
            "max_cache_size": 1000000000,
            "cleanup_threshold": 0.9
        },
        "riddle": {
            "timing": {
                "hook": {
                    "start_padding": 0.5,
                    "end_padding": 0.5
                },
                "cta": {
                    "start_padding": 0.5,
                    "end_padding": 0.5
                },
                "thinking": {
                    "start_padding": 0.25,
                    "end_padding": 0.25
                },
                "question": {
                    "start_padding": 1.0,
                    "end_padding": 1.0
                },
                "answer": {
                    "start_padding": 1.5,
                    "end_padding": 1.5
                },
                "transition": {
                    "start_padding": 0.25,
                    "end_padding": 0.25
                }
            },
            "format": {
                "hook_patterns": [
                    "Can You Solve These Mind-Bending Riddles?",
                    "Test Your Brain with These Riddles!",
                    "Only Geniuses Can Solve These Riddles!"
                ],
                "challenge_patterns": [
                    "Time to test your brain!",
                    "Think you're smart enough?",
                    "Bet you can't solve this!"
                ],
                "reveal_patterns": [
                    "The answer is...",
                    "Did you get it right?",
                    "Here's the solution!"
                ]
            }
        }
    }

    def __init__(self, config_path: Optional[str] = None, logger=None):
        self.logger = logger or log
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """Load configuration from a JSON file."""
        try:
            if not os.path.exists(config_path):
                self.logger.warning(f"Config file not found at {config_path}, using defaults")
                return

            with open(config_path, 'r') as f:
                user_config = json.load(f)

            # Deep merge user config with defaults
            self._deep_merge(self.config, user_config)
            
            # Validate the merged configuration
            self.validate_config()
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Failed to parse config file: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {str(e)}")

    def validate_config(self) -> None:
        """Validate the configuration values."""
        try:
            self._validate_video_config()
            self._validate_presentation_config()
            self._validate_cache_config()
            self._validate_riddle_config()
        except ConfigValidationError as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            raise

    def _validate_video_config(self) -> None:
        """Validate video-related configuration."""
        video_config = self.config.get("video", {})
        
        # Validate resolution
        resolution = video_config.get("resolution", {})
        width = resolution.get("width")
        height = resolution.get("height")
        
        if not isinstance(width, int) or width < video_config.get("min_width", 1080):
            raise ConfigValidationError("Invalid video width", "video.resolution.width", str(width))
        if not isinstance(height, int) or height < video_config.get("min_height", 1920):
            raise ConfigValidationError("Invalid video height", "video.resolution.height", str(height))

        # Validate durations
        duration = video_config.get("duration", {})
        min_total = duration.get("min_total")
        max_total = duration.get("max_total")
        
        if not isinstance(min_total, (int, float)) or min_total <= 0:
            raise ConfigValidationError("Invalid minimum total duration", "video.duration.min_total", str(min_total))
        if not isinstance(max_total, (int, float)) or max_total <= min_total:
            raise ConfigValidationError("Invalid maximum total duration", "video.duration.max_total", str(max_total))

    def _validate_presentation_config(self) -> None:
        """Validate presentation-related configuration."""
        text_config = self.config.get("presentation", {}).get("text_overlay", {})
        
        # Validate font size
        font_size = text_config.get("font_size")
        if not isinstance(font_size, int) or font_size <= 0:
            raise ConfigValidationError("Invalid font size", "presentation.text_overlay.font_size", str(font_size))
            
        # Validate opacity
        opacity = text_config.get("background_opacity")
        if not isinstance(opacity, (int, float)) or not 0 <= opacity <= 1:
            raise ConfigValidationError("Invalid background opacity", "presentation.text_overlay.background_opacity", str(opacity))

    def _validate_cache_config(self) -> None:
        """Validate cache-related configuration."""
        cache_config = self.config.get("cache", {})
        
        # Validate cache size
        max_size = cache_config.get("max_cache_size")
        if not isinstance(max_size, int) or max_size <= 0:
            raise ConfigValidationError("Invalid max cache size", "cache.max_cache_size", str(max_size))
        
        # Validate cleanup threshold
        threshold = cache_config.get("cleanup_threshold")
        if not isinstance(threshold, (int, float)) or not 0 < threshold < 1:
            raise ConfigValidationError("Invalid cleanup threshold", "cache.cleanup_threshold", str(threshold))

    def _validate_riddle_config(self) -> None:
        """Validate riddle-related configuration."""
        timing_config = self.config.get("riddle", {}).get("timing", {})
        
        for segment_type, timing in timing_config.items():
            for padding_type in ["start_padding", "end_padding"]:
                if padding_type in timing:
                    padding = timing[padding_type]
                    if not isinstance(padding, (int, float)) or padding < 0:
                        raise ConfigValidationError(
                            f"Invalid {padding_type} for {segment_type}",
                            f"riddle.timing.{segment_type}.{padding_type}",
                            str(padding)
                        )

    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        try:
            value = self.config
            for k in key.split('.'):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
