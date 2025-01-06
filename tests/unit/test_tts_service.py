"""Unit tests for TTS service"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from services.tts_service import TTSService
from config.exceptions import TTSError

@pytest.fixture
def tts_service():
    """Create TTS service instance"""
    return TTSService()

def test_init(tts_service):
    """Test TTS service initialization"""
    assert tts_service.voice_id == "Adam"
    assert tts_service.base_url == "https://api.elevenlabs.io/v1"

def test_generate_speech_cached(tts_service, tmp_path):
    """Test generating speech when cached"""
    # Create mock cached file
    cache_key = str(hash("test text"))
    cached_path = tmp_path / cache_key
    cached_path.write_text("test audio content")
    
    # Mock cache manager to return cached path
    tts_service.cache_manager.get = MagicMock(return_value=cached_path)
    
    result = tts_service.generate_speech("test text")
    assert result == cached_path
    assert result.read_text() == "test audio content"

@patch('requests.post')
def test_generate_speech_api_call(mock_post, tts_service):
    """Test generating speech via API call"""
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"test audio content"
    mock_post.return_value = mock_response
    
    # Mock cache miss
    tts_service.cache_manager.get = MagicMock(return_value=None)
    
    # Mock cache put
    output_path = Path("test_output.mp3")
    tts_service.cache_manager.put = MagicMock(return_value=output_path)
    
    result = tts_service.generate_speech("test text")
    assert result == output_path
    
    # Verify API call
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert kwargs["json"]["text"] == "test text"

@patch('requests.post')
def test_generate_speech_api_error(mock_post, tts_service):
    """Test handling API errors"""
    # Mock failed API response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "API error"
    mock_post.return_value = mock_response
    
    # Mock cache miss
    tts_service.cache_manager.get = MagicMock(return_value=None)
    
    with pytest.raises(TTSError) as exc_info:
        tts_service.generate_speech("test text")
    
    assert "API error" in str(exc_info.value) 