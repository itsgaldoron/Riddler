from abc import ABC, abstractmethod
from typing import Dict, List
from moviepy.editor import CompositeAudioClip

class AudioCompositionServiceBase(ABC):
    @abstractmethod
    def create_audio_composition(
        self,
        segments: List[Dict],
        timings: Dict[str, float]
    ) -> CompositeAudioClip:
        pass

    @abstractmethod
    def mix_audio_tracks(
        self,
        tracks: List[CompositeAudioClip],
        timings: Dict[str, float]
    ) -> CompositeAudioClip:
        pass 