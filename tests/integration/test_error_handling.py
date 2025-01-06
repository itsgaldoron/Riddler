"""Integration tests for error handling"""

import pytest
from pathlib import Path
from unittest.mock import patch
from core.riddler import Riddler
from services.tts_service import TTSService
from services.video_service import VideoService
from config.exceptions import (
    RiddlerException,
    ConfigurationError,
    TTSError,
    VideoError,
    CacheError
)

@pytest.mark.integration
def test_missing_api_keys(monkeypatch):
    """Test handling missing API keys"""
    # Remove all API keys
    monkeypatch.delenv("RIDDLER_PEXELS_API_KEY", raising=False)
    monkeypatch.delenv("RIDDLER_ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("RIDDLER_OPENAI_API_KEY", raising=False)
    
    with pytest.raises(ConfigurationError) as exc_info:
        Riddler()
    assert "API key not found" in str(exc_info.value)

@pytest.mark.integration
def test_invalid_config_file(tmp_path):
    """Test handling invalid configuration file"""
    # Create invalid config file
    config_path = tmp_path / "config.json"
    config_path.write_text("invalid json")
    
    with pytest.raises(ConfigurationError) as exc_info:
        Riddler()
    assert "Invalid configuration format" in str(exc_info.value)

@pytest.mark.integration
def test_cache_directory_permissions(temp_cache_dir):
    """Test handling cache directory permission errors"""
    # Remove write permissions
    temp_cache_dir.chmod(0o444)
    
    service = TTSService()
    with pytest.raises(CacheError) as exc_info:
        service.generate_speech("Test message")
    assert "Permission denied" in str(exc_info.value)

@pytest.mark.integration
def test_network_errors():
    """Test handling network errors"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError("Network error")
        
        service = TTSService()
        with pytest.raises(TTSError) as exc_info:
            service.generate_speech("Test message")
        assert "Network error" in str(exc_info.value)

@pytest.mark.integration
def test_invalid_video_format(temp_cache_dir):
    """Test handling invalid video format"""
    # Create invalid video file
    invalid_video = temp_cache_dir / "invalid.mp4"
    invalid_video.write_text("not a video")
    
    service = VideoService()
    service.cache_manager.get = lambda _: invalid_video
    
    with pytest.raises(VideoError) as exc_info:
        service.get_video("geography")
    assert "Invalid video format" in str(exc_info.value)

@pytest.mark.integration
def test_concurrent_cache_access(temp_cache_dir):
    """Test handling concurrent cache access"""
    import threading
    
    service = TTSService()
    errors = []
    
    def generate_speech():
        try:
            service.generate_speech(f"Test message {threading.get_ident()}")
        except Exception as e:
            errors.append(e)
    
    # Create multiple threads
    threads = [threading.Thread(target=generate_speech) for _ in range(5)]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify no errors occurred
    assert not errors

@pytest.mark.integration
def test_full_error_chain():
    """Test error propagation through the entire chain"""
    riddler = Riddler()
    
    # Mock services to raise errors
    riddler.tts_service.generate_speech = lambda _: exec('raise TTSError("TTS failed")')
    riddler.video_service.get_video = lambda _: exec('raise VideoError("Video failed")')
    
    with pytest.raises(RiddlerException) as exc_info:
        riddler.create_video({
            "riddle": "Test riddle",
            "answer": "Test answer",
            "explanation": "Test explanation",
            "fun_fact": "Test fun fact"
        }, "geography")
    
    error_msg = str(exc_info.value)
    assert "TTS failed" in error_msg or "Video failed" in error_msg

@pytest.mark.integration
def test_cleanup_after_error(temp_cache_dir):
    """Test cleanup after error occurs"""
    service = TTSService()
    
    # Create some files
    for i in range(3):
        (temp_cache_dir / f"test_{i}.mp3").touch()
    
    try:
        # Force an error
        service.generate_speech("Test message")
    except:
        pass
    
    # Verify temporary files were cleaned up
    temp_files = list(temp_cache_dir.glob("*.tmp"))
    assert not temp_files 