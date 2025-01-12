"""Text-to-Speech service implementation."""

import logging
import os
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict
from riddler.utils.decorators import retry
from riddler.utils.cache import CacheManager
from riddler.utils.logger import log
from riddler.config.exceptions import TTSError
from riddler.services.tts.base import TTSServiceBase

class TTSService(TTSServiceBase):
    """Text-to-Speech service implementation using ElevenLabs."""
    
    def __init__(
        self,
        api_key: str,
        voice_id: str,
        model: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        logger=None,
        cache_dir: str = "cache/voice",
        config: Optional[Dict] = None
    ):
        """Initialize TTS service.
        
        Args:
            api_key: ElevenLabs API key
            voice_id: Voice ID to use
            model: Model to use
            stability: Voice stability
            similarity_boost: Voice similarity boost
            logger: Optional logger instance
            cache_dir: Cache directory for audio files
            config: Optional configuration dictionary
        """
        self.base_url = "https://api.elevenlabs.io/v1"
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.stability = stability
        self.similarity_boost = similarity_boost
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize cache
        self.cache = CacheManager(cache_dir, config=config)
        
        # Verify API key
        self._verify_api_key()

    def _verify_api_key(self) -> None:
        """Verify the API key by making a test request.
        
        Raises:
            TTSError: If verification fails
        """
        try:
            url = f"{self.base_url}/user"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(
                    f"Failed to verify API key: {response.status_code} - {response.text}"
                )
                raise TTSError(
                    f"Invalid API key. Please check your ElevenLabs API key. "
                    f"Response: {response.text}"
                )
                
            self.logger.info("Successfully verified ElevenLabs API key")
            
        except Exception as e:
            self.logger.error(f"Error verifying API key: {str(e)}")
            raise TTSError(f"Failed to verify API key: {str(e)}")

    @retry(retries=3, delay=1.0, backoff=2.0)
    def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None
    ) -> str:
        """Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID to use
            stability: Optional stability value
            similarity_boost: Optional similarity boost value
            
        Returns:
            Path to generated audio file
            
        Raises:
            TTSError: If generation fails
        """
        try:
            # Use provided values or defaults
            voice_id = voice_id or self.voice_id
            stability = stability or self.stability
            similarity_boost = similarity_boost or self.similarity_boost
            
            # Generate cache key
            cache_key = self._generate_cache_key(
                text=text,
                voice_id=voice_id,
                stability=stability,
                similarity_boost=similarity_boost
            )
            
            # Create cache subdirectory
            cache_subdir = os.path.join(self.cache.cache_dir, cache_key[:2])
            os.makedirs(cache_subdir, exist_ok=True)
            
            # Full path for cached file
            cache_path = os.path.join(cache_subdir, f"{cache_key}.mp3")
            
            # Return cached file if it exists and is valid
            if os.path.exists(cache_path) and self.validate_audio(cache_path):
                self.logger.info(f"Using cached audio: {cache_path}")
                return cache_path
            
            # Generate audio using the API
            self.logger.info("Generating speech with ElevenLabs")
            
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": self.model,
                "voice_settings": {
                    "stability": float(stability if stability is not None else self.stability),
                    "similarity_boost": float(similarity_boost if similarity_boost is not None else self.similarity_boost)
                }
            }
            
            self.logger.info(f"Request data: {data}")
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                raise TTSError(
                    f"ElevenLabs API error: {response.status_code} - "
                    f"{response.text}"
                )
            
            # Save audio file
            with open(cache_path, "wb") as f:
                f.write(response.content)
            
            # Validate generated audio
            if not self.validate_audio(cache_path):
                os.remove(cache_path)
                raise TTSError("Generated audio validation failed")
            
            self.logger.info(f"Generated audio: {cache_path}")
            return cache_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate speech: {str(e)}")
            raise TTSError(f"Failed to generate speech: {str(e)}")

    def validate_audio(self, audio_path: str) -> bool:
        """Validate audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_path):
                return False
            
            # Check if file is empty
            if os.path.getsize(audio_path) == 0:
                return False
            
            # Check if file is readable
            with open(audio_path, "rb") as f:
                # Read first few bytes to check MP3 header
                header = f.read(4)
                if not header.startswith(b"\xFF\xFB") and not header.startswith(b"ID3"):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate audio: {str(e)}")
            return False

    def _generate_cache_key(
        self,
        text: str,
        voice_id: str,
        stability: float,
        similarity_boost: float
    ) -> str:
        """Generate cache key for TTS parameters.
        
        Args:
            text: Input text
            voice_id: Voice ID
            stability: Stability value
            similarity_boost: Similarity boost value
            
        Returns:
            Cache key string
        """
        if not text:
            return None
            
        # Create string with all parameters
        params = f"{text}|{voice_id}|{stability}|{similarity_boost}"
        
        # Generate SHA-256 hash
        return hashlib.sha256(params.encode()).hexdigest() 