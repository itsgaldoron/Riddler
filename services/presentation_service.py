"""Text-to-Speech service using ElevenLabs"""

import json
import os
import random
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip

from utils.cache import CacheManager
from utils.logger import Logger
from utils.video_processor import VideoProcessor
from config.exceptions import PresentationError

class PresentationService:
    """Service for creating TikTok-optimized videos with effects and animations"""
    
    def __init__(self):
        """Initialize presentation service"""
        self.config = Config()
        self.text_config = self.config.get("presentation.text_overlay")
        self.timing_config = self.config.get("presentation.timing")
        self.engagement_config = self.config.get("presentation.engagement")
        self.tiktok_config = self.config.get("video.tiktok_optimization")
        self.video_processor = VideoProcessor()
        self.logger = Logger()
        
        # Load sound effects
        self.sound_effects = {
            "hook": AudioFileClip("assets/audio/hook.mp3"),
            "reveal": AudioFileClip("assets/audio/reveal.mp3"),
            "countdown": AudioFileClip("assets/audio/countdown.mp3"),
            "celebration": AudioFileClip("assets/audio/celebration.mp3")
        }
        
        # Load background music
        self.background_music = AudioFileClip("assets/audio/background.mp3")
        
    def create_tiktok_video(
        self,
        video_path: Path,
        text_segments: List[Dict],
        difficulty: str = "medium"
    ) -> Path:
        """Create TikTok-optimized video with all effects and features
        
        Args:
            video_path: Path to background video
            text_segments: List of {text, start_time, duration} dicts
            difficulty: Riddle difficulty level
            
        Returns:
            Path to rendered video
        """
        try:
            # Load background video
            background = VideoFileClip(str(video_path))
            
            # Create segments
            segments = []
            current_time = 0
            
            # Hook section (first 3 seconds)
            hook = self._create_hook_section(
                background.subclip(0, self.tiktok_config["hook_duration"]),
                text_segments[0],
                difficulty
            )
            segments.append(hook)
            current_time += hook.duration
            
            # Main content
            for segment in text_segments[1:]:
                clip = self._create_content_segment(
                    background.subclip(current_time, current_time + segment["duration"]),
                    segment
                )
                segments.append(clip)
                current_time += clip.duration
            
            # Call to action
            cta = self._create_call_to_action(
                background.subclip(
                    current_time,
                    current_time + self.tiktok_config["end_screen_duration"]
                )
            )
            segments.append(cta)
            
            # Combine segments
            final_video = CompositeVideoClip(segments)
            
            # Add background music
            background_audio = self.background_music.set_duration(final_video.duration)
            background_audio = background_audio.volumex(
                self.tiktok_config["sound_effects"]["background_music_volume"]
            )
            
            final_video = final_video.set_audio(
                CompositeAudioClip([
                    clip.audio for clip in segments if clip.audio is not None
                ] + [background_audio])
            )
            
            # Optimize for TikTok
            output_path = Path("temp_final.mp4")
            final_video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=self.tiktok_config["fps"]
            )
            
            optimized_path = Path("final.mp4")
            self.video_processor.optimize_for_tiktok(
                str(output_path),
                str(optimized_path)
            )
            
            return optimized_path
            
        except Exception as e:
            self.logger.error(f"Error creating TikTok video: {str(e)}")
            raise PresentationError(f"Failed to create TikTok video: {str(e)}")
            
    def _create_hook_section(
        self,
        video: VideoFileClip,
        segment: Dict,
        difficulty: str
    ) -> CompositeVideoClip:
        """Create attention-grabbing hook section
        
        Args:
            video: Background video clip
            segment: Text segment data
            difficulty: Riddle difficulty
            
        Returns:
            Hook section clip
        """
        hook_config = self.engagement_config["hook_text"]
        
        # Add difficulty indicator
        difficulty_text = "🧠" * (
            1 if difficulty == "easy"
            else 2 if difficulty == "medium"
            else 3
        )
        
        # Create text clips with animations
        hook_text = self._create_animated_text(
            segment["text"],
            duration=video.duration,
            position=hook_config["position"],
            animation="scale_up",
            word_by_word=True
        )
        
        difficulty_clip = self._create_animated_text(
            difficulty_text,
            duration=video.duration,
            position="top",
            animation="bounce"
        )
        
        # Add dramatic music build-up
        hook_audio = self.sound_effects["hook"].set_duration(video.duration)
        
        # Apply zoom effect
        video = self._apply_zoom_effect(video)
        
        return CompositeVideoClip(
            [video, hook_text, difficulty_clip]
        ).set_audio(hook_audio)
        
    def _create_content_segment(
        self,
        video: VideoFileClip,
        segment: Dict
    ) -> CompositeVideoClip:
        """Create main content segment with effects
        
        Args:
            video: Background video clip
            segment: Text segment data
            
        Returns:
            Content segment clip
        """
        clips = [video]
        
        # Create text with word-by-word animation
        text_clip = self._create_animated_text(
            segment["text"],
            duration=video.duration,
            position=self._calculate_text_position(video, segment["text"]),
            animation="slide_up",
            word_by_word=True
        )
        clips.append(text_clip)
        
        # Add pause prompt if needed
        if segment.get("pause_prompt"):
            pause_clip = self._create_pause_prompt(
                duration=2.0,
                position="bottom"
            )
            clips.append(pause_clip)
        
        # Add countdown if needed
        if segment.get("countdown"):
            countdown_clip = self._create_countdown(
                duration=5.0,
                position="center"
            )
            clips.append(countdown_clip)
        
        # Apply visual effects
        video = self._apply_zoom_effect(video)
        
        return CompositeVideoClip(clips)
        
    def _create_animated_text(
        self,
        text: str,
        duration: float,
        position: str,
        animation: str = "fade",
        word_by_word: bool = False
    ) -> Union[TextClip, CompositeVideoClip]:
        """Create animated text clip
        
        Args:
            text: Text content
            duration: Clip duration
            position: Text position
            animation: Animation type
            word_by_word: Whether to animate word by word
            
        Returns:
            Animated text clip
        """
        if not word_by_word:
            return self._create_single_text_animation(
                text, duration, position, animation
            )
        
        words = text.split()
        word_duration = duration / len(words)
        word_clips = []
        
        for i, word in enumerate(words):
            clip = self._create_single_text_animation(
                word,
                duration - (i * word_duration),
                position,
                animation
            ).set_start(i * word_duration)
            word_clips.append(clip)
        
        return CompositeVideoClip(word_clips)
        
    def _create_single_text_animation(
        self,
        text: str,
        duration: float,
        position: str,
        animation: str
    ) -> TextClip:
        """Create single text clip with animation
        
        Args:
            text: Text content
            duration: Clip duration
            position: Text position
            animation: Animation type
            
        Returns:
            Animated text clip
        """
        clip = TextClip(
            text,
            fontsize=self.text_config["font_size"],
            color=self.text_config["color"],
            font=self.text_config["font_family"],
            bg_color=f"rgba(0,0,0,{self.text_config['background_opacity']})"
        ).set_duration(duration)
        
        if animation == "fade":
            clip = clip.fadein(0.5)
        elif animation == "slide_up":
            clip = clip.set_position(
                lambda t: (
                    position[0],
                    position[1] + (100 * (1 - min(t, 0.5) * 2))
                )
            )
        elif animation == "scale_up":
            clip = clip.set_position(position).resize(
                lambda t: 1 + (0.5 * (1 - min(t, 0.5) * 2))
            )
        elif animation == "bounce":
            clip = clip.set_position(
                lambda t: (
                    position[0],
                    position[1] + (20 * abs(np.sin(t * np.pi * 2)))
                )
            )
        
        return clip
        
    def _create_pause_prompt(
        self,
        duration: float,
        position: str
    ) -> TextClip:
        """Create pause prompt with animation
        
        Args:
            duration: Prompt duration
            position: Prompt position
            
        Returns:
            Animated pause prompt
        """
        return self._create_animated_text(
            "⏸️ Pause now to think!",
            duration=duration,
            position=position,
            animation="bounce"
        )
        
    def _create_countdown(
        self,
        duration: float,
        position: str
    ) -> CompositeVideoClip:
        """Create countdown timer with effects
        
        Args:
            duration: Countdown duration
            position: Timer position
            
        Returns:
            Countdown clip
        """
        clips = []
        countdown_audio = self.sound_effects["countdown"].set_duration(duration)
        
        for i in range(int(duration), 0, -1):
            clip = self._create_animated_text(
                str(i),
                duration=1.0,
                position=position,
                animation="scale_up"
            ).set_start(duration - i)
            clips.append(clip)
        
        return CompositeVideoClip(clips).set_audio(countdown_audio)
        
    def _create_call_to_action(self, video: VideoFileClip) -> CompositeVideoClip:
        """Create engaging call-to-action
        
        Args:
            video: Background video clip
            
        Returns:
            CTA clip
        """
        cta_config = self.engagement_config["call_to_action"]
        
        # Create CTA text clips
        primary_cta = self._create_animated_text(
            cta_config["primary"],
            duration=video.duration,
            position="center",
            animation="slide_up"
        )
        
        secondary_cta = self._create_animated_text(
            cta_config["secondary"],
            duration=video.duration,
            position="bottom",
            animation="fade"
        )
        
        return CompositeVideoClip(
            [video, primary_cta, secondary_cta]
        )
        
    def _apply_zoom_effect(self, video: VideoFileClip) -> VideoFileClip:
        """Apply subtle zoom effect
        
        Args:
            video: Input video clip
            
        Returns:
            Video with zoom effect
        """
        zoom_config = self.engagement_config["visual_effects"]["zoom"]
        
        if not zoom_config["enabled"]:
            return video
        
        return video.resize(
            lambda t: 1 + (
                (zoom_config["max_scale"] - 1)
                * (1 - np.cos(t * np.pi / video.duration)) / 2
            )
        )
        
    def _calculate_text_position(
        self,
        video: VideoFileClip,
        text: str
    ) -> Tuple[int, int]:
        """Calculate optimal text position
        
        Args:
            video: Video clip
            text: Text content
            
        Returns:
            Optimal (x, y) position
        """
        if self.text_config["position"] != "smart":
            return self._get_fixed_position(video.size)
        
        # Get frame from middle of video
        frame = video.get_frame(video.duration / 2)
        
        # Implement smart positioning logic
        # - Face detection
        # - Busy area detection
        # - Preferred zone selection
        
        # For now, return center position
        return (video.w // 2, video.h // 2) 