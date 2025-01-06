"""Integration tests for complete riddle generation flow"""

import pytest
from pathlib import Path
from core.riddler import Riddler
from services.tts_service import TTSService
from services.video_service import VideoService
from utils.validators import validate_category, validate_difficulty

@pytest.fixture
def services():
    """Create service instances"""
    return {
        "riddler": Riddler(),
        "tts": TTSService(),
        "video": VideoService()
    }

@pytest.mark.integration
def test_complete_flow(services, tmp_path):
    """Test complete riddle generation and video creation flow"""
    # 1. Generate riddle
    riddle_data = services["riddler"].generate_riddle("geography", "medium")
    
    # Validate riddle data
    assert isinstance(riddle_data, dict)
    assert all(key in riddle_data for key in ["riddle", "answer", "explanation"])
    assert all(len(value) > 0 for value in riddle_data.values())
    
    # 2. Create video
    video_path = services["riddler"].create_video(riddle_data, "geography")
    
    # Validate video
    assert video_path.exists()
    assert video_path.stat().st_size > 0
    
    # Clean up
    video_path.unlink()

@pytest.mark.integration
def test_multiple_categories(services):
    """Test riddle generation across all categories"""
    categories = ["geography", "math", "physics", "history", "logic", "wordplay"]
    
    for category in categories:
        # Validate category
        assert validate_category(category)
        
        # Generate riddle
        riddle_data = services["riddler"].generate_riddle(category, "medium")
        
        # Validate riddle data
        assert isinstance(riddle_data, dict)
        assert all(key in riddle_data for key in ["riddle", "answer", "explanation"])
        assert all(len(value) > 0 for value in riddle_data.values())

@pytest.mark.integration
def test_difficulty_levels(services):
    """Test riddle generation across difficulty levels"""
    difficulties = ["easy", "medium", "hard"]
    
    for difficulty in difficulties:
        # Validate difficulty
        assert validate_difficulty(difficulty)
        
        # Generate riddle
        riddle_data = services["riddler"].generate_riddle("geography", difficulty)
        
        # Validate riddle data
        assert isinstance(riddle_data, dict)
        assert all(key in riddle_data for key in ["riddle", "answer", "explanation"])
        assert all(len(value) > 0 for value in riddle_data.values())

@pytest.mark.integration
@pytest.mark.slow
def test_batch_processing(services, tmp_path):
    """Test batch processing of multiple riddles"""
    batch_size = 3
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    for i in range(batch_size):
        # Generate riddle
        riddle_data = services["riddler"].generate_riddle("geography", "medium")
        
        # Create video
        video_path = services["riddler"].create_video(riddle_data, "geography")
        
        # Move to output directory
        output_path = output_dir / f"riddle_{i+1}.mp4"
        video_path.rename(output_path)
        
        # Validate output
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    # Verify batch results
    video_files = list(output_dir.glob("*.mp4"))
    assert len(video_files) == batch_size 