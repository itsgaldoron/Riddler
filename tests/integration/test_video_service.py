"""Integration tests for video service"""

import pytest
from pathlib import Path
from services.video_service import VideoService
from config.exceptions import VideoError

@pytest.mark.integration
def test_get_video_full_flow(temp_cache_dir):
    """Test complete video retrieval flow"""
    service = VideoService()
    
    # Get video for category
    result = service.get_video("geography")
    
    # Verify result
    assert isinstance(result, Path)
    assert result.exists()
    assert result.suffix == ".mp4"
    assert result.stat().st_size > 0

@pytest.mark.integration
def test_get_video_caching(temp_cache_dir):
    """Test video retrieval with caching"""
    service = VideoService()
    category = "geography"
    
    # First retrieval
    result1 = service.get_video(category)
    modified_time1 = result1.stat().st_mtime
    
    # Second retrieval (should use cache)
    result2 = service.get_video(category)
    modified_time2 = result2.stat().st_mtime
    
    assert result1 == result2
    assert modified_time1 == modified_time2

@pytest.mark.integration
def test_get_video_different_categories(temp_cache_dir):
    """Test getting videos for different categories"""
    service = VideoService()
    categories = ["geography", "math", "physics"]
    
    results = []
    for category in categories:
        result = service.get_video(category)
        assert result.exists()
        results.append(result)
    
    # Verify unique files generated
    assert len(set(results)) == len(categories)

@pytest.mark.integration
def test_get_video_invalid_api_key(temp_cache_dir, monkeypatch):
    """Test handling invalid API key"""
    monkeypatch.setenv("RIDDLER_PEXELS_API_KEY", "invalid_key")
    
    service = VideoService()
    with pytest.raises(VideoError) as exc_info:
        service.get_video("geography")
    assert "API error" in str(exc_info.value)

@pytest.mark.integration
def test_get_video_cache_cleanup(temp_cache_dir):
    """Test cache cleanup during video retrieval"""
    service = VideoService()
    categories = ["geography", "math", "physics"]
    
    # Generate multiple files to trigger cleanup
    for _ in range(3):
        for category in categories:
            result = service.get_video(category)
            assert result.exists()
    
    # Verify cache size is maintained
    cache_size = sum(f.stat().st_size for f in Path(temp_cache_dir).glob("*"))
    assert cache_size <= service.cache_manager.max_size

@pytest.mark.integration
def test_get_video_resolution_requirements(temp_cache_dir):
    """Test video meets resolution requirements"""
    service = VideoService()
    result = service.get_video("geography")
    
    # Verify video properties (requires opencv-python)
    import cv2
    video = cv2.VideoCapture(str(result))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    
    assert width >= 1080  # Minimum width
    assert height >= 1920  # Minimum height for vertical video
    assert fps >= 30  # Minimum FPS 