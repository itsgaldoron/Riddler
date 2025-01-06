"""Audio asset generator for TikTok riddle videos"""

import os
import numpy as np
from pathlib import Path
from typing import Optional
import soundfile as sf
import librosa
import sounddevice as sd
from scipy import signal

class AudioGenerator:
    """Generates audio assets for TikTok riddle videos"""
    
    def __init__(self, output_dir: str = "assets/audio"):
        """Initialize audio generator
        
        Args:
            output_dir: Directory to save generated audio files
        """
        self.output_dir = Path(output_dir)
        self.sample_rate = 44100  # CD quality
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_hook_sound(
        self,
        duration: float = 3.0,
        fade_in: float = 0.5,
        fade_out: float = 0.5
    ) -> Path:
        """Generate dramatic hook sound effect
        
        Args:
            duration: Sound duration in seconds
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Path to generated audio file
        """
        # Generate dramatic rising tone
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        freq = 200 + 400 * np.exp(t / duration)  # Exponential frequency rise
        tone = np.sin(2 * np.pi * freq * t)
        
        # Add harmonics
        tone += 0.5 * np.sin(4 * np.pi * freq * t)
        tone += 0.25 * np.sin(6 * np.pi * freq * t)
        
        # Add reverb
        tone = self._add_reverb(tone)
        
        # Normalize
        tone = tone / np.max(np.abs(tone))
        
        # Apply fade in/out
        tone = self._apply_fade(tone, fade_in, fade_out)
        
        # Save to file
        output_path = self.output_dir / "hook.mp3"
        sf.write(str(output_path), tone, self.sample_rate)
        
        return output_path
        
    def generate_reveal_sound(
        self,
        duration: float = 1.0,
        fade_out: float = 0.3
    ) -> Path:
        """Generate reveal sound effect
        
        Args:
            duration: Sound duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Path to generated audio file
        """
        # Generate bright chord
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Major chord frequencies
        freqs = [523.25, 659.25, 783.99]  # C5, E5, G5
        chord = np.zeros_like(t)
        
        for freq in freqs:
            chord += np.sin(2 * np.pi * freq * t)
        
        # Add shimmer effect
        shimmer = np.sin(2 * np.pi * 20 * t)  # 20 Hz tremolo
        chord *= (1 + 0.2 * shimmer)
        
        # Add reverb
        chord = self._add_reverb(chord)
        
        # Normalize
        chord = chord / np.max(np.abs(chord))
        
        # Apply fade out
        chord = self._apply_fade(chord, fade_in=0, fade_out=fade_out)
        
        # Save to file
        output_path = self.output_dir / "reveal.mp3"
        sf.write(str(output_path), chord, self.sample_rate)
        
        return output_path
        
    def generate_countdown_sound(
        self,
        duration: float = 1.0,
        fade_out: float = 0.1
    ) -> Path:
        """Generate countdown beep sound
        
        Args:
            duration: Sound duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Path to generated audio file
        """
        # Generate beep tone
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        freq = 1000  # 1 kHz beep
        tone = np.sin(2 * np.pi * freq * t)
        
        # Add slight pitch drop
        freq_mod = 1 - 0.1 * (t / duration)
        tone *= np.sin(2 * np.pi * freq * t * freq_mod)
        
        # Normalize
        tone = tone / np.max(np.abs(tone))
        
        # Apply fade out
        tone = self._apply_fade(tone, fade_in=0, fade_out=fade_out)
        
        # Save to file
        output_path = self.output_dir / "countdown.mp3"
        sf.write(str(output_path), tone, self.sample_rate)
        
        return output_path
        
    def generate_celebration_sound(
        self,
        duration: float = 2.0,
        fade_out: float = 0.5
    ) -> Path:
        """Generate celebration sound effect
        
        Args:
            duration: Sound duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Path to generated audio file
        """
        # Generate ascending arpeggio
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Major scale frequencies
        freqs = [523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 987.77, 1046.50]
        
        # Create ascending pattern
        sound = np.zeros_like(t)
        step_duration = duration / len(freqs)
        
        for i, freq in enumerate(freqs):
            start = int((i * step_duration) * self.sample_rate)
            end = int(((i + 1) * step_duration) * self.sample_rate)
            t_segment = t[start:end]
            sound[start:end] = np.sin(2 * np.pi * freq * t_segment)
        
        # Add sparkle effect
        sparkle = np.random.rand(len(t)) * np.sin(2 * np.pi * 5000 * t)
        sound += 0.2 * sparkle
        
        # Add reverb
        sound = self._add_reverb(sound)
        
        # Normalize
        sound = sound / np.max(np.abs(sound))
        
        # Apply fade out
        sound = self._apply_fade(sound, fade_in=0, fade_out=fade_out)
        
        # Save to file
        output_path = self.output_dir / "celebration.mp3"
        sf.write(str(output_path), sound, self.sample_rate)
        
        return output_path
        
    def generate_background_music(
        self,
        duration: float = 30.0,
        fade_in: float = 1.0,
        fade_out: float = 1.0
    ) -> Path:
        """Generate ambient background music
        
        Args:
            duration: Music duration in seconds
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Path to generated audio file
        """
        # Generate ambient pad sound
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Base frequencies for ambient chord
        freqs = [65.41, 98.00, 130.81]  # C2, G2, C3
        
        # Create layered pad sound
        pad = np.zeros_like(t)
        
        for freq in freqs:
            # Main tone
            pad += np.sin(2 * np.pi * freq * t)
            # Detuned layers for thickness
            pad += 0.5 * np.sin(2 * np.pi * (freq * 1.001) * t)
            pad += 0.5 * np.sin(2 * np.pi * (freq * 0.999) * t)
        
        # Add slow modulation
        mod = 1 + 0.1 * np.sin(2 * np.pi * 0.1 * t)  # 0.1 Hz modulation
        pad *= mod
        
        # Add reverb
        pad = self._add_reverb(pad)
        
        # Normalize
        pad = pad / np.max(np.abs(pad))
        
        # Apply fade in/out
        pad = self._apply_fade(pad, fade_in, fade_out)
        
        # Save to file
        output_path = self.output_dir / "background.mp3"
        sf.write(str(output_path), pad, self.sample_rate)
        
        return output_path
        
    def _add_reverb(
        self,
        audio: np.ndarray,
        room_size: float = 0.8,
        damping: float = 0.5
    ) -> np.ndarray:
        """Add reverb effect to audio
        
        Args:
            audio: Input audio array
            room_size: Reverb room size (0-1)
            damping: Reverb damping factor (0-1)
            
        Returns:
            Audio with reverb effect
        """
        # Create impulse response
        n_samples = int(room_size * self.sample_rate)
        impulse = np.exp(-damping * np.arange(n_samples) / self.sample_rate)
        impulse = impulse * np.random.randn(n_samples)
        
        # Apply convolution reverb
        reverb = signal.convolve(audio, impulse, mode='full')[:len(audio)]
        
        # Mix with dry signal
        return 0.7 * audio + 0.3 * reverb
        
    def _apply_fade(
        self,
        audio: np.ndarray,
        fade_in: float,
        fade_out: float
    ) -> np.ndarray:
        """Apply fade in/out to audio
        
        Args:
            audio: Input audio array
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Audio with fades applied
        """
        samples = len(audio)
        fade_in_samples = int(fade_in * self.sample_rate)
        fade_out_samples = int(fade_out * self.sample_rate)
        
        # Create fade curves
        fade_in_curve = np.linspace(0, 1, fade_in_samples)
        fade_out_curve = np.linspace(1, 0, fade_out_samples)
        
        # Apply fades
        audio[:fade_in_samples] *= fade_in_curve
        audio[-fade_out_samples:] *= fade_out_curve
        
        return audio

def main():
    """Generate all audio assets"""
    generator = AudioGenerator()
    
    # Generate all sound effects
    generator.generate_hook_sound()
    generator.generate_reveal_sound()
    generator.generate_countdown_sound()
    generator.generate_celebration_sound()
    generator.generate_background_music()
    
if __name__ == "__main__":
    main() 