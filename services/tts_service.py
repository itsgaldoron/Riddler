"""Text-to-Speech service using ElevenLabs"""

import os
import requests
from pathlib import Path
from typing import Optional
from utils.decorators import retry
from utils.cache import CacheManager
from utils.logger import log, StructuredLogger
from config.exceptions import TTSError

class TTSService:
    """Service for generating speech using ElevenLabs"""
    
    def __init__(
        self,
        api_key: str,
        voice_id: str,
        model: str,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        cache_dir: str = "cache/voice",
        logger: Optional[StructuredLogger] = None
    ):
        """Initialize TTS service
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use
            model: Model to use
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)
            cache_dir: Cache directory for audio files
            logger: Logger instance
        """
        self.base_url = "https://api.elevenlabs.io/v1"
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.logger = logger or log
        
        # Initialize cache
        self.cache = CacheManager(cache_dir)
        
        # Verify API key
        self._verify_api_key()
        
    def _verify_api_key(self) -> None:
        """Verify the API key by making a test request."""
        try:
            # Try to get user info
            url = f"{self.base_url}/user"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(
                    f"Failed to verify API key: {response.status_code} - {response.text}"
                )
                self.logger.error(f"API Key being used: {self.api_key}")
                raise TTSError(
                    f"Invalid API key. Please check your ElevenLabs API key. "
                    f"Response: {response.text}"
                )
                
            self.logger.info("Successfully verified ElevenLabs API key")
            
        except Exception as e:
            self.logger.error(f"Error verifying API key: {str(e)}")
            raise TTSError(f"Failed to verify API key: {str(e)}")
    
    @retry(retries=3, delay=1.0, backoff=2.0)
    def generate_speech(self, text: str) -> str:
        """Generate speech from text
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Path to generated audio file
            
        Raises:
            TTSError: If generation fails
        """
        try:
            # Generate cache key
            cache_key = f"{hash(text)}_{self.voice_id}_{self.model}"
            
            # Check cache
            cached_path = self.cache.get(cache_key)
            if cached_path:
                self.logger.info(f"Using cached audio: {cached_path}")
                return str(cached_path)
            
            # Generate audio using the API
            self.logger.info("Generating speech with ElevenLabs")
            
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": self.model,
                "voice_settings": {
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                raise TTSError(
                    f"ElevenLabs API error: {response.status_code} - "
                    f"{response.text}"
                )
            
            # Save audio file
            output_path = Path(self.cache.base_dir) / f"{cache_key}.mp3"
            output_path.write_bytes(response.content)
            
            # Add to cache
            self.cache.put(cache_key, str(output_path))
            
            self.logger.info(f"Generated audio: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error generating speech: {str(e)}")
            raise TTSError(f"Failed to generate speech: {str(e)}") 