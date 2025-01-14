"""Configuration schema validation"""

from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum
from riddler.config.exceptions import ConfigValidationError

class VideoOrientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"

class TextPosition(str, Enum):
    CENTER = "center"
    LOWER_THIRD = "lower_third"
    SMART = "smart"

@dataclass
class TTSConfig:
    """Text-to-speech configuration."""
    provider: str
    voice_id: str
    model: str
    stability: float
    similarity_boost: float
    cache_dir: str
    language: str

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate TTS configuration."""
        if not 0 <= data.get("stability", 0) <= 1:
            raise ConfigValidationError("Stability must be between 0 and 1")
        if not 0 <= data.get("similarity_boost", 0) <= 1:
            raise ConfigValidationError("Similarity boost must be between 0 and 1")

@dataclass
class VideoResolution:
    """Video resolution configuration."""
    width: int
    height: int

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate video resolution."""
        if data.get("width", 0) < 1 or data.get("height", 0) < 1:
            raise ConfigValidationError("Width and height must be positive")

@dataclass
class VideoDuration:
    """Video duration configuration."""
    min_total: int
    max_total: int
    target_total: int
    min_segment: int
    max_segment: int

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate video duration."""
        if data.get("min_total", 0) > data.get("max_total", 0):
            raise ConfigValidationError("Minimum total duration cannot exceed maximum")
        if data.get("target_total", 0) > data.get("max_total", 0):
            raise ConfigValidationError("Target duration cannot exceed maximum")

@dataclass
class PexelsConfig:
    """Pexels API configuration."""
    categories: List[str]
    resolution: VideoResolution
    fps: int
    preferred_orientation: str
    min_duration: int
    max_duration: int

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate Pexels configuration."""
        if not data.get("categories"):
            raise ConfigValidationError("At least one category is required")
        if data.get("min_duration", 0) > data.get("max_duration", 0):
            raise ConfigValidationError("Minimum duration cannot exceed maximum")

@dataclass
class VideoTextConfig:
    """Video text overlay configuration."""
    font_scale: float
    font_thickness: int
    font_color: List[int]
    background_color: List[int]
    font_size: int
    font_family: str
    background_opacity: float
    position: str

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate video text configuration."""
        if not 0 <= data.get("background_opacity", 0) <= 1:
            raise ConfigValidationError("Background opacity must be between 0 and 1")
        if not all(0 <= c <= 255 for c in data.get("font_color", [])):
            raise ConfigValidationError("Font color values must be between 0 and 255")

@dataclass
class VideoEffects:
    """Video effects configuration."""
    zoom: Dict[str, Any]

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate video effects."""
        if "zoom" in data and not isinstance(data["zoom"], dict):
            raise ConfigValidationError("Zoom configuration must be a dictionary")

@dataclass
class TikTokOptimization:
    """TikTok optimization configuration."""
    target_duration: int
    hook_duration: int
    end_screen_duration: int
    sound_effects: Dict[str, Any]

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate TikTok optimization."""
        if not 15 <= data.get("target_duration", 0) <= 60:
            raise ConfigValidationError("Target duration must be between 15 and 60 seconds")
        if "sound_effects" in data:
            if not 0 <= data["sound_effects"].get("background_music_volume", 0) <= 1:
                raise ConfigValidationError("Background music volume must be between 0 and 1")

@dataclass
class VideoConfig:
    """Video configuration."""
    min_duration: int
    max_duration: int
    min_width: int
    min_height: int
    orientation: str
    resolution: VideoResolution
    fps: int
    pexels: PexelsConfig
    text: VideoTextConfig
    effects: VideoEffects
    duration: VideoDuration
    tiktok_optimization: TikTokOptimization
    cache_dir: str
    max_cache_size_gb: int

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate video configuration."""
        if data.get("min_duration", 0) > data.get("max_duration", 0):
            raise ConfigValidationError("Minimum duration cannot exceed maximum")
        if data.get("orientation") not in ["portrait", "landscape", "square"]:
            raise ConfigValidationError("Invalid orientation")

@dataclass
class RiddleTiming:
    """Riddle timing configuration."""
    hook: Dict[str, int]
    cta: Dict[str, int]
    thinking: Dict[str, int]
    question: Dict[str, int]
    answer: Dict[str, int]

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate riddle timing."""
        for section in ["hook", "cta", "thinking", "question", "answer"]:
            if section in data and not isinstance(data[section], dict):
                raise ConfigValidationError(f"{section} timing must be a dictionary")

@dataclass
class RiddleFormat:
    """Riddle format configuration."""
    hook_patterns: List[str]
    challenge_patterns: List[str]
    reveal_patterns: List[str]

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate riddle format."""
        if not data.get("hook_patterns"):
            raise ConfigValidationError("At least one hook pattern is required")
        if not data.get("challenge_patterns"):
            raise ConfigValidationError("At least one challenge pattern is required")
        if not data.get("reveal_patterns"):
            raise ConfigValidationError("At least one reveal pattern is required")

@dataclass
class OpenAIDifficultyLevel:
    """OpenAI difficulty level configuration."""
    complexity: float
    educational_level: str

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate difficulty level."""
        if not 0 <= data.get("complexity", 0) <= 1:
            raise ConfigValidationError("Complexity must be between 0 and 1")
        if data.get("educational_level") not in ["elementary", "high_school", "college"]:
            raise ConfigValidationError("Invalid educational level")

@dataclass
class OpenAITemplate:
    """OpenAI template configuration."""
    system_prompt: str
    example_format: str

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate template."""
        if not data.get("system_prompt"):
            raise ConfigValidationError("System prompt is required")
        if not data.get("example_format"):
            raise ConfigValidationError("Example format is required")

@dataclass
class OpenAIRiddleGeneration:
    """OpenAI riddle generation configuration."""
    categories: List[str]
    difficulty_levels: Dict[str, OpenAIDifficultyLevel]
    templates: Dict[str, OpenAITemplate]

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate riddle generation configuration."""
        valid_categories = ["geography", "math", "physics", "history", "logic", "wordplay"]
        for category in data.get("categories", []):
            if category not in valid_categories:
                raise ConfigValidationError(f"Invalid category: {category}")

@dataclass
class OpenAIConfig:
    """OpenAI configuration."""
    model: str
    temperature: float
    max_tokens: int
    max_attempts: int
    cache_dir: str
    riddle_generation: OpenAIRiddleGeneration

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate OpenAI configuration."""
        if not data.get("model"):
            raise ConfigValidationError("OpenAI model is required")
        if not 0 <= data.get("temperature", 0) <= 2:
            raise ConfigValidationError("Temperature must be between 0 and 2")
        if data.get("max_tokens", 0) < 1:
            raise ConfigValidationError("Max tokens must be positive")

@dataclass
class ConfigSchema:
    """Configuration schema."""
    tts: TTSConfig
    video: VideoConfig
    presentation: Dict[str, Any]
    cache: Dict[str, Any]
    riddle: Dict[str, Any]
    openai: OpenAIConfig

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate configuration."""
        for key, value in data.items():
            if hasattr(self, key) and hasattr(getattr(self, key), "validate"):
                getattr(self, key).validate(value)

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration."""
        return {
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
                        "enabled": true,
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
                        "min_duration": 5,
                        "padding": 1
                    },
                    "cta": {
                        "min_duration": 4,
                        "padding": 1
                    },
                    "thinking": {
                        "duration": 6
                    },
                    "question": {
                        "padding": 2
                    },
                    "answer": {
                        "padding": 3
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
            },
            "openai": {
                "model": "gpt-4o-mini-2024-07-18",
                "temperature": 0.7,
                "max_tokens": 500,
                "max_attempts": 3,
                "cache_dir": "cache/riddles",
                "riddle_generation": {
                    "categories": [
                        "geography",
                        "math",
                        "physics",
                        "history",
                        "logic",
                        "wordplay"
                    ],
                    "difficulty_levels": {
                        "easy": {
                            "complexity": 0.3,
                            "educational_level": "elementary"
                        },
                        "medium": {
                            "complexity": 0.6,
                            "educational_level": "high_school"
                        },
                        "hard": {
                            "complexity": 0.9,
                            "educational_level": "college"
                        }
                    },
                    "templates": {
                        "geography": {
                            "system_prompt": "You are a geography expert creating engaging riddles about countries, landmarks, and geographical features.",
                            "example_format": "I have cities but no houses, rivers but no water, forests but no trees. What am I? Answer: A map"
                        },
                        "math": {
                            "system_prompt": "You are a mathematics expert creating riddles that make math fun and engaging.",
                            "example_format": "The more you take away, the larger I become. What am I? Answer: A hole"
                        },
                        "physics": {
                            "system_prompt": "You are a physics expert creating riddles about physical phenomena and scientific concepts.",
                            "example_format": "I am faster than light but cannot escape a mirror. What am I? Answer: A reflection"
                        },
                        "history": {
                            "system_prompt": "You are a history expert creating riddles about historical events, figures, and discoveries.",
                            "example_format": "I was signed in 1776, I declared something great, I helped make a nation, What date am I? Answer: July 4th"
                        },
                        "logic": {
                            "system_prompt": "You are a logic expert creating riddles that challenge the mind with deductive reasoning.",
                            "example_format": "Two fathers and two sons went fishing together. They caught three fish which they shared equally. How is this possible? Answer: There were only three people - a grandfather, his son, and his grandson"
                        },
                        "wordplay": {
                            "system_prompt": "You are a wordsmith creating riddles that play with language, puns, and double meanings.",
                            "example_format": "What has keys but no locks, space but no room, and you can enter but not go in? Answer: A keyboard"
                        }
                    }
                }
            }
        }