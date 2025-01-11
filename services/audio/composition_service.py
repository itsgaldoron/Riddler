import logging
from typing import Dict, List
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_audioclips
from config.exceptions import AudioCompositionError
from services.audio.base import AudioCompositionServiceBase
from utils.logger import log

class AudioCompositionService(AudioCompositionServiceBase):
    def __init__(self, config: Dict = None, logger: logging.Logger = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        self.background_music_volume = self.config.get("audio", {}).get("background_volume", 0.1)
        self.voice_volume = self.config.get("audio", {}).get("voice_volume", 1.0)
        self.sound_effects_volume = self.config.get("audio", {}).get("sound_effects_volume", 0.7)
        
        # Sound effects paths
        self.countdown_sound = "assets/audio/countdown.mp3"
        self.reveal_sound = "assets/audio/reveal.mp3"

    def create_audio_composition(
        self,
        segments: List[Dict],
        timings: Dict[str, float]
    ) -> CompositeAudioClip:
        try:
            # Create audio clips for each segment
            audio_clips = []
            current_time = 0
            
            for segment in segments:
                segment_id = segment.get("id")
                segment_type = segment.get("type", "")
                if not segment_id or segment_id not in timings:
                    continue
                
                # Get segment duration
                duration = timings[segment_id]
                
                # Handle voice audio if present
                voice_path = segment.get("voice_path")
                if voice_path:
                    voice_clip = AudioFileClip(voice_path)
                    voice_clip = voice_clip.set_start(current_time)
                    voice_clip = voice_clip.volumex(self.voice_volume)
                    audio_clips.append(voice_clip)
                
                # Add countdown sound for thinking segments
                if segment_type == "thinking":
                    countdown_clip = AudioFileClip(self.countdown_sound)
                    countdown_clip = countdown_clip.set_start(current_time)
                    countdown_clip = countdown_clip.volumex(self.sound_effects_volume)
                    audio_clips.append(countdown_clip)
                    
                    # Add reveal sound right after countdown ends
                    reveal_clip = AudioFileClip(self.reveal_sound)
                    reveal_clip = reveal_clip.set_start(current_time + countdown_clip.duration)
                    reveal_clip = reveal_clip.volumex(self.sound_effects_volume)
                    audio_clips.append(reveal_clip)
                
                # Handle background music if present
                bg_music_path = segment.get("background_music")
                if bg_music_path:
                    bg_clip = AudioFileClip(bg_music_path)
                    
                    # Loop background music if needed
                    if bg_clip.duration < duration:
                        n_loops = int(duration / bg_clip.duration) + 1
                        bg_clip = bg_clip.loop(n=n_loops)
                    
                    # Trim to exact duration and set volume
                    bg_clip = bg_clip.subclip(0, duration)
                    bg_clip = bg_clip.set_start(current_time)
                    bg_clip = bg_clip.volumex(self.background_music_volume)
                    audio_clips.append(bg_clip)
                
                current_time += duration
            
            # Combine all audio clips
            if not audio_clips:
                self.logger.warning("No audio clips to compose")
                return CompositeAudioClip([])
            
            return CompositeAudioClip(audio_clips)
            
        except Exception as e:
            self.logger.error(f"Failed to create audio composition: {str(e)}")
            raise AudioCompositionError(f"Failed to create audio composition: {str(e)}")
