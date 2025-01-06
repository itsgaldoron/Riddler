"""Unit tests for validators module"""

import pytest
from utils.validators import (
    validate_category,
    validate_difficulty,
    validate_duration,
    validate_api_key
)

def test_validate_category_valid():
    """Test validating valid categories"""
    valid_categories = ["geography", "math", "physics", "history", "logic", "wordplay"]
    for category in valid_categories:
        assert validate_category(category) is True

def test_validate_category_invalid():
    """Test validating invalid categories"""
    invalid_categories = ["", "invalid", "123", None]
    for category in invalid_categories:
        with pytest.raises(ValueError) as exc_info:
            validate_category(category)
        assert "Invalid category" in str(exc_info.value)

def test_validate_difficulty_valid():
    """Test validating valid difficulty levels"""
    valid_difficulties = ["easy", "medium", "hard"]
    for difficulty in valid_difficulties:
        assert validate_difficulty(difficulty) is True

def test_validate_difficulty_invalid():
    """Test validating invalid difficulty levels"""
    invalid_difficulties = ["", "invalid", "expert", None]
    for difficulty in invalid_difficulties:
        with pytest.raises(ValueError) as exc_info:
            validate_difficulty(difficulty)
        assert "Invalid difficulty" in str(exc_info.value)

def test_validate_duration_valid():
    """Test validating valid video durations"""
    valid_durations = [30, 45, 60]
    for duration in valid_durations:
        assert validate_duration(duration) is True

def test_validate_duration_invalid():
    """Test validating invalid video durations"""
    invalid_durations = [-1, 0, 15, 120, "30"]
    for duration in invalid_durations:
        with pytest.raises(ValueError) as exc_info:
            validate_duration(duration)
        assert "Invalid duration" in str(exc_info.value)

def test_validate_api_key_valid():
    """Test validating valid API keys"""
    valid_keys = {
        "RIDDLER_PEXELS_API_KEY": "test_pexels_key",
        "RIDDLER_ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "RIDDLER_OPENAI_API_KEY": "test_openai_key"
    }
    for key, value in valid_keys.items():
        assert validate_api_key(key, value) is True

def test_validate_api_key_invalid():
    """Test validating invalid API keys"""
    invalid_keys = {
        "INVALID_KEY": "value",
        "RIDDLER_PEXELS_API_KEY": "",
        "RIDDLER_ELEVENLABS_API_KEY": None
    }
    for key, value in invalid_keys.items():
        with pytest.raises(ValueError) as exc_info:
            validate_api_key(key, value)
        assert "Invalid API key" in str(exc_info.value) 