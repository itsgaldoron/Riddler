"""Unit tests for helpers module"""

import pytest
import os
from pathlib import Path
from utils.helpers import (
    get_api_key,
    format_duration,
    get_file_size,
    format_file_size,
    ensure_dir_exists,
    clean_filename
)

def test_get_api_key_valid(monkeypatch):
    """Test getting valid API key"""
    monkeypatch.setenv("RIDDLER_TEST_KEY", "test_value")
    assert get_api_key("RIDDLER_TEST_KEY") == "test_value"

def test_get_api_key_missing():
    """Test getting missing API key"""
    with pytest.raises(ValueError) as exc_info:
        get_api_key("NONEXISTENT_KEY")
    assert "API key not found" in str(exc_info.value)

def test_format_duration():
    """Test duration formatting"""
    test_cases = [
        (30, "00:30"),
        (60, "01:00"),
        (90, "01:30"),
        (3600, "60:00")
    ]
    for seconds, expected in test_cases:
        assert format_duration(seconds) == expected

def test_format_duration_invalid():
    """Test formatting invalid durations"""
    invalid_durations = [-1, "30", None]
    for duration in invalid_durations:
        with pytest.raises(ValueError):
            format_duration(duration)

def test_get_file_size(tmp_path):
    """Test getting file size"""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("x" * 1024)  # 1KB of data
    
    size = get_file_size(test_file)
    assert size == 1024

def test_get_file_size_nonexistent():
    """Test getting size of nonexistent file"""
    with pytest.raises(FileNotFoundError):
        get_file_size(Path("nonexistent.txt"))

def test_format_file_size():
    """Test file size formatting"""
    test_cases = [
        (500, "500 B"),
        (1024, "1.0 KB"),
        (1024 * 1024, "1.0 MB"),
        (1024 * 1024 * 1024, "1.0 GB")
    ]
    for size, expected in test_cases:
        assert format_file_size(size) == expected

def test_format_file_size_invalid():
    """Test formatting invalid file sizes"""
    invalid_sizes = [-1, "1024", None]
    for size in invalid_sizes:
        with pytest.raises(ValueError):
            format_file_size(size)

def test_ensure_dir_exists(tmp_path):
    """Test directory creation"""
    test_dir = tmp_path / "test_dir"
    ensure_dir_exists(test_dir)
    assert test_dir.exists()
    assert test_dir.is_dir()

def test_ensure_dir_exists_nested(tmp_path):
    """Test nested directory creation"""
    nested_dir = tmp_path / "parent" / "child" / "grandchild"
    ensure_dir_exists(nested_dir)
    assert nested_dir.exists()
    assert nested_dir.is_dir()

def test_clean_filename():
    """Test filename cleaning"""
    test_cases = [
        ("test.txt", "test.txt"),
        ("test/file.txt", "test_file.txt"),
        ("test\\file.txt", "test_file.txt"),
        ("test:*?.txt", "test___.txt"),
        ("", "unnamed"),
        (None, "unnamed")
    ]
    for filename, expected in test_cases:
        assert clean_filename(filename) == expected

def test_clean_filename_max_length():
    """Test filename length limitation"""
    long_name = "x" * 300 + ".txt"
    result = clean_filename(long_name)
    assert len(result) <= 255  # Maximum filename length on most systems 