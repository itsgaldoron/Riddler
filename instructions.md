# AI-Friendly Code Refactoring Guide

## Project Overview

This project is designed to create viral riddle videos for TikTok using AI-powered content generation and modern video production techniques. The system automatically generates, produces, and optimizes educational riddle videos that are specifically crafted for TikTok's viral ecosystem.

### Key Features
1. **AI-Generated Content**
   - Smart riddle generation across multiple categories (geography, math, physics, etc.)
   - Dynamic commentary and explanations
   - Engaging video descriptions and hashtags

2. **Professional Production**
   - High-quality voice-over using ElevenLabs' Adam voice
   - 4K UHD background videos from Pexels
   - Smart text positioning and animations
   - TikTok-optimized format (9:16 aspect ratio)

3. **Viral Optimization**
   - Attention-grabbing hooks
   - Strategic pacing and timing
   - Engagement prompts
   - Call-to-action optimization
   - Smart hashtag strategy

### Target Audience
- Educational content creators
- TikTok influencers
- Knowledge-sharing channels
- Riddle enthusiasts
- Educational institutions

### Content Categories
- Geography riddles
- Mathematical puzzles
- Physics brain-teasers
- Historical mysteries
- Logic challenges
- Wordplay riddles

### Viral Strategy
1. **Hook & Retention**
   - First 3 seconds grab attention
   - Educational value keeps viewers engaged
   - Strategic pauses for interaction
   - Satisfying reveal and explanation

2. **Engagement Triggers**
   - Comment prompts
   - Difficulty indicators
   - Think-time encouragement
   - Share-worthy content

3. **Growth Mechanics**
   - Series potential
   - Cross-category appeal
   - Educational hashtags
   - Community building

This guide is designed for AI code generators to refactor the Riddler project while maintaining all existing functionality. Each section includes explicit instructions and examples.

## Current Functionality Overview

1. **Text-to-Speech (TTS)**
   - Caches voice outputs in `voice_cache/`
   - Uses hash-based filenames (e.g., `3326441952578474770.mp3`)

2. **Video Management**
   - Fetches videos from Pexels API
   - Caches in `pexels_cache/`
   - Supports UHD resolution (2160p/4K)
   - Categories: "world map globe", "world celebration"

3. **Audio System**
   - Plays countdown.wav for timer
   - Plays answer.wav for responses
   - Supports volume control

## Project Structure

```
riddler/
├── config/
│   ├── __init__.py
│   ├── config.py        # Configuration class and settings
│   ├── constants.py     # Global constants
│   └── exceptions.py    # Custom exceptions
├── core/
│   ├── __init__.py
│   ├── riddler.py       # Main game logic
│   ├── game_state.py    # Game state management
│   └── types.py        # Type definitions
├── services/
│   ├── __init__.py
│   ├── audio_service.py # Audio handling
│   ├── video_service.py # Video handling (Pexels integration)
│   └── tts_service.py   # Text-to-speech service
├── utils/
│   ├── __init__.py
│   ├── cache.py        # Cache management
│   ├── validators.py   # Input validation
│   └── helpers.py      # Utility functions
├── tests/              # Test directory structure
├── cache/             
│   ├── voice/          # TTS cache
│   └── video/          # Pexels video cache
├── assets/            
│   ├── audio/
│   └── video/
└── [configuration files]
```

## Creator Configuration Guide

This section provides an easy way to modify all aspects of your riddle videos. All settings are in one place for quick modifications.

### Quick Start Configuration (creator_config.json)
```json
{
  "creator": {
    "branding": {
      "creator_name": "Your Name",
      "watermark": "assets/branding/watermark.png",
      "logo": "assets/branding/logo.png",
      "social_links": {
        "tiktok": "@your_handle",
        "instagram": "@your_handle"
      }
    },
    "style": {
      "theme_color": "#FF5733",
      "secondary_color": "#33FF57",
      "font": "Poppins",
      "emoji_style": "minimal"  // minimal, moderate, heavy
    }
  },
  "content": {
    "riddle_preferences": {
      "favorite_categories": [
        "geography",
        "math",
        "physics"
      ],
      "default_difficulty": "medium",
      "style": "educational"  // educational, funny, mysterious
    },
    "voice": {
      "voice_id": "Adam",
      "speaking_style": "engaging",
      "speed": 1.0,
      "emphasis_level": 1.2
    },
    "music": {
      "background_track": "assets/audio/background.mp3",
      "volume_levels": {
        "voice": 1.0,
        "background": 0.1,
        "effects": 0.5
      }
    }
  },
  "video": {
    "style_preferences": {
      "preferred_backgrounds": [
        "world map globe",
        "space nebula",
        "abstract waves"
      ],
      "text_position": "center",  // center, lower_third, smart
      "animation_style": "smooth"  // smooth, bouncy, dramatic
    },
    "timing": {
      "total_duration": 27,
      "hook_duration": 3,
      "thinking_time": 5,
      "reveal_duration": 4
    }
  },
  "engagement": {
    "hooks": {
      "custom_patterns": [
        "Can you crack this {category} riddle?",
        "Only genius can solve this!",
        "Watch how this {category} trick works!"
      ]
    },
    "calls_to_action": {
      "primary": "Follow for more riddles!",
      "secondary": "Comment your answer below! 👇",
      "timing": "end"  // end, middle, both
    },
    "hashtags": {
      "always_include": [
        "#riddles",
        "#brainteaser",
        "#{category}riddle"
      ],
      "max_count": 5
    }
  }
}
```

### Easy Modifications Guide

1. **Branding and Style**
   ```json
   {
     "creator": {
       "branding": {
         "creator_name": "CHANGE THIS",
         "social_links": {
           "tiktok": "CHANGE THIS"
         }
       },
       "style": {
         "theme_color": "CHANGE THIS",
         "font": "CHANGE THIS"
       }
     }
   }
   ```

2. **Content Preferences**
   ```json
   {
     "content": {
       "riddle_preferences": {
         "favorite_categories": [
           "ADD YOUR PREFERRED CATEGORIES"
         ],
         "default_difficulty": "CHANGE THIS"
       }
     }
   }
   ```

3. **Video Style**
   ```json
   {
     "video": {
       "style_preferences": {
         "preferred_backgrounds": [
           "ADD YOUR PREFERRED BACKGROUNDS"
         ],
         "animation_style": "CHANGE THIS"
       }
     }
   }
   ```

4. **Engagement Settings**
   ```json
   {
     "engagement": {
       "hooks": {
         "custom_patterns": [
           "ADD YOUR HOOK PHRASES"
         ]
       },
       "calls_to_action": {
         "primary": "CHANGE THIS"
       }
     }
   }
   ```

### Configuration Loading (config/creator_config.py)
```python
from pathlib import Path
from typing import Any, Dict
import json

class CreatorConfig:
    def __init__(self):
        self.config_path = Path("creator_config.json")
        self.load_config()

    def load_config(self):
        """Load creator configuration"""
        if not self.config_path.exists():
            self.create_default_config()
        
        with open(self.config_path) as f:
            self.config = json.load(f)

    def create_default_config(self):
        """Create default creator configuration"""
        default_config = {
            "creator": {
                "branding": {
                    "creator_name": "Creator Name",
                    "social_links": {"tiktok": "@handle"}
                }
            }
            # ... rest of default configuration
        }
        
        with open(self.config_path, "w") as f:
            json.dump(default_config, f, indent=2)

    def update_setting(self, path: str, value: Any):
        """
        Update a specific setting using dot notation.
        Example: update_setting("creator.branding.creator_name", "New Name")
        """
        current = self.config
        *parts, last = path.split(".")
        
        for part in parts:
            current = current.setdefault(part, {})
        
        current[last] = value
        self.save_config()

    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_setting(self, path: str, default: Any = None) -> Any:
        """
        Get a specific setting using dot notation.
        Example: get_setting("creator.branding.creator_name")
        """
        current = self.config
        try:
            for part in path.split("."):
                current = current[part]
            return current
        except (KeyError, TypeError):
            return default
```

### Usage Example
```python
# Initialize creator configuration
creator_config = CreatorConfig()

# Update branding
creator_config.update_setting("creator.branding.creator_name", "Riddle Master")
creator_config.update_setting("creator.style.theme_color", "#FF5733")

# Update content preferences
creator_config.update_setting("content.riddle_preferences.favorite_categories", 
    ["geography", "math", "physics"])

# Get settings
creator_name = creator_config.get_setting("creator.branding.creator_name")
theme_color = creator_config.get_setting("creator.style.theme_color")
```

The creator configuration provides:
1. Single source of truth for all settings
2. Easy modification of common settings
3. Organized grouping of related settings
4. Clear documentation and examples
5. Simple API for updating settings

## Configuration Files

### 1. config.json
```json
{
  "game": {
    "countdown_duration": 60,
    "max_attempts": 3,
    "difficulty_levels": ["easy", "medium", "hard"]
  },
  "audio": {
    "countdown_file": "assets/audio/countdown.wav",
    "answer_file": "assets/audio/answer.wav",
    "volume": 1.0,
    "supported_formats": ["wav", "mp3"]
  },
  "tts": {
    "provider": "elevenlabs",
    "voice_id": "Adam",
    "model": "eleven_monolingual_v1",
    "stability": 0.71,
    "similarity_boost": 0.75,
    "cache_dir": "cache/voice",
    "language": "en-US",
    "voice_settings": {
      "speaking_rate": 1.0,
      "pause_between_sentences": 0.8
    }
  },
  "video": {
    "pexels": {
      "categories": [
        "world map globe",
        "world celebration"
      ],
      "resolution": {
        "width": 3840,
        "height": 2160
      },
      "fps": 30,
      "preferred_orientation": "portrait",
      "min_duration": 15,
      "max_duration": 60,
      "quality": "4k"
    },
    "tiktok_optimization": {
      "aspect_ratio": "9:16",
      "target_duration": 27,
      "hook_duration": 3,
      "end_screen_duration": 2,
      "auto_captions": true,
      "sound_effects": {
        "enabled": true,
        "background_music_volume": 0.1,
        "voice_volume": 1.0
      }
    },
    "cache_dir": "cache/video",
    "max_cache_size_gb": 1
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
        "avoid_faces": true,
        "avoid_busy_areas": true,
        "preferred_zones": ["center", "lower_third"]
      },
      "tiktok_style": {
        "text_animations": ["slide_up", "fade_in", "bounce"],
        "word_by_word": true,
        "emoji_usage": true,
        "highlight_keywords": true,
        "caption_style": "auto_sync"
      }
    },
    "timing": {
      "voice_break_threshold": 1.5,
      "min_text_duration": 3,
      "fade_duration": 0.5,
      "hook_timing": {
        "initial_pause": 0.5,
        "word_timing": 0.2,
        "emphasis_words_delay": 0.3
      }
    },
    "engagement": {
      "hook_text": {
        "position": "center",
        "style": "dramatic",
        "animation": "scale_up"
      },
      "call_to_action": {
        "enabled": true,
        "position": "bottom",
        "timing": "last_3_seconds"
      },
      "visual_effects": {
        "zoom": {
          "enabled": true,
          "speed": "slow",
          "max_scale": 1.1
        },
        "transitions": {
          "type": "smooth_fade",
          "duration": 0.3
        }
      }
    }
  },
  "cache": {
    "voice_dir": "cache/voice",
    "video_dir": "cache/video",
    "max_cache_size": 1000000000,
    "cleanup_threshold": 0.9
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
    },
    "engagement": {
      "countdown": {
        "enabled": true,
        "duration": 5,
        "style": "dramatic"
      },
      "difficulty_indicator": {
        "enabled": true,
        "style": "brain_emoji",
        "levels": {
          "easy": "🧠",
          "medium": "🧠🧠",
          "hard": "🧠🧠🧠"
        }
      },
      "interactive_elements": {
        "pause_prompt": {
          "enabled": true,
          "text": "Pause now to think!",
          "duration": 2
        },
        "comment_prompt": {
          "enabled": true,
          "text": "Comment your answer below! 👇",
          "timing": "before_reveal"
        }
      }
    },
    "visual_style": {
      "question_emphasis": {
        "keywords_highlight": true,
        "zoom_on_key_parts": true
      },
      "answer_reveal": {
        "style": "dramatic_buildup",
        "animation": "fade_zoom",
        "celebration_effect": true
      }
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
        }
      }
    },
    "commentary_generation": {
      "hooks": [
        "This mind-bending {category} riddle will test your knowledge!",
        "Only true {category} experts can solve this one!",
        "Think you know {category}? Prove it!"
      ],
      "explanations": {
        "style": "educational",
        "format": "step_by_step",
        "include_fun_facts": true,
        "engagement_level": "high"
      }
    }
  }
}
```

### 2. .env
```plaintext
RIDDLER_PEXELS_API_KEY=your_pexels_api_key
RIDDLER_ELEVENLABS_API_KEY=your_elevenlabs_api_key
RIDDLER_OPENAI_API_KEY=your_openai_api_key
RIDDLER_GAME_COUNTDOWN_DURATION=60
```

## Service Implementation Examples

### 1. TTS Service (services/tts_service.py)
```python
from pathlib import Path
from typing import Optional
from config.config import Config
from utils.cache import CacheManager
import requests

class TTSService:
    def __init__(self):
        self.config = Config()
        self.cache_manager = CacheManager(
            self.config.get("tts.cache_dir"),
            self.config.get("cache.max_cache_size")
        )
        self.voice_id = self.config.get("tts.voice_id")
        self.api_key = os.getenv("RIDDLER_ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"

    def generate_speech(self, text: str) -> Path:
        """
        Generate speech from text using ElevenLabs API with Adam's voice.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Path to the audio file
        """
        cache_key = str(hash(text))
        cached_path = self.cache_manager.get(cache_key)
        if cached_path:
            return cached_path

        # ElevenLabs API call
        url = f"{self.base_url}/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": self.config.get("tts.model"),
            "voice_settings": {
                "stability": self.config.get("tts.stability"),
                "similarity_boost": self.config.get("tts.similarity_boost")
            }
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise TTSError(f"ElevenLabs API error: {response.text}")

        # Save to cache
        temp_path = Path("temp.mp3")
        temp_path.write_bytes(response.content)
        return self.cache_manager.put(cache_key, temp_path)
```

### 2. Video Service (services/video_service.py)
```python
from pathlib import Path
from typing import List, Optional
from config.config import Config
from utils.cache import CacheManager
import requests

class VideoService:
    def __init__(self):
        self.config = Config()
        self.cache_manager = CacheManager(
            self.config.get("video.cache_dir"),
            self.config.get("cache.max_cache_size")
        )
        self.categories = self.config.get("video.pexels.categories")
        self.api_key = os.getenv("RIDDLER_PEXELS_API_KEY")

    def get_video(self, category: str) -> Optional[Path]:
        """
        Get a high-quality video from Pexels for the specified category.
        
        Args:
            category: Video category (e.g., "world map globe")
            
        Returns:
            Path to the video file
        """
        cache_key = f"{category}_{hash(category)}"
        cached_path = self.cache_manager.get(cache_key)
        if cached_path:
            return cached_path

        # Pexels API call
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.api_key}
        params = {
            "query": category,
            "orientation": self.config.get("video.pexels.preferred_orientation"),
            "size": "large",
            "per_page": 15,
            "min_duration": self.config.get("video.pexels.min_duration"),
            "max_duration": self.config.get("video.pexels.max_duration")
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise VideoError(f"Pexels API error: {response.text}")

        videos = response.json().get("videos", [])
        if not videos:
            raise VideoError(f"No videos found for category: {category}")

        # Find the highest quality video file
        video_files = videos[0]["video_files"]
        uhd_video = next(
            (v for v in video_files 
             if v["width"] == self.config.get("video.pexels.resolution.width") 
             and v["height"] == self.config.get("video.pexels.resolution.height")),
            None
        )

        if not uhd_video:
            raise VideoError("No UHD video found")

        # Download and cache video
        video_response = requests.get(uhd_video["link"], stream=True)
        temp_path = Path("temp.mp4")
        with temp_path.open("wb") as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)

        return self.cache_manager.put(cache_key, temp_path)
```

### 3. Presentation Service (services/presentation_service.py)
```python
from pathlib import Path
from typing import Dict, Tuple
from config.config import Config
import cv2
import numpy as np

class PresentationService:
    def __init__(self):
        self.config = Config()
        self.text_config = self.config.get("presentation.text_overlay")
        self.timing_config = self.config.get("presentation.timing")
        self.engagement_config = self.config.get("presentation.engagement")
        self.tiktok_config = self.config.get("video.tiktok_optimization")

    def calculate_text_position(self, frame: np.ndarray, text: str) -> Tuple[int, int]:
        """
        Calculate optimal text position avoiding faces and busy areas.
        
        Args:
            frame: Video frame
            text: Text to overlay
            
        Returns:
            Tuple of x, y coordinates
        """
        if self.text_config["position"] != "smart":
            return self._get_fixed_position(frame.shape)

        # Implement smart positioning logic
        # - Face detection
        # - Busy area detection
        # - Preferred zone selection
        # Return optimal x, y coordinates

    def create_text_overlay(self, video_path: Path, text_segments: List[Dict]) -> Path:
        """
        Create video with text overlays and proper timing.
        
        Args:
            video_path: Path to background video
            text_segments: List of {text, start_time, duration} dicts
            
        Returns:
            Path to rendered video
        """
        # Implementation for text overlay with smart positioning
        # and timing synchronized with voice-over

    def create_tiktok_video(self, video_path: Path, text_segments: List[Dict]) -> Path:
        """
        Create TikTok-optimized video with viral-friendly features.
        
        Args:
            video_path: Path to background video
            text_segments: List of {text, start_time, duration} dicts
            
        Returns:
            Path to rendered video
        """
        # Load video and prepare canvas
        video = cv2.VideoCapture(str(video_path))
        
        # Create hook section (first 3 seconds)
        self._create_hook_section(video, text_segments[0])
        
        # Process main content
        self._process_main_content(video, text_segments)
        
        # Add call to action
        self._add_call_to_action(video)
        
        return self._render_final_video(video)

    def _create_hook_section(self, video: cv2.VideoCapture, first_segment: Dict) -> None:
        """Create attention-grabbing hook section"""
        hook_config = self.engagement_config["hook_text"]
        
        # Implementation for dramatic hook
        # - Large, centered text
        # - Word-by-word animation
        # - Zoom effect
        # - Background music build-up

    def _process_main_content(self, video: cv2.VideoCapture, segments: List[Dict]) -> None:
        """Process main video content with TikTok optimizations"""
        tiktok_style = self.text_config["tiktok_style"]
        
        for segment in segments:
            # Apply text animations
            if tiktok_style["word_by_word"]:
                self._animate_words(segment["text"])
            
            # Add visual interest
            self._apply_zoom_effect()
            
            # Synchronize with voice
            self._sync_text_with_audio(segment)

    def _animate_words(self, text: str) -> None:
        """Animate text word by word with TikTok-style effects"""
        words = text.split()
        animations = self.text_config["tiktok_style"]["text_animations"]
        
        for word in words:
            animation = random.choice(animations)
            # Apply animation to word
            # Add slight delay between words

    def _sync_text_with_audio(self, segment: Dict) -> None:
        """Synchronize text with voice-over timing"""
        # Use voice timing to match text appearance
        # Add emphasis on key words
        # Handle pauses naturally

    def _add_call_to_action(self, video: cv2.VideoCapture) -> None:
        """Add engaging call to action at the end"""
        cta_config = self.engagement_config["call_to_action"]
        
        if cta_config["enabled"]:
            # Add animated CTA
            # Include subtle motion
            # Optimize timing

    def _apply_zoom_effect(self) -> None:
        """Apply subtle zoom effect for visual interest"""
        zoom_config = self.engagement_config["visual_effects"]["zoom"]
        
        if zoom_config["enabled"]:
            # Implement smooth zoom
            # Maintain focus on text
            # Control zoom speed

    def _render_final_video(self, video: cv2.VideoCapture) -> Path:
        """Render final video with all TikTok optimizations"""
        # Ensure portrait orientation
        # Apply final effects
        # Optimize for TikTok platform
        # Return rendered video path
```

### 4. Riddle Generator Service (services/riddle_generator.py)
```python
from typing import Dict, List
import openai
from config.config import Config

class RiddleGeneratorService:
    def __init__(self):
        self.config = Config()
        self.openai_config = self.config.get("openai")
        openai.api_key = os.getenv("RIDDLER_OPENAI_API_KEY")

    def generate_riddle(self, category: str, difficulty: str) -> Dict[str, str]:
        """
        Generate a riddle and its solution using OpenAI.
        
        Args:
            category: Riddle category (e.g., "geography", "math")
            difficulty: Difficulty level
            
        Returns:
            Dictionary containing riddle, answer, and explanation
        """
        template = self.openai_config["riddle_generation"]["templates"][category]
        difficulty_config = self.openai_config["riddle_generation"]["difficulty_levels"][difficulty]

        system_prompt = template["system_prompt"]
        user_prompt = f"""
        Create an engaging {category} riddle with these requirements:
        - Difficulty: {difficulty} (complexity: {difficulty_config['complexity']})
        - Educational level: {difficulty_config['educational_level']}
        - Must be solvable within 15 seconds
        - Include a clear, concise answer
        - Provide a brief, educational explanation
        
        Format:
        Riddle: [the riddle]
        Answer: [concise answer]
        Explanation: [educational explanation]
        Fun Fact: [related interesting fact]
        """

        response = openai.ChatCompletion.create(
            model=self.openai_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.openai_config["temperature"],
            max_tokens=self.openai_config["max_tokens"]
        )

        return self._parse_riddle_response(response.choices[0].message.content)

    def generate_commentary(self, riddle_data: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Generate engaging commentary for the riddle video.
        
        Args:
            riddle_data: Dictionary containing riddle, answer, and explanation
            
        Returns:
            List of commentary segments with timing
        """
        commentary_config = self.openai_config["commentary_generation"]
        
        system_prompt = """
        Create engaging TikTok commentary for a riddle video. Include:
        1. Attention-grabbing hook
        2. Riddle presentation
        3. Think-time prompt
        4. Answer reveal
        5. Educational explanation
        6. Fun fact
        7. Call-to-action
        
        Make it dynamic and engaging for TikTok.
        """

        user_prompt = f"""
        Create commentary for this riddle:
        {riddle_data['riddle']}
        
        Answer: {riddle_data['answer']}
        Explanation: {riddle_data['explanation']}
        Fun Fact: {riddle_data['fun_fact']}
        
        Format each segment with timing and style instructions.
        """

        response = openai.ChatCompletion.create(
            model=self.openai_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.openai_config["temperature"]
        )

        return self._parse_commentary_response(response.choices[0].message.content)

    def _parse_riddle_response(self, response: str) -> Dict[str, str]:
        """Parse the OpenAI response into structured riddle data"""
        # Implementation to parse the response into components
        # Return dictionary with riddle, answer, explanation, fun_fact

    def _parse_commentary_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the OpenAI response into timed commentary segments"""
        # Implementation to parse the response into timed segments
        # Return list of segments with text and timing
```

### 5. Usage Example
```python
# Create engaging geography riddle video
riddle_generator = RiddleGeneratorService()
presentation = PresentationService()
tts = TTSService()
video = VideoService()

# Generate riddle and commentary
riddle_data = riddle_generator.generate_riddle("geography", "medium")
commentary = riddle_generator.generate_commentary(riddle_data)

# Get background video
video_path = video.get_video("world map globe")

# Generate voice-overs for each commentary segment
audio_segments = [
    tts.generate_speech(segment["text"])
    for segment in commentary
]

# Create final video
final_video = presentation.create_tiktok_video(
    video_path=video_path,
    text_segments=commentary
)
```

### 6. Video Description Generator (services/description_generator.py)
```python
from typing import Dict, List
import openai
from config.config import Config

class DescriptionGeneratorService:
    def __init__(self):
        self.config = Config()
        self.openai_config = self.config.get("openai")
        openai.api_key = os.getenv("RIDDLER_OPENAI_API_KEY")

    def generate_description(self, riddle_data: Dict[str, str], category: str) -> Dict[str, str]:
        """
        Generate TikTok video description with hashtags and engagement hooks.
        
        Args:
            riddle_data: Dictionary containing riddle info
            category: Riddle category
            
        Returns:
            Dictionary containing description, hashtags, and hooks
        """
        system_prompt = """
        Create an engaging TikTok video description that:
        1. Hooks viewers with an intriguing question
        2. Uses relevant hashtags
        3. Encourages engagement (likes, comments, follows)
        4. Includes category-specific keywords
        5. Follows TikTok best practices
        """

        user_prompt = f"""
        Create a TikTok description for this {category} riddle:
        Riddle: {riddle_data['riddle']}
        Category: {category}
        Difficulty: {riddle_data.get('difficulty', 'medium')}

        Include:
        1. Main description (compelling hook)
        2. Relevant hashtags (max 5)
        3. Engagement prompt
        4. Category-specific keywords

        Format:
        Description: [engaging text]
        Hashtags: [hashtag list]
        Keywords: [keyword list]
        """

        response = openai.ChatCompletion.create(
            model=self.openai_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        return self._parse_description_response(response.choices[0].message.content)

    def _parse_description_response(self, response: str) -> Dict[str, str]:
        """Parse OpenAI response into description components"""
        # Implementation to parse response into description parts
        # Return dictionary with description, hashtags, keywords
```

### 7. CLI Interface (main.py)
```python
import argparse
import json
from pathlib import Path
from typing import Dict, Optional
from config.creator_config import CreatorConfig
from services.riddle_generator import RiddleGeneratorService
from services.description_generator import DescriptionGeneratorService
from services.presentation import PresentationService
from services.tts import TTSService
from services.video import VideoService

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TikTok Riddle Video Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate a geography riddle:
    %(prog)s --category geography --difficulty medium
  
  Generate multiple riddles:
    %(prog)s --batch 5 --category math
  
  Use custom configuration:
    %(prog)s --config custom_config.json --category physics
        """
    )

    # Required arguments
    parser.add_argument(
        "--category",
        choices=["geography", "math", "physics", "history", "logic", "wordplay"],
        required=True,
        help="Riddle category"
    )

    # Optional arguments
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Riddle difficulty level (default: medium)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--batch",
        type=int,
        default=1,
        help="Number of riddles to generate (default: 1)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory for generated videos (default: ./output)"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching for this run"
    )
    
    parser.add_argument(
        "--update-config",
        type=json.loads,
        help="Update configuration with JSON string"
    )
    
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available riddle categories and exit"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    return parser.parse_args()

def main():
    """Main CLI entry point"""
    args = parse_args()
    
    # Handle listing categories
    if args.list_categories:
        list_categories()
        return

    # Initialize configuration
    config = init_configuration(args)
    
    # Initialize services
    riddle_generator = RiddleGeneratorService()
    description_generator = DescriptionGeneratorService()
    presentation = PresentationService()
    tts = TTSService()
    video = VideoService()

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate riddles
    for i in range(args.batch):
        try:
            # Generate riddle and description
            riddle_data = riddle_generator.generate_riddle(
                args.category,
                args.difficulty
            )
            
            description_data = description_generator.generate_description(
                riddle_data,
                args.category
            )
            
            # Generate commentary
            commentary = riddle_generator.generate_commentary(riddle_data)
            
            # Get background video
            video_path = video.get_video("world map globe")
            
            # Generate voice-overs
            audio_segments = [
                tts.generate_speech(segment["text"])
                for segment in commentary
            ]
            
            # Create final video
            output_path = args.output_dir / f"riddle_{i+1}.mp4"
            final_video = presentation.create_tiktok_video(
                video_path=video_path,
                text_segments=commentary
            )
            
            # Save description
            description_path = args.output_dir / f"riddle_{i+1}_description.txt"
            save_description(description_path, description_data)
            
            if args.verbose:
                print(f"Generated riddle {i+1}/{args.batch}")
                
        except Exception as e:
            print(f"Error generating riddle {i+1}: {str(e)}")
            if args.verbose:
                import traceback
                traceback.print_exc()

def init_configuration(args: argparse.Namespace) -> CreatorConfig:
    """Initialize configuration with CLI arguments"""
    config = CreatorConfig()
    
    # Load custom config if provided
    if args.config and args.config.exists():
        with open(args.config) as f:
            custom_config = json.load(f)
            for key, value in custom_config.items():
                config.update_setting(key, value)
    
    # Apply CLI updates
    if args.update_config:
        for key, value in args.update_config.items():
            config.update_setting(key, value)
    
    return config

def list_categories():
    """List available riddle categories with descriptions"""
    categories = {
        "geography": "Riddles about countries, landmarks, and geographical features",
        "math": "Mathematical puzzles and number-based riddles",
        "physics": "Riddles about physical phenomena and scientific concepts",
        "history": "Historical events, figures, and time-based riddles",
        "logic": "Pure logic and reasoning puzzles",
        "wordplay": "Riddles based on language and word manipulation"
    }
    
    print("\nAvailable Riddle Categories:")
    for category, description in categories.items():
        print(f"\n{category}:")
        print(f"  {description}")

def save_description(path: Path, description_data: Dict[str, str]):
    """Save video description to file"""
    with open(path, "w") as f:
        f.write("=== TikTok Video Description ===\n\n")
        f.write(description_data["description"])
        f.write("\n\nHashtags:\n")
        f.write(" ".join(description_data["hashtags"]))
        f.write("\n\nKeywords:\n")
        f.write(", ".join(description_data["keywords"]))

if __name__ == "__main__":
    main()
```

### Example CLI Usage:
```bash
# Generate a single geography riddle
python main.py --category geography --difficulty medium

# Generate 5 math riddles with custom config
python main.py --category math --batch 5 --config custom_config.json

# List available categories
python main.py --list-categories

# Update configuration via CLI
python main.py --category physics --update-config '{"creator": {"branding": {"creator_name": "RiddleMaster"}}}'

# Generate riddle with verbose output
python main.py --category logic --verbose

# Generate riddle without using cache
python main.py --category wordplay --no-cache
```

The CLI provides:
1. Easy command-line access to all features
2. Configuration management
3. Batch processing
4. Custom output directory
5. Cache control
6. Verbose logging
7. Category listing
8. Error handling

The description generator ensures:
1. Engaging TikTok descriptions
2. Relevant hashtags
3. Category-specific keywords
4. Engagement prompts
5. Platform-optimized format

## OpenAI Integration Best Practices

1. **Riddle Generation**
   - Use specific system prompts for each category
   - Maintain consistent difficulty levels
   - Ensure riddles are solvable within time limit
   - Include educational content and fun facts

2. **Commentary Style**
   - Match TikTok's engaging style
   - Keep segments concise and dynamic
   - Include hooks and calls-to-action
   - Maintain educational value

3. **Category-Specific Guidelines**
   - Geography: Focus on interesting locations and cultural facts
   - Math: Make complex concepts accessible and fun
   - Physics: Relate to everyday phenomena
   - History: Connect past events to present day
   - Logic: Encourage critical thinking
   - Wordplay: Keep it clever but solvable

4. **Educational Value**
   - Include relevant facts
   - Explain concepts clearly
   - Connect to real-world applications
   - Encourage further learning

## Error Handling

### 1. Custom Exceptions (config/exceptions.py)
```python
class RiddlerException(Exception):
    """Base exception for Riddler application"""
    pass

class ConfigurationError(RiddlerException):
    """Raised when configuration is invalid"""
    pass

class CacheError(RiddlerException):
    """Raised when cache operations fail"""
    pass

class VideoError(RiddlerException):
    """Raised when video operations fail"""
    pass

class TTSError(RiddlerException):
    """Raised when TTS operations fail"""
    pass
```

## Cache Management (utils/cache.py)

```python
from pathlib import Path
from typing import Optional
import shutil

class CacheManager:
    def __init__(self, cache_dir: str, max_size: int):
        self.cache_dir = Path(cache_dir)
        self.max_size = max_size
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Path]:
        """Get item from cache"""
        path = self.cache_dir / f"{key}"
        return path if path.exists() else None

    def put(self, key: str, file_path: Path) -> Path:
        """Add item to cache"""
        if self.should_cleanup():
            self.cleanup()
        
        cache_path = self.cache_dir / f"{key}"
        shutil.copy2(file_path, cache_path)
        return cache_path

    def should_cleanup(self) -> bool:
        """Check if cache cleanup is needed"""
        current_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*'))
        return current_size > self.max_size
```

## AI Code Generator Instructions

When implementing this refactoring:

1. **Configuration Loading**
   - Always use the Config singleton for accessing settings
   - Never hardcode values that should be configurable
   - Validate configuration on startup

2. **Service Implementation**
   - Each service should be self-contained
   - Use dependency injection
   - Handle all errors gracefully
   - Implement proper cleanup

3. **Cache Management**
   - Use the CacheManager for all caching operations
   - Implement proper file handling
   - Handle disk space issues

4. **Error Handling**
   - Use custom exceptions for different error types
   - Provide meaningful error messages
   - Log errors appropriately

5. **Type Hints**
   - Use proper type hints for all functions
   - Define custom types in core/types.py
   - Use Optional[] for nullable values

## Migration Process

1. **Setup**
   ```bash
   mkdir -p config core services utils tests cache/voice cache/video assets/audio assets/video
   ```

2. **Configuration**
   - Create config.json with all settings
   - Move environment variables to .env
   - Implement Config class

3. **Services**
   - Implement each service one at a time
   - Write tests for each service
   - Verify functionality

4. **Testing**
   - Create test fixtures
   - Write unit tests
   - Test error conditions

Remember to maintain all current functionality:
- TTS caching with hash-based filenames
- Pexels video integration with UHD support
- Audio playback system
- Configuration flexibility
- Error handling and recovery
xw
This structure ensures maintainability while preserving all existing features.

## TikTok Riddle Best Practices

1. **Hook Creation (First 3 Seconds)**
   - Use attention-grabbing phrases
   - Include difficulty indicator (🧠)
   - Use dynamic text animations

2. **Question Presentation**
   - Clear, readable text
   - Word-by-word animation
   - Highlight key terms
   - Synchronize with voice-over

3. **Engagement Optimization**
   - Add pause prompt for thinking
   - Include comment prompt
   - Use countdown timer
   - Add difficulty indicator

4. **Answer Reveal**
   - Build suspense
   - Use dramatic effects
   - Add celebration animation
   - Clear explanation

5. **Audio Strategy**
   - Clear voice-over (Adam's voice)
   - Background music (10% volume)
   - Sound effects for emphasis
   - Proper audio mixing

6. **Visual Elements**
   - Portrait orientation (9:16)
   - High-quality background
   - Smart text positioning
   - Dynamic transitions

7. **Timing and Pacing**
   - Hook: 3 seconds
   - Question: 15 seconds
   - Thinking time: 5 seconds
   - Answer reveal: 4 seconds

8. **Call-to-Action**
   - Comment prompt
   - Follow suggestion
   - Like reminder
   - Share encouragement
