"""Unit tests for main CLI module"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from main import parse_args, list_categories, main

def test_parse_args_defaults():
    """Test parsing command line arguments with defaults"""
    with patch('sys.argv', ['main.py', 'geography']):
        args = parse_args()
        assert args.category == 'geography'
        assert args.difficulty == 'medium'
        assert args.batch_size == 1
        assert args.output_dir == 'output'
        assert not args.list_categories

def test_parse_args_custom():
    """Test parsing command line arguments with custom values"""
    with patch('sys.argv', [
        'main.py',
        'math',
        '--difficulty', 'hard',
        '--batch-size', '5',
        '--output-dir', 'custom_output'
    ]):
        args = parse_args()
        assert args.category == 'math'
        assert args.difficulty == 'hard'
        assert args.batch_size == 5
        assert args.output_dir == 'custom_output'

def test_parse_args_list_categories():
    """Test parsing list categories argument"""
    with patch('sys.argv', ['main.py', '--list-categories']):
        args = parse_args()
        assert args.list_categories

def test_parse_args_invalid_batch_size():
    """Test parsing invalid batch size"""
    with patch('sys.argv', ['main.py', 'geography', '--batch-size', '0']):
        with pytest.raises(SystemExit):
            parse_args()

def test_list_categories(capsys):
    """Test listing available categories"""
    list_categories()
    captured = capsys.readouterr()
    
    # Verify output contains all categories
    assert "Geography" in captured.out
    assert "Math" in captured.out
    assert "Physics" in captured.out
    assert "History" in captured.out
    assert "Logic" in captured.out
    assert "Wordplay" in captured.out

@patch('core.riddler.Riddler')
def test_main_single_riddle(mock_riddler_class, tmp_path):
    """Test generating a single riddle"""
    # Mock Riddler instance
    mock_riddler = MagicMock()
    mock_riddler_class.return_value = mock_riddler
    
    # Mock riddle data
    mock_riddle = {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation",
        "fun_fact": "Test fun fact"
    }
    mock_riddler.generate_riddle.return_value = mock_riddle
    
    # Mock video path
    mock_video = tmp_path / "test_video.mp4"
    mock_video.touch()
    mock_riddler.create_video.return_value = mock_video
    
    # Run main with arguments
    with patch('sys.argv', ['main.py', 'geography']):
        main()
    
    # Verify calls
    mock_riddler.generate_riddle.assert_called_once_with("geography", "medium")
    mock_riddler.create_video.assert_called_once_with(mock_riddle, "geography")

@patch('core.riddler.Riddler')
def test_main_batch_processing(mock_riddler_class, tmp_path):
    """Test generating multiple riddles"""
    # Mock Riddler instance
    mock_riddler = MagicMock()
    mock_riddler_class.return_value = mock_riddler
    
    # Mock riddle data
    mock_riddle = {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation",
        "fun_fact": "Test fun fact"
    }
    mock_riddler.generate_riddle.return_value = mock_riddle
    
    # Mock video path
    mock_video = tmp_path / "test_video.mp4"
    mock_video.touch()
    mock_riddler.create_video.return_value = mock_video
    
    # Run main with batch arguments
    with patch('sys.argv', ['main.py', 'geography', '--batch-size', '3']):
        main()
    
    # Verify multiple calls
    assert mock_riddler.generate_riddle.call_count == 3
    assert mock_riddler.create_video.call_count == 3

@patch('core.riddler.Riddler')
def test_main_output_directory(mock_riddler_class, tmp_path):
    """Test custom output directory"""
    # Mock Riddler instance
    mock_riddler = MagicMock()
    mock_riddler_class.return_value = mock_riddler
    
    # Mock riddle data and video
    mock_riddle = {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation",
        "fun_fact": "Test fun fact"
    }
    mock_riddler.generate_riddle.return_value = mock_riddle
    
    mock_video = tmp_path / "test_video.mp4"
    mock_video.touch()
    mock_riddler.create_video.return_value = mock_video
    
    # Run main with custom output directory
    output_dir = tmp_path / "custom_output"
    with patch('sys.argv', ['main.py', 'geography', '--output-dir', str(output_dir)]):
        main()
    
    # Verify output directory was created
    assert output_dir.exists()
    assert output_dir.is_dir()

@patch('core.riddler.Riddler')
def test_main_error_handling(mock_riddler_class):
    """Test error handling in main"""
    # Mock Riddler instance
    mock_riddler = MagicMock()
    mock_riddler_class.return_value = mock_riddler
    
    # Mock error in riddle generation
    mock_riddler.generate_riddle.side_effect = ValueError("Test error")
    
    # Run main and verify error handling
    with patch('sys.argv', ['main.py', 'geography']):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1 