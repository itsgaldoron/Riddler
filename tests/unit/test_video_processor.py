"""Unit tests for video processor"""

import pytest
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from utils.video_processor import (
    VideoProcessor,
    add_text_overlay,
    resize_video,
    merge_audio_video,
    optimize_for_tiktok
)

@pytest.fixture
def sample_frame():
    """Create a sample video frame"""
    return np.zeros((1920, 1080, 3), dtype=np.uint8)

@pytest.fixture
def video_processor():
    """Create VideoProcessor instance"""
    return VideoProcessor()

def test_add_text_overlay(sample_frame):
    """Test adding text overlay to frame"""
    text = "Test Riddle"
    result = add_text_overlay(sample_frame, text)
    
    # Convert result to grayscale and check if any pixels are non-zero
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    assert np.any(gray > 0)  # Text should create non-zero pixels

def test_resize_video(tmp_path):
    """Test video resizing"""
    # Create test video
    input_path = tmp_path / "input.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(input_path), fourcc, 30, (1920, 1080))
    
    # Write some frames
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    for _ in range(30):
        writer.write(frame)
    writer.release()
    
    # Resize video
    output_path = tmp_path / "output.mp4"
    resize_video(input_path, output_path, (720, 1280))
    
    # Verify output
    cap = cv2.VideoCapture(str(output_path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    assert width == 720
    assert height == 1280

@patch('subprocess.run')
def test_merge_audio_video(mock_run, tmp_path):
    """Test merging audio and video"""
    video_path = tmp_path / "video.mp4"
    audio_path = tmp_path / "audio.mp3"
    output_path = tmp_path / "output.mp4"
    
    # Create dummy files
    video_path.touch()
    audio_path.touch()
    
    merge_audio_video(video_path, audio_path, output_path)
    
    # Verify ffmpeg command was called
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "ffmpeg" in args
    assert str(video_path) in args
    assert str(audio_path) in args
    assert str(output_path) in args

def test_optimize_for_tiktok(tmp_path):
    """Test TikTok video optimization"""
    # Create test video
    input_path = tmp_path / "input.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(input_path), fourcc, 30, (1920, 1080))
    
    # Write some frames
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    for _ in range(30):
        writer.write(frame)
    writer.release()
    
    # Optimize video
    output_path = tmp_path / "output.mp4"
    optimize_for_tiktok(input_path, output_path)
    
    # Verify output
    cap = cv2.VideoCapture(str(output_path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    cap.release()
    
    assert width == 1080  # TikTok recommended width
    assert height == 1920  # TikTok recommended height
    assert fps == 30  # TikTok recommended FPS

def test_video_processor_add_riddle_text(video_processor, tmp_path):
    """Test adding riddle text to video"""
    # Create test video
    input_path = tmp_path / "input.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(input_path), fourcc, 30, (1080, 1920))
    
    # Write some frames
    frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
    for _ in range(30):
        writer.write(frame)
    writer.release()
    
    # Add riddle text
    output_path = tmp_path / "output.mp4"
    riddle_data = {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation"
    }
    
    video_processor.add_riddle_text(input_path, output_path, riddle_data)
    
    # Verify output exists
    assert output_path.exists()
    assert output_path.stat().st_size > 0

def test_video_processor_invalid_input(video_processor):
    """Test handling invalid input video"""
    with pytest.raises(ValueError) as exc_info:
        video_processor.add_riddle_text(
            Path("nonexistent.mp4"),
            Path("output.mp4"),
            {"riddle": "Test"}
        )
    assert "Invalid input video" in str(exc_info.value)

def test_video_processor_invalid_riddle_data(video_processor, tmp_path):
    """Test handling invalid riddle data"""
    # Create test video
    input_path = tmp_path / "input.mp4"
    input_path.touch()
    
    with pytest.raises(ValueError) as exc_info:
        video_processor.add_riddle_text(
            input_path,
            tmp_path / "output.mp4",
            {}  # Empty riddle data
        )
    assert "Invalid riddle data" in str(exc_info.value) 