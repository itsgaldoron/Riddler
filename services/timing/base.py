from abc import ABC, abstractmethod
from typing import Dict, List

class SegmentTimingServiceBase(ABC):
    @abstractmethod
    def calculate_segment_timings(
        self,
        segments: List[Dict],
        config: Dict
    ) -> List[Dict[str, float]]:
        pass

    @abstractmethod
    def validate_timings(
        self,
        timings: List[Dict[str, float]],
        config: Dict
    ) -> bool:
        pass 