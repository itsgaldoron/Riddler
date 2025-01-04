from typing import List, Dict, Optional, Union, Tuple
import os
import numpy as np
from pathlib import Path
import json
from urllib.parse import urlparse
import requests
import openai
from PIL import Image
import logging
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from elevenlabs.client import ElevenLabs

# Add Pillow compatibility layer
from PIL import Image
try:
    ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    ANTIALIAS = Image.ANTIALIAS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration and utilities
from config import (
    VIDEO_SETTINGS, TIMING, CACHE, API, OUTPUT, 
    PARALLEL, ASSETS, TEXT, FONTS, TEXT_STYLES, TEXT_POSITIONS
)
from utils import ProgressBar, process_in_parallel, chunk_list

# Set up MoviePy with proper configuration before importing
os.environ["IMAGEMAGICK_BINARY"] = "/opt/homebrew/bin/convert"
os.environ["FFMPEG_BINARY"] = "ffmpeg"

# Import MoviePy components after configuration
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, ColorClip
from moviepy.editor import concatenate_videoclips, CompositeVideoClip, CompositeAudioClip

# Import riddle content
from riddle_content import RIDDLES

# API configuration
openai.api_key = API['openai']['api_key']
os.environ["OPENAI_API_KEY"] = API['openai']['api_key']
PEXELS_API_KEY = API['pexels']['api_key']
os.environ["PEXELS_API_KEY"] = API['pexels']['api_key']

def create_text_clip(
    text: Union[str, List[str], Tuple[str, ...]], 
    style: str = 'riddle',  # Style key from TEXT_STYLES
    color: Optional[str] = None,
    position: Optional[Union[str, Tuple[str, str]]] = None,
    size: Optional[Tuple[int, Optional[int]]] = None,
    duration: Optional[float] = None
) -> TextClip:
    """
    Create a text clip with proper styling and error handling.
    
    Args:
        text: Text content to display
        style: Style key from TEXT_STYLES config
        color: Override default text color
        position: Override default position
        size: Override default size
        duration: Clip duration
    
    Returns:
        TextClip with applied styling
    """
    try:
        if isinstance(text, (list, tuple)):
            text = "\n".join(str(item) for item in text)
        
        # Get style settings
        font_size = FONTS.get(style, FONTS['riddle'])
        text_color = color or VIDEO_SETTINGS['text_color']
        text_position = position or TEXT_POSITIONS.get(style, ('center', 'center'))
        text_size = size or (VIDEO_SETTINGS['width']-100, None)
        style_settings = TEXT_STYLES.get(style, {})
        
        # Create text clip with stroke
        txt_clip = TextClip(
            txt=str(text),
            fontsize=font_size,
            color=text_color,
            font=VIDEO_SETTINGS['font'],
            size=text_size,
            method='caption',
            align='center',  # Center text horizontally within its box
            stroke_color=style_settings.get('stroke_color', VIDEO_SETTINGS['text_stroke_color']),
            stroke_width=style_settings.get('stroke_width', VIDEO_SETTINGS['text_stroke_width'])
        )
        
        # Ensure position is a tuple for center positioning
        if text_position == 'center':
            text_position = ('center', 'center')
            
        # Set position and duration
        txt_clip = txt_clip.set_position(text_position)
        if duration:
            txt_clip = txt_clip.set_duration(duration)
        
        return txt_clip
        
    except Exception as e:
        logger.error(f"Error creating text clip: {e}")
        return TextClip(
            txt="Error displaying text",
            fontsize=FONTS['riddle'],
            color=VIDEO_SETTINGS['text_color'],
            font=VIDEO_SETTINGS['font']
        ).set_position(('center', 'center'))  # Center error message as well

class PexelsVideoManager:
    """Manages video downloads and caching from Pexels API."""
    
    def __init__(self):
        if not PEXELS_API_KEY:
            raise ValueError("PEXELS_API_KEY environment variable is not set")
            
        self.headers = {"Authorization": PEXELS_API_KEY}
        self.cache_dir = Path(CACHE['pexels_dir'])
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = Path(CACHE['pexels_mapping'])
        self.video_mapping = self._load_cache()
        
        # Define target resolution for TikTok
        self.target_width = 1080  # TikTok recommended width
        self.target_height = 1920  # TikTok recommended height
        self.min_duration = 3  # Minimum video duration in seconds
    
    def _resize_video(self, video_clip: VideoFileClip) -> VideoFileClip:
        """Resize video to match TikTok dimensions while maintaining aspect ratio."""
        # Calculate scaling factors
        width_scale = self.target_width / video_clip.w
        height_scale = self.target_height / video_clip.h
        
        # Use the larger scaling factor to ensure video fills the frame
        scale = max(width_scale, height_scale)
        
        # Calculate new dimensions
        new_width = int(video_clip.w * scale)
        new_height = int(video_clip.h * scale)
        
        # Resize video with LANCZOS resampling
        resized = video_clip.resize(
            (new_width, new_height),
            resample=ANTIALIAS
        )
        
        # Crop to target dimensions if needed
        x_center = (new_width - self.target_width) // 2
        y_center = (new_height - self.target_height) // 2
        
        return resized.crop(
            x1=max(0, x_center),
            y1=max(0, y_center),
            x2=min(new_width, x_center + self.target_width),
            y2=min(new_height, y_center + self.target_height)
        )
    
    def _load_cache(self) -> Dict[str, str]:
        """Load the video mapping cache from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save the video mapping cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.video_mapping, f)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _get_video_filename(self, video_url: str) -> str:
        """Generate a filename from the video URL."""
        parsed = urlparse(video_url)
        return f"{Path(parsed.path).stem}.mp4"
    
    def get_background_video(self, search_query: str, duration: float = 3) -> Optional[VideoFileClip]:
        """
        Get a sequence of background videos for the given search query.
        
        Args:
            search_query: Search term for the video
            duration: Total desired duration
        
        Returns:
            VideoFileClip object or None if videos cannot be retrieved
        """
        try:
            # Calculate how many 3-second clips we need
            num_clips = int(np.ceil(duration / 3))
            clips = []
            
            # Get multiple videos from cache or Pexels
            for i in range(num_clips):
                cache_key = f"{search_query}_{i}"
                clip = self._get_single_video(cache_key, search_query)
                if clip is None:
                    # If we can't get a new clip, loop the last successful one
                    if clips:
                        clip = clips[-1].copy()
                    else:
                        # Create a color clip as fallback
                        clip = ColorClip(
                            size=(self.target_width, self.target_height),
                            color=VIDEO_SETTINGS['background_color']
                        ).set_duration(3)
                clips.append(clip)
            
            # Concatenate all clips
            final_clip = concatenate_videoclips(clips)
            
            # Trim to exact duration
            return final_clip.set_duration(duration)
            
        except Exception as e:
            logger.error(f"Error creating background video sequence: {e}")
            return None
    
    def _get_single_video(self, cache_key: str, search_query: str) -> Optional[VideoFileClip]:
        """Get a single 3-second video clip."""
        try:
            # Check cache first
            if cache_key in self.video_mapping:
                cached_path = self.cache_dir / self.video_mapping[cache_key]
                if cached_path.exists():
                    video = VideoFileClip(str(cached_path))
                    video = self._resize_video(video)
                    return video.subclip(0, min(3, video.duration))
            
            # If not in cache, search Pexels
            response = requests.get(
                f"https://api.pexels.com/videos/search",
                params={
                    "query": search_query,
                    "per_page": 5,
                    "orientation": "portrait",
                    "size": "large"
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('videos'):
                return None
            
            # Filter videos by duration and resolution
            suitable_videos = []
            for video in data['videos']:
                video_files = video['video_files']
                portrait_files = [
                    f for f in video_files 
                    if f['height'] >= self.target_height 
                    and f['width'] >= self.target_width
                ]
                if portrait_files and video['duration'] >= 3:
                    suitable_videos.append((video, max(portrait_files, key=lambda x: x['height'])))
            
            if not suitable_videos:
                return None
            
            # Choose a random video from suitable ones
            video, video_file = suitable_videos[hash(cache_key) % len(suitable_videos)]
            video_url = video_file['link']
            
            # Download the video
            filename = f"{cache_key}_{self._get_video_filename(video_url)}"
            filepath = self.cache_dir / filename
            
            if not filepath.exists():
                video_response = requests.get(video_url, stream=True, timeout=30)
                video_response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            # Update cache
            self.video_mapping[cache_key] = filename
            self._save_cache()
            
            # Load, resize, and return video
            video = VideoFileClip(str(filepath))
            video = self._resize_video(video)
            return video.subclip(0, min(3, video.duration))
            
        except Exception as e:
            logger.error(f"Error getting single video clip: {e}")
            return None

class RiddleVideo:
    """Creates and manages video segments for geographic riddles."""
    
    def __init__(self):
        self.clips: List[Union[CompositeVideoClip, VideoFileClip]] = []
        self.current_time: float = 0
        self.voice_cache: Dict[str, str] = {}
        self.pexels_manager = PexelsVideoManager()
        self.voice_cache_dir = Path(CACHE['voice_dir'])
        self.voice_cache_dir.mkdir(exist_ok=True)
        self.voice_cache_file = self.voice_cache_dir / "voice_mapping.json"
        self.voice_mapping = self._load_voice_cache()
        self.elevenlabs_client = ElevenLabs(api_key=API['elevenlabs']['api_key'])
    
    def _load_voice_cache(self) -> Dict[str, str]:
        """Load the voice mapping cache from file."""
        try:
            if self.voice_cache_file.exists():
                with open(self.voice_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading voice cache: {e}")
        return {}
    
    def _save_voice_cache(self) -> None:
        """Save the voice mapping cache to file."""
        try:
            with open(self.voice_cache_file, 'w') as f:
                json.dump(self.voice_mapping, f)
        except Exception as e:
            logger.error(f"Error saving voice cache: {e}")
    
    def create_voice_over(
        self, 
        text: str, 
        filename: str, 
        voice: str = "Adam"  # Default ElevenLabs voice
    ) -> Optional[AudioFileClip]:
        """
        Create a voice over using ElevenLabs Text-to-Speech API with caching.
        
        Args:
            text: Text to convert to speech
            filename: Temporary filename for the voice clip
            voice: Voice ID or name to use from ElevenLabs
        
        Returns:
            AudioFileClip object or None if generation fails
        """
        cache_key = f"{text}_{voice}"
        
        try:
            # Check cache first
            if cache_key in self.voice_mapping:
                cached_path = self.voice_cache_dir / self.voice_mapping[cache_key]
                if cached_path.exists():
                    return AudioFileClip(str(cached_path))
            
            # Generate new voice clip
            audio = self.elevenlabs_client.generate(
                text=text,
                voice=voice,
                model="eleven_monolingual_v1"
            )
            
            # Save to cache directory
            cached_filename = f"{hash(cache_key)}.mp3"
            cached_path = self.voice_cache_dir / cached_filename
            
            # Save audio data
            with open(cached_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            
            # Update cache mapping
            self.voice_mapping[cache_key] = cached_filename
            self._save_voice_cache()
            
            return AudioFileClip(str(cached_path))
            
        except Exception as e:
            logger.error(f"Error creating voice-over: {e}")
            return None
    
    def create_text_clip(
        self, 
        text: str, 
        duration: float, 
        fontsize: int = FONTS['options'], 
        color: str = VIDEO_SETTINGS['text_color'], 
        position: Union[str, Tuple[str, str]] = ('center', 'center')  # Default to center
    ) -> TextClip:
        """
        Create a text clip with specified duration and styling.
        
        Args:
            text: Text content to display
            duration: Duration of the text clip
            fontsize: Size of the font
            color: Color of the text
            position: Position of the text on screen
        
        Returns:
            TextClip object
        """
        try:
            txt_clip = TextClip(
                text, 
                fontsize=fontsize, 
                color=color, 
                size=(VIDEO_SETTINGS['width']-100, None),
                method='caption', 
                align='center',  # Center text horizontally within its box
                bg_color='transparent'
            )
            
            # Ensure position is a tuple for center positioning
            if position == 'center':
                position = ('center', 'center')
                
            return txt_clip.set_position(position).set_duration(duration)
            
        except Exception as e:
            logger.error(f"Error creating text clip: {e}")
            return TextClip(
                "Error displaying text",
                fontsize=fontsize,
                color=color,
                font=VIDEO_SETTINGS['font']
            ).set_position(('center', 'center')).set_duration(duration)  # Center error message as well
    
    def create_timer(self, duration: float = 5) -> VideoFileClip:
        """
        Create a countdown timer with synchronized audio.
        
        Args:
            duration: Duration of the countdown
        
        Returns:
            VideoFileClip of the countdown timer
        """
        try:
            # Fixed 3-second countdown
            countdown_duration = 3
            
            # Load countdown sound effect and take exactly 3 seconds
            countdown_audio = AudioFileClip(ASSETS['countdown_sound'])
            if countdown_audio.duration > countdown_duration:
                # Take the last 3 seconds of the audio
                countdown_audio = countdown_audio.subclip(-countdown_duration)
            elif countdown_audio.duration < countdown_duration:
                # If audio is shorter, loop it to exactly 3 seconds
                repeats = int(np.ceil(countdown_duration / countdown_audio.duration))
                countdown_audio = concatenate_audioclips([countdown_audio] * repeats)
                countdown_audio = countdown_audio.subclip(0, countdown_duration)
            
            # Create timer clips with exact 1-second durations
            timer_clips = []
            for i in range(countdown_duration, 0, -1):
                timer = TextClip(
                    str(i), 
                    fontsize=FONTS['timer'], 
                    color=VIDEO_SETTINGS['text_color'], 
                    font=VIDEO_SETTINGS['font'],
                    bg_color='transparent',
                    stroke_color=TEXT_STYLES['timer']['stroke_color'],
                    stroke_width=TEXT_STYLES['timer']['stroke_width'],
                    method='caption',  # Use caption method for better centering
                    align='center',  # Center text horizontally
                    size=(VIDEO_SETTINGS['width'], None)  # Set width to match video
                ).set_position(('center', 'center')).set_duration(1.0)  # Exact 1-second duration
                timer_clips.append(timer)
            
            # Create the timer video
            timer_video = concatenate_videoclips(timer_clips)
            
            # Set the audio
            return timer_video.set_audio(countdown_audio)
            
        except Exception as e:
            logger.error(f"Error creating timer: {e}")
            # Return a simple fallback timer without audio
            return TextClip(
                "⏱", 
                fontsize=FONTS['timer'],
                color=VIDEO_SETTINGS['text_color'],
                font=VIDEO_SETTINGS['font'],
                method='caption',
                align='center',
                size=(VIDEO_SETTINGS['width'], None)
            ).set_position(('center', 'center')).set_duration(countdown_duration)
    
    def create_riddle_segment(
        self,
        riddle_text: str,
        options: List[str],
        answer: str,
        fact: str,
        question_number: int,
        duration: float = TIMING['riddle_duration']
    ) -> CompositeVideoClip:
        """
        Create a complete riddle segment with properly timed audio and visuals.
        """
        try:
            # Add question number to the riddle text
            numbered_riddle = f"Question {question_number}:\n{riddle_text}"
            
            # Format options text with proper spacing for voice-over
            options_vo_text = "\n".join(f"Option {i+1}... {opt}." for i, opt in enumerate(options))
            # Format options text for display
            options_display_text = "\n".join(f"{i+1}) {opt}" for i, opt in enumerate(options))
            
            # Generate all voice-overs first to get their durations
            riddle_vo = self.create_voice_over(
                f"Question {question_number}. {riddle_text}",
                "temp_riddle_vo.mp3",
                voice=API['elevenlabs']['voices']['riddle']
            )
            options_vo = self.create_voice_over(
                options_vo_text,  # Use formatted options text for voice-over
                "temp_options_vo.mp3",
                voice=API['elevenlabs']['voices']['options']
            )
            answer_vo = self.create_voice_over(
                f"The answer is {answer}! {fact}",
                "temp_answer_vo.mp3",
                voice=API['elevenlabs']['voices']['answer']
            )
            
            # Load sound effects
            countdown_audio = AudioFileClip(ASSETS['countdown_sound'])
            answer_sound = AudioFileClip(ASSETS['correct_sound'])
            
            # Smart timing calculations
            min_display_time = 2.5  # Minimum time to display text for readability
            
            # Natural break durations for different transitions
            BREAK_DURATIONS = {
                'after_riddle': 0.3,    # Very short break after riddle (question to options)
                'after_options': 0.0,    # No break before countdown
                'after_countdown': 0.3,  # Very brief pause after countdown for impact
                'after_answer': 0.8      # Short break between segments
            }
            
            # Calculate optimal additional break based on content complexity
            def calculate_content_break(text: str, base_time: float = 0.2) -> float:
                """Calculate additional break time based on content complexity"""
                # Count words and special characters as complexity indicators
                words = len(text.split())
                special_chars = len([c for c in text if not c.isalnum() and not c.isspace()])
                complexity = (words + special_chars) / 30
                return base_time * min(1.2, max(1.0, complexity))
            
            # Calculate riddle segment timing
            riddle_vo_duration = riddle_vo.duration if riddle_vo else 0
            riddle_content_break = calculate_content_break(riddle_text)
            riddle_display_time = max(min_display_time, riddle_vo_duration + riddle_content_break)
            riddle_duration = riddle_display_time + BREAK_DURATIONS['after_riddle']
            
            # Calculate options segment timing
            options_vo_duration = options_vo.duration if options_vo else 0
            options_content_break = calculate_content_break(options_display_text)
            options_display_time = max(min_display_time, options_vo_duration + options_content_break)
            options_duration = options_display_time + BREAK_DURATIONS['after_options']
            
            # Countdown timing - fixed duration with break
            countdown_duration = 3.0  # Fixed 3-second countdown
            countdown_total = countdown_duration + BREAK_DURATIONS['after_countdown']
            
            # Answer and fact timing
            answer_sound_duration = min(1.0, answer_sound.duration)
            answer_vo_duration = answer_vo.duration if answer_vo else 0
            answer_content_break = calculate_content_break(fact)
            answer_display_time = max(
                min_display_time,
                answer_vo_duration + answer_sound_duration + answer_content_break
            )
            answer_total = answer_display_time + BREAK_DURATIONS['after_answer']
            
            # Calculate total segment duration
            total_duration = (riddle_duration + options_duration + 
                            countdown_total + answer_total)
            
            # Create background video
            bg_video = self.pexels_manager.get_background_video(
                "geography landscape aerial",
                total_duration
            )
            if bg_video is None:
                bg_video = ColorClip(
                    size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                    color=VIDEO_SETTINGS['background_color']
                ).set_duration(total_duration)
            
            # Create text clips with proper timing and styling
            riddle = create_text_clip(
                numbered_riddle,
                style='riddle',
                duration=riddle_display_time
            )
            
            options_clip = create_text_clip(
                options_display_text,  # Use display format for text
                style='options',
                duration=options_display_time
            ).set_start(riddle_duration)
            
            timer = self.create_timer(countdown_duration).set_start(
                riddle_duration + options_duration
            )
            
            # Position answer at center and fact at bottom with proper timing
            answer_text = create_text_clip(
                f"Answer: {answer}",
                style='answer',
                duration=answer_display_time,
                position=('center', 'center')
            ).set_start(riddle_duration + options_duration + countdown_total)
            
            fact_text = create_text_clip(
                fact,
                style='fact',
                duration=answer_display_time,
                position=('center', 0.85)
            ).set_start(riddle_duration + options_duration + countdown_total)
            
            # Create audio compositions with smart timing
            audio_clips = []
            
            # Add riddle voice-over at start with fade out
            if riddle_vo:
                riddle_vo = riddle_vo.audio_fadeout(0.3)  # Smooth fade out
                audio_clips.append(riddle_vo)
            
            # Add options voice-over after natural break with fades
            if options_vo:
                options_vo = options_vo.audio_fadein(0.2).audio_fadeout(0.3)  # Smooth transitions
                audio_clips.append(options_vo.set_start(riddle_duration))
            
            # Add countdown audio
            audio_clips.append(countdown_audio.set_start(
                riddle_duration + options_duration
            ))
            
            # Add answer sound effect
            audio_clips.append(answer_sound.set_start(
                riddle_duration + options_duration + countdown_total
            ))
            
            # Add answer voice-over with fade in
            if answer_vo:
                answer_vo = answer_vo.audio_fadein(0.2)  # Smooth fade in
                audio_clips.append(answer_vo.set_start(
                    riddle_duration + options_duration + countdown_total + answer_sound_duration
                ))
            
            # Combine all audio with crossfade
            final_audio = CompositeAudioClip(audio_clips)
            
            # Create final composition
            return CompositeVideoClip([
                bg_video,
                riddle,
                options_clip,
                timer,
                answer_text,
                fact_text
            ]).set_audio(final_audio)
            
        except Exception as e:
            logger.error(f"Error creating riddle segment: {e}")
            return ColorClip(
                size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                color=VIDEO_SETTINGS['background_color'],
                duration=duration
            ).set_duration(duration)
    
    def create_intro(self) -> CompositeVideoClip:
        """
        Create the intro segment with hook text and voice-over.
        
        Returns:
            CompositeVideoClip of the intro segment
        """
        try:
            intro_text = "Get ready for some mind-bending geographic riddles! Only 1% can solve them all. Can you?"
            hook_text = "🌎 Only 1% Can Solve These\nGeographic Riddles! 🌍\nCan You?"
            
            # Add break after intro
            intro_break = 1.5  # 1.5 second break after intro
            total_duration = TIMING['intro_duration'] + intro_break
            
            # Create voice-over for intro with energetic voice
            intro_vo = self.create_voice_over(
                intro_text,
                "temp_intro_vo.mp3",
                voice=API['elevenlabs']['voices']['intro']
            )
            
            # Create background video for intro
            bg_video = self.pexels_manager.get_background_video(
                "world map globe",
                total_duration
            )
            if bg_video is None:
                bg_video = ColorClip(
                    size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                    color=VIDEO_SETTINGS['background_color']
                ).set_duration(total_duration)
            
            # Create hook text with new styling
            hook = create_text_clip(
                hook_text,
                style='hook',
                duration=TIMING['intro_duration']  # Original duration without break
            )
            
            # Add voice-over if available
            if intro_vo:
                hook = hook.set_audio(intro_vo)
            
            return CompositeVideoClip([bg_video, hook]).set_duration(total_duration)
            
        except Exception as e:
            logger.error(f"Error creating intro: {e}")
            return ColorClip(
                size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                color=VIDEO_SETTINGS['background_color'],
                duration=total_duration
            ).set_duration(total_duration)
    
    def create_outro(self) -> CompositeVideoClip:
        """
        Create the outro segment with call-to-action and voice-over.
        
        Returns:
            CompositeVideoClip of the outro segment
        """
        try:
            outro_text = "How many did you get right? Drop your score in the comments and don't forget to follow for more brain-teasers!"
            display_text = "Thanks for watching! 👋\nComment your score below!\nFollow for more riddles!"
            
            # Create voice-over for outro with friendly voice
            outro_vo = self.create_voice_over(
                outro_text,
                "temp_outro_vo.mp3",
                voice=API['elevenlabs']['voices']['outro']
            )
            
            # Create background video for outro
            bg_video = self.pexels_manager.get_background_video(
                "world celebration",
                TIMING['outro_duration']
            )
            if bg_video is None:
                bg_video = ColorClip(
                    size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                    color=VIDEO_SETTINGS['background_color']
                ).set_duration(TIMING['outro_duration'])
            
            # Create outro text with new styling
            outro = create_text_clip(
                display_text,
                style='outro',
                duration=TIMING['outro_duration']
            )
            
            # Add voice-over if available
            if outro_vo:
                outro = outro.set_audio(outro_vo)
            
            return CompositeVideoClip([bg_video, outro]).set_duration(TIMING['outro_duration'])
            
        except Exception as e:
            logger.error(f"Error creating outro: {e}")
            return ColorClip(
                size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                color=VIDEO_SETTINGS['background_color'],
                duration=TIMING['outro_duration']
            ).set_duration(TIMING['outro_duration'])
    
    def generate_video(self) -> VideoFileClip:
        """Generate the complete video by combining all segments."""
        try:
            clips = []
            
            # Create intro
            with ProgressBar(1, desc="Creating intro") as pbar:
                clips.append(self.create_intro())
                pbar.update()
            
            # Process riddles sequentially with progress bar
            with ProgressBar(len(RIDDLES), desc="Processing riddles") as pbar:
                for i, riddle in enumerate(RIDDLES, 1):  # Start counting from 1
                    segment = self.create_riddle_segment(
                        riddle_text=riddle["riddle"],
                        options=riddle["options"],
                        answer=riddle["answer"],
                        fact=riddle["fact"],
                        question_number=i  # Pass the question number
                    )
                    clips.append(segment)
                    pbar.update()
            
            # Create outro
            with ProgressBar(1, desc="Creating outro") as pbar:
                clips.append(self.create_outro())
                pbar.update()
            
            # Combine all clips
            with ProgressBar(1, desc="Combining segments") as pbar:
                final_video = concatenate_videoclips(clips, method="compose")
                pbar.update()
            
            # Clean up temporary files
            with ProgressBar(1, desc="Cleaning up") as pbar:
                temp_files = [f for f in Path('.').glob('temp_*.mp3')]
                for file in temp_files:
                    try:
                        os.remove(file)
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file {file}: {e}")
                pbar.update()
            
            return final_video
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return ColorClip(
                size=(VIDEO_SETTINGS['width'], VIDEO_SETTINGS['height']),
                color=VIDEO_SETTINGS['background_color'],
                duration=60
            ).set_duration(60)

class ProgressBarLogger:
    """Custom logger for MoviePy that displays a progress bar."""
    
    def __init__(self, total_duration: float):
        self.progress_bar = ProgressBar(100, desc="Saving video")  # Use percentage
        self.total_duration = total_duration
        self.last_t = 0
        
    def __call__(self, *args, **kwargs):
        """Update progress bar based on current time."""
        # Handle both positional and keyword arguments
        t = args[0] if args else kwargs.get('t', 0)
        
        percentage = int((t / self.total_duration) * 100)
        if percentage > self.last_t:  # Only update if progress has changed
            # Calculate how many steps to update
            steps = percentage - self.last_t
            self.progress_bar.update(steps)
            self.last_t = percentage
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.last_t < 100:  # Ensure we reach 100%
            self.progress_bar.update(100 - self.last_t)

def calculate_total_duration() -> float:
    """Calculate the total duration of the video."""
    intro_duration = TIMING['intro_duration']
    riddle_duration = TIMING['riddle_duration'] * len(RIDDLES)
    outro_duration = TIMING['outro_duration']
    total_duration = intro_duration + riddle_duration + outro_duration
    return total_duration

def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def main() -> None:
    """Main function to create and save the geographic riddles video."""
    try:
        # Check environment variables
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        if not os.getenv('PEXELS_API_KEY'):
            raise ValueError("PEXELS_API_KEY environment variable is not set")
        
        # Calculate and display total duration
        total_duration = calculate_total_duration()
        formatted_duration = format_duration(total_duration)
        logger.info(f"Estimated video duration: {formatted_duration}")
        
        # Create output directory
        output_dir = Path(OUTPUT['directory'])
        output_dir.mkdir(exist_ok=True)
        
        # Initialize and generate video
        logger.info("Initializing RiddleVideo...")
        riddle_video = RiddleVideo()
        
        logger.info("Generating video...")
        final_video = riddle_video.generate_video()
        
        # Verify actual duration
        actual_duration = format_duration(final_video.duration)
        logger.info(f"Actual video duration: {actual_duration}")
        
        # Save video
        output_path = output_dir / OUTPUT['filename']
        logger.info(f"Saving video to {output_path}...")
        
        # Save video with optimized settings for M1 Pro
        final_video.write_videofile(
            str(output_path),
            fps=VIDEO_SETTINGS['fps'],
            codec=OUTPUT['video_codec'],
            audio=True,
            audio_codec=OUTPUT['audio_codec'],
            audio_bufsize=OUTPUT['audio_bufsize'],
            bitrate=OUTPUT['bitrate'],
            preset=OUTPUT['preset'],
            threads=PARALLEL['max_workers'],
            verbose=False,
            logger='bar',
            ffmpeg_params=OUTPUT['ffmpeg_params']
        )
        
        logger.info("Video generation complete!")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 