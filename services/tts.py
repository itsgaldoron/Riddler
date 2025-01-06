import os
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from openai import OpenAI
from utils.logger import log
from utils.cache import cache
from utils.helpers import generate_cache_key, ensure_directory
from config.exceptions import TTSError

class TTSService:
    """Text-to-speech service using OpenAI's API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        voice: str = "alloy",
        model: str = "tts-1",
        output_format: str = "mp3",
        cache_dir: str = "cache/voice"
    ):
        """Initialize TTS service.
        
        Args:
            api_key: OpenAI API key (defaults to env var)
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model to use
            output_format: Output audio format
            cache_dir: Directory for caching audio files
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise TTSError("OpenAI API key not found")
            
        self.client = OpenAI(api_key=self.api_key)
        self.voice = voice
        self.model = model
        self.output_format = output_format
        self.cache_dir = ensure_directory(cache_dir)
        
    def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        output_format: Optional[str] = None,
        cache_key: Optional[str] = None
    ) -> Path:
        """Generate speech from text.
        
        Args:
            text: Text to convert to speech
            voice: Override default voice
            model: Override default model
            output_format: Override default format
            cache_key: Custom cache key
            
        Returns:
            Path to generated audio file
            
        Raises:
            TTSError: If speech generation fails
        """
        # Use defaults if not specified
        voice = voice or self.voice
        model = model or self.model
        output_format = output_format or self.output_format
        
        # Generate cache key if not provided
        if not cache_key:
            cache_key = generate_cache_key(
                "tts",
                text=text,
                voice=voice,
                model=model,
                format=output_format
            )
            
        # Check cache first
        cached_file = cache.get(cache_key)
        if cached_file:
            return cached_file
            
        try:
            # Generate speech using OpenAI API
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=output_format
            )
            
            # Save to file
            output_path = self.cache_dir / f"{cache_key}.{output_format}"
            
            # Stream response to file
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=1024):
                    f.write(chunk)
                    
            # Cache the file path
            cache.set(
                cache_key,
                output_path,
                metadata={
                    "text": text,
                    "voice": voice,
                    "model": model,
                    "format": output_format
                }
            )
            
            log.info(
                "Generated speech",
                extra={
                    "text_length": len(text),
                    "voice": voice,
                    "model": model,
                    "format": output_format,
                    "file_size": output_path.stat().st_size
                }
            )
            
            return output_path
            
        except Exception as e:
            raise TTSError(f"Failed to generate speech: {str(e)}")
            
    def get_available_voices(self) -> Dict[str, Any]:
        """Get information about available voices.
        
        Returns:
            Dictionary of voice information
        """
        return {
            "alloy": {
                "description": "Neutral, balanced voice",
                "gender": "neutral"
            },
            "echo": {
                "description": "Warm, natural voice",
                "gender": "male"
            },
            "fable": {
                "description": "Expressive, dynamic voice",
                "gender": "male"
            },
            "onyx": {
                "description": "Deep, authoritative voice",
                "gender": "male"
            },
            "nova": {
                "description": "Friendly, energetic voice",
                "gender": "female"
            },
            "shimmer": {
                "description": "Clear, professional voice",
                "gender": "female"
            }
        }
        
    def validate_voice(self, voice: str) -> bool:
        """Check if voice is valid.
        
        Args:
            voice: Voice to validate
            
        Returns:
            True if voice is valid
        """
        return voice in self.get_available_voices()
        
    def get_voice_description(self, voice: str) -> Optional[str]:
        """Get description of voice.
        
        Args:
            voice: Voice to get description for
            
        Returns:
            Voice description if found, None otherwise
        """
        voices = self.get_available_voices()
        if voice in voices:
            return voices[voice]["description"]
        return None
        
    def clear_cache(self) -> None:
        """Clear TTS cache directory."""
        try:
            for file_path in self.cache_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
        except Exception as e:
            log.error(f"Failed to clear TTS cache: {e}")

# Initialize global TTS service
tts_service = TTSService() 