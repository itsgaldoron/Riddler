"""Integration tests for Riddler class"""

import pytest
from pathlib import Path
from core.riddler import Riddler
from core.types import RiddleData

@pytest.fixture
def riddler():
    """Create Riddler instance for testing"""
    return Riddler()

def test_generate_riddle(riddler):
    """Test complete riddle generation flow"""
    riddle_data = riddler.generate_riddle("geography", "medium")
    
    # Verify structure
    assert isinstance(riddle_data, dict)
    assert "riddle" in riddle_data
    assert "answer" in riddle_data
    assert "explanation" in riddle_data
    
    # Verify content
    assert len(riddle_data["riddle"]) > 0
    assert len(riddle_data["answer"]) > 0
    assert len(riddle_data["explanation"]) > 0

@pytest.mark.slow
def test_create_video(riddler, tmp_path):
    """Test complete video creation flow"""
    # Generate riddle
    riddle_data = riddler.generate_riddle("geography", "medium")
    
    # Create video
    video_path = riddler.create_video(riddle_data, "geography")
    
    # Verify video was created
    assert video_path.exists()
    assert video_path.stat().st_size > 0
    
    # Clean up
    video_path.unlink() 