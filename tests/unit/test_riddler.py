"""Unit tests for Riddler class"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.riddler import Riddler
from config.exceptions import ConfigurationError

@pytest.fixture
def riddler():
    """Create Riddler instance"""
    return Riddler()

def test_init(riddler):
    """Test Riddler initialization"""
    assert riddler.tts_service is not None
    assert riddler.video_service is not None

@patch('openai.ChatCompletion.create')
def test_generate_riddle_success(mock_create, riddler):
    """Test successful riddle generation"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
    {
        "riddle": "What has cities, but no houses?",
        "answer": "A map",
        "explanation": "A map shows cities but doesn't contain actual houses",
        "fun_fact": "The oldest known map is from ancient Babylon"
    }
    """
    mock_create.return_value = mock_response
    
    riddle_data = riddler.generate_riddle("geography", "medium")
    
    assert isinstance(riddle_data, dict)
    assert "riddle" in riddle_data
    assert "answer" in riddle_data
    assert "explanation" in riddle_data
    assert "fun_fact" in riddle_data
    assert riddle_data["answer"] == "A map"

@patch('openai.ChatCompletion.create')
def test_generate_riddle_invalid_response(mock_create, riddler):
    """Test handling invalid OpenAI response"""
    # Mock invalid response format
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Invalid response"
    mock_create.return_value = mock_response
    
    with pytest.raises(ValueError) as exc_info:
        riddler.generate_riddle("geography", "medium")
    assert "Failed to parse riddle response" in str(exc_info.value)

def test_create_video_success(riddler, tmp_path):
    """Test successful video creation"""
    # Mock riddle data
    riddle_data = {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation",
        "fun_fact": "Test fun fact"
    }
    
    # Mock service responses
    riddler.tts_service.generate_speech = MagicMock(return_value=tmp_path / "audio.mp3")
    riddler.video_service.get_video = MagicMock(return_value=tmp_path / "video.mp4")
    
    video_path = riddler.create_video(riddle_data, "geography")
    
    assert video_path.exists()
    assert video_path.suffix == ".mp4"

def test_create_video_invalid_data(riddler):
    """Test video creation with invalid riddle data"""
    invalid_data = {
        "riddle": "Test riddle"
        # Missing required fields
    }
    
    with pytest.raises(ValueError) as exc_info:
        riddler.create_video(invalid_data, "geography")
    assert "Invalid riddle data" in str(exc_info.value)

def test_parse_riddle_response_valid():
    """Test parsing valid riddle response"""
    response = """
    {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation",
        "fun_fact": "Test fun fact"
    }
    """
    
    result = Riddler._parse_riddle_response(response)
    
    assert isinstance(result, dict)
    assert result["riddle"] == "Test riddle"
    assert result["answer"] == "Test answer"
    assert result["explanation"] == "Test explanation"
    assert result["fun_fact"] == "Test fun fact"

def test_parse_riddle_response_invalid():
    """Test parsing invalid riddle response"""
    invalid_responses = [
        "Not JSON",
        "{}",  # Empty JSON
        '{"riddle": "Missing fields"}'
    ]
    
    for response in invalid_responses:
        with pytest.raises(ValueError) as exc_info:
            Riddler._parse_riddle_response(response)
        assert "Failed to parse riddle response" in str(exc_info.value) 