"""Test fixtures and sample data"""

# Sample riddle data for different categories
SAMPLE_RIDDLES = {
    "geography": {
        "riddle": "What has cities, but no houses?",
        "answer": "A map",
        "explanation": "A map shows cities but doesn't contain actual houses",
        "fun_fact": "The oldest known map is from ancient Babylon"
    },
    "math": {
        "riddle": "What number has the same number of letters as its value?",
        "answer": "Four",
        "explanation": "The word 'four' has four letters",
        "fun_fact": "Four is the only number in English with this property"
    },
    "physics": {
        "riddle": "What can travel around the world while staying in a corner?",
        "answer": "A stamp",
        "explanation": "A stamp stays in the corner of an envelope while traveling",
        "fun_fact": "The first adhesive postage stamp was the Penny Black"
    }
}

# Sample API responses
SAMPLE_API_RESPONSES = {
    "openai": {
        "success": {
            "choices": [{
                "message": {
                    "content": """
                    {
                        "riddle": "What has cities, but no houses?",
                        "answer": "A map",
                        "explanation": "A map shows cities but doesn't contain actual houses",
                        "fun_fact": "The oldest known map is from ancient Babylon"
                    }
                    """
                }
            }]
        },
        "error": {
            "error": {
                "message": "API error"
            }
        }
    },
    "pexels": {
        "success": {
            "videos": [{
                "video_files": [{
                    "width": 3840,
                    "height": 2160,
                    "link": "https://example.com/video.mp4"
                }]
            }]
        },
        "error": {
            "error": "API error"
        }
    }
}

# Sample configuration data
SAMPLE_CONFIG = {
    "tts": {
        "provider": "elevenlabs",
        "voice_id": "test_voice",
        "model": "test_model",
        "stability": 0.5,
        "similarity_boost": 0.5
    },
    "video": {
        "pexels": {
            "categories": {
                "geography": ["world map globe", "world celebration"],
                "math": ["numbers calculation", "mathematics education"],
                "physics": ["science experiment", "physics demonstration"]
            }
        },
        "resolution": {
            "width": 1080,
            "height": 1920
        },
        "fps": 30
    },
    "cache": {
        "voice_dir": "cache/voice",
        "video_dir": "cache/video",
        "max_size_mb": 1000,
        "cleanup_threshold": 0.9
    }
}

# Sample error messages
ERROR_MESSAGES = {
    "config": {
        "missing_file": "config.json not found",
        "invalid_format": "Invalid configuration format",
        "missing_required": "Missing required configuration"
    },
    "api": {
        "openai": "OpenAI API error",
        "pexels": "Pexels API error",
        "elevenlabs": "ElevenLabs API error"
    },
    "validation": {
        "category": "Invalid category",
        "difficulty": "Invalid difficulty level",
        "duration": "Invalid video duration",
        "api_key": "Invalid API key"
    }
} 