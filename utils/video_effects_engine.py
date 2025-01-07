"""Video effects and animation engine"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from moviepy.video.tools.subtitles import SubtitlesClip
from utils.logger import log, StructuredLogger
from config.config import Config
import random

class VideoEffectsEngine:
    """Engine for applying video effects and animations"""
    
    def __init__(
        self,
        output_dir: str = "output",
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None,
        logger: Optional[StructuredLogger] = None
    ):
        """Initialize video effects engine
        
        Args:
            output_dir: Output directory
            width: Video width (defaults to config)
            height: Video height (defaults to config)
            fps: Frames per second (defaults to config)
            logger: Logger instance
        """
        self.config = Config()
        self.logger = logger or log
        
        # Load video settings from config
        self.width = width or self.config.get("video.resolution.width", 1080)
        self.height = height or self.config.get("video.resolution.height", 1920)
        self.fps = fps or self.config.get("video.fps", 30)
        
        # Load text settings from config
        self.text_config = {
            "font_scale": self.config.get("video.text.font_scale", 1.0),
            "font_thickness": self.config.get("video.text.font_thickness", 2),
            "font_color": tuple(self.config.get("video.text.font_color", [255, 255, 255])),
            "background_color": tuple(self.config.get("video.text.background_color", [0, 0, 0])),
            "font_size": self.config.get("video.text.font_size", 36),
            "font_family": self.config.get("video.text.font_family", "Arial"),
            "background_opacity": self.config.get("video.text.background_opacity", 0.5),
            "position": self.config.get("video.text.position", "smart")
        }
        
        # Load effects settings from config
        self.visual_effects_config = {
            "zoom": {
                "enabled": self.config.get("video.effects.zoom.enabled", True),
                "max_scale": self.config.get("video.effects.zoom.max_scale", 1.2)
            }
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def createMultiRiddleVideo(
        self,
        background_path: str,
        riddle_segments: List[Dict],
        output_path: str,
        tts_engine: Any,  # ElevenLabs TTS engine
        video_service: Any,  # VideoService instance
        category: str,
        effects: Optional[List[str]] = None,
        transitions: Optional[List[str]] = None
    ) -> bool:
        """Create a multi-riddle video with effects
        
        Args:
            background_path: Path to background video
            riddle_segments: List of riddle segments
            output_path: Output video path
            tts_engine: TTS engine instance
            video_service: Video service instance
            category: Riddle category
            effects: List of effects to apply
            transitions: List of transitions to use
            
        Returns:
            True if successful
        """
        try:
            # Generate hook and CTA audio
            hook_text = random.choice(self.config.get("riddle.format.hook_patterns"))
            cta_text = "Follow for more riddles!"
            
            hook_audio = tts_engine.generate_speech(hook_text)
            cta_audio = tts_engine.generate_speech(cta_text)
            
            # Generate/load question number voice overs
            question_number_audios = []
            for i in range(len(riddle_segments)):
                cache_path = f"cache/voice/question_{i+1}_eleven.mp3"
                if os.path.exists(cache_path):
                    question_number_audios.append(AudioFileClip(cache_path))
                else:
                    question_vo = tts_engine.generate_speech(f"Question number {i+1}")
                    os.rename(question_vo, cache_path)
                    question_number_audios.append(AudioFileClip(cache_path))
            
            # Load all media
            try:
                countdown_audio = AudioFileClip("assets/audio/countdown.mp3")
                reveal_audio = AudioFileClip("assets/audio/reveal.mp3")
                hook_audio_clip = AudioFileClip(str(hook_audio))
                cta_audio_clip = AudioFileClip(str(cta_audio))
                
                # Load all riddle audios
                riddle_audios = []
                for segment in riddle_segments:
                    riddle_audio = AudioFileClip(segment['riddle_audio'])
                    answer_audio = AudioFileClip(segment['answer_audio'])
                    riddle_audios.append((riddle_audio, answer_audio))
            except Exception as e:
                raise ValueError(f"Failed to load media files: {str(e)}")
            
            # Calculate durations from config
            hook_min_duration = self.config.get("riddle.timing.hook.min_duration", 5)
            hook_padding = self.config.get("riddle.timing.hook.padding", 1)
            hook_duration = max(hook_min_duration, hook_audio_clip.duration + hook_padding)
            
            cta_min_duration = self.config.get("riddle.timing.cta.min_duration", 4)
            cta_padding = self.config.get("riddle.timing.cta.padding", 1)
            cta_duration = max(cta_min_duration, cta_audio_clip.duration + cta_padding)
            
            thinking_duration = self.config.get("riddle.timing.thinking.duration", 6)
            question_padding = self.config.get("riddle.timing.question.padding", 2)
            answer_padding = self.config.get("riddle.timing.answer.padding", 3)
            
            total_duration = hook_duration
            segment_timings = []
            
            for i, (riddle_audio, answer_audio) in enumerate(riddle_audios):
                question_number_duration = question_number_audios[i].duration + 0.5
                question_duration = riddle_audio.duration + question_padding
                answer_duration = answer_audio.duration + answer_padding
                
                segment_timings.append({
                    'number_start': total_duration,
                    'number_end': total_duration + question_number_duration,
                    'question_start': total_duration + question_number_duration,
                    'question_end': total_duration + question_number_duration + question_duration,
                    'thinking_start': total_duration + question_number_duration + question_duration,
                    'thinking_end': total_duration + question_number_duration + question_duration + thinking_duration,
                    'answer_start': total_duration + question_number_duration + question_duration + thinking_duration,
                    'answer_end': total_duration + question_number_duration + question_duration + thinking_duration + answer_duration
                })
                
                total_duration += question_number_duration + question_duration + thinking_duration + answer_duration
            
            total_duration += cta_duration
            
            # Create video segments with different background videos
            video_segments = []
            
            # Hook section - get a new background video
            hook_bg_path = video_service.get_video(category)
            hook_bg = VideoFileClip(hook_bg_path, audio=False)
            if hook_bg.duration < hook_duration:
                hook_bg = hook_bg.loop(duration=hook_duration)
            else:
                hook_bg = hook_bg.subclip(0, hook_duration)
            hook_segment = hook_bg.fl_image(lambda frame: self._create_text_overlay(frame, hook_text))
            video_segments.append(hook_segment)
            
            # Riddle sections
            for i, timing in enumerate(segment_timings):
                # Get new background videos for each segment
                number_bg_path = video_service.get_video(category)
                question_bg_path = video_service.get_video(category)
                thinking_bg_path = video_service.get_video(category)
                answer_bg_path = video_service.get_video(category)
                
                # Question number segment
                number_duration = timing['number_end'] - timing['number_start']
                number_bg = VideoFileClip(number_bg_path, audio=False)
                if number_bg.duration < number_duration:
                    number_bg = number_bg.loop(duration=number_duration)
                else:
                    number_bg = number_bg.subclip(0, number_duration)
                number_segment = number_bg.fl_image(lambda frame: self._create_text_overlay(frame, f"Question #{i+1}"))
                video_segments.append(number_segment)
                
                # Question segment
                question_duration = timing['question_end'] - timing['question_start']
                question_bg = VideoFileClip(question_bg_path, audio=False)
                if question_bg.duration < question_duration:
                    question_bg = question_bg.loop(duration=question_duration)
                else:
                    question_bg = question_bg.subclip(0, question_duration)
                question_segment = question_bg.fl_image(lambda frame: self._create_text_overlay(frame, riddle_segments[i]['riddle_text']))
                video_segments.append(question_segment)
                
                # Thinking segment
                thinking_duration = timing['thinking_end'] - timing['thinking_start']
                thinking_bg = VideoFileClip(thinking_bg_path, audio=False)
                if thinking_bg.duration < thinking_duration:
                    thinking_bg = thinking_bg.loop(duration=thinking_duration)
                else:
                    thinking_bg = thinking_bg.subclip(0, thinking_duration)
                thinking_segment = thinking_bg.fl_image(
                    lambda frame: self._create_text_overlay(frame, "⏱️ Time to Think!")
                )
                video_segments.append(thinking_segment)
                
                # Answer segment
                answer_duration = timing['answer_end'] - timing['answer_start']
                answer_bg = VideoFileClip(answer_bg_path, audio=False)
                if answer_bg.duration < answer_duration:
                    answer_bg = answer_bg.loop(duration=answer_duration)
                else:
                    answer_bg = answer_bg.subclip(0, answer_duration)
                answer_segment = answer_bg.fl_image(
                    lambda frame: self._create_text_overlay(frame, f"The answer is:\n{riddle_segments[i]['answer_text']}")
                )
                video_segments.append(answer_segment)
            
            # CTA section - get a new background video
            cta_bg_path = video_service.get_video(category)
            cta_bg = VideoFileClip(cta_bg_path, audio=False)
            if cta_bg.duration < cta_duration:
                cta_bg = cta_bg.loop(duration=cta_duration)
            else:
                cta_bg = cta_bg.subclip(0, cta_duration)
            cta_segment = cta_bg.fl_image(lambda frame: self._create_text_overlay(frame, "👆 Follow for Daily Riddles!\n❤️ Like if You Got Them Right!"))
            video_segments.append(cta_segment)
            
            # Concatenate all video segments
            final_video = concatenate_videoclips(video_segments, method="compose")
            
            # Create audio segments
            audio_segments = []
            
            # Add hook audio
            audio_segments.append(hook_audio_clip.set_start(0))
            
            # Add CTA audio at the end
            audio_segments.append(cta_audio_clip.set_start(total_duration - cta_duration))
            
            for i, (riddle_audio, answer_audio) in enumerate(riddle_audios):
                # Add question number audio
                audio_segments.append(question_number_audios[i].set_start(segment_timings[i]['number_start']))
                
                # Add riddle audio
                audio_segments.append(riddle_audio.set_start(segment_timings[i]['question_start']))
                
                # Add countdown audio (played twice)
                countdown_start = segment_timings[i]['thinking_start']
                audio_segments.append(countdown_audio.copy().set_start(countdown_start))
                audio_segments.append(countdown_audio.copy().set_start(countdown_start + 3))
                
                # Add reveal and answer audio
                answer_start = segment_timings[i]['answer_start']
                audio_segments.append(reveal_audio.copy().set_start(answer_start))
                audio_segments.append(answer_audio.set_start(answer_start + reveal_audio.duration))
            
            # Combine all audio
            final_audio = CompositeAudioClip(audio_segments)
            final_video = final_video.set_audio(final_audio)
            
            # Write final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=self.fps,
                preset='ultrafast',
                threads=4
            )
            
            # Clean up
            try:
                countdown_audio.close()
                reveal_audio.close()
                hook_audio_clip.close()
                cta_audio_clip.close()
                final_video.close()
                for audio in question_number_audios:
                    audio.close()
                for riddle_audio, answer_audio in riddle_audios:
                    riddle_audio.close()
                    answer_audio.close()
                for segment in video_segments:
                    segment.close()
            except Exception as e:
                self.logger.error(f"Error closing clips: {str(e)}")
            
            # Clean up temporary files
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                self.logger.error(f"Error cleaning up temp files: {str(e)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating multi-riddle video: {str(e)}")
            return False 
    
    def _create_text_overlay(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Create consistent text overlay for all segments with text wrapping and safe zones
        
        Args:
            frame: Input frame
            text: Text to overlay
            
        Returns:
            Frame with text overlay
        """
        result = frame.copy()
        
        # Add gradient background
        overlay = np.zeros_like(frame)
        h, w = frame.shape[:2]
        for i in range(h):
            alpha = 0.7 * (1 - abs(i - h/2)/(h/2))
            overlay[i, :] = [0, 0, 0]  # Black background
            cv2.addWeighted(overlay[i:i+1, :], alpha, result[i:i+1, :], 1-alpha, 0, result[i:i+1, :])
        
        # Text settings
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.8
        thickness = 2
        
        # Define safe zone (80% of width, centered)
        safe_width = int(w * 0.8)
        margin = (w - safe_width) // 2
        
        # Split text into lines
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            current_line = []
            current_width = 0
            
            for word in words:
                word_size = cv2.getTextSize(word, font, font_scale, thickness)[0]
                space_size = cv2.getTextSize(" ", font, font_scale, thickness)[0]
                
                # If adding this word would exceed safe width, start a new line
                if current_width + word_size[0] + (len(current_line) * space_size[0]) > safe_width:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_size[0]
                else:
                    current_line.append(word)
                    current_width += word_size[0]
            
            if current_line:
                lines.append(" ".join(current_line))
            
            # Add empty line between paragraphs if there are more paragraphs
            if paragraph != text.split('\n')[-1]:
                lines.append("")
        
        # Calculate total text height
        line_height = cv2.getTextSize("A", font, font_scale, thickness)[0][1] + 20
        total_height = len(lines) * line_height
        
        # Start drawing from vertical center
        y = (h - total_height) // 2 + line_height
        
        # Draw each line
        for line in lines:
            if line:  # Skip empty lines (just adds spacing)
                # Get line width for centering
                text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
                x = (w - text_size[0]) // 2
                
                # Draw outline
                cv2.putText(result, line, (x, y), font, font_scale, (0, 0, 0), thickness * 3)
                cv2.putText(result, line, (x, y), font, font_scale, (255, 255, 255), thickness)
            
            y += line_height
        
        return result
    
    def createAnimatedOverlay(
        self,
        text: str,
        duration: float,
        position: str,
        animation: str = "fade",
        word_by_word: bool = False
    ) -> Union[TextClip, CompositeVideoClip]:
        """Create animated overlay with text"""
        if not word_by_word:
            return self._createSingleOverlayAnimation(
                text, duration, position, animation
            )
        
        words = text.split()
        word_duration = duration / len(words)
        word_clips = []
        
        for i, word in enumerate(words):
            clip = self._createSingleOverlayAnimation(
                word,
                duration - (i * word_duration),
                position,
                animation
            ).set_start(i * word_duration)
            word_clips.append(clip)
        
        return CompositeVideoClip(word_clips)
    
    def _createSingleOverlayAnimation(
        self,
        text: str,
        duration: float,
        position: str,
        animation: str
    ) -> TextClip:
        """Create single overlay animation"""
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
    
    def createInteractionPrompt(
        self,
        duration: float,
        position: str
    ) -> TextClip:
        """Create interactive user prompt with animation"""
        return self.createAnimatedOverlay(
            "⏸️ Pause now to think!",
            duration=duration,
            position=position,
            animation="bounce"
        )
    
    def createCountdown(
        self,
        duration: float,
        position: str
    ) -> CompositeVideoClip:
        """Create countdown timer with effects"""
        clips = []
        
        for i in range(int(duration), 0, -1):
            clip = self.createAnimatedOverlay(
                str(i),
                duration=1.0,
                position=position,
                animation="scale_up"
            ).set_start(duration - i)
            clips.append(clip)
        
        return CompositeVideoClip(clips)
    
    def applyDynamicZoom(self, video: VideoFileClip) -> VideoFileClip:
        """Apply dynamic zoom effect to video"""
        if not self.visual_effects_config["zoom"]["enabled"]:
            return video
        
        return video.resize(
            lambda t: 1 + (
                (self.visual_effects_config["zoom"]["max_scale"] - 1)
                * (1 - np.cos(t * np.pi / video.duration)) / 2
            )
        )
    
    def calculateOptimalPosition(
        self,
        video: VideoFileClip,
        text: str
    ) -> Tuple[int, int]:
        """Calculate optimal position for overlay"""
        if self.text_config["position"] != "smart":
            return self._get_fixed_position(video.size)
        
        # Get frame from middle of video
        frame = video.get_frame(video.duration / 2)
        
        # Smart positioning logic
        # - Face detection
        # - Busy area detection
        # - Preferred zone selection
        
        # For now, return center position
        return (video.w // 2, video.h // 2)
    
    def _get_fixed_position(self, size: Tuple[int, int]) -> Tuple[int, int]:
        """Get fixed position based on video size"""
        return (size[0] // 2, size[1] // 2) 