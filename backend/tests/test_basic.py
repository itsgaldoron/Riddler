"""
Basic tests for the Riddler application.
"""
import os
import sys
import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that key modules can be imported."""
    try:
        import config
        import utils
        import services
        import core
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"

@pytest.mark.parametrize(
    "category,difficulty",
    [
        ("geography", "easy"),
        ("math", "medium"),
        ("physics", "hard"),
        ("history", "medium"),
        ("logic", "easy"),
        ("wordplay", "hard"),
    ]
)
def test_valid_categories_and_difficulties(category, difficulty):
    """Test that validators accept valid categories and difficulties."""
    try:
        from utils.validators import validate_category, validate_difficulty
        
        validate_category(category)
        validate_difficulty(difficulty)
        assert True
    except Exception as e:
        assert False, f"Validation failed: {e}"

def test_config_loading():
    """Test that the config can be loaded."""
    try:
        from config.config import load_config
        
        config = load_config()
        assert config is not None
        assert "tts" in config
        assert "video" in config
        assert "style" in config
    except Exception as e:
        assert False, f"Config loading failed: {e}" 