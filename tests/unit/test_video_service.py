"""Unit tests for Video service"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from services.video_service import VideoService
from config.exceptions import VideoError

@pytest.fixture
def video_service():
    """Create Video service instance"""
    return VideoService()

def test_init(video_service):
    """Test Video service initialization"""
    assert "world map globe" in video_service.categories
    assert "world celebration" in video_service.categories

def test_get_video_invalid_category(video_service):
    """Test getting video with invalid category"""
    with pytest.raises(VideoError) as exc_info:
        video_service.get_video("invalid_category")
    assert "Invalid category" in str(exc_info.value)

def test_get_video_cached(video_service, tmp_path):
    """Test getting video when cached"""
    # Create mock cached file
    cache_key = "world map globe_123"
    cached_path = tmp_path / cache_key
    cached_path.write_text("test video content")
    
    # Mock cache manager to return cached path
    video_service.cache_manager.get = MagicMock(return_value=cached_path)
    
    result = video_service.get_video("world map globe")
    assert result == cached_path
    assert result.read_text() == "test video content"

@patch('requests.get')
def test_get_video_api_call(mock_get, video_service):
    """Test getting video via API call"""
    # Mock successful API responses
    search_response = MagicMock()
    search_response.status_code = 200
    search_response.json.return_value = {
        "videos": [{
            "video_files": [{
                "width": 3840,
                "height": 2160,
                "link": "https://example.com/video.mp4"
            }]
        }]
    }
    
    video_response = MagicMock()
    video_response.iter_content.return_value = [b"test video content"]
    
    mock_get.side_effect = [search_response, video_response]
    
    # Mock cache miss
    video_service.cache_manager.get = MagicMock(return_value=None)
    
    # Mock cache put
    output_path = Path("test_output.mp4")
    video_service.cache_manager.put = MagicMock(return_value=output_path)
    
    result = video_service.get_video("world map globe")
    assert result == output_path
    
    # Verify API calls
    assert mock_get.call_count == 2
    search_call, video_call = mock_get.call_args_list
    assert "search" in search_call[0][0]
    assert "video.mp4" in video_call[0][0]

@patch('requests.get')
def test_get_video_api_error(mock_get, video_service):
    """Test handling API errors"""
    # Mock failed API response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "API error"
    mock_get.return_value = mock_response
    
    # Mock cache miss
    video_service.cache_manager.get = MagicMock(return_value=None)
    
    with pytest.raises(VideoError) as exc_info:
        video_service.get_video("world map globe")
    
    assert "API error" in str(exc_info.value)

@patch('requests.get')
def test_get_video_no_results(mock_get, video_service):
    """Test handling no video results"""
    # Mock empty API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"videos": []}
    mock_get.return_value = mock_response
    
    # Mock cache miss
    video_service.cache_manager.get = MagicMock(return_value=None)
    
    with pytest.raises(VideoError) as exc_info:
        video_service.get_video("world map globe")
    
    assert "No videos found" in str(exc_info.value) 