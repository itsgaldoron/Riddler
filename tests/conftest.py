"""Shared test fixtures"""

import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock
from core.riddler import Riddler
from services.tts_service import TTSService
from services.video_service import VideoService
from utils.cache import CacheManager
from .fixtures.test_data import (
    SAMPLE_RIDDLES,
    SAMPLE_API_RESPONSES,
    SAMPLE_CONFIG
)

@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config file"""
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(SAMPLE_CONFIG, f)
    return config_path

@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory"""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir

@pytest.fixture
def mock_tts_service():
    """Create mock TTS service"""
    service = MagicMock(spec=TTSService)
    service.generate_speech.return_value = Path("test_audio.mp3")
    return service

@pytest.fixture
def mock_video_service():
    """Create mock video service"""
    service = MagicMock(spec=VideoService)
    service.get_video.return_value = Path("test_video.mp4")
    return service

@pytest.fixture
def mock_cache_manager():
    """Create mock cache manager"""
    manager = MagicMock(spec=CacheManager)
    manager.get.return_value = None
    manager.put.return_value = Path("cached_file")
    return manager

@pytest.fixture
def riddler_with_mocks(mock_tts_service, mock_video_service):
    """Create Riddler instance with mock services"""
    riddler = Riddler()
    riddler.tts_service = mock_tts_service
    riddler.video_service = mock_video_service
    return riddler

@pytest.fixture
def sample_riddle_data():
    """Get sample riddle data"""
    return SAMPLE_RIDDLES["geography"]

@pytest.fixture
def sample_api_responses():
    """Get sample API responses"""
    return SAMPLE_API_RESPONSES

@pytest.fixture
def sample_config():
    """Get sample configuration"""
    return SAMPLE_CONFIG 