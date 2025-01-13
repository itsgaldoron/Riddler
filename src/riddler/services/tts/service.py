"""Text-to-Speech service implementation."""

import logging
import os
import hashlib
import base64
from pathlib import Path
from typing import Optional, Dict, Tuple
import requests
from elevenlabs import ElevenLabs
from riddler.utils.decorators import retry
from riddler.utils.cache import CacheManager
from riddler.utils.logger import log
from riddler.config.exceptions import TTSError
from riddler.services.tts.base import TTSServiceBase

class TTSService(TTSServiceBase):
    def __init__(self, config: Dict = None, logger=None):
        self.config = config or {}
        self.logger = logger or log
        self.api_key = self.config.get("tts", {}).get("api_key")
        self.base_url = self.config.get("tts", {}).get("base_url", "https://api.elevenlabs.io/v1")
        self.model = self.config.get("tts", {}).get("model", "eleven_multilingual_v2")
        self.stability = self.config.get("tts", {}).get("stability", 0.5)
        self.similarity_boost = self.config.get("tts", {}).get("similarity_boost", 0.75)
        self.output_format = self.config.get("tts", {}).get("output_format", "mp3_44100_128")
        
        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)

    @retry(retries=3, delay=1.0, backoff=2.0)
    def generate_speech_with_timestamps(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None
    ) -> Tuple[str, Dict]:
        """Generate speech with timestamp data for karaoke-style highlighting.
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID to use
            stability: Optional stability value
            similarity_boost: Optional similarity boost value
            
        Returns:
            Tuple of (path to audio file, timestamp data)
        """
        try:
            # Use default voice if none provided
            voice_id = voice_id or self.config.get("tts", {}).get("voice_id")
            if not voice_id:
                raise TTSError("No voice ID provided")

            # Generate cache key
            cache_key = hashlib.md5(
                f"{text}{voice_id}{stability}{similarity_boost}".encode()
            ).hexdigest()
            
            # Get cache paths
            cache_dir = Path(self.config.get("cache", {}).get("dir", "cache"))
            audio_cache_path = cache_dir / f"{cache_key}.mp3"
            timestamps_cache_path = cache_dir / f"{cache_key}.timestamps.json"
            
            # Create cache directory if it doesn't exist
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Return cached files if they exist and are valid
            if (
                os.path.exists(audio_cache_path) 
                and os.path.exists(timestamps_cache_path)
                and self.validate_audio(str(audio_cache_path))
            ):
                self.logger.info(f"Using cached audio and timestamps")
                import json
                with open(timestamps_cache_path) as f:
                    timestamps = json.load(f)
                return str(audio_cache_path), timestamps

            # Generate audio with timestamps using ElevenLabs
            self.logger.info("Generating speech with timestamps using ElevenLabs")
            
            response = self.client.text_to_speech.convert_with_timestamps(
                voice_id=voice_id,
                text=text,
                output_format=self.output_format,
                model_id=self.model,
                voice_settings={
                    "stability": float(stability if stability is not None else self.stability),
                    "similarity_boost": float(similarity_boost if similarity_boost is not None else self.similarity_boost)
                }
            )

            # Save audio file
            audio_data = base64.b64decode(response["audio_base64"])
            with open(audio_cache_path, "wb") as f:
                f.write(audio_data)

            # Save timestamps
            timestamps = response["normalized_alignment"]
            import json
            with open(timestamps_cache_path, "w") as f:
                json.dump(timestamps, f)

            # Validate generated audio
            if not self.validate_audio(str(audio_cache_path)):
                os.remove(audio_cache_path)
                os.remove(timestamps_cache_path)
                raise TTSError("Generated audio validation failed")

            self.logger.info(f"Generated audio with timestamps: {audio_cache_path}")
            return str(audio_cache_path), timestamps

        except Exception as e:
            self.logger.error(f"Failed to generate speech with timestamps: {str(e)}")
            raise TTSError(f"Failed to generate speech with timestamps: {str(e)}")

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
        """
        try:
            # Use default voice if none provided
            voice_id = voice_id or self.config.get("tts", {}).get("voice_id")
            if not voice_id:
                raise TTSError("No voice ID provided")
            
            # Generate cache key
            cache_key = hashlib.md5(
                f"{text}{voice_id}{stability}{similarity_boost}".encode()
            ).hexdigest()
            
            # Get cache path
            cache_dir = Path(self.config.get("cache", {}).get("dir", "cache"))
            cache_path = cache_dir / f"{cache_key}.mp3"
            
            # Create cache directory if it doesn't exist
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Return cached file if it exists and is valid
            if os.path.exists(cache_path) and self.validate_audio(str(cache_path)):
                self.logger.info(f"Using cached audio: {cache_path}")
                return str(cache_path)
            
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
            if not self.validate_audio(str(cache_path)):
                os.remove(cache_path)
                raise TTSError("Generated audio validation failed")
            
            self.logger.info(f"Generated audio: {cache_path}")
            return str(cache_path)
            
        except Exception as e:
            self.logger.error(f"Failed to generate speech: {str(e)}")
            raise TTSError(f"Failed to generate speech: {str(e)}")

    def validate_audio(self, audio_path: str) -> bool:
        """Validate generated audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if file exists and is not empty
            if not os.path.exists(audio_path):
                return False
                
            if os.path.getsize(audio_path) == 0:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate audio: {str(e)}")
            return False 