"""
Riddler - AI-Powered Riddle Generation System

This file is part of Riddler.
Copyright (c) 2025 Riddler

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0
International License. To view a copy of this license, visit:
https://creativecommons.org/licenses/by-nc/4.0/
"""

import logging
from typing import Dict, List, Optional
from config.config import Configuration
from core.service_factory import ServiceFactory
from config.exceptions import RiddlerException
from utils.logger import log

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
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True,
        no_cache: bool = False
    ) -> Dict[str, str]:
        """Generate a riddle using OpenAI."""
        try:
            openai_service = self.service_factory.get_openai_service()
            return openai_service.generate_riddle(
                category=category,
                difficulty=difficulty,
                style=style,
                target_age=target_age,
                educational=educational,
                no_cache=no_cache
            )
        except Exception as e:
            self.logger.error(f"Failed to generate riddle: {str(e)}")
            raise RiddlerException(f"Failed to generate riddle: {str(e)}")

    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None
    ) -> str:
        """Generate speech from text using TTS service."""
        try:
            tts_service = self.service_factory.get_tts_service()
            return tts_service.generate_speech(
                text=text,
                voice_id=voice_id,
                stability=stability,
                similarity_boost=similarity_boost
            )
        except Exception as e:
            self.logger.error(f"Failed to generate speech: {str(e)}")
            raise RiddlerException(f"Failed to generate speech: {str(e)}")

    def create_riddle_video(
        self,
        riddle_segments: List[Dict],
        output_path: str,
        category: str
    ) -> bool:
        """Create a riddle video from the provided segments."""
        try:
            # Get the video composition service
            video_service = self.service_factory.get_video_composition_service()
            
            # Create the video
            success = video_service.create_multi_riddle_video(
                riddle_segments=riddle_segments,
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