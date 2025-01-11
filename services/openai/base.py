"""OpenAI service base interface."""

from abc import ABC, abstractmethod
from typing import Dict, Optional

class OpenAIServiceBase(ABC):
    """Base class for OpenAI service implementations."""
    
    @abstractmethod
    def generate_riddle(
        self,
        category: str,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True
    ) -> Dict[str, str]:
        """Generate a riddle using OpenAI.
        
        Args:
            category: Riddle category
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            
        Returns:
            Dictionary containing riddle and answer
        """
        pass

    @abstractmethod
    def validate_response(self, response: Dict) -> bool:
        """Validate OpenAI response format.
        
        Args:
            response: Response from OpenAI
            
        Returns:
            True if valid, False otherwise
        """
        pass 