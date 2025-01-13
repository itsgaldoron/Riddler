from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip

class VideoCompositionServiceBase(ABC):
    @abstractmethod
    def create_multi_riddle_video(
        self,
        riddle_segments: List[Dict],
        output_path: str,
        category: str
    ) -> bool:
        pass

class VideoEffectsServiceBase(ABC):
    @abstractmethod
    def apply_effect(self, clip: VideoFileClip, effect_type: str) -> VideoFileClip:
        pass

    @abstractmethod
    def standardize_video(self, clip: VideoFileClip, target_duration: float) -> VideoFileClip:
        pass

class TextOverlayServiceBase(ABC):
    @abstractmethod
    def create_text_overlay(
        self, 
        clip: VideoFileClip, 
        text: str, 
        emoji: Optional[str] = None,
        timestamps: Optional[Dict] = None
    ) -> VideoFileClip:
        pass

    @abstractmethod
    def calculate_text_layout(self, text: str, max_width: int) -> List[str]:
        pass

class SegmentServiceBase(ABC):
    @abstractmethod
    def process_segment(self, segment: Dict, timing: Dict[str, float]) -> VideoFileClip:
        pass 