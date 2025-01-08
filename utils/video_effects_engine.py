"""Video effects and animation engine"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
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
        """Initialize video effects engine"""
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
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True) 
    
    def _create_text_overlay_function(self, text: str):
        """Create a function that will overlay text on a frame
        
        Args:
            text: Text to overlay
            
        Returns:
            Function that takes a frame and returns a frame with text overlay
        """
        return lambda frame: self._create_text_overlay(frame, text)
    
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
        """Create a multi-riddle video with effects"""
        # Create temporary directory for intermediate files
        temp_dir = os.path.join(os.path.dirname(output_path), "temp_video_files")
        os.makedirs(temp_dir, exist_ok=True)
        
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
                    question_vo = tts_engine.generate_speech(f"Question {i+1}")
                    os.rename(question_vo, cache_path)
                    question_number_audios.append(AudioFileClip(cache_path))
            
            # Load all media
            try:
                countdown_audio = AudioFileClip("assets/audio/countdown.mp3")
                reveal_audio = AudioFileClip("assets/audio/reveal.mp3")
                hook_audio_clip = AudioFileClip(str(hook_audio))
                cta_audio_clip = AudioFileClip(str(cta_audio))
                
                # Process riddle segments in order
                processed_segments = []
                for i, segment in enumerate(riddle_segments):
                    # Use the audio files that were passed in
                    riddle_audio = AudioFileClip(str(segment['riddle_audio']))
                    answer_audio = AudioFileClip(str(segment['answer_audio']))
                    
                    processed_segments.append({
                        'index': i,
                        'riddle_text': segment['riddle'],
                        'answer_text': segment['answer'],
                        'riddle_audio': riddle_audio,
                        'answer_audio': answer_audio
                    })
                
                # Sort segments by index to maintain order
                processed_segments.sort(key=lambda x: x['index'])
                
                # Extract audio clips in order
                riddle_audios = [(s['riddle_audio'], s['answer_audio']) for s in processed_segments]
                riddle_data = [{
                    'riddle_text': s['riddle_text'],
                    'answer_text': s['answer_text']
                } for s in processed_segments]
                
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
            hook_segment = hook_bg.fl_image(self._create_text_overlay_function(hook_text))
            video_segments.append(hook_segment)
            
            # Riddle sections - use riddle_data to maintain order
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
                number_text = f"Question {i+1}"
                number_segment = number_bg.fl_image(self._create_text_overlay_function(number_text))
                video_segments.append(number_segment)
                
                # Question segment
                question_duration = timing['question_end'] - timing['question_start']
                question_bg = VideoFileClip(question_bg_path, audio=False)
                if question_bg.duration < question_duration:
                    question_bg = question_bg.loop(duration=question_duration)
                else:
                    question_bg = question_bg.subclip(0, question_duration)
                question_segment = question_bg.fl_image(self._create_text_overlay_function(riddle_data[i]['riddle_text']))
                video_segments.append(question_segment)
                
                # Thinking segment
                thinking_duration = timing['thinking_end'] - timing['thinking_start']
                thinking_bg = VideoFileClip(thinking_bg_path, audio=False)
                if thinking_bg.duration < thinking_duration:
                    thinking_bg = thinking_bg.loop(duration=thinking_duration)
                else:
                    thinking_bg = thinking_bg.subclip(0, thinking_duration)
                thinking_segment = thinking_bg.fl_image(self._create_text_overlay_function("⏱️ Time to Think!"))
                video_segments.append(thinking_segment)
                
                # Answer segment
                answer_duration = timing['answer_end'] - timing['answer_start']
                answer_bg = VideoFileClip(answer_bg_path, audio=False)
                if answer_bg.duration < answer_duration:
                    answer_bg = answer_bg.loop(duration=answer_duration)
                else:
                    answer_bg = answer_bg.subclip(0, answer_duration)
                answer_text = f"The answer is:\n{riddle_data[i]['answer_text']}"
                answer_segment = answer_bg.fl_image(self._create_text_overlay_function(answer_text))
                video_segments.append(answer_segment)
            
            # CTA section - get a new background video
            cta_bg_path = video_service.get_video(category)
            cta_bg = VideoFileClip(cta_bg_path, audio=False)
            if cta_bg.duration < cta_duration:
                cta_bg = cta_bg.loop(duration=cta_duration)
            else:
                cta_bg = cta_bg.subclip(0, cta_duration)
            cta_segment = cta_bg.fl_image(self._create_text_overlay_function("👆 Follow for Daily Riddles!\n❤️ Like if You Got Them Right!"))
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
            
            # Combine audio segments
            final_audio = CompositeAudioClip(audio_segments)
            
            # Set audio to video
            final_video = final_video.set_audio(final_audio)
            
            # Write final video
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=self.fps,
                preset='ultrafast',
                threads=4,
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
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
        """Create consistent text overlay for all segments with text wrapping and safe zones"""
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