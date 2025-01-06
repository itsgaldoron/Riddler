"""Service for generating and managing video captions."""

import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import whisper
from utils.logger import log
from utils.cache import cache
from utils.helpers import generate_cache_key
from config.exceptions import VideoProcessingError

def generate_captions(
    video: VideoFileClip,
    model_name: str = "base",
    language: str = "en",
    font: str = "Arial",
    font_size: int = 40,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 2,
    position: str = "bottom",
    margin: int = 50
) -> List[Dict[str, Any]]:
    """Generate captions for a video using Whisper.
    
    Args:
        video: Input video clip
        model_name: Whisper model name
        language: Caption language
        font: Font name
        font_size: Font size
        color: Text color
        stroke_color: Text stroke color
        stroke_width: Text stroke width
        position: Caption position
        margin: Margin from edges
        
    Returns:
        List of caption segments with timing and text
    """
    try:
        # Generate cache key
        cache_key = generate_cache_key(
            "captions",
            video_hash=hash(video),
            model=model_name,
            language=language
        )
        
        # Check cache
        cached_captions = cache.get(cache_key)
        if cached_captions:
            return cached_captions
        
        # Extract audio
        audio = video.audio
        if audio is None:
            log.warning("Video has no audio track, skipping captions")
            return []
            
        # Save temporary audio file
        temp_audio = Path("cache/audio/temp.wav")
        os.makedirs(temp_audio.parent, exist_ok=True)
        audio.write_audiofile(str(temp_audio))
        
        # Load Whisper model
        model = whisper.load_model(model_name)
        
        # Transcribe audio
        result = model.transcribe(
            str(temp_audio),
            language=language,
            task="transcribe"
        )
        
        # Clean up temp file
        temp_audio.unlink()
        
        # Process segments
        captions = []
        for segment in result["segments"]:
            caption = {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "style": {
                    "font": font,
                    "font_size": font_size,
                    "color": color,
                    "stroke_color": stroke_color,
                    "stroke_width": stroke_width,
                    "position": position,
                    "margin": margin
                }
            }
            captions.append(caption)
        
        # Cache results
        cache.put(cache_key, captions)
        
        return captions
        
    except Exception as e:
        raise VideoProcessingError(f"Failed to generate captions: {str(e)}")

def apply_captions(
    video: VideoFileClip,
    captions: List[Dict[str, Any]]
) -> VideoFileClip:
    """Apply captions to a video.
    
    Args:
        video: Input video clip
        captions: List of caption segments
        
    Returns:
        Video with captions applied
    """
    try:
        if not captions:
            return video
            
        # Create caption clips
        caption_clips = []
        for caption in captions:
            # Create text clip
            text = caption["text"]
            style = caption["style"]
            
            clip = (
                TextClip(
                    text,
                    fontsize=style["font_size"],
                    font=style["font"],
                    color=style["color"],
                    stroke_color=style["stroke_color"],
                    stroke_width=style["stroke_width"]
                )
                .set_start(caption["start"])
                .set_end(caption["end"])
            )
            
            # Position caption
            width, height = clip.size
            if style["position"] == "bottom":
                position = ("center", video.h - height - style["margin"])
            elif style["position"] == "top":
                position = ("center", style["margin"])
            else:
                position = "center"
                
            clip = clip.set_position(position)
            
            caption_clips.append(clip)
            
        # Combine with video
        return CompositeVideoClip([video] + caption_clips)
        
    except Exception as e:
        raise VideoProcessingError(f"Failed to apply captions: {str(e)}")

def extract_captions(
    video_path: Union[str, Path],
    output_format: str = "srt",
    language: str = "en"
) -> Path:
    """Extract captions from a video to a file.
    
    Args:
        video_path: Path to video file
        output_format: Caption file format
        language: Caption language
        
    Returns:
        Path to caption file
    """
    try:
        video_path = Path(video_path)
        output_path = video_path.with_suffix(f".{output_format}")
        
        # Generate captions
        video = VideoFileClip(str(video_path))
        captions = generate_captions(video, language=language)
        
        # Write caption file
        if output_format == "srt":
            _write_srt(captions, output_path)
        else:
            raise ValueError(f"Unsupported caption format: {output_format}")
            
        return output_path
        
    except Exception as e:
        raise VideoProcessingError(f"Failed to extract captions: {str(e)}")

def _write_srt(captions: List[Dict[str, Any]], output_path: Path) -> None:
    """Write captions to SRT file.
    
    Args:
        captions: List of caption segments
        output_path: Output file path
    """
    def format_time(seconds: float) -> str:
        """Format time in SRT format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")
    
    with open(output_path, "w", encoding="utf-8") as f:
        for i, caption in enumerate(captions, 1):
            # Write segment number
            f.write(f"{i}\n")
            
            # Write timestamp
            start = format_time(caption["start"])
            end = format_time(caption["end"])
            f.write(f"{start} --> {end}\n")
            
            # Write text
            f.write(f"{caption['text']}\n\n") 