"""Service for generating and managing audio for TikTok videos."""

from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize, speedup
from pydub.generators import Sine
from utils.logger import log
from utils.cache import cache
from utils.helpers import (
    ensure_directory,
    generate_cache_key,
    format_timestamp,
    parse_timestamp
)
from config.exceptions import AudioError

class AudioService:
    """Service for generating and managing audio for TikTok videos."""
    
    def __init__(
        self,
        output_dir: str = "output/audio",
        cache_dir: str = "cache/audio",
        tts_provider: str = "google",
        default_voice: str = "en-US-Neural2-C",
        default_music_volume: float = 0.3,
        default_voice_volume: float = 1.0,
        default_sfx_volume: float = 0.7
    ):
        """Initialize audio service.
        
        Args:
            output_dir: Directory for final audio files
            cache_dir: Directory for cached audio files
            tts_provider: TTS provider to use
            default_voice: Default TTS voice
            default_music_volume: Default background music volume
            default_voice_volume: Default voice volume
            default_sfx_volume: Default sound effects volume
        """
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.tts_provider = tts_provider
        self.default_voice = default_voice
        self.default_music_volume = default_music_volume
        self.default_voice_volume = default_voice_volume
        self.default_sfx_volume = default_sfx_volume
        
        # Create directories
        ensure_directory(self.output_dir)
        ensure_directory(self.cache_dir)
        
    def generate_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        emphasis: Optional[List[str]] = None,
        output_name: Optional[str] = None
    ) -> Path:
        """Generate TTS audio from text.
        
        Args:
            text: Text to convert to speech
            voice: TTS voice to use
            speed: Speech speed multiplier
            pitch: Pitch adjustment in semitones
            emphasis: List of words to emphasize
            output_name: Optional custom output filename
            
        Returns:
            Path to generated audio file
        """
        try:
            # Generate cache key
            cache_key = generate_cache_key(
                "tts",
                text=text,
                voice=voice or self.default_voice,
                speed=speed,
                pitch=pitch,
                emphasis=emphasis
            )
            
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.mp3"
            if cached_path.exists():
                return cached_path
                
            # Generate TTS using provider
            if self.tts_provider == "google":
                audio = self._generate_google_tts(
                    text,
                    voice or self.default_voice,
                    emphasis
                )
            else:
                raise AudioError(f"Unsupported TTS provider: {self.tts_provider}")
                
            # Apply effects
            if speed != 1.0:
                audio = speedup(audio, speed)
                
            if pitch != 0.0:
                audio = self._adjust_pitch(audio, pitch)
                
            # Normalize audio
            audio = normalize(audio)
            
            # Save to cache
            audio.export(
                cached_path,
                format="mp3",
                parameters=["-q:a", "2"]  # High quality
            )
            
            log.info(
                "Generated TTS audio",
                extra={
                    "text": text,
                    "voice": voice or self.default_voice,
                    "output_path": str(cached_path)
                }
            )
            
            return cached_path
            
        except Exception as e:
            raise AudioError(f"Failed to generate TTS: {str(e)}")
            
    def _generate_google_tts(
        self,
        text: str,
        voice: str,
        emphasis: Optional[List[str]] = None
    ) -> AudioSegment:
        """Generate TTS using Google Cloud TTS.
        
        Args:
            text: Text to convert to speech
            voice: TTS voice to use
            emphasis: List of words to emphasize
            
        Returns:
            Generated audio segment
        """
        try:
            from google.cloud import texttospeech
            
            # Initialize client
            client = texttospeech.TextToSpeechClient()
            
            # Add SSML emphasis if needed
            if emphasis:
                # Escape special characters
                text = text.replace("&", "&amp;")
                text = text.replace("<", "&lt;")
                text = text.replace(">", "&gt;")
                
                # Add emphasis tags
                for word in emphasis:
                    text = text.replace(
                        word,
                        f'<emphasis level="strong">{word}</emphasis>'
                    )
                    
                # Wrap in SSML
                text = f"<speak>{text}</speak>"
                
                input_text = texttospeech.SynthesisInput(ssml=text)
            else:
                input_text = texttospeech.SynthesisInput(text=text)
                
            # Configure voice
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=voice[:5],
                name=voice
            )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Generate speech
            response = client.synthesize_speech(
                input=input_text,
                voice=voice_params,
                audio_config=audio_config
            )
            
            # Save temporary file
            temp_path = self.cache_dir / "temp-tts.mp3"
            with open(temp_path, "wb") as f:
                f.write(response.audio_content)
                
            # Load as AudioSegment
            return AudioSegment.from_mp3(temp_path)
            
        except Exception as e:
            raise AudioError(f"Failed to generate Google TTS: {str(e)}")
            
    def _adjust_pitch(
        self,
        audio: AudioSegment,
        semitones: float
    ) -> AudioSegment:
        """Adjust audio pitch by semitones.
        
        Args:
            audio: Audio segment to adjust
            semitones: Number of semitones to adjust by
            
        Returns:
            Pitch-adjusted audio segment
        """
        # Convert semitones to frequency multiplier
        freq_mult = 2 ** (semitones / 12)
        
        # Resample audio
        return audio._spawn(
            audio.raw_data,
            overrides={
                "frame_rate": int(audio.frame_rate * freq_mult)
            }
        ).set_frame_rate(audio.frame_rate)
        
    def create_background_music(
        self,
        duration: float,
        style: str = "dramatic",
        bpm: int = 120,
        key: str = "C",
        output_name: Optional[str] = None
    ) -> Path:
        """Create background music.
        
        Args:
            duration: Duration in seconds
            style: Music style
            bpm: Beats per minute
            key: Musical key
            output_name: Optional custom output filename
            
        Returns:
            Path to generated audio file
        """
        try:
            # Generate cache key
            cache_key = generate_cache_key(
                "music",
                duration=duration,
                style=style,
                bpm=bpm,
                key=key
            )
            
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.mp3"
            if cached_path.exists():
                return cached_path
                
            # Create base track
            audio = self._create_base_track(duration, bpm, key)
            
            # Add style-specific elements
            if style == "dramatic":
                audio = self._add_dramatic_elements(audio, bpm)
            elif style == "mysterious":
                audio = self._add_mysterious_elements(audio, bpm)
            elif style == "playful":
                audio = self._add_playful_elements(audio, bpm)
                
            # Normalize and fade
            audio = normalize(audio)
            audio = audio.fade_in(2000).fade_out(2000)
            
            # Save to cache
            audio.export(
                cached_path,
                format="mp3",
                parameters=["-q:a", "2"]
            )
            
            log.info(
                "Generated background music",
                extra={
                    "style": style,
                    "duration": duration,
                    "output_path": str(cached_path)
                }
            )
            
            return cached_path
            
        except Exception as e:
            raise AudioError(f"Failed to create background music: {str(e)}")
            
    def _create_base_track(
        self,
        duration: float,
        bpm: int,
        key: str
    ) -> AudioSegment:
        """Create base music track.
        
        Args:
            duration: Duration in seconds
            bpm: Beats per minute
            key: Musical key
            
        Returns:
            Base audio track
        """
        # Calculate frequencies for key
        root_freq = self._note_to_freq(key)
        chord_freqs = [
            root_freq,
            root_freq * 1.25,  # Major third
            root_freq * 1.5    # Perfect fifth
        ]
        
        # Create chord progression
        progression = []
        beat_duration = 60000 / bpm  # ms per beat
        
        for freq in chord_freqs:
            tone = Sine(freq).to_audio_segment(duration=beat_duration)
            progression.append(tone)
            
        # Combine and loop
        base = sum(progression)
        num_loops = int(duration * 1000 / base.duration_seconds)
        
        return base * num_loops
        
    def _note_to_freq(self, note: str) -> float:
        """Convert musical note to frequency.
        
        Args:
            note: Note name (e.g. "C4")
            
        Returns:
            Frequency in Hz
        """
        # Note to semitone mapping
        notes = {
            "C": 0, "C#": 1, "D": 2, "D#": 3,
            "E": 4, "F": 5, "F#": 6, "G": 7,
            "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        
        # Parse note and octave
        if len(note) == 1:
            note_name = note
            octave = 4
        else:
            note_name = note[0]
            octave = int(note[1])
            
        # Calculate frequency
        n = notes[note_name]
        freq = 440 * (2 ** ((n - 9) / 12)) * (2 ** (octave - 4))
        
        return freq
        
    def _add_dramatic_elements(
        self,
        base: AudioSegment,
        bpm: int
    ) -> AudioSegment:
        """Add dramatic elements to base track.
        
        Args:
            base: Base audio track
            bpm: Beats per minute
            
        Returns:
            Enhanced audio track
        """
        # Add low drone
        drone = Sine(55).to_audio_segment(duration=base.duration_seconds * 1000)
        drone = drone - 12  # Reduce volume
        
        # Add rhythmic elements
        beat_ms = 60000 / bpm
        kick = self._create_kick_drum(beat_ms)
        
        # Pattern: X...X...X...X... (X = kick)
        pattern = []
        for _ in range(int(base.duration_seconds * 1000 / (beat_ms * 4))):
            pattern.append(kick)
            pattern.extend([AudioSegment.silent(duration=beat_ms)] * 3)
            
        rhythm = sum(pattern)
        
        # Combine elements
        return base.overlay(drone).overlay(rhythm)
        
    def _add_mysterious_elements(
        self,
        base: AudioSegment,
        bpm: int
    ) -> AudioSegment:
        """Add mysterious elements to base track.
        
        Args:
            base: Base audio track
            bpm: Beats per minute
            
        Returns:
            Enhanced audio track
        """
        # Add shimmer effect
        shimmer = Sine(1200).to_audio_segment(duration=base.duration_seconds * 1000)
        shimmer = shimmer - 24  # Reduce volume
        shimmer = shimmer.fade_in(1000).fade_out(1000)
        
        # Add reverb
        reverb = base.reverse()
        reverb = reverb - 18  # Reduce volume
        reverb = reverb.fade_out(2000)
        
        # Combine elements
        return base.overlay(shimmer).overlay(reverb)
        
    def _add_playful_elements(
        self,
        base: AudioSegment,
        bpm: int
    ) -> AudioSegment:
        """Add playful elements to base track.
        
        Args:
            base: Base audio track
            bpm: Beats per minute
            
        Returns:
            Enhanced audio track
        """
        # Add bouncy melody
        melody_freqs = [523.25, 587.33, 659.25, 783.99]  # C5, D5, E5, G5
        beat_ms = 60000 / bpm
        
        melody = []
        for freq in melody_freqs:
            tone = Sine(freq).to_audio_segment(duration=beat_ms)
            tone = tone - 12  # Reduce volume
            melody.append(tone)
            melody.append(AudioSegment.silent(duration=beat_ms))
            
        melody_track = sum(melody) * int(base.duration_seconds * 1000 / (len(melody) * beat_ms))
        
        # Combine elements
        return base.overlay(melody_track)
        
    def _create_kick_drum(self, duration_ms: float) -> AudioSegment:
        """Create kick drum sound.
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            Kick drum audio
        """
        # Start with 150 Hz sine wave
        kick = Sine(150).to_audio_segment(duration=duration_ms)
        
        # Add pitch envelope
        env_duration = min(duration_ms, 100)
        num_steps = 10
        step_duration = env_duration / num_steps
        
        envelope = []
        for i in range(num_steps):
            freq = 150 * (1 - i/num_steps)
            tone = Sine(freq).to_audio_segment(duration=step_duration)
            envelope.append(tone)
            
        kick = sum(envelope)
        
        # Add amplitude envelope
        return kick.fade_out(env_duration)
        
    def create_sound_effect(
        self,
        effect: str,
        duration: float = 1.0,
        pitch: float = 0.0,
        output_name: Optional[str] = None
    ) -> Path:
        """Create sound effect.
        
        Args:
            effect: Effect type
            duration: Duration in seconds
            pitch: Pitch adjustment in semitones
            output_name: Optional custom output filename
            
        Returns:
            Path to generated audio file
        """
        try:
            # Generate cache key
            cache_key = generate_cache_key(
                "sfx",
                effect=effect,
                duration=duration,
                pitch=pitch
            )
            
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.mp3"
            if cached_path.exists():
                return cached_path
                
            # Generate effect
            if effect == "success":
                audio = self._create_success_effect(duration)
            elif effect == "reveal":
                audio = self._create_reveal_effect(duration)
            elif effect == "countdown":
                audio = self._create_countdown_effect(duration)
            else:
                raise AudioError(f"Unsupported effect type: {effect}")
                
            # Apply pitch adjustment
            if pitch != 0.0:
                audio = self._adjust_pitch(audio, pitch)
                
            # Normalize audio
            audio = normalize(audio)
            
            # Save to cache
            audio.export(
                cached_path,
                format="mp3",
                parameters=["-q:a", "2"]
            )
            
            log.info(
                "Generated sound effect",
                extra={
                    "effect": effect,
                    "duration": duration,
                    "output_path": str(cached_path)
                }
            )
            
            return cached_path
            
        except Exception as e:
            raise AudioError(f"Failed to create sound effect: {str(e)}")
            
    def _create_success_effect(self, duration: float) -> AudioSegment:
        """Create success sound effect.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Success effect audio
        """
        # Create ascending arpeggio
        freqs = [523.25, 659.25, 783.99]  # C5, E5, G5
        note_duration = duration / len(freqs) * 1000
        
        notes = []
        for freq in freqs:
            tone = Sine(freq).to_audio_segment(duration=note_duration)
            tone = tone.fade_in(20).fade_out(50)
            notes.append(tone)
            
        return sum(notes)
        
    def _create_reveal_effect(self, duration: float) -> AudioSegment:
        """Create reveal sound effect.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Reveal effect audio
        """
        # Create rising sweep
        start_freq = 200
        end_freq = 1000
        num_steps = 50
        step_duration = duration * 1000 / num_steps
        
        sweep = []
        for i in range(num_steps):
            freq = start_freq + (end_freq - start_freq) * (i / num_steps)
            tone = Sine(freq).to_audio_segment(duration=step_duration)
            sweep.append(tone)
            
        return sum(sweep).fade_in(100).fade_out(100)
        
    def _create_countdown_effect(self, duration: float) -> AudioSegment:
        """Create countdown sound effect.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Countdown effect audio
        """
        # Create descending beeps
        freqs = [880, 784, 698.46, 659.25]  # A5, G5, F5, E5
        note_duration = duration * 1000 / len(freqs)
        
        beeps = []
        for freq in freqs:
            tone = Sine(freq).to_audio_segment(duration=note_duration * 0.3)
            tone = tone.fade_in(10).fade_out(50)
            
            # Add silence
            beeps.append(tone)
            beeps.append(AudioSegment.silent(duration=note_duration * 0.7))
            
        return sum(beeps)
        
    def mix_audio(
        self,
        tracks: List[Union[Path, AudioSegment]],
        volumes: Optional[List[float]] = None,
        crossfade: Optional[float] = None,
        output_name: Optional[str] = None
    ) -> Path:
        """Mix multiple audio tracks.
        
        Args:
            tracks: List of audio tracks or file paths
            volumes: List of volume multipliers
            crossfade: Crossfade duration in seconds
            output_name: Optional custom output filename
            
        Returns:
            Path to mixed audio file
        """
        try:
            # Load tracks
            audio_segments = []
            for track in tracks:
                if isinstance(track, Path):
                    segment = AudioSegment.from_file(str(track))
                else:
                    segment = track
                audio_segments.append(segment)
                
            # Apply volumes
            if volumes:
                audio_segments = [
                    segment + (20 * np.log10(vol))
                    for segment, vol in zip(audio_segments, volumes)
                ]
                
            # Apply crossfade
            if crossfade:
                fade_ms = int(crossfade * 1000)
                for i in range(len(audio_segments) - 1):
                    audio_segments[i] = audio_segments[i].fade_out(fade_ms)
                    audio_segments[i+1] = audio_segments[i+1].fade_in(fade_ms)
                    
            # Mix tracks
            mixed = sum(audio_segments)
            
            # Generate output path
            if output_name:
                output_path = self.output_dir / f"{output_name}.mp3"
            else:
                cache_key = generate_cache_key("mix", tracks=tracks)
                output_path = self.output_dir / f"{cache_key}.mp3"
                
            # Export mixed audio
            mixed.export(
                output_path,
                format="mp3",
                parameters=["-q:a", "2"]
            )
            
            log.info(
                "Mixed audio tracks",
                extra={
                    "num_tracks": len(tracks),
                    "output_path": str(output_path)
                }
            )
            
            return output_path
            
        except Exception as e:
            raise AudioError(f"Failed to mix audio: {str(e)}")

# Initialize global audio service
audio_service = AudioService() 