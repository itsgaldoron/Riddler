"""Integration tests for TTS service"""

import pytest
from pathlib import Path
from services.tts_service import TTSService
from config.exceptions import TTSError

@pytest.mark.integration
def test_generate_speech_full_flow(temp_cache_dir):
    """Test complete speech generation flow"""
    service = TTSService()
    
    # Generate speech
    text = "This is a test of the text to speech service"
    result = service.generate_speech(text)
    
    # Verify result
    assert isinstance(result, Path)
    assert result.exists()
    assert result.suffix == ".mp3"
    assert result.stat().st_size > 0

@pytest.mark.integration
def test_generate_speech_caching(temp_cache_dir):
    """Test speech generation with caching"""
    service = TTSService()
    text = "Test caching functionality"
    
    # First generation
    result1 = service.generate_speech(text)
    modified_time1 = result1.stat().st_mtime
    
    # Second generation (should use cache)
    result2 = service.generate_speech(text)
    modified_time2 = result2.stat().st_mtime
    
    assert result1 == result2
    assert modified_time1 == modified_time2

@pytest.mark.integration
def test_generate_speech_different_texts(temp_cache_dir):
    """Test generating speech for different texts"""
    service = TTSService()
    texts = [
        "First test message",
        "Second test message",
        "Third test message"
    ]
    
    results = []
    for text in texts:
        result = service.generate_speech(text)
        assert result.exists()
        results.append(result)
    
    # Verify unique files generated
    assert len(set(results)) == len(texts)

@pytest.mark.integration
def test_generate_speech_invalid_api_key(temp_cache_dir, monkeypatch):
    """Test handling invalid API key"""
    monkeypatch.setenv("RIDDLER_ELEVENLABS_API_KEY", "invalid_key")
    
    service = TTSService()
    with pytest.raises(TTSError) as exc_info:
        service.generate_speech("Test message")
    assert "API error" in str(exc_info.value)

@pytest.mark.integration
def test_generate_speech_cache_cleanup(temp_cache_dir):
    """Test cache cleanup during speech generation"""
    service = TTSService()
    
    # Generate multiple files to trigger cleanup
    for i in range(10):
        text = f"Test message {i}"
        result = service.generate_speech(text)
        assert result.exists()
    
    # Verify cache size is maintained
    cache_size = sum(f.stat().st_size for f in Path(temp_cache_dir).glob("*"))
    assert cache_size <= service.cache_manager.max_size 