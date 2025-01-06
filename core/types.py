"""Type definitions for the Riddler application"""

from typing import Dict, List, Literal, TypedDict, Union
from pathlib import Path
from pydantic import BaseModel

# Category types
Category = Literal["geography", "math", "physics", "history", "logic", "wordplay"]
Difficulty = Literal["easy", "medium", "hard"]

# Riddle types
class RiddleData(TypedDict):
    riddle: str
    answer: str
    explanation: str
    fun_fact: str
    category: Category
    difficulty: Difficulty

# Structured output types
class Step(BaseModel):
    explanation: str
    output: str

class RiddleReasoning(BaseModel):
    riddle: str
    answer: str
    explanation: str

# Video types
class VideoMetadata(TypedDict):
    width: int
    height: int
    fps: int
    duration: float
    url: str

class VideoFile(TypedDict):
    path: Path
    metadata: VideoMetadata

# Audio types
class AudioSegment(TypedDict):
    text: str
    start_time: float
    duration: float
    path: Path

# Configuration types
class TTSConfig(TypedDict):
    provider: str
    voice_id: str
    model: str
    stability: float
    similarity_boost: float

class VideoConfig(TypedDict):
    width: int
    height: int
    fps: int
    orientation: str
    min_duration: int
    max_duration: int

class CacheConfig(TypedDict):
    voice_dir: str
    video_dir: str
    max_size: int
    cleanup_threshold: float 