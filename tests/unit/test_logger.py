"""Unit tests for logger"""

import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from utils.logger import (
    setup_logger,
    log_error,
    log_api_call,
    log_cache_operation,
    log_video_processing
)

@pytest.fixture
def log_file(tmp_path):
    """Create temporary log file"""
    return tmp_path / "riddler.log"

@pytest.fixture
def logger(log_file):
    """Set up logger for testing"""
    return setup_logger(log_file)

def test_setup_logger(log_file):
    """Test logger setup"""
    logger = setup_logger(log_file)
    
    assert logger.name == "riddler"
    assert logger.level == logging.INFO
    assert log_file.exists()

def test_log_error(logger, log_file):
    """Test error logging"""
    error = ValueError("Test error")
    log_error(logger, error, "Test operation")
    
    log_content = log_file.read_text()
    assert "ERROR" in log_content
    assert "Test error" in log_content
    assert "Test operation" in log_content

def test_log_api_call(logger, log_file):
    """Test API call logging"""
    service = "OpenAI"
    endpoint = "/v1/chat/completions"
    status = 200
    duration = 1.5
    
    log_api_call(logger, service, endpoint, status, duration)
    
    log_content = log_file.read_text()
    assert "INFO" in log_content
    assert service in log_content
    assert endpoint in log_content
    assert str(status) in log_content
    assert str(duration) in log_content

def test_log_cache_operation(logger, log_file):
    """Test cache operation logging"""
    operation = "get"
    key = "test_key"
    result = "hit"
    
    log_cache_operation(logger, operation, key, result)
    
    log_content = log_file.read_text()
    assert "INFO" in log_content
    assert operation in log_content
    assert key in log_content
    assert result in log_content

def test_log_video_processing(logger, log_file):
    """Test video processing logging"""
    operation = "resize"
    input_path = Path("input.mp4")
    output_path = Path("output.mp4")
    duration = 2.5
    
    log_video_processing(logger, operation, input_path, output_path, duration)
    
    log_content = log_file.read_text()
    assert "INFO" in log_content
    assert operation in log_content
    assert str(input_path) in log_content
    assert str(output_path) in log_content
    assert str(duration) in log_content

def test_log_rotation(tmp_path):
    """Test log file rotation"""
    log_file = tmp_path / "riddler.log"
    logger = setup_logger(log_file, max_bytes=100, backup_count=3)
    
    # Generate enough logs to trigger rotation
    for i in range(100):
        logger.info("Test log message " * 10)
    
    # Check backup files were created
    backup_files = list(tmp_path.glob("riddler.log.*"))
    assert len(backup_files) > 0
    assert len(backup_files) <= 3

def test_log_formatting(logger, log_file):
    """Test log message formatting"""
    logger.info("Test message")
    
    log_content = log_file.read_text()
    # Check timestamp format: YYYY-MM-DD HH:MM:SS,mmm
    assert any(line.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}") 
              for line in log_file.read_text().splitlines())
    assert "INFO" in log_content
    assert "Test message" in log_content

def test_log_levels(logger, log_file):
    """Test different log levels"""
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    log_content = log_file.read_text()
    assert "DEBUG" not in log_content  # Default level is INFO
    assert "Info message" in log_content
    assert "Warning message" in log_content
    assert "Error message" in log_content
    assert "Critical message" in log_content

def test_concurrent_logging(tmp_path):
    """Test concurrent logging from multiple threads"""
    import threading
    
    log_file = tmp_path / "riddler.log"
    logger = setup_logger(log_file)
    errors = []
    
    def log_messages():
        try:
            for i in range(100):
                logger.info(f"Test message {threading.get_ident()} - {i}")
        except Exception as e:
            errors.append(e)
    
    # Create multiple threads
    threads = [threading.Thread(target=log_messages) for _ in range(5)]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify no errors occurred
    assert not errors
    
    # Verify all messages were logged
    log_content = log_file.read_text()
    assert len(log_content.splitlines()) == 500  # 5 threads * 100 messages 