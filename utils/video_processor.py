"""Video processing utilities"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.tools.subtitles import SubtitlesClip
from utils.logger import log, StructuredLogger

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
        effects: Optional[List[str]] = None,
        transitions: Optional[List[str]] = None
    ) -> bool:
        """Create a complete riddle video
        
        Args:
            background_path: Path to background video
            riddle_audio_path: Path to riddle audio
            answer_audio_path: Path to answer audio
            riddle_text: Riddle text
            answer_text: Answer text
            output_path: Output path
            effects: List of visual effects to apply
            transitions: List of transitions to use
            
        Returns:
            True if successful
        """
        try:
            # Create temporary files
            temp_dir = os.path.join(self.output_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            resized_bg = os.path.join(temp_dir, "resized_bg.mp4")
            
            # Step 1: Resize background video
            if not self.resize_video(
                background_path,
                resized_bg,
                effects=effects
            ):
                raise ValueError("Failed to resize background video")
            
            # Step 2: Load video and audio clips
            try:
                video = VideoFileClip(resized_bg, audio=False)  # Disable audio for background
                riddle_audio = AudioFileClip(riddle_audio_path)
                answer_audio = AudioFileClip(answer_audio_path)
            except Exception as e:
                raise ValueError(f"Failed to load media files: {str(e)}")
            
            # Step 3: Create riddle segment
            riddle_segment = video.subclip(0, riddle_audio.duration)
            riddle_segment = riddle_segment.set_audio(riddle_audio)
            
            # Step 4: Create answer segment
            answer_segment = video.subclip(
                riddle_audio.duration,
                riddle_audio.duration + answer_audio.duration
            )
            answer_segment = answer_segment.set_audio(answer_audio)
            
            # Create text overlay function for riddle
            def riddle_text_overlay(frame):
                # Create a copy of the frame
                result = frame.copy()
                
                # Add semi-transparent black background
                overlay = np.zeros_like(frame)
                cv2.rectangle(
                    overlay,
                    (0, int(frame.shape[0] * 0.4)),
                    (frame.shape[1], int(frame.shape[0] * 0.6)),
                    (0, 0, 0),
                    -1
                )
                cv2.addWeighted(overlay, 0.5, result, 1 - 0.5, 0, result)
                
                # Split text into lines
                max_width = int(frame.shape[1] * 0.8)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.5
                thickness = 2
                
                # Calculate text size and split into lines
                words = riddle_text.split()
                lines = []
                current_line = []
                current_width = 0
                
                for word in words:
                    word_size = cv2.getTextSize(
                        word + " ",
                        font,
                        font_scale,
                        thickness
                    )[0]
                    
                    if current_width + word_size[0] <= max_width:
                        current_line.append(word)
                        current_width += word_size[0]
                    else:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_width = word_size[0]
                
                if current_line:
                    lines.append(" ".join(current_line))
                
                # Draw text lines
                y = int(frame.shape[0] * 0.5)
                for line in lines:
                    text_size = cv2.getTextSize(
                        line,
                        font,
                        font_scale,
                        thickness
                    )[0]
                    x = (frame.shape[1] - text_size[0]) // 2
                    
                    # Draw text with outline
                    cv2.putText(
                        result,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        (0, 0, 0),  # Black outline
                        thickness * 3
                    )
                    cv2.putText(
                        result,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        (255, 255, 255),  # White text
                        thickness
                    )
                    y += text_size[1] + 10
                
                return result
            
            # Create text overlay function for answer
            def answer_text_overlay(frame):
                # Create a copy of the frame
                result = frame.copy()
                
                # Add semi-transparent black background
                overlay = np.zeros_like(frame)
                cv2.rectangle(
                    overlay,
                    (0, int(frame.shape[0] * 0.4)),
                    (frame.shape[1], int(frame.shape[0] * 0.6)),
                    (0, 0, 0),
                    -1
                )
                cv2.addWeighted(overlay, 0.5, result, 1 - 0.5, 0, result)
                
                # Split text into lines
                max_width = int(frame.shape[1] * 0.8)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.5
                thickness = 2
                
                # Calculate text size and split into lines
                words = ("The answer is: " + answer_text).split()
                lines = []
                current_line = []
                current_width = 0
                
                for word in words:
                    word_size = cv2.getTextSize(
                        word + " ",
                        font,
                        font_scale,
                        thickness
                    )[0]
                    
                    if current_width + word_size[0] <= max_width:
                        current_line.append(word)
                        current_width += word_size[0]
                    else:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_width = word_size[0]
                
                if current_line:
                    lines.append(" ".join(current_line))
                
                # Draw text lines
                y = int(frame.shape[0] * 0.5)
                for line in lines:
                    text_size = cv2.getTextSize(
                        line,
                        font,
                        font_scale,
                        thickness
                    )[0]
                    x = (frame.shape[1] - text_size[0]) // 2
                    
                    # Draw text with outline
                    cv2.putText(
                        result,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        (0, 0, 0),  # Black outline
                        thickness * 3
                    )
                    cv2.putText(
                        result,
                        line,
                        (x, y),
                        font,
                        font_scale,
                        (255, 255, 255),  # White text
                        thickness
                    )
                    y += text_size[1] + 10
                
                return result
            
            # Apply text overlays
            riddle_segment = riddle_segment.fl_image(riddle_text_overlay)
            answer_segment = answer_segment.fl_image(answer_text_overlay)
            
            # Step 5: Concatenate segments with crossfade
            final_video = concatenate_videoclips(
                [riddle_segment, answer_segment],
                method="compose",
                padding=-0.5  # Add a small crossfade
            )
            
            # Step 6: Write final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=self.fps,
                preset='ultrafast',  # Faster encoding
                threads=4  # Use multiple threads
            )
            
            # Step 7: Clean up
            try:
                video.close()
                riddle_audio.close()
                answer_audio.close()
                riddle_segment.close()
                answer_segment.close()
                final_video.close()
            except Exception as e:
                self.logger.error(f"Error closing clips: {str(e)}")
            
            # Clean up temporary files
            try:
                if os.path.exists(resized_bg):
                    os.remove(resized_bg)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                self.logger.error(f"Error cleaning up temp files: {str(e)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating riddle video: {str(e)}")
            return False
    
    def _create_segment(
        self,
        video_path: str,
        audio_path: str,
        text: str,
        output_path: str,
        text_position: Tuple[float, float]
    ) -> bool:
        """Create a video segment with audio and text
        
        Args:
            video_path: Path to video
            audio_path: Path to audio
            text: Text to overlay
            output_path: Output path
            text_position: Text position (x, y) as fractions
            
        Returns:
            True if successful
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Create output video
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (width, height)
            )
            
            # Calculate text position
            text_x = int(width * text_position[0])
            text_y = int(height * text_position[1])
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Add text with animation
                progress = min(frame_count / (fps * 0.5), 1.0)
                frame = self.add_text_overlay(
                    frame,
                    text,
                    (text_x, text_y),
                    animation="fade",
                    progress=progress
                )
                
                out.write(frame)
                frame_count += 1
            
            # Release resources
            cap.release()
            out.release()
            
            # Add audio
            return self._merge_audio_video(output_path, audio_path, output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating segment: {str(e)}")
            return False
    
    def _merge_segments(
        self,
        segment_paths: List[str],
        output_path: str,
        transitions: Optional[List[str]] = None
    ) -> bool:
        """Merge video segments with transitions
        
        Args:
            segment_paths: List of segment paths
            output_path: Output path
            transitions: List of transitions to use
            
        Returns:
            True if successful
        """
        try:
            if not segment_paths:
                raise ValueError("No segments to merge")
            
            if len(segment_paths) == 1:
                # Just copy the single segment
                import shutil
                shutil.copy2(segment_paths[0], output_path)
                return True
            
            # Get first segment properties
            cap = cv2.VideoCapture(segment_paths[0])
            if not cap.isOpened():
                raise ValueError("Could not open first segment")
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            # Create output video
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (width, height)
            )
            
            # Process segments
            transition_frames = int(fps)  # 1 second transition
            transitions = transitions or ["fade"]
            current_transition = 0
            
            for i, segment_path in enumerate(segment_paths):
                cap = cv2.VideoCapture(segment_path)
                
                # Write segment frames
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # If not last segment, handle transition
                    if (i < len(segment_paths) - 1 and
                        cap.get(cv2.CAP_PROP_POS_FRAMES) >
                        cap.get(cv2.CAP_PROP_FRAME_COUNT) - transition_frames):
                        
                        # Get next segment's first frame
                        next_cap = cv2.VideoCapture(segment_paths[i + 1])
                        _, next_frame = next_cap.read()
                        next_cap.release()
                        
                        if next_frame is not None:
                            # Calculate transition progress
                            progress = (cap.get(cv2.CAP_PROP_POS_FRAMES) -
                                      (cap.get(cv2.CAP_PROP_FRAME_COUNT) -
                                       transition_frames)) / transition_frames
                            
                            # Apply transition
                            transition = transitions[
                                current_transition % len(transitions)
                            ]
                            frame = self.add_transition(
                                frame,
                                next_frame,
                                progress,
                                transition
                            )
                    
                    out.write(frame)
                
                cap.release()
                current_transition += 1
            
            out.release()
            return True
            
        except Exception as e:
            self.logger.error(f"Error merging segments: {str(e)}")
            return False
    
    def _merge_audio_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> bool:
        """Merge audio and video files
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Output path
            
        Returns:
            True if successful
        """
        try:
            import subprocess
            
            # Use ffmpeg to merge audio and video
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if result.returncode != 0:
                raise ValueError(
                    f"FFmpeg error: {result.stderr.decode()}"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error merging audio and video: {str(e)}")
            return False 