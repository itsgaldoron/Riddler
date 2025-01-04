from pathlib import Path
from typing import Tuple
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Load all API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Video settings
VIDEO_SETTINGS = {
    'width': 1080,  # TikTok recommended width
    'height': 1920,  # TikTok recommended height
    'fps': 30,
    'font': 'Helvetica-Bold',  # Use a bold font for better visibility
    'text_color': 'white',
    'background_color': (0, 0, 0),  # Black background
    'text_stroke_color': 'black',  # Text stroke for better visibility
    'text_stroke_width': 2,  # Stroke width for text
}

# Timing settings (in seconds)
TIMING = {
    'intro_duration': 5,
    'riddle_duration': 5.625,  # 45 seconds total / 8 riddles
    'outro_duration': 5,
    'timer_duration': 3,
}

# Cache settings
CACHE = {
    'pexels_dir': 'pexels_cache',
    'pexels_mapping': 'pexels_cache/video_mapping.json',
    'voice_dir': 'voice_cache',
    'voice_mapping': 'voice_cache/voice_mapping.json',
}

# API settings
API = {
    'pexels': {
        'api_key': PEXELS_API_KEY,
        'timeout': 10,
        'download_timeout': 30,
        'chunk_size': 8192,
    },
    'elevenlabs': {
        'api_key': ELEVENLABS_API_KEY,
        'voices': {
            'riddle': 'Adam',      # Clear and authoritative
            'options': 'Adam',      # Use Adam for all voices
            'answer': 'Adam',       # Use Adam for all voices
            'intro': 'Adam',        # Use Adam for all voices
            'outro': 'Adam',        # Use Adam for all voices
        }
    },
    'openai': {
        'api_key': OPENAI_API_KEY,
        'tts_model': 'tts-1',
        'tts_speed': 1.3,  # Increase speech speed
        'voices': {
            'riddle': 'onyx',      # Clear and authoritative
            'options': 'nova',      # Friendly and engaging
            'answer': 'shimmer',    # Energetic and exciting
            'intro': 'shimmer',     # Energetic intro
            'outro': 'nova',        # Friendly outro
        }
    }
}

# Output settings
OUTPUT = {
    'directory': 'output',
    'filename': 'geographic_riddles.mp4',
    'video_codec': 'libx264',
    'audio_codec': 'aac',
    'audio_bufsize': 2000,
    'bitrate': '8000k',  # High quality bitrate
    'preset': 'ultrafast',  # Fastest encoding preset
    'ffmpeg_params': [
        '-colorspace', 'bt709',
        '-color_primaries', 'bt709',
        '-color_trc', 'bt709',
        '-movflags', '+faststart',  # Enable fast start for web playback
        '-tune', 'zerolatency'  # Minimize encoding latency
    ]
}

# Parallel processing settings
PARALLEL = {
    'max_workers': 4,  # Number of parallel processes
    'chunk_size': 2,   # Number of riddles per chunk
}

# Asset files
ASSETS = {
    'countdown_sound': "countdown.wav",
    'correct_sound': "answer.wav",
}

# Text content
TEXT = {
    'intro': {
        'voice': "Get ready for some mind-bending geographic riddles! Only 1% can solve them all. Can you?",
        'display': "🌎 Only 1% Can Solve These\nGeographic Riddles! 🌍\nCan You?"
    },
    'outro': {
        'voice': "How many did you get right? Drop your score in the comments and don't forget to follow for more brain-teasers!",
        'display': "Thanks for watching! 👋\nComment your score below!\nFollow for more riddles!"
    }
}

# Font sizes
FONTS = {
    'hook': 120,      # Larger, more attention-grabbing size for intro hook
    'riddle': 90,     # Larger size for riddle text
    'options': 80,    # Larger size for multiple choice options
    'timer': 200,     # Much larger countdown timer
    'answer': 100,    # Larger size for answer reveal
    'fact': 70,       # Good size for fun facts
    'outro': 110,     # Larger size for call-to-action
}

# Progress bar settings
PROGRESS = {
    'width': 50,  # Progress bar width in characters
    'fill': '█',  # Progress bar fill character
    'empty': '░', # Progress bar empty character
    'format': '[{bar}] {percentage}% | {desc}'
}

# Text positioning (relative to screen height)
TEXT_POSITIONS = {
    'hook': ('center', 'center'),      # Center of screen
    'riddle': ('center', 'center'),    # Center of screen
    'options': ('center', 'center'),   # Center of screen
    'timer': ('center', 'center'),     # Center of screen
    'answer': ('center', 'center'),    # Center of screen
    'fact': ('center', 'center'),      # Center of screen
    'outro': ('center', 'center'),     # Center of screen
}

# Text styling
TEXT_STYLES = {
    'hook': {'stroke_color': 'black', 'stroke_width': 4},
    'riddle': {'stroke_color': 'black', 'stroke_width': 3},
    'options': {'stroke_color': 'black', 'stroke_width': 3},
    'timer': {'stroke_color': 'black', 'stroke_width': 5},
    'answer': {'stroke_color': 'black', 'stroke_width': 4},
    'fact': {'stroke_color': 'black', 'stroke_width': 3},
    'outro': {'stroke_color': 'black', 'stroke_width': 4},
} 