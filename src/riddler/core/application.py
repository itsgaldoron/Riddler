import logging
import uuid
import random
from typing import Dict, List, Optional, Tuple
from riddler.config.config import Configuration
from riddler.core.service_factory import ServiceFactory
from riddler.config.exceptions import RiddlerException
from riddler.utils.logger import log

class Application:
    """Main application class."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        logger: logging.Logger = None
    ):
        # Set up logging
        self.logger = logger or log
        
        # Initialize configuration
        self.config = Configuration(config_path, self.logger)
        
        # Initialize service factory
        self.service_factory = ServiceFactory(self.config.config, self.logger)

    def generate_riddle(
        self,
        category: str,
        num_riddles: int = 1,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True,
        no_cache: bool = False
    ) -> List[Dict[str, str]]:
        """Generate multiple riddles using OpenAI."""
        try:
            openai_service = self.service_factory.get_openai_service()
            return openai_service.generate_riddle(
                category=category,
                num_riddles=num_riddles,
                difficulty=difficulty,
                style=style,
                target_age=target_age,
                educational=educational,
                no_cache=no_cache
            )
        except Exception as e:
            self.logger.error(f"Failed to generate riddles: {str(e)}")
            raise RiddlerException(f"Failed to generate riddles: {str(e)}")

    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None
    ) -> Tuple[str, Dict]:
        """Generate speech from text using TTS service."""
        try:
            tts_service = self.service_factory.get_tts_service()
            return tts_service.generate_speech_with_timestamps(
                text=text,
                voice_id=voice_id,
                stability=stability,
                similarity_boost=similarity_boost
            )
        except Exception as e:
            self.logger.error(f"Failed to generate speech: {str(e)}")
            raise RiddlerException(f"Failed to generate speech: {str(e)}")

    def _get_difficulty_emoji(self, difficulty: Optional[str] = None) -> str:
        """Get emoji string based on difficulty level."""
        if not difficulty:
            return ""
        
        emoji_map = {
            "easy": "🧠",
            "medium": "🧠🧠",
            "hard": "🧠🧠🧠"
        }
        return emoji_map.get(difficulty, "")
    
    def _create_video_segments(self, riddles: List[Dict[str, str]], difficulty: str) -> List[Dict]:
        """Transform riddles into video segments with proper timing and structure.
        
        Args:
            riddles: List of riddle dictionaries containing 'riddle' and 'answer' keys
            
        Returns:
            List of segment dictionaries with all necessary metadata
        """
        segments = []
        
        # Process each riddle
        for i, riddle in enumerate(riddles):
            # Add hook segment for first riddle
            if i == 0:
                hook_text = self._get_random_pattern("hook_patterns", "Can you solve this riddle?")
                hook_speech, hook_timestamps = self.generate_speech(hook_text)
                segments.append({
                    "id": f"hook_{uuid.uuid4().hex[:8]}",
                    "type": "hook",
                    "text": hook_text,
                    "voice_path": hook_speech,
                    "timestamps": hook_timestamps,
                    "index": len(segments),
                    "emoji": self._get_difficulty_emoji(difficulty)
                })
            
            # Add riddle question segment
            question_speech, question_timestamps = self.generate_speech(riddle["riddle"])
            segments.append({
                "id": f"question_{uuid.uuid4().hex[:8]}",
                "type": "question",
                "text": riddle["riddle"],
                "voice_path": question_speech,
                "timestamps": question_timestamps,
                "index": len(segments)
            })
            
            # Add thinking segment
            think_text = self._get_random_pattern("thinking_patterns", "Time to think...")
            segments.append({
                "id": f"thinking_{uuid.uuid4().hex[:8]}",
                "type": "thinking",
                "text": think_text,
                "index": len(segments)
            })
            
            # Add answer segment
            answer_speech, answer_timestamps = self.generate_speech(riddle["answer"])
            segments.append({
                "id": f"answer_{uuid.uuid4().hex[:8]}",
                "type": "answer",
                "text": riddle["answer"],
                "voice_path": answer_speech,
                "timestamps": answer_timestamps,
                "index": len(segments)
            })
            
            # Add transition for all but last riddle
            if i < len(riddles) - 1:
                next_text = self._get_random_pattern("next_riddle_patterns", "Next riddle...")
                next_speech, next_timestamps = self.generate_speech(next_text)
                segments.append({
                    "id": f"transition_{uuid.uuid4().hex[:8]}",
                    "type": "transition",
                    "text": next_text,
                    "voice_path": next_speech,
                    "timestamps": next_timestamps,
                    "index": len(segments)
                })
        
        # Add call to action at the end
        cta_text = self._get_random_pattern("call_to_action_patterns", "Follow for more riddles!")
        cta_speech, cta_timestamps = self.generate_speech(cta_text)
        segments.append({
            "id": f"cta_{uuid.uuid4().hex[:8]}",
            "type": "cta",
            "text": cta_text,
            "voice_path": cta_speech,
            "timestamps": cta_timestamps,
            "index": len(segments)
        })
        
        return segments
    
    def _get_random_pattern(self, pattern_key: str, default: str) -> str:
        """Get a random pattern from config with fallback to default.
        
        Args:
            pattern_key: The key for the pattern list in config
            default: Default pattern if none found in config
            
        Returns:
            A randomly selected pattern string
        """
        patterns = self.config.config.get("riddle", {}).get("format", {}).get(pattern_key, [])
        return random.choice(patterns) if patterns else default

    def create_riddle_video(
        self,
        riddles: List[Dict[str, str]],
        output_path: str,
        category: str,
        difficulty: str
    ) -> bool:
        """Create a riddle video from the provided riddles.
        
        Args:
            riddles: List of riddle dictionaries
            output_path: Path where the video should be saved
            category: Category of riddles for video background selection
            
        Returns:
            True if video creation was successful, False otherwise
        """
        try:
            # Transform riddles into video segments
            segments = self._create_video_segments(riddles, difficulty)
            
            # Get the video composition service
            video_service = self.service_factory.get_video_composition_service()
            
            # Create the video
            success = video_service.create_multi_riddle_video(
                riddle_segments=segments,
                output_path=output_path,
                category=category
            )
            
            if success:
                self.logger.info(f"Successfully created video at {output_path}")
            else:
                self.logger.error("Failed to create video")
            
            return success
            
        except RiddlerException as e:
            self.logger.error(f"Failed to create riddle video: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating riddle video: {str(e)}")
            raise RiddlerException(f"Unexpected error: {str(e)}")
        finally:
            # Clean up services
            self.service_factory.cleanup()