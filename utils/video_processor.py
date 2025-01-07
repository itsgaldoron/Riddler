"""Video processing utilities"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from moviepy.video.tools.subtitles import SubtitlesClip
from utils.logger import log, StructuredLogger
import random

class VideoProcessor:
    """Video processor class for editing and combining videos"""
    
    def __init__(
        self,
        output_dir: str = "output",
        width: Optional[int] = 1080,
        height: Optional[int] = 1920,
        fps: int = 30,
        font_scale: float = 1.0,
        font_thickness: int = 2,
        font_color: Tuple[int, int, int] = (255, 255, 255),
        background_color: Tuple[int, int, int] = (0, 0, 0),
        logger: Optional[StructuredLogger] = None
    ):
        """Initialize video processor
        
        Args:
            output_dir: Output directory for processed videos
            width: Output video width (optional)
            height: Output video height (optional)
            fps: Output video FPS
            font_scale: Font scale for text overlays
            font_thickness: Font thickness for text overlays
            font_color: Font color for text overlays (BGR)
            background_color: Background color for text overlays (BGR)
            logger: Logger instance
        """
        # Ensure even dimensions for MPEG4/libx264
        self.width = (width if width % 2 == 0 else width + 1) if width is not None else 1080
        self.height = (height if height % 2 == 0 else height + 1) if height is not None else 1920
        self.output_dir = output_dir
        self.fps = fps
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.font_color = font_color
        self.background_color = background_color
        self.logger = logger or log
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def add_text_overlay(
        self,
        frame: np.ndarray,
        text: str,
        position: Tuple[int, int],
        font: int = cv2.FONT_HERSHEY_SIMPLEX,
        background: bool = True,
        animation: Optional[str] = None,
        progress: float = 0.0
    ) -> np.ndarray:
        """Add text overlay to video frame
        
        Args:
            frame: Input frame
            text: Text to overlay
            position: Text position (x, y)
            font: OpenCV font
            background: Whether to add background behind text
            animation: Animation type (fade/slide)
            progress: Animation progress (0-1)
            
        Returns:
            Frame with text overlay
        """
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            text,
            font,
            self.font_scale,
            self.font_thickness
        )
        
        # Apply animation
        if animation == "fade":
            alpha = progress
        elif animation == "slide":
            position = (
                int(position[0] - text_width * (1 - progress)),
                position[1]
            )
        
        if background:
            # Add background rectangle
            padding = 10
            p1 = (
                position[0] - padding,
                position[1] - text_height - padding
            )
            p2 = (
                position[0] + text_width + padding,
                position[1] + padding
            )
            
            if animation == "fade":
                bg_color = list(self.background_color)
                bg_color.append(int(255 * alpha))
                cv2.rectangle(
                    frame,
                    p1,
                    p2,
                    tuple(bg_color),
                    -1
                )
            else:
                cv2.rectangle(
                    frame,
                    p1,
                    p2,
                    self.background_color,
                    -1
                )
        
        # Add text
        if animation == "fade":
            # Create text overlay
            overlay = frame.copy()
            cv2.putText(
                overlay,
                text,
                position,
                font,
                self.font_scale,
                self.font_color,
                self.font_thickness
            )
            # Blend with original frame
            cv2.addWeighted(
                overlay,
                alpha,
                frame,
                1 - alpha,
                0,
                frame
            )
        else:
            cv2.putText(
                frame,
                text,
                position,
                font,
                self.font_scale,
                self.font_color,
                self.font_thickness
            )
        
        return frame
    
    def add_visual_effects(
        self,
        frame: np.ndarray,
        effects: List[str]
    ) -> np.ndarray:
        """Add visual effects to frame
        
        Args:
            frame: Input frame
            effects: List of effects to apply
            
        Returns:
            Frame with effects
        """
        result = frame.copy()
        
        for effect in effects:
            if effect == "blur":
                result = cv2.GaussianBlur(result, (15, 15), 0)
            
            elif effect == "grayscale":
                result = cv2.cvtColor(
                    result,
                    cv2.COLOR_BGR2GRAY
                )
                result = cv2.cvtColor(
                    result,
                    cv2.COLOR_GRAY2BGR
                )
            
            elif effect == "vignette":
                rows, cols = result.shape[:2]
                kernel_x = cv2.getGaussianKernel(cols, cols/4)
                kernel_y = cv2.getGaussianKernel(rows, rows/4)
                kernel = kernel_y * kernel_x.T
                mask = kernel / kernel.max()
                for i in range(3):
                    result[:, :, i] = result[:, :, i] * mask
            
            elif effect == "sepia":
                kernel = np.array([
                    [0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189]
                ])
                result = cv2.transform(result, kernel)
            
            elif effect == "sharpen":
                kernel = np.array([
                    [-1, -1, -1],
                    [-1,  9, -1],
                    [-1, -1, -1]
                ])
                result = cv2.filter2D(result, -1, kernel)
        
        return result
    
    def add_transition(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        progress: float,
        transition: str = "fade"
    ) -> np.ndarray:
        """Add transition between frames
        
        Args:
            frame1: First frame
            frame2: Second frame
            progress: Transition progress (0-1)
            transition: Transition type
            
        Returns:
            Blended frame
        """
        if transition == "fade":
            return cv2.addWeighted(
                frame1,
                1 - progress,
                frame2,
                progress,
                0
            )
        
        elif transition == "wipe":
            rows, cols = frame1.shape[:2]
            split_col = int(cols * progress)
            result = frame1.copy()
            result[:, split_col:] = frame2[:, split_col:]
            return result
        
        elif transition == "dissolve":
            mask = np.random.random(frame1.shape[:2]) < progress
            mask = np.stack([mask] * 3, axis=2)
            return np.where(mask, frame2, frame1)
        
        return frame1
    
    def resize_video(
        self,
        input_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        effects: Optional[List[str]] = None
    ) -> bool:
        """Resize video to target dimensions using moviepy
        
        Args:
            input_path: Input video path
            output_path: Output video path
            width: Target width (optional)
            height: Target height (optional)
            effects: List of effects to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert paths to strings
            input_path = str(input_path)
            output_path = str(output_path)
            
            # Verify input file exists
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input video not found: {input_path}")
            
            # Verify input file is not empty
            if os.path.getsize(input_path) == 0:
                raise ValueError(f"Input video is empty: {input_path}")
            
            self.logger.debug(f"Loading video: {input_path}")
            
            # Load video with error handling
            try:
                video = VideoFileClip(input_path, audio=False)  # Disable audio loading for faster processing
            except Exception as e:
                self.logger.error(f"Failed to load video with error: {str(e)}")
                raise ValueError(f"Failed to load video: {str(e)}")
            
            if video is None:
                raise ValueError("VideoFileClip returned None")
            
            # Calculate target dimensions (ensuring they're even)
            if width is None and height is None:
                width = self.width
                height = self.height
            elif width is None:
                # Calculate width while maintaining aspect ratio
                aspect_ratio = video.w / video.h
                width = int(height * aspect_ratio)
                width = width if width % 2 == 0 else width + 1
            elif height is None:
                # Calculate height while maintaining aspect ratio
                aspect_ratio = video.h / video.w
                height = int(width * aspect_ratio)
                height = height if height % 2 == 0 else height + 1
            
            # Ensure both dimensions are even
            width = width if width % 2 == 0 else width + 1
            height = height if height % 2 == 0 else height + 1
            
            self.logger.debug(f"Resizing video to {width}x{height}")
            
            # Resize video
            resized = video.resize(width=width, height=height)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write output with lower preset for faster processing
            resized.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=self.fps,
                preset='ultrafast',  # Faster encoding
                threads=4  # Use multiple threads
            )
            
            # Clean up
            video.close()
            resized.close()
            
            self.logger.debug(f"Successfully resized video: {output_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Video resize failed: {str(e)}")
            return False
    
    def merge_audio_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> bool:
        """Merge audio and video files
        
        Args:
            video_path: Input video path
            audio_path: Input audio path
            output_path: Output video path
            
        Returns:
            True if successful
        """
        try:
            # Use ffmpeg to merge audio and video
            cmd = (
                f"ffmpeg -i {video_path} -i {audio_path} "
                f"-c:v copy -c:a aac -strict experimental "
                f"-map 0:v:0 -map 1:a:0 {output_path}"
            )
            
            result = os.system(cmd)
            success = result == 0
            
            self.logger.video_processing(
                "merge",
                f"{video_path}+{audio_path}",
                output_path,
                success
            )
            return success
            
        except Exception as e:
            self.logger.error(f"Error merging audio and video: {str(e)}")
            self.logger.video_processing(
                "merge",
                f"{video_path}+{audio_path}",
                output_path,
                False
            )
            return False
    
    def optimize_for_tiktok(
        self,
        input_path: str,
        output_path: str
    ) -> bool:
        """Optimize video for TikTok
        
        Args:
            input_path: Input video path
            output_path: Output video path
            
        Returns:
            True if successful
        """
        try:
            # Use ffmpeg to optimize video
            cmd = (
                f"ffmpeg -i {input_path} "
                f"-c:v libx264 -preset medium "
                f"-b:v 2500k -maxrate 2500k -bufsize 5000k "
                f"-c:a aac -b:a 128k "
                f"-movflags +faststart "
                f"{output_path}"
            )
            
            result = os.system(cmd)
            success = result == 0
            
            self.logger.video_processing(
                "optimize",
                input_path,
                output_path,
                success
            )
            return success
            
        except Exception as e:
            self.logger.error(f"Error optimizing video: {str(e)}")
            self.logger.video_processing(
                "optimize",
                input_path,
                output_path,
                False
            )
            return False
    
    def create_riddle_video(
        self,
        background_path: str,
        riddle_audio_path: str,
        answer_audio_path: str,
        riddle_text: str,
        answer_text: str,
        output_path: str,
        video_service: Any,  # VideoService instance
        category: str,
        effects: Optional[List[str]] = None,
        transitions: Optional[List[str]] = None
    ) -> bool:
        try:
            # Create temporary files
            temp_dir = os.path.join(os.path.dirname(output_path), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Step 1: Load video and audio clips
            try:
                riddle_audio = AudioFileClip(riddle_audio_path)
                answer_audio = AudioFileClip(answer_audio_path)
                countdown_audio = AudioFileClip("assets/audio/countdown.mp3")
                reveal_audio = AudioFileClip("assets/audio/reveal.mp3")
            except Exception as e:
                raise ValueError(f"Failed to load media files: {str(e)}")
            
            # Get timing configuration
            question_duration = riddle_audio.duration + 2  # Add buffer for text display
            thinking_time = 6  # Countdown duration
            answer_duration = answer_audio.duration + 3  # Add buffer for explanation
            
            # Create video segments with different background videos
            video_segments = []
            
            # Question segment - get a new background video
            question_bg_path = video_service.get_video(category)
            question_bg = VideoFileClip(question_bg_path, audio=False)
            if question_bg.duration < question_duration:
                question_bg = question_bg.loop(duration=question_duration)
            else:
                question_bg = question_bg.subclip(0, question_duration)
            question_segment = question_bg.fl_image(lambda frame: self._create_text_overlay(frame, riddle_text))
            question_segment = question_segment.set_audio(riddle_audio)
            video_segments.append(question_segment)
            
            # Thinking segment - get a new background video
            thinking_bg_path = video_service.get_video(category)
            thinking_bg = VideoFileClip(thinking_bg_path, audio=False)
            if thinking_bg.duration < thinking_time:
                thinking_bg = thinking_bg.loop(duration=thinking_time)
            else:
                thinking_bg = thinking_bg.subclip(0, thinking_time)
            thinking_segment = thinking_bg.fl_image(lambda frame: self._create_text_overlay(frame, "⏱️ Time to Think!"))
            countdown_audio_doubled = concatenate_audioclips([countdown_audio, countdown_audio])
            thinking_segment = thinking_segment.set_audio(countdown_audio_doubled)
            video_segments.append(thinking_segment)
            
            # Answer segment - get a new background video
            answer_bg_path = video_service.get_video(category)
            answer_bg = VideoFileClip(answer_bg_path, audio=False)
            if answer_bg.duration < answer_duration:
                answer_bg = answer_bg.loop(duration=answer_duration)
            else:
                answer_bg = answer_bg.subclip(0, answer_duration)
            answer_segment = answer_bg.fl_image(lambda frame: self._create_text_overlay(frame, f"The answer is:\n{answer_text}"))
            reveal_with_answer = concatenate_audioclips([reveal_audio, answer_audio])
            answer_segment = answer_segment.set_audio(reveal_with_answer)
            video_segments.append(answer_segment)
            
            # Concatenate segments with crossfade
            final_video = concatenate_videoclips(
                video_segments,
                method="compose",
                padding=-0.5  # Smooth crossfade
            )
            
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
                riddle_audio.close()
                answer_audio.close()
                countdown_audio.close()
                reveal_audio.close()
                final_video.close()
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
            self.logger.error(f"Error creating riddle video: {str(e)}")
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
    
    def create_multi_riddle_video(
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
        try:
            # Create temporary directory
            temp_dir = os.path.join(os.path.dirname(output_path), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Step 1: Generate/load voice overs
            hook_text = "Can You Solve These Mind-Bending Riddles?"
            cta_text = "Follow for Daily Riddles! Like if You Got Them Right!"
            
            # Generate hook and CTA voice overs
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
            
            # Step 2: Load all media
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
            
            # Calculate total duration needed
            hook_duration = max(5, hook_audio_clip.duration + 1)  # At least 5 seconds or audio duration + 1s
            cta_duration = max(4, cta_audio_clip.duration + 1)
            
            total_duration = hook_duration
            segment_timings = []
            
            for i, (riddle_audio, answer_audio) in enumerate(riddle_audios):
                question_number_duration = question_number_audios[i].duration + 0.5
                question_duration = riddle_audio.duration + 2
                thinking_duration = 6
                answer_duration = answer_audio.duration + 3
                
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