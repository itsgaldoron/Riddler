"""Global constants for the Riddler application"""

# Cache settings
MAX_CACHE_SIZE = 1_000_000_000  # 1GB
VIDEO_CACHE_SIZE = 5_000_000_000  # 5GB
CLEANUP_THRESHOLD = 0.9

# Video settings
DEFAULT_VIDEO_WIDTH = 3840
DEFAULT_VIDEO_HEIGHT = 2160
DEFAULT_FPS = 30
MIN_VIDEO_DURATION = 15
MAX_VIDEO_DURATION = 60

# TikTok optimization
TIKTOK_ASPECT_RATIO = "9:16"
TARGET_DURATION = 27
HOOK_DURATION = 3
END_SCREEN_DURATION = 2

# Audio settings
DEFAULT_VOICE_ID = "Adam"
DEFAULT_STABILITY = 0.71
DEFAULT_SIMILARITY_BOOST = 0.75
BACKGROUND_MUSIC_VOLUME = 0.1
VOICE_VOLUME = 1.0

# Categories
RIDDLE_CATEGORIES = [
    "geography",
    "math",
    "physics",
    "history",
    "logic",
    "wordplay"
]

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

# API endpoints
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
PEXELS_BASE_URL = "https://api.pexels.com/videos"

# Environment variables
ENV_PEXELS_API_KEY = "RIDDLER_PEXELS_API_KEY"
ENV_ELEVENLABS_API_KEY = "RIDDLER_ELEVENLABS_API_KEY"
ENV_OPENAI_API_KEY = "RIDDLER_OPENAI_API_KEY" 