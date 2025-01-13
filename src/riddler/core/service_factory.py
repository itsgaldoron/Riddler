import logging
from typing import Dict, Optional
from riddler.utils.helpers import get_api_key
from riddler.utils.logger import log

from riddler.services.external.pexels_service import PexelsService
from riddler.services.video.composition_service import VideoCompositionService
from riddler.services.video.effects_service import VideoEffectsService
from riddler.services.video.text_overlay_service import TextOverlayService
from riddler.services.video.segment_service import SegmentService
from riddler.services.audio.composition_service import AudioCompositionService
from riddler.services.timing.segment_timing_service import SegmentTimingService
from riddler.services.openai.service import OpenAIService
from riddler.services.tts.service import TTSService

class ServiceFactory:
    """Factory class for creating and managing service instances."""
    
    def __init__(self, config: Dict, logger=None):
        self.config = config
        self.logger = logger or log
        self._services = {}

    def get_openai_service(self) -> OpenAIService:
        """Get or create OpenAIService instance."""
        return self._get_or_create_service(
            "openai",
            lambda: OpenAIService(
                config=self.config,
                api_key=get_api_key("openai"),
                logger=self.logger
            )
        )

    def get_tts_service(self) -> TTSService:
        """Get or create TTSService instance."""
        # Update config with TTS-specific settings
        tts_config = self.config.setdefault("tts", {})
        tts_config.update({
            "api_key": get_api_key("elevenlabs"),
            "voice_id": tts_config.get("voice_id", "pqHfZKP75CvOlQylNhV4"),
            "model": tts_config.get("model", "eleven_monolingual_v1"),
            "stability": float(tts_config.get("stability", 0.5)),
            "similarity_boost": float(tts_config.get("similarity_boost", 0.75)),
            "cache_dir": tts_config.get("cache_dir", "cache/voice")
        })
        
        return self._get_or_create_service(
            "tts",
            lambda: TTSService(
                config=self.config,
                logger=self.logger
            )
        )

    def get_pexels_service(self) -> PexelsService:
        """Get or create PexelsService instance."""
        video_config = self.config.get("video", {})
        pexels_config = video_config.get("pexels", {})
        return self._get_or_create_service(
            "pexels",
            lambda: PexelsService(
                config=self.config,
                min_duration=pexels_config.get("min_duration", 1),
                max_duration=pexels_config.get("max_duration", 3),
                min_width=video_config.get("min_width", 1080),
                min_height=video_config.get("min_height", 1920),
                orientation=video_config.get("orientation", "portrait"),
                cache_dir=video_config.get("cache_dir", "cache/video"),
                logger=self.logger
            )
        )

    def get_video_effects_service(self) -> VideoEffectsService:
        """Get or create VideoEffectsService instance."""
        return self._get_or_create_service(
            "video_effects",
            lambda: VideoEffectsService(
                config=self.config,
                logger=self.logger
            )
        )

    def get_text_overlay_service(self) -> TextOverlayService:
        """Get or create TextOverlayService instance."""
        return self._get_or_create_service(
            "text_overlay",
            lambda: TextOverlayService(
                config=self.config.get("video", {}),
                logger=self.logger
            )
        )

    def get_segment_service(self) -> SegmentService:
        """Get or create SegmentService instance."""
        return self._get_or_create_service(
            "segment",
            lambda: SegmentService(
                video_effects=self.get_video_effects_service(),
                text_overlay=self.get_text_overlay_service(),
                config=self.config,
                logger=self.logger
            )
        )

    def get_audio_composition_service(self) -> AudioCompositionService:
        """Get or create AudioCompositionService instance."""
        return self._get_or_create_service(
            "audio_composition",
            lambda: AudioCompositionService(
                config=self.config,
                logger=self.logger
            )
        )

    def get_segment_timing_service(self) -> SegmentTimingService:
        """Get or create SegmentTimingService instance."""
        return self._get_or_create_service(
            "segment_timing",
            lambda: SegmentTimingService(
                config=self.config,
                logger=self.logger
            )
        )

    def get_video_composition_service(self) -> VideoCompositionService:
        """Get or create VideoCompositionService instance."""
        return self._get_or_create_service(
            "video_composition",
            lambda: VideoCompositionService(
                pexels_service=self.get_pexels_service(),
                text_overlay=self.get_text_overlay_service(),
                video_effects=self.get_video_effects_service(),
                audio_composition=self.get_audio_composition_service(),
                segment_timing=self.get_segment_timing_service(),
                segment_service=self.get_segment_service(),
                config=self.config,
                logger=self.logger
            )
        )

    def _get_or_create_service(self, service_name: str, factory_func):
        """Get an existing service instance or create a new one."""
        if service_name not in self._services:
            self._services[service_name] = factory_func()
        return self._services[service_name]

    def cleanup(self):
        """Clean up all service instances."""
        for service in self._services.values():
            if hasattr(service, 'cleanup'):
                try:
                    service.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up service: {str(e)}")
        self._services.clear() 