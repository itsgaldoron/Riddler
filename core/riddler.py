"""Core Riddler implementation"""

import os
import random
from typing import Dict, List, Optional, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import log, StructuredLogger
from utils.helpers import ensure_directory, get_api_key
from services.openai_service import OpenAIService
from services.tts_service import TTSService
from services.video_service import VideoService
from utils.video_processor import VideoProcessor
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
            api_key=get_api_key("openai"),
            model=self.config.get("openai.model", "gpt-4"),
            temperature=self.config.get("openai.temperature", 0.7)
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
        
        # Initialize video processor
        self.processor = VideoProcessor(
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
    
    def create_video(
        self,
        riddle_data: Dict[str, str],
        category: str,
        output_path: Optional[str] = None
    ) -> str:
        """Create a video for a riddle
        
        Args:
            riddle_data: Riddle data from generate_riddle
            category: Riddle category
            output_path: Optional output path
            
        Returns:
            Path to created video
            
        Raises:
            RiddlerException: If video creation fails
        """
        try:
            # Validate riddle data
            if not isinstance(riddle_data, dict):
                raise RiddlerException("Invalid riddle data format")
            
            if "riddle" not in riddle_data or "answer" not in riddle_data:
                raise RiddlerException("Missing required fields in riddle data")
            
            # Generate speech for riddle and answer
            riddle_audio = self.tts.generate_speech(riddle_data["riddle"])
            answer_audio = self.tts.generate_speech(
                f"The answer is: {riddle_data['answer']}"
            )
            
            # Get background video
            background = self.video.get_video(category)
            
            # Process video
            if not output_path:
                output_path = os.path.join(
                    self.output_dir,
                    f"riddle_{category}_{os.urandom(4).hex()}.mp4"
                )
            
            # Get video config
            effects = self.config.get("video.effects.enabled", [])
            transitions = self.config.get("video.effects.transitions", ["fade"])
            
            # Create final video
            success = self.processor.create_riddle_video(
                background_path=str(background),
                riddle_audio_path=str(riddle_audio),
                answer_audio_path=str(answer_audio),
                riddle_text=str(riddle_data["riddle"]),
                answer_text=str(riddle_data["answer"]),
                output_path=str(output_path),
                effects=effects,
                transitions=transitions
            )
            
            if not success:
                raise RiddlerException("Failed to create video")
            
            self.logger.info(f"Created video: {output_path}")
            return str(output_path)
            
        except Exception as e:
            raise RiddlerException(f"Failed to create video: {str(e)}")
    
    def batch_create_videos(
        self,
        categories: List[str],
        difficulty: str,
        count: int = 1
    ) -> List[str]:
        """Create multiple videos in parallel
        
        Args:
            categories: List of categories to use
            difficulty: Difficulty level
            count: Number of videos per category
            
        Returns:
            List of created video paths
        """
        video_paths = []
        
        def create_video_for_category(category: str) -> List[str]:
            paths = []
            for _ in range(count):
                try:
                    riddle_data = self.generate_riddle(category, difficulty)
                    video_path = self.create_video(riddle_data, category)
                    paths.append(str(video_path))
                except Exception as e:
                    self.logger.error(f"Error creating video for {category}: {str(e)}")
            return paths
        
        # Create videos in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(create_video_for_category, category): category
                for category in categories
            }
            
            for future in as_completed(futures):
                category = futures[future]
                try:
                    paths = future.result()
                    video_paths.extend(paths)
                except Exception as e:
                    self.logger.error(f"Error processing {category}: {str(e)}")
        
        return video_paths 