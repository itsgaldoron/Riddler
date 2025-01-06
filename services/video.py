"""Video processing service with MoviePy and Pillow."""

import os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.video.io.bindings import mplfig_to_npimage
from utils.logger import log
from utils.helpers import ensure_directory
from config.exceptions import VideoProcessingError

class VideoService:
    """Service for video processing using MoviePy."""
    
    def __init__(
        self,
        output_dir: str = "output",
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        font: str = "Arial",
        font_size: int = 70
    ):
        """Initialize video service."""
        self.output_dir = ensure_directory(output_dir)
        self.width = width
        self.height = height
        self.fps = fps
        self.font = font
        self.font_size = font_size

    def create_text_clip(self, text: str, duration: int, start: int = 0) -> TextClip:
        """Create a video clip from text."""
        try:
            # Create text clip with minimal settings
            clip = TextClip(
                text,
                fontsize=self.font_size,
                color='white',
                size=(self.width, self.height),
                method='label',
                align='center'
            )
            
            # Set duration and start time
            clip = clip.set_duration(duration)
            if start > 0:
                clip = clip.set_start(start)
                
            return clip
            
        except Exception as e:
            raise VideoProcessingError(f"Failed to create text clip: {str(e)}")

    def generate_riddle_video(
        self,
        riddle_text: str,
        answer_text: str,
        output_name: Optional[str] = None,
        **kwargs
    ) -> Path:
        """Generate a riddle video."""
        clips = []
        try:
            # Create background
            background = ColorClip(
                size=(self.width, self.height),
                color=(0, 0, 0),
                duration=10
            )
            clips.append(background)
            
            # Create text clips
            riddle_clip = self.create_text_clip(riddle_text, duration=5)
            answer_clip = self.create_text_clip(answer_text, duration=3, start=6)
            clips.extend([riddle_clip, answer_clip])
            
            # Combine clips
            final_clip = CompositeVideoClip(
                clips,
                size=(self.width, self.height)
            )
            
            # Generate output path
            if not output_name:
                output_name = f"riddle_{os.urandom(4).hex()}"
            output_path = Path(self.output_dir) / f"{output_name}.mp4"
            
            # Write video with minimal settings
            final_clip.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio=False,
                preset='ultrafast',
                threads=2,
                verbose=False,
                logger=None
            )
            
            return output_path
            
        except Exception as e:
            raise VideoProcessingError(f"Failed to generate video: {str(e)}")
        finally:
            # Clean up all clips
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass 