"""Unit tests for Config class"""

import pytest
import json
from pathlib import Path
from config.config import Config
from config.exceptions import ConfigurationError

@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file"""
    config_data = {
        "tts": {
            "provider": "test_provider",
            "voice_id": "test_voice",
            "model": "test_model"
        },
        "video": {
            "pexels": {
                "categories": ["test_category"]
            }
        },
        "cache": {
            "voice_dir": "cache/voice",
            "video_dir": "cache/video"
        }
    }
    
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f)
    
    return config_path

@pytest.fixture
def mock_config(monkeypatch, config_file):
    """Create Config instance with mocked config file"""
    monkeypatch.setattr(Config, "_config_path", config_file)
    return Config()

def test_singleton(mock_config):
    """Test Config is a singleton"""
    config2 = Config()
    assert mock_config is config2

def test_get_existing_value(mock_config):
    """Test getting existing configuration value"""
    assert mock_config.get("tts.provider") == "test_provider"
    assert mock_config.get("tts.voice_id") == "test_voice"

def test_get_missing_value(mock_config):
    """Test getting missing configuration value"""
    assert mock_config.get("nonexistent.key", "default") == "default"
    assert mock_config.get("nonexistent") is None

def test_get_nested_value(mock_config):
    """Test getting nested configuration value"""
    categories = mock_config.get("video.pexels.categories")
    assert isinstance(categories, list)
    assert "test_category" in categories

def test_set_value(mock_config):
    """Test setting configuration value"""
    mock_config.set("test.key", "value")
    assert mock_config.get("test.key") == "value"

def test_set_nested_value(mock_config):
    """Test setting nested configuration value"""
    mock_config.set("test.nested.key", "value")
    assert mock_config.get("test.nested.key") == "value"

def test_set_existing_value(mock_config):
    """Test overwriting existing configuration value"""
    mock_config.set("tts.provider", "new_provider")
    assert mock_config.get("tts.provider") == "new_provider"

def test_validate_config(mock_config):
    """Test configuration validation"""
    assert mock_config.validate() is True

def test_validate_missing_required(mock_config):
    """Test validation with missing required value"""
    mock_config._config = {}  # Empty config
    with pytest.raises(ConfigurationError) as exc_info:
        mock_config.validate()
    assert "Missing required configuration" in str(exc_info.value)

def test_config_file_not_found():
    """Test handling missing config file"""
    with pytest.raises(ConfigurationError) as exc_info:
        Config._config_path = Path("nonexistent.json")
        Config()
    assert "config.json not found" in str(exc_info.value) 