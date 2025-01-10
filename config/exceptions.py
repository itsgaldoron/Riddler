"""Custom exceptions for the Riddler application."""

class RiddlerException(Exception):
    """Base exception for Riddler application."""
    pass

class ConfigurationError(RiddlerException):
    """Raised when configuration is invalid."""
    pass

class ConfigValidationError(ConfigurationError):
    """Raised when configuration validation fails."""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        self.field = field
        self.value = value
        super().__init__(message)

class VideoProcessingError(RiddlerException):
    """Raised when video processing fails."""
    pass

class AudioProcessingError(RiddlerException):
    """Raised when audio processing fails."""
    pass

class ContentGenerationError(RiddlerException):
    """Raised when content generation fails."""
    pass

class ResourceError(RiddlerException):
    """Raised when system resources are insufficient."""
    pass

class CacheError(RiddlerException):
    """Raised when cache operations fail."""
    pass

class ValidationError(RiddlerException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)

class TikTokOptimizationError(RiddlerException):
    """Raised when TikTok optimization requirements are not met."""
    
    def __init__(self, message: str, requirement: str = None):
        self.requirement = requirement
        super().__init__(message)

class EngagementFeatureError(RiddlerException):
    """Raised when engagement feature implementation fails."""
    pass

class APIError(RiddlerException):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, service: str = None, status_code: int = None):
        self.service = service
        self.status_code = status_code
        super().__init__(message)

class OpenAIError(APIError):
    """Raised when OpenAI API calls fail."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message, service="OpenAI", status_code=status_code)

class TTSError(APIError):
    """Raised when Text-to-Speech API calls fail."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message, service="ElevenLabs", status_code=status_code)

class AssetError(RiddlerException):
    """Raised when required assets are missing or invalid."""
    
    def __init__(self, message: str, asset_path: str = None):
        self.asset_path = asset_path
        super().__init__(message)

class VideoError(RiddlerException):
    """Exception raised for video service errors"""
    pass 

class PexelsServiceError(Exception):
    """Exception raised for errors in the Pexels service."""
    pass

class VideoCompositionError(Exception):
    """Exception raised for errors in video composition."""
    pass

class AudioCompositionError(Exception):
    """Exception raised for errors in audio composition."""
    pass

class TextOverlayError(Exception):
    """Exception raised for errors in text overlay processing."""
    pass

class TimingServiceError(Exception):
    """Exception raised for errors in timing calculations."""
    pass

class VideoEffectsError(Exception):
    """Exception raised for errors in video effects processing."""
    pass

class SegmentServiceError(Exception):
    """Exception raised for errors in segment processing."""
    pass 