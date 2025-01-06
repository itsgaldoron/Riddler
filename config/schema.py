"""Configuration schema validation"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from config.exceptions import ConfigValidationError

class VideoOrientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE = "square"

class TextPosition(str, Enum):
    CENTER = "center"
    LOWER_THIRD = "lower_third"
    SMART = "smart"

class AnimationStyle(str, Enum):
    SMOOTH = "smooth"
    BOUNCY = "bouncy"
    DRAMATIC = "dramatic"

class RiddleStyle(str, Enum):
    EDUCATIONAL = "educational"
    FUNNY = "funny"
    MYSTERIOUS = "mysterious"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class CTATiming(str, Enum):
    END = "end"
    MIDDLE = "middle"
    BOTH = "both"

@dataclass
class SocialLinks:
    tiktok: str
    instagram: Optional[str] = None

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate social links"""
        if not data.get("tiktok", "").startswith("@"):
            raise ValueError("TikTok handle must start with @")

@dataclass
class CreatorBranding:
    creator_name: str
    watermark: Optional[str] = None
    logo: Optional[str] = None
    social_links: Optional[SocialLinks] = None
    theme_color: str = "#FF5733"
    secondary_color: str = "#33FF57"
    font: str = "Poppins"

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate creator branding"""
        if not data.get("creator_name"):
            raise ValueError("Creator name is required")
        if "theme_color" in data and not data["theme_color"].startswith("#"):
            raise ValueError("Theme color must be a hex color code")
        if "secondary_color" in data and not data["secondary_color"].startswith("#"):
            raise ValueError("Secondary color must be a hex color code")

@dataclass
class RiddlePreferences:
    favorite_categories: List[str]
    default_difficulty: Difficulty
    style: RiddleStyle

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate riddle preferences"""
        valid_categories = ["geography", "math", "physics", "history", "logic", "wordplay"]
        for category in data.get("favorite_categories", []):
            if category not in valid_categories:
                raise ValueError(f"Invalid category: {category}")

@dataclass
class VoiceSettings:
    voice_id: str
    speaking_style: str = "engaging"
    speed: float = 1.0
    emphasis_level: float = 1.2

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate voice settings"""
        if not 0.5 <= data.get("speed", 1.0) <= 2.0:
            raise ValueError("Speed must be between 0.5 and 2.0")
        if not 0.5 <= data.get("emphasis_level", 1.0) <= 2.0:
            raise ValueError("Emphasis level must be between 0.5 and 2.0")

@dataclass
class MusicSettings:
    background_track: Optional[str] = None
    volume_levels: Optional[Dict[str, float]] = None

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate music settings"""
        if "volume_levels" in data:
            for key, value in data["volume_levels"].items():
                if not 0 <= value <= 1:
                    raise ValueError(f"Volume level for {key} must be between 0 and 1")

@dataclass
class TikTokOptimization:
    aspect_ratio: str = "9:16"
    target_duration: int = 27
    hook_duration: int = 3
    end_screen_duration: int = 2
    auto_captions: bool = True
    sound_effects: Optional[Dict[str, Any]] = None

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate TikTok optimization settings"""
        if data.get("aspect_ratio") != "9:16":
            raise ValueError("Aspect ratio must be 9:16 for TikTok")
        if not 15 <= data.get("target_duration", 0) <= 60:
            raise ValueError("Target duration must be between 15 and 60 seconds")
        if not 2 <= data.get("hook_duration", 0) <= 5:
            raise ValueError("Hook duration must be between 2 and 5 seconds")

@dataclass
class EngagementSettings:
    hooks: Dict[str, List[str]]
    calls_to_action: Dict[str, Any]
    hashtags: Dict[str, Any]

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate engagement settings"""
        if "hashtags" in data:
            max_count = data["hashtags"].get("max_count", 0)
            if not 1 <= max_count <= 30:
                raise ValueError("Hashtag count must be between 1 and 30")

@dataclass
class OpenAIRiddleTemplate:
    """Schema for OpenAI riddle template configuration."""
    system_prompt: str
    example_format: str
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate riddle template configuration."""
        if not data.get("system_prompt"):
            raise ConfigValidationError("System prompt is required for riddle template")
        if not data.get("example_format"):
            raise ConfigValidationError("Example format is required for riddle template")

@dataclass
class OpenAIDifficultyLevel:
    """Schema for OpenAI difficulty level configuration."""
    complexity: float = 0.5
    educational_level: str = "high_school"
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate difficulty level configuration."""
        if not 0 <= data.get("complexity", 0.5) <= 1:
            raise ConfigValidationError("Complexity must be between 0 and 1")
        if data.get("educational_level") not in ["elementary", "high_school", "college"]:
            raise ConfigValidationError("Invalid educational level")

@dataclass
class OpenAIRiddleGeneration:
    """Schema for OpenAI riddle generation configuration."""
    categories: List[str]
    difficulty_levels: Dict[str, Dict[str, Any]]
    templates: Dict[str, Dict[str, Any]]
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate riddle generation configuration."""
        if not data.get("categories"):
            raise ConfigValidationError("At least one category is required")
            
        for level_data in data.get("difficulty_levels", {}).values():
            OpenAIDifficultyLevel(**level_data).validate(level_data)
            
        for template_data in data.get("templates", {}).values():
            OpenAIRiddleTemplate(**template_data).validate(template_data)

@dataclass
class OpenAICommentaryGeneration:
    """Schema for OpenAI commentary generation configuration."""
    hooks: List[str]
    explanations: Dict[str, Any]
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate commentary generation configuration."""
        if not data.get("hooks"):
            raise ConfigValidationError("At least one hook pattern is required")
            
        if not isinstance(data.get("explanations"), dict):
            raise ConfigValidationError("Explanations must be a dictionary")
            
        required_explanation_keys = ["style", "format"]
        if not all(key in data.get("explanations", {}) for key in required_explanation_keys):
            raise ConfigValidationError("Missing required explanation settings")

@dataclass
class OpenAIConfig:
    """Schema for OpenAI configuration."""
    riddle_generation: Dict[str, Any]
    commentary_generation: Optional[Dict[str, Any]] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 500
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate OpenAI configuration."""
        if not data.get("model"):
            raise ConfigValidationError("OpenAI model is required")
            
        if not 0 <= data.get("temperature", 0.7) <= 2:
            raise ConfigValidationError("Temperature must be between 0 and 2")
            
        if data.get("max_tokens", 500) < 1:
            raise ConfigValidationError("Max tokens must be positive")
            
        if "riddle_generation" in data:
            OpenAIRiddleGeneration(**data["riddle_generation"]).validate(data["riddle_generation"])
        if "commentary_generation" in data:
            OpenAICommentaryGeneration(**data["commentary_generation"]).validate(data["commentary_generation"])

@dataclass
class ConfigSchema:
    """Configuration schema."""
    tts: Dict[str, Any]
    video: Dict[str, Any]
    presentation: Dict[str, Any]
    cache: Dict[str, Any]
    game: Dict[str, Any]
    audio: Dict[str, Any]
    visual_style: Dict[str, Any]
    riddle: Dict[str, Any]
    openai: Optional[Dict[str, Any]] = None
    creator: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    engagement: Optional[Dict[str, Any]] = None

    def validate(self, data: Dict[str, Any]) -> None:
        """Validate configuration."""
        if "openai" in data:
            OpenAIConfig(**data["openai"]).validate(data["openai"])
        if "creator" in data:
            CreatorBranding(**data["creator"]).validate(data["creator"])
        if "engagement" in data:
            EngagementSettings(**data["engagement"]).validate(data["engagement"])

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "tts": {
                "provider": "elevenlabs",
                "voice_id": "default",
                "speaking_rate": 1.0,
                "pitch": 0.0,
                "volume_gain_db": 0.0
            },
            "video": {
                "orientation": "portrait",
                "resolution": {
                    "width": 1080,
                    "height": 1920
                },
                "fps": 30,
                "duration": {
                    "min": 15,
                    "max": 60,
                    "target": 30
                },
                "background": {
                    "type": "video",
                    "blur": 0.5,
                    "opacity": 0.8
                }
            },
            "presentation": {
                "text_overlay": {
                    "font_size": 48,
                    "font_family": "Arial",
                    "color": "#FFFFFF",
                    "background_opacity": 0.6,
                    "padding": 20,
                    "position": "smart",
                    "smart_positioning": {
                        "avoid_faces": True,
                        "avoid_busy_areas": True,
                        "preferred_zones": ["center", "lower_third"]
                    }
                }
            },
            "cache": {
                "voice_dir": "cache/voice",
                "video_dir": "cache/video",
                "max_cache_size": 1000000000,
                "cleanup_threshold": 0.9
            },
            "game": {
                "countdown_duration": 60,
                "max_attempts": 3,
                "difficulty_levels": ["easy", "medium", "hard"]
            },
            "audio": {
                "countdown_file": "assets/audio/countdown.mp3",
                "answer_file": "assets/audio/reveal.mp3",
                "volume": 1.0,
                "supported_formats": ["wav", "mp3"]
            },
            "visual_style": {
                "question_emphasis": {
                    "keywords_highlight": True,
                    "zoom_on_key_parts": True
                },
                "answer_reveal": {
                    "style": "dramatic_buildup",
                    "animation": "fade_zoom",
                    "celebration_effect": True
                }
            },
            "riddle": {
                "format": {
                    "hook_patterns": [
                        "Can you solve this?",
                        "Only 1% can figure this out",
                        "Watch till the end!",
                        "Your IQ is {number} if you get this right"
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
                },
                "timing": {
                    "hook_duration": 3,
                    "question_duration": 15,
                    "thinking_time": 5,
                    "reveal_duration": 4
                }
            },
            "openai": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 500,
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
                        "default": {
                            "system_prompt": "You are a creative riddle generator. Create engaging and educational riddles that are fun to solve.",
                            "example_format": "Here's a {difficulty} {category} riddle:\n{riddle}\nAnswer: {answer}"
                        }
                    }
                }
            }
        } 