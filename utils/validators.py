"""Input validation utilities"""

import os
from typing import List
from config.config import Config

def validate_category(category: str) -> bool:
    """Validate riddle category
    
    Args:
        category: Category to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If category is invalid
    """
    config = Config()
    valid_categories = config.get("openai.riddle_generation.categories", [
        "geography",
        "math",
        "physics",
        "history",
        "logic",
        "wordplay"
    ])
    
    if not category or category not in valid_categories:
        raise ValueError(
            f"Invalid category: {category}. "
            f"Must be one of: {', '.join(valid_categories)}"
        )
    
    return True

def validate_difficulty(difficulty: str) -> bool:
    """Validate difficulty level
    
    Args:
        difficulty: Difficulty level to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If difficulty is invalid
    """
    config = Config()
    valid_difficulties = list(config.get("openai.riddle_generation.difficulty_levels", {}).keys())
    
    if not difficulty or difficulty not in valid_difficulties:
        raise ValueError(
            f"Invalid difficulty: {difficulty}. "
            f"Must be one of: {', '.join(valid_difficulties)}"
        )
    
    return True

def validate_file_path(file_path: str) -> bool:
    """Validate file path
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If path is invalid
    """
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    return True

def validate_cache_dir(cache_dir: str) -> bool:
    """Validate cache directory
    
    Args:
        cache_dir: Directory to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If directory is invalid
    """
    if not cache_dir:
        raise ValueError("Cache directory cannot be empty")
    
    if not os.path.isdir(cache_dir):
        raise ValueError(f"Not a directory: {cache_dir}")
    
    # Check write permissions
    try:
        test_file = os.path.join(cache_dir, ".test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except (IOError, OSError):
        raise ValueError(f"No write permission: {cache_dir}")
    
    return True 