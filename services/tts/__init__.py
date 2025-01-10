"""Text-to-Speech service module."""

from services.tts.base import TTSServiceBase
from services.tts.service import TTSService

__all__ = [
    'TTSServiceBase',
    'TTSService'
] 