"""Core Riddler implementation"""

from typing import Dict, List, Optional
from utils.logger import log, StructuredLogger
from utils.helpers import ensure_directory, get_api_key
from services.openai_service import OpenAIService
from services.tts_service import TTSService
from services.video_service import VideoService
from utils.video_effects_engine import VideoEffectsEngine
from config.config import Config
from config.exceptions import RiddlerException

class Riddler:
    """Main class for generating riddle videos"""
    
    def __init__(
        self,
        output_dir: str = "output",
        max_workers: int = 4,
        logger: Optional[StructuredLogger] = None
    ):
        """Initialize Riddler
        
        Args:
            output_dir: Output directory for videos
            max_workers: Maximum number of parallel workers
            logger: Logger instance
        """
        self.config = Config()
        self.logger = logger or log
        self.output_dir = output_dir
        self.max_workers = max_workers
        
        # Ensure output directory exists
        ensure_directory(output_dir)
        
        # Initialize services
        self.openai = OpenAIService(
            config=self.config,
            api_key=get_api_key("openai")
        )
        
        self.tts = TTSService(
            api_key=get_api_key("elevenlabs"),
            voice_id=self.config.get("tts.voice_id"),
            model=self.config.get("tts.model"),
            stability=self.config.get("tts.stability"),
            similarity_boost=self.config.get("tts.similarity_boost"),
            logger=self.logger
        )
        
        self.video = VideoService(
            min_duration=self.config.get("video.min_duration", 30),
            max_duration=self.config.get("video.max_duration", 60),
            min_width=self.config.get("video.min_width", 1080),
            min_height=self.config.get("video.min_height", 1920),
            orientation=self.config.get("video.orientation", "portrait"),
            cache_dir=self.config.get("video.cache_dir", "cache/video"),
            logger=self.logger
        )
        
        # Initialize effects engine
        self.effects_engine = VideoEffectsEngine(
            output_dir=output_dir,
            width=self.config.get("video.resolution.width"),
            height=self.config.get("video.resolution.height"),
            fps=self.config.get("video.fps"),
            logger=self.logger
        )
    
    def generate_riddle(
        self,
        category: str,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True
    ) -> Dict[str, str]:
        """Generate a riddle
        
        Args:
            category: Riddle category
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            
        Returns:
            Dictionary with riddle and answer
            
        Raises:
            RiddlerException: If generation fails
        """
        try:
            # Generate riddle using OpenAI
            riddle_data = self.openai.generate_riddle(
                category=category,
                difficulty=difficulty,
                style=style,
                target_age=target_age,
                educational=educational
            )
            
            # Validate the riddle data
            if not isinstance(riddle_data, dict):
                raise RiddlerException("Invalid riddle data format")
            
            if "riddle" not in riddle_data or "answer" not in riddle_data:
                raise RiddlerException("Missing required fields in riddle data")
            
            if not isinstance(riddle_data["riddle"], str) or not isinstance(riddle_data["answer"], str):
                raise RiddlerException("Invalid field types in riddle data")
            
            # Clean up the data
            riddle_data["riddle"] = riddle_data["riddle"].strip()
            riddle_data["answer"] = riddle_data["answer"].strip()
            
            # Extract only the required fields
            return {
                "riddle": riddle_data["riddle"],
                "answer": riddle_data["answer"]
            }
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate riddle: {str(e)}")
    
    def create_multi_riddle_video(
        self,
        riddles: List[Dict],
        category: str,
        output_path: str
    ) -> str:
        """Create a multi-riddle video
        
        Args:
            riddles: List of riddle data dictionaries
            category: Riddle category
            output_path: Output path
            
        Returns:
            Path to created video
        """
        try:
            # Create riddle segments with proper ordering
            riddle_segments = []
            for i, riddle in enumerate(riddles):
                # Generate speech for riddle and answer
                riddle_audio = self.tts.generate_speech(riddle["riddle"])
                answer_audio = self.tts.generate_speech(f"The answer is: {riddle['answer']}")
                
                # Create segment with index for ordering
                segment = {
                    'index': i,
                    'riddle': riddle["riddle"],
                    'answer': riddle["answer"],
                    'riddle_audio': riddle_audio,
                    'answer_audio': answer_audio
                }
                riddle_segments.append(segment)
            
            # Sort segments by index to maintain order
            riddle_segments.sort(key=lambda x: x['index'])
            
            # Create final video
            success = self.effects_engine.createMultiRiddleVideo(
                riddle_segments=riddle_segments,
                output_path=output_path,
                tts_engine=self.tts,
                video_service=self.video,
                category=category
            )
            
            if not success:
                raise RiddlerException("Failed to create multi-riddle video")
            
            self.logger.info(f"Successfully created multi-riddle video: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating multi-riddle video: {str(e)}")
            raise RiddlerException(f"Failed to create multi-riddle video: {str(e)}") 