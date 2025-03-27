"""Text-to-Speech service base interface."""

from abc import ABC, abstractmethod
from typing import Optional

class TTSServiceBase(ABC):
    """Base class for Text-to-Speech service implementations."""
    
    @abstractmethod
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
        pass

    @abstractmethod
    def validate_audio(self, audio_path: str) -> bool:
        """Validate generated audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if valid, False otherwise
        """
        pass 